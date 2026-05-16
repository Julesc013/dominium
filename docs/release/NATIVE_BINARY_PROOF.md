Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Native Binary Proof

## Status

- Phase: POST-CONVERGE-10G
- Status: partial

## Build Tuple

| Field | Value |
| --- | --- |
| tuple ID | `verify.winnt10.x64.msvc143.mt.debug` |
| toolchain | `msvc143` |
| generator | `Visual Studio 17 2022` |
| config | `debug` |
| platform | `win32` |
| renderer | `software` |
| proof level | build; focused AuditX and unit invariant CTest fixed; full CTest blocked by RepoX/discovery/wall-time gates |

## Product Binaries

| Product | Target | Executable Name | Path | Present? | Notes |
| --- | --- | --- | --- | --- | --- |
| setup | `setup_cli` | `setup` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/setup.exe` | yes | tuple build passes |
| launcher | `launcher_cli` | `launcher` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/launcher.exe` | yes | tuple build passes |
| client | `dominium_client` | `client` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/client.exe` | yes | tuple build passes |
| server | `dominium_server` | `server` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/server.exe` | yes | tuple build passes |
| tools | `dominium-tools` | `tools` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/tools.exe` | yes | tuple build passes |

## What This Proves

- The build contract, probe, local preset generator, and tuple runner exist.
- The local machine detects Visual Studio 2022/MSVC v143 and can generate the canonical local tuple preset.
- CMake configure passes for the tuple and canonical `verify` preset.
- The VS2022/v143 tuple build passes and emits native product binaries.
- The canonical `verify` build passes and bounded product smoke checks pass.
- Focused AuditX CTest cases pass after targeted path and generated-projection fixes.
- Focused tuple `invariant_units_present` passes after unit registry remediation.

## What This Does Not Prove

- product boot
- runtime/session proof
- portable projection proof
- public release support
- renderer or native GUI support

## Current Blocker

CTest remains blocked after build proof:

- `invariant_units_present` is fixed: `unit.mass_energy.stub` is declared in `data/registries/unit_registry.json`, and `unit.schema` path fragments are no longer treated as unit IDs
- focused tuple `inv_repox_rules` still fails on broad RepoX/canonical-evidence drift
- canonical `ctest --preset verify -N` currently discovers 0 tests, while the tuple verify build discovers 493 tests
- canonical `ctest --preset verify --output-on-failure` previously exceeded a 40-minute shell timeout; full CTest was not rerun in POST-CONVERGE-10F because focused RepoX still fails
- no generated binaries were committed

## POST-CONVERGE-10G Update

POST-CONVERGE-10G does not add product boot proof. It reduces focused RepoX from 1844 failures to 1769 failures, but focused tuple `inv_repox_rules` remains a semantic blocker. Native product boot proof remains deferred until RepoX is green or a reviewed gate explicitly accepts the remaining semantic failures.

## POST-CONVERGE-10H Update

POST-CONVERGE-10H does not add product boot proof. It reduces focused RepoX to 153 failures and 5 warnings, but product boot proof remains deferred until focused RepoX passes or receives reviewed disposition.

## POST-CONVERGE-10I Update - Historical Reference Remediation

- Result: PARTIAL.
- Focused RepoX improved from 153 failures / 5 warnings to 71 failures / 5 warnings.
- `INV-CANON-NO-HIST-REF` reduced from 81 to 0 by aligning RepoX enforcement to canonical-doc scope and preserving DERIVED quarantine/archive evidence references.
- POST-CONVERGE-11 remains blocked.
- Next recommended task: `POST-CONVERGE-10J - Authority-Sensitive Documentation Status Review`.

## POST-CONVERGE-10J Update - Authority Documentation Status

- Result: PARTIAL.
- Focused RepoX improved from 71 failures / 5 warnings to 60 failures / 5 warnings.
- `INV-DOC-STATUS-HEADER` reduced from 12 to 0.
- No product boot proof was run.
- POST-CONVERGE-11 remains blocked until focused RepoX is green or receives a reviewed disposition.
- Next recommended task: `POST-CONVERGE-10K - Contract Registry Acceptance Backlog Remediation`.

## POST-CONVERGE-10K Update - Contract Registry Acceptance

- Result: PARTIAL.
- Focused RepoX actual local state improved from 59 failures / 5 warnings to 51 failures / 5 warnings.
- The prior 10J-reported 60th failure was `INV-LOCKLIST-FROZEN`, which was absent at 10K start because `origin/main` equaled local HEAD.
- `INV-NEW-CONTRACT-REQUIRES-ENTRY` reduced from 9 to 0 by adding four accepted current architecture contract rows to `data/registries/semantic_contract_registry.json`.
- POST-CONVERGE-11 remains blocked because focused tuple `inv_repox_rules` still fails on distribution/product proof, retired-domain path policy, tool hash/audit staleness, ruleset mapping, and related families.
- Next recommended task: `POST-CONVERGE-10L - Distribution Descriptor and Product Proof Blocker Classification`.

## TEST-PERF-00 Update - Validation Tiers

- TEST-PERF-00 does not add product boot proof.
- Canonical CTest discovery is repaired locally after `cmake --preset verify`, with 493 tests discovered.
- CTest smoke label discovery now reports 57 tests after label metadata repair and reconfigure.
- Tiered and impacted validation tooling was added so product proof tasks can select focused tests before promotion gates.
- Full CTest, product boot proof, portable projection proof, package proof, and release proof remain not run by TEST-PERF-00.

## POST-CONVERGE-10L Update - Distribution/Product Proof Classification

- POST-CONVERGE-10L does not add product boot proof.
- Focused RepoX remains at 51 failures / 5 warnings after repairing a transient audit status-header issue.
- The remaining distribution/product target failures are missing `dist/bin` wrapper/projection surfaces for descriptor emission and AppShell-owned delegation.
- Native product binaries previously proven by build remain local build outputs and were not committed.
- POST-CONVERGE-11 remains blocked until non-proof RepoX failures are remediated or explicitly accepted by a reviewed gate.

## POST-CONVERGE-10M Update - Retired-Domain Path Policy

- POST-CONVERGE-10M does not add product boot proof.
- Focused RepoX improved from 51 failures / 5 warnings to 23 failures / 5 warnings by updating stale retired-domain RepoX rule paths to current source locations.
- Native product binaries previously proven by build remain local build outputs and were not committed.
- POST-CONVERGE-11 remains blocked until the remaining non-proof RepoX failures are remediated or explicitly accepted by a reviewed gate.

## POST-CONVERGE-10N Update - Tool Hash and Audit Staleness

- POST-CONVERGE-10N does not add product boot proof.
- Focused RepoX improved from 23 failures / 5 warnings to 20 failures / 5 warnings by refreshing stale identity and SecureX integrity evidence.
- Native product binaries previously proven by build remain local build outputs and were not committed.
- POST-CONVERGE-11 remains blocked until the remaining non-proof RepoX governance/source-policy failures are remediated or explicitly accepted by a reviewed gate.

## POST-CONVERGE-10O Update - RepoX Closeout Gate

- POST-CONVERGE-10O does not add product boot proof.
- Focused RepoX remains 20 failures / 5 warnings.
- Canonical `ctest --preset verify -N` reports 493 tests, but the listing includes missing-executable notices for many compiled tests because this closeout did not rerun the build.
- Native product binaries previously proven by build remain local build outputs and were not committed or refreshed by 10O.
- POST-CONVERGE-11 remains blocked because focused RepoX still has real non-proof governance/source-policy failures.
- Next recommended task: `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`.

## POST-CONVERGE-11 Update - Product Boot Gate

- POST-CONVERGE-11 does not add product boot proof.
- Focused RepoX remains 20 failures / 5 warnings and no accepted-warning ledger authorizes product boot.
- Product binaries were not inspected or executed.
- Native product binaries previously proven by build remain local build outputs and were not committed or refreshed by 11.
- POST-CONVERGE-12 is not ready.
- Next recommended task: `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`.

## POST-CONVERGE-12 Update - Portable Projection Gate

- POST-CONVERGE-12 does not refresh native binary proof.
- Product boot proof remains blocked, so native binaries were not inspected, copied, refreshed, or executed.
- No portable projection root was generated.
- RELEASE-00 internal pilot release is not ready.
- Next recommended task: `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`.

## Closeout Remediation Update - Native Binary Command Smoke

- Native binaries exist under `out/build/vs2026/verify/bin/`.
- `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, and `tools.exe` each returned exit code 0 for `--help`, `--version`, `--status`, and `--smoke`.
- `cmake --preset verify` passes.
- A full `cmake --build --preset verify` run was not completed because it timed out during verification after producing the binaries; this remains a TEST-PERF/partitioning follow-up rather than a product command-surface failure.
- No binaries, build outputs, package outputs, release outputs, or projection outputs were committed.
