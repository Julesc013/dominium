# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-20T14:05:40Z`
- completed: `2026-05-20T14:11:17Z`
- elapsed seconds: `337.406`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.125` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.046` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.625` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.579` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.078` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `11.156` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `12.656` |
| `t1.aide_test` | `T1` | `true` | `pass` | `18.36` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `16.75` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `2.203` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.235` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `3.047` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `5.828` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `5.015` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.203` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.204` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.234` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.234` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.297` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.313` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.14` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.11` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `1.734` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `4.578` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.156` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.344` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `118.781` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `29.313` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `51.234` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `50.813` |

## Not Run

10 command(s) were outside the selected mode.
