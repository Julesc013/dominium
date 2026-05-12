# Post-CONVERGE Next Steps

Status: PROVISIONAL

Phase: POST-CONVERGE

## Current Correction After POST-CONVERGE-07

POST-CONVERGE-00 confirmed that exception retirement and build/runtime proof must precede platform, render, native shell, worldgen, and broad domain expansion.

POST-CONVERGE-06 completed targeted build, FAST, and AIDE diagnostics:

- the AIDE pack Python compatibility blocker is fixed locally
- the original FAST `repox_runner` structural crash is reduced to broader RepoX drift findings
- local `cmake --preset verify` remains blocked by the missing Visual Studio 17 2022 generator
- build and CTest proof remain pending until a valid verify toolchain or accepted CI lane is available

POST-CONVERGE-07 attempted canonical local runtime proof and is blocked:

- no `client`, `server`, `setup`, or `launcher` binary exists locally
- no full local playtest/session/status/save/load/resume sequence was run
- `python apps/server/server_main.py --help` exits 0 but enters AppShell TUI because the script invocation does not forward CLI args
- `tools/validators/check_local_playtest_path.py` records the current blocked state

Current priority order:

1. provide a valid Visual Studio 17 2022 verify lane or accepted CI proof
2. run configure/build/CTest through the canonical verify lane
3. remediate or explicitly accept remaining RepoX FAST drift findings
4. rerun POST-CONVERGE-07 only after build and FAST status is accepted

Planning references:

- `docs/repo/audits/POST_CONVERGE_00_HEALTH.md`
- `docs/repo/audits/POST_CONVERGE_EXCEPTION_TRIAGE.md`
- `docs/repo/audits/POST_CONVERGE_06_BUILD_FAST_REMEDIATION.md`
- `docs/repo/audits/POST_CONVERGE_07_LOCAL_RUNTIME_PROOF.md`
- `docs/repo/EXCEPTION_RETIREMENT_QUEUE.md`
- `docs/repo/BUILD_ENVIRONMENT_REMEDIATION.md`
- `docs/repo/BUILD_VERIFICATION_PATHS.md`
- `docs/repo/FAST_GATE_REMEDIATION.md`
- `docs/repo/AIDE_PACK_REMEDIATION.md`
- `docs/runtime/CANONICAL_LOCAL_PLAYTEST.md`
- `docs/release/LOCAL_RUNTIME_PROOF.md`

## What Can Proceed

The repository is ready for scoped work in these areas:

- toolchain installation or CI proof for the existing `verify` preset
- targeted RepoX FAST drift remediation
- targeted command-surface remediation for script-level CLI argument forwarding, after build proof is available
- documentation updates that reflect the current validation state
- narrowly scoped AIDE/tooling compatibility fixes

Platform, render, native shell, AppShell enforcement, worldgen, domain realism, and release/package expansion should wait until build proof and FAST status are resolved or explicitly accepted.

## What Must Not Happen

- no new root-level domain folders
- no new root-level product folders
- no GUI toolkit owning product semantics
- no renderer owning simulation truth
- no distribution/runtime/install/media roots treated as source roots
- no support claims without component matrix status
- no new machine-readable authority under transitional roots without contract review
- no runtime/playtest proof until build and FAST status are accepted

## Suggested Sequence

1. Install or expose Visual Studio 17 2022 build tools, or capture accepted CI proof for `cmake --preset verify`.
2. Run configure, build, and CTest through the canonical verify lane.
3. Address remaining RepoX FAST drift findings in a targeted remediation task.
4. Rerun strict layout validators, docs/build/UI/ABI checks, FAST, and AIDE pack.
5. Rerun POST-CONVERGE-07 canonical local runtime/playtest proof if the gates are pass or explicitly accepted warn.
6. Start POST-CONVERGE-08 product boot matrix proof only after POST-CONVERGE-07 records full or accepted partial product command proof.

## Domain Work Rule

Future domain work must use the split model:

- schemas, registries, capabilities, and protocols under `contracts/`
- implementation under `game/domains/`
- authored data and packs under `content/`
- human explanation under `docs/domains/`
- fixtures, determinism, regression, and golden tests under `tests/`

## Matrix Rule

Future platform/render/native/toolchain/package work must update `contracts/release/component_matrix.contract.toml` and relevant `docs/release/*_MATRIX.md` docs when status changes.

Planned, stub, and research rows are not supported implementations.
