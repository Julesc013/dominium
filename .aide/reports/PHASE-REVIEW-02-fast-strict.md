# Fast Strict Test Tier Result

- status: `PASS`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T18:17:09Z`
- completed: `2026-05-21T18:21:47Z`
- elapsed seconds: `277.663`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.124` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.079` |
| `t0.changed_json_parse` | `T0` | `true` | `pass` | `0.597` |
| `t0.changed_toml_parse` | `T0` | `true` | `pass` | `0.59` |
| `t0.forbidden_active_roots` | `T0` | `true` | `pass` | `0.087` |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `11.349` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `11.003` |
| `t1.aide_test` | `T1` | `true` | `pass` | `14.588` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `14.105` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `1.917` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `1.824` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `1.931` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `5.026` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `4.857` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.201` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.217` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.245` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.308` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.243` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.232` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.147` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.118` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `1.171` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `2.889` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.143` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.256` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `3.533` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `3.504` |
| `t1.architecture_policy` | `T1` | `true` | `pass` | `0.191` |
| `t1.repox_strict` | `T1` | `true` | `pass` | `76.466` |
| `t2.cmake_configure_verify` | `T2` | `true` | `pass` | `29.53` |
| `t2.cmake_build_all_build` | `T2` | `true` | `pass` | `42.202` |
| `t2.ctest_smoke` | `T2` | `true` | `pass` | `47.984` |

## Not Run

10 command(s) were outside the selected mode.
