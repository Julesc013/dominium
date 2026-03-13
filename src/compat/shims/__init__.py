"""Transitional compatibility shims for convergence without semantic drift."""

from .flag_shims import FLAG_SHIM_ROWS, FLAG_WARNING_KEY, apply_flag_shims, legacy_flag_rows
from .path_shims import PATH_SHIM_ROWS, PATH_SHIM_WARNING_KEY, path_shim_rows, redirect_legacy_path
from .tool_shims import TOOL_SHIM_ROWS, TOOL_WARNING_KEY, emit_legacy_tool_warning, tool_shim_rows
from .validation_shims import VALIDATION_SHIM_ROWS, VALIDATION_WARNING_KEY, run_legacy_validate_all, validation_shim_rows

__all__ = [
    "FLAG_SHIM_ROWS",
    "FLAG_WARNING_KEY",
    "PATH_SHIM_ROWS",
    "PATH_SHIM_WARNING_KEY",
    "TOOL_SHIM_ROWS",
    "TOOL_WARNING_KEY",
    "VALIDATION_SHIM_ROWS",
    "VALIDATION_WARNING_KEY",
    "apply_flag_shims",
    "emit_legacy_tool_warning",
    "legacy_flag_rows",
    "path_shim_rows",
    "redirect_legacy_path",
    "run_legacy_validate_all",
    "tool_shim_rows",
    "validation_shim_rows",
]
