Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.31eab3d2fa423840`

- Symbol: `extract_capabilities`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/pack/pack_validate.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tests/app/pack_resolution_tests.py`
- `tests/contentlib/contentlib_fab_validate_tests.py`
- `tests/contentlib/contentlib_pack_contract_tests.py`
- `tests/data_1/data1_fab_validate_tests.py`
- `tests/data_1/data1_pack_contract_tests.py`
- `tools/coverage/coverage_inspect.py`
- `tools/pack/capability_inspect.py`
- `tools/pack/pack_validate.py`

## Scorecard

- `tools/pack/pack_validate.py` disposition=`canonical` rank=`1` total_score=`70.55` risk=`HIGH`
- `tools/pack/capability_inspect.py` disposition=`quarantine` rank=`2` total_score=`68.05` risk=`HIGH`
- `tests/app/pack_resolution_tests.py` disposition=`merge` rank=`3` total_score=`63.6` risk=`HIGH`
- `tools/coverage/coverage_inspect.py` disposition=`merge` rank=`4` total_score=`63.23` risk=`HIGH`
- `tests/contentlib/contentlib_fab_validate_tests.py` disposition=`drop` rank=`5` total_score=`53.93` risk=`HIGH`
- `tests/data_1/data1_fab_validate_tests.py` disposition=`drop` rank=`6` total_score=`52.14` risk=`HIGH`
- `tests/data_1/data1_pack_contract_tests.py` disposition=`drop` rank=`7` total_score=`52.14` risk=`HIGH`
- `tests/contentlib/contentlib_pack_contract_tests.py` disposition=`drop` rank=`8` total_score=`45.36` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/CLI_CONTRACTS.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
