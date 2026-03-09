Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# Embodiment Baseline Report

## Scope

This report records the EMB-0 embodiment baseline delivered for Dominium v0.0.0.

## Body System Template Summary

Implemented baseline:

- canonical body template `template.body.pill`
- primitive capsule collider only
- canonical `body_state` row with `subject_id`, `frame_id`, `position_ref`, and `orientation_ref`
- PHYS momentum state attached at body instantiation time
- deterministic template instance record emitted for spawned bodies

The embodiment body remains art-free.
Renderers may show primitive capsules or equivalent debug primitives without requiring meshes, textures, or skeletons.

## Movement Model Summary

Implemented motion processes:

- `process.body_apply_input`
- `process.body_tick`

Behavior:

- control intent resolves into deterministic force application
- PHYS momentum updates remain authoritative
- gravity couples through `field.gravity_vector`
- damping and integration are deterministic and replay-stable
- resulting `body_state` rows track the authoritative body transform after each lawful motion step

## Lens Modes And Gating

Implemented lens profiles:

- `lens.fp`
- `lens.tp`
- `lens.freecam`
- `lens.inspect`

Gating model:

- first-person and third-person remain embodied/diegetic
- freecam requires dev-style nondiegetic access entitlements
- inspect requires elevated observer/override entitlements
- lens helpers emit render-facing camera state only and do not mutate truth directly

## UX Readiness

MVP runtime bootstrap now exposes embodiment defaults for:

- `template.body.pill`
- default lens profile selection
- move input binding
- look input binding
- toggle-lens binding
- teleport binding

This is sufficient for UX-0 freecam traversal and v0.0.0 packaging/bootstrap work.

## Forward Readiness

EMB-0 is ready for:

- freecam traversal and lawful camera switching
- later tool interactions built on top of the body baseline
- future embodiment extensions such as jump, crouch, fall damage, and richer interaction surfaces without changing the base body identity contract
