Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.ba30ba0401c9833c`

- Symbol: `load_text`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/contract/product_shell/product_shell_contract_tests.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tests/contract/frozen_contracts_guard.py`
- `tests/contract/id_reuse_detection.py`
- `tests/contract/product_shell/product_shell_contract_tests.py`

## Scorecard

- `tests/contract/product_shell/product_shell_contract_tests.py` disposition=`canonical` rank=`1` total_score=`66.49` risk=`HIGH`
- `tests/contract/frozen_contracts_guard.py` disposition=`quarantine` rank=`2` total_score=`61.21` risk=`HIGH`
- `tests/contract/id_reuse_detection.py` disposition=`quarantine` rank=`3` total_score=`60.25` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/CHECKPOINTS.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/SLICE_0_CONTRACT.md, docs/archive/repox/APRX_INVENTORY.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/REPO_TREE_INDEX.md`

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
