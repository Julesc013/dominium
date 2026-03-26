Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b5e6ad10e00ea249`

- Symbol: `build_compat_report`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/setup/setup_cli.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/ops/ops_cli.py`
- `tools/setup/setup_cli.py`

## Scorecard

- `tools/setup/setup_cli.py` disposition=`canonical` rank=`1` total_score=`61.61` risk=`HIGH`
- `tools/ops/ops_cli.py` disposition=`quarantine` rank=`2` total_score=`60.12` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/APPSHELL_CONSTITUTION.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/COMMANDS_AND_REFUSALS.md, docs/appshell/TUI_FRAMEWORK.md, docs/architecture/CANON_INDEX.md, docs/architecture/CHECKPOINTS.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/INVARIANT_REGISTRY.md`

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
