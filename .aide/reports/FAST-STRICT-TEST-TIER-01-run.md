# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T17:27:33Z`
- completed: `2026-05-21T17:32:44Z`
- elapsed seconds: `311.276`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.173` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.095` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.643` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.645` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.094` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `12.209` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `11.762` |
| `t1.aide_test` | `T1` | `true` | `pass` | `17.287` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `15.824` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `1.95` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.17` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `1.974` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `5.023` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `5.009` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.198` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.227` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.246` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.238` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.23` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.263` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.149` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.121` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `3.286` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `2.843` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.156` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.239` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `6.609` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `3.627` |
| `t1.architecture_policy` | `T1` | `true` | `pass` | `0.183` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `85.222` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `30.681` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `47.263` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `54.63` |

## Not Run

10 command(s) were outside the selected mode.
