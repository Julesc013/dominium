# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T11:14:03Z`
- completed: `2026-05-21T11:19:00Z`
- elapsed seconds: `296.553`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.187` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.075` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.714` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.666` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.085` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `11.638` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `11.654` |
| `t1.aide_test` | `T1` | `true` | `pass` | `15.724` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `15.693` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `2.105` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.172` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `2.086` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `4.759` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `4.855` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.227` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.207` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.237` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.293` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.228` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.247` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.155` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.131` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `1.333` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `3.228` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.151` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.27` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `3.831` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `3.716` |
| `t1.architecture_policy` | `T1` | `true` | `pass` | `0.206` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `81.355` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `33.0` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `46.254` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `49.065` |

## Not Run

10 command(s) were outside the selected mode.
