"""Renderer backends consuming RenderModel artifacts only."""

from .hw_renderer_gl import render_hardware_gl_snapshot
from .model_api import (
    build_render_model,
    capture_render_snapshot,
    load_render_model_from_artifact,
    resolve_representation,
)
from runtime.render.providers.null.null_renderer import render_null_snapshot
from runtime.render.providers.software.software_renderer import render_software_snapshot

__all__ = [
    "build_render_model",
    "capture_render_snapshot",
    "load_render_model_from_artifact",
    "render_hardware_gl_snapshot",
    "render_null_snapshot",
    "render_software_snapshot",
    "resolve_representation",
]
