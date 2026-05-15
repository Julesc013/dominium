# AIDE-STRUCTURE-02 Wrapper Execution

## Status

- Result: PASS_WITH_WARNINGS
- Selected family: AIDE-native validation wrappers
- Selected commands: `aide.tools`, `aide.roots`, `aide.repo`
- Unknown tool execution: false
- Moves/deletes/renames: false

## Commands Listed

`python tools/aide/run_task.py --repo-root . list`

Result: PASS. Registered commands:

- `aide.repo`
- `aide.roots`
- `aide.tools`

## Descriptions Checked

`describe` succeeded for all selected commands. Each command reports:

- `execution_allowed: True`
- `apply_allowed: False`
- `network_allowed: False`
- `writes_allowed: False`
- `timeout_seconds: 60`

## Dry-Runs

| Command | Result | Underlying command |
| --- | --- | --- |
| `aide.tools` | PASS | `py -3 .aide/scripts/aide_lite.py tools validate` |
| `aide.roots` | PASS | `py -3 .aide/scripts/aide_lite.py roots validate` |
| `aide.repo` | PASS | `py -3 .aide/scripts/aide_lite.py repo validate` |

Dry-run mode printed the underlying command and did not execute it.

## Executions

Execution was allowed only for the selected AIDE-native validation wrappers.

| Command | Result | Notes |
| --- | --- | --- |
| `aide.tools` | PASS | AIDE Lite tools validate passed; provider/model calls none; network calls none; unknown tool execution false; tool deletion/rename/migration false. |
| `aide.roots` | PASS | AIDE Lite roots validate passed; provider/model calls none; network calls none; file moves false; file deletes false; reference rewrites false. |
| `aide.repo` | PASS_WITH_WARNINGS | AIDE Lite repo validate exited 0 with known warning: unknown file classifications: 1669; provider/model calls none; network calls none. |

## Warnings

- `aide.repo` keeps the existing known warning for unknown file
  classifications.
- High-risk and unknown tools remain preserved but execution-disabled.

## Blockers

- Broad XStack/AuditX/RepoX/TestX commands are not wrapped or executed here.
- Full eval, full CTest, build, package, release, and GitHub operations remain
  deferred.
- Strict legacy repo layout validators may still be blocked locally by ignored
  generated `build/` and `out/` roots.
