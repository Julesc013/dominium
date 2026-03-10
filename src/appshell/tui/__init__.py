"""Shared AppShell TUI surfaces."""

from .tui_engine import (
    attach_ipc_session_to_surface,
    build_tui_surface,
    detach_ipc_session_from_surface,
    execute_console_session_command,
    load_tui_layout_registry,
    load_tui_panel_registry,
    refresh_ipc_sessions_in_surface,
    render_tui_text,
    run_tui_mode,
)

__all__ = [
    "attach_ipc_session_to_surface",
    "build_tui_surface",
    "detach_ipc_session_from_surface",
    "execute_console_session_command",
    "load_tui_layout_registry",
    "load_tui_panel_registry",
    "refresh_ipc_sessions_in_surface",
    "render_tui_text",
    "run_tui_mode",
]
