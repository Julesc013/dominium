Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: MAT-3 Bill of Materials + Assembly Graph + deterministic blueprint compilation baseline.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# BOM + Assembly Graph Baseline

## 1) Canonical Structural Model
Doctrine source: `docs/materials/BOM_AND_ASSEMBLY_GRAPH.md`

MAT-3 defines:
- `BOM` as abstract material/part-class requirements for planning/logistics/commitments.
- `Assembly Graph (AG)` as deterministic, schema-validated structural composition over nodes and connection edges.
- Blueprint compilation as a deterministic transformation from pack data into canonical BOM/AG artifacts.

No crafting/inventory/manufacturing solver behavior is introduced.

## 2) Schemas + Registries
Schemas (strict v1.0.0):
- `bom`, `part_class`, `assembly_graph`, `ag_node`, `ag_edge`, `connection_type`, `blueprint`
- Registry schemas for `part_class_registry`, `connection_type_registry`, `blueprint_registry`

Material structure registries:
- `data/registries/part_class_registry.json`
- `data/registries/connection_type_registry.json`
- `data/registries/blueprint_registry.json`

Baseline part classes:
- `partclass.bolt.generic`, `partclass.beam.generic`, `partclass.panel.generic`
- `partclass.pipe.generic`, `partclass.gear.generic`, `partclass.bearing.generic`
- `partclass.motor.generic`, `partclass.circuit.generic`

Baseline connection types:
- `conn.bolted`, `conn.welded`, `conn.riveted`, `conn.press_fit`, `conn.mortar`

Baseline blueprints:
- `blueprint.house.basic`
- `blueprint.lathe.basic`
- `blueprint.road.segment.basic`
- `blueprint.simple_bridge.basic`
- `blueprint.space_elevator.template` (stub)

## 3) Deterministic Blueprint Compilation
Implementation:
- `src/materials/blueprint_engine.py`
- `tools/materials/tool_blueprint_compile.py`

Determinism guarantees:
- Stable node/edge ordering.
- Deterministic instancing expansion.
- Canonical compiled artifacts + provenance header.
- Cache key stability: `H(blueprint_id, params_hash, pack_lock_hash)`.

Refusal codes:
- `refusal.blueprint.missing_part_class`
- `refusal.blueprint.invalid_graph`
- `refusal.blueprint.parameter_invalid`

## 4) RND Integration (Asset-Free)
MAT-3 adds blueprint interaction/inspection stubs without construction execution:
- `interaction.inspect_blueprint`
- `interaction.place_blueprint_ghost`
- `interaction.generate_bom_summary`

Behavior:
- deterministic blueprint ghost overlay with wireframe primitives
- stable color hashing by part/material tags
- deterministic BOM inspection summary

## 5) Provenance, Commitments, and Tier Mapping
MAT-3 preserves MAT-0/MAT-1/MAT-2 contracts:
- AG node metadata supports planned commitment IDs and batch linkage stubs.
- No macro silent mutation path is introduced.
- Compilation is data-driven and pack-resolved; runtime does not hardwire default blueprints.
- Null compatibility preserved: blueprint-aware registries are loaded optionally and degrade/refuse deterministically when unavailable.

Tier mapping:
- Macro: planning-level BOM quantities and commitment planning.
- Meso: AG-subassembly and logistics scheduling targets.
- Micro (ROI): explicit AG-node visualization/inspection overlays; no automatic construction mutation in MAT-3.

## 6) Invariants + Guardrails
RepoX invariants:
- `INV-BLUEPRINTS-DATA-ONLY`
- `INV-DETERMINISTIC-BLUEPRINT-COMPILATION`
- `INV-NO-HARDCODED-STRUCTURES`

AuditX analyzers:
- `HardcodedBlueprintSmell` (`E60_HARDCODED_BLUEPRINT_SMELL`)
- `NonDeterministicGraphOrderSmell` (`E61_NONDETERMINISTIC_GRAPH_ORDER_SMELL`)

TestX MAT-3 required tests:
- `testx.materials.blueprint_compile_deterministic`
- `testx.materials.bom_ag_schema_valid`
- `testx.materials.instancing_expansion_deterministic`
- `testx.materials.missing_part_class_refusal`
- `testx.materials.blueprint_visualization_render_model_hash_stable`

## 7) Extension Points (MAT-4 .. MAT-10)
- MAT-4 logistics: bind AG/BOM outputs to shipment and node inventory commitments.
- MAT-5 construction: convert AG milestones into process-backed authoritative construction events.
- MAT-6 failures: map failure modes onto part classes and connection types.
- MAT-7 maintenance: attach backlog/deferred maintenance commitments to AG nodes.
- MAT-8 optimization: deterministic planning/caching for large instancing graphs.
- MAT-9 simulation integration: physics/structural domain adapters remain solver-optional.
- MAT-10 scaling hardening: mega-structure partitioning, shard-safe deterministic graph compilation.

## 8) Gate Snapshot (2026-02-27)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass` (warn-level finding present in AuditX report threshold)
2. AuditX run
   - command: `py -3 tools/auditx/auditx.py scan --repo-root .`
   - result: `result=scan_complete`, findings_count=1654
3. TestX PASS (MAT-3 required subset)
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.materials.blueprint_compile_deterministic,testx.materials.bom_ag_schema_valid,testx.materials.instancing_expansion_deterministic,testx.materials.missing_part_class_refusal,testx.materials.blueprint_visualization_render_model_hash_stable,testx.materials.guardrail_declarations_present`
   - result: `status=pass`, selected_tests=6
4. strict build PASS
   - command: `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
   - result: build completed successfully
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: `result=complete`
