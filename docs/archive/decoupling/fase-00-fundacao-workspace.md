# Fase 0 — Fundação de workspace (uv)

## Objetivo

Migrar o build-system de **Poetry** (`poetry-core` + `poetry-dynamic-versioning`)
para **uv workspace** com backend **hatchling**, criando o diretório `packages/`
e transformando o `pyproject.toml` raiz na distribuição guarda-chuva `radioskysim`
— **sem mover código ainda** (apenas tooling).

## O que foi feito

1. **Inicialização do projeto git**
   - `git init -b main` na raiz do workspace.
   - `radioskysim_orig/` (monólito original, sem git) **gitignored** — fica como
     referência local e nunca vai para o remoto.

2. **Cópia não destrutiva do código original**
   - `src/`, `tests/`, `docs/`, `notebooks/`, `scripts/`, `.prompts/`, `settings.toml`,
     `conf.py`, `Makefile`, etc. copiados de `radioskysim_orig/` para a raiz do novo repo.

3. **`pyproject.toml` raiz (distribuição guarda-chuva `radioskysim`)**
   - Build backend: `hatchling` + `hatch-vcs` (substitui `poetry-core` +
     `poetry-dynamic-versioning`).
   - `[tool.uv.workspace] members = ["packages/*"]`.
   - Extras por sub-pacote previstos (`core`, `beam`, `sources`, `radiotelescope`,
     `simulation`, `viz`, `waterfall`, `gnss`, `all`) — populados conforme as fases.
   - `[project.scripts]` preservados (`radioskysims`, `gnss4astro`).
   - Wheel inclui `src/radioskysims`, `src/gnsstools4astro`, `src/bingo`,
     `src/analysis`, `src/arpls`, `src/GNSStools4Astro`.

4. **Reprodução do ambiente testado**
   - O `poetry.lock` original estava **defasado** (não continha `pyccl`, `camb`,
     `healpy`, `georinex`, `sqlmodel`, `pydantic`, etc.) e foi descartado.
   - O ambiente real testado é descrito por `requirements.txt` (numpy 2.3.0,
     xarray 2025.6.1, astropy 7.1.0, pandas 2.3.0, dask 2026.x).
   - `constraint-dependencies` no `[tool.uv]` reproduzem esse ambiente (171 pins).
   - `constraints.txt` mantido como artefato legível (derivado de `requirements.txt`).

5. **Dependências runtime completas**
   - O monólito importa mais do que o `pyproject.toml` original declarava
     (astropy, numpy, sqlmodel, pydantic, psycopg2-binary, astroquery, healpy,
     h5py, h5netcdf, zarr, httpx, matplotlib, pysm3, pyvo, reproject, ...).
   - Todas declaradas no umbrella para que `uv sync` instale o ambiente completo.

6. **`gnsstools4astro` em top-level**
   - Movido de `src/GNSStools4Astro/gnsstools4astro/` para `src/gnsstools4astro/`
     para que `import gnsstools4astro` funcione com `src` no path (precedente
     para a Fase 4, que o transforma em membro do workspace).

7. **Limpeza**
   - Diretórios vazios legados (sobras de `__pycache__`) removidos —
     `src/radioskysims/beam/` etc. (git não rastreia diretórios vazios).

## Verificação (gate da fase)

```bash
uv sync                          # OK — resolve workspace completo
uv run pytest tests -q -m "not integration" --ignore=tests/performance
# → 1107 passed, 15 skipped, 1 xfailed
```

- `import radioskysims` e `import gnsstools4astro` OK.
- Ambiente reproduzido: numpy 2.3.0, xarray 2025.6.1, dask 2026.8.0,
  pandas 2.3.0, astropy 7.1.0.

## Design decisions respeitadas

- ✅ uv workspace (não Poetry) — decidido com usuário.
- ✅ Backend hatchling (não poetry-core).
- ✅ `poetry-dynamic-versioning` → `hatch-vcs`.
- ✅ Extras seletivos por pacote no umbrella.
- ✅ `radioskysim_orig` excluído do remoto (gitignore total) — decidido com usuário.

## Commit

`ce34742` — "Fase 0: fundação uv workspace — migração de Poetry para uv"
