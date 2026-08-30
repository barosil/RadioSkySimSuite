from __future__ import annotations

__all__ = ["SkyMapRecord"]


def __getattr__(name: str):
    if name == "SkyMapRecord":
        from radioskysims_skymap.infrastructure.db.skymap_models import SkyMapRecord

        return SkyMapRecord
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
