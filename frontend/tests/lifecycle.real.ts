import { test, expect } from '@playwright/test';
import { spawn, type ChildProcess } from 'node:child_process';
import { resolve, join } from 'node:path';
import { mkdirSync, writeFileSync } from 'node:fs';

test('API real: validação 422, backend indisponível e relatório perdido após reinício', async ({page, context}) => {
  test.skip(!process.env.MANAGERAI_E2E_REAL || !process.env.MANAGERAI_BACKEND_PYTHON, 'Exige Python instalado explicitamente para integração real');
  const root=resolve('..'); const destination=process.env.MANAGERAI_REAL_ARTIFACTS || '/tmp/managerai-frontend-real';mkdirSync(destination,{recursive:true});
  const env={...process.env,MANAGERAI_DATA_ROOT:resolve(root,'open-data/data'),MANAGERAI_OLLAMA_MODEL:'',MANAGERAI_PROXY_TARGET:'http://127.0.0.1:8012',PYTHONDONTWRITEBYTECODE:'1'};
  const backendArgs=['-I','-B','-m','uvicorn','managerai.api:create_app','--factory','--host','127.0.0.1','--port','8012','--workers','1','--no-access-log'];
  let backend:ChildProcess|undefined,frontend:ChildProcess|undefined;
  async function waitReady(url:string){await expect.poll(async()=>{try{return (await fetch(url)).status;}catch{return 0;}},{timeout:15000}).toBe(200);}
  async function stop(child:ChildProcess|undefined){if(child&&child.exitCode===null&&!child.killed){child.kill('SIGTERM');await new Promise<void>((resolve,reject)=>{const timer=setTimeout(()=>{child.kill('SIGKILL');reject(new Error('Processo de teste não encerrou'));},7000);child.once('exit',()=>{clearTimeout(timer);resolve();});});}}
  try{
    backend=spawn(process.env.MANAGERAI_BACKEND_PYTHON!,backendArgs,{cwd:root,env,stdio:'ignore'});
    frontend=spawn(process.execPath,['node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','5178'],{cwd:process.cwd(),env,stdio:'ignore'});
    await waitReady('http://127.0.0.1:8012/v1/health');await waitReady('http://127.0.0.1:5178');
    await page.goto('http://127.0.0.1:5178');await page.getByLabel('Minha equipe',{exact:true}).selectOption('36');await page.getByLabel('Adversário',{exact:true}).selectOption('1');await page.getByLabel('Partida de referência',{exact:true}).selectOption('3754314');
    await page.getByLabel('Mando declarado').selectOption('fora');await expect(page.getByRole('alert')).toContainText('Confira');
    await expect(page.getByRole('button',{name:'Analisar confronto'})).toBeDisabled();
    await page.getByLabel('Mando declarado').selectOption('desconhecido');await expect(page.getByRole('button',{name:'Analisar confronto'})).toBeEnabled();await page.getByRole('button',{name:'Analisar confronto'}).click();await expect(page.getByRole('article')).toBeVisible();
    await stop(backend);
    const unavailable=await context.newPage();await unavailable.goto('http://127.0.0.1:5178');await expect(unavailable.getByRole('heading',{name:'Não foi possível acessar os dados'})).toBeVisible();await unavailable.close();
    backend=spawn(process.env.MANAGERAI_BACKEND_PYTHON!,backendArgs,{cwd:root,env,stdio:'ignore'});await waitReady('http://127.0.0.1:8012/v1/health');
    const missing=page.waitForResponse(r=>r.url().includes('/export?format=json'));await page.getByRole('button',{name:'Exportar JSON'}).click();expect((await missing).status()).toBe(404);
    await expect(page.getByRole('alert')).toContainText('expirou');await expect(page.getByRole('article')).toBeVisible();
    writeFileSync(join(destination,'lifecycle-browser.json'),JSON.stringify({realAPI:true,realBrowser:true,mocks:false,invalidContextHTTP:422,backendUnavailableObserved:true,restartClearedReport:true,exportAfterRestartHTTP:404,pageRetainsReport:true,ttlClockAccelerated:false},null,2));
  }finally{await stop(frontend);await stop(backend);}
});
