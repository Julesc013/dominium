Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.333b9f17445b2110`

- Symbol: `repo_rel`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/invariant/process_only_mutation_tests.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tests/app/path_hygiene_tests.py`
- `tests/app/slice0_hardcoded_ids.py`
- `tests/app/slice1_hardcoded_constants.py`
- `tests/app/slice2_hardcoded_roles.py`
- `tests/contract/archive_presence_tests.py`
- `tests/contract/drp1_data_first_guard.py`
- `tests/contract/id_reuse_detection.py`
- `tests/contract/namespace_validation.py`
- `tests/contract/no_raw_file_paths_lint.py`
- `tests/contract/product_shell/product_shell_contract_tests.py`
- `tests/contract/unit_annotation_validation.py`
- `tests/invariant/capability_scope_tests.py`
- `tests/invariant/content_id_reference_tests.py`
- `tests/invariant/float_authoritative_tests.py`
- `tests/invariant/invariant_lang_c89.py`
- `tests/invariant/invariant_lang_cpp98.py`
- `tests/invariant/invariant_no_anon_rng.py`
- `tests/invariant/invariant_no_raw_paths.py`
- `tests/invariant/invariant_no_wallclock.py`
- `tests/invariant/process_only_mutation_tests.py`
- `tests/invariant/terrain_authority_invariant.py`
- `tools/ci/arch_checks.py`

## Scorecard

- `tests/invariant/process_only_mutation_tests.py` disposition=`canonical` rank=`1` total_score=`75.0` risk=`HIGH`
- `tests/invariant/invariant_no_raw_paths.py` disposition=`quarantine` rank=`2` total_score=`67.34` risk=`HIGH`
- `tests/contract/product_shell/product_shell_contract_tests.py` disposition=`quarantine` rank=`3` total_score=`66.49` risk=`HIGH`
- `tests/contract/namespace_validation.py` disposition=`quarantine` rank=`4` total_score=`66.04` risk=`HIGH`
- `tests/contract/archive_presence_tests.py` disposition=`merge` rank=`5` total_score=`61.67` risk=`HIGH`
- `tests/invariant/terrain_authority_invariant.py` disposition=`drop` rank=`6` total_score=`61.11` risk=`HIGH`
- `tests/app/path_hygiene_tests.py` disposition=`merge` rank=`7` total_score=`60.25` risk=`HIGH`
- `tests/contract/id_reuse_detection.py` disposition=`merge` rank=`8` total_score=`60.25` risk=`HIGH`
- `tests/invariant/capability_scope_tests.py` disposition=`merge` rank=`9` total_score=`60.14` risk=`HIGH`
- `tests/invariant/content_id_reference_tests.py` disposition=`merge` rank=`10` total_score=`60.14` risk=`HIGH`
- `tests/invariant/float_authoritative_tests.py` disposition=`drop` rank=`11` total_score=`60.14` risk=`HIGH`
- `tools/ci/arch_checks.py` disposition=`drop` rank=`12` total_score=`60.12` risk=`HIGH`
- `tests/contract/unit_annotation_validation.py` disposition=`merge` rank=`13` total_score=`56.68` risk=`HIGH`
- `tests/contract/no_raw_file_paths_lint.py` disposition=`merge` rank=`14` total_score=`55.71` risk=`HIGH`
- `tests/app/slice0_hardcoded_ids.py` disposition=`merge` rank=`15` total_score=`52.14` risk=`HIGH`
- `tests/app/slice1_hardcoded_constants.py` disposition=`merge` rank=`16` total_score=`52.14` risk=`HIGH`
- `tests/app/slice2_hardcoded_roles.py` disposition=`merge` rank=`17` total_score=`52.14` risk=`HIGH`
- `tests/contract/drp1_data_first_guard.py` disposition=`drop` rank=`18` total_score=`52.14` risk=`HIGH`
- `tests/invariant/invariant_lang_c89.py` disposition=`drop` rank=`19` total_score=`49.88` risk=`HIGH`
- `tests/invariant/invariant_lang_cpp98.py` disposition=`drop` rank=`20` total_score=`49.88` risk=`HIGH`
- `tests/invariant/invariant_no_anon_rng.py` disposition=`drop` rank=`21` total_score=`46.31` risk=`HIGH`
- `tests/invariant/invariant_no_wallclock.py` disposition=`drop` rank=`22` total_score=`45.87` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/VALIDATION_RULES.md, docs/audit/BOM_AG_BASELINE.md, docs/audit/CANON_CONFORMANCE_REPORT.md, docs/audit/CANON_MAP.md, docs/audit/CHEM_DEGRADATION_BASELINE.md, docs/audit/CIVILISATION_SUBSTRATE_BASELINE.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
