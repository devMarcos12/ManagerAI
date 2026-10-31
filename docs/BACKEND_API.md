# Integração com o Core HTTP

O contrato de serviço é `2.0.0`. Os relatórios legados mantêm `1.0.0` e `1.1.0` dentro de `legacy_report`. O serviço não prevê vitória, escalação ideal ou eficácia de estratégias. A aplicação histórica funciona sem LLM.

## Instalação e execução

Em ambiente novo escolhido pelo operador, a partir deste checkout:

```bash
python3 -m venv /tmp/managerai-backend-env
/tmp/managerai-backend-env/bin/python -m pip install '.[api,v3,experiments]'
MANAGERAI_DATA_ROOT="$PWD/open-data/data" /tmp/managerai-backend-env/bin/python -I -B -m uvicorn managerai.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

Esse é um serviço local, sem autenticação multiusuário. Não expor publicamente sem uma implantação específica que trate autenticação, TLS e limites por usuário. CORS fica fechado por padrão; `MANAGERAI_CORS_ORIGINS=http://localhost:3000` libera somente a origem indicada. O cliente não pode escolher caminho de dados, destino de arquivos, URL de provedor ou credenciais.

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
