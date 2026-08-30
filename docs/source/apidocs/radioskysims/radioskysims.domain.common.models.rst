:py:mod:`radioskysims.domain.common.models`
===========================================

.. py:module:: radioskysims.domain.common.models

.. autodoc2-docstring:: radioskysims.domain.common.models
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`FrequencyRange <radioskysims.domain.common.models.FrequencyRange>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange
          :summary:
   * - :py:obj:`AngularRange <radioskysims.domain.common.models.AngularRange>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange
          :summary:
   * - :py:obj:`TimeRange <radioskysims.domain.common.models.TimeRange>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange
          :summary:
   * - :py:obj:`Observer <radioskysims.domain.common.models.Observer>`
     -

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`_module_available <radioskysims.domain.common.models._module_available>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models._module_available
          :summary:
   * - :py:obj:`_lazy_import_xarray <radioskysims.domain.common.models._lazy_import_xarray>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_xarray
          :summary:
   * - :py:obj:`_lazy_import_dask <radioskysims.domain.common.models._lazy_import_dask>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_dask
          :summary:
   * - :py:obj:`_lazy_import_astropy_time <radioskysims.domain.common.models._lazy_import_astropy_time>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_astropy_time
          :summary:
   * - :py:obj:`_lazy_import_astropy_location <radioskysims.domain.common.models._lazy_import_astropy_location>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_astropy_location
          :summary:
   * - :py:obj:`_lazy_import_skyfield <radioskysims.domain.common.models._lazy_import_skyfield>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_skyfield
          :summary:
   * - :py:obj:`_lazy_import_pandas <radioskysims.domain.common.models._lazy_import_pandas>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_pandas
          :summary:
   * - :py:obj:`parse_angle <radioskysims.domain.common.models.parse_angle>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models.parse_angle
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`_LAZY_IMPORTS_CACHE <radioskysims.domain.common.models._LAZY_IMPORTS_CACHE>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models._LAZY_IMPORTS_CACHE
          :summary:
   * - :py:obj:`AngleInput <radioskysims.domain.common.models.AngleInput>`
     - .. autodoc2-docstring:: radioskysims.domain.common.models.AngleInput
          :summary:

API
~~~

.. py:data:: _LAZY_IMPORTS_CACHE
   :canonical: radioskysims.domain.common.models._LAZY_IMPORTS_CACHE
   :type: dict[str, typing.Any]
   :value: None

   .. autodoc2-docstring:: radioskysims.domain.common.models._LAZY_IMPORTS_CACHE

.. py:function:: _module_available(name: str) -> bool
   :canonical: radioskysims.domain.common.models._module_available

   .. autodoc2-docstring:: radioskysims.domain.common.models._module_available

.. py:function:: _lazy_import_xarray()
   :canonical: radioskysims.domain.common.models._lazy_import_xarray

   .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_xarray

.. py:function:: _lazy_import_dask()
   :canonical: radioskysims.domain.common.models._lazy_import_dask

   .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_dask

.. py:function:: _lazy_import_astropy_time()
   :canonical: radioskysims.domain.common.models._lazy_import_astropy_time

   .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_astropy_time

.. py:function:: _lazy_import_astropy_location()
   :canonical: radioskysims.domain.common.models._lazy_import_astropy_location

   .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_astropy_location

.. py:function:: _lazy_import_skyfield()
   :canonical: radioskysims.domain.common.models._lazy_import_skyfield

   .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_skyfield

.. py:function:: _lazy_import_pandas()
   :canonical: radioskysims.domain.common.models._lazy_import_pandas

   .. autodoc2-docstring:: radioskysims.domain.common.models._lazy_import_pandas

