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

To be completed before review.
