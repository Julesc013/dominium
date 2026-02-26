"""Renderer backends consuming RenderModel artifacts only."""

from .null_renderer import render_null_snapshot

__all__ = ["render_null_snapshot"]
