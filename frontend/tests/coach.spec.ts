import { test, expect } from '@playwright/test';
import { coachTeams, mockApi, selectTeam } from './fixtures';

test('começa pelo time, identifica histórico e analisa sem adversário', async ({ page }) => {
  const errors: string[] = []; page.on('pageerror', e => errors.push(e.message));
  const state = await mockApi(page); await page.goto('/');
  await expect(page.getByLabel('Competição', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Analisar meu time' })).toHaveCount(0);
  await selectTeam(page);
  await expect(page.getByLabel('Analisar jogos anteriores a')).toHaveValue('2020-01-10');
  await expect(page.getByText('Premier League · 2015/2016', { exact: true }).first()).toBeVisible();
  const analyze = page.getByRole('button', { name: 'Analisar meu time' }); await expect(analyze).toBeEnabled(); await analyze.click();
  await expect(page.getByRole('article', { name: 'Panorama do time' })).toBeVisible();
  expect(state.requests).toHaveLength(0); expect(state.teamRequests).toHaveLength(1);
  expect(state.teamRequests![0]).toEqual({ competition_id: 2, season_id: 27, team_id: 1, cutoff_date: '2020-01-10', recent_matches_window: 10 });
  await expect(page.getByText('Indisponível', { exact: true }).first()).toBeVisible();
  const promise = page.waitForEvent('download'); await page.getByRole('button', { name: 'Exportar panorama JSON' }).click();
  expect((await promise).suggestedFilename()).toBe('managerai-panorama.json'); expect(errors).toEqual([]);
});

test('busca por nome, teclado e ausência de time disponível', async ({ page }) => {
  await mockApi(page); await page.goto('/');
  const input = page.getByRole('combobox', { name: 'Qual é o seu time?' });
  await input.fill('eQUIpe b'); await input.press('Enter');
  await expect(input).toHaveValue('Equipe B');
  await expect(page.getByRole('button', { name: 'Analisar meu time' })).toBeEnabled();
  await input.fill('Time ausente'); await expect(page.getByText('Nenhum time encontrado no histórico disponível.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Analisar meu time' })).toHaveCount(0);
});

test('temporadas sobrepostas exigem escolha explícita, sem agregação', async ({ page }) => {
  const index = structuredClone(coachTeams);
  index[0].recuts[1] = { ...index[0].recuts[1], first_date: '2020-01-01', last_date: '2020-01-09' };
  const state = await mockApi(page, { requests: [], coverageRequests: [], index }); await page.goto('/'); await selectTeam(page);
  await expect(page.getByText('Não foi possível identificar um único histórico para esta data.', { exact: false })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Analisar meu time' })).toBeDisabled();
  await page.getByLabel('Histórico da equipe', { exact: true }).selectOption('2/28');
  await expect(page.getByRole('button', { name: 'Analisar meu time' })).toBeEnabled();
  await page.getByRole('button', { name: 'Analisar meu time' }).click();
  await expect(page.getByRole('article')).toBeVisible(); expect(state.teamRequests![0].season_id).toBe(28);
});

test('adversário é opcional e trocar time desfaz a preparação anterior', async ({ page }) => {
  await mockApi(page); await page.goto('/'); await selectTeam(page);
  await page.getByLabel('Preparar contra um adversário').check();
  await expect(page.getByRole('button', { name: 'Comparar equipes' })).toBeDisabled();
  await expect(page.locator('#opponent option[value="1"]')).toHaveCount(0);
  await page.getByLabel('Adversário', { exact: true }).selectOption('2');
  await expect(page.getByRole('button', { name: 'Comparar equipes' })).toBeEnabled();
  await selectTeam(page, 'Equipe C');
  await expect(page.getByLabel('Preparar contra um adversário')).not.toBeChecked();
  await expect(page.getByLabel('Adversário', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Analisar meu time' })).toBeEnabled();
});

test('data posterior à cobertura avisa e alteração durante cálculo mantém a identidade', async ({ page }) => {
  const state = await mockApi(page, { requests: [], coverageRequests: [], teamDelay: 700 });
  await page.goto('/'); await selectTeam(page);
  await page.getByLabel('Analisar jogos anteriores a').fill('2026-11-01');
  await expect(page.getByText('Esta consulta não representa jogos atuais.', { exact: false })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Analisar meu time' })).toBeEnabled();
  await page.getByRole('button', { name: 'Analisar meu time' }).click();
  await page.getByLabel('Jogos anteriores', { exact: true }).fill('1');
  await expect(page.getByRole('article')).toBeVisible();
  await expect(page.getByText('O formulário mudou. Este panorama corresponde à consulta anterior;', { exact: false })).toBeVisible();
  expect(state.teamRequests).toHaveLength(1); expect(state.teamRequests![0].recent_matches_window).toBe(10);
});

test('insuficiência individual continua descritiva e cabe no celular', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await mockApi(page); await page.goto('/'); await selectTeam(page);
  await page.getByLabel('Jogos anteriores', { exact: true }).fill('1');
  await expect(page.getByRole('button', { name: 'Analisar meu time' })).toBeEnabled();
  await page.getByRole('button', { name: 'Analisar meu time' }).click();
  await expect(page.getByRole('heading', { name: 'Histórico insuficiente para conclusões' })).toBeVisible();
  await page.getByText('Consultar todos os indicadores e suas amostras', { exact: true }).click();
  await expect(page.getByRole('table').first()).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('erro no panorama não gera repetição automática', async ({ page }) => {
  const state = await mockApi(page, { requests: [], coverageRequests: [], analysisStatus: 429 });
  await page.goto('/'); await selectTeam(page);
  await expect(page.getByRole('button', { name: 'Analisar meu time' })).toBeEnabled();
  await page.getByRole('button', { name: 'Analisar meu time' }).click(); await expect(page.getByRole('alert')).toBeVisible();
  expect(state.teamRequests).toHaveLength(1); await expect(page.getByRole('article')).toHaveCount(0);
});
