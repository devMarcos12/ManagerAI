"""Contratos serializáveis; ausência de evidência é None, nunca NaN."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
import json
import math
from typing import Any, Literal


@dataclass(frozen=True)
class AnalysisRequest:
    competition_id: int
    season_id: int
    team_id: int
    opponent_id: int
    cutoff_date: str | None = None
    target_match_id: int | None = None
    recent_matches_window: int = 10
    venue: str = "desconhecido"
    match_context: str = "regular"
    strategic_objective: str = "equilibrado"
    unavailable_player_ids: tuple[int, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        ids = (self.competition_id, self.season_id, self.team_id, self.opponent_id)
        if any(type(x) is not int or x <= 0 for x in ids):
            raise ValueError("IDs devem ser inteiros positivos.")
        if self.team_id == self.opponent_id:
            raise ValueError("Equipe e adversário precisam ser diferentes.")
        if (self.cutoff_date is None) == (self.target_match_id is None):
            raise ValueError("Informe exatamente cutoff_date ou target_match_id.")
        if self.cutoff_date is not None:
            parsed = date.fromisoformat(self.cutoff_date)
            if parsed.isoformat() != self.cutoff_date:
                raise ValueError("cutoff_date deve ter formato AAAA-MM-DD.")
        if self.target_match_id is not None and (type(self.target_match_id) is not int or self.target_match_id <= 0):
            raise ValueError("target_match_id deve ser inteiro positivo.")
        if type(self.recent_matches_window) is not int or not 1 <= self.recent_matches_window <= 100:
            raise ValueError("Janela deve estar entre 1 e 100 partidas.")
        if self.venue not in {"casa", "fora", "neutro", "desconhecido"}:
            raise ValueError("venue inválido.")
        if self.match_context not in {"regular", "clássico", "eliminatório", "decisivo", "outro"}:
            raise ValueError("match_context inválido.")
        if self.strategic_objective not in {"equilibrado", "pressionar alto", "proteger vantagem", "buscar gol", "outro"}:
            raise ValueError("strategic_objective inválido.")
        if any(type(x) is not int or x <= 0 for x in self.unavailable_player_ids):
            raise ValueError("Jogadores indisponíveis devem ter IDs inteiros positivos.")
        if not isinstance(self.notes, str) or len(self.notes) > 4000:
            raise ValueError("notes deve ser texto com até 4000 caracteres.")


@dataclass(frozen=True)
class MetricEvidence:
    metric_id: str
    value: float | None
    unit: str
    sample_size: int
    match_ids: list[int]
    numerator: float | None = None
    denominator: float | None = None
    median: float | None = None
    standard_deviation: float | None = None
    per_match: list[dict[str, Any]] = field(default_factory=list)
    formula_version: str = "1.0.0"


@dataclass
class TeamProfile:
    team_id: int
    team_name: str
    match_ids: list[int]
    period_start: str | None
    period_end: str | None
    sample_status: Literal["insuficiente", "limitada"]
    metrics: dict[str, MetricEvidence]
    quality: dict[str, int]


@dataclass(frozen=True)
class TacticalHypothesis:
    rule_id: str
    recommendation: str
    condition: str
    evidence_metrics: list[str]
    limitations: list[str]
    risks: list[str]
    preconditions: list[str]
    confidence_level: str = "limitada"


@dataclass
class AnalysisReport:
    metadata: dict[str, Any]
    request: AnalysisRequest
    team_profile: TeamProfile
    opponent_profile: TeamProfile
    comparison: list[dict[str, Any]]
    key_findings: list[dict[str, Any]]
    tactical_hypotheses: list[TacticalHypothesis]
    formation_options: list[dict[str, Any]]
    lineup_options: list[dict[str, Any]]
    data_gaps: list[str]
    methodology: dict[str, Any]
    schema_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        # Reject non-finite values even when called outside the CLI.
        json.dumps(result, allow_nan=False, ensure_ascii=False)
        for profile in (self.team_profile, self.opponent_profile):
            for metric in profile.metrics.values():
                if metric.value is not None and not math.isfinite(metric.value):
                    raise ValueError("Métrica não finita.")
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
