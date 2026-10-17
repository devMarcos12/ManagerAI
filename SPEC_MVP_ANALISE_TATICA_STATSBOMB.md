# SPEC — MVP de Sistema Inteligente de Apoio à Decisão Tática no Futebol

**Status:** especificação inicial para inspeção do repositório e planejamento técnico  
**Fonte:** documentação PI6 e EDA StatsBomb fornecidas pela equipe  
**Idioma do sistema/relatórios:** português brasileiro  
**Objetivo desta spec:** orientar o Codex a analisar o código e propor uma implementação consistente, sem inventar dados ou assumir que um modelo treinado já existe.

## 1. Contexto e visão do produto

Construir um sistema de apoio à comissão técnica para planejamento pré-jogo. O treinador informa sua equipe, o adversário e contexto da partida; o sistema consulta dados históricos locais da StatsBomb, descreve características táticas e fornece um **relatório fundamentado em indicadores observáveis**, com possíveis estratégias e, quando os dados permitirem, sugestões condicionais de formação e escalação.

O produto é **apoio à decisão**, não um sistema que garante vitória ou determina uma “tática ideal” comprovada causalmente.

### 1.1 Escopo confirmado

- Utilizar **somente competições, temporadas, equipes, jogadores e partidas disponíveis no dataset StatsBomb Open Data local**.
- O recorte já estudado é **Premier League 2015/2016**, com **380 partidas** e **20 clubes** no inventário da EDA.
- Considerar o projeto inicialmente **histórico**, sem consultar resultados atuais ou presumir disponibilidade de atletas na temporada presente.
- Não depender de API paga, dados ao vivo ou fontes externas para o fluxo principal do MVP.
- Utilizar a arquitetura híbrida descrita no projeto como **direção de design**: análise/inferência estruturada em Python + LLM para explicação textual. A adoção de fine-tuning permanece condicionada à viabilidade de dados, rótulos e avaliação.

### 1.2 Fora de escopo na primeira versão

- Jogos, jogadores, lesões, suspensões, escalações ou estatísticas atuais não existentes no conjunto histórico local.
- Previsão garantida de vitória, causalidade entre esquema tático e resultado, ou afirmações de que uma formação é objetivamente a melhor.
- Coleta/scraping de outras plataformas, mercado de transferências, integração com sistema de clubes e deployment em produção.
- Fine-tuning obrigatório antes de existir um baseline mensurável.

## 2. Base existente e evidências

A EDA fornecida cobre a Premier League 2015/16 e inclui:

1. Cobertura das partidas por clube (38 no recorte).
2. Frequência de tipos de eventos, como Pass, Ball Receipt, Carry, Pressure, Ball Recovery e Shot.
3. Localização e xG das finalizações.
4. Mapa de localização de eventos Pressure (**eventos de pressão não equivalem a pressões bem-sucedidas**).
5. Entradas no terço final por 90 minutos, com dispersão entre partidas.
6. Uso relativo dos corredores esquerdo, central e direito em uma janela pré-jogo.
7. Distribuição e variabilidade do xG favorável por partida em janelas pequenas.

A EDA propõe investigar Arsenal x Manchester City, sem afirmar causalidade ou já possuir um modelo de recomendação validado. Os gráficos existentes são descrições exploratórias e **não constituem labels supervisionados de “boa estratégia”**.

**Ação obrigatória do Codex:** verificar a estrutura, a cobertura efetiva e os campos dos arquivos existentes no repositório; não presumir que todas as temporadas disponham de events, lineups e dados 360 com a mesma completude.

## 3. Perfis de uso e casos de uso

**Usuário principal:** treinador ou membro da comissão técnica.

**Caso de uso central:** “Como poderíamos preparar o [meu time histórico] para enfrentar o [adversário histórico] em [data de referência]?”

Fluxo:

1. Selecionar competição/temporada contemplada pelo dataset.
2. Selecionar time analisado e adversário compatíveis com o recorte escolhido.
3. Informar contexto adicional (ver campos de entrada).
4. Determinar uma **data de corte** ou jogo-alvo histórico para que apenas observações anteriores sejam usadas.
5. Calcular perfis e comparar forças, fragilidades e incerteza.
6. Gerar hipóteses táticas baseadas em regras transparentes ou modelo validado.
7. Renderizar relatório com evidências, limitações e origem dos indicadores.

