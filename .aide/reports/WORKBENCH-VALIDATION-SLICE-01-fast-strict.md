# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T14:58:21Z`
- completed: `2026-05-21T15:03:54Z`
- elapsed seconds: `332.344`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `1.562` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.266` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `2.109` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.766` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.109` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `13.063` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `12.64` |
| `t1.aide_test` | `T1` | `true` | `pass` | `16.109` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `16.172` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `2.203` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.157` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `2.015` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `5.469` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `5.328` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.203` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.203` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.266` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.266` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.218` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.282` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.156` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.125` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `2.031` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `5.094` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.141` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.312` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `6.141` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `4.562` |
| `t1.architecture_policy` | `T1` | `true` | `pass` | `0.188` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `108.797` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `30.937` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `43.188` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `49.25` |

## Not Run

10 command(s) were outside the selected mode.
