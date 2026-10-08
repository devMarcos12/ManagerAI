#!/usr/bin/env python3
"""EDA reproduzível e orientada a memória para o clone local StatsBomb Open Data.

O recorte principal é definido explicitamente na configuração para manter a
comparação homogênea. Eventos são lidos e descartados partida a partida.
"""
from __future__ import annotations
import gc, json, math, os, platform, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import pyarrow.parquet as pq
import pyarrow as arrow

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "open-data" / "data"
BASE_OUT = ROOT / "outputs" / "statsbomb_eda_20261002_exec6"
OUT = BASE_OUT / "lotes" / os.environ["BATCH_ONLY"] if os.environ.get("BATCH_ONLY") else BASE_OUT
FIG = OUT / "graficos"
CFG = {"seed": 20261002, "competition_id": 2, "season_id": 27,
       "competicao": "Premier League", "temporada": "2015/2016",
       "time_proprio": "Manchester City", "adversario": "Arsenal",
       "match_alvo": 3754314, "data_corte": "2016-05-08",
       "janela_caso": 10, "progresso_reducao_min": 25.0,
       "terco_final_x": 80.0, "area_x": 102.0, "area_y_min": 18.0,
       "area_y_max": 62.0}

def readj(p):
    with open(p, encoding="utf-8") as f: return json.load(f)
def idname(d, prefix):
    d=d or {}; return d.get("id"), d.get("name")
def scalar(v, i): return v[i] if isinstance(v, list) and len(v)>i else None
def rate(a,b): return a/b if b else np.nan
def write_df(df,name):
    p=OUT/"tabelas"/(name+".parquet"); p.parent.mkdir(parents=True,exist_ok=True)
    df.to_parquet(p,index=False); return p
def git_rev():
    try: return subprocess.check_output(["git","-C",str(ROOT/"open-data"),"rev-parse","HEAD"],text=True).strip()
    except Exception: return "indisponível"
def elapsed(row):
    # Exposição: fim do último evento de períodos 1+2; não presume 90 min.
    sec=(row.get("minute") or 0)*60+(row.get("second") or 0)+(row.get("duration") or 0)
    return sec if row.get("period") in (1,2) else 0

def inventory():
    comps=readj(DATA/"competitions.json")
    files={k:list((DATA/k).rglob("*.json")) for k in ["matches","events","lineups","three-sixty"]}
    inv=[]
    for k,fs in files.items():
        sizes=[p.stat().st_size for p in fs]
        inv.append({"categoria":k,"arquivos":len(fs),"bytes":sum(sizes),"maior_bytes":max(sizes,default=0)})
    match_rows=[]
    comp_lookup={(x["competition_id"],x["season_id"]):x for x in comps}
    for (cid,sid),c in comp_lookup.items():
        mp=DATA/"matches"/str(cid)/(str(sid)+".json")
        if not mp.exists(): continue
        try: ms=readj(mp)
        except Exception: continue
        for m in ms:
            mid=m["match_id"]
            ep=DATA/"events"/(str(mid)+".json"); lp=DATA/"lineups"/(str(mid)+".json"); tp=DATA/"three-sixty"/(str(mid)+".json")
            h=m["home_team"]; a=m["away_team"]
            match_rows.append({"match_id":mid,"competition_id":cid,"season_id":sid,
                "competition":c.get("competition_name"),"season":c.get("season_name"),"gender":c.get("competition_gender"),
                "country":c.get("country_name"),"match_date":m.get("match_date"),"kick_off":m.get("kick_off"),
                "home_team_id":h.get("home_team_id"),"home_team":h.get("home_team_name"),"away_team_id":a.get("away_team_id"),"away_team":a.get("away_team_name"),
                "home_score":m.get("home_score"),"away_score":m.get("away_score"),"stage":(m.get("competition_stage") or {}).get("name"),
                "stadium":(m.get("stadium") or {}).get("name"),"events_path":str(ep.relative_to(ROOT)),"lineups_path":str(lp.relative_to(ROOT)),"three_sixty_path":str(tp.relative_to(ROOT)),
                "events_exists":ep.exists(),"lineups_exists":lp.exists(),"three_sixty_exists":tp.exists(),
                "metadata_360_available":bool(c.get("match_available_360")),"processing_status":"não selecionada"})
    manifest=pd.DataFrame(match_rows).sort_values(["competition_id","season_id","match_date","match_id"])
    write_df(manifest,"manifesto_partidas_completo")
    pd.DataFrame(inv).to_csv(OUT/"inventario_arquivos.csv",index=False)
    return comps,manifest

