# Fast Strict Test Tier Result

- status: `FAIL`
- mode: `tier`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-23T13:51:10Z`
- completed: `2026-05-23T13:55:05Z`
- elapsed seconds: `235.0`
- selected tiers: `T1`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t1.aide_doctor` | `T1` | `true` | `pass` | `13.703` |
| `t1.aide_validate` | `T1` | `true` | `pass` | `13.875` |
| `t1.aide_test` | `T1` | `true` | `pass` | `21.39` |
| `t1.aide_selftest` | `T1` | `true` | `pass` | `19.157` |
| `t1.aide_tools_validate` | `T1` | `true` | `pass` | `2.25` |
| `t1.aide_roots_validate` | `T1` | `true` | `pass` | `2.328` |
| `t1.aide_repo_validate` | `T1` | `true` | `pass` | `2.625` |
| `t1.repo_layout_strict` | `T1` | `true` | `pass` | `5.0` |
| `t1.root_allowlist_strict` | `T1` | `true` | `pass` | `5.328` |
| `t1.distribution_layout_strict` | `T1` | `true` | `pass` | `0.234` |
| `t1.component_matrices_strict` | `T1` | `true` | `pass` | `0.235` |
| `t1.no_src_source_dirs` | `T1` | `true` | `pass` | `0.312` |
| `t1.forbidden_root_names` | `T1` | `true` | `pass` | `0.281` |
| `t1.bad_root_absence` | `T1` | `true` | `pass` | `0.25` |
| `t1.directory_naming_advisory` | `T1` | `false` | `pass` | `0.344` |
| `t1.test_tiers_contract` | `T1` | `true` | `pass` | `0.172` |
| `t1.presentation_contract` | `T1` | `true` | `pass` | `0.188` |
| `t1.docs_sanity` | `T1` | `true` | `pass` | `0.156` |
| `t1.include_sanity` | `T1` | `true` | `pass` | `1.719` |
| `t1.build_target_boundaries` | `T1` | `true` | `pass` | `4.531` |
| `t1.ui_shell_purity` | `T1` | `true` | `pass` | `0.14` |
| `t1.abi_boundaries` | `T1` | `true` | `pass` | `0.344` |
| `t1.language_baseline` | `T1` | `true` | `pass` | `4.563` |
| `t1.cpp17_forbidden_library_use` | `T1` | `true` | `pass` | `4.328` |
| `t1.architecture_policy` | `T1` | `true` | `pass` | `0.219` |
| `t1.repox_strict` | `T1` | `true` | `fail` | `131.328` |

## Findings

### t1.repox_strict

- status: `fail`
- returncode: `1`

```text
WARN: INV-AUDITX-OUTPUT-STALE: audit outputs may be stale (74 commits since docs/archive/audit/auditx/FINDINGS.json)
INV-DOC-STATUS-HEADER: missing status header: docs/repo/audits/CANON_STRUCTURE_ACTUAL_FINAL_CLEANUP_01.md
INV-DOC-STATUS-HEADER: missing status header: docs/repo/audits/PRESENTATION_CONTRACT_01.md
```


## Not Run

18 command(s) were outside the selected mode.
