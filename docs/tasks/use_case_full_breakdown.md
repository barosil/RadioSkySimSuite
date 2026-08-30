# Use Case: breakdown completo de tasks

Este documento transforma o `/.prompts/use_case.md` em um conjunto acionável de tasks, estimativas, prioridades e critérios de aceitação. Serve como referência para sprints e para criação de tickets por área.

## Visão geral

O `use_case.md` cobre documentação, arquitetura, configuração, simulações (TOD, mapas), fontes (satélites, radio sources), visualização (waterfall), performance, formatos e testes. Abaixo as áreas divididas com tasks concretas.

---

## 1. Documentação e organização (Docs MyST)

- Objetivo: converter esqueleto em site MyST com exemplos executáveis e cobertura científica em inglês.
- Tasks
  - DOC-001: Criar estrutura MyST (index, quickstart, API reference) — 8h — Alta
  - DOC-002: Extrair notebooks relevantes e gerar versões myst-nb com outputs cacheados — 16h — Alta
  - DOC-003: Revisar e limpar docs históricos (lista para revisão antes de deletar) — 6h — Média
  - DOC-004: Escrever guidelines de contribuição para docs (style, idioma, exemplos) — 4h — Baixa
- Critério de aceitação: site MyST com Quickstart que reproduz um TOD mínimo; notebooks convertidos disponíveis.

## 2. Instalação e configuração

- Objetivo: documentar instalação, inicialização de DB e settings.
- Tasks
  - CFG-001: Documentar passos de instalação (requirements, uv, env) — 4h — Alta
  - CFG-002: Script `init_db` para criar schema inicial (migrations simples) — 6h — Alta
  - CFG-003: `settings.toml` examples e resolver utilitário (já existe) — 3h — Alta
- Critério de aceitação: `README` de instalação e script `init_db` funcionam em ambiente limpo.

## 3. Base de Dados e Persistência

- Objetivo: definir e implementar esquema para metadados (jobs, persisted maps, signals).
- Tasks
  - DB-001: Definir esquema inicial (jobs, persisted_maps, signals metadata) — 8h — Alta
  - DB-002: Implementar migrations iniciais (sqlite + alembic opcional) — 8h — Média
- Critério de aceitação: migrations aplicáveis e tabela jobs disponível.

## 4. Radiotelescope

- Objetivo: documentar e testar criação de radiotelescópio por parâmetros inline e via settings.
- Tasks
  - RT-001: Exemplos de instantiation inline e via settings + testes unitários — 6h — Média
  - RT-002: Função utilitária para plot OSM e visualização do feixe — 8h — Média
- Critério de aceitação: exemplos reproduzem mapas e plots localmente.

## 5. Satellites (TLE / RINEX)

- Objetivo: consolidar fluxos de criação de satélites, tracks e visualizações.
- Tasks
  - SAT-001: Documentar pipeline TLE → tracks → PSD → export signals.json — 8h — Média
  - SAT-002: Integrar RINEX pipeline e exemplos — 8h — Média
- Critério de aceitação: notebook demonstra criação de tracks e export para signals.json.

## 6. LocalSources e RadioSources

- Tasks
  - SRC-001: Documentar Sun source e custom local sources (exemplos) — 4h — Média
  - SRC-002: RadioSources: NVSS, TAP queries e exemplos de uso — 6h — Média
- Critério de aceitação: exemplos de uso e testes básicos.

## 7. Healpix Maps e Mapmaking

- Tasks
  - MAP-001: Documentar uso de Healpix maps na geração de TOD — 6h — Alta
  - MAP-002: Testes de integração para TOD ←→ Mapmaking — 8h — Alta
- Critério de aceitação: pipeline reproduce mapa a partir de TOD em testes de integração.

## 8. Simulações (TOD e Maps)

- Objetivo: consolidar APIs de simulação, parametrização via config e execução non-blocking.
- Tasks
  - SIM-001: Definir API pública para gerar TOD (signature e exemplos) — 6h — Alta
  - SIM-002: Implementar CLI `tod export` (tickets já criados) — 20h — Alta
  - SIM-003: Notebook helpers non-blocking (JobHandle / widget) — 12h — Alta
- Critério de aceitação: APIs documentadas e CLI capaz de gerar TOD mínimo.

## 9. Waterfall Visualization

- Tasks
  - VIZ-001: Exemplos de waterfall com limites de cor e widgets interativos — 8h — Média
- Critério de aceitação: notebook com waterfall interativo.

## 10. Units, Conventions, Performance

- Tasks
  - PERF-001: Documentar unidades e convenções (MHz, degrees, MJD) — 2h — Alta
  - PERF-002: Guia para Dask LocalCluster e tuning (n_workers, chunking) — 6h — Alta
  - PERF-003: Benchmark scripts e exemplos (mini-bench) — 8h — Média
- Critério de aceitação: guia de tuning e benchmark reproduzível.

## 11. File formats e APIs

- Tasks
  - IO-001: Documentar formatos suportados (NetCDF, Zarr, HDF5) e metadata — 4h — Média
  - IO-002: API docs automáticos (Sphinx apidoc) para módulos principais — 6h — Média
- Critério de aceitação: documentação de IO e apidocs gerados.

## 12. Arquitetura, Diagramas e Sequence Flows

- Tasks
  - ARCH-001: Diagramas C4 / sequence para use cases principais (TOD, background jobs) — 8h — Média
  - ARCH-002: Class/ER diagrams para DB e modelos — 6h — Média
- Critério de aceitação: diagramas atualizados em `docs/source/diagrams`.

## 13. Tests e QA

- Tasks
  - QA-001: Definir matriz de testes: unit, integration, e2e (notebooks) — 6h — Alta
  - QA-002: Implementar CI rodando testes rápidos em PRs — 8h — Média
- Critério de aceitação: CI configurado e testes de smoke passando.

## 14. Release, Changelog e Migração

- Tasks
  - REL-001: Checklist de release e changelog template — 4h — Baixa
  - REL-002: Guia de migração para usuários antigos (settings + notebooks) — 6h — Média
- Critério de aceitação: PR com changelog e guia inclusos.

---

## Priorização sugerida

- Fase 0 (imediata): DOC-001/002, CFG-001/002, SIM-001, SIM-002 (CLI foreground), DB-001
- Fase 1: Background runner (SIM-004), Notebook helpers (SIM-003), Jobs DB (DB-002)
- Fase 2: Performance tuning e integração HPC (PERF-003), diagrams, polish docs

## Como transformar em issues

- Cada task acima deve virar uma issue com tags: area, priority, estimate(h)
- Vincular issues menores (TOD-001..TOD-010) ao epic `TOD export CLI + Job Runner`.

## Observações finais

- Manter `settings.toml` como fonte primária de configuração — utilitário criado.
- Dask: usar `LocalCluster` para MVP; documentar caminho para `dask-mpi` caso se deseje HPC.
