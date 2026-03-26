Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.a72e5a1e4be96773`

- Symbol: `projection_profile_registry_hash`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/__init__.py`
- `src/geo/lens/__init__.py`

## Scorecard

- `src/geo/__init__.py` disposition=`canonical` rank=`1` total_score=`71.79` risk=`HIGH`
- `src/geo/lens/__init__.py` disposition=`quarantine` rank=`2` total_score=`65.6` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/TUI_FRAMEWORK.md, docs/architecture/CANON_INDEX.md, docs/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/EARTH4_RETRO_AUDIT.md, docs/audit/GAL0_RETRO_AUDIT.md, docs/audit/GALAXY_PROXY_BASELINE.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
