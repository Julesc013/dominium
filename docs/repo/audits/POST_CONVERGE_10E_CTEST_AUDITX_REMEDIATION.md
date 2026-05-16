Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# POST-CONVERGE-10E CTest / AuditX Remediation Audit

## Status

- Task ID: POST-CONVERGE-10E
- Result: partial
- Date/time: 2026-05-13T22:55:46+10:00
- Branch: `main`
- HEAD SHA: `0f842071f543e31c18edc557576adc6ff301cd81`
- origin/main SHA: `0f842071f543e31c18edc557576adc6ff301cd81`
- Working tree status before task: clean tracked tree; ignored `.dominium.local/`, generated build output, and distribution output present
- Working tree status after task: targeted AuditX/CTest fixes, audit docs, proof docs, and AIDE task packet modified for commit; generated local outputs remain ignored/uncommitted

## Scope

This task covered:

- targeted CTest/AuditX/RepoX/TestX remediation
- no feature work
- no product boot proof
- no runtime proof
- no package/projection proof
- no renderer/platform/native implementation
- no target, binary, or product ID rename

## Prior Blocker

POST-CONVERGE-10D proved:

- `verify.winnt10.x64.msvc143.mt.debug` configure: pass
- `verify.winnt10.x64.msvc143.mt.debug` build: pass
- `cmake --preset verify`: pass
- `cmake --build --preset verify`: pass
- native binaries are produced

The 10D CTest blockers were:

- `tools_coverage_inspect` and `tools_refusal_explain` failing with `ModuleNotFoundError: No module named 'compat'`.
- AuditX/governance tests failing on a retired root `schema` path.
- RepoX drift remaining active.

## Failing Tests

| Test | Result | Failure Class | First Meaningful Failure | Notes |
| --- | --- | --- | --- | --- |
| `tools_refusal_explain` | fixed | stale_path | subprocess could not import root `compat` package | fixed by making `tools/distribution/distribution_lib.py` add repo root to `sys.path` for direct tool subprocesses |
| `tools_coverage_inspect` | fixed | stale_path | subprocess could not import root `compat` package | same import-root fix |
| `tools_auditx` | fixed | stale_path / missing_canonical_root | `FileNotFoundError: ... dominium\\schema`; then missing generated `release_manifest.json` escaped as an exception | fixed schema projection source and converted missing release manifest into deterministic refused verification |
| `test_auditx_canonical_hash_stability` | fixed | stale_path / missing_canonical_root | same root `schema` and release manifest exception path | focused CTest passed after remediation |
| `test_auditx_empty_path` | fixed | stale_path / timeout | same AuditX path path; slow after fix | focused CTest passed in about 15.8 minutes |
| `test_auditx_arbitrary_cwd` | fixed | stale_path | arbitrary cwd scan reached repo-root-aware paths | focused CTest passed |
| `invariant_units_present` | remaining | real_drift | `unit.mass_energy.stub` and `unit.schema` not declared in canonical unit table | outside safe 10E AuditX path remediation scope |
| `inv_repox_rules` | remaining | real_drift | broad RepoX drift backlog, including root structure, stale audit evidence, and missing AppShell/embodiment/projection surfaces | not safe to resolve in this task without broad governance/product work |

## References Found

| Reference | File | Classification | Action | Notes |
| --- | --- | --- | --- | --- |
| `compat.shims` | `tools/distribution/distribution_lib.py` | stale subprocess import assumption | fixed | direct script subprocesses now add repo root to import path |
| `contracts/schemas` | `tools/dist/dist_tree_common.py` | current canonical schema root | fixed | portable projection still emits `schema/` and `schemas/` bundle projections from canonical source |
| `schema` | `tools/dist/dist_tree_common.py` | generated bundle projection | preserved | destination only; not reintroduced as source authority |
| `schemas` | `tools/dist/dist_tree_common.py` | generated bundle projection | preserved | destination only; not reintroduced as source authority |
| `apps` runtime source | `tools/dist/dist_tree_common.py` | convergence root | fixed | portable wrapper smoke needs current product Python modules |
| `game` runtime source | `tools/dist/dist_tree_common.py` | convergence root | fixed | portable wrapper smoke needs current game package imports |
| `dict | None` annotations | `tools/setup/setup_cli.py` | Python 3.9 compatibility blocker | fixed | postponed annotation evaluation; no behavior change |
| `verify_release_manifest` exception | `tools/mvp/ecosystem_verify_common.py` | generated manifest absence surfaced as crash | fixed | now returns deterministic refused result with blocking error |
| `unit.mass_energy.stub` | `contracts/schemas/quantity.schema.json` | unit registry drift | classified | not changed in this task |
| `unit.schema` | `contracts/schemas/materials/unit.schema` | false-positive unit-token/path-string drift | classified | not changed in this task |

