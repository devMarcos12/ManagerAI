# SPEC V2 — ManagerAI: Relatório compreensível e interface de análise pré-jogo

**Status:** proposta de próxima iteração, para implementação incremental após inspeção do repositório.  
**Idioma do produto:** português brasileiro.  
**Base:** implementação existente `src/managerai`, StatsBomb Open Data local, relatórios `report.json` e `report.md`.  
**Objetivo:** permitir que uma pessoa da comissão técnica informe os parâmetros de um confronto histórico, execute a análise sem terminal e receba um relatório compreensível, com métricas rigorosas, hipóteses fundamentadas e limitações visíveis.

## 0. Instruções essenciais para o Codex

1. **Inspecione o repositório e leia a documentação existente antes de modificar código:** `architecture.md`, `data_dictionary.md`, `metrics.md`, `tactical_rules.md`, `evaluation.md`, `TUTORIAL_TESTES.md` e os módulos reais (ajuste caminhos conforme o repositório). Não assuma nomes de arquivos inexistentes.
2. Preserve o pipeline de cálculo, regras, validações temporais, hashes de fontes e os contratos que já funcionam. **Não reescreva o motor nem altere fórmulas apenas para melhorar a linguagem.**
3. Implemente a V2 em etapas verificáveis, com testes por etapa. Se houver incompatibilidade, documente e proponha adaptação mínima.
4. **Não execute fine-tuning, não crie um preditor de vitórias e não invente recomendações de escalação ou formação.** Isso permanece fora do escopo da V2.
5. Não altere JSONs originais da StatsBomb; não sobrescreva relatórios anteriores; evite dependências e serviços pagos ou chaves de API.
6. Na camada interna, mantenha `metric_id`, `rule_id`, nomes técnicos, valores exatos e evidências. **Somente a apresentação ao treinador** deve usar linguagem acessível.
7. Se surgir dúvida que afete a fidelidade da interpretação dos dados, prefira uma descrição neutra e registre a limitação em vez de criar uma conclusão.

## 1. O que já existe e deve ser reaproveitado

A entrega anterior descreve: catálogo de competições/temporadas/equipes, seleção de histórico anterior à data ou partida-alvo, engenharia de métricas, comparação entre equipes, regras R01/R02/R03, `AnalysisRequest`, `AnalysisReport`, CLI e saídas `.json`/`.md`, sem LLM. A base documentada usa Premier League 2015/16 (competition_id=2, season_id=27); o exemplo é Manchester City (36) contra Arsenal (1), partida-alvo 3754314, janela 10.

**Não assumir que funções estejam exatamente como descritas sem inspecionar o código.**

## 2. Problemas observados no relatório atual

- Excesso de expressões internas: `xG`, `eventos/90`, `Pressure`, `R01_PROGRESSAO`, `evidence_metrics`, `y menor que 80/3` e IDs de métricas.
- Os principais indicadores estão em tabela extensa, sem interpretação inicial do que mais importa.
- As hipóteses são genericamente formuladas como “investigar”, mesmo quando poderiam citar **valores históricos específicos** para explicar a motivação; sem extrapolar além deles.
- Formações e escalações não são suportadas; isso deve ficar explicitamente identificado, sem parecer falha de execução.
- O usuário consegue passar argumentos no terminal, mas ainda não possui formulário visual.
- Campo manual de contexto não muda a análise; interface e relatório devem informar isso.

## 3. Objetivos da V2 e prioridades

### P0 — Relatório 2.0 (obrigatório)

Gerar o relatório humanizado em Markdown, derivado do objeto estruturado existente, sem alterar resultados numéricos. Preservar a versão detalhada/auditável para quem quiser conferir.

Estrutura sugerida:

