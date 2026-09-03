from __future__ import annotations

import argparse
import sys
import traceback
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO, cast

from radioskysims_skymap.application.skymap.analyze import (
    AnalyzeSkyMapUseCase,
)
from radioskysims_skymap.application.skymap.generate import (
    ContinuumSurveyMapUseCase,
    GenerateSkyMapUseCase,
)
from radioskysims_skymap.domain.skymap.exceptions import (
    AnalysisError,
    InvalidDatasetError,
    InvalidNSideError,
)

from radioskysims.interfaces.cli.commands.analyze_skymap import (
    SkyMapReader,
    execute_analyze_command,
)
from radioskysims.interfaces.cli.commands.export_tod import (
    execute_export_tod_command,
    launch_background_export,
)
from radioskysims.interfaces.cli.commands.fetch_survey import (
    execute_survey_command,
)
from radioskysims.interfaces.cli.commands.generate_skymap import (
    execute_generate_command,
)
from radioskysims.interfaces.cli.commands.jobs_cmd import (
    execute_jobs_cancel,
    execute_jobs_list,
    execute_jobs_monitor,
    execute_jobs_status,
)
from radioskysims.interfaces.cli.formatters import (
    OutputFormat,
)

SUPPORTED_COMPONENTS = (
    "cmb",
    "synchrotron",
    "dust",
    "freefree",
    "ame",
)

SurveyUseCaseFactory = Callable[
    [Path],
    ContinuumSurveyMapUseCase,
]


@dataclass(frozen=True, slots=True)
class SkyMapCLIUseCases:
    """Dependências injetadas na CLI de SkyMap."""

    generate_skymap: GenerateSkyMapUseCase
    continuum_survey_factory: SurveyUseCaseFactory | None = None
    analyze_skymap: AnalyzeSkyMapUseCase | None = None
    skymap_reader: SkyMapReader | None = None


