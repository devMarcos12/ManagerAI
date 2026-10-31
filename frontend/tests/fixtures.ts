// Fixtures sintéticas somente para testes portáteis; não são evidências esportivas.
import type { Page } from '@playwright/test';
import type { AnalysisRequest, Report, Evidence } from '../src/api';
export const capabilities = { schema_version: '2.0.0', engines: ['deterministic'], llm: { configured: false, provider: null, model: null, mode: 'validated_claim_selection', availability: 'checked_on_generation' }, fine_tuned_model: 'experimental_not_promoted', shots_prediction: 'experimental_not_integrated', individual_recommendations: false, v3_recuts: [[2,27]], limits: { request_bytes:64000, window:12, concurrent_analyses:1, analyses_per_minute:10, report_bytes:32000000, retained_reports:8, report_ttl_seconds:300 }, storage:'Memória' };
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
  return { schema_version:'2.0.0',report_id:'synthetic-report',report_key:'synthetic-key',request,legacy_report:{},evidence,
    display:{competition:'Premier League',season:'2015/2016',cutoff_date:'2020-01-08',team:profile(1,'Equipe A'),opponent:profile(2,'Equipe B'),sources:[{path:'events/1.json',sha256:'synthetic-hash'}],metric_definitions:{}},
    sufficiency:{status:n<5?'amostra insuficiente':'evidência limitada',sufficient:n>=5,minimum_matches:5,warnings:[],team:metricCoverage('Equipe A'),opponent:metricCoverage('Equipe B')},
    plans:n<5?[]:[{plan_id:'R01_PROGRESSAO',observation:'Observação sintética',evidence_ids:['opponent_profile.metrics.final_third_entries'],condition:'Conferir em vídeo.',possible_action:'Investigar proteção das zonas.',risks:['Pode conceder território.'],restrictions:[],limitations:['Sem eficácia validada.'],preconditions:['Avaliar no treino.'],abstention_reason:null,context_priority:0}],
    excluded_plans:[],plan_comparisons:[],abstention_reason:n<5?'Evidência central insuficiente.':null,
    ordering:{version:'context-order-2',meaning:'Prioridade declarada',ties:'Sem mérito',rule:'+2/+1',objective_note:null},
    roster_policy:{status:'missing',provenance:'Declaração',individual_suggestions:'abstained',reason:'Sem avaliação individual.'},
    model_status:{tactical:'deterministic',shots_predictor:'experimental_not_integrated',fine_tuned_explainer:'experimental_not_promoted'},
    explanation:{status:request.explanation==='optional'?'unavailable':'disabled',reason:null,provider:null,model:null,prompt_version:'1',input_fingerprint:'synthetic',claims:[],policy:'Seleção restrita'},limitations:['Histórico não é previsão.'],provenance:{} };
}
export interface MockState { analysisStatus?:number; analysisCode?:string; hangAnalysis?:boolean; exportStatus?:number; bootstrapFail?:boolean; configured?:boolean; delayAnalysis?:number; coverageDelay?:(window:number)=>number; requests:AnalysisRequest[]; coverageRequests:AnalysisRequest[] }
export async function mockApi(page: Page, state: MockState = {requests:[],coverageRequests:[]}) {
  await page.route('**/v1/**', async route => {
    const path = new URL(route.request().url()).pathname;
    const fulfill = async (data: unknown, status=200) => { try { await route.fulfill({status,json:data}); } catch { /* Busca cancelada pelo cliente. */ } };
    if (state.bootstrapFail) return route.abort('connectionfailed');
    if (path.endsWith('/health')) return fulfill({status:'ok',service_version:'2.0.0',data_present:true});
    if (path.endsWith('/capabilities')) return fulfill({...capabilities,llm:{...capabilities.llm,configured:!!state.configured}});
    if (path.endsWith('/catalog')) return fulfill(catalog);
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
