Revisão técnica detalhada — Decoupling RadioSkySim (2026-08-29)

Resumo rápido
- Esta revisão complementa o plano principal com foco em testabilidade, reprodutibilidade, escalabilidade, extensibilidade e manutenção para uso científico em HPC.

Pontos fortes
- Arquitetura hexagonal já presente facilita criação de packages e interfaces claras.
- Boa cobertura de testes atual que serve como defesa contra regressões.
- Precedente de packages (GNSStools4Astro) como referência.

Riscos críticos
- Mudança massiva de imports (130+ fontes, 148 testes) requer codemods e validação automatizada; sem isso o risco de regressão é alto.
- Vazamento de dependências pesadas entre pacotes pode inflar instalações e criar conflitos binários (netCDF4/numpy ABI).
- I/O e provedores externos (RINEX, SpaceTrack, TAP catalogs, healpy) precisam de contratos bem definidos para garantir interoperabilidade e testes determinísticos.

Recomendações técnicas (detalhadas)
1) Ports/Adapters e contratos
- Definir ports claros em `radioskysims_core.ports`:
  - `EphemerisProvider`/`TrackProvider` → adapters: `RinexAdapter`, `SpaceTrackAdapter`.
  - `GeometryProvider` → adapter padrão `SkyfieldGeometryProvider`.
  - `CatalogTapPort` → adapter padrão `AstroqueryTapAdapter`.
  - `SkymapEnginePort` → adapter padrão `HealpyEngineAdapter`.
- Todos os adapters devem implementar métodos para: fetch(query|file), parse(raw) -> TypedTrack/TypedSkyMap, metadata().
- Fornecer Fakes (test doubles) com fixtures determinísticos para cada adapter.

2) Contratos de tipos e unidades
- Tracks: time em ISO + MJD (documentado), ra/dec em graus, unidade de frequência em MHz, flux em Jy, erros/uncertainties opcionais.
- SkyMap: formatos xarray-friendly com coords ('freq','time','ra','dec' ou 'nside' conforme engine) e metadata incluindo healpix_nside quando aplicável.

3) Reprodutibilidade
- Criar utilitário `repro/experiment_manifest` que grava:
  - git commit + uncommitted diff hash
  - pyproject lockfile hash ou environment spec
  - provider inputs (RINEX file hash, SpaceTrack query timestamp, TAP query string)
  - RNG seeds
  - container image tag (se aplicável)
- Permitirá reproduzir runs científicos exatos.

4) Testabilidade e CI
- Tests por pacote em `packages/<nome>/tests/` (unit + integration superficial + fixtures).
- Testes de integração pesados (dados RINEX, TAP responses) devem usar fixtures armazenados (pequenos) e rodar em etapa separada de CI (nightly/optional) ou com marker `integration` que CI pode condicionar.
- Adicionar checks na pipeline: pre-commit (ruff, black), unit tests, mypy, package tests isolados, integração, coverage gate.

5) Escalabilidade e preparação para GPU
- Todas as operações de transformação/matemática devem aceitar e retornar xarray objects; evitar conversões para numpy arrays internas sem necessidade.
- Usar dask arrays/xarray for lazy evaluation; expor parâmetros de chunking em APIs de alto nível.
- Separar kernels que fazem redução/transformação pesadas em funções que possam ser reimplementadas com cupy/numba (backend-agnostic pattern).
- Planejar benchmarks de desempenho para identificar hotspots antes da migração a GPU.

6) Dependências e empacotamento
- Cada package deve declarar dependências mínimas no seu `pyproject.toml`; extras para funcionalidades pesadas (e.g., `[project.optional-dependencies]['full'] = ['pyccl','camb','healpy']`).
- CI deve validar que `uv sync --package <nome>` não instala dependências indesejadas para pacotes leves.

7) Observabilidade
- Expor métricas simples (timings, peak memory, bytes read) e usar logging estruturado.
- Preferir métricas baseadas em context managers/utilitários no `radioskysims-core` para reaproveitamento.

Checklist rápido de implementação (ordem sugerida)
- [x] Definir Ports mínimos no `radioskysims-core` (Ephemeris, Geometry, CatalogTap, SkymapEngine).
- [x] Implementar adapters padrão (Skyfield, Healpy, Astroquery, Rinex via georinex).
- [x] Criar fakes e fixtures para cada adapter.
- [x] Estabelecer `repro/experiment_manifest` e integrá-lo às pipelines de exemplo.
- [ ] Codemod para renomear imports + validação automatizada (unidade e integration).
- [ ] CI gating completo com package-level tests e coverage thresholds.
- [ ] Benchmarks e plano de migração para GPU.

Notas finais
- A prioridade inicial deve ser garantir contratos estáveis e test doubles; somente então migrar código massivamente com codemods e gates de CI.
- Implementar as recomendações reduzirá muito o custo de manutenção e tornará o projeto adequado para uso científico reprodutível e em HPC.
