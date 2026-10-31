"""Contratos HTTP tipados; projeção de apresentação sem recalcular métricas."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .options import Venue, MatchContext, Objective, Strategy, PlanId, ExplanationMode, Availability
from .service_schema import ServiceRequest


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class AnalysisPayload(StrictModel):
    competition_id: int = Field(gt=0)
    season_id: int = Field(gt=0)
    team_id: int = Field(gt=0)
    opponent_id: int = Field(gt=0)
    cutoff_date: str | None = None
    target_match_id: int | None = Field(default=None, gt=0)
    recent_matches_window: int = Field(default=10, ge=1, le=20)
    venue: Venue = "desconhecido"
    match_context: MatchContext = "regular"
    strategic_objective: Objective = "equilibrado"
    unavailable_player_ids: list[int] = Field(default_factory=list, max_length=60)
    notes: str = Field(default="", max_length=4000)


class RosterPayload(StrictModel):
    player_id: int = Field(gt=0)
    team_id: int = Field(gt=0)
    positions: list[str] = Field(min_length=1, max_length=5)
    availability: Availability
    source: str = Field(min_length=1, max_length=200)
    observed_on: str


class AnalysisBody(StrictModel):
    schema_version: Literal["2.0.0"] = "2.0.0"
    analysis: AnalysisPayload
    include_v3: bool = False
    intended_strategy: Strategy = "equilibrada"
    blocked_plan_ids: list[PlanId] = Field(default_factory=list, max_length=5)
    roster: list[RosterPayload] = Field(default_factory=list, max_length=60)
    explanation: ExplanationMode = "none"
    engine: Literal["deterministic"] = "deterministic"
    explainer_model: str | None = Field(default=None, min_length=1, max_length=160)

    @model_validator(mode="before")
    @classmethod
    def preserve_service_errors(cls, value):
        # Manter códigos INVALID_ROSTER/INVALID_RESTRICTIONS/ENGINE_UNAVAILABLE.
        if isinstance(value, dict):
            ServiceRequest.from_dict(value)
        return value


class ErrorBody(BaseModel):
    code: str
    message: str


class HealthBody(BaseModel):
    status: Literal["ok"]
    service_version: str
    data_present: bool


class LLMCapability(BaseModel):
    configured: bool
    provider: str | None
    model: str | None
    mode: Literal["validated_claim_selection"]
    availability: Literal["checked_on_generation"]


class LimitsBody(BaseModel):
    request_bytes: int
    window: int
    concurrent_analyses: int
    analyses_per_minute: int
    report_bytes: int
    retained_reports: int
    report_ttl_seconds: int


class CapabilitiesBody(BaseModel):
    schema_version: str
    engines: list[Literal["deterministic"]]
    llm: LLMCapability
    fine_tuned_model: Literal["experimental_not_promoted"]
    shots_prediction: Literal["experimental_not_integrated"]
    individual_recommendations: Literal[False]
    v3_recuts: list[tuple[int, int]]
    limits: LimitsBody
    storage: str


class CatalogBody(BaseModel):
    model_config = ConfigDict(extra="allow")
    competition_id: int
    season_id: int
    competition_name: str
    season_name: str
    country_name: str | None = None
    v3_certified: bool


class TeamBody(BaseModel):
    team_id: int
    name: str


class MatchBody(BaseModel):
    match_id: int
    date: str
    home_team_id: int
    away_team_id: int


class TeamCoverageBody(BaseModel):
    team_id: int
    team_name: str
    calendar_matches_before_cutoff: int
    selected_match_ids: list[int]
    selected_match_dates: list[str]
    event_match_ids: list[int]
    missing_event_match_ids: list[int]
    available_period_start: str | None
    available_period_end: str | None
    selected_period_start: str | None
    selected_period_end: str | None
    event_period_start: str | None
    event_period_end: str | None
    warnings: list[str]


class CoverageBody(BaseModel):
    team: TeamCoverageBody
    opponent: TeamCoverageBody
    cutoff: str
    requested_window: int
    minimum_matches: int
    policy: str


class PerMatchBody(BaseModel):
    model_config = ConfigDict(extra="allow")
    match_id: int
    match_date: str
    value: float | None
    numerator: float | None
    denominator: float | None


class MetricBody(BaseModel):
    metric_id: str
    value: float | None
    unit: str
    sample_size: int
    match_ids: list[int]
    numerator: float | None
    denominator: float | None
    median: float | None
    standard_deviation: float | None
    per_match: list[PerMatchBody]
    formula_version: str


class EvidenceBody(MetricBody):
    team_id: int
    team_name: str


class MetricCoverageBody(BaseModel):
    team_name: str
    sample_sizes: dict[str, int]
    minimum_sample_size: int
    insufficient_metrics: list[str]


class SufficiencyBody(BaseModel):
    status: str
    sufficient: bool
    team: MetricCoverageBody
    opponent: MetricCoverageBody
    minimum_matches: int
    warnings: list[str]


class PlanBody(BaseModel):
    plan_id: PlanId
    observation: str
    evidence_ids: list[str]
    condition: str
    possible_action: str
    risks: list[str]
    restrictions: list[PlanId]
    limitations: list[str]
    preconditions: list[str]
    abstention_reason: str | None
    context_priority: int


class ComparisonBody(BaseModel):
    plans: list[PlanId]
    different_evidence_ids: list[str]
    interpretation: str
    context_priority_tied: bool


class ExcludedPlanBody(BaseModel):
    plan_id: PlanId
    reason: str


class OrderingBody(BaseModel):
    version: str
    meaning: str
    ties: str
    rule: str
    objective_note: str | None


class RosterPolicyBody(BaseModel):
    status: Literal["declared", "missing"]
    provenance: str
    individual_suggestions: Literal["abstained"]
    reason: str


class ModelStatusBody(BaseModel):
    tactical: Literal["deterministic"]
    shots_predictor: Literal["experimental_not_integrated"]
    fine_tuned_explainer: Literal["experimental_not_promoted"]


class ClaimBody(BaseModel):
    id: str
    text: str
    evidence_ids: list[str]
    plan_id: PlanId | None = None


class ExplanationBody(BaseModel):
    status: Literal["disabled", "unavailable", "failed", "generated"]
    reason: str | None
    provider: str | None
    model: str | None
    prompt_version: str
    input_fingerprint: str
    claims: list[ClaimBody]
    policy: str
    duration_seconds: float | None = None
    model_digest: str | None = None


class ShotBody(BaseModel):
    id: str | None
    match_id: int
    team_id: int
    period: int
    x: float
    y: float
    xg: float | None


class DisplayProfile(BaseModel):
    team_id: int
    team_name: str
    period_start: str | None
    period_end: str | None
    match_ids: list[int]
    shots: list[ShotBody]


class SourceBody(BaseModel):
    path: str
    sha256: str


class DisplayBody(BaseModel):
    competition: str
    season: str
    cutoff_date: str
    team: DisplayProfile
    opponent: DisplayProfile
    sources: list[SourceBody]
    metric_definitions: dict[str, str]


class ReportBody(BaseModel):
    schema_version: str
    report_id: str
    request: AnalysisBody
    legacy_report: dict[str, Any]  # Compatibilidade; frontend usa display/evidence.
    display: DisplayBody
    evidence: dict[str, EvidenceBody]
    sufficiency: SufficiencyBody
    plans: list[PlanBody]
    excluded_plans: list[ExcludedPlanBody]
    plan_comparisons: list[ComparisonBody]
    abstention_reason: str | None
    ordering: OrderingBody
    roster_policy: RosterPolicyBody
    model_status: ModelStatusBody
    explanation: ExplanationBody
    limitations: list[str]
    provenance: dict[str, Any]  # Contrato V4.1 preservado; sem consumidor visual opaco.
    report_key: str


def display_projection(result):
    from .presentation.terminology import TERMS
    legacy = result["legacy_report"]
    v3 = legacy.get("tactical_v3", {})
    definitions = {key: term.title for key, term in TERMS.items()}
    if v3:
        definitions.update({key: value["label"] for key, value in v3["metric_definitions"].items()})
    sources = {s["path"]: s["sha256"] for s in legacy["methodology"]["sources"]}
    sources.update({s["path"]: s["sha256"] for s in v3.get("methodology", {}).get("sources", [])})
    def profile(side):
        original = legacy[side]
        return {key: original[key] for key in ("team_id", "team_name", "period_start", "period_end", "match_ids")} | {
            "shots": v3.get(side, {}).get("shots", [])}
    return {"competition": legacy["metadata"]["competition"], "season": legacy["metadata"]["season"],
            "cutoff_date": legacy["metadata"]["cutoff_date"], "team": profile("team_profile"),
            "opponent": profile("opponent_profile"), "sources": [{"path":p,"sha256":h} for p,h in sorted(sources.items())],
            "metric_definitions": definitions}
