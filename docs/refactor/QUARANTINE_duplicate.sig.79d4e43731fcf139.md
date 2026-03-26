Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.79d4e43731fcf139`

- Symbol: `canonical_platform_id`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/platform/platform_probe.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/platform/__init__.py`
- `src/platform/platform_probe.py`

## Scorecard

- `src/platform/platform_probe.py` disposition=`canonical` rank=`1` total_score=`78.45` risk=`HIGH`
- `src/platform/__init__.py` disposition=`quarantine` rank=`2` total_score=`75.0` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/RUNTIME_LOOP.md, docs/app/TESTX_COMPLIANCE.md, docs/appshell/UI_MODE_RESOLUTION.md, docs/architecture/CONTROL_LAYERS.md, docs/archive/app/APR1_RUNTIME_AUDIT.md, docs/audit/CLEAN_ROOM_win64.md, docs/audit/EARTH1_RETRO_AUDIT.md, docs/audit/EARTH_PROCEDURAL_BASELINE.md`

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
