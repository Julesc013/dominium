Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# POST-CONVERGE-09 Portable Projection / Package Smoke Proof Audit

## Status

- Task ID: POST-CONVERGE-09
- Result: partial
- Date/time: 2026-05-12T22:05:00+10:00
- Branch: `main`
- HEAD SHA: `9083d064bc3726f10b98727c5371bc94972b5ea7`
- origin/main SHA: `4ccb80276ed4e2b250876fd1e037ccbe98522964`
- Working tree status before task: clean; `main` was ahead of `origin/main` by 1 local POST-CONVERGE-08 commit
- Working tree status after task: POST-CONVERGE-09 docs and validator modified for commit

## Scope

This task covered:

- portable projection/package smoke proof only
- distribution contract, portable layout, package export, and package tool discovery
- dry-run projection validation
- temporary local `.dompkg` pack/verify smoke
- no public release
- no generated artifacts committed
- no new features
- no semantic changes
- no platform/render/native implementation

## Prior Proof Inputs

| Input | Status | Notes |
| --- | --- | --- |
| POST-CONVERGE-07 runtime proof | blocked | canonical local runtime/session proof is blocked by missing build output |
| POST-CONVERGE-08 product boot proof | partial | script/wrapper help surfaces were proven; native product binaries were not |
| build path | blocked | `cmake --preset verify` fails locally because Visual Studio 17 2022 is missing |

Portable projection generation is therefore not build-proven. This task records dry-run projection coherence and package-tool smoke only.

## Distribution Commands / Tools Discovered

| Command/Tool | Purpose | Safe To Run? | Result | Notes |
| --- | --- | --- | --- | --- |
| `python release/packaging/setup/scripts/packaging/pipeline.py --help` | packaging pipeline root help | yes | pass | exposes `assemble`, `portable`, `windows`, `steam`, `macos`, and `linux` |
| `python release/packaging/setup/scripts/packaging/pipeline.py assemble --help` | assemble artifact root from build output | yes, help only | pass | real run requires build dir |
| `python release/packaging/setup/scripts/packaging/pipeline.py portable --help` | create portable archive from artifact root | yes, help only | pass | real run requires artifact root |
| `python tools/package/distribution/tool_pkg_pack.py --help` | pack deterministic `.dompkg` artifacts | yes | pass | also used for temp docs package smoke |
| `python tools/package/distribution/tool_pkg_verify.py --help` | verify `.dompkg` artifacts | yes | pass | also used for temp docs package smoke |
| `python tools/package/distribution/tool_pkg_index.py --help` | create package index | yes, help only | pass | real run requires package directory |
| `python tools/package/distribution/pkg_pack_all.py --help` | pack build outputs into package groups | yes, help only | pass | real run requires build output |
| `python tools/package/distribution/pkg_verify_all.py --help` | verify package output tree | yes, help only | pass | real run requires package directory |
| `python tools/package/distribution/build_manifest.py --help` | generate dist build manifest | yes, help only | pass | real run requires package index |
| `python tools/package/distribution/setup_install_smoke.py --help` | setup smoke runner | yes, help only | pass | real run currently inherits setup Python bridge blocker |
| `python tools/package/distribution/launcher_run_smoke.py --help` | launcher smoke runner | yes, help only | pass | real run creates temp manifests and requires launcher CLI behavior |

## Portable Projection Sequence Tested

| Step | Command/Input | Result | Evidence | Notes |
| --- | --- | --- | --- | --- |
| contract audit | `python tools/validators/check_portable_projection.py --repo-root .` | pass, partial proof | `proof_status: partial` | contract/docs/tools coherent; binaries and projection root missing |
| dry-run layout | `python tools/validators/check_portable_projection.py --repo-root . --dry-run` | pass, partial proof | dry-run printed blocked sequence | no output creation |
| strict projection proof | `python tools/validators/check_portable_projection.py --repo-root . --strict` | expected fail | strict exits non-zero because `proof_status` is not `proven` | no projection root or built binaries exist |
| `.dompkg` pack smoke | `python tools/package/distribution/tool_pkg_pack.py --input-file docs/distribution/PORTABLE_INSTALL_LAYOUT.md --out %TEMP%/.../smoke_docs.dompkg ...` | pass | `result: ok`, `file_count: 1` | temp output removed |
| `.dompkg` verify smoke | `python tools/package/distribution/tool_pkg_verify.py --pkg %TEMP%/.../smoke_docs.dompkg` | pass | `result: ok`, matching content hash | temp output removed |

## Projection Layout Result

