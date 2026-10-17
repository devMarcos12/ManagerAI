# SPEC — ManagerAI | V2.2 (correções) + V3 (inteligência tática baseada em eventos)

**Status:** especificação de implementação · **Idioma:** português brasileiro · **Ambiente:** repositório local do usuário · **Entrada:** base local StatsBomb Open Data · **Prioridade:** confiabilidade antes de complexidade.

## 0. Missão do agente e autorização para trabalho autônomo

Você (Codex) deve **inspecionar o repositório existente**, implementar e validar **duas fases sequenciais**: (A) fechar problemas da V2 e (B) desenvolver a primeira V3 com análises táticas observáveis por eventos. O usuário ficará ausente temporariamente; **não aguarde confirmação entre tarefas comuns**. Você está autorizado a criar/editar arquivos necessários, executar comandos shell, rodar testes e auditorias, instalar dependências do projeto no ambiente virtual existente quando justificável e inspecionar dados locais. **Subagentes podem ser usados se estiverem disponíveis**, especialmente em frentes independentes (auditoria de dados, UX/testes e engenharia de métricas), mas a orquestração deve evitar modificações concorrentes no mesmo arquivo; se não estiverem disponíveis, continue sozinho.

### Restrições não negociáveis

- **NÃO FAÇA COMMITS**: não execute `git commit`, `git push`, criação de PR, publicação de pacote, deploy ou qualquer ação remota que altere repositórios. Não altere configurações de remotes nem histórico Git.
- Não execute `git reset --hard`, `git clean -fd`, `rm -rf` ou exclusões em massa. Preserve alterações existentes do usuário; verifique `git status` antes e depois. Não sobrescreva trabalhos não relacionados.
- Não modifique JSONs originais em `open-data/data` nem mude ou exclua arquivos de EDA/outputs existentes. Saídas de teste e relatórios novos devem estar em novos diretórios versionáveis ou temporários seguros; não sobrescreva resultados anteriores.
- Não use serviços pagos, APIs externas, chave de LLM, fine-tuning nem download massivo de datasets; só dados locais e ferramentas já disponíveis, salvo dependências Python necessárias para executar a UI/testes.
- Não fabrique fatos esportivos, lesões, disponibilidade, avaliações de jogadores, sucesso de pressão ou probabilidade de vitória. **Não utilize eventos, escalações ou resultados da partida-alvo ou posteriores na análise pré-jogo.**
- Evite migrações destrutivas e quebra de compatibilidade. Preserve a API/CLI e o contrato técnico `report.json` V1/V2, salvo se mudanças aditivas e versionadas forem realmente necessárias. Documente mudanças e testes.
- Se encontrar bloqueio (dados insuficientes, erro estrutural, ausência de ambiente), registre no documento final e avance nas tarefas independentes; não elimine validações para obter teste verde.

## 1. Contexto do produto

O ManagerAI é um **sistema de apoio à comissão técnica** que recebe equipe, adversário, competição/temporada, partida histórica ou data de referência, janela de jogos, mando, contexto e objetivo manual; analisa **partidas anteriores** existentes no StatsBomb Open Data e gera um relatório acessível e rastreável. O projeto já possui CLI Python, pipeline de indicadores e regras conservadoras, relatórios `.md` e `.json`, UI Streamlit e testes.

Documentos que devem ser lidos quando presentes no repositório: `SPEC_MVP_ANALISE_TATICA_STATSBOMB.md`, `SPEC_V2_MANAGERAI_RELATORIO_INTERFACE.md`, `TUTORIAL_V2.md`, `architecture.md`, `data_dictionary.md`, `metrics.md`, `tactical_rules.md`, `evaluation.md`, além do código-fonte, testes e README. Trate a implementação real como fonte da verdade operacional; anote divergências com tutoriais.

### Evidência do problema na V2

