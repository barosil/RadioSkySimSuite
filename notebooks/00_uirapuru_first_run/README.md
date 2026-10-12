# `notebooks/00_uirapuru_first_run/` — primeira execução do UIRAPURU

Instrumentação da simulação de **primeira luz** do radiotelescópio UIRAPURU,
com EIRP de satélites recalculado e fluxo solar do provider NoRP/NRO.

## Parâmetros do experimento

| parâmetro | valor |
|---|---|
| LO do DDC (`CENTRE_FREQUENCY_MHZ`) | **1120.0 MHz** (notch DC esperado) |
| `NUMBER_OF_CHANNELS` | **4096** (banda do backend 250 MHz → df = 250/4096 MHz) |
| `REQUESTED_INTEGRATION_TIME_S` | **30.0 s** |
| `CONSTELLATIONS` | **GPS, GALILEO, GLONASS, BEIDOU** |
| `INCLUDE_SATELLITES` / `INCLUDE_LOCAL_SOURCES` | **True** / **True** (Sol) |
| `BEAM_PATTERN_PATH` | `src/radioskysims/resources/beams/beampattern_horn01.csv` |
| `POINTING_ALT_DEG` / `POINTING_AZ_DEG` | **80.0°** / **9.0°** (fixo) |
| janela temporal | 1 h, passo de 30 s (`2026-10-11T13:00Z` → `14:00Z`) |
| fluxo solar | **NoRP/NRO** (`solar_flux.source = "nro"`) |

## Conteúdo

| arquivo | papel |
|---|---|
| `00_uirapuru_first_run.ipynb` | notebook que documenta e instrumenta a execução |
| `signals.json` | **EIRP recalculado** — por constelação **e** por satélite (NORAD) |
| `settings_first_run.toml` | perfil `uirapuru_first_run` (cópia do `settings.toml` raiz + ajustes) |
| `run_first_run.py` | runner: estimativa de tempo + execução (daemonizável) |
| `output/` | `run.log`, `estimate.json`, `uirapuru_first_run.nc` (+ `.json` sidecar) |

## `signals.json`

Gerado a partir de `BINGO_ASSEMBLY/notebooks/04_GNSS_SIGNAL_ESTIMATION.ipynb`
(link budget: C/N0 → P_rec → EIRP via FSPL). Usa o formato estendido aceito por
`SignalRepository`:

```jsonc
{
  "constellations": [ { "constellation": "GPS", "eirp_dbw": 26.05, "signals": [ ... ] }, ... ],
  "satellites":     [ { "norad_id": 38251, "constellation": "GPS", "eirp_dbw": 22.7 }, ... ]
}
```

Novos valores (mediana das estimativas por constelação):

| constelação | EIRP nominal (antigo) | **EIRP recalculado** |
|---|---|---|
| GPS | 24.6 dBW | **26.05 dBW** |
| GALILEO | 25.8 dBW | **28.90 dBW** |
| GLONASS | 21.1 dBW | **21.80 dBW** |
| BEIDOU | 24.6 dBW | **24.00 dBW** |

## Como executar

```bash
cd <raiz do projeto>

# interativo
.venv/bin/python notebooks/00_uirapuru_first_run/run_first_run.py

# daemonizado (sobrevive ao fechamento do console)
setsid nohup .venv/bin/python notebooks/00_uirapuru_first_run/run_first_run.py \
    > notebooks/00_uirapuru_first_run/output/run.log 2>&1 < /dev/null &
cat notebooks/00_uirapuru_first_run/output/run.pid   # se usar o launcher
tail -f notebooks/00_uirapuru_first_run/output/run.log
```

## Notas

- **Notch do DDC**: a LO em 1120 MHz cai no centro do grid (canal ~2048). O
  backend real remove/marca esse canal; o pós-processamento deve aplicar o
  notch (máscara) no waterfall antes da análise.
- Cobertura do NoRP: as frequências do NoRP são 1, 2, 3.75, 9.4, 17, 35 GHz —
  **apenas 1 GHz cai na banda do BINGO**. A média diária interpola/estrapola
  linearmente em frequência (o espectro solar é suave).
- A primeira execução usa `use_processor=True`; se a saída exceder a memória, os
  batches são gravados em disco automaticamente (streaming) e reabertos lazy.
