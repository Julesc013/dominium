Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.3348d88a4969c6f3`

- Symbol: `_status_from_findings`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/compatx/check.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/compatx/check.py`
- `tools/xstack/controlx/orchestrator.py`
- `tools/xstack/repox/check.py`

## Scorecard

- `tools/xstack/compatx/check.py` disposition=`canonical` rank=`1` total_score=`73.81` risk=`HIGH`
- `tools/xstack/repox/check.py` disposition=`quarantine` rank=`2` total_score=`66.07` risk=`HIGH`
- `tools/xstack/controlx/orchestrator.py` disposition=`drop` rank=`3` total_score=`47.94` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CAPABILITY_REGISTRY_BASELINE.md, docs/audit/COMPILED_MODEL_BASELINE.md, docs/audit/DRIFT_REVALIDATION_BASELINE.md, docs/audit/FIDELITY_ARBITRATION_BASELINE.md, docs/audit/FLUID_CONTAINMENT_BASELINE.md, docs/audit/FORCE_MOMENTUM_BASELINE.md, docs/audit/GEO_CONSTITUTION_BASELINE.md, docs/audit/GEO_FRAMES_BASELINE.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
