Status: DERIVED
Last Reviewed: 2026-03-01
Scope: CTRL-7 retro-consistency audit for capability-driven control
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# CTRL7 Retro-Consistency Audit

## Canon Inputs
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/control/CONTROL_PLANE_CONSTITUTION.md`
- `AGENTS.md`

## Audit Method
- Type/class branch scan:
  - `rg -n "entity_type|assembly_type|vehicle|building|machine_type|plan_type_id ==|target_kind ==|isinstance\\(" src tools -g "*.py"`
- Feature flag scan:
  - `rg -n "has_|can_be_|supports_|requires_" src tools -g "*.py"`
- Control resolution capability usage scan:
  - `rg -n "required_capabilities|build_control_resolution|control_action_rows_by_id" src tools -g "*.py"`

## Findings

### F1 - Control resolution does not enforce target capability bindings
- Paths:
  - `src/control/control_plane_engine.py`
- Current state:
  - `control_action.required_capabilities` is normalized but not validated against target bindings.
  - Allowed/refused outcomes are currently driven by law/policy/entitlements, not target capability presence.
- Risk:
  - Actions can be approved for targets that do not expose required feature capabilities.

### F2 - Planning path still branches on plan type for blueprint behavior
- Paths:
  - `src/control/planning/plan_engine.py`
- Current state:
  - Blueprint compile/execution selection uses `plan_type_id == "structure"` branches.
  - Planning eligibility does not query `capability.can_be_planned`.
- Risk:
  - Planning behavior remains partially type-driven and brittle across future entity expansions.

### F3 - Pose and port process paths do not gate by capability bindings
- Paths:
  - `tools/xstack/sessionx/process_runtime.py`
- Current state:
  - `process.pose_enter/process.pose_exit` validate occupancy/access but not `capability.has_pose_slots`.
  - `process.port_*` validate row existence/type but not `capability.has_ports`.
- Risk:
  - Feature affordances are inferred from row presence, not explicit capability contracts.

### F4 - ActionSurface resolution has no capability requirement filter
- Paths:
  - `src/interaction/action_surface_engine.py`
- Current state:
  - Surface eligibility is gated by law/tool/visibility but not target capability requirements.
- Risk:
  - Surface affordances can surface on entities lacking intended capabilities.

### F5 - Capability visibility is missing from inspection snapshots
- Paths:
  - `src/inspection/inspection_engine.py`
  - `data/registries/inspection_section_registry.json`
- Current state:
  - No `section.capabilities_summary` output exists.
- Risk:
  - Capability state is not auditable/inspectable through deterministic inspection pathways.

### F6 - No canonical capability registry/binding subsystem exists yet
- Paths:
  - missing: `src/control/capability/*`
  - missing: `data/registries/capability_registry.json`
- Current state:
  - Capability IDs are referenced in control action/IR static requirements but no unified registry + binding query engine exists.
- Risk:
  - Capability checks can drift across modules and fallback to ad-hoc assumptions.

## Migration Plan
1. Introduce canonical capability artifacts:
   - `schema/control/capability.schema`
   - `schema/control/capability_binding.schema`
   - `data/registries/capability_registry.json`
2. Add deterministic capability engine:
   - `src/control/capability/capability_engine.py`
   - Pure query APIs with deterministic ordering.
3. Integrate capability checks into control and interaction:
   - Control resolution validates `required_capabilities` against target capability bindings.
   - ActionSurface optionally filters by target required capabilities.
4. Migrate type-branch hotspots:
   - Planning blueprint path uses capability presence (`capability.can_be_planned`) as primary gate.
   - Pose and port processes gate target entities by `capability.has_pose_slots` / `capability.has_ports`.
5. Add inspection visibility:
   - `section.capabilities_summary` with epistemic redaction handling.
6. Add RepoX/AuditX enforcement:
   - `INV-NO-TYPE-BRANCHING`
   - `INV-CAPABILITY-REGISTRY-REQUIRED`
   - `TypeBranchSmell`
   - `HiddenFeatureFlagSmell`

## Invariants Mapped
- A1 Determinism primary (`constitution_v1.md` §3 A1)
- A2 Process-only mutation (`constitution_v1.md` §3 A2)
- A3 Law-gated authority (`constitution_v1.md` §3 A3)
- A9 Pack-driven integration (`constitution_v1.md` §3 A9)
- A10 Explicit degradation/refusal (`constitution_v1.md` §3 A10)
