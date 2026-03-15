"""Compatibility helpers with lazy exports to avoid cross-layer import cycles."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "COMPAT_MODE_DEGRADED": ("src.compat.capability_negotiation", "COMPAT_MODE_DEGRADED"),
    "COMPAT_MODE_FULL": ("src.compat.capability_negotiation", "COMPAT_MODE_FULL"),
    "COMPAT_MODE_READ_ONLY": ("src.compat.capability_negotiation", "COMPAT_MODE_READ_ONLY"),
    "COMPAT_MODE_REFUSE": ("src.compat.capability_negotiation", "COMPAT_MODE_REFUSE"),
    "READ_ONLY_LAW_PROFILE_ID": ("src.compat.capability_negotiation", "READ_ONLY_LAW_PROFILE_ID"),
    "build_default_endpoint_descriptor": ("src.compat.capability_negotiation", "build_default_endpoint_descriptor"),
    "build_endpoint_descriptor": ("src.compat.capability_negotiation", "build_endpoint_descriptor"),
    "negotiate_endpoint_descriptors": ("src.compat.capability_negotiation", "negotiate_endpoint_descriptors"),
    "verify_negotiation_record": ("src.compat.capability_negotiation", "verify_negotiation_record"),
    "REFUSAL_CONNECTION_NEGOTIATION_MISMATCH": ("src.compat.handshake", "REFUSAL_CONNECTION_NEGOTIATION_MISMATCH"),
    "REFUSAL_CONNECTION_NO_NEGOTIATION": ("src.compat.handshake", "REFUSAL_CONNECTION_NO_NEGOTIATION"),
    "build_compat_refusal": ("src.compat.handshake", "build_compat_refusal"),
    "build_handshake_message": ("src.compat.handshake", "build_handshake_message"),
    "build_session_begin_payload": ("src.compat.handshake", "build_session_begin_payload"),
    "DEFAULT_UI_CAPABILITY_PREFERENCE": ("src.compat.negotiation", "DEFAULT_UI_CAPABILITY_PREFERENCE"),
    "REFUSAL_COMPAT_FEATURE_DISABLED": ("src.compat.negotiation", "REFUSAL_COMPAT_FEATURE_DISABLED"),
    "build_compat_status_payload": ("src.compat.negotiation", "build_compat_status_payload"),
    "build_degrade_runtime_state": ("src.compat.negotiation", "build_degrade_runtime_state"),
    "enforce_negotiated_capability": ("src.compat.negotiation", "enforce_negotiated_capability"),
    "negotiate_product_endpoints": ("src.compat.negotiation", "negotiate_product_endpoints"),
    "verify_recorded_negotiation": ("src.compat.negotiation", "verify_recorded_negotiation"),
    "build_product_build_metadata": ("src.compat.descriptor", "build_product_build_metadata"),
    "build_product_descriptor": ("src.compat.descriptor", "build_product_descriptor"),
    "descriptor_json_text": ("src.compat.descriptor", "descriptor_json_text"),
    "emit_product_descriptor": ("src.compat.descriptor", "emit_product_descriptor"),
    "product_descriptor_bin_names": ("src.compat.descriptor", "product_descriptor_bin_names"),
    "write_descriptor_file": ("src.compat.descriptor", "write_descriptor_file"),
    "ARTIFACT_KIND_IDS": ("src.compat.migration_lifecycle", "ARTIFACT_KIND_IDS"),
    "DECISION_LOAD": ("src.compat.migration_lifecycle", "DECISION_LOAD"),
    "DECISION_MIGRATE": ("src.compat.migration_lifecycle", "DECISION_MIGRATE"),
    "DECISION_READ_ONLY": ("src.compat.migration_lifecycle", "DECISION_READ_ONLY"),
    "DECISION_REFUSE": ("src.compat.migration_lifecycle", "DECISION_REFUSE"),
    "determine_migration_decision": ("src.compat.migration_lifecycle", "determine_migration_decision"),
    "plan_migration_path": ("src.compat.migration_lifecycle", "plan_migration_path"),
}


def __getattr__(name: str):
    target = _EXPORTS.get(str(name))
    if target is None:
        raise AttributeError("module 'src.compat' has no attribute '{}'".format(str(name)))
    module_name, attr_name = target
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[str(name)] = value
    return value


__all__ = sorted(_EXPORTS.keys())
