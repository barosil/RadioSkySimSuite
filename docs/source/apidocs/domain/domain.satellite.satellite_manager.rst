:py:mod:`domain.satellite.satellite_manager`
============================================

.. py:module:: domain.satellite.satellite_manager

.. autodoc2-docstring:: domain.satellite.satellite_manager
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`SatelliteManager <domain.satellite.satellite_manager.SatelliteManager>`
     - .. autodoc2-docstring:: domain.satellite.satellite_manager.SatelliteManager
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`logger <domain.satellite.satellite_manager.logger>`
     - .. autodoc2-docstring:: domain.satellite.satellite_manager.logger
          :summary:

API
~~~

.. py:data:: logger
   :canonical: domain.satellite.satellite_manager.logger
   :value: 'getLogger(...)'

   .. autodoc2-docstring:: domain.satellite.satellite_manager.logger

.. py:class:: SatelliteManager(satellites: list[domain.satellite.models.Satellite], location: astropy.coordinates.EarthLocation)
   :canonical: domain.satellite.satellite_manager.SatelliteManager

   .. autodoc2-docstring:: domain.satellite.satellite_manager.SatelliteManager

   .. rubric:: Initialization

   .. autodoc2-docstring:: domain.satellite.satellite_manager.SatelliteManager.__init__

   .. py:method:: get_satellite(sat_id: str) -> domain.satellite.models.Satellite | None
      :canonical: domain.satellite.satellite_manager.SatelliteManager.get_satellite

      .. autodoc2-docstring:: domain.satellite.satellite_manager.SatelliteManager.get_satellite

   .. py:method:: compute_skycoord(satellite: domain.satellite.models.Satellite, timestamp: astropy.time.Time) -> astropy.coordinates.SkyCoord
      :canonical: domain.satellite.satellite_manager.SatelliteManager.compute_skycoord

      .. autodoc2-docstring:: domain.satellite.satellite_manager.SatelliteManager.compute_skycoord

   .. py:method:: list_signals(sat_id: str) -> list[domain.satellite.models.Signal]
      :canonical: domain.satellite.satellite_manager.SatelliteManager.list_signals

      .. autodoc2-docstring:: domain.satellite.satellite_manager.SatelliteManager.list_signals
