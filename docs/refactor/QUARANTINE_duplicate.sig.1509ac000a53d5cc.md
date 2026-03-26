Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.1509ac000a53d5cc`

- Symbol: `explain_cache_key`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/meta/explain/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/meta/explain/__init__.py`
- `src/meta/explain/explain_engine.py`

## Scorecard

- `src/meta/explain/__init__.py` disposition=`canonical` rank=`1` total_score=`67.14` risk=`HIGH`
- `src/meta/explain/explain_engine.py` disposition=`quarantine` rank=`2` total_score=`59.58` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/GEO_FINAL_BASELINE.md, docs/audit/META_CONTRACT0_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/MVP_VIEWER_BASELINE.md, docs/audit/PROCESS_MATURITY_BASELINE.md, docs/audit/REFINEMENT_PIPELINE_BASELINE.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/VALIDATION_STACK_MAP.md`

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
