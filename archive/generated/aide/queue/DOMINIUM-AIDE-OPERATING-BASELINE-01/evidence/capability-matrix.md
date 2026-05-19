# Capability Matrix

Status: PARTIAL_BASELINE_NEEDS_REPAIR

Interpreter used for reliable AIDE command execution:

`C:\Users\Jules\AppData\Local\Python\pythoncore-3.14-64\python.exe`

| Capability | Command Available | Result | Artifact Output | Warnings | Blocking? | Evidence Refs |
|---|---|---|---|---|---|---|
| doctor | yes | PASS | status output | controller/report-only warnings | no | command log, `.aide/scripts/aide_lite.py` |
| validate | yes | PASS | validation output | review packet missing generated controller refs | no | command log |
| test | yes | PASS | test output | requires Python 3.14 in this sandbox | no | final rerun, `.aide/scripts/aide_lite.py` |
| selftest | yes | PASS | selftest output | requires Python 3.14 in this sandbox | no | final rerun, `.aide/scripts/aide_lite.py` |
| eval | yes | WARN/TIMEOUT | prior eval reports | full eval timeout-prone | no | Q50-Q53 logs |
| verify | yes | WARN exit 0 | `.aide/context/latest-review-packet.md` | diff-scope and generated controller refs while dirty | no | command log |
| intent | yes | PASS | `.aide/intake/latest-intent-packet.*` | generated from bounded prompt | no | `.aide/intake/` |
| repo intelligence | yes | PASS | `.aide/repo/file-inventory.json`, maps, markdown | 1669 unknown file classifications | no | `.aide/repo/` |
| quality ledger | yes | PASS | `.aide/reports/file-quality-ledger.json` | unknowns inherited from repo index | no | `.aide/reports/file-quality-*` |
| refactor control | yes | PASS | validation output | no apply | no | command log |
| root recycling | yes | PASS | `.aide/roots/latest-root-*`, Dominium Q52 outputs | 43 high-risk roots; Q52 uncommitted | no for analysis, yes for durability | `.aide/roots/` |
| tool absorption | yes | PASS | `.aide/tools/latest-tool-*`, Dominium Q51 outputs | 854 unknown tool candidates | no | `.aide/tools/` |
| XStack integration | yes | PASS | `.aide/tools/xstack-*`, `.aide/reports/dominium-xstack-aide-integration.md` | legacy execution disabled pending per-wrapper proof | no | `.aide/tools/xstack-wrapper-registry.json` |
| install planning | yes | PASS | `.aide/install/latest-*` | observe only | no | `.aide/install/` |
| repair planning | yes | PASS | `.aide/repair/latest-*` | observe only | no | `.aide/repair/` |
| upgrade planning | yes | PASS | `.aide/upgrade/latest-*` | source-state warnings from Q50 remain classified | no | `.aide/upgrade/` |
| rollback/uninstall planning | yes | PASS | `.aide/rollback/latest-*`, `.aide/uninstall/latest-*` | plan only | no | `.aide/rollback/`, `.aide/uninstall/` |
| git policy | yes | PASS | `.aide/git/latest-*` | commit write blocked by sandbox, policy itself works | yes for commit durability | `.aide/git/` |
| commit check | yes | PASS | latest commit check | latest committed Q51 passes; Q52/Q53 uncommitted | yes for baseline finalization | command log |
| changelog preview | yes | PASS | `.aide/changelog/*` | generated preview only | no | `.aide/changelog/` |
| task packet generation | yes | PASS | `.aide/context/latest-task-packet.md` | generated for Q53R repair before Q54 | no | `.aide/context/latest-task-packet.md` |

## Counts

- Pass count: 20 capability rows.
- Warning count: 8 rows with non-blocking warnings.
- Blocking count: 2 durability rows affected by git write/commit finalization.
- Unsupported count: 0 AIDE capabilities; environment has an unsupported/default Python 3.8 path.