def build_parser() -> argparse.ArgumentParser:
    """Constrói o parser principal da CLI."""

    parser = argparse.ArgumentParser(
        prog="radioskysims",
        description="Interface de linha de comando do RadioSkySim.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Exibe traceback completo em caso de falha.",
    )

    contexts = parser.add_subparsers(
        dest="context",
        required=True,
    )

    # --------------------------------------------------------------
    # gui
    # --------------------------------------------------------------

    contexts.add_parser(
        "gui",
        help="Abre a interface gráfica (Panel) do RadioSkySim.",
        description=(
            "Abre a interface gráfica do RadioSkySim (dashboard SkyMap) no "
            "navegador, usando o composition root do umbrella."
        ),
    )

    skymap_parser = contexts.add_parser(
        "skymap",
        help="Operações relacionadas a mapas do céu.",
    )

    skymap_commands = skymap_parser.add_subparsers(
        dest="skymap_command",
        required=True,
    )

    # --------------------------------------------------------------
    # generate
    # --------------------------------------------------------------

    generate_parser = skymap_commands.add_parser(
        "generate",
        help="Gera um mapa do céu sintético.",
    )

    generate_parser.add_argument(
        "--frequency-ghz",
        type=float,
        required=True,
        help="Frequência central em GHz (banda do mapa).",
    )

    generate_parser.add_argument(
        "--nside",
        type=int,
        required=True,
        help="Resolução HEALPix (nside) do mapa.",
    )

    generate_parser.add_argument(
        "--components",
        nargs="+",
        required=True,
        choices=SUPPORTED_COMPONENTS,
        help="Componentes de emissão (cmb, synchrotron, dust, freefree, ame).",
    )

    generate_parser.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
        help="Formato de saída: text (padrão) ou json.",
    )

    # --------------------------------------------------------------
    # survey
    # --------------------------------------------------------------

    survey_parser = skymap_commands.add_parser(
        "survey",
        help="Obtém um mapa contínuo de um survey.",
    )

    survey_parser.add_argument(
        "--survey-id",
        required=True,
        help="Identificador do survey contínuo (ex.: NVSS).",
    )

    survey_parser.add_argument(
        "--ra-deg",
        type=float,
        required=True,
        help="Centro do campo em ascensão reta (graus).",
    )

    survey_parser.add_argument(
        "--dec-deg",
        type=float,
        required=True,
        help="Centro do campo em declinação (graus).",
    )

    survey_parser.add_argument(
        "--fov-deg",
        type=float,
        required=True,
        help="Campo de visão do recorte (graus).",
    )

    survey_parser.add_argument(
        "--nside",
        type=int,
        required=True,
        help="Resolução HEALPix (nside) do mapa.",
    )

    survey_parser.add_argument(
        "--frequency-ghz",
        type=float,
        default=None,
        help="Frequência central em GHz (omitir = banda completa do survey).",
    )

    survey_parser.add_argument(
        "--field",
        choices=("I", "Q", "U"),
        default="I",
        help="Componente de polarização (I, Q ou U).",
    )

    survey_parser.add_argument(
        "--base-path",
        type=Path,
        required=True,
        help="Diretório base para leitura/cache do survey.",
    )

    survey_parser.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
        help="Formato de saída: text (padrão) ou json.",
    )

    # --------------------------------------------------------------
    # analyze
    # --------------------------------------------------------------

    analyze_parser = skymap_commands.add_parser(
        "analyze",
        help="Calcula o espectro angular de um mapa HEALPix.",
    )

    analyze_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Arquivo FITS HEALPix de entrada.",
    )

    analyze_parser.add_argument(
        "--lmax",
        type=int,
        default=None,
        help="Multipolo máximo.",
    )

    analyze_parser.add_argument(
        "--unit",
        default="unknown",
        help="Unidade física associada ao mapa.",
    )

    analyze_parser.add_argument(
        "--frame",
        choices=(
            "galactic",
            "equatorial",
            "ecliptic",
        ),
        default="galactic",
    )

    analyze_parser.add_argument(
        "--field",
        choices=("I", "Q", "U"),
        default="I",
    )

    analyze_parser.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
    )

    # --------------------------------------------------------------
    # tod
    # --------------------------------------------------------------

    tod_parser = contexts.add_parser(
        "tod",
        help="Operações de simulação TOD.",
    )

    tod_commands = tod_parser.add_subparsers(
        dest="tod_command",
        required=True,
    )

    export_parser = tod_commands.add_parser(
        "export",
        help="Roda uma simulação TOD curta e grava o dataset.",
        epilog=(
            "Pré-requisitos de 1º uso: (1) settings.toml na raiz com o perfil do "
            "radiotelescópio usado por --telescope (ex.: [radiotelescopes.default] "
            "em settings.toml) e a seção [simulations] time_range; (2) PostgreSQL "
            "no ar apenas para --source db/consultas de catálogo; (3) "
            "credentials.env (ST_USER/ST_PWD) apenas para downloads do SpaceTrack."
        ),
    )

    export_parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Arquivo de settings completo (ex.: settings.toml).",
    )

    export_parser.add_argument(
        "--telescope",
        default="default",
        help="Perfil de radiotelescópio no settings.",
    )

    export_parser.add_argument(
        "--constellations",
        nargs="*",
        default=None,
        help="Constelações GNSS (ex.: GPS GALILEO). Se omitido, sem satélites.",
    )

    export_parser.add_argument(
        "--local-sources",
        action="store_true",
        default=False,
        help="Inclui fontes locais (Sol).",
    )

    export_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Caminho do dataset de saída (default: data/TOD/tod_<ts>.nc).",
    )

    export_parser.add_argument(
        "--use-processor",
        action="store_true",
        default=False,
        help="Usa ResourceAwareProcessor (batches com controle de memória).",
    )

    export_parser.add_argument(
        "--background",
        action="store_true",
        default=False,
        help="Executa em background (cria job + subprocesso worker).",
    )

    export_parser.add_argument(
        "--jobs-db",
        default=None,
        help="URL do banco de jobs (default: sqlite:///data/jobs.db).",
    )

    jobs_parser = tod_commands.add_parser(
        "jobs",
        help="Gerenciamento de jobs (list/status/cancel).",
    )

    jobs_commands = jobs_parser.add_subparsers(
        dest="jobs_command",
        required=True,
    )

    jobs_list_parser = jobs_commands.add_parser(
        "list",
        help="Lista os jobs (mais recentes primeiro).",
    )
    jobs_list_parser.add_argument(
        "--jobs-db",
        default=None,
        help="URL do banco de jobs.",
    )

    jobs_status_parser = jobs_commands.add_parser(
        "status",
        help="Exibe o detalhe de um job.",
    )
    jobs_status_parser.add_argument(
        "job_id",
        type=int,
        help="ID do job.",
    )
    jobs_status_parser.add_argument(
        "--jobs-db",
        default=None,
        help="URL do banco de jobs.",
    )

    jobs_cancel_parser = jobs_commands.add_parser(
        "cancel",
        help="Cancela um job em PENDING/RUNNING (SIGTERM ao worker).",
    )
    jobs_cancel_parser.add_argument(
        "job_id",
        type=int,
        help="ID do job.",
    )
    jobs_cancel_parser.add_argument(
        "--jobs-db",
        default=None,
        help="URL do banco de jobs.",
    )

    jobs_monitor_parser = jobs_commands.add_parser(
        "monitor",
        help="Exibe/monitora o progresso de um job (barra + ETA).",
    )
    jobs_monitor_parser.add_argument(
        "job_id",
        type=int,
        help="ID do job.",
    )
    jobs_monitor_parser.add_argument(
        "--jobs-db",
        default=None,
        help="URL do banco de jobs.",
    )
    jobs_monitor_parser.add_argument(
        "--watch",
        action="store_true",
        help="Segue o progresso até o job concluir.",
    )
    jobs_monitor_parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Intervalo de polling (s) com --watch.",
    )

    return parser


