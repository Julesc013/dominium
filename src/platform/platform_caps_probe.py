"""Backward-compatible wrapper around the canonical platform probe."""

from __future__ import annotations

from typing import Mapping

from .platform_probe import probe_platform_descriptor


def probe_platform_caps(
    repo_root: str,
    *,
    product_id: str,
    platform_id: str = "",
    env: Mapping[str, object] | None = None,
    stdin_tty: object = None,
    stdout_tty: object = None,
    stderr_tty: object = None,
    gui_available: object = None,
    native_available: object = None,
    rendered_available: object = None,
    ncurses_available: object = None,
    console_window_present: object = None,
    cocoa_available: object = None,
) -> dict:
    return probe_platform_descriptor(
        repo_root,
        product_id=product_id,
        platform_id=platform_id,
        env=env,
        stdin_tty=stdin_tty,
        stdout_tty=stdout_tty,
        stderr_tty=stderr_tty,
        gui_available=gui_available,
        native_available=native_available,
        rendered_available=rendered_available,
        ncurses_available=ncurses_available,
        console_window_present=console_window_present,
        cocoa_available=cocoa_available,
    )


__all__ = ["probe_platform_caps"]
