// Fixtures sintéticas somente para testes portáteis; não são evidências esportivas.
import type { Page } from '@playwright/test';
import type { AnalysisRequest, Report, Evidence, TeamRequest, TeamReport } from '../src/api';
export const capabilities = { schema_version: '2.0.0', engines: ['deterministic'], llm: { configured: false, provider: null, model: null, mode: 'validated_claim_selection', availability: 'checked_on_generation' }, fine_tuned_model: 'experimental_not_promoted', shots_prediction: 'experimental_not_integrated', individual_recommendations: false, v3_recuts: [[2,27]], limits: { request_bytes:64000, window:12, concurrent_analyses:1, analyses_per_minute:10, report_bytes:32000000, retained_reports:8, report_ttl_seconds:300 }, storage:'Memória', data_policies:['legacy','quality_v1'] };
const catalog = [{ competition_id:2, season_id:27, competition_name:'Premier League', season_name:'2015/2016', country_name:'England', v3_certified:true }, { competition_id:2, season_id:28, competition_name:'Premier League', season_name:'2016/2017', v3_certified:false }, {competition_id:11,season_id:90,competition_name:'La Liga',season_name:'2020/2021',v3_certified:true}];
export function makeReport(request: AnalysisRequest): Report {
  const n = request.analysis.recent_matches_window === 1 ? 1 : 5;
  const evidence: Record<string, Evidence> = {};
  for (const side of ['team','opponent']) for (const key of ['shots_for','shots_against','xg_for','xg_against','pass_accuracy','final_third_entries','final_third_pass_entries','final_third_carry_entries']) {
    const v3 = key.includes('_pass_') || key.includes('_carry_');
    evidence[`${v3?'tactical_v3.':''}${side}_profile.metrics.${key}`] = { team_id:side==='team'?1:2,team_name:side==='team'?'Equipe A':'Equipe B',metric_id:key,value:key==='xg_for'?null:5,unit:key.includes('entries')?'eventos/90':'eventos/jogo',sample_size:n,match_ids:[1],numerator:5,denominator:1,median:5,standard_deviation:null,formula_version:'1.0.0',per_match:[{match_id:1,match_date:'2020-01-01',value:5,numerator:5,denominator:1}] };
  }
  const profile = (id: number, name: string) => ({team_id:id,team_name:name,period_start:'2020-01-01',period_end:'2020-01-07',match_ids:[1,2,3,4,5],shots:[{id:'synthetic-shot',match_id:1,team_id:id,period:1,x:110,y:40,xg:null}]});
  const metricCoverage = (name: string) => ({team_name:name,sample_sizes:{shots_for:n},minimum_sample_size:n,insufficient_metrics:n<5?['shots_for']:[]});
  return { schema_version:'2.0.0',report_id:'synthetic-report',report_key:'synthetic-key',request:{...request,data_policy:request.data_policy || 'legacy'},legacy_report:{},evidence,
    ...(request.data_policy==='quality_v1' ? {data_quality:{policy_version:'quality-report-1',applied:true,scope:'selected_history_only' as const,full_snapshot_status:'not_checked' as const,spatial_season_certified:false,minimum_matches:5,required_core_metrics:['shots_for'],mask_fingerprint:'synthetic',metrics:[{evidence_id:'team_profile.metrics.shots_for',metric_id:'shots_for',team_id:1,team_name:'Equipe A',family:'shot_counts',original_sample_size:n,usable_sample_size:n,selected_matches:n+1,excluded_match_ids:[99],reason_counts:{not_diagnosed:1}}],reason_labels:{not_diagnosed:'Arquivo de eventos ausente na janela selecionada.'},limitations:['Fixture sintética, sem certificação.']}} : {}),
    display:{competition:'Premier League',season:'2015/2016',cutoff_date:'2020-01-08',team:profile(1,'Equipe A'),opponent:profile(2,'Equipe B'),sources:[{path:'events/1.json',sha256:'synthetic-hash'}],metric_definitions:{}},
    sufficiency:{status:n<5?'amostra insuficiente':'evidência limitada',sufficient:n>=5,minimum_matches:5,warnings:[],team:metricCoverage('Equipe A'),opponent:metricCoverage('Equipe B')},
    plans:n<5?[]:[{plan_id:'R01_PROGRESSAO',observation:'Observação sintética',evidence_ids:['opponent_profile.metrics.final_third_entries'],condition:'Conferir em vídeo.',possible_action:'Investigar proteção das zonas.',risks:['Pode conceder território.'],restrictions:[],limitations:['Sem eficácia validada.'],preconditions:['Avaliar no treino.'],abstention_reason:null,context_priority:0}],
    excluded_plans:[],plan_comparisons:[],abstention_reason:n<5?'Evidência central insuficiente.':null,
    ordering:{version:'context-order-2',meaning:'Prioridade declarada',ties:'Sem mérito',rule:'+2/+1',objective_note:null},
    roster_policy:{status:'missing',provenance:'Declaração',individual_suggestions:'abstained',reason:'Sem avaliação individual.'},
    model_status:{tactical:'deterministic',shots_predictor:'experimental_not_integrated',fine_tuned_explainer:'experimental_not_promoted'},
    explanation:{status:request.explanation==='optional'?'unavailable':'disabled',reason:null,provider:null,model:null,prompt_version:'1',input_fingerprint:'synthetic',claims:[],policy:'Seleção restrita'},limitations:['Histórico não é previsão.'],provenance:{} };
}
export const coachTeams = [1,2,3].map(id => ({team_id:id,name:`Equipe ${String.fromCharCode(64+id)}`,aliases:[`Equipe ${String.fromCharCode(64+id)}`],recuts:[
  {competition_id:2,season_id:27,competition_name:'Premier League',season_name:'2015/2016',competition_gender:'male',first_date:'2020-01-01',last_date:'2020-01-09',calendar_matches:9,event_matches:9},
  {competition_id:2,season_id:28,competition_name:'Premier League',season_name:'2016/2017',competition_gender:'male',first_date:'2019-01-01',last_date:'2019-01-09',calendar_matches:9,event_matches:9},
]}));
export function makeTeamReport(body: TeamRequest): TeamReport {
  const pair = makeReport({schema_version:'2.0.0',engine:'deterministic',explanation:'none',include_v3:false,intended_strategy:'equilibrada',analysis:{...body,opponent_id:2,match_context:'regular',notes:'',strategic_objective:'equilibrado',venue:'desconhecido'}});
  const metrics = Object.fromEntries(Object.entries(pair.evidence).filter(([key])=>key.startsWith('team_profile.')).map(([,value])=>[value.metric_id,value]));
  return {schema_version:'team-overview-1',request:body,competition:'Premier League',season:'2015/2016',
    profile:{...pair.display.team,metrics,quality:{},sample_status:body.recent_matches_window===1?'insuficiente':'limitada'},
    coverage:{team_id:body.team_id,team_name:'Equipe A',calendar_matches_before_cutoff:9,selected_match_ids:[1,2,3,4,5],selected_match_dates:['2020-01-01'],event_match_ids:[1,2,3,4,5],missing_event_match_ids:[],available_period_start:'2020-01-01',available_period_end:'2020-01-07',selected_period_start:'2020-01-01',selected_period_end:'2020-01-07',event_period_start:'2020-01-01',event_period_end:'2020-01-07',warnings:[]},
    metric_definitions:Object.fromEntries(Object.keys(metrics).map(key=>[key,{title:key==='shots_for'?'Finalizações por jogo':key,unit:metrics[key].unit,explanation:'Definição sintética.'}])),
    sample_status:body.recent_matches_window===1?'amostra insuficiente':'evidência limitada',insufficient_metrics:body.recent_matches_window===1?['shots_for']:[],minimum_matches:5,warnings:[],limitations:['Fixture sintética.'],methodology:{formula_version:'1.0.0',temporal_policy:'Dia do corte excluído.',data_policy:'legacy',data_fingerprint:'synthetic',sources:[],attribution:'StatsBomb Open Data'}};
}
export async function selectTeam(page: Page, name = 'Equipe A') {
  await page.getByRole('combobox',{name:'Qual é o seu time?'}).fill(name);
  await page.getByRole('option',{name:new RegExp(name)}).click();
}
export async function openComparison(page: Page) {
  await page.goto('/'); await selectTeam(page);
  await page.getByLabel('Preparar contra um adversário').check();
  await page.getByLabel('Adversário',{exact:true}).selectOption('2');
  await page.getByText('Mais opções de análise',{exact:true}).click();
  await page.getByLabel('Partida histórica',{exact:true}).check();
  await page.getByText('Como será o jogo? (opcional)',{exact:true}).click();
}