## Changes Made

| File | Change | Reason | Validation Strength Changed? |
| --- | --- | --- | --- |
| `tools/distribution/distribution_lib.py` | adds repo root to `sys.path` before importing `compat.shims` | direct CTest subprocesses run from build test directories | no |
| `tools/dist/dist_tree_common.py` | copies canonical `contracts/schemas/` into generated `schema/` and `schemas/` bundle projections | avoid retired root `schema` as source while preserving bundle layout | no |
| `tools/dist/dist_tree_common.py` | includes `apps` and `game` in runtime source roots | current portable wrapper smoke imports converged roots | no |
| `tools/setup/setup_cli.py` | adds postponed annotations | generated wrapper smoke runs under Python 3.9 | no |
| `tools/mvp/ecosystem_verify_common.py` | wraps missing/unreadable release manifest verification as deterministic refused result | AuditX reports blocker instead of crashing | no |

## Configure / Build / Test Result

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --dry-run` | pass | tuple commands resolved |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --configure` | pass | required ignored `CMakeUserPresets.json` generated locally for CMake consumption |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --build` | pass | native product binaries produced |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --test` | timeout/fail | runner timeout after 20 minutes; tuple CTest reached `invariant_units_present`, which fails |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R "^tools_auditx$" --output-on-failure` | pass | 1048.11 seconds |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R "^test_auditx_canonical_hash_stability$" --output-on-failure` | pass | 19.98 seconds |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R "^test_auditx_empty_path$" --output-on-failure` | pass | 946.27 seconds |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R "^test_auditx_arbitrary_cwd$" --output-on-failure` | pass | 10.32 seconds |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R "^invariant_units_present$" --output-on-failure` | fail | undeclared `unit.mass_energy.stub` and `unit.schema` |
| `cmake --preset verify` | pass | canonical configure green |
| `cmake --build --preset verify` | pass | canonical build and bounded product smoke checks green |
| `ctest --preset verify --output-on-failure` | timeout/fail | shell timeout after 40 minutes; focused log shows `inv_repox_rules` fails and AuditX tests pass before timeout |
| `ctest --test-dir out/build/vs2026/verify -C Debug -R "^inv_repox_rules$" --output-on-failure` | fail | broad RepoX drift backlog |

## Native Binary Result

| Product | Produced? | Path | Notes |
| --- | --- | --- | --- |
| setup | yes | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/setup.exe` | generated, ignored |
| launcher | yes | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/launcher.exe` | generated, ignored |
| client | yes | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/client.exe` | generated, ignored |
| server | yes | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/server.exe` | generated, ignored |
| tools | yes | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/tools.exe` | generated, ignored |

Canonical `verify` also produced `setup.exe`, `launcher.exe`, `client.exe`, and `server.exe` under `out/build/vs2026/verify/bin` during validation. Root `out/` output was removed before commit, and generated binaries were not committed.

## Remaining Blockers

- `invariant_units_present` fails because the unit validation table does not declare `unit.mass_energy.stub`, and it treats `contracts/schemas/materials/unit.schema` as a `unit.schema` reference.
- `inv_repox_rules` fails on broad existing RepoX drift. This includes missing generated distribution descriptors, canonical index drift, missing AppShell/embodiment/projection surfaces, stale generated audit evidence, rule map gaps, and root-structure drift.
- `ctest --preset verify --output-on-failure` exceeds a 40-minute shell timeout because slow AuditX tests are part of the full test set, even though the focused AuditX tests now pass.

