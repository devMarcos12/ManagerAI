import type { Schema } from './api';
export const number = (n: number | null | undefined) => n == null ? 'Indisponível' : new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 }).format(n);
// Não usar Date(ISO): datas de calendário não devem mudar com o fuso do navegador.
export const date = (iso: string | null | undefined) => iso ? iso.slice(0, 10).split('-').reverse().join('/') : 'Sem período disponível';
export const planLabels: Record<Schema['PlanBody']['plan_id'], string> = {
  R01_PROGRESSAO: 'Proteger zonas de progressão', R02_PRESSAO_ALTA: 'Rever a saída sob pressão adversária',
  R03_CHANCES: 'Proteger espaços de finalização', V3_ENTRADAS_PASSE: 'Proteger recepções no terço final',
  V3_CHUTES_AREA: 'Rever a proteção da área',
};
export const strategyLabels: Record<NonNullable<Schema['AnalysisBody']['intended_strategy']>, string> = {
  equilibrada: 'Equilibrada', proteger_area: 'Proteção da área', saida_sob_pressao: 'Saída sob pressão', proteger_progressao: 'Proteção da progressão',
};
