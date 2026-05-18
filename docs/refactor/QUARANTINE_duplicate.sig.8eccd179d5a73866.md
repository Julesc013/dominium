Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.8eccd179d5a73866`

- Symbol: `product_capability_default_rows_by_id`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/tools/validators/compatibility/descriptor/descriptor_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/tools/validators/compatibility/descriptor/descriptor_engine.py`
- `src/tools/release/build_id_engine.py`

## Scorecard

- `src/tools/validators/compatibility/descriptor/descriptor_engine.py` disposition=`canonical` rank=`1` total_score=`68.39` risk=`HIGH`
- `src/tools/release/build_id_engine.py` disposition=`quarantine` rank=`2` total_score=`60.12` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/apps/CLI_CONTRACTS.md, docs/apps/PRODUCT_BOUNDARIES.md, docs/apps/TESTX_COMPLIANCE.md, docs/runtime/shell/APPSHELL_CONSTITUTION.md, docs/runtime/shell/CLI_REFERENCE.md, docs/runtime/shell/COMMANDS_AND_REFUSALS.md, docs/runtime/shell/IPC_DISCOVERY.md, docs/runtime/shell/TUI_FRAMEWORK.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validators/suite/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