1. **Visão geral do confronto**: equipes, temporada, data de referência, jogos anteriores usados, mensagem de limitação histórica.
2. **Resumo para a comissão técnica**: 3–5 observações concretas, com números e período; não prometer vitória.
3. **Comparação dos times**: tabela curta de 6–10 indicadores priorizados, contendo explicação curta e unidade correta; detalhes completos em seção expansível da interface ou apêndice Markdown.
4. **O que merece atenção no adversário**: interpretações descritivas justificadas por indicadores e tamanho da amostra.
5. **Possíveis ajustes para avaliar em treino/vídeo**: cada hipótese deve responder: *o que foi observado*, *por que importa*, *o que a comissão poderia verificar/testar*, *o risco e a limitação*. Hipóteses devem citar as evidências pertinentes; nunca transformar limiares arbitrários em certeza.
6. **Informações declaradas pelo treinador**: manter claro que clássico, importância e objetivo são informados manualmente e **não alteram o cálculo nesta versão**.
7. **O que o sistema ainda não consegue recomendar**: escalação, formação ideal, lesões, suspensões, eficácia causal e resultado da partida.
8. **Detalhes técnicos (apêndice)**: nomes/IDs de métricas, regras, fórmulas, lacunas, IDs das partidas e rastreabilidade, quando relevantes. Não omitir evidências: mantê-las no JSON integral.

**Exemplo de estilo (usar valores apenas quando realmente presentes no relatório):**

> Nos dez jogos anteriores analisados, o Arsenal realizou em média 15,3 finalizações por partida, contra 13,3 do Manchester City. Já a qualidade estimada das chances criadas foi de 1,50 gol esperado por jogo para o Arsenal e 1,58 para o City. Isso não determina qual time teria melhor desempenho no confronto; sugere revisar a localização e o contexto das finalizações antes de escolher os ajustes defensivos.

Não usar expressões como “Arsenal tem ataque mais forte” apenas com base no maior volume de chutes, nem afirmar que o City "cria 1,58 chances de gol" — **xG não é contagem de chances nem probabilidade de vencer**.

### P0 — Vocabulário para público de futebol (obrigatório)

Criar um módulo isolado, por exemplo `presentation/terminology.py`, ou outra estrutura consistente com o projeto, que mapeie IDs técnicos para título, unidade e explicação curta, com testes.

| Identificador interno | Título amigável sugerido | Explicação / ressalva |
|---|---|---|
| `xg_for` | Qualidade estimada das chances criadas (gols esperados) | Soma do valor esperado das finalizações por partida; **não** é quantidade de chances, gol real nem probabilidade de vencer. Apresentar “xG” apenas entre parênteses/tooltip na primeira menção. |
| `xg_against` | Qualidade estimada das chances permitidas ao adversário | xG concedido, não número de gols sofridos. |
| `xg_per_shot` | Qualidade média das finalizações | Valor esperado por chute, não porcentagem de finalizações certas. |
| `shots_for` | Finalizações por jogo | Quantidade média de chutes. |
| `shots_against` | Finalizações permitidas por jogo | Chutes do oponente. |
| `pass_accuracy` | Passes certos (%) | Percentual de passes completos conforme a regra de dados. |
| `pass_accuracy_under_pressure` | Passes certos em ações marcadas sob pressão (%) | Somente os passes explicitamente marcados sob pressão. |
| `pass_accuracy_explicit_no_pressure` | Passes certos em ações explicitamente sem pressão (%) | Pode estar indisponível; não preencher com dados “sem marcação”. |
| `pass_accuracy_unmarked_pressure` | Passes certos sem informação de pressão (%) | **Não** rotular como “passes sem pressão”. |
| `final_third_entries` | Entradas no terço de ataque por 90 min | Entradas por passe completo ou condução, não toda posse ou entrada de jogador. |
| `final_third_attempts` | Tentativas de avançar ao terço de ataque por 90 min | Inclui passes tentados que não se completaram. |
| `box_entries` | Entradas na área por passe ou condução por 90 min | Não inclui toda forma de entrada ou cruzamento sem contexto. |
| `pressures` | Ações de pressão registradas por 90 min | Número de eventos registrados, não eficiência. |
| `pressure_high_share` | Parcela da pressão realizada no terço ofensivo (%) | Não equivale a sucesso da pressão. |
| `counterpressures` | Ações de contrapressão registradas por 90 min | Eventos marcados como contrapressão. |
| `recoveries` | Recuperações de bola registradas por 90 min | Definição de evento StatsBomb; sem afirmar todas bem-sucedidas. |
| `interceptions` | Interceptações registradas por 90 min | Eventos registrados, sem inferir êxito universal. |
| `duel_tackles` | Disputas de bola do tipo desarme por 90 min | Não afirmar desarme bem-sucedido. |
| `lane_low_y`, `lane_central`, `lane_high_y` | Distribuição das ações por faixa do campo (%) | **Não** atribuir automaticamente esquerda/direita a `low_y` ou `high_y`, pois a orientação não foi validada. |

