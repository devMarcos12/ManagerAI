"""Leitura do AnalysisReport; não recalcula features nem aciona novas regras."""
from dataclasses import dataclass

from ..report_schema import AnalysisReport, MetricEvidence, TacticalHypothesis, TeamProfile
from .terminology import (CORE_METRICS, MINIMUM_CORE_MATCHES, PRIORITY_METRICS, TERMS,
                          count_label, date_label, number, reading)


@dataclass(frozen=True)
class CoachHypothesis:
    title: str
    observed: str
    why_it_matters: str
    action: str
    condition: str
    risks: list[str]
    limitations: list[str]
    preconditions: list[str]
    evidence_paths: list[str]


@dataclass(frozen=True)
class CoachReport:
    overview: list[str]
    summary: list[str]
    comparison: list[dict[str, str]]
    attention: list[str]
    hypotheses: list[CoachHypothesis]
    warnings: list[str]


def period(profile: TeamProfile) -> str:
    if not profile.match_ids:
        return f"{profile.team_name}: sem jogos anteriores disponíveis."
    return (f"{profile.team_name}: {count_label(len(profile.match_ids))}, de {date_label(profile.period_start)} "
            f"a {date_label(profile.period_end)}.")


def metric_period(profile: TeamProfile, metric: MetricEvidence) -> str:
    """Período dos jogos calculáveis; não atribui período da janela a métrica nula."""
    if metric.value is None or metric.sample_size == 0:
        return "sem informação calculável"
    dates = sorted(row["match_date"] for row in metric.per_match if row.get("match_date"))
    if dates:
        return f"{date_label(dates[0])} a {date_label(dates[-1])}"
    # Perfis produzidos pelo pipeline sempre têm per_match; fallback identifica a janela.
    return f"janela: {date_label(profile.period_start)} a {date_label(profile.period_end)}"


def insufficient_core_evidence(report: AnalysisReport) -> bool:
    """Política de apresentação compartilhável pela UI, sem alterar o JSON V1/V2."""
    return any(profile.metrics.get(key) is None or profile.metrics[key].value is None
               or profile.metrics[key].sample_size < MINIMUM_CORE_MATCHES
               for profile in (report.team_profile, report.opponent_profile) for key in CORE_METRICS)


def core_evidence_warnings(report: AnalysisReport) -> list[str]:
    warnings = []
    for profile in (report.team_profile, report.opponent_profile):
        missing = [key for key in CORE_METRICS if profile.metrics.get(key) is None
                   or profile.metrics[key].value is None
                   or profile.metrics[key].sample_size < MINIMUM_CORE_MATCHES]
        if missing:
            counts = [profile.metrics[key].sample_size if profile.metrics.get(key)
                      and profile.metrics[key].value is not None else 0 for key in missing]
            warnings.append(f"Amostra insuficiente — {profile.team_name}: pelo menos um indicador central tem apenas "
                            f"{count_label(min(counts))} com informação calculável. Histórico insuficiente para comparação confiável. "
                            "Os valores são uma consulta descritiva; não interpretar diferenças como superioridade. "
                            "Não são apresentadas conclusões comparativas nem hipóteses de ajuste.")
    return warnings


def evidence(report: AnalysisReport, path: str) -> tuple[TeamProfile, MetricEvidence] | None:
    parts = path.split(".")
    if len(parts) != 3 or parts[0] not in ("team_profile", "opponent_profile") or parts[1] != "metrics":
        return None
    profile = getattr(report, parts[0])
    metric = profile.metrics.get(parts[2])
    return (profile, metric) if metric is not None else None


def plain(text: str) -> str:
    return (text.replace("Pressure", "ações de pressão").replace("xG positivo", "gols esperados positivos")
            .replace("xG concedido", "gols esperados permitidos").replace("xG", "gols esperados")
            .replace("terço final", "terço de ataque")
            .replace("Regra exploratória sem validação causal ou de eficácia.", "Sugestão exploratória: não foi demonstrado que esse ajuste melhora o desempenho."))