| Path/Manifest | Required? | Present? | Evidence | Notes |
| --- | --- | --- | --- | --- |
| `install.manifest.json` | yes | no | no projection root generated | blocker |
| `semantic_contract_registry.json` | yes | no | no projection root generated | source registry exists, but no portable copy |
| `release.manifest.json` | yes | no | no projection root generated | blocker |
| `bin/` | yes | no | no projection root generated | native binaries missing |
| `descriptors/` | yes | no | no projection root generated | blocker |
| `store/packs/` | yes | no | no projection root generated | blocker |
| `store/profiles/` | yes | no | no projection root generated | blocker |
| `store/locks/` | yes | no | no projection root generated | blocker |
| `instances/` | yes | no | no projection root generated | blocker |
| `saves/` | yes | no | no projection root generated | blocker |
| `exports/` | yes | no | no projection root generated | blocker |
| `logs/` | yes | no | no projection root generated | blocker |
| `runtime/ipc/` | yes | no | no projection root generated | blocker |
| `runtime/locks/` | yes | no | no projection root generated | blocker |
| `runtime/temp/` | yes | no | no projection root generated | blocker |
| `cache/` | yes | no | no projection root generated | blocker |
| `ops/transactions/` | yes | no | no projection root generated | blocker |
| `docs/` | yes | no | no projection root generated | blocker |
| `LICENSES/` | yes | no | no projection root generated | blocker |

## Package Smoke Result

| Surface | Result | Evidence | Notes |
| --- | --- | --- | --- |
| `.dompkg` package tool | partial | temp docs package packed with `result: ok` | proves tool path, not release payload |
| `.dompkg` verification tool | partial | temp docs package verified with `result: ok` | unsigned smoke package |
| package index | not run | help only | real run requires package directory |
| build manifest | not run | help only | real run requires package index |
| portable archive | blocked | help only | real run requires assembled artifact root |

## Blockers

- Local `cmake --preset verify` cannot configure because Visual Studio 17 2022 is missing.
- No build output exists for native product binaries.
- POST-CONVERGE-08 product boot proof is partial, not native binary proof.
- Packaging pipeline `assemble` requires a build directory containing built outputs.
- No real portable projection root was generated.
- Required portable manifests were not generated into a projection root.
- Setup Python bridge and `archive/generated/dist/bin/dom` blockers remain from POST-CONVERGE-08.

## Files Added/Changed

- Added `docs/repo/audits/POST_CONVERGE_09_PORTABLE_PROJECTION_PROOF.md`.
- Added `docs/distribution/PORTABLE_PROJECTION_SMOKE_PROOF.md`.
- Added `docs/release/PACKAGE_SMOKE_PROOF.md`.
- Added `tools/validators/check_portable_projection.py`.
- Updated distribution, packaging, component-matrix, and next-step docs.
- Updated AIDE task packet and migration inventory/move-map generated metadata.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/package/distribution/tool_pkg_pack.py ...` | pass | temporary docs `.dompkg` generated under `%TEMP%` |
| `python tools/package/distribution/tool_pkg_verify.py --pkg <temp>/smoke_docs.dompkg` | pass | temporary package verified and then removed |
| `python -m py_compile tools/validators/check_portable_projection.py` | pass | validator parses successfully |
| `python tools/validators/check_portable_projection.py --repo-root .` | pass, partial proof | blockers: missing built product binaries and no projection root |
| `python tools/validators/check_portable_projection.py --repo-root . --json` | pass, partial proof | JSON report emitted; contract/docs/tools present |
| `python tools/validators/check_portable_projection.py --repo-root . --dry-run` | pass, partial proof | dry-run sequence reported configure/build/projection blockers |
| `python tools/validators/check_portable_projection.py --repo-root . --strict` | expected fail | strict requires a proven projection root and built binaries |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | active exceptions: 32; unexcepted violations: none |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | active exceptions: 32; unexcepted violations: none |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | required logical roots/projections present |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | matrix sections/statuses/evidence valid |
| `python tools/validators/check_local_playtest_path.py --repo-root .` | pass, blocked proof | reports missing built binaries and server CLI forwarding blocker |
| `python tools/validators/check_product_boot_matrix.py --repo-root .` | pass, partial proof | reports missing built product binaries |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | build boundary checks passed |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK |
| `git diff --check` | pass | line-ending warnings only; no whitespace errors |
| `git diff --cached --check` | pass | staged whitespace check passed |

## Next Recommended Task

Targeted package/projection/setup remediation before CONTRACT-00:

- provide the Visual Studio 17 2022 verify lane or accepted CI build proof
- run configure/build/CTest and rerun product boot proof
- fix or classify setup Python bridge compatibility and the missing `archive/generated/dist/bin/dom` target
- add or prove a real portable projection assembly path that emits required manifests and roots
- rerun POST-CONVERGE-09 after a real projection root can be generated or explicitly accepted as partial