.. py:class:: FrequencyRange(/, **data: typing.Any)
   :canonical: radioskysims.domain.common.models.FrequencyRange

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.__init__

   .. py:attribute:: min_mhz
      :canonical: radioskysims.domain.common.models.FrequencyRange.min_mhz
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.min_mhz

   .. py:attribute:: max_mhz
      :canonical: radioskysims.domain.common.models.FrequencyRange.max_mhz
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.max_mhz

   .. py:attribute:: resolution_mhz
      :canonical: radioskysims.domain.common.models.FrequencyRange.resolution_mhz
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.resolution_mhz

   .. py:method:: _convert_to_mhz(v)
      :canonical: radioskysims.domain.common.models.FrequencyRange._convert_to_mhz
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange._convert_to_mhz

   .. py:method:: _ensure_resolution()
      :canonical: radioskysims.domain.common.models.FrequencyRange._ensure_resolution

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange._ensure_resolution

   .. py:method:: from_floats(min_val: float, max_val: float, resolution: float | None = None, unit: astropy.units.Unit = u.MHz)
      :canonical: radioskysims.domain.common.models.FrequencyRange.from_floats
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.from_floats

   .. py:method:: from_array(arr: list[float] | numpy.ndarray | list[astropy.units.Quantity])
      :canonical: radioskysims.domain.common.models.FrequencyRange.from_array
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.from_array

   .. py:method:: from_string(s: str, unit: astropy.units.Unit = u.MHz)
      :canonical: radioskysims.domain.common.models.FrequencyRange.from_string
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.from_string

   .. py:method:: from_config(cfg: dict)
      :canonical: radioskysims.domain.common.models.FrequencyRange.from_config
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.from_config

   .. py:property:: value
      :canonical: radioskysims.domain.common.models.FrequencyRange.value
      :type: numpy.ndarray

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.value

   .. py:property:: range
      :canonical: radioskysims.domain.common.models.FrequencyRange.range

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.range

   .. py:property:: resolution
      :canonical: radioskysims.domain.common.models.FrequencyRange.resolution
      :type: float

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.resolution

   .. py:property:: min
      :canonical: radioskysims.domain.common.models.FrequencyRange.min
      :type: float

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.min

   .. py:property:: max
      :canonical: radioskysims.domain.common.models.FrequencyRange.max
      :type: float

      .. autodoc2-docstring:: radioskysims.domain.common.models.FrequencyRange.max

.. py:class:: AngularRange(/, **data: typing.Any)
   :canonical: radioskysims.domain.common.models.AngularRange

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.__init__

   .. py:attribute:: min_rad
      :canonical: radioskysims.domain.common.models.AngularRange.min_rad
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.min_rad

   .. py:attribute:: max_rad
      :canonical: radioskysims.domain.common.models.AngularRange.max_rad
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.max_rad

   .. py:attribute:: resolution_rad
      :canonical: radioskysims.domain.common.models.AngularRange.resolution_rad
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.resolution_rad

   .. py:method:: _convert_to_rad(v)
      :canonical: radioskysims.domain.common.models.AngularRange._convert_to_rad
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange._convert_to_rad

   .. py:method:: _ensure_resolution()
      :canonical: radioskysims.domain.common.models.AngularRange._ensure_resolution

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange._ensure_resolution

   .. py:method:: from_floats(min_val: float, max_val: float, resolution: float | None = None, unit: astropy.units.Unit = u.deg)
      :canonical: radioskysims.domain.common.models.AngularRange.from_floats
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.from_floats

   .. py:method:: from_array(arr: list[float] | numpy.ndarray | list[astropy.units.Quantity])
      :canonical: radioskysims.domain.common.models.AngularRange.from_array
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.from_array

   .. py:method:: from_string(s: str, unit: astropy.units.Unit = u.deg)
      :canonical: radioskysims.domain.common.models.AngularRange.from_string
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.from_string

   .. py:method:: from_degrees(min_val: float, max_val: float, resolution: float | None = None)
      :canonical: radioskysims.domain.common.models.AngularRange.from_degrees
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.from_degrees

   .. py:method:: from_hours(min_val: float, max_val: float, resolution: float | None = None)
      :canonical: radioskysims.domain.common.models.AngularRange.from_hours
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.from_hours

   .. py:method:: from_config(cfg: dict)
      :canonical: radioskysims.domain.common.models.AngularRange.from_config
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.from_config

   .. py:property:: value
      :canonical: radioskysims.domain.common.models.AngularRange.value
      :type: numpy.ndarray

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.value

   .. py:property:: range
      :canonical: radioskysims.domain.common.models.AngularRange.range

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.range

   .. py:property:: angle
      :canonical: radioskysims.domain.common.models.AngularRange.angle
      :type: astropy.coordinates.Angle

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.angle

   .. py:property:: resolution
      :canonical: radioskysims.domain.common.models.AngularRange.resolution
      :type: float

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.resolution

   .. py:property:: min
      :canonical: radioskysims.domain.common.models.AngularRange.min
      :type: float

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.min

   .. py:property:: max
      :canonical: radioskysims.domain.common.models.AngularRange.max
      :type: float

      .. autodoc2-docstring:: radioskysims.domain.common.models.AngularRange.max

   .. py:method:: __repr__() -> str
      :canonical: radioskysims.domain.common.models.AngularRange.__repr__

