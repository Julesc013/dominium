"""Meta subsystem package with lazy public exports.

The package is imported from runtime logging paths. Keep imports lazy so logging
does not eagerly load compile, domain, and governance surfaces during product
bootstrap.
"""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "REFUSAL_COMPILE_INVALID": ("engine.foundation.meta.compile", "REFUSAL_COMPILE_INVALID"),
    "REFUSAL_COMPILE_MISSING_PROOF": ("engine.foundation.meta.compile", "REFUSAL_COMPILE_MISSING_PROOF"),
    "REFUSAL_COMPILE_SOURCE_MISSING": ("engine.foundation.meta.compile", "REFUSAL_COMPILE_SOURCE_MISSING"),
    "REFUSAL_COMPILE_UNSUPPORTED_TYPE": ("engine.foundation.meta.compile", "REFUSAL_COMPILE_UNSUPPORTED_TYPE"),
    "compiled_model_execute": ("engine.foundation.meta.compile", "compiled_model_execute"),
    "compiled_model_is_valid": ("engine.foundation.meta.compile", "compiled_model_is_valid"),
    "evaluate_compile_request": ("engine.foundation.meta.compile", "evaluate_compile_request"),
    "generate_measurement_observation": ("engine.foundation.meta.instrumentation", "generate_measurement_observation"),
    "resolve_instrumentation_surface": ("engine.foundation.meta.instrumentation", "resolve_instrumentation_surface"),
    "route_forensics_request": ("engine.foundation.meta.instrumentation", "route_forensics_request"),
    "validate_control_access": ("engine.foundation.meta.instrumentation", "validate_control_access"),
    "apply_override": ("engine.foundation.meta.profile", "apply_override"),
    "resolve_effective_profile_snapshot": ("engine.foundation.meta.profile", "resolve_effective_profile_snapshot"),
    "resolve_profile": ("engine.foundation.meta.profile", "resolve_profile"),
    "REFUSAL_COMPUTE_BUDGET_EXCEEDED": ("engine.foundation.meta.compute", "REFUSAL_COMPUTE_BUDGET_EXCEEDED"),
    "REFUSAL_COMPUTE_INVALID_OWNER": ("engine.foundation.meta.compute", "REFUSAL_COMPUTE_INVALID_OWNER"),
    "REFUSAL_COMPUTE_MEMORY_EXCEEDED": ("engine.foundation.meta.compute", "REFUSAL_COMPUTE_MEMORY_EXCEEDED"),
    "evaluate_compute_budget_tick": ("engine.foundation.meta.compute", "evaluate_compute_budget_tick"),
    "request_compute": ("engine.foundation.meta.compute", "request_compute"),
    "evaluate_reference_evaluator": ("engine.foundation.meta.reference", "evaluate_reference_evaluator"),
    "evaluate_reference_suite": ("engine.foundation.meta.reference", "evaluate_reference_suite"),
}


def __getattr__(name: str):
    target = _EXPORTS.get(str(name))
    if target is None:
        raise AttributeError("module 'engine.foundation.meta' has no attribute '{}'".format(str(name)))
    module_name, attr_name = target
    value = getattr(import_module(module_name), attr_name)
    globals()[str(name)] = value
    return value


__all__ = sorted(_EXPORTS.keys())
