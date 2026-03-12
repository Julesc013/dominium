Status: DERIVED
Last Reviewed: 2026-02-27
Version: 1.0.0
Scope: MAT-4 logistics graph, manifests, and deterministic delivery commitments baseline.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Logistics Baseline

## 1) Canonical Scope
MAT-4 establishes the macro/meso logistics substrate for deterministic material movement.

Primary doctrine references:
- `docs/materials/LOGISTICS_GRAPH.md`
- `docs/materials/MANIFESTS_AND_SHIPMENTS.md`

MAT-4 intentionally excludes:
- micro vehicles/pathfinding
- traffic simulation
- economy pricing
- crafting/inventory gameplay

## 2) Graph Schema Baseline
Logistics schemas (strict v1.0.0):
- `logistics_node`
- `logistics_edge`
- `logistics_graph`
- `routing_rule`
- `manifest`
- `shipment_commitment`
- `node_inventory`

Registries:
- `data/registries/logistics_routing_rule_registry.json`
  - `route.direct_only`
  - `route.shortest_delay`
  - `route.min_cost_units`
- `data/registries/logistics_graph_registry.json`
  - empty/null-safe baseline graph set (procedural generation stub-ready)

Determinism guarantees:
- stable edge/node ordering by ID
- deterministic tie-break behavior (`edge_id` lexical)
- deterministic route expansion for multi-hop rules

## 3) Manifest Lifecycle Baseline
Canonical process entrypoints:
- `process.manifest_create`
- `process.manifest_tick`

Lifecycle status channel:
- `planned`
- `in_transit`
- `delivered`
- `lost`
- `failed`

Process behavior:
- create validates stock and route, then creates shipment commitment + manifest
- tick advances manifests by deterministic tick/order rules
- depart debits source node inventory
- arrive credits destination node inventory
- loss emits explicit `shipment_lost` provenance and ledger exception pathway

Refusal codes:
- `refusal.logistics.insufficient_stock`
- `refusal.logistics.invalid_route`

## 4) Conservation + Ledger Integration
RS-2 integration path:
- node inventory is macro stock (`material_id -> mass`) with optional batch refs
- transfers are process-driven inventory debits/credits only
- no silent material creation/destruction allowed
- loss path routes through explicit exception handling (`_ledger_emit_exception`) with policy-selected exception type

Invariants preserved:
- process-only mutation (A2)
- deterministic replay order (A1)
- manifest/provenance continuity for shipment events

## 5) Commitments + Reenactment Hooks
Shipment commitments are canonical artifacts linked to manifests.

Each manifest records:
- commitment link
- provenance event IDs
- deterministic fingerprint
- route edge IDs, actor subject, and departure/arrival timing

This provides MAT-8 reenactment readiness for optional micro-vehicle replay without changing macro truth.

## 6) Visualization + Interaction Baseline (Asset-Free)
RND integration additions:
- inspect node inventory
- inspect shipment manifests
- create shipment (lab/admin profiles)

Render behavior:
- procedural graph-edge overlays
- procedural flow arrows per manifest route
- deterministic overlay ordering/hash stability for inspection snapshots

## 7) Performance/Budget Behavior
`process.manifest_tick` execution cost scales with:
- manifests processed
- routing computations

Budget policy behavior:
- deterministic degrade/chunk processing when over budget
- stable manifest processing order by `manifest_id`
- deterministic sequence cursor persisted in runtime state

## 8) Invariants + Guardrails
RepoX rules:
- `INV-NO-SILENT-TRANSFER`
- `INV-MANIFESTS-PROCESS-ONLY`
- `INV-LOGISTICS-DETERMINISTIC-ROUTING`

AuditX analyzers:
- `SilentShipmentSmell` (`E62_SILENT_SHIPMENT_SMELL`)
- `NonDeterministicRoutingSmell` (`E63_NONDETERMINISTIC_ROUTING_SMELL`)

TestX MAT-4 required coverage:
- `testx.materials.manifest_create_deterministic`
- `testx.materials.manifest_tick_delivery_deterministic`
- `testx.materials.loss_fraction_deterministic`
- `testx.materials.conservation_ledger_transfer_balanced`
- `testx.materials.budget_degrade_order_deterministic`
- `testx.materials.visual_overlay_render_model_hash_stable`

## 9) Extension Points (MAT-5..MAT-10)
1. MAT-5 construction execution can consume shipment commitments as prerequisites.
2. MAT-6 maintenance/failure systems can publish spare-part manifests into the same commitment/provenance pipeline.
3. MAT-7+ can add mode-specific transport constraints as routing-rule registry extensions.
4. MAT-8 can add micro reenactment vehicle spawning sourced from manifest descriptors.
5. MAT-9/10 can shard mega graphs while retaining deterministic route/manifest ordering contracts.

## 10) Gate Snapshot (2026-02-27)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass` (warn-level finding present)
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=968 (warn-level findings)
3. TestX PASS (MAT-4 required subset)
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.materials.manifest_create_deterministic,testx.materials.manifest_tick_delivery_deterministic,testx.materials.loss_fraction_deterministic,testx.materials.conservation_ledger_transfer_balanced,testx.materials.budget_degrade_order_deterministic,testx.materials.visual_overlay_render_model_hash_stable,testx.materials.guardrail_declarations_present`
   - result: `status=pass`, selected_tests=7
4. strict build PASS
   - command: `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
   - result: build completed successfully
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: `result=complete`
