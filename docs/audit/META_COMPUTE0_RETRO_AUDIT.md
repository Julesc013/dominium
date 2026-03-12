Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# META_COMPUTE0 Retro-Consistency Audit

Status: AUDIT
Series: META-COMPUTE-0
Date: 2026-03-07

## Scope
Audit deterministic budget surfaces and compute-like execution pathways to establish unified compute metering without introducing mode flags, nondeterminism, or wall-clock dependence.

## Existing Budget Systems (RS-5 style cost units)

Observed deterministic cost/budget envelopes already in use:

- `src/system/macro/macro_capsule_engine.py`
  - `max_capsules_per_tick`, `tick_bucket_stride`, `max_cost_units_per_capsule`
  - deterministic defer reasons (`degrade.system.macro_tick_bucket`, `degrade.system.macro_budget_cap`)
- `src/thermal/network/thermal_network_engine.py`
  - bounded model cost and deterministic degradation markers
- `src/time/time_mapping_engine.py`
  - bounded mapping budget and deterministic deferred rows
- `src/interaction/task/task_engine.py`
  - task tick budget enforcement and strict budget refusals
- `src/system/reliability/*`
  - deterministic scheduler budget degradation signals

Audit conclusion:
- Cost budgeting exists in several domains but compute-specific instruction/memory metering is not a first-class shared contract.

## Existing Execution Loops that Map to Compute

Compute-like loops requiring explicit metering hooks:

- SYS macro model evaluation:
  - `src/system/macro/macro_capsule_engine.py` (`evaluate_macro_capsules_tick`)
- COMPILE runtime execution:
  - `src/meta/compile/compile_engine.py` (`compiled_model_execute`)
- PROC software pipeline compile/test steps:
  - `src/process/software/pipeline_engine.py` (`evaluate_software_pipeline_execution`)

Future-aligned target:
- LOGIC evaluator paths (not yet implemented in this series) should consume compute budgets through the same engine.

## Integration Points Required

1. SYS macro capsules:
- must request instruction units before per-capsule model binding execution
- over-budget must deterministically defer/degrade/refuse with logs

2. COMPILE runtime:
- `compiled_model_execute` must request compute units and emit consumption records

3. PROC software pipeline:
- compile/test steps must request compute units using deterministic cost estimates

4. Optional physics coupling:
- profile-gated conversion of instruction usage to power/heat hooks through ledger transforms (e.g., electrical->thermal)

## Current Gaps

- No canonical `compute_budget_profile` schema/registry.
- No canonical `compute_consumption_record` artifact row.
- No central compute budget engine/API (`request_compute`) for shared deterministic throttling.
- No dedicated enforcement for unmetered compute paths.

## Preliminary Risk Categorization

- Safety-critical risk:
  - unmetered compiled/control execution can starve deterministic simulation budget
- Correctness risk:
  - ad-hoc local throttling policies diverge across subsystems
- Governance risk:
  - missing canonical logs for throttling/refusal/shutdown prevents replay-grade auditability

## Migration Plan (META-COMPUTE-0)

- Introduce canonical compute schemas + registries.
- Add shared deterministic compute budget engine in `src/meta/compute`.
- Add non-breaking hooks into SYS/COMPILE/PROC execution points.
- Emit canonical compute consumption records and deterministic decision logs.
- Add RepoX/AuditX enforcement and TestX coverage.
