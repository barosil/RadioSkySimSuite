cat >> docs/audits/modules/beam_audit.md <<'EOF'

## BEAM-001 — Namespace legado na raiz

### Situação inicial

O projeto possuía dois namespaces concorrentes para o bounded context Beam:

- `radioskysims.beam`
- `radioskysims.domain.beam`

O namespace `radioskysims.beam` funcionava como uma camada de compatibilidade,
mas ainda continha uma implementação própria de `Beam` e uma `BeamFactory`.
Essa implementação era consumida por código de Application, pela GUI e por
testes.

Também existia o wrapper:

- `radioskysims.infrastructure.ports.beam`

que apenas reexportava os ports definidos na camada Application.

### Problemas identificados

- Duplicidade de modelos Beam.
- APIs incompatíveis entre o Beam legado e o Beam de domínio.
- Imports concorrentes para a mesma responsabilidade.
- Port definido corretamente na Application, mas reexportado pela Infrastructure.
- Risco de manutenção duplicada e divergência de comportamento.
- Dificuldade para identificar o namespace oficial.

### Alterações realizadas

- `BeamFactory` foi transferida para:

  `radioskysims.domain.beam.factory`

- O painel Beam passou a utilizar:

  `radioskysims.domain.beam.models.Beam`

- O padrão gaussiano do painel passou a ser representado por `xarray.Dataset`,
  conforme o modelo oficial do domínio.
- Os testes do painel foram atualizados para a API oficial.
- Os testes de contrato passaram a importar os ports diretamente de:

  `radioskysims.application.ports.beam`

- O diretório legado foi removido:

  `src/radioskysims/beam`

- O wrapper de port foi removido:

  `src/radioskysims/infrastructure/ports/beam.py`

- Foi criado um teste arquitetural para impedir:
  - a recriação do namespace legado;
  - novos imports de `radioskysims.beam`.

### Evidências de validação

- Testes do painel:

  `6 passed`

- Testes de contrato:

  `26 passed, 3 skipped`

- Suíte específica do Beam:

  `54 passed, 3 skipped`

- Teste arquitetural:

  `2 passed`

- Compilação:

  `python -m compileall -q src tests`

  concluída sem erros.

- Suíte global:

  executada com sucesso após a migração dos imports restantes.

### Resultado

Status: **RESOLVIDO**

Classificação anterior: **P1 — Alta**

Namespace oficial:

`radioskysims.domain.beam`

Port oficial:

`radioskysims.application.ports.beam`

### Commits

- `3c8a9c4` — remoção e migração principal do namespace legado.
- `50af176` — remoção do wrapper legado de port da Infrastructure.
EOF