"""Serviço coletivo auditável; API/LLM não recalculam métricas nem escolhem atletas."""
from dataclasses import asdict

from .coverage import preview_coverage, report_sufficiency
from .data_inventory import load_season, team_ids
from .data_loader import LocalData
from .explanation import explain, fingerprint
from .pipeline import analyze
from .service_schema import ServiceError, ServiceRequest, SERVICE_VERSION
from .tactical_engines import compare_engines
from .v3_schema import VALIDATED_RECUTS

ORDERING_VERSION = "context-order-1"
STRATEGY_PREFERENCE = {"equilibrada": (), "proteger_area": ("R03_CHANCES", "V3_CHUTES_AREA"),
                       "saida_sob_pressao": ("R02_PRESSAO_ALTA",),
                       "proteger_progressao": ("R01_PROGRESSAO", "V3_ENTRADAS_PASSE")}
OBJECTIVE_PREFERENCE = {"proteger vantagem": ("R03_CHANCES", "V3_CHUTES_AREA"),
                        "pressionar alto": ("R02_PRESSAO_ALTA",)}


def validate_context(root, request):
    core = request.analysis
    season = load_season(LocalData(root), core.competition_id, core.season_id)
    preview = preview_coverage(LocalData(root), core, season)
    if request.include_v3 and (core.competition_id, core.season_id) not in VALIDATED_RECUTS:
        raise ServiceError("SEASON_NOT_CERTIFIED", "Recorte não certificado para V3.")
    if core.target_match_id is not None and core.venue != "desconhecido":
        target = next(m for m in season.matches if m["match_id"] == core.target_match_id)
        home, _ = team_ids(target)
        if core.venue != ("casa" if home == core.team_id else "fora"):
            raise ServiceError("CONTEXT_CONFLICT", "Mando declarado contradiz mando formal do calendário; não inferir campo neutro.")
    if any(p.observed_on > preview.cutoff[:10] for p in request.roster):
        raise ServiceError("FUTURE_ROSTER", "Elenco informado tem referência posterior ao corte.")
    return preview


def coverage(root, request):
    return asdict(validate_context(root, request))


def build_service_report(root, request: ServiceRequest, *, provider=None):
    validate_context(root, request)
    if request.explainer_model is not None and (provider is None or provider.model != request.explainer_model):
        raise ServiceError("MODEL_UNAVAILABLE", "Modelo solicitado não está configurado; nenhum substituto foi usado.", 503)
    if request.explanation == "required" and provider is None:
        raise ServiceError("MODEL_UNAVAILABLE", "Explicação obrigatória sem provedor configurado.", 503)
    report = analyze(root, request.analysis, include_v3=request.include_v3)
    legacy = report.to_dict()
    engine = compare_engines(report)[0].to_dict()
    sufficiency = asdict(report_sufficiency(report))
    evidence = {}
    for side in ("team_profile", "opponent_profile"):
        for key, metric in legacy[side]["metrics"].items():
            evidence[f"{side}.metrics.{key}"] = {**metric, "team_id": legacy[side]["team_id"],
                                                "team_name": legacy[side]["team_name"]}
        if request.include_v3:
            for key, metric in legacy["tactical_v3"][side]["metrics"].items():
                evidence[f"tactical_v3.{side}.metrics.{key}"] = {**metric, "team_id": legacy[side]["team_id"],
                                                               "team_name": legacy[side]["team_name"]}
    plans, excluded = [], []
    preferred = STRATEGY_PREFERENCE[request.intended_strategy]
    objective = OBJECTIVE_PREFERENCE.get(request.analysis.strategic_objective, ())
    for h in engine["hypotheses"]:
        pid = h["hypothesis_id"] if "hypothesis_id" in h else h.get("rule_id")
        if pid in request.blocked_plan_ids:
            excluded.append({"plan_id": pid, "reason": "Restrição declarada pelo treinador."})
            continue
        refs = h["evidence_metrics"] if "evidence_metrics" in h else h["evidence_refs"]
        if any(ref not in evidence or evidence[ref]["value"] is None for ref in refs):
            raise ServiceError("INVALID_EVIDENCE", "Motor retornou evidência inválida.", 500)
        plans.append({"plan_id": pid, "observation": h.get("observation") or h["condition"],
                      "evidence_ids": refs, "condition": h["condition"],
                      "possible_action": h.get("action", h.get("recommendation")),
                      "risks": h["risks"], "restrictions": list(request.blocked_plan_ids),
                      "limitations": h["limitations"], "preconditions": h["preconditions"],
                      "abstention_reason": None,
                      "context_priority": (2 if pid in preferred else 0) + (1 if pid in objective else 0)})
    plans.sort(key=lambda p: (-p["context_priority"], p["plan_id"]))
    abstention = ("Evidência central insuficiente." if not sufficiency["sufficient"] else
                  "Todos os planos sustentados foram restringidos." if excluded and not plans else
                  "Nenhuma regra satisfeita." if not plans else None)
    claims = [{"id": "scope", "text": "Análise histórica; hipóteses condicionais sem eficácia esportiva validada.",
               "evidence_ids": ["report.metadata"]},
              {"id": "sample", "text": ("Há evidência limitada para comparação coletiva." if sufficiency["sufficient"]
                                         else "Amostra insuficiente: abstenção de planos comparativos."),
               "evidence_ids": ["service.sufficiency"]}]
    for i, p in enumerate(plans):
        claims.append({"id": f"plan_{i}", "text": f"Possibilidade condicional: {p['possible_action']} Condição: {p['condition']}",
                       "evidence_ids": p["evidence_ids"], "plan_id": p["plan_id"]})
    claims.append({"id": "roster", "text": "Nenhuma escalação ideal ou disponibilidade atual é inferida do histórico.",
                   "evidence_ids": ["service.roster_policy"]})
    comparisons = [{"plans": [left["plan_id"], right["plan_id"]],
                   "different_evidence_ids": sorted(set(left["evidence_ids"]) ^ set(right["evidence_ids"])),
                   "interpretation": "Opções condicionais distintas; evidências não estimam qual funciona melhor.",
                   "context_priority_tied": left["context_priority"] == right["context_priority"]}
                  for i, left in enumerate(plans) for right in plans[i+1:]]
    identity = fingerprint({"request": request.to_dict(), "legacy": legacy})
    projection = {"report_id": identity, "claims": claims}
    explanation = explain(projection, mode=request.explanation, provider=provider)
    if request.explanation == "required" and explanation["status"] != "generated":
        raise ServiceError("EXPLANATION_FAILED", "Provedor não produziu explicação válida.", 503)
    return {"schema_version": SERVICE_VERSION, "report_id": identity,
            "request": request.to_dict(), "legacy_report": legacy, "evidence": evidence,
            "sufficiency": sufficiency, "plans": plans, "excluded_plans": excluded, "plan_comparisons": comparisons,
            "abstention_reason": abstention,
            "ordering": {"version": ORDERING_VERSION, "meaning": "Prioridade declarada, não eficácia ou superioridade.",
                         "ties": "Empates não são ordenação de mérito; IDs apenas estabilizam apresentação.",
                         "rule": "Estratégia compatível +2; objetivo compatível +1; demais 0."},
            "roster_policy": {"status": "declared" if request.roster else "missing",
                              "provenance": "Declarações do treinador; não verificadas externamente.",
                              "individual_suggestions": "abstained",
                              "reason": "Sem avaliação validada para recomendações individuais."},
            "model_status": {"tactical": "deterministic", "shots_predictor": "experimental_not_integrated",
                             "fine_tuned_explainer": "experimental_not_promoted"},
            "explanation": explanation, "limitations": list(report.data_gaps),
            "provenance": {"engine": engine, "context": "coach_declared", "ordering_version": ORDERING_VERSION}}


