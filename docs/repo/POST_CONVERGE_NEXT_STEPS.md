# Post-CONVERGE Next Steps

Status: PROVISIONAL

Phase: POST-CONVERGE

## Current Correction After POST-CONVERGE-10C

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

POST-CONVERGE-08 attempted product boot matrix proof at the user's request and is partial:

- launcher AppShell help boots through `python tools/launcher/launch.py --help`
- client AppShell help boots through `python dist/bin/dominium_client --help`
- server AppShell help boots through `python dist/bin/dominium_server --help`
- the attach-console tool stub help boots through `python tools/appshell/product_stub_cli.py --product-id tool.attach_console_stub --help`
- setup remains blocked before help through the Python bridge on local Python 3.8
- `dist/bin/dom` remains blocked because `dist/bin/tool_attach_console_stub` is missing
- no native product binary boot was proven

POST-CONVERGE-09 attempted portable projection/package smoke proof and is partial:

- distribution contracts and portable/package docs are coherent
- package/projection tool help surfaces exist
- a temporary one-file `.dompkg` smoke package was packed and verified under `%TEMP%`, then removed
- no real portable projection root was generated
- required portable manifests and native product binaries remain blocked by the missing build output

POST-CONVERGE-10 added the tuple-driven build contract and machine probe. POST-CONVERGE-10B reprobed after Visual Studio installation:

- build contract files now exist under `contracts/build/`
- local probe output is generated under ignored `.dominium.local/`
- Visual Studio Enterprise 2022 and MSVC v143 are now detected
- generated local preset data now includes `verify.winnt10.x64.msvc143.mt.debug`
- `CMakeUserPresets.json` can be generated as ignored local data so CMake can consume the tuple preset; POST-CONVERGE-10B removed it before final strict layout validation
- CMake selects Windows SDK `10.0.26100.0` and MSVC tools `14.44.35207`
- configure now fails during CMake generation because tests still reference stale pre-convergence root paths:
  - `client/presentation/frame_graph_builder.cpp`
  - `server/authority/dom_server_authority.cpp`
- no native product binaries were produced

POST-CONVERGE-10C fixed the stale client/server CMake and test paths:

- `verify.winnt10.x64.msvc143.mt.debug` configure now passes
- `cmake --preset verify` now passes
- tuple and canonical builds produce native product binaries before failing
- build remains red because `tool_ui_bind --check` reports stale generated outputs in `libs/appcore/ui_bind/`
- `ctest --preset verify` was not run because build failed

Current priority order:

1. remediate stale UI bind generated outputs under `libs/appcore/ui_bind/`
2. rerun the generated `verify.winnt10.x64.msvc143.mt.debug` tuple build and CTest
3. remediate or explicitly accept remaining RepoX FAST drift findings
4. fix or classify setup Python bridge compatibility and the missing `dist/bin/dom` target
5. fix or classify direct `apps/server/server_main.py` CLI argument forwarding
6. add or prove a real portable projection assembly path that emits required manifests and roots
7. rerun product boot and portable projection proof only after build, product command, and projection blockers are accepted or resolved

Planning references:

- `docs/repo/audits/POST_CONVERGE_00_HEALTH.md`
- `docs/repo/audits/POST_CONVERGE_EXCEPTION_TRIAGE.md`
- `docs/repo/audits/POST_CONVERGE_06_BUILD_FAST_REMEDIATION.md`
- `docs/repo/audits/POST_CONVERGE_07_LOCAL_RUNTIME_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_08_PRODUCT_BOOT_MATRIX_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_09_PORTABLE_PROJECTION_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_10_BUILD_BINARY_PROOF.md`
- `docs/repo/EXCEPTION_RETIREMENT_QUEUE.md`
- `docs/repo/BUILD_ENVIRONMENT_REMEDIATION.md`
- `docs/repo/BUILD_VERIFICATION_PATHS.md`
- `docs/repo/FAST_GATE_REMEDIATION.md`
- `docs/repo/AIDE_PACK_REMEDIATION.md`
- `docs/runtime/CANONICAL_LOCAL_PLAYTEST.md`
- `docs/release/LOCAL_RUNTIME_PROOF.md`
- `docs/release/PRODUCT_BOOT_PROOF.md`
- `docs/distribution/PORTABLE_PROJECTION_SMOKE_PROOF.md`
- `docs/release/PACKAGE_SMOKE_PROOF.md`
- `docs/release/NATIVE_BINARY_PROOF.md`
- `docs/build/BUILD_CONTRACT.md`

## What Can Proceed

The repository is ready for scoped work in these areas:

- targeted UI bind generated-output remediation for the existing `verify` preset
- targeted build tuple/probe/preset remediation using `contracts/build/`
- targeted RepoX FAST drift remediation
- targeted command-surface remediation for script-level CLI argument forwarding, after build proof is available
- targeted setup Python compatibility remediation if the Python setup bridge remains a product proof path
- targeted `dist/bin/dom` wrapper remediation or retirement if that wrapper remains a shipped tool surface
- targeted portable projection assembly/manifest generation remediation
- documentation updates that reflect the current validation state
- narrowly scoped AIDE/tooling compatibility fixes

Platform, render, native shell, Universal Reality enforcement, worldgen, domain realism, and public release/package expansion should wait until build proof, product boot proof, and portable projection status are resolved or explicitly accepted.

## What Must Not Happen

- no new root-level domain folders
- no new root-level product folders
- no GUI toolkit owning product semantics
- no renderer owning simulation truth
- no distribution/runtime/install/media roots treated as source roots
- no support claims without component matrix status
- no new machine-readable authority under transitional roots without contract review
- no CONTRACT-00 Universal Reality enforcement until build, product boot, and portable projection blockers are accepted or resolved

## Suggested Sequence

1. Fix stale UI bind generated outputs under `libs/appcore/ui_bind/`.
2. Rerun `tools/build/probe_toolchains.py` and generate ignored local preset data.
3. Run build and CTest through `verify.winnt10.x64.msvc143.mt.debug` or the canonical `verify` lane.
4. Address remaining RepoX FAST drift findings in a targeted remediation task.
5. Remediate or explicitly classify setup Python bridge compatibility and the missing `dist/bin/dom` target.
6. Add or prove a portable projection assembly path that emits `install.manifest.json`, `semantic_contract_registry.json`, `release.manifest.json`, product binaries, and required portable roots.
7. Rerun strict layout validators, docs/build/UI/ABI checks, FAST, and AIDE pack.
8. Run POST-CONVERGE-11 product boot proof with native binaries after build output exists.
9. Rerun portable projection smoke proof after projection generation is available.
10. Start CONTRACT-00 only after these blockers are resolved or explicitly accepted as warning-only.

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
