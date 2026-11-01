# ManagerAI — pendências e validação

**Elegibilidade por família — 01/11/2026:** diagnóstico implementado e executado na La Liga 2015/16; contagens históricas úteis separadas dos bloqueios espaciais e de exposição. 16 famílias/50 indicadores; regras e resultados no §23. Não houve certificação ou alteração da análise de produção.

**CORE-02 — 01/11/2026:** conteúdo integral da La Liga 2015/16 auditado; resultado reprovado sob as guardas atuais, sem certificação V3. Gate de snapshot completo permanece não verificado. Evidências, testes e distinção entre calendário e calculabilidade no §22.

**Entrega web 31/10/2026: frontend local implementado e integrado com API real; correções A1–A3 e evidências atuais no §21. Resultados e conclusões do §20 são históricos da etapa de IA; não foram reutilizados como testes desta execução. Validade esportiva e avaliação humana permanecem pendentes.**

Atualização de interface em 30/10/2026: mitigação da sobrecarga da prévia JSON V3 implementada e validada por AppTest; confirmação manual do travamento no navegador pendente (§19). Os status CORE não foram reavaliados naquela correção; a execução posterior de 31/10 está no §20.

**31/10: serviço/API 2.0.0 implementados; wheel atualizado instalado e conferido com `python -I`, 282 testes instalados com dados reais aprovados. Ollama real validado; ajuste LoRA real de explicação concluído como experimento, sem promoção. Motor tático aprendido e validação esportiva humana continuam ausentes. CORE-02 não certificou novas temporadas. Estado e rastreabilidade CORE-03…16 no §20.**

Registro histórico de 25/10/2026 (superado no que se refere a API/LLM/ajuste pelo §20; frontend no §21). Estado, contratos e comandos: [CURRENT_VERSION.md](CURRENT_VERSION.md). Regras: [AGENTS.md](../AGENTS.md). **V4.1, V4.2 e V4.3-A/B concluídas; dataset e regressões offline validados (§14).** Há OLS/Ridge experimentalmente ajustadas para previsão de chutes. Naquele registro ainda não havia API/LLM ou ajuste de explicação; o serviço e a pesquisa posteriores estão no §20. Motor tático aprendido e recomendações individuais continuam não implementados. V4.3-C concluída como estudo exploratório; CORE-00 no §16.

## 1. Estado conferido e prioridades

Na V4.1, este documento foi corrigido a partir do estado antigo da Fase 1 para refletir a limpeza já realizada, sem repetir exclusões. HEAD de entrada V4.1 e V4.2: `09b73b75c74266347a2f924a67dc95d7c803720f` (`fix: remove unused files`). A V4.2 começou com alterações locais da V4.1, preservadas; status inicial/final e mudanças exclusivas desta fase estão no §13. As referências `13c50e5` dos backups são históricas.

| ID | Status | Dependência / critério de conclusão |
|---|---|---|
| DOC-01 / DOC-02 | CONCLUÍDOS | Três documentos operacionais; README aponta a estado/pendências e demos finais. Conteúdo técnico consolidado em CURRENT_VERSION |
| CLEAN-01 / CLEAN-02 | FASES 1–3 CONCLUÍDAS, REGISTRO HISTÓRICO | Grupo A: 29 arquivos e dois diretórios vazios; B1–B3: 37 arquivos e dois requirements paralelos; C: 29 históricos preservados externamente e ausentes do checkout. Nenhuma remoção na V4.1 |
| ENV-01 | INSTALAÇÃO LIMPA VALIDADA NA CORE-00 | Pyproject canônico e requirements `.[v3]`, extras `ui/v3/dev/experiments/eda`; dois ambientes novos. Lock completo de transitivas continua decisão separada |
| HIST-01 | BACKUP LOCAL PRESENTE E HASH CONFERIDO | Dois pacotes permanentes, §2. Redundância fora da máquina e acesso pela equipe exigem decisão |
| V4.1 | CONCLUÍDA | Contratos, baseline adaptado e seleção explícita; validação histórica §6, revalidação V4.2 §13. Sem modelo treinado |
| V4.2 | CONCLUÍDA | Inventário, amostragem, quatro tarefas, atributos/alvos, modelos/fine-tuning e protocolo documentados; 153 testes e 16 comparações, §13. Gates V4.3 no §12 |
| V4.3-A/B | CONCLUÍDA | 330 exemplos/50 excluídos; baselines, OLS/Ridge e avaliação 198/65/67 reproduzidos; 191 testes e 16 comparações aprovados; §14 |
| V4.3-C | CONCLUÍDA | Estudo exploratório, reprodução e 228 testes históricos no §15; pré-requisitos versionados na CORE-00 |
| CORE-00 | BASE CONSOLIDADA E VALIDADA | Instalação limpa e CI aprovadas; integração rastreada pelo PR #10, §16 |
| CORE-01 / DATA-01 | WHEEL E DADOS LINUX VALIDADOS EM 31/10 | Pacote instalado atualizado e contrato empacotado conferidos; 282 testes reais aprovados no §20. Finalidade/distribuição e responsável nominal continuam decisão humana; §17 histórico |
| ART-01 | IMPLEMENTADO NA C, CONFERIDO NA CORE-00 | `open-data/` e `outputs/runs/` ignorados; fixtures, exemplos finais e verificadores preservados/rastreados |
| TEAM-01 / B4 | DECISÃO HUMANA | Responsáveis por contratos, dados/indicadores, UI e avaliação; confirmar uso compartilhado de `.vscode/settings.json` |
| REF-01 | SUFICIÊNCIA CONSOLIDADA | Constantes e predicado compartilhados; regras V3 deixam de importar apresentação para suficiência. Helpers de formatação ainda reutilizados; sem alteração de fórmulas/contratos |
| V3-01 / CORE-02 | PARCIAL: CONTEÚDO LA LIGA AUDITADO, NÃO CERTIFICADO | 380 jogos/1.295.354 eventos; seis partidas com falhas, orientação inconclusiva e completude integral H5/H10 zero. Gate CORE-01 completo não verificado nesta execução; §22 |
| PERF-01 | MEDIÇÕES INICIAIS E LIMITES IMPLEMENTADOS | Duração/payload reais e limites de API no §20; prévia JSON da UI mitigada. Perfil completo de releitura e revisão visual continuam pendentes |
| EVAL-01 | PENDENTE | Revisão especializada/vídeo/treino com correção, rastreabilidade, plausibilidade, compreensão, riscos e utilidade separados |
| AI-01 | EXPERIMENTO QUANTITATIVO A/B IMPLEMENTADO | OLS/Ridge treinadas offline para chutes; sem motor tático aprendido no runtime, validação de estratégia ou integração V3/V4.1. Decisão C no §14 |
| AI-02 | AJUSTE REAL DE EXPLICAÇÃO EXPERIMENTAL | SmolLM2-135M + LoRA, 192 passos, avaliação sintética e recarregamento reais, §20. Decisão tática aprendida bloqueada por ausência de rótulos revisados |
| AI-03 | INFERÊNCIA LOCAL REAL VALIDADA | Qwen2.5 1.5B via Ollama; seleção restrita de afirmações autorizadas; sem provedor pago. Sem prosa livre ou avaliação humana de utilidade |
| AI-04 | NÃO IMPLEMENTADO, SEM ESCOPO APROVADO | Escalação/formação ideal exige disponibilidade atual, tarefa e validação próprias; histórico de atletas não basta |

`PENDENTE` não autoriza execução. Os módulos ativos V3, 14 módulos anteriores de testes, fixture congelada, dois exemplos finais, scripts/verificadores independentes, brutos, licenças, EDA e ambiente funcional continuam preservados. V4.1 acrescenta um módulo de testes e dois módulos de infraestrutura.

## 2. Histórico e recuperação

Histórico fora do contexto operacional diário: `/home/marcos-junior/ManagerAI-backups/`, destino aprovado na Fase 3. Conferência nesta tarefa: SHA-256 dos dois pacotes coincidente com seus arquivos laterais e presença dos 29 caminhos C em cada manifesto; todos esses originais estão ausentes do checkout. Extração integral testada na Fase 3, não repetida como resultado novo da V4.1.

| Pacote | SHA-256 |
|---|---|
| `ManagerAI-history-13c50e5-20261017.tar.gz` | `48a57a602895eba21526ead7a53495520263989881aa19cdfaa082d3de9cf236` |
| `ManagerAI-history-phase3-13c50e5-20261017.tar.gz` | `8930e55539ed6510ecb43a6e73ae6db02086086609bfcb7c203886ce50e9efd1` |

O primeiro preserva C antes da migração de links, snapshot original EDA e PENDING anterior à Fase 2; o segundo preserva exatamente os 29 C antes da retirada. Ambos incluem `MANIFEST.json`, `SHA256SUMS`, `RECOVERY.md` e referência `13c50e5cc7e54e6f45487b89cdbe3994d621587f`. Três documentos diferem apenas em destinos de links migrados; conservar ambos. Specs, changelogs, auditoria e logs datados são referências históricas, sem autoridade operacional.

Recuperação seletiva: conferir o arquivo lateral `.tar.gz.sha256` com `sha256sum -c` no diretório do backup; listar membros; criar diretório NOVO com `mktemp -d /tmp/managerai-recovery-XXXXXXXX`; extrair nele com `tar --keep-old-files --no-same-owner -xzf /caminho/absoluto/pacote.tar.gz -C /pasta/nova`; nessa pasta executar `sha256sum -c SHA256SUMS` e conferir manifesto/commit. Não extrair sobre o checkout nem executar instruções antigas automaticamente. Comparar e restaurar somente caminhos autorizados, sem sobrescrever trabalho existente. Não usar reset/clean.

O snapshot de dependências EDA continua em `docs/history/requirements-eda-20261017.txt`, SHA-256 `cda85b3a30d5094ec44bc285b580cecb195047f9fa7ff43bee6994a811e9453b`; não é instalação operacional. Dados, clone e EDA completa não estão nesses pacotes.

## 3. Decisões e limites da V4.1

- Integração depois do relatório: `pipeline.analyze` mantém API/padrão; `tactical_engines` não recebe raiz de dados nem recalcula features/regras. Não houve integração CLI/Streamlit, por desnecessária para o contrato Python.
- `TacticalEngineInput` é snapshot imutável dos perfis/indicadores calculados, contexto declarado e proveniência. Exclui hipóteses baseline, eventos brutos, roster e sequências extensas. O `Protocol` aceita motores futuros explicitamente registrados; o único incluído é `deterministic`.
- `DeterministicEngine` copia resultados reais das duas camadas, sem sugerir capacidade aprendida. Versão 4.1.0 é do adaptador; fórmulas/regras legadas 1.0.0 e V3 3.0.0 permanecem na proveniência. Saída separada; schemas 1.0.0/1.1.0 e valores originais preservados.
- Abstenção reutiliza `coverage.report_sufficiency`. Algumas hipóteses brutas legadas podem existir sem suficiência central; o sidecar se abstém e mantém o relatório original intacto. Um motor futuro também pode abster com suficiência central se suas exigências adicionais falharem.
- `compare_engines` valida seleção completa antes de executar motores, compartilha o snapshot e confere motor/versão, fingerprint, proveniência e referências. Não calcula ranking, qualidade esportiva, probabilidades ou superioridade. Motor desconhecido gera erro explícito; erros reais não viram fallback ou hipótese vazia.
- A validação confere datas/IDs/amostras/fontes do relatório recebido. Não reabre brutos para certificar todas as declarações, disponibilidade original das revisões nem ausência de vazamento no pré-treino externo. Escalações de jogos sem eventos podem ser fontes legítimas. Contratos não isolam plugins Python maliciosos nem provam que uma justificativa textual é verdadeira: fidelidade semântica exige avaliação.
- Contrato atual é para análise pré-jogo sobre indicadores agregados. Um futuro modelo sequencial pode exigir contrato específico de eventos/janelas e transformação separada; não incluir eventos do alvo nem ampliar silenciosamente o contrato atual. A decisão fica para a tarefa escolhida na V4.2.

## 4. Modelos candidatos e fine-tuning — comparação atualizada V4.2

Pesquisa primária consultada em 17/10/2026. O modelo deve seguir a tarefa: contagem futura, representação ou explicação são problemas diferentes. Na V4.2 nenhum candidato foi instalado/treinado/otimizado. As regressões lineares posteriores e seus baselines reais estão no §14; as demais famílias continuam não implementadas. Tamanhos, licenças e suporte abaixo são declarações das fontes, não benchmarks ManagerAI; fixar pacote/checkpoint/commit/hash antes de experimentar. Código, pesos e dados têm permissões separadas.

