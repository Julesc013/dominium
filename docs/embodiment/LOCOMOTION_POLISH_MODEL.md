Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# Locomotion Polish Model

This document freezes the EMB-2 locomotion polish contract for Dominium v0.0.0.

It is subordinate to:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/embodiment/EMBODIMENT_BASELINE.md`
- `docs/embodiment/TERRAIN_COLLISION_MODEL.md`

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A3` Law-gated authority
- `docs/canon/constitution_v1.md` `A7` Observer-renderer-truth separation
- `docs/canon/constitution_v1.md` `E2` Deterministic ordering
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/canon/constitution_v1.md` `E7` Hash-partition equivalence

## 1. Scope

EMB-2 adds locomotion feel polish without changing the EMB-0 body identity contract.

EMB-2 includes:

- deterministic jump as a lawful optional impulse
- deterministic render-only camera smoothing for first-person and third-person views
- deterministic impact logging at terrain contact
- model-driven horizontal damping using terrain friction proxy when available

EMB-2 does not include:

- health
- injury
- death
- ragdolls
- rigid-body stacks

## 2. Jump

`process.body_jump` is the canonical jump process.

Rules:

- Jump is optional and profile gated.
- Preconditions:
  - `grounded == true`
  - `ent.move.jump` is present in `AuthorityContext`
  - the active `LawProfile` allows `process.body_jump`
- The process applies a deterministic upward impulse in the body local up axis.
- Jump cooldown, if non-zero, is tick-based only.
- Jump clears grounded state until the next lawful terrain contact clamp.

Refusals must remain deterministic:

- `refusal.move.jump_not_grounded`
- `refusal.move.jump_cooldown`

## 3. Camera Smoothing

Camera smoothing is render-only.

Rules:

- Smoothing applies only to the derived FP/TP camera transform.
- The smoothing helper consumes:
  - target camera transform
  - previous render camera transform
  - `camera_smoothing_params`
- The helper uses fixed-point bounded blending.
- There is no time-based exponential using wall-clock time.
- No smoothing state may mutate authoritative body or camera truth.

MVP semantics:

- smoothing affects follow position only
- camera orientation remains directly aligned to the target transform
- smoothing is disabled for freecam and inspect

## 4. Impact Hooks

Impact hooks do not change survival state.

Rules:

- On terrain ground clamp, capture pre-clamp downward speed.
- If speed exceeds the configured threshold, emit a canonical `impact_event`.
- The event is informational and replay-relevant.
- The explain surface is `explain.impact_event`.
- No health, injury, or death effect is applied by EMB-2.

## 5. Friction Model

Horizontal damping is model driven.

Inputs:

- base movement damping from the body template
- terrain slope response from EARTH-6
- optional `field.friction` proxy if available at the current body position

Rules:

- missing friction field degrades to deterministic default `1000`
- slope and friction modifiers remain bounded and integer-only
- the resulting horizontal damping remains clamped to the legal body-movement range

## 6. Debug And UX Surface

EMB-2 exposes:

- `move jump` command surface when entitled
- derived debug state for:
  - grounded
  - jump cooldown remaining
  - last impact speed

These surfaces are profile gated and must not bypass epistemic policy.

## 7. Proof And Replay

Proof requirements:

- jump impulses remain visible through canonical momentum/impulse rows
- impact events participate in proof and replay when present
- camera smoothing is excluded from authoritative truth proofs because it is render-only

## 8. Success Surface

EMB-2 is complete when the repository can deterministically:

- refuse jump without entitlement
- refuse jump while airborne
- apply a lawful upward jump impulse when grounded
- emit impact events for above-threshold terrain contacts
- apply deterministic friction-tuned damping
- smooth FP/TP camera output without mutating truth
