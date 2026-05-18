"""Governance and control-plane tooling exports.

Exports are lazy so runtime paths can import narrow governance helpers without
eagerly loading planning, domain, and XStack surfaces.
"""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "CONTROL_REFUSAL_DEGRADED": ("tools.governance.control_plane_engine", "CONTROL_REFUSAL_DEGRADED"),
    "action_template_rows_by_id": ("tools.governance.control_plane_engine", "action_template_rows_by_id"),
    "build_control_intent": ("tools.governance.control_plane_engine", "build_control_intent"),
    "build_control_resolution": ("tools.governance.control_plane_engine", "build_control_resolution"),
    "control_action_rows_by_id": ("tools.governance.control_plane_engine", "control_action_rows_by_id"),
    "control_policy_rows_by_id": ("tools.governance.control_plane_engine", "control_policy_rows_by_id"),
    "REFUSAL_EFFECT_FORBIDDEN": ("tools.governance.effects", "REFUSAL_EFFECT_FORBIDDEN"),
    "REFUSAL_EFFECT_INVALID_TARGET": ("tools.governance.effects", "REFUSAL_EFFECT_INVALID_TARGET"),
    "STACK_MODE_ADD": ("tools.governance.effects", "STACK_MODE_ADD"),
    "STACK_MODE_MAX": ("tools.governance.effects", "STACK_MODE_MAX"),
    "STACK_MODE_MIN": ("tools.governance.effects", "STACK_MODE_MIN"),
    "STACK_MODE_MULTIPLY": ("tools.governance.effects", "STACK_MODE_MULTIPLY"),
    "STACK_MODE_REPLACE": ("tools.governance.effects", "STACK_MODE_REPLACE"),
    "active_effect_rows_by_target": ("tools.governance.effects", "active_effect_rows_by_target"),
    "build_effect": ("tools.governance.effects", "build_effect"),
    "effect_type_rows_by_id": ("tools.governance.effects", "effect_type_rows_by_id"),
    "get_effective_modifier": ("tools.governance.effects", "get_effective_modifier"),
    "get_effective_modifier_map": ("tools.governance.effects", "get_effective_modifier_map"),
    "normalize_effect_rows": ("tools.governance.effects", "normalize_effect_rows"),
    "prune_expired_effect_rows": ("tools.governance.effects", "prune_expired_effect_rows"),
    "stacking_policy_rows_by_id": ("tools.governance.effects", "stacking_policy_rows_by_id"),
    "DEFAULT_FIDELITY_POLICY_ID": ("tools.governance.fidelity", "DEFAULT_FIDELITY_POLICY_ID"),
    "FIDELITY_LEVEL_ORDER": ("tools.governance.fidelity", "FIDELITY_LEVEL_ORDER"),
    "NO_DOWNGRADE": ("tools.governance.fidelity", "NO_DOWNGRADE"),
    "RANK_FAIR_POLICY_ID": ("tools.governance.fidelity", "RANK_FAIR_POLICY_ID"),
    "REFUSAL_CTRL_FIDELITY_DENIED": ("tools.governance.fidelity", "REFUSAL_CTRL_FIDELITY_DENIED"),
    "SINGLEPLAYER_RELAXED_POLICY_ID": ("tools.governance.fidelity", "SINGLEPLAYER_RELAXED_POLICY_ID"),
    "arbitrate_fidelity_requests": ("tools.governance.fidelity", "arbitrate_fidelity_requests"),
    "build_budget_allocation_record": ("tools.governance.fidelity", "build_budget_allocation_record"),
    "build_fidelity_allocation": ("tools.governance.fidelity", "build_fidelity_allocation"),
    "build_fidelity_request": ("tools.governance.fidelity", "build_fidelity_request"),
    "ARCHIVE_POLICY_ID": ("tools.governance.governance_profile", "ARCHIVE_POLICY_ID"),
    "DEFAULT_GOVERNANCE_MODE_REGISTRY_REL": ("tools.governance.governance_profile", "DEFAULT_GOVERNANCE_MODE_REGISTRY_REL"),
    "DEFAULT_GOVERNANCE_PROFILE_REL": ("tools.governance.governance_profile", "DEFAULT_GOVERNANCE_PROFILE_REL"),
    "FORK_POLICY_ID": ("tools.governance.governance_profile", "FORK_POLICY_ID"),
    "GOVERNANCE_MODE_CORE_CLOSED": ("tools.governance.governance_profile", "GOVERNANCE_MODE_CORE_CLOSED"),
    "GOVERNANCE_MODE_MIXED": ("tools.governance.governance_profile", "GOVERNANCE_MODE_MIXED"),
    "GOVERNANCE_MODE_OPEN": ("tools.governance.governance_profile", "GOVERNANCE_MODE_OPEN"),
    "REDISTRIBUTION_POLICY_ID": ("tools.governance.governance_profile", "REDISTRIBUTION_POLICY_ID"),
    "canonicalize_governance_mode_row": ("tools.governance.governance_profile", "canonicalize_governance_mode_row"),
    "canonicalize_governance_profile": ("tools.governance.governance_profile", "canonicalize_governance_profile"),
    "deterministic_fingerprint": ("tools.governance.governance_profile", "deterministic_fingerprint"),
    "governance_profile_hash": ("tools.governance.governance_profile", "governance_profile_hash"),
    "governance_profile_path": ("tools.governance.governance_profile", "governance_profile_path"),
    "load_governance_mode_registry": ("tools.governance.governance_profile", "load_governance_mode_registry"),
    "load_governance_profile": ("tools.governance.governance_profile", "load_governance_profile"),
    "parse_release_tag": ("tools.governance.governance_profile", "parse_release_tag"),
    "select_governance_mode_row": ("tools.governance.governance_profile", "select_governance_mode_row"),
    "ALLOWED_CONTROL_IR_OP_TYPES": ("tools.governance.ir", "ALLOWED_CONTROL_IR_OP_TYPES"),
    "REFUSAL_CTRL_IR_COST_EXCEEDED": ("tools.governance.ir", "REFUSAL_CTRL_IR_COST_EXCEEDED"),
    "REFUSAL_CTRL_IR_FORBIDDEN_OP": ("tools.governance.ir", "REFUSAL_CTRL_IR_FORBIDDEN_OP"),
    "REFUSAL_CTRL_IR_INVALID": ("tools.governance.ir", "REFUSAL_CTRL_IR_INVALID"),
    "build_ai_controller_stub_ir": ("tools.governance.ir", "build_ai_controller_stub_ir"),
    "build_autopilot_stub_ir": ("tools.governance.ir", "build_autopilot_stub_ir"),
    "build_blueprint_execution_ir": ("tools.governance.ir", "build_blueprint_execution_ir"),
    "compile_control_ir": ("tools.governance.ir", "compile_control_ir"),
    "compile_ir_program": ("tools.governance.ir", "compile_ir_program"),
    "multiplayer_ir_mode": ("tools.governance.ir", "multiplayer_ir_mode"),
    "reconstruct_ir_action_sequence": ("tools.governance.ir", "reconstruct_ir_action_sequence"),
    "validate_control_ir_multiplayer": ("tools.governance.ir", "validate_control_ir_multiplayer"),
    "verify_and_compile_control_ir": ("tools.governance.ir", "verify_and_compile_control_ir"),
    "verify_control_ir": ("tools.governance.ir", "verify_control_ir"),
    "DOWNGRADE_BUDGET": ("tools.governance.negotiation", "DOWNGRADE_BUDGET"),
    "DOWNGRADE_EPISTEMIC": ("tools.governance.negotiation", "DOWNGRADE_EPISTEMIC"),
    "DOWNGRADE_POLICY": ("tools.governance.negotiation", "DOWNGRADE_POLICY"),
    "DOWNGRADE_RANK_FAIRNESS": ("tools.governance.negotiation", "DOWNGRADE_RANK_FAIRNESS"),
    "DOWNGRADE_TARGET_NOT_AVAILABLE": ("tools.governance.negotiation", "DOWNGRADE_TARGET_NOT_AVAILABLE"),
    "NEGOTIATION_AXIS_ORDER": ("tools.governance.negotiation", "NEGOTIATION_AXIS_ORDER"),
    "REFUSAL_CTRL_ENTITLEMENT_MISSING": ("tools.governance.negotiation", "REFUSAL_CTRL_ENTITLEMENT_MISSING"),
    "REFUSAL_CTRL_FORBIDDEN_BY_LAW": ("tools.governance.negotiation", "REFUSAL_CTRL_FORBIDDEN_BY_LAW"),
    "REFUSAL_CTRL_META_FORBIDDEN": ("tools.governance.negotiation", "REFUSAL_CTRL_META_FORBIDDEN"),
    "REFUSAL_CTRL_VIEW_FORBIDDEN": ("tools.governance.negotiation", "REFUSAL_CTRL_VIEW_FORBIDDEN"),
    "arbitrate_negotiation_requests": ("tools.governance.negotiation", "arbitrate_negotiation_requests"),
    "build_downgrade_entry": ("tools.governance.negotiation", "build_downgrade_entry"),
    "build_negotiation_request": ("tools.governance.negotiation", "build_negotiation_request"),
    "negotiate_request": ("tools.governance.negotiation", "negotiate_request"),
    "REFUSAL_PLAN_BUDGET_EXCEEDED": ("tools.governance.planning", "REFUSAL_PLAN_BUDGET_EXCEEDED"),
    "REFUSAL_PLAN_COMPILE_REFUSED": ("tools.governance.planning", "REFUSAL_PLAN_COMPILE_REFUSED"),
    "REFUSAL_PLAN_INVALID": ("tools.governance.planning", "REFUSAL_PLAN_INVALID"),
    "REFUSAL_PLAN_NOT_FOUND": ("tools.governance.planning", "REFUSAL_PLAN_NOT_FOUND"),
    "REFUSAL_PLAN_POLICY_REFUSED": ("tools.governance.planning", "REFUSAL_PLAN_POLICY_REFUSED"),
    "build_execute_plan_intent": ("tools.governance.planning", "build_execute_plan_intent"),
    "build_plan_execution_ir": ("tools.governance.planning", "build_plan_execution_ir"),
    "build_plan_intent": ("tools.governance.planning", "build_plan_intent"),
    "create_plan_artifact": ("tools.governance.planning", "create_plan_artifact"),
    "update_plan_artifact_incremental": ("tools.governance.planning", "update_plan_artifact_incremental"),
    "capability_binding_rows": ("tools.governance.capability", "capability_binding_rows"),
    "capability_rows_by_id": ("tools.governance.capability", "capability_rows_by_id"),
    "get_capability_params": ("tools.governance.capability", "get_capability_params"),
    "has_capability": ("tools.governance.capability", "has_capability"),
    "normalize_capability_binding_rows": ("tools.governance.capability", "normalize_capability_binding_rows"),
    "resolve_missing_capabilities": ("tools.governance.capability", "resolve_missing_capabilities"),
    "build_control_proof_bundle_from_decision_logs": ("tools.governance.proof", "build_control_proof_bundle_from_decision_logs"),
    "build_control_proof_bundle_from_markers": ("tools.governance.proof", "build_control_proof_bundle_from_markers"),
    "collect_control_decision_markers": ("tools.governance.proof", "collect_control_decision_markers"),
    "REFUSAL_VIEW_ENTITLEMENT_MISSING": ("tools.governance.view", "REFUSAL_VIEW_ENTITLEMENT_MISSING"),
    "REFUSAL_VIEW_POLICY_FORBIDDEN": ("tools.governance.view", "REFUSAL_VIEW_POLICY_FORBIDDEN"),
    "REFUSAL_VIEW_REQUIRES_EMBODIMENT": ("tools.governance.view", "REFUSAL_VIEW_REQUIRES_EMBODIMENT"),
    "REFUSAL_VIEW_TARGET_INVALID": ("tools.governance.view", "REFUSAL_VIEW_TARGET_INVALID"),
    "apply_view_binding": ("tools.governance.view", "apply_view_binding"),
    "normalize_view_binding_rows": ("tools.governance.view", "normalize_view_binding_rows"),
    "resolve_view_policy_id": ("tools.governance.view", "resolve_view_policy_id"),
    "view_policy_rows_by_id": ("tools.governance.view", "view_policy_rows_by_id"),
}


def __getattr__(name: str):
    target = _EXPORTS.get(str(name))
    if target is None:
        raise AttributeError("module 'tools.governance' has no attribute '{}'".format(str(name)))
    module_name, attr_name = target
    value = getattr(import_module(module_name), attr_name)
    globals()[str(name)] = value
    return value


__all__ = sorted(_EXPORTS.keys())
