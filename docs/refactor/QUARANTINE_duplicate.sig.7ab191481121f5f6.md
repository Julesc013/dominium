Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7ab191481121f5f6`

- Symbol: `_resolve_path`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/appshell/paths/virtual_paths.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/appshell/paths/virtual_paths.py`
- `src/lib/install/install_discovery_engine.py`

## Scorecard

- `src/appshell/paths/virtual_paths.py` disposition=`canonical` rank=`1` total_score=`73.87` risk=`MED`
- `src/lib/install/install_discovery_engine.py` disposition=`quarantine` rank=`2` total_score=`73.09` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/IPC_DISCOVERY.md, docs/appshell/VIRTUAL_PATHS.md, docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/CLEAN_ROOM_win64.md, docs/audit/DIST2_RETRO_AUDIT.md, docs/audit/DISTRIBUTION_ARCHITECTURE_FREEZE.md, docs/audit/DOC_DRIFT_MATRIX.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
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