## 4. Contrato de entrada

### 4.1 Obrigatórios

- `competition_id` e `season_id` (ou chave canônica equivalente encontrada no dataset).
- `team_id` — equipe cuja comissão técnica consulta o sistema.
- `opponent_id` — adversário diferente de `team_id`.
- `cutoff_date` **ou** `target_match_id` — ponto histórico até o qual os dados podem ser usados. O início da janela precisa preceder esse ponto.

### 4.2 Opcionais (propostos; não presentes de forma garantida na StatsBomb)

- `venue`: casa, fora, neutro, desconhecido.
- `match_context`: regular, clássico, eliminatório, decisivo, outro.
- `strategic_objective`: equilibrado, pressionar alto, proteger vantagem, buscar gol, outro.
- `unavailable_player_ids`: jogadores ausentes informados manualmente.
- `notes`: condições/contexto livre informado pelo treinador.
- `recent_matches_window`: quantidade de partidas anteriores consideradas (padrão sugerido: até 10, configurável).

**Atenção:** clássico, importância do jogo, lesões/suspensões e mando real devem ser tratados como entradas fornecidas pelo treinador ou campos explicitamente confirmados, nunca inferidos sem evidência. `match_context` e `strategic_objective` são fatores de contextualização, não variáveis comprovadas causalmente.

### 4.3 Regras de validação

- IDs selecionados devem existir no inventário local.
- Equipes precisam corresponder ao universo histórico analisável; rejeitar ou explicar confrontos incompatíveis.
- Não usar jogo futuro em relação ao `cutoff_date`; para análise pré-jogo, excluir o próprio `target_match_id` do cálculo de features.
- Se a janela possuir poucos jogos, sinalizar amostra insuficiente em vez de produzir confiança falsa.
- Não sugerir atleta fora do elenco histórico elegível ou marcado como indisponível.

## 5. Contrato de saída — relatório estruturado

O motor analítico deve fornecer um objeto estruturado serializável (JSON ou esquema tipado), com os campos conceituais:

```json
{
  "metadata": {
    "competition": "Premier League",
    "season": "2015/2016",
    "team": "Manchester City",
    "opponent": "Arsenal",
    "cutoff_date": "DATA_HISTORICA_EXEMPLO",
    "matches_analyzed_team": 0,
    "matches_analyzed_opponent": 0
  },
  "team_profile": {},
  "opponent_profile": {},
  "comparison": [],
  "key_findings": [],
  "tactical_hypotheses": [
    {
      "recommendation": "Descrição hipotética, somente quando houver suporte nos dados",
      "evidence_metrics": [],
      "limitations": [],
      "confidence_level": "insuficiente"
    }
  ],
  "formation_options": [],
  "lineup_options": [],
  "data_gaps": [],
  "methodology": {}
}
```

Esse JSON é **ilustrativo**, não um output real nem uma especificação final de API. O Codex deverá tipar os objetos e propor um schema específico conforme a estrutura do repositório.

### 5.1 Seções do relatório legível

1. Identificação do confronto e período observado.
2. Diagnóstico do adversário: perfil ofensivo, defensivo, zonas de ação, progressão e pressão.
3. Comparativo com o próprio time, normalizado por jogo ou por 90 minutos quando apropriado.
4. Forças e vulnerabilidades **observadas**, associadas a métricas.
5. Duas ou três **hipóteses táticas condicionais**: o que fazer, por que os dados sugerem investigar, riscos e pré-condições.
6. Formação/escalação **somente se houver dados suficientes para justificar**; caso contrário, registrar “não suportado pelos dados atuais”.
7. Fontes, período, tamanho da amostra, qualidade da evidência e ressalvas.

A LLM **não deve criar números, lesões, escalações, resultados, atletas ou fatos** ausentes do JSON calculado. Deve preservar a distinção entre fatos, interpretações e hipóteses.

## 6. Engenharia de dados e features

### 6.1 Inventário e qualidade

