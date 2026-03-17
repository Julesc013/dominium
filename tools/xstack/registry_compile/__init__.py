"""Deterministic registry compile entry points."""

from __future__ import annotations

from typing import Any

__all__ = ["compile_bundle", "validate_lockfile_payload"]


def compile_bundle(*args: Any, **kwargs: Any):
    from .compiler import compile_bundle as _compile_bundle

    return _compile_bundle(*args, **kwargs)


def validate_lockfile_payload(*args: Any, **kwargs: Any):
    from .lockfile import validate_lockfile_payload as _validate_lockfile_payload

    return _validate_lockfile_payload(*args, **kwargs)

