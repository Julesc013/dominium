# Kernel Backend Selection

Scope: deterministic kernel backend selection for Work IR execution.

## Invariants
- Authoritative selection is deterministic and auditable.
- Profiling never affects authoritative selection.
- GPU is derived-only for authoritative classes.

## Dependencies
- `docs/architecture/EXECUTION_MODEL.md`
- `docs/architecture/SYS_CAPS_AND_EXEC_POLICY.md`

This guide defines how kernel backends are selected deterministically while
preserving authoritative correctness.

## Policy Model

Kernel selection is driven by a `KernelPolicy` object with:
- Ordered backend list (default order)
- Per-op overrides (optional)
- Determinism constraints (strict vs derived masks)
- Budget constraints for derived tasks
- Law/capability masks to disable backends

The policy is interpreted deterministically. If a policy configuration changes,
selection results change deterministically and are auditable.

## Determinism Classes

- STRICT/ORDERED/COMMUTATIVE: treated as authoritative for selection
  - GPU is never eligible
  - SIMD only if policy allows and backend is deterministic
- DERIVED: non-authoritative
  - GPU allowed if policy and capabilities allow

## Selection Algorithm

Selection is deterministic and ordered:

1) Determine the backend order:
   - Use per-op override if present
   - Otherwise use policy default order
2) Filter candidates by:
   - determinism class (GPU forbidden for authoritative)
   - policy strict/derived backend masks
   - capability availability
   - law/capability masks
3) Select the first backend in the ordered list that satisfies filters.
4) If no candidate exists, selection is refused with a deterministic error.

## Derived Profiling & Budgets

Profiling may only influence derived selection:
- If policy allows adaptive derived selection, a derived request may skip the
  primary backend when profiling indicates it is slow.
- Derived budget enforcement can bias selection toward GPU when available.

Profiling must never affect authoritative selection.

## Policy Format (C/C++ Config)

Policy can be loaded from a deterministic config structure:

```
dom_kernel_policy_config config;
config.default_order = ...;        // ordered backend ids
config.default_order_count = ...;
config.strict_backend_mask = ...;  // scalar/simd only
config.derived_backend_mask = ...; // scalar/simd/gpu allowed
config.flags = ...;                // disable simd/gpu, adaptive derived
config.max_cpu_time_us_derived = ...;
config.overrides = ...;            // per-op override entries
config.override_count = ...;
```

## Debugging Selection Outcomes

To debug selection:
- Verify determinism_class and policy masks
- Verify capability masks (SIMD/GPU availability)
- Verify law/capability masks
- Check per-op overrides and order

If no candidate is selected, the selector returns a deterministic refusal code.

## Forbidden assumptions
- Adaptive profiling can change authoritative outcomes.
- Unknown capabilities imply availability.

## See also
- `schema/syscaps/README.md`
