import os
import requests
from datetime import datetime
import zipfile

def build_rinex_url(date, station, rinex_type):
    doy = f"{date.timetuple().tm_yday:03d}"
    year = date.year

    base_url = "https://geoftp.ibge.gov.br/informacoes_sobre_posicionamento_geodesico/rbmc/dados"

    station = station.lower()

    # RBMC moderno → zip diário
    filename = f"{station}{doy}1.zip"

    return f"{base_url}/{year}/{doy}/{filename}"


def download_file(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    print(f"Downloading: {url}")

    r = requests.get(url)

    if r.status_code != 200:
        raise RuntimeError(f"Erro ao baixar: {url}")

    if "html" in r.text[:200].lower():
        raise RuntimeError(f"Resposta inválida (HTML): {url}")

    zip_path = os.path.join(output_dir, "data.zip")

    with open(zip_path, "wb") as f:
        f.write(r.content)

    # extrair
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    os.remove(zip_path)

    # encontrar arquivos RINEX
    rinex_files = []
    for f in os.listdir(output_dir):
        if f.endswith(("o", "n", "rnx", "obs", "nav")):
            rinex_files.append(os.path.join(output_dir, f))

    if not rinex_files:
        raise RuntimeError("Nenhum arquivo RINEX encontrado no ZIP")

    return rinex_files