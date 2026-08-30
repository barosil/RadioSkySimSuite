:py:mod:`radioskysims.domain.satellite.chunks`
==============================================

.. py:module:: radioskysims.domain.satellite.chunks

.. autodoc2-docstring:: radioskysims.domain.satellite.chunks
   :allowtitles:

Module Contents
---------------

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`_bytes_per_element <radioskysims.domain.satellite.chunks._bytes_per_element>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.chunks._bytes_per_element
          :summary:
   * - :py:obj:`_estimate_chunk_bytes <radioskysims.domain.satellite.chunks._estimate_chunk_bytes>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.chunks._estimate_chunk_bytes
          :summary:
   * - :py:obj:`_group_satellites_by_constellation <radioskysims.domain.satellite.chunks._group_satellites_by_constellation>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.chunks._group_satellites_by_constellation
          :summary:
   * - :py:obj:`set_chunks <radioskysims.domain.satellite.chunks.set_chunks>`
     - .. autodoc2-docstring:: radioskysims.domain.satellite.chunks.set_chunks
          :summary:

API
~~~

.. py:function:: _bytes_per_element(dtype: numpy.dtype) -> int
   :canonical: radioskysims.domain.satellite.chunks._bytes_per_element

   .. autodoc2-docstring:: radioskysims.domain.satellite.chunks._bytes_per_element

.. py:function:: _estimate_chunk_bytes(shape: tuple[int, ...], dtype: numpy.dtype) -> int
   :canonical: radioskysims.domain.satellite.chunks._estimate_chunk_bytes

   .. autodoc2-docstring:: radioskysims.domain.satellite.chunks._estimate_chunk_bytes

.. py:function:: _group_satellites_by_constellation(ds: xarray.Dataset)
   :canonical: radioskysims.domain.satellite.chunks._group_satellites_by_constellation

   .. autodoc2-docstring:: radioskysims.domain.satellite.chunks._group_satellites_by_constellation

.. py:function:: set_chunks(ds: xarray.Dataset, var: str = 'positions', *, max_chunk_mb: float | None = None, allow_merge_constellations: bool = True) -> xarray.Dataset
   :canonical: radioskysims.domain.satellite.chunks.set_chunks

   .. autodoc2-docstring:: radioskysims.domain.satellite.chunks.set_chunks
