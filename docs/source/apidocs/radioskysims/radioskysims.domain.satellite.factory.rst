:py:mod:`radioskysims.domain.satellite.factory`
===============================================

.. py:module:: radioskysims.domain.satellite.factory

.. autodoc2-docstring:: radioskysims.domain.satellite.factory
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`SatelliteFactory <radioskysims.domain.satellite.factory.SatelliteFactory>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.factory.SatelliteFactory
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`logger <radioskysims.domain.satellite.factory.logger>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.factory.logger
          :summary:

API
~~~

.. py:data:: logger
   :canonical: radioskysims.domain.satellite.factory.logger
   :value: 'getLogger(...)'

   .. autodoc2-docstring:: radioskysims.domain.satellite.factory.logger

.. py:class:: SatelliteFactory
   :canonical: radioskysims.domain.satellite.factory.SatelliteFactory

   .. autodoc2-docstring:: radioskysims.domain.satellite.factory.SatelliteFactory

   .. py:method:: build(*, tr: radioskysims.domain.common.TimeRange, repository: radioskysims.infrastructure.db.satellite.satelliterepository.SatelliteRepository, ids: list[int] | None = None, constellations: list[str] | None = None, interval: int = 5) -> dict[radioskysims.domain.common.TimeRange, list[radioskysims.domain.satellite.models.Satellite]]
      :canonical: radioskysims.domain.satellite.factory.SatelliteFactory.build

      .. autodoc2-docstring:: radioskysims.domain.satellite.factory.SatelliteFactory.build
