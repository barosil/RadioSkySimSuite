from __future__ import annotations

from datetime import datetime

import pytest

from radioskysims_sources.domain.satellite.factory import SatelliteFactory
from radioskysims_sources.domain.satellite.models import Satellite
from radioskysims.infrastructure.db.models import OrbitalElement, SatID


class DummyRepository:
    """Mock simples para substituir o SatelliteRepository."""

    def __init__(self, sats: list[SatID]):
        self._sats = sats

    def query_satellites(self, norad_ids: list[int]) -> list[SatID]:
        return [s for s in self._sats if s.norad_id in norad_ids]

    def load_from_constellation(self, constellation: str) -> list[SatID]:
        return [s for s in self._sats if s.constellation == constellation]


@pytest.fixture
def sample_sat():
    """Cria um SatID + OrbitalElement de exemplo (mock)."""
    sat = SatID(
        norad_id=25544,
        name="ISS",
        period=92.68,
        inclination=51.64,
        apogee=420.0,
        perigee=418.0,
        eccentricity=0.0001,
        gp_age=0.0,
        constellation="LEO",
        type="station",
    )
    elem = OrbitalElement(
        object_name="ISS",
        norad_id=25544,
        epoch=datetime(2021, 10, 2, 12, 0, 0),
        tle_line1="1 25544U 98067A   21275.51857639  .00002182  00000-0  50362-4 0  9991",
        tle_line2="2 25544  51.6443  21.4184 0004295  35.2895 324.8335 15.48942522302788",
    )
    sat.elements = [elem]
    return sat


def test_create_from_norad_ids(sample_sat):
    repo = DummyRepository([sample_sat])
    factory = SatelliteFactory(repo)

    sats = factory.create_from_norad_ids([25544], datetime(2021, 10, 2, 12, 0, 0))

    assert len(sats) == 1
    assert isinstance(sats[0], Satellite)
    # O Satellite retornado deve ter o elemento orbital correto
    assert sats[0].element.tle_line1.startswith("1 25544")


def test_create_from_constellations(sample_sat):
    repo = DummyRepository([sample_sat])
    factory = SatelliteFactory(repo)

    sats = factory.create_from_constellations(["LEO"], datetime(2021, 10, 2, 12, 0, 0))

    assert len(sats) == 1
    assert sats[0].element.tle_line1.startswith("1 25544")


def test_create_satellite_without_elements_should_fail():
    """Se o SatID não tiver OrbitalElement, deve levantar ValueError."""
    sat = SatID(
        norad_id=99999,
        name="FAKE",
        period=100.0,
        inclination=45.0,
        apogee=500.0,
        perigee=490.0,
        eccentricity=0.01,
        gp_age=0.0,
        constellation="TEST",
        type="dummy",
    )
    sat.elements = []  # nenhum elemento orbital

    repo = DummyRepository([sat])
    factory = SatelliteFactory(repo)

    with pytest.raises(ValueError, match="Sem elementos orbitais disponíveis"):
        factory.create_from_norad_ids([99999], datetime(2021, 10, 2, 12, 0, 0))
