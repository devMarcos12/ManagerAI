# V2.2 — marco A validado

Prévia de cobertura reativa por calendário, janela e presença de arquivos, sem abrir eventos. Avisos antes de executar para amostra pequena. Sem junção entre temporadas nem compensação por arquivos ausentes.

Apresentação descritiva com n e períodos por indicador. Qualquer métrica central (xG a favor/contra, chutes a favor/contra, passes certos, entradas no terço) ausente ou com menos de cinco jogos suprime conclusões comparativas e hipóteses amigáveis. JSON V1/V2 permanece inalterado, inclusive regras técnicas anteriores; detalhes técnicos continuam identificados como tal. Cinco jogos é um mínimo operacional, não significância estatística.

Português: singular/plural, percentuais, gols esperados e tentativas de pressão. Contexto manual permanece declarado, sem efeito nos cálculos/gatilhos. A janela agora fica fora do formulário para atualizar a prévia imediatamente; sua alteração limpa resultado anterior.

Validação antes de iniciar implementação V3: suíte completa 64 testes aprovados (9,640 s), mais suíte de interface A1 com 14 execuções aprovadas (5,755 s; inclui testes reutilizados). Baseline anterior: 48 testes aprovados. Logs em outputs/v22_v3_validation. Caso real Real Madrid × Barcelona confirma 1/10 e alerta antes/depois; City mantém JSON anterior byte a byte nos testes de integração.

Dois testes de apresentação anteriores foram adaptados: a fixture adversária sem passes agora exige abstenção; para testar a tradução de hipóteses, a fixture declara explicitamente passes calculáveis. Validações não foram removidas.
