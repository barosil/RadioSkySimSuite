:py:mod:`domain.satellite.factory`
==================================

.. py:module:: domain.satellite.factory

.. autodoc2-docstring:: domain.satellite.factory
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`SatelliteFactory <domain.satellite.factory.SatelliteFactory>`
     - .. autodoc2-docstring:: domain.satellite.factory.SatelliteFactory
          :summary:

API
~~~

.. py:class:: SatelliteFactory(db_session: radioskysims.infrastructure.database.DatabaseSession, spacetrack_client: radioskysims.infrastructure.spacetrack_client.SpaceTrackClient)
   :canonical: domain.satellite.factory.SatelliteFactory

   .. autodoc2-docstring:: domain.satellite.factory.SatelliteFactory

   .. rubric:: Initialization

   .. autodoc2-docstring:: domain.satellite.factory.SatelliteFactory.__init__

   .. py:method:: create_from_norad_ids(norad_ids: list[str], epoch: datetime.datetime) -> list[radioskysims.domain.satellite.models.Satellite]
      :canonical: domain.satellite.factory.SatelliteFactory.create_from_norad_ids

      .. autodoc2-docstring:: domain.satellite.factory.SatelliteFactory.create_from_norad_ids

   .. py:method:: create_from_constellations(constellation_names: list[str], epoch: datetime.datetime) -> list[radioskysims.domain.satellite.models.Satellite]
      :canonical: domain.satellite.factory.SatelliteFactory.create_from_constellations

      .. autodoc2-docstring:: domain.satellite.factory.SatelliteFactory.create_from_constellations

   .. py:method:: _build_satellite(norad_id: str, epoch: datetime.datetime) -> radioskysims.domain.satellite.models.Satellite
      :canonical: domain.satellite.factory.SatelliteFactory._build_satellite

      .. autodoc2-docstring:: domain.satellite.factory.SatelliteFactory._build_satellite

   .. py:method:: _is_epoch_valid(current_epoch: datetime.datetime, target_epoch: datetime.datetime, tolerance_days: int = 5) -> bool
      :canonical: domain.satellite.factory.SatelliteFactory._is_epoch_valid

      .. autodoc2-docstring:: domain.satellite.factory.SatelliteFactory._is_epoch_valid

   .. py:method:: _parse_and_store_gpe(gpe: str, norad_id: str) -> radioskysims.domain.satellite.models.OrbitalParameters
      :canonical: domain.satellite.factory.SatelliteFactory._parse_and_store_gpe

      .. autodoc2-docstring:: domain.satellite.factory.SatelliteFactory._parse_and_store_gpe
