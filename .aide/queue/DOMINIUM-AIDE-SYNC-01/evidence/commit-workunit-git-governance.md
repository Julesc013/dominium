# Q33 Commit, WorkUnit, And Git Governance

## Commit Discipline

- Policy: `.aide/policies/commit-messages.yaml`
- Hook template: `.aide/hooks/commit-msg`
- Commit template: `.aide/git/commit-template.md`
- Command status:
  - `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS for the
    latest Q33 structured commit.
  - `py -3 .aide/scripts/aide_lite.py commit template`: PASS.
- Changelog preview:
  - `py -3 .aide/scripts/aide_lite.py changelog preview`: WARN because older
    pre-policy Dominium commits do not use structured bodies.
  - Preview paths: `.aide/changelog/CHANGELOG.preview.md`,
    `.aide/changelog/RELEASE_NOTES.preview.md`,
    `.aide/changelog/malformed-commits.md`.

## Task / WorkUnit Recovery

- Policies:
  - `.aide/policies/task-resumption.yaml`
  - `.aide/policies/work-units.yaml`
  - `.aide/policies/recovery.yaml`
- Command status:
  - `task inspect --task-id DOMINIUM-AIDE-SYNC-01`: PASS; classification
    `partial` while Q33 is running.
  - `task noop-check --task-id DOMINIUM-AIDE-SYNC-01`: PASS; result
    `continue_from_status_and_evidence`.
  - `task status`: PASS; queue reports the Q23 pilot and Q33 sync tasks.
- `task current` still infers the stale Q17 phase from the pre-Q33 packet
  until the latest task packet is interpreted by a specific future queue id.

## Git Workflow Governance

- Policies:
  - `.aide/policies/git-workflow.yaml`
  - `.aide/policies/branch-roles.yaml`
  - `.aide/policies/promotion-rules.yaml`
  - `.aide/policies/sync-policy.yaml`
  - `.aide/policies/prune-policy.yaml`
  - `.aide/git/helper-policy.yaml`
- Target-local reports:
  - `.aide/git/workflow-detection.json`
  - `.aide/git/workflow-detection.md`
  - `.aide/git/latest-helper-plan.json`
  - `.aide/git/latest-helper-plan.md`
- Command status:
  - `git detect`: PASS; detected `trunk_without_dev`, current branch `main`,
    current role `canonical`.
  - `git doctor`: PASS with warnings for dirty tree and missing `dev`.
  - `git status`: PASS; dirty tree true during Q33.
  - `git policy`: PASS with helper-plan warnings before plan generation.
  - `git sync --dry-run`: PASS command, blocked by dirty tree for apply.
  - `git land --dry-run --target dev`: PASS command, blocked because current
    branch is canonical and `dev` is missing.
  - `git promote --dry-run --from dev --to main`: PASS command, blocked
    because `dev` is missing.
  - `git prune --dry-run`: PASS command, no protected/current branch pruned.

## Manual Content Preservation

- `AGENTS.md` changed only inside the managed AIDE adapter section.
- The imported hook template was not installed into `.git/hooks`.
- No branch helper `--apply` or `--push` was run.