.. py:class:: TimeRange(/, **data: typing.Any)
   :canonical: radioskysims.domain.common.models.TimeRange

   Bases: :py:obj:`pydantic.BaseModel`

   .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.__init__

   .. py:attribute:: model_config
      :canonical: radioskysims.domain.common.models.TimeRange.model_config
      :value: 'ConfigDict(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.model_config

   .. py:attribute:: start_jd
      :canonical: radioskysims.domain.common.models.TimeRange.start_jd
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.start_jd

   .. py:attribute:: end_jd
      :canonical: radioskysims.domain.common.models.TimeRange.end_jd
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.end_jd

   .. py:attribute:: resolution_sec
      :canonical: radioskysims.domain.common.models.TimeRange.resolution_sec
      :type: float
      :value: 'Field(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.resolution_sec

   .. py:method:: _convert_to_jd(v)
      :canonical: radioskysims.domain.common.models.TimeRange._convert_to_jd
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange._convert_to_jd

   .. py:method:: _convert_resolution(v)
      :canonical: radioskysims.domain.common.models.TimeRange._convert_resolution
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange._convert_resolution

   .. py:method:: _ensure_resolution() -> radioskysims.domain.common.models.TimeRange
      :canonical: radioskysims.domain.common.models.TimeRange._ensure_resolution

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange._ensure_resolution

   .. py:method:: from_astropy(start, end, resolution: float | None = None, unit: astropy.units.Unit = u.s)
      :canonical: radioskysims.domain.common.models.TimeRange.from_astropy
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.from_astropy

   .. py:method:: from_iso(start: str, end: str, resolution: float | None = None, unit: astropy.units.Unit = u.s)
      :canonical: radioskysims.domain.common.models.TimeRange.from_iso
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.from_iso

   .. py:method:: from_jd(start_jd: float, end_jd: float, resolution: float | None = None, unit: astropy.units.Unit = u.s)
      :canonical: radioskysims.domain.common.models.TimeRange.from_jd
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.from_jd

   .. py:method:: from_config(cfg: dict)
      :canonical: radioskysims.domain.common.models.TimeRange.from_config
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.from_config

   .. py:property:: value
      :canonical: radioskysims.domain.common.models.TimeRange.value
      :type: numpy.ndarray

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.value

   .. py:property:: range
      :canonical: radioskysims.domain.common.models.TimeRange.range

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.range

   .. py:method:: to_astropy()
      :canonical: radioskysims.domain.common.models.TimeRange.to_astropy

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.to_astropy

   .. py:method:: to_numpy() -> numpy.ndarray
      :canonical: radioskysims.domain.common.models.TimeRange.to_numpy

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.to_numpy

   .. py:method:: to_pandas()
      :canonical: radioskysims.domain.common.models.TimeRange.to_pandas

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.to_pandas

   .. py:method:: to_skyfield()
      :canonical: radioskysims.domain.common.models.TimeRange.to_skyfield

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.to_skyfield

   .. py:method:: to_tuple()
      :canonical: radioskysims.domain.common.models.TimeRange.to_tuple

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.to_tuple

   .. py:method:: slice(interval_days: float) -> list[radioskysims.domain.common.models.TimeRange]
      :canonical: radioskysims.domain.common.models.TimeRange.slice

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.slice

   .. py:property:: min
      :canonical: radioskysims.domain.common.models.TimeRange.min
      :type: float

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.min

   .. py:property:: max
      :canonical: radioskysims.domain.common.models.TimeRange.max
      :type: float

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.max

   .. py:property:: resolution
      :canonical: radioskysims.domain.common.models.TimeRange.resolution
      :type: float

      .. autodoc2-docstring:: radioskysims.domain.common.models.TimeRange.resolution

   .. py:method:: __repr__() -> str
      :canonical: radioskysims.domain.common.models.TimeRange.__repr__

