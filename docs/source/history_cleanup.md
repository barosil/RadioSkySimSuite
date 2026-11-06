# Documentation History & Cleanup

This page tracks the review of **historical documentation** (task `DOC-003`).
The editorial policy (see `docs/CHANGELOG_DOCUMENTACAO_2026-08.md`) is:

1. **Do not delete technical history** — preserve baselines.
2. **Add a temporal delta** — mark documents with an `as-of` date and a
   revalidation note.
3. **Separate history from the current snapshot** — stale data must not drive
   decisions.
4. **Standardize validity** — quantitative reports carry `as-of`.

## Already handled

| Item | Action |
|---|---|
| `docs/source/index.md` legacy content | Moved to `docs/source/legacy_notes.md` (2026-08-29) |
| `docs/_archive/reports_2026-01/SUMARIO_EXECUTIVO.md` | Editorial banner + links to current snapshots (2026-08-05) |
| `docs/_archive/reports_2026-01/ANALISE_RADIOSKYSIM.md` | Editorial banner + links to current snapshots (2026-08-05) |
| `docs/architecture/dependency_injection.md` | Marked as Sprint 2.4 snapshot + revalidation 2026-08-05 |
| `docs/architecture/technical_debt.md` | Revalidation section + status per item (2026-08-05) |
| `docs/architecture/current_architecture.md` | Baseline 2026-07-16 + delta 2026-08-05 |
| `docs/architecture/module_dependencies.md` | Baseline 2026-07-16 + delta 2026-08-05 (AST recalc) |
| `docs/code_quality.md` | `Revalidação (as-of): 2026-08-05` |

## Pending review (candidates for archival or revalidation)

| Path | Status | Suggested action |
|---|---|---|
| `docs/_archive/reports_2026-01/DOCUMENTATION_STATUS.md` | historical | keep archived; verify links |
| `docs/_archive/reports_2026-01/INDICE_ANALISE.md` | historical | keep archived |
| `docs/_archive/reports_2026-01/ROADMAP_SDLC.md` | historical | keep archived; check roadmap relevance |
| `docs/_archive/reports_2026-01/SIMPLIFICACAO_IMPORTS_2026-01-24.md` | historical | keep archived (superseded by decoupling) |
| `docs/_archive/reports_2026-01/STATUS_PROJETO.txt` | historical | keep archived |
| `docs/architecture/_bounded_contexts.md` | outdated? | compare with `bounded_contexts.md`; merge or archive |
| `docs/architecture/target_architecture.md` / `refactoring_roadmap.md` | historical | marked `as-of` + link to `docs/archive/decoupling/` (2026-08-30) |
| `docs/architecture/relatorio_auditoria_skymap_radioskysim.md` | snapshot | add `as-of` banner |
| `docs/architecture/skymap_gui_plan.md` | snapshot | add `as-of` banner |
| `docs/source/barosi_docs.md`, `vanderson_docs.md` | legacy | linked from `index` as legacy; optionally move under an archive section |
| `docs/source/modules/*.md`, `apidocs/*`, `_static/api/*` | stale (monolith API) | **excluded from the Sphinx build** (2026-08-29) — files kept on disk; regenerate via autodoc2 for the decoupled packages (task `IO-002`) |
| `radioskym_orig/` (monolithic snapshot) | reference | keep as frozen reference; do not edit |
| `docs/relatorio_ago_2026*.md` | snapshot | marked `as-of: 2026-08-05` (2026-08-30) |

## Process

For each item above, when reviewed:

1. Add a top banner: `> **Historical document** — snapshot as of YYYY-MM-DD.`
2. Link to the current equivalent page (if any).
3. Move truly obsolete items into `docs/_archive/<year>-<month>/` with a short
   note in this file.
4. Never silently delete — record the decision here.
