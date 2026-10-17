"""Apresentação fiel ao contrato, sem geração livre de fatos."""
from __future__ import annotations

from .report_schema import AnalysisReport
from .presentation.terminology import count, measure
from .presentation.coach_report import core_evidence_warnings, metric_period


def number(value: float | None) -> str:
    return "não disponível" if value is None else f"{value:.2f}".replace(".", ",")


def render_technical_markdown(report: AnalysisReport) -> str:
    report.to_dict()
    m = report.metadata
    lines = ["# Relatório histórico de apoio pré-jogo", "",
             f"**{m['team']} × {m['opponent']} — {m['competition']} {m['season']}**", "",
             f"Corte: {m['cutoff_date']}. Somente datas anteriores; o dia do corte é excluído.",
             f"Amostra: {count(m['matches_analyzed_team'])} da equipe e {count(m['matches_analyzed_opponent'])} do adversário.", "",
             *core_evidence_warnings(report), "",
             "## Período observado", ""]
    for p in (report.team_profile, report.opponent_profile):
        lines.append(f"- {p.team_name}: {p.period_start or 'sem histórico'} a {p.period_end or 'sem histórico'}; evidência {p.sample_status}.")
    lines.extend(["", "## Indicadores comparáveis", "",
                  "Taxas e proporções usam denominadores agregados; n indica jogos com métrica calculável.", "",
                  "| Indicador | Unidade | Equipe | n | Período da equipe | Adversário | n | Período do adversário |", "|---|---|---:|---:|---|---:|---:|---|"])
    for c in report.comparison:
        key = c['metric_id']
        a = metric_period(report.team_profile, report.team_profile.metrics[key])
        b = metric_period(report.opponent_profile, report.opponent_profile.metrics[key])
        lines.append(f"| {c['label']} | {c['unit']} | {number(c['team_value'])} | {c['team_sample_size']} | {a} | {number(c['opponent_value'])} | {c['opponent_sample_size']} | {b} |")
    lines.extend(["", "## Achados observáveis", ""])
    if not report.key_findings:
        lines.append("Não há evidência comparável suficiente para emitir achados.")
    for finding in report.key_findings:
        lines.append(f"- {finding['description']} Equipe: {measure(finding['team_value'], finding['unit'])}; adversário: {measure(finding['opponent_value'], finding['unit'])}.")
        lines.append(f"  Evidências: {', '.join(finding['evidence_metrics'])}.")
    lines.extend(["", "Diferenças observadas não demonstram superioridade, vulnerabilidade causal ou eficácia de uma estratégia.",
                  "", "## Hipóteses condicionais para investigação", ""])
    if not report.tactical_hypotheses:
        lines.append("Hipóteses não emitidas: amostra ou evidência insuficiente para as regras.")
    for h in report.tactical_hypotheses:
        lines.extend([f"### {h.rule_id}", "", h.recommendation, "", f"Condição: {h.condition}",
                      f"Evidências: {', '.join(h.evidence_metrics)}.", f"Qualidade da evidência: {h.confidence_level}.", "",
                      "Pré-condições:", "", *[f"- {x}" for x in h.preconditions], "", "Riscos:", "",
                      *[f"- {x}" for x in h.risks], "", "Limitações:", "", *[f"- {x}" for x in h.limitations], ""])
    lines.extend(["## Formação e escalação", "", "Não suportado pelos dados atuais.", "",
                  "## Contexto informado pelo treinador", "",
                  f"Mando declarado: {report.request.venue}. Contexto declarado: {report.request.match_context}.",
                  f"Objetivo declarado: {report.request.strategic_objective}.",
                  "Indisponíveis declarados (IDs): " + (", ".join(map(str, report.request.unavailable_player_ids)) or "nenhum informado"),
                  "", "Notas declaradas (texto do treinador, não verificado):", ""])
    lines.extend(["> " + x for x in (report.request.notes or "Nenhuma nota informada.").splitlines()])
    lines.extend(["", "## Lacunas e limites", "", *[f"- {x}" for x in report.data_gaps], "",
                  "## Metodologia e rastreabilidade", ""])
    for key in ("baseline", "temporal_policy", "exposure", "aggregation", "coordinates", "sample_policy", "context_policy", "reporter", "attribution"):
        lines.append(f"- {report.methodology[key]}")
    lines.extend(["", f"Versão das fórmulas: {report.methodology['formula_version']}; regras: {report.methodology['rules_version']}.",
                  f"Fingerprint SHA-256 dos arquivos efetivamente lidos: `{m['data_fingerprint']}`.",
                  "IDs das partidas, valores individuais, medianas, desvios-padrão, numeradores, denominadores e hashes das fontes estão em report.json.", ""])
    import re
    return re.sub(r"(?<![0-9])1 jogos\b", "1 jogo", "\n".join(lines))


def render_markdown(report: AnalysisReport) -> str:
    """Apresentação V2 com versão técnica V1 preservada no apêndice."""
    from .presentation.coach_report import render_coach_markdown

    technical = render_technical_markdown(report)
    appendix = "\n".join("##" + line if line.startswith("#") else line for line in technical.splitlines())
    extra = ""
    if getattr(report, "tactical_v3", None):
        from .v3_presentation import render_v3_markdown
        extra = render_v3_markdown(report)
    return render_coach_markdown(report) + extra + "\n## Apêndice técnico — indicadores e rastreabilidade\n\n" + appendix + "\n"
