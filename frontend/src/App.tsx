import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react';
import { api, errorMessage, type AnalysisRequest, type Coverage, type Report, type Schema } from './api';
import { contexts, explanations, objectives, planIds, strategies, venues } from './generated/options';
import { date, planLabels, strategyLabels } from './format';
import { useDebounced, useRemote } from './useRemote';
import ReportView from './ReportView';

type Analysis = Schema['AnalysisPayload'];
interface FormState {
  competition: number; season: number; team: number; opponent: number; target: number;
  reference: 'match' | 'cutoff'; cutoff: string; window: number; v3: boolean;
  venue: NonNullable<Analysis['venue']>; context: NonNullable<Analysis['match_context']>;
  objective: NonNullable<Analysis['strategic_objective']>; strategy: NonNullable<AnalysisRequest['intended_strategy']>;
  blocked: NonNullable<AnalysisRequest['blocked_plan_ids']>; notes: string;
  explanation: NonNullable<AnalysisRequest['explanation']>;
}
const initial: FormState = { competition: 0, season: 0, team: 0, opponent: 0, target: 0, reference: 'match', cutoff: '', window: 10,
  v3: false, venue: 'desconhecido', context: 'regular', objective: 'equilibrado', strategy: 'equilibrada', blocked: [], notes: '', explanation: 'none' };
const explanationLabels = { none: 'Não executar (padrão)', optional: 'Executar, mantendo relatório em caso de falha', required: 'Exigir explicação válida para concluir' };

function CoverageView({ value }: { value: Coverage }) {
  return <section className="coverage" aria-label="Cobertura do histórico"><h3>Antes de analisar</h3><div className="coverage-grid">
    {[value.team, value.opponent].map(team => <div key={team.team_id}><h4>{team.team_name}</h4><strong>{team.event_match_ids.length}<span> de {team.selected_match_ids.length} jogos com arquivo de eventos</span></strong>
      <p>{date(team.selected_period_start)} a {date(team.selected_period_end)}</p>
      <p className="small">{team.calendar_matches_before_cutoff} anteriores no calendário · {team.missing_event_match_ids.length} sem arquivo na janela</p>
      {team.warnings.map(w => <p className="coverage-warning" key={w}>{w}</p>)}</div>)}
  </div><p className="small muted">Presença de arquivos não certifica qualidade do conteúdo. Amostra insuficiente permite consulta descritiva, sem promessa de planos.</p></section>;
}

