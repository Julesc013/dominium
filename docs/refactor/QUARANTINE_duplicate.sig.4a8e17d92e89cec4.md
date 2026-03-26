Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.4a8e17d92e89cec4`

- Symbol: `_rows_from_registry`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/process/maturity/metrics_engine.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_medium_risk_batch_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/interaction/action_surface_engine.py`
- `src/process/capsules/capsule_builder.py`
- `src/process/drift/drift_engine.py`
- `src/process/maturity/maturity_engine.py`
- `src/process/maturity/metrics_engine.py`
- `src/process/process_run_engine.py`
- `src/process/qc/qc_engine.py`
- `src/process/software/pipeline_engine.py`

## Scorecard

- `src/process/maturity/metrics_engine.py` disposition=`canonical` rank=`1` total_score=`77.62` risk=`MED`
- `src/process/maturity/maturity_engine.py` disposition=`merge` rank=`2` total_score=`75.48` risk=`MED`
- `src/process/drift/drift_engine.py` disposition=`merge` rank=`3` total_score=`73.87` risk=`MED`
- `src/process/process_run_engine.py` disposition=`merge` rank=`4` total_score=`71.25` risk=`MED`
- `src/process/qc/qc_engine.py` disposition=`quarantine` rank=`5` total_score=`69.76` risk=`HIGH`
- `src/process/capsules/capsule_builder.py` disposition=`merge` rank=`6` total_score=`68.57` risk=`MED`
- `src/interaction/action_surface_engine.py` disposition=`merge` rank=`7` total_score=`59.94` risk=`MED`
- `src/process/software/pipeline_engine.py` disposition=`merge` rank=`8` total_score=`54.35` risk=`MED`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/PROC4_RETRO_AUDIT.md, docs/audit/PROC5_RETRO_AUDIT.md, docs/audit/PROCESS_MATURITY_BASELINE.md, docs/audit/REPO_TREE_INDEX.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
