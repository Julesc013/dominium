--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time, deterministic scheduling primitives, and command envelopes.
GAME:
- Refinement and collapse rules, provenance handling, and event scheduling.
SCHEMA:
- Refinement/collapse formats, constraints, and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No random sampling or hidden AI decisions.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_AGENT_REFINEMENT - Refinement and Collapse (AGENT3)

Status: draft
Version: 1

## Purpose
Define deterministic refinement and collapse transitions between aggregate and
individual agent representations.

## Refinement schema
Required fields:
- aggregate_agent_id
- candidate_ids (bounded list)
- selected_ids (bounded list)
- desired_count
- trigger_act
- provenance_ref

## Collapse schema
Required fields:
- aggregate_agent_id
- individual_refs (bounded list)
- belief_summary
- goal_summary
- trigger_act
- provenance_ref

## Refinement rules
- Selection is deterministic by stable person_id and role relevance.
- No random sampling.
- No new agents fabricated.

## Collapse rules
- Preserve counts, doctrine compliance, and belief uncertainty bounds.
- No commands are lost or duplicated.
- Interest set blocks collapse when required.

## Determinism rules
- Batch vs step equivalence required for refine/collapse schedules.
- Stable ordering keys for event processing.

## Refusal codes
- REFINEMENT_LIMIT_REACHED
- COLLAPSE_BLOCKED_BY_INTEREST
- AGENT_STATE_INCONSISTENT

## Prohibitions
- No per-tick agent simulation.
- No hidden authority or doctrine bypass.

## Test plan (spec-level)
Required scenarios:
- Deterministic refinement selection.
- Deterministic collapse from permuted inputs.
- Batch vs step equivalence for refinement/collapse scheduling.
