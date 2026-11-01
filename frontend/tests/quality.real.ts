import { prepareRealComparison } from './real_selection';
import { test, expect } from '@playwright/test';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

// Requer os eventos/escalações da La Liga 2015/16 e a API instalada atualizada.
test.skip(!process.env.MANAGERAI_E2E_REAL, 'Integração real opt-in');
const destination=process.env.MANAGERAI_REAL_ARTIFACTS || '/tmp/managerai-quality-real';
test.beforeAll(()=>mkdirSync(destination,{recursive:true}));

for(const scenario of [
  {name:'classic',team:'220',opponent:'217',target:'267533',window:'10',pressure:10},
  {name:'duration',team:'223',opponent:'1049',target:'3825672',window:'10',pressure:9},
  {name:'insufficient',team:'220',opponent:'217',target:'267533',window:'1',pressure:1},
]) test(`qualidade real: ${scenario.name}`,async({page})=>{
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  await prepareRealComparison(page, 11, 27, Number(scenario.team), Number(scenario.opponent), Number(scenario.target));
  await page.getByLabel('Jogos anteriores por equipe').fill(scenario.window);
  await page.getByLabel('Aplicar filtros de qualidade por indicador',{exact:true}).check();
  await expect(page.getByLabel('Incluir mapas e indicadores adicionais',{exact:true})).toBeDisabled();
  const analyze=page.getByRole('button',{name:'Comparar equipes'});await expect(analyze).toBeEnabled();
  const responsePromise=page.waitForResponse(r=>r.url().endsWith('/v1/analyses')&&r.request().method()==='POST');
  const started=Date.now();await analyze.click();const response=await responsePromise;
  expect(response.status()).toBe(200);const report=await response.json();
  const quality=page.getByRole('region',{name:'Qualidade dos dados'});
  await expect(quality.getByRole('heading',{name:'Qualidade aplicada aos indicadores'})).toBeVisible();
  expect(report.request.data_policy).toBe('quality_v1');
  expect(report.data_quality.full_snapshot_status).toBe('not_checked');
  expect(report.data_quality.spatial_season_certified).toBe(false);
  expect(report.evidence['opponent_profile.metrics.pressures'].sample_size).toBe(scenario.pressure);
  expect(report.evidence['opponent_profile.metrics.shots_for'].sample_size).toBe(Number(scenario.window));
  expect(report.evidence['team_profile.metrics.final_third_entries'].value).toBeNull();
  expect(report.plans.map((p:{plan_id:string})=>p.plan_id)).toEqual(scenario.window==='1'?[]:['R03_CHANCES']);
  await quality.getByText('Conferir amostras e motivos de exclusão',{exact:true}).click();
  await expect(quality.locator('tbody tr')).toHaveCount(42);
  await expect(quality.getByRole('table')).toContainText('Temporada sem certificação espacial');
  if(scenario.name==='duration'){
    expect(report.evidence['opponent_profile.metrics.pressures'].match_ids).not.toContain(3825665);
    await expect(quality.getByRole('table')).toContainText('Duração inválida');
    await expect(quality.getByRole('table')).toContainText('9 de 10');
  }
  if(scenario.window==='1')await expect(page.getByRole('heading',{name:'Sem planos comparativos neste recorte'})).toBeVisible();
  for(const [name,ext] of [['Exportar JSON','json'],['Exportar Markdown','md']]){
    const promise=page.waitForEvent('download');await page.getByRole('button',{name}).click();
    const download=await promise;expect(await download.failure()).toBeNull();
    const path=join(destination,`${scenario.name}.${ext}`);await download.saveAs(path);
    if(ext==='json')expect(JSON.parse(readFileSync(path,'utf8'))).toEqual(report);
    else expect(readFileSync(path,'utf8')).toContain('Qualidade dos dados');
  }
  await quality.scrollIntoViewIfNeeded();await page.screenshot({path:join(destination,`${scenario.name}-desktop.png`)});
  await page.setViewportSize({width:390,height:844});await quality.scrollIntoViewIfNeeded();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await page.screenshot({path:join(destination,`${scenario.name}-mobile.png`)});
  expect(errors).toEqual([]);
  writeFileSync(join(destination,`${scenario.name}-checks.json`),JSON.stringify({realAPI:true,realBrowser:true,mocks:false,
    target:scenario.target,window:scenario.window,opponentPressureSample:scenario.pressure,
    analysisAndChecksMs:Date.now()-started,jsonExportEqualsAPI:true,markdownQuality:true,pageErrors:errors,
    desktop:[1440,1000],mobile:[390,844],horizontalOverflow:false},null,2));
});
