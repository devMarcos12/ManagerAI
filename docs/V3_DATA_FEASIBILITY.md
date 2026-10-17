# Viabilidade dos dados para a V3

Auditoria realizada em 11/10/2026, exclusivamente nos JSONs locais de
`open-data/data`. Não houve consulta externa, modificação dos dados brutos ou
treinamento. Esta auditoria descreve o snapshot completo; não é um relatório
pré-jogo. As análises do produto devem continuar lendo somente o histórico anterior
ao corte, sem eventos ou escalações do alvo/futuro.

## Escopo e reprodução

O [artefato da auditoria](../outputs/v3_feasibility/audit.json) contém cobertura
**por cada um dos 80 pares competição/temporada**, contagens por campo/tipo,
contagens por partida, chutes por equipe/período e SHA-256 dos arquivos de eventos
lidos integralmente. O [script](../outputs/v3_feasibility/reproduce_audit.py) usa
apenas a biblioteca padrão Python. Para repetir sem sobrescrever o artefato:

```bash
python3 outputs/v3_feasibility/reproduce_audit.py > /tmp/managerai_auditoria_nova.json
```

Escolha um caminho novo se esse arquivo temporário já existir. A execução lê uma
partida de cada vez. Foram inspecionados integralmente os eventos e escalações das
380 partidas da Premier League 2015/16 e das 35 partidas de La Liga 2020/21.
Nas demais temporadas, a auditoria verificou catálogo e existência dos arquivos,
**não completude nem semântica dos campos de eventos**. Não generalizar cobertura
de campos desses dois recortes para outras temporadas.

Catálogo: 3.961 partidas, todas com arquivos de eventos e escalações, e 426 com
arquivo 360. Há 4.235 arquivos de eventos/escalações no inventário anterior: os
274 IDs sem vínculo no catálogo continuam fora da seleção. Presença de arquivo
não certifica qualidade. PL 2015/16 tem 380/380 eventos e escalações e **zero 360**;
La Liga 2020/21 tem 35/35 eventos e escalações e **35 arquivos 360**.
O conteúdo desses arquivos 360 não foi consumido nem validado: a V3 não depende
deles e sua presença não equivale a tracking contínuo ou cobertura de toda ação.

## Cobertura parcial Real Madrid × Barcelona

- Competição **11**, temporada **90** (2020/2021).
- Real Madrid **220**, Barcelona **217**.
- Alvo **3773497**, em **10/04/2021**.
- Real Madrid possui apenas **dois jogos no calendário local dessa temporada**:
  o alvo e **3773585, em 24/10/2020**. Logo, há **um jogo anterior elegível**.
- Barcelona possui 35 jogos catalogados, dos quais 27 anteriores ao corte. A
  janela de até dez seleciona 31/01/2021–05/04/2021, todos com eventos.
- Os dez IDs do Barcelona são: 3773403, 3773631, 3773526, 3773415, 3764440,
  3773625, 3773665, 3773369, 3773597 e 3773474.

O desequilíbrio 1×10 é legítimo neste snapshot; não deve ser corrigido completando
o histórico com jogos futuros, alvo ou outra temporada. Os valores válidos podem
ser apresentados descritivamente, acompanhados de amostra e período. Comparações
de superioridade e hipóteses automáticas devem se abster.

Oportunidades no catálogo, **sem junção implementada ou autorizada**:

| Temporada La Liga | Real Madrid | Barcelona |
|---|---:|---:|
| 2019/2020 | 2 | 33 |
| 2018/2019 | 1 | 34 |
| 2017/2018 | 2 | 36 |
| 2016/2017 | 2 | 34 |
| 2015/2016 | 38 | 38 |
| 2014/2015 | 2 | 38 |

São contagens do catálogo completo de cada temporada. La Liga 2015/16, temporada
27, tem 380 partidas e oferece um cenário futuro mais equilibrado. Seus eventos
não foram auditados nesta frente. Integrar temporadas exige regra de mudança de
elenco/comissão, envelhecimento da evidência, completude e seleção temporal;
simplesmente somar partidas antigas não resolve representatividade de 2021.

## Campos efetivamente observados

Contagens incluem todas as equipes dos jogos e todos os períodos. Para métricas
regulamentares, o pipeline mantém somente períodos 1 e 2.

