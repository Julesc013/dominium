# Q33 Validation

## Baseline Before Sync

- `git status --short`: PASS; clean before baseline commands.
- `git branch --show-current`: PASS; `main`.
- `git branch --all`: PASS; local `main`; remotes `origin/main`,
  `origin/recovery/mega-13cb8ca7`.
- `git remote -v`: PASS; origin `https://github.com/Julesc013/dominium.git`.
- `git rev-parse HEAD`: PASS;
  `06d383b3d85563f33276e4be8ad561c962c6695e`.
- `git check-ignore .aide.local/`: PASS; `.aide.local/`.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS with existing WARNs for
  optional controller/gateway/provider generated reports.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with existing WARNs for
  stale review-packet references.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 6/6 golden tasks.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 4 stale generated-report
  references, 0 errors.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: FAIL before sync
  because generated adapter manifest/drift report are absent.
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: NOT AVAILABLE
  before sync; command exited 2.
- `py -3 .aide/scripts/aide_lite.py changelog preview`: NOT AVAILABLE before
  sync; command exited 2.
- `py -3 .aide/scripts/aide_lite.py git detect|doctor|status|policy|plan`:
  NOT AVAILABLE before sync; each command exited 2.

## Final Validation

- `git status --short`: PASS; dirty only from Q33 generated artifacts before
  final evidence commit.
- `git diff --check`: to be rerun after final evidence edits.
- `git branch --show-current`: PASS; `main`.
- `git branch --all`: PASS; local `main`; remotes `origin/main`,
  `origin/recovery/mega-13cb8ca7`.
- `git check-ignore .aide.local/`: PASS; `.aide.local/`.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS with warnings for optional
  controller/gateway/provider generated status outputs.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with warnings for optional
  review-packet generated status refs.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 25/25 golden tasks.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 0 errors; warnings are
  optional generated status refs and diff-scope warnings for Q33 generated
  `.aide/git`/`.aide/changelog` outputs.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS packet generation;
  verifier result WARN.
- `py -3 .aide/scripts/aide_lite.py ledger scan`: PASS with budget warnings
  for generated cache/eval reports.
- `py -3 .aide/scripts/aide_lite.py ledger report`: PASS with budget warnings
  for generated cache/eval reports.
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS for latest
  structured Q33 commit when run after the governance sync commit.
- `py -3 .aide/scripts/aide_lite.py commit template`: PASS.
- `py -3 .aide/scripts/aide_lite.py changelog preview`: WARN; older
  pre-policy commits are malformed for changelog extraction.
- `py -3 .aide/scripts/aide_lite.py task inspect --task-id DOMINIUM-AIDE-SYNC-01`:
  PASS; classification partial while task is running.
- `py -3 .aide/scripts/aide_lite.py task status`: PASS.
- `py -3 .aide/scripts/aide_lite.py task noop-check --task-id DOMINIUM-AIDE-SYNC-01`:
  PASS; continue from status/evidence.
- `py -3 .aide/scripts/aide_lite.py git detect`: PASS; current branch `main`,
  role `canonical`, workflow `trunk_without_dev`.
- `py -3 .aide/scripts/aide_lite.py git doctor`: PASS with warnings for dirty
  tree and missing `dev`.
- `py -3 .aide/scripts/aide_lite.py git status`: PASS; dirty tree reported.
- `py -3 .aide/scripts/aide_lite.py git policy`: PASS.
- `py -3 .aide/scripts/aide_lite.py git plan`: PASS command; result blocked
  by dirty tree classification, non-mutating.
- `py -3 .aide/scripts/aide_lite.py git sync --dry-run`: PASS command; result
  blocked for apply by dirty tree, non-mutating.
- `py -3 .aide/scripts/aide_lite.py git land --dry-run --target dev`: PASS
  command; result blocked because current branch is canonical and `dev` is
  missing, non-mutating.
- `py -3 .aide/scripts/aide_lite.py git promote --dry-run --from dev --to main`:
  PASS command; result blocked because `dev` is missing, non-mutating.
- `py -3 .aide/scripts/aide_lite.py git prune --dry-run`: PASS command; no
  protected/current branch pruned, non-mutating.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS after
  `adapter render`.
- `py -3 .aide/scripts/aide_lite.py pack --task "Select the next bounded Dominium task after canonical AIDE governance sync"`:
  PASS; latest task packet generated.
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`:
  PASS; 4,632 chars, about 1,158 tokens.
- `py -3 scripts/verify_docs_sanity.py`: PASS.

## Not Run / Not Applicable

- Branch helper `--apply`: NOT RUN; forbidden by Q33.
- Branch helper `--push`: NOT RUN; forbidden by Q33.
- Hook installation: NOT RUN; hook template is opt-in.
- Provider/model/network calls: NOT RUN; forbidden by Q33.
