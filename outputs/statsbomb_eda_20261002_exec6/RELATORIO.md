# EDA StatsBomb Open Data — apoio tático (prova de conceito)

## Objetivo

Demonstrar, sem treinamento de modelos e sem inferência causal, como o clone local do **StatsBomb Open Data** pode sustentar perfis descritivos pré-jogo. Fonte: [StatsBomb Open Data](https://github.com/hudl/open-data), atribuída conforme o README local. Execução: 2026-10-02 20:50 UTC; semente 20261002; revisão do clone: `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`.

## Cobertura e recorte

O inventário do clone está em `inventario_arquivos.csv` e o manifesto integral em `tabelas/manifesto_partidas_completo.parquet`. O recorte principal é **Premier League 2015/2016** (`competition_id=2`, `season_id=27`): 380 partidas, 20 equipes, de 2015-08-08 a 2016-05-17. É uma competição de clubes masculina, fase registrada como `Regular Season`, com 100% de arquivos de eventos e 100% de escalações presentes no clone. A escolha privilegia temporada contínua e 38 jogos por equipe, não uma coleção de partidas famosas. Não se afirma que seja cobertura comercial completa: é a cobertura publicada neste clone.

Há 426 partidas com arquivo 360 no clone total, mas nenhuma análise 360 é misturada a este recorte sem medir evento a evento; o recorte principal não possui arquivo 360. A pasta `open-data/doc/` não está presente; a semântica foi conferida no README local e na estrutura observada. A ausência deve ser suprida por documentação oficial em trabalho futuro.

## Qualidade, relações e transformações

Foram lidos eventos completos uma partida por vez (não todos os 12+ GB simultaneamente), depois descartados da memória. A amostra determinística de até 20 partidas para esquema está em `amostra_inspecao_esquema.csv` e **não** alimenta os resultados do recorte. Os resultados de validação estão em `validacoes_qualidade.csv`: IDs de eventos, vínculo de `match_id`, completude de xG somente entre chutes e fim de passe somente entre passes.

Chaves: competição/temporada → arquivo de partidas; `match_id` → eventos e escalações; 360, quando houver, → `event_uuid=id`. A tabela de escalações não foi expandida na tabela principal de eventos; logo não multiplica passes, chutes ou xG. Nulos não foram transformados globalmente em zero. Para passe, `pass.outcome` ausente é tratado como completo, conforme a convenção StatsBomb observada; para outros booleanos omitidos, mantém-se nulo.

Coordenadas são unidades do plano StatsBomb 120×80, **não metros**. Não foi feito espelhamento automático do visitante: mapas são da orientação registrada. Entradas no terço final exigem início `<80` e fim `≥80`; área exige cruzar `x=102` e terminar em `y∈[18,62]`. A progressão deste estudo é a entrada de passe/condução nessas zonas, uma definição configurável — não uma verdade universal. Exposição por 90 usa o maior tempo observado em períodos 1–2 por partida; prorrogação e pênaltis ficam fora desse denominador.

## Indicadores e leitura descritiva

Os cálculos, filtros, denominadores e limitações estão no dicionário de indicadores. No perfil pré-jogo (até 10 jogos anteriores), Manchester City teve 10 jogos, xG médio 1.58, xG concedido 1.03, acerto de passe médio 81.5%, 79.8 entradas no terço final/90 e 145.8 Pressures/90. Arsenal teve 10 jogos, xG médio 1.50, xG concedido 0.75, acerto 83.0%, 83.2 entradas/90 e 129.2 Pressures/90.

Isso descreve comportamentos na janela, não demonstra que qualquer comportamento causou vitória. `Pressure` é ação de quem pressiona; `under_pressure` é condição de quem executa a ação, portanto as duas medidas não foram confundidas. Recuperações, interceptações e duelos permanecem contagens operacionais distintas; não se conclui “pressiona melhor” por volume bruto.

## Estudo de caso pré-jogo

Confronto demonstrativo: **Manchester City (time próprio) × Arsenal (adversário)**, `match_id=3754314`, data 2016-05-08, fase `Regular Season`, formalmente Manchester City em casa. A data de corte exclui esta partida; os históricos utilizados e suas datas estão em `tabelas/perfil_historico_caso.parquet`. A partida-alvo só pode ser usada em avaliação posterior separada, nunca como entrada do perfil.

Hipóteses para a comissão investigar (não recomendações validadas):

1. **Transição e progressão do Arsenal:** confrontar as entradas no terço final/90 e a distribuição de corredores de Arsenal com vídeo das partidas da janela; métrica de acompanhamento: entradas após recuperação verificável e chutes na mesma posse. Esta entrega ainda não classifica toda troca de posse como recuperação, por isso não reivindica um resultado de transição causal.
2. **Robustez da saída sob pressão do Manchester City:** comparar acerto de passe sob pressão e sem pressão por partida, junto aos mapas de Pressure do adversário. Uma diferença é hipótese de risco de construção, sujeita ao contexto de placar, expulsões e adversários.
3. **Proteção da área:** confrontar xG concedido e localizações dos chutes, não apenas número de chutes. A estabilidade deve ser julgada pela dispersão do gráfico 07 e pelo pequeno n=10, não pela média isolada.

Não é possível concluir a melhor formação, superioridade tática, rivalidade, mando real, campo neutro, lesões/suspensões, importância para título/classificação/rebaixamento ou causalidade de vitória. A fase registrada é `Regular Season`, que não equivale por si a “jogo decisivo”. Formação em Starting XI/Tactical Shift é nominal e não descreve automaticamente a organização com/sem bola.

## Adequação e próximos dados

Esta base sustenta EDA, mapas, perfis históricos e uma prova de conceito de preparação pré-jogo. Um sistema real exigirá atualização periódica, dados completos da competição, integração verificável de calendário/estádio/mando real, lesões, suspensões, elenco, rivalidade e informação entregue pelo treinador, além de validação com analistas. Features futuras pré-jogo podem usar apenas histórico datado, escalações prováveis e contexto externo conhecido antes do apito; placar final, eventos e xG da partida-alvo são produzidos durante/depois e são proibidos como entradas pré-jogo. Qualquer modelo futuro deve usar divisão cronológica e validação por especialistas.

Consulte `MATRIZ_INFORMACOES.md`, `DICIONARIO_DADOS.md`, `DICIONARIO_INDICADORES.md` e os sete gráficos para a rastreabilidade completa.
