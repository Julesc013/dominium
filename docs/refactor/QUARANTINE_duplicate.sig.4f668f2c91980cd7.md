Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.4f668f2c91980cd7`

- Symbol: `DEFAULT_FINAL_DOC_REL`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/mvp/cross_platform_gate_common.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/mvp/cross_platform_gate_common.py`
- `tools/mvp/mvp_smoke_common.py`
- `tools/mvp/stress_gate_common.py`
- `tools/time/time_anchor_common.py`

## Scorecard

- `tools/mvp/cross_platform_gate_common.py` disposition=`canonical` rank=`1` total_score=`71.9` risk=`HIGH`
- `tools/mvp/mvp_smoke_common.py` disposition=`quarantine` rank=`2` total_score=`69.88` risk=`HIGH`
- `tools/mvp/stress_gate_common.py` disposition=`quarantine` rank=`3` total_score=`66.96` risk=`HIGH`
- `tools/time/time_anchor_common.py` disposition=`quarantine` rank=`4` total_score=`66.07` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/CONVERGENCE_FINAL.md, docs/audit/DOC_INDEX.md, docs/audit/EARTH_MVP_FINAL_BASELINE.md, docs/audit/LIB_FINAL_BASELINE.md, docs/audit/MVP_CROSS_PLATFORM_FINAL.md, docs/audit/MVP_STRESS_FINAL.md`

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
