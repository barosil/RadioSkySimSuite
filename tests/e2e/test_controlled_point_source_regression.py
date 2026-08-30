from __future__ import annotations

import json
import subprocess


def run_script():
    out = subprocess.check_output(
        ["python3", "scripts/controlled_point_source_experiment.py"], text=True
    )
    return json.loads(out)


def test_radiometry_and_fwhm_and_flux():
    report = run_script()

    # Radiometry: T_A_max matches T_expected (within numerical tol)
    b = report["B_radiometry"]
    rel_err = abs(b["rel_error"]) if isinstance(b.get("rel_error"), (int, float)) else float("inf")
    assert rel_err < 1e-9

    # Flux recovery ~1 Jy
    d = report["D_flux_recovery"]
    assert abs(d["flux_rel_error"]) < 1e-3

    # FWHM ~ 0.6 deg
    c = report["C_profile"]
    fwhm = c["fwhm_recovered_deg"]
    assert abs(fwhm - 0.6) < 1e-3