| Medida/campo | PL 2015/16: 380 partidas | La Liga 2020/21: 35 partidas |
|---|---:|---:|
| Eventos | 1.313.773 | 139.030 |
| `possession`, `possession_team`, `timestamp` presentes | 1.313.773 cada | 139.030 cada |
| `duration` presente | 973.459 | 99.833 |
| Durações inválidas | 2 | 0 |
| Localizações iniciais presentes | 1.305.696 | 138.145 |
| Localizações iniciais fora do domínio | 3 | 0 |
| Passes | 368.619 | 40.337 |
| Passes com payload e fim válido | 368.619 | 40.337 |
| Passes com início válido | 368.617 | 40.337 |
| Passes sem resultado marcado (convenção de completo) | 282.379 | 34.643 |
| Conduções com payload, início e fim válidos | 276.949 | 32.900 |
| Chutes | 9.908 | 839 |
| Chutes com xG válido | 9.908 | 839 |
| Chutes com localização inicial válida | 9.907 | 839 |
| Tentativas de pressão registradas | 115.402 | 10.832 |
| Pressões com localização válida | 115.402 | 10.832 |
| Pressões com `counterpress=True` | 24.224 | 2.056 |
| Recuperações registradas | 40.943 | 2.822 |
| Recuperações com `recovery_failure=True` | 3.249 | 181 |
| Eventos com jogador | 1.309.036 | 138.548 |
| Jogador do evento ausente da escalação da sua equipe | 0 | 0 |
| Starting XI com formação e lista de jogadores | 760/760 | 70/70 |
| Tactical Shift com formação e lista de jogadores | 625/625 | 79/79 |
| Registros jogador/equipe/partida nas escalações | 13.678 | 1.542 |
| Desses registros com posições não vazias | 10.469 | 1.070 |

Não foram encontrados IDs de eventos duplicados **dentro das partidas**, equipes
de evento inválidas ou equipes de posse estranhas ao confronto. A associação de
jogadores usou `event.team.id` + `event.player.id` contra a escalação daquela
equipe naquela partida; não usou elenco futuro. A auditoria não testou duplicação
global entre todas as temporadas; o pipeline possui verificação entre jogos lidos.

Ausência de `duration` é comum e não indica, por si só, partida truncada. A exposição
do baseline soma o maior `timestamp + duration` de cada tempo, com duração ausente
zero e duração inválida ignorada na extensão do relógio. Isso **não mede bola em
jogo**. Posições ausentes nas escalações incluem registros sem participação;
presença no arquivo não significa minutos jogados nem disponibilidade futura.

## Orientação espacial: o que foi verificado

Plano registrado 120×80. Valores inválidos são excluídos dos indicadores espaciais,
sem recorte artificial para a borda. Os finais de chute podem ter terceiro valor
(altura), que não integra o plano do campo.

| Recorte/período | Chutes com início válido | Início x≥80 | Média x inicial | Fim x=120 | Fim x=0 |
|---|---:|---:|---:|---:|---:|
| PL, primeiro tempo | 4.483 | 4.470 | 103,45 | 2.004 | 0 |
| PL, segundo tempo | 5.424 | 5.404 | 103,77 | 2.332 | 0 |
| La Liga, primeiro tempo | 357 | 353 | 104,74 | 161 | 0 |
| La Liga, segundo tempo | 482 | 481 | 104,78 | 218 | 0 |

O artefato também conserva essa checagem por equipe. O padrão interno em ambos os
períodos sustenta usar x crescente em direção à meta x=120 para a equipe da ação
nesses recortes; não há evidência para espelhar automaticamente visitante ou
segundo tempo. A concentração de chutes não substitui a documentação semântica
integral da StatsBomb, ausente em `open-data/doc` no snapshot.

**Não foi certificado o significado tático de esquerda/direita no eixo y.** Usar
“faixa de y baixo”, “faixa central” e “faixa de y alto”, acompanhadas de legenda do
mapa. Pressão e posse de equipes opostas podem ter referências espaciais distintas;
não calcular distância pressão→recuperação entre equipes sem transformação
explicitamente validada. Não inferir ocupação contínua, shape defensivo,
posicionamento sem bola ou tracking por eventos isolados.

## Posses, recuperações e sequências

Agrupamentos `(match_id, period, possession)` somam 72.264 blocos na PL e 6.143 na
La Liga; nenhum bloco contém mais de um `possession_team.id`. Há uma diminuição de
ID de posse no fluxo PL e nenhuma na La Liga, motivo adicional para não presumir
que o número sozinho define uma sequência contínua nem ordenar por ele.
O caso foi localizado em **3754136**: `Referee Ball-Drop`, índice 1181,
primeiro tempo 32:09.994, posse 74/Newcastle; seguido de `Ball Receipt*`, índice
1182, 32:12.320, posse 73/Aston Villa. A ordem dos eventos é válida, mas o ID de
posse retrocede; agrupar globalmente por número poderia ligar blocos separados.

