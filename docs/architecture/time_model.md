Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/universe_state.schema.json` v1.0.0 and process runtime in `tools/xstack/sessionx/process_runtime.py`.

# Time Model v1

## Purpose
Define deterministic lab time control semantics for camera navigation tooling.

## Authoritative Time Fields (`UniverseState`)
- `simulation_time.tick` (integer logical tick)
- `simulation_time.timestamp_utc` (run-meta placeholder; not a hash driver for outcomes)
- `time_control.rate_permille` (fixed-point scalar, 1000 = 1.0x)
- `time_control.paused` (boolean)
- `time_control.accumulator_permille` (optional deterministic sub-tick accumulator)

## Process Semantics
- `process.time_control_set_rate`
  - requires `entitlement.time_control`
  - sets `rate_permille` in `[0, 10000]`
  - `rate_permille = 0` implies paused
- `process.time_pause`
  - requires `entitlement.time_control`
  - sets `paused = true`
- `process.time_resume`
  - requires `entitlement.time_control`
  - sets `paused = false`

## Deterministic Tick Advance Rule
For each process-execution step when not paused:
1. `total = accumulator_permille + rate_permille`
2. `tick_delta = floor(total / 1000)`
3. `accumulator_permille = total % 1000`
4. `simulation_time.tick += tick_delta`

When paused, no authoritative tick advance occurs.

## Interest-Region Update Coupling
- `process.region_management_tick` runs at deterministic process points and advances simulation tick by one logical step.
- ROI expand/collapse decisions therefore depend on deterministic tick order, not wall-clock cadence.
- Changing `time_control.rate_permille` affects future tick accumulation deterministically and therefore changes when ROI transitions may occur, but never changes transition logic itself.

## Invariants
- Time mutation is process-only.
- No wall-clock time is used to determine authoritative outcomes.
- Replay with identical inputs must produce identical tick sequence and hash anchors.
- Time-control commands do not mutate `UniverseIdentity`.
- ROI update ordering remains deterministic under any permitted time rate.

## Example
```json
{
  "simulation_time": {
    "tick": 12,
    "timestamp_utc": "1970-01-01T00:00:00Z"
  },
  "time_control": {
    "rate_permille": 1500,
    "paused": false,
    "accumulator_permille": 500
  }
}
```

## TODO
- Add SRZ/shard-aware time synchronization policy.
- Add causal ordering tuple contract for distributed process streams.
- Add compatibility guidance for future non-linear time overlays.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/contracts/law_profile.md`
- `docs/contracts/authority_context.md`
- `docs/architecture/camera_and_navigation.md`
- `docs/architecture/interest_regions.md`
