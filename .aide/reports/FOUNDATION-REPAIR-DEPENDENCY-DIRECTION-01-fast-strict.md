# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T09:44:13Z`
- completed: `2026-05-21T09:49:25Z`
- elapsed seconds: `312.147`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.127` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.085` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.641` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.643` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.094` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `12.489` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `11.363` |
| `t1.aide_test` | `T1` | `true` | `pass` | `18.77` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `15.518` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `2.039` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.036` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `2.123` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `4.736` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `4.614` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.262` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.215` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.238` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.241` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.224` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.277` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.167` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.158` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `1.269` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `3.007` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.145` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.257` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `3.941` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `3.649` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `91.518` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `38.377` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `43.072` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `49.845` |

## Not Run

10 command(s) were outside the selected mode.
