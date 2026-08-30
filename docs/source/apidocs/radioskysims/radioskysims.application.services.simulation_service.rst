:py:mod:`radioskysims.application.services.simulation_service`
==============================================================

.. py:module:: radioskysims.application.services.simulation_service

.. autodoc2-docstring:: radioskysims.application.services.simulation_service
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`SimulationService <radioskysims.application.services.simulation_service.SimulationService>`
     - .. autodoc2-docstring:: radioskysims.application.services.simulation_service.SimulationService
          :summary:

API
~~~

.. py:class:: SimulationService(satellite_service: radioskysims.application.services.satellite_service.SatelliteService, geometry: radioskysims.domain.geometry.GeometryProvider, signal_factory: radioskysims.domain.signal.SignalFactory, tod_simulator: radioskysims.domain.tod.TODSimulator)
   :canonical: radioskysims.application.services.simulation_service.SimulationService

   .. autodoc2-docstring:: radioskysims.application.services.simulation_service.SimulationService

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.application.services.simulation_service.SimulationService.__init__

   .. py:method:: run_by_ids(norad_ids: collections.abc.Iterable[int], time_range: radioskysims.domain.common.TimeRange) -> radioskysims.domain.simulation.SimulationResult
      :canonical: radioskysims.application.services.simulation_service.SimulationService.run_by_ids

      .. autodoc2-docstring:: radioskysims.application.services.simulation_service.SimulationService.run_by_ids

   .. py:method:: run_by_constellations(constellations: collections.abc.Iterable[str], time_range: radioskysims.domain.common.TimeRange) -> radioskysims.domain.simulation.SimulationResult
      :canonical: radioskysims.application.services.simulation_service.SimulationService.run_by_constellations

      .. autodoc2-docstring:: radioskysims.application.services.simulation_service.SimulationService.run_by_constellations

   .. py:method:: run(satellites: collections.abc.Iterable[radioskysims.domain.satellite.Satellite], time_range: radioskysims.domain.common.TimeRange) -> radioskysims.domain.simulation.SimulationResult
      :canonical: radioskysims.application.services.simulation_service.SimulationService.run

      .. autodoc2-docstring:: radioskysims.application.services.simulation_service.SimulationService.run

   .. py:method:: _run(satellites: list[radioskysims.domain.satellite.Satellite], time_range: radioskysims.domain.common.TimeRange) -> radioskysims.domain.simulation.SimulationResult
      :canonical: radioskysims.application.services.simulation_service.SimulationService._run

      .. autodoc2-docstring:: radioskysims.application.services.simulation_service.SimulationService._run
