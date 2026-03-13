"""Shared deterministic AppShell supervisor surfaces."""

from .args_canonicalizer import canonicalize_arg_map, canonicalize_args, canonicalize_flag_pairs
from .supervisor_engine import (
    DEFAULT_SUPERVISOR_POLICY_ID,
    SUPERVISOR_AGGREGATED_LOG_REL,
    SUPERVISOR_RUN_MANIFEST_REL,
    SUPERVISOR_STATE_REL,
    SupervisorEngine,
    build_supervisor_run_spec,
    attach_supervisor_children,
    clear_current_supervisor_engine,
    discover_active_supervisor_endpoint,
    get_current_supervisor_engine,
    invoke_supervisor_service_command,
    launch_supervisor_service,
    load_supervisor_runtime_state,
    set_current_supervisor_engine,
)

__all__ = [
    "DEFAULT_SUPERVISOR_POLICY_ID",
    "SUPERVISOR_AGGREGATED_LOG_REL",
    "SUPERVISOR_RUN_MANIFEST_REL",
    "SUPERVISOR_STATE_REL",
    "SupervisorEngine",
    "build_supervisor_run_spec",
    "canonicalize_arg_map",
    "canonicalize_args",
    "canonicalize_flag_pairs",
    "attach_supervisor_children",
    "clear_current_supervisor_engine",
    "discover_active_supervisor_endpoint",
    "get_current_supervisor_engine",
    "invoke_supervisor_service_command",
    "launch_supervisor_service",
    "load_supervisor_runtime_state",
    "set_current_supervisor_engine",
]
