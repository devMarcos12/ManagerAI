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
