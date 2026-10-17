"""Apresentação V3 de evidências calculadas, sem inferir novas recomendações."""
from __future__ import annotations

from .presentation.coach_report import insufficient_core_evidence
from .presentation.terminology import count, date_label, measure


def _payload(report):
    return getattr(report, "tactical_v3", None) or {}


def _definitions():
    from .v3_features import V3_METRICS
    return V3_METRICS


def metric_period(profile, metric):
    """Identifica o período calculável; usa fallback explicitamente identificado."""
    if metric.get("value") is None or not metric.get("sample_size"):
        return "sem informação calculável"
    dates = sorted(row["match_date"] for row in metric.get("per_match", []) if row.get("match_date"))
    if dates:
        return f"{date_label(dates[0])} a {date_label(dates[-1])}"
    return (f"janela: {date_label(profile.get('period_start'))} a "
            f"{date_label(profile.get('period_end'))}")


def _friendly_definition(key):
    if key.startswith("progressive_"):
        return "Avanços por passe completo ou condução que aproximam a bola da meta; critério de distância nos detalhes técnicos."
    if key.startswith("final_third_"):
        return "A bola passa de antes do terço de ataque para dentro dele; não mede a chegada de jogadores."
    if key.startswith("box_"):
        return "A bola passa de fora para dentro da área por esse tipo de ação; não comprova perigo ou eficácia."
    if key.startswith("entry_lane_"):
        return "Parcela das entradas no terço de ataque com destino nessa faixa transversal; sem atribuir esquerda ou direita tática."
    if key.startswith("pressure_lane_"):
        return "Parcela das tentativas de pressão registradas nessa faixa transversal; não mede sucesso."
    if key.startswith("pressures_"):
        return "Tentativas de pressão localizadas nessa região; maior volume não comprova eficácia."
    if key.startswith("shots_"):
        return "Parcela das finalizações com localização nessa zona; confira os jogos calculáveis."
    if key.startswith("xg_"):
        return "Qualidade estimada das finalizações localizadas; não é contagem de chances nem probabilidade de vitória."
    if key == "recoveries_explicit_failure":
        return "Registros de recuperação que têm falha explicitamente marcada."
    if key == "recoveries_explicit_nonfailure":
        return "Registros com ausência de falha explicitamente marcada; a marcação ausente não entra neste grupo."
    return "Registros de recuperação de bola; não comprovam posse consolidada nem vínculo causal com uma pressão."


def _friendly_label(label):
    return label.replace("faixa de y baixo", "faixa transversal de coordenada baixa").replace("faixa de y alto", "faixa transversal de coordenada alta")


def _friendly_unit(unit):
    return {"eventos/90": "por 90 min", "xG/jogo": "gols esperados por jogo", "xG/chute": "gols esperados por chute"}.get(unit, unit)


def _rows(payload, pressure=False):
    definitions = _definitions()
    rows = []
    for side in ("team_profile", "opponent_profile"):
        profile = payload.get(side) or {}
        for key, metric in profile.get("metrics", {}).items():
            is_pressure = key.startswith(("pressure", "recover"))
            if is_pressure != pressure:
                continue
            definition = definitions.get(key, {})
            if not definition:
                continue  # Sem vocabulário validado, não exibe ID interno ao treinador.
            rows.append({
                "Equipe": profile.get("team_name", "Equipe sem identificação"),
                "Indicador": _friendly_label(definition["label"]),
                "Valor": measure(metric.get("value"), _friendly_unit(definition["unit"])),
                "Jogos com informação": metric.get("sample_size", 0),
                "Período calculável": metric_period(profile, metric),
                "Como ler": _friendly_definition(key),
            })
    return rows


def _markdown_table(rows):
    if not rows:
        return ["Não disponível: não há indicadores calculáveis desta família."]
    headings = list(rows[0])
    clean = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(headings) + " |", "|" + "---|" * len(headings)]
    lines.extend("| " + " | ".join(clean(row[key]) for key in headings) + " |" for row in rows)
    return lines


def _hypotheses(report, payload):
    return [] if insufficient_core_evidence(report) else payload.get("hypotheses", [])


