# AIDE Command Surface Audit

Status: needs_review

| Family | Available | Command Run | Result | Generated Outputs | No-Apply Safe | Warnings |
| --- | --- | --- | --- | --- | --- | --- |
| core | yes | doctor/validate/test/selftest/verify/review-pack | PASS except verify/review-pack WARN exit 0 | context/review packets | yes | missing optional controller refs |
| intent | yes | validate/compile/status | PASS | .aide/intake/latest-* | yes | compiled prompt safe_to_execute=false |
| repo | yes | inventory/validate/status | PASS/WARN | .aide/repo/* | yes | 1669 unknown classifications |
| quality | yes | ledger/validate/status | PASS | .aide/reports/file-quality-* | yes | warn-level quality records are advisory |
| refactor | yes | status/validate/dry-run/map-status/validate-map | PASS plus validate-map FAIL | .aide/refactors/* | yes | move/salvage/path-alias maps absent |
| roots | yes | inventory/classify/plan/validate/status | PASS | .aide/roots/* | yes | 44 roots, high review posture |
| tools | yes | inventory/classify/wrap-plan/validate/status/capabilities | PASS | .aide/tools/* | yes | 3000 tools, 858 unknown, execution false |
| xstack | yes | status/wrap-plan/validate | PASS | .aide/tools/xstack-* | yes | no-apply registry only |
| install | yes | observe/plan/dry-run/validate/status | PASS | .aide/install/* | yes | 267 conflicts preserved/skipped; no writes |
| repair | yes | observe/diagnose/plan/dry-run/validate/status | PASS | .aide/repair/* | yes | 5 issues, 4 blockers, no apply |
| upgrade | yes | observe/compare/plan/dry-run/validate/status | PASS | .aide/upgrade/* | yes | source pack unavailable in target observation; no apply |
| rollback | yes | observe/plan/dry-run/validate/status | PASS | .aide/rollback/* | yes | no restores/removals |
| uninstall | yes | observe/plan/dry-run/validate/status | PASS | .aide/uninstall/* | yes | future candidates only; no deletion |
| git | yes | detect/doctor/status/policy/plan/dry-runs | PASS with blocked plans | .aide/git/* | dry-run only | dirty canonical branch blocks branch-sensitive work |
| changelog | yes | preview/validate/status | PASS | .aide/changelog/* | yes | historical malformed count advisory |
| release/github | yes | release validate/status; github validate/advisory | release FAIL, github PASS | .aide/release, .aide/github | report-only | target release bundle missing; no GitHub API |

Fresh rerun counts: 87 PASS, 5 FAIL, 1 TIMEOUT.
