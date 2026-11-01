"""Entrada por equipe e panorama descritivo; não fabrica um adversário."""
from dataclasses import asdict, dataclass
from datetime import date
import json

from .coverage import WINDOW_POLICY, team_coverage
from .data_inventory import load_season, team_ids
from .data_loader import DataError, LocalData
from .feature_engineering import FORMULA_VERSION, MIN_SAMPLE, build_profiles
from .presentation.terminology import TERMS
from .sufficiency import CORE_METRICS
from .temporal import history_before
from .ui_support import available_catalog


@dataclass(frozen=True)
class TeamRequest:
    competition_id: int
    season_id: int
    team_id: int
    cutoff_date: str
    recent_matches_window: int = 10

    def __post_init__(self):
        if any(type(v) is not int or v <= 0 for v in (self.competition_id, self.season_id, self.team_id)):
            raise ValueError("IDs devem ser inteiros positivos.")
        if not isinstance(self.cutoff_date, str) or date.fromisoformat(self.cutoff_date).isoformat() != self.cutoff_date:
            raise ValueError("Informe uma data AAAA-MM-DD válida.")
        if type(self.recent_matches_window) is not int or not 1 <= self.recent_matches_window <= 20:
            raise ValueError("Informe de 1 a 20 jogos.")


def coach_catalog(root):
    """Índice global obtido só de catálogo/calendários e presença de arquivos."""
    data = LocalData(root)
    clubs, warnings, seen = {}, [], set()
    for entry in available_catalog(root):
        pair = entry["competition_id"], entry["season_id"]
        if pair in seen:
            raise DataError("Competição/temporada duplicada no catálogo.")
        seen.add(pair)
        try:
            season = load_season(data, *pair)
        except DataError:
            warnings.append(f"Calendário indisponível ou inválido: {entry['competition_name']} · {entry['season_name']}.")
            continue
        for tid, name in season.teams.items():
            matches = [m for m in season.matches if tid in team_ids(m)]
            dates = sorted(m["match_date"] for m in matches)
            club = clubs.setdefault(tid, {"team_id": tid, "name": name, "aliases": [], "recuts": []})
            if name not in club["aliases"]:
                club["aliases"].append(name)
            club["recuts"].append({
                "competition_id": pair[0], "season_id": pair[1],
                "competition_name": season.competition, "season_name": season.season,
                "competition_gender": entry.get("competition_gender"),
                "first_date": dates[0], "last_date": dates[-1], "calendar_matches": len(matches),
                "event_matches": sum(data.exists("events", m["match_id"]) for m in matches),
            })
    for club in clubs.values():
        club["recuts"].sort(key=lambda c: (c["last_date"], c["competition_id"], c["season_id"]), reverse=True)
    return {"teams": sorted(clubs.values(), key=lambda c: (c["name"].casefold(), c["team_id"])), "warnings": warnings}


def _selection(root, request):
    data = LocalData(root)
    season = load_season(data, request.competition_id, request.season_id)
    history = history_before(season, request.team_id, request.cutoff_date, request.recent_matches_window)
    return data, season, history


def team_preview(root, request):
    data, season, history = _selection(root, request)
    return {"team": asdict(team_coverage(data, season, request.team_id, history, request.cutoff_date)),
            "cutoff": request.cutoff_date, "requested_window": request.recent_matches_window,
            "minimum_matches": MIN_SAMPLE, "policy": WINDOW_POLICY}


def analyze_team(root, request):
    data, season, history = _selection(root, request)
    preview = asdict(team_coverage(data, season, request.team_id, history, request.cutoff_date))
    profiles, gaps = build_profiles(data, {request.team_id: history}, season.teams)
    profile = profiles[request.team_id]
    insufficient = [key for key in CORE_METRICS
                    if profile.metrics[key].value is None or profile.metrics[key].sample_size < MIN_SAMPLE]
    for key, metric in profile.metrics.items():
        if metric.sample_size < len(profile.match_ids):
            gaps.append(f"{TERMS[key].title}: calculável em {metric.sample_size}/{len(profile.match_ids)} jogos.")
    for key, count in sorted(profile.quality.items()):
        if count:
            gaps.append(f"Checagem de conteúdo: {key}={count}.")
    result = {
        "schema_version": "team-overview-1", "request": asdict(request),
        "competition": season.competition, "season": season.season,
        "profile": asdict(profile), "coverage": preview,
        "metric_definitions": {key: asdict(term) for key, term in TERMS.items()},
        "sample_status": "amostra insuficiente" if insufficient else "evidência limitada",
        "insufficient_metrics": insufficient, "minimum_matches": MIN_SAMPLE,
        "warnings": sorted(set(gaps + list(preview["warnings"]))),
        "limitations": [
            "Panorama individual descritivo, sem comparação, plano tático ou sugestão de escalação.",
            "Cinco jogos é um mínimo operacional; não representa confiança estatística ou eficácia esportiva.",
            "Gols esperados descrevem a qualidade das finalizações; não são gols reais nem probabilidade de vitória.",
            "Pressão e recuperações registradas não comprovam sucesso dessas ações.",
            "Indicadores usam as fórmulas básicas, sem os filtros opt-in de qualidade por família. Presença no catálogo não certifica a temporada ou a orientação espacial.",
            "O histórico disponível não comprova elenco, calendário ou condição atual da equipe.",
        ],
        "methodology": {"formula_version": FORMULA_VERSION, "temporal_policy": WINDOW_POLICY,
                        "data_policy": "legacy", "data_fingerprint": data.fingerprint(),
                        "sources": [{"path": p, "sha256": h} for p, h in sorted(data.sources.items())],
                        "attribution": "StatsBomb Open Data"},
    }
    json.dumps(result, allow_nan=False)
    return result
