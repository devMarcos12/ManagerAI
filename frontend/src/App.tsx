import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react';
import { api, errorMessage, type AnalysisRequest, type CoachTeam, type Coverage, type Report, type Schema, type TeamPreview, type TeamReport, type TeamRequest } from './api';
import { contexts, explanations, objectives, planIds, strategies, venues } from './generated/options';
import { date, planLabels, strategyLabels } from './format';
import { nextDay, normalize, recutKey, resolveRecut } from './coach';
import { useDebounced, useRemote } from './useRemote';
import ReportView from './ReportView';
import TeamOverview from './TeamOverview';

type Analysis = Schema['AnalysisPayload'];
interface FormState {
  team: number; cutoff: string; window: number; recut: string; compare: boolean; opponent: number;
  reference: 'match' | 'cutoff'; target: number; v3: boolean; quality: boolean;
  venue: NonNullable<Analysis['venue']>; context: NonNullable<Analysis['match_context']>;
  objective: NonNullable<Analysis['strategic_objective']>; strategy: NonNullable<AnalysisRequest['intended_strategy']>;
  blocked: NonNullable<AnalysisRequest['blocked_plan_ids']>; notes: string;
  explanation: NonNullable<AnalysisRequest['explanation']>; ai: boolean;
}
const initial: FormState = { team: 0, cutoff: '', window: 10, recut: '', compare: false, opponent: 0,
  reference: 'cutoff', target: 0, v3: false, quality: false, venue: 'desconhecido', context: 'regular',
  objective: 'equilibrado', strategy: 'equilibrada', blocked: [], notes: '', explanation: 'none', ai: true };
const explanationLabels = { none: 'Sem explicação adicional', optional: 'Incluir, se disponível', required: 'Exigir explicação adicional' };
const venueLabels = { casa: 'Em casa', fora: 'Fora de casa', neutro: 'Campo neutro', desconhecido: 'Ainda não definido' };
type Result = { kind: 'team'; data: TeamReport } | { kind: 'comparison'; data: Report };

function TeamSearch({ teams, selected, onChange }: { teams: CoachTeam[]; selected?: CoachTeam; onChange: (team?: CoachTeam) => void }) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const matches = teams.filter(t => t.aliases.some(name => normalize(name).includes(normalize(query))));
  const options = matches.slice(0, 30);
  function choose(team: CoachTeam) { onChange(team); setQuery(team.name); setOpen(false); }
  return <div className="team-search"><label htmlFor="team-search">Qual é o seu time?</label>
    <input id="team-search" role="combobox" type="search" autoComplete="off" placeholder="Busque pelo nome do time" value={selected ? selected.name : query}
      aria-expanded={open} aria-controls="team-results" aria-autocomplete="list" aria-activedescendant={open && options[active] ? `team-option-${options[active].team_id}` : undefined}
      onFocus={() => setOpen(true)} onBlur={() => setOpen(false)}
      onChange={e => { setQuery(e.target.value); setActive(0); setOpen(true); onChange(undefined); }}
      onKeyDown={e => {
        if (e.key === 'ArrowDown') { e.preventDefault(); setOpen(true); setActive(a => Math.min(a + 1, options.length - 1)); }
        if (e.key === 'ArrowUp') { e.preventDefault(); setActive(a => Math.max(a - 1, 0)); }
        if (e.key === 'Escape') setOpen(false);
        if (e.key === 'Enter' && open) { e.preventDefault(); if (options[active]) choose(options[active]); }
      }} />
    {open && <><ul id="team-results" role="listbox" aria-label="Times disponíveis">{options.map((team, index) => <li id={`team-option-${team.team_id}`} role="option" aria-selected={index === active} key={team.team_id}
      onMouseDown={e => e.preventDefault()} onClick={() => choose(team)} onMouseEnter={() => setActive(index)}>
      <strong>{team.name}</strong><small>{team.recuts[0]?.competition_name} · {team.recuts[0]?.season_name}{team.recuts[0]?.competition_gender ? ` · ${team.recuts[0].competition_gender === 'female' ? 'Feminino' : 'Masculino'}` : ''}</small>
    </li>)}</ul>{!options.length && <p className="small notice" role="status">Nenhum time encontrado no histórico disponível.</p>}{matches.length > 30 && <p className="small muted">Digite mais letras para refinar a busca.</p>}</>}
  </div>;
}

