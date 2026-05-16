# Build Verification Paths

## Status

- Phase: POST-CONVERGE-10G
- Current status: build proven, targeted AuditX fixed, unit invariant fixed, RepoX reduced but CTest still blocked by RepoX and discovery/wall-time gates

POST-CONVERGE-06 confirmed that repository layout and supplemental validators can run locally, while the canonical CMake verify lane was blocked by this machine's missing Visual Studio toolchain at that time. POST-CONVERGE-07 confirmed that no local product runtime proof could proceed without build output or an accepted equivalent CI proof.

POST-CONVERGE-08 re-ran `cmake --preset verify` with the same missing-generator failure. Product boot proof is therefore limited to script/wrapper AppShell help surfaces and does not replace native configure/build/CTest proof.

POST-CONVERGE-10 added a tuple-driven build contract and local machine probe. POST-CONVERGE-10B reprobed after Visual Studio installation. POST-CONVERGE-10C fixed the stale client/server source paths in active CMake and test inputs. POST-CONVERGE-10D fixed the UI bind byte-for-byte freshness issue by pinning tracked UI bind generated sources to LF line endings. POST-CONVERGE-10E fixed the targeted AuditX path and generated-projection blockers. POST-CONVERGE-10F fixed the unit invariant blocker. The VS2022/MSVC v143 tuple and the canonical `verify` preset now configure and build successfully, focused AuditX CTest cases pass, and focused tuple `invariant_units_present` passes. Full CTest is still blocked by `inv_repox_rules`, canonical `verify` CTest discovery, and local wall-time.

Build contract references:

- `contracts/build/floors.toml`
- `contracts/build/toolchains.toml`
- `contracts/build/tuples.toml`
- `contracts/build/artifacts.toml`
- `docs/build/BUILD_CONTRACT.md`

## Canonical Verify Lane

The canonical lane remains:

```text
cmake --preset verify
cmake --build --preset verify
ctest --preset verify
```

`verify` inherits `verify-win-vs2026` and `msvc-base` in `CMakePresets.json`.

| Property | Value |
| --- | --- |
| Generator | `Visual Studio 17 2022` |
| Architecture | `x64` |
| Binary dir | `${sourceDir}/out/build/vs2026/${presetName}` |
| Build type | `Debug` |
| Tests | `DOM_BUILD_TESTS=ON` |
| Local status | configure and build pass; focused AuditX and unit invariant tests pass in tuple lane; canonical CTest discovery currently reports 0 tests; full CTest remains blocked by RepoX and wall-time |
| CI status | intended MSVC proof lane if CI has Visual Studio 2022 |

## Local Fallback Lane

No committed fallback preset was added in POST-CONVERGE-06, POST-CONVERGE-10, or POST-CONVERGE-10B.

Reason:

- `where.exe cl`: not found, but CMake finds the VS2022-local compiler through the Visual Studio generator
- `where.exe ninja`: not found
- `where.exe gcc`, `clang`, `clang-cl`, `mingw32-make`, `nmake`, and `make`: not found

POST-CONVERGE-10B generated ignored local preset data at:

```text
.dominium.local/CMakeUserPresets.generated.json
CMakeUserPresets.json
```

`CMakeUserPresets.json` is ignored/local and exists only so CMake can consume generated tuple presets. Regenerate it before rerunning tuple commands, and remove it before final strict layout validation. The generated presets expose `tuple.verify.winnt10.x64.msvc143.mt.debug`, `tuple.verify.host.host.host_default.host.debug`, and `tuple.smoke.host.host.host_default.host.debug`.

## Build Contract Commands

Probe:

```text
python tools/build/probe_toolchains.py --repo-root . --out .dominium.local/toolchains.detected.json
```

Generate local preset data:

```text
python tools/build/generate_user_presets.py --repo-root . --probe .dominium.local/toolchains.detected.json --out .dominium.local/CMakeUserPresets.generated.json
```

Validate build contracts:

```text
python tools/build/validate_build_contract.py --repo-root . --strict
```

Run a tuple after a generated mapping exists:

```text
python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --dry-run
python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --configure
python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --build
python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --test
```

## Build/Test Commands

Canonical configure:

```text
cmake --preset verify
```

Canonical build, run only after configure passes:

```text
cmake --build --preset verify
```

Canonical tests, run only after configure and build pass:

```text
ctest --preset verify
```

## Environment Requirements

