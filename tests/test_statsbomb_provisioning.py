"""Auditoria portátil de provisionamento com clone sintético pequeno."""
from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from managerai.cli import main
from managerai.statsbomb_provisioning import GitSnapshot, load_contract, verify_snapshot
from managerai.v3_schema import VALIDATED_RECUTS


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


class SnapshotFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.repo = Path(self.temp.name) / "open-data"
        self.root = self.repo / "data"
        self.repo.mkdir()
        self.write_bytes("README.md", b"StatsBomb synthetic README")
        self.write_bytes("LICENSE.pdf", b"synthetic license")
        catalog = [{"competition_id": 2, "season_id": 27,
                    "competition_name": "Liga sintética", "season_name": "2020"}]
        self.write_json("data/competitions.json", catalog)
        matches = [self.match(101, 1), self.match(102, 2)]
        self.write_json("data/matches/2/27.json", matches)
        for mid in (101, 102):
            self.write_json(f"data/events/{mid}.json", [])
            self.write_json(f"data/lineups/{mid}.json", [])
        self.write_json("data/three-sixty/101.json", [])
        self.write_json("data/events/999.json", [])
        self.write_json("data/lineups/999.json", [])
        self.contract = {
            "contract_version": "1.0.0",
            "source": {"revision": "abc123", "accepted_origins": ["https://github.com/hudl/open-data.git",
                                                             "https://github.com/statsbomb/open-data.git"]},
            "required_paths": ["README.md", "LICENSE.pdf", "data/competitions.json",
                               "data/matches", "data/events", "data/lineups"],
            "control_sha256": {name: _digest((self.repo / name).read_bytes()) for name in
                               ("README.md", "LICENSE.pdf", "data/competitions.json")},
            "coverage": {
                "competition_count": 1, "season_count": 1, "cataloged_matches": 2,
                "file_counts": {"events": 3, "lineups": 3, "three-sixty": 1},
                "orphan_counts": {"events": 1, "lineups": 1, "three-sixty": 0},
                "seasons": [{"competition_id": 2, "season_id": 27, "matches": 2,
                             "events": 2, "lineups": 2, "three_sixty": 1,
                             "match_ids_sha256": _digest(b"[101,102]"),
                             "calendar_sha256": _digest((self.root / "matches/2/27.json").read_bytes())}],
            },
            "v3_certified_recuts": [[2, 27], [11, 90]],
        }
        self.git = GitSnapshot(self.repo.resolve(), "https://github.com/statsbomb/open-data.git", "abc123", ())

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def match(mid: int, day: int) -> dict:
        return {"match_id": mid, "match_date": f"2020-01-{day:02d}",
                "competition": {"competition_id": 2}, "season": {"season_id": 27},
                "home_team": {"home_team_id": 1, "home_team_name": "A"},
                "away_team": {"away_team_id": 2, "away_team_name": "B"}}

    def write_bytes(self, relative: str, data: bytes) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def write_json(self, relative: str, data: object) -> None:
        self.write_bytes(relative, json.dumps(data).encode("utf-8"))

    def check(self, *, contract: dict | None = None, git: GitSnapshot | None = None) -> dict:
        return verify_snapshot(self.root, contract=contract or self.contract,
                               git_reader=lambda _: git or self.git)

    def codes(self, result: dict) -> set[str]:
        return {issue["code"] for issue in result["issues"]}


