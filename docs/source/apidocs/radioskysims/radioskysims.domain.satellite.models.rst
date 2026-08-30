:py:mod:`radioskysims.domain.satellite.models`
==============================================

.. py:module:: radioskysims.domain.satellite.models

.. autodoc2-docstring:: radioskysims.domain.satellite.models
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Satellite <radioskysims.domain.satellite.models.Satellite>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.models.Satellite
          :summary:
   * - :py:obj:`SatelliteAssembled <radioskysims.domain.satellite.models.SatelliteAssembled>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.models.SatelliteAssembled
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`INTERVAL_DAYS <radioskysims.domain.satellite.models.INTERVAL_DAYS>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.models.INTERVAL_DAYS
          :summary:

API
~~~

.. py:data:: INTERVAL_DAYS
   :canonical: radioskysims.domain.satellite.models.INTERVAL_DAYS
   :value: 5

   .. autodoc2-docstring:: radioskysims.domain.satellite.models.INTERVAL_DAYS

.. py:class:: Satellite(/, **data: typing.Any)
   :canonical: radioskysims.domain.satellite.models.Satellite

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: radioskysims.domain.satellite.models.Satellite

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.satellite.models.Satellite.__init__

   .. py:attribute:: norad_id
      :canonical: radioskysims.domain.satellite.models.Satellite.norad_id
      :type: int
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.satellite.models.Satellite.norad_id

   .. py:attribute:: name
      :canonical: radioskysims.domain.satellite.models.Satellite.name
      :type: str | None
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.satellite.models.Satellite.name

   .. py:attribute:: constellation
      :canonical: radioskysims.domain.satellite.models.Satellite.constellation
      :type: str | None
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.satellite.models.Satellite.constellation

   .. py:attribute:: epoch
      :canonical: radioskysims.domain.satellite.models.Satellite.epoch
      :type: datetime.datetime
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.satellite.models.Satellite.epoch

   .. py:attribute:: element
      :canonical: radioskysims.domain.satellite.models.Satellite.element
      :type: radioskysims.infrastructure.db.satellite.models.OrbitalElement
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.satellite.models.Satellite.element

   .. py:method:: validate_epoch_interval()
      :canonical: radioskysims.domain.satellite.models.Satellite.validate_epoch_interval

      .. autodoc2-docstring:: radioskysims.domain.satellite.models.Satellite.validate_epoch_interval

.. py:class:: SatelliteAssembled(*, name: str, tracks: xarray.Dataset, signals: xarray.Dataset)
   :canonical: radioskysims.domain.satellite.models.SatelliteAssembled

   .. autodoc2-docstring:: radioskysims.domain.satellite.models.SatelliteAssembled

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.satellite.models.SatelliteAssembled.__init__

   .. py:method:: angle() -> xarray.DataArray
      :canonical: radioskysims.domain.satellite.models.SatelliteAssembled.angle

      .. autodoc2-docstring:: radioskysims.domain.satellite.models.SatelliteAssembled.angle

   .. py:method:: range() -> xarray.DataArray
      :canonical: radioskysims.domain.satellite.models.SatelliteAssembled.range

      .. autodoc2-docstring:: radioskysims.domain.satellite.models.SatelliteAssembled.range

   .. py:method:: psd() -> xarray.DataArray
      :canonical: radioskysims.domain.satellite.models.SatelliteAssembled.psd

      .. autodoc2-docstring:: radioskysims.domain.satellite.models.SatelliteAssembled.psd
