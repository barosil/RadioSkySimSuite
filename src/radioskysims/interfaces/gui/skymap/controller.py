"""src/radioskysims/interfaces/gui/skymap/controller.py
Controller da GUI SkyMap.
Copyright BINGO Collaboration
Last modified: 2026-07-23
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from inspect import signature

from radioskysims_skymap.application.skymap.dto import (
    AnalyzeSkyMapInputDTO,
    GenerateSkyMapInputDTO,
)

from .presenters import (
    AnalyzeViewModel,
    GenerateViewModel,
    SurveyViewModel,
    normalize_error,
    present_analyze,
    present_generate,
    present_survey,
)
from .state import SkyMapGuiState

logger = logging.getLogger(__name__)


class SkyMapGUIController:
    """Controller da GUI SkyMap."""

    def __init__(
        self,
        state: SkyMapGuiState,
        *,
        generate_use_case: Any | None = None,
        survey_use_case: Any | None = None,
        analyze_use_case: Any | None = None,
        skymap_reader: Any | None = None,
    ) -> None:
        self._state = state
        self._generate_use_case = generate_use_case
        self._survey_use_case = survey_use_case
        self._analyze_use_case = analyze_use_case
        self._skymap_reader = skymap_reader

    @staticmethod
    def _build_generate_dto(
        *,
        frequency_ghz: float,
        nside: int,
        components: list[str],
        unit: str,
        frame: str,
        field: str,
    ) -> GenerateSkyMapInputDTO:
        """Constrói o DTO usando somente os campos do contrato real."""

        payload = {
            "frequency_ghz": frequency_ghz,
            "nside": nside,
            "components": components,
            "unit": unit,
            "frame": frame,
            "field": field,
        }

        model_fields = getattr(
            GenerateSkyMapInputDTO,
            "model_fields",
            None,
        )

        if model_fields is not None:
            valid_fields = set(model_fields)
            filtered_payload = {
                key: value
                for key, value in payload.items()
                if key in valid_fields
            }

            return GenerateSkyMapInputDTO.model_validate(
                filtered_payload
            )

        valid_parameters = set(
            signature(
                GenerateSkyMapInputDTO
            ).parameters
        )

        filtered_payload = {
            key: value
            for key, value in payload.items()
            if key in valid_parameters
        }

        return GenerateSkyMapInputDTO(
            **filtered_payload
        )
    @staticmethod
    def _invoke_use_case(use_case: Any, dto: GenerateSkyMapInputDTO) -> Any:
        if hasattr(use_case, "execute") and callable(use_case.execute):
            return use_case.execute(dto)
        if callable(use_case):
            return use_case(dto)
        msg = "GenerateSkyMapUseCase inválido para execução."
        raise TypeError(msg)

    def generate(
        self,
        *,
        frequency_ghz: float,
        nside: int,
        components: list[str],
        unit: str,
        frame: str,
        field: str,
    ) -> GenerateViewModel | None:
        """Executa fluxo Generate via use case da Application."""
        form = {
            "frequency_ghz": frequency_ghz,
            "nside": nside,
            "components": components,
            "unit": unit,
            "frame": frame,
            "field": field,
        }

        self._state.begin_processing(form)
        try:
            if self._generate_use_case is None:
                msg = "Caso de uso GenerateSkyMapUseCase não configurado."
                raise RuntimeError(msg)
            if frequency_ghz <= 0:
                msg = "frequency_ghz deve ser maior que zero."
                raise ValueError(msg)
            if nside <= 0:
                msg = "nside deve ser maior que zero."
                raise ValueError(msg)
            if not components:
                msg = "Selecione ao menos um componente."
                raise ValueError(msg)

            dto = self._build_generate_dto(
                frequency_ghz=frequency_ghz,
                nside=nside,
                components=components,
                unit=unit,
                frame=frame,
                field=field,
            )
            output = self._invoke_use_case(self._generate_use_case, dto)
            vm = present_generate(output)

            self._state.current_map = vm.current_map
            self._state.map_origin = "generated"
            self._state.input_params = form
            self._state.add_success("Mapa gerado com sucesso.")
            return vm

        except (ValueError, TypeError) as exc:
            self._state.add_error(normalize_error(exc))
            return None
        except Exception:  # noqa: BLE001
            logger.exception("Erro inesperado no fluxo Generate.")
            self._state.add_error("Falha inesperada ao gerar mapa. Verifique os logs.")
            return None
        finally:
            self._state.finish_processing()

    @staticmethod
    def _resolve_survey_use_case(
        survey_dependency: Any,
        *,
        base_path: str,
    ) -> Any:
        if hasattr(survey_dependency, "execute") and callable(survey_dependency.execute):
            return survey_dependency

        if callable(survey_dependency):
            return survey_dependency(Path(base_path))

        msg = "ContinuumSurveyMapUseCase inválido para execução."
        raise TypeError(msg)

    def survey(
        self,
        *,
        survey_id: str,
        ra_deg: float,
        dec_deg: float,
        fov_deg: float,
        nside: int,
        frequency_ghz: float,
        unit: str,
        frame: str,
        field: str,
        base_path: str,
    ) -> SurveyViewModel | None:
        """Executa fluxo Survey via caso de uso da Application."""

        form = {
            "survey_id": survey_id,
            "ra_deg": ra_deg,
            "dec_deg": dec_deg,
            "fov_deg": fov_deg,
            "nside": nside,
            "frequency_ghz": frequency_ghz,
            "unit": unit,
            "frame": frame,
            "field": field,
            "base_path": base_path,
        }

        self._state.begin_processing(form)
        try:
            if self._survey_use_case is None:
                msg = "Caso de uso ContinuumSurveyMapUseCase não configurado."
                raise RuntimeError(msg)

            if not survey_id or not survey_id.strip():
                msg = "survey_id não pode ser vazio."
                raise ValueError(msg)
            if fov_deg <= 0:
                msg = "fov_deg deve ser maior que zero."
                raise ValueError(msg)
            if nside <= 0:
                msg = "nside deve ser maior que zero."
                raise ValueError(msg)
            if frequency_ghz <= 0:
                msg = "frequency_ghz deve ser maior que zero."
                raise ValueError(msg)

            try:
                _ = float(ra_deg)
                _ = float(dec_deg)
            except (TypeError, ValueError) as exc:
                msg = "RA e Dec devem ser numéricos."
                raise TypeError(msg) from exc

            if callable(self._survey_use_case):
                if not base_path or not base_path.strip():
                    msg = "base_path é obrigatório."
                    raise ValueError(msg)

            survey_use_case = self._resolve_survey_use_case(
                self._survey_use_case,
                base_path=base_path,
            )

            output = survey_use_case.execute(
                survey_id=survey_id,
                ra_deg=ra_deg,
                dec_deg=dec_deg,
                fov_deg=fov_deg,
                nside=nside,
                freq_ghz=frequency_ghz,
                field=field,
            )

            presenter_payload: dict[str, Any] = {
                "survey_id": survey_id,
                "ra_deg": ra_deg,
                "dec_deg": dec_deg,
                "fov_deg": fov_deg,
                "frequency_ghz": frequency_ghz,
                "unit": unit,
                "frame": frame,
                "field": field,
                "source_path": base_path,
            }

            if isinstance(output, Mapping):
                presenter_payload.update(output)
                presenter_payload.setdefault("skymap", output)
            else:
                presenter_payload["skymap"] = output

            vm = present_survey(presenter_payload)

            self._state.current_map = vm.current_map
            self._state.map_origin = "survey"
            self._state.input_params = form
            self._state.add_success("Mapa de survey carregado com sucesso.")

            return vm

        except (ValueError, TypeError, FileNotFoundError) as exc:
            self._state.add_error(normalize_error(exc))
            return None
        except Exception:
            logger.exception("Erro inesperado no fluxo Survey.")
            self._state.add_error("Falha inesperada ao carregar survey. Verifique os logs.")
            return None
        finally:
            self._state.finish_processing()

    def analyze(
        self,
        *,
        input_path: str,
        lmax: int,
        unit: str,
        frame: str,
        field: str,
    ) -> AnalyzeViewModel | None:
        """Executa fluxo Analyze via leitura FITS e caso de uso da Application."""

        form = {
            "input_path": input_path,
            "lmax": lmax,
            "unit": unit,
            "frame": frame,
            "field": field,
        }

        self._state.begin_processing(form)

        try:
            if self._skymap_reader is None:
                msg = "Leitor SkyMap não configurado."
                raise RuntimeError(msg)
            if self._analyze_use_case is None:
                msg = "Caso de uso AnalyzeSkyMapUseCase não configurado."
                raise RuntimeError(msg)
            if not input_path or not input_path.strip():
                msg = "input_path não pode ser vazio."
                raise ValueError(msg)
            if lmax <= 0:
                msg = "lmax deve ser positivo."
                raise ValueError(msg)

            sky_map = self._skymap_reader.read_map(
                input_path,
                unit=unit,
                frame=frame,
                field=field,
            )

            dto = AnalyzeSkyMapInputDTO(
                sky_map=sky_map,
                lmax=lmax,
            )

            output = self._analyze_use_case.execute(dto)
            vm = present_analyze(
                {
                    "analysis_output": output,
                    "sky_map": sky_map,
                    "input_path": input_path,
                    "unit": unit,
                    "frame": frame,
                    "field": field,
                    "lmax": lmax,
                }
            )

            self._state.current_map = vm.current_map
            self._state.map_origin = "fits"
            self._state.analysis_result = output
            self._state.input_params = form
            self._state.add_success("Análise concluída com sucesso.")

            return vm

        except (ValueError, TypeError, FileNotFoundError) as exc:
            self._state.add_error(normalize_error(exc))
            return None
        except Exception:
            logger.exception("Erro inesperado no fluxo Analyze.")
            self._state.add_error("Falha inesperada ao analisar mapa. Verifique os logs.")
            return None
        finally:
            self._state.finish_processing()


# Alias para compatibilidade com código anterior
SkyMapGuiController = SkyMapGUIController