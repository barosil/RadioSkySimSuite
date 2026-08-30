:py:mod:`radioskysims.paths`
============================

.. py:module:: radioskysims.paths

.. autodoc2-docstring:: radioskysims.paths
   :allowtitles:

Module Contents
---------------

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`get_project_root <radioskysims.paths.get_project_root>`
     - .. autodoc2-docstring:: radioskysims.paths.get_project_root
          :summary:
   * - :py:obj:`load_config <radioskysims.paths.load_config>`
     - .. autodoc2-docstring:: radioskysims.paths.load_config
          :summary:
   * - :py:obj:`load_env <radioskysims.paths.load_env>`
     - .. autodoc2-docstring:: radioskysims.paths.load_env
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`ROOT <radioskysims.paths.ROOT>`
     - .. autodoc2-docstring:: radioskysims.paths.ROOT
          :summary:
   * - :py:obj:`SRC_DIR <radioskysims.paths.SRC_DIR>`
     - .. autodoc2-docstring:: radioskysims.paths.SRC_DIR
          :summary:
   * - :py:obj:`DATA_DIR <radioskysims.paths.DATA_DIR>`
     - .. autodoc2-docstring:: radioskysims.paths.DATA_DIR
          :summary:
   * - :py:obj:`AUX_DIR <radioskysims.paths.AUX_DIR>`
     - .. autodoc2-docstring:: radioskysims.paths.AUX_DIR
          :summary:
   * - :py:obj:`CATALOG_DIR <radioskysims.paths.CATALOG_DIR>`
     - .. autodoc2-docstring:: radioskysims.paths.CATALOG_DIR
          :summary:
   * - :py:obj:`SATELLITE_DIR <radioskysims.paths.SATELLITE_DIR>`
     - .. autodoc2-docstring:: radioskysims.paths.SATELLITE_DIR
          :summary:
   * - :py:obj:`SKYMAP_DIR <radioskysims.paths.SKYMAP_DIR>`
     - .. autodoc2-docstring:: radioskysims.paths.SKYMAP_DIR
          :summary:
   * - :py:obj:`TEMP_DIR <radioskysims.paths.TEMP_DIR>`
     - .. autodoc2-docstring:: radioskysims.paths.TEMP_DIR
          :summary:
   * - :py:obj:`LOG_DIR <radioskysims.paths.LOG_DIR>`
     - .. autodoc2-docstring:: radioskysims.paths.LOG_DIR
          :summary:
   * - :py:obj:`NOTEBOOKS_DIR <radioskysims.paths.NOTEBOOKS_DIR>`
     - .. autodoc2-docstring:: radioskysims.paths.NOTEBOOKS_DIR
          :summary:
   * - :py:obj:`CONFIG_FILE <radioskysims.paths.CONFIG_FILE>`
     - .. autodoc2-docstring:: radioskysims.paths.CONFIG_FILE
          :summary:
   * - :py:obj:`ENV_FILE <radioskysims.paths.ENV_FILE>`
     - .. autodoc2-docstring:: radioskysims.paths.ENV_FILE
          :summary:

API
~~~

.. py:function:: get_project_root() -> pathlib.Path
   :canonical: radioskysims.paths.get_project_root

   .. autodoc2-docstring:: radioskysims.paths.get_project_root

.. py:data:: ROOT
   :canonical: radioskysims.paths.ROOT
   :value: 'get_project_root(...)'

   .. autodoc2-docstring:: radioskysims.paths.ROOT

.. py:data:: SRC_DIR
   :canonical: radioskysims.paths.SRC_DIR
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.SRC_DIR

.. py:data:: DATA_DIR
   :canonical: radioskysims.paths.DATA_DIR
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.DATA_DIR

.. py:data:: AUX_DIR
   :canonical: radioskysims.paths.AUX_DIR
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.AUX_DIR

.. py:data:: CATALOG_DIR
   :canonical: radioskysims.paths.CATALOG_DIR
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.CATALOG_DIR

.. py:data:: SATELLITE_DIR
   :canonical: radioskysims.paths.SATELLITE_DIR
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.SATELLITE_DIR

.. py:data:: SKYMAP_DIR
   :canonical: radioskysims.paths.SKYMAP_DIR
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.SKYMAP_DIR

.. py:data:: TEMP_DIR
   :canonical: radioskysims.paths.TEMP_DIR
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.TEMP_DIR

.. py:data:: LOG_DIR
   :canonical: radioskysims.paths.LOG_DIR
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.LOG_DIR

.. py:data:: NOTEBOOKS_DIR
   :canonical: radioskysims.paths.NOTEBOOKS_DIR
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.NOTEBOOKS_DIR

.. py:data:: CONFIG_FILE
   :canonical: radioskysims.paths.CONFIG_FILE
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.CONFIG_FILE

.. py:data:: ENV_FILE
   :canonical: radioskysims.paths.ENV_FILE
   :value: None

   .. autodoc2-docstring:: radioskysims.paths.ENV_FILE

.. py:function:: load_config(path: pathlib.Path = CONFIG_FILE) -> dict
   :canonical: radioskysims.paths.load_config

   .. autodoc2-docstring:: radioskysims.paths.load_config

.. py:function:: load_env(path: pathlib.Path = ENV_FILE) -> None
   :canonical: radioskysims.paths.load_env

   .. autodoc2-docstring:: radioskysims.paths.load_env
