"""Compatibility helpers with lazy exports to avoid cross-layer import cycles."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "COMPAT_MODE_DEGRADED": ("runtime.compatibility.capability_negotiation", "COMPAT_MODE_DEGRADED"),
    "COMPAT_MODE_FULL": ("runtime.compatibility.capability_negotiation", "COMPAT_MODE_FULL"),
    "COMPAT_MODE_READ_ONLY": ("runtime.compatibility.capability_negotiation", "COMPAT_MODE_READ_ONLY"),
    "COMPAT_MODE_REFUSE": ("runtime.compatibility.capability_negotiation", "COMPAT_MODE_REFUSE"),
    "READ_ONLY_LAW_PROFILE_ID": ("runtime.compatibility.capability_negotiation", "READ_ONLY_LAW_PROFILE_ID"),
    "build_default_endpoint_descriptor": ("runtime.compatibility.capability_negotiation", "build_default_endpoint_descriptor"),
    "build_endpoint_descriptor": ("runtime.compatibility.capability_negotiation", "build_endpoint_descriptor"),
    "negotiate_endpoint_descriptors": ("runtime.compatibility.capability_negotiation", "negotiate_endpoint_descriptors"),
    "verify_negotiation_record": ("runtime.compatibility.capability_negotiation", "verify_negotiation_record"),
    "REFUSAL_CONNECTION_NEGOTIATION_MISMATCH": ("runtime.compatibility.handshake", "REFUSAL_CONNECTION_NEGOTIATION_MISMATCH"),
    "REFUSAL_CONNECTION_NO_NEGOTIATION": ("runtime.compatibility.handshake", "REFUSAL_CONNECTION_NO_NEGOTIATION"),
    "build_compat_refusal": ("runtime.compatibility.handshake", "build_compat_refusal"),
    "build_handshake_message": ("runtime.compatibility.handshake", "build_handshake_message"),
    "build_session_begin_payload": ("runtime.compatibility.handshake", "build_session_begin_payload"),
    "DEFAULT_UI_CAPABILITY_PREFERENCE": ("runtime.compatibility.negotiation", "DEFAULT_UI_CAPABILITY_PREFERENCE"),
    "REFUSAL_COMPAT_FEATURE_DISABLED": ("runtime.compatibility.negotiation", "REFUSAL_COMPAT_FEATURE_DISABLED"),
    "build_compat_status_payload": ("runtime.compatibility.negotiation", "build_compat_status_payload"),
    "build_degrade_runtime_state": ("runtime.compatibility.negotiation", "build_degrade_runtime_state"),
    "enforce_negotiated_capability": ("runtime.compatibility.negotiation", "enforce_negotiated_capability"),
    "negotiate_product_endpoints": ("runtime.compatibility.negotiation", "negotiate_product_endpoints"),
    "verify_recorded_negotiation": ("runtime.compatibility.negotiation", "verify_recorded_negotiation"),
    "build_product_build_metadata": ("runtime.compatibility.descriptor", "build_product_build_metadata"),
    "build_product_descriptor": ("runtime.compatibility.descriptor", "build_product_descriptor"),
    "descriptor_json_text": ("runtime.compatibility.descriptor", "descriptor_json_text"),
    "emit_product_descriptor": ("runtime.compatibility.descriptor", "emit_product_descriptor"),
    "product_descriptor_bin_names": ("runtime.compatibility.descriptor", "product_descriptor_bin_names"),
    "write_descriptor_file": ("runtime.compatibility.descriptor", "write_descriptor_file"),
    "ARTIFACT_KIND_IDS": ("runtime.compatibility.migration_lifecycle", "ARTIFACT_KIND_IDS"),
    "DECISION_LOAD": ("runtime.compatibility.migration_lifecycle", "DECISION_LOAD"),
    "DECISION_MIGRATE": ("runtime.compatibility.migration_lifecycle", "DECISION_MIGRATE"),
    "DECISION_READ_ONLY": ("runtime.compatibility.migration_lifecycle", "DECISION_READ_ONLY"),
    "DECISION_REFUSE": ("runtime.compatibility.migration_lifecycle", "DECISION_REFUSE"),
    "determine_migration_decision": ("runtime.compatibility.migration_lifecycle", "determine_migration_decision"),
    "plan_migration_path": ("runtime.compatibility.migration_lifecycle", "plan_migration_path"),
}


def __getattr__(name: str):
    target = _EXPORTS.get(str(name))
    if target is None:
        raise AttributeError("module 'compat' has no attribute '{}'".format(str(name)))
    module_name, attr_name = target
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[str(name)] = value
    return value


__all__ = sorted(_EXPORTS.keys())
