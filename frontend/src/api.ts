import type { components } from './generated/api';
export type Schema = components['schemas'];
export type AnalysisRequest = Schema['AnalysisBody'];
export type Report = Schema['ReportBody'];
export type Coverage = Schema['CoverageBody'];
export type Capabilities = Schema['CapabilitiesBody'];
export type Catalog = Schema['CatalogBody'];
export type Team = Schema['TeamBody'];
export type Match = Schema['MatchBody'];
export type Evidence = Schema['EvidenceBody'];

const base = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) { super(message); }
}
const messages: Record<number, string> = {
  404: 'O relatório expirou ou saiu da memória do servidor. O conteúdo nesta página continua disponível; para exportar, faça uma nova análise por sua escolha.',
  413: 'O pedido ou relatório excede o limite. Reduza a janela ou o conteúdo informado.',
  422: 'Confira equipes, referência temporal e contexto informado.',
  429: 'O servidor está ocupado ou atingiu o limite de análises. Aguarde antes de tentar novamente.',
  500: 'Não foi possível concluir a análise. Tente novamente por ação explícita.',
  503: 'O motor ou a explicação solicitada está indisponível. Você pode escolher uma análise sem explicação opcional.',
};
export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Não foi possível conectar ao backend. Confira se o serviço local está em execução e use Tentar conexão novamente.';
}
async function checkedFetch<T>(path: string, read: (response: Response) => Promise<T>, init: RequestInit = {}, timeout = 15000): Promise<T> {
  const controller = new AbortController();
  const external = init.signal;
  const abort = () => controller.abort();
  if (external?.aborted) controller.abort();
  external?.addEventListener('abort', abort, { once: true });
  const timer = setTimeout(abort, timeout);
  try {
    const response = await fetch(base + path, { ...init, signal: controller.signal });
    if (!response.ok) {
      let code = 'HTTP_ERROR';
      try { code = (await response.json()).code || code; } catch { /* Resposta de proxy sem JSON. */ }
      const detail = code === 'SEASON_NOT_CERTIFIED' ? 'Esta temporada não é certificada para V3. Desmarque V3 explicitamente ou escolha um recorte certificado.'
        : code === 'DATA_UNAVAILABLE_OR_INVALID' ? 'Não foi possível ler o histórico local. Confira o provisionamento dos dados no backend ou escolha um recorte disponível.'
        : response.status === 404 && !path.startsWith('/v1/reports/') ? 'Recurso da API não encontrado. Confira a configuração do endereço do backend.' : messages[response.status];
      throw new ApiError(response.status, code, detail || 'Não foi possível concluir o pedido.');
    }
    return await read(response);
  } catch (error) {
    if (controller.signal.aborted && !external?.aborted) {
      throw new ApiError(0, 'TIMEOUT', 'O tempo de espera terminou. O cálculo pode continuar no servidor. Não reenviamos o pedido; aguarde antes de iniciar outra análise.');
    }
    throw error;
  } finally { clearTimeout(timer); external?.removeEventListener('abort', abort); }
}
async function json<T>(path: string, init: RequestInit = {}, timeout?: number): Promise<T> {
  return checkedFetch(path, response => response.json() as Promise<T>, init, timeout);
}
const post = (body: AnalysisRequest, signal?: AbortSignal): RequestInit => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal });
export const api = {
  bootstrap: async (signal: AbortSignal) => {
    const [health, capabilities, catalog] = await Promise.all([
      json<Schema['HealthBody']>('/v1/health', { signal }), json<Capabilities>('/v1/capabilities', { signal }), json<Catalog[]>('/v1/catalog', { signal }),
    ]);
    return { health, capabilities, catalog };
  },
  season: async (competition: number, season: number, signal: AbortSignal) => {
    const query = `?competition_id=${competition}&season_id=${season}`;
    const [teams, matches] = await Promise.all([json<Team[]>('/v1/teams' + query, { signal }), json<Match[]>('/v1/matches' + query, { signal })]);
    return { teams, matches };
  },
  coverage: (body: AnalysisRequest, signal: AbortSignal) => json<Coverage>('/v1/coverage', post(body, signal)),
  analyze: (body: AnalysisRequest) => json<Report>('/v1/analyses', post(body), 120000),
  export: (key: string, format: 'json' | 'markdown') => checkedFetch(`/v1/reports/${encodeURIComponent(key)}/export?format=${format}`, response => response.blob()),
};
