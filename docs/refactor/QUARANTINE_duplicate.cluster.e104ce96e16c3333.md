Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.e104ce96e16c3333`

- Symbol: `extensions_get`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/meta_extensions_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/meta/extensions/__init__.py`
- `src/meta/extensions/extensions_engine.py`
- `src/meta_extensions_engine.py`

## Scorecard

- `src/meta_extensions_engine.py` disposition=`canonical` rank=`1` total_score=`79.64` risk=`HIGH`
- `src/meta/extensions/extensions_engine.py` disposition=`quarantine` rank=`2` total_score=`73.87` risk=`HIGH`
- `src/meta/extensions/__init__.py` disposition=`quarantine` rank=`3` total_score=`73.33` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/COMPAT_SEM2_RETRO_AUDIT.md, docs/audit/EFFECT_SYSTEM_BASELINE.md, docs/audit/GEO4_RETRO_AUDIT.md, docs/governance/REPOX_RULESETS.md`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
