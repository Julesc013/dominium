"""Meta subsystem package."""

from meta.compile import (
    REFUSAL_COMPILE_INVALID,
    REFUSAL_COMPILE_MISSING_PROOF,
    REFUSAL_COMPILE_SOURCE_MISSING,
    REFUSAL_COMPILE_UNSUPPORTED_TYPE,
    compiled_model_execute,
    compiled_model_is_valid,
    evaluate_compile_request,
)
from meta.instrumentation import (
    generate_measurement_observation,
    resolve_instrumentation_surface,
    route_forensics_request,
    validate_control_access,
)
from meta.profile import (
    apply_override,
    resolve_effective_profile_snapshot,
    resolve_profile,
)
from meta.compute import (
    REFUSAL_COMPUTE_BUDGET_EXCEEDED,
    REFUSAL_COMPUTE_INVALID_OWNER,
    REFUSAL_COMPUTE_MEMORY_EXCEEDED,
    evaluate_compute_budget_tick,
    request_compute,
)


def evaluate_reference_evaluator(*args, **kwargs):
    from meta.reference import evaluate_reference_evaluator as _evaluate_reference_evaluator

    return _evaluate_reference_evaluator(*args, **kwargs)


def evaluate_reference_suite(*args, **kwargs):
    from meta.reference import evaluate_reference_suite as _evaluate_reference_suite

    return _evaluate_reference_suite(*args, **kwargs)

__all__ = [
    "REFUSAL_COMPILE_INVALID",
    "REFUSAL_COMPILE_SOURCE_MISSING",
    "REFUSAL_COMPILE_UNSUPPORTED_TYPE",
    "REFUSAL_COMPILE_MISSING_PROOF",
    "evaluate_compile_request",
    "compiled_model_is_valid",
    "compiled_model_execute",
    "evaluate_reference_evaluator",
    "evaluate_reference_suite",
    "resolve_instrumentation_surface",
    "validate_control_access",
    "generate_measurement_observation",
    "route_forensics_request",
    "resolve_profile",
    "apply_override",
    "resolve_effective_profile_snapshot",
    "REFUSAL_COMPUTE_INVALID_OWNER",
    "REFUSAL_COMPUTE_BUDGET_EXCEEDED",
    "REFUSAL_COMPUTE_MEMORY_EXCEEDED",
    "request_compute",
    "evaluate_compute_budget_tick",
]
