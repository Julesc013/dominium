# MOVE-FAMILY-00B-PLAN Validation

Status: DRAFT
Last Reviewed: 2026-05-17

## Initial State

- Branch: `main`.
- HEAD at start: `18ca419fc22e623166f02fede283d2594951b29e`.
- `origin/main` after fetch: `18ca419fc22e623166f02fede283d2594951b29e`.
- Expected prior commit present: yes.
- `.aide.local/` and `.dominium.local/`: ignored/local.

## Evidence Checks

- Prior MOVE-FAMILY-00-PLAN blocked evidence inspected.
- MOVE-FAMILY-00-REFINE manifest recommendation inspected.
- Root constitution, ownership slots, and layout exception evidence inspected.
- Current `ide/manifests/**` tracked files inspected with `git ls-files`.
- Manifest JSON/schema content inspected and parsed.
- Current references and consumers scanned with `rg`.

## Final Validation

| Command | Result | Notes |
| --- | --- | --- |
| JSON parse for MOVE-FAMILY-00B plan artifacts | PASS | Parsed 8 JSON files. |
| TOML parse for `.aide/refactors/MOVE-FAMILY-00B.plan.toml` | PASS | Parsed with Python `tomllib`. |
| IDE manifest structural check | PASS | Both example manifests include required schema fields and no unknown top-level fields. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE Lite environment healthy. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | No validation failures. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE Lite tests passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Portable selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tool registry validation passed; no provider/model/network calls. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Root validation passed; validator refreshed `tools/migration/*` timestamps, then this task restored that out-of-scope churn. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo validation passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Previous commit metadata valid. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict pass; validator emitted TOML fallback-parser warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict pass; validator emitted TOML fallback-parser warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict pass; validator emitted TOML fallback-parser warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict pass; validator emitted TOML fallback-parser warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK. |
| `git status --short -- ide contracts tools apps engine game runtime content tests cmake release` | PASS | No protected target/source path modifications after restoring `tools/migration/*` validator churn. |
| `git status --short --ignored .dominium.local .aide.local` | PASS_WITH_WARNINGS | Ignored local roots present only as generated evidence. |

## Not Run By Scope

- Full CTest.
- Full eval.
- CMake configure/build.
- Product binaries.
- Package/release generation.
- Move/apply commands.
- Unknown XStack/AuditX/RepoX/TestX execution.
