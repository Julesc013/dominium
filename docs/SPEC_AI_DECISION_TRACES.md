# SPEC_AI_DECISION_TRACES - AI Decision Trace Records

This spec defines the non-authoritative decision trace format for AI planners.

## 1. Purpose
- Provide an auditable record of AI decisions.
- Enable debugging without affecting simulation state.
- Persisted under `RUN_ROOT` as optional output.

Decision traces are **non-sim-affecting** and may be dropped if storage fails.

## 2. Trace format (TLV)
Trace files use a deterministic TLV layout (core TLV):

Required fields:
- `schema_version` (u32)
- `plan_id` (u64)
- `faction_id` (u64)
- `tick_index` (u64)
- `input_digest` (u64)
- `output_digest` (u64)
- `output_count` (u32)
- `reason_code` (u32)

Optional fields:
- `ops_used` (u32)
- `budget_hit` (u32, 0/1)

Reason codes (v0):
- `0`: NONE (no-op)
- `1`: ACTIONS_EMITTED
- `2`: BUDGET_HIT
- `3`: INVALID_INPUT

## 3. Storage
- Location: `RUN_ROOT/log/` (preferred) or `RUN_ROOT/`
- Filename pattern: `ai_trace_<run_id>_<tick>_<faction_id>_<plan_id>.tlv`
- Failure to write MUST NOT affect simulation.

## 4. Determinism
- Trace contents MUST be deterministic given inputs and outputs.
- Trace ordering is not authoritative; timestamps are not stored.

## Related specs
- `docs/SPEC_FACTIONS.md`
- `docs/SPEC_AI_DETERMINISM.md`
