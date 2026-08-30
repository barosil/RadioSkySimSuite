:py:mod:`domain.common.models`
==============================

.. py:module:: domain.common.models

.. autodoc2-docstring:: domain.common.models
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`FrequencyRange <domain.common.models.FrequencyRange>`
     - .. autodoc2-docstring:: domain.common.models.FrequencyRange
          :summary:
   * - :py:obj:`AngularRange <domain.common.models.AngularRange>`
     - .. autodoc2-docstring:: domain.common.models.AngularRange
          :summary:
   * - :py:obj:`TimeRange <domain.common.models.TimeRange>`
     - .. autodoc2-docstring:: domain.common.models.TimeRange
          :summary:
   * - :py:obj:`Observer <domain.common.models.Observer>`
     - .. autodoc2-docstring:: domain.common.models.Observer
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`parse_angle <domain.common.models.parse_angle>`
     - .. autodoc2-docstring:: domain.common.models.parse_angle
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`AngleInput <domain.common.models.AngleInput>`
     - .. autodoc2-docstring:: domain.common.models.AngleInput
          :summary:

API
~~~

.. py:class:: FrequencyRange
   :canonical: domain.common.models.FrequencyRange

   Bases: :py:obj:`BaseModel`

   .. autodoc2-docstring:: domain.common.models.FrequencyRange

   .. py:attribute:: min_mhz
      :canonical: domain.common.models.FrequencyRange.min_mhz
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.min_mhz

   .. py:attribute:: max_mhz
      :canonical: domain.common.models.FrequencyRange.max_mhz
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.max_mhz

   .. py:attribute:: resolution_mhz
      :canonical: domain.common.models.FrequencyRange.resolution_mhz
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.resolution_mhz

   .. py:method:: _convert_to_mhz(v)
      :canonical: domain.common.models.FrequencyRange._convert_to_mhz
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.FrequencyRange._convert_to_mhz

   .. py:method:: _ensure_resolution()
      :canonical: domain.common.models.FrequencyRange._ensure_resolution

      .. autodoc2-docstring:: domain.common.models.FrequencyRange._ensure_resolution

   .. py:method:: from_floats(min_val: float, max_val: float, resolution: float | None = None, unit: u.Unit = u.MHz)
      :canonical: domain.common.models.FrequencyRange.from_floats
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.from_floats

   .. py:method:: from_array(arr: list[float] | np.ndarray | list[u.Quantity])
      :canonical: domain.common.models.FrequencyRange.from_array
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.from_array

   .. py:method:: from_string(s: str, unit: u.Unit = u.MHz)
      :canonical: domain.common.models.FrequencyRange.from_string
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.from_string

   .. py:method:: from_config(cfg: dict)
      :canonical: domain.common.models.FrequencyRange.from_config
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.from_config

   .. py:property:: value
      :canonical: domain.common.models.FrequencyRange.value
      :type: np.ndarray

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.value

   .. py:property:: range
      :canonical: domain.common.models.FrequencyRange.range
      :type: xr.DataArray

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.range

   .. py:property:: resolution
      :canonical: domain.common.models.FrequencyRange.resolution
      :type: float

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.resolution

   .. py:property:: min
      :canonical: domain.common.models.FrequencyRange.min
      :type: float

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.min

   .. py:property:: max
      :canonical: domain.common.models.FrequencyRange.max
      :type: float

      .. autodoc2-docstring:: domain.common.models.FrequencyRange.max

