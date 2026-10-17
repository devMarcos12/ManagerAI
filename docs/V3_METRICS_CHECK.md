# Conferência independente das métricas V3

Executada em 11/10/2026, com dados locais, sem alterar JSONs originais.
O [script reproduzível](../outputs/v22_v3_validation/check_metrics.py) recalcula
oito indicadores diretamente dos arrays originais, sem chamar helpers V3 de
geometria, contadores ou exposição. Depois compara com `analyze_match_v3`, com
tolerância absoluta de 1e-12 para arredondamento de ponto flutuante.
O [resultado completo](../outputs/v22_v3_validation/independent_metrics.json)
contém numeradores, denominadores, multiplicadores, valores e SHA-256 dos
calendários/eventos. **16 comparações passaram em duas partidas.** Isso não
certifica todas as métricas nem todas as partidas do dataset.

## Casos observados

Manchester City: última partida anterior a 08/05/2016 no calendário da PL 2015/16
é **3754320, em 01/05/2016**. Real Madrid: partida anterior **3773585, em
24/10/2020**, para o corte 10/04/2021 em La Liga 2020/21. Não são dados dos alvos.
Os dois jogos têm localização válida nos eventos relevantes e xG válido em todos
os chutes do próprio time; o script exige isso explicitamente, em vez de preencher
lacunas. Os valores abaixo são apenas dessas partidas, não das janelas de dez.

| Indicador bruto | City, 01/05/2016 | Real Madrid, 24/10/2020 |
|---|---:|---:|
| Exposição observada em minutos | 96,0611 | 97,0999 |
| Passes completos progressivos | 100 | 108 |
| Entradas no terço de ataque por passe completo | 41 | 34 |
| Entradas no terço de ataque por condução | 19 | 20 |
| Chutes dentro da área / chutes localizados | 4/6 | 14/16 |
| Soma de xG dentro da área | 0,664152418 | 2,838038508 |
| Soma de xG / chutes localizados | 0,755861508/6 | 2,900067952/16 |
| Tentativas de pressão no terço de ataque / localizadas | 30/188 | 40/198 |

## Fórmulas conferidas

- Progressivo: distância euclidiana à meta registrada `(120,40)` no início menos
  distância no fim **≥10 unidades**; somente passes completos. Não são metros,
  eficácia nem valor tático comprovado.
- Entrada no terço: início `x<80`, fim `x>=80`, separando passe completo e condução.
- Área: chute em `x>=102` e `18<=y<=62`; proporção = `100 × chutes na área / chutes
  localizados`. xG da zona é a soma dos valores válidos, agregada por jogo.
- Qualidade média dos chutes localizados = `soma de xG / quantidade de chutes`.
  **xG estima a qualidade das finalizações, não o número de chances nem a chance
  de vitória.**
- Pressão alta registrada: `Pressure` com localização `x>=80`; proporção =
  `100 × pressões nessa zona / pressões localizadas`. Não mede sucesso de pressão.
- Taxas por 90 = `90 × contagem / minutos de exposição observada`. A exposição é
  a soma do maior `timestamp + duration` de cada período 1/2, em minutos, incluindo
  acréscimos; não mede tempo de bola em jogo.

O catálogo contém **26 métricas** nas três famílias: progressão, finalização/xG e
pressão/recuperações registradas. A conferência acima cobre oito delas, incluindo
ao menos uma medida de cada família. Testes sintéticos cobrem adicionalmente
limites geométricos, equipes, períodos, lacunas, denominadores, agregação e ausência
de desvio-padrão com uma partida.

## Reprodução

Na raiz do repositório:

```bash
PYTHONPATH=src python3 -B outputs/v22_v3_validation/check_metrics.py
MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p test_v3_features.py -v
MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -p test_v3_rules.py -v
```

O script imprime JSON no terminal, sem escrever arquivos. Para salvar outra
execução, use um destino novo; não sobrescreva o artefato preservado.
Fonte: StatsBomb Open Data, snapshot local.
