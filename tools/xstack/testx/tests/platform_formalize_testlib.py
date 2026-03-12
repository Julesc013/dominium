"""Helpers for PLATFORM-FORMALIZE-0 TestX coverage."""

from __future__ import annotations

import sys
from typing import Mapping


def ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def load_registry(repo_root: str) -> dict:
    ensure_repo_root(repo_root)
    from src.platform import load_platform_capability_registry

    payload, error = load_platform_capability_registry(repo_root)
    if error:
        raise ValueError(error)
    return dict(payload)


def probe(
    repo_root: str,
    *,
    product_id: str,
    platform_id: str,
    tty: bool,
    gui: bool,
    native: bool | None = None,
    rendered: bool | None = None,
    tui: bool | None = None,
) -> dict:
    ensure_repo_root(repo_root)
    from src.platform import probe_platform_descriptor

    return probe_platform_descriptor(
        repo_root,
        product_id=product_id,
        platform_id=platform_id,
        stdin_tty=tty,
        stdout_tty=tty,
        stderr_tty=tty,
        gui_available=gui,
        native_available=native,
        rendered_available=rendered,
        ncurses_available=tui,
    )


def default_descriptor(
    repo_root: str,
    *,
    product_id: str,
    product_version: str,
    platform_id: str,
    platform_probe: Mapping[str, object] | None = None,
) -> dict:
    ensure_repo_root(repo_root)
    from src.compat import build_default_endpoint_descriptor

    return build_default_endpoint_descriptor(
        repo_root,
        product_id=product_id,
        product_version=product_version,
        platform_id=platform_id,
        platform_descriptor_override=dict(platform_probe or {}),
    )


def mode_selection(
    repo_root: str,
    *,
    product_id: str,
    requested_mode_id: str,
    probe_payload: Mapping[str, object],
) -> dict:
    ensure_repo_root(repo_root)
    from tools.release.ui_mode_resolution_common import selection_for_product

    return selection_for_product(
        repo_root,
        product_id=product_id,
        requested_mode_id=requested_mode_id,
        mode_source="explicit",
        mode_requested=True,
        probe=dict(probe_payload),
    )
