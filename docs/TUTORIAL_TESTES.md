# Tutorial: executar e testar o MVP

> Tutorial original da CLI. A V2 preserva esses comandos e o JSON; o Markdown agora
> tem apresentação amigável com apêndice técnico. Para interface, dependência opcional
> e testes adicionais, consulte [TUTORIAL_V2.md](TUTORIAL_V2.md).

Execute os comandos no diretório raiz do ManagerAI. Nenhum passo exige acesso à
internet, chave de API, GPU ou instalação de dependências. Os exemplos usam apenas
os dados locais. Não é necessário criar commits.

## 1. Conferir o ambiente

```bash
python3 --version
PYTHONPATH=src python3 -B -m managerai --help
```

Requer Python 3.12 ou superior. Se preferir o ambiente virtual existente, substitua
`python3` por `venv/bin/python`. Não é necessário ativá-lo. `PYTHONPATH=src` torna
o pacote importável sem instalação; `-B` evita gerar arquivos de bytecode.

O MVP não depende do `requirements.txt` da EDA. Também não precisa executar os
scripts originais da EDA, que têm diretórios fixos e proteções contra sobrescrita.

## 2. Rodar os testes rápidos

```bash
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Resultado esperado: testes sintéticos aprovados e um teste de integração local
marcado como `skipped`. As fixtures são criadas em diretórios temporários e
removidas ao terminar; nunca alteram os JSONs StatsBomb.

São cobertos:

- IDs, contexto, datas e janelas inválidos;
- seleção de histórico, primeira partida, pouca amostra e exclusão do mesmo dia;
- exclusão de eventos/escalações do alvo e futuro, inclusive arquivos corrompidos
  propositalmente nas fixtures para demonstrar que não são lidos;
- xG favorável/contra, xG ausente, passe incompleto, entrada lateral na área,
  contrapressão, desarmes, coordenadas e durações inválidas;
- exposição dos dois tempos e exclusão de prorrogação;
- proporções agregadas por tentativas e taxas por exposição;
- fontes, repetibilidade, hipóteses fundamentadas, indisponibilidade manual e
  recusa de sobrescrita/gravação na raiz bruta.

## 3. Rodar a integração com os dados reais

```bash
MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Esse comando também confere a cobertura da Premier League 2015/16, executa duas
vezes o relatório City × Arsenal, compara os JSONs e recalcula o xG diretamente
nos arquivos brutos para conferir atribuição e agregação. Não grava relatórios.

O teste espera o recorte local de 380 jogos e 20 clubes descrito na spec. Se os dados
forem substituídos por outro snapshot, revise a cobertura esperada conscientemente.

## 4. Consultar catálogo, equipes e partidas

```bash
PYTHONPATH=src python3 -B -m managerai catalog > /tmp/managerai_catalog.json
PYTHONPATH=src python3 -B -m managerai teams --competition-id 2 --season-id 27
PYTHONPATH=src python3 -B -m managerai matches --competition-id 2 --season-id 27 > /tmp/managerai_matches.json
```

No recorte inicial, Manchester City tem ID **36** e Arsenal tem ID **1**. O alvo
da demo é **3754314**, em **2016-05-08**. `matches` lista calendário, IDs e cobertura,
sem exibir resultados da partida como preparação pré-jogo.

O catálogo inclui cobertura de todas as temporadas locais e IDs de arquivos sem
vínculo no catálogo. Esses arquivos não são incorporados às seleções. A presença de
arquivos de outras temporadas não equivale a validação integral do seu conteúdo.

Para dados em outro local, o argumento global deve vir **antes do subcomando**:

```bash
PYTHONPATH=src python3 -B -m managerai --data-root open-data/data teams --competition-id 2 --season-id 27
```

## 5. Auditar as 380 partidas

```bash
PYTHONPATH=src python3 -B -m managerai audit --competition-id 2 --season-id 27 > /tmp/managerai_quality.json
python3 -m json.tool /tmp/managerai_quality.json
```

