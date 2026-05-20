# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-20T12:48:19Z`
- completed: `2026-05-20T12:53:52Z`
- elapsed seconds: `332.828`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.109` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.063` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.594` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.609` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.078` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `10.938` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `10.484` |
| `t1.aide_test` | `T1` | `true` | `pass` | `16.813` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `14.203` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `1.859` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `1.844` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `1.922` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `4.453` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `4.328` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.187` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.219` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.203` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.235` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.203` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.25` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.14` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.11` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `1.781` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `4.688` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.296` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.61` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `128.031` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `30.875` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `48.438` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `48.265` |

## Not Run

10 command(s) were outside the selected mode.
