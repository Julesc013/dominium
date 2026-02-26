"""Renderer backends consuming RenderModel artifacts only."""

from .null_renderer import render_null_snapshot
from .software_renderer import render_software_snapshot

__all__ = ["render_null_snapshot", "render_software_snapshot"]
