:py:mod:`radioskysims.domain.signal.factory`
============================================

.. py:module:: radioskysims.domain.signal.factory

.. autodoc2-docstring:: radioskysims.domain.signal.factory
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`SignalFactory <radioskysims.domain.signal.factory.SignalFactory>`
     - .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory
          :summary:

API
~~~

.. py:class:: SignalFactory(frequency_range: radioskysims.domain.common.FrequencyRange, signal_repo: radioskysims.infrastructure.db.signal.repository.SignalRepository)
   :canonical: radioskysims.domain.signal.factory.SignalFactory

   .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory.__init__

   .. py:property:: fr
      :canonical: radioskysims.domain.signal.factory.SignalFactory.fr
      :type: radioskysims.domain.common.FrequencyRange

      .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory.fr

   .. py:method:: frequency_grid_hz() -> numpy.typing.NDArray[numpy.floating]
      :canonical: radioskysims.domain.signal.factory.SignalFactory.frequency_grid_hz

      .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory.frequency_grid_hz

   .. py:method:: _generate_prn(length: int) -> numpy.typing.NDArray[numpy.floating]
      :canonical: radioskysims.domain.signal.factory.SignalFactory._generate_prn

      .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory._generate_prn

   .. py:method:: _bpsk(chips: numpy.typing.NDArray[numpy.floating], sps: int) -> numpy.typing.NDArray[numpy.floating]
      :canonical: radioskysims.domain.signal.factory.SignalFactory._bpsk

      .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory._bpsk

   .. py:method:: _qpsk(chips: numpy.typing.NDArray[numpy.floating], sps: int) -> numpy.typing.NDArray[numpy.complexfloating]
      :canonical: radioskysims.domain.signal.factory.SignalFactory._qpsk

      .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory._qpsk

   .. py:method:: _boc(chips: numpy.typing.NDArray[numpy.floating], sps: int, m: int) -> numpy.typing.NDArray[numpy.floating]
      :canonical: radioskysims.domain.signal.factory.SignalFactory._boc

      .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory._boc

   .. py:method:: _cboc(chips: numpy.typing.NDArray[numpy.floating], sps: int) -> numpy.typing.NDArray[numpy.floating]
      :canonical: radioskysims.domain.signal.factory.SignalFactory._cboc

      .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory._cboc

   .. py:method:: _simulate_psd(*, modulation: str, fc_hz: float, prn_len: int, fs_factor: int) -> numpy.ndarray
      :canonical: radioskysims.domain.signal.factory.SignalFactory._simulate_psd

      .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory._simulate_psd

   .. py:method:: _build(*, modulation: str, fc_hz: float, prn_len: int = 1023, fs_factor: int = 10)
      :canonical: radioskysims.domain.signal.factory.SignalFactory._build

      .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory._build

   .. py:method:: build(sats=None)
      :canonical: radioskysims.domain.signal.factory.SignalFactory.build

      .. autodoc2-docstring:: radioskysims.domain.signal.factory.SignalFactory.build
