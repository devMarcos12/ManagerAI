import { test, expect } from '@playwright/test';
import { mockApi, openComparison } from './fixtures';

test('provedor Groq aparece na configuração e no relatório',async({page})=>{
  const state=await mockApi(page,{requests:[],coverageRequests:[],advisorConfigured:true,advisorProvider:'groq'});
  await openComparison(page);
  await expect(page.getByText('Envia indicadores e contexto ao Groq.',{exact:false})).toBeVisible();
  await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();await page.getByRole('button',{name:'Comparar equipes'}).click();
  await expect(page.getByRole('region',{name:'Sugestões táticas da IA'}).getByText('Groq · test-model',{exact:false})).toBeVisible();
  expect(state.requests[0].ai_analysis).toBe('optional');
});


test('acesso negado não acusa chave inválida e identifica o provedor',async({page})=>{
  await mockApi(page,{requests:[],coverageRequests:[],advisorConfigured:true,advisorProvider:'groq',advisorReason:'PROVIDER_ACCESS_DENIED'});
  await openComparison(page);
  await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();await page.getByRole('button',{name:'Comparar equipes'}).click();
  const region=page.getByRole('region',{name:'Sugestões táticas da IA'});
  await expect(region.getByText('Groq · test-model',{exact:false})).toBeVisible();
  await expect(region.getByText('Isso não confirma chave inválida.',{exact:false})).toBeVisible();
  await expect(region.getByText('A chave não foi aceita.',{exact:false})).toHaveCount(0);
  await expect(page.getByRole('heading',{name:'O que o histórico mostra'})).toBeVisible();
});
