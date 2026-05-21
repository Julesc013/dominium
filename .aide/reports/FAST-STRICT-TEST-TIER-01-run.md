# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T08:23:47Z`
- completed: `2026-05-21T08:31:06Z`
- elapsed seconds: `439.232`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.38` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.077` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.802` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.731` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.085` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `23.387` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `10.703` |
| `t1.aide_test` | `T1` | `true` | `pass` | `18.524` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `15.258` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `2.163` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.097` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `2.185` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `4.81` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `4.604` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.286` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.343` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.282` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.277` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.28` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.275` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.191` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.218` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `11.058` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `11.111` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.184` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.802` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `6.302` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `5.452` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `168.523` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `41.184` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `54.782` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `51.869` |

## Not Run

10 command(s) were outside the selected mode.
