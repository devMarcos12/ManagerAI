import { test, expect } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
const destination = process.env.MANAGERAI_REAL_ARTIFACTS || '/tmp/managerai-frontend-real';
test.beforeAll(()=>mkdirSync(destination,{recursive:true}));
test.skip(!process.env.MANAGERAI_E2E_REAL, 'Integração real opt-in');

async function city(page: import('@playwright/test').Page) {
  await page.goto('/');
  await page.getByLabel('Competição',{exact:true}).selectOption('2');
  await page.getByLabel('Temporada',{exact:true}).selectOption('27');
  await page.getByLabel('Minha equipe',{exact:true}).selectOption('36');
  await page.getByLabel('Adversário',{exact:true}).selectOption('1');
  await page.getByLabel('Partida de referência',{exact:true}).selectOption('3754314');
}

test('API real: V3, planos, evidências, downloads e responsividade desktop/mobile',async({page})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await city(page);
  await page.getByLabel('Incluir análise por eventos (V3)',{exact:true}).check();
  await expect(page.getByRole('button',{name:'Analisar confronto'})).toBeEnabled();
  const tick=Date.now();const responsePromise=page.waitForResponse(r=>r.url().endsWith('/v1/analyses')&&r.request().method()==='POST');
  await page.getByRole('button',{name:'Analisar confronto'}).click();const response=await responsePromise;
  expect(response.status()).toBe(200);const bytes=(await response.body()).byteLength;
  await expect(page.getByRole('article').getByRole('heading',{name:'Manchester City × Arsenal'})).toBeVisible();
  const analysisAndRenderMs=Date.now()-tick;
  await expect(page.locator('.plan')).not.toHaveCount(0);
  await page.getByText('Explorar gráficos por eventos (V3)',{exact:true}).click();
  await expect(page.getByRole('img',{name:'Mapa de finalizações de Manchester City, coordenadas StatsBomb 120 por 80'})).toBeVisible();
  await page.locator('.pitch-grid').scrollIntoViewIfNeeded();await page.screenshot({path:join(destination,'desktop-charts.png')});
  const responsiveness=await page.evaluate(async()=>{const started=performance.now();await new Promise(requestAnimationFrame);return performance.now()-started;});
  for(const [name,extension] of [['Exportar JSON','json'],['Exportar Markdown','md']]){
    const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name}).click();const download=await downloadPromise;
    expect(await download.failure()).toBeNull();await download.saveAs(join(destination,`city-report.${extension}`));
  }
  await page.getByRole('article').scrollIntoViewIfNeeded();await page.screenshot({path:join(destination,'desktop-report.png')});
  await page.locator('.evidence summary').first().click();await expect(page.getByRole('table').first()).toBeVisible();
  await page.setViewportSize({width:390,height:844});await page.getByRole('article').getByRole('heading',{name:'Manchester City × Arsenal'}).scrollIntoViewIfNeeded();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await page.screenshot({path:join(destination,'mobile-report.png')});
  await page.getByText('Consultar todos os indicadores e suas amostras',{exact:true}).click();
  await expect(page.locator('.all-metrics table tbody tr')).toHaveCount(47);
  await page.locator('.all-metrics table').scrollIntoViewIfNeeded();await page.screenshot({path:join(destination,'mobile-indicators.png')});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  writeFileSync(join(destination,'city-browser.json'),JSON.stringify({realAPI:true,realBrowser:true,mocks:false,jsonBytes:bytes,analysisAndRenderMs,requestAnimationFrameDelayMs:responsiveness,pageErrors:errors,desktop:[1440,1000],mobile:[390,844],horizontalOverflow:false,explanation:'none'},null,2));
  expect(errors).toEqual([]);
});

test('API real: insuficiência e abstenção',async({page})=>{
  await page.goto('/');await page.getByLabel('Competição',{exact:true}).selectOption('11');await page.getByLabel('Temporada',{exact:true}).selectOption('90');
  await page.getByLabel('Minha equipe',{exact:true}).selectOption('220');await page.getByLabel('Adversário',{exact:true}).selectOption('217');
  await page.getByLabel('Partida de referência',{exact:true}).selectOption('3773497');await page.getByLabel('Incluir análise por eventos (V3)',{exact:true}).check();
  await expect(page.getByRole('button',{name:'Analisar confronto'})).toBeEnabled();await page.getByRole('button',{name:'Analisar confronto'}).click();
  await expect(page.getByRole('heading',{name:'Sem planos comparativos neste recorte'})).toBeVisible();await expect(page.locator('.plan')).toHaveCount(0);
  await page.screenshot({path:join(destination,'insufficient-report.png')});
  writeFileSync(join(destination,'insufficient-browser.json'),JSON.stringify({realAPI:true,realBrowser:true,abstained:true,plans:0}));
});

test('API real: explicação opcional configurada e resultado explícito',async({page})=>{
  await city(page);await page.getByText('Opções avançadas',{exact:true}).click();
  const select=page.getByLabel('Explicação opcional',{exact:true});test.skip(await select.isDisabled(),'Provedor não configurado no servidor');
  await select.selectOption('optional');await expect(page.getByRole('button',{name:'Analisar confronto'})).toBeEnabled();
  const promise=page.waitForResponse(r=>r.url().endsWith('/v1/analyses'));await page.getByRole('button',{name:'Analisar confronto'}).click();const response=await promise;
  expect(response.status()).toBe(200);const report=await response.json();await expect(page.getByRole('heading',{name:'Explicação opcional',exact:true})).toBeVisible();
  writeFileSync(join(destination,'llm-browser.json'),JSON.stringify({realAPI:true,realBrowser:true,status:report.explanation.status,provider:report.explanation.provider,model:report.explanation.model,durationSeconds:report.explanation.duration_seconds,reason:report.explanation.reason},null,2));
  expect(['generated','failed','unavailable']).toContain(report.explanation.status);
});
