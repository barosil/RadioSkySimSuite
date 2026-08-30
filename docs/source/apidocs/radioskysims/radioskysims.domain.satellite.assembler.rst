:py:mod:`radioskysims.domain.satellite.assembler`
=================================================

.. py:module:: radioskysims.domain.satellite.assembler

.. autodoc2-docstring:: radioskysims.domain.satellite.assembler
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`SatelliteAssembler <radioskysims.domain.satellite.assembler.SatelliteAssembler>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.assembler.SatelliteAssembler
          :summary:

API
~~~

.. py:class:: SatelliteAssembler(signal_factory, track_factory)
   :canonical: radioskysims.domain.satellite.assembler.SatelliteAssembler

   .. autodoc2-docstring:: radioskysims.domain.satellite.assembler.SatelliteAssembler

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.satellite.assembler.SatelliteAssembler.__init__

   .. py:method:: assemble(sats, recalculate=False, sats_assembled=None, frequency_range=None) -> radioskysims.domain.satellite.models.SatelliteAssembled
      :canonical: radioskysims.domain.satellite.assembler.SatelliteAssembler.assemble

      .. autodoc2-docstring:: radioskysims.domain.satellite.assembler.SatelliteAssembler.assemble

   .. py:method:: _frequency_coord() -> xarray.DataArray
      :canonical: radioskysims.domain.satellite.assembler.SatelliteAssembler._frequency_coord

      .. autodoc2-docstring:: radioskysims.domain.satellite.assembler.SatelliteAssembler._frequency_coord
