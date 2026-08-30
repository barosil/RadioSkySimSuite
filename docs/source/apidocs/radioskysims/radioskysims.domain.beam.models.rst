:py:mod:`radioskysims.domain.beam.models`
=========================================

.. py:module:: radioskysims.domain.beam.models

.. autodoc2-docstring:: radioskysims.domain.beam.models
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Beam <radioskysims.domain.beam.models.Beam>`
     - .. autodoc2-docstring:: radioskysims.domain.beam.models.Beam
          :summary:

API
~~~

.. py:class:: Beam(dataset: xarray.Dataset)
   :canonical: radioskysims.domain.beam.models.Beam

   .. autodoc2-docstring:: radioskysims.domain.beam.models.Beam

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.beam.models.Beam.__init__

   .. py:method:: evaluate(*, frequency: xarray.DataArray, angle: xarray.DataArray, polarization: str | None = None) -> xarray.DataArray
      :canonical: radioskysims.domain.beam.models.Beam.evaluate

      .. autodoc2-docstring:: radioskysims.domain.beam.models.Beam.evaluate
