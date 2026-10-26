# Provisionamento e auditoria do StatsBomb Open Data

Este guia usa o contrato versionado [statsbomb_snapshot.json](../src/managerai/statsbomb_snapshot.json). Ele fixa a revisão Git, hashes de controle e a cobertura por competição/temporada; consulte o JSON para números e pares exatos. O verificador é local, somente leitura e não acessa a rede. Os dados não fazem parte do wheel Python nem do Git ManagerAI.

## Provisionar um clone novo

Pré-requisitos: Git e Python 3.12+ com ManagerAI instalado ou executado a partir de `src`. Reserve espaço em disco, tempo e rede compatíveis com o clone completo; o custo varia conforme conexão e sistema de arquivos, sem prazo ou tamanho garantido por este guia. Execute na raiz do checkout ManagerAI e escolha `open-data/` somente se esse destino ainda não existir. **Não execute clone/checkout sobre o clone local existente.**

Linux/macOS:

```sh
git clone -c core.autocrlf=false https://github.com/hudl/open-data.git open-data
git -C open-data checkout --detach 4b73468fc5b0f1950f9f66fada70ad3a4f9327cb
git -C open-data rev-parse HEAD
PYTHONDONTWRITEBYTECODE=1 python3 -B -m managerai --data-root open-data/data verify-data
```

Windows PowerShell:

```powershell
git clone -c core.autocrlf=false https://github.com/hudl/open-data.git open-data
git -C open-data checkout --detach 4b73468fc5b0f1950f9f66fada70ad3a4f9327cb
git -C open-data rev-parse HEAD
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B -m managerai --data-root open-data/data verify-data
```

O último comando exige ManagerAI instalado. No checkout sem instalação, use `PYTHONPATH=src` no shell POSIX ou `$env:PYTHONPATH = 'src'` no PowerShell antes do comando Python. `-c core.autocrlf=false` preserva os bytes LF dos blobs Git, inclusive no Windows. A revisão impressa por `rev-parse` deve ser exatamente a do contrato. O resultado JSON com `status: "compatível"` e código de saída `0` é a comprovação automática; guarde o comando, a saída, a revisão e a versão do contrato no registro interno da equipe. Código `2` e `status: "incompatível"` exigem correção. O JSON contém `code`, `path`, `message` e `action` para cada lacuna.

`open-data/data` é a raiz de dados, enquanto `open-data/` é a raiz Git. É possível manter o clone em outro local:

```sh
python3 -B -m managerai --data-root /caminho/para/open-data/data verify-data
```

```powershell
$env:MANAGERAI_DATA_ROOT = 'C:\caminho\para\open-data\data'
python -B -m managerai verify-data
```

`--data-root` prevalece sobre `MANAGERAI_DATA_ROOT`. A variável também serve à interface. Não copie os dados para `data/raw/`; essa não é a raiz usada. Não grave relatórios, temporários ou resultados dentro de `open-data/`; use destino novo fora dos brutos. O clone é independente e ignorado pelo Git principal.

## O que o diagnóstico comprova

O modo rápido consulta Git local sem atualizar o clone, exige a origem aceita, revisão exata e worktree limpo, confere SHA-256 dos **bytes dos blobs Git** de README, licença, catálogo e 80 calendários, valida a estrutura dos calendários e compara cobertura por temporada. Ele enumera arquivos de eventos, escalações e 360, identifica partidas catalogadas sem arquivo e arquivos órfãos. Não lê integralmente os aproximadamente 16 GB de eventos/escalações/360. Assim, `arquivo presente` não significa `conteúdo estruturalmente válido`, nem `recorte certificado para V3`. A estrutura dos calendários é validada; a semântica dos eventos e a calculabilidade das métricas dependem dos testes/análises de recortes específicos. Só os pares em `v3_certified_recuts` no contrato são certificados para V3.

A origem canônica para provisionar é `https://github.com/hudl/open-data.git`. O clone local auditado tem remoto `https://github.com/statsbomb/open-data.git`; o contrato aceita esses dois nomes no GitHub, nas formas HTTPS e SSH descritas no JSON, **somente** com revisão, worktree, hashes e cobertura correspondentes. Não se aceita mirror arbitrário nem uma nova revisão por ter o mesmo nome. O verificador não consulta redirects pela rede.

Diagnóstico comum:

