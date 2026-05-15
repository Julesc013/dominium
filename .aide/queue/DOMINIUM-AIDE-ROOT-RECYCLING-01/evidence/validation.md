# Validation Evidence

Status: needs_review

## Baseline

- `git status --short`: clean before Q52.
- `git branch --show-current`: `main`.
- `git remote -v`: origin points to `https://github.com/Julesc013/dominium.git`.
- `git rev-parse HEAD`: `d22537869be05860d5eda70eebb2f3ed261e276c` at Q52 start.
- `git check-ignore .aide.local/`: PASS.
- `git diff --check`: PASS.

## AIDE Baseline Commands

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: TIMEOUT at 120 seconds; lingering eval processes were stopped.
- `py -3 .aide/scripts/aide_lite.py verify`: PASS exit 0.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS.
- `py -3 .aide/scripts/aide_lite.py intent validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo inventory`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py quality ledger`: PASS.
- `py -3 .aide/scripts/aide_lite.py quality validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools inventory`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots inventory`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots classify`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots plan`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots status`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots explain-root ide`: PASS; `ide` has 4 tracked files, status `review_required`, risk `high`.
- `py -3 .aide/scripts/aide_lite.py git policy`: PASS.
- `py -3 .aide/scripts/aide_lite.py git plan`: PASS/no branch mutation.
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS.
- `py -3 .aide/scripts/aide_lite.py changelog preview`: PASS.
- `py -3 .aide/scripts/aide_lite.py changelog validate`: PASS.

## JSON Checks

- `ide/manifests/projection_manifest.schema.json`: parsed.
- `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json`: parsed.
- `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json`: parsed.

## Final Validation

Post-artifact validation after Q52 evidence and Q53 packet generation:

- `py -3 .aide/scripts/aide_lite.py pack --task "Q53 Dominium Operating Baseline"`: PASS.
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`: PASS; about 1,403 tokens, within 3,200-token budget.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: TIMEOUT at 120 seconds; lingering eval processes were stopped.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN status with exit 0; warnings are missing generated controller report refs and active diff-scope warnings for `.aide` generated outputs.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots status`: PASS; 44 roots, 15,977 files, 43 high-risk roots, no-apply true.
- `py -3 .aide/scripts/aide_lite.py tools validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: PASS with warning for 1,669 unknown file classifications.
- `py -3 .aide/scripts/aide_lite.py quality validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py intent validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py git policy`: PASS.
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS.
- `git diff --check`: PASS, with line-ending conversion warnings only.
- `git check-ignore .aide.local/`: PASS.
- JSON parse checks for generated Dominium and AIDE root JSON files: PASS.
- Targeted high-confidence secret scan: reviewed; matches were detector/policy/example strings, not live credentials.

## Not Run

- No XStack/AuditX/RepoX/TestX command was executed.
- No product build, package, clean, release, or publish command was run.
