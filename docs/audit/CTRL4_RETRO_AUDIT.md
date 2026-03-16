Status: DERIVED
Last Reviewed: 2026-03-01
Supersedes: none
Superseded By: none
Scope: CTRL-4 Phase 0 retro-consistency audit
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CTRL4 Retro-Consistency Audit

## Canon Inputs
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/control/CONTROL_PLANE_CONSTITUTION.md`
- `docs/architecture/RETRO_CONSISTENCY_AUDIT_FRAMEWORK.md`

## Audit Method
- Planning/execution mutation scan:
  - `rg -n "construction_project_create|tick_construction_projects|installed_structure|build_blueprint_execution_ir|compile_blueprint_artifacts" src tools -g "*.py"`
- UI placement/ghost scan:
  - `rg -n "blueprint_place_ghost|preview|ghost|inspection_overlays|construction_overlay" src data -g "*.py" -g "*.json"`
- Commitment bypass scan:
  - `rg -n "installed_node_states|event.install_part|status = \"completed\"|construction_commitments" src/tools -g "*.py"`

## Findings

### F1 - Blueprint compile and construction state creation are coupled in execution path
- Paths:
  - `tools/xstack/sessionx/process_runtime.py` (`process.construction_project_create`)
  - `src/materials/construction/construction_engine.py` (`create_construction_project`)
- Current state:
  - Construction create path compiles blueprint artifacts and immediately mutates authoritative construction state (`construction_projects`, `construction_steps`, `construction_commitments`, `installed_structure_instances`).
  - Blueprint execution IR is generated and attached as extension metadata, but is not the authoritative gate for execution.
- Risk:
  - Planning and execution semantics are mixed; plan lifecycle is not first-class and auditable.

### F2 - Installation progression still mutates installed structure state directly in tick loop
- Paths:
  - `src/materials/construction/construction_engine.py` (`tick_construction_projects`)
  - `tools/xstack/sessionx/process_runtime.py` (`process.construction_project_tick`)
- Current state:
  - Completion path sets commitments and directly mutates `installed_structure_instances.installed_node_states` in the same deterministic loop.
- Risk:
  - Commitment-driven execution intent exists, but install mutation is not represented as explicit plan execution artifact and can drift from unified planning model.

### F3 - Ghost rendering is not backed by durable PlanArtifact lifecycle
- Paths:
  - `src/client/interaction/preview_generator.py`
  - `src/client/interaction/inspection_overlays.py`
  - `src/materials/blueprint_engine.py` (`build_blueprint_ghost_overlay`)
- Current state:
  - Ghost overlays are derived at preview/inspection time, but there is no canonical `plan_artifact` entity providing versioned plan state (`draft -> validated -> approved -> executed`).
- Risk:
  - Ghost output can diverge from execution candidate artifacts and cannot be replayed as a first-class planning object.

### F4 - Manual/interactive planning actions are fragmented
- Paths:
  - `data/registries/interaction_action_registry.json` (`interaction.place_blueprint_ghost`)
  - `tools/xstack/sessionx/process_runtime.py` (`order.build_plan` extension-only plan artifact)
- Current state:
  - Existing planning signals are split across order extensions and interaction preview actions.
  - No canonical incremental plan mutation API for manual placement (track/road/segment edits).
- Risk:
  - Bespoke plan-like behaviors may proliferate outside unified plan engine + Control IR execution flow.

## Code Paths Requiring Migration
- `process.construction_project_create` -> must become `process.plan_create` (derived-only) plus explicit `process.plan_execute`.
- `process.construction_project_tick` -> execution tick should operate on approved/executing plans and commitment pipeline generated from plan IR.
- `order.build_plan` extension-only payload -> must emit canonical `plan_intent`/`plan_artifact` records.
- blueprint ghost preview/inspection overlays -> must consume persisted `plan_artifact.spatial_preview_data` where available.

## Migration Plan to CTRL-4 Pipeline
1. Add canonical schemas: `plan_intent`, `plan_artifact`, `execute_plan_intent` and register in CompatX.
2. Introduce `src/control/planning/plan_engine.py`:
   - `process.plan_create`: compile blueprint (if needed), compute BOM summary + ghost data, no Truth mutation.
   - deterministic plan fingerprinting/versioning.
3. Introduce `process.plan_execute`:
   - negotiate via CTRL-3 kernel.
   - compile plan to Control IR (stepwise commitments/tasks/waits).
   - compile IR through control plane only.
4. Rewire construction creation path:
   - `process.construction_project_create` delegates to plan-create/execute adapters (compat path) and records deprecation.
5. Add incremental manual placement API:
   - deterministic plan update IDs.
   - no direct assembly writes on interaction click paths.
6. Route ghost rendering to `plan_artifact.spatial_preview_data` and gate by ViewPolicy + plan status.
7. Add RepoX/AuditX rules for direct install bypass and ghost derivation invariants.

## Invariants Mapped
- A1 Determinism primary (`constitution_v1.md` §3 A1)
- A2 Process-only mutation (`constitution_v1.md` §3 A2)
- A3 Law-gated authority (`constitution_v1.md` §3 A3)
- A4 Truth/Observation/Rendering separation (`constitution_v1.md` §3 A4)
- A10 Explicit degradation/refusal (`constitution_v1.md` §3 A10)
