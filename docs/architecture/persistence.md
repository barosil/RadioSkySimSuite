# Persistência — RadioSkySimSuite

**Data:** 2026-09-01

## 1. Visão geral

O projeto usa dois mecanismos de persistência complementares:

- **PostgreSQL** (via SQLModel/SQLAlchemy) para metadados, catálogos e
  índices de execução (ex.: satélites selecionados, resumos de simulação);
- **HDF5** (`h5netcdf`) ou **Zarr** para os datasets físicos volumosos
  (arrays `xarray`/`dask` de TOD, mapas, waterfalls).

Essa separação é intencional: bancos relacionais para metadados
consultáveis, formatos científicos colunares/chunked para os arrays
propriamente ditos.

## 2. PostgreSQL / SQLModel

`radioskysims_core.db.engine.Database` (pacote `radioskysims-core`, usado
por todos os pacotes que precisam de persistência relacional):

- Credenciais carregadas via `load_config(key="DB")` (de `settings.toml` +
  variáveis de ambiente), com defaults de desenvolvimento (`radio`/`radio`/
  `localhost`/`5432`/`radioskysims`) — **nunca deve ir para produção com os
  defaults**.
- URI montada em `_build_uri()`: `postgresql+psycopg2://user:pass@host:port/db`,
  com `quote_plus` na senha (correto para caracteres especiais).
- `create_engine(self.uri, echo=False, future=True)` — engine única por
  instância `Database`, sessions via `sessionmaker(class_=Session,
  expire_on_commit=False)`.
- `__repr__` sanitiza a URL removendo tudo antes de `@` — **boa prática**
  para não vazar credenciais em `print(db)`/logs de erro que usem `repr`.
- `test_connection()`, `clear_db()` (via `SQLModel.metadata.drop_all`),
  `close()` (via `engine.dispose()`) como operações administrativas básicas.
- Eventos de banco emitidos via `log_db_event(slogger, ...)` (ver
  `logging.md §3`) para `connect`/`disconnect`/`drop_all`/`select`.

### 2.1 Achado de segurança — URI completa em log DEBUG (CORRIGIDO)

`_create_engine()` continha:

```python
logger.debug("Criando engine para URI: %s", self.uri)
```

`self.uri` continha a **senha em texto plano** (via `quote_plus`). Como
`configure_logging(enable_file=True)` (default) grava um `FileHandler` em
`logs/radioskysim_<timestamp>.json`, rodar a aplicação com `log_level=DEBUG`
persistia a senha do banco em disco, em JSON. Falha de **OWASP A09
(Security Logging and Monitoring Failures)** / exposição de credencial.

**Status: corrigido nesta rodada** — o log agora usa apenas `self.db`
(`host:port`, sem credenciais):

```python
logger.debug("Criando engine para %s", self.db)
```

## 3. HDF5 / Zarr

`radioskysims_simulation.domain.simulation.simulation` (`SimulationResult` e
correlatos) expõe:

- `to_zarr(path, chunk_s=..., target_mb=64.0, compute=True|False, **kwargs)`
  — grava um `xr.Dataset` em Zarr; com `compute=False` retorna um `delayed`
  do Dask, permitindo que o scheduler escreva cada chunk sob demanda (útil
  para datasets maiores que a RAM);
- `to_hdf5(path, engine="h5netcdf", **kwargs)` — grava via
  `xr.Dataset.to_netcdf(engine="h5netcdf")`; o backend `scipy` (NetCDF3) é
  explicitamente desencorajado no docstring por não suportar os recursos
  necessários;
- `save_result(...)`/`load_result(...)` (em `simulation.py` e replicado em
  `sim_orchestrator.py`) — fachada de alto nível que decide o formato
  (Zarr vs HDF5) e persiste também metadados (JSON/YAML sidecar) para
  reconstrução via `load_result`.
- `resource_processor.py` usa o mesmo `engine="h5netcdf"` como default para
  os batches intermediários gravados em disco (`batch_output_dir`), mantendo
  consistência de formato entre resultado final e batches parciais.

### 3.1 Escolha de formato — quando usar cada um

| Critério | Zarr | HDF5 (`h5netcdf`) |
|---|---|---|
| Escrita incremental/paralela (Dask `compute=False`) | Sim (nativo) | Não recomendado |
| Portabilidade single-file | Não (diretório de chunks) | Sim (arquivo único) |
| Uso atual dominante | Resultados grandes/streaming | Resultados intermediários e exports simples |

## 4. Estrutura de diretórios de dados

Conforme `settings.toml`/`quickstart.md`, a árvore em `data/` separa por
finalidade: `data/aux` (auxiliares Skyfield/efemérides), `data/TOD` (saída de
simulação), além de diretórios equivalentes para catálogos, cache HiPS,
banco (quando SQLite de desenvolvimento é usado) e mapas — cada pacote
resolve seus próprios subdiretórios via `radioskysims_core.config` em vez de
paths hardcoded (ver `AGENTS.md` — "evitar paths hardcoded").

## 5. Segurança de dados sensíveis

- Credenciais do PostgreSQL: `settings.toml` + env vars, **não versionadas**
  (confirmado resolvido pela auditoria de `architecture.md §7` — mesmo
  padrão já usado para SpaceTrack).
- `S608` (SQL hardcoded) aparece 2x na varredura `--select=ALL` de
  `code_quality.md §2.2` — recomenda-se revisão pontual para confirmar que
  não há concatenação de input de usuário em query SQL (risco de injection).
- Nenhuma outra exposição de segredo foi encontrada nesta auditoria além do
  item §2.1.

## 6. Recomendações

1. ~~Corrigir o log de URI completa em `Database._create_engine()` (§2.1)~~
   — **corrigido** nesta rodada.
2. Auditar as 2 ocorrências de `S608` (SQL hardcoded) para confirmar
   ausência de injection.
3. Documentar formalmente em qual cenário usar Zarr vs HDF5 no
   docstring/guia de usuário (`docs/source/`), hoje só implícito no código.
4. Considerar testes de contrato para `save_result`/`load_result`
   garantindo *round-trip* (persistir e recarregar sem perda de metadados)
   como parte da suíte de integração.