.. py:class:: AngularRange
   :canonical: domain.common.models.AngularRange

   Bases: :py:obj:`BaseModel`

   .. autodoc2-docstring:: domain.common.models.AngularRange

   .. py:attribute:: min_rad
      :canonical: domain.common.models.AngularRange.min_rad
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.common.models.AngularRange.min_rad

   .. py:attribute:: max_rad
      :canonical: domain.common.models.AngularRange.max_rad
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.common.models.AngularRange.max_rad

   .. py:attribute:: resolution_rad
      :canonical: domain.common.models.AngularRange.resolution_rad
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.common.models.AngularRange.resolution_rad

   .. py:method:: _convert_to_rad(v)
      :canonical: domain.common.models.AngularRange._convert_to_rad
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.AngularRange._convert_to_rad

   .. py:method:: _ensure_resolution()
      :canonical: domain.common.models.AngularRange._ensure_resolution

      .. autodoc2-docstring:: domain.common.models.AngularRange._ensure_resolution

   .. py:method:: from_floats(min_val: float, max_val: float, resolution: float | None = None, unit: u.Unit = u.deg)
      :canonical: domain.common.models.AngularRange.from_floats
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.AngularRange.from_floats

   .. py:method:: from_array(arr: list[float] | np.ndarray | list[u.Quantity])
      :canonical: domain.common.models.AngularRange.from_array
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.AngularRange.from_array

   .. py:method:: from_string(s: str, unit: u.Unit = u.deg)
      :canonical: domain.common.models.AngularRange.from_string
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.AngularRange.from_string

   .. py:method:: from_degrees(min_val: float, max_val: float, resolution: float | None = None)
      :canonical: domain.common.models.AngularRange.from_degrees
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.AngularRange.from_degrees

   .. py:method:: from_hours(min_val: float, max_val: float, resolution: float | None = None)
      :canonical: domain.common.models.AngularRange.from_hours
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.AngularRange.from_hours

   .. py:method:: from_config(cfg: dict)
      :canonical: domain.common.models.AngularRange.from_config
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.AngularRange.from_config

   .. py:property:: value
      :canonical: domain.common.models.AngularRange.value
      :type: np.ndarray

      .. autodoc2-docstring:: domain.common.models.AngularRange.value

   .. py:property:: range
      :canonical: domain.common.models.AngularRange.range
      :type: xr.DataArray

      .. autodoc2-docstring:: domain.common.models.AngularRange.range

   .. py:property:: angle
      :canonical: domain.common.models.AngularRange.angle
      :type: Angle

      .. autodoc2-docstring:: domain.common.models.AngularRange.angle

   .. py:property:: resolution
      :canonical: domain.common.models.AngularRange.resolution
      :type: float

      .. autodoc2-docstring:: domain.common.models.AngularRange.resolution

   .. py:property:: min
      :canonical: domain.common.models.AngularRange.min
      :type: float

      .. autodoc2-docstring:: domain.common.models.AngularRange.min

   .. py:property:: max
      :canonical: domain.common.models.AngularRange.max
      :type: float

      .. autodoc2-docstring:: domain.common.models.AngularRange.max

   .. py:method:: __repr__() -> str
      :canonical: domain.common.models.AngularRange.__repr__

      .. autodoc2-docstring:: domain.common.models.AngularRange.__repr__

.. py:class:: TimeRange
   :canonical: domain.common.models.TimeRange

   Bases: :py:obj:`BaseModel`

   .. autodoc2-docstring:: domain.common.models.TimeRange

   .. py:attribute:: start_tai
      :canonical: domain.common.models.TimeRange.start_tai
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.common.models.TimeRange.start_tai

   .. py:attribute:: end_tai
      :canonical: domain.common.models.TimeRange.end_tai
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.common.models.TimeRange.end_tai

   .. py:attribute:: resolution_sec
      :canonical: domain.common.models.TimeRange.resolution_sec
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.common.models.TimeRange.resolution_sec

   .. py:method:: _convert_to_tai_seconds(v)
      :canonical: domain.common.models.TimeRange._convert_to_tai_seconds
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.TimeRange._convert_to_tai_seconds

   .. py:method:: _ensure_resolution() -> Self
      :canonical: domain.common.models.TimeRange._ensure_resolution

      .. autodoc2-docstring:: domain.common.models.TimeRange._ensure_resolution

   .. py:method:: from_astropy(start: Time, end: Time, resolution: float | None = None, unit: u.Unit = u.s)
      :canonical: domain.common.models.TimeRange.from_astropy
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.TimeRange.from_astropy

   .. py:method:: from_iso(start: str, end: str, resolution: float | None = None, unit: u.Unit = u.s)
      :canonical: domain.common.models.TimeRange.from_iso
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.TimeRange.from_iso

   .. py:method:: from_jd(start_jd: float, end_jd: float, resolution: float | None = None, unit: u.Unit = u.s)
      :canonical: domain.common.models.TimeRange.from_jd
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.TimeRange.from_jd

   .. py:method:: from_config(cfg: dict)
      :canonical: domain.common.models.TimeRange.from_config
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.TimeRange.from_config

   .. py:property:: value
      :canonical: domain.common.models.TimeRange.value
      :type: np.ndarray

      .. autodoc2-docstring:: domain.common.models.TimeRange.value

   .. py:property:: range
      :canonical: domain.common.models.TimeRange.range
      :type: xr.DataArray

      .. autodoc2-docstring:: domain.common.models.TimeRange.range

   .. py:method:: to_astropy() -> Time
      :canonical: domain.common.models.TimeRange.to_astropy

      .. autodoc2-docstring:: domain.common.models.TimeRange.to_astropy

   .. py:method:: to_numpy() -> np.ndarray
      :canonical: domain.common.models.TimeRange.to_numpy

      .. autodoc2-docstring:: domain.common.models.TimeRange.to_numpy

   .. py:method:: to_pandas() -> pd.DatetimeIndex
      :canonical: domain.common.models.TimeRange.to_pandas

      .. autodoc2-docstring:: domain.common.models.TimeRange.to_pandas

   .. py:method:: to_skyfield()
      :canonical: domain.common.models.TimeRange.to_skyfield

      .. autodoc2-docstring:: domain.common.models.TimeRange.to_skyfield

   .. py:property:: min
      :canonical: domain.common.models.TimeRange.min
      :type: float

      .. autodoc2-docstring:: domain.common.models.TimeRange.min

   .. py:property:: max
      :canonical: domain.common.models.TimeRange.max
      :type: float

      .. autodoc2-docstring:: domain.common.models.TimeRange.max

   .. py:property:: resolution
      :canonical: domain.common.models.TimeRange.resolution
      :type: float

      .. autodoc2-docstring:: domain.common.models.TimeRange.resolution

   .. py:method:: __repr__() -> str
      :canonical: domain.common.models.TimeRange.__repr__

      .. autodoc2-docstring:: domain.common.models.TimeRange.__repr__

