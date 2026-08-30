import pytest

from radioskysims.interfaces.gui.skymap.presenters import (
    normalize_error,
    present_analyze,
    present_generate,
    present_survey,
)


def test_present_generate_success() -> None:
    out = {
        "frequency_ghz": 1.4,
        "nside": 8,
        "unit": "K_RJ",
        "frame": "galactic",
        "field": "I",
        "components": ["synchrotron"],
        "map_data": [0.0, 1.0, 2.0, 3.0],
    }
    vm = present_generate(out)
    assert vm.nside == 8
    assert vm.npix == 4
    assert vm.histogram is not None
    assert vm.map_preview is not None
    counts, bins = vm.histogram
    pixel_index, pixel_value = vm.map_preview
    assert len(counts) > 0
    assert len(bins) == len(counts) + 1
    assert len(pixel_index) == len(pixel_value)
    assert vm.metadata["frequency_ghz"] == "1.4"


def test_normalize_error() -> None:
    assert normalize_error(ValueError("entrada inválida")) == "entrada inválida"


def test_present_survey_success_with_metadata_and_coverage() -> None:
    out = {
        "survey_id": "NVSS",
        "ra_deg": 180.0,
        "dec_deg": 0.0,
        "fov_deg": 2.0,
        "frequency_ghz": 1.4,
        "source_path": "data/hips",
        "skymap": {
            "nside": 8,
            "npix": 8,
            "unit": "K_RJ",
            "frame": "equatorial",
            "field": "I",
            "map_data": [0.0, 1.0, 2.0, 3.0, 4.0, float("nan"), float("inf"), -1.0],
        },
    }

    vm = present_survey(out)

    assert vm.survey_id == "NVSS"
    assert vm.nside == 8
    assert vm.npix == 8
    assert vm.valid_pixels == 6
    assert vm.invalid_pixels == 2
    assert vm.valid_fraction == pytest.approx(0.75)
    assert vm.metadata["source_path"] == "data/hips"
    assert vm.histogram is not None
    assert vm.map_preview is not None

    counts, bins = vm.histogram
    pixel_index, pixel_value = vm.map_preview
    assert len(counts) > 0
    assert len(bins) == len(counts) + 1
    assert len(pixel_index) == len(pixel_value)


def test_present_survey_handles_no_valid_pixels() -> None:
    out = {
        "survey_id": "NVSS",
        "skymap": {
            "nside": 8,
            "npix": 4,
            "unit": "K_RJ",
            "frame": "equatorial",
            "field": "I",
            "map_data": [float("nan"), float("inf"), float("nan"), float("inf")],
        },
    }

    vm = present_survey(out)

    assert vm.valid_pixels == 0
    assert vm.invalid_pixels == 4
    assert vm.valid_fraction == 0.0
    assert vm.histogram is None
    assert vm.map_preview is None


def test_present_survey_rejects_none_result() -> None:
    with pytest.raises(ValueError):
        present_survey(None)


def test_present_analyze_success() -> None:
    out = {
        "input_path": "data/map.fits",
        "unit": "uK_CMB",
        "frame": "galactic",
        "field": "I",
        "sky_map": {
            "nside": 8,
            "npix": 8,
            "map_data": [1.0, 2.0, 3.0, 4.0, 5.0, float("nan"), 7.0, 8.0],
        },
        "analysis_output": {
            "nside": 8,
            "lmax": 4,
            "cls": [1.0, 0.5, 0.25, 0.125, 0.0625],
        },
    }

    vm = present_analyze(out)

    assert vm.nside == 8
    assert vm.npix == 8
    assert vm.input_path == "data/map.fits"
    assert vm.lmax == 4
    assert vm.cls_length == 5
    assert vm.histogram is not None
    assert vm.map_preview is not None
    assert vm.spectrum
    assert vm.cls_table
    assert vm.metadata["field"] == "I"


def test_present_analyze_rejects_none_result() -> None:
    with pytest.raises(ValueError):
        present_analyze(None)