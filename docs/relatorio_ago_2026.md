> **Documento histórico** — snapshot quantitativo com ``as-of: 2026-08-05``.
> Não deve orientar decisões correntes; veja o estado atual em
> `docs/architecture.md` e `docs/roadmap.md`.

# Relatório Snapshot — Situação Atual do RadioSkySim (Agosto/2026)

**Data de referência:** 2026-08-05  
**Branch analisada:** `dev`  
**Escopo:** consolidação do `TODO.md` e do conteúdo de `docs/` para visão de estado atual.

---

## 1) Resumo executivo

O projeto **RadioSkySim** apresenta base técnica sólida para simulação científica (arquitetura hexagonal, domínio rico, pipeline TOD funcional, evolução ativa de SkyMap), mas ainda possui pontos críticos para “produção robusta”:

- **Segurança:** pendência crítica com credenciais/versionamento e backlog de vulnerabilidades.
- **Arquitetura:** houve avanço relevante em DI/composition root, porém coexistem documentos com divergências de estado e débitos arquiteturais legados.
- **Qualidade:** grande volume de testes e documentação em expansão, mas lint ainda elevado e módulos grandes concentrando complexidade.
- **Operação científica:** performance com guias e limites definidos; pipeline TOD e SkyMap estão operacionais, com recomendações de hardening.

**Leitura rápida:** projeto em fase de **consolidação avançada** (bom para desenvolvimento científico e integração incremental), ainda não totalmente “clean” para governança de engenharia em escala.

---

## 2) Fontes usadas para este snapshot

- `TODO.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/code_quality.md`
- `docs/performance/PROFILING_GUIDE.md`
- `docs/architecture/current_architecture.md`
- `docs/architecture/technical_debt.md`
- `docs/architecture/refactoring_roadmap.md`
- `docs/architecture/target_architecture.md`
- `docs/architecture/module_dependencies.md`
- `docs/architecture/entrypoints.md`
- `docs/architecture/dependency_injection.md`
- `docs/architecture/application_ports.md`
- `docs/architecture/relatorio_auditoria_skymap_radioskysim.md`
- `docs/architecture/architecture_rules.md`
- `docs/architecture/bounded_contexts.md`
- `docs/_archive/reports_2026-01/SUMARIO_EXECUTIVO.md`
- `docs/_archive/reports_2026-01/ANALISE_RADIOSKYSIM.md`
- `docs/_archive/reports_2026-01/ROADMAP_SDLC.md`
- `docs/_archive/reports_2026-01/DOCUMENTATION_STATUS.md`

### Evidências diretas da base de código (cotejamento em 2026-08-05)

Além da leitura documental, este snapshot foi **cotejado contra o código real** em `src/` e `tests/`, com coleta objetiva de:

- imports entre camadas (`application`, `domain`, `infrastructure`);
- presença/ausência de módulos legados citados em relatórios;
- métricas atuais de tamanho por camada e maiores arquivos;
- compilação sintática (AST parse) do pacote;
- coleta de testes via `pytest --collect-only`;
- estado de lint via `ruff check ... --statistics`.

---

## 3) Descrição resumida do projeto

O **RadioSkySim** é um pacote Python para simulação e análise de céu em rádio (contexto BINGO), com foco em:

- modelagem de feixe (beam);
- satélites/tracks e geometria orbital;
- fontes locais e catálogos de rádio fontes;
- geração de **TOD** (Time Ordered Data);
- geração/análise de mapas HEALPix (SkyMap).

Arquitetura alvo e predominante: **Hexagonal (Ports and Adapters)** com organização por `domain`, `application`, `infrastructure`, `interfaces` e `bootstrap`.

---

## 4) Adesão à arquitetura DDD/Hexagonal

### Estado atual

**Pontos fortes**
- Separação de camadas está explicitada em estrutura e documentos canônicos.
- Bounded contexts mapeados (Beam, Satellite, SkyMap, TOD, Simulation, RadioSources).
- Ports em `application/ports` formalizados na Sprint 2.2.
- Composition root/DI consolidado no `bootstrap` (Sprint 2.4).

**Pontos de atenção**
- Há relatórios com momentos diferentes: alguns indicam vazamentos de camada (auditoria 16/07), outros registram correção parcial/total no `application` após Sprint 2.4.
- Persistem dívidas documentadas (duplicidade de caminhos de beam, módulos grandes, legados misturados).
- Necessário gate automatizado contínuo para evitar regressão arquitetural.

### Cotejamento docs × código (evidência objetiva)

Na base atual, ainda há importações que violam parcialmente o alvo arquitetural:

- `application -> infrastructure` (exemplos reais):
	- `src/radioskysims/application/services/catalog_services.py:35`
	- `src/radioskysims/application/services/sim_orchestrator.py:28,262,266,436`
	- `src/radioskysims/application/services/simulation_service.py:87`
- `domain -> application` (exemplos reais):
	- `src/radioskysims/domain/geometry/interface.py:18`
	- `src/radioskysims/domain/geometry/skyfield_provider.py:7`
	- `src/radioskysims/domain/simulation/simulation.py:1045`

