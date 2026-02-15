Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/universe_state.schema.json` v1.0.0, `schemas/law_profile.schema.json` v1.0.0, and SessionX process runtime.

# Camera and Navigation v1

## Purpose
Define process-driven lab camera navigation and deterministic time control without introducing gameplay systems.

## Camera Assembly (`TruthModel` / `UniverseState`)
`camera.main` fields:
- `assembly_id`
- `frame_id`
- `position_mm` (`x`, `y`, `z`, integer fixed-point millimeters)
- `orientation_mdeg` (`yaw`, `pitch`, `roll`, integer millidegrees)
- `velocity_mm_per_tick` (`x`, `y`, `z`, integer)
- `lens_id`

Camera seed definition is pack-provided:
- `packs/core/pack.core.camera/data/camera_assembly.main.json`
- contribution id: `registry.camera.assembly.main`

## Process Definitions
- `process.camera_move`
  - inputs: `delta_local_mm{x,y,z}`, `dt_ticks`
  - mutates: `camera.main.position_mm`, `camera.main.velocity_mm_per_tick`
- `process.camera_teleport`
  - inputs (deterministic target selection):
    - `target_site_id`
    - or `target_object_id`
    - or direct coordinates via `target_frame_id` (or legacy `frame_id`) + `position_mm{x,y,z}` + `orientation_mdeg{yaw,pitch,roll}`
  - mutates: `camera.main.frame_id`, `position_mm`, `orientation_mdeg`, `velocity_mm_per_tick`
- `process.time_control_set_rate`
  - input: `rate_permille`
  - mutates: `time_control.rate_permille`, `time_control.paused`
- `process.time_pause`
  - mutates: `time_control.paused = true`
- `process.time_resume`
  - mutates: `time_control.paused = false`
- `process.region_management_tick`
  - inputs: none (policy-driven)
  - mutates: `interest_regions`, `macro_capsules`, `micro_regions`, `performance_state`
  - deterministic transition order: collapse first, then expand

All authoritative mutation occurs through process dispatch (`tools/xstack/sessionx/process_runtime.py`).

## Authority Mapping
Entitlement gates:
- `process.camera_move` -> `entitlement.camera_control`
- `process.camera_teleport` -> `entitlement.teleport`
- `process.region_management_tick` -> `session.boot`
- `process.time_control_set_rate` -> `entitlement.time_control`
- `process.time_pause` -> `entitlement.time_control`
- `process.time_resume` -> `entitlement.time_control`

Privilege floors:
- `camera_move`: `observer`
- `camera_teleport`: `operator`
- `region_management_tick`: `observer`
- `time_control_*`: `operator`

Law profile source:
- `packs/law/law.lab.unrestricted/data/law_profile.unrestricted.json`

## Intent Pipeline (Headless)
`Input -> Intent -> Process -> TruthModel -> Observation Kernel -> PerceivedModel`

CLI:
```text
tools/xstack/session_script_run saves/<save_id>/session_spec.json tools/xstack/testdata/session/script.camera_nav.fixture.json
```

Teleport resolution source is compiled registry data only:
- `build/registries/astronomy.catalog.index.json`
- `build/registries/site.registry.index.json`

No raw pack reads are performed during process execution.

## Tool UI Binding (Prompt 10)
Descriptor-driven lab windows are compiled into `ui.registry.json` and bind to PerceivedModel channels only:
- `window.tool.navigator` uses `navigation.hierarchy`
- `window.tool.goto` uses `navigation.search_results`
- `window.tool.site_browser` uses `sites.entries`
- `window.tool.time` uses `time.summary` and emits time-control process intents
- `window.tool.log` uses `process_log.entries` and `tool.log.entries`
- `window.tool.inspector` uses `entities.entries` and `entities.selected_fields`

UI actions emit intents through the same process runtime:
- No direct authoritative field mutation from UI.
- Refusals are surfaced in tool log using refusal contract reason codes.

Gating:
- Law gate: nondiegetic overlays require `debug_allowances.allow_nondiegetic_overlays=true`.
- Entitlement gate:
  - navigator/goto/site browser -> `entitlement.teleport`
  - time window -> `entitlement.time_control`
  - inspector -> `entitlement.inspect`
  - log viewer -> `entitlement.inspect`

## Determinism Invariants
- Fixed-point integer camera math only (mm, mdeg).
- Deterministic process ordering follows script order.
- Each process appends deterministic `process_log` entry including `state_hash_anchor`.
- Identical script + session inputs produce identical:
  - `state_hash_anchors[]`
  - final state hash
  - PerceivedModel hash
  - run-meta deterministic fields hash
- Region transitions preserve `mass_stub` conservation; violations refuse with `CONSERVATION_VIOLATION`.
- Budget overrun behavior is deterministic:
  - degrade/cap under `degrade_fidelity`
  - refuse under `refuse` fallback.

## Refusal Codes
- `PROCESS_FORBIDDEN`
- `ENTITLEMENT_MISSING`
- `PRIVILEGE_INSUFFICIENT`
- `PROCESS_INPUT_INVALID`
- `REGISTRY_MISSING`
- `TARGET_NOT_FOUND`

Reserved for future name-query flows:
- `TARGET_AMBIGUOUS`
- `BUDGET_EXCEEDED`
- `CONSERVATION_VIOLATION`

## Teleport Default Rules
- `target_site_id`:
  - resolves to site `frame_id` and deterministic position conversion.
- `target_object_id`:
  - resolves to object `frame_id`
  - default position = `+Z` at deterministic distance `max(1000, sphere_radius_mm * 2)` (or fallback `1_000_000 mm`).
- direct coordinates:
  - uses provided frame and transform fields verbatim after validation.

## Example Script Snippet
```json
{
  "intents": [
    {
      "intent_id": "intent.001",
      "process_id": "process.camera_move",
      "inputs": {
        "delta_local_mm": {
          "x": 1000,
          "y": 0,
          "z": 0
        },
        "dt_ticks": 1
      }
    },
    {
      "intent_id": "intent.003",
      "process_id": "process.camera_teleport",
      "inputs": {
        "frame_id": "frame.world",
        "position_mm": {
          "x": 42000,
          "y": -12000,
          "z": 8000
        },
        "orientation_mdeg": {
          "yaw": 90000,
          "pitch": -5000,
          "roll": 0
        }
      }
    }
  ]
}
```

## TODO
- Move camera assembly/process descriptors into typed registry outputs (currently read via `registry_entries` contribution payload).
- Add SRZ/threaded scheduler semantics beyond deterministic single-worker stub.
- Add coordinate-frame transform catalog for teleport targets by object/site id.
- Add optional deterministic facing rules per site kind.
- Add dedicated read-only performance monitor tool window descriptor for `PerceivedModel.performance.*`.

## Cross-References
- `docs/architecture/truth_model.md`
- `docs/architecture/observation_kernel.md`
- `docs/architecture/time_model.md`
- `docs/architecture/interest_regions.md`
- `docs/architecture/macro_capsules.md`
- `docs/architecture/budget_policy.md`
- `docs/architecture/fidelity_policy.md`
- `docs/architecture/astronomy_catalogs.md`
- `docs/architecture/site_registry.md`
- `docs/architecture/ui_registry.md`
- `docs/contracts/authority_context.md`
- `docs/contracts/law_profile.md`
- `docs/contracts/refusal_contract.md`
