"""Registry-backed AppShell command dispatch with lazy exports."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "dispatch_registered_command": ("appshell.commands.command_engine", "dispatch_registered_command"),
}

__all__ = sorted(_EXPORTS.keys())


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if not target:
        raise AttributeError("module 'appshell.commands' has no attribute {!r}".format(name))
    module_name, attr_name = target
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(__all__))