| Família | Entrada, alvos, dados e evidência de domínio | Pesos / adaptação / interpretabilidade | Recursos, reprodução e parecer |
|---|---|---|---|
| Regressão regularizada; regressão de contagem Poisson | Poucos indicadores anteriores → finalizações futuras. Alvo observável, sem mínimo universal de amostra; até 330 jogos candidatos são um estudo pequeno, não comprovação de poder estatístico | Ajuste supervisionado desde o início, sem pesos pré-treinados necessários. Coeficientes auditáveis, sem interpretação causal; verificar pressupostos e dispersão | CPU é candidata razoável para tabela pequena, ainda não medida; normalização e regularização só no treino/validação. **Viável para experimento** sob gates. [Modelos lineares](https://scikit-learn.org/stable/modules/linear_model.html) |
| Random Forest | Mesma tabela/alvo; não linearidades/interações; não exige rótulo de tática ideal para prever contagem | Sem checkpoint esportivo necessário. Ajuste supervisionado; importâncias não demonstram causalidade | CPU/memória crescem com árvores/profundidade; seed e orçamento fixos, risco de sobreajuste com 198 jogos de treino ilustrativos. **Viável para experimento**, candidato secundário. [Ensembles](https://scikit-learn.org/stable/modules/ensemble.html) |
| Gradient Boosting | Mesma tarefa tabular, perda compatível com regressão/contagem | Sem pré-treino obrigatório; relações não lineares, explicações indiretas; não declarar vantagem sem teste comum | CPU possível em configuração pequena; mais escolhas de hiperparâmetros que regressão, tuning restrito ao treino/validação. **Viável para experimento**, secundário. [Ensembles](https://scikit-learn.org/stable/modules/ensemble.html) |
| MLP | Tabela padronizada → alvo supervisionado; amostra local pequena torna estabilidade uma questão empírica | Nenhum peso esportivo compatível comprovado. Treino do zero; interpretação menor que regressão; controlar inicialização/regularização | Implementação scikit-learn usa CPU; GPU exigiria outro framework. Não pressupor milhares de eventos como milhares de exemplos independentes. **Viável mediante condições**, baixa prioridade. [MLP](https://scikit-learn.org/stable/modules/neural_networks_supervised.html) |
| RNN / Transformer de eventos | Sequências ordenadas → próximo tipo/tempo/local ou representação; essa tarefa não é previsão pré-jogo automaticamente | Precisa tokenização, máscara, segmentos, orientação/unidades e supervisão; pesos genéricos não asseguram compatibilidade. Treino/fine-tuning dependem de arquitetura/corpus específicos | CPU/GPU/RAM dependem do modelo, comprimento e batch; nenhum requisito universal medido. Grupos continuam partidas. **Viável mediante condições**, com contrato de eventos separado |
| TabPFN | Tabela derivada dos snapshots → regressão/classificação rotulada. Pesos reais, sem evidência verificada de recomendação tática pronta | Adaptação em contexto não é fine-tuning; atualização de pesos existe. Código Apache-2.0; pesos v2 têm licença própria/atribuição, versões 2.5, 2.6, 3 e 3.5 consultadas têm restrições não comerciais; default consultado já é 3.5: não usar default mutável | GPU recomendada para ajuste; custo depende da versão/tabela. Validar sem ajuste antes de fine-tuning e passar validação cronológica explícita, não split automático de 10%. **Viável mediante condições**; ganho local ainda não demonstrado. [Projeto](https://github.com/PriorLabs/TabPFN), [fine-tuning](https://docs.priorlabs.ai/capabilities/fine-tuning), [licença v2 regressor](https://huggingface.co/Prior-Labs/TabPFN-v2-reg/blob/main/LICENSE.txt) |
| Chronos-2 | Séries numéricas por equipe, 120M parâmetros; covariáveis e séries multivariadas suportadas. Não recebe eventos JSON diretamente; futebol/adversário/calendário irregular precisam de representação e validação próprias | Pesos `amazon/chronos-2` Apache-2.0; API oferece ajuste `full` ou `lora` e `validation_inputs`. Nenhuma evidência de adequação ao futebol foi comprovada nesta consulta | Inferência CPU/GPU; treinamento depende de memória/contexto. Conferir dependências para não trocar LoRA por ajuste completo silenciosamente. **Viável mediante condições**; até 38 jogos/equipe é série curta. [Model card](https://huggingface.co/amazon/chronos-2), [API oficial](https://github.com/amazon-science/chronos-forecasting/blob/main/src/chronos/chronos2/pipeline.py) |
| TimesFM | Previsão de séries numéricas; indicadores por jogo exigem tratar intervalos irregulares e adversário. Benchmarks genéricos não demonstram adequação esportiva | Pesos 2.5 de 200M disponíveis Apache-2.0; exemplos oficiais de LoRA. Código e pesos têm licenças distintas: pesos 3.0 são não comerciais/não produção, embora código seja Apache | Custo CPU/GPU depende da versão/contexto, não medido. Fixar checkpoint elegível. **Viável mediante condições**, sem escolha antecipada. [Projeto/licenças](https://github.com/google-research/timesfm), [pesos 2.5](https://huggingface.co/google/timesfm-2.5-200m-pytorch), [adaptação](https://github.com/google-research/timesfm/tree/master/timesfm-forecasting/examples/finetuning) |
| OpenSTARLab/Event | Seq2Event/NMSTPP/LEM/FMS; benchmark dos autores inclui StatsBomb para próximo evento, tempo e posição | Código Apache-2.0/PyTorch. Pesos pré-treinados aparecem no roadmap; checkpoint utilizável/corpus/licença dos pesos **não comprovados**, portanto não afirmar fine-tuning pronto | Precisa transformação e tarefa de sequência; hardware e volume útil ainda a medir. Treino **condicionado**; fine-tuning de peso esportivo **ainda não demonstrado**. [Autores](https://github.com/open-starlab/Event) |
| Football2Vec | Representações Action2Vec/Player2Vec anunciadas, posição/tipo de ações; similaridade não é decisão ótima | Código Apache-2.0, pacote externo pré-treinado anunciado; integridade/licença dos pesos/corpus/datas não verificados por download | Pode ser estudado como representação sob tarefa/avaliação próprias. **Ainda não demonstrada** a adaptação utilizável neste projeto. [Autores](https://github.com/ofirmg/football2vec) |
| TacticAI | Evidência científica de apoio a escanteios, usando posição/velocidade de todos os jogadores e avaliação especializada | Não foi comprovado checkpoint aberto pronto/licença de pesos para ManagerAI; artigo não equivale a modelo disponível. Frames 360 locais não substituem tracking sincronizado/velocidade completos | Reprodução na representação exigida **inviável com os dados disponíveis**; não generalizar o resultado do artigo para nossa tarefa. [Artigo](https://www.nature.com/articles/s41467-024-45965-x), [autores](https://deepmind.google/blog/tacticai-ai-assistant-for-football-tactics/) |
| LLM explicadora / SFT ou LoRA | Relatório estruturado → explicação fiel. Precisa pares entrada/saída revisados e avaliação humana; não há corpus supervisionado validado do projeto | Exemplo verificável de pesos: Qwen2.5-7B-Instruct Apache-2.0; SFT/PEFT possíveis. Ajustar texto/apresentação não treina um modelo quantitativo nem comprova raciocínio/decisão tática ideal | Bilhões de parâmetros acrescentam frameworks/memória/custo. **Viável mediante condições** para explicação; estratégia ideal **ainda não demonstrada**. [Checkpoint/licença](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct), [SFT/PEFT](https://huggingface.co/docs/trl/en/sft_trainer) |

As implementações scikit-learn citadas têm licença BSD-3-Clause ([projeto](https://github.com/scikit-learn/scikit-learn)); isso não licencia os dados StatsBomb. VAEP/xT são outras referências de valoração de ações com conversão StatsBomb→SPADL, não substitutos diretos da tarefa pré-jogo escolhida: VAEP usa horizonte de dez ações, xT estima valor espacial. Não comparar seus scores com MAE de finalizações. [VAEP](https://socceraction.readthedocs.io/en/latest/documentation/valuing_actions/vaep.html), [xT](https://socceraction.readthedocs.io/en/stable/documentation/valuing_actions/xT.html).

Não existe limiar universal de quantidade de exemplos para essas famílias. Regressões/árvores pequenas podem ser investigadas com as centenas disponíveis; redes/candidatos de transferência exigem curvas de aprendizado e estabilidade, não promessa por volume bruto. O corpus temporal de um modelo pré-treinado precisa ser auditado: testá-lo em 2016 com pré-treino posterior pode contaminar a comparação, mesmo com features corretamente cortadas.

## 5. Escopo encerrado da V4.2 e continuidade

A V4.2 entrega inventário e diagnóstico limitado (§7), quatro tarefas comparadas (§8), atributos/corte/compatibilidade (§9), protocolo temporal (§10), respostas explícitas sobre fine-tuning (§11) e gates V4.3 (§12). Não construiu dataset de treino, novos contratos, features, scorer ou modelo. Esses itens passam a ser propostas condicionadas da V4.3, não trabalho concluído. Resultados atuais de validação no §13; os resultados V4.1 abaixo permanecem identificados como históricos.

## 6. Validação real da V4.1

Python 3.12.3 e opcionais existentes, sem instalações. Referência histórica: 135 testes anteriores; a V4.1 acrescenta **18 testes**, total real **153**.

| Execução final | Resultado |
|---|---|
| Suíte completa com integrações locais, UI e V3 | **153 aprovados**, 0 falhas, 0 erros, 0 pulos; código 0; 59,537 s |
| Modo biblioteca padrão, `python3 -B -S` | 153 descobertos: **128 aprovados**, 25 pulados por opcionais/integração local; 0 falhas/erros; código 0; 5,306 s |
| Comparações independentes | **16/16 aprovadas**, código 0; oito métricas em dois jogos |
| Compatibilidade real do adaptador | Fixture schema 1.0.0 e dois exemplos schema 1.1.0 adaptados sem releitura/cálculo; relatórios byte a byte preservados; City emite hipóteses reais e Real se abstém |
| Sintaxe e links locais | 49 Python com AST válida; 16 destinos Markdown locais existentes; zero links quebrados |
| Integridade | Nenhuma remoção; somente três documentos editados e três arquivos Python criados. Todos os 26 módulos anteriores, 14 módulos anteriores de testes, dependências, README, fixture, demos e artefatos mantidos têm hashes do início desta tarefa |
| Brutos/EDA | 8.980 arquivos do clone fora de `.git` (8.977 em `open-data/data`) coincidem com os hashes integrais guardados na Fase 3; 108 EDA coincidem com o baseline inicial V4.1; clone limpo na revisão `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb` |

Comandos finais:

```bash
MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg venv/bin/python -B -m unittest discover -s tests -v
PYTHONPATH=src python3 -B -S -m unittest discover -s tests -q
PYTHONPATH=src venv/bin/python -B outputs/v22_v3_validation/check_metrics.py
```

Na suíte completa, `TMPDIR`, `MPLCONFIGDIR` e caches XDG ficaram em temporários exclusivos `/tmp/managerai-v41-*`. AppTest exibiu avisos conhecidos `missing ScriptRunContext`, sem falha. Não houve teste manual de navegador nem avaliação esportiva ou de modelo treinado. Não se executaram geradores EDA, treinamento ou download de pesos.

Durante desenvolvimento, a primeira suíte completa encontrou dois erros de subcasos no teste novo de leitura de relatórios: a reconstrução da fixture não convertia dicionários de hipóteses para `TacticalHypothesis`. O carregador do teste foi corrigido; a repetição final acima passou. Os testes iniciais também identificaram que a fixture compartilhada não contém passes do adversário; o cenário novo acrescenta esse passe sintético explicitamente, sem mudar fixtures compartilhadas nem artefatos reais. A revisão independente acrescentou validações de perfil incompleto, tipos de estatísticas, alias de caminhos e sequências de lacunas. Não foram alteradas fórmulas para fazer os testes passarem.

Arquivos criados: `src/managerai/tactical_engine_schema.py`, `src/managerai/tactical_engines.py`, `tests/test_tactical_engines.py`. Editados: `AGENTS.md`, `docs/CURRENT_VERSION.md`, `docs/PENDING.md`. Nenhum pacote instalado, código legado alterado ou arquivo removido.

Evidências temporárias em `/tmp/managerai-v41-qx7c_hkb/`: baseline/status inicial, hashes, `after_tests.log`, `after_summary.json`, `after_metrics.json`, `final_integrity.json` e logs da primeira execução. O PENDING anterior à correção está em `PENDING-before-v41.md` e no commit de entrada. Isso não cria outro documento operacional.

HEAD principal permanece `09b73b75c74266347a2f924a67dc95d7c803720f`; `git diff --check` sem problemas. `git status --short` final:

```text
 M AGENTS.md
 M docs/CURRENT_VERSION.md
 M docs/PENDING.md
?? open-data/
?? src/managerai/tactical_engine_schema.py
?? src/managerai/tactical_engines.py
?? tests/test_tactical_engines.py
```

`open-data/` já era não rastreado no início. Não houve commit, push, integração externa, alteração de histórico ou início da V4.2.

## 7. Inventário e diagnóstico V4.2 — evidências locais

### 7.1 Método e quatro níveis de cobertura

Inventário por `data_inventory.inventory(LocalData(...))`: somente `competitions.json`, os 80 calendários `matches/{competition}/{season}.json`, existência de eventos/escalações/360 e nomes dos arquivos para órfãos. Não abriu todos os eventos nem carregou os 16 GB. `load_season` validou metadados/IDs/equipes/datas; isso não valida os conteúdos dos arquivos referenciados.

- **Presença:** 3.961 partidas catalogadas, 24 competições e 80 pares, datas entre 24/06/1958 e 27/07/2025. Eventos e escalações presentes em 3.961/3.961; 360 em 426/3.961 (10,75%). Há 4.235 arquivos de eventos e 4.235 de escalações, incluindo 274 IDs não vinculados ao catálogo em cada conjunto; não entram automaticamente. Dos 80 pares, 67 são masculinos, 13 femininos e um juvenil. Não somar isso como população homogênea.
- **Integridade estrutural:** confirmada nos calendários e em 12 partidas amostradas; não em todos os 4.235 JSONs de eventos. EDA e auditorias anteriores têm escopos próprios e não são nova validação integral.
- **Cobertura funcional:** o núcleo interpreta eventos e calcula 21 indicadores, a V3 acrescenta 26 e três métricas de sequência somente nos recortes autorizados `(2,27)` e `(11,90)`. Presença 360 não implementa análise 360. Fora desses pares, nenhuma certificação V3 foi concedida.
- **Adequação científica:** calendário contínuo, alvos/rótulos, disponibilidade temporal, independência e divisão precisam ser adequados à tarefa. 2.291 partidas têm, apenas pelo calendário/presença de eventos, cinco anteriores de ambas as equipes dentro do próprio par; **não** são um pool validado de treino. O total cobre domínios e versões diferentes.

### 7.2 Disponibilidade por competição/temporada

Fonte: `open-data/data/competitions.json` e `open-data/data/matches/{ID competição}/{ID temporada}.json`. Todas as linhas abaixo têm eventos/escalações presentes em N/N. Distribuição por equipe é mínimo/mediana/máximo de partidas **daquele par**, não da carreira. H5 = jogos-alvo com pelo menos cinco anteriores ao dia do alvo para ambas as equipes, sem misturar temporadas, por metadados/presença apenas; não garante suficiência de cada indicador.

| Competição | Temporada | IDs | N partidas | N equipes | Jogos/equipe min/med/max | 360 | H5 |
|---|---|---|---:|---:|---|---:|---:|
| 1. Bundesliga | 2023/2024 | 9/281 | 34 | 18 | 2/2/34 | 34 | 0 |
| 1. Bundesliga | 2015/2016 | 9/27 | 34 | 18 | 2/2/34 | 0 | 0 |
| African Cup of Nations | 2023 | 1267/107 | 52 | 24 | 3/4/7 | 1 | 4 |
| Champions League | 2018/2019 | 16/4 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2017/2018 | 16/1 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2016/2017 | 16/2 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2015/2016 | 16/27 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2014/2015 | 16/26 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2013/2014 | 16/25 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2012/2013 | 16/24 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2011/2012 | 16/23 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2010/2011 | 16/22 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2009/2010 | 16/21 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2008/2009 | 16/41 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2006/2007 | 16/39 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2004/2005 | 16/37 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 2003/2004 | 16/44 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 1999/2000 | 16/76 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 1972/1973 | 16/277 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 1971/1972 | 16/71 | 1 | 2 | 1/1/1 | 0 | 0 |
| Champions League | 1970/1971 | 16/276 | 1 | 2 | 1/1/1 | 0 | 0 |
| Copa America | 2024 | 223/282 | 32 | 16 | 3/3.5/6 | 0 | 2 |
| Copa del Rey | 1983/1984 | 87/84 | 1 | 2 | 1/1/1 | 0 | 0 |
| Copa del Rey | 1982/1983 | 87/268 | 1 | 2 | 1/1/1 | 0 | 0 |
| Copa del Rey | 1977/1978 | 87/279 | 1 | 2 | 1/1/1 | 0 | 0 |
| FA Women's Super League | 2023/2024 | 37/281 | 132 | 12 | 22/22/22 | 0 | 102 |
| FA Women's Super League | 2020/2021 | 37/90 | 131 | 12 | 21/22/22 | 0 | 99 |
| FA Women's Super League | 2019/2020 | 37/42 | 87 | 12 | 13/14/16 | 0 | 56 |
| FA Women's Super League | 2018/2019 | 37/4 | 107 | 11 | 19/19/20 | 0 | 78 |
| FIFA U20 World Cup | 1979 | 1470/274 | 1 | 2 | 1/1/1 | 0 | 0 |
| FIFA World Cup | 2022 | 43/106 | 64 | 32 | 3/3.5/7 | 64 | 4 |
| FIFA World Cup | 2018 | 43/3 | 64 | 32 | 3/3.5/7 | 0 | 4 |
| FIFA World Cup | 1990 | 43/55 | 1 | 2 | 1/1/1 | 0 | 0 |
| FIFA World Cup | 1986 | 43/54 | 3 | 4 | 1/1/3 | 0 | 0 |
| FIFA World Cup | 1974 | 43/51 | 6 | 6 | 1/1.5/5 | 0 | 0 |
| FIFA World Cup | 1970 | 43/272 | 6 | 7 | 1/1/6 | 0 | 0 |
| FIFA World Cup | 1962 | 43/270 | 1 | 2 | 1/1/1 | 0 | 0 |
| FIFA World Cup | 1958 | 43/269 | 2 | 3 | 1/1/2 | 0 | 0 |
| Frauen Bundesliga | 2023/2024 | 135/281 | 132 | 12 | 22/22/22 | 0 | 102 |
| Indian Super league | 2021/2022 | 1238/108 | 115 | 11 | 20/20/23 | 0 | 85 |
| La Liga | 2020/2021 | 11/90 | 35 | 19 | 1/2/35 | 35 | 0 |
| La Liga | 2019/2020 | 11/42 | 33 | 20 | 1/2/33 | 0 | 0 |
| La Liga | 2018/2019 | 11/4 | 34 | 20 | 1/2/34 | 0 | 0 |
| La Liga | 2017/2018 | 11/1 | 36 | 20 | 1/2/36 | 0 | 0 |
| La Liga | 2016/2017 | 11/2 | 34 | 20 | 1/2/34 | 0 | 0 |
| La Liga | 2015/2016 | 11/27 | 380 | 20 | 38/38/38 | 0 | 330 |
| La Liga | 2014/2015 | 11/26 | 38 | 20 | 2/2/38 | 0 | 0 |
| La Liga | 2013/2014 | 11/25 | 31 | 20 | 1/2/31 | 0 | 0 |
| La Liga | 2012/2013 | 11/24 | 32 | 20 | 1/2/32 | 0 | 0 |
| La Liga | 2011/2012 | 11/23 | 37 | 20 | 1/2/37 | 0 | 0 |
| La Liga | 2010/2011 | 11/22 | 33 | 20 | 1/2/33 | 0 | 0 |
| La Liga | 2009/2010 | 11/21 | 35 | 20 | 1/2/35 | 0 | 0 |
| La Liga | 2008/2009 | 11/41 | 31 | 19 | 1/2/31 | 0 | 0 |
| La Liga | 2007/2008 | 11/40 | 27 | 20 | 1/1/27 | 0 | 0 |
| La Liga | 2006/2007 | 11/39 | 26 | 20 | 1/1/26 | 0 | 0 |
| La Liga | 2005/2006 | 11/38 | 17 | 17 | 1/1/17 | 0 | 0 |
| La Liga | 2004/2005 | 11/37 | 7 | 7 | 1/1/7 | 0 | 0 |
| La Liga | 1973/1974 | 11/278 | 1 | 2 | 1/1/1 | 0 | 0 |
| Liga F | 2023/2024 | 182/281 | 240 | 16 | 30/30/30 | 0 | 200 |
| Liga Profesional | 1997/1998 | 81/48 | 1 | 2 | 1/1/1 | 0 | 0 |
| Liga Profesional | 1981 | 81/275 | 1 | 2 | 1/1/1 | 0 | 0 |
| Ligue 1 | 2022/2023 | 7/235 | 32 | 20 | 1/2/32 | 32 | 0 |
| Ligue 1 | 2021/2022 | 7/108 | 26 | 18 | 1/2/26 | 26 | 0 |
| Ligue 1 | 2015/2016 | 7/27 | 377 | 20 | 37/38/38 | 0 | 327 |
| Major League Soccer | 2023 | 44/107 | 6 | 7 | 1/1/6 | 6 | 0 |
| North American League | 1977 | 116/68 | 1 | 2 | 1/1/1 | 0 | 0 |
| NWSL | 2023 | 49/107 | 137 | 12 | 22/22.5/25 | 0 | 107 |
| NWSL | 2018 | 49/3 | 36 | 9 | 5/7/13 | 0 | 10 |
| Premier League | 2015/2016 | 2/27 | 380 | 20 | 38/38/38 | 0 | 330 |
| Premier League | 2003/2004 | 2/44 | 38 | 20 | 2/2/38 | 0 | 0 |
| Serie A | 2015/2016 | 12/27 | 380 | 20 | 38/38/38 | 0 | 330 |
| Serie A | 1986/1987 | 12/86 | 1 | 2 | 1/1/1 | 0 | 0 |
| Serie A Women | 2023/2024 | 131/281 | 130 | 10 | 26/26/26 | 0 | 105 |
| UEFA Euro | 2024 | 55/282 | 51 | 24 | 3/4/7 | 51 | 3 |
| UEFA Euro | 2020 | 55/43 | 51 | 24 | 3/4/7 | 51 | 3 |
| UEFA Europa League | 1988/1989 | 35/75 | 3 | 4 | 1/1/3 | 0 | 0 |
| UEFA Women's Euro | 2025 | 53/315 | 31 | 16 | 3/3.5/6 | 31 | 1 |
| UEFA Women's Euro | 2022 | 53/106 | 31 | 16 | 3/3.5/6 | 31 | 1 |
| Women's World Cup | 2023 | 72/107 | 64 | 32 | 3/3.5/7 | 64 | 4 |
| Women's World Cup | 2019 | 72/30 | 52 | 24 | 3/4/7 | 0 | 4 |

### 7.3 Recortes úteis, distribuição e EDA

PL 2015/16 (2/27): 380 jogos, 20 equipes ×38, de 08/08/2015 a 17/05/2016; 330 alvos com cinco anteriores de ambas, 280 com dez. São **grupos por partida**, com dependência adicional entre equipes/janelas: duas linhas por confronto produziriam 660 registros, não 660 exemplos independentes. A tarefa inicial propõe uma linha do mandante, até 330 grupos.

La Liga 2020/21 (11/90): 35 jogos e 19 equipes; Barcelona aparece em 35, 17 adversários em dois e Elche em um. H5 bilateral = **zero**. Serve ao teste de abstenção, não a treino/teste comparável à PL com o mesmo critério. Outras ligas 2015/16 têm calendário amplo (La Liga/Serie A 380, Ligue 1 377), mas não estão funcionalmente auditadas pela V3. Podem ser candidatos a auditoria futura, não ampliação automática do recorte.

EDA preservada `outputs/statsbomb_eda_20261002_exec6/`: `CHECKPOINT.json`, `RELATORIO.md`, `validacoes_qualidade.csv` e metadados Parquet consultados. Rodapés indicam manifesto completo 3.961, manifesto do recorte 380, eventos do recorte 1.313.773, escalações 13.678, equipe/partida 760, histórico do caso 20 e resumo do caso dois registros. Apenas sete colunas da pequena tabela `equipe_partida.parquet` foram lidas (760 linhas/380 IDs), sem carregar `eventos_recorte.parquet`: chutes/chutes sofridos e xG/xG sofrido sem nulos nessa tabela; chutes entre 1 e 37. São resultados históricos calculados pela EDA, não automaticamente labels validados do pipeline atual. O núcleo usa definições/exposição/agregações diferentes em vários indicadores (§4 de CURRENT_VERSION). Oito contagens de chutes dos quatro jogos PL amostrados coincidiram entre EDA e `match_features`; não se extrapola equivalência para todas as fórmulas.

### 7.4 Amostra controlada e rótulos observáveis

Seleção reproduzível: ordenar cada calendário por `(match_date, kick_off ou vazio, match_id)` e escolher posições `[0,n//3,2*n//3,n-1]` de `(2,27)`, `(11,90)` e `(37,4)`. IDs:

- PL: 3754097, 3754301, 3754244, 3754159.
- La Liga: 3773593, 3773523, 3773665, 3773457.
- WSL 2018/19: 19717, 19753, 19792, 19822.

Doze eventos/escalações e somente dois JSONs 360 (primeiro/último La Liga); fontes e SHA-256 registrados no diagnóstico temporário. Leitura sequencial, 30 fontes distintas e 58.745.935 bytes somados nesse diagnóstico, além dos calendários globais lidos no inventário; não é carga integral do clone. Nos 12 jogos:

| Checagem | Observação real e limite |
|---|---|
| `match_features` | 12/12 passam checagens estruturais; contagem direta de Shot períodos1/2 coincide por equipe em todos. Nenhum modelo executado |
| Eventos/posse | 43.962 eventos nos períodos1/2; IDs de posse e equipe de posse presentes em todos; não prova que os blocos representem todas as posses reais |
| Chutes | 270/270 com xG finito em [0,1] e localização válida; suficiente para observar os alvos na amostra, não certifica todos os jogos |
| Passes | 12.382/12.382 com destino válido; 1.941 `under_pressure=True`, zero False explícito e 10.441 ausentes. Ausência não equivale a False |
| Formação | 24 Starting XI com formação nominal; decisões observadas, não rótulos de formação ideal/organização contínua |
| Localização | 248 ausências, zero coordenadas inválidas na amostra; eventos não espaciais podem legitimamente não ter posição |
| 360 em 3773593 | 3.914 frames/4.342 eventos; todos os UUIDs vinculam eventos, únicos; 6–21 jogadores/frame |
| 360 em 3773457 | 3.853 frames/4.205 eventos; UUIDs vinculados e únicos; 3–22 jogadores/frame |

Os dois arquivos 360 contêm `event_uuid`, `freeze_frame`, `visible_area`; jogadores têm `actor`, `keeper`, `location`, `teammate`. Nem todo evento tem frame nem todo frame tem 22 jogadores; não é tracking contínuo com velocidades. Essa observação impede tratar apenas “arquivo presente” como cobertura espacial integral. Não se auditou a totalidade dos 426 arquivos 360.

### 7.5 Mistura de domínios e disponibilidade temporal

Metadados locais incluem `data_version` 1.0.2, 1.0.3 e 1.1.0, combinações distintas de `shot_fidelity_version`/`xy_fidelity_version` e objetos `metadata` vazios. WSL 2018/19 contém 80 jogos 1.0.3, 20 jogos 1.1.0 com shot_fidelity2 e sete 1.1.0 sem esse campo. Nomes/ausências/fidelidade e orientação não podem ser presumidos homogêneos. PL/La Liga 2015/16 completas tampouco autorizam juntar ligas, gênero, juvenil, seleções e clubes sem auditar campo/definição e identificar domínio.

`match_date` informa realização, não publicação original. Na amostra, PL 2015 já possui `last_updated` em 2020; WSL 2019 tem atualização em 2021. `last_updated`, atualização360 e `metadata` não provam quando cada anotação se tornou disponível ao usuário. Trata-se de backtest **retrospectivo com recorte temporal de partidas**, não simulação comprovada de uma base como era conhecida em 2015. Data de obtenção/commit/hash devem acompanhar cada futuro dataset; ausência de timestamp de disponibilidade precisa permanecer explícita.

### 7.6 Licença e proveniência

Clone independente na revisão `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`. Foram lidos README e PDF local integralmente: `open-data/LICENSE.pdf`, *StatsBomb Public Data User Agreement*, atualização indicada de 08/09/2023. A cláusula1.1 descreve análise/pesquisa; 1.2.1 restringe edição/distribuição/reprodução/fornecimento a terceiros e 1.2.2 restringe exploração comercial dos dados/análises; 1.4 exige atribuição com logo. A seção7 trata transferência/licenciamento de conteúdo proprietário. Não tratar “open-data” como licença permissiva irrestrita ou presumir permissão de publicar dataset derivado/pesos; responsável/professor deve confirmar termos aplicáveis e eventual autorização antes da distribuição ou uso comercial. Não houve compartilhamento externo de dados nesta fase. [Arquivo oficial na revisão local](https://github.com/hudl/open-data/blob/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/LICENSE.pdf), [README oficial](https://github.com/hudl/open-data/blob/master/README.md).

As consultas externas da especificação360 retornaram página ausente e o navegador não renderizou o PDF bruto da licença; esta análise de termos usa o **PDF local lido por pdftotext**, preservado e versionado no clone. Esclarecimento jurídico/comercial não foi obtido por consulta ao fornecedor. Separar direitos de dados, código dos algoritmos e pesos. Preservar atribuição e evitar redistribuir JSONs/dados pessoais de jogadores por inferência de uma licença de software.

## 8. Matriz de tarefas candidatas

| Tarefa | Problema e valor ao treinador | Unidade / entradas / alvo ou aprendizado | Labels, volume e dados adicionais | Avaliação, vazamento e limitações | Viabilidade |
|---|---|---|---|---|---|
| T1 — característica ofensiva | Antecipar volume de finalizações para contextualizar preparação, sem recomendar uma estratégia | Uma partida/mandante; médias históricas próprias de `shots_for`, `shots_against` e equivalentes do adversário, amostras/qualidade; y=Shot do mandante nos períodos1/2 do alvo, incluindo acréscimos e excluindo prorrogação e disputa de pênaltis; pênaltis cobrados nos períodos1/2 contam | Label derivável depois do confronto via `match_features`, verificado nos 12 jogos amostrados. Até330 grupos elegíveis PL; poder e n final dependem de calculabilidade. Não exige rótulo humano para contagem, mas interpretação útil exige revisão técnica | MAE primário, RMSE/viés secundários contra médias históricas; placar/xG/eventos do alvo nunca entram em X. Contagem não mede qualidade/eficácia nem determina intervenção | **Viável para experimento** pequeno, com gates; recomendada inicialmente |
| T2 — exposição defensiva observável | Antecipar finalizações sofridas; sinal descritivo de carga defensiva, não diagnóstico causal de vulnerabilidade | Uma partida/equipe; históricos ofensivos do adversário e defensivos próprios; y=`shots_against` futuro, xG contra secundário sob completude | Mesmos até330 grupos PL, não outros330 independentes. Chutes sofridos pelo mandante são chutes do visitante; pares/targets compartilham a partida. Para afirmar vulnerabilidade espacial, acrescentar revisão/lances e critérios externos | Mesmos splits/baselines para o alvo escolhido, MAE/RMSE; xG é anotação do fornecedor e não tática ideal. Não usar exposição/placar final do alvo como feature | **Viável mediante condições**, como previsão descritiva; vulnerabilidade causal não demonstrada |
| T3 — padrões observáveis | Resumir semelhanças/variações de circulação, progressão e pressão para revisão em vídeo | Equipe/jogo ou janela histórica; 21+26 indicadores/3 agregados quando elegíveis; clustering/representação sem rótulo, ou classificação somente com taxonomia humana | EDA tem760 linhas em380 grupos; após H5 até660 linhas dependentes/330 grupos, n efetivo menor. Eventos internos não são amostras independentes. Labels de estilo exigem especialistas/vídeo/concordância | Transformação e clusters ajustados no treino; estabilidade em tempo/seeds, sensibilidade a faltantes, representação em holdout e revisão cega; silhouette isolada não valida “estilo tático”. Sem clustering transdutivo no teste | **Viável mediante condições** para padrões estatísticos; interpretação tática externa ainda não demonstrada |
| T4 — apoio à escolha de estratégia | Recomendar formação/estilo/ajuste com utilidade e riscos sustentados | Situação decisória, alternativas disponíveis, execução e consequências; política/avaliação especializada exigem informações além de agregados | Há **zero rótulos validados de estratégia ideal demonstrados**, não zero decisões históricas. Formação registrada é decisão realizada; não revela alternativas/contrafactual, aptidão, intenção ou qualidade. Exige rótulos de especialistas, contexto, vídeo/tracking conforme tarefa e desenho de avaliação | Julgamento cego de sustentação/utilidade não prova eficácia; intervenção causal exige controle de confundimento e desenho próprio. Vitória/gols/hipóteses baseline não viram verdade de referência | Estratégia ótima validada **inviável com os dados disponíveis**; apoio descritivo e hipóteses atuais continuam possíveis |

Não há número mínimo mágico de jogos para “treinar IA”. Os números acima são tetos de grupos por partida, não observações estatisticamente independentes; as mesmas equipes e janelas introduzem dependência. T1 permite testar se existe sinal preditivo; não garante ganho nem produto pronto.

## 9. Atributos, alvos e corte de cada exemplo

### 9.1 Disponibilidade e instante de corte

Fixar para cada alvo m o corte no **início do seu dia de calendário**, mantendo a política de `temporal.select_history`: datas `<match_date(m)`, mesmo dia inteiro excluído, uma competição/temporada, últimas dez partidas agendadas anteriores por equipe, sem completar a janela por ausência de arquivos. Quando a requisição inclui horário do alvo, o núcleo ainda exclui todo o dia. Fuso/publicação original não comprovados; registrar essa limitação. y pode ser conhecido depois, em armazenamento/scorer separado; nem seu arquivo nem transformação dependente dele entra no snapshot X.

| Classe | Atributos / fontes reais | Utilização e ressalvas |
|---|---|---|
| 1 — diretamente antes, sob disponibilidade confirmada | IDs do confronto/competição/temporada, data programada e mando formal do calendário; contexto declarado pelo técnico | O catálogo retrospectivo não certifica publicação inicial. IDs são identificadores, não números ordinais. Mando formal não prova estádio neutro/efeito causal; primeiro experimento seleciona `team_id=home_team_id` no manifesto de labels, sem presumir `request.venue` verificado |
| 2 — calculáveis de histórico anterior | Ofensivo/defensivo: chutes/xG a favor/contra; criação por chute; médias, dispersão e amostras. Passes/acerto separado por pressão; progressão/entradas; pressão/recuperação e qualidade | Usar `MetricEvidence` e versões existentes; razões por somas e denominadores próprios, não refazer fórmula a partir da EDA. xG anterior requer completude; campos null e n precisam acompanhar valor |
| 2 — espacial/transição/temporal | V3: localização de chutes/pressão/entradas, três métricas de blocos; janelas e evolução de histórico próprio/adversário; formações Starting XI/Tactical Shift históricas | V3 só nos dois pares permitidos. Blocos não comprovam contra-ataques/transições eficazes; faixas y não significam esquerda/direita tática nem organização contínua. Tendências requerem definição anterior ao teste; formações históricas não indicam aptidão atual |
| 3 — somente depois do alvo | Chutes/xG/passes/pressão do próprio confronto, exposição observada, placar, expulsões, escalação/formação executada, substituições e eventos/360 do alvo | Proibidos em X pré-jogo. Servem para y ou auditoria/estratificação de erros predefinida; não ajustar seleção/normalização com resultados do teste |
| 4 — indisponíveis/insuficientes | Disponibilidade atual, lesão/suspensão, formação ideal, intenção tática, comportamento contínuo sem bola, pressão eficaz e efeitos contrafactuais | Não inferir de roster/formações/pressão registrada. 360 limitado por eventos/jogadores/recorte; tracking e contexto adicionais exigem fontes/direitos/validação próprios |

### 9.2 Menor conjunto proposto e preparação futura

Primeiro experimento: quatro valores históricos (média própria `shots_for`/`shots_against`, média adversária dos mesmos dois indicadores), n e máscaras de qualidade/suficiência. A própria regra de elegibilidade exige pelo menos cinco jogos calculáveis das duas equipes na janela10. Começar pequeno em vez de dezenas de variáveis para198 grupos de treino; xG, evolução temporal, dispersão, pressão e V3 são ablações posteriores, não expansão automática. Rótulo inicial é contagem bruta de chutes regulamentares; não mudar para taxa por90 usando exposição do alvo como feature.

Padronização para regressão/MLP: estimar parâmetros no treino; árvores não precisam dessa etapa por padrão. Imputação/categorias/seleção ajustadas só no treino, com máscaras/n e estratégia definida para faltantes; zero somente quando fluxo íntegro observou nenhuma ocorrência. `under_pressure` ausente fica separado de False; denominador zero continua null. Não imputar alvo ausente nem selecionar retrospectivamente partidas por ter bom resultado. Logs de exclusão/abstenção e cobertura fazem parte do score. Não misturar temporadas/gênero/competição ou usar estatísticas finais da temporada; identificar explicitamente os domínios. Nenhum desses transformadores foi implementado nesta fase.

### 9.3 Compatibilidade real com V4.1

`TacticalEngineInput`/`build_engine_input` já fornecem IDs/request/contexto declarado, perfis, evidência por partida, qualidade, datas, fontes/fingerprints e indicadores21+26/3 sequências quando V3. O snapshot não inclui recomendações baseline como atributos. `build_engine_input` exclui histórico detalhado de atletas/formações, sequências extensas e `metadata.formal_home_team_id`; `request.venue` é declaração manual, padrão desconhecido. Portanto formações/mando verificado não são automaticamente features prontas no contrato.

`TacticalEngineOutput` contém hipóteses/abstenção, **não previsão numérica**. Para T1/T2, V4.3 precisa de contrato quantitativo de tarefa/scorer/manifesto separado, preservando integralmente V4.1 e schemas legados. Não criar hipótese artificial para acomodar regressão nem usar `compare_engines` como se já calculasse MAE. O adaptador determinístico serve à avaliação de hipóteses; médias históricas são os baselines quantitativos adequados a T1. Para sequências, outro contrato de entrada poderá ser necessário. Nada disso foi implementado na V4.2.

## 10. Protocolo experimental proposto

### 10.1 Elegibilidade e divisões

Uma linha por partida PL2015/16, alvo do mandante, janela10 estritamente anterior e mínimo5 calculáveis de ambas equipes. Pelo calendário, até330 candidatos; auditá-los integralmente no futuro builder/scorer antes de congelar n final, conferindo alvos e features separadamente. Excluir de forma documentada fluxos inválidos sem repor partidas antigas. Datas por aproximação60/20/20, mantendo o mesmo dia em um único conjunto, calculadas somente com calendários:

| Partição ilustrativa | Datas-alvo inclusivas | Grupos por partida candidatos |
|---|---|---:|
| Treino | 19/09/2015–06/02/2016 | 198 |
| Validação | 07/02/2016–03/04/2016 | 65 |
| Teste final bloqueado | 09/04/2016–17/05/2016 | 67 |

Não são splits implementados nem garantia de198/65/67 após validação de calculabilidade. Fixar fronteiras antes de olhar y do teste; falhas não autorizam escolher novas datas pelo score. Variante com mínimo10 produz280 candidatos e deve ser outro protocolo, sem trocar o critério após resultados.

Treino/validação/teste agrupados por `match_id` e dia: nunca separar equipes, posses, chutes ou eventos do mesmo jogo entre conjuntos. Janelas sobrepostas são dependência esperada em previsão histórica; não usar split aleatório. Prever de forma prequential: pesos/preprocessing ficam congelados após escolha no treino/validação, mas indicadores do jogo anterior ao próximo alvo podem usar jogos já ocorridos do período de teste se essa política de disponibilidade for pré-registrada. Isso não permite retreinar/selecionar parâmetros com y de teste; alternativa de previsão de bloco sem atualização de histórico é experimento distinto.

Nenhuma segunda temporada completa já autorizada V3 suporta hoje alegação de generalização temporal entre temporadas. Liga/temporada externa exige auditoria separada e teste por domínio, sem ampliar VALIDATED_RECUTS. Leave-team-out deve excluir do treino **todas** as partidas envolvendo equipes retidas e recontar n; apenas reservar suas linhas deixando os adversários no treino contamina os grupos. Analisar erro por clube/período sem prometer precisão por equipe com poucas partidas.

### 10.2 Baselines, métricas e três qualidades distintas

- **T1/T2 regressão:** B0 é a média histórica própria do alvo. T1: B0=`shots_for` próprio; B1=50% `shots_for` próprio +50% `shots_against` adversário. T2: B0=`shots_against` próprio; B1=50% `shots_against` próprio +50% `shots_for` adversário. Combinações pré-fixadas, nenhum parâmetro ajustado no teste. Regressão regularizada/de contagem e uma árvore candidata sob mesmos jogos/alvo. MAE primário em chutes/jogo; RMSE e viés médio secundários, erro por equipe/data, cobertura e erro condicionado à disponibilidade. Poisson deviance se modelo/valores válidos; R² descritivo pode ser negativo. Não comparar esses scores com número/qualidade de hipóteses determinísticas.
- **Classificação futura:** somente com categoria/limiar/labels definidos no treino/protocolo; baseline prevalência, log-loss/Brier e precisão/recall conforme custo e desequilíbrio, confiabilidade/calibração em conjunto de validação. Probabilidade só se realmente produzida e avaliada; intervalos/quantis de regressão exigem cobertura e largura, não linguagem de certeza.
- **Padrões/representações:** estabilidade por seeds/blocos temporais, sensibilidade a escala/faltantes, consistência em dados futuros e avaliação especializada cega; silhouette/dimensões latentes não são medida de acerto tático.
- **Qualidade preditiva:** erro no alvo sob teste temporal independente das decisões de ajuste.
- **Qualidade de evidência:** fonte/hash/corte/denominador/rastreabilidade, cobertura e fidelidade da justificativa aos fatos; pode ser boa mesmo com previsão ruim.
- **Qualidade de recomendação:** utilidade, plausibilidade, riscos/precondições, correção e compreensão julgadas por especialistas, com desacordos e casos não avaliáveis registrados. Bom MAE não comprova melhor estratégia, e placar favorável não comprova eficácia causal.

### 10.3 Reprodução, faltantes e critério de ganho

Registrar manifesto de jogos/exclusões, versão de métrica/schema/código, checksum de fontes/transformadores/checkpoints, seed, versão de bibliotecas e ambiente, configuração, custo/latência e falhas. Repetir ajustes estocásticos com seeds pré-fixadas em treino/validação e relatar dispersão; um teste final não vira mecanismo de seleção entre dezenas de modelos. Fazer curvas de aprendizado/ablação somente nos conjuntos permitidos.

Testar amostra0/1/4, campos ausentes, denominador zero, dados de outra temporada, fonte alterada e abstenção. Comparar modelos na interseção comum com análise adicional de cobertura total; não esconder rejeições por comparar apenas casos fáceis. Não forçar previsão ou recomendação quando política de suficiência falha.

Propor antes do treino uma margem mínima de melhora ΔMAE útil ao professor/comissão e orçamento de custo/latência; **não há valor de Δ aprovado nesta fase**. Ganho exigirá redução pareada de MAE contra B0/B1 no mesmo teste bloqueado, intervalo de incerteza que sustente essa margem, estabilidade nos recortes/seed e sem piora material de cobertura/risco. Para incerteza, reamostragem em blocos temporais de partidas, com análise de sensibilidade ao tamanho do bloco escolhido no treino; partidas/equipes são dependentes, n=67 é pequeno. Não usar bootstrap de eventos como se fossem independentes.

Impedem concluir superioridade: intervalo incluindo ausência de ganho relevante, teste usado para tuning/seleção, alvos incompatíveis, possível contaminação não resolvida de pré-treino, exclusão seletiva, instabilidade por clube/tempo, ausência de comparação com checkpoint congelado e custo desproporcional. Mesmo ganho preditivo válido não demonstra ganho causal de recomendações.

## 11. Fine-tuning — respostas explícitas e decisão

| Questão | Conclusão fundamentada |
|---|---|
| Há tarefa com alvos observáveis e exemplos suficientes? | Há alvos observáveis de chutes:12 jogos amostrados, EDA760 linhas sem nulos, PLaté330 grupos elegíveis. Há volume para **experimento pequeno**, não comprovação de suficiência para redes/fine-tuning nem de poder estatístico após198/65/67 |
| Menor tarefa cientificamente defensável? | T1: prever contagem de finalizações do mandante nos períodos1/2, PL2015/16, quatro indicadores históricos anteriores e cobertura; média histórica como referência |
| Há arquitetura/pesos compatíveis? | TabPFN é tabular após transformação; Chronos-2/TimesFM exigem representação de séries; não recebem JSONs crus. Compatibilidade representacional não prova adequação esportiva. Nenhum checkpoint pronto de estratégia ideal foi verificado |
| Qual adaptação poderia existir? | TabPFN atualização supervisionada de pesos; Chronos full/LoRA; TimesFM exemplos LoRA; LLM SFT/LoRA para apresentação, não previsão quantitativa/decisão causal. Aprendizado em contexto não é fine-tuning. Tudo condicionado; nada executado |
| Recursos necessários? | Regressão/árvores pequenas são candidatas CPU. Host observado:8 CPUs lógicos, MemTotal16.110.076 kB (~15,36GiB); `nvidia-smi` indisponível, portanto GPU/VRAM não verificadas. Ajustes neurais precisam orçamento/GPU/contexto/batch definidos; não há mínimo universal validado. Somente pesos:120M float32≈480 MB,200M ≈800 MB,7B bf16 ≈14 GB (limites aritméticos, excluem ativações/otimizador/KV/overheads, não dimensionamento de máquina). Não inferir que cabem/treinam no host. Nenhum benchmark local executado |
| Quais licenças/dados faltam? | Aprovação de termos StatsBomb para finalidade/distribuição/derivados (§7.6), licença exata de pesos/código, corpus/datas de pré-treino, dados rotulados externos e representação; licenças permissivas dos modelos não resolvem os termos do dataset |
| O que falta para recomendações? | Tarefa decisória/alternativas, disponibilidade e intenção verificadas, evidência de execução/contexto, especialistas e concordância, vídeo/tracking quando necessário e avaliação de intervenção/confundimento; vitória ou formação observada não fornecem idealidade |
| Que ganho justificaria fine-tuning? | Comparar mesmo alvo/teste temporal contra B0/B1, regressão/árvore e o **mesmo checkpoint congelado sem ajuste**, sob direitos/corpus elegíveis. ΔMAE útil e orçamento pré-acordados, incerteza por blocos e estabilidade/cobertura. Sem ganho relevante reproduzível, adotar a opção mais simples; não presumir vantagem de fine-tuning |

Classificação consolidada: T1/regressão e árvores **viáveis para experimento**; T2, T3 e adaptação tabular/temporal **viáveis mediante condições**; benefício do fine-tuning e modelo esportivo pronto **ainda não demonstrados**; estratégia ideal/reprodução TacticAI com a representação atual **inviáveis com os dados disponíveis**. Um modelo especializado pode inicialmente ser supervisionado simples; não depende de fine-tuning para ser especializado na tarefa.

## 12. Gates definidos na V4.2 — estado após V4.3-A/B

Recomendação: aprovar primeiro um experimento **de previsão de chutes**, mantendo hipóteses determinísticas como camada separada. Não prometer “motor de estratégia ideal”.

| Gate / prioridade | Dependência / responsável a definir | Aceite antes de prosseguir |
|---|---|---|
| V43-01 / P0 | ESCOPO A/B AUTORIZADO | Usuário aprovou T1, janela exata5, regressões leves e execução local. Fronteiras da V4.2 fixadas antes de y. Margem útil ΔMAE/aceite esportivo ainda não aprovada |
| V43-02 / P0 | PESQUISA LOCAL CONFERIDA | Clone/hashes/licença registrados; nenhum peso pré-treinado ou dado publicado. Permissões de distribuição/comercialização continuam decisão separada |
| V43-03 / P0 | CONCLUÍDO A/B | 380 jogos auditados, 330 exemplos válidos e 50 excluídos; builder puro de X e passagem posterior de labels, fontes separadas |
| V43-04 / P0 | CONCLUÍDO A/B | Contrato quantitativo próprio, dataset/scorer offline; nenhum campo adicionado aos schemas/V4.1 |
| V43-05 / P1 | PROTOCOLO NUMÉRICO EXECUTADO | Treino198/validação65/teste67, janela5, B0/B1/OLS/Ridgealpha1, nenhuma seleção/tuning em holdout. Avaliação humana de utilidade e incerteza não realizadas |
| V43-06 / P1 | CONCLUÍDO SOMENTE A/B | Regressão linear e Ridge ajustadas; sem árvores, redes, pré-treino/fine-tuning ou integração ao produto. Continuidade C condicionada ao §14 |

Ainda exigem decisão humana: finalidade acadêmica/comercial e permissões; tarefa e tolerância a erro/abstenção; especialista/taxonomia/pares de texto quando aplicáveis; temporadas futuras e auditoria; orçamento/hardware; responsáveis por dados/contratos/modelo/avaliação; distribuição de resultados/pesos. Esse era o limite da autorização A/B. A autorização posterior C gerou o §15; a CORE-00 autoriza somente estabilização/integração do §16. Fine-tuning, redes e integração de modelo no runtime continuam fora do escopo.

## 13. Validação real da V4.2

Execução em 17/10/2026, Python 3.12.3 e opcionais existentes. Nenhum novo teste, modelo, feature, dependência ou artefato foi criado na árvore do projeto; somente os dois documentos autorizados foram editados. Resultados históricos do §6 não foram usados como substituto desta execução.

| Checagem corrente | Resultado efetivamente observado |
|---|---|
| Suíte completa local/UI/V3/V4.1 | **153 aprovados**, zero falhas, erros e pulos; código 0; 65,438 s |
| Verificação independente | **16/16 aprovadas**, código 0; JSON idêntico ao da V4.1 |
| Contratos e schemas | Suíte inclui snapshots, seleção de motores, abstenção, datas/evidências, fixture schema1.0.0 e demos schema1.1.0 preservados byte a byte; código funcional tem hashes do início desta fase |
| Inventário | Catálogo + 80 calendários validados, sem abrir os eventos de todas as partidas; 3.961 IDs catalogados e cobertura por presença registrada |
| Diagnóstico amostral | 12/12 `match_features` passam, contagens Shot concordam com núcleo em todas; oito contagens PL concordam com pequena tabela EDA; dois arquivos 360 inspecionados. Não é auditoria integral de alvos/features dos 330 candidatos |
| Integridade do projeto | 180 arquivos fora dos dois docs com mesmos SHA-256; nenhum arquivo criado/removido. Inclui todos os fontes/testes, AGENTS, README, dependências, demos, fixture e 108 artefatos EDA |
| Integridade do clone | 8.980 arquivos rastreados com mesmo tamanho/mtime_ns, status limpo e revisão inalterada; SHA-256 conferido em 107 fontes distintas (catálogo/80 calendários/12 eventos/12 escalações/2arquivos 360). **Não** se releu/hashou integralmente os 16 GB, nem se afirma certificação binária integral do restante |
| Links locais | 16 destinos Markdown existentes em raiz/docs/outputs, zero ausentes |
| Git/histórico | HEAD principal `09b73b75c74266347a2f924a67dc95d7c803720f`, clone `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`, ambos inalterados; `git diff --check` sem problemas |

Comandos desta execução:

```bash
MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg venv/bin/python -B -m unittest discover -s tests -v
PYTHONPATH=src venv/bin/python -B outputs/v22_v3_validation/check_metrics.py
```

TMPDIR, MPLCONFIGDIR e caches XDG ficaram em temporários exclusivos. Avisos conhecidos AppTest `missing ScriptRunContext` não causaram falhas. A suíte usa dados reais de recortes limitados; não houve navegação manual nem revisão esportiva/humana. Não foram executados treinamento, fine-tuning, tuning, criação de previsões/recomendações artificiais ou download de pesos.

Diagnósticos e logs somente em `/tmp/managerai-v42-91atel2d/`: `baseline.json` (hashes/status e metadados iniciais), `inventory_diagnostic.py`, `inventory.json`, `inventory_summary.json`, `sample_diagnostic.py`, `sample.json` (fontes/hashes/contagens), `calendar_eligibility.json` (IDs candidatos e splits de calendário), `eda_metadata.json`, `eda_small_table.json`, `eda_label_sample_comparison.json`, `after_tests.log`, `after_summary.json`, `after_metrics.json`, `check_integrity.py` e `integrity.json`. Cópias dos dois documentos anteriores à fase também estão nesse temporário. Evidência durável resumida e números relevantes permanecem neste documento; temporários não são novos manuais operacionais.

O status inicial já continha mudanças da V4.1 e os arquivos Python novos/não rastreados. O status final tem os mesmos caminhos; comparação SHA-256 desta fase comprova que **somente `docs/CURRENT_VERSION.md` e `docs/PENDING.md` mudaram**. `AGENTS.md` não foi alterado nesta fase. `git status --short`:

```text
 M AGENTS.md
 M docs/CURRENT_VERSION.md
 M docs/PENDING.md
?? open-data/
?? src/managerai/tactical_engine_schema.py
?? src/managerai/tactical_engines.py
?? tests/test_tactical_engines.py
```

Nenhum commit/push, integração externa, alteração de CLI/Streamlit/pipeline/contratos/fórmulas/recortes ou modificação de dados/EDA. V4.2 encerra com recomendação de experimento condicionado; V4.3 exige autorização específica.

## 14. V4.3-A/B — dataset, baselines e decisão

### 14.1 Escopo e protocolo fixados antes dos resultados

Autorização atual: experimento acadêmico local não comercial, regressões leves e um artefato estruturado novo; não publicação de dataset/pesos nem exploração comercial. Os termos locais de pesquisa/análise foram conferidos (§7.6); distribuição/comercialização permanecem pendentes, sem impedir este experimento local. Não houve envio externo de dados.

A mudança da proposta V4.2 (janela10/min5) para **janela exata5/min5** segue a SPEC A/B, não o desempenho observado. Duas features mínimas pré-fixadas: média de finalizações do mandante e média de finalizações concedidas pelo visitante nos seus respectivos cinco jogos anteriores. São históricos de cada clube em qualquer mando. IDs, fontes, cobertura/qualidade ficam para auditoria, não como números ordinais na regressão. Alvo e seus hashes estão separados: Shot ID16/nomeShot do mandante, períodos1/2, todos outcomes, acréscimos e pênaltis regulamentares incluídos; prorrogação e disputa excluídas. Não usar eventos/placar/escalação do alvo nem preencher ausências com zero.

B0=média histórica própria; B1=50% B0 +50% média concedida pelo visitante. OLS com intercepto via `numpy.linalg.lstsq`; Ridgealpha1 fixo, intercepto não penalizado. Scaler populacional somente treino, constante recebe1. Validação e teste são apenas avaliação; sem ajuste de hiperparâmetros, seleção, imputação, normalização ou refit nesses conjuntos. Todos seguem `max(0,raw)`, sem arredondamento; houve zero truncamentos. Esse protocolo foi registrado antes da leitura dos erros; não foi escolhido modelo vencedor nem alterado split depois.

### 14.2 Auditoria e exemplos reais

- Catálogo PL2/27:380 IDs únicos,20 equipes,38 jogos/equipe; eventos de380 partidas disponíveis, auditados em duas passagens específicas do experimento, sem reexecutar os geradores EDA.
- **330 exemplos válidos**, uma linha por partida; **50 excluídos** por histórico menor que cinco de pelo menos uma equipe, com ID/data/motivos no artefato. Nenhum alvo ausente, exemplo duplicado ou histórico inválido foi preenchido. Os excluídos iniciais vão de08/08/2015 até a fase anterior ao primeiro alvo elegível de19/09/2015; datas exatas por arquivo.
- 1.313.773 IDs de eventos únicos,9.908 Shots das duas equipes; outcomes: Blocked 2880, Goal 988, Off T 3197, Post 170, Saved 2209, Saved Off Target 45, Saved to Post 23, Wayward 396. Todos contam como Shot; Own Goal Against é tipo distinto. ID/nome incoerente, ID/índice repetido ou flag explícita de cancelamento bloqueiam; nenhuma dessas falhas foi detectada. Ausência de flag não certifica anulação/VAR real não representada pelo fornecedor.
- Qualidade:2 durações inválidas,3 coordenadas inválidas e8.077 localizações ausentes, preservadas/sinalizadas. Contagem de Shot não usa geometria/exposição nem esses campos como predictors; por isso não são inconsistência material impeditiva para **esta tarefa de contagem**. Não estender essa conclusão a indicadores espaciais/taxas.
- 762 fontes e SHA-256 no artefato: catálogo+calendário+380 eventos+380 escalações. Nenhuma modificação de brutos; presença/integridade contada não reconstrói a disponibilidade original das anotações em2015.

### 14.3 Divisões e unidade de avaliação

| Conjunto | Período-alvo inclusivo | Partidas | Equipes |
|---|---|---:|---:|
| Treino | 2015-09-19 a 2016-02-06 | 198 | 20 |
| Validação | 2016-02-07 a 2016-04-03 | 65 | 20 |
| Teste | 2016-04-09 a 2016-05-17 | 67 | 20 |

Fronteiras fixadas a priori: treino<=06/02/2016, validação até03/04/2016, teste desde09/04/2016. Mesma data nunca se divide, sem embaralhamento; não há candidato no intervalo04–08/04. Uma única temporada não permite separar temporadas completas; blocos conservam dias completos, mas não meses/rodadas inteiras, mantendo o protocolo já proposto antes dos resultados. Cada conjunto contém os mesmos20 clubes: não avalia generalização a equipes não vistas.

Histórico prequential: jogos já ocorridos da validação/teste podem alimentar a janela de confrontos posteriores, sempre antes do dia-alvo; pesos e scaler continuam ajustados somente nos198 de treino. Não são660 linhas independentes nem milhões de exemplos:330 grupos com dependência adicional de equipes/janelas; teste tem67 grupos. Mínimos de execução pré-fixados30/10/20 são guardas operacionais, não prova de poder estatístico.

### 14.4 Métricas reais

MAE/RMSE em chutes por jogo; viés=`predito−observado` (negativo=subestima). Quantis de erro assinados e absolutos usam posição `(n−1)*p` com interpolação linear. Todos os quatro modelos foram avaliados nos mesmos 65 jogos de validação e 67 de teste.

| Modelo | MAE val | RMSE val | Viés val | MAE teste | RMSE teste | Viés teste |
|---|---:|---:|---:|---:|---:|---:|
| B0 média histórica | 4.270769 | 5.671955 | -2.123077 | 4.725373 | 6.229683 | -2.241791 |
| B1 médias50/50 | 4.280000 | 5.534396 | -2.015385 | 4.382090 | 5.854556 | -2.408955 |
| OLS | 4.084661 | 5.180458 | -0.665221 | 4.092347 | 5.451691 | -1.035549 |
| Ridge α=1 | 4.083566 | 5.181834 | -0.664851 | 4.091673 | 5.452651 | -1.036467 |

Diferenças `MAE_modelo−MAE_referência`, negativas indicam menor erro numérico; percentual divide pelo MAE da referência (null se zero). B0/B1 e ambas regressões completos estão no artefato:

| Partição / modelo | ΔMAE vs B0 | Δ% vs B0 | ΔMAE vs B1 | Δ% vs B1 |
|---|---:|---:|---:|---:|
| validation / B0 média histórica | 0.000000 | 0.0000% | -0.009231 | -0.2157% |
| validation / B1 médias50/50 | 0.009231 | 0.2161% | 0.000000 | 0.0000% |
| validation / OLS | -0.186108 | -4.3577% | -0.195339 | -4.5640% |
| validation / Ridge α=1 | -0.187203 | -4.3834% | -0.196434 | -4.5896% |
| test / B0 média histórica | 0.000000 | 0.0000% | 0.343284 | 7.8338% |
| test / B1 médias50/50 | -0.343284 | -7.2647% | 0.000000 | 0.0000% |
| test / OLS | -0.633026 | -13.3963% | -0.289742 | -6.6120% |
| test / Ridge α=1 | -0.633700 | -13.4106% | -0.290416 | -6.6273% |

Distribuições de erro no teste (resumo; completo no JSON):

| Modelo | Mediana erro assinado | Mediana erro absoluto | P90 absoluto | Máximo absoluto |
|---|---:|---:|---:|---:|
| B0 média histórica | -1.400000 | 3.400000 | 9.280000 | 20.200000 |
| B1 médias50/50 | -2.100000 | 3.700000 | 8.540000 | 21.400000 |
| OLS | -0.554247 | 2.966146 | 8.341682 | 19.961235 |
| Ridge α=1 | -0.544658 | 2.970570 | 8.335856 | 19.976092 |

Períodos mensais descritivos (todos com n>=10); n por mês evita interpretar divisão pequena como robustez temporal:

| Partição / mês | n | MAE B0 | MAE B1 | MAE OLS | MAE Ridge |
|---|---:|---:|---:|---:|---:|
| validation / 2016-02 | 20 | 5.390000 | 5.150000 | 4.931366 | 4.932415 |
| validation / 2016-03 | 35 | 3.908571 | 3.974286 | 3.909469 | 3.907450 |
| validation / 2016-04 | 10 | 3.300000 | 3.610000 | 3.004419 | 3.002277 |
| test / 2016-04 | 39 | 4.415385 | 3.869231 | 3.709110 | 3.706565 |
| test / 2016-05 | 28 | 5.157143 | 5.096429 | 4.626142 | 4.628075 |

### 14.5 Interpretação, aceite e V4.3-C

Há menor erro **numérico observado** para OLS/Ridge frente a B0/B1 nesse teste, sem seleção posterior. Ridge reduz MAE em 0,633700 vs B0 (13,4106%) e 0,290416 vs B1 (6,6273%). OLS/Ridge praticamente empatam (diferença de MAE ~0,000674); não eleger Ridge como superior a partir disso. Todos subestimam em média, sobretudo os baselines; ainda ocorrem erros absolutos próximos de20 chutes.

Não há ΔMAE mínimo útil aprovado, intervalo de incerteza calculado ou avaliação humana. BootstrapIID de eventos/jogos não é adequado à dependência de equipes/janelas; não foi produzido um intervalo artificial. Redução de erro não demonstra eficácia de estratégia ou recomendação ideal. Os baselines misturam mandos no histórico; parte do ganho pode ser calibração de mando/regressão à média, não evidência nova de inteligência tática.

**Recomendação: continuidade C somente condicionada a aprovação, para robustez/ablação e avaliação, não fine-tuning ou integração ao produto.** Pré-registrar baseline constante de média de chutes do mandante no treino e ablação da informação adversária; são propostas futuras, não modelos adicionais ajustados depois de olhar este teste. Definir ΔMAE útil/custo/abstenção com professor/comissão; investigar viés/outliers e incerteza por blocos com dependência temporal/equipes; planejar dados externos/temporada nova e licenças/auditoria próprios. Como o teste67 já foi observado, não reutilizá-lo para tuning e depois chamá-lo de teste independente de novas escolhas. Sem dados independentes adequados, limitar a conclusão a um piloto reproduzível nesta temporada.

Critérios técnicos A/B satisfeitos: unidade/labels verificáveis, X/y separados, janela5, partições fixas, fit sótreino, previsões finitas/não negativas, mesmos jogos, auditoria/exclusões e reprodução. **Critérios de superioridade esportiva/produto continuam não satisfeitos.** Nenhuma árvore/rede/Transformer/fine-tuning/LLM/escalação, serviço ou integração de terceiro foi implementada.

### 14.6 Artefato e reprodução

Único resultado durável novo:

```text
outputs/runs/v43_ab_pl2015_16_20261017/run.json
```

Tamanho 4584043 bytes; SHA-256 `29688df92f7e06aadb393eec5c8c469a3b9ef9d07732055f95401d33812889a5`. Dataset fingerprint `7b05d8df08b8f55388b9a5b73220dba7b33e77447c1d9fd39b8bc6bf988a99c5`. Protocol fingerprint `36e230673236e7ec9ca73d6a0dc00cf6fda48f5c21600cd53006ec458c06b8bb`.

O JSON reúne dataset 330/exclusões 50, protocolo, fontes/hashes, partições/IDs, coeficientes/scaler, métricas/deltas/distribuições e528 previsões (4×132 jogos), com fontes de X separadas de y. Head do código `09b73b75c74266347a2f924a67dc95d7c803720f` e estado local registrados; hashes de todos os módulos e pyproject identificam código não commitado. Python 3.12.3, NumPy 2.5.2 existentes, sem instalações. Execução com `OPENBLAS_NUM_THREADS=1` e `OMP_NUM_THREADS=1`, solvers e regras fixos. Metadados de contexto Git podem mudar entre execuções; não são features.

Reprodução independente nesta fase reabriu os brutos e gerou somente temporário `/tmp/managerai-v43ab-jgtzgsnz/reproduction/run.json`: **protocolo, dataset/fingerprint e resultados completos (coeficientes, scaler, métricas e previsões) iguais** ao original. Não é somente reimpressão de previsões guardadas. Não sobrescrever o original: comando e regras de destino novo em CURRENT_VERSION§11.

### 14.7 Validação e integridade A/B

Validação efetivamente executada em 17/10/2026, sem instalar dependências:

| Verificação | Resultado |
|---|---|
| Suíte completa, incluindo testes locais e contratos V4.1 | **191 aprovados**, zero falhas, erros ou pulos; 39,974 s na suíte |
| Comparações independentes | **16/16 aprovadas**, resultados iguais à execução V4.2 |
| Execução sem site-packages (`-S`) | 191 descobertos: **157 aprovados e 34 pulados** por dependências opcionais; zero falhas/erros |
| Reprodução desde os brutos em destino novo | Protocolo, dataset e resultados numéricos completos iguais (§14.6) |
| Validação sintática Python | 55 arquivos válidos |
| Links Markdown locais | 16 destinos existentes, zero links quebrados |
| Contratos e compatibilidade | Testes de schemas legados, fixture, adaptador V4.1 e novo contrato quantitativo aprovados; sem integração no runtime |
| Integridade das fontes | SHA-256 das 762 fontes do experimento reconferidos; tamanho/mtime de 8.980 arquivos do clone preservados; clone limpo na mesma revisão |
| EDA, fixture e demais arquivos anteriores | 108 arquivos EDA e fixture congelada com SHA-256 preservado; 179 arquivos anteriores fora das três alterações autorizadas sem alteração de conteúdo |
| Diff e Git | `git diff --check` sem erros; HEAD inalterado, sem exclusões, commits ou push |

Comando da suíte: `venv/bin/python -B -m unittest discover -s tests -v`, com `PYTHONPATH=src`, `MANAGERAI_RUN_LOCAL_TESTS=1`, `PYTHONDONTWRITEBYTECODE=1`, `MPLBACKEND=Agg` e TMPDIR/caches gráficos em diretórios temporários novos. A execução `-S` verifica o comportamento sem dependências opcionais, não substitui a suíte completa. As 16 comparações usam os verificadores preservados, conforme procedimentos de CURRENT_VERSION. Logs e inventários auxiliares estão em `/tmp/managerai-v43ab-jgtzgsnz/`; são temporários, não novas evidências versionadas. Não foi recalculado o hash dos aproximadamente 16 GB completos: a verificação criptográfica dos brutos cobre as 762 fontes utilizadas, complementada por metadados do clone e status Git.

Arquivos **modificados nesta fase**: `pyproject.toml` (extra opt-in `experiments`), `docs/CURRENT_VERSION.md` e `docs/PENDING.md`. Arquivos **criados**: `src/managerai/experiments/__init__.py`, `dataset.py`, `models.py`, `runner.py`; `tests/test_experimental_dataset.py`, `tests/test_experimental_models.py`; `outputs/runs/v43_ab_pl2015_16_20261017/run.json`. Nenhum arquivo removido. AGENTS, README, código/testes legados e infraestrutura V4.1 não foram modificados nesta fase; alterações locais anteriores foram preservadas.

Estado final observado (`AGENTS`, infraestrutura V4.1 e clone já constavam do estado inicial):

```text
 M AGENTS.md
 M docs/CURRENT_VERSION.md
 M docs/PENDING.md
 M pyproject.toml
?? open-data/
?? outputs/runs/
?? src/managerai/experiments/
?? src/managerai/tactical_engine_schema.py
?? src/managerai/tactical_engines.py
?? tests/test_experimental_dataset.py
?? tests/test_experimental_models.py
?? tests/test_tactical_engines.py
```

A/B concluída como experimento quantitativo reproduzível. V4.3-C continua dependente de autorização e das condições do §14.5; não foi iniciada.

## 15. V4.3-C — robustez exploratória

Dados: **StatsBomb Open Data** — [fonte e termos na revisão utilizada](https://github.com/hudl/open-data/tree/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb). Atribuição com ícone da [organização oficial](https://github.com/statsbomb), verificado em 17/10/2026:

![StatsBomb](https://avatars.githubusercontent.com/u/23416229?s=200&v=4)

### 15.1 Protocolo fixado antes dos novos resultados

Autorização: robustez e ablação locais, regressões leves, testes, documentação e commits/push somente desta fase. A reprodução inicial desde os brutos confirmou igualdade de `protocol`, `dataset` e `results` com A/B. HEAD de entrada `09b73b75c74266347a2f924a67dc95d7c803720f`, branch `main`, remoto `git@github.com:devMarcos12/ManagerAI.git`; havia alterações locais anteriores em AGENTS/docs/pyproject e módulos V4.1/A/B não rastreados. Inventário e diferenças iniciais preservados em `/tmp/managerai-v43c-5nzibun9/baseline.json`. Não atribuir esses arquivos anteriores à C.

Fixado antes da avaliação C: sete meses completos de **novembro/2015 a maio/2016**, treino expansivo com datas anteriores ao início de cada mês (mínimo 50 exemplos), avaliação com mínimo 20. Sensibilidade separada com treino móvel dos **90 dias anteriores** e mínimo 30, mesmos meses/alvos; nunca reunir os dois protocolos como partidas adicionais. Datas inteiras são indivisíveis, sem shuffle. Fronteiras não serão alteradas por desempenho; meses insuficientes serão registrados sem previsão substituta. Histórico das features continua prequential H5, estritamente anterior ao dia-alvo; pesos/scaler são congelados durante cada mês. Não há retreino intramês.

Modelos: B0, B1, OLS e Ridge α=1 anteriores; controle adicional de média dos alvos somente do treino (intercepto). Ablação das regressões: apenas histórico próprio ou apenas concedido adversário, zerando a coluna removida antes do scaler/fit e da previsão; isso não imputa um dado ausente. Não existem grupos complementares nem feature variável de mando para remover. Nenhuma seleção de atributo ou hiperparâmetro decorrerá dessas análises. Comparações pareadas nos mesmos IDs, métricas MAE/RMSE/viés, distribuição e desempenho por mês/equipe. Equipes são grupos sobrepostos; suas contagens não se somam como amostra independente.

Diagnósticos pré-fixados: excluir uma observação ou um mês por vez da avaliação **sem reajuste**; retirar simultaneamente para todos os modelos os `ceil(5% × n)` maiores erros absolutos B1, somente com n>=20, desempate data/ID. Essa remoção usa resultados observados e é apenas sensibilidade a outliers, nunca uma nova métrica principal ou estimativa prospectiva. Não calcular IC/p-valor: sete meses e 20 clubes compartilhados não sustentam aqui uma inferência confiável com dependência temporal/equipes. Relatar as diferenças descritivamente, inclusive resultados desfavoráveis.

Todos os períodos já pertencem ao dataset visto na A/B. **Toda C é exploratória pós-A/B; abril/maio incluem o teste já conhecido. Não existe teste independente novo reservado.** Não escolher janelas, atributos ou arquitetura pelo antigo teste. Sem fine-tuning, redes, integração V4.1/LLM, novas temporadas ou alteração do runtime. Estado: CONCLUÍDA como análise exploratória; resultados e validação abaixo. Publicação do delta C não inclui trabalho anterior não rastreado.

### 15.2 Janelas e resultados reais

Todos os critérios pré-fixados foram mantidos. Cada linha usa um mês inteiro e os mesmos alvos nos dois esquemas. As features continuam H5; 90 dias é limite do conjunto de ajuste, não proibição de um exemplo de treino referenciar seu próprio histórico anterior ao começo desses 90 dias.

| Mês avaliado | Treino expansivo | Treino móvel90 | Avaliação | Equipes avaliadas |
|---|---:|---:|---:|---:|
| 2015-11 | 57 | 57 | 33 | 20 |
| 2015-12 | 90 | 90 | 50 | 20 |
| 2016-01 | 140 | 120 | 40 | 20 |
| 2016-02 | 180 | 120 | 38 | 20 |
| 2016-03 | 218 | 128 | 35 | 20 |
| 2016-04 | 253 | 113 | 49 | 20 |
| 2016-05 | 302 | 122 | 28 | 20 |

330 exemplos totais/50 excluídos preservados. Cada esquema avalia 273 partidas únicas (novembro a maio), sem adicionar os 57 exemplos iniciais usados só para treino à amostra de previsão. Os dois esquemas não formam 546 partidas independentes. Para todos os modelos, n=273 por esquema. Nenhum mês bloqueado ou previsão negativa truncada.

| Esquema / modelo | MAE | RMSE | Viés | ΔMAE vs B1 | Δ% vs B1 | Meses com menor MAE que B1 |
|---|---:|---:|---:|---:|---:|---:|
| expanding / B0 | 4.384615 | 5.713822 | -1.971429 | 0.260440 | 6.3149% | 2/7 |
| expanding / B1 | 4.124176 | 5.396909 | -2.015751 | 0.000000 | 0.0000% | 0/7 |
| expanding / Média y do treino | 4.285490 | 5.588999 | -0.645782 | 0.161314 | 3.9114% | 4/7 |
| expanding / OLS | 3.994988 | 5.140741 | -0.973664 | -0.129187 | -3.1324% | 6/7 |
| expanding / Ridge α=1 | 3.995920 | 5.141355 | -0.968684 | -0.128256 | -3.1099% | 6/7 |
| expanding / OLS só próprio | 4.086623 | 5.320034 | -0.793357 | -0.037553 | -0.9106% | 4/7 |
| expanding / Ridge só próprio | 4.087036 | 5.320171 | -0.791468 | -0.037140 | -0.9005% | 4/7 |
| expanding / OLS só adversário | 4.196389 | 5.437409 | -0.751557 | 0.072213 | 1.7510% | 3/7 |
| expanding / Ridge só adversário | 4.196556 | 5.437791 | -0.750544 | 0.072380 | 1.7550% | 3/7 |
| rolling90 / B0 | 4.384615 | 5.713822 | -1.971429 | 0.260440 | 6.3149% | 2/7 |
| rolling90 / B1 | 4.124176 | 5.396909 | -2.015751 | 0.000000 | 0.0000% | 0/7 |
| rolling90 / Média y do treino | 4.285756 | 5.570507 | -0.476600 | 0.161580 | 3.9179% | 3/7 |
| rolling90 / OLS | 4.074797 | 5.167582 | -0.599850 | -0.049379 | -1.1973% | 3/7 |
| rolling90 / Ridge α=1 | 4.073650 | 5.167031 | -0.596517 | -0.050526 | -1.2251% | 3/7 |
| rolling90 / OLS só próprio | 4.150491 | 5.323408 | -0.502279 | 0.026315 | 0.6381% | 3/7 |
| rolling90 / Ridge só próprio | 4.149323 | 5.322771 | -0.501451 | 0.025147 | 0.6097% | 3/7 |
| rolling90 / OLS só adversário | 4.211645 | 5.429816 | -0.498321 | 0.087469 | 2.1209% | 3/7 |
| rolling90 / Ridge só adversário | 4.211514 | 5.429784 | -0.497933 | 0.087339 | 2.1177% | 3/7 |

MAE principal agregado pondera partidas (não média não ponderada dos sete MAEs). Viés=predito−observado. As métricas incluem distribuição assinada/absoluta e quantis lineares A/B. Não se selecionou esquema/atributo/alpha pelo desempenho. Os 6,63% A/B permanecem resultado numérico do teste conhecido; os percentuais acima pertencem a outro protocolo, sem provar reprodução independente desse ganho.

MAE mensal, n nas janelas acima:

| Esquema / mês | B0 | B1 | Média treino | OLS | Ridge |
|---|---:|---:|---:|---:|---:|
| expanding / 2015-11 | 4.703030 | 3.900000 | 4.451356 | 4.251419 | 4.255425 |
| expanding / 2015-12 | 4.552000 | 4.004000 | 4.523111 | 3.991466 | 3.995278 |
| expanding / 2016-01 | 3.425000 | 3.335000 | 3.758571 | 3.247075 | 3.249503 |
| expanding / 2016-02 | 5.021053 | 5.126316 | 4.975439 | 4.683892 | 4.683108 |
| expanding / 2016-03 | 3.908571 | 3.974286 | 3.963434 | 3.964090 | 3.962043 |
| expanding / 2016-04 | 4.187755 | 3.816327 | 3.613132 | 3.601053 | 3.598987 |
| expanding / 2016-05 | 5.157143 | 5.096429 | 5.061258 | 4.560572 | 4.561900 |
| rolling90 / 2015-11 | 4.703030 | 3.900000 | 4.451356 | 4.251419 | 4.255425 |
| rolling90 / 2015-12 | 4.552000 | 4.004000 | 4.523111 | 3.991466 | 3.995278 |
| rolling90 / 2016-01 | 3.425000 | 3.335000 | 3.790833 | 3.343897 | 3.345329 |
| rolling90 / 2016-02 | 5.021053 | 5.126316 | 4.975439 | 4.654400 | 4.651321 |
| rolling90 / 2016-03 | 3.908571 | 3.974286 | 4.019196 | 4.186763 | 4.180794 |
| rolling90 / 2016-04 | 4.187755 | 3.816327 | 3.646018 | 3.866076 | 3.859116 |
| rolling90 / 2016-05 | 5.157143 | 5.096429 | 4.890515 | 4.498279 | 4.497351 |

### 15.3 Ablação e interpretação

Apenas dois grupos presentes foram removidos. Comparação pareada com o modelo completo, mesmas partidas/treino/alpha/scaler ajustado dentro de cada ablação:

| Esquema / família | ΔMAE ao remover adversário (só próprio) | ΔMAE ao remover próprio (só adversário) | Meses em que completo melhora só próprio / só adversário |
|---|---:|---:|---:|
| expanding / OLS | 0.091634 | 0.201401 | 5/7 / 6/7 |
| expanding / Ridge α=1 | 0.091116 | 0.200636 | 5/7 / 6/7 |
| rolling90 / OLS | 0.075694 | 0.136848 | 5/7 / 6/7 |
| rolling90 / Ridge α=1 | 0.075673 | 0.137864 | 5/7 / 6/7 |

Nenhum grupo se mostrou removível sem perda agregada, mas a contribuição não é uniforme por mês. Isso não comprova causalidade, relevância independente de liga/época nem necessidade de preservar features futuras. O controle intercepto/média de treino piora o agregado frente ao completo e ao B1; nesse protocolo, o ganho completo não se resume a prever uma constante. Não há experimento que isole causalmente mando: todos os alvos são mandantes e seus históricos misturam mandos. Não eliminar automaticamente atributo nem adicionar novos grupos por esses resultados.

### 15.4 Estabilidade, dependência e outliers

OLS/Ridge têm diferenças agregadas inferiores a 0,0012 chute/jogo e sinais semelhantes: não há vencedor sustentado. Frente a B1, OLS ganha em 151/perde em122 jogos expansivos e ganha em142/perde em131 móveis; n=273 em cada, não ensaios independentes. Diferenças de MAE mensais OLS variam de -0,535856 a +0,351419 no expansivo e de -0,598149 a +0,351419 no móvel. Todos subestimam em média; reduzir viés não garante menor MAE em cada período.

| Sensibilidade sem refit | ΔMAE OLS vs B1 expansivo | ΔMAE Ridge vs B1 expansivo | ΔMAE OLS vs B1 móvel | ΔMAE Ridge vs B1 móvel |
|---|---:|---:|---:|---:|
| Excluir 14 maiores erros B1, restam259 | -0.079228 | -0.078400 | 0.029758 | 0.028019 |
| Excluir um mês: amplitude | -0.195271 a -0.078536 | -0.194762 a -0.077327 | -0.104489 a 0.018946 | -0.106344 a 0.018112 |
| Excluir um jogo: amplitude | -0.137600 a -0.122179 | -0.136590 a -0.121257 | -0.066682 a -0.036008 | -0.067613 a -0.037223 |

No móvel, retirar fevereiro ou maio inverte o sinal da diferença agregada contra B1; a remoção dos 14 outliers de referência também inverte. No expansivo, os sinais persistem nessas exclusões, mas não convertem sete blocos correlacionados em confirmação estatística. Excluir um único jogo não inverte os agregados. Essas exclusões foram pré-fixadas como diagnóstico, usam outcomes e não substituem a métrica principal nem estimam desempenho esperado após “limpar” dados.

Exposição por clube: 20 clubes com 27–28 jogos avaliados, grupos sobrepostos. OLS/Ridge ficam numericamente abaixo de B1 em14 clubes no expansivo e12 no móvel; diferenças OLS por clube vão de -0,558906 a +0,191156 no expansivo e -0,558454 a +0,398974 no móvel. Isso descreve heterogeneidade, não generalização a clubes novos, ranking ou efeitos individuais. Cada jogo aparece em duas exposições; não somar seus Ns nem interpretar os grupos como independentes.

Não foram calculados ICs ou p-valores: não foi estabelecido aqui um modelo adequado de dependência para sete blocos temporais e equipes/históricos compartilhados. Não usar bootstrap IID ou teste de eventos como se houvesse milhões de exemplos. A melhoria C é pequena, heterogênea e sensível ao protocolo; não demonstra superioridade preditiva generalizável, estratégia ideal nem utilidade causal para treinadores.

### 15.5 Reprodução e validação

Artefato único C local: `outputs/runs/v43_c_pl2015_16_20261017/run.json`, 3116613 bytes, SHA-256 `e0ff278ef9636e1d0d0cf0cf5b4dfbd6b3ef62fe0c452738cd66cadbbb391f50`. Protocolo `07e4a0ae2176d73c89e059f8e5d6a5a81aa727bccf49f61668d57bfc3c3e914d`. Referência A/B SHA-256 `29688df92f7e06aadb393eec5c8c469a3b9ef9d07732055f95401d33812889a5`; fingerprint do dataset `7b05d8df08b8f55388b9a5b73220dba7b33e77447c1d9fd39b8bc6bf988a99c5`. Python3.12.3/NumPy2.5.2 existentes; threads BLAS=1, nenhum pacote instalado. Hashes do código/pyproject, HEAD de execução, branch e fontes referenciadas estão no JSON. Não copiar novamente o dataset inteiro.

Reprodução C desde os brutos, em `/tmp/managerai-v43c-5nzibun9/c_reproduction/run.json`: configuração/fingerprint, referência e resultados completos iguais ao original, incluindo janelas, scalers/coeficientes, previsões e sensibilidades. A/B também foi reproduzida antes da análise C: protocolo, dataset e resultados completos iguais. Não se compara contexto Git como resultado numérico; comandos e destinos novos em CURRENT_VERSION §12.

| Validação real | Resultado |
|---|---|
| Suíte completa local/UI/V3/V4.1/A/B/C | **228 aprovados**, zero falhas/erros/pulos; 76,194s de suíte; 37 testes novos |
| Sem site-packages (`-S`) | 228 descobertos, **185 aprovados/43 pulados** por dependências opcionais; zero falhas/erros; 7,351s |
| Comparações independentes V3 | **16/16 aprovadas**; sem alteração dos verificadores |
| Python/links | 59 arquivos AST válidos; 16 destinos Markdown locais existentes, zero quebrados |
| Preservação | A/B, V4.1, núcleo, testes anteriores, pyproject, README e AGENTS sem alteração de conteúdo nesta fase; EDA e fixture preservadas |
| Dados | Metadados de8.980 arquivos do clone preservados e clone limpo; SHA-256 das762 fontes do experimento reconferidos; não se afirma hash integral dos16GB |

Suíte: `MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg venv/bin/python -B -m unittest discover -s tests -v`, com TMPDIR/caches gráficos em temporários exclusivos. Verificação independente: `PYTHONPATH=src venv/bin/python -B outputs/v22_v3_validation/check_metrics.py`. Logs, inventários e cópias de reprodução ficam apenas em `/tmp/managerai-v43c-5nzibun9/`. Nenhum relatório Markdown novo, gráfico descartável, checkpoint ou dataset copiado foi criado na árvore operacional.

### 15.6 Decisão e próximos passos

**C concluída como estudo de robustez exploratório, sem exigir melhora de Ridge.** Recomenda-se manter OLS como referência simples de pesquisa e Ridge como controle, sem declarar vencedor; não há justificativa atual para redes, Transformers, modelos pré-treinados ou fine-tuning. B0/B1 e controle de média do treino devem continuar em futuras comparações.

| Próximo passo | Dependência | Aceite / estado |
|---|---|---|
| Avaliação independente | Nova temporada comparável, autorização de uso e auditoria de schemas/cobertura/anotações | Pré-registrar alvo/features/alpha/janelas/margem útil antes de olhar seus erros; **não iniciado** |
| Robustez estatística | Mais períodos e desenho adequado à dependência temporal/equipes | Definir método e cobertura antes do experimento; não reciclar este teste para tuning; **pendente** |
| Utilidade prática | Professor/comissão define tolerância de erro, viés/custo/abstenção | Revisão humana separada de qualidade preditiva; nenhum ganho tático demonstrado |
| Fine-tuning | Tarefa/representação e pesos compatíveis, licença, orçamento, dados/rótulos e ganho sobre modelos simples | **Sem evidência suficiente; não autorizado nem executado** |
| Integração futura | Contrato quantitativo com proveniência/suficiência e avaliação independente satisfatória | Migração própria, sem forçar previsão em TacticalEngineOutput; **não iniciada** |
| Publicação dos pré-requisitos anteriores | RESOLVIDA NA CORE-00, §16 | Origem conferida; V4.1 em `d59ba93`, A/B/dependência em `d075d33`, registros documentais consolidados; C preservada |

No encerramento C, o branch contendo somente seu delta não possuía todos os pré-requisitos A/B/V4.1. **CORE-00 resolveu esse bloqueio**, sem reescrever a C e identificando a origem do trabalho anterior (§16). O artefato A/B contém linhas/dados derivados e permanece local; C também fica local, ignorada por Git. Compartilhamento dos artefatos/dados/pesos exige confirmação específica dos direitos; publicação de código não concede esses direitos. Nenhuma integração LLM, fine-tuning ou V4.4 foi iniciada.

### 15.7 Arquivos e Git

Registro histórico do encerramento C, anterior à resolução de versionamento na CORE-00 (§16).

Modificados nesta fase: `.gitignore`, `docs/CURRENT_VERSION.md`, `docs/PENDING.md`. Criados: `src/managerai/experiments/robustness.py`, `src/managerai/experiments/robustness_diagnostics.py`, `tests/test_experimental_robustness.py`, `tests/test_robustness_diagnostics.py` e o único artefato C local/ignorado. **Nenhuma exclusão**; temporários da execução estão fora do checkout. `.gitignore` protege brutos e novos runs, sem ignorar outputs inteiro, fixtures ou exemplos congelados. Nenhum arquivo de venv, bruto, segredo ou checkpoint será adicionado.

Branch de desenvolvimento: `feat/v4.3c-robustness`, separado de main. Remoto conferido: `git@github.com:devMarcos12/ManagerAI.git`; main remoto coincide com HEAD inicial `09b73b75c74266347a2f924a67dc95d7c803720f`. Commit de código C: `a1e3cd115ef75818c798694733becf683a8ae341` (`feat(experiments): add exploratory walk-forward robustness study`), contendo somente quatro Python novos e `.gitignore`. O commit documental contém somente status/seções C; seções/documentos preexistentes, módulos V4.1/A/B, pyproject e artefatos anteriores permanecerão fora desses commits. O índice dos documentos foi construído com HEAD + apenas a seção/status C, preservando as versões completas locais. Isso evita incluir alterações anteriores só porque compartilham o mesmo arquivo. Hashes dos commits e resultado efetivo do push serão informados na entrega; não há merge, PR, force-push ou reescrita.

## 16. CORE-00 — estabilização e integração

### 16.1 Auditoria e origem

Entrada: `feat/v4.3c-robustness` em `e91e55dd51081bd381f69097353ec86ca5bf7583`, main local/remoto `09b73b75c74266347a2f924a67dc95d7c803720f`. Havia quatro arquivos modificados (AGENTS, dois docs, pyproject) e nove pré-requisitos não rastreados. Baseline, diff e hashes em `/tmp/managerai-core00-ftkm4jw5/baseline.json`. Todos os nove coincidiram com o inventário inicial C; módulos também coincidiram com os hashes dos runs. Origem identificada: implementações das sessões V4.1 e A/B, anteriormente mantidas locais por limitação do escopo C. Nenhuma alteração de autoria incerta foi incorporada silenciosamente.

GitHub consultado: repositório público `devMarcos12/ManagerAI`, nove Issues antigas (#1–#9) e nenhum PR anterior. Não há rulesets nem proteção obrigatória de main na auditoria inicial; reconferir condições no PR antes do merge. Nenhuma Issue foi criada, alterada ou fechada. Branch de integração `integration/core-00` descende dos dois commits publicados C; sem recriação, rebase, reset, clean ou push forçado. Branch compartilhado C será preservado.

### 16.2 Implementações versionadas e correções

- `d59ba93`: contratos/adaptador e testes V4.1, três arquivos, origem registrada no commit.
- `d075d33`: quatro módulos A/B, dois testes e extra `experiments` no pyproject; todos os pré-requisitos C passam a estar rastreados.
- `80abaa0`: correção real de instalação, `experiments/paths.py`, proveniência do pacote executado e referência A/B reconstruível; nove testes de regressão.
- `965d5b4`: workflow GitHub Actions com perfis core/opcionais, wheel instalado, Python3.12, testes portáveis e contratos; dados reais ficam fora do runner.
- Documentação: consolidação dos registros locais anteriores V4.1/V4.2/A/B, sem apresentar testes antigos como execução CORE-00; README e regras permanentes atualizados.

Primeiro teste de wheel limpo descobriu228 testes, com um erro e43 pulos: proteção de destino usava a raiz errada sob site-packages. A causa foi corrigida, sem modificar a asserção. A exigência do SHA binário A/B também impediria reproduzir a C sem distribuir um run antigo. Agora protocolo/dataset são exatos e todos os resultados são conferidos por assinatura a oito casas. Essa regra de referência não altera nem arredonda valores guardados, não afrouxa cortes de tempo e não escolhe modelos por resultado. O SHA histórico continua registrado, junto ao hash real da nova referência. Nenhuma fórmula/métrica, pipeline determinístico, contrato legado, interface ou adaptador V4.1 foi alterado.

### 16.3 Validação limpa real

Checkout temporário clonado apenas de commits em `/tmp/managerai-core00-ftkm4jw5/checkout`. Ambientes core-env/full-env novos e isolados, sem herdar o venv funcional, instalaram pelo pyproject e por requirements+experiments a partir do PyPI. Nenhuma atualização no ambiente original. NumPy2.5.2/Streamlit1.65.0/Matplotlib3.11.2 diretos mantidos; transitivas foram resolvidas no ambiente novo (não são lock). `pip check` passou. Os imports com `-I` apontaram para os wheels instalados, sem depender de arquivos não versionados.

| Execução corrente | Descobertos | Aprovados | Pulados | Falhas/erros | Tempo da suíte |
|---|---:|---:|---:|---:|---:|
| Wheel core sem opcionais | 237 | 194 | 43 | 0 | 6,489s |
| Sem site-packages (`-S`/src) | 237 | 194 | 43 | 0 | 6,638s |
| Wheel UI/V3/NumPy sem StatsBomb | 237 | 227 | 10 | 0 | 14,619s |
| Wheel completo com dados externos | 237 | 237 | 0 | 0 | 66,849s |
| Comparações independentes | 16 | 16 | 0 | 0 | Não cronometrado separadamente |

Os dez pulos portáveis são integrações reais opt-in, não falhas escondidas. Dados foram provisionados somente depois dos testes portáveis por symlink ignorado para o clone original; nada foi copiado para o Git. Os testes preservaram a fixture schema1.0.0, exemplos schema1.1.0, contratos V4.1, dados StatsBomb e EDA. Scripts de EDA não foram executados. Foram conferidos 61 arquivos Python, 17 destinos Markdown locais (zero quebrados), hashes dos108 arquivos EDA e das762 fontes do experimento, além dos metadados dos8.980 arquivos do clone limpo. Não se afirma hash integral dos16GB. Comandos de reprodução/instalação e limites de CI em CURRENT_VERSION §13.

Reprodução A/B desde os brutos, por wheel instalado, sem usar o run histórico como entrada: protocolo, dataset e resultados **exatamente iguais** ao original. A referência reconstruída passou a verificação congelada e foi usada para executar C: protocolo, fingerprint e resultados completos C também foram **exatamente iguais** aos originais (janelas, coeficientes/scalers, previsões e diagnósticos). Apenas metadados de execução e identificação do novo artefato A/B variaram, conforme esperado. Runs novos apenas no checkout temporário ignorado; artefatos originais A/B e C preservados. Logs/resultados auxiliares e freeze de transitivas ficam somente em `/tmp/managerai-core00-ftkm4jw5/`.

### 16.4 Publicação, CI e pendências

Publicação: branch `integration/core-00`, base main, [PR #10](https://github.com/devMarcos12/ManagerAI/pull/10). A primeira execução GitHub `39086601248` foi rejeitada na validação do workflow antes de executar testes: contexto `runner.temp` em env do job. Os diretórios foram corrigidos para caminhos /tmp válidos do runner Ubuntu; a execução seguinte [39086750802](https://github.com/devMarcos12/ManagerAI/actions/runs/39086750802), no commit `db6c49d`, **passou nos dois perfis core/opcionais**. Alterações documentais posteriores também precisam dos checks verdes no head atual antes do merge normal. Esta revisão reúne todos os pré-requisitos antes ausentes. O PR rastreia o estado publicado e o merge em main; usar seus checks atuais como gate. Não fazer merge enquanto houver falha, conflito ou revisão obrigatória. Não apagar branches compartilhados. A autorização CORE-00 permite merge normal apenas com validações verdes e regras atendidas.

Permanecem fora desta missão: teste esportivo independente em outra temporada, definição de ganho útil e avaliação por especialistas, licença para redistribuir dados/derivados/pesos, redundância externa dos backups e lock completo de transitivas. Fine-tuning, integração LLM, frontend de terceiros, novas fórmulas, planejamento definitivo do Core e roadmap de Issues não foram iniciados.

## 17. CORE-01 — auditoria e provisionamento StatsBomb (implementação local)

### 17.1 Contrato e diagnóstico

O contrato `src/managerai/statsbomb_snapshot.json` fixa a revisão `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`, origens GitHub `hudl/open-data` e alias `statsbomb/open-data`, SHA-256 de controles e 80 calendários, IDs/hash e cobertura por temporada, órfãos, totais e os dois recortes V3 já permitidos. Os valores de cobertura foram calculados pelo `data_inventory.inventory` no clone presente e conferidos com todas as 80 linhas de §7.2: **80/80 pares sem divergência de partidas/360**. Totais observados: 24 competições, 80 pares, 3.961 partidas, 4.235 arquivos de eventos, 4.235 escalações, 426 arquivos 360 e 274 órfãos de cada tipo eventos/escalações. Presença de arquivo não atesta conteúdo semântico.

**Divergência material encontrada antes de fixar hashes:** o clone local Windows em `open-data/` tem remoto `https://github.com/statsbomb/open-data.git`, HEAD correto e `git --no-optional-locks status --porcelain` vazio, mas o checkout converteu LF dos blobs Git para CRLF em README/JSONs. `open-data/data/competitions.json` tem SHA-256 em disco `c5f10d2811ace6057ff8e414bfd93c2c34c27dddb2199d9fc29ffc425bc30425` (igual ao valor anteriormente observado), enquanto `git show HEAD:data/competitions.json` dá `e6cd42f5d8956d6aa30fb917ce8d4c3b3df1879a93f02f8feba820930a6971fa`. Para `README.md`: disco `c01028f949815e9e4d1f8a25bd4c2e7013017538ce69b17246e4b33e3e4a8212`, blob `98a757466c4d931dba4b6c4290c55c2fe74e4550d7455bbe05fd884dc831aff3`. `LICENSE.pdf` coincide nos dois (`a5462e69aeb71a39268b760b110c5c2190a2e0cee3015ba976f66bd71f6c2bb4`). Os **42 hashes de fontes** de `outputs/mvp_demo_city_arsenal/report.json` coincidem com os respectivos blobs Git, zero diferenças; o teste `test_local_data.py::test_inventory_and_historical_report` diverge dos bytes locais. A própria fixture tem SHA-256 do blob Git `424389e2af0afee96eff3d5a7ef79d74f914f12f0965a052d361fe657fd56b08` e SHA-256 do checkout CRLF `473164bc6d84d3a8e4aca72686fc27b91e714005f2bd34238290ca71a8baca3f`, sem modificação registrada pelo Git. Portanto o contrato fixa hashes dos blobs Git, que reproduzem a fixture, e o verificador **recusa** a conversão CRLF. Não se escolheu silenciosamente entre hash local e documentação antiga.

`statsbomb_provisioning.verify_snapshot` usa `LocalData`/`load_season`, enumera presença e consulta Git local sem rede nem escrita. A CLI `verify-data` gera JSON determinístico e retorna 0/2. O modo rápido não abre eventos/escalações/360 integralmente; Git limpo sozinho não bastou neste Windows, então hashes canônicos de controles/calendários também são obrigatórios. No clone local atual, `python -B -m managerai --data-root open-data/data verify-data` retornou **2**, `status=incompatível`, 3 erros `LINE_ENDINGS_CHANGED` (README, catálogo e primeiro calendário afetado) e 2 informações `ORPHAN_FILES`; 3.961 partidas foram contabilizadas. O clone foi apenas lido, sem checkout/reset/configuração. O guia novo ensina a criar **outro clone** com `git clone -c core.autocrlf=false`, sem substituir o existente.

Validação real adicional: `git clone -c core.autocrlf=false --shared --local open-data C:\Users\matheuscb\AppData\Local\Temp\managerai-core01-compatible-20261025-a` criou clone temporário novo **sem rede** e sem modificar a fonte. HEAD ficou na revisão fixada, `core.autocrlf=false`, worktree limpo e SHA-256 de `data/competitions.json` igual ao blob Git `e6cd42f5...`. O clone local atribui por padrão `origin` ao caminho local; somente no **temporário** foi ajustado para `https://github.com/hudl/open-data.git`, refletindo a origem GitHub já observada no clone fonte. Isso testa o contrato, mas não prova obtenção independente pela URL. `venv/Scripts/python.exe -B -m managerai --data-root <temporário>/data verify-data` retornou **0**, `status=compatível`, 3.961 partidas, 2 informações `ORPHAN_FILES` e nenhum erro/aviso. `pipeline.analyze` para City × Arsenal, com dados desse clone, produziu `report.to_json()` igual ao conteúdo lido da fixture preservada e 42 fontes. O clone original e a fixture não foram escritos.

### 17.2 Validação desta execução e limites

Ambiente: Windows PowerShell, Python **3.14.7** do `venv/Scripts/python.exe`; Python 3.12 não está instalado aqui. `PYTHONDONTWRITEBYTECODE=1`, `-B`, temporários em `TEMP/TMP` longo e, para UI, `MPLBACKEND=Agg`/`MPLCONFIGDIR` temporário. Nenhum pacote foi instalado nesta fase. Resultados reais, separados dos números históricos da CORE-00:

| Comando / perfil | Aprovados | Falhas | Erros | Pulos | Código / observação |
|---|---:|---:|---:|---:|---|
| `venv/Scripts/python.exe -B -S -m unittest discover -s tests -p test_statsbomb_provisioning.py -v`, `PYTHONPATH=src` | 10 | 0 | 0 | 0 | 0; fixtures sintéticas, sem rede/dados reais |
| `venv/Scripts/python.exe -B -S -m unittest discover -s tests -q`, `PYTHONPATH=src` | 201 | 3 | 0 | 43 | 1; três subcasos de fixture byte a byte em `test_tactical_engines.py:272` falham porque arquivos preservados em disco têm CRLF e serialização usa LF |
| `venv/Scripts/python.exe -B -m unittest discover -s tests -q`, `PYTHONPATH=src`, sem dados opt-in | 234 | 3 | 0 | 10 | 1; mesmas três falhas LF/CRLF. Primeira tentativa teve ainda 1 timeout AppTest; o teste isolado e as repetições completas passaram sem esse erro |
| `venv/Scripts/python.exe -B -S -m unittest discover -s tests -p test_local_data.py -v`, `MANAGERAI_RUN_LOCAL_TESTS=1` | 0 | 1 | 0 | 0 | 1; fixture congelada diverge dos hashes dos brutos CRLF locais |
| Mesmo comando completo `-B -S -m unittest discover -s tests -q`, em checkout temporário LF com arquivos CORE-01 sobrepostos | 204 | 0 | 0 | 43 | 0; sem dados opt-in |
| Mesmo comando completo `-B -m unittest discover -s tests -q`, em checkout temporário LF com opcionais | 237 | 0 | 0 | 10 | 0; sem dados opt-in |
| Mesmo comando completo `-B -m unittest discover -s tests -q`, no temporário com ligação ao clone StatsBomb LF e `MANAGERAI_RUN_LOCAL_TESTS=1`, `PYTHONUTF8=1` | 247 | 0 | 0 | 0 | 0; integração real completa |

O checkout portátil temporário foi clonado do Git principal com `core.autocrlf=false`, sparse checkout de código/testes/fixtures e sobreposição dos dez caminhos CORE-01 ainda não commitados; não é validação de pacote instalado nem prova de arquivos já rastreados em commit. Uma ligação **somente nesse temporário** apontou `open-data/` ao clone StatsBomb LF temporário. A primeira execução opt-in falhou em três subcasos (2 falhas, 1 erro) porque o Python Windows usou `cp1252` em leituras sem `encoding=` nos testes legados; a repetição com `PYTHONUTF8=1` passou 247/247. Nenhum arquivo fonte, dado ou fixture foi modificado para obter o resultado.

Checagens adicionais: 16 links Markdown locais nos quatro documentos afetados, zero ausentes; as 80 linhas de cobertura de §7.2 coincidem com o manifesto. A declaração `tool.setuptools.package-data` foi lida com `tomllib` e o arquivo existe no checkout, sem construir o wheel. O comando real `verify-data` retornou 2 no clone original e 0 no clone temporário LF, conforme os diagnósticos esperados. O teste de wheel atualizado com `python -I` **não foi executado**: o venv contém uma instalação anterior do ManagerAI, mas não `setuptools` para construir/instalar o wheel novo; a validação era condicional à ausência de instalação adicional. A declaração de package-data não substitui o teste do wheel. A CI não foi alterada nem executada localmente em Ubuntu; continua sem StatsBomb, dados, cache de brutos ou segredos.

`git diff --check` passou sem erros de whitespace, exibindo apenas avisos do Git sobre futura conversão LF→CRLF dos arquivos editados. `git check-attr eol` confirmou `lf` para os três relatórios congelados após criar `.gitattributes`; isso protege **novos** checkouts Windows sem mudar bytes das fixtures atuais. `git status --short` continha somente os dez caminhos CORE-01 listados nesta fase; `open-data/`, EDA, runs e fixture não aparecem como alterações do Git principal. O clone independente permaneceu no mesmo HEAD e com status limpo. A pasta EDA protegida conserva 108 arquivos observados; não foram calculados hashes integrais da EDA nesta fase e nenhum gerador foi executado.

### 17.3 Status e próximos passos próprios da CORE-01

**Implementação e suítes de código fonte validadas; aceite integral pendente do wheel atualizado.** Repetir o provisionamento diretamente da URL oficial em destino novo no ambiente do próximo integrante e guardar o JSON de `verify-data`; o clone temporário local demonstrou o procedimento sem download. Validar o wheel atualizado com `python -I` em ambiente limpo, usando ferramenta de build já disponível/autorizada. O checkout Windows existente ainda tem CRLF nas três fixtures; preservá-las e não reescrevê-las nesta fase. Uma pessoa responsável ainda deve confirmar finalidade, distribuição/uso comercial e autorizações StatsBomb; nenhum nome foi presumido. Não houve commit, push, PR, download ou alteração do clone original, dados/EDA/runs/fixture nesta fase.

## 18. CORE-02 — matriz e gates portáveis (25/10/2026)

O [protocolo](CORE02_CERTIFICATION.md) foi fixado antes da inspeção agregada. `season_audit.py` usa o contrato CORE-01 e os calendários, sem ler eventos na matriz; diagnostica taxonomia, calculabilidade e orientação por partida em funções separadas. A auditoria integral de um candidato exige `verify_snapshot` compatível, lê somente o par selecionado, registra fontes/hashes e **não** altera a allowlist. São funções e testes portáveis; não equivalem a uma certificação real. O contrato CORE-01, a origem/revisão, guia, verificador e testes estão rastreados no HEAD `144d632`, mas o wheel instalado neste venv tem `statsbomb_provisioning.py` com SHA-256 diferente do fonte atual; o gate de wheel CORE-01 permanece pendente. Nenhuma responsabilidade CORE-01 foi reimplementada aqui.

A [matriz canônica desta execução](season_coverage_core02.json), fingerprint `a646c8d6a4259c00598378a258e3babcd546e86cf548d8a5a7047e0667bbeae3`, recalculou **80 pares, 3.961 partidas, zero eventos/escalações faltantes por presença e 426 arquivos 360 presentes**. O clone local continua na revisão Git `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb` e limpo, porém `verify-data` retornou `status=incompatível` por `LINE_ENDINGS_CHANGED` em README/catálogo/calendário; `ORPHAN_FILES` é informativo. A matriz marca a revisão como alegada pelo contrato e preserva hash esperado e observado por calendário. São **24 pares inconclusivos** com H5 de calendário positivo e **56 inelegíveis** para comparação H5 bilateral. Os pares previamente permitidos na V3 são identificados separadamente; seu status anterior não foi reavaliado ou revogado. Nenhum campo nulo de calculabilidade foi transformado em zero.

| Candidato | Partidas | H5/H10 bilateral de calendário | Estrutura/taxonomia/função | Geometria/orientação | Tempo | Decisão CORE-02 |
|---|---:|---:|---|---|---|---|
| La Liga 2015/16 `(11,27)` | 380 | 330/280 | Não auditadas nos eventos | Não auditadas | Política sintética testada; recorte real pendente | Inconclusivo, não permitido |
| Serie A 2015/16 `(12,27)` | 380 | 330/280 | Não auditadas nos eventos | Não auditadas | Política sintética testada; recorte real pendente | Inconclusivo, não permitido |
| Ligue 1 2015/16 `(7,27)` | 377 | 327/276 | Não auditadas nos eventos | Não auditadas | Política sintética testada; recorte real pendente | Inconclusivo, não permitido |

Com `--candidate-competition-id 11 --candidate-season-id 27` no clone atual, a CLI retornou código **2**, mensagem `Snapshot incompatível com CORE-01; auditoria real recusada.` e não criou arquivo. Isso é recusa de gate, não resultado de auditoria funcional da La Liga.

Os H5/H10 acima foram recalculados dos calendários CRLF locais e **não** são alvos com 21+26+3 indicadores calculáveis, nem amostras independentes. Não se leu evento real de nenhum candidato. PL 2015/16 continua permitida no código; La Liga 2020/21 continua permitida para abstenção, com H5 bilateral zero nesta matriz. A política de datas testada usa apenas competição/temporada, exclui alvo/futuro/dia inteiro e não repõe lacunas. A data de disponibilização original das anotações segue desconhecida; versões e fidelidades heterogêneas, domínio, dependência entre partidas/equipes e orientação ainda precisam de avaliação por recorte.

### 18.1 Revisão de conformidade da implementação

Foi identificada uma divergência entre o protocolo e a classificação da matriz: em `src/managerai/season_audit.py`, a expressão `mismatch` compara também `three_sixty` com a contagem do contrato. Como consequência, uma diferença ou ausência de arquivos 360 pode resultar em status `reprovado`, embora o gate 1 do protocolo considere 360 informativo e declare que sua ausência não reprova, pois a V3 não consome esses arquivos. **A correção e o teste sintético para 360 ausente/parcial continuam pendentes; não se deve interpretar esse status como reprovação científica do recorte até corrigir a regra.** O snapshot desta matriz tinha 426 arquivos 360 conforme o contrato, então esse desvio não explica os status atuais dos três candidatos.

O campo `files.related_orphans` é null em cada linha. Os arquivos órfãos são identificados globalmente, mas não pertencem de forma verificável a uma competição/temporada porque não constam do catálogo; não atribuí-los por proximidade de IDs ou outro critério inferido. Essa limitação está documentada, e a matriz não deve apresentar órfãos globais como cobertura de uma temporada específica.

Os testes CORE-02 aprovados nesta fase cobrem a matriz sintética, cortes temporais e leituras de eventos/escalações do alvo/futuro, taxonomia básica, geometrias e orientação sintéticas. Eles não substituem auditoria de conteúdo dos três candidatos, nem validação do wheel CORE-01 com `python -I`, suíte completa sem falhas ou teste real opt-in. Esses gates permanecem pendentes conforme a seção 18 e não há recorte novo certificado.

Validação desta fase: `venv/Scripts/python.exe` Python 3.14.7, `PYTHONPATH=src`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; sem instalação ou rede. `-B -S -m unittest discover -s tests -p test_season_audit.py -q`: **16 aprovados**, zero falhas/erros/pulos. `-B -S -m unittest discover -s tests -p test_statsbomb_provisioning.py -q`: **10 aprovados**, zero falhas/erros/pulos. Suíte `-B -S -m unittest discover -s tests -q`, com TEMP curto original: 262 descobertos, **5 falhas e 43 pulos**, das quais duas falhas de comparação de caminho curto/longo do TEMP. Com TEMP longo explícito: 263 descobertos, **217 aprovados, 3 falhas, 43 pulos**. Perfil com opcionais, mesmo TEMP longo, `-B -m unittest discover -s tests -q`: 263 descobertos, **250 aprovados, 3 falhas, 10 pulos**. As três falhas remanescentes são subcasos preexistentes de comparação byte a byte dos três relatórios congelados com CRLF neste checkout Windows; nenhum arquivo foi regravado para fazê-los passar. O teste de wheel atualizado com `python -I`, os opt-in com clone compatível e os candidatos reais não foram executados. Uma tentativa opcional de checkout LF temporário via `git clone --local` falhou por permissão de hardlink na pasta `.git` antes dos testes; não conta como validação.

Próximo gate: validar o wheel CORE-01 atualizado instalado em ambiente isolado sem pacote adicional não autorizado; provisionar clone novo LF em destino separado e confirmar `verify-data=compatível`; executar auditorias integrais dos três candidatos, registrar duração/bytes/fontes e testes reais opt-in; revisar versões, métricas e orientação segundo o protocolo; só então decidir cada inclusão explícita na allowlist. A meta de expansão permanece tecnicamente inconclusiva. Dados, EDA, relatórios e fixture congelada não foram alterados nesta fase; diff/status e hashes finais são conferidos no encerramento.

## 19. UI — prévia JSON extensa na V3 (30/10/2026)

Relato: navegador deixa de responder ao analisar com V3. No checkout Linux, a análise City × Arsenal de 08/05/2016, janela 10, terminou em 6,22 s e produziu JSON UTF-8 de 8.657.572 bytes e 211.447 linhas. Antes da correção, `results` enviava esse objeto inteiro para `st.json` com expansão padrão, inclusive dentro do expander fechado. O AppTest anterior passou os três testes V3 em 21,874 s; portanto não reproduziu travamento no servidor nem comprova a causa exclusiva do sintoma no navegador.

Mitigação em `src/managerai/streamlit_ui.py`: serializar uma vez para o download; limitar a prévia integral a 512.000 bytes, sempre recolhida; acima desse limite mostrar somente schema/metadados e orientar para o download completo. Indicadores, hipóteses, gráficos, fórmulas e schemas não foram alterados. `tests/test_v3_ui.py` verifica no confronto real que a prévia é limitada e recolhida, o download preserva exatamente o JSON completo e os dois gráficos continuam presentes.

Validação no `venv/bin/python` Python 3.12.3, Streamlit 1.65.0 e Matplotlib 3.11.2, sem instalação. Prefixo dos dois comandos: `MPLCONFIGDIR=/tmp/managerai-mpl PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests MANAGERAI_RUN_LOCAL_TESTS=1 venv/bin/python -B -m unittest discover -s tests`.

| Sufixo do comando | Aprovados | Falhas/erros/pulos | Tempo |
|---|---:|---:|---:|
| `-p test_v3_ui.py -v` | 3 | 0/0/0 | 22,098 s |
| `-p test_streamlit_ui.py -v` | 10 | 0/0/0 | 7,474 s |

Suíte completa e revisão visual em navegador real não executadas nesta tarefa. AppTest não mede responsividade do navegador. Próximo passo: reiniciar o Streamlit e repetir a demonstração com V3 no navegador do usuário; investigar console/terminal se o sintoma persistir. Não houve commit/push, instalação, geração de relatórios em disco nem alteração dos dados, da EDA ou das fixtures congeladas. Os gates CORE-01/02 continuam pendentes.


## 20. Core de serviço, API e pesquisa de IA — 31/10/2026

Esta seção prevalece para o estado da implementação nova. As evidências anteriores continuam históricas e não são contagens desta execução. Entrada: `main`, HEAD `37f2a13afe221454c78f2c7103d6999ddee6a53b`. Quatro alterações preexistentes preservadas: CURRENT_VERSION, PENDING, streamlit_ui e test_v3_ui. Patch inicial preservado em `/tmp/managerai-final-core/preexisting.patch`; nenhuma alteração própria em streamlit_ui/test_v3_ui.

### 20.1 Implementação e limites

Serviço versionado 2.0.0 em `service_schema.py`/`service.py`; API FastAPI em `api.py`; política comum em `sufficiency.py`; LLM local opcional em `explanation.py`. Pedidos validam contexto, corte, elenco com fonte/data e restrições. Ausência de elenco limita sugestões individuais, sem bloquear análise coletiva. Planos reutilizam evidências/regras reais; preferências só ordenam opções já sustentadas. JSON e Markdown preservam condições, riscos, limites e proveniência. Schemas legados 1.0.0/1.1.0 continuam intactos.

LLM: seleção validada de afirmações autorizadas, materializadas em português pelo Core. Sem prosa livre, ferramentas, recalcular números, chave de API ou chamadas pagas. Notas não entram no prompt. Provedor Ollama apenas loopback, modelo configurado no servidor, digest registrado; modo `required` falha explicitamente, `optional` conserva relatório determinístico. Modelos desconhecidos não recebem fallback silencioso.

Correção 360: removida a divergência 360 da reprovação da matriz, mantendo aviso e teste combinado com verify-data para ausência/cobertura parcial; eventos obrigatórios ausentes continuam incompatíveis/reprovados. Nenhuma alteração da allowlist V3. Linux atual: verify-data `compatível`, revisão `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`, remoto `hudl/open-data`, duas informações de órfãos e nenhum erro. Isso não altera o resultado histórico do checkout Windows CRLF nem certifica novas temporadas.

Contrato HTTP, instalação e exemplos: [BACKEND_API.md](BACKEND_API.md). API síncrona, um worker, janela até 20, uma análise concorrente, limite de dez análises/minuto e armazenamento volátil de oito relatórios/300 s, até 32 MB cada. Acesso por token aleatório de posse; serviço local, sem autenticação multiusuário. Reinício perde relatórios. Sem banco/fila/frontend novo. CI alterada para incluir extra api no perfil opcional, mas não executada remotamente nesta tarefa.

### 20.2 Recursos, direitos e protocolo

Python funcional 3.12.3; CPU i7-1165G7, oito CPUs lógicas, RAM total 15 GiB, aproximadamente 8,6 GiB disponível no início, disco livre 204 GiB. CUDA indisponível no PyTorch 2.14.0; não há nvidia-smi. Ollama local disponível: Qwen2.5 1.5B (~986 MB) e Llama3.1 8B (~4,92 GB). Apenas o menor foi usado, sem download de outro modelo Ollama. Seu digest: `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`.

`api-env`, `train-env` e `full-env` foram criados em `/tmp/managerai-final-core/`. O ambiente de treino reutiliza por .pth as bibliotecas já existentes do venv, instalando Transformers/PEFT somente no diretório isolado; isso não é instalação limpa de toda a pilha de treinamento. A validação do pacote/backend usa ambiente limpo separado. Nenhum pacote foi instalado no venv funcional. A primeira tentativa pip no sandbox falhou por DNS; repetição autorizada fora do sandbox baixou dependências públicas. TestClient também bloqueou no sandbox por restrição de sockets; testes HTTP executados fora dessa restrição, sem provedor externo.

O protocolo [core_ai_protocol.json](core_ai_protocol.json) foi gravado antes das avaliações; identidade canônica registrada nos artefatos. Distingue previsão de contagem, revisão tática e explicação. Sem rótulos táticos de especialistas, D1 permanece bloqueada: placar/regras não foram usados como tática ideal. Nenhuma revisão humana foi realizada. Rubrica/formulário em [tactical_review.schema.json](tactical_review.schema.json); casos e fontes preparados pelo verificador backend não são avaliações. Requisito acadêmico específico do professor não foi encontrado nos documentos operacionais; ajuste de explicação não pode ser anunciado como cumprimento de aprendizado de decisão tática.

Uso dos dados continua local/restrito; nenhuma redistribuição, publicação ou autorização comercial inferida. Para treinamento de explicação foram usados somente casos sintéticos locais, sem eventos StatsBomb, dados pessoais reais ou avaliação de especialistas. Licença do modelo base verificada nos metadados oficiais Apache-2.0; revisão fixada `12fd25f77366fa6b3b4b768ec3050bf629380bac` de HuggingFaceTB/SmolLM2-135M-Instruct. Download público de 271.177.292 bytes, em `outputs/runs/core_ai_model_20261031/`, ignorado pelo Git, com README/config/tokenizador/pesos e `provision.json` com SHA-256. Não houve gasto pago.

### 20.3 Avaliação quantitativa independente

Runner `experiments/independent.py`; auditoria integral específica de contagem parametrizada em `build_shots_dataset`, sem certificar geometria/V3. Treino PL2015/16 até 06/02/2016: 198 exemplos. Teste La Liga2015/16 a partir de 09/04/2016: 69 exemplos. É avaliação entre competições no mesmo período, não temporada futura. Cada recorte teve conteúdo auditado para o alvo de contagem; features H5 congeladas antes da passagem de labels, sem alvo/dia/futuro ou reposição. Todos os IDs, exclusões, fontes e dependências estão no artefato. Janelas/equipes compartilhadas não são observações IID.

Primeira execução real em `outputs/runs/core_ai_independent_20261031/evaluation.json`: MAE B0=3,9130434783; B1=3,3869565217; OLS=3,3503165445; Ridge=3,3504899821. OLS melhora 0,0366399772 chute (1,0818%); Ridge 0,0364665396 (1,0767%). Ambas falham os critérios pré-fixados de 0,2 chute E 5% contra B1. Nenhum modelo promovido. Métricas mensais, RMSE, viés e diferenças pareadas por jogo estão preservados, sem IC/p-valor IID. Previsão de chutes não avalia eficácia de planos.

### 20.4 Inferência real, ajuste e validação final

Primeiro verificador real da API: `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 /tmp/managerai-final-core/api-env/bin/python -u -B scripts/check_backend.py --data-root open-data/data --output-dir outputs/runs/core_ai_backend_real_20261031 --with-ollama`. Três casos com HTTP 200, explicação real `generated` e exportação JSON equivalente: City V3 (4 planos, 27,863 s, 4.947.691 bytes); Real/Barcelona insuficiente (0 planos, 9,438 s, 3.274.645 bytes); notas com injeção (2 planos, 10,448 s, 152.823 bytes). LLM durou 19,884/4,494/7,799 s. Isso não é prova visual de navegador; nenhuma ferramenta de inspeção visual estava disponível. Os bytes correspondem àquela revisão local; campos posteriores de comparação/contrato podem mudar o tamanho.

Treinamento real executado, com 96 casos sintéticos de treino, 24 de validação e 40 de teste, separados antes das derivações; seed 42, duas épocas, LoRA r8/alpha16 em q_proj/v_proj, lr 0,0005, até 768 tokens, quatro threads CPU. Avalia modelo base com o mesmo prompt, ajustado e template. Saída restrita exige seleção integral de IDs das afirmações autorizadas. Essa tarefa limitada de montagem de explicação não aprende decisão tática. Artefatos em `outputs/runs/core_ai_lora_20261031/`; resultados finais e carregamento do adaptador registrados abaixo.

### 20.5 Rastreabilidade CORE-03…CORE-16

| Issue | Estado local e critério |
|---|---|
| CORE-03 / #13 | Avaliação real entre competições executada; limiar útil não atingido; sem confirmação em temporada futura |
| CORE-04 / #14 | Contrato novo 2.0.0 de contexto/pedido implementado; schemas legados preservados |
| CORE-05 / #15 | Perfis/evidências reutilizados, política de suficiência consolidada; compatibilidade e custo medidos; sem novas fórmulas |
| CORE-06 / #16 | Tarefas/rubrica/formulário definidos; coleta e revisão humana de rótulos bloqueadas por ausência de avaliadores/dados revisados |
| CORE-07 / #17 | Planos condicionais rastreáveis, restrições e ordenação explícita implementados; eficácia não validada |
| CORE-08 / #18 | Preditores avaliados e não promovidos; D1 sem rótulos válidos; D2 com ajuste, avaliação e recarregamento reais concluídos como experimento, sem promoção |
| CORE-09 / #19 | Elenco declarado com posição/disponibilidade/fonte/data e validações; nenhuma recomendação individual validada |
| CORE-10 / #20 | Comparação descritiva de opções sustentadas e prioridades declaradas; sem ganho esperado ou eficácia estimada |
| CORE-11 / #21 | Serviço orquestra núcleo/planos/explicação opcional; preditores não aprovados permanecem fora da decisão |
| CORE-12 / #22 | Ollama real integrado e validado; seleção restrita em português, fallback explícito apenas no modo opcional |
| CORE-13 / #23 | JSON/Markdown versionados com contexto/evidências/abstenção; aceitação esportiva humana pendente |
| CORE-14 / #24 | API/OpenAPI, erros, exportação e fluxo HTTP real validados com pacote instalado; exemplos entregues |
| CORE-15 / #25 | Rubrica e casos preparados; zero avaliações especializadas, dependência externa explícita |
| CORE-16 / #26 | Homologação técnica local do backend aprovada; validação esportiva/direitos de distribuição continuam pendentes; frontend não construído |

Nenhuma issue remota foi alterada; não houve commit/push/merge/PR ou publicação. Estes status não significam fechamento automático dos critérios externos.


### 20.6 Resultados finais, artefatos e comandos reproduzíveis

**Fine-tuning real concluído como experimento de explicação restrita; sem promoção.** SmolLM2-135M + LoRA: 460.800 parâmetros treináveis, 192 passos; loss inicial 0,9454962611 e final 0,0001553384. Fit até o passo 192: 363,697 s. O campo `training.duration_seconds=528,203` do artefato inclui também avaliação pós-fit e recarregamento, não é tempo puro de otimização. No teste sintético n40: validade/cobertura exata e respeito à abstenção base=0%, ajustado=100%; na validação n24, ajustado=100%. Os nulos/fatos alterados são recusados pelo validador; zero conteúdo inseguro exposto após validação não significa que o modelo base não produziu conteúdo inválido. Saídas brutas e falhas completas estão preservadas.

Avaliação base: 261,188 s para 40 casos; ajustado: 91,863 s para 40; validação: 68,134 s para 24. Pico RSS cumulativo do processo: 1.624.220 KiB na base e 2.153.652 KiB após ajuste. Não são medições isoladas de VRAM/memória por modelo. Template: 100% por construção nessa supervisão, aproximadamente 0,000220 s para validar/materializar os 40 casos, sem parâmetros/modelo adicional. Portanto o ajuste demonstra viabilidade técnica nesta tarefa pequena, sem vantagem sobre template em fidelidade e custo. Zero revisões humanas de clareza/utilidade; nenhuma decisão tática aprendida ou adequação acadêmica comprovada. Modelo ajustado permanece experimental, fora da API de produção.

Artefato real: `outputs/runs/core_ai_lora_20261031/adapter/` (6.659.416 bytes incluindo tokenizador); SHA-256 de `adapter_model.safetensors`: `691444b0e23489dbb49c8ef1e9d6a45e9431e2a7b720fa151c3a8b99c571602d`. `evaluation.json` contém treino/perdas, casos completos base/ajustado/validação, decisão e hashes; `manifest.json` contém partições, configuração, dependências, identidade do modelo/dados/protocolo; `execution_identity.json` registra duração e proveniência complementar. O adaptador salvo foi recarregado com PEFT e produziu seleção válida para o primeiro caso de teste.

Limite de proveniência do primeiro ajuste: o processo já estava executando quando foram adicionados somente guards de destino e captura automática de código ao runner. Seu manifesto inicial não captura hash do código. A fonte exata do runner no lançamento foi reconstruída revertendo essas alterações não numéricas e preservada em `executed_explainer_training.py` (SHA-256 `68aedc24299a76d74c82d63e8370dcc6eb272fe9e65ee6f12ab56783de5bd18c`); essa reconstrução está explicitada em `execution_identity.json`, não apresentada como captura imutável no início. O runner entregue captura automaticamente hashes em futuras execuções. Nenhuma configuração, passo, dado ou resultado do ajuste original foi alterado para fazê-lo passar.

Protocolo: SHA-256 dos bytes `9fa36937190000fbebd86ab8a03cc2257c86aa2072a293f56f25ea39eac7f21d`; fingerprint canônico `8cc07c14063e05c196e4815d24f03e22687d1c9f05f7ab30a897f1a50aa3cddc`. A segunda avaliação quantitativa, agora com pacote instalado, está em `outputs/runs/core_ai_independent_installed_20261031/evaluation.json`, com hashes do código efetivamente executado. Reproduziu exatamente modelos, previsões, métricas e decisões da primeira, em 205,448 s. OLS/Ridge continuam sem atingir o limiar útil; não promover.

**Pacote instalado:** cópia temporária Git em `/tmp/managerai-final-core/checkout`, com sobreposição dos arquivos atuais rastreados e novos autorizados, incluindo as quatro alterações preexistentes. Não foi teste de HEAD antigo. Verificação byte a byte de todos os módulos Python instalados contra `src/managerai`: zero divergências. Contrato JSON empacotado com SHA-256 `952e0db46781d71cf7c99aadcc58d7f40d04d8e3671737b2598ac1c323aa7244`, idêntico ao fonte. Imports novos e contrato confirmados com `python -I`. `pip check`: nenhum requisito quebrado. Wheel salvo em `/tmp/managerai-final-core/wheels/`; o venv funcional não foi alterado. Atualizações documentais posteriores e comentário no pyproject não mudaram o código instalado; não se atribui um hash binário de wheel a outro build.

| Verificação desta execução | Comando/intérprete | Resultado real |
|---|---|---|
| Perfil mínimo fonte final | `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -B -S -m unittest discover -s tests -q` | 282 descobertos, 233 aprovados, 49 pulados, zero falhas/erros; 9,450 s |
| Serviço/API portátil focal | `PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 /tmp/managerai-final-core/api-env/bin/python -B -m unittest discover -s tests -p test_service.py -v` | 18 aprovados, zero falhas/erros/pulos; 2,800 s; executado fora da restrição de sockets |
| Núcleo instalado sem opcionais | `/tmp/managerai-final-core/core-env/bin/python -I -B -m unittest discover -s tests -q` no checkout temporário | 282 descobertos, 233 aprovados, 49 pulados, zero falhas/erros; 8,083 s |
| Pacote instalado portátil com opcionais | `MANAGERAI_RUN_LOCAL_TESTS=0 PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg MPLCONFIGDIR=/tmp/managerai-final-core/mpl-portable /tmp/managerai-final-core/full-env/bin/python -I -B -m unittest discover -s tests -q` no temporário | 282 descobertos, 272 aprovados, 10 pulados, zero falhas/erros; 14,577 s |
| Pacote instalado completo com dados reais | `MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg MPLCONFIGDIR=/tmp/managerai-final-core/mpl-installed /tmp/managerai-final-core/full-env/bin/python -I -B -m unittest discover -s tests -q` no temporário | 282 aprovados, zero falhas/erros/pulos; 85,319 s |
| Comparações independentes | `/tmp/managerai-final-core/full-env/bin/python -I -B outputs/v22_v3_validation/check_metrics.py`, MPLCONFIGDIR temporário | 16/16 aprovadas; código 0 |
| API instalada + Ollama real | `/tmp/managerai-final-core/full-env/bin/python -I -B scripts/check_backend.py --data-root open-data/data --output-dir outputs/runs/core_ai_backend_installed_20261031 --with-ollama` | 3/3 casos HTTP 200 e `generated`; exportações equivalentes; 28,704 / 7,760 / 9,190 s |
| HTTP TCP real sem LLM | Uvicorn instalado em loopback, script temporário `check_http.py` | HTTP 200, dois planos, 151.701 bytes, exportação equivalente, 2,799 s; servidor encerrado |

Integração instalada final: `outputs/runs/core_ai_backend_installed_20261031/` contém OpenAPI real, avaliação, hashes de código e `human_review_cases.json` com três casos/fontes, lista de revisões vazia. Os casos cobrem funções, não constituem amostra independente de utilidade. Payloads finais: 4.950.415 bytes (City V3), 3.274.667 (insuficiente), 153.199 (injeção). HTTP real/OpenAPI também em `outputs/runs/core_ai_http_20261031/`. Manifesto da entrega em `outputs/runs/core_ai_delivery_20261031/`. Artefatos permanecem locais/ignorados; não foram publicados.

Comandos de pesquisa efetivamente executados (variáveis de threads/caches isoladas quando aplicáveis):

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /tmp/managerai-final-core/train-env/bin/python -u -B -m managerai.experiments.explainer_training --model-path outputs/runs/core_ai_model_20261031 --protocol docs/core_ai_protocol.json --output-dir outputs/runs/core_ai_lora_20261031
OPENBLAS_NUM_THREADS=1 /tmp/managerai-final-core/full-env/bin/python -I -B -m managerai.experiments.independent --data-root open-data/data --protocol docs/core_ai_protocol.json --output-dir outputs/runs/core_ai_independent_installed_20261031
```

Os destinos acima já existem e são preservados; para repetir, escolher nomes novos. Para carregar o adaptador sem treinar: `LocalTransformerProvider('outputs/runs/core_ai_model_20261031', adapter_path='outputs/runs/core_ai_lora_20261031/adapter')`, em ambiente com training; método `generate(projection)` seguido obrigatoriamente por `validate_selection`. Isso é uso experimental explícito, não registro automático no servidor.

Preservação: os três relatórios congelados coincidem com SHA-256 inicial; Git do clone StatsBomb continua limpo e na revisão fixada; EDA mantém 108 arquivos observados, sem gerador executado. Não se fez hash integral da EDA nem inspeção visual de navegador. A mitigação de JSON da UI foi preservada e os testes reais passaram; confirmação humana de responsividade permanece pendente. Não foram executadas avaliações esportivas humanas, treino tático supervisionado, serviço pago, CI remota, certificação V3 adicional ou frontend novo.

**Status de entrega:** BACKEND PARA FRONTEND: APTO para integração local com as capacidades explicitadas no contrato. IA E FINE-TUNING: PARCIAIS — inferência e ajuste de explicação reais, avaliação técnica sintética concluída; sem decisão tática aprendida, superioridade sobre template, revisão humana ou validação esportiva. O projeto inteiro não está concluído; frontend novo e critérios externos permanecem abertos.


## 21. Frontend local e correções de integração — 31/10/2026

### 21.1 Estado de entrada, escopo e arquitetura

Entrada conferida: branch `main`, HEAD `4175df419443756d9a1af18a7701f9c1e2841b69`, checkout limpo, sem alterações preexistentes não commitadas. A referência coincidiu com HEAD; nenhum estado posterior foi descartado. Não havia frontend/package manager/lockfile; foi criada aplicação React/TypeScript/Vite em `frontend/`, com package-lock e configuração de exemplo sem segredos. CLI, Streamlit, fórmulas, schemas 1.0.0/1.1.0, dados/EDA e fixtures foram preservados. Não houve commit, push, PR, mudança de issue, publicação, autenticação, banco, fila ou novo treinamento.

A interface consome a API como fonte de catálogo/equipes/calendário/cobertura/relatório/exportação. Há seletores dependentes, exclusão entre alvo/corte, aviso de redefinição, janela limitada por capacidades, V3 certificada, contexto declarado e opções avançadas. Elenco não é editado nesta UI; análise permanece coletiva, com limitação explícita. Explicação é `none` por padrão; configuração do provedor não é anunciada como disponibilidade confirmada. Seleção de IDs pela LLM não é apresentada como raciocínio tático aprendido.

Acesso à API e mensagens em `frontend/src/api.ts`; tipos gerados e opções canônicas; requisições de leitura obsoletas canceladas e ignoradas por identidade. Pedidos de análise não recebem retry; o timeout cobre leitura do corpo e alerta que cálculo pode continuar no servidor. Resultado mantém identificação do pedido enviado se o formulário mudar. Relatórios/notas não são persistidos em localStorage; token de exportação não entra em analytics/logs da UI. Markdown é baixado pelo endpoint, não executado como HTML.

A apresentação prioriza indicadores e planos com observações, condições, riscos, pré-condições e evidências. Todos os indicadores ficam sob demanda: caso V3 tem 21+26 linhas, com unidades/amostras por equipe. Valores ausentes são indisponíveis, nunca zero. Barras não misturam unidades; porcentagens usam 0–100. Entradas/90 e mapa de chutes usam métricas/pontos existentes; plano 120×80, sem espelhamento. A tabela mobile foi inspecionada e ajustada para manter valores/amostras visíveis; tabela detalhada de evidências permite rolagem explicitamente indicada. Não se renderiza JSON/eventos/sequências integrais. Evidências/fontes/gráficos são expandidos sob demanda.

### 21.2 Correções e rastreabilidade

| Revisão/fluxo | Implementação e aceite local |
|---|---|
| A1 / prioridades | Removida associação objetivo `pressionar alto` → R02. A ação real de R02 é saída sob pressão adversária. Ordenação `context-order-2`, teste semântico e `objective_note` no JSON/Markdown; prioridades compatíveis preservadas. Métricas/hipóteses legadas intactas |
| A2 / CORE-04, CORE-14 | Literals comuns em options.py, modelos HTTP em http_schema.py, projeção display aditiva, respostas tipadas e erros próprios preservados; OpenAPI e TS/opções gerados e conferidos na CI |
| A3 / pesquisa | Contradições atuais de README/início de PENDING reconciliadas; registros anteriores identificados como históricos. Artefatos locais acessíveis e hashes/configurações/resultados consolidados em research_evidence.json, sem pesos/datasets no Git ou novo treino |
| B / seleção e cobertura | Dados reais da API, referência exclusiva, limites, amostra insuficiente descritiva, invalidar respostas antigas e mudanças de recorte |
| C / relatório | Indicadores, planos condicionais, comparação sem mérito validado, evidências e exportação real; estado recebido separado de expiração no servidor |
| D–E / uso e robustez | Layout desktop/mobile, teclado/foco/labels, tratamento 413/422/429/500/503 e 404 de exportação; proxy local, sem CORS aberto, retries de análise ou armazenamento local |
| F / CORE-16 técnico local | Build/TS, backend instalado, 16 testes portáteis de navegador e 4 cenários reais, incluindo V3/gráficos/downloads, insuficiência, LLM e ciclo de falhas |
| CORE-06, CORE-08, CORE-15 e critérios externos | Interface não valida tática aprendida, eficácia, utilidade esportiva ou requisito acadêmico. Revisão humana continua ausente; fine-tuning anterior permanece experimental e não foi refeito |

API mantém service_version 2.0.0 com campos aditivos de apresentação. `legacy_report` e proveniência V4.1 preservados; frontend não depende de reconstruir objetos opacos. Literals reutilizam valores canônicos do Core e verificações de equivalência; desconhecidos mantêm códigos do serviço, inclusive ENGINE_UNAVAILABLE e INVALID_RESTRICTIONS. Schema JSON de OpenAPI em frontend/openapi.json, TS em src/generated/api.d.ts, opções em options.ts. Gerar/conferir conforme BACKEND_API.md; sem servidor/dados/modelo. Job frontend adicionado à CI, preservando os dois perfis backend; CI remota não foi executada nesta entrega.

### 21.3 Ambiente, instalação e validação desta execução

Linux, Python 3.12.3, Node 20.19.4 e npm 10.8.2; Node 18.20.8 também estava no PATH inicial, mas é incompatível com Vite atual e não foi usado para build/testes. Node compatível foi selecionado por PATH, sem atualizar o sistema. Brave Chromium local em `/usr/bin/brave-browser`, executado headless por Playwright 1.64.1 com perfis temporários novos, sem reutilizar perfil pessoal. React 19.3.1, TypeScript 5.9.3, Vite 8.3.5. Sem imagens/escudos/fontes externas como dependência do fluxo.

Backend construído/instalado em `/tmp/managerai-frontend-20261031/backend-env`, novo e independente, a partir de clone temporário mais sobreposição fiel dos arquivos alterados/novos em `/tmp/managerai-frontend-20261031/checkout`. O código instalado foi comparado byte a byte com todos os módulos Python atuais: zero divergências. Dados reais referenciados por symlink ignorado somente no temporário. Pacote JSON e imports novos conferidos com `python -I`; pip check sem requisitos quebrados. Venvs funcionais não foram alterados. Instalação para outra pessoa usa `.venv-web` e npm ci conforme README, sem depender dos temporários de validação.

| Verificação atual | Comando/intérprete | Resultado |
|---|---|---|
| Backend completo instalado | `MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg MPLCONFIGDIR=/tmp/managerai-frontend-20261031/mpl /tmp/managerai-frontend-20261031/backend-env/bin/python -I -B -m unittest discover -s tests -q`, cwd temporário | 284 aprovados, zero falhas/erros/pulos; 73,070 s |
| Backend mínimo fonte | `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -B -S -m unittest discover -s tests -q` | 284 descobertos, 234 aprovados, 50 pulados, zero falhas/erros; 7,664 s |
| Serviço/API focal | `PYTHONPATH=src:tests /tmp/managerai-final-core/full-env/bin/python -B -m unittest discover -s tests -p test_service.py -q` | 20 aprovados, zero falhas/erros/pulos; 2,474 s; ambiente anterior apenas lido |
| Conferência independente | `/tmp/managerai-frontend-20261031/backend-env/bin/python -I -B outputs/v22_v3_validation/check_metrics.py`, MPLCONFIGDIR temporário | 16/16 aprovadas, código 0 |
| Contrato | `python -I -B scripts/export_openapi.py --check` com Python instalado + `npm run types:check` | OpenAPI atual, TS e opções equivalentes |
| Build frontend | `npm run build` com Node 20.19.4 | TypeScript sem erros e build de produção concluído; bundle sem datasets/pesos |
| Navegador portátil | `PLAYWRIGHT_BROWSER_EXECUTABLE_PATH=/usr/bin/brave-browser MANAGERAI_TEST_OUTPUT=/tmp/managerai-frontend-20261031/... npm test` | 16 aprovados, sem falhas/erros/pulos; fixtures sintéticas somente nos testes, sem backend/dados/modelo |
| Navegador/API reais | `MANAGERAI_BACKEND_PYTHON=/tmp/managerai-frontend-20261031/backend-env/bin/python PLAYWRIGHT_BROWSER_EXECUTABLE_PATH=/usr/bin/brave-browser MANAGERAI_REAL_ARTIFACTS=<destino novo> npm run test:real` | 4 aprovados, zero falhas/pulos; execução release em 40,2 s |
| Pesquisa histórica | `python3 -B scripts/check_research_evidence.py --check` | Artefatos/manifestos/dataset sintético/adapter hashes conferidos; nenhuma nova avaliação/treino |
| Dependências frontend | `npm ci`/lockfile e `npm audit --omit=dev` | Runtime sem vulnerabilidades reportadas. Auditoria completa reporta três moderadas na cadeia de desenvolvimento openapi-typescript/Redocly/minimatch; não estão no bundle. Não foi aplicado override incompatível nem apresentada auditoria total como limpa |

Falhas intermediárias corrigidas, não contadas como aprovações: reforço inicial do contrato causou quatro erros de validação de resposta por tuplas do serviço e uma falha de código de motor; normalização do pedido HTTP e preservação do erro original resolveram, focal final 20/20. Override de Redocly 2 quebrou exports internos do gerador; tentativa com gerador 6 trouxe outros avisos de dependência e foi abandonada. A entrega fixa openapi-typescript 7.13.0 compatível, com limitação de auditoria dev registrada acima. Uma reinstalação sem build isolation falhou por ausência de setuptools no venv novo; build isolation passou. Nada disso foi chamado de validação bem-sucedida. Porta 8000 já estava ocupada; a tentativa de bind falhou e o servidor preexistente foi preservado, usando 8011 para esta tarefa.

### 21.4 Navegador real e evidência visual

Artefatos finais de teste: `outputs/runs/frontend_browser_release_20261031/`, ignorado pelo Git. City × Arsenal de 08/05/2016, janela 10, V3: HTTP 200, 4.994.332 bytes, análise/apresentação inicial 6.938 ms; seis indicadores principais, 47 adicionais consultáveis e planos presentes. Downloads JSON/Markdown concluídos pelo servidor; pontos/gráficos/evidências exibidos; nenhum pageerror. Uma amostra requestAnimationFrame após a expansão levou 0,3 ms: é medição local pontual, não benchmark contínuo nem SLA. Desktop 1440×1000 e mobile 390×844, sem overflow horizontal do documento. Capturas desktop-report.png, desktop-charts.png, mobile-report.png e inspeção corretiva mobile-indicators-responsive.png (tabela com 316 px). Tabelas largas de evidência têm rolagem própria sinalizada; valores/amostras do resumo não são ocultos em mobile.

Real × Barcelona, La Liga2020/21: HTTP 200 com abstenção explícita e zero planos. Qwen2.5 1.5B local via Ollama: explicação opcional retornou `generated`, 10,393 s de geração na execução release; modo padrão não aciona LLM. Sem inferência paga, geração livre ou aprendizado tático presumido. Os casos não constituem avaliação de qualidade esportiva.

Ciclo real adicional em servidores próprios 8012/5178: mando conflitante gerou 422 e bloqueou envio; backend parado foi percebido por nova página; após reinício, exportação de chave antiga gerou 404, com relatório recebido preservado na página e sem sucesso fictício. Esse teste é perda real de memória por reinício, não espera de TTL. TTL de 300 s é testado no backend com relógio controlado e o 404 também em teste portátil da UI. Não se inventou espera real de cinco minutos. Teclado/foco e data em timezone America/Sao_Paulo foram conferidos nos testes portáteis. O novo frontend foi inspecionado visualmente; isso não equivale a homologação visual do Streamlit nem avaliação formal de acessibilidade com usuários.

### 21.5 Evidências preservadas, execução e pendências

`docs/research_evidence.json` é uma consolidação pequena e reproduzível, sem pesos/dados de partidas. Registra disponibilidade, configuração, partições, resultados históricos, hash de avaliação/manifesto e hashes do adaptador conferidos contra o acervo. Não houve treinamento, reavaliação quantitativa ou revisão humana nesta tarefa. Resultados antigos do §20 não foram transformados em execução nova.

Instalação reproduzível: README, seção Aplicação web local. `.venv-web` novo com `.[api,v3]`, Node compatível e npm ci. `python3 -B scripts/run_web.py` inicia interface/API; script preserva o caminho do Python do venv (não segue symlink até o Python do sistema), um worker, loopback. O comando conjunto foi efetivamente testado com `--python /tmp/managerai-frontend-20261031/backend-env/bin/python`: saúde, proxy e capacidades com LLM desativada por padrão confirmados. O encerramento do comando conjunto por Ctrl+C retornou código 0; conferência de sockets confirmou livres 8011/8012/5173/5177/5178. Servidores de teste/criados nesta execução foram encerrados; o servidor preexistente em 8000 permaneceu intacto.

Dados StatsBomb continuam na revisão fixada e com Git limpo; verificador retornou compatível nesta execução. Os três relatórios congelados coincidem com hashes iniciais. Nenhum gerador EDA foi executado; não se reivindica hash integral da EDA. Pendências externas: revisão humana/utilidade esportiva, rótulos válidos para decisão tática, generalização, direitos para distribuição/publicação e exigência acadêmica do ajuste. Implantação pública ainda exigiria tarefa própria de autenticação/TLS/gestão de armazenamento e recursos; nada disso foi implementado aqui.

Validação final do lockfile em cópia limpa `/tmp/managerai-frontend-20261031/frontend-clean`: `npm ci`, `npm run types:check`, `npm run build` e 16 testes portáteis aprovados em 23,8 s, sem backend de teste ativo. Isso confirma instalação sem depender de node_modules do checkout original. A última execução do checkout também passou 16/16 em 23,6 s após ajustar o timeout para cobrir o corpo da resposta. Checks de 36 links locais, JSON/contrato empacotado, identidade dos módulos instalados e git diff --check passaram.

**FRONTEND LOCAL: APTO** — fluxo documentado e executável com dados reais, build/contrato/testes/visualização e exportação validados localmente. **INTEGRAÇÃO REAL: VALIDADA** — navegador, API instalada, StatsBomb local, gráficos/downloads, insuficiência e ciclo de falhas exercitados; LLM local opcional confirmada separadamente. Estes status não validam IA esportiva nem concluem o projeto inteiro.

## 22. CORE-02 — conteúdo integral da La Liga 2015/16 (01/11/2026)

### Escopo, origem e decisão

Entrada: main `3418e2b11713bc07246dc2a7cd3c9874ec8ee821`. Artefato não rastreado observado na EDA após obter o checkout foi preservado. Python 3.12.14; núcleo construído e instalado em ambiente novo `/tmp/managerai-core02-20261101-env`, imports isolados com `-I` e contrato empacotado conferidos. A primeira instalação encontrou erro de markers de extras no pip 25.0.1; atualizar somente o pip desse ambiente para 26.2.2 permitiu instalar o wheel. Nenhuma versão do pyproject foi alterada.

O provisionamento Git completo não terminou neste ambiente; houve timeout HTTP e lock residual após interrupção. Não se obteve `verify-data=compatível` e não se substituiu a matriz histórica das 80 temporadas. Como alternativa de diagnóstico, a conexão GitHub forneceu a árvore oficial `d7669be3dba46aa3d506bd15ffeb58030c7879c9` da revisão fixada `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`. Os 380 eventos, 380 arquivos de escalação, catálogo e calendário foram obtidos por blob; tamanho e SHA Git de cada arquivo foram conferidos e hashes SHA-256 registrados. Total: 762 arquivos, 1.129.450.550 bytes. Essa prova é restrita aos arquivos selecionados, não é verificação do clone completo CORE-01.

**Decisão: La Liga 2015/16 não certificada.** A auditoria de conteúdo foi integral; sua reprovação decorre de falhas encontradas nas guardas vigentes. O gate de snapshot completo também permanece não verificado. `VALIDATED_RECUTS`, contrato StatsBomb, fórmulas, limiares e dados brutos não foram alterados. Resumo versionado: [core02_laliga_201516_audit.json](core02_laliga_201516_audit.json).

### Resultados reais

| Medida | Resultado |
|---|---:|
| Jogos catalogados/lidos/diagnosticados | 380 / 380 / 380 |
| Eventos examinados | 1.295.354 |
| Jogos/equipe diagnosticados | 760 |
| Métricas calculáveis em todos os jogos/equipe | 33 de 50 |
| Alvos H5 / H10 pelo calendário | 330 / 280 |
| Alvos H5 / H10 com todos os 50 indicadores em cada jogo histórico | 0 / 0 |
| Coordenadas de início inválidas | 9 |
| Coordenadas finais de movimento inválidas | 17 |
| Durações inválidas | 2 |
| Grupos de orientação coerente / inconclusiva / mista | 1.141 / 151 / 228 |

As dez ocorrências de reprovação por qualidade atingem seis partidas: `266106`, `266467`, `266961`, `267273`, `3825665` e `3825875`. Uma conferência independente diretamente nos seis JSONs reproduziu 9 posições inválidas, 17 finais de movimento inválidos e 2 durações negativas. Contagens de campos podem pertencer ao mesmo evento; não são 28 eventos distintos presumidos. JSON, ligações e cálculos foram diagnosticados nos 380 jogos; isso não torna suas anomalias aceitáveis para certificação.

`pass_accuracy_explicit_no_pressure` ficou indisponível nos 760 jogos/equipe. A implementação diferencia `under_pressure=False` de marcação ausente: não reinterpretar ausência como False para fazer o gate passar. Como o requisito de completude exige todos os 50 indicadores, essa indisponibilidade já impede qualquer H5/H10 integral. Isso não significa ausência de histórico útil: finalizações, xG, acerto global de passes e outros indicadores têm valores calculáveis em todos os 760 jogos/equipe. Disponibilidade não comprova qualidade certificada. Os 50 denominadores estão no resumo JSON.

Os três agregados de sequência ficaram disponíveis em 507 de 760 jogos/equipe. O contador de qualidade de sequência registra 264 ocorrências de relógio inválido/decrescente e 7 de geometria ofensiva inválida, acumuladas por análise de equipe; não tratá-las como contagem de eventos únicos. Geometrias incompletas de passes/conduções também estão discriminadas. Houve uma única combinação de versões: `data_version=1.1.0`, fidelidades de chute e coordenadas `2`.

Orientação agregada: inconclusiva, com 131 partidas tendo todos os quatro grupos coerentes. Os 228 grupos mistos não devem ser descritos como coordenadas comprovadamente invertidas: a guarda usa mediana dos chutes e fração de movimentos crescentes, não valida direção esportiva por si só. Nenhum grupo recebeu classificação invertida. O protocolo não foi recalibrado a partir destes resultados.

### Gates e implementação

| Gate | Estado nesta execução |
|---|---|
| 0 — fonte/instalação | Wheel isolado validado; hashes oficiais do recorte conferidos; snapshot completo CORE-01 não verificado |
| 1 — presença | 380 eventos e 380 escalações presentes e conferidos no recorte; 360 não necessário |
| 2–3 — estrutura/taxonomia/função | Diagnóstico integral concluído; falhas de qualidade registradas; completude de todos os indicadores não atingida |
| 4 — geometria/orientação | Bloqueado pelas geometrias inválidas e pelos grupos mistos/inconclusivos sob as guardas vigentes |
| 5 — tempo | Testes portáteis e caso real confirmaram seleção anterior ao dia do alvo, sem leitura do alvo/futuro nem reposição |
| 6 — amostra | Calendário H5/H10 calculado; critério integral tem zero alvos, não representa poder estatístico |
| 7 — V3 | Não certificado; teste real confirma que o recorte continua recusado pela V3 |

`season_audit.py` acrescenta contagem de eventos, disponibilidade por indicador com denominadores diagnosticado/catalogado e valores que sustentam a orientação (mediana x de chutes, movimentos crescentes e fração). `--content-only` é diagnóstico explícito de cópia parcial: ignora alegações de compatibilidade fornecidas pelo chamador, marca snapshot como não verificado, revisão null e certificação ausente. Sem essa opção, a exigência CORE-01 permanece. Nenhuma allowlist é promovida automaticamente.

### Execução, testes e preservação

Artefatos locais ignorados: `outputs/runs/core02_laliga_20261101/` com baseline, manifesto de fontes, auditoria integral, repetição, execução e verificação independente de qualidade. Hashes do código e das saídas estão no resumo versionado. Uma segunda execução instalada levou 46,531 s e reproduziu byte a byte a primeira saída, SHA-256 `fcfe3e32c98557f2f4d1bb29b4a69f910d09c001f697715d4895ceb9e37ea85c`. O tempo refere-se à repetição da auditoria, não ao download.

Comando executado com o pacote instalado:

```bash
/tmp/managerai-core02-20261101-env/bin/python -I -B -m managerai.season_audit --data-root /tmp/managerai-core02-api-data-20261101/data --audit-date 2026-11-01 --candidate-competition-id 11 --candidate-season-id 27 --content-only --output outputs/runs/core02_laliga_20261101/content_audit.json
```

O destino acima já existe. Para repetir, escolher destino novo. Com clone completo compatível, omitir `--content-only` e usar sua raiz real; isso continua sem autorizar inclusão na V3.

Focal instalado: `MANAGERAI_CORE02_CONTENT_ROOT=/tmp/managerai-core02-api-data-20261101/data PYTHONDONTWRITEBYTECODE=1 /tmp/managerai-core02-20261101-env/bin/python -I -B -m unittest discover -s tests -p test_season_audit.py -q`: **20 aprovados, zero falhas/erros/pulos**. Inclui caso real de histórico H10 e bloqueio V3; a variável é própria desse teste e não ativa as integrações que exigem o snapshot completo. Suítes finais fonte sem opcionais e pacote instalado, ambas com o caso real CORE-02: **288 descobertos, 238 aprovados, 50 pulados, zero falhas/erros** em cada perfil (5,931 s / 5,293 s). Saídas e comandos em `validation.json`. `pip check` passou. Não se executaram API, frontend, gráficos, LLM, avaliação humana ou treinamento nesta etapa.

Os três relatórios congelados mantêm os hashes iniciais; todos os 762 arquivos recebidos mantêm seus hashes após a auditoria. EDA e fórmulas foram preservadas. Sem commit, push, PR, publicação ou atualização de issue.

**Publicação posterior autorizada:** o usuário autorizou consolidar entregas em commits e enviá-las ao GitHub para atualização por git pull e validação local. Esta publicação inclui somente o auditor, seus testes, documentação e resumo compacto; os dados brutos e artefatos locais permanecem fora do commit. Os resultados de testes acima pertencem à execução da auditoria.

### Próximos passos deste recorte

1. Concluir o provisionamento CORE-01 em ambiente com o clone completo e executar o modo padrão, sem `--content-only`.
2. Investigar os seis jogos e documentar uma política de elegibilidade/abstenção por família de indicador, em mudança própria. Não editar os JSONs nem converter nulos em zero.
3. Rever a adequação científica da guarda de orientação e do requisito de completude global antes de formular eventual protocolo novo. Não reduzir limiares retroativamente para aprovar este recorte; exigir revisão e validação independente para uma política substituta.
4. Só após resolver esses gates considerar certificação e inclusão explícita com teste real. Serie A/Ligue 1 ainda não foram auditadas integralmente nesta execução; não presumir aprovação ou reprovação.

## 23. CORE-02 — elegibilidade diagnóstica por família (01/11/2026)

Entrada: main `9fe7f91b35fbe467184d051e5f749aecedf76c00`, sem alterações rastreadas preexistentes. Preservado o artefato não rastreado observado anteriormente na EDA. Escopo: política diagnóstica `metric-eligibility-1`, descrita após os achados exploratórios do §22 e registrada em `outputs/runs/core02_families_20261101/policy_before_run.json` antes da nova execução por família. Isso não constitui protocolo prospectivo independente nem substitui a certificação `core-02.1`.

### Política implementada

`metric_eligibility.py` particiona os 50 indicadores atuais em 16 famílias sem duplicação. Cada jogo/equipe recebe valores disponíveis, famílias elegíveis, métricas ausentes e causas de bloqueio. Um valor não nulo é necessário, mas não suficiente: exige as dependências de qualidade daquela família. Essa saída é aditiva ao auditor, sem recalcular valores ou alterar relatórios 1.0.0/1.1.0, API, UI ou regras táticas.

- Duração inválida bloqueia famílias com taxas por 90 das duas equipes, porque a exposição é compartilhada. Não bloqueia contagens ou acerto de passe por esse motivo.
- Geometria inválida ou ausente bloqueia somente famílias consumidoras da equipe afetada; uma posição inválida observada também bloqueia suas proporções por faixa. Destino inválido de passe incompleto afeta tentativas legadas, mas não progressões V3 de passes completos.
- Famílias direcionais exigem os dois grupos equipe/tempo coerentes sob a guarda já existente. Isso não demonstra orientação científica nem satisfaz a certificação da temporada.
- Marcador de pressão ausente continua distinto de False explícito. A família sem denominador de ausência explícita fica indisponível, sem impedir passes globais ou outros grupos de pressão.
- Sequências exigem seus valores calculáveis sob as regras existentes; relógios problemáticos não são corrigidos.
- Falha estrutural, arquivo ausente ou JSON malformado deixa o jogo sem diagnóstico utilizável. O auditor registra o erro e continua os demais jogos. UUID compartilhado entre partidas bloqueia as famílias de ambas, incluindo a primeira; esse é um controle retrospectivo de integridade do snapshot, não prova de disponibilidade histórica dos dados.

H5/H10 usa diretamente `temporal.select_history`, mesma competição/temporada e exclusão do dia do alvo/futuro. A janela precisa conter exatamente N jogos; todos os N precisam ser elegíveis para a família nas duas equipes. Não há reposição por partidas mais antigas. A saída completa guarda IDs dos alvos, não apenas totais. Nenhum resultado significa probabilidade de sucesso, utilidade tática validada, poder estatístico ou observações independentes.

### Resultado real e investigação dos seis jogos

| Família | Jogos/equipe elegíveis | H5 bilateral | H10 bilateral |
|---|---:|---:|---:|
| Contagem de finalizações | 760 | 330 | 280 |
| Qualidade de finalização | 759 | 325 | 270 |
| Acerto global de passes | 760 | 330 | 280 |
| Passes com pressão marcada / não marcada (cada família) | 760 | 330 | 280 |
| Passes com ausência explicitamente marcada de pressão | 0 | 0 | 0 |
| Pressões por 90 | 756 | 314 | 254 |
| Recuperações/interceptações/desarmes por 90 | 756 | 314 | 254 |
| Faixas de ações localizadas | 756 | 310 | 247 |
| Sequências | 507 | 2 | 0 |

As seis famílias direcionais têm apenas 437–441 jogos/equipe elegíveis: movimentos legados H5/H10=1/0; progressões por passe 2/0; condução 1/0; faixas de entrada 3/0; pressão espacial 2/0; localização de chutes 4/0. Em 319 jogos/equipe a direção não foi estabelecida pela guarda operacional. As contagens completas e motivos estão no campo `family_diagnostic` do [resumo existente](core02_laliga_201516_audit.json).

Os seis jogos permanecem no inventário, com problemas rastreáveis a campo, índice, ID de evento, equipe e famílias dependentes. `3825665` e `3825875` têm duração inválida; isso retira quatro jogos/equipe das famílias por 90. `266106`, `266467`, `266961` e `267273` concentram os problemas geométricos. Em todos os seis, contagens de finalizações e acerto global de passes continuam elegíveis no diagnóstico. Nenhum arquivo bruto foi editado ou excluído. Os 33/50 indicadores integralmente calculáveis e os zero alvos com completude global do §22 permanecem resultados corretos sob aquela definição.

### Validação e evidências desta etapa

Python 3.12.14, ambiente isolado criado na etapa anterior; wheel reconstruído e instalado com o código atual. Todos os módulos Python instalados foram comparados byte a byte com os fontes atuais; `pip check` passou. Não foi criada outra configuração de dependências.

- Fonte mínima: `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -B -S -m unittest discover -s tests -q`: 301 descobertos, **249 aprovados, 52 pulados**, zero falhas/erros; 3,216 s.
- Instalado com casos reais: `MANAGERAI_CORE02_CONTENT_ROOT=/tmp/managerai-core02-api-data-20261101/data PYTHONDONTWRITEBYTECODE=1 /tmp/managerai-core02-20261101-env/bin/python -I -B -m unittest discover -s tests -q`: 301 descobertos, **251 aprovados, 50 pulados**, zero falhas/erros; 5,758 s. Pulos de dependências e snapshot completo não contam como aprovação.
- Focais fonte com dados reais: `test_metric_eligibility.py` **13/13** (0,660 s); `test_season_audit.py` **20/20** (2,399 s), sem pulos. Cobrem famílias, False/ausência, exposição, geometria por equipe, períodos extras, orientação, janelas sem reposição, alvo/dia/futuro, duplicatas e JSON malformado; incluem os seis casos reais.
- Auditoria integral com pacote instalado: mesmo comando do §22, saída nova `outputs/runs/core02_families_20261101/audit.json`; **46,701 s**, SHA-256 `f651d67f84e77ef0603f6266c06a75111eb6cea1b9c975bd4d9ec73f2dda0745`. Todos os campos anteriores, exceto o fingerprint do relatório ampliado, coincidem com a auditoria do §22.
- Uma conferência independente de janelas a partir do calendário e das máscaras por jogo/equipe reproduziu IDs e totais das 32 combinações família/janela. Hashes dos 762 arquivos oficiais e das três fixtures congeladas foram reconferidos e preservados.

Artefatos locais ignorados: `outputs/runs/core02_families_20261101/`, com política, auditoria, execução e verificações independentes. O resumo JSON existente foi ampliado; não se criou outro manual ou relatório histórico paralelo. Nenhuma nova aquisição de dados, treinamento, inferência LLM, execução de API/frontend/navegador, revisão humana ou certificação foi feita nesta etapa.

**Estado:** política diagnóstica implementada e testada; a La Liga continua não certificada. Antes de integrar critérios de aproveitamento parcial ao produto, revisar a semântica/adequação da orientação e definir migração explícita dos gates com avaliação independente. O gate CORE-01 do clone completo permanece aberto. Não interpretar famílias com histórico elegível como licença para liberar V3 automaticamente.
