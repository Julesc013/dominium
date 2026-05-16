# AIDE-GATE-03 Post-Move Proof and Next Wave Readiness Gate

## Status

- Task ID: AIDE-GATE-03
- Gate result: PASS_WITH_WARNINGS
- Branch: main
- HEAD before gate evidence: 9a05800601809463ea596a84e2c8bdc9fcffdbad
- origin/main after fetch: 9a05800601809463ea596a84e2c8bdc9fcffdbad
- Working tree before evidence: clean
- Working tree after validation before evidence: clean after removing validator timestamp/SHA-only metadata side effects

## Purpose

AIDE-MOVE-01-APPLY was the first real AIDE-controlled move. This gate proves the move stayed inside scope, validators still pass, deferred material remained untouched, old references are intentionally preserved evidence, and the next phase may only plan another move wave.

## Sync State

Local `main` equals `origin/main` at the AIDE-MOVE-01-APPLY commit. This is an accepted synced state for this gate. No pull, rebase, reset, or push was run.

## Applied Move Verification

| Expected | Actual | Result | Notes |
| --- | --- | --- | --- |
| `ide/README.md` absent | Not tracked and not present | PASS | Source path no longer exists after AIDE-MOVE-01-APPLY. |
| `docs/architecture/IDE_PROJECTIONS.md` present | Tracked and present | PASS | Target path contains the moved projection policy document. |
| Move commit present | HEAD includes `9a05800601809463ea596a84e2c8bdc9fcffdbad` | PASS | Commit subject: `chore(repo): move IDE projection notes into docs`. |
| Only authorized move applied | One rename from old README path to architecture doc path | PASS | Commit diff contains no other file move. |

## Deferred Material

`ide/manifests/**` remains tracked, present, and untouched. The `ide/` root still exists only for deferred manifest metadata and generated projection output policy.

## Reference Rewrite Verification

- Planned apply-phase rewrites: 6
- Applied rewrites reported: 6
- Active current references checked: no current active source/tool/docs path still points to the old README.
- Remaining old references are allowed historical/audit/generated review references:
  - `data/architecture/module_registry*.json`
  - `data/architecture/architecture_graph*.json`
  - `docs/audit/REPO_STRUCTURE_AUDIT.json`
  - root-recycling planning and result documents

## Exception State

`contracts/repo/layout_exceptions.toml` was not changed by AIDE-MOVE-01-APPLY. The `ide` exception remains active, which is correct because `ide/manifests/**` remains deferred.

## Unauthorized Change Check

The AIDE-MOVE-01-APPLY commit changed only:

- moved doc file,
- planned reference rewrite files,
- AIDE reports/context/ledger/status surfaces,
- root-recycling docs.

No product/source/runtime/build files changed. No active aliases, shims, move maps, salvage maps, or exception retirements were introduced.

## Validation Results

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Clean before gate evidence. |
| `git fetch --all --prune` | PASS | Remote remained equal to local HEAD. |
| `git rev-parse HEAD` | PASS | `9a05800601809463ea596a84e2c8bdc9fcffdbad`. |
| `git rev-parse origin/main` | PASS | `9a05800601809463ea596a84e2c8bdc9fcffdbad`. |
| `git merge-base --is-ancestor origin/main HEAD` | PASS | Exit code 0. |
| `git merge-base --is-ancestor HEAD origin/main` | PASS | Exit code 0. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE test passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest commit message passed. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; Python emitted `tomllib` fallback warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; Python emitted `tomllib` fallback warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; Python emitted a `tomllib` fallback warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; Python emitted a `tomllib` fallback warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity passed. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity passed. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check passed. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged diff at validation time. |

## Known Warnings

- Remaining old-path references are historical, audit, generated review, or root-recycling evidence.
- `ide/` remains because deferred manifests remain.
- Strict validators run through `python` emit non-blocking `tomllib` fallback warnings.
- Strict validators temporarily rewrote generated migration metadata headers; those timestamp/SHA-only side effects were removed because this gate cannot write those paths.
- Full eval, full CTest, CMake configure/build, package/release generation, and product binaries remain out of scope.

## Blockers

None.

## Gate Decision

PASS_WITH_WARNINGS. The first move is verified, validator health is intact, deferred material remained untouched, and warnings are known/non-blocking.

## Authorization

`AIDE-MOVE-02-PLAN may proceed. No move application is authorized.`
