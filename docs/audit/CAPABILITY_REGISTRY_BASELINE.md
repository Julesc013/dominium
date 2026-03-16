Status: DERIVED
Last Reviewed: 2026-03-01
Supersedes: none
Superseded By: none
Scope: CTRL-7 capability registry enforcement, migration, and tests
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Capability Registry Baseline

## Capability Definitions
- Canonical registry: `data/registries/capability_registry.json`
- Baseline capability IDs:
  - `capability.has_interior`
  - `capability.has_pose_slots`
  - `capability.has_ports`
  - `capability.can_be_driven`
  - `capability.has_guide_geometry`
  - `capability.has_power_network`
  - `capability.has_flow_network`
  - `capability.is_pressurized`
  - `capability.can_be_planned`
  - `capability.can_mount`
  - `capability.can_attach`
  - `capability.can_emit_signal`
- Action-required capability IDs from control action registry are validated against this registry via RepoX invariant checks.

## Migration Summary
- Control-plane resolution now enforces action `required_capabilities` through deterministic capability bindings (`src/control/control_plane_engine.py` + `src/control/capability/capability_engine.py`).
- Planning path migrated from type-branching to capability checks:
  - blueprint compile gate uses `capability.can_be_planned` when capability bindings are present (`src/control/planning/plan_engine.py`).
- POSE and ports runtime checks now gate with:
  - `capability.has_pose_slots`
  - `capability.has_ports`
  - enforcement path in `tools/xstack/sessionx/process_runtime.py`.
- Inspection adds `section.capabilities_summary` with epistemic redaction behavior (`src/inspection/inspection_engine.py`).

## Enforcement Rules
- RepoX:
  - `INV-NO-TYPE-BRANCHING`
  - `INV-CAPABILITY-REGISTRY-REQUIRED`
- AuditX:
  - `E125_TYPE_BRANCH_SMELL` (`TypeBranchSmell`)
  - `E126_HIDDEN_FEATURE_FLAG_SMELL` (`HiddenFeatureFlagSmell`)

## TestX Coverage
- `test_capability_binding_deterministic`
- `test_control_resolution_uses_capability`
- `test_planning_requires_capability`
- `test_no_type_branching_detected`
- `test_capability_inspection_redaction`

## Extension Points (MOB)
- `capability.has_guide_geometry` for track/route guidance eligibility.
- `capability.can_be_driven` parameterization (`control_binding_id`, `max_occupants`) for vehicle control adapters.
- Future MOB dock/track systems should add new capabilities to registry and bind via `capability_binding`, not class/type forks.

## Gate Run Log
- RepoX (`python tools/xstack/repox/check.py --repo-root . --profile STRICT`):
  - `status=pass`
  - findings: 1 warning (`INV-AUDITX-REPORT-STRUCTURE` threshold warning)
- AuditX (`python tools/xstack/auditx/check.py --repo-root . --profile STRICT`):
  - `status=pass`
  - scan completed with warnings (non-gating)
- TestX required CTRL-7 subset:
  - command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_capability_binding_deterministic,test_control_resolution_uses_capability,test_planning_requires_capability,test_no_type_branching_detected,test_capability_inspection_redaction`
  - `status=pass` (5/5)
- Strict profile build (`python tools/xstack/run.py strict --repo-root . --cache on`):
  - `status=error` (pre-existing non-CTRL7 blockers)
  - `compatx` refusal findings
  - `testx` full-suite failures outside CTRL-7 subset
  - packaging tool crash due missing `build/dist.lab_validation.a/packs/derived/org.dominium.earth.tiles/data/earth_tile_pyramid.json`
- Topology map updated:
  - `python tools/governance/tool_topology_generate.py --repo-root .`
  - fingerprint: `3d94ab48d04f9d29d68114f24fa67fa0e2329e653b87cfa4e8234832941b97c9`
