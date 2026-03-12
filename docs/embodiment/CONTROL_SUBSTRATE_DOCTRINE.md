Status: DERIVED
Last Reviewed: 2026-02-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon/glossary v1.0.0, process-only mutation, and session pipeline contracts.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Control Substrate Doctrine v1

## Purpose
Define canonical separation between Agent, Embodiment, Controller, and Representation so control semantics stay lawful, deterministic, and profile-driven.

## Orthogonal Roles
1. Agent
- Simulation ontology node that can receive intents.
- May exist with or without embodiment.

2. Embodiment
- Truth-side body binding for an agent.
- May be absent; unembodied agents remain valid intent targets.

3. Controller
- Intent generator/dispatcher identity.
- Can be player input, script, AI policy, spectator, or admin tooling.
- May exist with no active bindings.

4. Representation
- RenderModel-only presentation layer.
- Never authoritative; cannot mutate truth.

## Binding Types
1. Camera binding
- Controller targets a camera assembly (spectator/freecam workflows).

2. Possession binding
- Controller targets an agent for direct control routing.
- Default policy is single possessor per agent unless law explicitly permits otherwise.

3. Order binding
- Controller targets group/order channels.
- Declared as stub surface for later CIV prompts.

## Baseline Validity Requirements
1. Zero agents is valid.
2. Zero embodiments is valid.
3. Zero controllers is valid.
4. Agents that are never controlled are valid.

These states must boot, reach `stage.session_ready`, and run without implicit fallback mode flags.

## Mutation and Authority Rules
1. All control/binding mutations are Process-only.
2. UI/tools/renderer cannot mutate bindings directly.
3. Every control process is gated by:
- `LawProfile.allowed_processes`/`forbidden_processes`
- `AuthorityContext.entitlements`
- `AuthorityContext.privilege_level`

## Determinism Rules
1. Binding state is canonical and ordered deterministically.
2. Repeated replay with identical inputs yields identical hash anchors.
3. Conflict handling (for example already-possessed target) must emit stable refusal reason codes.

## Canonical Refusal Families
1. `refusal.control.entitlement_missing`
2. `refusal.control.law_forbidden`
3. `refusal.control.target_invalid`
4. `refusal.control.already_possessed`
5. `refusal.control.possession_not_supported`
6. `refusal.control.lens_forbidden`
7. `refusal.control.cross_shard_possession_forbidden`

## Non-Goals (EB-1)
1. Movement physics
2. Collision
3. Embodiment geometry primitives
4. Survival/crafting/inventory semantics
5. Client prediction/rollback

## Cross-References
- `docs/architecture/session_lifecycle.md`
- `docs/contracts/authority_context.md`
- `docs/contracts/law_profile.md`
- `docs/contracts/refusal_contract.md`
- `docs/architecture/truth_perceived_render.md`
