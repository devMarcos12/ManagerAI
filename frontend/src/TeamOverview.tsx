import { useState } from 'react';
import type { TeamReport } from './api';
import { date, number } from './format';

const groups = [
  ['Ataque', ['shots_for', 'xg_for', 'xg_per_shot', 'box_entries']],
  ['Defesa', ['shots_against', 'xg_against', 'recoveries', 'interceptions']],
  ['Circulação e pressão', ['pass_accuracy', 'pass_accuracy_under_pressure', 'final_third_entries', 'pressures']],
] as const;

export default function TeamOverview({ report, changed }: { report: TeamReport; changed: boolean }) {
  const [all, setAll] = useState(false);
  const p = report.profile;
  function download() {
    const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }));
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'managerai-panorama.json'; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return <article className="report team-overview" aria-label="Panorama do time">
    {changed && <p className="notice" role="status">O formulário mudou. Este panorama corresponde à consulta anterior; analise novamente para atualizar.</p>}
    <div className="section-kicker">Panorama do time</div><h2>{p.team_name}</h2>
    <p className="report-subtitle">{report.competition} · {report.season}<br />Jogos de {date(p.period_start)} a {date(p.period_end)} · corte em {date(report.request.cutoff_date)}</p>
    <div className="report-status"><span className={`badge ${report.sample_status === 'amostra insuficiente' ? 'warning' : ''}`}>{report.sample_status}</span><span>{p.match_ids.length} de {report.coverage.selected_match_ids.length} jogos analisados</span></div>
    <p className="small muted">Leitura descritiva do histórico. Gols esperados (xG) medem a qualidade das finalizações, sem prever vitória. Ações de pressão não medem sua eficácia.</p>
    {report.insufficient_metrics.length > 0 && <section className="abstention"><h3>Histórico insuficiente para conclusões</h3><p>Há indicadores centrais com menos de {report.minimum_matches} jogos calculáveis. Os valores abaixo continuam disponíveis para consulta.</p></section>}
    {!p.match_ids.length && <p className="notice">Nenhum jogo com eventos pôde ser analisado nesta janela. Ajuste a data ou confira a cobertura disponível.</p>}
    {groups.map(([title, keys]) => <section className="report-section" key={title}><h3>{title}</h3><div className="overview-grid">{keys.map(key => {
      const m = p.metrics[key], definition = report.metric_definitions[key];
      return <div className="overview-card" key={key}><h4>{definition?.title || key}</h4><strong>{number(m?.value)}</strong><span>{definition?.unit || m?.unit}</span><small>{m?.sample_size ?? 0} jogos calculáveis</small><details><summary>O que este indicador mostra</summary><p>{definition?.explanation}</p></details></div>;
    })}</div></section>)}
    <section className="report-section all-metrics"><details onToggle={e => setAll(e.currentTarget.open)}><summary>Consultar todos os indicadores e suas amostras</summary>{all && <><div className="table-scroll"><table><caption>Indicadores calculados para a janela selecionada</caption><thead><tr><th>Indicador</th><th>Valor e unidade</th><th>Jogos</th></tr></thead><tbody>{Object.entries(p.metrics).map(([key, m]) => <tr key={key}><th>{report.metric_definitions[key]?.title || key}</th><td>{number(m.value)}<span>{m.unit}</span></td><td>{m.sample_size}</td></tr>)}</tbody></table></div>{Object.entries(p.metrics).map(([key, m]) => <details className="evidence" key={key}><summary>{report.metric_definitions[key]?.title || key} · evidências</summary><p>Numerador: {number(m.numerator)} · Denominador: {number(m.denominator)}.</p><p>Partidas: {m.match_ids.join(', ') || 'Nenhuma calculável.'}</p><div className="table-scroll"><table><thead><tr><th>Data</th><th>Partida</th><th>Valor</th></tr></thead><tbody>{m.per_match.map(row => <tr key={row.match_id}><td>{date(row.match_date)}</td><td>{row.match_id}</td><td>{number(row.value)}</td></tr>)}</tbody></table></div></details>)}</>}</details></section>
    <section className="report-section"><details><summary>Cobertura, limites e fontes</summary><p>{report.methodology.temporal_policy}</p><ul>{report.warnings.map(x => <li key={x}>{x}</li>)}{report.limitations.map(x => <li key={x}>{x}</li>)}</ul><ul className="sources">{report.methodology.sources.map(s => <li key={s.path}><span>{s.path}</span><code>{s.sha256}</code></li>)}</ul><p>Fonte: StatsBomb Open Data · fórmulas {report.methodology.formula_version}.</p></details></section>
    <div className="exports"><button className="secondary" onClick={download}>Exportar panorama JSON</button></div>
    <p className="small muted">Para preparar um confronto, adicione o adversário no formulário e solicite a comparação.</p>
  </article>;
}
