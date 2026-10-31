"""Contrato de serviço 2.0.0; não modifica os contratos de relatório legados."""
from dataclasses import asdict, dataclass, field, fields
from datetime import date
from typing import Any

from .report_schema import AnalysisRequest
from .options import PLAN_IDS, STRATEGIES

SERVICE_VERSION = "2.0.0"


class ServiceError(ValueError):
    def __init__(self, code: str, message: str, status: int = 422):
        super().__init__(message)
        self.code, self.status = code, status


def exact_keys(value, allowed):
    if not isinstance(value, dict) or set(value) - set(allowed):
        raise ServiceError("INVALID_REQUEST", "Objeto inválido ou campos desconhecidos.")


@dataclass(frozen=True)
class RosterEntry:
    player_id: int
    team_id: int
    positions: tuple[str, ...]
    availability: str
    source: str
    observed_on: str

    def __post_init__(self):
        if any(type(x) is not int or x <= 0 for x in (self.player_id, self.team_id)):
            raise ServiceError("INVALID_ROSTER", "IDs do elenco devem ser positivos.")
        if (not isinstance(self.positions, (tuple, list)) or not 1 <= len(self.positions) <= 5
                or any(not isinstance(p, str) or not 1 <= len(p) <= 80 for p in self.positions)):
            raise ServiceError("INVALID_ROSTER", "Informe de uma a cinco posições por atleta.")
        if self.availability not in ("available", "unavailable", "unknown"):
            raise ServiceError("INVALID_ROSTER", "Disponibilidade inválida.")
        if not isinstance(self.source, str) or not self.source.strip() or len(self.source) > 200:
            raise ServiceError("INVALID_ROSTER", "Fonte do elenco obrigatória, até 200 caracteres.")
        try:
            if date.fromisoformat(self.observed_on).isoformat() != self.observed_on:
                raise ValueError()
        except (TypeError, ValueError):
            raise ServiceError("INVALID_ROSTER", "Referência do elenco deve ser uma data ISO.") from None


@dataclass(frozen=True)
class ServiceRequest:
    analysis: AnalysisRequest
    schema_version: str = SERVICE_VERSION
    include_v3: bool = False
    intended_strategy: str = "equilibrada"
    blocked_plan_ids: tuple[str, ...] = ()
    roster: tuple[RosterEntry, ...] = ()
    explanation: str = "none"
    engine: str = "deterministic"
    explainer_model: str | None = None

    def __post_init__(self):
        if self.schema_version != SERVICE_VERSION or type(self.include_v3) is not bool:
            raise ServiceError("INVALID_REQUEST", "Versão ou opção V3 inválida.")
        if self.engine != "deterministic":
            raise ServiceError("ENGINE_UNAVAILABLE", "Motor solicitado indisponível.", 503)
        if self.explainer_model is not None and (not isinstance(self.explainer_model, str)
                                               or not 1 <= len(self.explainer_model) <= 160):
            raise ServiceError("INVALID_REQUEST", "Identidade de explicador inválida.")
        if self.explainer_model is not None and self.explanation == "none":
            raise ServiceError("INVALID_REQUEST", "Modelo solicitado requer explicação habilitada.")
        if self.intended_strategy not in STRATEGIES or self.explanation not in ("none", "optional", "required"):
            raise ServiceError("INVALID_REQUEST", "Estratégia ou modo de explicação inválido.")
        if (not isinstance(self.blocked_plan_ids, (list, tuple))
                or any(not isinstance(x, str) or x not in PLAN_IDS for x in self.blocked_plan_ids)
                or len(set(self.blocked_plan_ids)) != len(self.blocked_plan_ids)):
            raise ServiceError("INVALID_RESTRICTIONS", "Restrição deve identificar um plano conhecido, sem duplicatas.")
        if len(self.roster) > 60 or len({p.player_id for p in self.roster}) != len(self.roster):
            raise ServiceError("INVALID_ROSTER", "Elenco duplicado ou maior que 60 atletas.")
        if any(p.team_id != self.analysis.team_id for p in self.roster):
            raise ServiceError("INVALID_ROSTER", "Elenco deve pertencer à equipe informada.")
        if self.analysis.unavailable_player_ids:
            roster = {p.player_id: p for p in self.roster}
            if any(pid not in roster or roster[pid].availability != "unavailable"
                   for pid in self.analysis.unavailable_player_ids):
                raise ServiceError("INVALID_ROSTER", "Indisponíveis precisam de fonte e referência no elenco declarado.")

    @classmethod
    def from_dict(cls, value: dict[str, Any]):
        exact_keys(value, [f.name for f in fields(cls)])
        if "analysis" not in value:
            raise ServiceError("INVALID_REQUEST", "Campo analysis obrigatório.")
        raw = value["analysis"]
        exact_keys(raw, [f.name for f in fields(AnalysisRequest)])
        try:
            # Core também valida IDs/datas; verificar tipos de campos textuais e arrays antes.
            for key in ("venue", "match_context", "strategic_objective", "notes", "cutoff_date"):
                if key in raw and raw[key] is not None and not isinstance(raw[key], str):
                    raise ValueError("Campo textual inválido.")
            if "unavailable_player_ids" in raw and not isinstance(raw["unavailable_player_ids"], (list, tuple)):
                raise ValueError("Lista de indisponíveis inválida.")
            analysis = AnalysisRequest(**{**raw, "unavailable_player_ids": tuple(raw.get("unavailable_player_ids", ()))})
            roster = value.get("roster", [])
            if not isinstance(roster, list) or len(roster) > 60:
                raise ValueError("Elenco inválido.")
            parsed = []
            for p in roster:
                exact_keys(p, [f.name for f in fields(RosterEntry)])
                parsed.append(RosterEntry(**p))
            return cls(**{**value, "analysis": analysis, "roster": tuple(parsed)})
        except ServiceError:
            raise
        except (ValueError, TypeError, KeyError):
            raise ServiceError("INVALID_REQUEST", "Campos obrigatórios ausentes ou valores inválidos.") from None

    def to_dict(self):
        return asdict(self)
