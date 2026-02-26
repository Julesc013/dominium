"""Renderer backends consuming RenderModel artifacts only."""

from .hw_renderer_gl import render_hardware_gl_snapshot
from .null_renderer import render_null_snapshot
from .software_renderer import render_software_snapshot

__all__ = [
    "render_hardware_gl_snapshot",
    "render_null_snapshot",
    "render_software_snapshot",
]
