"""Deterministic pack compatibility validation."""

from __future__ import annotations

from importlib import import_module

from .pack_compat_validator import (
    PACK_COMPAT_MANIFEST_NAME,
    REFUSAL_PACK_COMPAT_MANIFEST_MISSING,
    REFUSAL_PACK_CONTRACT_MISMATCH,
    REFUSAL_PACK_MISSING_CAPABILITY,
    REFUSAL_PACK_MISSING_REGISTRY,
    attach_pack_compat_manifest,
    validate_pack_compat_manifest,
)


_PIPELINE_EXPORTS = {
    "PACK_COMPATIBILITY_REPORT_SCHEMA_NAME",
    "PACK_LOCK_SCHEMA_NAME",
    "REFUSAL_PACK_CONFLICT_IN_STRICT",
    "REFUSAL_PACK_CONTRACT_RANGE_MISMATCH",
    "REFUSAL_PACK_ENGINE_VERSION_MISMATCH",
    "REFUSAL_PACK_PROTOCOL_RANGE_MISMATCH",
    "REFUSAL_PACK_REGISTRY_MISSING",
    "REFUSAL_PACK_SCHEMA_INVALID",
    "REFUSAL_PACK_TRUST_DENIED",
    "build_verified_pack_lock",
    "verify_pack_set",
    "write_pack_compatibility_outputs",
}


def __getattr__(name: str):
    if name in _PIPELINE_EXPORTS:
        module = import_module(".pack_verification_pipeline", __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(name)


__all__ = [
    "PACK_COMPAT_MANIFEST_NAME",
    "PACK_COMPATIBILITY_REPORT_SCHEMA_NAME",
    "PACK_LOCK_SCHEMA_NAME",
    "REFUSAL_PACK_COMPAT_MANIFEST_MISSING",
    "REFUSAL_PACK_CONFLICT_IN_STRICT",
    "REFUSAL_PACK_CONTRACT_MISMATCH",
    "REFUSAL_PACK_CONTRACT_RANGE_MISMATCH",
    "REFUSAL_PACK_ENGINE_VERSION_MISMATCH",
    "REFUSAL_PACK_MISSING_CAPABILITY",
    "REFUSAL_PACK_MISSING_REGISTRY",
    "REFUSAL_PACK_PROTOCOL_RANGE_MISMATCH",
    "REFUSAL_PACK_REGISTRY_MISSING",
    "REFUSAL_PACK_SCHEMA_INVALID",
    "REFUSAL_PACK_TRUST_DENIED",
    "attach_pack_compat_manifest",
    "build_verified_pack_lock",
    "validate_pack_compat_manifest",
    "verify_pack_set",
    "write_pack_compatibility_outputs",
]
