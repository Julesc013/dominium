Status: DERIVED
Last Reviewed: 2026-05-21
Stability: provisional

# Service Conformance Fixtures

These fixtures prove the narrow `SERVICE-CONFORMANCE-LAW-01` validator.
They are contract-only and do not implement runtime services, provider calls,
product features, lifecycle behavior, state externalization, or Workbench UI.

Expected behavior:

- `valid_validation_service.json` passes service conformance validation.
- `invalid_path_identity.json` fails because service identity is path-like.
- `invalid_owns_truth.json` fails because services may not own truth.
- `invalid_runtime_implementation_authorized.json` fails because this law does
  not authorize runtime implementation.
- `invalid_missing_required_constraint.json` fails because all required
  conformance constraints must be declared.
