:py:mod:`domain.beam.beam`
==========================

.. py:module:: domain.beam.beam

.. autodoc2-docstring:: domain.beam.beam
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Beam <domain.beam.beam.Beam>`
     - .. autodoc2-docstring:: domain.beam.beam.Beam
          :summary:

API
~~~

.. py:class:: Beam(name: str, pattern: numpy.ndarray, frequency_range: typing.Optional[typing.Tuple[float, float]] = None, angular_resolution: typing.Optional[float] = None, is_normalized: bool = False)
   :canonical: domain.beam.beam.Beam

   Bases: :py:obj:`sqlmodel.SQLModel`

   .. autodoc2-docstring:: domain.beam.beam.Beam

   .. rubric:: Initialization

   .. autodoc2-docstring:: domain.beam.beam.Beam.__init__

   .. py:attribute:: id
      :canonical: domain.beam.beam.Beam.id
      :type: int
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.beam.beam.Beam.id

   .. py:attribute:: name
      :canonical: domain.beam.beam.Beam.name
      :type: str
      :value: None

      .. autodoc2-docstring:: domain.beam.beam.Beam.name

   .. py:attribute:: frequency_range
      :canonical: domain.beam.beam.Beam.frequency_range
      :type: typing.Optional[str]
      :value: 'Field(...)'

      .. autodoc2-docstring:: domain.beam.beam.Beam.frequency_range

   .. py:attribute:: angular_resolution
      :canonical: domain.beam.beam.Beam.angular_resolution
      :type: typing.Optional[float]
      :value: None

      .. autodoc2-docstring:: domain.beam.beam.Beam.angular_resolution

   .. py:attribute:: pattern
      :canonical: domain.beam.beam.Beam.pattern
      :type: numpy.ndarray
      :value: None

      .. autodoc2-docstring:: domain.beam.beam.Beam.pattern

   .. py:attribute:: fwhm
      :canonical: domain.beam.beam.Beam.fwhm
      :type: float
      :value: None

      .. autodoc2-docstring:: domain.beam.beam.Beam.fwhm

   .. py:attribute:: gain
      :canonical: domain.beam.beam.Beam.gain
      :type: float
      :value: None

      .. autodoc2-docstring:: domain.beam.beam.Beam.gain

   .. py:class:: Config
      :canonical: domain.beam.beam.Beam.Config

      .. autodoc2-docstring:: domain.beam.beam.Beam.Config

      .. py:attribute:: arbitrary_types_allowed
         :canonical: domain.beam.beam.Beam.Config.arbitrary_types_allowed
         :value: True

         .. autodoc2-docstring:: domain.beam.beam.Beam.Config.arbitrary_types_allowed

   .. py:method:: get_frequency_range()
      :canonical: domain.beam.beam.Beam.get_frequency_range

      .. autodoc2-docstring:: domain.beam.beam.Beam.get_frequency_range

   .. py:method:: _interpolate_pattern(pattern: numpy.ndarray, angular_resolution: float) -> numpy.ndarray
      :canonical: domain.beam.beam.Beam._interpolate_pattern

      .. autodoc2-docstring:: domain.beam.beam.Beam._interpolate_pattern

   .. py:method:: _normalize(pattern: numpy.ndarray) -> numpy.ndarray
      :canonical: domain.beam.beam.Beam._normalize

      .. autodoc2-docstring:: domain.beam.beam.Beam._normalize

   .. py:method:: _calculate_fwhm() -> float
      :canonical: domain.beam.beam.Beam._calculate_fwhm

      .. autodoc2-docstring:: domain.beam.beam.Beam._calculate_fwhm

   .. py:method:: _calculate_gain() -> float
      :canonical: domain.beam.beam.Beam._calculate_gain

      .. autodoc2-docstring:: domain.beam.beam.Beam._calculate_gain
