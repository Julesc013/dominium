Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.1db4f7ade615cef7`

- Symbol: `normalize_logic_network_runtime_state_rows`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/logic/eval/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/logic/__init__.py`
- `src/logic/eval/__init__.py`
- `src/logic/eval/runtime_state.py`

## Scorecard

- `src/logic/eval/__init__.py` disposition=`canonical` rank=`1` total_score=`76.67` risk=`HIGH`
- `src/logic/eval/runtime_state.py` disposition=`quarantine` rank=`2` total_score=`70.36` risk=`HIGH`
- `src/logic/__init__.py` disposition=`quarantine` rank=`3` total_score=`69.64` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/ELECTRICAL_PROTECTION_BASELINE.md, docs/audit/LOGIC0_RETRO_AUDIT.md, docs/audit/LOGIC10_RETRO_AUDIT.md, docs/audit/LOGIC4_RETRO_AUDIT.md, docs/audit/LOGIC5_RETRO_AUDIT.md`

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
