"""Meta subsystem package with lazy public exports.

The package is imported from runtime logging paths. Keep imports lazy so logging
does not eagerly load compile, domain, and governance surfaces during product
bootstrap.
"""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "REFUSAL_COMPILE_INVALID": ("tools.repo.meta.compile", "REFUSAL_COMPILE_INVALID"),
    "REFUSAL_COMPILE_MISSING_PROOF": ("tools.repo.meta.compile", "REFUSAL_COMPILE_MISSING_PROOF"),
    "REFUSAL_COMPILE_SOURCE_MISSING": ("tools.repo.meta.compile", "REFUSAL_COMPILE_SOURCE_MISSING"),
    "REFUSAL_COMPILE_UNSUPPORTED_TYPE": ("tools.repo.meta.compile", "REFUSAL_COMPILE_UNSUPPORTED_TYPE"),
    "compiled_model_execute": ("tools.repo.meta.compile", "compiled_model_execute"),
    "compiled_model_is_valid": ("tools.repo.meta.compile", "compiled_model_is_valid"),
    "evaluate_compile_request": ("tools.repo.meta.compile", "evaluate_compile_request"),
    "generate_measurement_observation": ("tools.repo.meta.instrumentation", "generate_measurement_observation"),
    "resolve_instrumentation_surface": ("tools.repo.meta.instrumentation", "resolve_instrumentation_surface"),
    "route_forensics_request": ("tools.repo.meta.instrumentation", "route_forensics_request"),
    "validate_control_access": ("tools.repo.meta.instrumentation", "validate_control_access"),
    "apply_override": ("tools.repo.meta.profile", "apply_override"),
    "resolve_effective_profile_snapshot": ("tools.repo.meta.profile", "resolve_effective_profile_snapshot"),
    "resolve_profile": ("tools.repo.meta.profile", "resolve_profile"),
    "REFUSAL_COMPUTE_BUDGET_EXCEEDED": ("tools.repo.meta.compute", "REFUSAL_COMPUTE_BUDGET_EXCEEDED"),
    "REFUSAL_COMPUTE_INVALID_OWNER": ("tools.repo.meta.compute", "REFUSAL_COMPUTE_INVALID_OWNER"),
    "REFUSAL_COMPUTE_MEMORY_EXCEEDED": ("tools.repo.meta.compute", "REFUSAL_COMPUTE_MEMORY_EXCEEDED"),
    "evaluate_compute_budget_tick": ("tools.repo.meta.compute", "evaluate_compute_budget_tick"),
    "request_compute": ("tools.repo.meta.compute", "request_compute"),
    "evaluate_reference_evaluator": ("tools.repo.meta.reference", "evaluate_reference_evaluator"),
    "evaluate_reference_suite": ("tools.repo.meta.reference", "evaluate_reference_suite"),
}


def __getattr__(name: str):
    target = _EXPORTS.get(str(name))
    if target is None:
        raise AttributeError("module 'tools.repo.meta' has no attribute '{}'".format(str(name)))
    module_name, attr_name = target
    value = getattr(import_module(module_name), attr_name)
    globals()[str(name)] = value
    return value


__all__ = sorted(_EXPORTS.keys())
