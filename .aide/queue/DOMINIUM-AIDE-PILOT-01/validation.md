# Validation

Final AIDE commands:

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS
- `py -3 .aide/scripts/aide_lite.py snapshot`: PASS, wrote `.aide/context/repo-snapshot.json`
- `py -3 .aide/scripts/aide_lite.py index`: PASS, wrote repo/test/context maps
- `py -3 .aide/scripts/aide_lite.py context`: PASS, latest context packet 1,866 chars / 467 approx tokens
- `py -3 .aide/scripts/aide_lite.py pack --task "Audit Dominium current repo state and produce the next compact doctrine-aware implementation task"`: PASS, latest task packet 4,347 chars / 1,087 approx tokens
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`: PASS
- `py -3 .aide/scripts/aide_lite.py route explain`: PASS, advisory only, no provider/model/network calls
- `py -3 .aide/scripts/aide_lite.py cache report`: PASS
- `py -3 .aide/scripts/aide_lite.py verify --review-packet "" --write-report .aide/verification/latest-verification-report.md`: WARN, no errors
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS, latest review packet 5,125 chars / 1,282 approx tokens
- `py -3 .aide/scripts/aide_lite.py ledger scan`: PASS, one near-budget warning for cache metadata
- `py -3 .aide/scripts/aide_lite.py ledger report`: PASS
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 6/6 golden tasks
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS
- `py -3 .aide/scripts/aide_lite.py test`: PASS

Other checks:

- `git check-ignore .aide.local/`: PASS, `.aide.local/` is ignored
- `git diff --check`: PASS, no whitespace errors; Git emitted line-ending
  normalization warnings only
- generated JSON parse check: PASS for snapshot, repo map, test map, context
  index, cache keys, route decision, and golden-task report
- targeted secret scan: inspected matches were policy/example/test references
  and task/token words; no provider keys, raw credentials, or private keys found

Observed recoveries:

- Initial source `import-pack --dry-run` passed with 127 operations and 0 conflicts, but full command import was too broad for Q23 allowed target paths.
- First snapshot attempt timed out before the ignore policy pruned exact directory names; the policy was narrowed and snapshot then passed.
- First verifier failed until `.aide.local.example/` example files, adapter guidance, verification report sequencing, and audit ignore scope were corrected.
- Optional selftest/test initially failed because the temporary selftest repo wrote
  YAML-like placeholders into `core/gateway/**` and `core/providers/**` when
  those source modules were intentionally not imported. The imported script now
  writes no-call Python stubs inside the temporary selftest repo only.

Dominium product FAST validation:

- Not rerun during Q23 because `data/audit/validation_report_FAST.json` and
  `docs/audit/VALIDATION_REPORT_FAST.md` were already modified before Q23 and
  are preserved as user/pre-existing work.
