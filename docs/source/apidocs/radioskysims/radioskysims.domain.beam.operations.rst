:py:mod:`radioskysims.domain.beam.operations`
=============================================

.. py:module:: radioskysims.domain.beam.operations

.. autodoc2-docstring:: radioskysims.domain.beam.operations
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`BeamOps <radioskysims.domain.beam.operations.BeamOps>`
     - .. autodoc2-docstring:: radioskysims.domain.beam.operations.BeamOps
          :summary:

API
~~~

.. py:class:: BeamOps
   :canonical: radioskysims.domain.beam.operations.BeamOps

   .. autodoc2-docstring:: radioskysims.domain.beam.operations.BeamOps

   .. py:method:: normalize(beam: radioskysims.domain.beam.models.Beam) -> radioskysims.domain.beam.models.Beam
      :canonical: radioskysims.domain.beam.operations.BeamOps.normalize
      :staticmethod:

      .. autodoc2-docstring:: radioskysims.domain.beam.operations.BeamOps.normalize

   .. py:method:: slice_angle(beam: radioskysims.domain.beam.models.Beam, amin: float, amax: float) -> radioskysims.domain.beam.models.Beam
      :canonical: radioskysims.domain.beam.operations.BeamOps.slice_angle
      :staticmethod:

      .. autodoc2-docstring:: radioskysims.domain.beam.operations.BeamOps.slice_angle

   .. py:method:: interpolate_angle(beam: radioskysims.domain.beam.models.Beam, new_angles: numpy.typing.NDArray[numpy.floating]) -> radioskysims.domain.beam.models.Beam
      :canonical: radioskysims.domain.beam.operations.BeamOps.interpolate_angle
      :staticmethod:

      .. autodoc2-docstring:: radioskysims.domain.beam.operations.BeamOps.interpolate_angle

   .. py:method:: symmetrize(beam: radioskysims.domain.beam.models.Beam) -> radioskysims.domain.beam.models.Beam
      :canonical: radioskysims.domain.beam.operations.BeamOps.symmetrize
      :staticmethod:

      .. autodoc2-docstring:: radioskysims.domain.beam.operations.BeamOps.symmetrize
