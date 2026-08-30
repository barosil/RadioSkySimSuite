:py:mod:`radioskysims.domain.satellite.selector`
================================================

.. py:module:: radioskysims.domain.satellite.selector

.. autodoc2-docstring:: radioskysims.domain.satellite.selector
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`TLESelector <radioskysims.domain.satellite.selector.TLESelector>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.selector.TLESelector
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`logger <radioskysims.domain.satellite.selector.logger>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.selector.logger
          :summary:

API
~~~

.. py:data:: logger
   :canonical: radioskysims.domain.satellite.selector.logger
   :value: 'getLogger(...)'

   .. autodoc2-docstring:: radioskysims.domain.satellite.selector.logger

.. py:class:: TLESelector
   :canonical: radioskysims.domain.satellite.selector.TLESelector

   .. autodoc2-docstring:: radioskysims.domain.satellite.selector.TLESelector

   .. py:method:: select(satids: list[radioskysims.infrastructure.db.satellite.models.SatID], epoch_jd: float) -> list[dict]
      :canonical: radioskysims.domain.satellite.selector.TLESelector.select
      :staticmethod:

      .. autodoc2-docstring:: radioskysims.domain.satellite.selector.TLESelector.select
