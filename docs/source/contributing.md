# Contributing

Guidelines for contributors — both for **documentation** and for **code**.
The meta-repo instructions in `AGENTS.md` are authoritative for the codebase.

## Documentation guidelines

### Language & tone

- The documentation site (`docs/source/`) is written in **English**.
- Use concise, imperative style; scientific content should be precise and
  reproducible.
- Existing Portuguese documents in `docs/` (architecture, reports) are
  maintained as-is; new content goes in English.

### Structure

- Add new pages under `docs/source/` and register them in the `index.md`
  toctree under the appropriate caption.
- Follow the existing page naming (`kebab-case.md`) and the section layout
  (Getting Started / Scientific Domains / Core Concepts / Engineering /
  API Reference).
- Mark anything **planned but not implemented** with a `:::{note}` or
  `:::{warning}` admonition — never document planned features as existing.

### MyST conventions

- Use MyST directives: `:::{note}`, `:::{warning}`, `:::{seealso}`.
- Fenced code blocks with the language tag (`python`, `bash`, `toml`).
- Reference other pages with `{doc}`/`{ref}` roles; link to files with
  Markdown links.
- Keep tables and parameter lists tight and factual.

### Examples

- Prefer **executable examples** (notebooks). The `notebooks/` directory holds
  the reference demos; convert/curate them with `myst-nb` when wiring them into
  the site (task `DOC-002`).
- Every example must state its prerequisites (DB running, network access for
  TLE/catalogs, etc.).

### Diagrams (Mermaid)

- Source diagrams live in `docs/source/diagrams/` (`.mmd`) and `docs/diagrams/`.
- **Validate** every Mermaid diagram before committing (use the Mermaid
  validator, then the preview), and keep `docs/architecture.md` in sync.

### API reference

- API pages are generated with **autodoc2** (see `docs/source/conf.py`).
- Public classes/functions need **docstrings** (NumPy or Google style) and
  type annotations; keep module-level docstrings with the file path, a short
  description, the BINGO collaboration copyright and `Last modified`.

## Code guidelines (summary)

- **Hexagonal**: `domain` → `application` (use cases + ports) → adapters/
  infrastructure. Never cross package boundaries via internal paths.
- **Models** use `pydantic` or `sqlmodel` (no `dataclass` in the domain).
- Value objects wrap **xarray + dask** (lazy/delayed).
- Persistence in **PostgreSQL** (SQLModel) + datasets in **HDF5**/`Zarr`.
- Astronomical calculations via **skyfield_provider**; catalog access via
  **astroquery (TAP)**; async downloads with **httpx**.
- Units follow {doc}`units_conventions`.

## Commands

```bash
uv sync                                    # sync the whole workspace
uv run pytest tests                        # meta-package suite
uv run --package radioskysims-<name> pytest packages/radioskysims-<name>/tests
uv run ruff check src packages/*/src       # lint
make docs                                  # build the docs site
```

## Pull-request workflow

1. Work in a branch (e.g. `feat/tod-<ticket>` for roadmap tickets).
2. Run lint + tests locally.
3. For docs-only PRs, run `make docs` and confirm no Sphinx warnings.
4. Package changes are committed **in the package submodule** first, then the
   submodule pointer is bumped in the meta-repo.
5. Reference the roadmap ticket / breakdown task in the PR description
   (`docs/tasks/use_case_full_breakdown.md`).
