Status: DERIVED
Last Reviewed: 2026-05-20
Task: FAST-STRICT-TEST-TIER-01

# Existing Proof Inventory

| Command | Purpose | Cost | Tier | Normal Gate | Notes |
| --- | --- | ---: | --- | --- | --- |
| `git diff --check` | whitespace and conflict-marker hygiene | fast | T0 | yes | required |
| built-in staged generated output check | prevent local/build/projection/release output staging | fast | T0 | yes | required |
| built-in changed JSON/JSONL parse | parse changed contract/evidence files | fast | T0 | yes | required |
| built-in changed TOML parse | parse changed TOML contracts without external deps | fast | T0 | yes | required |
| built-in forbidden active roots check | reject active `src`, `source`, `sources`, `common_source` roots | fast | T0 | yes | required |
| `py -3 .aide/scripts/aide_lite.py doctor` | AIDE installation/context health | 10.938s measured | T1 | yes | required |
| `py -3 .aide/scripts/aide_lite.py validate` | AIDE validation | 10.484s measured | T1 | yes | required |
| `py -3 .aide/scripts/aide_lite.py test` | AIDE tests | 16.813s measured | T1 | yes | required |
| `py -3 .aide/scripts/aide_lite.py selftest` | AIDE selftest | 14.203s measured | T1 | yes | required |
| `py -3 .aide/scripts/aide_lite.py tools validate` | AIDE tool registry validation | 1.859s measured | T1 | yes | required |
| `py -3 .aide/scripts/aide_lite.py roots validate` | AIDE root validation | 1.844s measured | T1 | yes | required |
| `py -3 .aide/scripts/aide_lite.py repo validate` | AIDE repo validation | 1.922s measured | T1 | yes | required |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | strict repo layout | 4.453s measured | T1 | yes | required |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | strict root allowlist | 4.328s measured | T1 | yes | required |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | distribution layout | 0.187s measured | T1 | yes | required |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | component matrix validation | 0.219s measured | T1 | yes | required |
| `python tools/validators/repo/check_no_src_source_dirs.py --repo-root . --strict` | no active source-root aliases | 0.203s measured | T1 | yes | required |
| `python tools/validators/repo/check_forbidden_root_names.py --repo-root . --strict` | forbidden root-name check | 0.235s measured | T1 | yes | required |
| `python tools/validators/repo/check_bad_root_absence.py --repo-root . --strict` | former bad-root absence | 0.203s measured | T1 | yes | required |
| `python tools/validators/repo/check_directory_naming.py --repo-root . --strict --max-findings 50` | naming classifier | 0.250s measured | T1 | yes | optional/advisory |
| `python tools/validators/testing/check_test_tiers.py --repo-root . --strict` | test-tier contract validation | 0.140s measured | T1 | yes | required |
| `python scripts/verify_docs_sanity.py --repo-root .` | docs sanity | 0.110s measured | T1 | yes | required |
| `python scripts/verify_includes_sanity.py --repo-root .` | include sanity | 1.781s measured | T1 | yes | required |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | build target boundaries | 4.688s measured | T1 | yes | required |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | UI shell purity | 0.296s measured | T1 | yes | required |
| `python scripts/verify_abi_boundaries.py --repo-root .` | ABI boundaries | 0.610s measured | T1 | yes | required |
| `python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT ...` | RepoX STRICT | 128.031s measured | T1 | yes | required, outputs redirected to `.aide/reports/**` |
| `cmake --preset verify` | configure verify preset | 30.875s measured | T2 | yes | required |
| `cmake --build --preset verify --target ALL_BUILD` | build native verify tree without broad verify target | 48.438s measured | T2 | yes | required |
| `ctest --preset verify -L smoke --output-on-failure --timeout 300` | smoke CTest | 48.265s measured | T2 | yes | required |
| `python tools/validators/check_product_boot_matrix.py ...` | product boot proof | not run here | T3 | task-dependent | release/extended only |
| `python tools/validators/check_portable_projection.py ...` | portable projection proof | not run here | T3 | task-dependent | release/extended only |
| `python tools/validators/check_internal_pilot_release.py ...` | internal pilot proof | not run here | T3 | task-dependent | release/extended only |
| focused schema/pack/content CTest | broad focused portability/content proof | known debt | T4 | no | not normal-gate green |
| public-header C89/C++98 consumer tests | public header consumer proof | known debt | T4 | no | full/release debt |
| full CTest | full certification proof | recorded prior 3227.41s | T4 | no | known full-gate debt |
