# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T18:00:34Z`
- completed: `2026-05-21T18:05:17Z`
- elapsed seconds: `282.676`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.144` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.066` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.599` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.616` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.088` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `11.226` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `10.482` |
| `t1.aide_test` | `T1` | `true` | `pass` | `14.321` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `14.227` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `1.946` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.016` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `1.977` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `4.981` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `4.894` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.201` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.212` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.264` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.225` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.215` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.26` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.16` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.115` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `1.209` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `2.847` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.145` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.281` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `3.633` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `3.41` |
| `t1.architecture_policy` | `T1` | `true` | `pass` | `0.196` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `73.75` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `30.88` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `47.357` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `49.727` |

## Not Run

10 command(s) were outside the selected mode.
