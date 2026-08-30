"""src/radioskysims/interfaces/gui/skymap/presenters.py
Presenters puros para GUI SkyMap.
Copyright BINGO Collaboration
Last modified: 2026-07-23
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class OperationViewModel:
    """Representação genérica de uma operação da GUI."""

    operation: str
    metadata: dict[str, str]
    payload: Any | None = None


@dataclass(frozen=True, slots=True)
class GenerateViewModel:
    """Dados de um mapa gerado preparados para apresentação."""

    current_map: Any
    nside: int | None
    npix: int
    frequency_ghz: float | None
    unit: str | None
    frame: str | None
    field: str | None
    components: tuple[str, ...]
    metadata: dict[str, str]
    histogram: tuple[tuple[float, ...], tuple[float, ...]] | None
    map_preview: tuple[tuple[int, ...], tuple[float, ...]] | None
    payload: Any


@dataclass(frozen=True, slots=True)
class SurveyViewModel:
    """Dados de um mapa de survey preparados para apresentação."""

    current_map: Any
    survey_id: str | None
    survey_name: str | None
    nside: int | None
    npix: int
    frequency_ghz: float | None
    unit: str | None
    frame: str | None
    field: str | None
    ra_deg: float | None
    dec_deg: float | None
    fov_deg: float | None
    source_path: str | None
    valid_pixels: int
    invalid_pixels: int
    valid_fraction: float | None
    metadata: dict[str, str]
    histogram: tuple[tuple[float, ...], tuple[float, ...]] | None
    map_preview: tuple[tuple[int, ...], tuple[float, ...]] | None
    payload: Any


@dataclass(frozen=True, slots=True)
class AnalyzeViewModel:
    """Dados de uma análise de mapa preparados para apresentação."""

    current_map: Any
    input_path: str | None
    nside: int | None
    npix: int
    dtype: str | None
    unit: str | None
    frame: str | None
    field: str | None
    lmax: int | None
    cls_length: int
    pixel_mean: float | None
    pixel_rms: float | None
    pixel_min: float | None
    pixel_max: float | None
    cls_min: float | None
    cls_max: float | None
    cls_mean: float | None
    metadata: dict[str, str]
    histogram: tuple[tuple[float, ...], tuple[float, ...]] | None
    map_preview: tuple[tuple[int, ...], tuple[float, ...]] | None
    spectrum: tuple[tuple[int, float], ...]
    cls_table: tuple[dict[str, int | float], ...]
    payload: Any


def normalize_error(exc: Exception) -> str:
    """Transforma uma exceção em mensagem segura para o usuário."""

    raw_message = str(exc).strip()

    if raw_message:
        return raw_message

    return f"Erro inesperado: {exc.__class__.__name__}"


def _read(
    source: Any,
    name: str,
    default: Any = None,
) -> Any:
    """Obtém um valor de mapping ou atributo sem acoplamento ao DTO."""

    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(name, default)

    return getattr(source, name, default)


def _first_available(
    sources: Sequence[Any],
    names: Sequence[str],
    default: Any = None,
) -> Any:
    """Retorna o primeiro valor disponível entre fontes e nomes."""

    for source in sources:
        for name in names:
            value = _read(source, name)

            if value is not None:
                return value

    return default


def _unwrap_value(value: Any) -> Any:
    """Desempacota value objects simples, como NSide."""

    return getattr(value, "value", value)


def _to_int(value: Any) -> int | None:
    if value is None:
        return None

    value = _unwrap_value(value)

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None

    value = _unwrap_value(value)

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_optional_string(value: Any) -> str | None:
    if value is None:
        return None

    return str(_unwrap_value(value))


def _flatten_values(value: Any) -> tuple[float, ...]:
    """Converte dados numéricos em uma tupla plana sem importar NumPy."""

    if value is None:
        return ()

    if hasattr(value, "compute") and callable(value.compute):
        value = value.compute()

    for attribute in ("values", "data"):
        nested = getattr(value, attribute, None)

        if nested is not None and nested is not value:
            value = nested
            break

    if hasattr(value, "reshape") and hasattr(value, "tolist"):
        try:
            value = value.reshape(-1).tolist()
        except (TypeError, ValueError):
            value = value.tolist()
    elif hasattr(value, "tolist"):
        value = value.tolist()

    flattened: list[float] = []

    def visit(item: Any) -> None:
        if isinstance(item, Sequence) and not isinstance(
            item,
            (str, bytes, bytearray),
        ):
            for child in item:
                visit(child)
            return

        try:
            flattened.append(float(item))
        except (TypeError, ValueError):
            return

    visit(value)

    return tuple(flattened)


def _extract_map_object(result: Any) -> Any:
    """Obtém o objeto de mapa encapsulado no DTO de saída."""

    return _first_available(
        (result,),
        (
            "skymap",
            "sky_map",
            "current_map",
            "map",
        ),
        default=result,
    )


def _extract_map_values(
    result: Any,
    current_map: Any,
) -> tuple[float, ...]:
    """Extrai dados de pixels para preview e histograma."""

    value = _first_available(
        (result, current_map),
        (
            "map_data",
            "data",
            "values",
            "dataset",
        ),
    )

    return _flatten_values(value)


def _extract_components(
    result: Any,
    current_map: Any,
) -> tuple[str, ...]:
    value = _first_available(
        (result, current_map),
        ("components",),
        default=(),
    )

    if value is None:
        return ()

    if isinstance(value, str):
        return (value,)

    try:
        return tuple(str(component) for component in value)
    except TypeError:
        return (str(value),)


def _build_histogram(
    values: tuple[float, ...],
) -> tuple[tuple[float, ...], tuple[float, ...]] | None:
    """Prepara pares (counts, bins) para a camada de visualização."""

    finite_values = tuple(value for value in values if math.isfinite(value))

    if not finite_values:
        return None

    vmin = min(finite_values)
    vmax = max(finite_values)

    if vmin == vmax:
        return (float(len(finite_values)),), (vmin - 0.5, vmax + 0.5)

    nbins = min(64, max(8, int(len(finite_values) ** 0.5)))
    bin_width = (vmax - vmin) / nbins

    bins = [vmin + idx * bin_width for idx in range(nbins + 1)]
    bins[-1] = vmax

    counts = [0.0] * nbins

    for value in finite_values:
        raw_index = int((value - vmin) / bin_width)
        bin_index = min(max(raw_index, 0), nbins - 1)
        counts[bin_index] += 1.0

    return tuple(counts), tuple(bins)


def _build_map_preview(
    values: tuple[float, ...],
    *,
    max_points: int = 2048,
) -> tuple[tuple[int, ...], tuple[float, ...]] | None:
    """Prepara dados de preview como pares (pixel_index, pixel_value)."""

    finite_values = tuple(value for value in values if math.isfinite(value))

    if not finite_values:
        return None

    preview_values = finite_values[:max_points]
    pixel_index = tuple(range(len(preview_values)))

    return pixel_index, preview_values


def present_survey(result: Any) -> SurveyViewModel:
    """Converte a saída do caso de uso Survey em ViewModel."""

    if result is None:
        msg = "A saída do caso de uso Survey não pode ser None."
        raise ValueError(msg)

    current_map = _extract_map_object(result)
    sources = (result, current_map)

    values = _extract_map_values(
        result,
        current_map,
    )

    finite_values = tuple(value for value in values if math.isfinite(value))

    nside = _to_int(
        _first_available(
            sources,
            ("nside", "nside_value"),
        )
    )

    explicit_npix = _to_int(
        _first_available(
            sources,
            ("npix",),
        )
    )

    npix = explicit_npix if explicit_npix is not None else len(values)

    survey_id = _to_optional_string(
        _first_available(
            sources,
            ("survey_id", "survey_name"),
        )
    )

    survey_name = _to_optional_string(
        _first_available(
            sources,
            ("survey_name", "survey_id"),
        )
    )

    frequency_ghz = _to_float(
        _first_available(
            sources,
            ("frequency_ghz", "freq_ghz"),
        )
    )

    unit = _to_optional_string(
        _first_available(
            sources,
            ("unit",),
        )
    )

    frame = _to_optional_string(
        _first_available(
            sources,
            ("frame",),
        )
    )

    field = _to_optional_string(
        _first_available(
            sources,
            ("field", "stokes"),
        )
    )

    ra_deg = _to_float(
        _first_available(
            sources,
            ("ra_deg",),
        )
    )

    dec_deg = _to_float(
        _first_available(
            sources,
            ("dec_deg",),
        )
    )

    fov_deg = _to_float(
        _first_available(
            sources,
            ("fov_deg",),
        )
    )

    source_path = _to_optional_string(
        _first_available(
            sources,
            ("source_path", "base_path", "fits_path", "path"),
        )
    )

    valid_pixels = len(finite_values)
    invalid_pixels = max(npix - valid_pixels, 0)
    valid_fraction = float(valid_pixels / npix) if npix > 0 else None

    metadata: dict[str, str] = {
        "npix": str(npix),
        "valid_pixels": str(valid_pixels),
        "invalid_pixels": str(invalid_pixels),
    }

    if survey_id is not None:
        metadata["survey_id"] = survey_id

    if survey_name is not None:
        metadata["survey_name"] = survey_name

    if nside is not None:
        metadata["nside"] = str(nside)

    if frequency_ghz is not None:
        metadata["frequency_ghz"] = str(frequency_ghz)

    if unit is not None:
        metadata["unit"] = unit

    if frame is not None:
        metadata["frame"] = frame

    if field is not None:
        metadata["field"] = field

    if ra_deg is not None:
        metadata["ra_deg"] = str(ra_deg)

    if dec_deg is not None:
        metadata["dec_deg"] = str(dec_deg)

    if fov_deg is not None:
        metadata["fov_deg"] = str(fov_deg)

    if source_path is not None:
        metadata["source_path"] = source_path

    if valid_fraction is not None:
        metadata["valid_fraction"] = f"{valid_fraction:.6f}"

    histogram = _build_histogram(values)
    map_preview = _build_map_preview(values)

    return SurveyViewModel(
        current_map=current_map,
        survey_id=survey_id,
        survey_name=survey_name,
        nside=nside,
        npix=npix,
        frequency_ghz=frequency_ghz,
        unit=unit,
        frame=frame,
        field=field,
        ra_deg=ra_deg,
        dec_deg=dec_deg,
        fov_deg=fov_deg,
        source_path=source_path,
        valid_pixels=valid_pixels,
        invalid_pixels=invalid_pixels,
        valid_fraction=valid_fraction,
        metadata=metadata,
        histogram=histogram,
        map_preview=map_preview,
        payload=result,
    )


def present_analyze(result: Any) -> AnalyzeViewModel:
    """Converte a saída do caso de uso Analyze em ViewModel."""

    if result is None:
        msg = "A saída do caso de uso Analyze não pode ser None."
        raise ValueError(msg)

    analysis_output = _first_available(
        (result,),
        ("analysis_output", "analyze_output", "output", "result"),
        default=result,
    )

    current_map = _first_available(
        (result,),
        ("sky_map", "skymap", "current_map", "map"),
        default=None,
    )

    sources: tuple[Any, ...]
    if current_map is None:
        sources = (analysis_output, result)
    else:
        sources = (analysis_output, result, current_map)

    pixel_values = _extract_map_values(result, current_map)
    finite_pixels = tuple(value for value in pixel_values if math.isfinite(value))

    raw_cls = _first_available(
        sources,
        ("cls", "cl", "spectrum"),
    )
    cls_values = _flatten_values(raw_cls)
    finite_cls = tuple(value for value in cls_values if math.isfinite(value))

    spectrum = tuple(
        (index, value) for index, value in enumerate(cls_values) if math.isfinite(value)
    )

    cls_table = tuple({"ell": ell, "cl": cl} for ell, cl in spectrum[:25])

    nside = _to_int(
        _first_available(
            sources,
            ("nside", "nside_value"),
        )
    )

    explicit_npix = _to_int(
        _first_available(
            sources,
            ("npix",),
        )
    )
    npix = explicit_npix if explicit_npix is not None else len(pixel_values)

    input_path = _to_optional_string(
        _first_available(
            (result,),
            ("input_path", "path", "fits_path", "source_path"),
        )
    )

    lmax = _to_int(
        _first_available(
            sources,
            ("lmax",),
        )
    )

    unit = _to_optional_string(
        _first_available(
            sources,
            ("unit",),
        )
    )

    frame = _to_optional_string(
        _first_available(
            sources,
            ("frame",),
        )
    )

    field = _to_optional_string(
        _first_available(
            sources,
            ("field", "stokes"),
        )
    )

    pixel_mean = sum(finite_pixels) / len(finite_pixels) if finite_pixels else None
    pixel_rms = (
        math.sqrt(sum(value * value for value in finite_pixels) / len(finite_pixels))
        if finite_pixels
        else None
    )
    pixel_min = min(finite_pixels) if finite_pixels else None
    pixel_max = max(finite_pixels) if finite_pixels else None

    cls_min = min(finite_cls) if finite_cls else None
    cls_max = max(finite_cls) if finite_cls else None
    cls_mean = sum(finite_cls) / len(finite_cls) if finite_cls else None

    dtype_value = _first_available(
        sources,
        ("dtype",),
    )

    if dtype_value is None:
        if raw_cls is not None and hasattr(raw_cls, "dtype"):
            dtype_value = raw_cls.dtype
        elif current_map is not None:
            map_data = _first_available(
                (current_map,),
                ("data", "values"),
            )
            if hasattr(map_data, "dtype"):
                dtype_value = map_data.dtype

    dtype = str(dtype_value) if dtype_value is not None else None

    metadata: dict[str, str] = {
        "npix": str(npix),
        "cls_length": str(len(cls_values)),
    }

    if input_path is not None:
        metadata["input_path"] = input_path
    if nside is not None:
        metadata["nside"] = str(nside)
    if unit is not None:
        metadata["unit"] = unit
    if frame is not None:
        metadata["frame"] = frame
    if field is not None:
        metadata["field"] = field
    if lmax is not None:
        metadata["lmax"] = str(lmax)
    if dtype is not None:
        metadata["dtype"] = dtype
    if pixel_mean is not None:
        metadata["pixel_mean"] = f"{pixel_mean:.6g}"
    if pixel_rms is not None:
        metadata["pixel_rms"] = f"{pixel_rms:.6g}"
    if pixel_min is not None:
        metadata["pixel_min"] = f"{pixel_min:.6g}"
    if pixel_max is not None:
        metadata["pixel_max"] = f"{pixel_max:.6g}"
    if cls_min is not None:
        metadata["cls_min"] = f"{cls_min:.6g}"
    if cls_max is not None:
        metadata["cls_max"] = f"{cls_max:.6g}"
    if cls_mean is not None:
        metadata["cls_mean"] = f"{cls_mean:.6g}"

    return AnalyzeViewModel(
        current_map=current_map,
        input_path=input_path,
        nside=nside,
        npix=npix,
        dtype=dtype,
        unit=unit,
        frame=frame,
        field=field,
        lmax=lmax,
        cls_length=len(cls_values),
        pixel_mean=pixel_mean,
        pixel_rms=pixel_rms,
        pixel_min=pixel_min,
        pixel_max=pixel_max,
        cls_min=cls_min,
        cls_max=cls_max,
        cls_mean=cls_mean,
        metadata=metadata,
        histogram=_build_histogram(pixel_values),
        map_preview=_build_map_preview(pixel_values),
        spectrum=spectrum,
        cls_table=cls_table,
        payload=result,
    )


def present_generate(result: Any) -> GenerateViewModel:
    """Converte a saída do caso de uso Generate em ViewModel."""

    if result is None:
        msg = "A saída do caso de uso Generate não pode ser None."
        raise ValueError(msg)

    current_map = _extract_map_object(result)
    sources = (result, current_map)

    values = _extract_map_values(
        result,
        current_map,
    )

    nside = _to_int(
        _first_available(
            sources,
            ("nside",),
        )
    )

    explicit_npix = _to_int(
        _first_available(
            sources,
            ("npix",),
        )
    )

    npix = explicit_npix if explicit_npix is not None else len(values)

    frequency_ghz = _to_float(
        _first_available(
            sources,
            (
                "frequency_ghz",
                "freq_ghz",
            ),
        )
    )

    unit = _to_optional_string(
        _first_available(
            sources,
            ("unit",),
        )
    )

    frame = _to_optional_string(
        _first_available(
            sources,
            ("frame",),
        )
    )

    field = _to_optional_string(
        _first_available(
            sources,
            ("field", "stokes"),
        )
    )

    components = _extract_components(
        result,
        current_map,
    )

    metadata: dict[str, str] = {}

    if frequency_ghz is not None:
        metadata["frequency_ghz"] = str(frequency_ghz)

    if nside is not None:
        metadata["nside"] = str(nside)

    metadata["npix"] = str(npix)

    if unit is not None:
        metadata["unit"] = unit

    if frame is not None:
        metadata["frame"] = frame

    if field is not None:
        metadata["field"] = field

    if components:
        metadata["components"] = ", ".join(components)

    histogram = _build_histogram(values)

    # Limita somente a quantidade enviada para a camada visual.
    # O mapa científico original permanece intacto em current_map.
    map_preview = _build_map_preview(values)

    return GenerateViewModel(
        current_map=current_map,
        nside=nside,
        npix=npix,
        frequency_ghz=frequency_ghz,
        unit=unit,
        frame=frame,
        field=field,
        components=components,
        metadata=metadata,
        histogram=histogram,
        map_preview=map_preview,
        payload=result,
    )


def _to_dict(obj: Any) -> dict[str, Any]:
    """Converte DTOs simples para dicionário."""

    if obj is None:
        return {}

    if isinstance(obj, Mapping):
        return dict(obj)

    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    if hasattr(obj, "dict"):
        return obj.dict()

    data: dict[str, Any] = {}

    for name in dir(obj):
        if name.startswith("_"):
            continue

        try:
            value = getattr(obj, name)
        except Exception:  # noqa: BLE001
            continue

        if not callable(value):
            data[name] = value

    return data


def _extract_metadata(result: Any) -> dict[str, str]:
    data = _to_dict(result)

    keys = (
        "frequency_ghz",
        "nside",
        "survey_name",
        "fits_path",
        "lmax",
        "stokes",
        "output_path",
        "map_name",
    )

    metadata: dict[str, str] = {}

    for key in keys:
        value = data.get(key)

        if value is not None:
            metadata[key] = str(value)

    return metadata


def present_generate_result(
    result: Any,
) -> OperationViewModel:
    """Compatibilidade com a API genérica anterior."""

    return OperationViewModel(
        operation="generate",
        metadata=_extract_metadata(result),
        payload=result,
    )


def present_survey_result(
    result: Any,
) -> OperationViewModel:
    return OperationViewModel(
        operation="survey",
        metadata=_extract_metadata(result),
        payload=result,
    )


def present_analyze_result(
    result: Any,
) -> OperationViewModel:
    return OperationViewModel(
        operation="analyze",
        metadata=_extract_metadata(result),
        payload=result,
    )
