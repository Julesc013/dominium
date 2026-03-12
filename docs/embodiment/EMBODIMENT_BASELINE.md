Status: CANONICAL
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Embodiment Baseline

This document freezes the EMB-0 embodiment baseline contract for Dominium v0.0.0.

It is subordinate to:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/mvp/MVP_RUNTIME_BUNDLE.md`

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A3` Observer and truth remain separate
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E2` Deterministic ordering
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/canon/constitution_v1.md` `E7` Cross-platform replay agreement

## 1. Scope

EMB-0 defines the minimal embodied presence for MVP v0.0.0.

EMB-0 includes:

- a canonical body system template using primitive capsule geometry
- deterministic body state and momentum coupling
- deterministic body input and body tick processes
- first-person, third-person, freecam, and inspect lens profiles
- profile-gated view selection

EMB-0 does not include:

- inventories
- crafting
- skeletal animation
- character art assets
- jump, crouch, or combat movement extensions

## 2. Body As System

The canonical body template is `template.body.pill`.

The body is a SYS template that binds:

- a primitive collider with `collider_kind = capsule`
- a deterministic mass value
- a deterministic movement parameter reference
- a momentum state carried by PHYS
- a body state carried as a canonical embodiment row

The body template interface exposes:

- control input:
  - local move vector
  - local look vector
- outputs:
  - `position_ref`
  - `velocity`
  - `orientation`

The authoritative motion state remains process-governed.
Renderers consume the resulting transform and may show capsule primitives only.

## 3. Movement Model

Movement is a deterministic process pair:

- `process.body_apply_input`
- `process.body_tick`

Rules:

- `process.body_apply_input` converts move/look control intent into momentum change and orientation updates
- `process.body_tick` applies gravity, deterministic damping, and momentum-to-position integration
- all authoritative body motion must occur through these processes or other explicit movement processes
- no UI, renderer, or tool may write body transforms directly

MVP movement behavior is intentionally minimal:

- walk acceleration only
- deterministic horizontal damping only
- no jump
- no crouch
- no fall damage yet

## 4. Gravity Coupling

Bodies couple to PHYS through the GEO-bound gravity field.

Rules:

- body tick samples `field.gravity_vector` at the body position
- gravity force is recorded as a deterministic process-local PHYS application
- the constitutive reference remains `model.phys_gravity_force`
- missing gravity field samples degrade to zero force, not wall-clock or platform defaults

## 5. Lens Profiles

EMB-0 declares four canonical embodiment lens profiles:

- `lens.fp`
- `lens.tp`
- `lens.freecam`
- `lens.inspect`

These profiles map onto the existing lawful view and lens surfaces rather than bypassing them.

Required semantics:

- `lens.fp`
  - embodied first-person follow
  - diegetic lens only
- `lens.tp`
  - embodied third-person follow with deterministic offset
  - diegetic lens only
- `lens.freecam`
  - detached free camera for dev/lab profiles only
  - profile gated
- `lens.inspect`
  - detached inspection view for observer/admin contexts only
  - profile gated
  - must not mutate truth

Lens transforms produce render-facing camera state only.
They are not an authority path.

## 6. Epistemics

View access is profile mediated.

Rules:

- freecam is dev/lab profile gated
- inspect is observer/admin gated
- a view mode may require embodiment before it binds to a target
- a lens profile may resolve to a lawful fallback if the requested view/lens combination is forbidden
- inspect output must reveal only information permitted by the active law profile, lens, and authority context

## 7. Geometry And Topology Neutrality

EMB-0 must operate across GEO profiles.

Rules:

- body state stores `frame_id` and `position_ref`
- movement operates on current frame transforms and GEO metric assumptions already selected by the runtime bundle
- first-person and third-person lenses derive transforms from body state, not hardcoded Euclidean-only camera hacks

## 8. Asset Independence

EMB-0 is art-free by constitution.

Rules:

- no textures are required
- no meshes are required
- no character skeleton is required
- the canonical embodiment visualization is a primitive capsule or equivalent debug primitive

## 9. MVP Success Surface

EMB-0 is complete when the repository can deterministically:

- instantiate `template.body.pill`
- attach momentum and body state rows
- apply gravity to the body through PHYS field sampling
- move the body via process-only motion
- switch between lawful first-person, third-person, freecam, and inspect lenses according to profile gates
- replay the embodiment state hash equivalently across repeated runs
