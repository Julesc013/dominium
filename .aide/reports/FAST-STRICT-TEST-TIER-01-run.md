# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-23T14:02:10Z`
- completed: `2026-05-23T14:08:31Z`
- elapsed seconds: `381.406`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.172` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.093` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.75` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.75` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.141` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `13.313` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `12.906` |
| `t1.aide_test` | `T1` | `true` | `pass` | `19.203` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `18.953` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `2.344` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.282` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `2.187` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `5.328` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `5.344` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.234` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.235` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.297` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.312` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.266` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.359` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.219` |
| `t1.presentation_contract` | `T1` | `true` | `pass` | `0.172` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.125` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `1.672` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `4.828` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.14` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.344` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `4.828` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `4.532` |
| `t1.architecture_policy` | `T1` | `true` | `pass` | `0.218` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `123.219` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `45.078` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `55.578` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `54.953` |

## Not Run

10 command(s) were outside the selected mode.
