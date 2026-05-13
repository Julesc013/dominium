# POST-CONVERGE-10 Build Contract / Native Binary Proof Audit

## Status

- Task ID: POST-CONVERGE-10
- Result: partial
- Date/time: 2026-05-13T13:57:59+10:00
- Branch: `main`
- HEAD SHA: `3455d6976847ad3a3072850fc4b3b49783246830`
- origin/main SHA: `3455d6976847ad3a3072850fc4b3b49783246830`
- Working tree status before task: clean; `main` synced to `origin/main`
- Working tree status after task: POST-CONVERGE-10 contract, tools, docs, and audit modified for commit

## Scope

This task covered:

- build contract
- machine probe
- generated local presets
- configure/build/test attempt
- native binary proof if possible
- no feature work
- no platform/render/native implementation
- no Universal Reality enforcement

## Prior State

POST-CONVERGE-06 through POST-CONVERGE-09 established:

- `cmake --preset verify` is blocked locally because Visual Studio 17 2022 is not installed or discoverable.
- `cmake --build --preset verify` and `ctest --preset verify` have not run.
- Product boot proof is partial and script/wrapper-only.
- Portable projection proof is partial; no real projection root or native binaries exist.
- FAST reaches RepoX drift after prior structural remediation.

## Machine Probe Result

| Tool | Detected? | Version/Detail | Notes |
| --- | --- | --- | --- |
| CMake | yes | `4.2.0` | generator names include Visual Studio 18 2026, 17 2022, 15 2017, Ninja, and others |
| Python | yes | `3.8.1` | local script runtime |
| Ninja | no | not found | blocks Ninja fallback |
| Visual Studio 17 2022 | no | no instance detected | canonical `verify` remains blocked |
| Visual Studio 18 2026 | no | no instance detected | generator name is not instance proof |
| Visual Studio 15 2017 | no | no instance detected | compatibility tuple blocked |
| GCC/G++ | no | not found | GCC tuple blocked |
| Clang/Clang++/clang-cl | no | not found | Clang tuple blocked |
| Xcode | no | not applicable | not a macOS host |

## Build Contract Files

| File | Role |
| --- | --- |
| `contracts/build/floors.toml` | floor registry |
| `contracts/build/toolchains.toml` | toolchain registry |
| `contracts/build/tuples.toml` | tuple registry |
| `contracts/build/artifacts.toml` | artifact identity policy |
| `contracts/build/build_contract.schema.json` | broad shape schema |

## Generated Preset Result

| Item | Result |
| --- | --- |
| generated file path | `.dominium.local/CMakeUserPresets.generated.json` |
| committed? | no |
| generated tuples | none |
| blocked tuples | all 7 contract tuples |

`CMakeUserPresets.json` remains ignored/local. `CMakePresets.json` was not changed.

## Configure / Build / Test Result

| Tuple | Configure | Build | Test | Output | Notes |
| --- | --- | --- | --- | --- | --- |
| `verify` | fail | not run | not run | none | `Visual Studio 17 2022` instance missing |
| `verify.host.host.host_default.host.debug` | blocked | not run | not run | none | generated preset unavailable because `host_default` is unavailable |

## Native Binary Result

| Product | Expected Binary | Produced? | Path | Notes |
| --- | --- | --- | --- | --- |
| setup | `setup` | no | none | no tuple configured |
| launcher | `launcher` | no | none | no tuple configured |
| client | `client` | no | none | no tuple configured |
| server | `server` | no | none | no tuple configured |
| tools | `tools` | no | none | no tuple configured |

## Blockers

- No Visual Studio 17 2022 instance is detected.
- No Visual Studio 18 2026 instance is detected.
- No Visual Studio 15 2017 instance is detected.
- `cl`, `ninja`, `gcc`, `g++`, `clang`, `clang++`, `clang-cl`, `nmake`, and `mingw32-make` are not detected on PATH.
- No generated local configure preset can be emitted for an available tuple.
- Native product binaries are still missing.

## Files Added/Changed

