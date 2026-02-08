Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Command Graph: Camera And Blueprint

## Canonical Commands

### `camera.set_mode`
- Required capabilities:
  - `ui.camera.mode.embodied` (baseline)
- Additional mode constraints:
  - `memory` mode requires `ui.camera.mode.memory`
  - `observer` mode requires `ui.camera.mode.observer` and `tool.truth.view`
- Epistemic scope:
  - `obs_only` for embodied mode
  - `memory_only` for memory mode
  - tool truth scope only with entitlement
- Refusal reason codes:
  - `CAMERA_REFUSE_POLICY`
  - `CAMERA_REFUSE_ENTITLEMENT`
  - `CAMERA_REFUSE_WORLD_INACTIVE`
  - `CAMERA_REFUSE_USAGE`

### `camera.set_pose`
- Required capabilities:
  - `ui.camera.mode.embodied`
- Epistemic scope:
  - `obs_only`
- Refusal reason codes:
  - `CAMERA_REFUSE_POLICY`
  - `CAMERA_REFUSE_WORLD_INACTIVE`
  - `CAMERA_REFUSE_USAGE`

### `blueprint.preview`
- Required capabilities:
  - `ui.blueprint.preview`
- Epistemic scope:
  - `memory_only`
- Refusal reason codes:
  - `BLUEPRINT_REFUSE_CAPABILITY`
  - `BLUEPRINT_REFUSE_WORLD_INACTIVE`
  - `BLUEPRINT_REFUSE_USAGE`

### `blueprint.place`
- Required capabilities:
  - `ui.blueprint.place`
- Epistemic scope:
  - `obs_only`
- Refusal reason codes:
  - `BLUEPRINT_REFUSE_CAPABILITY`
  - `BLUEPRINT_REFUSE_WORLD_INACTIVE`
  - `BLUEPRINT_REFUSE_USAGE`

## Binding Rule
- CLI is canonical.
- TUI/GUI invoke only canonical command ids.
- UI logic cannot bypass canonical command dispatch.

