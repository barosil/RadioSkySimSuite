# RadioSkySim

Simulação e análise do céu de rádio visto por um radiotelescópio *single dish*
em modo de trânsito. Desenvolvido pela **colaboração BINGO**.

## Visão geral

O `RadioSkySim` modela e simula sinais observados por radiotelescópios do tipo
BINGO, combinando:

- **Beams** — carregamento e avaliação de padrões de feixe (CSV/analítico);
- **Satélites** — elementos orbitais (TLE), tracks e geometria via Skyfield;
- **Fontes locais** — Sol e outras fontes de fluxo conhecido;
- **Catálogos de rádio fontes** — ingestão via TAP/astroquery (NVSS, Specfind);
- **TOD** — síntese de *Time Ordered Data* (temperatura de antena) com
  processamento consciente de memória (batches + dask);
- **SkyMap** — geração, transformação e análise de mapas HEALPix (Healpy, PySM3, HiPS).

O projeto segue **arquitetura hexagonal (Ports and Adapters)**, organizado como
**uv workspace** com **9 pacotes** em `packages/*` (submódulos git) e um
**meta-pacote** `radioskysim` na raiz (composition root + CLI/GUI + extras
seletivos). Persistência em **PostgreSQL** (SQLModel/Pydantic) e datasets em
**HDF5/Zarr**.

> O documento canônico de arquitetura é `docs/architecture.md` (mantido
> continuamente). Detalhes por tópico em `docs/architecture/`.

## Stack

- Python 3.11–3.14
- `uv` (workspace, ambientes e dependências reproduzidas)
- `xarray` + `dask[distributed]` (processamento lazy e batches com controle de memória)
- `astropy` / `astroquery` (unidades, TAP, catálogos)
- `skyfield` (ephemeris, tracks, eventos)
- `healpy` / `PySM3` (mapas HEALPix)
- `SQLModel` + `SQLAlchemy` (persistência)
- `Panel` / `HoloViews` / `Bokeh` (visualização e GUI)
- `httpx` (async) para downloads/fetches
- `ruff` (lint/formatação), `pytest` (testes)

## Estrutura do projeto

```
packages/
├── radioskysims-core/           # kernel: config, db, paths, domínio comum
├── radioskysims-beam/           # padrões de feixe e propriedades físicas
├── radioskysims-radiotelescope/ # perfis de radiotelescópio (antenas, pointing, backend)
├── radioskysims-sources/        # satélites, Sol, catálogos de rádio (TAP)
├── radioskysims-simulation/     # TOD + processamento consciente de memória
├── radioskysims-skymap/         # mapas HEALPix
├── radioskysims-viz/            # visualização (matplotlib/holoviews)
├── radioskysims-waterfall/      # waterfall (canal × tempo)
└── gnsstools4astro/             # ferramentas GNSS (repo próprio)

src/radioskysims/                # meta-pacote `radioskysim` (composition root)
├── bootstrap/                   # composition root + builders (DI)
├── interfaces/                  # CLI/GUI (skymap, tod, painel)
└── visualization/               # waterfall (legado)

docker/postgresql/               # Postgres + adminer + backup (docker compose)
notebooks/                       # tutoriais e demonstrações executáveis
docs/                            # documentação (Sphinx + MyST + Mermaid)
tests/                           # suíte de testes do meta-pacote
```

Cada pacote em `packages/<nome>/` segue o layout hexagonal:

```
packages/<nome>/pyproject.toml     # hatchling + hatch-vcs; versão estática
packages/<nome>/src/<nome_import>/ # domain/ application/ ports/ adapters/ infrastructure/
packages/<nome>/tests/             # testes movem junto com o código
```

> Cada pacote é um **submódulo git** (`barosil/<nome>`, ver `.gitmodules`).
> Alterações dentro de um pacote são commitadas **no próprio pacote** e o
> ponteiro é atualizado no meta-repo. Os imports são **próprios por pacote**
> (ex.: `radioskysims_core`, `radioskysims_beam`, …).

## Requisitos

- Linux/macOS/Windows (WSL) com Python 3.11+
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes/workspace)
- [Docker](https://www.docker.com/) com plugin Compose (para o Postgres)
- Opcional: Git

## Instalação

Use o **uv workspace**:

```bash
uv sync                          # sincroniza o workspace completo (9 pacotes + meta)
```

Ou via **Makefile** (recomendado — inicializa submódulos + extras de dev/docs):

```bash
make setup                       # submodules + uv sync (test/dev/docs)
make install                     # uv sync no .venv existente
```

> O ambiente é reproduzido via `constraint-dependencies` (do `requirements.txt`);
> alterações de dependência precisam ser refletidas lá.
> Extras seletivos do umbrella: `core`, `viz`, `beam`, `skymap`, `sources`,
> `radiotelescope`, `simulation`, `waterfall`, `gnss`, `all`.

### PostgreSQL (container)

```bash
make postgres-up      # sobe postgres + adminer + backup via docker compose
make postgres-down    # derruba os containers
make postgres-logs    # acompanha os logs
make postgres-reset   # derruba e recria (dados preservados em data/DB)
```

O acesso padrão é configurado em `settings.toml [DB]` (`radio`/`radio`,
`radioskysims`). Para sobrescrever, exporte as variáveis `POSTGRES_*` ou crie um
arquivo `.env` na pasta `docker/postgresql/`.

> ⚠️ **Segurança**: não commite credenciais. `settings.toml` contém credenciais
> do SpaceTrack — mova-as para `credentials.env` (veja `credentials.env.example`)
> ou variáveis de ambiente.

## Uso rápido

```python
from radioskysims_simulation.bootstrap.composition import create_sim_orchestrator

orchestrator = create_sim_orchestrator(telescope="default")
result = orchestrator.run(
    constellations=["GPS"],
    use_processor=True,
)
print(result.format_summary())
orchestrator.shutdown()   # libera cluster dask "distributed" se usado
```

> Perfis de radiotelescópio em `settings.toml`: `[radiotelescopes.uirapuru]` e
> `[radiotelescopes.default]` (cópia do Uirapuru). O dataset fica em
> `result.simulation_result.dataset`.

Outros entrypoints:

```bash
radioskysims                       # CLI do SkyMap/TOD (entry point do meta-pacote)
radioskysim-sources                # CLI de fontes de rádio/Sol
gnss4astro                         # CLI de ferramentas GNSS (download, tracks, sinais)
python scripts/start_service.py    # inicia a GUI/TOD Panel
python scripts/check_db.py         # diagnostica/repara a conexão Postgres
```

## Testes

```bash
uv run pytest tests                        # suíte do meta-pacote (raiz)
uv run --package radioskysims-<nome> pytest packages/radioskysims-<nome>/tests
                                           # suíte de um pacote isolado
uv run ruff check src packages/*/src       # lint

make test                                  # atalho: uv run pytest tests/
make lint                                  # atalho: ruff check + format --check
```

## Documentação

- `docs/architecture.md` — arquitetura (canônica)
- `docs/architecture/` — detalhes por tópico (bounded contexts, DI, entrypoints)
- `docs/diagrams/` — diagramas UML (Mermaid)
- `docs/source/` — documentação Sphinx (HTML/PDF)

## Licença

MIT — veja `LICENSE`.

