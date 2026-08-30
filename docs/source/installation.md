# Installation

## Requirements

- **Python 3.11–3.14** (Linux, macOS or Windows/WSL)
- [uv](https://docs.astral.sh/uv/) (recommended workspace manager) **or**
  `python3` + `pip`
- [Docker](https://www.docker.com/) with the Compose plugin — optional, only
  needed for the PostgreSQL container used for persistence
- Optional: `git`

## Option A — uv workspace (recommended)

The project is a **uv workspace** whose members live in `packages/*`. Sync the
whole workspace from the repository root:

```bash
uv sync
```

This creates the environment and installs all package members in editable mode
with their dependencies.

```{note}
Environment versions are pinned through `constraint-dependencies` (from
`requirements.txt`). If you change a dependency, mirror it there and re-run
`uv sync`.
```

## Option B — Makefile / pip

```bash
make setup        # creates .venv + installs the package (editable) + deps
# or, on an existing .venv:
make install

# optional extras (hvplot, fastapi, ...)
make install-extra
```

Equivalent manual steps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[test,dev,docs]"
pip install -r requirements.txt
pip install -r requirements_extra.txt   # optional
```

## PostgreSQL (container, optional)

Used by the persistence layer (satellite elements, simulations, map-making
results). The compose stack also starts **Adminer** on
`http://localhost:8080`.

```bash
make postgres-up       # start postgres + adminer + backup containers
make postgres-status   # status and healthcheck
make postgres-psql     # open psql inside the container
make postgres-down     # stop containers
```

Default credentials come from `settings.toml [DB]` (`radio`/`radio`,
database `radioskysims`). Override via the `POSTGRES_*` environment variables
or a `docker/postgresql/.env` file.

```{warning}
Never commit credentials. The `[SPACETRACK]` section of `settings.toml`
contains SpaceTrack credentials — move them to a git-ignored
`credentials.env` (see `credentials.env.example`) or environment variables.
```

## Verify the installation

```bash
uv run pytest tests            # meta-package test suite (root)
uv run ruff check src packages/*/src

# console scripts
radioskysims --help
gnss4astro --help
```

To run the test suite of a single package in isolation:

```bash
uv run --package radioskysims-simulation \
  pytest packages/radioskysims-simulation/tests
```

## Building the documentation (this site)

```bash
make docs        # or: cd docs && make html
# output in docs/build/html/
```

## What you get

The install provides:

- the umbrella package `radioskysim` (composition root + CLI/GUI);
- the 9 decoupled packages under `packages/*`
  (`radioskysims-core`, `-beam`, `-skymap`, `-radiotelescope`, `-sources`,
  `-simulation`, `-waterfall`, `-viz`, and `gnsstools4astro`);
- example notebooks under `notebooks/`.

See {doc}`configuration` for how to point the runtime at your settings file,
and {doc}`quickstart` to run your first TOD.