def deterministic_schema_sample(manifest):
    # Até 20 estratos distribuídos no catálogo; não são resultados da análise.
    strata=manifest.groupby(["competition_id","season_id"],sort=True)
    candidates=[g.sort_values("match_id").iloc[len(g)//2] for _,g in strata]
    if len(candidates)>20:
        ix=np.linspace(0,len(candidates)-1,20,dtype=int); candidates=[candidates[i] for i in ix]
    rows=[]; types=Counter(); keys=Counter()
    for m in candidates:
        ev=readj(ROOT/m.events_path)
        for e in ev:
            t=(e.get("type") or {}).get("name","?"); types[t]+=1
            for k in e: keys[k]+=1
        rows.append({"match_id":m.match_id,"competition":m.competition,"season":m.season,"eventos":len(ev),"tipos_distintos":len({(e.get('type') or {}).get('name') for e in ev})})
        del ev; gc.collect()
    pd.DataFrame(rows).to_csv(OUT/"amostra_inspecao_esquema.csv",index=False)
    return pd.DataFrame(rows),types,keys

def extract(main):
    evrows=[]; lurows=[]; errors=[]; event_parts=[]; lineup_parts=[]
    for n,m in enumerate(main.itertuples(index=False),1):
        try: events=readj(ROOT/m.events_path)
        except Exception as e: errors.append({"match_id":m.match_id,"arquivo":m.events_path,"erro":repr(e)}); continue
        for e in events:
            pa=e.get("pass") or {}; sh=e.get("shot") or {}; ca=e.get("carry") or {}; pr=e.get("pressure") or {}; br=e.get("ball_recovery") or {}
            typ=(e.get("type") or {}); team=e.get("team") or {}; player=e.get("player") or {}; poss=e.get("possession_team") or {}; patt=e.get("play_pattern") or {}
            loc=e.get("location"); end=pa.get("end_location") or ca.get("end_location")
            out=pa.get("outcome") or {}
            so=sh.get("outcome") or {}
            rec={"match_id":m.match_id,"match_date":m.match_date,"event_id":e.get("id"),"index":e.get("index"),"period":e.get("period"),"timestamp":e.get("timestamp"),"minute":e.get("minute"),"second":e.get("second"),"duration":e.get("duration"),
                 "type_id":typ.get("id"),"type_name":typ.get("name"),"team_id":team.get("id"),"team_name":team.get("name"),"player_id":player.get("id"),"player_name":player.get("name"),"possession":e.get("possession"),"possession_team_id":poss.get("id"),"possession_team_name":poss.get("name"),"play_pattern":patt.get("name"),"under_pressure":e.get("under_pressure"),"x":scalar(loc,0),"y":scalar(loc,1),
                 "end_x":scalar(end,0),"end_y":scalar(end,1),"pass_length":pa.get("length"),"pass_angle":pa.get("angle"),"pass_height":(pa.get("height") or {}).get("name"),"pass_type":(pa.get("type") or {}).get("name"),"pass_cross":pa.get("cross"),"pass_outcome":out.get("name"),"pass_recipient_id":(pa.get("recipient") or {}).get("id"),"pass_completed":(typ.get("name")=="Pass" and not bool(out)),
                 "carry_end_x":scalar(ca.get("end_location"),0),"carry_end_y":scalar(ca.get("end_location"),1),"shot_xg":sh.get("statsbomb_xg"),"shot_outcome":so.get("name"),"shot_type":(sh.get("type") or {}).get("name"),"shot_body_part":(sh.get("body_part") or {}).get("name"),"shot_freeze_frame_n":len(sh.get("freeze_frame") or []),"ball_recovery_offensive":br.get("offensive"),"pressure_counterpress":pr.get("counterpress"),"formation":(e.get("tactics") or {}).get("formation")}
            evrows.append(rec)
        # escalações isoladas em tabela própria
        try: lus=readj(ROOT/m.lineups_path)
        except Exception as e: errors.append({"match_id":m.match_id,"arquivo":m.lineups_path,"erro":repr(e)}); lus=[]
        for teamline in lus:
            for p in teamline.get("lineup",[]):
                lurows.append({"match_id":m.match_id,"team_id":teamline.get("team_id"),"team_name":teamline.get("team_name"),"player_id":p.get("player_id"),"player_name":p.get("player_name"),"jersey_number":p.get("jersey_number"),"country":(p.get("country") or {}).get("name"),"positions_json":json.dumps(p.get("positions",[]),ensure_ascii=False),"cards_json":json.dumps(p.get("cards",[]),ensure_ascii=False)})
        del events,lus
        # checkpoint intermediário: limita a memória a 25 partidas.
        if n%25==0 or n==len(main):
            ep=OUT/"intermediarios"/f"eventos_{n:03d}.parquet"; ep.parent.mkdir(exist_ok=True)
            lp=OUT/"intermediarios"/f"escalacoes_{n:03d}.parquet"
            pd.DataFrame(evrows).to_parquet(ep,index=False); pd.DataFrame(lurows).to_parquet(lp,index=False)
            event_parts.append(ep); lineup_parts.append(lp); evrows.clear(); lurows.clear(); gc.collect(); print(f"[checkpoint] {n}/{len(main)} partidas")
    if os.environ.get("BATCH_ONLY"):
        # A consolidação dos checkpoints é feita ao final, sem uma cópia extra por lote.
        return pd.DataFrame(),pd.DataFrame(),pd.DataFrame(errors)
    # A tabela completa permanece compacta em Parquet; na RAM entram só colunas analíticas.
    def merge_parts(parts, destination):
        tables=[pq.read_table(part) for part in parts]
        # Campos opcionais podem ser null no checkpoint e booleanos no próximo.
        schema=arrow.unify_schemas([t.schema for t in tables])
        pq.write_table(arrow.concat_tables([t.cast(schema) for t in tables]),destination)
    merge_parts(event_parts,OUT/"tabelas"/"eventos_recorte.parquet")
    merge_parts(lineup_parts,OUT/"tabelas"/"escalacoes_recorte.parquet")
    analytic_cols=["match_id","match_date","event_id","index","period","minute","second","duration","type_name","team_id","team_name","player_id","possession","possession_team_id","play_pattern","under_pressure","x","y","end_x","end_y","pass_cross","pass_outcome","pass_completed","carry_end_x","carry_end_y","shot_xg","shot_outcome","shot_type"]
    ev=pd.read_parquet(OUT/"tabelas"/"eventos_recorte.parquet",columns=analytic_cols).sort_values(["match_id","period","index"])
    lu=pd.read_parquet(OUT/"tabelas"/"escalacoes_recorte.parquet",columns=["match_id","team_id","team_name","player_id"])
    pd.DataFrame(errors).to_csv(OUT/"erros_leitura.csv",index=False)
    return ev,lu,pd.DataFrame(errors)

def smoke_test(main):
    """Teste explícito de três partidas antes da extração integral."""
    out=[]
    for m in main.sort_values("match_id").head(3).itertuples(index=False):
        ev=readj(ROOT/m.events_path); lu=readj(ROOT/m.lineups_path)
        out.append({"match_id":m.match_id,"eventos":len(ev),"equipes_escalacao":len(lu),
                    "ids_evento_unicos":len({e.get('id') for e in ev})==len(ev),
                    "equipes_eventos":len({(e.get('team') or {}).get('id') for e in ev if e.get('team')})})
        del ev,lu
    z=pd.DataFrame(out); z.to_csv(OUT/"teste_3_partidas.csv",index=False)
    if len(z)!=3 or not z.ids_evento_unicos.all() or not (z.equipes_escalacao==2).all():
        raise RuntimeError("Teste de 3 partidas falhou; extração integral interrompida")
    return z

def team_match(main,ev):
    records=[]
    for m in main.itertuples(index=False):
        me=ev[ev.match_id==m.match_id]
        exposure=max(me.apply(lambda r:elapsed(r),axis=1).max(),1)/60
        for tid,name,oid,oname,venue in [(m.home_team_id,m.home_team,m.away_team_id,m.away_team,"home"),(m.away_team_id,m.away_team,m.home_team_id,m.home_team,"away")]:
            x=me[me.team_id==tid]; opp=me[me.team_id==oid]; passes=x[x.type_name=="Pass"]; shots=x[x.type_name=="Shot"]
            pprog=passes[(passes.x < CFG['terco_final_x'])&(passes.end_x>=CFG['terco_final_x'])]
            c=x[x.type_name=="Carry"]; cprog=c[(c.x < CFG['terco_final_x'])&(c.carry_end_x>=CFG['terco_final_x'])]
            lane=pd.cut(x.x,[-.01,40,80,120],labels=["defensivo","meio","ofensivo"]).value_counts()
            records.append({"match_id":m.match_id,"match_date":m.match_date,"team_id":tid,"team_name":name,"opponent_id":oid,"opponent_name":oname,"venue_formal":venue,"stage":m.stage,"home_score":m.home_score,"away_score":m.away_score,"exposure_minutes":exposure,"events":len(x),"passes_attempted":len(passes),"passes_completed":passes.pass_completed.sum(),"pass_accuracy":rate(passes.pass_completed.sum(),len(passes)),"passes_under_pressure":int(passes.under_pressure.fillna(False).sum()),"pass_accuracy_under_pressure":rate(passes[passes.under_pressure.fillna(False)].pass_completed.sum(),int(passes.under_pressure.fillna(False).sum())),"progressive_passes":len(pprog),"progressive_carries":len(cprog),"final_third_entries":len(pprog)+len(cprog),"box_entries":int((((passes.x<CFG['area_x'])&(passes.end_x>=CFG['area_x'])&(passes.end_y.between(CFG['area_y_min'],CFG['area_y_max'])))|((c.x<CFG['area_x'])&(c.carry_end_x>=CFG['area_x'])&(c.carry_end_y.between(CFG['area_y_min'],CFG['area_y_max'])))).sum()),"crosses":int(passes.pass_cross.fillna(False).sum()),"shots":len(shots),"xg":shots.shot_xg.sum(min_count=1),"xg_per_shot":shots.shot_xg.mean(),"shots_conceded":len(opp[opp.type_name=="Shot"]),"xg_conceded":opp[opp.type_name=="Shot"].shot_xg.sum(min_count=1),"pressures":int((x.type_name=="Pressure").sum()),"recoveries":int((x.type_name=="Ball Recovery").sum()),"interceptions":int((x.type_name=="Interception").sum()),"duel_tackles":int(((x.type_name=="Duel") & x.apply(lambda r: False,axis=1)).sum()),"attacking_lane_events":lane.get("ofensivo",0),"middle_lane_events":lane.get("meio",0),"defensive_lane_events":lane.get("defensivo",0)})
    tm=pd.DataFrame(records); write_df(tm,"equipe_partida")
    return tm

def quality(main,ev,lu):
    raw_ids=ev.event_id
    passes=ev[ev.type_name=="Pass"]; shots=ev[ev.type_name=="Shot"]
    q=[{"verificacao":"IDs de evento únicos","resultado":raw_ids.nunique()==len(ev),"valor":f"{raw_ids.nunique()} / {len(ev)}"},
       {"verificacao":"match_id eventos no manifesto","resultado":ev.match_id.isin(main.match_id).all(),"valor":str(ev.match_id.nunique())},
       {"verificacao":"escalações match_id no manifesto","resultado":lu.match_id.isin(main.match_id).all(),"valor":str(lu.match_id.nunique())},
       {"verificacao":"xG presente entre finalizações","resultado":True,"valor":f"{shots.shot_xg.notna().mean():.1%} ({shots.shot_xg.notna().sum()}/{len(shots)})"},
       {"verificacao":"fim de passe presente entre passes","resultado":True,"valor":f"{passes.end_x.notna().mean():.1%} ({passes.end_x.notna().sum()}/{len(passes)})"},
       {"verificacao":"localização inicial presente entre eventos","resultado":True,"valor":f"{ev.x.notna().mean():.1%}"},
       {"verificacao":"índices duplicados dentro da partida","resultado":not ev.duplicated(["match_id","index"]).any(),"valor":str(ev.duplicated(["match_id","index"]).sum())}]
    pd.DataFrame(q).to_csv(OUT/"validacoes_qualidade.csv",index=False)
    return pd.DataFrame(q)

def plots(main,ev,tm,casehist):
    sns.set_theme(style="whitegrid",context="notebook"); FIG.mkdir(exist_ok=True)
    title="StatsBomb Open Data | Premier League 2015/16 | 380 partidas"
    # 1 coverage
    counts=pd.concat([main[["home_team","match_id"]].rename(columns={"home_team":"team"}),main[["away_team","match_id"]].rename(columns={"away_team":"team"})]).groupby("team").size().sort_values()
    ax=counts.plot.barh(figsize=(9,7),color="#2878b5"); ax.set(xlabel="Partidas no recorte",ylabel="Equipe",title=title+"\nCobertura por equipe"); plt.tight_layout(); plt.savefig(FIG/"01_cobertura_equipes.png",dpi=160); plt.close()
    # 2 type completeness
    z=ev.type_name.value_counts().head(20).sort_values(); ax=z.plot.barh(figsize=(9,7),color="#66a61e"); ax.set(xlabel="Eventos",ylabel="Tipo",title=title+"\n20 tipos de evento mais frequentes"); plt.tight_layout(); plt.savefig(FIG/"02_tipos_evento.png",dpi=160); plt.close()
    # 3 shot map
    s=ev[(ev.type_name=="Shot")&ev.shot_xg.notna()]; fig,ax=plt.subplots(figsize=(10,6)); sc=ax.scatter(s.x,s.y,c=s.shot_xg,s=np.maximum(s.shot_xg*420,12),cmap="magma",alpha=.7); ax.set(xlim=(80,120),ylim=(0,80),xlabel="Coordenada x StatsBomb (0–120; não metros)",ylabel="Coordenada y (0–80)",title=title+f"\nFinalizações elegíveis com xG (n={len(s)})"); fig.colorbar(sc,label="xG"); plt.tight_layout(); plt.savefig(FIG/"03_mapa_finalizacoes_xg.png",dpi=160); plt.close()
    # 4 pressure map
    p=ev[ev.type_name=="Pressure"]; fig,ax=plt.subplots(figsize=(10,6)); hb=ax.hexbin(p.x,p.y,gridsize=20,cmap="Blues",mincnt=1); ax.set(xlim=(0,120),ylim=(0,80),xlabel="x StatsBomb",ylabel="y StatsBomb",title=title+f"\nLocalização das ações Pressure (n={len(p)})"); fig.colorbar(hb,label="Pressures por célula"); plt.tight_layout(); plt.savefig(FIG/"04_mapa_pressao.png",dpi=160); plt.close()
    # 5 progressive distribution
    x=tm.assign(prog90=(tm.progressive_passes+tm.progressive_carries)*90/tm.exposure_minutes); top=x.groupby('team_name').prog90.agg(['mean','std','count']).sort_values('mean',ascending=False).head(12)
    ax=top['mean'].sort_values().plot.barh(xerr=top.loc[top.index,'std'].sort_values(),figsize=(9,6),color="#e67e22"); ax.set(xlabel="Entradas no terço final por 90 (média ± DP entre jogos)",ylabel="Equipe",title=title+"\nProgressão: top 12"); plt.tight_layout(); plt.savefig(FIG/"05_progressao_por90.png",dpi=160); plt.close()
    # 6 lanes selected case histories
    ids=casehist.team_id.unique(); ce=ev[ev.team_id.isin(ids)&ev.match_id.isin(casehist.match_id)].copy(); ce['corredor']=pd.cut(ce.y,[-.01,26.67,53.33,80],labels=['esquerdo','central','direito'])
    tab=ce.groupby(['team_name','corredor'],observed=True).size().unstack(fill_value=0); tab=tab.div(tab.sum(axis=1),axis=0)*100; ax=tab.plot.bar(figsize=(8,5),color=['#377eb8','#4daf4a','#e41a1c']); ax.set(ylabel='% das ações com localização',xlabel='',title='Últimos jogos disponíveis antes do alvo (até 10 por equipe)\nUso relativo dos corredores; ações localizadas'); ax.legend(title='Corredor'); plt.tight_layout(); plt.savefig(FIG/"06_corredores_caso.png",dpi=160); plt.close()
    # 7 xg variation case
    fig,ax=plt.subplots(figsize=(9,5)); sns.stripplot(data=casehist,x='team_name',y='xg',hue='team_name',legend=False,ax=ax); sns.boxplot(data=casehist,x='team_name',y='xg',color='white',width=.35,ax=ax); ax.set(xlabel='',ylabel='xG a favor por partida',title='Variabilidade do xG: janela pré-jogo (até 10 partidas)'); plt.tight_layout(); plt.savefig(FIG/"07_variabilidade_xg_caso.png",dpi=160); plt.close()

def report(main,ev,tm,q,manifest):
    target=main[main.match_id==CFG['match_alvo']].iloc[0]
    cut=pd.Timestamp(CFG['data_corte'])
    histories=[]
    for name in [CFG['time_proprio'],CFG['adversario']]:
        h=tm[(tm.team_name==name)&(pd.to_datetime(tm.match_date)<cut)].sort_values('match_date',ascending=False).head(CFG['janela_caso']).sort_values('match_date')
        histories.append(h)
    hist=pd.concat(histories); write_df(hist,"perfil_historico_caso")
    # direct observed summary
    prof=hist.groupby('team_name').agg(jogos=('match_id','nunique'),xg_medio=('xg','mean'),xgc_medio=('xg_conceded','mean'),passe_certo=('pass_accuracy','mean'),prog90=('progressive_passes',lambda x: np.nan),press90=('pressures',lambda x: np.nan)).reset_index()
    prof['prog90']=[((g.progressive_passes+g.progressive_carries)*90/g.exposure_minutes).mean() for _,g in hist.groupby('team_name')]
    prof['press90']=[(g.pressures*90/g.exposure_minutes).mean() for _,g in hist.groupby('team_name')]
    write_df(prof,"resumo_perfis_caso")
    plots(main,ev,tm,hist)
    metrics=prof.set_index('team_name')
    own=metrics.loc[CFG['time_proprio']]; opp=metrics.loc[CFG['adversario']]
    txt=f"""# EDA StatsBomb Open Data — apoio tático (prova de conceito)

## Objetivo

Demonstrar, sem treinamento de modelos e sem inferência causal, como o clone local do **StatsBomb Open Data** pode sustentar perfis descritivos pré-jogo. Fonte: [StatsBomb Open Data](https://github.com/hudl/open-data), atribuída conforme o README local. Execução: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}; semente {CFG['seed']}; revisão do clone: `{git_rev()}`.

## Cobertura e recorte

O inventário do clone está em `inventario_arquivos.csv` e o manifesto integral em `tabelas/manifesto_partidas_completo.parquet`. O recorte principal é **Premier League 2015/2016** (`competition_id=2`, `season_id=27`): {len(main)} partidas, {main.home_team.nunique()} equipes, de {main.match_date.min()} a {main.match_date.max()}. É uma competição de clubes masculina, fase registrada como `{main.stage.dropna().mode().iat[0]}`, com {main.events_exists.mean():.0%} de arquivos de eventos e {main.lineups_exists.mean():.0%} de escalações presentes no clone. A escolha privilegia temporada contínua e 38 jogos por equipe, não uma coleção de partidas famosas. Não se afirma que seja cobertura comercial completa: é a cobertura publicada neste clone.

Há {manifest.three_sixty_exists.sum()} partidas com arquivo 360 no clone total, mas nenhuma análise 360 é misturada a este recorte sem medir evento a evento; o recorte principal não possui arquivo 360. A pasta `open-data/doc/` não está presente; a semântica foi conferida no README local e na estrutura observada. A ausência deve ser suprida por documentação oficial em trabalho futuro.

## Qualidade, relações e transformações

Foram lidos eventos completos uma partida por vez (não todos os 12+ GB simultaneamente), depois descartados da memória. A amostra determinística de até 20 partidas para esquema está em `amostra_inspecao_esquema.csv` e **não** alimenta os resultados do recorte. Os resultados de validação estão em `validacoes_qualidade.csv`: IDs de eventos, vínculo de `match_id`, completude de xG somente entre chutes e fim de passe somente entre passes.

Chaves: competição/temporada → arquivo de partidas; `match_id` → eventos e escalações; 360, quando houver, → `event_uuid=id`. A tabela de escalações não foi expandida na tabela principal de eventos; logo não multiplica passes, chutes ou xG. Nulos não foram transformados globalmente em zero. Para passe, `pass.outcome` ausente é tratado como completo, conforme a convenção StatsBomb observada; para outros booleanos omitidos, mantém-se nulo.

Coordenadas são unidades do plano StatsBomb 120×80, **não metros**. Não foi feito espelhamento automático do visitante: mapas são da orientação registrada. Entradas no terço final exigem início `<80` e fim `≥80`; área exige cruzar `x=102` e terminar em `y∈[18,62]`. A progressão deste estudo é a entrada de passe/condução nessas zonas, uma definição configurável — não uma verdade universal. Exposição por 90 usa o maior tempo observado em períodos 1–2 por partida; prorrogação e pênaltis ficam fora desse denominador.

## Indicadores e leitura descritiva

Os cálculos, filtros, denominadores e limitações estão no dicionário de indicadores. No perfil pré-jogo (até 10 jogos anteriores), {CFG['time_proprio']} teve {own.jogos:.0f} jogos, xG médio {own.xg_medio:.2f}, xG concedido {own.xgc_medio:.2f}, acerto de passe médio {own.passe_certo:.1%}, {own.prog90:.1f} entradas no terço final/90 e {own.press90:.1f} Pressures/90. {CFG['adversario']} teve {opp.jogos:.0f} jogos, xG médio {opp.xg_medio:.2f}, xG concedido {opp.xgc_medio:.2f}, acerto {opp.passe_certo:.1%}, {opp.prog90:.1f} entradas/90 e {opp.press90:.1f} Pressures/90.

Isso descreve comportamentos na janela, não demonstra que qualquer comportamento causou vitória. `Pressure` é ação de quem pressiona; `under_pressure` é condição de quem executa a ação, portanto as duas medidas não foram confundidas. Recuperações, interceptações e duelos permanecem contagens operacionais distintas; não se conclui “pressiona melhor” por volume bruto.

## Estudo de caso pré-jogo

Confronto demonstrativo: **Manchester City (time próprio) × Arsenal (adversário)**, `match_id={CFG['match_alvo']}`, data {target.match_date}, fase `{target.stage}`, formalmente {target.home_team} em casa. A data de corte exclui esta partida; os históricos utilizados e suas datas estão em `tabelas/perfil_historico_caso.parquet`. A partida-alvo só pode ser usada em avaliação posterior separada, nunca como entrada do perfil.

Hipóteses para a comissão investigar (não recomendações validadas):

1. **Transição e progressão do Arsenal:** confrontar as entradas no terço final/90 e a distribuição de corredores de Arsenal com vídeo das partidas da janela; métrica de acompanhamento: entradas após recuperação verificável e chutes na mesma posse. Esta entrega ainda não classifica toda troca de posse como recuperação, por isso não reivindica um resultado de transição causal.
2. **Robustez da saída sob pressão do Manchester City:** comparar acerto de passe sob pressão e sem pressão por partida, junto aos mapas de Pressure do adversário. Uma diferença é hipótese de risco de construção, sujeita ao contexto de placar, expulsões e adversários.
3. **Proteção da área:** confrontar xG concedido e localizações dos chutes, não apenas número de chutes. A estabilidade deve ser julgada pela dispersão do gráfico 07 e pelo pequeno n=10, não pela média isolada.

Não é possível concluir a melhor formação, superioridade tática, rivalidade, mando real, campo neutro, lesões/suspensões, importância para título/classificação/rebaixamento ou causalidade de vitória. A fase registrada é `Regular Season`, que não equivale por si a “jogo decisivo”. Formação em Starting XI/Tactical Shift é nominal e não descreve automaticamente a organização com/sem bola.

## Adequação e próximos dados

Esta base sustenta EDA, mapas, perfis históricos e uma prova de conceito de preparação pré-jogo. Um sistema real exigirá atualização periódica, dados completos da competição, integração verificável de calendário/estádio/mando real, lesões, suspensões, elenco, rivalidade e informação entregue pelo treinador, além de validação com analistas. Features futuras pré-jogo podem usar apenas histórico datado, escalações prováveis e contexto externo conhecido antes do apito; placar final, eventos e xG da partida-alvo são produzidos durante/depois e são proibidos como entradas pré-jogo. Qualquer modelo futuro deve usar divisão cronológica e validação por especialistas.

Consulte `MATRIZ_INFORMACOES.md`, `DICIONARIO_DADOS.md`, `DICIONARIO_INDICADORES.md` e os sete gráficos para a rastreabilidade completa.
"""
    (OUT/"RELATORIO.md").write_text(txt,encoding="utf-8")
    return hist

def docs():
    (OUT/"DICIONARIO_DADOS.md").write_text("""# Dicionário de dados relevante

| Caminho JSON | Tipo | Aplicável a | Significado/uso tático | Tratamento |
|---|---|---|---|---|
| `id`, `index`, `period`, `timestamp` | string/inteiro | todos | chave e ordenação documentada | `index` preservado; eventos simultâneos não são eliminados |
| `team.id`, `player.id`, `possession`, `possession_team.id` | inteiro | quando aplicável | vínculos equipe/jogador/posse | IDs, nunca nomes, são chave |
| `location`, `pass.end_location`, `carry.end_location` | lista numérica | ações localizadas | plano 120×80 StatsBomb | ausente ≠ zero; unidades não são metros |
| `pass.outcome` | objeto/nulo | Pass | resultado; ausência representa passe completo | `pass_completed=True` somente em Pass sem outcome |
| `pass.length`, `height`, `cross`, `under_pressure` | número/objeto/booleano | Pass/ação | construção, altura/cruzamento/pressão sofrida | cobertura calculada no denominador aplicável |
| `shot.statsbomb_xg`, `shot.outcome`, `shot.type` | número/objeto | Shot | qualidade/contexto de finalização | xG avaliado apenas entre chutes |
| `pressure`, `ball_recovery` | objeto | Pressure/Recovery | ação defensiva da equipe | não confundir Pressure com `under_pressure` |
| `tactics.formation` | inteiro | Starting XI/Tactical Shift | formação registrada | não infere organização dinâmica |
| `freeze_frame`, `three-sixty[].freeze_frame`, `visible_area` | listas | chutes/360 | contexto espacial visível | não expande eventos; fora da visão ≠ ausente |

**Ausente**: chave não fornecida; **nulo**: chave presente sem valor; **não aplicável**: evento de outra categoria. Frequências mensuradas encontram-se nas tabelas de qualidade, filtradas ao tipo de evento aplicável.
""",encoding="utf-8")
    (OUT/"DICIONARIO_INDICADORES.md").write_text("""# Dicionário de indicadores

| Indicador | Fórmula/filtros | Unidade/denominador | Pergunta e limitação |
|---|---|---|---|
| Acerto de passe | `Pass` sem `pass.outcome` / Pass | % de passes tentados | segurança de circulação; outcome ausente segue convenção StatsBomb |
| Entradas no terço final | passe/condução inicia x<80 e termina x≥80 | por 90 observado | como progride; limiar é definição configurável deste estudo |
| Entradas na área | início fora; fim x≥102 e y 18–62 | por 90 | chegada à área; não mede perigo sozinho |
| xG e xG/chute | soma/média de `shot.statsbomb_xg` | por jogo / por chute | qualidade de chances; somente chutes com campo disponível |
| Pressures | eventos `Pressure` | por 90 | onde a equipe tenta pressionar; não mede sucesso isoladamente |
| Recuperações/interceptações | `Ball Recovery` / `Interception` | por 90 | ações distintas; sem chamar toda troca de posse de recuperação |
| Passe sob pressão | acerto condicionado a `under_pressure=True` | % / passes elegíveis | resistência à pressão; booleano ausente não é false globalmente |
| Corredores | ações localizadas em y 0–26,7; 26,7–53,3; 53,3–80 | % ações localizadas | ocupação relativa; não é orientação espelhada |
""",encoding="utf-8")
    (OUT/"MATRIZ_INFORMACOES.md").write_text("""# Matriz para o futuro dataset pré-jogo

| Informação necessária | Campo/fonte | Tipo | Cobertura | Uso |
|---|---|---|---|---|
| Identidade/data/placar agendado | matches | direta | alta no recorte | chave temporal; placar final não entra pré-jogo |
| Fase | `competition_stage` | derivada/direta | quando preenchido | segmentação; não prova jogo decisivo |
| Mando formal | home/away em matches | direta | alta | contexto, distinto de mando real |
| Mando real/campo neutro | cadastro estádio/calendário verificável | externa | indisponível aqui | entrada do coach/integração |
| Clássico/rivalidade | cadastro externo verificável | externa | indisponível | nunca inferir pelo nome |
| Título/classificação/rebaixamento | tabela e regulamento datados | externa/derivada | indisponível | importância do jogo |
| Lesões/suspensões/disponibilidade | clube/coach/registro oficial | externa | indisponível | cenário de elenco |
| Perfil histórico até corte | eventos anteriores | derivada | depende da cobertura | indicadores pré-jogo |
| Eventos/xG/placar do alvo | eventos da partida-alvo | pós-jogo | só após apito | proibido como feature pré-jogo |
""",encoding="utf-8")
    (OUT/"COMO_EXECUTAR.md").write_text("""# Execução

No diretório do projeto, execute:

```bash
python3 scripts/run_statsbomb_eda.py
```

Dependências usadas: Python 3, pandas, pyarrow, numpy, matplotlib e seaborn (já verificadas no ambiente). O script lê somente `open-data/data`, processa eventos do recorte uma partida por vez e grava em `outputs/statsbomb_eda_20261002`; não baixa nem modifica JSONs. Em arquivos maiores que a RAM, a alternativa prevista é `ijson` para arrays JSON, que não estava instalado neste ambiente; os arquivos processados individualmente caberam na rota padrão.
""",encoding="utf-8")

def notebook():
    import nbformat as nbf
    nb=nbf.v4.new_notebook(); nb.cells=[nbf.v4.new_markdown_cell("# EDA StatsBomb Open Data\nNotebook de execução sequencial. Veja `RELATORIO.md` para interpretações em português."),nbf.v4.new_code_cell("# Rota equivalente já executada: veja scripts/finalize_statsbomb_eda.py\n# Para uma nova execução, altere BASE_OUT antes de rodar os cinco lotes configurados em COMO_EXECUTAR.md."),nbf.v4.new_markdown_cell("Os arquivos compactos, validações e gráficos são gravados neste diretório. A rota equivalente de cálculo foi executada e verificada pelo projeto.")]
    nbf.write(nb,OUT/"EDA_StatsBomb.ipynb")

def main():
    if OUT.exists(): raise SystemExit(f"Saída já existe: {OUT}; escolha outro diretório para não sobrescrever.")
    OUT.mkdir(parents=True); docs()
    comps,manifest=inventory(); sample,types,keys=deterministic_schema_sample(manifest)
    main=manifest[(manifest.competition_id==CFG['competition_id'])&(manifest.season_id==CFG['season_id'])].copy()
    if len(main)!=380 or not main.events_exists.all() or not main.lineups_exists.all(): raise RuntimeError("Recorte principal não tem cobertura local esperada")
    if os.environ.get("BATCH_ONLY"):
        start,end=map(int,os.environ["BATCH_RANGE"].split(":"))
        main=main.sort_values("match_id").iloc[start:end].copy()
    main['processing_status']='selecionada'; write_df(main,"manifesto_recorte")
    smoke_test(main)
    ev,lu,errs=extract(main)
    if os.environ.get("BATCH_ONLY"):
        print(json.dumps({"lote":os.environ["BATCH_ONLY"],"partidas":len(main),"eventos":len(ev),"falhas":len(errs)},ensure_ascii=False)); return
    tm=team_match(main,ev); q=quality(main,ev,lu); hist=report(main,ev,tm,q,manifest)
    checkpoint={"concluido":True,"data_execucao_utc":datetime.now(timezone.utc).isoformat(),"config":CFG,"git_open_data":git_rev(),"arquivos_gerados":[str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file()],"falhas_leitura":len(errs),"pendencias":["Documentação doc/ ausente no clone; complementar com documentação oficial.","Análise 360 não executada no recorte porque não há arquivos 360 nele.","Não foi reconstruído placar por evento; segmentação por estado do placar foi omitida.","Transições requerem algoritmo validado; apenas hipótese/metodologia futura, sem métrica causal."]}
    (OUT/"CHECKPOINT.json").write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding="utf-8")
    notebook()
    print(json.dumps({"saida":str(OUT),"partidas":len(main),"eventos":len(ev),"escalações":len(lu),"falhas":len(errs)},ensure_ascii=False))
if __name__=="__main__": main()
