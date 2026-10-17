# Indicadores e fórmulas — versão 1.0.0

Somente eventos dos períodos 1 e 2. Prorrogação e disputa de pênaltis são excluídas
das contagens e da exposição e aparecem como lacuna quando presentes. A orientação
é a registrada: não se espelha o visitante e não se interpreta y como lado tático
esquerdo/direito sem documentação adicional.

Exposição de um jogo: soma do maior `timestamp + duration` observado **em cada
período**, dividida por 60. Timestamps são relativos ao período; `minute` não é
somado novamente. Duração ausente é zero; duração inválida é sinalizada e ignorada
na extensão do relógio. É um proxy de exposição observada, inclui acréscimos e não
mede tempo de bola em jogo.

| metric_id | Medição por jogo | Agregação da janela |
|---|---|---|
| `xg_for` / `xg_against` | Soma do xG dos chutes da equipe / da adversária | Média dos jogos com xG completo |
| `shots_for` / `shots_against` | Contagem de Shot da equipe / da adversária | Média por jogo |
| `xg_per_shot` | xG / número de chutes | Soma xG / soma chutes, apenas jogos elegíveis |
| `pass_accuracy` | Pass completo / Pass tentado | 100 × somas numerador/denominador |
| `pass_accuracy_under_pressure` | Acerto de passes com True explícito | Proporção agregada desse grupo |
| `pass_accuracy_explicit_no_pressure` | Acerto com False explícito | Proporção agregada desse grupo; null se não existir |
| `pass_accuracy_unmarked_pressure` | Acerto sem marcação ou com null | Proporção agregada; não equivale a ausência comprovada de pressão |
| `final_third_attempts` | Pass ou Carry com início x<80 e fim x≥80, inclusive passe incompleto | 90 × soma contagens / soma minutos |
| `final_third_entries` | Mesmo cruzamento, com passe completo ou Carry | Por 90 agregado |
| `box_entries` | Início fora do retângulo x≥102, 18≤y≤62; fim dentro; passe completo ou Carry | Por 90 agregado, inclusive entradas laterais |
| `pressures` | Eventos Pressure | Por 90 agregado; não mede eficácia |
| `pressure_high_share` | Pressure com início x≥80 / Pressure com localização válida | Proporção agregada |
| `counterpressures` | Pressure com `counterpress=True` na raiz | Por 90 agregado; não mede recuperação subsequente |
| `recoveries` | Eventos Ball Recovery | Por 90 agregado; inclui eventos sem avaliação do desfecho |
| `interceptions` | Eventos Interception | Por 90 agregado; sem inferir êxito |
| `duel_tackles` | Duel cujo `duel.type.name` é Tackle | Por 90 agregado; sem inferir êxito |
| `lane_low_y` | Ações localizadas com 0≤y<80/3 / ações localizadas | Proporção agregada |
| `lane_central` | Ações com 80/3≤y<160/3 / ações localizadas | Proporção agregada |
| `lane_high_y` | Ações com 160/3≤y≤80 / ações localizadas | Proporção agregada |

Os corredores incluem todos os tipos de eventos com localização válida. São uma
distribuição de ações registradas, não ocupação contínua, posse ou posicionamento
de jogadores. Mudanças de posse não são convertidas em recuperações. Sequências de
transição não são estimadas no baseline.

## Nulos, cobertura e variação

Cada métrica inclui partidas elegíveis, `sample_size`, numerador, denominador,
valor individual por partida, mediana e desvio-padrão amostral (n−1). DP com n<2
é null. Denominador zero torna a proporção indisponível, sem inventar 0%.
O agregado por exposição pode diferir da média simples dos valores individuais.
Métricas distintas podem ter amostras distintas, identificadas no JSON e nas lacunas.

Menos de cinco partidas analisadas: evidência insuficiente e nenhuma hipótese.
Cinco ou mais: evidência limitada. Cada regra também exige cinco jogos calculáveis
para cada métrica usada. Esses mínimos são escolhas operacionais, não intervalos de
confiança ou validação de eficácia.

## Diferenças intencionais em relação à EDA original

1. A EDA contava passes incompletos nas entradas no terço final. O MVP separa
   tentativas e entradas por passe completo/condução.
2. A EDA usava o maior relógio global; o MVP soma os relógios relativos dos dois
   tempos, incluindo os acréscimos de ambos. Isso modifica denominadores por 90.
3. A EDA fazia médias de taxas/acertos por jogo; o MVP usa razões de somas para
   taxas e proporções, documentando exposição e tentativas.
4. Entradas laterais na área agora são contempladas pela geometria do retângulo.
5. Contrapressão usa a raiz `counterpress`; desarmes usam o tipo do duelo, em vez
   de uma condição que zerava todos os valores.
6. Pressão não marcada não vira False explícito. Corredores recebem nomes por
   intervalo de y para evitar assumir uma orientação tática não validada.
7. Coordenadas inválidas são isoladas e não alimentam indicadores espaciais.
8. O recorte por corredor usa exatamente a janela de cada equipe; não combina
   independentemente conjuntos de team_id e match_id de janelas diferentes.

Os scripts e sete gráficos originais ficam preservados em `outputs/statsbomb_eda_20261002_exec6`.
O MVP entrega as métricas que sustentam as análises; não promete igualdade numérica
com fórmulas anteriores nem redesenha automaticamente aqueles gráficos.
