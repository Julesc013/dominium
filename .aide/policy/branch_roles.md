Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-WORKFLOW-LAW-01
Stability: provisional
Binding Sources: `.aide/policies/branch-roles.yaml`, `.aide/policies/git-workflow.yaml`, `.aide/policies/promotion-rules.yaml`

# AIDE Branch Roles

## Role Table

| Role | Purpose | Allowed Contents | Allowed Warnings | Writers | Validation Before Merge | Promotion Eligibility | Forbidden Uses |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `origin/main` | Remote canonical baseline and ancestry reference. | Reviewed checkpoint, release, or hotfix truth. | Only checkpoint-accepted warnings with evidence. | Humans or reviewed automation only. | Main promotion gate, checkpoint evidence, contract impact, warning disposition. | Already canonical; may seed task/checkpoint branches. | Raw task output, partial work, unresolved blockers, force-push, hidden generated drift. |
| `origin/dev` | Remote shared integration baseline when configured. | Integrated task/repair work that passed dev policy. | Known bounded warnings recorded in warning ledger/status. | Coordinator or reviewed integration workflow. | Dev integration validation and conflict evidence. | May feed `checkpoint/<wave-id>`. | Treating dev as canonical truth or release truth. |
| `local/dev` | Local integration branch for bounded task aggregation. | Merge candidates, classified partials, repair outcomes, integration evidence. | Classified warnings and accepted partials only. | Coordinator or assigned local integration worker. | Targeted integration validation; queue/status ownership check. | Eligible for checkpoint, not direct main promotion. | Unclassified dirty work, broad feature work, hidden runtime claims. |
| `task/<task-id>` | Bounded WorkUnit execution lane. | Files inside allowed paths, task evidence, validation output. | Task-local warnings only when classified. | Assigned Codex/AIDE worker. | Task validation, `git diff --check`, evidence refs. | Eligible for `local/dev` after evidence. | Editing forbidden paths, broad cleanup, unrelated staging, direct main promotion. |
| `repair/<task-id>` | Bounded repair for a blocker or failed validation. | Minimal repair diff, blocker evidence, rerun validation. | Repair warnings only when tied to original blocker. | Assigned repair worker. | Original blocker reproduced or explained, repair validation passes or is classified. | Eligible for task branch or `local/dev`. | Expanding into feature work, silent rewrites, unrelated refactors. |
| `checkpoint/<wave-id>` | Temporary integration proof branch. | Selected dev/task changes plus checkpoint reports. | Only checkpoint-classified warnings. | Coordinator/checkpoint owner. | Checkpoint gate, selected validators, warning acceptance, rollback path. | Eligible for reviewed main promotion. | New feature development, speculative edits, hiding unresolved blockers. |
| `quarantine/<reason>` | Isolation lane for risky, untrusted, or ownership-conflicted work. | Inspection notes, risk classification, safe extraction or discard evidence. | Risk warnings only; no pass claims. | Coordinator or assigned triage worker. | Risk disposition, authority review, targeted validation. | Not promotable until risk is resolved and revalidated. | Direct integration, claiming support, unreviewed promotion. |
| `experiment/<name>` | Optional local exploration with no promotion path. | Throwaway experiments and notes outside promotion scope. | Any warnings must stay non-promotional. | Human or explicitly assigned explorer. | None for promotion because promotion is forbidden. | Not promotable; useful ideas must become a new task. | Shipping, evidence substitution, public-surface changes, branch reuse as task proof. |

## Additional Rules

- Only one coordinator may own `.aide/queue/current.toml` at a time.
- Latest task/review/status packets require explicit packet ownership.
- CMake/global build files, root contracts, and broad generated refreshes require
  lane ownership before concurrent edits.
- Branch role detection never authorizes mutation by itself.
- Unknown branches must be classified before promotion or destructive action.