Isso confirma evolução arquitetural relevante, porém **não completa**.

### Snapshot de maturidade arquitetural

- **Direção arquitetural:** correta ✅
- **Consistência plena entre módulos:** parcial ⚠️
- **Risco de dívida legada:** moderado/alto ⚠️

---

## 5) Tech stack comentado

- **Linguagem:** Python 3.x
- **Modelagem:** Pydantic/SQLModel
- **Dados científicos:** NumPy, Xarray, Dask (incluindo lazy/delayed)
- **Astronomia:** Skyfield, Healpy, PySM3, HiPS/FITS
- **Persistência:** PostgreSQL (docker), HDF5/Zarr para datasets
- **Interface:** Panel/HoloViews/Bokeh (GUI), CLI e notebooks
- **Qualidade/engenharia:** pytest, ruff, documentação Sphinx/MyST

Stack está bem alinhada ao objetivo científico, com bom equilíbrio entre modelagem física e infraestrutura prática.

---

## 6) Entrypoints e fluxo operacional

Conforme documentação arquitetural:

- **Entrypoint operacional principal:** `scripts/start_service.py`
- **Utilitário de banco:** `src/radioskysims/infrastructure/db/init_db.py`
- **Utilitário de documentação:** `scripts/check_docs.py`

`src/radioskysims/main.py` e outros blocos `main` em painéis aparecem como experimentais/legados em alguns documentos.

---

## 7) Casos de uso e estado funcional

### Contextos principais

- **Beam:** carregamento e avaliação de padrão de radiação.
- **Satellite:** curadoria/seleção orbital e tracks.
- **SkyMap:** geração, survey, análise estatística e espectral (CLI/GUI/notebook).
- **TOD:** síntese de temperatura de antena no domínio tempo × frequência.
- **Simulation:** orquestração end-to-end.

### Situação por maturidade (snapshot consolidado)

- **SkyMap:** avançado e operacional (com auditoria específica positiva).
- **TOD/Simulation:** funcional e em consolidação de robustez.
- **RFI/Noise/Catalog/Map:** há registros de lacunas/incompletudes em parte dos relatórios.

---

## 8) Qualidade de código (estado atual documentado + medido no código)

### Métricas medidas na base atual (2026-08-05)

#### Tamanho por camada (`src/radioskysims`)

- `domain`: **87 arquivos / 12.541 linhas**
- `application`: **31 arquivos / 4.497 linhas**
- `infrastructure`: **68 arquivos / 8.948 linhas**
- `interfaces`: **24 arquivos / 3.240 linhas**
- `bootstrap`: **5 arquivos / 484 linhas**
- `visualization`: **2 arquivos / 1.289 linhas**

#### Maiores arquivos atualmente

1. `domain/simulation/simulation.py` (1351)
2. `visualization/waterfall.py` (1251)
3. `application/services/simulation_service.py` (991)
4. `interfaces/gui/skymap/presenters.py` (920)
5. `infrastructure/processing/resource_processor.py` (864)

#### Integridade sintática

- Compilação via AST parse em todos os `*.py` de `src/radioskysims`: **0 erros**.

#### Testes

- Coleta com `pytest --collect-only -q --ignore=data/DB`: **860 testes coletados**.
- Observação operacional: sem `--ignore=data/DB`, há erro de permissão em `data/DB/conftest.py` durante coleta ampla na raiz.

#### Lint

- `ruff check src tests scripts --statistics`: **811 erros** no estado atual.
- Fixáveis diretos: **128** com `--fix` (+ correções adicionais com `--unsafe-fixes`).

### Leitura prática

- **Testabilidade:** boa base, com cobertura multi-camada.
- **Higiene de código:** ainda demanda esforço ativo (lint, módulos grandes, imports/estilo/logging).
- **Documentação técnica:** boa evolução, porém heterogênea entre áreas.

---

## 9) Simulação TOD — detalhamento do pipeline

Com base nos documentos canônicos e técnicos:

1. Interface/serviço chama composition root (`bootstrap`).
2. Builders montam configuração, logging, DB, repositórios e serviços.
3. `SimOrchestrator` coordena seleção de fontes e execução.
4. `SimulationService`/`SourceAssembler` agregam satélites, fontes locais e rádio fontes.
5. `Simulation` executa geometria + beam + simulador TOD.
6. Resultado sai como `xarray.Dataset` (com capacidade lazy/Dask).
7. Persistência em HDF5/Zarr e metadados/registro no PostgreSQL.

### Uso de settings, processor e memória

- Configuração central via `settings.toml` + credenciais por ambiente.
- `ResourceAwareProcessor` documentado para batch/chunks e controle de memória.
- Suporte a scheduler Dask (`threads`, `synchronous`, `distributed`), com recomendação de shutdown explícito em fluxos distribuídos.

---

## 10) Eficiência, gargalos e melhorias

Com base em `docs/performance/PROFILING_GUIDE.md`:

