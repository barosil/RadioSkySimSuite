# src/radioskysims/interfaces/cli/generate.py
from __future__ import annotations

import argparse

from radioskysims_skymap.application.skymap.dto import GenerateSkyMapInputDTO
from radioskysims_skymap.application.skymap.generate import GenerateSkyMapUseCase
from radioskysims_skymap.domain.skymap.value_objects import NSide
from radioskysims_skymap.infrastructure.skymap.providers.pysm import PySMSkyMapGeneratorAdapter


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a radio sky map using PySM3")

    parser.add_argument(
        "--freq",
        type=float,
        required=True,
        help="Frequency in GHz",
    )

    parser.add_argument(
        "--nside",
        type=int,
        required=True,
        help="HEALPix NSIDE",
    )

    parser.add_argument(
        "--components",
        nargs="+",
        required=True,
        help="Sky components (e.g. synchrotron dust freefree)",
    )

    args = parser.parse_args()

    # -------------------------
    # Wiring (Interface layer)
    # -------------------------
    generator = PySMSkyMapGeneratorAdapter(
        nside=NSide(args.nside),
        components=args.components,
    )

    use_case = GenerateSkyMapUseCase(generator=generator)

    input_dto = GenerateSkyMapInputDTO(
        frequency_ghz=args.freq,
        nside=args.nside,
        components=args.components,
    )

    output = use_case.execute(input_dto)

    print("SkyMap generated successfully")
    print(f"NSIDE: {output.nside}")
    print(f"NPIX : {output.npix}")