- CMake: local `cmake version 4.2.0` is available.
- Generator: `Visual Studio 17 2022` is required by the visible `verify` lane and is now backed by an installed VS2022 instance.
- Compiler/toolchain: Visual Studio Enterprise 2022 with C++ tools is detected; CMake selected MSVC tools `14.44.35207`.
- Windows SDK: CMake selected `10.0.26100.0`.
- Python: local `Python 3.8.1` is present and sufficient after the AIDE writer compatibility fix.
- Host: current visible canonical lane is Windows/MSVC-oriented.

## Current Gaps

- Local Visual Studio 2022 generator instance is present.
- Stale client/server CMake and test paths were remediated in POST-CONVERGE-10C.
- UI bind generated-output freshness was remediated in POST-CONVERGE-10D.
- Tuple and canonical `verify` builds now pass.
- Local Visual Studio 2026 and 2017 instances are not detected.
- Local configure/build proof is complete for the VS2022/v143 tuple and canonical `verify` preset.
- CTest proof is not complete: focused AuditX tests pass, focused tuple `invariant_units_present` now passes, focused tuple `inv_repox_rules` still fails, canonical `ctest --preset verify -N` currently reports 0 tests, and prior full CTest exceeded the local 40-minute shell timeout.
- Native product binaries are produced locally by the tuple build; canonical `verify` produces setup/launcher/client/server binaries.
- FAST still fails after the structural fix because RepoX exposes broad drift and missing-artifact backlog; tuple CTest exposes the same broad RepoX blocker through `inv_repox_rules`.
- POST-CONVERGE-07 could not run product binaries or prove local playtest/session/status/save/load/resume.
- POST-CONVERGE-08 could not run native product binaries; only partial script/wrapper help surfaces were proven.
- The Python server AppShell script can be invoked, but direct script execution currently ignores CLI args, so it is not a canonical product command proof.

## POST-CONVERGE-10G RepoX Update

Focused tuple `inv_repox_rules` still fails after safe 10G remediation, but the failure count dropped from 1844 to 1769. Canonical `ctest --preset verify -N` still discovers 0 tests, so tuple CTest remains the effective focused lane for this blocker. No configure/build rerun was required because only RepoX governance code and evidence docs changed.

## POST-CONVERGE-10H RepoX Update

Focused tuple `inv_repox_rules` remains failing after 10H, but the failure count is now 153. Canonical `ctest --preset verify -N` still discovers 0 tests. No configure/build rerun was required because changes were documentation metadata/index/evidence only.

## POST-CONVERGE-10I Update - Historical Reference Remediation

- Result: PARTIAL.
- Focused RepoX improved from 153 failures / 5 warnings to 71 failures / 5 warnings.
- `INV-CANON-NO-HIST-REF` reduced from 81 to 0 by aligning RepoX enforcement to canonical-doc scope and preserving DERIVED quarantine/archive evidence references.
- POST-CONVERGE-11 remains blocked.
- Next recommended task: `POST-CONVERGE-10J - Authority-Sensitive Documentation Status Review`.

## POST-CONVERGE-10J Update - Authority Documentation Status

- Result: PARTIAL.
- Focused tuple `inv_repox_rules` improved from 71 failures / 5 warnings to 60 failures / 5 warnings.
- `INV-DOC-STATUS-HEADER` reduced from 12 to 0.
- Canonical `ctest --preset verify -N` still discovers 0 tests, so tuple CTest remains the effective focused lane.
- No configure/build rerun was required because changes were documentation metadata, canon index, and evidence updates only.
- POST-CONVERGE-11 remains blocked.

## POST-CONVERGE-10K Update - Contract Registry Acceptance

- Result: PARTIAL.
- Focused RepoX actual local state improved from 59 failures / 5 warnings to 51 failures / 5 warnings.
- The prior 10J-reported 60th failure was `INV-LOCKLIST-FROZEN`, which was absent at 10K start because `origin/main` equaled local HEAD.
- `INV-NEW-CONTRACT-REQUIRES-ENTRY` reduced from 9 to 0 by adding four accepted current architecture contract rows to `data/registries/semantic_contract_registry.json`.
- POST-CONVERGE-11 remains blocked because focused tuple `inv_repox_rules` still fails on distribution/product proof, retired-domain path policy, tool hash/audit staleness, ruleset mapping, and related families.
- Next recommended task: `POST-CONVERGE-10L - Distribution Descriptor and Product Proof Blocker Classification`.

## TEST-PERF-00 Update - CTest Discovery and Tiers

