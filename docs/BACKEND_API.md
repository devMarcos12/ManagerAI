# Integração com o Core HTTP

O contrato de serviço é `2.0.0`. Os relatórios legados mantêm `1.0.0` e `1.1.0` dentro de `legacy_report`. O serviço não prevê vitória, escalação ideal ou eficácia de estratégias. A aplicação histórica funciona sem LLM.

## Instalação e execução

Em ambiente novo escolhido pelo operador, a partir deste checkout:

```bash
python3 -m venv /tmp/managerai-backend-env
/tmp/managerai-backend-env/bin/python -m pip install '.[api,v3,experiments]'
MANAGERAI_DATA_ROOT="$PWD/open-data/data" /tmp/managerai-backend-env/bin/python -I -B -m uvicorn managerai.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

Esse é um serviço local, sem autenticação multiusuário. Não expor publicamente sem uma implantação específica que trate autenticação, TLS e limites por usuário. CORS fica fechado por padrão; `MANAGERAI_CORS_ORIGINS=http://127.0.0.1:5173` libera somente a origem indicada quando a API é acessada diretamente. O frontend padrão usa proxy local, sem liberar CORS. O cliente não pode escolher caminho de dados, destino de arquivos, URL de provedor ou credenciais.

Para LLM local opcional, com Ollama já instalado e modelo presente, iniciar o mesmo comando com `MANAGERAI_OLLAMA_MODEL=qwen2.5:1.5b` e, de preferência, `MANAGERAI_OLLAMA_DIGEST` igual ao digest observado em `/api/tags`. O backend não baixa modelos nem chama provedores pagos. `explanation=none` não faz chamada. `optional` mantém o relatório com falha explícita; `required` retorna 503 se não gerar saída validada. `explainer_model`, quando informado, precisa ser exatamente o modelo configurado no servidor, sem substituição.

A LLM seleciona IDs de afirmações previamente autorizadas. A validação exige cobertura integral, ordem e ausência de campos adicionais; o Core materializa os textos em português. Não há prosa livre produzida pela LLM. Esse limite impede alteração de números e evita tratar uma citação isolada como prova semântica. Notas do treinador não entram no prompt. Uma falha preserva as seções determinísticas no modo opcional.

## Descobrir → conferir → analisar → exportar

Contrato OpenAPI real: `GET /openapi.json`; documentação interativa: `/docs`.

| Método/caminho | Resultado |
|---|---|
| `GET /v1/health` | Processo e presença do catálogo; não certifica a integridade do dataset |
| `GET /v1/capabilities` | Motores, LLM configurada, capacidades experimentais desativadas e limites |
| `GET /v1/catalog` | Competições/temporadas presentes e indicação de certificação V3 |
| `GET /v1/teams?competition_id=2&season_id=27` | Equipes do calendário |
| `GET /v1/matches?competition_id=2&season_id=27` | IDs, datas e equipes; sem placares |
| `POST /v1/coverage` | Prévia temporal por equipe; presença não certifica conteúdo |
| `POST /v1/analyses` | Relatório final, inclusive com abstenção quando a amostra é insuficiente |
| `GET /v1/reports/{report_key}` | Obter relatório ainda retido |
| `GET /v1/reports/{report_key}/export?format=json` | Exportação integral JSON |
| `GET /v1/reports/{report_key}/export?format=markdown` | Relatório legível em português |

Exemplo mínimo para ambos os POSTs:

```json
{
  "schema_version": "2.0.0",
  "analysis": {
    "competition_id": 2,
    "season_id": 27,
    "team_id": 36,
    "opponent_id": 1,
    "target_match_id": 3754314,
    "recent_matches_window": 10,
    "venue": "desconhecido",
    "match_context": "regular",
    "strategic_objective": "equilibrado",
    "notes": ""
  },
  "include_v3": true,
  "intended_strategy": "proteger_area",
  "blocked_plan_ids": [],
  "roster": [],
  "engine": "deterministic",
  "explanation": "none"
}
```

Pode-se substituir `target_match_id` por `cutoff_date` ISO, nunca informar ambos. Estratégias: `equilibrada`, `proteger_area`, `saida_sob_pressao`, `proteger_progressao`. Bloqueios identificam regras existentes, nunca texto arbitrário. Elenco opcional: cada entrada exige `player_id`, `team_id`, `positions`, `availability` (`available/unavailable/unknown`), `source` e `observed_on` ISO. Referência posterior ao corte, equipe divergente e duplicatas são recusadas. Declarações não são verificação externa; a ausência de elenco não bloqueia a análise coletiva. Sugestões individuais permanecem em abstenção.