def _items(value):
    if not value:
        return ["Não informado; verificar antes de testar."]
    return [value] if isinstance(value, str) else list(value)


SEQUENCE_TERMS = {
    "observed_blocks": ("Blocos observados com ações ofensivas", "blocos observados por jogo"),
    "entry_block_share": ("Blocos observados com entrada no terço de ataque ou na área", "%"),
    "shot_block_share": ("Blocos observados com finalização", "%"),
}
SEQUENCE_LIMIT = ("Blocos com ações ofensivas registradas não representam todas as posses reais nem tempo com a bola. "
                  "Ações no mesmo bloco não demonstram causalidade. Jogos com inconsistências são excluídos dos agregados, "
                  "sem converter ausências em zero.")
HISTORY_LIMIT = ("Participação histórica em ordem alfabética, sem ranking: as contagens não medem capacidade nem são "
                 "normalizadas por minutos. Disponibilidade no confronto é desconhecida. Formações são registros anteriores, "
                 "sem indicar esquema ideal, posicionamento contínuo ou eficácia; mudanças são apenas as registradas nos dois tempos.")


def _sequence_rows(payload):
    rows = []
    for side in ("team_profile", "opponent_profile"):
        profile = payload.get(side) or {}
        for key, (label, unit) in SEQUENCE_TERMS.items():
            metric = profile.get("sequence_metrics", {}).get(key)
            if metric is not None:
                rows.append({"Equipe": profile.get("team_name", "Equipe"), "Indicador": label,
                             "Valor": measure(metric.get("value"), unit),
                             "Jogos com informação": metric.get("sample_size", 0),
                             "Período calculável": metric_period(profile, metric)})
    return rows


def _sequence_warnings(payload):
    reasons = {
        "invalid_or_decreasing_timestamp": "horários de ações fora de ordem ou inválidos",
        "invalid_possession_context": "identificação de posse ausente ou inconsistente",
        "invalid_event_identity_or_index": "identificação ou ordem de ações inconsistente",
        "invalid_event_object": "registro de ação inválido",
        "invalid_period": "tempo de jogo inválido",
        "invalid_event_team": "equipe da ação inconsistente",
        "invalid_event_type": "tipo de ação ausente ou inválido",
        "offensive_action_missing_payload": "informação de passe ou condução incompleta",
        "offensive_action_invalid_geometry": "localização de passe ou condução ausente ou inválida",
        "no_regulation_events": "ausência de ações nos dois tempos regulamentares",
    }
    messages = []
    for side in ("team_profile", "opponent_profile"):
        profile = payload.get(side) or {}
        for sequence in profile.get("sequences", []):
            if sequence.get("valid_blocks") is None:
                quality = sequence.get("quality", {})
                descriptions = sorted({reasons.get(key, "inconsistência nos registros")
                                       for key, value in quality.items() if value})
                reason = "; ".join(descriptions) or "dados insuficientes para validar os blocos"
                messages.append(f"{profile.get('team_name', 'Equipe')} — {date_label(sequence.get('match_date'))}: "
                                f"jogo não calculável para sequências ({reason}).")
    return messages


def _historical_period(profile, match_ids):
    history = profile.get("historical") or {}
    dates = {str(key): value for key, value in history.get("match_dates", {}).items()}
    for metric in profile.get("metrics", {}).values():
        dates.update({str(row["match_id"]): row["match_date"] for row in metric.get("per_match", [])
                      if row.get("match_id") is not None and row.get("match_date")})
    dates.update({str(row["match_id"]): row["match_date"] for row in profile.get("sequences", [])
                  if row.get("match_id") is not None and row.get("match_date")})
    selected = sorted(dates[str(mid)] for mid in match_ids if str(mid) in dates)
    if selected and len(selected) == len(match_ids):
        return f"{date_label(selected[0])} a {date_label(selected[-1])}"
    return "janela: " + date_label(profile.get("period_start")) + " a " + date_label(profile.get("period_end"))


def _formation_label(value):
    return "-".join(str(value)) if isinstance(value, int) and value > 0 else "não disponível"


