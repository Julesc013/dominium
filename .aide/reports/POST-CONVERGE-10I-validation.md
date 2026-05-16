# POST-CONVERGE-10I Validation

Status: PARTIAL

## Focused Validation

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | pass | Started clean at `main`; local and origin were equal at `978818004c435ad2ca53355e065a888800fe2a94`. |
| `git fetch --all --prune` | pass | Remote refs fetched; no divergence. |
| `ctest --preset verify -N` | pass_with_warning | Canonical verify preset still discovers 0 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | pass_with_warning | Canonical verify lane still has no matching tests. |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R inv_repox_rules --output-on-failure` | fail_expected | Before remediation reproduced focused RepoX failure with historical-reference debt; after remediation focused tuple RepoX still fails with 71 failures and 5 warnings, with `INV-CANON-NO-HIST-REF` reduced to 0. |
| `python scripts/ci/check_repox_rules.py --repo-root . --proof-manifest-out .dominium.local/ctest/repox/proof_manifest_10i_after_rule_uncached.json --profile-out .dominium.local/ctest/repox/REPOX_PROFILE_10i_after_rule_uncached.json` | fail_expected | Uncached direct RepoX reports 71 failures and 5 warnings. |

## Final Validator Suite

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | pass | AIDE doctor passed after latest task/review packets were kept in the required structured format. |
| `py -3 .aide/scripts/aide_lite.py validate` | pass | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | pass | AIDE internal tests passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | pass | AIDE selftests passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | pass | AIDE tools validation passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | pass | AIDE roots validation passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | pass | AIDE repo validation passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | pass | Latest pre-10I commit check passed. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass_with_warning | Strict repo layout passed; Python emitted the known `tomllib` fallback warning. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass_with_warning | Strict root allowlist passed; Python emitted the known `tomllib` fallback warning. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | Strict distribution layout passed. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass_with_warning | Strict component matrix validation passed; Python emitted the known `tomllib` fallback warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK. |
| JSON parse for POST-CONVERGE-10I reports | pass | Historical-reference findings and before/after JSON parsed successfully. |
| `git diff --check` | pass | Whitespace check passed after final status-note normalization. |

## Not Run

- Full CTest: not run by task scope because focused RepoX remains a semantic governance failure.
- Build/package/release/product boot proof: not run by task scope.

## Generated Side Effects

Strict validators rewrote `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json` timestamp/HEAD fields during validation. Those generated metadata side effects are outside 10I scope and were removed before staging.
