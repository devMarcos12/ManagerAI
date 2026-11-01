import type { Report } from './api';
import { number } from './format';

const reasons: Record<string, string> = {
  NOT_CONFIGURED: 'Provedor de IA não configurado ou não ativado no backend.',
  PROVIDER_OVERLOADED: 'O provedor está temporariamente indisponível ou com demanda alta. Aguarde antes de tentar novamente.',
  RATE_LIMIT: 'Cota ou limite de uso atingido. Aguarde antes de solicitar outra análise.',
  AUTHORIZATION_FAILED: 'A chave não foi aceita. Confira sua chave e as permissões no painel do provedor.',
  INSUFFICIENT_EVIDENCE_OR_RESTRICTIONS: 'Amostra insuficiente ou planos restringidos manualmente. A IA não gerou sugestões para contornar essas limitações.',
  BUSY: 'Já existe uma solicitação à IA em execução.',
  INPUT_TOO_LARGE: 'O resumo excedeu o limite da integração. Reduza os indicadores adicionais.',
};
export default function AIAdvice({ report }: { report: Report }) {
  const advice = report.ai_tactical;
  if (!advice || advice.status === 'disabled') return null;
  return <section className="report-section" aria-label="Sugestões táticas da IA"><h3>Sugestões táticas da IA</h3>
    <p className="small muted">{advice.policy}</p>
    {advice.status !== 'generated' ? <p className="notice" role="status">{reasons[advice.reason || ''] || 'Não foi possível concluir a análise da IA. O relatório histórico continua disponível.'}</p> : <>
      <p>{advice.summary}</p>
      <p className="small muted">{advice.provider === 'groq' ? 'Groq' : advice.provider === 'gemini' ? 'Gemini' : 'IA'} · {advice.model}{advice.cached ? ' · Resultado reaproveitado para os mesmos dados e contexto' : ''}</p>
      {advice.options.map((option, index) => <section className="plan" key={index}><h4>{option.title}</h4><div className="action"><strong>Ação para considerar</strong><p>{option.action}</p></div>
        <p>{option.rationale}</p><div className="plan-details"><div><h5>Riscos</h5><ul>{option.risks.map((risk, i) => <li key={i}>{risk}</li>)}</ul></div><div><h5>Conferir no vídeo</h5><p>{option.video_check}</p><h5>Reavaliar quando</h5><p>{option.adjust_when}</p></div></div>
        <details><summary>Indicadores citados pela IA</summary><p className="small muted">As referências foram conferidas pelo sistema. A interpretação e a utilidade tática ainda precisam da avaliação do treinador.</p><ul>{option.evidence_ids.map(ref => {
          const e = report.evidence[ref];
          return e && <li key={ref}>{e.team_name} · {report.display.metric_definitions[e.metric_id] || e.metric_id}: {number(e.value)} {e.unit} · {e.sample_size} jogos.</li>;
        })}</ul></details>
      </section>)}
    </>}
  </section>;
}
