--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time, deterministic scheduling primitives, and command envelopes.
GAME:
- Doctrine application rules and evaluation ordering.
SCHEMA:
- Doctrine data formats, constraints, and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No agent-only mechanics or hidden simulation shortcuts.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_AGENT_DOCTRINE - Doctrine Policy (AGENT2)

Status: draft
Version: 1

## Purpose
Define doctrine as a declarative policy that constrains agent goal selection.
Doctrine never executes actions; it only limits and adjusts goal evaluation.

## Doctrine schema
Required fields:
- doctrine_id
- owner_ref (person/org/jurisdiction)
- scope (agent/cohort/org/jurisdiction)
- allowed_goal_types (bounded set)
- forbidden_goal_types (bounded set)
- priority_modifiers (per goal type)
- scheduling_policy
- expiry_act (optional)
- provenance_ref

Recommended fields:
- authority_required_mask
- legitimacy_min
- created_act

## Doctrine application
- Goals outside doctrine are ignored.
- Goals inside doctrine have priority adjusted deterministically.
- Conflicting doctrines resolve in order:
  1) explicit context
  2) role doctrine
  3) org doctrine
  4) jurisdiction doctrine
  5) personal fallback
  6) refusal

## Scheduling policy
Doctrine may constrain when agents can act via:
- minimum think intervals
- optional ACT windows

No per-tick reevaluation is allowed.

## Determinism rules
- No floats, RNG, or OS time.
- Stable ordering by doctrine_id and goal_id.
- All doctrine changes are scheduled events.

## Prohibitions
- Doctrine MUST NOT execute actions.
- Doctrine MUST NOT bypass command or authority systems.

## Test plan (spec-level)
Required scenarios:
- Deterministic filtering of goals by doctrine.
- Deterministic priority modification.
- Deterministic resolution of conflicting doctrines.
- Batch vs step equivalence for doctrine updates.
