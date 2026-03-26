Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7f86c070dac63b7d`

- Symbol: `normalize_logic_eval_state`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/logic/eval/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/logic/__init__.py`
- `src/logic/eval/__init__.py`
- `src/logic/eval/logic_eval_engine.py`
- `src/logic/eval/runtime_state.py`

## Scorecard

- `src/logic/eval/__init__.py` disposition=`canonical` rank=`1` total_score=`76.67` risk=`HIGH`
- `src/logic/eval/runtime_state.py` disposition=`quarantine` rank=`2` total_score=`70.36` risk=`HIGH`
- `src/logic/__init__.py` disposition=`quarantine` rank=`3` total_score=`69.64` risk=`HIGH`
- `src/logic/eval/logic_eval_engine.py` disposition=`merge` rank=`4` total_score=`58.51` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/audit/ARCH_AUDIT_BASELINE.md, docs/audit/ARCH_AUDIT_FIX_PLAN.md, docs/audit/ARCH_AUDIT_REPORT.md, docs/audit/CANON_MAP.md, docs/audit/CAP_NEG_FINAL_BASELINE.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
