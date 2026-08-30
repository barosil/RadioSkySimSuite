:py:mod:`radioskysims.infrastructure.external.satellite_downloader`
===================================================================

.. py:module:: radioskysims.infrastructure.external.satellite_downloader

.. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`CelestrakClient <radioskysims.infrastructure.external.satellite_downloader.CelestrakClient>`
     - .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.CelestrakClient
          :summary:
   * - :py:obj:`QueryResult <radioskysims.infrastructure.external.satellite_downloader.QueryResult>`
     - .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.QueryResult
          :summary:
   * - :py:obj:`SpaceTrackClient <radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient>`
     - .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`logger <radioskysims.infrastructure.external.satellite_downloader.logger>`
     - .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.logger
          :summary:
   * - :py:obj:`settings <radioskysims.infrastructure.external.satellite_downloader.settings>`
     - .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.settings
          :summary:

API
~~~

.. py:data:: logger
   :canonical: radioskysims.infrastructure.external.satellite_downloader.logger
   :value: 'getLogger(...)'

   .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.logger

.. py:class:: CelestrakClient()
   :canonical: radioskysims.infrastructure.external.satellite_downloader.CelestrakClient

   .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.CelestrakClient

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.CelestrakClient.__init__

   .. py:method:: fetch_sats(url: str | None = None)
      :canonical: radioskysims.infrastructure.external.satellite_downloader.CelestrakClient.fetch_sats

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.CelestrakClient.fetch_sats

.. py:class:: QueryResult
   :canonical: radioskysims.infrastructure.external.satellite_downloader.QueryResult

   .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.QueryResult

   .. py:attribute:: norad_id
      :canonical: radioskysims.infrastructure.external.satellite_downloader.QueryResult.norad_id
      :type: int
      :value: None

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.QueryResult.norad_id

   .. py:attribute:: payload
      :canonical: radioskysims.infrastructure.external.satellite_downloader.QueryResult.payload
      :type: dict[str, typing.Any]
      :value: None

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.QueryResult.payload

.. py:data:: settings
   :canonical: radioskysims.infrastructure.external.satellite_downloader.settings
   :value: 'load_config(...)'

   .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.settings

.. py:class:: SpaceTrackClient(epoch: datetime.datetime | None = None)
   :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient

   .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient

   .. rubric:: Initialization

   .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.__init__

   .. py:attribute:: BASE_URL
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.BASE_URL
      :value: 'https://www.space-track.org'

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.BASE_URL

   .. py:attribute:: API_URL
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.API_URL
      :value: None

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.API_URL

   .. py:attribute:: _queried_norad_ids
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._queried_norad_ids
      :type: set[int]
      :value: 'set(...)'

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._queried_norad_ids

   .. py:attribute:: _registry_day
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._registry_day
      :type: datetime.date
      :value: 'today(...)'

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._registry_day

   .. py:attribute:: _registry_lock_thread
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._registry_lock_thread
      :value: 'Lock(...)'

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._registry_lock_thread

   .. py:attribute:: _registry_lock_async
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._registry_lock_async
      :value: 'Lock(...)'

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._registry_lock_async

   .. py:method:: _set_epoch() -> None
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._set_epoch

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._set_epoch

   .. py:method:: _rotate_registry_if_needed() -> None
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._rotate_registry_if_needed
      :classmethod:

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._rotate_registry_if_needed

   .. py:method:: _rotate_registry_if_needed_async() -> None
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._rotate_registry_if_needed_async
      :async:
      :classmethod:

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._rotate_registry_if_needed_async

   .. py:method:: filter_new_sync(ids: collections.abc.Iterable[int]) -> list[int]
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.filter_new_sync
      :classmethod:

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.filter_new_sync

   .. py:method:: filter_new_async(ids: collections.abc.Iterable[int]) -> list[int]
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.filter_new_async
      :async:
      :classmethod:

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.filter_new_async

   .. py:method:: _build_queries(norad_ids: list[int], decay: str | None = None) -> list[str]
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._build_queries

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._build_queries

   .. py:method:: _prune_rate_windows() -> None
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._prune_rate_windows

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._prune_rate_windows

   .. py:method:: _wait_rate_limit_async() -> None
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._wait_rate_limit_async
      :async:

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._wait_rate_limit_async

   .. py:method:: _wait_rate_limit_sync() -> None
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._wait_rate_limit_sync

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._wait_rate_limit_sync

   .. py:method:: _do_query_async(client: httpx.AsyncClient, query: str) -> list[dict[str, typing.Any]]
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._do_query_async
      :async:

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._do_query_async

   .. py:method:: _do_query_sync(client: httpx.Client, query: str) -> list[dict[str, typing.Any]]
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._do_query_sync

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._do_query_sync

   .. py:method:: fetch_elements(norad_ids: collections.abc.Iterable[int]) -> pandas.DataFrame
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.fetch_elements
      :async:

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.fetch_elements

   .. py:method:: fetch_elements_sync(norad_ids: collections.abc.Iterable[int]) -> pandas.DataFrame
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.fetch_elements_sync

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.fetch_elements_sync

   .. py:method:: _to_dataframe(data: list[dict[str, typing.Any]]) -> pandas.DataFrame
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._to_dataframe

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient._to_dataframe

   .. py:method:: clear_registry() -> None
      :canonical: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.clear_registry
      :classmethod:

      .. autodoc2-docstring:: radioskysims.infrastructure.external.satellite_downloader.SpaceTrackClient.clear_registry
