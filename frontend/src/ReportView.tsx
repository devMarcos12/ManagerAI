import { useState } from 'react';
import { api, errorMessage, type Report, type Evidence, type Schema } from './api';
import { date, number, planLabels } from './format';

const metrics: [string, string][] = [
  ['shots_for', 'Finalizações a favor'], ['shots_against', 'Finalizações permitidas'],
  ['xg_for', 'Gols esperados a favor'], ['xg_against', 'Gols esperados concedidos'],
  ['pass_accuracy', 'Passes completos'], ['final_third_entries', 'Entradas no terço final'],
];

function EvidenceDetail({ id, evidence }: { id: string; evidence: Evidence }) {
  const [open, setOpen] = useState(false);
  return <details className="evidence" onToggle={e => setOpen(e.currentTarget.open)}>
    <summary>{evidence.team_name} · {evidence.metric_id} · {evidence.sample_size} jogos</summary>
    {open && <div><p>{number(evidence.value)} {evidence.unit} · Fórmula {evidence.formula_version}</p>
      <p>Numerador: {number(evidence.numerator)} · Denominador: {number(evidence.denominator)}. Ausência de dado não equivale a zero.</p>
      <p className="small muted">Em telas pequenas, deslize a tabela para consultar todas as colunas.</p><div className="table-scroll" tabIndex={0} role="region" aria-label="Tabela de partidas e evidências"><table><caption>Partidas e amostra específica desta métrica</caption><thead><tr><th>Partida</th><th>Data</th><th>Valor</th><th>Numerador</th><th>Denominador</th></tr></thead>
        <tbody>{evidence.per_match.slice(0, 20).map(row => <tr key={row.match_id}><td>{row.match_id}</td><td>{date(row.match_date)}</td><td>{number(row.value)}</td><td>{number(row.numerator)}</td><td>{number(row.denominator)}</td></tr>)}</tbody></table></div>
      {evidence.per_match.length > 20 && <p>Primeiras 20 partidas; lista integral na exportação.</p>}
      <small className="technical">Referência: {id}</small></div>}
  </details>;
}

function MetricComparison({ title, own, other }: { title: string; own?: Evidence; other?: Evidence }) {
  const compatible = own?.unit === other?.unit;
  const max = own?.unit === '%' && compatible ? 100 : Math.max(own?.value || 0, other?.value || 0, 1);
  return <div className="metric-row"><h4>{title} <span>{own?.unit || other?.unit || ''}</span></h4>
    {[own, other].map((e, i) => <div className="metric-side" key={i}>
      <span>{e?.team_name || (i ? 'Adversário' : 'Equipe')}</span>
      <div className="bar-track" aria-hidden="true" title={`Escala de 0 a ${number(max)} ${e?.unit || ''}`}><i className={i ? 'other' : ''} style={{ width: e?.value != null && compatible ? `${Math.max(0, e.value) / max * 100}%` : '0%' }} /></div>
      <strong>{number(e?.value)}</strong><small>{e?.sample_size ?? 0} jogos</small>
    </div>)}
    {!compatible && <small>Unidades incompatíveis: não há comparação gráfica.</small>}
  </div>;
}

function ShotMap({ profile }: { profile: Schema['DisplayProfile'] }) {
  const shots = profile.shots.filter(s => Number.isFinite(s.x) && Number.isFinite(s.y) && s.x >= 0 && s.x <= 120 && s.y >= 0 && s.y <= 80);
  return <figure className="pitch-figure"><figcaption><strong>{profile.team_name}</strong><span>{shots.length} finalizações localizadas · {date(profile.period_start)} a {date(profile.period_end)}</span></figcaption>
    <svg viewBox="-3 -3 126 86" role="img" aria-label={`Mapa de finalizações de ${profile.team_name}, coordenadas StatsBomb 120 por 80`}>
      <rect width="120" height="80" className="grass" /><path d="M60 0V80 M0 18H18V62H0 M120 18H102V62H120" className="pitch-line" />
      <circle cx="60" cy="40" r="9.15" className="pitch-line" />
      {shots.slice(0, 1000).map((s, i) => <circle key={s.id || i} cx={s.x} cy={s.y} r="1.25" className={s.xg == null ? 'shot unknown' : 'shot'}><title>Partida {s.match_id}; x={s.x}, y={s.y}; xG: {number(s.xg)}</title></circle>)}
    </svg>
    {!shots.length && <p>Sem finalizações localizadas disponíveis.</p>}
    {shots.length > 1000 && <p>Primeiros 1.000 pontos; dados integrais na exportação.</p>}
  </figure>;
}