class ProvisioningTests(SnapshotFixture):
    def test_compatible_alias_deterministic_and_orphans_informative(self):
        first = self.check()
        self.assertEqual(first["status"], "compatível")
        self.assertEqual(first["coverage"]["cataloged_matches"], 2)
        self.assertEqual(first["coverage"]["seasons"][0]["three_sixty"], 1)
        self.assertEqual(first["coverage"]["orphan_file_ids"]["events"], ["999"])
        self.assertIn("ORPHAN_FILES", self.codes(first))
        canonical_origin = GitSnapshot(self.repo.resolve(), "https://github.com/hudl/open-data.git", "abc123", ())
        self.assertEqual(self.check(git=canonical_origin)["status"], "compatível")
        self.assertEqual(first, self.check())
        self.assertEqual(json.dumps(first, sort_keys=True, ensure_ascii=False, allow_nan=False),
                         json.dumps(self.check(), sort_keys=True, ensure_ascii=False, allow_nan=False))

    def test_absent_wrong_root_and_missing_git(self):
        absent = verify_snapshot(self.repo / "missing", contract=self.contract,
                                 git_reader=lambda _: self.git)
        self.assertIn("DATASET_MISSING", self.codes(absent))
        wrong = verify_snapshot(self.repo, contract=self.contract, git_reader=lambda _: self.git)
        self.assertIn("ROOT_WRONG", self.codes(wrong))
        from managerai.data_loader import DataError
        def no_git(_: Path) -> GitSnapshot:
            raise DataError("sem .git")
        self.assertIn("GIT_METADATA_MISSING", self.codes(verify_snapshot(
            self.root, contract=self.contract, git_reader=no_git)))

    def test_revision_origin_worktree_and_git_root(self):
        for changed, expected in (
            (GitSnapshot(self.repo.resolve(), self.git.origin, "wrong", ()), "REVISION_MISMATCH"),
            (GitSnapshot(self.repo.resolve(), "https://example.org/open-data.git", "abc123", ()), "ORIGIN_INCOMPATIBLE"),
            (GitSnapshot(self.repo.resolve(), self.git.origin, "abc123", (" M data/events/101.json",)), "WORKTREE_MODIFIED"),
            (GitSnapshot(self.root.resolve(), self.git.origin, "abc123", ()), "GIT_ROOT_WRONG"),
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.codes(self.check(git=changed)))
                self.assertEqual(self.check(git=changed)["status"], "incompatível")

    def test_license_readme_and_catalog(self):
        (self.repo / "LICENSE.pdf").unlink()
        self.assertIn("LICENSE_MISSING", self.codes(self.check()))
        self.write_bytes("LICENSE.pdf", b"changed")
        self.assertIn("CONTROL_HASH_MISMATCH", self.codes(self.check()))
        (self.repo / "README.md").unlink()
        self.assertIn("README_MISSING", self.codes(self.check()))
        (self.root / "competitions.json").unlink()
        self.assertIn("CATALOG_MISSING", self.codes(self.check()))
        self.write_bytes("data/competitions.json", b"not json")
        codes = self.codes(self.check())
        self.assertIn("CATALOG_INVALID", codes)
        self.assertIn("CATALOG_HASH_MISMATCH", codes)
        self.write_json("data/competitions.json", [])
        self.assertIn("SEASON_NOT_CATALOGED", self.codes(self.check()))

    def test_missing_season_match_files_and_360(self):
        (self.root / "matches/2/27.json").unlink()
        self.assertIn("SEASON_MISSING", self.codes(self.check()))
        self.write_json("data/matches/2/27.json", [self.match(101, 1), self.match(102, 2)])
        (self.root / "events/102.json").unlink()
        (self.root / "lineups/101.json").unlink()
        result = self.check()
        self.assertIn("MATCH_FILE_MISSING", self.codes(result))
        self.assertEqual(result["coverage"]["seasons"][0]["events"], 1)
        (self.root / "three-sixty/101.json").unlink()
        result = self.check()
        self.assertIn("THREE_SIXTY_PARTIAL", self.codes(result))
        self.assertTrue(any(i["severity"] == "aviso" for i in result["issues"] if i["code"] == "THREE_SIXTY_PARTIAL"))

    def test_invalid_calendar_and_changed_match_ids(self):
        self.write_bytes("data/matches/2/27.json", b"invalid")
        codes = self.codes(self.check())
        self.assertIn("CALENDAR_HASH_MISMATCH", codes)
        self.assertIn("SEASON_INVALID", codes)
        self.write_json("data/matches/2/27.json", [self.match(101, 1), self.match(103, 2)])
        self.assertIn("MATCH_IDS_MISMATCH", self.codes(self.check()))

    def test_extra_orphan_and_path_escape(self):
        self.write_json("data/events/1000.json", [])
        self.assertIn("ORPHAN_COUNT_MISMATCH", self.codes(self.check()))
        bad = deepcopy(self.contract)
        bad["control_sha256"]["../outside.txt"] = "0" * 64
        self.assertIn("PATH_OUTSIDE_ROOT", self.codes(self.check(contract=bad)))

    def test_clean_git_with_crlf_converted_bytes_is_incompatible(self):
        catalog = (self.root / "competitions.json").read_text(encoding="utf-8")
        canonical = (catalog + "\n").encode("utf-8")
        self.contract["control_sha256"]["data/competitions.json"] = _digest(canonical)
        self.write_bytes("data/competitions.json", canonical.replace(b"\n", b"\r\n"))
        result = self.check()
        self.assertEqual(result["status"], "incompatível")
        self.assertIn("LINE_ENDINGS_CHANGED", self.codes(result))
        self.assertTrue(any("core.autocrlf=false" in issue["action"] for issue in result["issues"]))

    def test_cli_json_exit_codes_and_environment(self):
        def real_with_fixture(root: Path) -> dict:
            return verify_snapshot(root, contract=self.contract, git_reader=lambda _: self.git)
        with patch("managerai.cli.verify_snapshot", side_effect=real_with_fixture):
            out = StringIO()
            with redirect_stdout(out):
                code = main(["--data-root", str(self.root), "verify-data"])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out.getvalue())["status"], "compatível")
            with patch.dict("os.environ", {"MANAGERAI_DATA_ROOT": str(self.root)}):
                out = StringIO()
                with redirect_stdout(out):
                    self.assertEqual(main(["verify-data"]), 0)
            (self.root / "events/101.json").unlink()
            out = StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(["--data-root", str(self.root), "verify-data"]), 2)
            self.assertEqual(json.loads(out.getvalue())["status"], "incompatível")

    def test_packaged_contract_matches_v3_constant(self):
        contract = load_contract()
        self.assertEqual(contract["contract_version"], "1.0.0")
        self.assertEqual({tuple(pair) for pair in contract["v3_certified_recuts"]}, VALIDATED_RECUTS)
        self.assertEqual(len(contract["coverage"]["seasons"]), contract["coverage"]["season_count"])


if __name__ == "__main__":
    unittest.main()
