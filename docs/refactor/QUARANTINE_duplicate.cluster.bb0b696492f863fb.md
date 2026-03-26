Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.bb0b696492f863fb`

- Symbol: `repo_rel`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/contract/product_shell/product_shell_contract_tests.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `tests/contract/archive_presence_tests.py`
- `tests/contract/drp1_data_first_guard.py`
- `tests/contract/id_reuse_detection.py`
- `tests/contract/namespace_validation.py`
- `tests/contract/no_raw_file_paths_lint.py`
- `tests/contract/product_shell/product_shell_contract_tests.py`
- `tests/contract/unit_annotation_validation.py`

## Scorecard

- `tests/contract/product_shell/product_shell_contract_tests.py` disposition=`canonical` rank=`1` total_score=`66.49` risk=`HIGH`
- `tests/contract/namespace_validation.py` disposition=`quarantine` rank=`2` total_score=`66.04` risk=`HIGH`
- `tests/contract/archive_presence_tests.py` disposition=`quarantine` rank=`3` total_score=`61.67` risk=`HIGH`
- `tests/contract/id_reuse_detection.py` disposition=`quarantine` rank=`4` total_score=`60.25` risk=`HIGH`
- `tests/contract/unit_annotation_validation.py` disposition=`quarantine` rank=`5` total_score=`56.68` risk=`HIGH`
- `tests/contract/no_raw_file_paths_lint.py` disposition=`drop` rank=`6` total_score=`55.71` risk=`HIGH`
- `tests/contract/drp1_data_first_guard.py` disposition=`drop` rank=`7` total_score=`52.14` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/archive/repox/APRX_INVENTORY.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/REPO_TREE_INDEX.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
