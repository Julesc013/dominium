"""Compatibility helpers with lazy exports to avoid cross-layer import cycles."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "COMPAT_MODE_DEGRADED": ("tools.validators.compatibility.capability_negotiation", "COMPAT_MODE_DEGRADED"),
    "COMPAT_MODE_FULL": ("tools.validators.compatibility.capability_negotiation", "COMPAT_MODE_FULL"),
    "COMPAT_MODE_READ_ONLY": ("tools.validators.compatibility.capability_negotiation", "COMPAT_MODE_READ_ONLY"),
    "COMPAT_MODE_REFUSE": ("tools.validators.compatibility.capability_negotiation", "COMPAT_MODE_REFUSE"),
    "READ_ONLY_LAW_PROFILE_ID": ("tools.validators.compatibility.capability_negotiation", "READ_ONLY_LAW_PROFILE_ID"),
    "build_default_endpoint_descriptor": ("tools.validators.compatibility.capability_negotiation", "build_default_endpoint_descriptor"),
    "build_endpoint_descriptor": ("tools.validators.compatibility.capability_negotiation", "build_endpoint_descriptor"),
    "negotiate_endpoint_descriptors": ("tools.validators.compatibility.capability_negotiation", "negotiate_endpoint_descriptors"),
    "verify_negotiation_record": ("tools.validators.compatibility.capability_negotiation", "verify_negotiation_record"),
    "REFUSAL_CONNECTION_NEGOTIATION_MISMATCH": ("tools.validators.compatibility.handshake", "REFUSAL_CONNECTION_NEGOTIATION_MISMATCH"),
    "REFUSAL_CONNECTION_NO_NEGOTIATION": ("tools.validators.compatibility.handshake", "REFUSAL_CONNECTION_NO_NEGOTIATION"),
    "build_compat_refusal": ("tools.validators.compatibility.handshake", "build_compat_refusal"),
    "build_handshake_message": ("tools.validators.compatibility.handshake", "build_handshake_message"),
    "build_session_begin_payload": ("tools.validators.compatibility.handshake", "build_session_begin_payload"),
    "DEFAULT_UI_CAPABILITY_PREFERENCE": ("tools.validators.compatibility.negotiation", "DEFAULT_UI_CAPABILITY_PREFERENCE"),
    "REFUSAL_COMPAT_FEATURE_DISABLED": ("tools.validators.compatibility.negotiation", "REFUSAL_COMPAT_FEATURE_DISABLED"),
    "build_compat_status_payload": ("tools.validators.compatibility.negotiation", "build_compat_status_payload"),
    "build_degrade_runtime_state": ("tools.validators.compatibility.negotiation", "build_degrade_runtime_state"),
    "enforce_negotiated_capability": ("tools.validators.compatibility.negotiation", "enforce_negotiated_capability"),
    "negotiate_product_endpoints": ("tools.validators.compatibility.negotiation", "negotiate_product_endpoints"),
    "verify_recorded_negotiation": ("tools.validators.compatibility.negotiation", "verify_recorded_negotiation"),
    "build_product_build_metadata": ("tools.validators.compatibility.descriptor", "build_product_build_metadata"),
    "build_product_descriptor": ("tools.validators.compatibility.descriptor", "build_product_descriptor"),
    "descriptor_json_text": ("tools.validators.compatibility.descriptor", "descriptor_json_text"),
    "emit_product_descriptor": ("tools.validators.compatibility.descriptor", "emit_product_descriptor"),
    "product_descriptor_bin_names": ("tools.validators.compatibility.descriptor", "product_descriptor_bin_names"),
    "write_descriptor_file": ("tools.validators.compatibility.descriptor", "write_descriptor_file"),
    "ARTIFACT_KIND_IDS": ("tools.validators.compatibility.migration_lifecycle", "ARTIFACT_KIND_IDS"),
    "DECISION_LOAD": ("tools.validators.compatibility.migration_lifecycle", "DECISION_LOAD"),
    "DECISION_MIGRATE": ("tools.validators.compatibility.migration_lifecycle", "DECISION_MIGRATE"),
    "DECISION_READ_ONLY": ("tools.validators.compatibility.migration_lifecycle", "DECISION_READ_ONLY"),
    "DECISION_REFUSE": ("tools.validators.compatibility.migration_lifecycle", "DECISION_REFUSE"),
    "determine_migration_decision": ("tools.validators.compatibility.migration_lifecycle", "determine_migration_decision"),
    "plan_migration_path": ("tools.validators.compatibility.migration_lifecycle", "plan_migration_path"),
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
