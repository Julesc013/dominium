Status: DERIVED
Last Reviewed: 2026-02-28
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: ABS-1 core abstraction substrate and MAT logistics migration baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Core Abstractions Baseline

## 1) Scope Summary
ABS-1 establishes shared deterministic abstractions for:
- `NetworkGraph`
- `FlowSystem`
- `ConstraintComponent`
- `StateMachineComponent`
- `HazardModel`
- `ScheduleComponent`
- `SpatialNode`

Authoritative doctrine:
- `docs/architecture/CORE_ABSTRACTIONS.md`

## 2) New Schemas
Core component schemas:
- `network_graph`
- `network_node`
- `network_edge`
- `flow_channel`
- `constraint_component`
- `state_machine`
- `hazard_model`
- `schedule`
- `spatial_node`

Core registry output schemas:
- `core_routing_policy_registry`
- `core_flow_solver_policy_registry`
- `core_constraint_type_registry`
- `core_state_machine_type_registry`
- `core_hazard_type_registry`
- `core_schedule_policy_registry`

## 3) New Registries
Baseline source registries:
- `data/registries/core_routing_policy_registry.json`
- `data/registries/core_flow_solver_policy_registry.json`
- `data/registries/core_constraint_type_registry.json`
- `data/registries/core_state_machine_type_registry.json`
- `data/registries/core_hazard_type_registry.json`
- `data/registries/core_schedule_policy_registry.json`

Registry compile integration:
- Added compile/load/validate paths and emitted deterministic hashes.
- Added lockfile hash fields for all core abstraction registries.

## 4) Runtime Engines
New deterministic runtime modules:
- `src/core/graph/network_graph_engine.py`
- `src/core/flow/flow_engine.py`
- `src/core/constraints/constraint_engine.py`
- `src/core/state/state_machine_engine.py`
- `src/core/hazards/hazard_engine.py`
- `src/core/schedule/schedule_engine.py`
- `src/core/spatial/spatial_engine.py`

All modules are immutable-input deterministic helpers with explicit refusal paths and no wall-clock dependency.

## 5) Migration Completed
MAT logistics internal migration completed:
- `src/logistics/logistics_engine.py` now delegates route selection and route aggregate calculations to core `NetworkGraph` APIs.
- Loss/delivery transfer math now delegates to core `FlowSystem` helper.
- Public logistics behavior preserved:
  - same manifest lifecycle statuses
  - same refusal codes (`refusal.logistics.invalid_route`, `refusal.logistics.insufficient_stock`)
  - same event semantics (`shipment_depart`, `shipment_arrive`, `shipment_lost`)

## 6) Duplication Enforcement
RepoX rules added:
- `INV-NO-DUPLICATE-GRAPH-SUBSTRATES`
- `INV-NO-DUPLICATE-SCHEDULERS`
- `INV-NO-ADHOC-STATE-MACHINES`
- `INV-FLOW-USES-LEDGER`

AuditX analyzers added:
- `GraphDuplicationSmell` (`E84_GRAPH_DUPLICATION_SMELL`)
- `AdHocSchedulerSmell` (`E85_ADHOC_SCHEDULER_SMELL`)
- `AdHocStateMachineSmell` (`E86_ADHOC_STATE_MACHINE_SMELL`)
- `FlowBypassSmell` (`E87_FLOW_BYPASS_SMELL`)

## 7) Test Coverage
New TestX coverage:
- `test_network_graph_deterministic_ordering`
- `test_flow_engine_capacity_delay_loss_deterministic`
- `test_state_machine_transition_deterministic`
- `test_schedule_engine_recurrence_deterministic`
- `test_logistics_migration_behavior_equivalence`

## 8) Extension Guidance (INT/POSE/CTRL/MOB)
1. INT should model room/portal topology directly as `NetworkGraph` plus `SpatialNode` hierarchy.
2. POSE and MOB should model guide/docking/coupling restrictions via `ConstraintComponent` and `StateMachineComponent`.
3. CTRL should map orchestration timelines and recurrences to `ScheduleComponent`.
4. Hazard-heavy domains should reuse `HazardModel` accumulation contracts with policy-defined consequence processes.
5. New flow domains (signals/power/water) should bind to `FlowChannel` with explicit `quantity_id` and ledger policy handling.

## 9) Gate Snapshot (2026-02-28)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=0
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=876 (warn-level findings present)
3. TestX PASS
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.core.network_graph_deterministic_ordering,testx.core.flow_engine_capacity_delay_loss_deterministic,testx.core.state_machine_transition_deterministic,testx.core.schedule_engine_recurrence_deterministic,testx.materials.logistics_migration_behavior_equivalence`
   - result: `status=pass`, selected_tests=5
4. strict build PASS
   - command: `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.abs1 --cache on --format json`
   - result: `result=complete`
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: `result=complete`, checked_windows=21
