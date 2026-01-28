# Macro Time Model (SCALE0)

Status: binding.
Scope: macro-time stepping, event ordering, and replay integration.

## Purpose
Define how macro-scale simulation advances in time without breaking ACT,
determinism, or replay guarantees.

## Allowed macro stepping
- Macro steps MAY advance ACT in coarse increments.
- Macro steps MUST be decomposable into deterministic event batches.
- Macro steps MUST respect commit boundaries.

## Event-driven macro evolution
- Macro models advance only by scheduled events or explicit macro ticks.
- No hidden background scanning or wall-clock driven updates.
- All macro events are logged with stable ordering keys.

## Deterministic event ordering
- Ordering keys are stable (phase_id, task_id, sub_index or equivalents).
- Ties are resolved deterministically and identically across threads.
- Cross-thread results MUST be identical given identical inputs.

## Save/replay integration
- Collapse/expand events are recorded in the replay stream.
- Macro events and ordering are replayed exactly.
- Replays MUST reproduce identical macro capsules and expansion outputs.

## Explicitly forbidden
- Hidden wall-clock dependence.
- Nondeterministic scheduling or race-based ordering.

## See also
- `docs/architecture/EXECUTION_MODEL.md`
- `docs/architecture/REPLAY_AND_TIME_ASYMMETRY.md`
- `docs/architecture/REPLAY_FORMAT.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
