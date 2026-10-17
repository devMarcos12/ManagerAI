"""Interface local opcional; eventos só são lidos ao clicar em Analisar."""
from datetime import date
import os
import importlib.util
from pathlib import Path

import streamlit as st

from .data_inventory import load_season, team_ids
from .data_loader import LocalData
from .coverage import preview_coverage
from .presentation.coach_report import build_coach_report, insufficient_core_evidence, metric_period
from .presentation.terminology import TERMS, date_label, number, count
from .report_renderer import render_markdown, render_technical_markdown
from .report_schema import AnalysisRequest
from .v3_schema import VALIDATED_RECUTS
from .ui_support import available_catalog, friendly_error, match_options, run_analysis

DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "open-data" / "data"
INPUT_ERRORS = (ValueError, OSError, KeyError, TypeError, AttributeError)


@st.cache_data(ttl=60, show_spinner=False)
def cached_catalog(root: str) -> list[dict]:
    return available_catalog(root)


@st.cache_data(ttl=60, show_spinner=False)
def cached_season(root: str, competition_id: int, season_id: int):
    return load_season(LocalData(root), competition_id, season_id)


def results(report) -> None:
    view = build_coach_report(report)
    st.header("Análise do confronto")
    for line in view.overview:
        st.write(line)
    for warning in view.warnings:
        st.warning(warning)
    st.subheader("Resumo para a comissão técnica")
    if not view.summary:
        st.info("Não há histórico comparável suficiente para descrever diferenças entre as equipes.")
    for line in view.summary:
        st.write("• " + line)
    st.info("Gols esperados (xG) somam os valores esperados das finalizações. Não são quantidade de chances, gols reais ou probabilidade de vencer.")
    st.subheader("Indicadores observados (consulta descritiva)")
    if insufficient_core_evidence(report):
        st.warning("Amostra insuficiente: não interpretar diferenças como superioridade. Consulte n e período de cada indicador.")
    st.caption("Por 90 min considera o tempo observado, incluindo acréscimos. Indisponível não significa zero.")
    st.dataframe(view.comparison, hide_index=True, width="stretch")
    with st.expander("Ajuda para ler os indicadores"):
        for row in view.comparison:
            st.write(f"**{row['Indicador']}** — {row['Como ler']}")
    st.subheader("O que merece atenção no adversário")
    if not view.attention:
        st.info("Sem jogos anteriores disponíveis para descrever o adversário.")
    for line in view.attention:
        st.write("• " + line)
    st.subheader("Possíveis ajustes para avaliar em treino ou vídeo")
    if not view.hypotheses:
        st.info("Não foram emitidas hipóteses: o histórico ou as evidências não atendem aos critérios mínimos.")
    for h in view.hypotheses:
        st.markdown(f"### {h.title}")
        st.write("**O que foi observado:** " + h.observed)
        st.write("**Por que importa:** " + h.why_it_matters)
        st.write("**O que verificar ou testar:** " + h.action)
        st.write("**Condição:** " + h.condition)
        for title, lines in (("Antes de testar", h.preconditions), ("Riscos", h.risks), ("Limitações", h.limitations)):
            st.write(f"**{title}:**")
            for line in lines:
                st.write("• " + line)
    st.subheader("Cenário declarado pelo treinador")
    st.write("Contexto, mando, objetivo e notas são informados manualmente. Não alteram o cálculo nem os critérios das hipóteses nesta versão.")
    st.write(f"Mando: {report.request.venue}; contexto: {report.request.match_context}; objetivo: {report.request.strategic_objective}.")
    st.text(report.request.notes or "Nenhuma nota informada.")
    st.subheader("O que o sistema ainda não consegue recomendar")
    st.write("Formação ideal e escalação não são suportadas nesta versão. Não são inferidos lesões, suspensões, disponibilidade atual, resultado ou eficácia comprovada de um ajuste.")
    st.caption("As faixas espaciais não são chamadas automaticamente de esquerda ou direita: a orientação ainda precisa ser validada.")
    with st.expander("Como a análise foi feita"):
        st.write("Somente jogos de datas anteriores à referência, até a janela escolhida. Menos de cinco jogos: nenhuma hipótese. Acima disso, a evidência continua limitada.")
        st.write("As sugestões vêm de regras transparentes. Nenhum modelo foi treinado e nenhuma LLM foi utilizada.")
        st.write("Fonte: StatsBomb Open Data; consulte as condições de atribuição do dataset ao compartilhar análises.")
    with st.expander("Todos os indicadores e detalhes técnicos"):
        advanced = []
        for key, term in TERMS.items():
            a, b = report.team_profile.metrics[key], report.opponent_profile.metrics[key]
            advanced.append({"Indicador": term.title, "Unidade": term.unit,
                             report.team_profile.team_name: number(a.value), report.opponent_profile.team_name: number(b.value),
                             "Jogos disponíveis": f"{a.sample_size} / {b.sample_size}",
                             "Período da equipe": metric_period(report.team_profile, a),
                             "Período do adversário": metric_period(report.opponent_profile, b), "Explicação": term.explanation})
        st.dataframe(advanced, hide_index=True, width="stretch")
        st.markdown(render_technical_markdown(report))
        st.json(report.to_dict())
    if getattr(report, "tactical_v3", None):
        from .v3_presentation import render_v3_streamlit
        render_v3_streamlit(report)
    # In-memory downloads: no arbitrary paths and no writes to past reports.
    st.download_button("Baixar relatório legível (.md)", render_markdown(report).encode("utf-8"),
                       file_name="managerai_relatorio.md", mime="text/markdown", key="download_md")
    st.download_button("Baixar relatório técnico (.json)", report.to_json().encode("utf-8"),
                       file_name="managerai_relatorio.json", mime="application/json", key="download_json")


