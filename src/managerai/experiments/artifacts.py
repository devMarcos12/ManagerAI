"""Destinos de pesquisa novos; nunca gravar em dados, fixtures ou EDA."""
from pathlib import Path
from .paths import project_root


def new_run_dir(destination, *, data_root=None):
    out = Path(destination).resolve()
    checkout = project_root()
    allowed = (checkout/"outputs/runs").resolve()
    if out.exists() or (out.is_relative_to(checkout) and not out.is_relative_to(allowed)):
        raise ValueError("Use diretório novo em outputs/runs ou temporário externo ao checkout.")
    if data_root is not None:
        data = Path(data_root).resolve()
        if out == data or out.is_relative_to(data) or out.is_relative_to(data.parent):
            raise ValueError("Destino dentro do clone de dados é proibido.")
    out.mkdir(parents=True)
    return out
