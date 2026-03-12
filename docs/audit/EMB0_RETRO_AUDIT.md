Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# EMB0 Retro Audit

## Scope

This audit records the repository state before EMB-0 embodiment baseline work.

Audit targets:

- current input handling and camera mode surfaces
- existing player or embodied-agent assumptions
- runtime dependency on art or asset packs

## Existing Input And Camera Surfaces

The repository already contains deterministic camera/view processes and possession-aware movement.

Relevant surfaces:

- `tools/xstack/sessionx/process_runtime.py`
  - `process.control_bind_camera`
  - `process.camera_set_view_mode`
  - `process.control_set_view_lens`
  - `process.agent_move`
  - `process.agent_rotate`
  - `process.body_move_attempt`
- `data/registries/view_mode_registry.json`
  - `view.first_person.player`
  - `view.third_person.player`
  - `view.free.lab`
  - `view.free.observer_truth`
- `data/registries/view_policy_registry.json`
  - `view.first_person_diegetic`
  - `view.third_person_diegetic`
  - `view.freecam_lab`
  - `view.observer_truth`
- `data/registries/lenses.json`
  - diegetic body/instrument lenses
  - nondiegetic debug/freecam lenses

Audit conclusion:

- view-mode switching and lens gating already exist and are law/profile mediated
- EMB-0 does not need a second camera authority stack
- the missing piece is an explicit embodiment-layer registry and render-only lens transform helper

## Existing Embodied State Assumptions

The repository already uses body assemblies as primitive colliders and already treats agent movement as body-bound.

Relevant surfaces:

- `tools/xstack/sessionx/process_runtime.py`
  - `state["body_assemblies"]`
  - agent rows carrying `body_id`
  - `_agent_body_id(...)`
  - `_resolve_body_collisions(...)`
- `data/registries/body_shape_registry.json`
  - capsule support already declared
- existing tests:
  - `tools/xstack/testx/tests/test_embodied_move_determinism.py`
  - `tools/xstack/testx/tests/test_move_refuse_unembodied.py`
  - `tools/xstack/testx/tests/test_view_requires_embodiment_refusal.py`

Current gaps:

- no canonical body template registry
- no canonical body state row separate from raw body assemblies
- no explicit deterministic body input/tick process pair

Audit conclusion:

- EMB-0 can build on top of existing `body_assemblies` rather than inventing a new physical avatar type
- body template/state registries are the missing canonical layer

## Existing Physics And Gravity Coupling

The physics substrate already exposes momentum rows and gravity field sampling.

Relevant surfaces:

- `src/physics/momentum_engine.py`
  - `build_momentum_state(...)`
  - `apply_force_to_momentum_state(...)`
  - `apply_impulse_to_momentum_state(...)`
  - `velocity_from_momentum_state(...)`
- `tools/xstack/sessionx/process_runtime.py`
  - `process.apply_force`
  - `process.apply_impulse`
  - field sampling of `field.gravity_vector`
- `src/models/model_engine.py`
  - `model.phys_gravity_force`
- `data/registries/field_type_registry.json`
  - `field.gravity_vector`

Audit conclusion:

- EMB-0 can couple bodies to gravity through the existing PHYS field path
- no new physics-specific asset or simulation dependency is required

## Asset Dependency Audit

No current embodiment-critical surface requires meshes, skeletons, or texture packs.

Relevant surfaces:

- `body_assemblies` already use primitive shape descriptors
- camera/lens/view systems operate on transforms and profile gates only
- render tests already tolerate primitive-only entities

Audit conclusion:

- EMB-0 can remain fully art-free
- primitive capsule rendering is consistent with current renderer truth/presentation separation

## Audit Outcome

EMB-0 fits the current architecture if it does the following:

- define a canonical `template.body.pill`
- keep body motion inside authoritative processes
- reuse current view-mode and lens gating rather than duplicating it
- add deterministic lens transform helpers and body state rows without adding asset dependencies
