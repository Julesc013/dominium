"""Helpers for APPSHELL-PLATFORM-1 TestX coverage."""

from __future__ import annotations

from tools.release.ui_mode_resolution_common import build_test_probe, selection_for_product


def probe(
    repo_root: str,
    *,
    product_id: str,
    platform_id: str = "linux",
    tty: bool,
    gui: bool,
    native: bool,
    rendered: bool,
    tui: bool,
) -> dict:
    return build_test_probe(
        repo_root,
        product_id=product_id,
        platform_id=platform_id,
        tty=tty,
        gui=gui,
        native=native,
        rendered=rendered,
        tui=tui,
    )


def selection(
    repo_root: str,
    *,
    product_id: str,
    requested_mode_id: str = "",
    mode_source: str = "default",
    mode_requested: bool | None = None,
    probe_payload: dict,
) -> dict:
    return selection_for_product(
        repo_root,
        product_id=product_id,
        requested_mode_id=requested_mode_id,
        mode_source=mode_source,
        mode_requested=mode_requested,
        probe=probe_payload,
    )
