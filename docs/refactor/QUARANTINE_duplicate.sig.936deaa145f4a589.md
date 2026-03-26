Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.936deaa145f4a589`

- Symbol: `TICK_BITS`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/time/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/time/__init__.py`
- `src/time/tick_t.py`

## Scorecard

- `src/time/__init__.py` disposition=`canonical` rank=`1` total_score=`63.57` risk=`HIGH`
- `src/time/tick_t.py` disposition=`quarantine` rank=`2` total_score=`61.73` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/SIGNAL_BUS_BASELINE.md, docs/logic/SIGNAL_AND_BUS_MODEL.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/specs/SPEC_NUMERIC.md`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
