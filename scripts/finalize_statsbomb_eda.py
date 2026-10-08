#!/usr/bin/env python3
"""Consolida lotes da EDA sem reler os JSONs de eventos."""
import json
from datetime import datetime, timezone
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import run_statsbomb_eda as s

def merge(parts,dst):
    tables=[pq.read_table(p) for p in parts]
    schema=pa.unify_schemas([t.schema for t in tables])
    pq.write_table(pa.concat_tables([t.cast(schema) for t in tables]),dst)

def main():
    base=s.BASE_OUT
    if (base/'RELATORIO.md').exists(): raise SystemExit(f"Saída final já existe: {base}")
    base.mkdir(parents=True,exist_ok=True); s.OUT=base; s.FIG=base/'graficos'; s.docs()
    _,manifest=s.inventory()
    principal=manifest[(manifest.competition_id==s.CFG['competition_id'])&(manifest.season_id==s.CFG['season_id'])].copy()
    principal['processing_status']='selecionada'; s.write_df(principal,'manifesto_recorte')
    lots=sorted((base/'lotes').glob('lote*'))
    if len(lots)!=5: raise RuntimeError(f'Esperados 5 lotes, encontrados {len(lots)}')
    ep=[p for x in lots for p in sorted((x/'intermediarios').glob('eventos_*.parquet'))]
    lp=[p for x in lots for p in sorted((x/'intermediarios').glob('escalacoes_*.parquet'))]
    if not all(x.exists() for x in ep+lp): raise RuntimeError('Tabela intermediária ausente')
    (base/'tabelas').mkdir(exist_ok=True); merge(ep,base/'tabelas'/'eventos_recorte.parquet'); merge(lp,base/'tabelas'/'escalacoes_recorte.parquet')
    cols=['match_id','match_date','event_id','index','period','minute','second','duration','type_name','team_id','team_name','player_id','possession','possession_team_id','play_pattern','under_pressure','x','y','end_x','end_y','pass_cross','pass_outcome','pass_completed','carry_end_x','carry_end_y','shot_xg','shot_outcome','shot_type']
    ev=pd.read_parquet(base/'tabelas'/'eventos_recorte.parquet',columns=cols).sort_values(['match_id','period','index'])
    lu=pd.read_parquet(base/'tabelas'/'escalacoes_recorte.parquet',columns=['match_id','team_id','team_name','player_id'])
    tm=s.team_match(principal,ev); q=s.quality(principal,ev,lu); hist=s.report(principal,ev,tm,q,manifest)
    checkpoint={'concluido':True,'data_execucao_utc':datetime.now(timezone.utc).isoformat(),'config':s.CFG,'git_open_data':s.git_rev(),'arquivos_gerados':[str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()],'falhas_leitura':0,'pendencias':['Documentação doc/ ausente no clone; complementar com documentação oficial.','Não há arquivos 360 no recorte principal; estudo espacial foi omitido.','Placar por evento e transições causais foram omitidos por não terem validação suficiente.']}
    (base/'CHECKPOINT.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf-8'); s.notebook()
    print(json.dumps({'saida':str(base),'partidas':len(principal),'eventos':len(ev),'escalações':len(lu)},ensure_ascii=False))
if __name__=='__main__': main()
