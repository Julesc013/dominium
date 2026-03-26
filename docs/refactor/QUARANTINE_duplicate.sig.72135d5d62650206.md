Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.72135d5d62650206`

- Symbol: `_realism_profile_rows`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/worldgen/worldgen_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/worldgen/worldgen_engine.py`
- `src/worldgen/mw/system_query_engine.py`

## Scorecard

- `src/geo/worldgen/worldgen_engine.py` disposition=`canonical` rank=`1` total_score=`55.36` risk=`HIGH`
- `src/worldgen/mw/system_query_engine.py` disposition=`quarantine` rank=`2` total_score=`50.43` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/ARCHITECTURE_HEALTH_REPORT.md, docs/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/EARTH4_RETRO_AUDIT.md, docs/audit/GEO8_RETRO_AUDIT.md, docs/audit/GEO9_RETRO_AUDIT.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