- Descobrir diretórios/arquivos e formatos reais (`competitions`, `matches`, `events`, `lineups` e, se houver, `three-sixty`).
- Validar cobertura por competição, temporada e partida.
- Detectar duplicações, campos ausentes, coordenadas inválidas e referência inconsistente de IDs.
- Documentar significado de cada métrica, unidade, janela e denominador.
- Não assumir disponibilidade de 360, posicionamento integral sem bola ou tracking.

### 6.2 Features candidatas

- Finalizações, xG por chute, xG a favor e contra (quando calculável e atribuível corretamente).
- Localização das finalizações e distribuição espacial de eventos.
- Passes e acerto de passes, com e sem pressão **quando o esquema e a cobertura permitirem**.
- Entradas no terço final por 90 minutos (definir claramente o que conta como entrada).
- Distribuição relativa de ações por corredor.
- Eventos Pressure por região do campo, sem equipará-los automaticamente a recuperação ou eficácia.
- Posses/recuperações e sequências, **apenas após validar regras de atribuição**.
- Variação jogo a jogo, mediana e tamanho amostral; evitar concluir de médias instáveis.

**Critério metodológico:** distinguir medição de evento, proxy e interpretação tática. Padronizar orientação de ataque/defesa e o sistema de coordenadas StatsBomb antes de comparar mapas.

### 6.3 Prevenção de vazamento temporal

- Para cada jogo-alvo, usar exclusivamente partidas e informações anteriores ao início do jogo.
- Separar treinamento, validação e teste por tempo (e, se necessário, por partidas/equipes para investigar generalização).
- Em features móveis, não incluir o resultado do alvo ou estatísticas posteriores ao corte.
- Testar casos de limite: primeira partida da temporada, equipe com poucos jogos anteriores e confronto sem histórico recente.

## 7. Camadas e arquitetura recomendada

Separar componentes com contratos testáveis:

1. `data_inventory` — descobre cobertura e metadados locais.
2. `data_loader` — lê eventos, partidas e escalações sem alterar arquivos brutos.
3. `feature_engineering` — gera indicadores por partida/equipe e janelas históricas.
4. `tactical_analysis` — constrói perfis e comparativos reproduzíveis.
5. `recommendation_engine` — inicialmente hipóteses baseadas em regras documentadas; depois, eventualmente, modelo aprendido.
6. `report_schema` — contrato estruturado com métricas, proveniência e lacunas.
7. `llm_reporter` — explica somente dados recebidos; preferir template determinístico como fallback quando não houver API/chave.
8. `app_interface` — interface de demonstração, CLI ou API de acordo com a estrutura existente e prioridades do repositório.

**Não criar uma stack do zero sem antes inspecionar e respeitar as convenções e dependências do repositório.**

## 8. Estratégia de modelagem e avaliação

### 8.1 Baseline obrigatório antes de fine-tuning

Entregar primeiro um pipeline **determinístico e auditável** que compare equipes e gere hipóteses com evidências rastreáveis.

### 8.2 Decisão sobre aprendizado de máquina

Antes de selecionar modelo pré-treinado ou fazer fine-tuning, responder documentalmente:

- Qual é a variável-alvo, exatamente?
- Como obter os rótulos sem inferir “estratégia ideal” apenas do resultado da partida?
- Qual é o número de exemplos válidos e independentes?
- Que baseline simples é apropriado (heurística, regressão, classificação etc.)?
- Como medir melhora real versus o baseline e evitar vazamento?
- Existe modelo pré-treinado esportivo **verificado**, relevante e licenciado para a tarefa?

Se não houver rótulos confiáveis, **não simular treinamento nem declarar acurácia de recomendação**; priorizar analítica descritiva, recuperação de evidências e recomendações condicionais.

### 8.3 Critérios de avaliação

- Qualidade de dados: cobertura, taxas de nulos e consistência de métricas.
- Reprodutibilidade: mesmas entradas + mesma versão dos dados = mesmas features.
- Temporalidade: zero vazamentos em testes automatizados.
- Fundamentação: toda hipótese tem métrica ou evidência rastreável.
- Fidelidade textual: relatório não inventa números ou participantes.
- Se houver predição com rótulos válidos: métricas adequadas ao alvo (não usar acurácia genericamente quando não aplicável), avaliação temporal e comparação com baseline.

## 9. Entregas em etapas

### Etapa 0 — Auditoria do repositório

