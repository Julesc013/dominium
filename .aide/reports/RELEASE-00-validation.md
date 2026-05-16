# RELEASE-00 Validation

## Completed Before Full Validation Sweep

| Command | Result | Notes |
| --- | --- | --- |
| `python -m py_compile tools/release/stage_internal_pilot.py tools/validators/check_internal_pilot_release.py` | PASS | tooling compiles |
| `python tools/release/stage_internal_pilot.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --release-root .dominium.local/releases/internal-pilot-0` | PASS | staged release proof tree |
| `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0` | PASS | non-strict validation pass |
| `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --json --strict` | PASS | strict validation pass; blockers none |
| `git status --short --ignored=matching .dominium.local/releases/internal-pilot-0` | PASS | release staging is ignored |

## Full Validation Sweep

| Command | Result | Notes |
| --- | --- | --- |
| `python -m json.tool` on RELEASE-00 JSON reports and generated local manifest/provenance/validation JSON | PASS | JSON parsed |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | no hard validation failures |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validation passed |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | internal AIDE test set passed |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | internal AIDE selftest set passed |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | large inventory trace; result PASS |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | validation side-effect metadata was removed from scope before commit |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | repo intelligence validation passed |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | latest pre-commit message passed AIDE policy |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS | strict pass; expected TOML fallback warnings |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS | strict pass; expected TOML fallback warnings |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS | strict pass; expected TOML fallback warning |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS | strict pass; expected TOML fallback warning |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | build boundary checks passed |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK |
| `ctest --preset verify -N` | PASS | 493 tests discovered; CTest still prints missing-executable notices for some compiled tests |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | PASS | first run failed on missing RELEASE-00 audit status header; header was fixed and rerun passed |
| `ctest --preset verify -L smoke --output-on-failure --timeout 300` | PASS | 57/57 smoke tests passed |
| `git diff --check` | PASS | no whitespace errors |

## Not Run

- Full CTest was not run.
- Full eval was not run.
- Public release, GitHub release, tag creation, upload, installer build, and package publication were not run.
- Full `cmake --build --preset verify` was not rerun for RELEASE-00.