A auditoria lê uma partida por vez e verifica duplicações, referências de equipes,
escalações e campos usados nas features. O conjunto de IDs é mantido em memória
para detectar duplicações entre partidas. Pode levar mais tempo que os testes rápidos.

No snapshot validado nesta entrega, o resultado foi:

- `matches_catalogued`: 380;
- `matches_checked`: 380;
- `events_read`: 1.313.773;
- `missing_event_match_ids`: vazio;
- `locations_missing`: 8.077;
- `locations_invalid`: 3;
- `durations_invalid`: 2;
- `status`: `com_lacunas`.

`com_lacunas` indica ocorrências reportadas, incluindo localizações ausentes que
podem ser esperadas em eventos não espaciais. O comando termina com código 0 quando
a auditoria conclui; código 2 indica erro estrutural/entrada inválida e mensagem em
stderr. Não interprete código 0 como certificação de perfeição dos dados.

## 6. Gerar o relatório pré-jogo

Escolha um diretório de saída **que ainda não exista**:

```bash
PYTHONPATH=src python3 -B -m managerai analyze \
  --competition-id 2 \
  --season-id 27 \
  --team-id 36 \
  --opponent-id 1 \
  --target-match-id 3754314 \
  --window 10 \
  --output-dir outputs/tutorial_city_arsenal_01
```

O comando imprime os caminhos dos dois arquivos:

- `report.md`: apresentação em português para leitura;
- `report.json`: contrato completo, métricas por jogo, mediana/DP, regras e hashes.

Resultado esperado no snapshot atual: **10 jogos por equipe, quatro achados e duas
hipóteses**, R01_PROGRESSAO e R03_CHANCES. O adversário não satisfaz o gatilho de
30% da regra R02; o motor não cria uma terceira hipótese para completar a quantidade.

Uma demonstração já gerada está em `outputs/mvp_demo_city_arsenal/`. Para executar
novamente, use outro nome de diretório; não é necessário apagar resultados anteriores.

## 7. Inspecionar o JSON e a temporalidade

```bash
python3 - <<'PY'
import json
from pathlib import Path

r = json.loads(Path('outputs/tutorial_city_arsenal_01/report.json').read_text())
assert r['metadata']['matches_analyzed_team'] == 10
assert r['metadata']['matches_analyzed_opponent'] == 10
for key in ('team_profile', 'opponent_profile'):
    p = r[key]
    assert 3754314 not in p['match_ids']
    assert p['period_end'] < '2016-05-08'
    print(p['team_name'], p['period_start'], p['period_end'])
    for metric in ('xg_for', 'xg_against', 'final_third_entries'):
        m = p['metrics'][metric]
        print(metric, m['value'], m['unit'], 'n=', m['sample_size'])
assert r['formation_options'] == []
assert r['lineup_options'] == []
assert all(s['path'] not in ('events/3754314.json', 'lineups/3754314.json')
           for s in r['methodology']['sources'])
print('Hipóteses:', [h['rule_id'] for h in r['tactical_hypotheses']])
print('Fingerprint:', r['metadata']['data_fingerprint'])
PY
```

Para verificar uma evidência de hipótese, siga o caminho informado em
`evidence_metrics`, por exemplo `opponent_profile.metrics.final_third_entries`.
O objeto contém IDs, datas e valores das partidas elegíveis, unidade e fórmula.
Não há placar final ou escalação do alvo nas features.

## 8. Corte por data livre e contexto manual

```bash
PYTHONPATH=src python3 -B -m managerai analyze \
  --competition-id 2 --season-id 27 \
  --team-id 36 --opponent-id 1 \
  --cutoff-date 2016-05-08 \
  --venue casa \
  --match-context regular \
  --strategic-objective 'proteger vantagem' \
  --notes 'Cenário informado pelo treinador para ensaio em treino.' \
  --output-dir outputs/tutorial_data_livre_01
```

