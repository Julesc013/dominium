# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T15:14:55Z`
- completed: `2026-05-21T15:21:05Z`
- elapsed seconds: `369.954`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.219` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.11` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.734` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.703` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.125` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `13.469` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `11.453` |
| `t1.aide_test` | `T1` | `true` | `pass` | `16.531` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `16.344` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `2.234` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.172` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `2.281` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `5.766` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `5.844` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.25` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.234` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.25` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.313` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.25` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.343` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.172` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.141` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `2.422` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `5.265` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.188` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.344` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `5.218` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `4.657` |
| `t1.architecture_policy` | `T1` | `true` | `pass` | `0.218` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `136.829` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `33.843` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `47.735` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `53.297` |

## Not Run

10 command(s) were outside the selected mode.
