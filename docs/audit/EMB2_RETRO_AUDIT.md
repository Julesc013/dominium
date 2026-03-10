Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# EMB2 Retro Audit

Task: EMB-2 Locomotion Polish

## Scope

Audited surfaces:

- `tools/xstack/sessionx/process_runtime.py`
- `src/embodiment/body/body_system.py`
- `src/embodiment/collision/macro_heightfield_provider.py`
- `src/embodiment/lens/lens_engine.py`
- `src/client/ui/viewer_shell.py`
- `tools/embodiment/tool_replay_movement_window.py`
- `tools/embodiment/earth6_probe.py`
- `data/registries/body_template_registry.json`
- `data/registries/lens_profile_registry.json`
- `data/registries/entitlement_registry.json`
- `data/registries/movement_slope_params_registry.json`

## Findings

1. Movement params and slope modifiers
- `process.body_apply_input` already resolves walk acceleration, look rate, and slope response from deterministic registry-backed helpers.
- `process.body_tick` already applies gravity, horizontal damping, terrain collision, and body-state mirroring.

2. Grounded state source of truth
- Grounded state is computed in `_apply_ground_contact(...)` after momentum integration and terrain sampling.
- The grounded/clamped result is mirrored into `body.extensions.terrain_collision_state` and then into `body_state.extensions`.
- This is the correct insertion point for impact detection because it observes pre-clamp vertical speed and post-clamp contact outcome in one deterministic branch.

3. Lens smoothing behavior
- Third-person smoothing currently lives inside `src/embodiment/lens/lens_engine.py` and is invoked from both viewer-side helpers and `process.body_tick`.
- That means smoothing currently leaks into process-driven camera updates.
- EMB-2 should move smoothing to a render-only helper so camera polish does not mutate authoritative state.

4. Float risk
- Authoritative embodiment movement paths are fixed-point/int based.
- Current inline lens smoothing is integer-only.
- No float-based authoritative smoothing was found in embodiment/collision code paths.

5. Terrain/collision surface
- EARTH-6 already exposes deterministic macro terrain height and slope queries through `resolve_macro_heightfield_sample(...)`.
- This provides the necessary height and gradient data for jump grounding checks, friction tuning, and impact hooks without adding new terrain queries.

6. Command exposure
- Viewer shell and runtime bundle already expose movement, look, lens toggle, and EMB-1 tool commands.
- There is no existing `move jump` command surface, and no existing `process.body_jump`.

## Minimum Safe Integration Points

- Add `process.body_jump` beside `process.body_apply_input` and `process.body_tick`.
- Add impact logging inside `_apply_ground_contact(...)` consumers in `process.body_tick`.
- Replace inline third-person smoothing in `resolve_lens_camera_state(...)` with a render-only smoothing helper invoked by `viewer_shell`.
- Extend debug/viewer surfaces with grounded and jump cooldown summaries only through derived payloads.

## Risks To Avoid

- Do not write body transforms from lens/camera code.
- Do not add wall-clock or float-dependent smoothing to authoritative paths.
- Do not bypass process entitlement/law validation for jump.
- Do not couple impact hooks to health or injury systems.
