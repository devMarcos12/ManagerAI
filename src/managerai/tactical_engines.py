"""Motores explícitos sobre relatórios calculados, sem alterar pipeline/CLI/UI."""
from __future__ import annotations

from dataclasses import asdict
from typing import Protocol

from .report_schema import AnalysisReport
from .tactical_engine_schema import EngineHypothesis, TacticalEngineInput, TacticalEngineOutput
from .v3_schema import AnalysisReportV3


class TacticalEngine(Protocol):
    """Motores futuros recebem apenas o snapshot; não recalculam o núcleo."""

    engine_id: str
    engine_version: str

    def analyze(self, inputs: TacticalEngineInput) -> TacticalEngineOutput: ...


class EngineUnavailableError(ValueError):
    """Seleção inexistente/indisponível; nunca substituída silenciosamente."""


def build_engine_input(report: AnalysisReport) -> TacticalEngineInput:
    """Seleciona evidências existentes; exclui hipóteses, eventos e roster."""
    if not isinstance(report, AnalysisReport):
        raise ValueError("Esperado AnalysisReport ou AnalysisReportV3.")
    request = report.request
    for key, expected in (("competition_id", request.competition_id), ("season_id", request.season_id),
                          ("target_match_id", request.target_match_id)):
        if report.metadata[key] != expected:
            raise ValueError("Metadados incompatíveis com a requisição.")
    profiles = {"team_profile": asdict(report.team_profile), "opponent_profile": asdict(report.opponent_profile)}
    methodology = report.methodology
    provenance = {"report_schema_version": report.schema_version, "software_version": report.metadata["software_version"],
                  "sources": methodology["sources"], "data_fingerprint": report.metadata["data_fingerprint"],
                  "formula_version": methodology["formula_version"], "rules_version": methodology["rules_version"],
                  "temporal_policy": methodology["temporal_policy"], "window_policy": methodology["window_policy"]}
    if isinstance(report, AnalysisReportV3):
        extra = report.tactical_v3
        profiles["tactical_v3"] = {
            side: {key: extra[side][key] for key in ("team_id", "team_name", "match_ids", "period_start", "period_end", "metrics", "quality", "sequence_metrics")}
            for side in ("team_profile", "opponent_profile")}
        provenance.update(v3_formula_version=extra["formula_version"], v3_rules_version=extra["rules_version"],
                          v3_sources=extra["methodology"]["sources"], v3_data_fingerprint=extra["methodology"]["data_fingerprint"])
    return TacticalEngineInput(request, report.metadata["cutoff_date"][:10], profiles, provenance, tuple(report.data_gaps))


class DeterministicEngine:
    """Adaptador por relatório. Copia hipóteses reais, sem repetir regras/features.

    O sidecar aplica a política de abstenção central existente na apresentação;
    hipóteses brutas do JSON legado continuam intocadas no relatório original.
    """

    engine_id = "deterministic"
    engine_version = "4.1.0"  # Versão do adaptador; regras 1.0.0/3.0.0 na proveniência.

    def __init__(self, report: AnalysisReport):
        snapshot = build_engine_input(report)
        self.inputs = snapshot
        self._fingerprint = snapshot.input_fingerprint
        mapped = []
        for h in report.tactical_hypotheses:
            mapped.append(EngineHypothesis(h.rule_id, "legacy", h.recommendation, h.condition,
                          tuple(h.evidence_metrics), tuple(h.risks), tuple(h.limitations), tuple(h.preconditions)))
        if isinstance(report, AnalysisReportV3):
            for h in report.tactical_v3["hypotheses"]:
                mapped.append(EngineHypothesis(h["rule_id"], "v3", h["action"], h["condition"],
                              tuple(h["evidence_metrics"]), tuple(h["risks"]), tuple(h["limitations"]),
                              tuple(h["preconditions"]), h["observation"], h["title"]))
        self._hypotheses = tuple(mapped)

    def analyze(self, inputs: TacticalEngineInput) -> TacticalEngineOutput:
        if inputs.input_fingerprint != self._fingerprint:
            raise ValueError("Adaptador vinculado a outro snapshot.")
        sufficient = inputs.sufficiency.sufficient
        hypotheses = self._hypotheses if sufficient else ()
        output = TacticalEngineOutput(self.engine_id, self.engine_version, inputs.input_fingerprint, inputs.provenance,
                 sufficient, "abstained" if not sufficient else "hypotheses" if hypotheses else "no_hypotheses",
                 hypotheses, ("Hipóteses determinísticas exploratórias; sem modelo treinado ou eficácia causal validada.",
                              "A saída separada exige suficiência central; não modifica as hipóteses brutas do JSON legado.",
                              *inputs.sufficiency.warnings))
        output.validate_for(inputs)
        return output


def compare_engines(report: AnalysisReport, *, engine_ids: tuple[str, ...] = ("deterministic",),
                    engines: tuple[TacticalEngine, ...] = ()) -> tuple[TacticalEngineOutput, ...]:
    """Executa os motores selecionados no mesmo snapshot, sem ranking de mérito.

    O registro é local à chamada, sem plugins automáticos, rede, fallback ou estado
    global. Falha de motor interrompe a comparação; não vira recomendação vazia.
    Engines futuros são fornecidos explicitamente pelo chamador autorizado.
    """
    if not engine_ids or len(set(engine_ids)) != len(engine_ids):
        raise ValueError("Selecione motores únicos, explicitamente.")
    baseline = DeterministicEngine(report)
    inputs = baseline.inputs
    registry: dict[str, TacticalEngine] = {baseline.engine_id: baseline}
    for engine in engines:
        if not isinstance(engine.engine_id, str) or not engine.engine_id.strip() or not isinstance(engine.engine_version, str) or not engine.engine_version.strip() or not callable(getattr(engine, "analyze", None)):
            raise ValueError("Identificação/interface do motor inválida.")
        if engine.engine_id in registry:
            raise ValueError("ID de motor duplicado/reservado.")
        registry[engine.engine_id] = engine
    for selected in engine_ids:
        if selected not in registry:
            raise EngineUnavailableError(f"Motor não disponível: {selected}. Nenhum modelo especializado está incluído na V4.1.")
    results = []
    for selected in engine_ids:
        engine = registry[selected]
        output = engine.analyze(inputs)
        if not isinstance(output, TacticalEngineOutput) or (output.engine_id, output.engine_version) != (engine.engine_id, engine.engine_version):
            raise ValueError("Identidade/contrato da saída do motor inválido.")
        output.validate_for(inputs)
        results.append(output)
    return tuple(results)
