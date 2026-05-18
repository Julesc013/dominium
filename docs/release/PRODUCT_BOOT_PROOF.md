Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Product Boot Proof

## Status

- Phase: RESTRUCTURE-REPAIR-00 command-surface proof
- Status: pass
- Date: 2026-05-18

## Purpose

This document records product boot evidence. It is not an implementation plan, support promise, release claim, or product-mode semantic change.

## Build Path

| Step | Command | Result | Notes |
| --- | --- | --- | --- |
| configure | `cmake --preset verify` | pass | existing SDL2/PkgConfig warnings only |
| build | `cmake --build --preset verify --target ALL_BUILD` | pass | build-only proof; broad verify target remains partitioning debt |
| test | `ctest --preset verify -L smoke --output-on-failure --timeout 300` | pass | smoke CTest 57/57 |

Expected verify binary output remains `out/build/vs2026/verify/bin/`. Local built `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, and `tools.exe` were available and passed strict product boot matrix smoke during RESTRUCTURE-REPAIR-00.

## Historical Product Boot Matrix

The matrix below records the earlier POST-CONVERGE proof state. The latest RESTRUCTURE-REPAIR-00 status is the command-surface pass recorded above and in the closeout sections near the end of this file.

| Product | Source Path | Binary/Entrypoint | Mode | Command | Result | Status | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| setup | `apps/setup/` | `setup` | cli | `setup --help` | not run | blocked | no built binary | CMake target `setup_cli` outputs `setup` |
| setup | `tools/setup/setup_cli.py` | Python setup AppShell bridge | cli | `python tools/setup/setup_cli.py --help` | fail | blocked | `TypeError: unsupported operand type(s) for \|: 'type' and 'NoneType'` | local Python 3.8 cannot evaluate the Python 3.10 union annotation in this script |
| launcher | `apps/launcher/` | `launcher` | cli | `launcher --help` | not run | blocked | no built binary | CMake target `launcher_cli` outputs `launcher` |
| launcher | `tools/launcher/launch.py` | Python launcher AppShell bridge | cli | `python tools/launcher/launch.py --help` | pass | partial | AppShell help for `product_id: launcher` | script help boot only; native product binary not proven |
| client | `apps/client/` | `client` | cli | `client --help` | not run | blocked | no built binary | CMake target `dominium_client` outputs `client` |
| client | `archive/generated/dist/bin/dominium_client` | tracked Python wrapper | cli | `python archive/generated/dist/bin/dominium_client --help` | pass | partial | AppShell help for `product_id: client` | wrapper proof only; native product binary not proven |
| client | `tools/mvp/runtime_entry.py` | Python MVP runtime entry | cli | `python tools/mvp/runtime_entry.py client --help` | pass | partial | AppShell help for `product_id: client` | script proof only |
| server | `apps/server/` | `server` | headless/cli | `server --help` | not run | blocked | no built binary | CMake target `dominium_server` outputs `server` |
| server | `archive/generated/dist/bin/dominium_server` | tracked Python wrapper | cli | `python archive/generated/dist/bin/dominium_server --help` | pass | partial | AppShell help for `product_id: server` | wrapper proof only; native product binary not proven |
| server | `tools/mvp/runtime_entry.py` | Python MVP runtime entry | cli | `python tools/mvp/runtime_entry.py server --help` | pass | partial | AppShell help for `product_id: server` | script proof only |
| server | `apps/server/server_main.py` | Python server AppShell bridge | default | `python apps/server/server_main.py --help` | pass with wrong surface | partial | exits 0 but enters AppShell TUI | script invocation still does not forward `sys.argv[1:]` |
| tools | `tools/` | `tools` | cli | `tools --help` | not run | blocked | no built binary | CMake target `dominium-tools` outputs `tools` |
| tools | `tools/validators/shell/product_stub_cli.py` | Python tool attach-console stub | cli | `python tools/validators/shell/product_stub_cli.py --product-id tool.attach_console_stub --help` | pass | partial | AppShell help for `product_id: tool.attach_console_stub` | tool stub proof only; shipped tools host not proven |
| tools | `archive/generated/dist/bin/dom` | tracked Python wrapper | cli | `python archive/generated/dist/bin/dom --help` | fail | blocked | missing `archive/generated/dist/bin/tool_attach_console_stub` target | wrapper target is absent |

## Product Results

### setup

The C setup product target is declared, but no built `setup` binary exists locally. The Python setup bridge fails before help under local Python 3.8 because the file contains a Python 3.10-style union annotation evaluated at import time. Setup boot proof is blocked.

### launcher

The C launcher product target is declared, but no built `launcher` binary exists locally. The Python launcher AppShell bridge starts and emits deterministic AppShell help for `product_id: launcher`, so launcher has partial script-level help proof only.

### client

The C client product target is declared, but no built `client` binary exists locally. Both the tracked `archive/generated/dist/bin/dominium_client` wrapper and `tools/mvp/runtime_entry.py client --help` emit deterministic AppShell help for `product_id: client`. Client has partial wrapper/script help proof only.

### server

The C server product target is declared, but no built `server` binary exists locally. The tracked `archive/generated/dist/bin/dominium_server` wrapper and `tools/mvp/runtime_entry.py server --help` emit deterministic AppShell help for `product_id: server`. Direct `apps/server/server_main.py --help` still enters the default TUI path because script invocation does not forward CLI args. Server has partial wrapper/script help proof only.

### tools

The C tools host target is declared as `dominium-tools` with output name `tools`, but no built `tools` binary exists locally. The AppShell attach-console tool stub emits help for `product_id: tool.attach_console_stub`. The tracked `archive/generated/dist/bin/dom` wrapper fails because its target `archive/generated/dist/bin/tool_attach_console_stub` is absent. Tools have partial stub help proof only.

## Unsupported Or Blocked Modes

- Native product binaries are not proven for any product.
- Setup CLI help is blocked in the Python bridge on the local Python version.
- Full client rendered/null/software smoke is not proven.
- Full server headless smoke/status/session proof is not proven.
- The shipped tools host binary is not proven.
- The `archive/generated/dist/bin/dom` wrapper is broken because its target is missing.
- No pack/profile/session/bootstrap state was created or mutated.

## Relationship To Component Matrix

Product boot proof does not mean public release support. Planned, stub, provisional, and research statuses remain non-support unless command proof and the component matrix both support promotion. POST-CONVERGE-08 does not change the machine-readable component matrix contract.

## Readiness For Portable Projection Smoke

POST-CONVERGE-09 should not proceed yet. The next work should provide a valid build proof or accepted CI lane, fix or classify the setup Python entrypoint compatibility failure, repair or retire the missing `archive/generated/dist/bin/dom` wrapper target, and rerun product boot proof.

## POST-CONVERGE-11 Update - Native Product Boot Gate

POST-CONVERGE-11 did not run product binaries. The task stopped at the required RepoX readiness gate because focused `inv_repox_rules` still fails with 20 failures and 5 warnings, and no accepted-warning ledger authorizes product boot proof.

Current product boot status remains blocked:

| Product | Native Command Surface | POST-CONVERGE-11 Result | Blocker |
| --- | --- | --- | --- |
| setup | `setup.exe` | not run | RepoX semantic blocker |
| launcher | `launcher.exe` | not run | RepoX semantic blocker |
| client | `client.exe` | not run | RepoX semantic blocker |
| server | `server.exe` | not run | RepoX semantic blocker |
| tools | `tools.exe` | not run | RepoX semantic blocker |

The next required task is `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`. Product boot proof should be retried only after focused RepoX passes or a reviewed accepted-warning ledger explicitly authorizes boot despite remaining findings.

## POST-CONVERGE-12 Update - Portable Projection Gate

POST-CONVERGE-12 did not proceed to projection generation because this product boot proof remains blocked. No portable projection root was generated, no native binaries were inspected or copied, and no release readiness was claimed.

The next required task remains `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`. After that gate is resolved or explicitly accepted, POST-CONVERGE-11 must be rerun before POST-CONVERGE-12 can provide a real portable projection proof.

## Closeout Remediation Update - Native Command Smoke

Focused RepoX now passes, so the native command smoke blocker recorded above has been superseded by local closeout evidence.

Local binary root:

```text
out/build/vs2026/verify/bin/
```

Commands run:

| Product | Commands | Result |
| --- | --- | --- |
| setup | `--help`, `--version`, `--status`, `--smoke` | pass |
| launcher | `--help`, `--version`, `--status`, `--smoke` | pass |
| client | `--help`, `--version`, `--status`, `--smoke` | pass |
| server | `--help`, `--version`, `--status`, `--smoke` | pass |
| tools | `--help`, `--version`, `--status`, `--smoke` | pass |

This is command-surface boot smoke only. It does not create a package, release, installer, portable projection, or gameplay proof.

## Portable Projection Input Update

The command-surface proof above was used as input for a local portable projection proof. The generated ignored projection root includes the five native product binaries and validates with `proof_status: proven`.

## RELEASE-00 Consumer Update

The portable projection that includes the native command-surface binaries was staged into Internal Pilot Release 0. The release validator confirms the staged `projection/bin/` contains:

- `setup.exe`
- `launcher.exe`
- `client.exe`
- `server.exe`
- `tools.exe`

RELEASE-00 does not add gameplay proof. It preserves the command/help/status/smoke level established by the product boot closeout evidence.

## BASELINE-00 Update

BASELINE-00 freezes the RELEASE-00 command-surface product boot posture as part of the structural regression baseline.

- Baseline HEAD: `0b631fc5f09f3d927a54e8312976b926d111a72e`.
- Product command-surface baseline: `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, and `tools.exe` present in the portable projection and internal pilot staging roots.
- Proof level remains command/help/status/smoke; no gameplay, renderer, native GUI, or operating-environment MVP proof is added by BASELINE-00.
- Future build-sensitive MOVE-FAMILY waves must preserve this proof level or rerun product boot proof before claiming success.

<!-- POST-RESTRUCTURE-00-BLOCKED -->

## POST-RESTRUCTURE-00 Blocked Proof Note

POST-RESTRUCTURE-00 did not run the full proof chain because MOVE-BULK-08 closure says full proof is not ready.

- Remaining former bad-root files: 1764.
- Deferred batches: B-G.
- Blocked batch: H.
- Ready for DOE-00: no.
- Next recommended task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.

<!-- RESTRUCTURE-REPAIR-00 -->

## RESTRUCTURE-REPAIR-00 Product Boot Update

`python tools/validators/check_product_boot_matrix.py --repo-root . --json --strict --run-smoke --timeout 30` passed with `proof_status: proven` and no blockers.

This remains command-surface boot proof only. It does not authorize gameplay, public release, installer, package publication, or feature work.
