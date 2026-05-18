Status: DERIVED
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-01

# MOVE-ROUTER-01 Exception Actions

| Metric | Count |
| --- | ---: |
| `bad_roots` | 24 |
| `roots_empty` | 24 |
| `exceptions_retired` | 23 |
| `exceptions_already_retired` | 1 |
| `exceptions_remaining` | 0 |

## Retired Or Empty

| Root | Exception | Action |
| --- | --- | --- |
| `governance` | `governance_root` | `retired` |
| `ide` | `ide_root` | `already_retired` |
| `meta` | `meta_root` | `retired` |
| `performance` | `performance_root` | `retired` |
| `validation` | `validation_root` | `retired` |
| `bundles` | `bundles_root` | `retired` |
| `compat` | `compat_root` | `retired` |
| `control` | `control_root` | `retired` |
| `core` | `core_root` | `retired` |
| `data` | `data_root` | `retired` |
| `lib` | `lib_root` | `retired` |
| `libs` | `libs_root` | `retired` |
| `locks` | `locks_root` | `retired` |
| `modding` | `modding_root` | `retired` |
| `models` | `models_root` | `retired` |
| `net` | `net_root` | `retired` |
| `packs` | `packs_root` | `retired` |
| `profiles` | `profiles_root` | `retired` |
| `repo` | `repo_root` | `retired` |
| `safety` | `safety_root` | `retired` |
| `security` | `security_root` | `retired` |
| `specs` | `specs_root` | `retired` |
| `templates` | `templates_root` | `retired` |
| `updates` | `updates_root` | `retired` |

## Remaining

| Root | Exception | Count | Action |
| --- | --- | ---: | --- |
| none |  | 0 |  |

## Ledger Form

Retired entries were moved from `[exceptions.*]` to `[retired_exceptions.*]`
because the existing strict layout validators treat inactive entries inside the
active exception namespace as malformed.

Empty former-root directory shells left after `git mv` were removed only after
confirming they had zero tracked files. Roots containing only untracked
`__pycache__/*.pyc` generated leftovers were cleaned before root-presence
validation.
