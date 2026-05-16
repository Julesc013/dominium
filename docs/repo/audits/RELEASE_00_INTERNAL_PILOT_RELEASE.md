Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# RELEASE-00 Internal Pilot Release 0

## Status

- Task ID: RELEASE-00
- Result: PASS_WITH_WARNINGS
- Branch: main
- HEAD: c7d0a1a1b4d92a127bfb58cb740d4d177131f213
- origin/main: 7b9068bd421d1fa4ae872fdda598d412313548fe
- Worktree before: clean except ignored `.aide.local/` and `.dominium.local/`
- Worktree after: scoped tracked proof/tooling changes plus ignored generated release staging

## Scope

This task staged an internal pilot release proof only. It did not create a public release, GitHub release, tag, upload, installer, package publication, feature work, source-root move, rename, delete, active alias, move map, or salvage map.

## Readiness Inputs

POST-CONVERGE closeout evidence records focused RepoX clean, native product command smoke passing, and portable projection proof locally proven.

The accepted portable projection input is:

```text
.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium
```

## Release Authority

| Authority | Use |
| --- | --- |
| `contracts/distribution/layout.contract.toml` | portable projection roots/manifests and generated output policy |
| `contracts/release/component_matrix.contract.toml` | product/component release scope |
| `contracts/build/artifacts.toml` | generated artifact policy |
| `docs/release/PORTABLE_PROJECTION_PROOF.md` | projection proof input |
| `docs/release/PRODUCT_BOOT_PROOF.md` | command-surface proof input |
| `docs/release/NATIVE_BINARY_PROOF.md` | native binary proof input |
| `.aide/reports/latest-warning-disposition.md` | internal warning ledger input |

## Release Staging Root

Generated local ignored root:

```text
.dominium.local/releases/internal-pilot-0
```

This root is ignored by git and was not staged for commit.

## Release Contents

| Item | Required | Present | Notes |
| --- | --- | --- | --- |
| Projection tree | yes | yes | copied under `projection/` |
| Internal pilot manifest | yes | yes | `manifest/internal_pilot_release.manifest.json` |
| Provenance | yes | yes | `manifest/provenance.json` |
| Checksums | yes | yes | `manifest/checksums.sha256`, 4718 entries |
| Install manifest | yes | yes | `projection/install.manifest.json` |
| Release manifest | yes | yes | `projection/release.manifest.json` |
| Semantic contract registry | yes | yes | `projection/semantic_contract_registry.json` |
| Native binaries | yes | yes | setup, launcher, client, server, tools |
| Proof reports | yes | yes | native, boot, projection, warning ledger, validation |
| Runbook and rollback notes | yes | yes | local operator docs |

## Manifest and Checksum Proof

The local stager wrote `manifest/internal_pilot_release.manifest.json`, `manifest/provenance.json`, and `manifest/checksums.sha256`. The read-only validator parsed the JSON files, verified 4718 checksum entries, found no checksum mismatches, and found no absolute host paths in public/projection manifests.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `python -m py_compile tools/release/stage_internal_pilot.py tools/validators/check_internal_pilot_release.py` | PASS | tooling syntax |
| `python tools/release/stage_internal_pilot.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --release-root .dominium.local/releases/internal-pilot-0` | PASS | staged local proof |
| `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0` | PASS | validator pass |
| `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --json --strict` | PASS | strict validator pass |
| `git status --short --ignored=matching .dominium.local/releases/internal-pilot-0` | PASS | generated release root ignored |
| `ctest --preset verify -N` | PASS | 493 tests discovered |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | PASS | focused RepoX rerun passed after adding this audit status header |
| `ctest --preset verify -L smoke --output-on-failure --timeout 300` | PASS | 57/57 smoke tests passed |
| AIDE doctor/validate/test/selftest/tools/roots/repo validators | PASS | AIDE checks passed |
| strict repo/root/distribution/component validators | PASS | strict validators passed |
| docs/build/UI/ABI checks | PASS | supplemental checks passed |
| `git diff --check` | PASS | no whitespace errors |

Full validation sweep results are recorded in `.aide/reports/RELEASE-00-validation.md`.

## Blockers

No RELEASE-00 blocker remains.

## Readiness for Operating-Environment MVP

Ready: yes_with_warnings.

The internal pilot proof demonstrates that current build, product boot, portable projection, manifest, checksum, provenance, warning, runbook, and rollback evidence can be collected into one self-describing local artifact. DOE-00 may proceed. Full promotion CTest, public release, installer, tag, upload, and package publication remain future gates.
