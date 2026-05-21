"""Transitional compatibility shims for convergence without semantic drift."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "FLAG_SHIM_ROWS": ("runtime.compatibility.shims.flag_shims", "FLAG_SHIM_ROWS"),
    "FLAG_WARNING_KEY": ("runtime.compatibility.shims.flag_shims", "FLAG_WARNING_KEY"),
    "apply_flag_shims": ("runtime.compatibility.shims.flag_shims", "apply_flag_shims"),
    "legacy_flag_rows": ("runtime.compatibility.shims.flag_shims", "legacy_flag_rows"),
    "PATH_SHIM_ROWS": ("runtime.compatibility.shims.path_shims", "PATH_SHIM_ROWS"),
    "PATH_SHIM_WARNING_KEY": ("runtime.compatibility.shims.path_shims", "PATH_SHIM_WARNING_KEY"),
    "path_shim_rows": ("runtime.compatibility.shims.path_shims", "path_shim_rows"),
    "redirect_legacy_path": ("runtime.compatibility.shims.path_shims", "redirect_legacy_path"),
    "TOOL_SHIM_ROWS": ("runtime.compatibility.shims.tool_shims", "TOOL_SHIM_ROWS"),
    "TOOL_WARNING_KEY": ("runtime.compatibility.shims.tool_shims", "TOOL_WARNING_KEY"),
    "emit_legacy_tool_warning": ("runtime.compatibility.shims.tool_shims", "emit_legacy_tool_warning"),
    "tool_shim_rows": ("runtime.compatibility.shims.tool_shims", "tool_shim_rows"),
}


def __getattr__(name: str):
    target = _EXPORTS.get(str(name))
    if target is None:
        raise AttributeError("module 'runtime.compatibility.shims' has no attribute '{}'".format(str(name)))
    module_name, attr_name = target
    value = getattr(import_module(module_name), attr_name)
    globals()[str(name)] = value
    return value


__all__ = sorted(_EXPORTS.keys())
