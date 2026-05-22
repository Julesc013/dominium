Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-WORKFLOW-LAW-01
Stability: provisional
Binding Sources: `.aide/policies/recovery.yaml`, `.aide/policies/git-workflow.yaml`, `.aide/policies/work-units.yaml`

# AIDE Dirty-Worktree Policy

## Core Rule

Do not stop merely because the worktree is dirty.

Before declaring blocked due to dirty state, classify the dirtiness:

- ignored/generated/transient
- prior task evidence
- unstaged unrelated changes
- same-task continuation
- overlapping another-task changes
- merge conflict markers
- global AIDE/status file conflict

## Required Inspection

Run or record equivalent evidence for:

- `git status --short --branch`
- changed paths grouped by allowed, forbidden, generated, and unknown scope
- ownership of `.aide/queue/current.toml`, latest packets, status docs, and
  shared report files
- conflict marker check when merge or patch conflicts are suspected

## Continue Conditions

Continue when all are true:

- current edits are limited to allowed paths
- unrelated dirty files are path-disjoint and not staged
- no merge conflict markers affect touched files
- no global AIDE/status packet conflict exists
- no destructive git command is required
- no semantic authority conflict is present

## Stop Conditions

Stop or quarantine when any are true:

- dirty state requires overwriting unrelated user changes
- `.aide/queue/current.toml` or latest packets already contain incompatible
  updates from another coordinator
- conflict markers remain in target files
- destructive git is required to proceed
- a source-authority conflict must be resolved to continue
- secrets or local-only state would be exposed

## Forbidden Actions

- Do not stage unrelated files.
- Do not overwrite unrelated user changes.
- Do not run `git reset --hard`, force checkout, branch delete, or force-push.
- Do not fabricate clean state.
- Do not silently move work into generated or quarantined roots.

## Isolated Worktrees

Use an isolated worktree from `origin/main` or `origin/dev` when concurrent work
would otherwise overlap unsafe paths. Isolated worktrees still require queue
ownership, evidence, and promotion gates.