- Identificar linguagem, estrutura, scripts existentes, dependências, testes e localização dos dados.
- Mapear o que já está implementado versus planejado.
- Produzir resumo de riscos, perguntas abertas e plano incremental.
- **Não modificar código nessa etapa sem autorização explícita.**

### Etapa 1 — Inventário e recorte

- Confirmar quantos jogos, clubes e temporadas estão efetivamente disponíveis.
- Adotar Premier League 2015/16 como recorte inicial reproduzível.
- Gerar dicionário de dados e checagens de qualidade.

### Etapa 2 — Features e análises

- Implementar cálculos com janela temporal e testes.
- Reproduzir métricas e gráficos da EDA e documentar diferenças.
- Gerar perfis comparáveis para dois times.

### Etapa 3 — Motor de hipóteses e relatório

- Definir regras explícitas para sugestões condicionais.
- Emitir relatório JSON com evidências e lacunas.
- Criar relatório de apresentação via template ou LLM, sem invenções.

### Etapa 4 — Avaliação e decisão de fine-tuning

- Avaliar qualidade, coerência e limitações do pipeline.
- Formalizar um experimento de ML somente se houver tarefa-alvo e rótulos defensáveis.
- Se validado, executar experimento pequeno com baseline, split temporal e documentação.

### Etapa 5 — Demonstração

- Interface mínima para seleção de equipes/corte/contexto.
- Relatório completo para ao menos um cenário histórico reproduzível.
- Documentação de execução local e limitações.

## 10. Critérios de aceite do MVP

- [ ] O sistema lista somente confrontos/equipes suportados pelos dados locais.
- [ ] Recebe seleção de dois clubes e referência histórica de jogo/data.
- [ ] Usa apenas dados anteriores ao corte.
- [ ] Gera indicadores ofensivos/defensivos comparáveis, com período e amostra.
- [ ] Mostra ao menos dois achados com métricas rastreáveis.
- [ ] Produz hipóteses táticas **condicionais**, não afirmações causais.
- [ ] Retorna lacunas explicitamente em vez de fabricar dados.
- [ ] Não inventa escalação ou atletas ausentes do dataset.
- [ ] Gera relatório estruturado e apresentação legível em português.
- [ ] Testes automatizados cobrem temporalidade e integridade dos dados.
- [ ] Um caso de uso histórico pode ser reproduzido localmente.
- [ ] Documenta o que foi ou não possível inferir do dataset.

## 11. Instruções operacionais ao Codex

**Primeira execução: auditoria e plano; não implementar automaticamente.**

1. Leia este arquivo integralmente.
2. Inspecione a estrutura do repositório e identifique scripts, notebooks, dados, configurações, testes e README.
3. Compare o repositório real com as seções da spec. Não presuma que arquivos/nomes de módulos aqui sugeridos já existem.
4. Entregue uma análise de lacunas (`implementado`, `parcial`, `não iniciado`), riscos e dependências.
5. Proponha um plano de implementação com arquivos a criar/editar, ordem de execução e verificações.
6. Faça perguntas apenas quando impedirem uma decisão importante; caso contrário, liste premissas explícitas.
7. **Não altere nenhum arquivo de código nem instale dependências nesta primeira passada.** Solicite autorização antes da implementação.
8. Após autorização, implemente incrementalmente, priorizando testes e documentação; preserve dados brutos.
9. Se houver conflito entre a spec e o código/dados reais, relate o conflito antes de decidir.

## 12. Pendências a decidir com a equipe

1. Recorte: somente Premier League 2015/16 na demo inicial ou mais competições com cobertura suficiente?
2. Data de referência: sempre jogo histórico específico ou também corte por data livre?
3. Entrega inicial: CLI, endpoint de API, notebook reprodutível ou interface web?
4. Formação/escalação: condição para incluí-las no MVP e evidências exigidas.
5. Acesso à LLM: provedor, restrições de custo, privacidade e fallback determinístico.
6. Critério de sucesso de recomendação: avaliação por especialistas, aderência às evidências, ou alvo preditivo formalmente especificado?

---

**Princípio norteador:** demonstrar um sistema útil, auditável e cientificamente defensável com os dados que realmente existem, antes de adicionar complexidade de modelagem.
