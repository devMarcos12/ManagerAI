#!/usr/bin/env python3
"""Gera um .docx autocontido a partir dos resultados já calculados da EDA."""
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED
import pandas as pd
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'/'statsbomb_eda_20261002_exec6'
DEST=OUT/'Apresentacao_EDA_StatsBomb.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'

def run(text,bold=False,size=None):
    prop=(f'<w:b/>' if bold else '')+(f'<w:sz w:val="{size}"/>' if size else '')
    return f'<w:r><w:rPr>{prop}</w:rPr><w:t xml:space="preserve">{escape(str(text))}</w:t></w:r>'
def para(text='',style=None,bold=False,size=None):
    ps=f'<w:pStyle w:val="{style}"/>' if style else ''
    return f'<w:p><w:pPr>{ps}</w:pPr>{run(text,bold,size)}</w:p>'
def pagebreak(): return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
def table(headers,rows):
    def cell(v,head=False): return f'<w:tc><w:tcPr><w:shd w:fill="D9EAF7"/></w:tcPr><w:p>{run(v,head)}</w:p></w:tc>'
    data='<w:tr>'+''.join(cell(x,True) for x in headers)+'</w:tr>'
    for row in rows: data+='<w:tr>'+''.join(cell(x) for x in row)+'</w:tr>'
    return '<w:tbl><w:tblPr><w:tblBorders><w:top w:val="single"/><w:left w:val="single"/><w:bottom w:val="single"/><w:right w:val="single"/><w:insideH w:val="single"/><w:insideV w:val="single"/></w:tblBorders></w:tblPr>'+data+'</w:tbl>'