.. py:data:: AngleInput
   :canonical: radioskysims.domain.common.models.AngleInput
   :value: None

   .. autodoc2-docstring:: radioskysims.domain.common.models.AngleInput

.. py:function:: parse_angle(value: radioskysims.domain.common.models.AngleInput, default_unit=u.deg) -> astropy.coordinates.Angle
   :canonical: radioskysims.domain.common.models.parse_angle

   .. autodoc2-docstring:: radioskysims.domain.common.models.parse_angle

.. py:class:: Observer(/, **data: typing.Any)
   :canonical: radioskysims.domain.common.models.Observer

   Bases: :py:obj:`pydantic.BaseModel`

   .. py:attribute:: model_config
      :canonical: radioskysims.domain.common.models.Observer.model_config
      :value: 'ConfigDict(...)'

      .. autodoc2-docstring:: radioskysims.domain.common.models.Observer.model_config

   .. py:attribute:: lat
      :canonical: radioskysims.domain.common.models.Observer.lat
      :type: radioskysims.domain.common.models.AngleInput
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.common.models.Observer.lat

   .. py:attribute:: lon
      :canonical: radioskysims.domain.common.models.Observer.lon
      :type: radioskysims.domain.common.models.AngleInput
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.common.models.Observer.lon

   .. py:attribute:: height
      :canonical: radioskysims.domain.common.models.Observer.height
      :type: float | astropy.units.Quantity | None
      :value: 0.0

      .. autodoc2-docstring:: radioskysims.domain.common.models.Observer.height

   .. py:attribute:: timeframe
      :canonical: radioskysims.domain.common.models.Observer.timeframe
      :type: radioskysims.domain.common.models.TimeRange
      :value: None

      .. autodoc2-docstring:: radioskysims.domain.common.models.Observer.timeframe

   .. py:method:: validate_lat(v)
      :canonical: radioskysims.domain.common.models.Observer.validate_lat
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.Observer.validate_lat

   .. py:method:: validate_lon(v)
      :canonical: radioskysims.domain.common.models.Observer.validate_lon
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.Observer.validate_lon

   .. py:method:: validate_height(v)
      :canonical: radioskysims.domain.common.models.Observer.validate_height
      :classmethod:

      .. autodoc2-docstring:: radioskysims.domain.common.models.Observer.validate_height

   .. py:method:: to_astropy()
      :canonical: radioskysims.domain.common.models.Observer.to_astropy

      .. autodoc2-docstring:: radioskysims.domain.common.models.Observer.to_astropy

   .. py:method:: to_skyfield()
      :canonical: radioskysims.domain.common.models.Observer.to_skyfield

      .. autodoc2-docstring:: radioskysims.domain.common.models.Observer.to_skyfield
