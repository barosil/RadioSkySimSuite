:py:mod:`radioskysims.domain.tod.simulator`
===========================================

.. py:module:: radioskysims.domain.tod.simulator

.. autodoc2-docstring:: radioskysims.domain.tod.simulator
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`TODSimulator <radioskysims.domain.tod.simulator.TODSimulator>`
     - .. autodoc2-docstring:: radioskysims.domain.tod.simulator.TODSimulator
          :summary:

API
~~~

.. py:class:: TODSimulator(*, beam, gain: float)
   :canonical: radioskysims.domain.tod.simulator.TODSimulator

   .. autodoc2-docstring:: radioskysims.domain.tod.simulator.TODSimulator

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.domain.tod.simulator.TODSimulator.__init__

   .. py:method:: simulate(*, sat, sky: xarray.Dataset | None = None, noise: xarray.Dataset | None = None) -> xarray.Dataset
      :canonical: radioskysims.domain.tod.simulator.TODSimulator.simulate

      .. autodoc2-docstring:: radioskysims.domain.tod.simulator.TODSimulator.simulate