O relatório histórico **Real Madrid × Barcelona — La Liga 2020/21, referência 10/04/2021** apresentou **Real Madrid com 1 jogo** (24/10/2020) e **Barcelona com 10 jogos** (31/01–05/04/2021). Mesmo abstendo-se corretamente de sugerir ajustes, exibiu uma tabela comparativa com, por exemplo, 2,90 versus 1,87 de gols esperados/jogo. Isso pode induzir leitura comparativa enganosa. Também exibe `1 jogos`; usa frases pouco naturais e recebe `fora`, `eliminatório`, `buscar gol` sem que esses campos mudem as regras. **Não trate esse exemplo como bug de valores sem verificar os arquivos brutos:** pode ser cobertura parcial legítima.

O recorte principal já validado é **Premier League 2015/16** (competição 2, temporada 27, 380 partidas, 20 clubes); exemplo reprodutível **Manchester City (36) × Arsenal (1), alvo 3754314 em 08/05/2016** com 10 jogos anteriores de cada equipe. Dados de La Liga e outras competições podem ter cobertura parcial.

## 2. Estratégia geral: dois marcos, execução contínua

**Marco A — V2.2:** auditoria da cobertura, políticas de qualidade e UX, relatórios legíveis, testes de regressão. Apenas prossiga ao Marco B quando os testes essenciais da V2.2 passarem; se houver testes falhando, diagnostique e corrija antes.

**Marco B — V3:** novas métricas observáveis, análises de sequências e padrões de equipe usando eventos e, quando possível, análises exploratórias de jogadores e formações **sem sugerir escalação ideal**. Acrescente achados e hipóteses com evidência explícita e explicação acessível. Não treine modelo sem rótulos e validação.

## 3. Marco A — V2.2: requisitos obrigatórios

### A1 — Cobertura antes da análise

1. Exibir no formulário Streamlit um **diagnóstico de cobertura** referente ao time, adversário, competição/temporada, data-alvo/corte e janela solicitada: jogos históricos **encontrados** por equipe, período disponível e quantidade elegível; não ler eventos para uma simples prévia do catálogo (usar metadados do calendário). Quando não houver arquivos de eventos, distinguir `partidas no calendário` de `partidas com eventos disponíveis` e destacar que a qualidade só é conhecida após a análise.
2. Mostrar avisos claros antes de executar quando uma equipe possuir menos de 5 jogos; ex.: “Real Madrid: apenas 1 jogo anterior disponível; comparação não confiável”. O usuário pode executar mesmo assim para exploração descritiva, mas não obter recomendações apoiadas em amostra insuficiente.
3. Informar que `janela = 10` significa **até 10 partidas anteriores disponíveis**, não obrigatoriamente 10; **não completar** com jogos posteriores nem de datas iguais ao corte.
4. Investigar se outras temporadas anteriores da mesma equipe e competição seriam incorporáveis, mas **não fazer junção automática entre temporadas ou elencos sem regra documentada e aprovada**; nesta entrega, apenas registrar oportunidades de melhoria de cobertura.

### A2 — Apresentação proporcional à evidência

1. Se uma equipe possuir <5 jogos calculáveis nas métricas centrais, classificar comparação como **“amostra insuficiente”**, destacar aviso no começo do relatório e junto à tabela; não usar linguagem de vantagem, superioridade ou fraqueza comparativa.
2. Separar **“indicadores observados (consulta descritiva)”** de **“conclusões sustentadas”**. Em amostras diferentes, mostrar `n` e data das partidas em todas as tabelas pertinentes. Não suprimir valores brutos válidos, mas reduza sua saliência ou indique explicitamente “não interpretar diferenças como superioridade”.
3. Na UI, para n=0, mostrar `não disponível`, nunca 0; para n=1, não inventar desvio-padrão; não usar cores/ícones de vitória/derrota para comparações sem suporte.
4. Criar testes para Real Madrid × Barcelona e City × Arsenal, incluindo n=1 versus n=10 e n=10 versus n=10.

### A3 — Português acessível e terminologia

