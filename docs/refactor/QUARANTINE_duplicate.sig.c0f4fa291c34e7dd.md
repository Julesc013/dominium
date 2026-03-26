Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c0f4fa291c34e7dd`

- Symbol: `roi_distance_mm`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/frame/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/__init__.py`
- `src/geo/frame/__init__.py`
- `src/geo/frame/domain_adapters.py`

## Scorecard

- `src/geo/frame/__init__.py` disposition=`canonical` rank=`1` total_score=`58.94` risk=`HIGH`
- `src/geo/__init__.py` disposition=`quarantine` rank=`2` total_score=`57.5` risk=`HIGH`
- `src/geo/frame/domain_adapters.py` disposition=`quarantine` rank=`3` total_score=`50.75` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/camera_and_navigation.md, docs/audit/GEO0_RETRO_AUDIT.md, docs/audit/GEO10_RETRO_AUDIT.md, docs/audit/GEO2_RETRO_AUDIT.md, docs/audit/GEO_FRAMES_BASELINE.md, docs/audit/GEO_METRIC_BASELINE.md, docs/audit/GEO_PATHING_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md`

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
