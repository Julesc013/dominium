Status: DERIVED
Version: 1.0.0

# Migration Status

- deprecations_registry: `data/governance/deprecations.json`
- topology_map: `docs/audit/TOPOLOGY_MAP.json`
- registry_validation: `pass`

## Lifecycle Counts
- deprecated: 9
- quarantined: 1

## Deadlines
- `data/registries/deprecation_registry.json` -> target `2.0.0` (deprecated)
- `schema/deprecation/deprecation_entry.schema` -> target `2.0.0` (quarantined)
- `src/client/interaction/interaction_dispatch.py#build_interaction_envelope` -> target `2.0.0` (deprecated)
- `src/client/interaction/interaction_dispatch.py#execute_affordance` -> target `2.0.0` (deprecated)
- `tools/control/control_cli.py#_execute_command` -> target `2.0.0` (deprecated)
- `tools/xstack/sessionx/observation.py#_interior_occlusion_bypass_allowed` -> target `2.0.0` (deprecated)
- `tools/xstack/sessionx/process_runtime.py#_civ_admin_override` -> target `2.0.0` (deprecated)
- `tools/xstack/sessionx/process_runtime.py#pending_task_completion_intents` -> target `2.0.0` (deprecated)
- `tools/xstack/sessionx/srz.py#build_intent_envelopes` -> target `2.0.0` (deprecated)
- `tools/xstack/sessionx/ui_host.py#dispatch_window_action` -> target `2.0.0` (deprecated)

## Deprecated and Quarantined
- `data/registries/deprecation_registry.json` (deprecated) -> `data/governance/deprecations.json`
- `schema/deprecation/deprecation_entry.schema` (quarantined) -> `schema/governance/deprecation_entry.schema`
- `src/client/interaction/interaction_dispatch.py#build_interaction_envelope` (deprecated) -> `src/control/control_plane_engine.py#build_control_envelope`
- `src/client/interaction/interaction_dispatch.py#execute_affordance` (deprecated) -> `src/control/control_plane_engine.py#resolve_and_execute`
- `tools/control/control_cli.py#_execute_command` (deprecated) -> `src/control/control_plane_engine.py#submit_control_intent`
- `tools/xstack/sessionx/observation.py#_interior_occlusion_bypass_allowed` (deprecated) -> `src/control/view_policy_engine.py#resolve_occlusion_bypass`
- `tools/xstack/sessionx/process_runtime.py#_civ_admin_override` (deprecated) -> `src/control/control_plane_engine.py#resolve_meta_override`
- `tools/xstack/sessionx/process_runtime.py#pending_task_completion_intents` (deprecated) -> `src/control/control_plane_engine.py#dispatch_completion_resolution`
- `tools/xstack/sessionx/srz.py#build_intent_envelopes` (deprecated) -> `src/control/control_plane_engine.py#emit_intent_envelopes`
- `tools/xstack/sessionx/ui_host.py#dispatch_window_action` (deprecated) -> `src/control/control_plane_engine.py#dispatch_window_control_intent`

## Remaining References
- `data/registries/deprecation_registry.json`: 11
  - `build/impact_graph.json`
  - `build/impact_graph.test.a.json`
  - `build/impact_graph.test.b.json`
  - `build/impact_graph.test.det.json`
  - `build/semantic_impact.latest.json`
  - `docs/audit/MIGRATION_STATUS.md`
  - `docs/audit/RETRO_CONSISTENCY_FRAMEWORK_BASELINE.md`
  - `docs/audit/TOPOLOGY_MAP.json`
  - `schemas/deprecation_entry.schema.json`
  - `tools/governance/adapters/deprecation_registry_adapter.py`
  - `tools/xstack/testx/tests/test_deprecation_registry_consistency.py`
- `schema/deprecation/deprecation_entry.schema`: 9
  - `build/auditx/changed_only_a/FINDINGS.json`
  - `build/auditx/changed_only_b/FINDINGS.json`
  - `build/auditx/smoke/FINDINGS.json`
  - `build/impact_graph.json`
  - `build/semantic_impact.latest.json`
  - `docs/audit/MIGRATION_STATUS.md`
  - `docs/audit/RETRO_CONSISTENCY_FRAMEWORK_BASELINE.md`
  - `docs/audit/TOPOLOGY_MAP.json`
  - `docs/audit/auditx/FINDINGS.json`
- `src/client/interaction/interaction_dispatch.py#build_interaction_envelope`: 1
  - `docs/audit/CTRL0_RETRO_AUDIT.md`
- `src/client/interaction/interaction_dispatch.py#execute_affordance`: 0
- `tools/control/control_cli.py#_execute_command`: 1
  - `docs/audit/CTRL0_RETRO_AUDIT.md`
- `tools/xstack/sessionx/observation.py#_interior_occlusion_bypass_allowed`: 1
  - `docs/audit/CTRL0_RETRO_AUDIT.md`
- `tools/xstack/sessionx/process_runtime.py#_civ_admin_override`: 1
  - `docs/audit/CTRL0_RETRO_AUDIT.md`
- `tools/xstack/sessionx/process_runtime.py#pending_task_completion_intents`: 1
  - `docs/audit/CTRL1_RETRO_AUDIT.md`
- `tools/xstack/sessionx/srz.py#build_intent_envelopes`: 1
  - `docs/audit/CTRL0_RETRO_AUDIT.md`
- `tools/xstack/sessionx/ui_host.py#dispatch_window_action`: 2
  - `docs/audit/CTRL0_RETRO_AUDIT.md`
  - `docs/audit/CTRL1_RETRO_AUDIT.md`

## Validation Errors
- none
