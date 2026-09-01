# Pontos de Entrada do Projeto — RadioSkySimSuite

**Data:** 2026-09-01
**Escopo:** `src/radioskysims` (umbrella), `packages/*` (9 pacotes) e `scripts/`.

> **Status do documento:** substitui integralmente a versão de 2026-07-16, que
> descrevia entrypoints do monólito pré-desacoplamento (ex.:
> `src/radioskysims/domain/satellite/main.py`, `application/*_panel.py`
> soltos). Após o desacoplamento (Fases 1–7), cada pacote pode expor seu
> próprio `project.scripts`, e o umbrella concentra CLI/GUI de composição.

## Classificação de estado

- **Oficial**: ponto de entrada recomendado para uso corrente.
- **Experimental**: útil para desenvolvimento/protótipo, sem compromisso forte de estabilidade.
- **Legado**: ainda presente por compatibilidade, mas não recomendado para novos fluxos.
- **Obsoleto**: inconsistente com a arquitetura atual ou com alto risco de falha.

## 1. Console scripts (`project.scripts`)

| Comando | Pacote | Target | Estado | Observação |
|---|---|---|---|---|
| `radioskysims` | `radioskysim` (umbrella) | `radioskysims.bootstrap.skymap_cli:main` | Oficial | CLI principal; monta casos de uso de SkyMap/TOD via composition root. |
| `radioskysim-sources` | `radioskysims-sources` | `radioskysims_sources.interfaces.cli.sources_cli:main` | Oficial | CLI própria do pacote de satélites/rádio-fontes/fontes locais — **novo desde o desacoplamento**, não existia antes da Fase 4. |
| `gnss4astro` | `gnsstools4astro` | `gnsstools4astro.bootstrap.gnss4astro_cli:main` | Oficial | CLI de ferramentas GNSS/RINEX (download NAV/OBS, tracks por TLE). |

Nenhum outro pacote (`beam`, `core`, `viz`, `skymap`, `radiotelescope`,
`simulation`, `waterfall`) declara `project.scripts` próprio hoje — são
consumidos como bibliotecas pelo umbrella ou por `radioskysims-sources`/
`radioskysims-simulation`.

## 2. CLI do umbrella (`src/radioskysims/interfaces/cli`)

| Localização | Finalidade | Estado | Recomendação |
|---|---|---|---|
| `interfaces/cli/main.py` | Parser (argparse) que registra os subcomandos abaixo; ponto de entrada de `radioskysims` | Oficial | Grande (603 linhas) — candidato a subcomandos em módulos próprios (ver `relatorio_set_2026_v2.md §8.4`). |
| `interfaces/cli/commands/generate_skymap.py` | Subcomando `generate` — cria mapa sintético/PySM3 | Oficial | Bom exemplo de DTO → caso de uso → formatter (`relatorio_set_2026.md §8.4`). |
| `interfaces/cli/commands/analyze_skymap.py` | Subcomando `analyze` — estatística e `Cℓ` de mapas | Oficial | Usa `Protocol` para baixo acoplamento; referência de qualidade. |
| `interfaces/cli/commands/fetch_survey.py` | Subcomando de aquisição contínua de survey (HiPS) | Oficial | — |
| `interfaces/cli/commands/export_tod.py` | Subcomando `tod export` — roda `SimOrchestrator` em foreground/background | Oficial | Documentado em `docs/source/quickstart.md` (`quickstart-cli`). |
| `interfaces/cli/commands/export_worker.py` | Worker de background para exportação de TOD | Oficial | Consumido por `export_tod.py`/`jobs_cmd.py`; não é chamado diretamente pelo usuário. |
| `interfaces/cli/commands/jobs_cmd.py` | Subcomando `jobs` — status/cancelamento de jobs em background | Oficial | Usa `radioskysims_core.db.job_repository.JobRepository`. |
| `interfaces/cli/commands/progress.py` | Utilitário de leitura/escrita de arquivo de progresso | Oficial (suporte) | Consumido pelos comandos acima. |

## 3. GUI (Panel) do umbrella

| Localização | Finalidade | Estado | Recomendação |
|---|---|---|---|
| `bootstrap/skymap_gui.py` | Composition root da GUI de SkyMap | Oficial | Monta `interfaces/gui/skymap/app.py` com casos de uso injetados. |
| `interfaces/gui/skymap/app.py` | App Panel principal (SkyMap) | Oficial | — |
| `interfaces/gui/skymap/{controller,presenters,state,views,widgets}.py` | MVC/MVP do painel SkyMap | Oficial | `presenters.py` (885 linhas) é candidato a dividir por caso de uso (`generate`/`survey`/`analyze`). |
| `scripts/start_service.py` | Sobe `SimOrchestrator` (via `bootstrap.composition.create_sim_orchestrator`) + `TODPanel` | Oficial | Entrypoint operacional de GUI/TOD de baixo atrito — mantém a recomendação do documento histórico. |

## 4. "API" de notebook (não é REST)

