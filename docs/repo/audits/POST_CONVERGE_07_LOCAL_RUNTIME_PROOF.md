# POST-CONVERGE-07 Local Runtime Proof Audit

## Status

- Task ID: POST-CONVERGE-07
- Result: blocked
- Date/time: 2026-05-12T21:17:57+10:00
- Branch: `main`
- HEAD SHA: `b5d89feadad1fe6ffa67a02ad8b849b7976b5086`
- origin/main SHA: `44bf83626fd1efade2d8e96ffe5bf8497a5aed3b`
- Working tree status before task: clean; `main` was ahead of `origin/main` by 2 local post-CONVERGE commits
- Working tree status after task: POST-CONVERGE-07 docs and validator modified for commit

## Scope

This task covered:

- canonical local runtime/playtest proof discovery
- product smoke command discovery
- local server/AppShell preflight check
- no new features
- no semantic changes
- no platform/render/native implementation

## Build Path Used

| Step | Command | Result | Not-run Reason |
| --- | --- | --- | --- |
| configure | `cmake --preset verify` | fail | Visual Studio 17 2022 generator instance is missing locally |
| build | `cmake --build --preset verify` | not run | configure failed |
| test | `ctest --preset verify` | not run | configure failed |

No build output was available under the expected verify binary directories, so product binaries were not executed.

## Product Commands Tested

| Product | Command | Result | Notes |
| --- | --- | --- | --- |
| server | `python apps/server/server_main.py --help` | partial | exited 0, but entered AppShell TUI because script invocation ignores `sys.argv[1:]` |
| server | `python apps/server/server_main.py --repo-root . --descriptor` | partial | exited 0, but also entered AppShell TUI; descriptor command was not honored as an actual script command |
| setup | `setup --help` | blocked | no built `setup` binary |
| launcher | `launcher --help` | blocked | no built `launcher` binary |
| client | `client --help` | blocked | no built `client` binary |
| server | `server --help` | blocked | no built `server` binary |

## Runtime Sequence Tested

| Step | Command/Input | Result | Evidence | Notes |
| --- | --- | --- | --- | --- |
| configure | `cmake --preset verify` | blocked | missing generator error | same blocker as POST-CONVERGE-06 |
| build | `cmake --build --preset verify` | not run | configure failed | no binaries |
| test | `ctest --preset verify` | not run | configure failed | no CTest proof |
| setup preflight | `setup --help` | blocked | no binary | target exists only in CMake |
| launcher preflight | `launcher --help` | blocked | no binary | target exists only in CMake |
| server preflight | Python server script | partial | AppShell TUI output | not a canonical binary proof |
| client preflight | `client --help` | blocked | no binary | target exists only in CMake |
| session create/select | not run | blocked | no build-proven command | no speculative runtime state created |
| local authority/server | not run | blocked | no build-proven command | no long-running server started |
| client attach | not run | blocked | no build-proven command | no local playtest session |
| status | not run | blocked | no build-proven command | not proven |
| save | not run | blocked | no build-proven command | not proven |
| load/resume | not run | blocked | no build-proven command | not proven |
| shutdown | not run | blocked | no runtime started | not applicable |

## Proof Status

Status: `blocked`

Reason:

- the canonical build path cannot configure on this machine
- product binaries are absent
- FAST remains in RepoX `DRIFT`
- the only runnable server script preflight does not honor CLI args when invoked as a script

This is not a full or partial local runtime proof. It is a blocked proof with exact blockers and durable command documentation.

## Blockers

- Missing local Visual Studio 17 2022 generator instance for `cmake --preset verify`.
- No validated fallback build lane.
- No local product binaries for `client`, `server`, `setup`, or `launcher`.
- FAST gate still fails as RepoX `DRIFT`.
- `apps/server/server_main.py` script invocation does not forward CLI args, so direct `--help` and `--descriptor` are not valid command-surface proof.
- No build-proven command exists for local session create/select, authority start, client attach, status, save, load/resume, or shutdown.

## Files Added/Changed

- Added `docs/repo/audits/POST_CONVERGE_07_LOCAL_RUNTIME_PROOF.md`.
- Added `docs/runtime/CANONICAL_LOCAL_PLAYTEST.md`.
- Added `docs/release/LOCAL_RUNTIME_PROOF.md`.
- Added `tools/validators/check_local_playtest_path.py`.
- Updated `docs/repo/POST_CONVERGE_NEXT_STEPS.md`.
- Updated `docs/repo/BUILD_VERIFICATION_PATHS.md`.
- Updated `.aide/context/latest-task-packet.md`.
- Refreshed `tools/migration/root_inventory.json`.
- Refreshed `tools/migration/root_move_map.json`.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `cmake --preset verify` | fail | `Visual Studio 17 2022` generator instance is missing locally |
| `cmake --build --preset verify` | not run | configure failed |
| `ctest --preset verify` | not run | configure failed |
| `python apps/server/server_main.py --help` | partial | exits 0, enters AppShell TUI because CLI args are not forwarded |
| `python apps/server/server_main.py --repo-root . --descriptor` | partial | exits 0, enters AppShell TUI; descriptor command not honored |
| `python tools/validators/check_local_playtest_path.py --repo-root .` | pass | audit mode reports `proof_status: blocked` |
| `python tools/validators/check_local_playtest_path.py --repo-root . --json` | pass | JSON report emitted |
| `python tools/validators/check_local_playtest_path.py --repo-root . --dry-run` | pass | command sequence printed without running runtime |
| `python tools/validators/check_local_playtest_path.py --repo-root . --strict` | fail as expected | exit code 2 because full local playtest path is blocked |
| `python -m py_compile tools/validators/check_local_playtest_path.py` | pass | validator parses |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | unexcepted violations: 0 after generated local roots were removed |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | unexcepted violations: 0 after generated local roots were removed |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | warnings: 0 |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | warnings: 0 |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | build boundary checks passed |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK |
| `python .aide/scripts/aide_lite.py doctor` | pass | existing warnings only |
| `python .aide/scripts/aide_lite.py validate` | pass | existing review-packet warnings only |
| `python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-07 local runtime proof"` | pass | task packet written |
| `git diff --check` | pass | final whitespace check |
| `git diff --cached --check` | pass | final staged whitespace check |

## Next Recommended Task

Targeted remediation before POST-CONVERGE-08:

- install or expose the Visual Studio 17 2022 verify lane, or provide an accepted CI proof
- run `cmake --preset verify`, `cmake --build --preset verify`, and `ctest --preset verify`
- remediate or explicitly accept remaining RepoX `DRIFT`
- then rerun POST-CONVERGE-07 before product boot matrix proof

## POST-CONVERGE-08 Follow-up Note

POST-CONVERGE-08 was attempted on 2026-05-12 at the user's request. It recorded partial script/wrapper help proof for launcher, client, server, and the attach-console tool stub, but no native product binary proof. Setup remains blocked in the Python bridge on local Python 3.8, and `dist/bin/dom` points at a missing wrapper target. See `docs/repo/audits/POST_CONVERGE_08_PRODUCT_BOOT_MATRIX_PROOF.md`.
