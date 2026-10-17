# Avaliação e decisão sobre aprendizado de máquina

## Baseline entregue

Analítica descritiva, regras transparentes e apresentação determinística. Não há
modelo treinado, predição de vitória, rótulo de boa estratégia nem acurácia declarada.
O contexto manual não é tratado como variável causal.

## Decisão sobre treinamento

| Pergunta | Situação atual |
|---|---|
| Qual variável-alvo? | Não definida para recomendação; requer definição pela equipe |
| Como obter labels? | Não há rótulos validados de estratégia apropriada. Placar não é label de tática ideal |
| Quantos exemplos independentes? | 380 partidas no recorte; 760 observações equipe/partida compartilham os mesmos jogos e não são 760 exemplos independentes de recomendação |
| Baseline apropriado? | Indicadores históricos e regras condicionais auditáveis |
| Como medir melhora? | Primeiro fundamentação, coerência e avaliação de especialistas; um alvo preditivo futuro exige baseline próprio e teste temporal |
| Modelo esportivo pré-treinado relevante/licenciado? | Nenhum foi selecionado ou verificado nesta implementação; não há dependência desse recurso |

Fine-tuning fica adiado até existir tarefa-alvo defensável, rótulos e protocolo de
avaliação. Se houver experimento futuro, separar partidas cronologicamente, calcular
features apenas com passado e evitar o mesmo jogo dos dois lados da divisão. Escolher
métricas adequadas ao alvo e reportar tamanho amostral e limitações.

## Verificações executáveis

- Contratos: IDs, recorte, confronto, referência temporal e janela válidos.
- Temporalidade: primeira partida, pouca amostra, janela, mesmo dia, alvo e futuro.
  Um teste corrompe propositalmente arquivos sintéticos do alvo e futuro e confirma
  que o relatório permanece idêntico, pois esses arquivos não são lidos.
- Integridade: duplicações, equipes incompatíveis, arquivos ausentes, coordenadas,
  xG incompleto, contrapressão, desarmes e durações inválidas.
- Métricas: xG adversário, entradas por passe completo, entradas laterais e
  agregação ponderada por exposição/tentativas.
- Fundamentação: todas as referências emitidas pelas hipóteses resolvem para métricas
  calculáveis com a amostra mínima.
- Reprodução e segurança de arquivos: JSON idêntico para mesmas entradas/fontes,
  hashes rastreáveis e recusa de sobrescrever relatórios ou gravar na raiz bruta.
- Integração local opt-in: cobertura de 380 jogos/20 clubes, relatório City × Arsenal,
  recomputação independente de xG nos JSONs e caso sem histórico.

O tutorial contém os comandos completos, inclusive auditoria integral do recorte.
Os testes sintéticos são identificados como tais e não são evidência de desempenho
esportivo. As checagens automatizadas não substituem revisão metodológica humana.

## Revisão pela comissão técnica

Para cada hipótese, verificar rastreabilidade até partidas e eventos, interpretação
coerente, limites claros, riscos/pré-condições úteis e ausência de afirmações causais.
Registrar avaliação com justificativa e desacordos. Não há avaliação por especialistas
executada nesta entrega; não se reivindica eficácia das recomendações.
