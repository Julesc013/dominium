Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
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
- `docs/specs/SPEC_FACTIONS.md`
- `docs/specs/SPEC_AI_DECISION_TRACES.md`
- `docs/specs/SPEC_DETERMINISM.md`