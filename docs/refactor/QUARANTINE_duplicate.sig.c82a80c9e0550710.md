Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c82a80c9e0550710`

- Symbol: `build_client_main_menu_surface`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/client/ui/main_menu_surface.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/client/ui/__init__.py`
- `src/client/ui/main_menu_surface.py`

## Scorecard

- `src/client/ui/main_menu_surface.py` disposition=`canonical` rank=`1` total_score=`74.94` risk=`HIGH`
- `src/client/ui/__init__.py` disposition=`quarantine` rank=`2` total_score=`72.38` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/TUI_FRAMEWORK.md, docs/architecture/CANON_INDEX.md, docs/architecture/CHECKPOINTS.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/PRODUCT_SHELL_CONTRACT.md, docs/architecture/SLICE_0_CONTRACT.md, docs/audit/CANON_MAP.md, docs/audit/DIST5_UX_POLISH_FINAL.md`

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