export interface MockState { analysisStatus?:number; analysisCode?:string; hangAnalysis?:boolean; exportStatus?:number; bootstrapFail?:boolean; configured?:boolean; delayAnalysis?:number; coverageDelay?:(window:number)=>number; requests:AnalysisRequest[]; coverageRequests:AnalysisRequest[]; teamRequests?:TeamRequest[]; teamDelay?:number; index?:typeof coachTeams }
export async function mockApi(page: Page, state: MockState = {requests:[],coverageRequests:[]}) {
  await page.route('**/v1/**', async route => {
    const path = new URL(route.request().url()).pathname;
    const fulfill = async (data: unknown, status=200) => { try { await route.fulfill({status,json:data}); } catch { /* Busca cancelada pelo cliente. */ } };
    if (state.bootstrapFail) return route.abort('connectionfailed');
    if (path.endsWith('/health')) return fulfill({status:'ok',service_version:'2.0.0',data_present:true});
    if (path.endsWith('/capabilities')) return fulfill({...capabilities,llm:{...capabilities.llm,configured:!!state.configured}});
    if (path.endsWith('/catalog')) return fulfill(catalog);
    if (path.endsWith('/coach/teams')) return fulfill({teams:state.index || coachTeams,warnings:[]});
    if (path.endsWith('/team-coverage')) {
      const body=route.request().postDataJSON() as TeamRequest; const report=makeTeamReport(body);
      return fulfill({team:report.coverage,cutoff:body.cutoff_date,requested_window:body.recent_matches_window,minimum_matches:5,policy:'Dia do corte excluído.'});
    }
    if (path.endsWith('/team-analyses')) {
      const body=route.request().postDataJSON() as TeamRequest; (state.teamRequests ||= []).push(body);
      if(state.teamDelay) await new Promise(resolve=>setTimeout(resolve,state.teamDelay));
      return state.analysisStatus ? fulfill({code:'SYNTHETIC_ERROR'},state.analysisStatus) : fulfill(makeTeamReport(body));
    }
    if (path.endsWith('/teams')) return fulfill([{team_id:1,name:'Equipe A'},{team_id:2,name:'Equipe B'},{team_id:3,name:'Equipe C'}]);
    if (path.endsWith('/matches')) return fulfill([{match_id:8,date:'2020-01-08',home_team_id:1,away_team_id:2},{match_id:9,date:'2020-01-09',home_team_id:1,away_team_id:3}]);
    if (path.endsWith('/coverage')) {
      const body = route.request().postDataJSON() as AnalysisRequest; state.coverageRequests.push(body);
      const n = body.analysis.recent_matches_window || 10;
      await new Promise(resolve => setTimeout(resolve, state.coverageDelay?.(n) || 0));
      const coverage = (id:number,name:string) => ({team_id:id,team_name:name,calendar_matches_before_cutoff:20,selected_match_ids:Array.from({length:n},(_,i)=>i+1),selected_match_dates:['2020-01-01'],event_match_ids:Array.from({length:n},(_,i)=>i+1),missing_event_match_ids:[],available_period_start:'2020-01-01',available_period_end:'2020-01-07',selected_period_start:'2020-01-01',selected_period_end:'2020-01-07',event_period_start:'2020-01-01',event_period_end:'2020-01-07',warnings:n<5?['Amostra insuficiente; exploração descritiva.']:[]});
      return fulfill({team:coverage(1,'Equipe A'),opponent:coverage(2,'Equipe B'),cutoff:body.analysis.cutoff_date||'2020-01-08',requested_window:n,minimum_matches:5,policy:'Dia do corte excluído.'});
    }
    if (path.endsWith('/analyses')) {
      const body=route.request().postDataJSON() as AnalysisRequest;state.requests.push(body);
      if(state.hangAnalysis) return new Promise<void>(()=>{});
      if(state.delayAnalysis) await new Promise(resolve=>setTimeout(resolve,state.delayAnalysis));
      return state.analysisStatus ? fulfill({code:state.analysisCode||'SYNTHETIC_ERROR',message:'não expor stack trace'},state.analysisStatus) : fulfill(makeReport(body));
    }
    if (path.endsWith('/export')) return state.exportStatus ? fulfill({code:'REPORT_NOT_FOUND'},state.exportStatus) : route.fulfill({status:200,contentType:'application/octet-stream',body:'synthetic export'});
    return fulfill({code:'NOT_FOUND'},404);
  });
  return state;
}