Planos contêm observação, evidências, condição, ação possível, pré-condições, riscos e limitações. Estratégia compatível soma 2 à prioridade; objetivo compatível soma 1, conforme mapas explícitos em `service.py`. Isso só ordena planos já sustentados. Empates são apresentados sem mérito estimado. `plan_comparisons` identifica diferenças de evidências e ausência de comparação de eficácia.

O frontend deve ler `sufficiency`, `abstention_reason`, `model_status` e `explanation.status` antes de apresentar conclusões. `report_id` é a identidade determinística do pedido e relatório; `report_key` é token aleatório de acesso por posse. Não tratar o token como autorização de equipe ou usuário autenticado. Não registrar notas ou tokens em analytics por padrão. Renderizar texto/Markdown como conteúdo não confiável, sem executar HTML ou scripts.

## Filtros de qualidade opcionais

`data_policy` aceita `legacy` (padrão, também quando omitido) ou `quality_v1`. A capacidade é anunciada em `GET /v1/capabilities`, campo `data_policies`. Para testar a nova opção, usar `"data_policy":"quality_v1"` e `"include_v3":false`. A combinação com V3 retorna 422 `INCOMPATIBLE_DATA_POLICY`; política desconhecida retorna 422 `INVALID_DATA_POLICY`. Não há fallback automático.

No modo novo, `evidence`, `sufficiency` e `plans` usam a projeção filtrada. `legacy_report` guarda o resultado original, inclusive hipóteses originais: essas hipóteses não são os planos filtrados do serviço. Os schemas legados 1.0.0/1.1.0 e o contrato de motores V4.1 não mudam. O serviço usa o contrato separado `service-quality-1`, identificado na proveniência como `deterministic-quality`, versão `quality-report-1`. A seleção pública de motor continua `deterministic`; nenhuma IA aprendida foi acrescentada.

`data_quality` registra as 42 combinações indicador/equipe: amostra original, utilizável e selecionada, IDs excluídos, motivos por família e fingerprint da máscara. Famílias exigem todos os seus indicadores ativos calculáveis, portanto a exclusão pode ser conservadora mesmo quando um valor isolado existe. Taxas por 90 exigem duração válida; geometrias exigem suas dependências; a guarda de orientação continua vigente. As famílias direcionais são bloqueadas em temporadas fora da allowlist V3, mesmo com orientação local coerente. A máscara é aplicada somente às evidências por jogo existentes; agregação usa soma de numeradores/denominadores e mantém fórmula, unidade, nulo, zero válido e datas. Não repõe partidas excluídas.

A suficiência deste modo exige cinco jogos em `xg_for`, `xg_against`, `shots_for`, `shots_against` e `pass_accuracy` nas duas equipes. Cinco é mínimo operacional, sem confiança calibrada. Cada regra ainda exige suas evidências e mínimos próprios; sem suporte, há abstenção. A releitura se limita à janela anterior ao dia do corte e confere os hashes do relatório original. Alteração entre leituras gera erro de dados, sem misturar versões. `full_snapshot_status="not_checked"` declara que o filtro não verifica o clone completo nem certifica a temporada. `spatial_season_certified` apenas reflete a allowlist existente.