| Localização | Finalidade | Estado | Recomendação |
|---|---|---|---|
| `interfaces/api/notebook.py` | `run_simulation(...)` para uso direto em notebooks — foreground (retorna resumo) ou background (`JobHandle`) | Oficial | Apesar do nome do diretório (`api/`), **não é uma API REST/FastAPI** — é uma fachada programática para notebooks. Renomear o diretório para `interfaces/notebook_api/` ou similar reduziria ambiguidade com o antigo `interfaces/api` do monólito (FastAPI, já removido). |
| `interfaces/api/widget.py` | Widget auxiliar para acompanhamento de jobs em notebook | Experimental | — |

**Nota:** o `interfaces/api` do monólito que expunha FastAPI
(`satellite_controller.py`, mencionado no documento de 2026-07-16) **não
existe mais** — confirmando que a violação "domain com responsabilidade de
interface web" apontada nos relatórios anteriores foi removida.

## 5. Bootstrap (composition root)

| Localização | Finalidade | Estado | Recomendação |
|---|---|---|---|
| `bootstrap/composition.py` | Composition root oficial; **delega** para `radioskysims_simulation.bootstrap.composition` | Oficial | Bootstrap fino, sem lógica própria — referência de boa prática. |
| `bootstrap/builders.py` | Builders auxiliares de composição | Oficial | — |
| `bootstrap/skymap_cli.py` | Composition root + entrypoint da CLI de SkyMap (`radioskysims`) | Oficial | — |
| `bootstrap/skymap_gui.py` | Composition root da GUI | Oficial | — |

## 6. Scripts utilitários (`scripts/`)

| Localização | Finalidade | Estado | Recomendação |
|---|---|---|---|
| `scripts/start_service.py` | Sobe GUI/TOD (ver §3) | Oficial | Manter. |
| `scripts/check_db.py` | Diagnóstico de conexão/schema PostgreSQL | Oficial | Manter como utilitário de infraestrutura. |
| `scripts/check_docs.py` | Verificador de docstrings/type hints (só cobre `src/`, não os pacotes) | Oficial (limitado) | Estender para varrer `packages/*/src` (ver sugestão em `relatorio_set_2026_v2.md §11`). |
| `scripts/regenerate_beam_csv.py` | Regenera fixtures CSV de beam | Experimental | Ferramenta de manutenção de dados de teste/exemplo. |
| `scripts/controlled_point_source_experiment.py` | Experimento controlado de fonte pontual | Experimental | Reprodutibilidade científica pontual, não é fluxo operacional. |
| `scripts/mapmaking_binned_scaling_experiment.py` | Experimento de escala de mapmaking binned | Experimental | Idem. |
| `scripts/plot_mapmaking_binned_scaling.py` | Plot dos resultados do experimento acima | Experimental | Idem. |

## 7. Entrypoints legados/obsoletos

| Localização | Finalidade | Estado | Recomendação |
|---|---|---|---|
| `src/radioskysims/main.py` | Monta `SatelliteManager`/`SatelliteFactory`/`SatelliteRepository`/`SpaceTrackClient` e abre `SatellitePanel` manualmente (engine SQLite hardcoded) | **Obsoleto** | Não usar como referência de bootstrap: cria engine própria (`sqlite:///db.db`) fora do composition root e da configuração central (`settings.toml`/`radioskysims_core.db.engine`). Mesma classificação do documento histórico, agora com imports apontando para o pacote `radioskysims-sources` (pós-desacoplamento) em vez do monólito. |
| `src/radioskysims/application/gain_panel.py` (bloco `main`) | Painel de ganho sintético para visualização manual | Experimental/Legado | Resíduo do umbrella pré-desacoplamento (ver `module_dependencies.md §5`); sem garantia de API estável. |
| `src/radioskysims/infrastructure/db/init_db.py` (bloco `main`) | Inicialização de schema via SQLModel | Oficial (utilitário) | Manter como utilitário de setup de ambiente; equivalente ao `check_db.py` em escopo mais restrito. |

## 8. Entrypoints por pacote (fora do umbrella)

Os 9 pacotes em `packages/*` são majoritariamente **bibliotecas** consumidas
pelo umbrella e por `radioskysims-simulation`. Exceções com CLI própria já
listadas em §1 (`radioskysims-sources`, `gnsstools4astro`). Nenhum outro
pacote expõe `__main__`/CLI própria fora de testes/exemplos internos.

## 9. Observações de estabilização

1. O desacoplamento **melhorou** a clareza de entrypoints: hoje há 3
   console scripts oficiais (`radioskysims`, `radioskysim-sources`,
   `gnss4astro`), contra 0 antes da Fase 4.
2. O entrypoint mais seguro para uso corrente de TOD/GUI continua sendo
   `scripts/start_service.py`; para SkyMap, o comando `radioskysims`.
3. `src/radioskysims/main.py` permanece obsoleto e deveria ser removido ou
   reescrito para usar o composition root oficial — ele é o único entrypoint
   que ainda constrói infraestrutura (engine SQLite) fora de
   `radioskysims_core.db`/`settings.toml`.
4. O diretório `interfaces/api/` deveria ser renomeado para deixar claro que
   é uma fachada de notebook, não uma API REST (ambiguidade com o antigo
   `interfaces/api` do monólito, já removido).
5. `scripts/check_docs.py` cobre apenas o umbrella; estendê-lo para
   `packages/*/src` fecharia uma lacuna de qualidade citada em
   `relatorio_set_2026_v2.md`.
