"""Shared OBSERVABILITY-0 TestX helpers."""

from __future__ import annotations

import os
import tempfile

from tools.meta.observability_common import build_observability_report


_CACHE: dict[str, dict] = {}


def build_report(repo_root: str) -> dict:
    token = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    cached = dict(_CACHE.get(token) or {})
    if cached:
        return cached
    report = build_observability_report(token)
    _CACHE[token] = dict(report)
    return dict(report)


def make_temp_dir(prefix: str = "obs0_") -> str:
    return tempfile.mkdtemp(prefix=prefix)


__all__ = ["build_report", "make_temp_dir"]