- Existem testes de performance com `pytest -m performance` e profiling via `cProfile/pstats`.
- Limites aceitos documentados para TOD, operações Healpy e interpolação de beam.
- Gargalos típicos: transformadas esféricas (`map2alm`) e overhead de primeira chamada/interpolação.

### Melhorias recomendadas (já alinhadas nos docs)

- reduzir cópias e overhead em loops;
- vetorização adicional;
- adoção seletiva de `float32` quando fisicamente aceitável;
- hardening de cache e estratégia de resolução para mapas grandes;
- reforço de telemetria e métricas de execução em CI/performance regressiva.

---

## 11) Novas features e avanços recentes

Evidências de evolução recente na documentação:

- consolidação de **Application Ports**;
- consolidação de **Dependency Injection/Composition Root**;
- amadurecimento do contexto **SkyMap** (CLI/GUI/notebook + casos de uso);
- organização de roadmap técnico em trilhas (segurança, qualidade, arquitetura, ciência/produto).

---

## 12) Riscos e pendências críticas

### Prioridade alta (P0)

1. **Segurança de credenciais**: manter enforcement para evitar regressão; no `settings.toml` atual os campos `ST_USER`/`ST_PWD` estão vazios e comentados para uso via ambiente.
2. **Vulnerabilidades de dependências**: atacar backlog critical/high.
3. **Gate contínuo de arquitetura**: automatizar verificação de imports proibidos por camada.

### Prioridade média/alta (P1/P2)

4. reduzir passivo de lint (foco em lotes por camada);
5. fatiar módulos “grandes” e reduzir acoplamento;
6. consolidar caminhos canônicos de beam/loaders e deprecar legados com plano explícito;
7. aumentar cobertura de integração/E2E nos fluxos mais críticos de simulação.

---

## 13) Roadmap sugerido (snapshot Ago/2026)

### Horizonte de 4 a 8 semanas

- **Semana 1-2:** segurança + higiene mínima (credenciais, vulnerabilidades, lint auto-fix, CI gates básicos).
- **Semana 3-4:** arquitetura (eliminação de vazamentos residuais, contratos estáveis, limpeza de legados).
- **Semana 5-8:** robustez científica (RFI/Noise/Catalog/Map), E2E e hardening de performance.

Meta de chegada: baseline de engenharia consistente com a maturidade científica já alcançada.

---

## 14) Cobertura explícita do pedido do TODO

O `TODO.md` pediu um relatório com:

- descrição resumida do projeto ✅
- adesão DDD ✅
- tech stack comentado ✅
- entrypoints ✅
- casos de uso ✅
- qualidade de código (linhas, módulos, lint, docs, type hints) ✅ *(com ressalva de variação temporal entre relatórios)*
- detalhamento da simulação TOD (settings, repository, processor, lazy arrays, memória) ✅
- análise de eficiência e gargalos ✅
- novos features ✅
- roadmap de evolução ✅

---

## 15) Conclusão

O RadioSkySim está em um ponto muito bom de **capacidade científica e funcionalidade**, com arquitetura bem direcionada e documentação rica. O passo decisivo de agosto/2026 é transformar esse avanço em **consistência operacional de engenharia**: segurança, limpeza arquitetural final, redução de dívida técnica e gates automatizados contínuos.

Em resumo: **motor científico forte, governança técnica em consolidação final**.

---

## 16) Documentos potencialmente desatualizados (outdated) segundo o código atual

Lista de documentos que merecem revisão porque parte das afirmações não bate mais com a base atual:

1. `docs/architecture/dependency_injection.md`
	- Declara “0 imports diretos de Infrastructure dentro de Application” após Sprint 2.4.
	- **Cotejo atual:** ainda existem imports diretos em `catalog_services.py`, `sim_orchestrator.py` e `simulation_service.py`.

2. `docs/architecture/current_architecture.md`
	- Registra pontos que incluíam `domain/satellite/main.py` e outros vazamentos daquele snapshot.
	- **Cotejo atual:** `src/radioskysims/domain/satellite/main.py` não existe mais.

3. `docs/architecture/technical_debt.md`
	- Itens como TD-004 e TD-007 citam artefatos específicos (ex.: `domain/satellite/main.py`, `IndentationError` em `application/tod_panel.py`).
	- **Cotejo atual:** módulo de satélite citado não existe e a varredura sintática atual encontrou **0 erros de compilação**.

4. `docs/architecture/module_dependencies.md`
	- Cita duplicidade entre `infrastructure/files/*` e `infrastructure/beams/loaders/*`.
	- **Cotejo atual:** não há `src/radioskysims/infrastructure/files/**/*.py`; há apenas `infrastructure/beams/loaders/*`.

5. `docs/code_quality.md`
	- Métricas de lint e volume de testes datadas (ex.: 797 issues; 843 testes em snapshot anterior).
	- **Cotejo atual:** 811 issues de lint e 860 testes coletados (com `--ignore=data/DB`).

> Recomendação: manter esses documentos, mas incluir “data de validade do snapshot” e uma seção “diferenças em relação ao estado atual” para evitar decisões com base em diagnóstico vencido.
