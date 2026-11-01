import type { CoachRecut } from './api';

export const recutKey = (r: CoachRecut) => `${r.competition_id}/${r.season_id}`;
export const nextDay = (day: string) => {
  const value = new Date(`${day}T12:00:00Z`);
  value.setUTCDate(value.getUTCDate() + 1);
  return value.toISOString().slice(0, 10);
};
export const normalize = (text: string) => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR');

// Só resolve um recorte. Sobreposição exige escolha explícita e nunca agrega temporadas.
export function resolveRecut(recuts: CoachRecut[], cutoff: string, override: string) {
  if (override) return recuts.find(r => recutKey(r) === override);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(cutoff)) return undefined;
  const active = recuts.filter(r => r.first_date < cutoff && cutoff <= nextDay(r.last_date));
  if (active.length) return active.length === 1 ? active[0] : undefined;
  const earlier = recuts.filter(r => r.last_date < cutoff);
  const latest = earlier.reduce((last, r) => r.last_date > last ? r.last_date : last, '');
  const candidates = earlier.filter(r => r.last_date === latest);
  return candidates.length === 1 ? candidates[0] : undefined;
}
