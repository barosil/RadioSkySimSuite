"""src/radioskysims/interfaces/gui/skymap/widgets.py
Widgets da GUI SkyMap.
Copyright BINGO Collaboration
Last modified: 2026-07-23
"""

from __future__ import annotations

from dataclasses import dataclass

import panel as pn


@dataclass(slots=True)
class GenerateWidgets:
    frequency_ghz: pn.widgets.FloatInput
    nside: pn.widgets.IntInput
    components: pn.widgets.MultiChoice
    unit: pn.widgets.Select
    frame: pn.widgets.Select
    field: pn.widgets.Select
    generate: pn.widgets.Button
    reset: pn.widgets.Button


@dataclass(slots=True)
class SurveyWidgets:
    survey_id: pn.widgets.TextInput
    ra_deg: pn.widgets.FloatInput
    dec_deg: pn.widgets.FloatInput
    fov_deg: pn.widgets.FloatInput
    nside: pn.widgets.IntInput
    frequency_ghz: pn.widgets.FloatInput
    unit: pn.widgets.Select
    frame: pn.widgets.Select
    field: pn.widgets.Select
    base_path: pn.widgets.TextInput
    load_survey: pn.widgets.Button
    reset: pn.widgets.Button


@dataclass(slots=True)
class AnalyzeWidgets:
    input_path: pn.widgets.TextInput
    lmax: pn.widgets.IntInput
    unit: pn.widgets.Select
    frame: pn.widgets.Select
    field: pn.widgets.Select
    analyze: pn.widgets.Button
    reset: pn.widgets.Button


def build_generate_widgets() -> GenerateWidgets:
    return GenerateWidgets(
        frequency_ghz=pn.widgets.FloatInput(name="Frequência (GHz)", value=1.4, step=0.1),
        nside=pn.widgets.IntInput(name="NSide", value=64, step=1, start=1),
        components=pn.widgets.MultiChoice(
            name="Componentes",
            options=["synchrotron", "freefree", "ame", "cmb", "dust"],
            value=["synchrotron"],
        ),
        unit=pn.widgets.Select(name="Unidade", options=["K_RJ", "K_CMB", "MJy/sr"], value="K_RJ"),
        frame=pn.widgets.Select(name="Frame", options=["galactic", "icrs"], value="galactic"),
        field=pn.widgets.Select(name="Stokes", options=["I", "Q", "U"], value="I"),
        generate=pn.widgets.Button(name="Generate", button_type="primary"),
        reset=pn.widgets.Button(name="Reset", button_type="warning"),
    )


def build_survey_widgets() -> SurveyWidgets:
    return SurveyWidgets(
        survey_id=pn.widgets.TextInput(name="Survey ID", value="NVSS"),
        ra_deg=pn.widgets.FloatInput(name="RA (deg)", value=180.0, step=0.1),
        dec_deg=pn.widgets.FloatInput(name="DEC (deg)", value=0.0, step=0.1),
        fov_deg=pn.widgets.FloatInput(name="FOV (deg)", value=2.0, step=0.1, start=0.0001),
        nside=pn.widgets.IntInput(name="NSide", value=64, step=1, start=1),
        frequency_ghz=pn.widgets.FloatInput(name="Frequência (GHz)", value=1.4, step=0.1, start=0.0001),
        unit=pn.widgets.Select(name="Unidade", options=["K_RJ", "K_CMB", "MJy/sr", "unknown"], value="K_RJ"),
        frame=pn.widgets.Select(name="Frame", options=["equatorial", "galactic", "ecliptic"], value="equatorial"),
        field=pn.widgets.Select(name="Stokes", options=["I", "Q", "U"], value="I"),
        base_path=pn.widgets.TextInput(name="Base Path", value="data/hips"),
        load_survey=pn.widgets.Button(name="Load Survey", button_type="primary"),
        reset=pn.widgets.Button(name="Reset", button_type="warning"),
    )


def build_analyze_widgets() -> AnalyzeWidgets:
    return AnalyzeWidgets(
        input_path=pn.widgets.TextInput(name="Input FITS", value=""),
        lmax=pn.widgets.IntInput(name="lmax", value=16, step=1, start=0),
        unit=pn.widgets.Select(name="Unidade", options=["uK_CMB", "K_RJ", "unknown"], value="uK_CMB"),
        frame=pn.widgets.Select(name="Frame", options=["galactic", "equatorial", "ecliptic"], value="galactic"),
        field=pn.widgets.Select(name="Stokes", options=["I", "Q", "U"], value="I"),
        analyze=pn.widgets.Button(name="Analyze", button_type="primary"),
        reset=pn.widgets.Button(name="Reset", button_type="warning"),
    )