def image_paragraph(rid,num,path):
    with Image.open(path) as im:
        width,height=im.size
    maxw=5_800_000; w=min(width*9525,maxw); h=int(height*9525*(w/(width*9525)))
    return f'''<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{w}" cy="{h}"/><wp:docPr id="{num}" name="Figura {num}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="{num}" name="{escape(path.name)}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}" xmlns:r="{R}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''

def main():
    if not OUT.exists(): raise SystemExit('Saída da EDA não encontrada.')
    perfil=pd.read_parquet(OUT/'tabelas'/'resumo_perfis_caso.parquet').sort_values('team_name')
    quality=pd.read_csv(OUT/'validacoes_qualidade.csv')
    inv=pd.read_csv(OUT/'inventario_arquivos.csv')
    body=[]
    body += [para('ManagerAI', 'Title', True, 40),para('Análise Exploratória de Dados Táticos — StatsBomb Open Data','Subtitle',True,28),para('Documento para apresentação acadêmica',None,False,22),para('Recorte principal: Premier League 2015/2016 | Estudo de caso: Manchester City × Arsenal | Execução: 02/10/2026',None,False,18),pagebreak()]
    body += [para('Resumo executivo','Heading1',True),para('Esta entrega demonstra uma prova de conceito de apoio pré-jogo. Os dados locais da StatsBomb foram inventariados, validados e agregados sem treinamento de modelos e sem afirmar causalidade entre tática e vitória.'),para('A análise principal cobre 380 partidas da Premier League 2015/16, uma temporada contínua de clubes masculinos, com arquivos locais de eventos e escalações presentes em todas as partidas do recorte.')]
    body += [para('Objetivo e limites','Heading1',True),para('Objetivo: transformar eventos históricos em perfis descritivos de equipes, mapas e perguntas táticas para investigação da comissão técnica. Limite central: padrões observados não demonstram que uma tática causa vitória. Contextos como rivalidade, mando real, lesões, suspensões e importância competitiva exigem fontes externas verificáveis ou entrada do treinador.')]
    body += [para('Fonte, estrutura e cobertura','Heading1',True),para('Fonte: StatsBomb Open Data (https://github.com/hudl/open-data). Foram preservados os JSONs originais. A estrutura relaciona competição/temporada às partidas; match_id a eventos e escalações; e, quando houver, frames 360 ao id do evento. A pasta doc/ não estava presente no clone local.')]
    body += [table(['Categoria','Arquivos','Tamanho (bytes)'],[[r.categoria,f'{r.arquivos:,}',f'{r.bytes:,}'] for r in inv.itertuples(index=False)])]
    body += [para('Qualidade e validações','Heading1',True),para('Eventos foram processados partida a partida e gravados em Parquet. Nulos não foram preenchidos globalmente com zero. Para passes, outcome ausente foi interpretado como passe completo; xG foi avaliado somente entre finalizações.')]
    body += [table(['Verificação','Resultado','Valor'],[[r.verificacao,'OK' if r.resultado else 'Revisar',r.valor] for r in quality.itertuples(index=False)])]
    body += [para('Indicadores e estudo de caso','Heading1',True),para('Partida-alvo: Manchester City × Arsenal, 08/05/2016, match_id 3754314, fase Regular Season. Perfis calculados exclusivamente com até dez jogos anteriores à data de corte; a partida-alvo não entra como evidência pré-jogo.')]
    body += [table(['Equipe','Jogos','xG médio','xG contra','Acerto passe','Entradas terço final/90','Pressures/90'],[[r.team_name,str(r.jogos),f'{r.xg_medio:.2f}',f'{r.xgc_medio:.2f}',f'{r.passe_certo:.1%}',f'{r.prog90:.1f}',f'{r.press90:.1f}'] for r in perfil.itertuples(index=False)])]
    body += [para('Leituras para a comissão técnica','Heading1',True),para('1. Investigar em vídeo como o Arsenal transforma progressão em finalizações, sobretudo após recuperações verificáveis. 2. Comparar o acerto de passe do Manchester City sob pressão e sem pressão para avaliar riscos na saída. 3. Usar xG concedido e localização de chutes, e não somente volume de chutes, para discutir proteção de área. Estas são hipóteses operacionais, não recomendações comprovadas.')]
    body += [para('Gráficos e interpretações','Heading1',True)]
    captions=[
      'Cobertura por equipe: confirma histórico uniforme de 38 partidas por clube no recorte.',
      'Tipos de evento: descreve a composição dos registros usados; não mede desempenho por si só.',
      'Mapa de finalizações: xG por chute permite examinar qualidade e localização das oportunidades.',
      'Mapa de Pressure: mostra onde a equipe tentou pressionar; Pressure não é igual a sucesso da pressão.',
      'Progressão por 90: compara entrada no terço final, com variabilidade entre partidas.',
      'Corredores no caso: distribuição relativa de ações localizadas nas janelas pré-jogo.',
      'Variabilidade do xG: evita interpretar médias de apenas dez partidas como resultado estável.' ]
    figs=sorted((OUT/'graficos').glob('*.png'))
    for i,(fig,cap) in enumerate(zip(figs,captions),1):
        body += [image_paragraph(f'rId{i}',i,fig),para(f'Figura {i} — {cap} Fonte: StatsBomb Open Data; Premier League 2015/16.',None,False,18)]
    body += [para('Limitações e próximos passos','Heading1',True),para('Não foi feita análise 360 porque o recorte principal não tem arquivos 360. Não se reconstruiu o placar por evento e não se classificou toda mudança de posse como recuperação. Um sistema real exigirá atualização cronológica, cobertura mais ampla, dados de elenco e contexto pré-jogo, validação com especialistas e avaliação temporal futura.')]
    body += [para('Referências e rastreabilidade','Heading1',True),para('StatsBomb Open Data. https://github.com/hudl/open-data. Consulte também o relatório técnico, o dicionário de dados, o dicionário de indicadores e a matriz de informações no diretório de saída da EDA.')]
    sect='<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>'
    doc=f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>{"".join(body)}{sect}</w:body></w:document>'
    rels=''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{p.name}"/>' for i,p in enumerate(figs,1))
    styles=f'''<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="{W}"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/></w:style><w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/></w:style></w:styles>'''
    content='''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'''
    with ZipFile(DEST,'w',ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',content); z.writestr('_rels/.rels','''<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>''')
        z.writestr('word/document.xml',doc); z.writestr('word/styles.xml',styles); z.writestr('word/_rels/document.xml.rels',f'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
        for p in figs: z.write(p,'word/media/'+p.name)
    print(DEST)
if __name__=='__main__': main()
