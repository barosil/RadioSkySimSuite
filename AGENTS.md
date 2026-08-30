# AGENTS.md

Instruções para colaboradores e agentes automatizados no meta-repo **RadioSkySim**.

## Contexto

- Projeto em Python, **arquitetura Hexagonal** (Ports and Adapters), organizado
  como **uv workspace** com **9 pacotes** em `packages/*` (submódulos git) e um
  **meta-pacote** `radioskysim` na raiz (composition root + CLI/GUI + extras).
- Nomenclatura de imports **própria por pacote** (ex.: `radioskysims_core`,
  `radioskysims_beam`, ...) — **não** usar namespace único `radioskysims.*`.
- Documento canônico de arquitetura: `docs/architecture.md` (mantido
  continuamente). Detalhes por tópico em `docs/architecture/`.
- Plano de desacoplamento e documentação fase a fase:
  `prompts/plan-radioSkySimDecoupling.prompt.md` + `docs/decoupling/`.

## Layout dos pacotes

```
packages/<nome>/pyproject.toml        # hatchling + hatch-vcs; versão estática
packages/<nome>/src/<nome_import>/    # domain/ application/ ports/ adapters/ infrastructure/
packages/<nome>/tests/                # testes movem junto com o código
packages/<nome>/README.md
```

- Cada pacote é um **submódulo git** (`barosil/<nome>`, ver `.gitmodules`).
  Alterações dentro de um pacote são commitadas **no próprio pacote** e o
  ponteiro é atualizado no meta-repo.
- O meta-pacote `radioskysim` (raiz) contém apenas: `src/radioskysims/`
  (composition root `bootstrap/`, `interfaces/` CLI/GUI, `main.py`,
  `visualization/waterfall.py`, resíduos `domain/map` e `GNSStools4Astro`,
  `analysis`, `bingo`, `arpls` — vendorizados, fora de escopo). **Não** recriar
  shims de compatibilidade `radioskysims.* → pacote` (removidos na Fase 7).

## Comandos (uv workspace)

```bash
uv sync                                   # sincroniza o workspace completo
uv run pytest tests                       # suite do meta-pacote (raiz)
uv run --package radioskysims-<nome> pytest packages/radioskysims-<nome>/tests
                                          # suite de um pacote isolado
uv run ruff check src packages/*/src      # lint
```

- Ambiente reproduzido via `constraint-dependencies` (do `requirements.txt`);
  alterações de dependência precisam ser refletidas lá.
- Extras seletivos do umbrella: `core`, `viz`, `beam`, `skymap`, `sources`,
  `radiotelescope`, `simulation`, `waterfall`, `gnss`, `all`.

## Diretrizes de código

- **Hexagonal**: domain (entidades/value objects/regras) → application (casos de
  uso + ports) → adapters/infrastructure (integrações externas).
- Modelos com **pydantic** ou **sqlmodel** (sem `dataclass` no domínio).
- Value Objects encapsulam **xarray + dask** (lazy/delayed).
- Persistência em **PostgreSQL** (container, `settings.toml`) com registro
  SQLModel; datasets em **HDF5** (`h5netcdf`) ou **Zarr**.
- Cálculos astronômicos (tracks, ângulos, eventos) via **skyfield_provider**.
- Acesso a catálogos via **astroquery** (TAP); downloads preferencialmente com
  **httpx async**.
- Processor (`ResourceAwareProcessor`, em `radioskysims-simulation`) orquestra
  dask em chunks com controle de memória.
- Docstring no **nível do módulo** com caminho do arquivo, breve descrição,
  copyright BINGO Collaboration e `Last modified`.
- Anotações de tipo; imports do pacote de origem (nunca atravessar fronteiras
  via caminho interno de outro pacote).

## Unidades

- Frequência: **MHz** · Ângulos: **graus** (usuário) / **radianos** (interno) ·
  Tempo interno: **MJD/UTC** · Intervalos: **segundos** · Entradas ISO ·
  Fluxo: **Jy** · Temperatura de antena: **Kelvin**.

## Docs

- `docs/architecture.md` — canônico; atualizar diagramas Mermaid (validar com
  `mermaid-diagram-validator` e prévia com `mermaid-diagram-preview`).
- `docs/decoupling/` — documentação fase a fase do desacoplamento.
- `docs/source/` — build Sphinx (MyST).
- `notebooks/` — exemplos executáveis dos principais fluxos.
