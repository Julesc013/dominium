"""Helpers for TOOL-SURFACE-0 TestX coverage."""

from __future__ import annotations

from src.appshell.commands.command_engine import dispatch_registered_command
from src.tools import DOM_PRODUCT_ID, build_tool_surface_report


def build_report(repo_root: str) -> dict:
    return build_tool_surface_report(repo_root)


def dispatch_dom(repo_root: str, tokens: list[str]) -> dict:
    return dispatch_registered_command(
        repo_root,
        product_id=DOM_PRODUCT_ID,
        mode_id="cli",
        command_tokens=tokens,
    )
