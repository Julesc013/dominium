"""Unified tool surface exports."""

from .tool_surface_adapter import (
    DOM_PRODUCT_ID,
    TOOL_REFERENCE_PATH,
    TOOL_SURFACE_FINAL_PATH,
    TOOL_SURFACE_MAP_PATH,
    build_tool_surface_report,
    build_tool_surface_rows,
    execute_tool_surface_subprocess,
    format_tool_surface_area_help,
    format_tool_surface_root_help,
    sync_command_registry_with_tool_surface,
    tool_surface_row_from_command,
    tool_surface_violations,
    write_tool_surface_outputs,
)

__all__ = [
    "DOM_PRODUCT_ID",
    "TOOL_REFERENCE_PATH",
    "TOOL_SURFACE_FINAL_PATH",
    "TOOL_SURFACE_MAP_PATH",
    "build_tool_surface_report",
    "build_tool_surface_rows",
    "execute_tool_surface_subprocess",
    "format_tool_surface_area_help",
    "format_tool_surface_root_help",
    "sync_command_registry_with_tool_surface",
    "tool_surface_row_from_command",
    "tool_surface_violations",
    "write_tool_surface_outputs",
]