Data livre e jogo-alvo são alternativas exclusivas. Em ambos os modos, todo o dia
do corte fica fora do histórico. Contexto e notas são declarações, não verificações
automáticas ou evidências de eficácia. Não precisam alterar os indicadores nem as
regras. O mando formal registrado no alvo é separado do mando manual.

Para informar indisponibilidade, use `--unavailable-player-id ID`, repetindo o
argumento para cada atleta. Obtenha um ID real nas escalações **anteriores da própria
equipe na janela**; atletas observados somente no alvo/futuro ou na adversária são
rejeitados. Não é gerada escalação alternativa neste baseline.

## 9. Testar ausência de histórico e amostra pequena

```bash
PYTHONPATH=src python3 -B -m managerai analyze \
  --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 \
  --cutoff-date 2015-08-08 \
  --output-dir outputs/tutorial_sem_historico_01
```

Resultado: zero partidas anteriores, métricas indisponíveis em vez de zeros
fabricados, lacunas e nenhuma hipótese.

```bash
PYTHONPATH=src python3 -B -m managerai analyze \
  --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 \
  --target-match-id 3754314 --window 2 \
  --output-dir outputs/tutorial_amostra_pequena_01
```

Resultado: duas partidas por equipe, indicadores descritivos, amostra insuficiente
e nenhuma hipótese. O mínimo de cinco jogos é uma escolha operacional documentada.

## 10. Verificar reprodução e erros esperados

Execute novamente o cenário principal em uma saída diferente:

```bash
PYTHONPATH=src python3 -B -m managerai analyze \
  --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 \
  --target-match-id 3754314 --window 10 \
  --output-dir outputs/tutorial_city_arsenal_02
cmp outputs/tutorial_city_arsenal_01/report.json outputs/tutorial_city_arsenal_02/report.json
```

`cmp` deve terminar com código 0 e sem saída. Mesmas entradas e mesmos bytes de
fontes geram o mesmo relatório; o diretório de saída não entra no contrato.

Este comando deve falhar, pois a equipe não pode enfrentar a si mesma:

```bash
PYTHONPATH=src python3 -B -m managerai analyze \
  --competition-id 2 --season-id 27 --team-id 36 --opponent-id 36 \
  --cutoff-date 2016-05-08 --output-dir outputs/tutorial_entrada_invalida
```

Resultado esperado: `Erro:` e código 2; nenhum diretório de relatório criado.
Também são erros: competição/equipe inexistente, alvo de outro confronto, data
inválida, janela zero, dois modos de corte, saída já existente ou dentro dos dados.

## 11. O que esta entrega não valida

Não há promessa de vitória, formação ideal, disponibilidade atual, treinamento,
API de LLM, dados ao vivo ou inferência causal. Formações e escalações retornam
explicitamente não suportadas. Os relatórios precisam de leitura crítica pela
comissão técnica. Consulte [métricas](metrics.md), [regras](tactical_rules.md) e
[avaliação](evaluation.md) para as diferenças em relação à EDA e os limites.

## Diagnóstico rápido

| Sintoma | Ação |
|---|---|
| `No module named managerai` | Execute da raiz com `PYTHONPATH=src` |
| `competitions.json` não encontrado | Confira a raiz e use `--data-root` antes do subcomando |
| Saída já existe | Escolha outro sufixo de diretório; não é necessário apagar arquivos |
| Métrica null | Confira denominador e sample_size; ausência não equivale a zero |
| Menos de duas hipóteses | Confira amostra e gatilhos; o sistema se abstém quando não há suporte |
| Valores diferem da EDA | Leia as correções de entradas, exposição e agregação em metrics.md |
| Integração skipped | Defina `MANAGERAI_RUN_LOCAL_TESTS=1` para habilitá-la |
| Auditoria com lacunas | Leia os contadores; dados ausentes são explícitos, sem reparo silencioso dos JSONs |