1. Corrigir singular/plural em TODOS os canais visíveis: `1 jogo`, `2 jogos`, `1 partida`, `0 partidas`; corrigir espaços antes de `%`, incoerências e acentuação.
2. Preferir `Gols esperados a favor` e `Gols esperados concedidos`; explicar no primeiro uso: **xG estima a qualidade das finalizações, não o número de chances ou a chance de vitória**. Não usar apenas “chance de gol” como substituto matematicamente incorreto.
3. Preferir `Tentativas de pressão registradas` a `eventos Pressure`; esclarecer que contagem não prova êxito. Nomear avanços ao terço de ataque e entradas na área com linguagem comum, preservando fórmula em apêndice.
4. Códigos como `R01_PROGRESSAO`, `xg_against`, `y >= 160/3` e caminhos de evidência devem ficar somente em **detalhes técnicos**, nunca no texto principal. Toda afirmação principal deve ter base nas métricas.
5. Garantir que o texto esteja correto para um torcedor ou treinador sem conhecimento de estatística; em caso de termo essencial, incluir glossário curto ou tooltip.

### A4 — O que o contexto faz e NÃO faz

1. Rotular `mando`, `contexto (clássico/eliminatória/regular)` e `objetivo` como **informações declaradas pelo treinador**. Enquanto as regras não forem validadas, declarar junto aos inputs e no relatório que **não alteram indicadores nem hipóteses automáticas**.
2. Não inventar regras como “clássico exige pressão alta” ou “buscar gol garante estratégia ofensiva”. Registre no roadmap uma proposta para futura personalização *condicional* sem causalidade espúria.
3. Evitar chamar o resultado atual de “plano ideal” ou “escalação sugerida”.

### A5 — Compatibilidade e testes

- Preservar resultados numéricos e significado de cada campo do `report.json` em casos idênticos. Prefira mudar UI/renderização/novos metadados de apresentação em vez de alterar fórmulas.
- Rodar todos os testes existentes e adicionar testes de cobertura, mensagens, singular/plural, evidência insuficiente, consistência CLI/UI e não vazamento temporal.
- Documentar o que mudou em `docs/CHANGELOG_V2_2.md` ou local equivalente.

## 4. Marco B — V3: engenharia de análise tática orientada por evidências

### B1 — Antes de implementar, auditar o que os dados permitem

Mapear eventos, posses, passes, carregamentos, finalizações, pressões, recuperações, posições/formações e duração no snapshot local. Declarar cobertura por competição/temporada/campo. Verificar convenção espacial e orientação por período antes de chamar uma zona de lado esquerdo/direito tático. Identificar limitações de `three-sixty` (PL 2015/16 não possui arquivos 360 no inventário V1). **Não inferir posicionamento sem bola, shape defensivo ou ocupação contínua a partir de eventos isolados.**

Entregar `docs/V3_DATA_FEASIBILITY.md`: disponibilidade, fontes, significado, amostras, casos sem dados, riscos, priorização (viável / parcial / não viável).

### B2 — Métricas V3 prioritárias: somente se semanticamente justificáveis

Implementar pelo menos **três famílias de métricas robustas** dentre as seguintes, preferencialmente as primeiras, com contrato estável, testes sintéticos e casos reais:

1. **Progressão e construção ofensiva:** passes e conduções progressivas definidos por zonas/distância à meta de forma explícita; entradas no terço de ataque e área segmentadas por passes/conduções; sequência de passes ou conduções que levam à entrada, sem atribuir causalidade.
2. **Finalizações e criação de chances:** distribuição de localizações dos chutes e xG por zonas, com coordenadas verificadas, taxa de finalizações por posse/jogo quando denominadores existirem; qualidade média por chute (não confundir com gols), origem de sequências anteriores à finalização quando possível.
3. **Pressão e recuperação:** densidade espacial de `Pressure`, recuperações após pressões em janela de eventos/tempo (definição operacional validável, com verificações de troca de posse e exclusões), sem equiparar proximidade a causalidade; se impossível, implementar apenas descrição e marcar como não inferível.
4. **Padrões de posse/transição:** sequências de posse com começo/fim e critérios explícitos; tempos entre recuperação e finalização / entrada na área; distinguir contra-ataque observado de hipótese interpretativa.
5. **Perfis de jogadores e formações históricas (exploratório):** participação de atletas em passes/progressões/chutes por partida; posições e formações registradas em partidas **anteriores**; atribuir disponibilidade = desconhecida sem fonte externa. **Não emitir onze inicial, reservas ideais ou “formação vencedora” na V3.**

