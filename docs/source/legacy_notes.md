# Legacy project notes (pre-decoupling)

> **Status:** preserved for traceability. This page captures the original
> monolithic-era working notes that used to live on the documentation landing
> page (`index.md`). The content below is historical and does **not** reflect
> the current decoupled package layout. See the [index](index) for current
> documentation.

## Original `index.md` content (archived 2026-08-29)

Bem-vindo à documentação do RadioSkySim!

- Visão Geral da API (antiga `api.md`)
- Satélites (antiga `modules/satellite.md`)
- Modelos Comuns (antiga `modules/common.md`)
- Intervalos Temporais (antiga `modules/time.md`)

## TODO

- FrequencyRange (antiga `modules/FrequencyRange.md`)

### BAROSI

- [x] Implementar uso das classes de Common no domínio Satélite.
- [x] CelestrakClient
- [x] SpaceTrackClient
- [x] Sat_ID
- [x] Constellation
- [ ] SatelliteFactory
- [ ] SatelliteRepository
- [x] SatSignal
- [ ] SignalFactory

### VANDERSON

- [x] 🔭 Radiotelescope
  - Objeto de Valor no domínio (SQLModel) com as propriedades: EarthLocation, FrequencyRange, Beam
- [x] 🔭 RadiotelescopeFactory
  - Classe na camada de serviços que recebe informações necessárias e retorna objeto `Radiotelescope`
- [x] 🔭 RadiotelescopePanel
  - Objetos na camada de apresentação que apresentam panel widgets para selecionar EarthLocation, FrequencyRange e Beam e orquestra criação do objeto radiotelescopio.
- [x] 📶 Beam
  - [x] 🧹 Revisar o código da classe Beam e do BeamFactory, verificar qualidade de código, documentação e lógica.
  - [x] Integrar domínio com painel, permitindo criação e instanciação de sinais na camada de aplicação.
  - [x] 📔 Construir visualização de código utilizando holoviews + panel em um notebook.
    - [x] Amplitude x ângulo (x frequencia x polarização), normalizado em dB, com marcação de FWHM e Ganho(dB).
    - [x] Ganho x Frequência (x polarização)
    - Considerar seleção de métrica de ganho.
  - [x] 🌃 Integrar visualização com o painel da camada de apresentação.

[Detalhes](vanderson_docs.md)

**Radiotelescope (Objeto de Valor no Domínio)** — `src/radioskysims/domain/radiotelescope/models.py`
Value object representando um radiotelescópio definido por: EarthLocation (lat, lon, alt), FrequencyRange (mín/máx) e Beam.

**RadiotelescopeFactory (Serviço de Criação)** — `src/radioskysims/domain/radiotelescope/factory.py`
Serviço que orquestra a criação de um Radiotelescope a partir de inputs crus (números, strings, ranges).

**RadiotelescopePanel (Camada de Apresentação)** — `src/radioskysims/application/radiotelescope_panel.py`
Interface interativa (Panel widgets) para selecionar localização, faixa de frequências e modelo de feixe.

**Beam (entidade e domínio)** — `src/radioskysims/beam/models.py`
Classe que representa o feixe de uma antena (padrão de radiação angular/frequencial), guardando dados (pattern, resolução, faixa de frequência) e calculando métricas (FWHM, ganho).

**Integrar domínio com painel (camada de aplicação)** — `src/radioskysims/application/beam_panel.py` e `src/beam_panel_test.py`
Conecta a lógica do domínio (Beam) com a interface interativa (Panel).

**Construir visualização (holoviews + panel em notebook)** — `notebooks/beam_visualization.ipynb`
Gráficos interativos: Amplitude x Ângulo (x Frequência x Polarização), normalizado em dB com marcação de FWHM e Ganho(dB); Ganho x Frequência; seleção de métrica de ganho.

**Integrar visualização com o painel da camada de apresentação** — `src/radioskysims/application/beam_panel.py`
Interface final onde o usuário sobe feixes, ajusta parâmetros e vê gráficos em tempo real.

## Original diagrams (legacy)

The original monolithic diagrams were PNG files that no longer exist. The
current diagram sources are Mermaid/draw.io files under `diagrams/` — see
{doc}`architecture_diagrams`.