| Código | Ação |
|---|---|
| `DATASET_MISSING`, `ROOT_WRONG` | Provisione um clone novo ou aponte para sua pasta `data/`, não para `open-data/` ou `data/raw/`. |
| `GIT_METADATA_MISSING`, `GIT_ROOT_WRONG` | Use o clone Git inteiro; uma cópia isolada de JSONs não prova a revisão. |
| `ORIGIN_INCOMPATIBLE`, `REVISION_MISMATCH`, `WORKTREE_MODIFIED` | Confira o remoto e o HEAD; use um clone íntegro na revisão fixada. Investigue alterações sem reset/limpeza automática. |
| `LINE_ENDINGS_CHANGED` | O Git pode mostrar worktree limpo após converter LF para CRLF, mas os hashes usados pelo produto mudam. Crie um **novo** clone com `git clone -c core.autocrlf=false ...`; preserve o clone atual para investigação. |
| `README_MISSING`, `LICENSE_MISSING`, `CONTROL_HASH_MISMATCH` | Confira os arquivos de controle no checkout; não os substitua manualmente. |
| `CATALOG_MISSING`, `CATALOG_INVALID`, `CATALOG_HASH_MISMATCH` | Confira catálogo e revisão; catálogo inválido bloqueia a verificação de cobertura. |
| `SEASON_MISSING`, `SEASON_INVALID`, `MATCH_FILE_MISSING` | Confira a temporada/ID informado e reprovisione a revisão completa em outro clone. Uma partida sem eventos/escalação é lacuna, nunca zero. |
| `THREE_SIXTY_PARTIAL` | Aviso de cobertura informativa; 360 não é analisado pelo produto. Confira o clone se esse dado for necessário. |
| `ORPHAN_FILES` | Informação: arquivos sem partida no catálogo não entram nas análises. Diferença da contagem fixada é erro separado. |
| `PATH_OUTSIDE_ROOT` | Caminho ou link escapa da raiz; remova a referência insegura em um clone próprio. |

Para validação portátil sem dados: `python -B -m unittest discover -s tests -v`, com ManagerAI instalado e `MANAGERAI_RUN_LOCAL_TESTS` não definido. Os três relatórios congelados têm `eol=lf` em `.gitattributes` do ManagerAI para preservar comparações byte a byte em novos checkouts Windows; um checkout anterior à regra pode conservar CRLF até ser reprovisionado separadamente, sem editar as fixtures. Para a integração real opt-in, após `verify-data` compatível e opcionais disponíveis, defina `MANAGERAI_RUN_LOCAL_TESTS=1` e execute o mesmo comando. No PowerShell, defina também `$env:PYTHONUTF8 = '1'` antes dos testes reais: alguns testes legados leem textos sem `encoding=` explícito e `cp1252` pode falhar. A CI usa apenas fixtures sintéticas, sem download StatsBomb. Os testes reais incluem a fixture congelada e os recortes locais; não substituem avaliação científica integral.

## Licença, atribuição e atualização

O arquivo local auditado é `open-data/LICENSE.pdf`, *StatsBomb Public Data User Agreement*, com atualização indicada em 08/09/2023. O [README oficial da revisão](https://github.com/hudl/open-data/tree/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb) pede citar StatsBomb como fonte e usar seu logo ao publicar, compartilhar ou distribuir análises. O acordo local contém restrições observadas de edição, distribuição, reprodução, fornecimento a terceiros e exploração comercial dos dados/análises. “Open Data” não concede automaticamente licença permissiva irrestrita. Publicar código não concede direito de redistribuir dados, derivados, artefatos ou pesos. Isto registra os termos observados, sem aconselhamento jurídico; uma pessoa responsável pela finalidade de uso e distribuição deve confirmar autorizações antes de compartilhar ou explorar comercialmente. O repositório não designa uma pessoa nominal para isso.

Atualizações são mudanças próprias: não acompanhar `main`/`master` automaticamente. Para nova revisão, (1) abrir mudança específica; (2) reler README e licença; (3) regenerar o manifesto a partir do novo clone e revisar hashes/cobertura; (4) comparar versões de metadados e schemas; (5) rodar testes portáveis e integração real; (6) avaliar impacto nos recortes V3 certificados sem ampliá-los automaticamente; (7) atualizar README, estado e pendências; (8) obter aprovação da nova revisão. Até isso ocorrer, o verificador recusa uma revisão diferente, mesmo se os arquivos principais existirem.
