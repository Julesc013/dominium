Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.53f72618410a9546`

- Symbol: `REFUSAL_PROCESS_CAPSULE_INVALID`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/process/capsules/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/process/__init__.py`
- `src/process/capsules/__init__.py`
- `src/process/capsules/capsule_builder.py`

## Scorecard

- `src/process/capsules/__init__.py` disposition=`canonical` rank=`1` total_score=`59.56` risk=`HIGH`
- `src/process/__init__.py` disposition=`quarantine` rank=`2` total_score=`57.98` risk=`HIGH`
- `src/process/capsules/capsule_builder.py` disposition=`quarantine` rank=`3` total_score=`52.36` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/PROCESS_CAPSULE_BASELINE.md, docs/audit/PROC_FINAL_BASELINE.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SOFTWARE_PIPELINE_BASELINE.md, docs/process/PROCESS_CAPSULE_MODEL.md, docs/worldgen/REAL_DATA_IMPORT_PIPELINE.md`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
