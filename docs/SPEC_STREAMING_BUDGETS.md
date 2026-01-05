# SPEC_STREAMING_BUDGETS — Derived Work Budgets

## Scope
This spec defines budgeted execution for derived (non-authoritative) work in
the game runtime, including IO, decompression, and cache/build steps.

## Budget types
Each derived pump cycle MUST obey all applicable budgets:
- **Time budget:** maximum wall-clock time per pump (milliseconds).
- **IO budget:** maximum bytes of IO work attributed to the pump.
- **Job budget:** maximum number of jobs processed per pump.

## Rules (mandatory)
- Derived work MUST be processed only within explicit budgets.
- If the next job does not fit the remaining budget, it MUST remain pending.
- Derived jobs MAY supply budget hints; hints are advisory and MUST NOT affect
  authoritative state.
- Cancellation and deferral MUST NOT affect determinism.
- Job selection order MUST be deterministic (priority, then submit order).
- Budget exhaustion MUST NOT block the UI/render thread.

## Integration requirements
- Budget values are configurable and SHOULD have finite defaults.
- Budgets are independent of authoritative simulation cadence.
- Derived work completion order MUST NOT affect simulation hashes.

## Related specs
- `docs/SPEC_NO_MODAL_LOADING.md`
- `docs/SPEC_FIDELITY_DEGRADATION.md`
