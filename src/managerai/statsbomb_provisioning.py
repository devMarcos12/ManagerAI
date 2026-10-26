"""Compatibilidade do clone StatsBomb, sem rede nem escrita nos dados."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Callable

from .data_inventory import load_season
from .data_loader import DataError, LocalData


@dataclass(frozen=True)
class GitSnapshot:
    root: Path
    origin: str
    revision: str
    changes: tuple[str, ...]


GitReader = Callable[[Path], GitSnapshot]


def load_contract() -> dict[str, Any]:
    """Lê o contrato que acompanha inclusive o wheel instalado."""
    try:
        payload = files("managerai").joinpath("statsbomb_snapshot.json").read_text(encoding="utf-8")
        contract = json.loads(payload)
        if contract["contract_version"] != "1.0.0" or not isinstance(contract["coverage"]["seasons"], list):
            raise ValueError("versão ou estrutura desconhecida")
        return contract
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise DataError(f"Contrato StatsBomb empacotado inválido: {exc}") from exc


def read_git_snapshot(root: Path) -> GitSnapshot:
    """Consulta somente metadados locais; não atualiza índice ou clone."""
    if not (root / ".git").exists():
        raise DataError("Clone sem metadados Git; provisione com git clone para comprovar a revisão.")

    def run(*args: str) -> str:
        try:
            proc = subprocess.run(
                ["git", "--no-optional-locks", "-C", str(root), *args],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=60, check=False,
                env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"},
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise DataError(f"Git local indisponível: {exc}") from exc
        if proc.returncode:
            raise DataError(f"Falha ao consultar metadados Git ({' '.join(args)}): {proc.stderr.strip()}")
        return proc.stdout.strip()

    return GitSnapshot(
        Path(run("rev-parse", "--show-toplevel")).resolve(),
        run("remote", "get-url", "origin"),
        run("rev-parse", "HEAD"),
        tuple(run("status", "--porcelain", "--untracked-files=all").splitlines()),
    )


def _issue(issues: list[dict[str, str]], code: str, severity: str, path: str,
           message: str, action: str) -> None:
    issues.append({"code": code, "severity": severity, "path": path,
                   "message": message, "action": action})


def _safe_path(root: Path, relative: str, issues: list[dict[str, str]]) -> Path | None:
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        _issue(issues, "PATH_OUTSIDE_ROOT", "erro", relative,
               "Caminho resolve fora da raiz informada.", "Remova o link/escape e provisione o clone íntegro.")
        return None
    return candidate


def _hash_state(path: Path, expected: str) -> tuple[str, bool]:
    """Retorna hash de bytes e se apenas CRLF difere do blob esperado."""
    raw = path.read_bytes()
    observed = sha256(raw).hexdigest()
    converted = observed != expected and b"\r\n" in raw and sha256(raw.replace(b"\r\n", b"\n")).hexdigest() == expected
    return observed, converted


def _file_ids(root: Path, kind: str, issues: list[dict[str, str]]) -> set[str] | None:
    folder = _safe_path(root, kind, issues)
    if folder is None or not folder.is_dir():
        return None
    result: set[str] = set()
    for path in sorted(folder.glob("*.json")):
        if _safe_path(root, str(path.relative_to(root)), issues) is not None:
            result.add(path.stem)
    return result


def _origin_key(url: str) -> str:
    normalized = url.strip().lower().rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized.split(":", 1)[1]
    if normalized.startswith("ssh://git@github.com/"):
        normalized = "https://github.com/" + normalized.removeprefix("ssh://git@github.com/")
    return normalized


def verify_snapshot(data_root: str | Path, *, contract: dict[str, Any] | None = None,
                    git_reader: GitReader = read_git_snapshot) -> dict[str, Any]:
    """Compara origem, controles, calendários e presença com o contrato fixado.

    O modo rápido não abre JSONs de eventos, escalações ou 360. Git e hashes dos
    controles/calendários comprovam a revisão local, não integridade semântica.
    """
    spec = load_contract() if contract is None else contract
    requested = Path(data_root).absolute()
    root = requested.resolve()
    repo = root.parent
    issues: list[dict[str, str]] = []
    result: dict[str, Any] = {
        "status": "incompatível", "contract_version": spec["contract_version"],
        "data_root": str(root), "source": {"origin": None, "revision": None},
        "coverage": {"seasons": [], "file_counts": {}}, "issues": issues,
        "validation": {
            "controles_e_calendarios": "SHA-256 e estrutura JSON dos calendários",
            "eventos_escalacoes_360": "presença de arquivo; conteúdo não lido neste modo",
            "v3": "somente recortes explicitamente certificados no contrato; outros arquivos não ampliam a V3",
        },
    }

    if not root.exists():
        _issue(issues, "DATASET_MISSING", "erro", str(root), "Dataset ausente.",
               "Siga o guia de provisionamento e informe --data-root para open-data/data.")
        return result
    if not root.is_dir() or ((root / "data" / "competitions.json").exists()
                             and not (root / "competitions.json").exists()):
        _issue(issues, "ROOT_WRONG", "erro", str(root), "Raiz aponta para o diretório errado.",
               "Informe a pasta data do clone: --data-root open-data/data.")
        return result
    if not (root / "competitions.json").exists() and root.name != "data":
        _issue(issues, "ROOT_WRONG", "erro", str(root), "Raiz não contém competitions.json.",
               "Informe a pasta data do clone, não data/raw nem a raiz do repositório.")
        return result

    try:
        git = git_reader(repo)
    except DataError as exc:
        code = "GIT_QUERY_FAILED" if (repo / ".git").exists() else "GIT_METADATA_MISSING"
        _issue(issues, code, "erro", str(repo), str(exc),
               "Use um clone Git completo da origem oficial e confira se Git está disponível.")
    else:
        result["source"] = {"origin": git.origin, "revision": git.revision}
        if git.root.resolve() != repo:
            _issue(issues, "GIT_ROOT_WRONG", "erro", str(repo), "A raiz Git não é a pasta pai de data.",
                   "Aponte para data/ dentro do clone StatsBomb independente.")
        accepted = {_origin_key(url) for url in spec["source"]["accepted_origins"]}
        if _origin_key(git.origin) not in accepted:
            _issue(issues, "ORIGIN_INCOMPATIBLE", "erro", git.origin, "Origem Git incompatível.",
                   "Provisione da URL oficial; aliases aceitos constam no contrato, com revisão e hashes fixos.")
        if git.revision != spec["source"]["revision"]:
            _issue(issues, "REVISION_MISMATCH", "erro", git.revision, "Revisão Git diferente da fixada.",
                   f"Faça checkout da revisão {spec['source']['revision']} em um clone próprio.")
        if git.changes:
            _issue(issues, "WORKTREE_MODIFIED", "erro", str(repo),
                   f"Worktree StatsBomb modificado: {len(git.changes)} entrada(s) Git.",
                   "Use um clone íntegro; confira as alterações manualmente, sem limpeza automática.")

    for relative in spec["required_paths"]:
        path = _safe_path(repo, relative, issues)
        if path is None:
            continue
        if not path.exists():
            code = "REQUIRED_STRUCTURE_MISSING"
            if relative == "README.md":
                code = "README_MISSING"
            elif relative == "LICENSE.pdf":
                code = "LICENSE_MISSING"
            elif relative == "data/competitions.json":
                code = "CATALOG_MISSING"
            _issue(issues, code, "erro", relative, "Caminho obrigatório ausente.",
                   "Confira o checkout completo da revisão fixada; não copie arquivos avulsos.")
        elif relative.endswith("/") or relative in ("data/matches", "data/events", "data/lineups"):
            if not path.is_dir():
                _issue(issues, "REQUIRED_STRUCTURE_MISSING", "erro", relative,
                       "Era esperado um diretório.", "Provisione o clone completo.")
        elif not path.is_file():
            _issue(issues, "REQUIRED_STRUCTURE_MISSING", "erro", relative,
                   "Era esperado um arquivo.", "Provisione o clone completo.")

    for relative, expected in sorted(spec["control_sha256"].items()):
        path = _safe_path(repo, relative, issues)
        if path is None or not path.is_file():
            continue
        try:
            observed, converted = _hash_state(path, expected)
        except OSError as exc:
            _issue(issues, "CONTROL_UNREADABLE", "erro", relative, str(exc), "Verifique permissões e clone.")
            continue
        if observed != expected:
            code = "LINE_ENDINGS_CHANGED" if converted else (
                "CATALOG_HASH_MISMATCH" if relative.endswith("competitions.json") else "CONTROL_HASH_MISMATCH")
            _issue(issues, code, "erro", relative,
                   f"SHA-256 inesperado: esperado {expected}; observado {observed}.",
                   "Se houve conversão CRLF, crie um clone novo com git clone -c core.autocrlf=false; não altere os brutos." if converted
                   else "Provisione novamente a revisão fixada ou proponha atualização do contrato.")

    data = LocalData(root)
    catalog_path = _safe_path(root, "competitions.json", issues)
    catalog: list[dict[str, Any]] | None = None
    if catalog_path is not None and catalog_path.is_file():
        try:
            catalog = data.read("competitions.json")
            pairs = [(entry.get("competition_id"), entry.get("season_id")) for entry in catalog]
            if any(type(a) is not int or type(b) is not int or a <= 0 or b <= 0 for a, b in pairs) or len(pairs) != len(set(pairs)):
                raise DataError("IDs de competição/temporada inválidos ou duplicados")
        except (DataError, TypeError, ValueError) as exc:
            _issue(issues, "CATALOG_INVALID", "erro", "data/competitions.json", str(exc),
                   "Confira JSON e revisão; não corrija os brutos in loco.")
            catalog = None

    expected_rows = spec["coverage"]["seasons"]
    expected_pairs = {(r["competition_id"], r["season_id"]) for r in expected_rows}
    if catalog is not None:
        actual_pairs = {(c["competition_id"], c["season_id"]) for c in catalog}
        if len(actual_pairs) != spec["coverage"]["season_count"] or len({a for a, _ in actual_pairs}) != spec["coverage"]["competition_count"]:
            _issue(issues, "CATALOG_COVERAGE_MISMATCH", "erro", "data/competitions.json",
                   "Quantidade de competições ou temporadas difere do contrato.",
                   "Confira a revisão fixada e o catálogo.")
        for pair in sorted(expected_pairs - actual_pairs):
            _issue(issues, "SEASON_NOT_CATALOGED", "erro", f"{pair[0]}/{pair[1]}",
                   "Temporada esperada ausente do catálogo.", "Confira o catálogo da revisão fixada.")
        for pair in sorted(actual_pairs - expected_pairs):
            _issue(issues, "UNEXPECTED_SEASON", "erro", f"{pair[0]}/{pair[1]}",
                   "Temporada não consta do contrato.", "Abra mudança de contrato para nova revisão.")

    all_ids: set[int] = set()
    season_ids: dict[tuple[int, int], set[int]] = {}
    calendar_line_endings_reported = False
    for expected in expected_rows:
        ci, si = expected["competition_id"], expected["season_id"]
        relative = f"matches/{ci}/{si}.json"
        path = _safe_path(root, relative, issues)
        observed: dict[str, Any] = {"competition_id": ci, "season_id": si, "matches": None,
                                    "events": None, "lineups": None, "three_sixty": None}
        result["coverage"]["seasons"].append(observed)
        if path is None:
            continue
        if not path.is_file():
            _issue(issues, "SEASON_MISSING", "erro", f"data/{relative}",
                   "Arquivo da temporada ausente.", "Confira o checkout da revisão fixada.")
            continue
        if catalog is None:
            continue
        try:
            digest, converted = _hash_state(path, expected["calendar_sha256"])
            if digest != expected["calendar_sha256"]:
                if converted:
                    if not calendar_line_endings_reported:
                        _issue(issues, "LINE_ENDINGS_CHANGED", "erro", f"data/{relative}",
                               "Calendários em disco têm CRLF, enquanto a revisão Git contém LF; outros calendários podem estar afetados.",
                               "Crie um clone novo com git clone -c core.autocrlf=false; não altere os brutos.")
                        calendar_line_endings_reported = True
                else:
                    _issue(issues, "CALENDAR_HASH_MISMATCH", "erro", f"data/{relative}",
                           f"SHA-256 inesperado: esperado {expected['calendar_sha256']}; observado {digest}.",
                           "Confira o checkout ou proponha revisão do contrato.")
            season = load_season(data, ci, si)
            mids = {m["match_id"] for m in season.matches}
            if all_ids & mids:
                raise DataError("Partida duplicada entre temporadas")
            all_ids.update(mids)
            season_ids[(ci, si)] = mids
            observed["matches"] = len(mids)
            ids_digest = sha256(json.dumps(sorted(mids), separators=(",", ":")).encode("utf-8")).hexdigest()
            if "match_ids_sha256" in expected and ids_digest != expected["match_ids_sha256"]:
                _issue(issues, "MATCH_IDS_MISMATCH", "erro", f"data/{relative}",
                       "IDs de partidas diferem do contrato.", "Confira o calendário da revisão fixada.")
            if len(mids) != expected["matches"]:
                _issue(issues, "MATCH_COUNT_MISMATCH", "erro", f"data/{relative}",
                       f"Esperadas {expected['matches']} partidas; observadas {len(mids)}.",
                       "Confira o calendário da revisão fixada.")
        except (DataError, OSError, KeyError, TypeError, ValueError) as exc:
            _issue(issues, "SEASON_INVALID", "erro", f"data/{relative}", str(exc),
                   "Confira JSON e revisão da temporada; não corrija os brutos in loco.")

    files_by_kind = {kind: _file_ids(root, kind, issues) for kind in ("events", "lineups", "three-sixty")}
    catalog_complete = catalog is not None and len(season_ids) == len(expected_rows)
    known = {str(mid) for mid in all_ids}
    if not catalog_complete:
        result["coverage"]["orphan_file_ids"] = None
        _issue(issues, "ORPHANS_UNDETERMINED", "info", "data/matches",
               "Órfãos não determináveis: catálogo ou temporada incompleta.",
               "Corrija catálogo e temporadas antes de interpretar arquivos extras.")
    for kind, names in files_by_kind.items():
        result["coverage"]["file_counts"][kind] = None if names is None else len(names)
        if names is None:
            if kind == "three-sixty":
                _issue(issues, "THREE_SIXTY_PARTIAL", "aviso", "data/three-sixty",
                       "Diretório 360 ausente; cobertura espacial não verificável.",
                       "Confira a revisão se precisar dos 360; o produto não os analisa.")
            continue
        if not catalog_complete:
            continue
        orphans = sorted(names - known)
        result["coverage"].setdefault("orphan_file_ids", {})[kind] = orphans
        expected_orphans = spec["coverage"]["orphan_counts"][kind]
        if orphans:
            _issue(issues, "ORPHAN_FILES", "info", f"data/{kind}",
                   f"{len(orphans)} arquivo(s) sem partida no catálogo; não entram nas análises.",
                   "Mantenha separados do catálogo; investigue diferenças antes de atualizar a revisão.")
        if len(orphans) != expected_orphans:
            _issue(issues, "ORPHAN_COUNT_MISMATCH", "erro", f"data/{kind}",
                   f"Esperados {expected_orphans} órfãos; observados {len(orphans)}.",
                   "Confira revisão, catálogo e arquivos extras.")
        if len(names) != spec["coverage"]["file_counts"][kind]:
            severity = "aviso" if kind == "three-sixty" else "erro"
            _issue(issues, "FILE_COUNT_MISMATCH", severity, f"data/{kind}",
                   f"Esperados {spec['coverage']['file_counts'][kind]} arquivos; observados {len(names)}.",
                   "Confira a revisão e a cobertura antes da análise.")

    for row, observed in zip(expected_rows, result["coverage"]["seasons"]):
        mids = season_ids.get((row["competition_id"], row["season_id"]))
        if mids is None:
            continue
        for kind, key in (("events", "events"), ("lineups", "lineups"), ("three-sixty", "three_sixty")):
            names = files_by_kind[kind]
            if names is None:
                continue
            missing = sorted(mid for mid in mids if str(mid) not in names)
            observed[key] = len(mids) - len(missing)
            if kind in ("events", "lineups") and observed[key] != row[key]:
                _issue(issues, "SEASON_COVERAGE_MISMATCH", "erro", f"data/{kind}",
                       f"Cobertura {row['competition_id']}/{row['season_id']}: esperados {row[key]}, observados {observed[key]}.",
                       "Confira a temporada e os arquivos da revisão fixada.")
            if kind in ("events", "lineups") and missing:
                _issue(issues, "MATCH_FILE_MISSING", "erro",
                       f"data/{kind}/{missing[0]}.json",
                       f"{len(missing)} partida(s) catalogada(s) sem {kind} em {row['competition_id']}/{row['season_id']}; IDs: {missing[:20]}{'…' if len(missing) > 20 else ''}.",
                       "Confira o clone da revisão fixada; não substitua ausência por zero.")
            if kind == "three-sixty" and observed[key] < row["three_sixty"]:
                _issue(issues, "THREE_SIXTY_PARTIAL", "aviso",
                       f"data/three-sixty ({row['competition_id']}/{row['season_id']})",
                       f"360 presentes {observed[key]}/{row['three_sixty']} esperados neste par; cobertura parcial.",
                       "Confira o clone se 360 for necessário; 360 não é recorte certificado para análise.")

    if len(all_ids) != spec["coverage"]["cataloged_matches"] and len(season_ids) == len(expected_rows):
        _issue(issues, "TOTAL_MATCHES_MISMATCH", "erro", "data/matches",
               f"Esperadas {spec['coverage']['cataloged_matches']} partidas; observadas {len(all_ids)}.",
               "Confira os calendários da revisão fixada.")
    result["coverage"]["cataloged_matches"] = len(all_ids) if len(season_ids) == len(expected_rows) else None
    result["status"] = "incompatível" if any(i["severity"] == "erro" for i in issues) else "compatível"
    return result
