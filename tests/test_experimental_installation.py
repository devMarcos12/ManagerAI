"""Regressões de instalação e referência; fixtures sintéticas sem evidência esportiva."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from managerai.experiments import paths, robustness
from managerai.experiments.dataset import digest


class ExperimentPathTests(unittest.TestCase):
    def test_checkout_is_found_from_nested_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text('[project]\nname="managerai"\n')
            self.assertEqual(paths.project_root(root / "nested" / "child"), root)

    def test_other_project_does_not_shadow_managerai_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text('[project]\nname="managerai"\n')
            nested = root / "nested"
            nested.mkdir()
            (nested / "pyproject.toml").write_text('[project]\nname="other"\n')
            self.assertEqual(paths.project_root(nested), root)

    def test_installed_layout_does_not_mistake_venv_for_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(paths, "__file__", str(root / "env/lib/python3.12/site-packages/managerai/experiments/paths.py")):
                with self.assertRaisesRegex(ValueError, "checkout"):
                    paths.project_root(root / "unrelated")

    def test_hashes_describe_executing_package_with_stable_keys(self):
        hashes = paths.execution_code_hashes()
        self.assertEqual(hashes["src/managerai/experiments/paths.py"], sha256(Path(paths.__file__).read_bytes()).hexdigest())
        self.assertIn("src/managerai/tactical_engines.py", hashes)
        self.assertTrue(all(len(v) == 64 and k.startswith("src/managerai/") for k, v in hashes.items()))


class ReferenceValidationTests(unittest.TestCase):
    def setUp(self):
        self.reference = {"protocol": {"window": 5}, "dataset": {"examples": [1, 2]},
                          "results": {"predictions": [3.123456781], "status": "evaluated"},
                          "reproduction": {"head": "old"}}
        for key in ("protocol", "dataset"):
            self.reference[key + "_fingerprint"] = digest(self.reference[key])
        constants = {"REFERENCE_PROTOCOL": self.reference["protocol_fingerprint"],
                     "REFERENCE_DATASET": self.reference["dataset_fingerprint"],
                     "REFERENCE_RESULTS": digest(robustness.numerical_signature(self.reference["results"]))}
        self.patcher = patch.multiple(robustness, **constants)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def validate(self, value):
        return robustness.validate_reference(json.dumps(value).encode())

    def test_new_git_metadata_does_not_require_old_binary_artifact(self):
        changed = deepcopy(self.reference)
        changed["reproduction"] = {"head": "new", "code_sha256": {"module.py": "a" * 64}}
        self.assertEqual(self.validate(changed)["results"], self.reference["results"])

    def test_significant_prediction_changes_are_rejected(self):
        changed = deepcopy(self.reference)
        changed["results"]["predictions"][0] += .01
        with self.assertRaisesRegex(ValueError, "diverge"):
            self.validate(changed)

    def test_declared_precision_is_for_signature_only(self):
        changed = deepcopy(self.reference)
        changed["results"]["predictions"][0] += 1e-12
        self.assertEqual(self.validate(changed), changed)
        self.assertNotEqual(changed, self.reference)

    def test_modified_protocol_and_dataset_rejected_even_with_new_self_hash(self):
        for key in ("protocol", "dataset"):
            changed = deepcopy(self.reference)
            changed[key]["extra"] = True
            changed[key + "_fingerprint"] = digest(changed[key])
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "diverge"):
                self.validate(changed)

    def test_invalid_json_fingerprints_and_nonfinite_numbers_rejected(self):
        broken = deepcopy(self.reference)
        broken["dataset_fingerprint"] = "b" * 64
        for payload in (b"{}", b"[]", b"invalid", b'{"results": NaN}', json.dumps(broken).encode()):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                robustness.validate_reference(payload)
        with self.assertRaises(ValueError):
            robustness.numerical_signature(float("inf"))
