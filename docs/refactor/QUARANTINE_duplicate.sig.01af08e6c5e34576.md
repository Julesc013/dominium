Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.01af08e6c5e34576`

- Symbol: `REFUSAL_STANDARDS_SPEC_TYPE_FORBIDDEN`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/signals/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/signals/__init__.py`
- `src/signals/institutions/__init__.py`
- `src/signals/institutions/standards_engine.py`

## Scorecard

- `src/signals/__init__.py` disposition=`canonical` rank=`1` total_score=`58.1` risk=`HIGH`
- `src/signals/institutions/__init__.py` disposition=`quarantine` rank=`2` total_score=`54.04` risk=`HIGH`
- `src/signals/institutions/standards_engine.py` disposition=`quarantine` rank=`3` total_score=`51.77` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/INSTITUTIONAL_COMMS_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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