def present_hypothesis(report: AnalysisReport, hypothesis: TacticalHypothesis) -> CoachHypothesis:
    readings = []
    for path in hypothesis.evidence_metrics:
        found = evidence(report, path)
        if found is not None:
            profile, metric = found
            term = TERMS[metric.metric_id]
            readings.append(f"{profile.team_name} — {term.title.lower()}: {reading(metric.value, term.unit)} "
                            f"({count_label(metric.sample_size)} com informação disponível; {metric_period(profile, metric)})")
    descriptions = {
        "R01_PROGRESSAO": (
            "Preparar a proteção das zonas de chegada",
            "Essas ações registram avanços da bola até o terço de ataque; não mostram, sozinhas, o perigo de cada chegada.",
            "Rever em vídeo como essas entradas acontecem e ensaiar coberturas em treino. A zona específica e a altura do bloco ainda precisam dessa verificação."),
        "R02_PRESSAO_ALTA": (
            "Avaliar alternativas para sair sob pressão",
            "A localização da pressão ajuda a selecionar situações de treino. O acerto de passe considera apenas ações com pressão explicitamente marcada.",
            "Rever essas situações em vídeo e testar apoios próximos como uma alternativa de saída. A marca de 30% é um critério exploratório, não uma garantia de eficácia."),
        "R03_CHANCES": (
            "Rever a proteção dos espaços de finalização",
            "A qualidade estimada das finalizações complementa a contagem de chutes. A média não identifica onde está uma falha defensiva nem prevê gols no confronto.",
            "Rever a localização e o contexto das finalizações nas partidas analisadas e testar a proteção desses espaços em treino, antes de escolher um ajuste defensivo."),
    }
    title, why, action = descriptions.get(hypothesis.rule_id, (
        "Avaliação adicional apoiada no histórico", "A observação precisa de revisão da comissão técnica.",
        "Consultar as evidências e limitações no relatório detalhado antes de testar qualquer ajuste."))
    return CoachHypothesis(title, "; ".join(readings) + "." if readings else "Evidências indisponíveis; não interpretar como zero.",
                           why, action, plain(hypothesis.condition), [plain(x) for x in hypothesis.risks],
                           [plain(x) for x in hypothesis.limitations], [plain(x) for x in hypothesis.preconditions],
                           list(hypothesis.evidence_metrics))


def build_coach_report(report: AnalysisReport) -> CoachReport:
    report.to_dict()
    own, opp = report.team_profile, report.opponent_profile
    overview = [f"{own.team_name} × {opp.team_name} — {report.metadata['competition']} {report.metadata['season']}.",
                f"Referência histórica: {date_label(report.metadata['cutoff_date'])}. O dia da referência fica fora da análise.",
                period(own), period(opp),
                "Este relatório usa dados históricos locais; não descreve os elencos ou a situação atual dos clubes."]
    insufficient = insufficient_core_evidence(report)
    summary = []
    for key in ("shots_for", "xg_for", "xg_against", "pass_accuracy", "final_third_entries"):
        a, b = own.metrics[key], opp.metrics[key]
        if insufficient or a.value is None or b.value is None:
            continue
        term = TERMS[key]
        summary.append(f"{term.title}: {reading(a.value, term.unit)} para {own.team_name} "
                       f"({count_label(a.sample_size)}; {metric_period(own, a)}) e {reading(b.value, term.unit)} para {opp.team_name} "
                       f"({count_label(b.sample_size)}; {metric_period(opp, b)}).")
    comparison = []
    for key in PRIORITY_METRICS:
        a, b = own.metrics[key], opp.metrics[key]
        term = TERMS[key]
        comparison.append({"Indicador": term.title, "Unidade": term.unit,
                           own.team_name: number(a.value), opp.team_name: number(b.value),
                           "Jogos com informação (meu time / adversário)": f"{a.sample_size} / {b.sample_size}",
                           "Período (meu time)": metric_period(own, a),
                           "Período (adversário)": metric_period(opp, b),
                           "Como ler": term.explanation})
    attention = []
    for key, interpretation in (
        ("shots_for", "O volume não basta para afirmar que um ataque é mais forte; confira a localização e o contexto dos chutes."),
        ("xg_for", "Esse valor descreve a qualidade estimada das finalizações, sem prever gols ou vitória no confronto."),
        ("final_third_entries", "São avanços da bola por passe completo ou condução; a zona específica exige revisão em vídeo."),
        ("pressures", "O número de ações não informa quantas pressões deram certo e não define sozinho um estilo de jogo."),
    ):
        metric = opp.metrics[key]
        if metric.value is not None:
            term = TERMS[key]
            attention.append(f"{opp.team_name} — {term.title.lower()}: {reading(metric.value, term.unit)}, "
                             f"em {count_label(metric.sample_size)} com informação disponível ({metric_period(opp, metric)}). {interpretation}")
    warnings = core_evidence_warnings(report)
    if not insufficient:
        warnings.append("A evidência continua limitada: adversários e datas podem diferir entre as janelas. "
                        "As diferenças não comprovam superioridade ou eficácia de um ajuste.")
    if any(p.quality for p in (own, opp)):
        warnings.append("Há registros ausentes ou ocorrências de qualidade nas partidas analisadas. "
                        "A disponibilidade de cada indicador e as ocorrências constam dos detalhes técnicos.")
    return CoachReport(overview, summary, comparison, attention,
                       [] if insufficient else [present_hypothesis(report, h) for h in report.tactical_hypotheses], warnings)


