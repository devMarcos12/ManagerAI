"""Contratos V4.1 separados dos schemas legados; snapshots JSON imutáveis."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields
from datetime import date
from hashlib import sha256
import json
import math
from pathlib import PurePosixPath
from types import MappingProxyType, SimpleNamespace
from typing import Literal

from .coverage import ComparisonSufficiency, report_sufficiency
from .report_schema import AnalysisRequest, MetricEvidence, TeamProfile

type JSONValue = None | bool | int | float | str | tuple[JSONValue, ...] | Mapping[str, JSONValue]
CONTRACT_VERSION = "4.1.0"


def freeze(value):
    """Copia valores JSON sem compartilhar listas/dicionários com o relatório."""
    if isinstance(value, Mapping):
        if any(not isinstance(k, str) for k in value):
            raise ValueError("Chaves JSON devem ser strings.")
        return MappingProxyType({k: freeze(v) for k, v in value.items()})
    if isinstance(value, (tuple, list)):
        return tuple(freeze(v) for v in value)
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    raise ValueError("Esperado valor JSON finito.")


def thaw(value):
    """Devolve cópia JSON mutável; nenhuma alteração alcança o snapshot."""
    if isinstance(value, Mapping):
        return {k: thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [thaw(v) for v in value]
    return value


def fingerprint(value) -> str:
    raw = json.dumps(thaw(value), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(raw.encode()).hexdigest()


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: texto obrigatório.")


def _digest(value):
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("Esperado SHA-256 hexadecimal.")


def _ids(values):
    if not isinstance(values, tuple) or any(type(v) is not int or v <= 0 for v in values) or len(set(values)) != len(values):
        raise ValueError("IDs de partidas devem ser inteiros positivos únicos.")


@dataclass(frozen=True)
class TacticalEngineInput:
    """Perfis calculados, contexto declarado e fontes; sem labels/hipóteses baseline.

    profiles reutiliza os campos MetricEvidence existentes, com acesso somente de
    leitura. Não contém eventos brutos, placar do alvo, roster ou pesos de modelos.
    A validação temporal confere o relatório recebido, não audita o fornecedor.
    """

    request: AnalysisRequest
    cutoff_date: str
    profiles: Mapping[str, JSONValue]
    provenance: Mapping[str, JSONValue]
    data_gaps: tuple[str, ...]

    def __post_init__(self):
        try:
            self._initialize()
        except (KeyError, TypeError, AttributeError) as exc:
            raise ValueError("Estrutura de entrada incompleta ou inválida.") from exc

    def _initialize(self):
        if not isinstance(self.request, AnalysisRequest):
            raise ValueError("Esperado AnalysisRequest.")
        # AnalysisRequest é frozen, mas rejeitar listas mutáveis passadas em runtime.
        if not isinstance(self.request.unavailable_player_ids, tuple):
            raise ValueError("unavailable_player_ids deve ser tuple.")
        object.__setattr__(self, "profiles", freeze(self.profiles))
        object.__setattr__(self, "provenance", freeze(self.provenance))
        if not isinstance(self.data_gaps, (tuple, list)):
            raise ValueError("Lacunas devem ser sequência de textos.")
        object.__setattr__(self, "data_gaps", tuple(self.data_gaps))
        if any(not isinstance(x, str) for x in self.data_gaps):
            raise ValueError("Lacunas devem ser textos.")
        cutoff = date.fromisoformat(self.cutoff_date)
        if cutoff.isoformat() != self.cutoff_date or (self.request.cutoff_date and self.request.cutoff_date != self.cutoff_date):
            raise ValueError("Corte incompatível com a requisição.")
        if not isinstance(self.profiles, Mapping) or not isinstance(self.provenance, Mapping):
            raise ValueError("Perfis e proveniência devem ser objetos.")
        if set(self.profiles) not in ({"team_profile", "opponent_profile"}, {"team_profile", "opponent_profile", "tactical_v3"}):
            raise ValueError("Perfis incompatíveis com os contratos suportados.")
        for side, tid in (("team_profile", self.request.team_id), ("opponent_profile", self.request.opponent_id)):
            if set(self.profiles[side]) != {f.name for f in fields(TeamProfile)}:
                raise ValueError("Estrutura TeamProfile inválida.")
            if self.profiles[side]["sample_status"] not in ("insuficiente", "limitada"):
                raise ValueError("Estado da amostra inválido.")
            self._validate_profile(self.profiles[side], tid, cutoff)
            if "tactical_v3" in self.profiles:
                extra = self.profiles["tactical_v3"][side]
                self._validate_profile(extra, tid, cutoff)
                if extra["match_ids"] != self.profiles[side]["match_ids"]:
                    raise ValueError("Cobertura V3 diverge do perfil legado.")
        sources = self.provenance["sources"]
        source_map = {}
        observed_ids = set(self.profiles["team_profile"]["match_ids"]) | set(self.profiles["opponent_profile"]["match_ids"])
        for source in sources:
            path, digest = source["path"], source["sha256"]
            _text(path, "Fonte")
            parsed = PurePosixPath(path)
            if not parsed.parts or parsed.is_absolute() or path != parsed.as_posix() or ".." in parsed.parts or "\\" in path or path in source_map:
                raise ValueError("Fonte relativa inválida ou duplicada.")
            _digest(digest)
            if parsed.parts[0] == "events" and (len(parsed.parts) != 2 or parsed.suffix != ".json"
                    or not parsed.stem.isdecimal() or int(parsed.stem) not in observed_ids):
                raise ValueError("Fonte de eventos fora das partidas históricas analisadas.")
            if self.request.target_match_id is not None and path in (
                f"events/{self.request.target_match_id}.json", f"lineups/{self.request.target_match_id}.json"
            ):
                raise ValueError("Fonte inclui eventos/escalação do alvo.")
            source_map[path] = digest
        if not sources or fingerprint(source_map) != self.provenance["data_fingerprint"]:
            raise ValueError("Fingerprint das fontes inconsistente.")
        if "tactical_v3" in self.profiles:
            v3_sources = self.provenance["v3_sources"]
            v3_map = {x["path"]: x["sha256"] for x in v3_sources}
            if (not v3_sources or len(v3_map) != len(v3_sources)
                    or any(source_map.get(p) != h for p, h in v3_map.items())
                    or fingerprint(v3_map) != self.provenance["v3_data_fingerprint"]):
                raise ValueError("Fontes V3 incompatíveis com o relatório original.")
        expected = "1.1.0" if "tactical_v3" in self.profiles else "1.0.0"
        if self.provenance["report_schema_version"] != expected:
            raise ValueError("Schema de origem incompatível com os perfis.")

    def _validate_profile(self, profile, tid, cutoff):
        if not isinstance(profile, Mapping) or type(profile["team_id"]) is not int or profile["team_id"] != tid:
            raise ValueError("Equipe incompatível com a requisição.")
        _text(profile["team_name"], "Equipe")
        mids = profile["match_ids"]
        _ids(mids)
        if len(mids) > self.request.recent_matches_window or self.request.target_match_id in mids:
            raise ValueError("Janela ou exclusão do alvo violada.")
        for key in ("period_start", "period_end"):
            value = profile[key]
            if (value is None) != (not mids) or (value is not None and date.fromisoformat(value) >= cutoff):
                raise ValueError("Período histórico inválido ou não anterior ao corte.")
        if mids and profile["period_start"] > profile["period_end"]:
            raise ValueError("Período histórico invertido.")
        if not isinstance(profile["metrics"], Mapping) or not isinstance(profile["quality"], Mapping):
            raise ValueError("Métricas e qualidade devem ser objetos.")
        if any(type(v) is not int or v < 0 for v in profile["quality"].values()):
            raise ValueError("Contadores de qualidade devem ser inteiros não negativos.")
        for family in ("metrics", "sequence_metrics"):
            for key, metric in profile.get(family, {}).items():
                if set(metric) != {f.name for f in fields(MetricEvidence)} or metric["metric_id"] != key:
                    raise ValueError("Estrutura MetricEvidence inválida.")
                sample = metric["sample_size"]
                _ids(metric["match_ids"])
                if type(sample) is not int or sample < 0 or sample != len(metric["match_ids"]) or not set(metric["match_ids"]) <= set(mids):
                    raise ValueError("Amostra da métrica incompatível com a janela.")
                if metric["value"] is not None and type(metric["value"]) not in (int, float):
                    raise ValueError("Valor da métrica deve ser número ou null.")
                for name in ("numerator", "denominator", "median", "standard_deviation"):
                    if metric[name] is not None and type(metric[name]) not in (int, float):
                        raise ValueError("Estatística da métrica deve ser número ou null.")
                _text(metric["unit"], "Unidade")
                _text(metric["formula_version"], "Versão da fórmula")
                rows = metric["per_match"]
                if len(rows) != sample or tuple(r["match_id"] for r in rows) != metric["match_ids"]:
                    raise ValueError("Evidências por partida inconsistentes.")
                for row in rows:
                    for name in ("value", "numerator", "denominator"):
                        if row.get(name) is not None and type(row[name]) not in (int, float):
                            raise ValueError("Estatística por partida deve ser número ou null.")
                    day = date.fromisoformat(row["match_date"])
                    if day >= cutoff or not profile["period_start"] <= row["match_date"] <= profile["period_end"]:
                        raise ValueError("Evidência fora do período histórico.")

    @property
    def sufficiency(self) -> ComparisonSufficiency:
        """Reutiliza a política central existente, sem recalcular indicadores."""
        def profile(side):
            value = thaw(self.profiles[side])
            value["metrics"] = {k: MetricEvidence(**v) for k, v in value["metrics"].items()}
            return TeamProfile(**value)
        return report_sufficiency(SimpleNamespace(team_profile=profile("team_profile"), opponent_profile=profile("opponent_profile")))

    def evidence(self, reference: str) -> Mapping[str, JSONValue]:
        parts = reference.split(".")
        if parts[0] == "tactical_v3":
            if len(parts) != 4 or parts[1] not in ("team_profile", "opponent_profile") or parts[2] not in ("metrics", "sequence_metrics"):
                raise ValueError("Referência de evidência inválida.")
        elif len(parts) != 3 or parts[0] not in ("team_profile", "opponent_profile") or parts[1] != "metrics":
            raise ValueError("Referência de evidência inválida.")
        value = self.profiles
        try:
            for part in parts:
                value = value[part]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Evidência ausente: {reference}") from exc
        return value

    def to_dict(self) -> dict:
        return {"contract_version": CONTRACT_VERSION, "request": asdict(self.request), "cutoff_date": self.cutoff_date,
                "profiles": thaw(self.profiles), "provenance": thaw(self.provenance), "data_gaps": list(self.data_gaps),
                "sufficiency": asdict(self.sufficiency)}

    @property
    def input_fingerprint(self) -> str:
        return fingerprint(self.to_dict())


@dataclass(frozen=True)
class EngineHypothesis:
    hypothesis_id: str
    origin: str
    action: str
    condition: str
    evidence_metrics: tuple[str, ...]
    risks: tuple[str, ...]
    limitations: tuple[str, ...]
    preconditions: tuple[str, ...]
    observation: str | None = None
    title: str | None = None

    def __post_init__(self):
        for name in ("hypothesis_id", "origin", "action", "condition"):
            _text(getattr(self, name), name)
        for name in ("evidence_metrics", "risks", "limitations", "preconditions"):
            if not isinstance(getattr(self, name), (tuple, list)):
                raise ValueError(f"{name}: esperado conjunto de textos.")
            value = tuple(getattr(self, name))
            if not value:
                raise ValueError(f"{name}: ao menos um item obrigatório.")
            for item in value:
                _text(item, name)
            object.__setattr__(self, name, value)
        for name in ("observation", "title"):
            if getattr(self, name) is not None:
                _text(getattr(self, name), name)


@dataclass(frozen=True)
class TacticalEngineOutput:
    engine_id: str
    engine_version: str
    input_fingerprint: str
    provenance: Mapping[str, JSONValue]
    sufficient: bool
    status: Literal["hypotheses", "no_hypotheses", "abstained"]
    hypotheses: tuple[EngineHypothesis, ...]
    limitations: tuple[str, ...]

    def __post_init__(self):
        _text(self.engine_id, "Motor")
        _text(self.engine_version, "Versão")
        _digest(self.input_fingerprint)
        if not isinstance(self.hypotheses, (tuple, list)) or not isinstance(self.limitations, (tuple, list)):
            raise ValueError("Hipóteses e limitações devem ser sequências.")
        object.__setattr__(self, "provenance", freeze(self.provenance))
        if not isinstance(self.provenance, Mapping):
            raise ValueError("Proveniência deve ser objeto.")
        object.__setattr__(self, "hypotheses", tuple(self.hypotheses))
        object.__setattr__(self, "limitations", tuple(self.limitations))
        if type(self.sufficient) is not bool or self.status not in ("hypotheses", "no_hypotheses", "abstained"):
            raise ValueError("Estado de execução inválido.")
        if (self.status == "hypotheses") != bool(self.hypotheses) or (not self.sufficient and self.status != "abstained"):
            raise ValueError("Hipóteses incompatíveis com estado/suficiência.")
        if any(not isinstance(h, EngineHypothesis) for h in self.hypotheses):
            raise ValueError("Esperado EngineHypothesis.")
        if not self.limitations:
            raise ValueError("Limitações obrigatórias.")
        for item in self.limitations:
            _text(item, "Limitação")

    def validate_for(self, inputs: TacticalEngineInput) -> None:
        if self.input_fingerprint != inputs.input_fingerprint or self.provenance != inputs.provenance or self.sufficient != inputs.sufficiency.sufficient:
            raise ValueError("Saída não corresponde à entrada/proveniência/suficiência.")
        identifiers = [(h.origin, h.hypothesis_id) for h in self.hypotheses]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Hipóteses duplicadas.")
        for hypothesis in self.hypotheses:
            for path in hypothesis.evidence_metrics:
                metric = inputs.evidence(path)
                if metric["value"] is None or metric["sample_size"] < inputs.sufficiency.minimum_matches:
                    raise ValueError("Hipótese sem evidência calculável suficiente.")

    def to_dict(self) -> dict:
        return {"contract_version": CONTRACT_VERSION, "engine_id": self.engine_id, "engine_version": self.engine_version,
                "input_fingerprint": self.input_fingerprint, "provenance": thaw(self.provenance),
                "sufficient": self.sufficient, "status": self.status,
                "hypotheses": [asdict(h) for h in self.hypotheses], "limitations": list(self.limitations)}