.. py:data:: AngleInput
   :canonical: domain.common.models.AngleInput
   :value: None

   .. autodoc2-docstring:: domain.common.models.AngleInput

.. py:function:: parse_angle(value: domain.common.models.AngleInput, default_unit=u.deg) -> Angle
   :canonical: domain.common.models.parse_angle

   .. autodoc2-docstring:: domain.common.models.parse_angle

.. py:class:: Observer
   :canonical: domain.common.models.Observer

   Bases: :py:obj:`BaseModel`

   .. autodoc2-docstring:: domain.common.models.Observer

   .. py:attribute:: model_config
      :canonical: domain.common.models.Observer.model_config
      :value: 'ConfigDict(...)'

      .. autodoc2-docstring:: domain.common.models.Observer.model_config

   .. py:attribute:: lat
      :canonical: domain.common.models.Observer.lat
      :type: domain.common.models.AngleInput
      :value: None

      .. autodoc2-docstring:: domain.common.models.Observer.lat

   .. py:attribute:: lon
      :canonical: domain.common.models.Observer.lon
      :type: domain.common.models.AngleInput
      :value: None

      .. autodoc2-docstring:: domain.common.models.Observer.lon

   .. py:attribute:: height
      :canonical: domain.common.models.Observer.height
      :type: float | u.Quantity | None
      :value: 0.0

      .. autodoc2-docstring:: domain.common.models.Observer.height

   .. py:attribute:: timeframe
      :canonical: domain.common.models.Observer.timeframe
      :type: domain.common.models.TimeRange
      :value: None

      .. autodoc2-docstring:: domain.common.models.Observer.timeframe

   .. py:method:: validate_lat(v)
      :canonical: domain.common.models.Observer.validate_lat
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.Observer.validate_lat

   .. py:method:: validate_lon(v)
      :canonical: domain.common.models.Observer.validate_lon
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.Observer.validate_lon

   .. py:method:: validate_height(v)
      :canonical: domain.common.models.Observer.validate_height
      :classmethod:

      .. autodoc2-docstring:: domain.common.models.Observer.validate_height

   .. py:method:: to_astropy() -> EarthLocation
      :canonical: domain.common.models.Observer.to_astropy

      .. autodoc2-docstring:: domain.common.models.Observer.to_astropy

   .. py:method:: to_skyfield()
      :canonical: domain.common.models.Observer.to_skyfield

      .. autodoc2-docstring:: domain.common.models.Observer.to_skyfield
