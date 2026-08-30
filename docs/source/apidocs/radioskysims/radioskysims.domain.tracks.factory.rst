:py:mod:`radioskysims.domain.tracks.factory`
============================================

.. py:module:: radioskysims.domain.tracks.factory

.. autodoc2-docstring:: radioskysims.domain.tracks.factory
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`TrackFactory <radioskysims.domain.tracks.factory.TrackFactory>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.factory.TrackFactory
          :summary:
   * - :py:obj:`SkyfieldAdapter <radioskysims.domain.tracks.factory.SkyfieldAdapter>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.factory.SkyfieldAdapter
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`_lazy_skyfield <radioskysims.domain.tracks.factory._lazy_skyfield>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.factory._lazy_skyfield
          :summary:
   * - :py:obj:`_lazy_SatID <radioskysims.domain.tracks.factory._lazy_SatID>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.factory._lazy_SatID
          :summary:
   * - :py:obj:`_lazy_Tracks <radioskysims.domain.tracks.factory._lazy_Tracks>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.factory._lazy_Tracks
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`logger <radioskysims.domain.tracks.factory.logger>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.factory.logger
          :summary:
   * - :py:obj:`config <radioskysims.domain.tracks.factory.config>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.factory.config
          :summary:
   * - :py:obj:`_lazy_cache <radioskysims.domain.tracks.factory._lazy_cache>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.factory._lazy_cache
          :summary:

API
~~~

.. py:data:: logger
   :canonical: radioskysims.domain.tracks.factory.logger
   :value: 'getLogger(...)'

   .. autodoc2-docstring:: radioskysims.domain.tracks.factory.logger

.. py:data:: config
   :canonical: radioskysims.domain.tracks.factory.config
   :value: 'load_config(...)'

   .. autodoc2-docstring:: radioskysims.domain.tracks.factory.config

.. py:data:: _lazy_cache
   :canonical: radioskysims.domain.tracks.factory._lazy_cache
   :value: None

   .. autodoc2-docstring:: radioskysims.domain.tracks.factory._lazy_cache

.. py:function:: _lazy_skyfield()
   :canonical: radioskysims.domain.tracks.factory._lazy_skyfield

   .. autodoc2-docstring:: radioskysims.domain.tracks.factory._lazy_skyfield

.. py:function:: _lazy_SatID()
   :canonical: radioskysims.domain.tracks.factory._lazy_SatID

   .. autodoc2-docstring:: radioskysims.domain.tracks.factory._lazy_SatID

.. py:function:: _lazy_Tracks()
   :canonical: radioskysims.domain.tracks.factory._lazy_Tracks

   .. autodoc2-docstring:: radioskysims.domain.tracks.factory._lazy_Tracks

.. py:class:: TrackFactory()
   :canonical: radioskysims.domain.tracks.factory.TrackFactory

   .. autodoc2-docstring:: radioskysims.domain.tracks.factory.TrackFactory

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.tracks.factory.TrackFactory.__init__

   .. py:method:: _build_earthsatellites(satellites: list[typing.Any])
      :canonical: radioskysims.domain.tracks.factory.TrackFactory._build_earthsatellites

      .. autodoc2-docstring:: radioskysims.domain.tracks.factory.TrackFactory._build_earthsatellites

   .. py:method:: _build_block_dataset(satellites: list[typing.Any], times: typing.Any) -> xarray.Dataset
      :canonical: radioskysims.domain.tracks.factory.TrackFactory._build_block_dataset

      .. autodoc2-docstring:: radioskysims.domain.tracks.factory.TrackFactory._build_block_dataset

   .. py:method:: _build_track_ds() -> xarray.Dataset
      :canonical: radioskysims.domain.tracks.factory.TrackFactory._build_track_ds

      .. autodoc2-docstring:: radioskysims.domain.tracks.factory.TrackFactory._build_track_ds

   .. py:method:: build(satellites_block=None, scheduler: str | None = None)
      :canonical: radioskysims.domain.tracks.factory.TrackFactory.build

      .. autodoc2-docstring:: radioskysims.domain.tracks.factory.TrackFactory.build

.. py:class:: SkyfieldAdapter()
   :canonical: radioskysims.domain.tracks.factory.SkyfieldAdapter

   .. autodoc2-docstring:: radioskysims.domain.tracks.factory.SkyfieldAdapter

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.tracks.factory.SkyfieldAdapter.__init__

   .. py:property:: loader
      :canonical: radioskysims.domain.tracks.factory.SkyfieldAdapter.loader

      .. autodoc2-docstring:: radioskysims.domain.tracks.factory.SkyfieldAdapter.loader

   .. py:property:: ts
      :canonical: radioskysims.domain.tracks.factory.SkyfieldAdapter.ts

      .. autodoc2-docstring:: radioskysims.domain.tracks.factory.SkyfieldAdapter.ts

   .. py:method:: times(timerange: typing.Any)
      :canonical: radioskysims.domain.tracks.factory.SkyfieldAdapter.times

      .. autodoc2-docstring:: radioskysims.domain.tracks.factory.SkyfieldAdapter.times

   .. py:method:: earthsatellite(satellite: typing.Any)
      :canonical: radioskysims.domain.tracks.factory.SkyfieldAdapter.earthsatellite

      .. autodoc2-docstring:: radioskysims.domain.tracks.factory.SkyfieldAdapter.earthsatellite
