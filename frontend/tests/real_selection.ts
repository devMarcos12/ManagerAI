import { expect, type Page } from '@playwright/test';
import type { Schema } from '../src/api';

// Exercita o mesmo fluxo visível do treinador com o catálogo real da instalação.
export async function prepareRealComparison(page: Page, competition: number, season: number, teamId: number, opponentId: number, target: number, url = '/') {
  await page.goto(url);
  const response = await page.request.get(new URL('/v1/coach/teams', page.url()).href);
  expect(response.ok()).toBe(true);
  const index = await response.json() as Schema['CoachCatalogBody'];
  const team = index.teams.find(t => t.team_id === teamId);
  expect(team, `Time ${teamId} no catálogo local`).toBeDefined();
  await page.getByRole('combobox', { name: 'Qual é o seu time?' }).fill(team!.name);
  await page.locator(`#team-option-${teamId}`).click();
  if (team!.recuts.length > 1) {
    const change = page.getByText('Trocar competição ou temporada', { exact: true });
    if (await change.isVisible()) await change.click();
    await page.getByLabel('Histórico da equipe', { exact: true }).selectOption(`${competition}/${season}`);
  } else {
    expect(team!.recuts[0].competition_id).toBe(competition); expect(team!.recuts[0].season_id).toBe(season);
  }
  await page.getByLabel('Preparar contra um adversário').check();
  await page.getByLabel('Adversário', { exact: true }).selectOption(String(opponentId));
  await page.getByText('Mais opções de análise', { exact: true }).click();
  await page.getByLabel('Partida histórica', { exact: true }).check();
  await page.getByLabel('Partida de referência', { exact: true }).selectOption(String(target));
}
