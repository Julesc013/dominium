Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Affordance Extension Contract

Status: CANONICAL
Last Updated: 2026-03-03
Scope: COMPLETENESS-1 extension governance for future series/domain work.

## 1) Purpose

This contract defines non-negotiable declaration requirements for any new domain series (for example ELEC/LOGIC/DOM/ECO/SCI/MIL/ADV).
No feature series may be accepted without explicit RWAM mapping and substrate/tier declarations.

## 2) Required Declaration Block

Every new series must provide, at minimum:

1. RWAM mapping
- map to one or more canonical affordance IDs from `data/meta/real_world_affordance_matrix.json`
- declare coverage as implemented or planned

2. Substrate mapping
- declare which existing substrates are used:
  - Graph
  - Flow
  - Constraint
  - State
  - Hazard
  - Schedule
  - Spec
  - Field
  - Action
  - Info
  - Control
- no bespoke substrate bypasses

3. Tier behavior
- declare macro/meso/micro behavior and transitions
- declare degradation/refusal behavior under budget pressure

4. Determinism contract
- deterministic ordering keys
- named RNG streams only (if randomness is required)
- thread-count invariance statement

5. Replay/proof impact
- state what events/hashes are added to proof bundles
- state reenactment/replay implications and hash anchors

## 3) Enforcement Hooks

Mandatory checks:

- RepoX `INV-AFFORDANCE-DECLARED`
- AuditX `AffordanceGapSmell`
- TestX RWAM presence/mapping/schema checks

## 4) Amendment Rule

No new ontology primitives may be introduced without constitutional amendment.
Complex features must be compositions over existing canonical affordances and substrates.

## 5) Non-Goals

- no runtime semantic changes
- no solver implementation requirements
- no optional-pack boot requirements