Se uma das famílias for inviável, **não improvise**. Faça a análise de viabilidade e substitua por outra justificável, documentando a decisão. Prefira 3 análises verificáveis a 10 superficiais.

### B3 — Comparações, indicadores e contexto

- Calcular perfis próprios e do adversário usando janelas históricas com o MESMO critério de corte temporal, amostras claramente identificadas e métricas por partida/90 ou proporções com denominadores corretos.
- Exigir mínimo operacional configurado/documentado para qualquer hipótese; mostrar número de jogos elegíveis **por métrica**; não atribuir “confiança 90%” ou probabilidades não calibradas.
- Identificar padrões úteis mas conservadores, como concentração de entradas em determinadas **faixas do campo** e zonas das finalizações. Só usar esquerda/direita quando orientação for comprovada.
- Ao sugerir ação tática, formular **hipótese testável**, por exemplo “avaliar proteção das entradas por passe no setor X”, sempre com observação numérica, pré-condição, risco e limite, sem proclamar eficácia.
- O objetivo manual poderá ordenar **apenas a apresentação** de hipóteses (por exemplo, “buscar gol” prioriza achados ofensivos) se isso for explicitamente descrito como priorização editorial e não como previsão de eficácia; se muito custoso, mantenha somente como cenário declarado. Nunca alterar retrospectivamente métricas.

### B4 — UI e relatório V3

- Manter a experiência atual do Streamlit; adicionar seções **“Como o adversário ataca”**, **“Como ele pressiona e recupera a bola”**, **“Padrões observados dos jogadores”** (somente se viável) e **“Hipóteses para testar”**, ocultando ou marcando indisponível quando faltem dados.
- Incluir pelo menos **duas visualizações úteis** (por exemplo, mapa de chutes e comparação da progressão por zonas), sem destruir gráficos/EDA pré-existentes. Cada gráfico deve ter título, unidade, legenda clara, amostra e descrição curta do que NÃO é possível concluir; respeitar coordenadas e fonte.
- Gerar `.md` amigável e `.json` estruturado; adicionar campos V3 de forma aditiva com `schema_version` e documentação. Se o contrato antigo não puder continuar byte a byte idêntico, manter campos e semântica e adicionar testes que garantam compatibilidade dos consumidores existentes.
- A interface deverá continuar funcional sem LLM, rede ou serviço pago. **Não integrar fine-tuning/LLM neste ciclo.**

### B5 — Validação técnica e esportiva

1. Testes unitários de parsing, associação equipe/evento/jogador, geometrias, janelas temporais, posses, contadores, denominadores e valores nulos.
2. Testes de **não vazamento**: corromper ou editar sinteticamente arquivos do alvo/futuro e demonstrar que o relatório pré-jogo não muda. Não tocar nos dados brutos reais.
3. Executar V3 para City × Arsenal (08/05/2016; alvo 3754314; janela 10), preservando suas métricas V2; executar cenário de cobertura parcial Real Madrid × Barcelona (10/04/2021), com abstenção coerente.
4. Comparar novos indicadores independentemente a partir de uma amostra dos JSONs originais e fornecer fórmulas/exemplos reproduzíveis.
5. Testar CLI e interface Streamlit com `AppTest` quando disponível; documentar screenshots/manualmente a revisão visual apenas se realmente inspecionada, sem alegar validação visual automatizada de navegação real.
6. Avaliação esportiva: preparar checklist para a comissão técnica revisar cada hipótese (rastreabilidade, plausibilidade, riscos, interpretação, utilidade). **Não declarar eficácia esportiva demonstrada** sem avaliação de especialistas.

