Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.21b30fbdfb76aa6f`

- Symbol: `build_position_ref`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/frame/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/__init__.py`
- `src/geo/frame/__init__.py`
- `src/geo/frame/frame_engine.py`

## Scorecard

- `src/geo/frame/__init__.py` disposition=`canonical` rank=`1` total_score=`74.7` risk=`HIGH`
- `src/geo/__init__.py` disposition=`quarantine` rank=`2` total_score=`71.79` risk=`HIGH`
- `src/geo/frame/frame_engine.py` disposition=`quarantine` rank=`3` total_score=`68.45` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/WORLDDEFINITION_CONTRACT.md, docs/audit/EMBODIMENT_BASELINE_REPORT.md, docs/audit/GAL1_RETRO_AUDIT.md, docs/audit/GEO10_RETRO_AUDIT.md, docs/audit/GEO2_RETRO_AUDIT.md, docs/audit/GEO4_RETRO_AUDIT.md, docs/audit/GEO_FIELD_BINDING_BASELINE.md, docs/audit/GEO_FRAMES_BASELINE.md`

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
