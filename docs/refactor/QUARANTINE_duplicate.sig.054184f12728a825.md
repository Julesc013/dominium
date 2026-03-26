Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.054184f12728a825`

- Symbol: `normalize_logic_security_fail_rows`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/logic/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `src/logic/__init__.py`
- `src/logic/eval/__init__.py`
- `src/logic/eval/runtime_state.py`

## Scorecard

- `src/logic/__init__.py` disposition=`canonical` rank=`1` total_score=`69.64` risk=`HIGH`
- `src/logic/eval/__init__.py` disposition=`quarantine` rank=`2` total_score=`67.14` risk=`HIGH`
- `src/logic/eval/runtime_state.py` disposition=`drop` rank=`3` total_score=`56.52` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CONSISTENCY_AUDIT_REPORT.md, docs/audit/LOGIC10_RETRO_AUDIT.md, docs/audit/LOGIC8_RETRO_AUDIT.md, docs/audit/LOGIC_FAULT_NOISE_BASELINE.md, docs/audit/LOGIC_FINAL_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/STABILITY_CLASSIFICATION_BASELINE.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