def render_coach_markdown(report: AnalysisReport) -> str:
    view = build_coach_report(report)
    overview = [part for line in view.overview for part in (line, "")]
    lines = ["# Preparação pré-jogo — ManagerAI", "", *view.warnings, "", "## Visão geral do confronto", "", *overview,
             "Gols esperados (xG) representam a soma dos valores esperados das finalizações. "
             "xG estima a qualidade das finalizações. Não são uma contagem de chances, gols reais ou probabilidade de vencer.", "",
             "## Conclusões sustentadas — resumo para a comissão técnica", "", *[f"- {s}" for s in view.summary]]
    if not view.summary:
        lines.append("Não há histórico comparável suficiente para descrever diferenças entre as equipes.")
    lines.extend(["", "## Indicadores observados (consulta descritiva)", "", *view.warnings, "", "As taxas por 90 min consideram o tempo observado, incluindo acréscimos. "
                  "Indisponível significa ausência de informação calculável, nunca zero.", "",
                  f"| Indicador | Unidade | {report.team_profile.team_name} | {report.opponent_profile.team_name} | Jogos disponíveis (equipe / adversário) | Período da equipe | Período do adversário | Como ler |",
                  "|---|---|---:|---:|---|---|---|---|"])
    own, opp = report.team_profile.team_name, report.opponent_profile.team_name
    for row in view.comparison:
        lines.append(f"| {row['Indicador']} | {row['Unidade']} | {row[own]} | {row[opp]} | {row['Jogos com informação (meu time / adversário)']} | {row['Período (meu time)']} | {row['Período (adversário)']} | {row['Como ler']} |")
    lines.extend(["", "## Observações descritivas do adversário", "", *[f"- {s}" for s in view.attention]])
    if not view.attention:
        lines.append("Sem jogos anteriores disponíveis para descrever o adversário.")
    lines.extend(["", "## Possíveis ajustes para avaliar em treino ou vídeo", ""])
    if not view.hypotheses:
        lines.append("Não foram emitidas hipóteses: o histórico ou as evidências não atendem aos critérios mínimos. Não completamos sugestões artificialmente.")
    for h in view.hypotheses:
        lines.extend([f"### {h.title}", "", f"**O que foi observado:** {h.observed}", "",
                      f"**Por que importa:** {h.why_it_matters}", "", f"**O que verificar ou testar:** {h.action}", "",
                      f"**Condição:** {h.condition}", "", "**Antes de testar:**", "", *[f"- {x}" for x in h.preconditions],
                      "", "**Riscos:**", "", *[f"- {x}" for x in h.risks], "", "**Limitações:**", "", *[f"- {x}" for x in h.limitations], ""])
    lines.extend(["## Informações declaradas pelo treinador", "",
                  "São um cenário de planejamento informado manualmente. Não alteram o cálculo nem os critérios das hipóteses nesta versão.", "",
                  f"- Mando declarado: {report.request.venue}.", f"- Contexto declarado: {report.request.match_context}.",
                  f"- Objetivo declarado: {report.request.strategic_objective}.",
                  f"- Jogadores indisponíveis declarados: {len(report.request.unavailable_player_ids)}; não há sugestão de substitutos.", "",
                  "Notas declaradas (texto do treinador, não verificado):", ""])
    lines.extend(["> " + line for line in (report.request.notes or "Nenhuma nota informada.").splitlines()])
    lines.extend(["", "## O que o sistema ainda não consegue recomendar", "",
                  "Formação ideal e escalação: Não suportado pelos dados atuais. Essa é uma limitação deliberada, não uma falha de execução.",
                  "O sistema não infere lesões, suspensões, disponibilidade presente, resultado do confronto ou eficácia comprovada de um ajuste.",
                  "As faixas espaciais não são chamadas automaticamente de esquerda ou direita: a orientação ainda precisa ser validada.", "",
                  "## Como conferir a análise", "", "A apresentação vem do mesmo relatório calculado pela CLI. "
                  "O relatório técnico em JSON preserva valores exatos, partidas, fórmulas e fontes. "
                  "As hipóteses são exploratórias e exigem avaliação da comissão técnica.", "",
                  "Fonte: StatsBomb Open Data. Nenhum modelo foi treinado e nenhuma LLM foi utilizada.", ""])
    return "\n".join(lines)
