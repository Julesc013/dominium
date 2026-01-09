# SPEC_AI_DETERMINISM - Deterministic AI Contracts

This spec defines determinism requirements for all AI/planner subsystems.

## 1. Deterministic inputs
AI decisions are a deterministic function of:
- `tick_index` and `ups`,
- faction state (resources, policies, known nodes),
- world state digest (e.g., `dom_game_hash`),
- `ai_seed` per faction.

No other inputs are allowed.

## 2. Scheduling
- AI runs at discrete decision ticks (periodic, e.g., every N ticks).
- Decision ticks are deterministic and stored in scheduler state.
- AI is invoked at tick boundaries only.

## 3. Budgets and bounded cost
- AI must respect budgets:
  - `max_ops_per_tick`
  - `max_factions_per_tick`
- When budget is exceeded:
  - AI emits a deterministic "no-op" result,
  - AI logs a decision trace with a budget-hit reason,
  - AI MUST NOT block or defer to wall-clock time.

## 4. Outputs are explicit
AI outputs MUST be explicit and auditable:
- Commands (same pipeline as player commands), or
- Scheduled macro events.

AI MUST NOT:
- mutate authoritative state directly,
- reorder commands based on non-deterministic data,
- use wall-clock time or platform RNG.

## 5. Replay invariants
- Given the same inputs and seeds, AI outputs must be identical across replay.
- Deterministic ordering (by IDs and stable tie-break rules) is required.

## Related specs
- `docs/SPEC_FACTIONS.md`
- `docs/SPEC_AI_DECISION_TRACES.md`
- `docs/SPEC_DETERMINISM.md`
