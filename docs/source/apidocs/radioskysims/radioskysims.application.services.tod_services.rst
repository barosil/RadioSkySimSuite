:py:mod:`radioskysims.application.services.tod_services`
========================================================

.. py:module:: radioskysims.application.services.tod_services

.. autodoc2-docstring:: radioskysims.application.services.tod_services
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`TODService <radioskysims.application.services.tod_services.TODService>`
     - .. autodoc2-docstring:: radioskysims.application.services.tod_services.TODService
          :summary:

API
~~~

.. py:class:: TODService(*, simulator: radioskysims.domain.tod.TODSimulator)
   :canonical: radioskysims.application.services.tod_services.TODService

   .. autodoc2-docstring:: radioskysims.application.services.tod_services.TODService

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.application.services.tod_services.TODService.__init__

   .. py:method:: run(*, satellites: collections.abc.Iterable[radioskysims.domain.satellite.Satellite]) -> xarray.Dataset
      :canonical: radioskysims.application.services.tod_services.TODService.run

      .. autodoc2-docstring:: radioskysims.application.services.tod_services.TODService.run
