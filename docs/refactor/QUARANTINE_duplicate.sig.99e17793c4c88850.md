Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.99e17793c4c88850`

- Symbol: `REFUSAL_SOFTWARE_PIPELINE_INVALID`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/process/software/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `src/process/__init__.py`
- `src/process/software/__init__.py`
- `src/process/software/pipeline_engine.py`

## Scorecard

- `src/process/software/__init__.py` disposition=`canonical` rank=`1` total_score=`58.65` risk=`HIGH`
- `src/process/software/pipeline_engine.py` disposition=`quarantine` rank=`2` total_score=`50.49` risk=`HIGH`
- `src/process/__init__.py` disposition=`drop` rank=`3` total_score=`48.39` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/PROC9_RETRO_AUDIT.md, docs/audit/PROC_FINAL_BASELINE.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SOFTWARE_PIPELINE_BASELINE.md, docs/audit/STABILITY_CLASSIFICATION_BASELINE.md, docs/governance/REPOX_RULESETS.md`

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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
