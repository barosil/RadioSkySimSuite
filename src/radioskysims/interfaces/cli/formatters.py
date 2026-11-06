from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Literal, TypeAlias, cast

from radioskysims_skymap.application.skymap.dto import (
    GenerateSkyMapOutputDTO,
)
from radioskysims_skymap.domain.skymap import SkyMap

from pathlib import Path

import numpy as np

from radioskysims_skymap.application.skymap.dto import (
    AnalyzeSkyMapOutputDTO,
)


OutputFormat: TypeAlias = Literal["text", "json"]


def format_generate_result(
    *,
    output: GenerateSkyMapOutputDTO,
    frequency_ghz: float,
    components: Sequence[str],
    output_format: OutputFormat,
) -> str:
    """Formata o resultado do comando ``skymap generate``."""

    payload: dict[str, object] = {
        "status": "success",
        "command": "skymap.generate",
        "nside": output.nside,
        "npix": output.npix,
        "frequency_ghz": frequency_ghz,
        "components": list(components),
        "dtype": str(output.map_data.dtype),
    }

    if output_format == "json":
        return json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )

    return "\n".join(
        [
            "SkyMap gerado com sucesso",
            f"NSide: {output.nside}",
            f"Número de pixels: {output.npix}",
            f"Frequência: {frequency_ghz} GHz",
            f"Componentes: {', '.join(components)}",
            f"Tipo dos dados: {output.map_data.dtype}",
        ]
    )


def format_survey_result(
    *,
    sky_map: SkyMap,
    survey_id: str,
    ra_deg: float,
    dec_deg: float,
    fov_deg: float,
    frequency_ghz: float | None,
    output_format: OutputFormat,
) -> str:
    """Formata o resultado do comando ``skymap survey``."""

    map_data = sky_map.data

    payload: dict[str, object] = {
        "status": "success",
        "command": "skymap.survey",
        "survey_id": survey_id,
        "ra_deg": ra_deg,
        "dec_deg": dec_deg,
        "fov_deg": fov_deg,
        "nside": sky_map.nside_value,
        "npix": sky_map.npix,
        "unit": sky_map.unit,
        "frame": sky_map.frame,
        "frequency_ghz": frequency_ghz,
        "field": sky_map.field,
        "dtype": str(map_data.dtype),
    }

    if output_format == "json":
        return json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )

    frequency_text = f"{frequency_ghz} GHz" if frequency_ghz is not None else "não informada"

    return "\n".join(
        [
            "Mapa de survey obtido com sucesso",
            f"Survey: {survey_id}",
            f"Centro: RA={ra_deg}°, DEC={dec_deg}°",
            f"Campo de visão: {fov_deg}°",
            f"NSide: {sky_map.nside_value}",
            f"Número de pixels: {sky_map.npix}",
            f"Unidade: {sky_map.unit}",
            f"Referencial: {sky_map.frame}",
            f"Frequência: {frequency_text}",
            f"Campo: {sky_map.field}",
            f"Tipo dos dados: {map_data.dtype}",
        ]
    )


def format_analyze_result(
    *,
    output: AnalyzeSkyMapOutputDTO,
    sky_map: SkyMap,
    input_path: Path,
    output_format: OutputFormat,
) -> str:
    """Formata o resultado do comando ``skymap analyze``."""

    cls = np.asarray(
        output.cls,
        dtype=np.float64,
    )

    finite_cls = cls[np.isfinite(cls)]

    cls_min = float(np.min(finite_cls)) if finite_cls.size else None

    cls_max = float(np.max(finite_cls)) if finite_cls.size else None

    cls_mean = float(np.mean(finite_cls)) if finite_cls.size else None

    effective_lmax = int(output.lmax) if output.lmax is not None else max(int(cls.size) - 1, 0)

    payload: dict[str, object] = {
        "status": "success",
        "command": "skymap.analyze",
        "input": str(input_path),
        "nside": output.nside,
        "npix": sky_map.npix,
        "unit": sky_map.unit,
        "frame": sky_map.frame,
        "field": sky_map.field,
        "lmax": effective_lmax,
        "cls_length": int(cls.size),
        "cls_min": cls_min,
        "cls_max": cls_max,
        "cls_mean": cls_mean,
        "dtype": str(cls.dtype),
    }

    if output_format == "json":
        return json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )

    return "\n".join(
        [
            "Análise espectral concluída",
            f"Arquivo: {input_path}",
            f"NSide: {output.nside}",
            f"Número de pixels: {sky_map.npix}",
            f"Unidade: {sky_map.unit}",
            f"Referencial: {sky_map.frame}",
            f"Campo: {sky_map.field}",
            f"lmax: {effective_lmax}",
            f"Quantidade de coeficientes Cℓ: {cls.size}",
            f"Cℓ mínimo: {cls_min}",
            f"Cℓ máximo: {cls_max}",
            f"Cℓ médio: {cls_mean}",
            f"Tipo dos dados: {cls.dtype}",
        ]
    )