def render_service_markdown(result):
    from .presentation.terminology import number
    lines = ["# Preparação histórica do confronto", "", f"Relatório: {result['report_id']}", "",
             "Hipóteses condicionais; sem eficácia esportiva validada.", "",
             f"Suficiência: {result['sufficiency']['status']}.", ""]
    meta = result["legacy_report"]["metadata"]
    lines += [f"{meta['team']} × {meta['opponent']}; corte: {meta['cutoff_date']}.", "",
              f"Contexto declarado: {result['request']['analysis']['match_context']}; "
              f"objetivo: {result['request']['analysis']['strategic_objective']}; "
              f"estratégia pretendida: {result['request']['intended_strategy']}.", "",
              "Prioridades são preferências declaradas, sem comparação de eficácia.", "",
              f"Elenco: {result['roster_policy']['status']}. Sugestões individuais: abstenção.", ""]
    if result["abstention_reason"]:
        lines += [result["abstention_reason"], ""]
    for p in result["plans"]:
        lines += [f"## {p['plan_id']}", "", p["observation"], "", p["possible_action"], "",
                  f"Condição: {p['condition']}", "", "Riscos: " + " ".join(p["risks"]), "",
                  "Limitações: " + " ".join(p["limitations"]), ""]
        lines += ["Pré-condições: " + " ".join(p["preconditions"]), ""]
        for ref in p["evidence_ids"]:
            e = result["evidence"][ref]
            lines += [f"- {ref}: {e['team_name']}; {number(e['value'])} {e['unit']}; "
                      f"n={e['sample_size']}; jogos={e['match_ids']}; numerador={e['numerator']}; denominador={e['denominator']}; "
                      f"datas={[row.get('match_date') for row in e.get('per_match', [])]}; fórmula={e.get('formula_version')}."]
        lines += [""]
    lines += ["## Explicação", "", f"Estado: {result['explanation']['status']}.", ""]
    lines += [c["text"] for c in result["explanation"]["claims"]]
    lines += ["", "## Limitações", ""] + ["- " + x for x in result["limitations"]]
    lines += ["", f"Fontes e hashes: fingerprint {meta['data_fingerprint']}; lista integral no JSON."]
    return "\n".join(lines) + "\n"
