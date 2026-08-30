import xarray as xr



# ---------------------------------------------------------------------
# Fakes / Mocks simples
# ---------------------------------------------------------------------

class FakeGeometryProvider:
    def compute(self, satellites, time_range):
        return xr.Dataset(
            data_vars={
                "elevation": (("satellite", "time"), [[45.0]]),
            },
            coords={
                "satellite": [s.id.norad_id for s in satellites],
                "time": [time_range.start.datetime],
            },
        )


class FakeSignalFactory:
    def simulate(self, satellites, geometry, time_range):
        _ = (satellites, time_range)  # assinala uso (interface/reservado)
        return xr.Dataset(
            data_vars={
                "power": (("satellite", "time"), [[-120.0]]),
            },
            coords=geometry.coords,
        )

