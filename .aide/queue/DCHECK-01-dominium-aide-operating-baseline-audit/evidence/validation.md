# Validation Evidence

Status: needs_review

Fresh DCHECK rerun command summary: 87 PASS, 5 FAIL, 1 TIMEOUT.

Non-pass commands:

| Command | Status | Exit | Summary |
| --- | --- | --- | --- |
| aide_eval_run | TIMEOUT | None |  |
| aide_refactor_validate_map | FAIL | 1 | AIDE Lite refactor validate-map | result: FAIL | - PASS Q42 required file exists: .aide/policies/move-map.yaml | - PASS Q42 required file exists: .aide/policies/salvage-map.yaml | - PASS Q42 required file exists: .aide/p |
| aide_commit_check_range | FAIL | 1 | AIDE Lite commit range check | result: FAIL | range: HEAD~20..HEAD | commit_count: 20 | policy: .aide/policies/commit-messages.yaml | - 44bf836 FAIL chore(repo): narrow high-risk contract root exceptions |   - FAIL commi |
| aide_task_inspect | FAIL | 1 | AIDE Lite task inspect | task_id: Q17 | status: missing | classification: missing | task_yaml:  | status_yaml:  | evidence_dir: .aide/queue/Q17/evidence | evidence_files: 0 |
| aide_release_validate | FAIL | 1 | AIDE Lite release validate | result: FAIL | - PASS release model file exists: .aide/policies/release-bundle.yaml | - PASS release model file exists: .aide/policies/release-artifacts.yaml | - PASS release model file exist |
| aide_release_status | FAIL | 1 | AIDE Lite release status | bundle: missing | no_publish: true |

Key PASS commands include `doctor`, `validate`, `test`, `selftest`, `intent validate`, `repo inventory`, `quality ledger`, `roots validate`, `tools validate`, lifecycle validators, `commit check --latest`, `changelog validate`, `github validate`, and `xstack validate`.

`git diff --check` passed with CRLF normalization warnings only. `git check-ignore .aide.local/` passed.

## Final Post-Write Validation

After writing the DCHECK-01 reports and latest task packet, the required final validation set was rerun under Python 3.14.

- Final command log directory: `.aide/queue/DCHECK-01-dominium-aide-operating-baseline-audit/evidence/final-command-logs-rerun/`
- Final count: 21 PASS, 1 TIMEOUT.
- PASS: `git status --short`, `git diff --check`, `git check-ignore .aide.local/`, `doctor`, `validate`, `test`, `selftest`, `verify`, `intent validate`, `repo validate`, `quality validate`, `roots validate`, `tools validate`, `install validate`, `repair validate`, `upgrade validate`, `rollback validate`, `uninstall validate`, `commit check --latest`, `xstack validate`, and task-packet `estimate`.
- TIMEOUT: `eval run`, classified `deferred_non_blocking`.
- `verify` and `repo validate` exit 0 with WARN output; warnings are classified in `warning-disposition-audit.md`.