## 5. Priorização para execução longa sem acompanhamento

Siga esta ordem:

1. `git status` e inventário do código/documentos/dados; registrar baseline dos testes.
2. Implementar A1–A4 (cobertura, qualidade, português, transparência dos inputs).
3. Rodar testes + corrigir regressões; salvar changelog V2.2.
4. Fazer auditoria de viabilidade V3 e registrar achados.
5. Implementar B2 por prioridade e B3, com testes pequenos e regulares.
6. Integrar V3 no pipeline/JSON/renderização e depois na UI com duas visualizações.
7. Rodar testes completos, integração real e cenários extremos; gerar relatórios demonstrativos em diretórios novos.
8. Atualizar `README` e tutoriais para uso por pessoa não técnica; criar `docs/RELATORIO_FINAL_V2_2_V3.md` com entregas, comandos, testes executados/resultados, evidências, limitações e próximos passos.
9. Finalizar com `git status` e resumo da lista de arquivos alterados. **Não commitar**.

Se o tempo/ambiente não permitir completar toda a V3, entregue um marco coerente testado e descreva explicitamente o restante; não afirme “concluído” para funções não implementadas. Evite iniciar funcionalidades experimentais que comprometam estabilidade.

## 6. Critérios de aceite

### V2.2
- [ ] Real Madrid × Barcelona com 1 vs 10 jogos apresenta alerta de amostra insuficiente antes e depois da análise e **não fornece conclusão de superioridade**.
- [ ] City × Arsenal com amostra de 10/10 mantém números V2 e permite emitir hipóteses preexistentes.
- [ ] Sem `1 jogos`, nem códigos internos no corpo amigável; glossário explica xG corretamente.
- [ ] Inputs contextuais explicitam que não mudam a analítica nem gatilhos no estágio atual.
- [ ] Testes anteriores passam; dados brutos intocados.

### V3
- [ ] Auditoria de viabilidade escrita e ancorada nos campos efetivos do dataset.
- [ ] Ao menos três famílias robustas de indicadores observáveis com fórmulas, testes e políticas de ausência de dados; ou justificativa documentada para escopo menor quando o dataset impedir.
- [ ] Pelo menos duas visualizações efetivamente funcionando no Streamlit com legenda, fontes e limitações.
- [ ] Hipóteses novas, quando existirem, citam métricas calculadas e evitam alegações causais ou “vitória provável”.
- [ ] A exclusão da partida-alvo e futuro continua garantida por testes.
- [ ] UI, CLI, `.md`, `.json` operam com casos reais e sem treinamento nem chamadas externas.
- [ ] Todos os testes aplicáveis executados e resultados registrados; mudanças finais **não commitadas**.

## 7. Orientações para relatório de término ao usuário

Ao concluir, apresente em português claro:

- O que foi corrigido na V2 e o que foi construído na V3.
- Quais indicadores novos realmente funcionam e quais não puderam ser construídos.
- Como iniciar o Streamlit e como gerar City × Arsenal, com comandos exatos para este repositório.
- Resumo de testes com número de aprovados/falhas e comandos utilizados (não inventar resultados).
- Caminhos dos documentos, relatórios e gráficos criados.
- Limitações do dataset e próximos passos para eventual IA treinada.
- Confirmação factual de que **não fez commits/push**, baseada no registro de comandos/status; reporte qualquer impedimento ou exceção.

**Regra final:** construir uma ferramenta que ajuda a avaliar evidências, não uma “IA tática infalível”. Robustez, explicabilidade e confiança na proveniência dos dados são mais importantes que volume de funcionalidades.