Na interface, mostrar descrições curtas via ajuda/tooltip; no relatório, usar glossário ou notas discretas. Unidades amigáveis como “por 90 min”, “por jogo”, “%” devem ser consistentes; arredondamento de exibição não pode modificar valores internos. Não substituir métricas de xG por gols reais ou por probabilidade de vitória.

### P1 — Interface interativa local, preferencialmente Streamlit

Após concluir P0, criar uma interface funcional simples que use o **mesmo pipeline** da CLI. Dependência `streamlit` pode ser adicionada em arquivo separado de dependências para interface, mantendo o núcleo funcionando sem ela.

**Fluxo do treinador:**

1. Selecionar competição e temporada entre as realmente disponíveis no catálogo.
2. Selecionar **meu time** e **adversário** com nomes legíveis, filtrados pelo recorte; impedir selecionar o mesmo time duas vezes.
3. Selecionar **partida-alvo histórica** disponível para esse confronto OU **data de corte livre**. Os modos são exclusivos e explicados na tela. Ao selecionar partida, mostrar data e mando formal se disponível, sem revelar placar como evidência pré-jogo.
4. Informar janela de partidas anteriores (padrão 10, respeitando a validação 1–100), mando/contexto/objetivo manual e notas. Jogadores indisponíveis apenas se o controle for possível usando elenco elegível anterior ao corte; caso contrário, não expor seletor enganoso.
5. Botão **Analisar confronto** com validação e tratamento claro de erros; mensagens de insuficiência de histórico.
6. Mostrar tela de resultado: resumo, tabela comparativa, hipóteses rastreáveis, limites, metodologia compacta, opção de inspecionar dados avançados.
7. Permitir baixar **relatório legível `.md`** e **relatório técnico `.json`**. Opcional: HTML/PDF somente se trivial e fiel ao Markdown, sem atrasar prioridades.

**Arquitetura da interface:** chamar funções Python do pipeline diretamente, se houver API interna apropriada, ou criar adaptador reutilizável; evitar executar CLI por shell e evitar recalcular métricas em código de apresentação. Não ler todos os eventos a cada mudança de campo no formulário. Tratar caminhos de saída com segurança. Não confiar em entradas de texto para comandos ou caminhos arbitrários.

**Acessibilidade:** textos em português do Brasil; ajudas curtas; estado de carregamento; modo escuro/claro padrão do Streamlit; sem exigir conhecimento de `competition_id`, `team_id` ou `target_match_id`.

### P1 — Análises mais úteis, mas somente com dados comprovados

- Tornar as hipóteses existentes específicas ao confronto, inserindo comparações numéricas calculadas **somente** a partir das métricas referenciadas e disponíveis.
- Não sugerir corredores “esquerdo/direito” sem validação espacial; se não houver granularidade confiável, indicar que a zona específica ainda exige vídeo.
- Não tratar maior valor bruto de pressão como pressão mais eficaz, nem concluir estilo de jogo a partir de uma estatística isolada.
- Contexto manual deve aparecer no relatório como cenário de planejamento, sem afetar gatilhos não validados. Se houver desejos de personalização real, apresentar **plano futuro** e campos necessários, não fingir inteligência contextual.
- Identificar indicadores indisponíveis e não inventar substitutos; com menos de cinco jogos, preservar abstenção.

### P2 — Planejamento da evolução (documentar, não implementar nesta versão)

- Estudar escalações e formações observadas historicamente, critérios de elegibilidade pré-jogo e métricas por atleta, antes de qualquer sugestão nominal.
- Avaliar se existem variáveis-alvo e rótulos válidos para treinar um modelo; placar de jogo não equivale à melhor estratégia.
- Considerar integração com LLM apenas como camada opcional de apresentação, com controle de fidelidade, evidências e testes contra alucinações.
- Considerar visualizações de campo somente depois de verificar orientação e semântica espacial dos eventos.

## 4. Critérios de aceite

### Dados e regressão

- [ ] Mesma requisição e mesmos dados produzem indicadores numéricos idênticos aos do relatório técnico V1 (salvo bug identificado e aprovado separadamente).
- [ ] `report.json` segue válido e mantém IDs técnicos, unidades, dados por partida, tamanhos amostrais, referências e hashes. Mudanças de schema são versionadas e documentadas.
- [ ] Testes de seleção temporal confirmam que arquivos do alvo e do futuro não entram nas métricas.
- [ ] Motor não passa a afirmar vitória provável, melhor escalação, eficácia de regra ou causalidade.

