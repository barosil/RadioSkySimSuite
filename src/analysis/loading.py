"""Carga lazy e redução dos datasets de simulação e observação.

Estratégia de memória (validada neste ambiente):
  - Abrir com ``xr.open_dataset(..., chunks=...)`` → as reduções ficam lazy
    (dask), nunca materializando os arquivos de 13–22 GB inteiros.
  - Reduzir ANTES de materializar: somar polarizações e agregar fontes no
    dataset lazy; só então ``.compute()`` o resultado pequeno (time × frequency).
  - Ler apenas ``T_antenna`` (nunca ``power`` junto quando não for preciso) —
    cada variável tem ~12 GB no arquivo de simulação.
  - Não usar ``dask.array.from_array`` sobre memmap gigante (criação de um
    array de 13 GB levou ~104 s); a carga via ``xr.open_dataset(chunks=...)``
    é a via recomendada.

Unidades: a coordenada ``frequency`` dos arquivos .nc está em **Hz** e é
normalizada para **MHz** (padrão dos demais módulos do projeto).
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import xarray as xr

from ._utils import _freq_to_mhz

# Constante de Boltzmann (J/K) — usada em ObservationData.to_power_spectrum
K_B = 1.380649e-23

# Polarizações co-pol (as cruzadas *_CROSS são ignoradas por padrão)
CO_POLARIZATIONS = ("H_COPOL", "V_COPOL")


def reduce_polarization(da, polarizations=CO_POLARIZATIONS):
    """Soma ``T_antenna`` sobre as polarizações indicadas (mantém lazy).

    Parameters
    ----------
    da:
        DataArray com dimensão ``polarization``.
    polarizations:
        Nomes das polarizações a somar (ex.: ``("H_COPOL", "V_COPOL")``).

    Returns
    -------
    xr.DataArray
        Mesmas dims de ``da`` sem a dimensão ``polarization``.
    """
    pols = list(da["polarization"].values)
    missing = [p for p in polarizations if p not in pols]
    if missing:
        msg = f"Polarizações ausentes no dataset: {missing} (disponíveis: {pols})"
        raise KeyError(msg)
    return da.sel(polarization=list(polarizations)).sum("polarization", keep_attrs=True)


def load_sim_lazy(
    path,
    polarizations=CO_POLARIZATIONS,
    agg_source: str = "sum",
    chunks: dict | None = None,
    decimate_freq: int = 1,
) -> xr.DataArray:
    """Carrega o .nc de simulação **lazy** e reduz para ``(time, frequency)``.

    O dataset de simulação tem dims ``(time, frequency, polarization, source,
    pointing)`` com ~13 GB (``T_antenna`` + ``power``). Este loader:

    - lê apenas ``T_antenna`` (não ``power``);
    - soma ``T_antenna`` sobre as polarizações indicadas (co-pol por padrão);
    - agrega ``source`` e ``pointing`` (soma por padrão — ``T_antenna`` é
      aditiva entre fontes; use ``agg_source="mean"`` para a média);
    - normaliza a frequência para MHz;
    - retorna um DataArray **lazy** ``(time, frequency)`` — pequeno
      (~29 MB materializado para o arquivo atual), pronto para ``.load()``.

    Parameters
    ----------
    path:
        Caminho do .nc de simulação.
    polarizations:
        Polarizações a somar (``reduce_polarization``).
    agg_source:
        ``"sum"`` (total de T_antenna sobre fontes) ou ``"mean"``.
    chunks:
        Dicionário de chunks para ``xr.open_dataset``. O padrão
        ``{"time": 100, "frequency": 500}`` gera blocos de ~90 MB.
    decimate_freq:
        Subsample da frequência (mantém cada ``decimate_freq``-ésimo canal)
        antes de retornar — útil para reduzir canais sem perder lazy.

    Returns
    -------
    xr.DataArray
        ``T_antenna`` com dims ``(time, frequency)``, freq em MHz, lazy (dask).
    """
    if chunks is None:
        chunks = {"time": 1000, "frequency": 2048}
    ds = xr.open_dataset(path, chunks=chunks)
    da = ds["T_antenna"]  # só T_antenna (não power)
    da = reduce_polarization(da, polarizations)  # soma pols → (time, freq, source, pointing)
    if str(agg_source).lower() == "sum":
        da = da.sum(dim=["source", "pointing"], keep_attrs=True)
    else:
        da = da.mean(dim=["source", "pointing"], keep_attrs=True)
    if decimate_freq and decimate_freq > 1:
        da = da.isel(frequency=slice(None, None, decimate_freq))
    da = _freq_to_mhz(da)
    da = da.transpose("time", "frequency")
    da = da.rename("T_antenna")
    return da


def load_obs_lazy(
    path,
    chunks: dict | None = None,
    decimate_freq: int = 1,
) -> xr.DataArray:
    """Carrega o .nc observacional **lazy** como ``(time, frequency)``.

    O arquivo observacional tem ``power (time, frequency)`` com ~22 GB e
    cadência de 0.3 s (337600 amostras × 32768 canais). Este loader apenas
    abre lazy, normaliza a frequência para MHz e (opcionalmente) decima a
    frequência — **não materializa nada**. Use ``resample``/``ObservationData``
    para reduzir tempo antes de ``.compute()``.

    Parameters
    ----------
    path:
        Caminho do .nc observacional.
    chunks:
        Dicionário de chunks. Padrão ``{"time": 2000, "frequency": 2048}``
        (~33 MB por bloco).
    decimate_freq:
        Subsample da frequência (mantém cada ``decimate_freq``-ésimo canal).

    Returns
    -------
    xr.DataArray
        ``power`` com dims ``(time, frequency)``, freq em MHz, lazy (dask).
    """
    if chunks is None:
        chunks = {"time": 2000, "frequency": 2048}
    ds = xr.open_dataset(path, chunks=chunks)
    da = ds["power"]
    if decimate_freq and decimate_freq > 1:
        da = da.isel(frequency=slice(None, None, decimate_freq))
    da = _freq_to_mhz(da)
    da = da.transpose("time", "frequency")
    da = da.rename("power")
    return da


def load_sim_data_reduced(
    path,
    polarizations=CO_POLARIZATIONS,
    agg_source: str = "sum",
    chunks: dict | None = None,
    decimate_freq: int = 1,
) -> xr.Dataset:
    """Cria o dataset ``sim_data_reduced`` (já materializado).

    Equivalente a ``load_sim_lazy(...)`` seguido de ``.load()``: o resultado
    reduzido é pequeno (~29 MB), então é seguro materializar. Retorna um
    ``xr.Dataset`` com a variável ``T_antenna`` e dims ``(time, frequency)`` —
    sem as dimensões de satélites/localsources/radiosources.

    Returns
    -------
    xr.Dataset
        ``T_antenna`` (time, frequency), freq em MHz.
    """
    da = load_sim_lazy(
        path,
        polarizations=polarizations,
        agg_source=agg_source,
        chunks=chunks,
        decimate_freq=decimate_freq,
    )
    return da.load().to_dataset()


def list_sources(path) -> list[tuple[str, str]]:
    """Lista as fontes de um .nc de simulação: ``[(source, source_type), ...]``.

    Item 6 do roteiro: para calibrar usando satélites GNSS ou radiosources,
    precisamos saber quais fontes existem no arquivo e seus tipos
    (``satellite``, ``localsource``, ``radiosource``).

    Parameters
    ----------
    path:
        Caminho do .nc de simulação (tem coordenadas ``source``/``source_type``).

    Returns
    -------
    list[tuple[str, str]]
        Pares ``(nome da fonte, tipo)`` na ordem do arquivo.
    """
    ds = xr.open_dataset(path)
    try:
        sources = np.asarray(ds["source"].values)
        stype = np.asarray(ds["source_type"].values)
    finally:
        ds.close()
    return list(zip([str(s) for s in sources], [str(t) for t in stype]))


def load_sim_sources(
    path,
    polarizations=CO_POLARIZATIONS,
    agg_pointing: str = "sum",
    chunks: dict | None = None,
    decimate_freq: int = 1,
) -> xr.DataArray:
    """Carrega um .nc de simulação **mantendo a dimensão ``source``** (lazy).

    Item 6 do roteiro: a calibração local precisa de passagens individuais de
    satélites/radiosources, então **não** agregamos as fontes (diferente de
    ``load_sim_data_reduced``, que soma tudo). O resultado é um DataArray lazy
    ``(time, frequency, source)`` — as fontes podem ser fatiadas por nome.

    Parameters
    ----------
    path:
        Caminho do .nc de simulação (satélites, radiosources, ...).
    polarizations:
        Polarizações a somar (``reduce_polarization``).
    agg_pointing:
        ``"sum"`` (padrão) ou ``"mean"`` sobre a dimensão ``pointing``.
    chunks:
        Chunks para ``xr.open_dataset``. Padrão ``{"time": -1, "frequency": 2048}``
        (lê o tempo inteiro por bloco; mantém ``source`` inteiro).
    decimate_freq:
        Subsample da frequência (mantém cada ``decimate_freq``-ésimo canal).

    Returns
    -------
    xr.DataArray
        ``T_antenna`` com dims ``(time, frequency, source)``, freq em MHz,
        lazy (dask).
    """
    if chunks is None:
        chunks = {"time": -1, "frequency": 2048}
    ds = xr.open_dataset(path, chunks=chunks)
    da = ds["T_antenna"]  # só T_antenna (não power)
    da = reduce_polarization(da, polarizations)  # (time, freq, source, pointing)
    if str(agg_pointing).lower() == "sum":
        da = da.sum("pointing", keep_attrs=True)
    else:
        da = da.mean("pointing", keep_attrs=True)
    if decimate_freq and decimate_freq > 1:
        da = da.isel(frequency=slice(None, None, decimate_freq))
    da = _freq_to_mhz(da)
    da = da.transpose("time", "frequency", "source")
    da = da.rename("T_antenna")
    return da


def build_obs_cache(
    path,
    out,
    decimate_freq: int = 8,
    n_bins: int = 2048,
    interval_s: int = 120,
    chunk_s: int = 40000,
) -> Path:
    """Constrói o cache (média) da observação via leitura h5py direta.

    O arquivo observacional é HDF5 com gzip (chunks ``(200, 32768)``): o dask
    descomprime tudo com alto overhead (o resample de 24 h pode passar de
    10 min). Esta função lê a hiperslab decimada (cada ``decimate_freq``-ésimo
    canal) em blocos de tempo e faz o coarsen com numpy — ~5 min para os 24 h,
    usando ~10-15 GB de RAM.

    O resultado (ex.: ``730×2048``, ~12 MB) é salvo em ``out`` (netCDF) e pode
    ser lido instantaneamente nas próximas execuções — evita reler os 22 GB.

    Parameters
    ----------
    path:
        Caminho do .nc observacional (HDF5 com gzip).
    out:
        Caminho do arquivo de cache a gravar (``*.nc``).
    decimate_freq:
        Subsample da frequência (mantém cada ``decimate_freq``-ésimo canal).
    n_bins:
        Nº de canais de frequência na saída (coarsen por média de pares).
    interval_s:
        Largura do bin temporal (segundos) da média de saída.
    chunk_s:
        Tamanho (em amostras de tempo) de cada bloco de leitura.

    Returns
    -------
    Path
        Caminho do cache gravado.
    """
    import h5py  # noqa: PLC0415

    path = Path(path)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(path, "r") as f:
        time_ns = np.asarray(f["time"][:], dtype=np.int64)  # ns desde o epoch
        freq_hz = np.asarray(f["frequency"][:], dtype=np.float64)
        n_t, n_f = f["power"].shape
        # epoch a partir de units: b'nanoseconds since 2025-02-27 12:12:17'
        units = f["time"].attrs["units"]
        units = units.decode() if isinstance(units, (bytes, np.bytes_)) else str(units)
        epoch = np.datetime64(units.split("since ")[-1].strip().replace(" ", "T"), "ns")

        # 1) leitura decimada (cada decimate_freq-ésimo canal), em blocos
        freq_idx = np.arange(0, n_f, decimate_freq)
        arr = np.empty((n_t, freq_idx.size), dtype=np.float64)
        data = f["power"]
        for i in range(0, n_t, chunk_s):
            hi = min(i + chunk_s, n_t)
            arr[i:hi] = data[i:hi, freq_idx]

    # 2) coarsen frequência → n_bins (média de pares)
    freq_factor = max(1, int(round(freq_idx.size / n_bins)))
    nf = (freq_idx.size // freq_factor) * freq_factor
    arr = arr[:, :nf].reshape(n_t, -1, freq_factor).mean(axis=2)
    n_bins_out = arr.shape[1]
    freq_bin_mhz = freq_hz[freq_idx[:nf]].reshape(-1, freq_factor).mean(axis=1) / 1e6

    # 3) coarsen tempo → interval_s (média)
    dt_s = float(np.median(np.diff(time_ns))) / 1e9
    time_factor = max(1, int(round(interval_s / dt_s)))
    nt = (n_t // time_factor) * time_factor
    arr_t = arr[:nt].reshape(nt // time_factor, time_factor, n_bins_out).mean(axis=1)
    time_bin = epoch + time_ns[:nt].reshape(nt // time_factor, time_factor).mean(axis=1).astype(
        "timedelta64[ns]"
    )

    # 4) grava cache
    ds = xr.Dataset(
        {"power": (("time", "frequency"), arr_t)},
        coords={"time": ("time", time_bin), "frequency": ("frequency", freq_bin_mhz)},
    )
    ds["power"].attrs["units"] = "power"
    ds.to_netcdf(out, engine="h5netcdf")
    return out


# ──────────────────────────────────────────────────────────────────────
# Análise prévia de chunks — antes de qualquer carga pesada
# ──────────────────────────────────────────────────────────────────────
def _format_bytes(n: float) -> str:
    """Formata bytes de forma legível (B → GiB)."""
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(n) < 1024.0 or unit == "TiB":
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} TiB"


def _recommend_chunks(sizes: dict, target_mb: float = 64.0) -> dict:
    """Sugere chunks (dicionário p/ ``xr.open_dataset(chunks=...)``).

    Estratégia simples e determinística: define o chunk da menor dimensão como
    a dimensão inteira (ou a que couber no orçamento) e ajusta as demais para
    que o produto `prod(sizes)*itemsize` fique perto de ``target_mb``.
    """
    dims = list(sizes)
    if not dims:
        return {}
    itemsize = 8  # float64
    # começa com a dimensão mais rápida (última) inteira e reduz até caber
    chunks = {d: s for d, s in sizes.items()}
    total_bytes = math.prod(sizes.values()) * itemsize
    # ordem de redução: das dimensões maiores para as menores (exceto a última)
    order = sorted(dims[:-1], key=lambda d: sizes[d], reverse=True)
    for d in order:
        while total_bytes > target_mb * 2**20 and chunks[d] > 1:
            chunks[d] = max(1, chunks[d] // 2)
            total_bytes = math.prod(chunks.values()) * itemsize
    return chunks


def analyze_chunks(path, print_report: bool = True) -> dict:
    """Analisa a estrutura de um arquivo de dados **antes** de carregá-lo.

    Lê apenas metadados (não materializa os dados): dims, variáveis, tamanho
    não-comprimido por variável, layout de chunks reais no disco (HDF5) e uma
    sugestão de chunking para ``xr.open_dataset(..., chunks=...)``. Útil para
    decidir a estratégia de carga lazy sem tocar nos 13–22 GB dos arquivos.

    Parameters
    ----------
    path:
        Caminho do arquivo (``*.nc``, HDF5/h5netcdf).
    print_report:
        Se ``True``, imprime um relatório formatado (retorna o dict na mesma).

    Returns
    -------
    dict
        ``{"path", "size_bytes", "dims", "variables", "h5_chunks",
        "recommended_chunks"}``.
    """
    import h5py  # noqa: PLC0415

    path = Path(path)
    info = {
        "path": path,
        "size_bytes": path.stat().st_size,
        "dims": {},
        "variables": {},
        "h5_chunks": {},
        "recommended_chunks": {},
    }

    # ── metadados xarray (dims, vars, dtype, tamanho não-comprimido) ──
    ds = xr.open_dataset(path)
    info["dims"] = dict(ds.sizes)
    for v in ds.data_vars:
        da = ds[v]
        nbytes = int(np.prod(da.shape, dtype=np.int64)) * da.dtype.itemsize
        info["variables"][v] = {
            "dims": tuple(da.dims),
            "shape": tuple(da.shape),
            "dtype": str(da.dtype),
            "uncompressed_mb": nbytes / 1e6,
        }
    ds.close()

    # ── layout de chunks reais no disco (HDF5) ──
    try:
        with h5py.File(path, "r") as f:
            for key in f:
                obj = f[key]
                if isinstance(obj, h5py.Dataset) and key not in ("time", "frequency"):
                    info["h5_chunks"][key] = {
                        "chunks": list(obj.chunks) if obj.chunks else None,
                        "compression": obj.compression,
                        "compression_opts": obj.compression_opts,
                    }
    except Exception:  # noqa: BLE001 — arquivo pode não ser HDF5 acessível
        pass

    # ── sugestão de chunking (alvo ~64 MB por chunk) ──
    if "time" in info["dims"] and "frequency" in info["dims"]:
        info["recommended_chunks"] = _recommend_chunks(
            {"time": info["dims"]["time"], "frequency": info["dims"]["frequency"]}
        )

    if print_report:
        _print_chunk_report(info)
    return info


def _print_chunk_report(info: dict) -> None:
    """Imprime o relatório formatado de ``analyze_chunks``."""
    line = "─" * 78
    print(f"📦 Chunk report | {info['path'].name}")
    print(line)
    print(f"  Arquivo  : {info['path']}  ({_format_bytes(info['size_bytes'])})")
    print(f"  Dims     : {info['dims']}")
    print("  Variáveis:")
    for v, m in info["variables"].items():
        print(
            f"    • {v:12s} {m['dtype']:>8s} {m['shape']!s:>24s} "
            f"{_format_bytes(m['uncompressed_mb'] * 1e6):>10s} (sem compressão)"
        )
    if info["h5_chunks"]:
        print("  Chunks no disco (HDF5):")
        for v, c in info["h5_chunks"].items():
            comp = c.get("compression") or "none"
            print(f"    • {v:12s} {c['chunks']!s:>24s}  gzip={comp}")
    print(f"  Chunks sugeridos (xarray): {info['recommended_chunks']}")
    print(line)
