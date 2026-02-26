"""Platform abstraction surfaces for client presentation/runtime integration."""

from .platform_audio import close_audio_device, create_audio_device, submit_audio_frame
from .platform_gfx import (
    create_graphics_context,
    destroy_graphics_context,
    list_available_backends,
    present_frame,
    resize_graphics_surface,
)
from .platform_input import (
    create_keyboard_event,
    create_mouse_event,
    normalize_input_event,
    queue_input_event,
)
from .platform_window import close_window, create_window, detect_platform_id, resize_window

__all__ = [
    "close_audio_device",
    "close_window",
    "create_audio_device",
    "create_graphics_context",
    "create_keyboard_event",
    "create_mouse_event",
    "create_window",
    "detect_platform_id",
    "destroy_graphics_context",
    "list_available_backends",
    "normalize_input_event",
    "present_frame",
    "queue_input_event",
    "resize_graphics_surface",
    "resize_window",
    "submit_audio_frame",
]
