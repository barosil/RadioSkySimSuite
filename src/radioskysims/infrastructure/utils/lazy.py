# infrastructure/utils/lazy.py
from __future__ import annotations

from functools import lru_cache
from importlib import import_module


@lru_cache(None)
def lazy_import(path: str):
    return import_module(path)
