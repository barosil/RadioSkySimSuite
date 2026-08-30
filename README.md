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

O projeto segue **arquitetura hexagonal (Ports and Adapters)**, com persistência
em **PostgreSQL** (SQLModel/Pydantic) e cache/processamento local em
`data/temp`.

## Stack

- Python 3.11–3.14
- `xarray` + `dask` (processamento lazy e batches com controle de memória)
- `astropy` / `astroquery` (unidades, TAP, catálogos)
- `skyfield` (ephemeris, tracks, eventos)
- `healpy` / `PySM3` (mapas HEALPix)
- `SQLModel` + `SQLAlchemy` (persistência)
- `Panel` / `HoloViews` / `Bokeh` (visualização e GUI)
- `httpx` (async) para downloads/fetches
- `ruff` (lint/formatação), `pytest` (testes)

## Estrutura do projeto

```
src/radioskysims/
├── domain/            # Entidades, value objects e regras de negócio
│   ├── beam/ catalog/ common/ geometry/ localsources/ map/ noise/
│   ├── radiosources/ radiotelescope/ rfi/ satellite/ signal/ simulation/
│   ├── skymap/ source/ tod/ tracks/
├── application/       # Casos de uso e orquestração
│   ├── ports/         # Contratos (ports) da aplicação
│   └── services/      # Serviços e casos de uso
├── infrastructure/    # Adapters concretos (DB, IO, providers)
│   ├── beams/ config/ db/ external/ ports/ processing/ skymap/ utils/
├── interfaces/        # Entrypoints (API/CLI/GUI)
│   ├── api/ cli/ gui/
├── bootstrap/         # Composition Root (DI)
├── visualization/     # Plotagem (waterfall, skymap)
└── resources/         # Dados embutidos (beams, catálogos, satélites)

docker/postgresql/     # Postgres + adminer + backup (docker compose)
notebooks/             # Tutoriais e demonstrações
docs/                  # Documentação (Sphinx + MyST + Mermaid)
tests/                 # Suíte de testes (unit, integration, e2e)
```

## Requisitos

- Linux/macOS/Windows (WSL) com Python 3.11+
- [Docker](https://www.docker.com/) com plugin Compose (para o Postgres)
- Opcional: Git

## Instalação

Use o **Makefile** (recomendado):

```bash
make setup          # cria .venv e instala dependências + pacote em modo editável
make install        # instala dependências e o pacote (usa .venv existente)
```

Ou manualmente:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[test]"
pip install -r requirements.txt            # dependências completas pinadas
pip install -r requirements_extra.txt      # extras (fastapi, hvplot, ...)
```

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
from radioskysims.bootstrap.composition import create_sim_orchestrator

orchestrator = create_sim_orchestrator(telescope="bingo")
result = orchestrator.run(
    constellations=["GPS"],
    use_processor=True,
)
result.compute()
print(result.format_summary())
orchestrator.shutdown()   # libera cluster dask "distributed" se usado
```

Outros entrypoints:

```bash
python scripts/start_service.py    # inicia a GUI/TOD Panel
python scripts/check_db.py         # diagnostica/repara a conexão Postgres
radioskysims                       # CLI do SkyMap (entry point do pacote)
```

## Testes

```bash
make test        # roda pytest
```

## Documentação

- `docs/architecture.md` — arquitetura (canônica)
- `docs/diagrams/` — diagramas UML (Mermaid)
- `docs/source/` — documentação Sphinx (HTML/PDF)
- `docs/architecture/` — detalhes por tópico (bounded contexts, DI, entrypoints)

## Licença

MIT — veja `LICENSE`.

