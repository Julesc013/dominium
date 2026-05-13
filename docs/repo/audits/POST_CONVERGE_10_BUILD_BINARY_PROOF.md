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
| `git diff --check` | pending | final whitespace check |

## Next Recommended Task

Targeted build/toolchain remediation:

- install or expose Visual Studio 17 2022 Build Tools for the canonical `verify` lane, or provide reviewed CI proof
- alternatively install a supported compiler plus build tool and add a reviewed tuple mapping
- rerun POST-CONVERGE-10 to configure/build/test and produce native binaries
- then run POST-CONVERGE-11 product boot proof with native binaries
