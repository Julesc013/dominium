"""Shared deterministic product shell bootstrap with lazy exports."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "appshell_main": ("src.appshell.bootstrap", "appshell_main"),
}

__all__ = sorted(_EXPORTS.keys())


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if not target:
        raise AttributeError("module 'src.appshell' has no attribute {!r}".format(name))
    module_name, attr_name = target
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(__all__))