def run(
    argv: Sequence[str] | None = None,
    *,
    use_cases: SkyMapCLIUseCases,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Executa a CLI com dependências injetadas."""

    output_stream = stdout or sys.stdout
    error_stream = stderr or sys.stderr

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.context == "gui":
            from radioskysims.interfaces.cli.commands.gui_cmd import (
                execute_gui_command,
            )

            return execute_gui_command()

        if args.context == "skymap" and args.skymap_command == "generate":
            result = execute_generate_command(
                use_case=use_cases.generate_skymap,
                frequency_ghz=args.frequency_ghz,
                nside=args.nside,
                components=args.components,
                output_format=cast(
                    OutputFormat,
                    args.output_format,
                ),
            )

            print(result, file=output_stream)
            return 0

        if args.context == "skymap" and args.skymap_command == "survey":
            if use_cases.continuum_survey_factory is None:
                msg = "ContinuumSurveyMapUseCase não foi configurado."
                raise RuntimeError(msg)

            survey_use_case = use_cases.continuum_survey_factory(args.base_path)

            result = execute_survey_command(
                use_case=survey_use_case,
                survey_id=args.survey_id,
                ra_deg=args.ra_deg,
                dec_deg=args.dec_deg,
                fov_deg=args.fov_deg,
                nside=args.nside,
                frequency_ghz=args.frequency_ghz,
                field=args.field,
                output_format=cast(
                    OutputFormat,
                    args.output_format,
                ),
            )

            print(result, file=output_stream)
            return 0

        if args.context == "skymap" and args.skymap_command == "analyze":
            if use_cases.analyze_skymap is None:
                msg = "AnalyzeSkyMapUseCase não foi configurado."
                raise RuntimeError(msg)

            if use_cases.skymap_reader is None:
                msg = "Leitor de SkyMap não foi configurado."
                raise RuntimeError(msg)

            result = execute_analyze_command(
                use_case=use_cases.analyze_skymap,
                reader=use_cases.skymap_reader,
                input_path=args.input,
                lmax=args.lmax,
                unit=args.unit,
                frame=args.frame,
                field=args.field,
                output_format=cast(
                    OutputFormat,
                    args.output_format,
                ),
            )

            print(result, file=output_stream)
            return 0

        if args.context == "tod" and args.tod_command == "export":
            if args.background:
                job_id = launch_background_export(
                    config_path=args.config,
                    telescope=args.telescope,
                    constellations=args.constellations,
                    include_local_sources=args.local_sources,
                    use_processor=args.use_processor,
                    output=args.output,
                    jobs_db=args.jobs_db,
                    stderr=error_stream,
                )
                print(
                    f"Job {job_id} criado. Use 'radioskysims tod jobs status "
                    f"{job_id}' para acompanhar.",
                    file=output_stream,
                )
                return 0

            result = execute_export_tod_command(
                config_path=args.config,
                telescope=args.telescope,
                constellations=args.constellations,
                include_local_sources=args.local_sources,
                use_processor=args.use_processor,
                output=args.output,
                stderr=error_stream,
            )

            print(result, file=output_stream)
            return 0

        if args.context == "tod" and args.tod_command == "jobs":
            if args.jobs_command == "list":
                result = execute_jobs_list(jobs_db=args.jobs_db)
            elif args.jobs_command == "status":
                result = execute_jobs_status(
                    args.job_id,
                    jobs_db=args.jobs_db,
                )
            elif args.jobs_command == "cancel":
                result = execute_jobs_cancel(
                    args.job_id,
                    jobs_db=args.jobs_db,
                )
            elif args.jobs_command == "monitor":
                return execute_jobs_monitor(
                    args.job_id,
                    jobs_db=args.jobs_db,
                    watch=args.watch,
                    interval=args.interval,
                    stdout=output_stream,
                )
            else:
                parser.error("Comando de jobs não reconhecido.")

            print(result, file=output_stream)
            return 0

        parser.error("Comando não reconhecido.")

    except (
        TypeError,
        ValueError,
        InvalidNSideError,
        InvalidDatasetError,
    ) as exc:
        print(
            f"Erro de entrada: {exc}",
            file=error_stream,
        )

        if args.debug:
            traceback.print_exc(file=error_stream)

        return 2

    except FileNotFoundError as exc:
        print(
            f"Arquivo não encontrado: {exc}",
            file=error_stream,
        )

        if args.debug:
            traceback.print_exc(file=error_stream)

        return 3

    except ImportError as exc:
        print(
            f"Dependência indisponível: {exc}",
            file=error_stream,
        )

        if args.debug:
            traceback.print_exc(file=error_stream)

        return 4

    except AnalysisError as exc:
        print(
            f"Falha de análise: {exc}",
            file=error_stream,
        )

        if args.debug:
            traceback.print_exc(file=error_stream)

        return 5

    except Exception as exc:
        print(
            f"Erro inesperado: {type(exc).__name__}: {exc}",
            file=error_stream,
        )

        if args.debug:
            traceback.print_exc(file=error_stream)

        return 1

    return 1