## Files Added/Changed

- Added `docs/repo/audits/POST_CONVERGE_10E_CTEST_AUDITX_REMEDIATION.md`.
- Updated `tools/distribution/distribution_lib.py`.
- Updated `tools/dist/dist_tree_common.py`.
- Updated `tools/setup/setup_cli.py`.
- Updated `tools/mvp/ecosystem_verify_common.py`.
- Updated POST-CONVERGE-10/10D build proof docs.
- Updated build verification, build environment remediation, FAST remediation, native binary proof, and next-step docs.
- Refreshed `.aide/context/latest-task-packet.md`.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `python .aide/scripts/aide_lite.py doctor` | pass | warnings only |
| `python .aide/scripts/aide_lite.py validate` | pass | warnings only |
| `python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-10E CTest AuditX remediation"` | pass | task packet updated |
| `python -m py_compile tools/build/build_contract_common.py tools/build/probe_toolchains.py tools/build/generate_user_presets.py tools/build/validate_build_contract.py tools/build/run_tuple.py tools/mvp/ecosystem_verify_common.py tools/distribution/distribution_lib.py tools/dist/dist_tree_common.py tools/setup/setup_cli.py` | pass | build and touched tools parse |
| `python tests/tools/tools_coverage_inspect_tests.py --repo-root .` | pass | `coverage_inspect OK` |
| `python tests/tools/tools_refusal_explain_tests.py --repo-root .` | pass | `refusal_explain OK` |
| `python tools/build/validate_build_contract.py --repo-root . --strict` | pass | build contract valid |
| `python tools/build/probe_toolchains.py --repo-root . --out .dominium.local/toolchains.detected.json` | pass | available: `host_default`, `msvc143` |
| `python tools/build/generate_user_presets.py --repo-root . --probe .dominium.local/toolchains.detected.json --out .dominium.local/CMakeUserPresets.generated.json` | pass | generated local tuple data |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --dry-run` | pass | tuple commands resolved |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --configure` | pass | tuple configure green |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --build` | pass | tuple build green |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --test` | timeout/fail | internal 20-minute timeout; CTest reached later invariant blocker |
| focused AuditX CTest cases | pass | all targeted AuditX tests pass individually |
| `cmake --preset verify` | pass | canonical configure green |
| `cmake --build --preset verify` | pass | canonical build green |
| `ctest --preset verify --output-on-failure` | timeout/fail | `inv_repox_rules` failed; run exceeded 40-minute shell timeout |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | strict layout validator green; transient root inventory output restored before commit |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | strict root allowlist validator green |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | strict distribution validator green |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | strict component matrix validator green |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | build boundary checks passed |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK |
| `python tools/validators/check_local_playtest_path.py --repo-root .` | pass, blocked proof | reports missing committed product binaries and server script CLI forwarding blocker |
| `python tools/validators/check_product_boot_matrix.py --repo-root .` | pass, partial proof | reports missing committed product binaries |
| `python tools/validators/check_portable_projection.py --repo-root .` | pass, partial proof | reports missing committed product binaries and no projection root |
| `git diff --check` | pass | line-ending warnings only; no whitespace errors |

## Readiness

- ready_for_POST_CONVERGE_11: no
- reason: native build and targeted AuditX tests pass, but CTest still has real failing gates (`invariant_units_present`, `inv_repox_rules`) and full canonical CTest exceeds the local timeout.

## POST-CONVERGE-10F Follow-Up Note

POST-CONVERGE-10F cleared the `invariant_units_present` blocker by declaring `unit.mass_energy.stub` in `data/registries/unit_registry.json` and avoiding false-positive unit parsing from `materials/unit.schema` path fragments.

`inv_repox_rules` remains a real broad RepoX/canonical-evidence drift blocker. POST-CONVERGE-10F also found that canonical `ctest --preset verify -N` currently discovers 0 tests while the tuple verify build discovers 493 tests. Product boot proof remains deferred until RepoX drift and canonical CTest discovery are remediated or explicitly dispositioned.
