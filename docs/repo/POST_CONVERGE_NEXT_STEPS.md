Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Post-CONVERGE Next Steps

Status: PROVISIONAL

Phase: POST-CONVERGE

## Current Correction After POST-CONVERGE-10E

POST-CONVERGE-00 confirmed that exception retirement and build/runtime proof must precede platform, render, native shell, worldgen, and broad domain expansion.

POST-CONVERGE-06 completed targeted build, FAST, and AIDE diagnostics:

- the AIDE pack Python compatibility blocker is fixed locally
- the original FAST `repox_runner` structural crash is reduced to broader RepoX drift findings
- local `cmake --preset verify` was blocked at that time by the missing Visual Studio 17 2022 generator
- build and CTest proof were pending until a valid verify toolchain or accepted CI lane was available

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

POST-CONVERGE-10D fixed the UI bind generated-output freshness gate:

- `libs/appcore/ui_bind/**` is now pinned to LF line endings for byte-identical generated-source checks
- `tool_ui_bind --check` passes
- `verify.winnt10.x64.msvc143.mt.debug` configure and build pass
- `cmake --preset verify` and `cmake --build --preset verify` pass
- native product binaries are present under `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/`
- canonical verify binaries for setup/launcher/client/server are present under `out/build/vs2026/verify/bin/`
- CTest remains blocked by tools/auditx failures and timeout

POST-CONVERGE-10E fixed the targeted AuditX/CTest path blockers:

- `tools_refusal_explain` and `tools_coverage_inspect` now pass after direct tool subprocesses resolve the repo root before importing `compat`
- AuditX no longer assumes retired root `schema` as source authority; generated bundle projections now source schemas from `contracts/schemas/`
- generated wrapper smoke includes current converged `apps/` and `game/` runtime roots
- missing generated release manifests now surface as deterministic refused verification results instead of uncaught AuditX crashes
- focused AuditX CTest cases pass
- `verify.winnt10.x64.msvc143.mt.debug` configure/build still pass
- `cmake --preset verify` and `cmake --build --preset verify` still pass
- full CTest remains blocked by `invariant_units_present`, `inv_repox_rules`, and local wall-time

POST-CONVERGE-10F remediated and classified the remaining unit/RepoX blockers:

- `invariant_units_present` now passes in the tuple verify CTest lane
- `unit.mass_energy.stub` is declared in `data/registries/unit_registry.json`
- the unit validator no longer treats path fragments such as `materials/unit.schema` as unit identifiers
- `inv_repox_rules` still fails with broad RepoX/canonical-evidence drift
- the RepoX CTest wrapper now writes generated proof/profile output to ignored `.dominium.local/ctest/repox/`
- canonical `ctest --preset verify -N` currently discovers 0 tests, while the tuple verify build discovers 493 tests
- full CTest remains blocked by RepoX semantic failures and wall-time/discovery concerns

Current priority order:

1. remediate `inv_repox_rules` broad RepoX/canonical-evidence drift
2. repair or regenerate canonical `verify` CTest discovery so `ctest --preset verify` sees the expected tests
3. partition or classify full CTest wall-time after semantic RepoX failures are resolved
4. decide whether POST-CONVERGE-11 may proceed with build-green/CTest-warning status
5. fix or classify setup Python bridge compatibility and the missing `dist/bin/dom` target
6. fix or classify direct `apps/server/server_main.py` CLI argument forwarding
7. add or prove a real portable projection assembly path that emits required manifests and roots
8. rerun product boot and portable projection proof only after build, product command, and projection blockers are accepted or resolved

Planning references:

- `docs/repo/audits/POST_CONVERGE_00_HEALTH.md`
- `docs/repo/audits/POST_CONVERGE_EXCEPTION_TRIAGE.md`
- `docs/repo/audits/POST_CONVERGE_06_BUILD_FAST_REMEDIATION.md`
- `docs/repo/audits/POST_CONVERGE_07_LOCAL_RUNTIME_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_08_PRODUCT_BOOT_MATRIX_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_09_PORTABLE_PROJECTION_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_10_BUILD_BINARY_PROOF.md`
- `docs/repo/audits/POST_CONVERGE_10E_CTEST_AUDITX_REMEDIATION.md`
- `docs/repo/audits/POST_CONVERGE_10F_UNIT_REPOX_REMEDIATION.md`
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

- targeted CTest/auditx remediation for the existing `verify` preset
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

