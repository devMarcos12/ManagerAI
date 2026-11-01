import { test, expect } from '@playwright/test';
import { mockApi, openComparison } from './fixtures';

test('seleções dependentes, referência exclusiva, limites e padrão sem LLM', async ({page}) => {
  const state=await mockApi(page);await openComparison(page);
  const analyze=page.getByRole('button',{name:'Comparar equipes'});await expect(analyze).toBeEnabled();
  await expect(page.locator('#opponent option[value="1"]')).toHaveCount(0);
  await expect(page.getByLabel('Jogos anteriores por equipe')).toHaveAttribute('max','12');
  await page.getByLabel('Usar a data informada',{exact:true}).check();await page.getByLabel('Analisar jogos anteriores a',{exact:true}).fill('2020-01-07');await page.getByLabel('Adversário',{exact:true}).selectOption('2');
  await expect(analyze).toBeEnabled();await analyze.click();await expect(page.getByRole('article')).toBeVisible();
  expect(state.requests[0].explanation).toBe('none');expect(state.requests[0].analysis.cutoff_date).toBe('2020-01-07');expect(state.requests[0].analysis.target_match_id).toBeUndefined();
  await page.getByLabel('Partida histórica',{exact:true}).check();await expect(analyze).toBeEnabled();await analyze.click();await expect(page.getByRole('article')).toBeVisible();
  expect(state.requests[1].analysis.cutoff_date).toBeUndefined();expect(state.requests[1].analysis.target_match_id).toBe(8);
  await page.getByLabel('Incluir mapas e indicadores adicionais',{exact:true}).check();await page.getByText('Trocar competição ou temporada',{exact:true}).click();await page.getByLabel('Histórico da equipe',{exact:true}).selectOption('2/28');
  await expect(page.getByLabel('Incluir mapas e indicadores adicionais',{exact:true})).toBeDisabled();await expect(page.getByText('Histórico alterado.',{exact:false})).toBeVisible();
});

test('cobertura antiga não sobrescreve seleção nova e janela inválida bloqueia envio', async ({page}) => {
  await mockApi(page,{requests:[],coverageRequests:[],coverageDelay:n=>n===6?900:20});await openComparison(page);
  const analyze=page.getByRole('button',{name:'Comparar equipes'});await expect(analyze).toBeEnabled();
  await page.getByLabel('Jogos anteriores por equipe').fill('6');await page.waitForTimeout(350);
  await page.getByLabel('Jogos anteriores por equipe').fill('7');await expect(page.locator('.coverage-grid strong').first()).toContainText('7');
  await page.waitForTimeout(950);await expect(page.locator('.coverage-grid strong').first()).toContainText('7');
  await page.getByLabel('Jogos anteriores por equipe').fill('13');await expect(analyze).toBeDisabled();await expect(page.getByText('Informe de 1 a 12 jogos.')).toBeVisible();
});

test('insuficiência HTTP 200, dados nulos, evidências e exportação real do endpoint mockado', async ({page}) => {
  await mockApi(page);await openComparison(page);await page.getByLabel('Jogos anteriores por equipe').fill('1');
  const analyze=page.getByRole('button',{name:'Comparar equipes'});await expect(analyze).toBeEnabled();await analyze.click();
  await expect(page.getByRole('heading',{name:'Sem planos comparativos neste recorte'})).toBeVisible();
  await expect(page.getByText('Indisponível',{exact:true}).first()).toBeVisible();
  const download=page.waitForEvent('download');await page.getByRole('button',{name:'Exportar Markdown'}).click();expect((await download).suggestedFilename()).toBe('managerai-relatorio.md');
});

test('pedidos duplicados bloqueados e relatório associado ao pedido enviado', async ({page}) => {
  const state=await mockApi(page,{requests:[],coverageRequests:[],delayAnalysis:900});await openComparison(page);
  const analyze=page.getByRole('button',{name:'Comparar equipes'});await expect(analyze).toBeEnabled();await analyze.click();
  await expect(page.getByRole('button',{name:'Analisando histórico…'})).toBeDisabled();
  await page.getByLabel('Qual é a prioridade?').selectOption('buscar gol');await expect(page.getByRole('article')).toBeVisible();
  expect(state.requests).toHaveLength(1);expect(state.requests[0].analysis.strategic_objective).toBe('equilibrado');
  await expect(page.getByText('O formulário mudou.',{exact:false}).first()).toBeVisible();
});

test('exportação expirada não remove relatório recebido nem simula sucesso', async ({page}) => {
  await mockApi(page,{requests:[],coverageRequests:[],exportStatus:404});await openComparison(page);
  await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();await page.getByRole('button',{name:'Comparar equipes'}).click();
  await page.getByRole('button',{name:'Exportar JSON'}).click();await expect(page.getByRole('alert')).toContainText('expirou');await expect(page.getByRole('article')).toBeVisible();
  await expect(page.getByText('Arquivo recebido do servidor para download.')).toHaveCount(0);
});

test('backend indisponível permite reconexão explícita', async ({page}) => {
  const state=await mockApi(page,{requests:[],coverageRequests:[],bootstrapFail:true});await page.goto('/');
  await expect(page.getByRole('heading',{name:'Não foi possível acessar os dados'})).toBeVisible();state.bootstrapFail=false;
  await page.getByRole('button',{name:'Tentar conexão novamente'}).click();await expect(page.getByRole('combobox',{name:'Qual é o seu time?'})).toBeVisible();
});

