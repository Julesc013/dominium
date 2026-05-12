# Local Runtime Proof

## Status

- Phase: POST-CONVERGE-07
- Status: blocked

## Product Surfaces

| Product | Mode | Command | Result | Notes |
| --- | --- | --- | --- | --- |
| setup | cli | `setup --help` | blocked | CMake target `setup_cli` outputs `setup`, but no local binary exists. |
| launcher | cli | `launcher --help` | blocked | CMake target `launcher_cli` outputs `launcher`, but no local binary exists. |
| client | cli/rendered/tui | `client --help` | blocked | CMake target `dominium_client` outputs `client`, but no local binary exists. |
| server | headless/cli/tui | `server --help` | blocked | CMake target `dominium_server` outputs `server`, but no local binary exists. |
| server | Python AppShell preflight | `python apps/server/server_main.py --help` | partial | Exits 0, but enters AppShell TUI because script invocation does not forward CLI args. |
| tools | cli | CMake `all_tools` / tool targets | blocked | Product tools are planned; build output is not available. |

## Session / Authority / Save / Resume Proof

| Step | Result | Evidence | Notes |
| --- | --- | --- | --- |
| build | blocked | `cmake --preset verify` fails with missing VS 2022 generator | No build output. |
| setup preflight | blocked | no `setup` binary | Help cannot be run. |
| launcher preflight | blocked | no `launcher` binary | Help cannot be run. |
| server preflight | partial | `python apps/server/server_main.py --help` exits 0 | Actual script args are ignored; this is not product CLI proof. |
| session create/select | blocked | no build-proven command | Existing Python modules suggest session machinery, but no canonical product command was proven. |
| local authority/server | blocked | no `server` binary | Python server command surface is not canonical proof. |
| client attach | blocked | no `client` binary | No local client path was run. |
| status | blocked | no build-proven command | Not proven. |
| save | blocked | no build-proven command | Not proven. |
| load/resume | blocked | no build-proven command | Not proven. |
| shutdown | blocked | no runtime started | Not proven. |

## Logs And Evidence

- POST-CONVERGE-06 build evidence: `docs/repo/audits/POST_CONVERGE_06_BUILD_FAST_REMEDIATION.md`.
- POST-CONVERGE-07 audit: `docs/repo/audits/POST_CONVERGE_07_LOCAL_RUNTIME_PROOF.md`.
- Canonical playtest path: `docs/runtime/CANONICAL_LOCAL_PLAYTEST.md`.
- Local playtest validator: `tools/validators/check_local_playtest_path.py`.

No runtime log bundle, screenshot, save artifact, or proof bundle was produced because the full runtime path is blocked before build.

## Readiness For Product Boot Matrix

POST-CONVERGE-08 should not proceed yet. The next work should resolve the local verify toolchain/build proof, then address remaining RepoX `DRIFT` or accept it through review before product boot matrix proof.
