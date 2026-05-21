# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T10:11:42Z`
- completed: `2026-05-21T10:16:14Z`
- elapsed seconds: `272.607`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.1` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.062` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.62` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.545` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.087` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `10.347` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `10.012` |
| `t1.aide_test` | `T1` | `true` | `pass` | `14.086` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `13.856` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `1.864` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `1.965` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `1.871` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `4.302` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `4.253` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.186` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.187` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.207` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.216` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.195` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.221` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.139` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.117` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `1.14` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `2.691` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.16` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.243` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `3.33` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `3.573` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `76.447` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `28.976` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `41.625` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `48.98` |

## Not Run

10 command(s) were outside the selected mode.
