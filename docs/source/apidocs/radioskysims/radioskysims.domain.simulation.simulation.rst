:py:mod:`radioskysims.domain.simulation.simulation`
===================================================

.. py:module:: radioskysims.domain.simulation.simulation

.. autodoc2-docstring:: radioskysims.domain.simulation.simulation
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`SimulationResult <radioskysims.domain.simulation.simulation.SimulationResult>`
     - .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.SimulationResult
          :summary:
   * - :py:obj:`Simulation <radioskysims.domain.simulation.simulation.Simulation>`
     - .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.Simulation
          :summary:

API
~~~

.. py:class:: SimulationResult
   :canonical: radioskysims.domain.simulation.simulation.SimulationResult

   .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.SimulationResult

   .. py:attribute:: dataset
      :canonical: radioskysims.domain.simulation.simulation.SimulationResult.dataset
      :type: xarray.Dataset
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.SimulationResult.dataset

   .. py:attribute:: satellites
      :canonical: radioskysims.domain.simulation.simulation.SimulationResult.satellites
      :type: list[radioskysims.domain.satellite.Satellite]
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.SimulationResult.satellites

   .. py:attribute:: time_range
      :canonical: radioskysims.domain.simulation.simulation.SimulationResult.time_range
      :type: radioskysims.domain.common.TimeRange
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.SimulationResult.time_range

.. py:class:: Simulation(satellites: collections.abc.Iterable[radioskysims.domain.satellite.Satellite], time_range: radioskysims.domain.common.TimeRange, geometry: radioskysims.domain.geometry.GeometryProvider, signal_factory: radioskysims.domain.signal.SignalFactory, tod_simulator: radioskysims.domain.tod.TODSimulator)
   :canonical: radioskysims.domain.simulation.simulation.Simulation

   .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.Simulation

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.Simulation.__init__

   .. py:property:: satellites
      :canonical: radioskysims.domain.simulation.simulation.Simulation.satellites
      :type: list[radioskysims.domain.satellite.Satellite]

      .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.Simulation.satellites

   .. py:property:: time_range
      :canonical: radioskysims.domain.simulation.simulation.Simulation.time_range
      :type: radioskysims.domain.common.TimeRange

      .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.Simulation.time_range

   .. py:method:: run() -> radioskysims.domain.simulation.simulation.SimulationResult
      :canonical: radioskysims.domain.simulation.simulation.Simulation.run

      .. autodoc2-docstring:: radioskysims.domain.simulation.simulation.Simulation.run