- Added build contracts under `contracts/build/`.
- Added build probe/generator/validator/runner scripts under `tools/build/`.
- Added build docs under `docs/build/`.
- Added `docs/release/NATIVE_BINARY_PROOF.md`.
- Updated build verification, remediation, release matrix, and post-CONVERGE next-step docs.
- Updated `.gitignore` for local generated preset/probe output.
- Updated repo layout/root-allowlist contracts to classify `.dominium.local/` as ignored local metadata.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `python -m py_compile tools/build/build_contract_common.py tools/build/probe_toolchains.py tools/build/generate_user_presets.py tools/build/validate_build_contract.py tools/build/run_tuple.py` | pass | build tools parse |
| `python tools/build/validate_build_contract.py --repo-root .` | pass | floors: 9; toolchains: 9; tuples: 7; artifacts: 2 |
| `python tools/build/validate_build_contract.py --repo-root . --json` | pass | no errors or warnings |
| `python tools/build/validate_build_contract.py --repo-root . --strict` | pass | strict result pass |
| `python tools/build/probe_toolchains.py --repo-root . --json` | pass | no available toolchains |
| `python tools/build/probe_toolchains.py --repo-root . --out .dominium.local/toolchains.detected.json` | pass | ignored local probe output written |
| `python tools/build/generate_user_presets.py --repo-root . --dry-run` | pass | generated no presets; all tuples blocked |
| `python tools/build/generate_user_presets.py --repo-root . --probe .dominium.local/toolchains.detected.json --out .dominium.local/CMakeUserPresets.generated.json` | pass | ignored local generated preset data written |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.host.host.host_default.host.debug --dry-run` | expected blocked | `host_default` unavailable |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.host.host.host_default.host.debug --all` | expected blocked | no generated configure preset exists |
| `cmake --list-presets` | pass | visible presets: `local`, `verify`, `release-check`, `release-winnt-x86_64` |
| `cmake --list-presets=all` | pass | configure/build/test visible preset sets listed |
| `cmake --preset verify` | fail | Visual Studio 17 2022 instance missing |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | `.dominium.local/` classified as metadata; unexcepted violations: none |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | `.dominium.local/` classified as metadata; unexcepted violations: none |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | warnings: 0 |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | warnings: 0 |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | build boundary checks passed |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK |
| `python tools/validators/check_local_playtest_path.py --repo-root .` | pass, blocked proof | built product binaries missing; server script CLI forwarding blocker remains |
| `python tools/validators/check_product_boot_matrix.py --repo-root .` | pass, partial proof | built product binaries missing |
| `python tools/validators/check_portable_projection.py --repo-root .` | pass, partial proof | built binaries and projection root missing |
| `git diff --check` | pass | line-ending warnings only; no whitespace errors |
| `git diff --cached --check` | pass | staged whitespace check passed |
| final `git diff --check` | pass | line-ending warnings only; no whitespace errors |

## Next Recommended Task

Targeted build/toolchain remediation:

- install or expose Visual Studio 17 2022 Build Tools for the canonical `verify` lane, or provide reviewed CI proof
- alternatively install a supported compiler plus build tool and add a reviewed tuple mapping
- rerun POST-CONVERGE-10 to configure/build/test and produce native binaries
- then run POST-CONVERGE-11 product boot proof with native binaries

## POST-CONVERGE-10B Follow-up

POST-CONVERGE-10B reprobed this machine after Visual Studio installation.

Updated result:

- Visual Studio Enterprise 2022 `17.14.37301.10` is detected.
- `vswhere -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64` detects a C++-capable VS2022 instance.
- CMake selects Windows SDK `10.0.26100.0` and MSVC toolset path `VC/Tools/MSVC/14.44.35207`.
- Generated ignored local presets now include `tuple.verify.winnt10.x64.msvc143.mt.debug`.
- The tuple and direct `verify` configure both fail during CMake generation on stale pre-convergence source paths:
  - `client/presentation/frame_graph_builder.cpp`
  - `server/authority/dom_server_authority.cpp`
- Build and CTest were not run because configure did not complete.
- No native product binaries were produced.

Current blocker: targeted CMake/test path remediation is required before native build proof can proceed.

## POST-CONVERGE-10C Follow-up