export default function ReportView({ report, changed }: { report: Report; changed: boolean }) {
  const [exporting, setExporting] = useState<string | null>(null);
  const [exportError, setExportError] = useState('');
  const [exportSuccess, setExportSuccess] = useState('');
  const [sources, setSources] = useState(10);
  const [charts, setCharts] = useState(false);
  const [allMetrics, setAllMetrics] = useState(false);
  const [qualityDetails, setQualityDetails] = useState(false);
  const d = report.display;
  async function download(format: 'json' | 'markdown') {
    if (exporting) return;
    setExporting(format); setExportError(''); setExportSuccess('');
    try {
      const blob = await api.export(report.report_key, format);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a'); link.href = url; link.download = `managerai-relatorio.${format === 'json' ? 'json' : 'md'}`;
      link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
      setExportSuccess('Arquivo recebido do servidor para download.');
    } catch (e) { setExportError(errorMessage(e)); }
    finally { setExporting(null); }
  }
  return <article className="report" aria-label="Relatório do confronto">
    {changed && <p className="notice">O formulário mudou. Este relatório pertence ao pedido enviado anteriormente, identificado abaixo. Gere outra análise para aplicar as novas escolhas.</p>}
    <div className="section-kicker">Leitura do confronto</div>
    <h2>{d.team.team_name} <span className="versus">×</span> {d.opponent.team_name}</h2>
    <p className="report-subtitle">{d.competition} · {d.season} · referência {date(d.cutoff_date)} · janela de até {report.request.analysis.recent_matches_window} jogos</p>
    <div className="report-status"><span className={report.sufficiency.sufficient ? 'badge' : 'badge warning'}>{report.sufficiency.status}</span><span>{d.team.match_ids.length} jogos da equipe · {d.opponent.match_ids.length} do adversário</span></div>
    <p className="muted">Amostras específicas podem variar por indicador. São observações históricas, sem previsão de vitória ou eficácia esportiva demonstrada.</p>
    <div className="exports"><button className="secondary" disabled={!!exporting} onClick={() => download('markdown')}>{exporting === 'markdown' ? 'Recebendo…' : 'Exportar Markdown'}</button><button className="text-button" disabled={!!exporting} onClick={() => download('json')}>{exporting === 'json' ? 'Recebendo…' : 'Exportar JSON'}</button></div>
    {exportError && <p role="alert" className="error">{exportError}</p>}{exportSuccess && <p role="status" className="muted">{exportSuccess}</p>}
    <p className="small muted">Exportação disponível enquanto o relatório estiver na memória do servidor. Esta página não é um histórico persistente.</p>
    {report.data_quality && <section className="report-section quality-details" aria-label="Qualidade dos dados"><h3>Qualidade aplicada aos indicadores</h3>
      <p>Os valores e planos abaixo usam somente os jogos utilizáveis por indicador. As amostras podem variar; nenhum jogo excluído foi substituído.</p>
      <p className="small muted">A suficiência básica exige cinco jogos em finalizações, gols esperados e acerto global de passes. Cada plano exige também suas próprias evidências. Os filtros não certificam a temporada.</p>
      <details onToggle={e => setQualityDetails(e.currentTarget.open)}><summary>Conferir amostras e motivos de exclusão</summary>{qualityDetails && <div className="table-scroll"><table>
        <caption>Jogos utilizáveis, amostras originais e motivos por indicador</caption><thead><tr><th>Equipe e indicador</th><th>Jogos utilizáveis</th><th>Motivos</th></tr></thead><tbody>
          {report.data_quality.metrics.map(q => <tr key={q.evidence_id}><th>{q.team_name} · {d.metric_definitions[q.metric_id] || q.metric_id}</th>
            <td>{q.usable_sample_size} de {q.selected_matches}<small>Amostra original: {q.original_sample_size}</small></td>
            <td>{Object.entries(q.reason_counts).map(([code, count]) => <p key={code}>{report.data_quality!.reason_labels[code] || code} ({count})</p>)}
              {q.excluded_match_ids.length > 0 && <small>Partidas excluídas: {q.excluded_match_ids.join(', ')}</small>}
              {!Object.keys(q.reason_counts).length && 'Sem exclusões adicionais.'}</td></tr>)}
        </tbody></table></div>}</details>
    </section>}
    {report.abstention_reason && <section className="abstention"><h3>Sem planos comparativos neste recorte</h3><p>{report.abstention_reason}</p><p>Você pode consultar os indicadores descritivos abaixo. Uma amostra menor não permite completar as evidências ausentes.</p>{report.sufficiency.warnings.map(w => <p key={w}>{w}</p>)}</section>}
    <section className="report-section"><div className="section-heading"><h3>O que o histórico mostra</h3><span>Indicadores por equipe</span></div>
      <p className="muted small">Gols esperados (xG) descrevem a qualidade esperada das finalizações registradas. Não são gols reais nem probabilidade de vencer.</p>
      <p className="muted small">Cada indicador tem escala própria, compartilhada entre as equipes. Porcentagens usam escala de 0 a 100.</p>
      <div className="metric-grid">{metrics.map(([key, title]) => <MetricComparison key={key} title={title} own={report.evidence[`team_profile.metrics.${key}`]} other={report.evidence[`opponent_profile.metrics.${key}`]} />)}</div>
      <details className="all-metrics" onToggle={e => setAllMetrics(e.currentTarget.open)}><summary>Consultar todos os indicadores e suas amostras</summary>{allMetrics && <>
        <div className="table-scroll"><table><caption>Valores calculados para o histórico; unidades e amostras preservadas por indicador</caption><thead><tr><th>Indicador</th><th>{d.team.team_name}</th><th>{d.opponent.team_name}</th></tr></thead><tbody>
          {Object.entries(report.evidence).filter(([id]) => id.includes('team_profile.metrics.')).map(([id, own]) => { const other = report.evidence[id.replace('team_profile.', 'opponent_profile.')]; return <tr key={id}><th>{d.metric_definitions[own.metric_id] || own.metric_id}</th><td><strong>{number(own.value)}</strong><span>{own.unit}</span><small>{own.sample_size} jogos</small></td><td><strong>{number(other?.value)}</strong><span>{other?.unit}</span><small>{other?.sample_size ?? 0} jogos</small></td></tr>; })}
        </tbody></table></div>
        <h4>Inspecionar evidências por métrica</h4>{Object.entries(report.evidence).map(([id, e]) => <EvidenceDetail key={id} id={id} evidence={e} />)}
      </>}</details>
    </section>
    <section className="report-section"><div className="section-heading"><h3>Planos para investigar</h3><span>{report.plans.length} opções condicionais</span></div>
      <p className="muted small">A prioridade reflete preferências declaradas, não confiança, probabilidade de sucesso ou ranking de eficácia.</p>
      {report.ordering.objective_note && <p className="notice">{report.ordering.objective_note}</p>}
      {report.plans.map((p, index) => <section className="plan" key={p.plan_id}><div className="plan-title"><span className="plan-number">{String(index + 1).padStart(2, '0')}</span><div><h4>{planLabels[p.plan_id]}</h4><span className="small muted">{p.context_priority ? 'Ordenado conforme a preferência informada' : 'Sem preferência de contexto'}</span></div></div>
        <p>{p.observation}</p><div className="action"><strong>Ação possível</strong><p>{p.possible_action}</p><strong>Sob esta condição</strong><p>{p.condition}</p></div>
        <div className="plan-details"><div><h5>Riscos</h5><ul>{p.risks.map(x => <li key={x}>{x}</li>)}</ul></div><div><h5>Antes de decidir</h5><ul>{p.preconditions.map(x => <li key={x}>{x}</li>)}</ul></div></div>
        <details><summary>Limitações desta opção</summary><ul>{p.limitations.map(x => <li key={x}>{x}</li>)}</ul></details>
        <div className="evidence-list"><h5>Evidências</h5>{p.evidence_ids.map(ref => report.evidence[ref] && <EvidenceDetail key={ref} id={ref} evidence={report.evidence[ref]} />)}</div>
      </section>)}
      {report.excluded_plans.map(p => <p className="muted" key={p.plan_id}>{planLabels[p.plan_id]}: {p.reason}</p>)}
      {report.plan_comparisons.length > 0 && <details className="comparison-details"><summary>Comparar as opções e entender empates</summary>{report.plan_comparisons.map((c, i) => <div key={i}><h4>{c.plans.map(id => planLabels[id]).join(' / ')}</h4><p>{c.interpretation} {c.context_priority_tied ? 'Há empate de prioridade de contexto.' : 'A diferença de prioridade decorre somente do contexto declarado.'}</p><p className="small">Evidências distintas: {c.different_evidence_ids.map(id => report.evidence[id]?.metric_id || id).join(', ') || 'Nenhuma.'}</p></div>)}</details>}
    </section>
    {report.request.include_v3 && <section className="report-section"><details onToggle={e => setCharts(e.currentTarget.open)}><summary>Explorar mapas e indicadores adicionais</summary>{charts && <div>
      <h4>Entradas no terço final</h4><p className="muted small">Taxas já calculadas pelo Core, por 90 minutos de exposição observada.</p>
      {(['final_third_pass_entries', 'final_third_carry_entries'] as const).map((key, i) => <MetricComparison key={key} title={i ? 'Entradas por condução' : 'Entradas por passe completo'} own={report.evidence[`tactical_v3.team_profile.metrics.${key}`]} other={report.evidence[`tactical_v3.opponent_profile.metrics.${key}`]} />)}
      <h4>Mapa de finalizações</h4><p className="muted small">Plano StatsBomb 120 × 80; meta de referência em x=120. Orientação preservada, sem espelhamento ou inferência de esquerda/direita tática. Pontos ocos: xG ausente.</p><div className="pitch-grid"><ShotMap profile={d.team} /><ShotMap profile={d.opponent} /></div>
    </div>}</details></section>}
    {report.explanation.status !== 'disabled' && <section className="report-section"><h3>Explicação opcional</h3>
      {report.explanation.status === 'generated' ? <><p className="muted small">Afirmações autorizadas selecionadas pela LLM e materializadas pelo Core. Não é raciocínio tático aprendido nem geração livre.</p>{report.explanation.claims.map(c => <p key={c.id}>{c.text}</p>)}</> : <p className="notice">A explicação opcional não foi gerada ({report.explanation.status === 'unavailable' ? 'indisponível' : 'falha'}). O relatório determinístico foi preservado.</p>}
    </section>}
    <section className="report-section"><details><summary>Lacunas, limites e fontes</summary><ul>{report.limitations.map(x => <li key={x}>{x}</li>)}</ul><p>{report.roster_policy.reason} O histórico não comprova disponibilidade atual.</p><h4>Fontes efetivamente lidas</h4><p className="muted">StatsBomb Open Data. A presença no catálogo não certifica todos os campos de uma partida.</p><ul className="sources">{d.sources.slice(0, sources).map(s => <li key={s.path}><span>{s.path}</span><code>{s.sha256}</code></li>)}</ul>{sources < d.sources.length && <button className="text-button" onClick={() => setSources(x => x + 10)}>Mostrar mais fontes</button>}</details></section>
    <details className="technical"><summary>Identificação e capacidades técnicas</summary><p>Relatório {report.report_id} · serviço {report.schema_version} · ordenação {report.ordering.version}</p><p>Motor tático: determinístico. Preditor de chutes e fine-tuning: experimentais, fora da decisão de produção.</p><p>Explicação: {report.explanation.status}; provedor {report.explanation.provider || 'não acionado'}; modelo {report.explanation.model || 'não acionado'}.</p></details>
  </article>;
}
