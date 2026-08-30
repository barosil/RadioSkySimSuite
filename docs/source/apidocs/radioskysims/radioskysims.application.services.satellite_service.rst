:py:mod:`radioskysims.application.services.satellite_service`
=============================================================

.. py:module:: radioskysims.application.services.satellite_service

.. autodoc2-docstring:: radioskysims.application.services.satellite_service
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`SatelliteService <radioskysims.application.services.satellite_service.SatelliteService>`
     - .. autodoc2-docstring:: radioskysims.application.services.satellite_service.SatelliteService
          :summary:

API
~~~

.. py:class:: SatelliteService(repository: radioskysims.infrastructure.db.satellite.satelliterepository.SatelliteRepository)
   :canonical: radioskysims.application.services.satellite_service.SatelliteService

   .. autodoc2-docstring:: radioskysims.application.services.satellite_service.SatelliteService

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.application.services.satellite_service.SatelliteService.__init__

   .. py:method:: get_all() -> list[radioskysims.domain.satellite.Satellite]
      :canonical: radioskysims.application.services.satellite_service.SatelliteService.get_all

      .. autodoc2-docstring:: radioskysims.application.services.satellite_service.SatelliteService.get_all

   .. py:method:: get_by_ids(norad_ids: collections.abc.Iterable[int]) -> list[radioskysims.domain.satellite.Satellite]
      :canonical: radioskysims.application.services.satellite_service.SatelliteService.get_by_ids

      .. autodoc2-docstring:: radioskysims.application.services.satellite_service.SatelliteService.get_by_ids

   .. py:method:: get_by_constellations(constellations: collections.abc.Iterable[str]) -> list[radioskysims.domain.satellite.Satellite]
      :canonical: radioskysims.application.services.satellite_service.SatelliteService.get_by_constellations

      .. autodoc2-docstring:: radioskysims.application.services.satellite_service.SatelliteService.get_by_constellations

   .. py:method:: update_orbital_elements(epoch: datetime.datetime | None = None, *, force: bool = False) -> None
      :canonical: radioskysims.application.services.satellite_service.SatelliteService.update_orbital_elements

      .. autodoc2-docstring:: radioskysims.application.services.satellite_service.SatelliteService.update_orbital_elements

   .. py:method:: update_from_celestrak() -> None
      :canonical: radioskysims.application.services.satellite_service.SatelliteService.update_from_celestrak

      .. autodoc2-docstring:: radioskysims.application.services.satellite_service.SatelliteService.update_from_celestrak

   .. py:method:: reset() -> None
      :canonical: radioskysims.application.services.satellite_service.SatelliteService.reset

      .. autodoc2-docstring:: radioskysims.application.services.satellite_service.SatelliteService.reset
