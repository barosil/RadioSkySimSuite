# Documentação do Desacoplamento — RadioSkySim

Este diretório documenta a implementação fase a fase do plano de desacoplamento do
monólito `radioskysims` em um ecossistema de pacotes (ver
[`prompts/plan-radioSkySimDecoupling.prompt.md`](../../prompts/plan-radioSkySimDecoupling.prompt.md)).

## Visão geral

| Fase | Pacote(s) | Status | Doc |
|---|---|---|---|
| 0 | Fundação uv workspace | ✅ Concluída | [fase-00](./fase-00-fundacao-workspace.md) |
| 1 | `radioskysims-core` | ✅ Concluída | [fase-01](./fase-01-radioskysims-core.md) |
| 2 | `radioskysims-viz` + `radioskysims-beam` (piloto) | ✅ Concluída | [fase-02](./fase-02-piloto-viz-beam.md) |
| 3 | `radioskysims-skymap` | ✅ Concluída | [fase-03](./fase-03-radioskysims-skymap.md) |
| 4 | `radioskysims-sources` + `radioskysims-radiotelescope` + `gnsstools4astro` | ✅ Concluída | [fase-04](./fase-04-sources-radiotelescope-gnss.md) |
| 5 | `radioskysims-simulation` | ✅ Concluída | [fase-05](./fase-05-radioskysims-simulation.md) |
| 6 | `radioskysims-waterfall` | ✅ Concluída | [fase-06](./fase-06-radioskysims-waterfall.md) |
| 7 | Consolidação / meta-pacote / limpeza de shims | ✅ Concluída | [fase-07](./fase-07-consolidacao.md) |

## Convenções adotadas (decisions do plano)

- **uv workspace** (migração de Poetry) com `[tool.uv.workspace] members = ["packages/*"]`.
- **9 pacotes** por grafo de acoplamento real (não os 18 itens literais).
- Nomenclatura **própria por pacote**: `radioskysims_core`, `radioskysims_beam`, ...
  (não namespace único `radioskysims` via PEP 420).
- `domain/geometry` + `domain/tracks` no `radioskysims-core`.
- `domain/skymap` em pacote dedicado `radioskysims-skymap` (Fase 3).
- `bingo`, `analysis`, `arpls` e `domain/map` **fora de escopo**.
- Testes movem **junto com o código** para `packages/<nome>/tests/`.
- **Shims de compatibilidade** mantidos até a Fase 7 (imports antigos reexportam
  dos novos caminhos, marcados deprecated).

## Notas de arquitetura

- O diretório `radioskysim_orig/` é a **referência original** (sem git) e está
  **gitignored** — nunca vai para o remoto.
- A distribuição guarda-chuva `radioskysim` continua construindo `src/radioskysims/`
  (código legado + shims) e expõe CLI/GUI.
- O ambiente é reproduzido via `constraint-dependencies` derivadas de
  `requirements.txt` (o `poetry.lock` estava defasado e foi descartado).

## Submódulos

Cada pacote em `packages/*` é um **submódulo** com repositório próprio no GitHub
(`barosil/<pacote>`), registrado via `.gitmodules`. O repo raiz é o meta-pacote.

| Submódulo | Repo | Fase |
|---|---|---|
| `radioskysims-core` | github.com/barosil/radioskysims-core | 1 |
| `radioskysims-viz` | github.com/barosil/radioskysims-viz | 2 |
| `radioskysims-beam` | github.com/barosil/radioskysims-beam | 2 |
| `radioskysims-skymap` | github.com/barosil/radioskysims-skymap | 3 |
| `radioskysims-sources` | github.com/barosil/radioskysims-sources | 4 |
| `radioskysims-radiotelescope` | github.com/barosil/radioskysims-radiotelescope | 4 |
| `radioskysims-simulation` | github.com/barosil/radioskysims-simulation | 5 |
| `radioskysims-waterfall` | github.com/barosil/radioskysims-waterfall | 6 |
| `gnsstools4astro` | github.com/barosil/gnsstools4astro | 4 |

```bash
git submodule update --init --recursive   # após um clone do repo raiz
```
