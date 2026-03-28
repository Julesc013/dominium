"""Deterministic UX-0 viewer shell package."""

from .teleport_controller import (
    RNG_UI_TELEPORT_RANDOM_STAR,
    build_teleport_plan,
    filter_habitable_systems_plan,
    list_systems_for_cell_plan,
    query_nearest_system_plan,
)
from .inspect_panels import build_inspection_panel_set
from .main_menu_surface import build_client_main_menu_surface
from .map_views import build_map_view_set

STATE_BOOT = "Boot"
STATE_BUNDLE_SELECT = "BundleSelect"
STATE_SEED_SELECT = "SeedSelect"
STATE_SESSION_RUNNING = "SessionRunning"


def build_viewer_shell_state(*args, **kwargs):
    from .viewer_shell import build_viewer_shell_state as impl

    return impl(*args, **kwargs)

__all__ = [
    "RNG_UI_TELEPORT_RANDOM_STAR",
    "STATE_BOOT",
    "STATE_BUNDLE_SELECT",
    "STATE_SEED_SELECT",
    "STATE_SESSION_RUNNING",
    "build_inspection_panel_set",
    "build_client_main_menu_surface",
    "build_map_view_set",
    "build_teleport_plan",
    "build_viewer_shell_state",
    "filter_habitable_systems_plan",
    "list_systems_for_cell_plan",
    "query_nearest_system_plan",
]
