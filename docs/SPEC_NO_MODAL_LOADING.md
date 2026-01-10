# SPEC_NO_MODAL_LOADING — Non-Blocking Runtime Contract

## Scope
This spec applies to the Dominium game runtime UI/render thread and any work
scheduled or executed on that thread.

## Terms
- **Modal loading:** any UI/render path that blocks on IO, decompression, content
  loading, or long computation.
- **Derived work:** non-authoritative jobs (IO, decompression, mesh/tile builds)
  that can be delayed, canceled, or dropped without affecting simulation.

## Rules (mandatory)
- The UI/render thread MUST NOT block on IO, decompression, content loading, or
  long computation.
- Authoritative simulation MUST NOT wait on derived work.
- All expensive work MUST be explicit, derived, budgeted, and cancellable.
- Missing or late derived data MUST degrade fidelity; it MUST NOT stall
  execution.
- Performance budget enforcement MAY reduce derived cadence or fidelity but MUST
  NOT change authoritative simulation semantics.
- Derived work MUST NOT mutate authoritative state.
- Derived job completion order MUST NOT affect determinism hashes.

## Enforcement
- UI-thread IO attempts MUST be refused: log a structured error, increment a
  violation counter, and return an error without blocking.
- A stall watchdog MUST emit diagnostics for frames that exceed a configured
  threshold; repeated stalls are treated as contract failures.
- Derived work pumping MUST obey the budgets defined in
  `docs/SPEC_STREAMING_BUDGETS.md` and `docs/SPEC_PERF_BUDGETS.md`.

## Test gates (required)
The following tests are mandatory and MUST pass:
- `test_no_modal_loading`
- `test_derived_order_independence`
- `test_snapshot_isolation`

## Related specs
- `docs/SPEC_STREAMING_BUDGETS.md`
- `docs/SPEC_PERF_BUDGETS.md`
- `docs/SPEC_PROFILING.md`
- `docs/SPEC_FIDELITY_DEGRADATION.md`
- `docs/SPEC_DETERMINISM.md`
