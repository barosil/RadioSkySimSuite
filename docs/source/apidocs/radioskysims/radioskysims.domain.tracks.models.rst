:py:mod:`radioskysims.domain.tracks.models`
===========================================

.. py:module:: radioskysims.domain.tracks.models

.. autodoc2-docstring:: radioskysims.domain.tracks.models
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Tracks <radioskysims.domain.tracks.models.Tracks>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`ChunkIndex <radioskysims.domain.tracks.models.ChunkIndex>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.models.ChunkIndex
          :summary:
   * - :py:obj:`LogType <radioskysims.domain.tracks.models.LogType>`
     - .. autodoc2-docstring:: radioskysims.domain.tracks.models.LogType
          :summary:

API
~~~

.. py:data:: ChunkIndex
   :canonical: radioskysims.domain.tracks.models.ChunkIndex
   :value: None

   .. autodoc2-docstring:: radioskysims.domain.tracks.models.ChunkIndex

.. py:data:: LogType
   :canonical: radioskysims.domain.tracks.models.LogType
   :value: None

   .. autodoc2-docstring:: radioskysims.domain.tracks.models.LogType

.. py:class:: Tracks(/, **data: typing.Any)
   :canonical: radioskysims.domain.tracks.models.Tracks

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.__init__

   .. py:attribute:: dataset
      :canonical: radioskysims.domain.tracks.models.Tracks.dataset
      :type: typing.Any
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.dataset

   .. py:attribute:: satellite_names
      :canonical: radioskysims.domain.tracks.models.Tracks.satellite_names
      :type: list[str]
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.satellite_names

   .. py:attribute:: time_range
      :canonical: radioskysims.domain.tracks.models.Tracks.time_range
      :type: tuple[str, str]
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.time_range

   .. py:attribute:: lock
      :canonical: radioskysims.domain.tracks.models.Tracks.lock
      :type: threading.Lock
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.lock

   .. py:attribute:: async_lock
      :canonical: radioskysims.domain.tracks.models.Tracks.async_lock
      :type: asyncio.Lock
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.async_lock

   .. py:attribute:: log
      :canonical: radioskysims.domain.tracks.models.Tracks.log
      :type: radioskysims.domain.tracks.models.LogType
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.log

   .. py:attribute:: model_config
      :canonical: radioskysims.domain.tracks.models.Tracks.model_config
      :value: 'ConfigDict(...)'

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.model_config

   .. py:method:: _validate_dataset(ds)
      :canonical: radioskysims.domain.tracks.models.Tracks._validate_dataset
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks._validate_dataset

   .. py:method:: _validate_structure(ds) -> None
      :canonical: radioskysims.domain.tracks.models.Tracks._validate_structure
      :staticmethod:

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks._validate_structure

   .. py:method:: _validate_positions_shape(ds) -> None
      :canonical: radioskysims.domain.tracks.models.Tracks._validate_positions_shape
      :staticmethod:

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks._validate_positions_shape

   .. py:method:: _validate_xyz_coords(ds) -> None
      :canonical: radioskysims.domain.tracks.models.Tracks._validate_xyz_coords
      :staticmethod:

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks._validate_xyz_coords

   .. py:method:: from_xr(ds) -> radioskysims.domain.tracks.models.Tracks
      :canonical: radioskysims.domain.tracks.models.Tracks.from_xr
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.from_xr

   .. py:method:: _extract_names(ds) -> list[str]
      :canonical: radioskysims.domain.tracks.models.Tracks._extract_names
      :staticmethod:

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks._extract_names

   .. py:method:: _extract_time_range(ds) -> tuple[str, str]
      :canonical: radioskysims.domain.tracks.models.Tracks._extract_time_range
      :staticmethod:

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks._extract_time_range

   .. py:method:: _spawn(ds) -> radioskysims.domain.tracks.models.Tracks
      :canonical: radioskysims.domain.tracks.models.Tracks._spawn

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks._spawn

   .. py:method:: filter_by_satellite(sat_id: int | tuple[int, ...]) -> radioskysims.domain.tracks.models.Tracks
      :canonical: radioskysims.domain.tracks.models.Tracks.filter_by_satellite

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.filter_by_satellite

   .. py:method:: filter_by_constellation(const: str | tuple[str, ...]) -> radioskysims.domain.tracks.models.Tracks
      :canonical: radioskysims.domain.tracks.models.Tracks.filter_by_constellation

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.filter_by_constellation

   .. py:method:: filter_by_time(start=None, end=None) -> radioskysims.domain.tracks.models.Tracks
      :canonical: radioskysims.domain.tracks.models.Tracks.filter_by_time

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.filter_by_time

   .. py:method:: to_zarr(path: str, *, mode='w', consolidated=True, **kwargs) -> None
      :canonical: radioskysims.domain.tracks.models.Tracks.to_zarr

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.to_zarr

   .. py:method:: to_hdf5(path: str, *, mode='w', engine='h5netcdf', **kwargs) -> None
      :canonical: radioskysims.domain.tracks.models.Tracks.to_hdf5

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.to_hdf5

   .. py:method:: summary() -> dict[str, typing.Any]
      :canonical: radioskysims.domain.tracks.models.Tracks.summary

      .. autodoc2-docstring:: radioskysims.domain.tracks.models.Tracks.summary
