"""Adaptador de metadados da interface; nenhum cálculo analítico é duplicado."""
from pathlib import Path

from .data_inventory import Season, team_ids
from .data_loader import DataError, LocalData
from .pipeline import analyze
from .presentation.terminology import date_label
from .report_schema import AnalysisReport, AnalysisRequest


def available_catalog(root: str | Path) -> list[dict]:
    data = LocalData(root)
    catalog = data.read("competitions.json")
    return [c for c in catalog if (data.root / "matches" / str(c["competition_id"]) / f"{c['season_id']}.json").is_file()]


def match_options(season: Season, team_id: int, opponent_id: int) -> list[dict]:
    if team_id == opponent_id:
        return []
    result = []
    for match in sorted(season.matches, key=lambda m: (m["match_date"], m["match_id"]), reverse=True):
        h, a = team_ids(match)
        if {h, a} == {team_id, opponent_id}:
            # Intentionally copy only schedule fields; never expose final score.
            result.append({"match_id": match["match_id"], "date": match["match_date"],
                           "home_team_id": h,
                           "label": f"{date_label(match['match_date'])} — {season.teams[h]} × {season.teams[a]}",
                           "formal_venue": "casa" if h == team_id else "fora"})
    return result


def run_analysis(root: str | Path, request: AnalysisRequest) -> AnalysisReport:
    return analyze(root, request)


def friendly_error(error: Exception) -> str:
    if isinstance(error, DataError) and "Não foi possível ler" in str(error):
        return "Não foi possível carregar os dados locais. Confira a instalação do dataset e a configuração da pasta de dados."
    if isinstance(error, (ValueError, DataError)):
        return "Não foi possível analisar o confronto. " + str(error)
    if isinstance(error, OSError):
        return "Não foi possível acessar os arquivos locais. Confira a pasta de dados e as permissões de leitura."
    return "Os dados locais não têm a estrutura esperada. Confira o catálogo e a integridade dos arquivos antes de tentar novamente."
