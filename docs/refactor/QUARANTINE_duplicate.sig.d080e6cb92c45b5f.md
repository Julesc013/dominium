Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.d080e6cb92c45b5f`

- Symbol: `lunar_phase`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/earth/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/worldgen/earth/__init__.py`
- `src/worldgen/earth/tide_phase_engine.py`

## Scorecard

- `src/worldgen/earth/__init__.py` disposition=`canonical` rank=`1` total_score=`64.64` risk=`HIGH`
- `src/worldgen/earth/tide_phase_engine.py` disposition=`quarantine` rank=`2` total_score=`59.79` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/ARCH_AUDIT0_RETRO_AUDIT.md, docs/audit/EARTH4_RETRO_AUDIT.md, docs/audit/EARTH5_RETRO_AUDIT.md, docs/audit/EARTH_LIGHTING_BASELINE.md, docs/audit/EARTH_SKY_STARFIELD_BASELINE.md, docs/audit/EARTH_TIDE_PROXY_BASELINE.md, docs/audit/ILLUMINATION_GEOMETRY_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md`

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
