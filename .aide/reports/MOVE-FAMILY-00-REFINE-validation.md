# MOVE-FAMILY-00-REFINE Validation

Status: DERIVED
Last Reviewed: 2026-05-17

## Initial State

- Branch: `main`.
- HEAD at start: `602eda2271cf0ad342a4f52d6c3ea677d3d610da`.
- `origin/main`: `602eda2271cf0ad342a4f52d6c3ea677d3d610da`.
- Expected prior commit present: yes.
- `.aide.local/` and `.dominium.local/`: ignored/local.

## Evidence Checks

- Prior MOVE-FAMILY-00 blocked plan inspected.
- AIDE root inventories, classifications, references, and salvage maps inspected.
- Root constitution, ownership slots, and layout exception ledger inspected.
- Current tracked target-root file list inspected with `git ls-files governance meta performance validation ide`.
- Direct import/reference scans run with `rg`.

## Final Validation

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE Lite environment healthy. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | No validation failures. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE Lite tests passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Portable selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tool registry validation passed; no provider/model/network calls enabled. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Root validation passed; validator refreshed `tools/migration/*` timestamps, then this task restored that out-of-scope churn. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo validation passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Previous commit metadata valid. |
| JSON parse for new MOVE-FAMILY-00 refine reports | PASS | Parsed 5 JSON artifacts. |
| TOML parse for refined cleanup strategy | PASS | Parsed with Python `tomllib`. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict pass; validator emitted TOML fallback-parser warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict pass; validator emitted TOML fallback-parser warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict pass; validator emitted TOML fallback-parser warnings. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict pass; validator emitted TOML fallback-parser warnings. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK. |
| `git status --short -- governance meta performance validation ide` | PASS | No target-root modifications. |
| `git status --short --ignored .dominium.local .aide.local` | PASS_WITH_WARNINGS | Ignored local roots present only as generated evidence. |

## Not Run By Scope

- Full CTest.
- Full eval.
- CMake configure/build.
- Product binaries.
- Package/release generation.
- Move/apply commands.
- Unknown XStack/AuditX/RepoX/TestX execution.
