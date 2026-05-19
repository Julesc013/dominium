# Warning Disposition

Status: needs_review

| Source | Warning Summary | Classification | Owner / Future Task | Blocking? |
|---|---|---|---|---|
| Git environment | Git cannot create `.git/index.lock`; Q52/Q53 cannot be committed in this sandbox | blocking | operator / `Q53 Dominium Baseline Commit Finalization` | yes |
| Q52 state | Q52 evidence exists but remains uncommitted | assigned_next | commit-finalization repair | yes for durable baseline |
| Q53 state | Q53 evidence will remain uncommitted if git write permission stays blocked | assigned_next | commit-finalization repair | yes for durable baseline |
| AIDE test/selftest | Earlier stale failure evidence is superseded; both pass under Python 3.14 | harmless | none | no |
| AIDE eval | Full `eval run` is timeout-prone | deferred_non_blocking | future eval-scope/performance task | no |
| AIDE verify | Missing generated controller refs in review packet | deferred_non_blocking | future controller outcome generation task | no |
| AIDE verify | Diff-scope warnings while Q52/Q53 files are dirty | expected_target_specific | resolves after commit/finalization | no |
| Repo intelligence | 1669 unknown file classifications | deferred_non_blocking | future repo classifier improvement | no |
| Tool absorption | 854 unknown tool candidates and 171 high-risk candidates | deferred_non_blocking | future Q55/Q-tool wrapper tasks | no |
| XStack integration | AIDE now has no-apply XStack registry/contract commands, but legacy command execution remains disabled | deferred_non_blocking | future Dominium wrapper task | no |
| Root recycling | 43 high-risk roots and unknown owners | deferred_non_blocking | future root pilots after Q53 | no |
| Q50 source bundle | Missing optional source-pack files noted in Q50 | deferred_non_blocking | future AIDE pack repair in AIDE repo | no |
| Python launcher | `py -3` inaccessible in current sandbox | expected_target_specific | environment/operator | no if Python 3.14 path is used |
| Default Python | `python` is Python 3.8 and fails current AIDE write helpers | expected_target_specific | environment/operator | no if Python 3.14 path is used |
| Shell profile | oh-my-posh init writes outside sandbox and prints access-denied noise | harmless | environment/operator | no |

No warning is unclassified.
