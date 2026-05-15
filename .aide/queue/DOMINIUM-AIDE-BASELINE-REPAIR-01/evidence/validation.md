# Validation

Interpreter:

`C:\Users\Jules\AppData\Local\Python\pythoncore-3.14-64\python.exe`

## Commands

| Command | Result | Notes |
|---|---|---|
| `python -m py_compile .aide/scripts/aide_lite.py` | PASS | Syntax check passed. |
| `aide_lite.py xstack wrap-plan` | PASS | Generated no-apply XStack contract and registry. |
| `aide_lite.py xstack validate` | PASS | XStack/AuditX/RepoX/TestX registry validated with execution disabled. |
| `aide_lite.py test` | PASS | Review-packet temp-repo leakage repaired. |
| `aide_lite.py selftest` | PASS | Review-packet temp-repo leakage repaired. |
| `aide_lite.py tools validate` | PASS | Tool inventory and wrapper outputs remain no-apply. |
| `aide_lite.py doctor` | PASS | No hard validation failures detected. |
| `aide_lite.py validate` | PASS | Includes XStack contract/registry checks; review-packet missing controller refs remain WARN only. |
| `aide_lite.py verify` | WARN | No errors; warnings are dirty-scope and missing optional controller report refs. |
| `aide_lite.py repo validate` | WARN | Unknown file classifications remain deferred. |
| `aide_lite.py roots validate` | PASS | No root move/delete/rewrite authorization. |
| `aide_lite.py quality validate` | PASS | Quality outputs remain advisory. |
| `aide_lite.py intent validate` | PASS | Prompt compiler surfaces are valid. |
| `aide_lite.py install validate` | PASS | No-apply install planning remains valid. |
| `aide_lite.py repair validate` | PASS | No-apply repair planning remains valid. |
| `aide_lite.py upgrade validate` | PASS | No-apply upgrade planning remains valid. |
| `aide_lite.py rollback validate` | PASS | No-apply rollback planning remains valid. |
| `aide_lite.py uninstall validate` | PASS | No-apply uninstall planning remains valid. |
| `aide_lite.py pack --task "DCHECK-01 Dominium AIDE Operating Baseline Audit Rerun"` | PASS | Succeeded when run alone; one parallel run failed from concurrent access and was rerun successfully. |
| `aide_lite.py estimate --file .aide/context/latest-task-packet.md` | PASS | Latest task packet is within budget at 1043 approximate tokens. |
| `aide_lite.py review-pack` | PASS/WARN | Review packet regenerated; verifier result is WARN, not FAIL. |
| `git diff --check` | PASS | Whitespace check passed; Git reported line-ending normalization warnings only. |
| `git check-ignore .aide.local/` | PASS | `.aide.local/` is ignored. |
| high-confidence secret scan | PASS | Matches are policy/test/evidence text only; no live credential value found. |
| `git add .aide` | FAIL | Filesystem denied `.git/index.lock`; no commit could be created in this sandbox. |

## Remaining Validation Warnings

- `verify` warns because the active latest task packet allows a narrow DCHECK rerun scope while the worktree still contains many generated `.aide/**` outputs from Q52/Q53/DCHECK/Q53R.
- `validate` warns that optional `.aide/controller/latest-*` report references in the review packet are absent.
- `repo validate` warns about unknown file classifications, deferred to future classifier work.
- Git commit finalization remains blocked by `.git/index.lock` permission.
