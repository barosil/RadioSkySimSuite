# Fase 5 — `radioskysims-simulation` (o integrador)

## Objetivo

Extrair a camada de simulação (TOD, simulação, noise, RFI, mapmaking e
orchestrators) para `packages/radioskysims-simulation/`, refatorar o
composition root (`builders.py`) em builders por pacote (strategy pattern) e
quebrar o ciclo lazy `sim_orchestrator ↔ bootstrap.composition`.

## O que foi movido

| Módulo | Pacote simulation |
|---|---|
| `domain/{tod,simulation,noise,rfi,mapmaking}` | `radioskysims_simulation.domain.*` |
| `application/services/{simulation_service,tod_orchestrator,sim_orchestrator,noise_services,rfi_services,tod_services,mapmaking_service,map_services}.py` | `radioskysims_simulation.application.services.*` |
| `application/mapmaking/*` | `radioskysims_simulation.application.mapmaking` |
| `application/ports/{mapmaking,mapmaking_repository,simulations}.py` | `radioskysims_simulation.application.ports.*` |
| `application/tod_panel.py` | refatorado: `TODPanel(PanelApplication)` |
| `infrastructure/mapmaking/*` | `radioskysims_simulation.infrastructure.mapmaking` |
| `infrastructure/db/{simulation,mapmaking}_*` | `radioskysims_simulation.infrastructure.db` |
| `infrastructure/processing/resource_processor.py` | `radioskysims_simulation.infrastructure.processing` |
| `infrastructure/skymap/tod_projector.py` | `radioskysims_simulation.infrastructure.skymap` (integração TOD↔SkyMap) |

## Refactor do composition root (acoplamento crítico #4)

`bootstrap/builders.py` (monolítico, ~480 linhas) foi distribuído em builders por
pacote:

- `radioskysims_core.bootstrap.builders` → `build_logging`, `build_database`
- `radioskysims_beam.bootstrap.builders` → `_load_beam_from_csv`
- `radioskysims_radiotelescope.bootstrap.builders` → `build_configuration`
- `radioskysims_sources.bootstrap.builders` → `build_repositories`,
  `build_cosmology_components`, `build_local_sources_service`,
  `build_radiosources_use_cases`
- `radioskysims_simulation.bootstrap.builders` → `build_skymap_components`,
  `build_domain_components`, `build_services`, `build_simulation_context_dependencies`

O `bootstrap/builders.py` do umbrella virou **fino** (re-export/composição).
O `bootstrap/composition.py` do umbrella delega para
`radioskysims_simulation.bootstrap.composition` — **quebra o ciclo lazy**
(`sim_orchestrator` agora importa do composition de simulação, não do root).

O teste `tests/bootstrap/test_builders_optional_cosmology.py` foi atualizado para
monkeypatchear os builders nos módulos reais dos pacotes.

## Dependências

Integrador: `core`, `viz`, `beam`, `skymap`, `sources`, `radiotelescope` +
`numpy`, `astropy`, `xarray`, `dask`, `healpy`, `panel`, `holoviews`, `hvplot`,
`pydantic`, `sqlmodel`. **Sem** `pyccl`, `camb`, `astroquery`, `georinex`.

## Testes movidos (junto com o código)

`packages/radioskysims-simulation/tests/` (28 arquivos): domain/{tod,simulation,
noise,rfi,mapmaking}, application/{mapmaking,ports,services}, infrastructure/
{db,mapmaking,skymap}, performance/test_tod_simulation_speed.py.

Ficaram na raiz (integrados): `tests/application/services/test_sim_orchestrator_*`,
`tests/e2e/*`, `tests/integration/*`, `tests/bootstrap/test_builders_optional_cosmology.py`.

## Verificação (gate da fase)

```bash
uv run --package radioskysims-simulation pytest packages/radioskysims-simulation/tests
# → 282 passed

uv run pytest tests -q -m "not integration" --ignore=tests/performance
# → 191 passed (inclui os orchestrators e2e)
```

- `create_sim_orchestrator("uirapuru")` produz `SimulationContext` completo
  (DB vivo é requisito de ambiente — PostgreSQL parado no momento do gate).
- Todos os pacotes verdes: core 88, viz 5, beam 55, skymap 325, sources 165,
  simulation 282, gnss 21.
- Isolamento (uv.lock): simulation sem pyccl/camb/astroquery/georinex.

## Submódulo

`packages/radioskysims-simulation` → `github.com/barosil/radioskysims-simulation`
(commit `3c416b9`).

## Commit

`94c0db7` — "Fase 5: radioskysims-simulation — o integrador"
