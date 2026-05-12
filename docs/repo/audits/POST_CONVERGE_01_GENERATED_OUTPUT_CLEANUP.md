# POST-CONVERGE-01 Generated / Output Root Cleanup

## Status

- Task ID: POST-CONVERGE-01
- Result: pass with review carryover
- Date/time: 2026-05-12T18:27:48+10:00
- Branch: `main`
- HEAD SHA before cleanup: `20ecdf86a6321f87360396eb57988e1fa2987557`
- HEAD SHA after cleanup before commit: `20ecdf86a6321f87360396eb57988e1fa2987557`
- `origin/main` SHA: `20ecdf86a6321f87360396eb57988e1fa2987557`
- Working tree before task: clean tracked tree, with untracked Python `__pycache__/` directories from prior validation.
- Working tree after cleanup before commit: tracked doc/ledger/inventory updates only.

## Scope

This task targeted only root generated/output/cache exceptions:

- `.xstack_cache`
- `artifacts`
- `build`
- `dist`
- `out`

No product roots moved. No runtime roots moved. No domain roots moved. No source semantics changed. No feature work was performed.

## Pre-Cleanup State

| Root | Exists? | Tracked? | Ignored? | Classification | Notes |
| --- | --- | --- | --- | --- | --- |
| `.xstack_cache` | yes | no | yes | ignored generated/cache safe to remove | 116 files, 133 directories; generated XStack cache/evidence residue. |
| `artifacts` | yes | yes, 10 files | no | tracked provenance review | Tracked `artifacts/toolchain_runs/...` JSON evidence; not deleted. |
| `build` | yes | no | yes | ignored generated build output safe to remove | 4 files, 9 directories under `build/appshell/`. |
| `dist` | yes | yes, 13 files | no | tracked distribution projection review | Tracked wrappers, pack/profile/lock projection files, and `.gitkeep` files; not deleted. |
| `out` | yes | no | yes | ignored generated output safe to remove | 6 files, 8 directories under `out/build/`. |

## Actions Taken

| Root | Action | Files removed? | Git-tracked changes? | Exception status | Notes |
| --- | --- | --- | --- | --- | --- |
| `.xstack_cache` | removed_untracked_generated | yes | no | retired | Removed after confirming zero tracked files and ignored status. |
| `artifacts` | left_for_review | no | no | active/narrowed | Kept because tracked toolchain-run provenance may need release/evidence policy handling. |
| `build` | removed_untracked_generated | yes | no | retired | Removed after confirming zero tracked files and ignored status. |
| `dist` | left_for_review | no | no | active/narrowed | Kept because tracked distribution projection files require policy review. |
| `out` | removed_untracked_generated | yes | no | retired | Removed after confirming zero tracked files and ignored status. |

Root-level and nested Python `__pycache__/` directories were also removed as generated validation residue. They were not layout-exception targets, but root-level `__pycache__/` appeared as an unexcepted strict-layout violation after the cleanup pass.

## .gitignore Changes

`.gitignore` already ignored `.xstack_cache/`, `build/`, `dist/`, and `out/`. No ignore was added for `artifacts/` because tracked provenance remains there pending review.

The file now re-ignores `**/__pycache__` after the broad `!/engine/**` and `!/game/**` source allow-list negations, so Python bytecode caches do not reappear as untracked source-tree noise.

## Exception Ledger Changes

| Exception ID | Path | Previous Active? | New Active? | New Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `xstack_cache_root` | `.xstack_cache` | true | false | retired | Moved under `retired_exceptions.*` in the ledger for audit history. |
| `artifacts_root` | `artifacts` | true | true | narrowed | Active because tracked toolchain-run provenance remains. |
| `build_root` | `build` | true | false | retired | Moved under `retired_exceptions.*` in the ledger for audit history. |
| `dist_root` | `dist` | true | true | narrowed | Active because tracked distribution projection files remain. |
| `out_root` | `out` | true | false | retired | Moved under `retired_exceptions.*` in the ledger for audit history. |

Active layout exceptions changed from 37 to 34. Unexcepted strict violations remain 0.

## Remaining Generated/Output Exceptions

- `artifacts_root`: still active because `artifacts/` contains tracked toolchain-run evidence JSON.
- `dist_root`: still active because `dist/` contains tracked distribution projection wrappers, locks, pack aliases, profile data, and `.gitkeep` files.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root .` | pass | Active exceptions: 34; unexcepted violations: 0. |
| `python tools/validators/check_repo_layout.py --repo-root . --json --no-write` | pass | JSON report emitted; active exceptions: 34. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | Strict result: pass. |
| `python tools/validators/check_root_allowlist.py --repo-root .` | pass | Active exceptions: 34; unexcepted violations: 0. |
| `python tools/validators/check_root_allowlist.py --repo-root . --json` | pass | JSON report emitted; active exceptions: 34. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | Strict result: pass. |
| `python tools/validators/check_distribution_layout.py --repo-root .` | pass | No warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | Strict result: pass. |
| `python tools/validators/check_component_matrices.py --repo-root .` | pass | No warnings. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | Strict result: pass. |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | Docs sanity OK after adding this report. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK. |
| `git diff --check` | pass | Line-ending warnings only; no whitespace errors. |
| `git diff --cached --check` | pass | No staged changes at check time. |

CMake, build, CTest, and FAST were not run in this task. POST-CONVERGE-00 already diagnosed the local Visual Studio generator issue and existing FAST/XStack blocker, and this task was scoped away from build/FAST remediation.

## Risks

- `artifacts/` may contain provenance needed for release, evidence, or audit policy.
- `dist/` may contain intentionally tracked distribution projection fixtures or historical release inputs.
- This task did not prove the build; it only preserved validator and supplemental audit health.

## Next Recommended Task

`POST-CONVERGE-02 - Root Wrapper / Tooling / Governance Cleanup`
