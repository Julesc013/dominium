# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T16:44:27Z`
- completed: `2026-05-21T16:51:49Z`
- elapsed seconds: `441.875`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.235` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.172` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.875` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.687` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.11` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `12.156` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `11.109` |
| `t1.aide_test` | `T1` | `true` | `pass` | `20.203` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `23.719` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `3.5` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.234` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `2.688` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `5.937` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `5.907` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.218` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.235` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.265` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.344` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.25` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.328` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.188` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.109` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `2.047` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `7.047` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.219` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.375` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `6.25` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `5.672` |
| `t1.architecture_policy` | `T1` | `true` | `pass` | `0.234` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `155.125` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `51.484` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `61.797` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `60.156` |

## Not Run

10 command(s) were outside the selected mode.
