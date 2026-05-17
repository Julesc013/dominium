# MOVE-BULK-01-APPLY Validation

## Status

Validation passed after applying the 26-file safe subset and repairing the latest AIDE task/review packets that initially missed required sections.

## Planned Commands

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | Initial run failed because packet sections were missing; rerun passed after packet repair |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Initial run failed on packet section requirements; rerun passed after packet repair |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE Tier 0 |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE Tier 0 |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE Tier 0 |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE Tier 0 |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE Tier 0 |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest committed task check |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Known `tomllib` fallback-parser warnings |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Known `tomllib` fallback-parser warnings |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Known `tomllib` fallback-parser warning |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Known `tomllib` fallback-parser warning |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build target boundaries |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundaries |
| Applied old-path scan | PASS | 0 exact matches for the 26 moved old paths before reports were written |
| Gate/Batch/evidence JSON parse | PASS | Gate authorization, Batch A, reference, validation, rollback, exception, and apply evidence JSON parsed |
| Moved JSON parse | PASS | 26 moved JSON files parsed |
| `git status --short --branch` | PASS | Only scoped changes present before staging |
| `git diff --check` | PASS | Whitespace |
| `git diff --cached --check` | PASS | Staged whitespace |

Focused RepoX is not required by MOVE-BULK-00-GATE for Batch A Tier 0 and was not run unless validation evidence later requires it.
