"""Session lifecycle tooling for deterministic out-of-game bootstrap and boot smoke runs.

This module exposes a lazy import surface to avoid eager circular imports between
session boot orchestration and policy modules.
"""

from __future__ import annotations

from importlib import import_module


_EXPORT_MAP = {
    "create_session_spec": ("tools.xstack.sessionx.creator", "create_session_spec"),
    "observe_truth": ("tools.xstack.sessionx.observation", "observe_truth"),
    "perceived_model_hash": ("tools.xstack.sessionx.observation", "perceived_model_hash"),
    "load_session_pipeline_contract": ("tools.xstack.sessionx.pipeline_contract", "load_session_pipeline_contract"),
    "execute_intent": ("tools.xstack.sessionx.process_runtime", "execute_intent"),
    "replay_intent_script": ("tools.xstack.sessionx.process_runtime", "replay_intent_script"),
    "build_render_model": ("tools.xstack.sessionx.render_model", "build_render_model"),
    "boot_session_spec": ("tools.xstack.sessionx.runner", "boot_session_spec"),
    "execute_single_intent_srz": ("tools.xstack.sessionx.scheduler", "execute_single_intent_srz"),
    "replay_intent_script_srz": ("tools.xstack.sessionx.scheduler", "replay_intent_script_srz"),
    "server_validate_transition": ("tools.xstack.sessionx.server_gate", "server_validate_transition"),
    "surface_abort_session": ("tools.xstack.sessionx.stage_parity", "surface_abort_session"),
    "surface_resume_session": ("tools.xstack.sessionx.stage_parity", "surface_resume_session"),
    "surface_stage_status": ("tools.xstack.sessionx.stage_parity", "surface_stage_status"),
    "abort_session_spec": ("tools.xstack.sessionx.session_control", "abort_session_spec"),
    "resume_session_spec": ("tools.xstack.sessionx.session_control", "resume_session_spec"),
    "session_stage_status": ("tools.xstack.sessionx.session_control", "session_stage_status"),
    "build_single_shard": ("tools.xstack.sessionx.srz", "build_single_shard"),
    "validate_intent_envelope": ("tools.xstack.sessionx.srz", "validate_intent_envelope"),
    "validate_srz_shard": ("tools.xstack.sessionx.srz", "validate_srz_shard"),
    "run_intent_script": ("tools.xstack.sessionx.script_runner", "run_intent_script"),
    "available_windows": ("tools.xstack.sessionx.ui_host", "available_windows"),
    "dispatch_window_action": ("tools.xstack.sessionx.ui_host", "dispatch_window_action"),
    "selector_get": ("tools.xstack.sessionx.ui_host", "selector_get"),
    "validate_ui_window_descriptor": ("tools.xstack.sessionx.ui_host", "validate_ui_window_descriptor"),
    "with_search_results": ("tools.xstack.sessionx.ui_host", "with_search_results"),
}

__all__ = sorted(_EXPORT_MAP.keys())


def __getattr__(name: str):
    target = _EXPORT_MAP.get(str(name))
    if not target:
        raise AttributeError("module '{}' has no attribute '{}'".format(__name__, name))
    module = import_module(target[0])
    value = getattr(module, target[1])
    globals()[name] = value
    return value