Na PL, **17.893 pressões** têm `team.id == possession_team.id`; na La Liga, **1.257**.
Isso impede interpretar automaticamente uma pressão como evento de posse rival
ou todo evento do bloco como ação ofensiva do titular da posse. `Ball Recovery`
também inclui falhas explícitas. Não converter toda troca de `possession_team` em
recuperação, nem toda recuperação anotada em posse consolidada.

Uma sequência operacional futura deve ordenar por `index`, separar períodos e
blocos contíguos, exigir o mesmo time nas ações ofensivas, tratar timestamps
simultâneos/ações sobrepostas e interromper em bolas paradas/fim de período quando
apropriado. Passes completos, conduções, entradas e chutes podem ser associados a
um bloco observado, sem dizer que uma ação causou a seguinte. Para tempo entre
recuperação e chute, excluir recuperações com falha, exigir posse subsequente
atribuível ao mesmo time e definir janela máxima e política de interrupções.

Relacionar pressão a recuperação por proximidade temporal é **parcialmente viável
como associação operacional**, não sucesso demonstrado ou causalidade. A primeira
entrega deve preferir pressão espacial, com recuperação apresentada separadamente,
até essas regras serem implementadas e verificadas.

## Priorização recomendada

| Família | Viabilidade | Definição inicial e limites |
|---|---|---|
| Progressão segmentada | Viável | Separar entradas por passe completo e condução, por terço/área/faixa registrada. Progressivo pode significar redução explícita da distância à meta ou avanço mínimo documentado; não dizer que avançar equivale a jogar melhor |
| Localização e qualidade das finalizações | Viável | Contagem, proporção e soma/média de xG por zonas disjuntas, com denominador de chutes localizados e cobertura de xG. Localização inválida reduz amostra espacial, sem alterar xG coletivo V2 |
| Pressão espacial | Viável | Contagem, proporção por zonas e por 90 com exposição registrada. Nomear tentativas de pressão; não estimar sucesso ou eficácia |
| Sequências ofensivas por posse | Parcial | Campos íntegros permitem blocos observados após validação de continuidade/equipe/período. IDs de posse não autorizam atribuir toda ação ao titular nem medir posse percentual pelo número de eventos |
| Recuperação após pressão/transição | Parcial, adiar causalidade | Possível associação temporal com regras e exclusões; sem evidência suficiente para chamar de pressão bem-sucedida ou contra-ataque efetivo |
| Participação histórica de jogadores | Viável como exploração | Contar ações atribuídas a jogador/equipe/partida nos jogos anteriores, com IDs e amostras. Não ranquear capacidade ou sugerir onze inicial |
| Formações históricas | Viável como registro; interpretação parcial | Starting XI/Tactical Shift permitem frequência de formações registradas, sem presumir que se mantiveram por 90 minutos ou expressam shape contínuo |
| Escalação ideal, disponibilidade no alvo, eficácia causal | Não viável | Não há rótulos, fonte de disponibilidade, tracking integral ou desenho causal |

As três primeiras famílias têm cobertura suficiente para serem priorizadas,
sem depender de sequências frágeis. Qualquer hipótese exige o mínimo operacional
documentado de cinco partidas elegíveis **em cada métrica citada e para ambas as
equipes**. Valores nulos e denominadores zero devem permanecer indisponíveis;
uma temporada coberta não elimina a exigência de verificar cada janela.

## Conclusão operacional

Os dados locais sustentam três famílias descritivas robustas para City × Arsenal
(PL 2015/16). La Liga 2020/21 suporta os cálculos, mas a janela Real Madrid ×
Barcelona permanece insuficiente para hipóteses. A auditoria autoriza desenvolver
analítica verificável, não afirma eficácia esportiva. Nenhum jogador deve ser
considerado disponível no alvo sem fonte; não emitir recomendações de escalação.

Fonte: StatsBomb Open Data, JSONs locais e README local; atribuição exigida ao
compartilhar análises. Fórmulas V1/V2 permanecem descritas em [metrics.md](metrics.md)
e limitações de qualidade em [data_dictionary.md](data_dictionary.md).