function CoverageView({ value }: { value: Coverage | TeamPreview }) {
  const profiles = 'opponent' in value ? [value.team, value.opponent] : [value.team];
  return <section className="coverage" aria-label="Cobertura do histórico"><h3>Histórico que será analisado</h3><div className="coverage-grid">
    {profiles.map(team => <div key={team.team_id}><h4>{team.team_name}</h4><strong>{team.event_match_ids.length}<span> de {team.selected_match_ids.length} jogos com eventos</span></strong>
      <p>{date(team.selected_period_start)} a {date(team.selected_period_end)}</p>
      {team.missing_event_match_ids.length > 0 && <p className="coverage-warning">{team.missing_event_match_ids.length} jogos sem arquivo; a janela não será ampliada.</p>}
      {team.warnings.map(w => <p className="coverage-warning" key={w}>{w}</p>)}</div>)}
  </div><p className="small muted">Só entram jogos anteriores ao dia do corte, da temporada indicada. A amostra calculável pode variar por indicador.</p></section>;
}

export default function App() {
  const [refresh, setRefresh] = useState(0);
  const boot = useRemote(`bootstrap-${refresh}`, async signal => {
    const [base, index] = await Promise.all([api.bootstrap(signal), api.coachTeams(signal)]);
    return { ...base, index };
  });
  const [form, setForm] = useState<FormState>(initial);
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const busyGuard = useRef(false);
  const [slow, setSlow] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [result, setResult] = useState<Result | null>(null);
  const [sentKey, setSentKey] = useState('');
  const resultHeading = useRef<HTMLElement>(null);
  const capabilities = boot.data?.capabilities;
  const maxWindow = capabilities?.limits.window ?? 20;
  const selected = boot.data?.index.teams.find(t => t.team_id === form.team);
  const recuts = selected?.recuts || [];
  const recut = resolveRecut(recuts, form.cutoff, form.recut);
  const seasonKey = recut ? recutKey(recut) : null;
  const season = useRemote(form.compare ? seasonKey : null, signal => api.season(recut!.competition_id, recut!.season_id, signal));
  const teams = useMemo(() => [...(season.data?.teams || [])].sort((a, b) => a.name.localeCompare(b.name)), [season.data]);
  const pairMatches = useMemo(() => (season.data?.matches || []).filter(m => (m.home_team_id === form.team && m.away_team_id === form.opponent)
    || (m.home_team_id === form.opponent && m.away_team_id === form.team)).sort((a, b) => b.date.localeCompare(a.date) || b.match_id - a.match_id), [season.data, form.team, form.opponent]);
  const target = pairMatches.find(m => m.match_id === form.target);
  useEffect(() => {
    if (pairMatches.some(m => m.match_id === form.target)) return;
    setForm(f => ({ ...f, target: pairMatches[0]?.match_id || 0 }));
  }, [pairMatches, form.target]);
  const v3Certified = !!boot.data?.catalog.find(c => c.competition_id === recut?.competition_id && c.season_id === recut?.season_id)?.v3_certified;
  const venue = form.reference === 'match' && target ? (target.home_team_id === form.team ? 'casa' : 'fora') : form.venue;
  const validDate = /^\d{4}-\d{2}-\d{2}$/.test(form.cutoff) && !Number.isNaN(Date.parse(form.cutoff)) && new Date(form.cutoff).toISOString().slice(0, 10) === form.cutoff;
  const ready = !!selected && !!recut && Number.isInteger(form.window) && form.window >= 1 && form.window <= maxWindow && validDate &&
    (!form.compare || (!!season.data && teams.some(t => t.team_id === form.opponent && t.team_id !== form.team) && (form.reference !== 'match' || !!target)));
  const teamRequest: TeamRequest = { competition_id: recut?.competition_id || 0, season_id: recut?.season_id || 0,
    team_id: form.team, cutoff_date: form.cutoff, recent_matches_window: form.window };
  const pairRequest: AnalysisRequest = { schema_version: '2.0.0', analysis: {
    competition_id: teamRequest.competition_id, season_id: teamRequest.season_id, team_id: form.team, opponent_id: form.opponent,
    ...(form.reference === 'match' ? { target_match_id: form.target } : { cutoff_date: form.cutoff }),
    recent_matches_window: form.window, venue, match_context: form.context, strategic_objective: form.objective, notes: form.notes,
  }, ...(form.ai && capabilities?.tactical_advisor?.configured ? { ai_analysis: 'optional' as const } : {}), include_v3: form.v3, ...(form.quality ? { data_policy: 'quality_v1' as const } : {}), intended_strategy: form.strategy, blocked_plan_ids: form.blocked, roster: [], engine: 'deterministic', explanation: form.explanation };
  const requestKey = ready ? JSON.stringify(form.compare ? { kind: 'comparison', body: pairRequest } : { kind: 'team', body: teamRequest }) : '';
  const debouncedKey = useDebounced(requestKey || null);
  const preview = useRemote(ready ? debouncedKey : null, signal => {
    const request = JSON.parse(debouncedKey!) as { kind: string; body: AnalysisRequest & TeamRequest };
    return request.kind === 'team' ? api.teamCoverage(request.body, signal) : api.coverage(request.body, signal);
  });
  const currentPreview = preview.key === requestKey && preview.data ? preview.data : undefined;
  const changed = !!sentKey && requestKey !== sentKey;
  useEffect(() => {
    if (!result) return;
    resultHeading.current?.focus({ preventScroll: true });
    resultHeading.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [result]);
  function update<K extends keyof FormState>(key: K, value: FormState[K]) { setForm(f => ({ ...f, [key]: value })); }
  function changeTeam(team?: CoachTeam) {
    setForm(f => ({ ...initial, window: Math.min(f.window || 10, maxWindow), team: team?.team_id || 0,
      cutoff: team ? nextDay(team.recuts[0].last_date) : f.cutoff }));
    setNotice(''); setAnalysisError('');
  }
  function changeRecut(value: string) {
    setForm(f => ({ ...f, recut: value, opponent: 0, target: 0, reference: 'cutoff', v3: false, venue: 'desconhecido' }));
    setNotice('Histórico alterado. Escolha novamente o adversário; os resultados anteriores continuam identificados pelo pedido original.');
  }
  function changeCutoff(value: string) {
    setForm(f => ({ ...f, cutoff: value, recut: '', opponent: 0, target: 0, reference: 'cutoff', v3: false, venue: 'desconhecido' }));
    if (form.compare) setNotice('Data alterada. Confira o histórico identificado e escolha novamente o adversário.');
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!ready || !currentPreview || busyGuard.current) return;
    busyGuard.current = true; setBusy(true); setSlow(false); setAnalysisError(''); setResult(null); setSentKey(requestKey);
    const timer = setTimeout(() => setSlow(true), 12000);
    try {
      setResult(form.compare ? { kind: 'comparison', data: await api.analyze(pairRequest) } : { kind: 'team', data: await api.analyzeTeam(teamRequest) });
    } catch (e) { setAnalysisError(errorMessage(e)); }
    finally { clearTimeout(timer); busyGuard.current = false; setBusy(false); setSlow(false); }
  }
  const name = (id: number) => teams.find(t => t.team_id === id)?.name || 'Equipe';
  const recutOptions = <><option value="">Identificar pela data</option>{recuts.map(r => <option key={recutKey(r)} value={recutKey(r)}>{r.competition_name} · {r.season_name}</option>)}</>;
  return <>
    <a className="skip-link" href="#preparar">Ir para preparação do confronto</a>
    <header className="masthead"><a className="brand" href="./" aria-label="ManagerAI início"><span className="brand-symbol" aria-hidden="true">M<span>↗</span></span>Manager<span>AI</span></a><span className="header-caption">Análise de equipes</span><span className="local-label">StatsBomb Open Data</span></header>
    <main><section className="intro coach-intro"><div><h1>Conheça o momento<br />do seu time.</h1><p>Escolha o time e o histórico. Adicione um adversário quando quiser preparar o confronto.</p></div></section>
      {boot.loading && <p role="status" className="notice">Carregando os times disponíveis…</p>}
      {boot.error !== undefined && <section className="connection-error" role="alert"><h2>Não foi possível acessar os dados</h2><p>{errorMessage(boot.error)}</p><button onClick={() => setRefresh(x => x + 1)}>Tentar conexão novamente</button></section>}
      {boot.data && !boot.data.index.teams.length && <p className="notice">Nenhum time com calendário local foi encontrado. Confira a instalação dos dados.</p>}
      {boot.data?.index.warnings.map(w => <p className="notice" key={w}>{w}</p>)}
      {boot.data && !!boot.data.index.teams.length && <div className="workspace">
        <aside className="preparation"><form onSubmit={submit} id="preparar"><h2>Comece pelo seu time</h2>
          <TeamSearch teams={boot.data.index.teams} selected={selected} onChange={changeTeam} />
          {selected && <>
            <label htmlFor="cutoff">Analisar jogos anteriores a</label><input id="cutoff" type="date" required value={form.cutoff} onChange={e => changeCutoff(e.target.value)} />
            <p className="small muted">A data inicial usa o fim do histórico disponível. O dia escolhido fica de fora da análise.</p>
            <label htmlFor="window">{form.compare ? 'Jogos anteriores por equipe' : 'Jogos anteriores'}</label><input id="window" type="number" min="1" max={maxWindow} step="1" value={form.window || ''} onChange={e => update('window', +e.target.value)} />
            {(!Number.isInteger(form.window) || form.window < 1 || form.window > maxWindow) && <p className="field-error">Informe de 1 a {maxWindow} jogos.</p>}
            {recut ? <div className="recut-summary"><strong>{recut.competition_name} · {recut.season_name}</strong><span>Calendário de {date(recut.first_date)} a {date(recut.last_date)}</span><span>{recut.event_matches} de {recut.calendar_matches} jogos com arquivos de eventos.</span>
              {form.cutoff > nextDay(recut.last_date) && <p className="coverage-warning">O histórico termina em {date(recut.last_date)}. Esta consulta não representa jogos atuais.</p>}
              {recuts.length > 1 && <details><summary>Trocar competição ou temporada</summary><label htmlFor="recut">Histórico da equipe</label><select id="recut" value={form.recut} onChange={e => changeRecut(e.target.value)}>{recutOptions}</select></details>}
            </div> : <div className="notice"><p>Não foi possível identificar um único histórico para esta data. Escolha qual deseja consultar.</p><label htmlFor="recut">Histórico da equipe</label><select id="recut" value={form.recut} onChange={e => changeRecut(e.target.value)}>{recutOptions}</select></div>}
            <label className="checkbox compare-toggle"><input type="checkbox" disabled={!recut} checked={form.compare} onChange={e => setForm(f => ({ ...f, compare: e.target.checked, opponent: 0, target: 0, reference: 'cutoff', v3: false, quality: false, explanation: 'none' }))} /><span>Preparar contra um adversário</span></label>
            {form.compare && <>
              <label htmlFor="opponent">Adversário</label><select id="opponent" value={form.opponent || ''} disabled={!season.data} onChange={e => setForm(f => ({ ...f, opponent: +e.target.value, target: 0 }))}><option value="">{season.loading ? 'Carregando times…' : 'Escolha o adversário'}</option>{teams.filter(t => t.team_id !== form.team).map(t => <option key={t.team_id} value={t.team_id}>{t.name}</option>)}</select>
              <p className="small muted">Times com calendário na mesma competição e temporada.</p>
              {season.error !== undefined && <p className="error" role="alert">{errorMessage(season.error)}</p>}
              <label className="checkbox compare-toggle"><input type="checkbox" disabled={!capabilities?.tactical_advisor?.configured} checked={form.ai && !!capabilities?.tactical_advisor?.configured} onChange={e => update('ai', e.target.checked)} /><span>Incluir sugestões táticas da IA</span></label>
              <p className="small muted">{capabilities?.tactical_advisor?.configured ? 'Envia indicadores e contexto ao Gemini. Notas e elenco não são enviados. Sugestões para avaliar no vídeo e no treino.' : 'Para habilitar, configure sua chave e ative o Gemini no .env do backend.'}</p>
              <details className="declarations"><summary>Como será o jogo? (opcional)</summary><p className="small muted">O contexto organiza a leitura dos planos disponíveis, mantendo os indicadores históricos.</p>
                <label htmlFor="venue">Onde vamos jogar?</label><select id="venue" value={venue} disabled={form.reference === 'match'} onChange={e => update('venue', e.target.value as FormState['venue'])}>{venues.map(v => <option key={v} value={v}>{venueLabels[v]}</option>)}</select>
                {form.reference === 'match' && <p className="small muted">Mando formal do calendário preenchido automaticamente; não confirma campo neutro.</p>}
                <label htmlFor="context">Que tipo de partida é?</label><select id="context" value={form.context} onChange={e => update('context', e.target.value as FormState['context'])}>{contexts.map(c => <option key={c}>{c}</option>)}</select>
                <label htmlFor="objective">Qual é a prioridade?</label><select id="objective" value={form.objective} onChange={e => update('objective', e.target.value as FormState['objective'])}>{objectives.map(o => <option key={o}>{o}</option>)}</select>
                <p className="small muted">Proteger vantagem pode priorizar planos compatíveis. As demais prioridades e o tipo de partida ficam registrados, sem gerar novos planos automaticamente.</p>
                {form.objective === 'pressionar alto' && <p className="small muted">Não há plano validado para priorizar pressão da própria equipe.</p>}
              </details>
              <details className="advanced"><summary>Mais opções de análise</summary>
                <fieldset className="reference"><legend>Referência temporal</legend><label className="radio"><input type="radio" name="reference" checked={form.reference === 'cutoff'} onChange={() => update('reference', 'cutoff')} />Usar a data informada</label><label className="radio"><input type="radio" name="reference" checked={form.reference === 'match'} onChange={() => update('reference', 'match')} />Partida histórica</label></fieldset>
                {form.reference === 'match' && <><label htmlFor="target">Partida de referência</label><select id="target" disabled={!pairMatches.length} value={form.target || ''} onChange={e => update('target', +e.target.value)}>{!pairMatches.length && <option value="">Sem partida deste confronto</option>}{pairMatches.map(m => <option key={m.match_id} value={m.match_id}>{date(m.date)} · {name(m.home_team_id)} × {name(m.away_team_id)}</option>)}</select><p className="small muted">O corte será a data desta partida, no lugar da data informada acima.</p>{!pairMatches.length && <p className="field-error">Não há confronto no calendário. Use a data informada.</p>}</>}
                <label className="checkbox v3-toggle"><input type="checkbox" disabled={!v3Certified || form.quality} checked={form.v3} onChange={e => update('v3', e.target.checked)} /><span>Incluir mapas e indicadores adicionais</span></label><p className="small muted">{v3Certified ? 'Disponíveis para esta competição e temporada.' : 'Indisponíveis para esta competição e temporada.'} Não combinam com os filtros de qualidade abaixo.</p>
                <label className="checkbox"><input type="checkbox" disabled={form.v3 || !capabilities?.data_policies?.includes('quality_v1')} checked={form.quality} onChange={e => update('quality', e.target.checked)} /><span>Aplicar filtros de qualidade por indicador</span></label><p className="small muted">Podem reduzir a amostra. Jogos excluídos não são substituídos; os filtros não certificam a temporada.</p>
                <label htmlFor="strategy">Estratégia pretendida</label><select id="strategy" value={form.strategy} onChange={e => update('strategy', e.target.value as FormState['strategy'])}>{strategies.map(s => <option key={s} value={s}>{strategyLabels[s]}</option>)}</select>
                <fieldset><legend>Opções que não deseja investigar</legend>{planIds.map(id => <label key={id} className="checkbox"><input type="checkbox" checked={form.blocked.includes(id)} onChange={e => update('blocked', e.target.checked ? [...form.blocked, id] : form.blocked.filter(x => x !== id))} />{planLabels[id]}</label>)}</fieldset>
                <label htmlFor="notes">Notas do treinador</label><textarea id="notes" rows={3} maxLength={4000} value={form.notes} onChange={e => update('notes', e.target.value)} /><small className="muted">{form.notes.length}/4.000 caracteres. Notas registradas, sem interpretação automática.</small>
                <label htmlFor="explanation">Explicação opcional</label><select id="explanation" disabled={!capabilities?.llm.configured} value={form.explanation} onChange={e => update('explanation', e.target.value as FormState['explanation'])}>{explanations.map(x => <option key={x} value={x}>{explanationLabels[x]}</option>)}</select><p className="small muted">{capabilities?.llm.configured ? 'Disponibilidade confirmada ao executar.' : 'Indisponível nesta instalação.'} A explicação usa afirmações autorizadas; não aprende ou escolhe uma tática.</p>
              </details>
            </>}
            {notice && <p role="status" className="small reset-notice">{notice}</p>}
            <div className="submit-area">{analysisError && <p role="alert" className="error">{analysisError}</p>}<button className="primary" type="submit" disabled={!ready || !currentPreview || busy}>{busy ? 'Analisando histórico…' : form.compare ? 'Comparar equipes' : 'Analisar meu time'}<span aria-hidden="true">↗</span></button>
              {busy && <p role="status" className="small">{slow ? 'A análise está demorando. O cálculo pode continuar no servidor; aguarde antes de reenviar.' : 'Calculando os indicadores do histórico…'}{changed && ' O formulário mudou; o resultado usará o pedido já enviado.'}</p>}
            </div>
          </>}
        </form></aside>
        <section className="analysis-space" tabIndex={-1} ref={resultHeading} aria-label="Área de análise">
          {ready && !currentPreview && preview.error === undefined && <p role="status" className="notice">Conferindo o histórico selecionado…</p>}
          {preview.key === requestKey && preview.error !== undefined && <p role="alert" className="error">{errorMessage(preview.error)}</p>}
          {currentPreview && <CoverageView value={currentPreview} />}
          {result ? result.kind === 'comparison' ? <ReportView key={result.data.report_key} report={result.data} changed={changed} /> : <TeamOverview report={result.data} changed={changed} /> : <div className="empty-report"><h2>{busy ? 'Analisando os jogos.' : 'Como seu time chega para o jogo?'}</h2><p>{busy ? 'O resultado vai mostrar o período e a amostra usados em cada indicador.' : 'Consulte ataque, defesa, circulação e pressão. Ao adicionar um adversário, veja as diferenças entre as equipes e os pontos para investigar no vídeo e no treino.'}</p><p className="small muted">A análise usa o histórico disponível na base. Ele pode ser antigo e não representa automaticamente a situação atual dos clubes.</p></div>}
        </section>
      </div>}
    </main><footer><span>ManagerAI · Análise de equipes</span><span>Fonte: StatsBomb Open Data · Histórico disponível</span></footer>
  </>;
}
