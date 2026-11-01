import { test, expect } from '@playwright/test';
import { mockApi, openComparison } from './fixtures';

test('Gemini configurado recebe opção explícita e mostra sugestões separadas das regras', async ({page}) => {
  const errors: string[]=[];page.on('pageerror',e=>errors.push(e.message));
  const state=await mockApi(page,{requests:[],coverageRequests:[],advisorConfigured:true});await openComparison(page);
  await expect(page.getByLabel('Incluir sugestões táticas da IA')).toBeChecked();
  await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();
  await page.getByRole('button',{name:'Comparar equipes'}).click();
  const section=page.getByRole('region',{name:'Sugestões táticas da IA'});
  await expect(section.getByRole('heading',{name:'Investigar proteção da área'})).toBeVisible();
  expect(state.requests[0].ai_analysis).toBe('optional');
  await section.getByText('Indicadores citados pela IA',{exact:true}).click();
  await expect(section.getByText('Equipe A · shots_for:',{exact:false})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Planos para investigar'})).toBeVisible();
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  expect(errors).toEqual([]);
});

test('cota esgotada preserva relatório e não repete pedido', async ({page}) => {
  const state=await mockApi(page,{requests:[],coverageRequests:[],advisorConfigured:true,advisorReason:'RATE_LIMIT'});await openComparison(page);
  await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();
  await page.getByRole('button',{name:'Comparar equipes'}).click();
  await expect(page.getByText('Cota ou limite de uso atingido.',{exact:false})).toBeVisible();
  await expect(page.getByRole('heading',{name:'O que o histórico mostra'})).toBeVisible();
  expect(state.requests).toHaveLength(1);
});

test('treinador pode desligar Gemini mesmo com chave configurada', async ({page}) => {
  const state=await mockApi(page,{requests:[],coverageRequests:[],advisorConfigured:true});await openComparison(page);
  await page.getByLabel('Incluir sugestões táticas da IA').uncheck();
  await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();await page.getByRole('button',{name:'Comparar equipes'}).click();
  await expect(page.getByRole('article')).toBeVisible();expect(state.requests[0].ai_analysis).toBeUndefined();
  await expect(page.getByRole('region',{name:'Sugestões táticas da IA'})).toHaveCount(0);
});