def main() -> None:
    st.set_page_config(page_title="ManagerAI — preparação pré-jogo", page_icon="⚽", layout="wide")
    st.title("ManagerAI")
    st.write("Prepare um confronto histórico com indicadores observáveis e hipóteses para avaliar em treino ou vídeo.")
    st.caption("Análise histórica local. As informações não representam a situação atual dos clubes.")
    root = str(Path(os.environ.get("MANAGERAI_DATA_ROOT", DEFAULT_ROOT)).resolve())
    if st.button("Atualizar catálogo", help="Recarrega os metadados locais e limpa a análise exibida."):
        cached_catalog.clear(); cached_season.clear()
        st.session_state.pop("report", None)
        st.rerun()
    try:
        catalog = cached_catalog(root)
        if not catalog:
            st.error("Não há competições e temporadas com calendário local disponível.")
            return
        comps = {c["competition_id"]: c for c in catalog}
        comp_ids = sorted(comps, key=lambda cid: (comps[cid]["competition_name"], cid))
        default_comp = next((i for i, cid in enumerate(comp_ids) if comps[cid]["competition_name"] == "Premier League"), 0)
        cid = st.selectbox("Competição", comp_ids, index=default_comp,
                           format_func=lambda x: f"{comps[x]['competition_name']} — {comps[x].get('country_name', '')}", key="competition")
        seasons = {c["season_id"]: c for c in catalog if c["competition_id"] == cid}
        season_ids = sorted(seasons, key=lambda sid: seasons[sid]["season_name"], reverse=True)
        sid = st.selectbox("Temporada", season_ids, format_func=lambda x: seasons[x]["season_name"], key=f"season_{cid}")
        season = cached_season(root, cid, sid)
        data = LocalData(root)
        supported_teams = {t for m in season.matches if data.exists("events", m["match_id"]) for t in team_ids(m)}
        ids = sorted(supported_teams, key=lambda t: season.teams[t])
        if len(ids) < 2:
            st.error("Esta temporada não tem eventos locais para analisar duas equipes.")
            return
        default_team = next((i for i, tid in enumerate(ids) if season.teams[tid] == "Manchester City"), 0)
        tid = st.selectbox("Meu time", ids, index=default_team, format_func=season.teams.get, key=f"team_{cid}_{sid}")
        opponents = [t for t in ids if t != tid]
        default_opponent = next((i for i, oid in enumerate(opponents) if season.teams[oid] == "Arsenal"), 0)
        oid = st.selectbox("Adversário", opponents, index=default_opponent, format_func=season.teams.get, key=f"opponent_{cid}_{sid}_{tid}")
        mode = st.radio("Referência da análise", ["Partida histórica", "Data de corte livre"], key="reference_mode",
                        help="Os modos são exclusivos. Só usamos datas anteriores à referência; o próprio dia é excluído.")
        target, cutoff = None, None
        matches = match_options(season, tid, oid)
        can_submit = True
        if mode == "Partida histórica":
            if not matches:
                st.info("Não há partida histórica deste confronto no recorte. Use uma data de corte livre.")
                can_submit = False
            else:
                lookup = {m["match_id"]: m for m in matches}
                target = st.selectbox("Partida de referência", list(lookup), format_func=lambda x: lookup[x]["label"], key=f"match_{cid}_{sid}_{tid}_{oid}")
                st.caption(f"Data: {date_label(lookup[target]['date'])}. Mando formal do seu time: {lookup[target]['formal_venue']}. O placar não é usado como evidência pré-jogo.")
        else:
            latest = max(m["match_date"] for m in season.matches)
            cutoff = st.date_input("Data de referência", value=date.fromisoformat(latest), key=f"cutoff_{cid}_{sid}",
                                   help="Mesmo dia e datas posteriores ficam fora da análise.").isoformat()
        window = st.number_input("Jogos anteriores por equipe", min_value=1, max_value=100, value=10, step=1, key="window",
                                 help="Até N jogos anteriores do calendário desta temporada. Ausências não ampliam a janela.")
        if can_submit:
            preview = preview_coverage(data, AnalysisRequest(cid, sid, tid, oid, cutoff_date=cutoff,
                                       target_match_id=target, recent_matches_window=int(window)), season)
            st.subheader("Cobertura antes da análise")
            for c in (preview.team, preview.opponent):
                st.write(f"**{c.team_name}**: {count(c.calendar_matches_before_cutoff)} no calendário antes do corte; "
                         f"{count(c.selected_matches)} na janela; {count(c.matches_with_events)} com arquivo de eventos.")
                st.caption(f"Período disponível no calendário: {date_label(c.available_period_start)} a {date_label(c.available_period_end)}. "
                           f"Período da janela: {date_label(c.selected_period_start)} a {date_label(c.selected_period_end)}.")
            for warning in preview.warnings:
                st.warning(warning)
            st.caption(preview.policy)
        has_v3_plots = importlib.util.find_spec("matplotlib") is not None
        if not has_v3_plots or (cid, sid) not in VALIDATED_RECUTS:
            st.session_state["include_v3"] = False
        include_v3 = st.checkbox("Incluir análise tática por eventos (V3)", value=False, key="include_v3", disabled=not has_v3_plots or (cid, sid) not in VALIDATED_RECUTS,
                                 help="Acrescenta progressão, finalizações por zonas, pressão espacial e gráficos; sem LLM ou escalação sugerida.")
        if (cid, sid) not in VALIDATED_RECUTS:
            include_v3 = False
            st.info("V3 validada para Premier League 2015/16 e La Liga 2020/21. Outros recortes continuam disponíveis na análise anterior; exigem auditoria antes da extensão V3.")
        if not has_v3_plots:
            st.info("Visualizações V3 indisponíveis neste ambiente. Consulte a instalação opcional no tutorial V3; a análise anterior continua disponível.")
        selector = (root, cid, sid, tid, oid, mode, target, cutoff, int(window), include_v3)
        if st.session_state.get("selector") != selector:
            st.session_state.pop("report", None)
            st.session_state["selector"] = selector
        with st.form("analysis_form"):
            st.caption("Cenário manual: os campos abaixo não alteram os cálculos nem os critérios das hipóteses nesta versão.")
            venue = st.selectbox("Mando informado", ["desconhecido", "casa", "fora", "neutro"], key="venue")
            context = st.selectbox("Contexto informado", ["regular", "clássico", "eliminatório", "decisivo", "outro"], key="context")
            objective = st.selectbox("Objetivo de planejamento", ["equilibrado", "pressionar alto", "proteger vantagem", "buscar gol", "outro"], key="objective")
            notes = st.text_area("Notas do treinador", max_chars=4000, key="notes")
            st.caption("Não há seletor de atletas nesta versão: ainda não recomendamos escalações ou substitutos.")
            submitted = st.form_submit_button("Analisar confronto", disabled=not can_submit)
        if submitted:
            st.session_state.pop("report", None)
            request = AnalysisRequest(cid, sid, tid, oid, cutoff_date=cutoff, target_match_id=target,
                                      recent_matches_window=int(window), venue=venue, match_context=context,
                                      strategic_objective=objective, notes=notes)
            with st.spinner("Consultando partidas anteriores e preparando o relatório…"):
                if include_v3:
                    from .pipeline import analyze
                    st.session_state["report"] = analyze(root, request, include_v3=True)
                else:
                    st.session_state["report"] = run_analysis(root, request)
        if "report" in st.session_state:
            report = st.session_state["report"]
            st.caption(f"Resultado da última análise enviada: janela de {count(report.request.recent_matches_window)}. "
                       "Ao editar o formulário, clique em Analisar confronto para atualizar o resultado e os downloads.")
            results(report)
    except INPUT_ERRORS as exc:
        st.session_state.pop("report", None)
        st.error(friendly_error(exc))
