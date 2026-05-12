# POST-CONVERGE-08 Product Boot Matrix Proof Audit

## Status

- Task ID: POST-CONVERGE-08
- Result: partial
- Date/time: 2026-05-12T21:38:30+10:00
- Branch: `main`
- HEAD SHA: `4ccb80276ed4e2b250876fd1e037ccbe98522964`
- origin/main SHA: `4ccb80276ed4e2b250876fd1e037ccbe98522964`
- Working tree status before task: clean; initial local status showed `main` ahead of `origin/main` by 3 local post-CONVERGE commits, then `origin/main` advanced to the same HEAD during the task
- Working tree status after task: POST-CONVERGE-08 docs and validator modified for commit

## Scope

This task covered product boot proof only:

- setup, launcher, client, server, and tools product surfaces
- build-output and wrapper/script product entrypoint discovery
- safe help/preflight command probes only
- no new features
- no semantic changes
- no platform/render/native implementation
- no public release proof

## Build Path Used

| Step | Command | Result | Notes |
| --- | --- | --- | --- |
| configure | `cmake --preset verify` | fail | local Visual Studio 17 2022 generator instance is missing |
| build | `cmake --build --preset verify` | not run | configure failed |
| test | `ctest --preset verify` | not run | configure failed |

The canonical verify lane remains the build path from POST-CONVERGE-07. No fallback build lane was introduced in this task.

## Product Commands Tested

| Product | Command | Result | Status | Notes |
| --- | --- | --- | --- | --- |
| setup | `python tools/setup/setup_cli.py --help` | fail | blocked | import-time `TypeError` from Python 3.10-style union annotation under local Python 3.8 |
| launcher | `python tools/launcher/launch.py --help` | pass | partial | AppShell help emitted for `product_id: launcher` |
| client | `python tools/mvp/runtime_entry.py client --help` | pass | partial | AppShell help emitted for `product_id: client` |
| client | `python dist/bin/dominium_client --help` | pass | partial | tracked wrapper emits AppShell help for `product_id: client` |
| server | `python tools/mvp/runtime_entry.py server --help` | pass | partial | AppShell help emitted for `product_id: server` |
| server | `python dist/bin/dominium_server --help` | pass | partial | tracked wrapper emits AppShell help for `product_id: server` |
| server | `python apps/server/server_main.py --help` | pass with wrong surface | partial | exits 0 but enters the default AppShell TUI because script args are not forwarded |
| tools | `python tools/appshell/product_stub_cli.py --product-id tool.attach_console_stub --help` | pass | partial | AppShell help emitted for the attach-console tool stub |
| tools | `python dist/bin/dom --help` | fail | blocked | wrapper target `dist/bin/tool_attach_console_stub` is missing |

Native commands `setup --help`, `launcher --help`, `client --help`, `server --help`, and `tools --help` were not run because no build output binary exists locally.

## Product Boot Evidence

Observed output summaries:

- launcher help: AppShell help header with `product_id: launcher`, command list including `compat-status`, `console`, `descriptor`, `diag`, `launcher start`, `launcher status`, and `launcher stop`.
- client help: AppShell help header with `product_id: client`, command list including `compat-status`, `packs`, `profiles`, `diag`, and client/geo/logic/session namespaces.
- server help: AppShell help header with `product_id: server`, command list including `compat-status`, `packs`, `profiles`, `diag`, and server/session namespaces.
- tools stub help: AppShell help header with `product_id: tool.attach_console_stub`, command list including tool namespaces under `dom`.
- setup failure: `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`.
- `dist/bin/dom` failure: `dom wrapper missing target: .../dist/bin/tool_attach_console_stub`.

These results prove script/wrapper help surfaces for launcher, client, server, and the attach-console tool stub. They do not prove native product binaries or full runtime/session behavior.

## Blockers

- `cmake --preset verify` cannot configure locally because Visual Studio 17 2022 is not installed or discoverable.
- No built `setup`, `launcher`, `client`, `server`, or `tools` binary exists under the verify output paths.
- Setup Python bridge fails before help under local Python 3.8.
- `apps/server/server_main.py` script invocation does not forward CLI args and therefore does not prove server `--help`.
- `dist/bin/dom` references missing `dist/bin/tool_attach_console_stub`.
- No client smoke, server headless smoke, status, save, load, resume, or shutdown command was build-proven.

## Files Added/Changed

- Added `docs/repo/audits/POST_CONVERGE_08_PRODUCT_BOOT_MATRIX_PROOF.md`.
- Added `docs/release/PRODUCT_BOOT_PROOF.md`.
- Added `tools/validators/check_product_boot_matrix.py`.
- Updated `docs/release/PRODUCT_MODE_MATRIX.md`.
- Updated `docs/release/COMPONENT_MATRIX.md`.
- Updated `docs/runtime/CANONICAL_LOCAL_PLAYTEST.md`.
- Updated `docs/release/LOCAL_RUNTIME_PROOF.md`.
- Updated `docs/repo/POST_CONVERGE_NEXT_STEPS.md`.
- Updated `docs/repo/audits/POST_CONVERGE_07_LOCAL_RUNTIME_PROOF.md`.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `cmake --preset verify` | fail | `Visual Studio 17 2022` generator instance is missing locally |
| `cmake --build --preset verify` | not run | configure failed |
| `ctest --preset verify` | not run | configure failed |
| `python tools/setup/setup_cli.py --help` | fail | Python 3.8 import-time annotation failure |
| `python tools/launcher/launch.py --help` | pass | AppShell launcher help |
| `python tools/mvp/runtime_entry.py client --help` | pass | AppShell client help |
| `python tools/mvp/runtime_entry.py server --help` | pass | AppShell server help |
| `python apps/server/server_main.py --help` | partial | exits 0 but enters TUI, not help |
| `python tools/appshell/product_stub_cli.py --product-id tool.attach_console_stub --help` | pass | AppShell tool-stub help |
| `python dist/bin/dominium_client --help` | pass | tracked client wrapper help |
| `python dist/bin/dominium_server --help` | pass | tracked server wrapper help |
| `python dist/bin/dom --help` | fail | missing wrapper target |
| `python -m py_compile tools/validators/check_product_boot_matrix.py` | pass | validator parses |
| `python tools/validators/check_product_boot_matrix.py --repo-root .` | pass | reports `proof_status: partial` |
| `python tools/validators/check_product_boot_matrix.py --repo-root . --json` | pass | JSON report emitted |
| `python tools/validators/check_product_boot_matrix.py --repo-root . --strict` | fail as expected | strict requires build-proven product binaries |
| `python tools/validators/check_local_playtest_path.py --repo-root .` | pass | reports `proof_status: blocked` |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | unexcepted violations: 0 |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | unexcepted violations: 0 |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | warnings: 0 |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | warnings: 0 |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | build boundary checks passed |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK |
| `python .aide/scripts/aide_lite.py doctor` | pass | existing warnings only |
| `python .aide/scripts/aide_lite.py validate` | pass | existing review-packet warnings only |
| `python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-08 product boot matrix proof"` | pass | task packet written |
| `git diff --check` | pending | final whitespace check |

## Next Recommended Task

Targeted product/AppShell/build remediation before POST-CONVERGE-09:

- install or expose the Visual Studio 17 2022 verify lane, or provide accepted CI proof
- run configure/build/CTest through `verify`
- fix or classify setup Python 3.8 compatibility for `tools/setup/setup_cli.py`
- repair or retire the tracked `dist/bin/dom` wrapper target
- fix or classify `apps/server/server_main.py` CLI argument forwarding
- rerun POST-CONVERGE-08 after those blockers are resolved or explicitly accepted
