# RinexDownloader

RinexDownloader is a lightweight Python package designed to download, extract, and process GNSS RINEX data from the Brazilian RBMC (IBGE) network.

It provides a simple pipeline to:

- Download daily GNSS data from RBMC servers
- Extract compressed `.zip` archives
- Convert CRINEX (`.d`) files to standard RINEX (`.o`)
- Load data using `georinex`
- Export datasets to NetCDF using `xarray`
- Subset time intervals (e.g., 1-hour windows)

---

## 📡 Data Source

This package uses data from the Brazilian GNSS network maintained by the IBGE:

- RBMC (Rede Brasileira de Monitoramento Contínuo)

Data access endpoint:

https://geoftp.ibge.gov.br/informacoes_sobre_posicionamento_geodesico/rbmc/dados/

## 📦 Installation

Clone the repository and install locally:

```bash
pip install -e .
```

🔧 Requirements

- Python ≥ 3.9

- georinex

- xarray

- numpy

- requests

🚀 Quick Start

Run the example script:
```bash
python examples/run_download.py
```

