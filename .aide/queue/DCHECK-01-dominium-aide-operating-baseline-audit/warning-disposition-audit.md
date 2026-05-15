# Warning Disposition Audit

Status: needs_review

| Source | Warning | Classification | Blocking? | Assigned To |
| --- | --- | --- | --- | --- |
| Git/worktree | Q52/Q53/Q53R/generated AIDE evidence remains uncommitted in the worktree | assigned_next | yes for durable baseline | DOMINIUM-AIDE-COMMIT-FINALIZATION-01 |
| AIDE script | Current PASS results depend on uncommitted `.aide/scripts/aide_lite.py` Q53R repair | blocking | yes for durable baseline | DOMINIUM-AIDE-COMMIT-FINALIZATION-01 |
| AIDE eval | `eval run` timed out at 180 seconds | deferred_non_blocking | no | future eval-scope/performance task |
| Refactor maps | move/salvage/path-alias/reference-rewrite maps are missing; map validation fails | deferred_non_blocking | no | future map-planning task |
| Commit range | `commit check --range HEAD~20..HEAD` fails on historical commits outside current audit | expected_legacy_history | no | none |
| Task inspect | default task inspect targets missing legacy Q17 surfaces | harmless | no | none |
| Release command | target-local release validate/status fail because Dominium has no local release bundle configured | deferred_non_blocking | no | future release-pack task if needed |
| Verify/review-pack | verify/review-pack return WARN due optional missing controller report refs and dirty generated scope | expected_generated_state | no | future controller evidence task |
| Repo intelligence | repo validate reports 1669 unknown file classifications | deferred_non_blocking | no | future classifier improvement |
| Tool absorption | tools status reports 858 unknown and 171 high-risk tool candidates; execution remains disabled | deferred_non_blocking | no | DOM-AIDE-02 wrapper planning |
| Root recycling | roots status reports high-risk/mixed roots; Q52 pilot was classification-only | deferred_non_blocking | no | future root pilot waves |
| Git policy | git dry-run plan/sync/land/promote are blocked on dirty canonical branch | expected_target_specific | no | commit finalization before branch-sensitive work |
| Line endings | git diff --check emits CRLF normalization warnings only | harmless | no | none |
| Eureka read-only check | Sibling Eureka already has Q54 preflight evidence and dirty state; DCHECK did not mutate it | expected_target_specific | no | Eureka queue owner |

Counts: harmless=2, expected_target_specific=2, expected_generated_state=1, expected_legacy_history=1, deferred_non_blocking=6, assigned_next=1, blocking=1, unknown_needs_review=0.
