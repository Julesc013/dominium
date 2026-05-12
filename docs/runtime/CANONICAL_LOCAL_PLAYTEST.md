# Canonical Local Playtest

## Status

- Phase: POST-CONVERGE-07
- Status: blocked
- Date: 2026-05-12

## Purpose

This document defines the canonical local developer/agent runtime path for Dominium. It records the command sequence that must become repeatable before product boot matrix proof, package proof, Universal Reality enforcement, or domain pilots.

## Preconditions

- Build requirement: `cmake --preset verify` must configure successfully.
- Toolchain requirement: the visible canonical verify lane requires `Visual Studio 17 2022`.
- Python requirement: local `Python 3.8.1` is sufficient for AIDE and the audit helpers after POST-CONVERGE-06.
- Pack/profile/session inputs: no canonical local playtest pack/profile/session input set is build-proven yet.
- Environment requirement: no local compiler or fallback build tool was discoverable during POST-CONVERGE-06.

## Canonical Command Sequence

| Status | Purpose | Command | Expected Result | Output / Log Path |
| --- | --- | --- | --- | --- |
| blocked | configure canonical verify lane | `cmake --preset verify` | configure succeeds | `out/build/vs2026/verify/` |
| blocked | build product/runtime targets | `cmake --build --preset verify` | `client`, `server`, `setup`, `launcher`, and tool targets produced | `out/build/vs2026/verify/bin/` |
| blocked | run CTest verify lane | `ctest --preset verify` | tests pass | CTest output under verify build tree |
| blocked | setup CLI preflight | `setup --help` | help exits 0 | built binary required |
| blocked | launcher CLI preflight | `launcher --help` | help exits 0 | built binary required |
| blocked | server CLI preflight | `server --help` | help exits 0 | built binary required |
| blocked | client CLI preflight | `client --help` | help exits 0 | built binary required |
| partial | Python server AppShell preflight | `python apps/server/server_main.py --help` | exits 0, but currently enters AppShell TUI because script invocation does not forward CLI args | console output |
| blocked | local session create/select | not supported as a proven product command | session spec materializes | not available |
| blocked | local authority/server start | not supported as a build-proven product command | authoritative loopback server starts | not available |
| blocked | client attach/null/software path | not supported as a build-proven product command | client attaches locally | not available |
| blocked | status | not supported as a build-proven product command | status payload returned | not available |
| blocked | save | not supported as a build-proven product command | save or snapshot artifact emitted | not available |
| blocked | load/resume | not supported as a build-proven product command | saved state resumes | not available |
| blocked | shutdown | not supported as a build-proven product command | clean shutdown | not available |

## Runtime Proof Scope

| Step | Status | Notes |
| --- | --- | --- |
| build | blocked | local Visual Studio 17 2022 generator instance is missing |
| setup preflight | blocked | `setup` binary is not produced locally |
| launcher preflight | blocked | `launcher` binary is not produced locally |
| session create/select | blocked | no build-proven product command exists |
| local authority/server | blocked | server executable is not produced locally |
| client/null/software | blocked | client executable is not produced locally |
| status | blocked | product command not build-proven |
| save | blocked | product command not build-proven |
| load/resume | blocked | product command not build-proven |
| shutdown | blocked | no local runtime sequence was started |
| proof bundle/log | blocked | no full runtime proof artifact was produced |

## Current Blockers

- `cmake --preset verify` fails locally because no Visual Studio 17 2022 instance is installed or discoverable.
- `cmake --build --preset verify` and `ctest --preset verify` cannot run until configure succeeds.
- No built product binaries are available for `client`, `server`, `setup`, or `launcher`.
- FAST still fails with RepoX `DRIFT`; POST-CONVERGE-06 fixed the prior structural crash but not the broad drift backlog.
- `apps/server/server_main.py` can be invoked, but script execution does not forward `sys.argv[1:]`, so `--help` and `--descriptor` are not honored as actual script-level commands.
- Full local session/status/save/load/resume proof is therefore not supported yet.

## Non-Goals

- No new gameplay systems.
- No renderer or native GUI proof.
- No network multiplayer proof beyond future local/loopback authority proof.
- No public release proof.