- `ctest --preset verify -N` reported 0 tests before the local verify build tree was refreshed.
- `cmake --preset verify` passed and restored canonical discovery to 493 tests.
- `dom_add_testx` now writes CTest labels directly, so label-filtered tiers are usable after reconfigure.
- `ctest --preset verify -N -L smoke` reports 57 tests after the label repair and reconfigure.
- Tiered validation helpers are available:
  - `python scripts/test_tier.py --list`
  - `python scripts/test_tier.py --tier t0`
  - `python scripts/test_impacted.py --from HEAD~1`
  - `python scripts/test_timing_report.py --preset verify --config Debug --regex invariant_units_present --limit 1 --out .dominium.local/test-perf-00/timing-sample.json`
- Full CTest remains the promotion gate and was not run by TEST-PERF-00.

## POST-CONVERGE-10L Update - Distribution/Product Proof Classification

- `ctest --preset verify -N` reports 493 tests in the refreshed local verify build tree.
- Focused `ctest --preset verify -R inv_repox_rules --output-on-failure` remains failing at 51 failures / 5 warnings after the safe audit status-header fix.
- The 12 distribution/product target failures are missing `dist/bin` wrapper/projection surfaces, not build-output proof that can be faked in a governance classification task.
- No configure/build rerun was required because POST-CONVERGE-10L changed evidence/status files only.
- POST-CONVERGE-11 remains blocked by non-proof RepoX governance failures.

## POST-CONVERGE-10M Update - Retired-Domain Path Policy

- `ctest --preset verify -N` reports 493 tests in the refreshed local verify build tree.
- Focused `ctest --preset verify -R inv_repox_rules --output-on-failure` remains failing, improved to 23 failures / 5 warnings after stale retired-domain RepoX paths were updated.
- No configure/build rerun was required because POST-CONVERGE-10M changed RepoX governance code and evidence/status files only.
- Full CTest remains a promotion gate and was not run because focused RepoX still has semantic failures.
- POST-CONVERGE-11 remains blocked by non-proof RepoX governance failures.

## POST-CONVERGE-10N Update - Tool Hash and Audit Staleness

- `ctest --preset verify -N` reports 493 tests in the refreshed local verify build tree.
- Focused `ctest --preset verify -R inv_repox_rules --output-on-failure` remains failing, improved to 20 failures / 5 warnings after stale identity and SecureX integrity evidence were refreshed.
- No configure/build rerun was required because POST-CONVERGE-10N changed RepoX governance code and evidence/status files only.
- Full CTest remains a promotion gate and was not run because focused RepoX still has semantic failures.
- POST-CONVERGE-11 remains blocked by non-proof RepoX governance/source-policy failures.

## POST-CONVERGE-10O Update - Closeout Gate

- `ctest --preset verify -N` reports 493 tests in the current local verify build tree.
- The discovery listing prints missing-executable notices for many compiled tests because POST-CONVERGE-10O did not run configure/build and does not refresh local binaries.
- Focused `ctest --preset verify -R inv_repox_rules --output-on-failure` remains failing at 20 failures / 5 warnings.
- Full CTest remains a promotion gate and was not run because focused RepoX still has hard semantic failures.
- POST-CONVERGE-11 remains blocked until non-proof RepoX governance/source-policy failures are remediated or explicitly accepted.

## POST-CONVERGE-11 Update - Product Boot Gate

- `ctest --preset verify -N` reports 493 tests.
- Focused `ctest --preset verify -R inv_repox_rules --output-on-failure` remains failing at 20 failures / 5 warnings.
- Product binary discovery and execution were not performed because focused RepoX remains a semantic blocker.
- No configure/build rerun was performed by POST-CONVERGE-11.
- Build and product boot should be retried only after the RepoX readiness gate passes or is explicitly accepted.

## POST-CONVERGE-12 Update - Portable Projection Gate

- POST-CONVERGE-12 did not run configure, build, product boot, package, release, or projection generation.
- The task stopped because POST-CONVERGE-11 product boot proof is blocked and not accepted as portable projection input.
- No generated projection root exists under `.dominium.local/projections/post-converge-12/`.
- Build and projection proof should be retried only after focused RepoX is pass or accepted-warning and POST-CONVERGE-11 product boot proof succeeds or is explicitly accepted.

## Closeout Remediation Update - Verify Fast Lane

- `cmake --preset verify` passes locally.
- `cmake --build --preset verify` was started but not completed; it timed out during verification after producing native product/tool binaries in `out/build/vs2026/verify/bin/`.
- Missing smoke executable blockers for the fast lane were remediated by adding the product tool host, field tools, and UI accessibility test dependencies to `verify_fast`.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300` passes 57/57.
- `ctest --preset verify -R inv_repox_rules --output-on-failure` passes.
- Full CTest remains a promotion gate and still needs sharding/wall-time work before it should be used as the normal feedback path.
