# ManagerAI — pendências e validação

**CORE-00: V4.1, A/B e C versionadas; instalação e 237 testes validados em checkout limpo. CI e integração Git registradas na seção CORE-00 ao final. O runtime do treinador permanece determinístico; regressões são experimentais.**

Atualizado em 17/10/2026. Estado, contratos e comandos: [CURRENT_VERSION.md](CURRENT_VERSION.md). Regras: [AGENTS.md](../AGENTS.md). **V4.1, V4.2 e V4.3-A/B concluídas; dataset e regressões offline validados (§14).** Há OLS/Ridge experimentalmente ajustadas para previsão de chutes. Motor aprendido integrado ao runtime, fine-tuning, LLM e recomendações de escalação continuam **não implementados**. V4.3-C concluída como estudo exploratório; CORE-00 no §16.

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
| DATA-01 | DECISÃO HUMANA | Provisionamento StatsBomb com revisão/licença/responsável e recuperação por outro integrante; dados e EDA mantidos |
| ART-01 | IMPLEMENTADO NA C, CONFERIDO NA CORE-00 | `open-data/` e `outputs/runs/` ignorados; fixtures, exemplos finais e verificadores preservados/rastreados |
| TEAM-01 / B4 | DECISÃO HUMANA | Responsáveis por contratos, dados/indicadores, UI e avaliação; confirmar uso compartilhado de `.vscode/settings.json` |
| REF-01 | NÃO INICIADO | Consolidar constantes de suficiência e revisar acoplamento regras/apresentação em refatoração própria, sem alterar fórmulas/contratos |
| V3-01 | NÃO INICIADO | Auditar novas temporadas, orientação/campos e envelhecimento da evidência antes de ampliar VALIDATED_RECUTS |
| PERF-01 | NÃO INICIADO | Medir releitura/tamanho dos relatórios; preservar proveniência, inspeção e compatibilidade |
| EVAL-01 | PENDENTE | Revisão especializada/vídeo/treino com correção, rastreabilidade, plausibilidade, compreensão, riscos e utilidade separados |
| AI-01 | EXPERIMENTO QUANTITATIVO A/B IMPLEMENTADO | OLS/Ridge treinadas offline para chutes; sem motor tático aprendido no runtime, validação de estratégia ou integração V3/V4.1. Decisão C no §14 |
| AI-02 | PLANEJADO | Fine-tuning depende de alvo, direitos, rótulos, avaliadores, divisão temporal e ganho mensurável; sem pacote/checkpoint escolhido |
| AI-03 | PLANEJADO | LLM explicadora depende de provedor/custo e avaliação de fidelidade aos números calculados; nenhuma integração atual |
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
