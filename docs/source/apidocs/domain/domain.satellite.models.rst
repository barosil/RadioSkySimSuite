:py:mod:`domain.satellite.models`
=================================

.. py:module:: domain.satellite.models

.. autodoc2-docstring:: domain.satellite.models
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`SatId <domain.satellite.models.SatId>`
     - .. autodoc2-docstring:: domain.satellite.models.SatId
          :summary:
   * - :py:obj:`OrbitalParameters <domain.satellite.models.OrbitalParameters>`
     - .. autodoc2-docstring:: domain.satellite.models.OrbitalParameters
          :summary:
   * - :py:obj:`TimeRange <domain.satellite.models.TimeRange>`
     - .. autodoc2-docstring:: domain.satellite.models.TimeRange
          :summary:
   * - :py:obj:`Signal <domain.satellite.models.Signal>`
     - .. autodoc2-docstring:: domain.satellite.models.Signal
          :summary:
   * - :py:obj:`Satellite <domain.satellite.models.Satellite>`
     - .. autodoc2-docstring:: domain.satellite.models.Satellite
          :summary:

API
~~~

.. py:class:: SatId
   :canonical: domain.satellite.models.SatId

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: domain.satellite.models.SatId

   .. py:attribute:: norad_id
      :canonical: domain.satellite.models.SatId.norad_id
      :type: int
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.SatId.norad_id

   .. py:attribute:: name
      :canonical: domain.satellite.models.SatId.name
      :type: str
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.SatId.name

   .. py:method:: __repr__()
      :canonical: domain.satellite.models.SatId.__repr__

      .. autodoc2-docstring:: domain.satellite.models.SatId.__repr__

.. py:class:: OrbitalParameters
   :canonical: domain.satellite.models.OrbitalParameters

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: domain.satellite.models.OrbitalParameters

   .. py:attribute:: epoch
      :canonical: domain.satellite.models.OrbitalParameters.epoch
      :type: datetime.datetime
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.OrbitalParameters.epoch

   .. py:attribute:: tle0
      :canonical: domain.satellite.models.OrbitalParameters.tle0
      :type: str
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.OrbitalParameters.tle0

   .. py:attribute:: tle1
      :canonical: domain.satellite.models.OrbitalParameters.tle1
      :type: str
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.OrbitalParameters.tle1

   .. py:attribute:: tle2
      :canonical: domain.satellite.models.OrbitalParameters.tle2
      :type: str
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.OrbitalParameters.tle2

   .. py:method:: __repr__()
      :canonical: domain.satellite.models.OrbitalParameters.__repr__

      .. autodoc2-docstring:: domain.satellite.models.OrbitalParameters.__repr__

.. py:class:: TimeRange
   :canonical: domain.satellite.models.TimeRange

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: domain.satellite.models.TimeRange

   .. py:attribute:: start
      :canonical: domain.satellite.models.TimeRange.start
      :type: datetime.datetime
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.TimeRange.start

   .. py:attribute:: end
      :canonical: domain.satellite.models.TimeRange.end
      :type: datetime.datetime
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.TimeRange.end

   .. py:method:: duration_seconds() -> float
      :canonical: domain.satellite.models.TimeRange.duration_seconds

      .. autodoc2-docstring:: domain.satellite.models.TimeRange.duration_seconds

.. py:class:: Signal
   :canonical: domain.satellite.models.Signal

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: domain.satellite.models.Signal

   .. py:attribute:: frequency
      :canonical: domain.satellite.models.Signal.frequency
      :type: float
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.Signal.frequency

   .. py:attribute:: bandwidth
      :canonical: domain.satellite.models.Signal.bandwidth
      :type: float
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.Signal.bandwidth

   .. py:attribute:: polarization
      :canonical: domain.satellite.models.Signal.polarization
      :type: str
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.Signal.polarization

   .. py:attribute:: power
      :canonical: domain.satellite.models.Signal.power
      :type: float
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.Signal.power

.. py:class:: Satellite
   :canonical: domain.satellite.models.Satellite

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: domain.satellite.models.Satellite

   .. py:attribute:: id
      :canonical: domain.satellite.models.Satellite.id
      :type: domain.satellite.models.SatId
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.Satellite.id

   .. py:attribute:: orbital_parameters
      :canonical: domain.satellite.models.Satellite.orbital_parameters
      :type: domain.satellite.models.OrbitalParameters
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.Satellite.orbital_parameters

   .. py:attribute:: time_range
      :canonical: domain.satellite.models.Satellite.time_range
      :type: typing.Optional[domain.satellite.models.TimeRange]
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.Satellite.time_range

   .. py:attribute:: signal
      :canonical: domain.satellite.models.Satellite.signal
      :type: typing.Optional[domain.satellite.models.Signal]
      :value: None

      .. autodoc2-docstring:: domain.satellite.models.Satellite.signal

   .. py:method:: describe() -> str
      :canonical: domain.satellite.models.Satellite.describe

      .. autodoc2-docstring:: domain.satellite.models.Satellite.describe

   .. py:method:: __repr__()
      :canonical: domain.satellite.models.Satellite.__repr__

      .. autodoc2-docstring:: domain.satellite.models.Satellite.__repr__
