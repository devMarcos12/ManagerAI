"""Localização do checkout e proveniência do código efetivamente executado."""
from hashlib import sha256
from pathlib import Path
import tomllib


def project_root(start: Path | None = None) -> Path:
    """Experimentos instalados são executados dentro de um checkout ManagerAI.

    O pacote em site-packages não contém pyproject nem artefatos. Procurar a
    raiz pelo diretório de execução evita confundi-la com a raiz do ambiente.
    O fallback permite executar o layout src a partir de um temporário externo.
    """
    anchor = Path.cwd() if start is None else Path(start).resolve()
    candidates = (*anchor.parents,)
    for candidate in (anchor, *candidates, Path(__file__).resolve().parents[3]):
        manifest = candidate / "pyproject.toml"
        if manifest.is_file():
            with manifest.open("rb") as handle:
                if tomllib.load(handle).get("project", {}).get("name") == "managerai":
                    return candidate
    raise ValueError("Execute o experimento dentro de um checkout ManagerAI com pyproject.toml.")


def execution_code_hashes() -> dict[str, str]:
    """Hash dos módulos carregados do src ou wheel, com chaves estáveis."""
    package = Path(__file__).resolve().parents[1]
    return {"src/managerai/" + p.relative_to(package).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in sorted(package.rglob("*.py"))}
