Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Product Boot Proof

## Status

- Phase: POST-CONVERGE-08
- Status: partial
- Date: 2026-05-12

## Purpose

This document records product boot evidence. It is not an implementation plan, support promise, release claim, or product-mode semantic change.

## Build Path

| Step | Command | Result | Notes |
| --- | --- | --- | --- |
| configure | `cmake --preset verify` | blocked | local Visual Studio 17 2022 generator instance is missing |
| build | `cmake --build --preset verify` | not run | configure failed |
| test | `ctest --preset verify` | not run | configure failed |

Expected verify binary output remains `out/build/vs2026/verify/bin/`. No local built `setup`, `launcher`, `client`, `server`, or `tools` binary was available during this proof.

## Product Boot Matrix

| Product | Source Path | Binary/Entrypoint | Mode | Command | Result | Status | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| setup | `apps/setup/` | `setup` | cli | `setup --help` | not run | blocked | no built binary | CMake target `setup_cli` outputs `setup` |
| setup | `tools/setup/setup_cli.py` | Python setup AppShell bridge | cli | `python tools/setup/setup_cli.py --help` | fail | blocked | `TypeError: unsupported operand type(s) for \|: 'type' and 'NoneType'` | local Python 3.8 cannot evaluate the Python 3.10 union annotation in this script |
| launcher | `apps/launcher/` | `launcher` | cli | `launcher --help` | not run | blocked | no built binary | CMake target `launcher_cli` outputs `launcher` |
| launcher | `tools/launcher/launch.py` | Python launcher AppShell bridge | cli | `python tools/launcher/launch.py --help` | pass | partial | AppShell help for `product_id: launcher` | script help boot only; native product binary not proven |
| client | `apps/client/` | `client` | cli | `client --help` | not run | blocked | no built binary | CMake target `dominium_client` outputs `client` |
| client | `dist/bin/dominium_client` | tracked Python wrapper | cli | `python dist/bin/dominium_client --help` | pass | partial | AppShell help for `product_id: client` | wrapper proof only; native product binary not proven |
| client | `tools/mvp/runtime_entry.py` | Python MVP runtime entry | cli | `python tools/mvp/runtime_entry.py client --help` | pass | partial | AppShell help for `product_id: client` | script proof only |
| server | `apps/server/` | `server` | headless/cli | `server --help` | not run | blocked | no built binary | CMake target `dominium_server` outputs `server` |
| server | `dist/bin/dominium_server` | tracked Python wrapper | cli | `python dist/bin/dominium_server --help` | pass | partial | AppShell help for `product_id: server` | wrapper proof only; native product binary not proven |
| server | `tools/mvp/runtime_entry.py` | Python MVP runtime entry | cli | `python tools/mvp/runtime_entry.py server --help` | pass | partial | AppShell help for `product_id: server` | script proof only |
| server | `apps/server/server_main.py` | Python server AppShell bridge | default | `python apps/server/server_main.py --help` | pass with wrong surface | partial | exits 0 but enters AppShell TUI | script invocation still does not forward `sys.argv[1:]` |
| tools | `tools/` | `tools` | cli | `tools --help` | not run | blocked | no built binary | CMake target `dominium-tools` outputs `tools` |
| tools | `tools/appshell/product_stub_cli.py` | Python tool attach-console stub | cli | `python tools/appshell/product_stub_cli.py --product-id tool.attach_console_stub --help` | pass | partial | AppShell help for `product_id: tool.attach_console_stub` | tool stub proof only; shipped tools host not proven |
| tools | `dist/bin/dom` | tracked Python wrapper | cli | `python dist/bin/dom --help` | fail | blocked | missing `dist/bin/tool_attach_console_stub` target | wrapper target is absent |

## Product Results

### setup

The C setup product target is declared, but no built `setup` binary exists locally. The Python setup bridge fails before help under local Python 3.8 because the file contains a Python 3.10-style union annotation evaluated at import time. Setup boot proof is blocked.

### launcher

The C launcher product target is declared, but no built `launcher` binary exists locally. The Python launcher AppShell bridge starts and emits deterministic AppShell help for `product_id: launcher`, so launcher has partial script-level help proof only.

### client

The C client product target is declared, but no built `client` binary exists locally. Both the tracked `dist/bin/dominium_client` wrapper and `tools/mvp/runtime_entry.py client --help` emit deterministic AppShell help for `product_id: client`. Client has partial wrapper/script help proof only.

### server

The C server product target is declared, but no built `server` binary exists locally. The tracked `dist/bin/dominium_server` wrapper and `tools/mvp/runtime_entry.py server --help` emit deterministic AppShell help for `product_id: server`. Direct `apps/server/server_main.py --help` still enters the default TUI path because script invocation does not forward CLI args. Server has partial wrapper/script help proof only.

### tools

The C tools host target is declared as `dominium-tools` with output name `tools`, but no built `tools` binary exists locally. The AppShell attach-console tool stub emits help for `product_id: tool.attach_console_stub`. The tracked `dist/bin/dom` wrapper fails because its target `dist/bin/tool_attach_console_stub` is absent. Tools have partial stub help proof only.

## Unsupported Or Blocked Modes

- Native product binaries are not proven for any product.
- Setup CLI help is blocked in the Python bridge on the local Python version.
- Full client rendered/null/software smoke is not proven.
- Full server headless smoke/status/session proof is not proven.
- The shipped tools host binary is not proven.
- The `dist/bin/dom` wrapper is broken because its target is missing.
- No pack/profile/session/bootstrap state was created or mutated.

## Relationship To Component Matrix

Product boot proof does not mean public release support. Planned, stub, provisional, and research statuses remain non-support unless command proof and the component matrix both support promotion. POST-CONVERGE-08 does not change the machine-readable component matrix contract.

## Readiness For Portable Projection Smoke

POST-CONVERGE-09 should not proceed yet. The next work should provide a valid build proof or accepted CI lane, fix or classify the setup Python entrypoint compatibility failure, repair or retire the missing `dist/bin/dom` wrapper target, and rerun product boot proof.