1. Address remaining RepoX FAST/CTest drift findings in a targeted remediation task.
2. Repair or regenerate canonical `verify` CTest discovery.
3. Rerun CTest through `verify.winnt10.x64.msvc143.mt.debug` and the canonical `verify` lane.
4. Run TEST-PERF-00 if semantic failures are clear but full CTest still exceeds local wall-time.
5. Remediate or explicitly classify setup Python bridge compatibility and the missing `dist/bin/dom` target.
6. Add or prove a portable projection assembly path that emits `install.manifest.json`, `semantic_contract_registry.json`, `release.manifest.json`, product binaries, and required portable roots.
7. Rerun strict layout validators, docs/build/UI/ABI checks, FAST, and AIDE pack.
8. Run POST-CONVERGE-11 product boot proof with native binaries after build output exists.
9. Rerun portable projection smoke proof after projection generation is available.
10. Start CONTRACT-00 only after these blockers are resolved or explicitly accepted as warning-only.

## POST-CONVERGE-10J Update - Authority Documentation Status

- Result: PARTIAL.
- Focused RepoX improved from 71 failures / 5 warnings to 60 failures / 5 warnings.
- `INV-DOC-STATUS-HEADER` reduced from 12 to 0 through narrow authority-sensitive metadata repairs.
- Seven architecture documents were added to the DERIVED canon index bucket to avoid introducing canon-index drift after their headers became parseable.
- POST-CONVERGE-11 remains blocked.
- Next recommended task: `POST-CONVERGE-10K - Contract Registry Acceptance Backlog Remediation`.

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

## POST-CONVERGE-10G Update

POST-CONVERGE-10G reduced focused tuple `inv_repox_rules` from 1844 failures and 5 warnings to 1769 failures and 5 warnings. Safe stale path/root assumptions were fixed for the RepoX top-level root check and retired AppShell root checks. RepoX cache keys now include the rule implementation file, so rule edits invalidate stale group output.

POST-CONVERGE-11 remains blocked. The next recommended task is `POST-CONVERGE-10H - Canonical Documentation Status and Canon Index Remediation`, focused on the `INV-DOC-STATUS-HEADER`, `INV-CANON-INDEX`, and `INV-CANON-NO-HIST-REF` families. Product boot, package proof, portable projection proof, and additional moves remain unauthorized.

## POST-CONVERGE-10H Update

POST-CONVERGE-10H reduced focused tuple `inv_repox_rules` from 1769 failures and 5 warnings to 153 failures and 5 warnings. It repaired 1533 clear DERIVED documentation status/header cases and added 84 missing canonical index entries for documents that already declared `Status: CANONICAL`.

POST-CONVERGE-11 remains blocked. The next recommended task is `POST-CONVERGE-10I - Historical Reference and Archive Citation Remediation`, focused on `INV-CANON-NO-HIST-REF`.

## POST-CONVERGE-10I Update - Historical Reference Remediation

- Result: PARTIAL.
- Focused RepoX improved from 153 failures / 5 warnings to 71 failures / 5 warnings.
- `INV-CANON-NO-HIST-REF` reduced from 81 to 0 by aligning RepoX enforcement to canonical-doc scope and preserving DERIVED quarantine/archive evidence references.
- POST-CONVERGE-11 remains blocked.
- Next recommended task: `POST-CONVERGE-10J - Authority-Sensitive Documentation Status Review`.

## POST-CONVERGE-10K Update - Contract Registry Acceptance

- Result: PARTIAL.
- Focused RepoX actual local state improved from 59 failures / 5 warnings to 51 failures / 5 warnings.
- The prior 10J-reported 60th failure was `INV-LOCKLIST-FROZEN`, which was absent at 10K start because `origin/main` equaled local HEAD.
- `INV-NEW-CONTRACT-REQUIRES-ENTRY` reduced from 9 to 0 by adding four accepted current architecture contract rows to `data/registries/semantic_contract_registry.json`.
- POST-CONVERGE-11 remains blocked because focused tuple `inv_repox_rules` still fails on distribution/product proof, retired-domain path policy, tool hash/audit staleness, ruleset mapping, and related families.
- Next recommended task: `POST-CONVERGE-10L - Distribution Descriptor and Product Proof Blocker Classification`.

## TEST-PERF-00 Update - Tiered Validation

- Result: PASS_WITH_WARNINGS.
- Canonical `verify` CTest discovery was repaired locally by running `cmake --preset verify`; `ctest --preset verify -N` now discovers 493 tests in this checkout.
- CTest label metadata was repaired so `ctest --preset verify -N -L smoke` discovers 57 smoke tests after reconfigure.
- Added `tests/validation_tiers.json`, `scripts/test_tier.py`, `scripts/test_impacted.py`, and `scripts/test_timing_report.py`.
- Full CTest remains the promotion gate, not the default post-change gate.
- Focused RepoX semantic failures remain from POST-CONVERGE-10K, so POST-CONVERGE-11 remains blocked until those failures are resolved or explicitly accepted by a later gate.
- Next recommended semantic task remains `POST-CONVERGE-10L - Distribution Descriptor and Product Proof Blocker Classification`; next test-performance task is `TEST-PERF-01 - CTest Sharding and Slow-Test Baseline`.