def _history_rows(payload):
    players, formations, changes = [], [], []
    for side in ("team_profile", "opponent_profile"):
        profile = payload.get(side) or {}
        history = profile.get("historical") or {}
        name = profile.get("team_name", "Equipe")
        for player in sorted(history.get("players", []), key=lambda row: row.get("name", "").casefold()):
            players.append({"Equipe": name, "Jogador": player.get("name", "não disponível"),
                            "Jogos com ações": player.get("matches_with_actions", 0),
                            "Período das ações": _historical_period(profile, player.get("match_ids", [])),
                            "Passes tentados": player.get("passes", 0), "Passes completos": player.get("passes_completed", 0),
                            "Conduções": player.get("carries", 0), "Finalizações": player.get("shots", 0),
                            "Tentativas de pressão": player.get("pressures", 0),
                            "Gols esperados acumulados": measure(player.get("xg"), "gols esperados"),
                            "Disponibilidade no confronto": "desconhecida"})
        for formation in history.get("initial_formations", []):
            formations.append({"Equipe": name, "Formação inicial registrada": _formation_label(formation.get("formation")),
                               "Jogos nessa formação": formation.get("matches", len(formation.get("match_ids", []))),
                               "Jogos com formação inicial calculável": history.get("matches_with_initial_formation", 0),
                               "Parcela dos jogos calculáveis": measure(formation.get("share"), "%"),
                               "Período dos registros": _historical_period(profile, formation.get("match_ids", []))})
        for change in history.get("formation_changes", []):
            changes.append({"Equipe": name, "Data do registro": date_label(change.get("match_date")),
                            "Formação registrada na mudança": _formation_label(change.get("formation")),
                            "Tempo do registro": "1º tempo" if change.get("period") == 1 else "2º tempo",
                            "Jogos deste registro": 1})
    return players, formations, changes


def _exploration_markdown(payload):
    lines = ["### Sequências ofensivas observadas", "", SEQUENCE_LIMIT, "", *_markdown_table(_sequence_rows(payload)), ""]
    lines.extend([f"- {message}" for message in _sequence_warnings(payload)])
    players, formations, changes = _history_rows(payload)
    lines.extend(["", "### Padrões observados dos jogadores", "", HISTORY_LIMIT, "", *_markdown_table(players), "",
                  "### Formações históricas registradas", "", *_markdown_table(formations), "",
                  "### Mudanças de formação registradas", "", *_markdown_table(changes), ""])
    return lines


def render_v3_markdown(report) -> str:
    payload = _payload(report)
    lines = ["## Análises táticas observáveis — V3", ""]
    if not payload:
        return "\n".join(lines + ["Não disponível: esta análise não contém a extensão V3.", ""])
    if insufficient_core_evidence(report):
        lines.extend(["**Amostra insuficiente:** consulta descritiva. Não interpretar diferenças como superioridade. "
                      "Não são apresentadas hipóteses de ajuste.", ""])
    lines.extend(["Os indicadores abaixo descrevem ações registradas em partidas anteriores. "
                  "Não mostram posicionamento contínuo sem bola nem demonstram eficácia de um ajuste.", "",
                  "### Como o adversário ataca", "",
                  "Avanços, entradas e finalizações ajudam a selecionar situações para revisão em vídeo. "
                  "As faixas do campo não são chamadas de esquerda ou direita tática.", "",
                  *_markdown_table(_rows(payload)), "",
                  "### Como ele pressiona e recupera a bola", "",
                  "Tentativas de pressão e registros de recuperação são descritos separadamente. "
                  "A contagem não prova êxito nem que uma pressão causou uma recuperação.", "",
                  *_markdown_table(_rows(payload, pressure=True)), "",
                  *_exploration_markdown(payload),
                  "### Hipóteses para testar", ""])
    hypotheses = _hypotheses(report, payload)
    if not hypotheses:
        lines.append("Nenhuma hipótese V3 emitida: a amostra ou as evidências não atendem aos critérios operacionais.")
    for hypothesis in hypotheses:
        lines.extend([f"#### {hypothesis.get('title', 'Avaliação em treino ou vídeo')}", "",
                      f"**Observação registrada:** {hypothesis.get('observation', 'Não disponível.')}", "",
                      f"**O que testar:** {hypothesis.get('action', 'Rever os registros antes de decidir.')}", "",
                      f"**Condição:** {hypothesis.get('condition', 'Rever a amostra e os registros antes de testar.')}", ""])
        for field, label in (("preconditions", "Antes de testar"), ("risks", "Riscos"), ("limitations", "Limitações")):
            lines.extend([f"**{label}:**", "", *[f"- {item}" for item in _items(hypothesis.get(field))], ""])
    lines.extend(["", "Fonte: StatsBomb Open Data local. As partidas, denominadores, fórmulas e referências "
                  "de cada hipótese estão nos detalhes técnicos e no JSON. "
                  "Os indicadores não estimam probabilidade de vitória.", ""])
    return "\n".join(lines)


