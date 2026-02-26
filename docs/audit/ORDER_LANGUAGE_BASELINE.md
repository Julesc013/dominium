Status: DERIVED
Last Reviewed: 2026-02-26
Version: 1.0.0
Scope: CIV-3/4 order language + institution scaffold baseline

# Order Language Baseline

## Implemented Order Types
- `order.move`
- `order.migrate`
- `order.assimilate`
- `order.patrol` (stub)
- `order.build_plan` (stub artifact emitter)
- `order.communicate` (ED-2 message artifact bridge)

## Execution Semantics
- Orders are created by `process.order_create` and persisted in `order_assemblies`.
- Orders are queued in `order_queue_assemblies` by deterministic owner mapping.
- Queue ordering key is deterministic:
  - `(priority desc, created_tick asc, order_id asc)`
- Tick execution uses `process.order_tick` with deterministic budget processing.
- Stub behavior in CIV-3:
  - micro-agent pathing is not implemented, so micro move/migrate refusal is explicit:
    - `refusal.civ.order_requires_pathing_not_supported`
  - `order.build_plan` emits deterministic `plan_artifact` metadata only.
  - `order.communicate` emits deterministic `message_artifact` metadata only.

## Institution And Role Scaffold
- Assemblies:
  - `institution_assemblies`
  - `role_assignment_assemblies`
- Processes:
  - `process.role_assign`
  - `process.role_revoke`
- Role delegation is law/profile gated:
  - `law_profile.allow_role_delegation`
  - `law_profile.delegable_entitlements`
  - policy-level `disallowed_role_entitlements` trimming

## Multiplayer Integration Notes
- Lockstep:
  - order creation is intent-driven; tick execution is deterministic.
- Server-authoritative:
  - server executes order queue and sends filtered perceived effects.
- SRZ hybrid:
  - target shard checks are deterministic.
  - unsupported cross-shard targets refuse with:
    - `refusal.civ.order_cross_shard_not_supported`

## Epistemic Safety
- Order state visibility is entitlement-gated in observation:
  - requires `entitlement.civ.view_orders`.
- Without entitlement, control payload redacts orders/queues/institutions/role assignments.
- Order creation and queueing do not grant map/truth revelation.

## Test Coverage Summary
- `test_order_create_deterministic`
- `test_order_queue_ordering_deterministic`
- `test_order_executor_stub_refusals_deterministic`
- `test_role_assignment_entitlement_gating`
- `test_cross_shard_order_behavior`
- `test_order_visibility_gated`

## Validation Snapshot (2026-02-26)
- RepoX PASS:
  - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Result: `status=pass` (`repox scan passed`, findings=`0`).
- AuditX run:
  - `py -3 tools/auditx/auditx.py scan --repo-root . --changed-only --format json`
  - Result: `result=scan_complete`, findings=`789`.
- TestX PASS (CIV-3 required suite):
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.civilisation.order_create_deterministic,testx.civilisation.order_queue_ordering_deterministic,testx.civilisation.order_executor_stub_refusals_deterministic,testx.civilisation.role_assignment_entitlement_gating,testx.civilisation.cross_shard_order_behavior,testx.civilisation.order_visibility_gated`
  - Result: `status=pass` (`selected_tests=6`).
- strict build PASS:
  - `C:\Program Files\CMake\bin\cmake.exe --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
  - Result: build complete for all strict targets.
- `ui_bind --check` PASS:
  - `py -3 tools/xstack/ui_bind.py --repo-root . --check`
  - Result: `result=complete`, `checked_windows=21`.

## Extension Points
- CIV-4 demography/procreation order handlers.
- MAT-series build plan materialization.
- Cross-shard multi-target order splitting and routing.
- Pathing-backed micro movement executors.

