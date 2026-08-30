# BAROSI

## Doing

### Common

- [ ] src/radioskysims/domain/common/models.py
  - `FrequencyRange(BaseModel)`
    - min_mhz (float): Minimum frequency in MHz.
    - max_mhz (float): Maximum frequency in MHz.
    - resolution_mhz (float): Resolution in MHz.
  - `AngularRange(BaseModel)`
    - min_rad (float): Minimum angle in radians.
    - max_rad (float): Maximum angle in radians.
    - resolution_rad (float): Angular resolution in radians.
  - `TimeRange(BaseModel)`
    - start_tai (float): Início do intervalo em segundos TAI.
    - end_tai (float): Fim do intervalo em segundos TAI.
    - resolution_sec (float): Resolução temporal em segundos.
  - `Observer(BaseModel)`
    - lat: AngleInput
    - lon: AngleInput
    - height: float | u.Quantity | None = 0.0  # metros
    - timeframe: TimeRange
  - [x] classes
  - [x] testes em notebook
  - [ ] unittests
  - [ ] code quality

- [x] src/radioskysims/infrastructure/coords.py
  - **arquivado**

### Satellite

#### Domain

- [x] src/radioskysims/domain/satellite/models.py
  - `Orbits(BaseModel):`
    - `get_sat_ids`
    - `get_timerange(self)`
    - `get_sats`
  - `Ephemeris(BaseModel)`
    - `positions: xr.DataArray`
    - `velocities: xr.DataArray`
  - `Satellite(BaseModel)`
    - `name: str`
    - `tle_line1: str`
    - `tle_line2: str`
    - `load_ephemeris(self, tr: TimeRange) -> Ephemeris:`
    - `Satellites(BaseModel)`
    - `make_orbits(self, tr: TimeRange) -> Orbits`
  - [x] classes
  - [ ] testes em notebook
  - [ ] unittests
  - [ ] code quality
- [ ] src/radioskysims/domain/satellite/factory.py
  - `SatelliteFactory`
    - repository
    - `create_from_norad_ids(
        self, norad_ids: list[int], epoch: datetime
    ) -> list[Satellite]:`
    - `create_from_constellations(
        self, constellations: list[str], epoch: datetime
    ) -> list[Satellite]`
    - `_to_domain_model(self, satid: SatID, epoch: datetime) -> Satellite`
    - Incorporar atributos da classe.
- [ ] src/radioskysims/domain/satellite/satellite_manager.py
- [x] src/radioskysims/domain/satellite/main.py
  - **removido**: lógica para app
- [ ] src/radioskysims/domain/satellite/simulation.py
- [ ] src/radioskysims/domain/satellite/selection.py

#### Infrastruture

- [x] src/radioskysims/infrastructure/db/models.py
  - `SatID(SQLModel, table=True)`
  - `OrbitalElement(SQLModel, table=True)`
  - [x] classes
  - [ ] code quality
- [x] src/radioskysims/infrastructure/satellite_file_repository.py
  - **arquivado**
- [ ] src/radioskysims/infrastructure/satellite_repository.py

#### Application

- [ ] src/radioskysims/interfaces/gui/satellite_panel.py

#### Presentation

- [ ] src/radioskysims/interfaces/api/satellite_controller.py

### Signal

- [ ] src/radioskysims/domain/signal/factory.py
- [ ] src/radioskysims/domain/signal/models.py

### Beam

- [ ] src/radioskysims/infrastructure/beam_repository.py
- [ ] src/radioskysims/interfaces/gui/beam_visualizer.py

### Doing

- [x] Implementar uso das classes de Common no domínio Satélite.
- [x] CelestrakClient
- [x] SpaceTrackClient
- [x] Sat_ID
- [x] Constellation
- [ ] SatelliteFactory
- [ ] SatelliteRepository
- [x] SatSignal
- [ ] SignalFactory
``