POST-CONVERGE-10C fixed the active stale client/server CMake and test references discovered by POST-CONVERGE-10B.

Updated proof level:

- `verify.winnt10.x64.msvc143.mt.debug` configure: pass.
- `cmake --preset verify`: pass.
- Tuple build: fail on stale UI bind generated outputs.
- Canonical `cmake --build --preset verify`: fail on the same UI bind freshness gate.
- `ctest --preset verify`: not run because build failed.

Native binary status:

- `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, and `tools.exe` were produced under `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin` before the tuple build failed.
- `setup.exe`, `launcher.exe`, `client.exe`, and `server.exe` were produced under `out/build/vs2026/verify/bin` before the canonical build failed.
- Generated binaries were not committed.

Current blocker: `tool_ui_bind --check` reports stale generated outputs in `libs/appcore/ui_bind/`.

## POST-CONVERGE-10D Follow-up

POST-CONVERGE-10D fixed the UI bind generated-output freshness blocker by adding a narrow LF line-ending policy for tracked generated UI bind outputs.

Updated proof level:

- `tool_ui_bind --check`: pass.
- `verify.winnt10.x64.msvc143.mt.debug` configure: pass.
- `verify.winnt10.x64.msvc143.mt.debug` build: pass.
- `verify.winnt10.x64.msvc143.mt.debug` CTest: timeout/fail in tools/auditx tests.
- `cmake --preset verify`: pass.
- `cmake --build --preset verify`: pass.
- `ctest --preset verify`: timeout/fail in tools/auditx tests.

Native binary status:

- `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, and `tools.exe` are present under `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin`.
- `setup.exe`, `launcher.exe`, `client.exe`, and `server.exe` were produced under `out/build/vs2026/verify/bin` during the canonical verify build.
- Generated binaries were not committed; root `out/` output was removed before final source commit.

Current blocker: CTest/auditx remediation is required. Representative failures include missing `compat` import resolution in `tools_coverage_inspect`, auditx/governance model assumptions about a root `schema` path, and existing RepoX drift.

## POST-CONVERGE-10E Follow-up

POST-CONVERGE-10E fixed the targeted CTest/AuditX blockers found in POST-CONVERGE-10D.

Updated proof level:

- `tools_refusal_explain`: pass.
- `tools_coverage_inspect`: pass.
- focused AuditX CTest cases: pass.
- `verify.winnt10.x64.msvc143.mt.debug` configure: pass.
- `verify.winnt10.x64.msvc143.mt.debug` build: pass.
- `verify.winnt10.x64.msvc143.mt.debug` CTest: timeout/fail; CTest reached `invariant_units_present`, which fails.
- `cmake --preset verify`: pass.
- `cmake --build --preset verify`: pass.
- `ctest --preset verify --output-on-failure`: timeout/fail; `inv_repox_rules` fails and full run exceeds the local 40-minute shell timeout.

Remediations:

- `tools/distribution/distribution_lib.py` now makes the repo root importable for direct tool subprocesses before importing `compat.shims`.
- `tools/dist/dist_tree_common.py` now sources generated `schema/` and `schemas/` bundle projections from canonical `contracts/schemas/`.
- `tools/dist/dist_tree_common.py` includes current converged `apps/` and `game/` runtime roots in generated portable wrapper runtime content.
- `tools/setup/setup_cli.py` defers annotation evaluation so generated wrapper smoke runs under Python 3.9.
- `tools/mvp/ecosystem_verify_common.py` converts missing release manifest verification into a deterministic refused result instead of an uncaught exception.

Native binary status:

- `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, and `tools.exe` are present under `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin`.
- `setup.exe`, `launcher.exe`, `client.exe`, and `server.exe` are present under `out/build/vs2026/verify/bin`.
- Generated binaries were not committed.

Current blockers:

- `invariant_units_present` fails because the canonical unit table does not declare `unit.mass_energy.stub` and the validator treats `contracts/schemas/materials/unit.schema` as a `unit.schema` token.
- `inv_repox_rules` fails on broad RepoX drift that remains outside safe POST-CONVERGE-10E remediation scope.
