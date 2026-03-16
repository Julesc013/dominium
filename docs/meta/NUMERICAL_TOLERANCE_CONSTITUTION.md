Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Numerical Tolerance Constitution (TOL-0)

Status: Normative  
Version: 1.0.0  
Scope: Authoritative deterministic math for quantities, model residuals, and conservation checks.

## 1) Purpose

Define a single deterministic numeric discipline for:

- fixed-point quantity resolution,
- rounding behavior,
- conservation tolerances,
- residual handling,
- overflow behavior.

This constitution is mandatory for authoritative simulation math and proof/replay equivalence.

## 2) Quantity Resolution (Normative)

Each `quantity_id` MUST declare:

- `base_resolution` (fixed-point unit),
- `tolerance_abs`,
- optional `tolerance_rel`,
- `rounding_mode`,
- `overflow_policy`.

`overflow_policy` is restricted to:

- `fail`
- `saturate`

`wrap` is forbidden.

## 3) Rounding Modes (Normative)

Allowed modes:

- `round_half_to_even`
- `floor`
- `ceiling`
- `truncate` (only for explicitly declared safe operation classes)

Rounding MUST be deterministic and operation-class explicit:

- division,
- multiplication scaling,
- model output quantization,
- threshold comparison pre-normalization.

Runtime code MUST NOT rely on language-default rounding behavior for authoritative paths.

## 4) Comparison Tolerance (Normative)

Conservation and invariant checks MUST use explicit tolerance:

- canonical form: `abs(delta) <= tolerance_abs`
- relative tolerance is optional and profile-controlled, never replacing `tolerance_abs`.

## 5) Model Residual Policy (Normative)

Each model with approximate or quantized output MUST declare:

- `max_expected_residual`,
- `residual_action` in `{log_only, strict_fail, clamp}`.

When residual exceeds declared bounds, runtime MUST emit deterministic residual diagnostics.

## 6) Determinism Rule

Authoritative math MUST be:

- fixed-point integer arithmetic,
- deterministic ordering,
- platform-independent,
- replay-stable.

Raw float math is forbidden for invariant/conservation core checks.

## 7) Conservation Integration

Conservation checks MUST resolve tolerance in this order:

1. Contract-set tolerance (domain/profile override)
2. Quantity tolerance registry default

This preserves existing profile semantics while eliminating implicit tolerance gaps.

## 8) Proof Integration

Proof payloads MUST include:

- `quantity_tolerance_registry` hash,
- rounding-policy hash.

Any change to tolerance or rounding policy is a proof-salient change.

## 9) Non-Goals

- No quantity semantic changes.
- No floating-point simulation substrate.
- No weakening of conservation invariants.
