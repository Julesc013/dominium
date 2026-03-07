# META-COMPUTE-0 Baseline

## Scope
- Deterministic compute budgeting established for executable owners (`controller|system|process`).
- Metering integrated into:
  - SYS macro capsule execution
  - COMPILE compiled model execution
  - PROC software pipeline compile/test steps
- Deterministic throttling outcomes logged with canonical compute consumption records.
- Optional profile-gated power/heat coupling hooks integrated via energy transform rows.

## Budgeting Rules
- Unit model:
  - `instruction_units` per tick
  - `memory_units` persistent footprint
- Profile source:
  - `data/registries/compute_budget_profile_registry.json`
  - `data/registries/compute_degrade_policy_registry.json`
- Deterministic owner ordering:
  - sort by `(priority, owner_id)`
- Over-budget actions:
  - `degrade`, `defer`, `refuse`, `shutdown` (policy-driven, deterministic)
- Canonical record:
  - `schema/meta/compute_consumption_record.schema`

## Degrade Policies
- `degrade.default_order`
  - frequency reduction, representation degrade, evaluation cap, refuse non-critical, optional shutdown
- `degrade.strict_shutdown`
  - no representation degrade, fail-safe shutdown on critical overrun

## Integration Hooks
- SYS:
  - `src/system/macro/macro_capsule_engine.py`
  - requests compute units per capsule eval and emits compute decision/consumption outputs
- COMPILE:
  - `src/meta/compile/compile_engine.py`
  - requests compute units for compiled-model execution and emits compute refusal/throttle explain rows
- PROC:
  - `src/process/software/pipeline_engine.py`
  - compile/test stages request compute units; refusals are deterministic and logged
- Explain + instrumentation:
  - explain contracts:
    - `explain.compute_throttle`
    - `explain.compute_refusal`
    - `explain.compute_shutdown`
  - instrumentation surfaces expose compute instruction/memory usage metrics.

## Verification Runs
- RepoX STRICT:
  - `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Result: `refusal` (repository-wide pre-existing strict blockers outside META-COMPUTE-0 scope remain)
- AuditX STRICT:
  - `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - Result: `pass`
- TestX (META-COMPUTE-0 targeted cases):
  - `test_budget_allocation_deterministic` pass
  - `test_throttle_order_deterministic` pass
  - `test_consumption_records_logged` pass
  - `test_power_coupling_ledgered_when_enabled` pass
  - `test_cross_platform_compute_hash_match` pass
- Stress harness (compute-heavy macro capsule scenario):
  - `python tools/system/tool_run_sys_stress.py --scenario compute-heavy-macro --seed 411 --system-count 256 --tick-count 12 --max-macro-capsules-per-tick 128 --output docs/audit/compute_budget_stress_results.json`
  - Result: `complete`
  - fingerprint: `4d84efd3128d69c283fdc5f427cdb3d22fc9f5f052a6a79c40a039117acd6786`
- Strict build:
  - `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game`
  - Result: `pass`
- Topology map:
  - regenerated via `python tools/governance/tool_topology_generate.py --repo-root .`

## Readiness
- META-COMPUTE-0 contracts and runtime hooks are in place for LOGIC-0 controller execution budgeting.
- Remaining strict-lane global refusals are repository baseline issues and not introduced by this series.