for(const status of [413,422,429,500,503]) test(`erro ${status} sem retry automático`,async({page})=>{
  const state=await mockApi(page,{requests:[],coverageRequests:[],analysisStatus:status});await openComparison(page);const analyze=page.getByRole('button',{name:'Comparar equipes'});await expect(analyze).toBeEnabled();await analyze.click();
  await expect(page.getByRole('alert')).toBeVisible();expect(state.requests).toHaveLength(1);await expect(page.getByRole('article')).toHaveCount(0);
});

test('modos opcionais de explicação e falha explícita preservam relatório',async({page})=>{
  const state=await mockApi(page,{requests:[],coverageRequests:[],configured:true});await openComparison(page);
  await page.getByLabel('Explicação opcional',{exact:true}).selectOption('optional');await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();await page.getByRole('button',{name:'Comparar equipes'}).click();
  await expect(page.getByText('A explicação opcional não foi gerada',{exact:false})).toBeVisible();expect(state.requests[0].explanation).toBe('optional');
  await page.getByLabel('Explicação opcional',{exact:true}).selectOption('required');state.analysisStatus=503;await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();await page.getByRole('button',{name:'Comparar equipes'}).click();await expect(page.getByRole('alert')).toBeVisible();
});

test('mobile, teclado e datas de calendário sem deslocamento de fuso',async({page})=>{
  await page.setViewportSize({width:390,height:844});await mockApi(page);await page.goto('/');await expect(page.getByRole('combobox',{name:'Qual é o seu time?'})).toBeVisible();await page.keyboard.press('Tab');await expect(page.getByRole('link',{name:'Ir para preparação do confronto'})).toBeFocused();
  await page.keyboard.press('Enter');await openComparison(page);await expect(page.getByLabel('Partida de referência')).toContainText('08/01/2020');
  await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();await page.getByRole('button',{name:'Comparar equipes'}).click();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
});

test('gráficos e indicadores adicionais são carregados sob demanda, preservando nulos',async({page})=>{
  await mockApi(page);await openComparison(page);await page.getByLabel('Incluir mapas e indicadores adicionais',{exact:true}).check();await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();await page.getByRole('button',{name:'Comparar equipes'}).click();await expect(page.getByRole('article')).toBeVisible();
  await expect(page.locator('.pitch-figure')).toHaveCount(0);await page.getByText('Explorar mapas e indicadores adicionais',{exact:true}).click();await expect(page.locator('.pitch-figure')).toHaveCount(2);await expect(page.locator('.shot.unknown')).toHaveCount(2);
  await page.getByText('Consultar todos os indicadores e suas amostras',{exact:true}).click();await expect(page.getByRole('table').first()).toBeVisible();await expect(page.getByRole('table').first()).toContainText('Indisponível');
  await page.locator('.evidence summary').first().click();await expect(page.getByText('Numerador: 5 · Denominador: 1.',{exact:false}).first()).toBeVisible();
});

test('recorte V3 recusado não gera fallback silencioso',async({page})=>{
  const state=await mockApi(page,{requests:[],coverageRequests:[],analysisStatus:422,analysisCode:'SEASON_NOT_CERTIFIED'});await openComparison(page);await page.getByLabel('Incluir mapas e indicadores adicionais',{exact:true}).check();await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();await page.getByRole('button',{name:'Comparar equipes'}).click();
  await expect(page.getByRole('alert')).toContainText('Desmarque V3 explicitamente');await expect(page.getByLabel('Incluir mapas e indicadores adicionais',{exact:true})).toBeChecked();expect(state.requests).toHaveLength(1);
});

test('timeout no navegador explica que cálculo pode continuar e não reenvia',async({page})=>{
  const state=await mockApi(page,{requests:[],coverageRequests:[],hangAnalysis:true});await openComparison(page);await expect(page.getByRole('button',{name:'Comparar equipes'})).toBeEnabled();await page.clock.install();await page.getByRole('button',{name:'Comparar equipes'}).click();await expect.poll(()=>state.requests.length).toBe(1);
  await page.clock.fastForward(120100);await expect(page.getByRole('alert')).toContainText('O cálculo pode continuar no servidor');expect(state.requests).toHaveLength(1);
});

test('qualidade é opt-in e incompatibilidade com V3 não muda escolhas silenciosamente',async({page})=>{
  const state=await mockApi(page);await openComparison(page);
  const analyze=page.getByRole('button',{name:'Comparar equipes'});await expect(analyze).toBeEnabled();
  const quality=page.getByLabel('Aplicar filtros de qualidade por indicador',{exact:true});
  const v3=page.getByLabel('Incluir mapas e indicadores adicionais',{exact:true});
  await expect(quality).not.toBeChecked();await quality.check();await expect(v3).toBeDisabled();
  await expect(analyze).toBeEnabled();await analyze.click();await expect(page.getByRole('article')).toBeVisible();
  expect(state.requests[0].data_policy).toBe('quality_v1');expect(state.requests[0].include_v3).toBe(false);
  const section=page.getByRole('region',{name:'Qualidade dos dados'});
  await expect(section.getByRole('heading',{name:'Qualidade aplicada aos indicadores'})).toBeVisible();
  await expect(section.getByRole('table')).toHaveCount(0);
  await section.getByText('Conferir amostras e motivos de exclusão',{exact:true}).click();
  await expect(section.getByRole('table')).toContainText('5 de 6');
  await expect(section.getByRole('table')).toContainText('Partidas excluídas: 99');
  await expect(section.getByRole('table')).toContainText('Arquivo de eventos ausente');
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await quality.uncheck();await v3.check();await expect(quality).toBeDisabled();await expect(v3).toBeChecked();
});