def render_v3_streamlit(report) -> None:
    import streamlit as st
    payload = _payload(report)
    st.header("Análises táticas observáveis — V3")
    if not payload:
        st.info("Não disponível: esta análise não contém a extensão V3.")
        return
    insufficient = insufficient_core_evidence(report)
    if insufficient:
        st.warning("Amostra insuficiente: consulta descritiva. Não interpretar diferenças como superioridade. "
                   "Não são apresentadas hipóteses de ajuste.")
    st.caption("Somente partidas anteriores. Ações registradas não representam posicionamento contínuo sem bola.")
    for heading, pressure in (("Como o adversário ataca", False), ("Como ele pressiona e recupera a bola", True)):
        st.subheader(heading)
        if pressure:
            st.caption("Tentativas de pressão não provam êxito. Registros de recuperação não demonstram causalidade com a pressão.")
        else:
            st.caption("Avanços e finalizações descrevem o histórico; as faixas não são interpretadas como esquerda ou direita tática.")
        rows = _rows(payload, pressure=pressure)
        if rows:
            if insufficient:
                st.caption("Consulta descritiva com amostra insuficiente; confira n e período de cada indicador.")
            st.dataframe(rows, hide_index=True, width="stretch")
        else:
            st.info("Não disponível: não há indicadores calculáveis desta família.")
    from .v3_plots import create_v3_figures
    import matplotlib.pyplot as plt
    figures = create_v3_figures(report)
    try:
        for figure in figures.values():
            st.pyplot(figure, clear_figure=False, width="stretch")
    finally:
        for figure in figures.values():
            plt.close(figure)
    st.subheader("Sequências ofensivas observadas")
    st.caption(SEQUENCE_LIMIT)
    rows = _sequence_rows(payload)
    if rows:
        st.dataframe(rows, hide_index=True, width="stretch")
    else:
        st.info("Não disponível: não há indicadores de sequências calculáveis.")
    for message in _sequence_warnings(payload):
        st.warning(message)
    st.subheader("Padrões observados dos jogadores")
    st.caption(HISTORY_LIMIT)
    players, formations, changes = _history_rows(payload)
    for heading, rows in (("Participações registradas — ordem alfabética", players),
                          ("Formações históricas registradas", formations),
                          ("Mudanças de formação registradas", changes)):
        st.markdown(f"#### {heading}")
        if rows:
            st.dataframe(rows, hide_index=True, width="stretch")
        else:
            st.info("Não disponível: não há registros verificáveis nesta janela.")
    st.subheader("Hipóteses para testar")
    hypotheses = _hypotheses(report, payload)
    if not hypotheses:
        st.info("Nenhuma hipótese V3 emitida: a amostra ou as evidências não atendem aos critérios operacionais.")
    for hypothesis in hypotheses:
        st.markdown(f"#### {hypothesis.get('title', 'Avaliação em treino ou vídeo')}")
        st.write("Observação registrada: " + hypothesis.get("observation", "Não disponível."))
        st.write("O que testar: " + hypothesis.get("action", "Rever os registros antes de decidir."))
        st.write("Condição: " + hypothesis.get("condition", "Rever a amostra e os registros antes de testar."))
        for field, label in (("preconditions", "Antes de testar"), ("risks", "Riscos"), ("limitations", "Limitações")):
            st.markdown(f"**{label}:**")
            for item in _items(hypothesis.get(field)):
                st.write("• " + item)
    st.caption("Fonte: StatsBomb Open Data local. Fórmulas, partidas e referências no JSON técnico. "
               "Não estima probabilidade de vitória.")
