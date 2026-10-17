"""Prévia de calendário e política de apresentação, sem alterar o relatório V1/V2.

Presença de arquivo não certifica conteúdo válido. A seleção é a mesma usada
pelo pipeline: últimas N partidas do calendário, sem compensar ausências.
"""
from __future__ import annotations

from dataclasses import dataclass

from .data_inventory import Season, load_season, team_ids
from .data_loader import LocalData
from .feature_engineering import MIN_SAMPLE
from .report_schema import AnalysisReport, AnalysisRequest, TeamProfile
from .temporal import select_history


CORE_METRICS = ("xg_for", "xg_against", "shots_for", "shots_against",
                "pass_accuracy", "final_third_entries")
WINDOW_POLICY = (
    "A janela considera até N partidas anteriores disponíveis no calendário desta temporada. "
    "Não inclui jogos do dia do corte ou posteriores, não amplia a janela para compensar "
    "arquivos ausentes e não junta temporadas. A qualidade dos eventos só é conhecida após a análise."
)


def _matches(count: int) -> str:
    return f"{count} jogo" if count == 1 else f"{count} jogos"


@dataclass(frozen=True)
class TeamCoverage:
    team_id: int
    team_name: str
    calendar_matches_before_cutoff: int
    selected_match_ids: tuple[int, ...]
    selected_match_dates: tuple[str, ...]
    event_match_ids: tuple[int, ...]
    missing_event_match_ids: tuple[int, ...]
    available_period_start: str | None
    available_period_end: str | None
    selected_period_start: str | None
    selected_period_end: str | None
    event_period_start: str | None
    event_period_end: str | None
    warnings: tuple[str, ...]

    @property
    def selected_matches(self) -> int:
        return len(self.selected_match_ids)

    @property
    def matches_with_events(self) -> int:
        return len(self.event_match_ids)


@dataclass(frozen=True)
class CoveragePreview:
    team: TeamCoverage
    opponent: TeamCoverage
    cutoff: str
    requested_window: int
    minimum_matches: int
    policy: str = WINDOW_POLICY

    @property
    def warnings(self) -> tuple[str, ...]:
        return self.team.warnings + self.opponent.warnings


def _validate_minimum(minimum_matches: int) -> None:
    if type(minimum_matches) is not int or minimum_matches < 1:
        raise ValueError("Mínimo de jogos deve ser inteiro positivo.")


def preview_coverage(data: LocalData, request: AnalysisRequest, season: Season | None = None,
                     minimum_matches: int = MIN_SAMPLE) -> CoveragePreview:
    """Lê somente catálogo/calendário; verifica eventos com is_file, sem abri-los."""
    _validate_minimum(minimum_matches)
    season = season or load_season(data, request.competition_id, request.season_id)
    histories, cutoff = select_history(season, request)

    def coverage(tid: int) -> TeamCoverage:
        # Same conservative date policy as select_history (whole cutoff day excluded).
        prior = sorted((m for m in season.matches if tid in team_ids(m)
                        and m["match_date"] < cutoff[:10]
                        and m["match_id"] != request.target_match_id),
                       key=lambda m: (m["match_date"], m.get("kick_off") or "", m["match_id"]))
        selected = histories[tid]
        mids = tuple(m["match_id"] for m in selected)
        available = tuple(mid for mid in mids if data.exists("events", mid))
        missing = tuple(mid for mid in mids if mid not in available)
        name = season.teams[tid]
        warnings = []
        if len(available) < minimum_matches:
            count_text = ("apenas 1 jogo anterior" if len(available) == 1
                          else f"apenas {len(available)} jogos anteriores")
            warnings.append(
                f"{name}: {count_text} com arquivo de eventos "
                "na janela; comparação não confiável. A exploração descritiva continua disponível."
            )
        if missing:
            warnings.append(
                f"{name}: {_matches(len(missing))} do calendário na janela sem arquivo de eventos; "
                "a janela não será ampliada."
            )
        return TeamCoverage(tid, name, len(prior), mids,
                            tuple(m["match_date"] for m in selected), available, missing,
                            prior[0]["match_date"] if prior else None,
                            prior[-1]["match_date"] if prior else None,
                            selected[0]["match_date"] if selected else None,
                            selected[-1]["match_date"] if selected else None,
                            next((m["match_date"] for m in selected if m["match_id"] in available), None),
                            next((m["match_date"] for m in reversed(selected) if m["match_id"] in available), None),
                            tuple(warnings))

    return CoveragePreview(coverage(request.team_id), coverage(request.opponent_id), cutoff,
                           request.recent_matches_window, minimum_matches)


@dataclass(frozen=True)
class CoreMetricCoverage:
    team_name: str
    sample_sizes: dict[str, int]
    minimum_sample_size: int
    insufficient_metrics: tuple[str, ...]


@dataclass(frozen=True)
class ComparisonSufficiency:
    status: str
    sufficient: bool
    team: CoreMetricCoverage
    opponent: CoreMetricCoverage
    minimum_matches: int
    warnings: tuple[str, ...]


def report_sufficiency(report: AnalysisReport, minimum_matches: int = MIN_SAMPLE,
                       core_metrics: tuple[str, ...] = CORE_METRICS) -> ComparisonSufficiency:
    """Suficiência central por métrica, nunca inferida só do total de partidas.

    Cinco jogos é um mínimo operacional, não significância estatística nem
    confiança calibrada. Métrica ausente/nula conta como não calculável.
    """
    _validate_minimum(minimum_matches)
    if not core_metrics:
        raise ValueError("Informe pelo menos uma métrica central.")

    def evaluate(profile: TeamProfile) -> CoreMetricCoverage:
        sizes = {key: (profile.metrics[key].sample_size
                       if key in profile.metrics and profile.metrics[key].value is not None else 0)
                 for key in core_metrics}
        return CoreMetricCoverage(profile.team_name, sizes, min(sizes.values()),
                                  tuple(key for key, n in sizes.items() if n < minimum_matches))

    own, other = evaluate(report.team_profile), evaluate(report.opponent_profile)
    sufficient = not own.insufficient_metrics and not other.insufficient_metrics
    warnings = tuple(
        f"{p.team_name}: métricas centrais calculáveis em pelo menos {_matches(p.minimum_sample_size)}; "
        f"mínimo operacional de {_matches(minimum_matches)}. Amostra insuficiente para conclusões comparativas."
        for p in (own, other) if p.insufficient_metrics
    )
    if not sufficient:
        warnings += ("Indicadores observados para consulta descritiva; não interpretar diferenças como superioridade.",)
    return ComparisonSufficiency("evidência limitada" if sufficient else "amostra insuficiente",
                                 sufficient, own, other, minimum_matches, warnings)
