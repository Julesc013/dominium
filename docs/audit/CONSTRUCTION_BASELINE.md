Status: DERIVED
Last Reviewed: 2026-02-27
Version: 1.0.0
Scope: MAT-5 construction, installation, commitments, provenance, and deterministic project execution baseline.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Construction Baseline

## 1) Canonical Scope
MAT-5 establishes commitment-driven construction and installation over compiled blueprint BOM/AG artifacts.

Primary doctrine references:
- `docs/materials/CONSTRUCTION_AND_INSTALLATION.md`
- `docs/materials/PROVENANCE_EVENTS.md`

MAT-5 intentionally excludes:
- crafting/inventory gameplay
- micro bolting/welding interactions
- structural stress solvers

## 2) Project + Step Schema Baseline
Construction schemas (strict v1.0.0):
- `construction_project`
- `construction_step`
- `provenance_event`
- `event_type_registry` (materials)

Registries:
- `data/registries/provenance_event_type_registry.json`
- `data/registries/construction_policy_registry.json`

Universe-state integration fields:
- `construction_projects`
- `construction_steps`
- `construction_commitments`
- `construction_provenance_events`
- `installed_structure_instances`
- `construction_runtime_state`

## 3) Deterministic Scheduling Baseline
Canonical process entrypoints:
- `process.construction_project_create`
- `process.construction_project_tick`
- `process.construction_pause`
- `process.construction_resume`

Scheduling rules:
- project and step identity are deterministic hashes of stable inputs
- AG-node execution ordering is stable by `ag_node_id`
- dependency gating and parallel-step limits are policy-driven and deterministic
- budget reduction degrades by deterministic project ordering (`project_id`)

## 4) Ledger + Accounting Baseline
Construction accounting behavior:
- step start emits `event.material_consumed` with `ledger_deltas.quantity.mass < 0`
- step completion emits `event.batch_created` with `ledger_deltas.quantity.mass > 0`
- install emits `event.install_part` with structural state update linkage
- no silent mutation path exists outside process runtime commit boundaries

Guarded invariants:
- `INV-LEDGER-DEBIT-CREDIT-REQUIRED`
- `INV-NO-SILENT-INSTALL`

## 5) Provenance + Commitments Baseline
Provenance event types included:
- `event.construct_project_created`
- `event.construct_step_started`
- `event.construct_step_completed`
- `event.material_consumed`
- `event.batch_created`
- `event.install_part`
- stubs: `event.deconstruct_part`, `event.maintenance_scheduled`

Commitment integration:
- per-step start/end commitments are deterministic canonical artifacts
- project milestone commitment IDs are persisted on project rows
- reenactment descriptor stores event-linked step sequence for MAT-8 playback readiness

Guarded invariants:
- `INV-CONSTRUCTION-REQUIRES-COMMITMENTS`
- `INV-PROVENANCE-EVENTS-REQUIRED`

## 6) Visualization + Inspection Baseline
Interaction and overlay support:
- inspect construction project
- inspect installed structure
- view construction provenance events

RenderModel behavior:
- planned nodes render as ghost wire primitives
- completed nodes render as solid procedural primitives
- deterministic metadata/material ordering preserves RenderModel hash stability

## 7) Guardrails + Tests
RepoX rules:
- `INV-CONSTRUCTION-REQUIRES-COMMITMENTS`
- `INV-PROVENANCE-EVENTS-REQUIRED`
- `INV-LEDGER-DEBIT-CREDIT-REQUIRED`
- `INV-NO-SILENT-INSTALL`

AuditX analyzers:
- `SilentConstructionSmell` (`E64_SILENT_CONSTRUCTION_SMELL`)
- `MissingProvenanceSmell` (`E65_MISSING_PROVENANCE_SMELL`)

TestX MAT-5 subset:
- `testx.materials.project_create_deterministic`
- `testx.materials.step_scheduling_deterministic`
- `testx.materials.material_consumption_balanced`
- `testx.materials.insufficient_material_refusal`
- `testx.materials.provenance_events_deterministic`
- `testx.materials.construction_visualization_render_model_hash_stable`
- `testx.materials.budget_parallelism_reduction_deterministic`
- `testx.materials.guardrail_declarations_present`

## 8) Extension Points (MAT-6..MAT-7)
1. MAT-6 failure/decay can consume `installed_structure_instances.maintenance_backlog`.
2. MAT-6 maintenance scheduling can emit canonical maintenance commitments/provenance events.
3. MAT-7 micro-part materialization can derive ROI micro entities from installed-node summaries + provenance lineage.
4. MAT-8 reenactment can consume `reenactment_descriptor.step_sequence` for watchable playback.

## 9) Gate Snapshot (2026-02-27)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=1 (warn-level)
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=926 (warn-level)
3. TestX PASS (MAT-5 required subset + guard presence)
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.materials.project_create_deterministic,testx.materials.step_scheduling_deterministic,testx.materials.material_consumption_balanced,testx.materials.insufficient_material_refusal,testx.materials.provenance_events_deterministic,testx.materials.construction_visualization_render_model_hash_stable,testx.materials.budget_parallelism_reduction_deterministic,testx.materials.guardrail_declarations_present`
   - result: `status=pass`, selected_tests=8
4. strict build PASS
   - command: `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
   - result: build completed successfully
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: `result=complete`