JSON e Markdown exportam a política aplicada e as exclusões. A prévia `/v1/coverage` continua mostrando presença de arquivos, antes da inspeção do conteúdo. Clientes antigos podem omitir a opção; o frontend só a envia quando marcada. Reinstalar o pacote no ambiente da API após `git pull`, conforme README. CLI e Streamlit continuam usando o comportamento anterior. Validação e revisão de orientação: [evidências da versão](PENDING.md#3-evidências-da-versão-em-uso) e [CORE-02](PENDING.md#5-core-02-e-certificação).

## Erros e limites

Erros têm `{ "code": "...", "message": "..." }`. `INVALID_REQUEST`, `INVALID_ROSTER`, `INVALID_RESTRICTIONS`, `CONTEXT_CONFLICT`, `FUTURE_ROSTER` e `SEASON_NOT_CERTIFIED` retornam 422. `DATA_UNAVAILABLE_OR_INVALID` também retorna 422. Motor/modelo indisponível ou explicação obrigatória inválida retornam 503 com códigos específicos. Ocupação/limite de chamadas retorna 429; relatório expirado, 404; payload excedido, 413; erro inesperado, 500 sem stack trace.

Amostra insuficiente é um resultado HTTP 200 com abstenção, não falha de execução. V3 não certificada não é fallback para relatório legado; o cliente precisa solicitar outra capacidade explicitamente.

Entrada limitada a 64.000 bytes, notas a 4.000 caracteres, elenco a 60 atletas, janela HTTP a 20 jogos, uma análise concorrente e dez pedidos de análise por minuto/processo. Provedor local: uma geração concorrente, uma tentativa, timeout de 45 s, contexto 4.096 tokens e saída até 256 tokens/8.192 bytes. Não há garantia de interrupção instantânea do cálculo Python; janela e concorrência limitam o trabalho. Usar timeout do cliente de pelo menos 120 s para o modo com LLM nesta máquina.

Fluxo síncrono escolhido após medição real: análise legada de City em 2,65 s; primeira medição V3 pela API com LLM em 27,86 s. São medições locais, não SLA. JSON V3 pode ter vários MB; não montar automaticamente um visualizador integral. Usar campos estruturados e exportação para inspeção completa.

Até oito relatórios de no máximo 32 MB ficam em memória por processo durante até 300 s; acesso a expirados remove a entrada. Reinício perde todos; limite cheio remove o mais antigo. Um worker é recomendado porque o armazenamento não é compartilhado. Não há fila distribuída nem persistência em disco.

## Validação e pesquisa

```bash
python -I -B -m unittest discover -s tests -p test_service.py -v
python -I -B scripts/check_backend.py --data-root open-data/data --output-dir outputs/runs/backend_check_novo
python -I -B scripts/check_backend.py --data-root open-data/data --output-dir outputs/runs/backend_llm_check_novo --with-ollama
```

O último comando acessa somente Ollama local e exige o modelo/digest usado no ensaio. Cada destino deve ser novo. AppTest e ASGI TestClient não são inspeção visual do navegador.

Protocolo de pesquisa: [core_ai_protocol.json](core_ai_protocol.json). Rubrica humana: [tactical_review.schema.json](tactical_review.schema.json); escores 0=sem suporte, 1=parcial, 2=sustentado, NA=não avaliável. Nenhuma revisão especializada foi realizada por estes scripts.

Fine-tuning de explicação: instalar `.[training]` em ambiente isolado somente quando necessário. O provisionamento do modelo deve registrar revisão/hash/licença em `provision.json`; o ensaio usou `HuggingFaceTB/SmolLM2-135M-Instruct` na revisão `12fd25f77366fa6b3b4b768ec3050bf629380bac` (Apache-2.0). O pipeline não baixa pesos implicitamente:

```bash
python -I -B -m managerai.experiments.explainer_training --model-path outputs/runs/core_ai_model_20261031 --protocol docs/core_ai_protocol.json --output-dir outputs/runs/lora_novo
python -I -B -m managerai.experiments.independent --data-root open-data/data --protocol docs/core_ai_protocol.json --output-dir outputs/runs/independente_novo
```

O ajuste usa supervisão sintética de seleção de afirmações em português, sem decisão tática aprendida. O modelo ajustado não é promovido automaticamente. Não se sabe se essa tarefa atende à exigência acadêmica do professor. Configuração, partições, métricas completas e checkpoints reais ficam nos destinos registrados em PENDING.

Referências de implementação: [FastAPI — CORS](https://fastapi.tiangolo.com/tutorial/cors/), [testes](https://fastapi.tiangolo.com/tutorial/testing/), [Ollama — saídas estruturadas](https://docs.ollama.com/capabilities/structured-outputs), [SmolLM2 — autores e licença](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct), [PEFT — LoRA](https://huggingface.co/docs/peft/en/package_reference/lora).


## Frontend React e contrato verificável

A aplicação em `frontend/` usa React/TypeScript/Vite, Node 20.19+ ou 22.12+ e `npm ci` com lockfile. Instalação e comando conjunto em [README](../README.md#aplicação-web-local). `scripts/run_web.py` inicia API instalada em 8011 e Vite em 5173, somente loopback; Ctrl+C encerra os processos que criou. Para testar sem alterar ambientes funcionais, pode-se passar `--python /caminho/do/venv/bin/python`. O Python precisa ter o pacote atualizado instalado. Portas ocupadas não são substituídas.

`frontend/.env.example` documenta `VITE_API_BASE_URL` (pública, sem segredos) e `MANAGERAI_PROXY_TARGET` (proxy de desenvolvimento/preview). O modo padrão usa mesma origem por proxy. Para comandos separados, iniciar API com um worker em 8011 e executar `npm run dev` em frontend. Para verificar o build local: `npm run build && npm run preview`, somente loopback em 4173, proxy para a mesma API. O build estático não implementa um proxy de produção; implantação pública é uma tarefa separada.

As opções de mando/contexto/objetivo/estratégia/planos têm Literals canônicos em `options.py`. A API mantém os erros próprios do serviço mesmo após tipagem. Modelos HTTP de respostas em `http_schema.py` tipificam catálogo, capacidades, equipes, partidas, cobertura, evidências, suficiência, planos, comparação, modelos e explicação. O campo `display` é projeção aditiva de apresentação: identificação, perfis/períodos, pontos localizados existentes, títulos canônicos de métricas e fontes/hashes do relatório. Não calcula indicadores nem modifica schemas legados. `legacy_report` e proveniência V4.1 continuam preservados; a interface não depende de reconstruir esses objetos opacos.

Atualizar e conferir contrato, na raiz com um Python que importe o backend atual:

```bash
.venv-web/bin/python -I -B scripts/export_openapi.py
cd frontend
npm run types
npm run types:check
npm run build
cd ..
.venv-web/bin/python -I -B scripts/export_openapi.py --check
```

O OpenAPI real está versionado em `frontend/openapi.json`; `src/generated/api.d.ts` e `options.ts` são derivados reproduzíveis, sem servidor/dataset/modelo. O primeiro check detecta mudança no backend; o segundo, divergência entre JSON e TypeScript/opções. A CI faz ambos antes dos testes portáteis. O gerador é dependência de desenvolvimento e lê somente o contrato local conhecido; não faz parte do bundle da aplicação.

Ordenação `context-order-2`: objetivo `pressionar alto` não favorece R02, que descreve saída sob pressão adversária. Objetivos sem plano compatível são declarações sem bônus; prioridade explícita de `saida_sob_pressao` para R02 e de `proteger vantagem` para proteção defensiva é preservada. `ordering.objective_note` expõe a limitação também no relatório Markdown. Nenhuma regra/fórmula legada foi alterada.

O frontend invalida buscas/previews obsoletos, mantém identificação do pedido enviado quando o formulário muda, impede duplicatas, usa timeout de 120 s sem retry de análise e distingue a página recebida da cópia volátil no servidor. Expiração/falta da chave na exportação não apaga o relatório local nem simula download. A referência usa datas de calendário, sem conversão por timezone. Nenhuma nota, elenco ou relatório é persistido em localStorage. V3 só é solicitada explicitamente para recorte certificado; mudança de temporada anuncia redefinição.

Há seis indicadores priorizados, todos os demais em tabela sob demanda (47 no caso V3: 21+26), evidências por métrica, planos com condições/riscos e comparação sem eficácia estimada. Barras usam unidades compatíveis, porcentagens 0–100; não há score composto. Gráficos V3 usam taxas/pontos existentes no relatório, no plano 120×80 sem espelhamento. JSON integral não é renderizado. Evidências limitam a tabela inicial a 20 partidas; fontes são paginadas em lotes de dez; mapa limita renderização a mil pontos por equipe, avisando quando há corte visual. A exportação permanece integral.

Testes portáteis, com navegador Playwright instalado:

```bash
cd frontend
npx playwright install chromium
npm test
```

Fixtures sintéticas existem somente em `frontend/tests/`, sem importar dados fictícios no produto. Integração real opt-in requer API atual em 8011, frontend em 5173 e dados locais; para o teste de reinício, indicar Python instalado:

```bash
cd frontend
MANAGERAI_BACKEND_PYTHON="$PWD/../.venv-web/bin/python" npm run test:real
```

Pode-se usar um navegador Chromium já instalado por `PLAYWRIGHT_BROWSER_EXECUTABLE_PATH`. `MANAGERAI_REAL_ARTIFACTS` deve apontar a diretório novo para evidências; padrão temporário `/tmp/managerai-frontend-real`. O teste de ciclo inicia e encerra somente seus servidores adicionais em 8012/5178; não depende de serviços pagos. O teste de LLM é pulado se não estiver configurada; geração só é confirmada pelo status retornado, separado de configuração. O cenário 404 real usa perda da memória em reinício; TTL de 300 s é coberto separadamente por teste do backend com relógio controlado, sem fingir espera de cinco minutos no navegador.

Resultados da entrega, limites e inspeção visual estão nas [evidências da versão](PENDING.md#3-evidências-da-versão-em-uso). Evidência histórica pequena da pesquisa, com disponibilidade/configurações/resultados e hashes conferíveis, em [research_evidence.json](research_evidence.json). `python3 -B scripts/check_research_evidence.py --check` verifica o acervo local quando disponível; ausência de artefatos em outra máquina não bloqueia a interface determinística, nem deve ser apresentada como avaliação conferida naquela máquina.