export default function App() {
  const [refresh, setRefresh] = useState(0);
  const boot = useRemote(`bootstrap-${refresh}`, api.bootstrap);
  const [form, setForm] = useState<FormState>(initial);
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const busyGuard = useRef(false);
  const [slow, setSlow] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [report, setReport] = useState<Report | null>(null);
  const [sentKey, setSentKey] = useState('');
  const resultHeading = useRef<HTMLElement>(null);
  const catalog = boot.data?.catalog;
  const capabilities = boot.data?.capabilities;
  const maxWindow = capabilities?.limits.window ?? 20;
  useEffect(() => {
    if (!catalog?.length) return;
    setForm(f => {
      if (catalog.some(c => c.competition_id === f.competition && c.season_id === f.season)) return f;
      const first = catalog.find(c => c.competition_name === 'Premier League') || catalog[0];
      return { ...initial, competition: first.competition_id, season: first.season_id, window: Math.min(10, maxWindow) };
    });
  }, [catalog, maxWindow]);
  const season = useRemote(form.competition && form.season ? `${form.competition}/${form.season}` : null,
    signal => api.season(form.competition, form.season, signal));
  const teams = useMemo(() => [...(season.data?.teams || [])].sort((a, b) => a.name.localeCompare(b.name)), [season.data]);
  const matches = season.data?.matches;
  useEffect(() => {
    if (!teams.length || !matches) return;
    setForm(f => {
      const team = teams.some(t => t.team_id === f.team) ? f.team : teams[0].team_id;
      const opponent = teams.some(t => t.team_id === f.opponent && t.team_id !== team) ? f.opponent : teams.find(t => t.team_id !== team)?.team_id || 0;
      const cutoff = f.cutoff || [...matches].map(m => m.date).sort().at(-1) || '';
      return team === f.team && opponent === f.opponent && cutoff === f.cutoff ? f : { ...f, team, opponent, cutoff, target: 0 };
    });
  }, [teams, matches]);
  const pairMatches = useMemo(() => (matches || []).filter(m => (m.home_team_id === form.team && m.away_team_id === form.opponent)
    || (m.home_team_id === form.opponent && m.away_team_id === form.team)).sort((a, b) => b.date.localeCompare(a.date)), [matches, form.team, form.opponent]);
  useEffect(() => {
    if (pairMatches.some(m => m.match_id === form.target)) return;
    setForm(f => ({ ...f, target: pairMatches[0]?.match_id || 0 }));
  }, [pairMatches, form.target]);
  const v3Certified = !!catalog?.find(c => c.competition_id === form.competition && c.season_id === form.season)?.v3_certified;
  const ready = !!season.data && form.team > 0 && form.opponent > 0 && form.team !== form.opponent &&
    Number.isInteger(form.window) && form.window >= 1 && form.window <= maxWindow &&
    (form.reference === 'match' ? pairMatches.some(m => m.match_id === form.target) : /^\d{4}-\d{2}-\d{2}$/.test(form.cutoff));
  const request = useMemo<AnalysisRequest>(() => ({ schema_version: '2.0.0', analysis: {
    competition_id: form.competition, season_id: form.season, team_id: form.team, opponent_id: form.opponent,
    ...(form.reference === 'match' ? { target_match_id: form.target } : { cutoff_date: form.cutoff }),
    recent_matches_window: form.window, venue: form.venue, match_context: form.context, strategic_objective: form.objective, notes: form.notes,
  }, include_v3: form.v3, intended_strategy: form.strategy, blocked_plan_ids: form.blocked, roster: [], engine: 'deterministic', explanation: form.explanation }), [form]);
  const requestKey = JSON.stringify(request); // Pedido pequeno; nunca serializar o relatório para renderizar.
  const debouncedKey = useDebounced(ready ? requestKey : null);
  const preview = useRemote(ready ? debouncedKey : null, signal => api.coverage(JSON.parse(debouncedKey!), signal));
  const currentPreview = preview.key === requestKey && preview.data ? preview.data : undefined;
  const changed = !!sentKey && requestKey !== sentKey;
  useEffect(() => {
    if (!report) return;
    resultHeading.current?.focus({ preventScroll: true });
    resultHeading.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [report]);
  function update<K extends keyof FormState>(key: K, value: FormState[K]) { setForm(f => ({ ...f, [key]: value })); }
  function changeSeason(competition: number, seasonId: number) {
    setForm(f => ({ ...f, competition, season: seasonId, team: 0, opponent: 0, target: 0, cutoff: '', v3: false, venue: 'desconhecido' }));
    setNotice('Recorte alterado: equipes, referência, mando e V3 foram redefinidos. Confira as novas escolhas.');
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!ready || !currentPreview || busyGuard.current) return;
    busyGuard.current = true; setBusy(true); setSlow(false); setAnalysisError(''); setReport(null); setSentKey(requestKey);
    const timer = setTimeout(() => setSlow(true), 12000);
    try { setReport(await api.analyze(request)); }
    catch (e) { setAnalysisError(errorMessage(e)); }
    finally { clearTimeout(timer); busyGuard.current = false; setBusy(false); setSlow(false); }
  }
  const competitionList = useMemo(() => [...new Map((catalog || []).map(c => [c.competition_id, c])).values()].sort((a, b) => a.competition_name.localeCompare(b.competition_name)), [catalog]);
  const name = (id: number) => teams.find(t => t.team_id === id)?.name || 'Equipe';
  return <>
    <a className="skip-link" href="#preparar">Ir para preparação do confronto</a>
    <header className="masthead"><a className="brand" href="./" aria-label="ManagerAI início"><span className="brand-symbol" aria-hidden="true">M<span>↗</span></span>Manager<span>AI</span></a><span className="header-caption">Inteligência no preparo. Critério na decisão.</span><span className="local-label">Análise histórica local</span></header>
    <main>
      <section className="intro"><div><div className="section-kicker">Preparação de jogo</div><h1>Leia o histórico.<br /><em>Prepare as perguntas certas.</em></h1><p>Compare equipes, investigue padrões e leve hipóteses fundamentadas para o vídeo e o treino.</p></div><div className="intro-note"><span className="mini-pitch" aria-hidden="true"><i /></span><p>O histórico informa.<br /><strong>A decisão continua com você.</strong></p></div></section>
      {boot.loading && <p role="status" className="notice">Conectando ao catálogo local…</p>}
      {boot.error !== undefined && <section className="connection-error" role="alert"><h2>Não foi possível acessar os dados</h2><p>{errorMessage(boot.error)}</p><button onClick={() => setRefresh(x => x + 1)}>Tentar conexão novamente</button></section>}
      {boot.data && !catalog?.length && <p className="notice">Nenhuma competição com calendário local foi encontrada. Confira o provisionamento dos dados.</p>}
      {boot.data && !!catalog?.length && <div className="workspace">
        <aside className="preparation"><form onSubmit={submit} id="preparar"><div className="section-kicker">01 · Preparar</div><h2>Escolha o confronto</h2><p className="muted small">Use o histórico disponível da mesma temporada.</p>
          <label htmlFor="competition">Competição</label><select id="competition" value={form.competition} onChange={e => { const id = +e.target.value; changeSeason(id, catalog.find(c => c.competition_id === id)!.season_id); }}>{competitionList.map(c => <option key={c.competition_id} value={c.competition_id}>{c.competition_name}{c.country_name ? ` · ${c.country_name}` : ''}</option>)}</select>
          <label htmlFor="season">Temporada</label><select id="season" value={form.season} onChange={e => changeSeason(form.competition, +e.target.value)}>{catalog.filter(c => c.competition_id === form.competition).map(c => <option key={c.season_id} value={c.season_id}>{c.season_name}</option>)}</select>
          {notice && <p role="status" className="small reset-notice">{notice}</p>}
          <div className="field-pair"><div><label htmlFor="team">Minha equipe</label><select id="team" disabled={!teams.length} value={form.team || ''} onChange={e => { const id = +e.target.value; setForm(f => ({ ...f, team: id, target: 0, opponent: f.opponent === id ? teams.find(t => t.team_id !== id)?.team_id || 0 : f.opponent })); }}>{!form.team && <option value="">Carregando…</option>}{teams.map(t => <option key={t.team_id} value={t.team_id}>{t.name}</option>)}</select></div>
          <div><label htmlFor="opponent">Adversário</label><select id="opponent" disabled={!teams.length} value={form.opponent || ''} onChange={e => setForm(f => ({ ...f, opponent: +e.target.value, target: 0 }))}>{!form.opponent && <option value="">Carregando…</option>}{teams.filter(t => t.team_id !== form.team).map(t => <option key={t.team_id} value={t.team_id}>{t.name}</option>)}</select></div></div>
          {season.error !== undefined && <p className="error" role="alert">{errorMessage(season.error)}</p>}
          <fieldset className="reference"><legend>Referência temporal</legend><label className="radio"><input type="radio" name="reference" checked={form.reference === 'match'} onChange={() => update('reference', 'match')} />Partida histórica</label><label className="radio"><input type="radio" name="reference" checked={form.reference === 'cutoff'} onChange={() => update('reference', 'cutoff')} />Data de corte</label></fieldset>
          {form.reference === 'match' ? <><label htmlFor="target">Partida de referência</label><select id="target" disabled={!pairMatches.length} value={form.target || ''} onChange={e => update('target', +e.target.value)}>{!pairMatches.length && <option value="">Sem partida deste confronto</option>}{pairMatches.map(m => <option key={m.match_id} value={m.match_id}>{date(m.date)} · {name(m.home_team_id)} × {name(m.away_team_id)}</option>)}</select>{!pairMatches.length && !season.loading && <p className="small field-error">Não há confronto no calendário. Use uma data de corte.</p>}</> : <><label htmlFor="cutoff">Data de referência</label><input id="cutoff" type="date" value={form.cutoff} required onChange={e => update('cutoff', e.target.value)} /></>}
          <label htmlFor="window">Jogos anteriores por equipe</label><input id="window" type="number" min="1" max={maxWindow} step="1" value={form.window || ''} onChange={e => update('window', +e.target.value)} aria-describedby="window-policy" />
          {(!Number.isInteger(form.window) || form.window < 1 || form.window > maxWindow) && <p className="field-error">Informe de 1 a {maxWindow} jogos.</p>}
          <p className="small muted" id="window-policy">Todo o dia da referência fica de fora. Arquivos ausentes não são repostos por jogos mais antigos; temporadas não são misturadas.</p>
          <div className="declarations"><h3>Contexto informado</h3><p className="small muted">Declarações do treinador, sem alterar os indicadores históricos.</p>
            <label htmlFor="venue">Mando declarado</label><select id="venue" value={form.venue} onChange={e => update('venue', e.target.value as FormState['venue'])}>{venues.map(v => <option key={v}>{v}</option>)}</select>
            <label htmlFor="context">Contexto</label><select id="context" value={form.context} onChange={e => update('context', e.target.value as FormState['context'])}>{contexts.map(c => <option key={c}>{c}</option>)}</select>
            <label htmlFor="objective">Objetivo declarado</label><select id="objective" value={form.objective} onChange={e => update('objective', e.target.value as FormState['objective'])}>{objectives.map(o => <option key={o}>{o}</option>)}</select>
            {form.objective === 'pressionar alto' && <p className="small muted">Não há plano validado para priorizar pressão da própria equipe. Este objetivo permanece apenas como declaração.</p>}
          </div>
          <label className="checkbox v3-toggle"><input type="checkbox" disabled={!v3Certified} checked={form.v3} onChange={e => update('v3', e.target.checked)} /><span>Incluir análise por eventos (V3)</span></label><p className="small muted">{v3Certified ? 'Recorte certificado: indicadores adicionais e gráficos disponíveis.' : 'V3 indisponível: esta temporada não está na lista de recortes certificados.'}</p>
          <details className="advanced"><summary>Opções avançadas</summary>
            <label htmlFor="strategy">Estratégia pretendida</label><select id="strategy" value={form.strategy} onChange={e => update('strategy', e.target.value as FormState['strategy'])}>{strategies.map(s => <option key={s} value={s}>{strategyLabels[s]}</option>)}</select>
            <fieldset><legend>Opções que não deseja investigar</legend>{planIds.map(id => <label key={id} className="checkbox"><input type="checkbox" checked={form.blocked.includes(id)} onChange={e => update('blocked', e.target.checked ? [...form.blocked, id] : form.blocked.filter(x => x !== id))} />{planLabels[id]}</label>)}</fieldset>
            <label htmlFor="notes">Notas do treinador</label><textarea id="notes" rows={3} maxLength={4000} value={form.notes} onChange={e => update('notes', e.target.value)} /><small className="muted">{form.notes.length}/4.000 caracteres. As notas não entram no prompt da LLM.</small>
            <label htmlFor="explanation">Explicação opcional</label><select id="explanation" disabled={!capabilities?.llm.configured} value={form.explanation} onChange={e => update('explanation', e.target.value as FormState['explanation'])}>{explanations.map(x => <option key={x} value={x}>{explanationLabels[x]}</option>)}</select>
            <p className="small muted">{capabilities?.llm.configured ? 'Provedor configurado; disponibilidade só é confirmada ao executar. ' : 'Nenhum provedor configurado no servidor. '}A LLM apenas seleciona afirmações autorizadas; o texto é materializado pelo Core. Não é raciocínio tático aprendido.</p>
            <p className="small muted">Elenco atual não é informado nesta interface. A análise é coletiva e não sugere escalação ideal ou disponibilidade de atletas.</p>
          </details>
          <div className="submit-area">{analysisError && <p role="alert" className="error">{analysisError}</p>}<button className="primary" type="submit" disabled={!ready || !currentPreview || busy}>{busy ? 'Analisando histórico…' : 'Analisar confronto'}<span aria-hidden="true">↗</span></button>
            {busy && <p role="status" className="small">{slow ? 'A análise está demorando. O cálculo pode continuar no servidor; não reenviamos pedidos automaticamente.' : 'Calculando indicadores e verificando evidências…'}{changed && ' O formulário mudou; o resultado será associado ao pedido já enviado.'}</p>}
          </div>
        </form></aside>
        <section className="analysis-space" tabIndex={-1} ref={resultHeading} aria-label="Área de análise">
          {ready && !currentPreview && preview.error === undefined && <p role="status" className="notice">Conferindo cobertura do recorte selecionado…</p>}
          {preview.key === requestKey && preview.error !== undefined && <p role="alert" className="error">{errorMessage(preview.error)}</p>}
          {currentPreview && <CoverageView value={currentPreview} />}
          {report ? <ReportView key={report.report_key} report={report} changed={changed} /> : <div className="empty-report"><div className="section-kicker">02 · Investigar</div><h2>{busy ? 'Um recorte de cada vez.' : 'Da evidência à conversa de campo.'}</h2><p>{busy ? 'O relatório usará exclusivamente o pedido enviado. Você pode revisar as escolhas enquanto aguarda.' : 'Confira a cobertura e solicite a análise. Aqui você encontrará comparações históricas, planos condicionais e as evidências de cada opção.'}</p><div className="empty-steps"><span><b>01</b> Compare o histórico</span><span><b>02</b> Examine condições e riscos</span><span><b>03</b> Leve perguntas para o treino</span></div><p className="small muted">Ausência de evidência gera abstenção. O sistema não prevê vitória nem comprova a eficácia de uma estratégia.</p></div>}
        </section>
      </div>}
    </main><footer><span>ManagerAI · Preparação com evidência</span><span>Fonte: StatsBomb Open Data · Histórico disponível, sem disponibilidade atual presumida.</span></footer>
  </>;
}