### Relatório e linguagem

- [ ] Títulos e narrativas principais usam linguagem cotidiana do futebol; códigos internos aparecem apenas no apêndice técnico.
- [ ] “Gols esperados (xG)” são definidos corretamente; não se afirma que 1,58 xG significa 1,58 chances de gol.
- [ ] Indicadores indisponíveis ficam explicitamente indisponíveis; jamais assumidos zero.
- [ ] Cada recomendação mostra números e observações rastreáveis, condição, risco e limitação.
- [ ] O treinador identifica rapidamente 3–5 achados principais quando houver dados suficientes, sem fabricação de achados.
- [ ] Termos e números da versão amigável são coerentes com o JSON; formato pt-BR sem confundir ponto decimal e separador de milhar.

### Interface

- [ ] É possível escolher City e Arsenal por nome e gerar o relatório do alvo histórico documentado sem digitar IDs.
- [ ] A seleção de partidas/data é validada; confrontos inválidos são impedidos com mensagens compreensíveis.
- [ ] A interface usa o mesmo pipeline de análise da CLI, sem duplicação de cálculos.
- [ ] Downloads `.md` e `.json` funcionam.
- [ ] O fluxo mantém funcionamento local sem LLM, chave de API, GPU ou internet (após instalar a dependência de UI).
- [ ] Testes novos passam e comandos da CLI anterior continuam funcionando.

## 5. Cenários obrigatórios de demonstração

**Cenário A — normal:** Premier League 2015/16, Manchester City (36) × Arsenal (1), alvo 3754314, janela 10. Valores de referência do relatório fornecido: xG a favor City 1,58 e Arsenal 1,50; finalizações City 13,30 e Arsenal 15,30; acerto de passe City 81,93% e Arsenal 83,79%; entradas no terço final City 59,90 e Arsenal 63,54 por 90 min. Não usar esses valores hardcoded: os cálculos devem vir dos JSONs.

**Cenário B — sem histórico:** corte 2015-08-08, mesmas equipes e temporada. Mostrar ausência de amostra e não gerar hipóteses artificiais.

**Cenário C — janela pequena:** janela 2, alvo histórico. Exibir observações com limitação e nenhuma hipótese, preservando política mínima documentada.

**Cenário D — dados/entradas inválidas:** times iguais, partida-alvo que não corresponde às equipes, diretório de dados ausente; erros claros sem traceback cru para o treinador.

**Cenário E — reprodução:** CLI antiga e UI devem produzir o mesmo `AnalysisReport` para a mesma requisição e fontes, exceto aspectos de apresentação.

## 6. Entregáveis solicitados

1. Alterações de código necessárias, incrementais e com testes.
2. Relatório V2 de demonstração (`.md`) e respectivo `.json`, gerados pelos dados reais; não sobrescrever resultados anteriores.
3. Aplicação Streamlit funcional, com instruções de execução (ex.: `streamlit run ...` com caminho real descoberto no repositório).
4. Documento curto `CHANGELOG_V2.md` informando arquivos alterados, decisões, limitações e comandos dos testes executados com resultados reais.
5. Evidência do cenário normal e ao menos um caso de amostra insuficiente.
6. Lista priorizada de questões ainda abertas para versão seguinte (formações, elenco, contexto, modelagem preditiva).

## 7. Sequência de trabalho para o Codex

**Passo 1:** inspecionar o projeto, enumerar arquivos relevantes, executar testes existentes e verificar se o relatório enviado corresponde ao pipeline real.  
**Passo 2:** implementar P0 (vocabulário + relatório humanizado), adicionar testes, executar o caso City × Arsenal e validar consistência com V1.  
**Passo 3:** implementar P1 (Streamlit), com entrada amigável e download, reutilizando o pipeline.  
**Passo 4:** executar cenários de aceite, corrigir problemas, documentar como rodar e mostrar o exemplo final.  
**Passo 5:** apresentar as limitações e plano P2, sem implementá-lo por conta própria.

Se a interface exigir alteração material na arquitetura, **explique primeiro o trade-off e aplique apenas a menor mudança compatível com as proteções já existentes**. Preserve os artefatos históricos gerados e a documentação do MVP anterior.
