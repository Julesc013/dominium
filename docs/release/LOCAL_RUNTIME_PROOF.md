Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Local Runtime Proof

## Status

- Phase: POST-CONVERGE-07
- Status: blocked

## Product Surfaces

| Product | Mode | Command | Result | Notes |
| --- | --- | --- | --- | --- |
| setup | cli | `setup --help` | blocked | CMake target `setup_cli` outputs `setup`, but no local binary exists. |
| setup | Python bridge | `python tools/setup/setup_cli.py --help` | blocked | Fails before help on local Python 3.8 due import-time union annotation. |
| launcher | cli | `launcher --help` | blocked | CMake target `launcher_cli` outputs `launcher`, but no local binary exists. |
| launcher | Python AppShell bridge | `python tools/launcher/launch.py --help` | partial | AppShell help emits for `product_id: launcher`; native binary not proven. |
| client | cli/rendered/tui | `client --help` | blocked | CMake target `dominium_client` outputs `client`, but no local binary exists. |
| client | tracked wrapper | `python archive/generated/dist/bin/dominium_client --help` | partial | AppShell help emits for `product_id: client`; native binary not proven. |
| server | headless/cli/tui | `server --help` | blocked | CMake target `dominium_server` outputs `server`, but no local binary exists. |
| server | tracked wrapper | `python archive/generated/dist/bin/dominium_server --help` | partial | AppShell help emits for `product_id: server`; native binary not proven. |
| server | Python AppShell preflight | `python apps/server/server_main.py --help` | partial | Exits 0, but enters AppShell TUI because script invocation does not forward CLI args. |
| tools | cli | `tools --help` | blocked | CMake target `dominium-tools` outputs `tools`, but no local binary exists. |
| tools | AppShell tool stub | `python tools/validators/shell/product_stub_cli.py --product-id tool.attach_console_stub --help` | partial | AppShell help emits for the attach-console tool stub; shipped tools host not proven. |

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
- POST-CONVERGE-08 product boot proof: `docs/release/PRODUCT_BOOT_PROOF.md`.
- Canonical playtest path: `docs/runtime/CANONICAL_LOCAL_PLAYTEST.md`.
- Local playtest validator: `tools/validators/check_local_playtest_path.py`.
- Product boot validator: `tools/validators/check_product_boot_matrix.py`.

No runtime log bundle, screenshot, save artifact, or proof bundle was produced because the full runtime path is blocked before build.

## Readiness For Product Boot Matrix

POST-CONVERGE-08 was attempted at the user's request and recorded partial script/wrapper help proof. It did not produce native product binary proof. POST-CONVERGE-09 should not proceed until the build lane and product boot blockers in `docs/release/PRODUCT_BOOT_PROOF.md` are resolved or explicitly accepted.

## POST-CONVERGE-10L Update

POST-CONVERGE-10L did not run product boot proof. It classified the focused RepoX distribution/product family as missing `archive/generated/dist/bin` wrapper/projection proof, including the absent `archive/generated/dist/bin/tool_attach_console_stub` target used by `archive/generated/dist/bin/dom`. Native product boot proof remains a separate POST-CONVERGE-11 task, and portable projection wrapper proof remains a POST-CONVERGE-12 or targeted dist wrapper task.

## POST-CONVERGE-10O Update

POST-CONVERGE-10O did not run product boot proof. The closeout gate keeps POST-CONVERGE-11 blocked because focused RepoX still has real non-proof governance/source-policy failures in addition to product/projection proof blockers.
