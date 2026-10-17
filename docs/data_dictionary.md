# Dados locais e qualidade

## Fonte e cobertura observada

Raiz padrão: `open-data/data`. Snapshot local identificado na auditoria inicial pela
revisão `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb` do repositório de dados.
Cada execução usa hashes SHA-256 dos bytes efetivamente lidos, sem depender do Git.

O catálogo observado contém 24 competições, 80 pares competição/temporada e 3.961
partidas distintas. Há 4.235 arquivos de eventos, 4.235 de escalações e 426 de 360.
Os 274 IDs adicionais de eventos/escalações não associados ao catálogo não entram
na seleção de partidas. Presença de arquivo não comprova qualidade do conteúdo.

Premier League 2015/16: competição 2, temporada 27, 380 jogos, 20 clubes, 38 jogos
por clube, de 2015-08-08 a 2016-05-17. Todos possuem eventos e escalações; nenhum
possui arquivo 360. A auditoria inicial leu 1.313.773 eventos e 13.678 registros de
jogadores por partida/equipe. Esses registros não são 13.678 atletas distintos.

## Arquivos e campos utilizados

| Arquivo/campo | Tipo | Uso e tratamento |
|---|---|---|
| `competitions.json` | array de objetos | Pares de IDs permitidos; duplicações são erro |
| `matches/{competition_id}/{season_id}.json` | array | Calendário e identificação; resultados não viram features |
| `match_id` | inteiro positivo | Chave única entre temporadas no inventário |
| `match_date`, `kick_off` | strings ISO | Corte por data; o mesmo dia é excluído conservadoramente |
| `home_team`, `away_team` | objetos | IDs, nomes e mando formal; não certificam mando real |
| `events/{match_id}.json` | array | Fonte das features; arquivo ausente gera lacuna |
| `id`, `index` | string / inteiro | Identidade e ordem; duplicações são erro |
| `period`, `timestamp`, `duration` | inteiro / string / número | Exposição observada nos períodos 1 e 2; duração inválida é registrada e não estende exposição |
| `team.id`, `possession_team.id` | inteiro | Consistência com as equipes da partida |
| `player.id` | inteiro opcional | Checagem contra escalação histórica da partida |
| `type.name` | string | Categoria de ação; não equivale a eficácia tática |
| `location` | array [x, y] | Plano 120×80; ausente/fora do domínio não entra em cálculos espaciais |
| `pass.end_location`, `carry.end_location` | arrays | Cruzamento de zonas; extremos precisam ser válidos |
| `pass.outcome` | objeto opcional | Ausência/objeto vazio interpretado como passe completo segundo a convenção usada na EDA; pressupõe payload pass íntegro |
| `under_pressure` | booleano opcional | True, False explícito e não marcado são grupos separados |
| `shot.statsbomb_xg` | número em [0,1] | Se ausente/inválido em algum chute, xG da equipe naquele jogo fica indisponível |
| `counterpress` | booleano na raiz | Usado apenas em eventos Pressure para contrapressões marcadas |
| `duel.type.name` | string | Tackle conta como duelo desse tipo, sem inferir sucesso |
| `lineups/{match_id}.json` | array de duas equipes | Sem expansão da tabela de eventos; IDs de jogadores únicos por equipe |
| `lineup[].positions`, `tactics.formation` | arrays / inteiro | Existem nos dados observados, mas não fundamentam recomendações de formação no MVP |
| `three-sixty/{match_id}.json` | array opcional | Apenas cobertura no inventário; não consumido pelas features |

O `freeze_frame` de chute não equivale a arquivo 360 ou tracking integral. A pasta
`open-data/doc` está ausente no snapshot; não presumimos validação semântica completa
das coordenadas, posicionamento sem bola ou campos opcionais.

## Política de qualidade

- Arquivos inválidos, IDs duplicados, equipes incompatíveis, timestamps inválidos e
  exposição sem os dois tempos regulamentares interrompem a análise com erro.
- Ausência de arquivo de eventos reduz a amostra; não busca jogos mais antigos para
  completar artificialmente a janela. Ausência de escalação gera lacuna e permite
  a analítica coletiva; não cria jogadores.
- Coordenadas ausentes ou inválidas são contabilizadas. Não são cortadas para o
  limite nem transformadas em zero; a ação permanece nas contagens não espaciais.
- Durações negativas/não finitas geram `durations_invalid`; a ação permanece, mas a
  duração inválida não participa da extensão do relógio. Isso é uma regra explícita
  de cálculo, não uma alteração do JSON bruto.
- xG incompleto nunca é somado parcialmente como se fosse o total do jogo. Um jogo
  sem chutes tem xG zero após a validação do fluxo de eventos; ausência de histórico
  tem valor `null`, não zero.
- As contagens de qualidade de cada perfil referem-se aos arquivos completos das
  partidas-fonte, incluindo as duas equipes; não são taxas específicas do clube.
- A auditoria não certifica completude comercial, ausência de todos os tipos de
  erro nem disponibilidade histórica de cada anotação na época do jogo.

As checagens locais iniciais encontraram três coordenadas com x acima de 120,
8.077 eventos sem localização e duas durações negativas (em 3754232 e 3754250).
A ausência de localização em eventos não espaciais pode ser esperada. Confira a
auditoria executável para o snapshot atual; `com_lacunas` não significa dados inutilizáveis.

## Versionamento e temporalidade

O relatório lista caminho relativo e SHA-256 de cada fonte lida. O fingerprint é
o SHA-256 do mapa ordenado caminho→hash. Não há timestamp variável de geração no
JSON: entradas, bytes de dados e versões iguais produzem relatório idêntico.

Metadados do calendário inteiro são lidos para validar o recorte e selecionar o
histórico. Placar final e atributos pós-jogo do alvo não são utilizados em features.
Eventos e escalações do alvo/futuro não são lidos. O dataset é retrospectivo: o corte
restringe as partidas utilizadas, mas não comprova que todas as anotações ou revisões
do fornecedor já estivessem publicadas naquela data histórica.
