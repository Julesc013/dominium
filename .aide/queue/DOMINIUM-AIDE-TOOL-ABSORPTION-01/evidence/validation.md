# Validation Evidence

Status: needs_review

## Baseline

- `git status --short`: clean before Q51.
- `git branch --show-current`: `main`.
- `git remote -v`: origin points to `https://github.com/Julesc013/dominium.git`.
- `git rev-parse HEAD`: `52eeb5a1f481231d55ad0938a8c9b3b54e2aa83f` at Q51 start.
- `git check-ignore .aide.local/`: PASS, `.aide.local/` is ignored.
- `git diff --check`: PASS at baseline.

## AIDE Lite Commands Run Before Artifact Writing

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: TIMEOUT at 240 seconds; lingering eval processes were stopped and the result is treated as WARN/TIMEOUT.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, missing generated controller report refs from `.aide/context/latest-review-packet.md`.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS.
- `py -3 .aide/scripts/aide_lite.py intent validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo inventory`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: WARN, unknown file classifications remain.
- `py -3 .aide/scripts/aide_lite.py quality ledger`: PASS.
- `py -3 .aide/scripts/aide_lite.py quality validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots inventory`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools inventory`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools classify`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools wrap-plan`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools status`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools capabilities`: PASS.
- `py -3 .aide/scripts/aide_lite.py git policy`: PASS.
- `py -3 .aide/scripts/aide_lite.py git plan`: supported but branch action blocked by policy; no branch mutation.
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS.
- `py -3 .aide/scripts/aide_lite.py changelog preview`: PASS.
- `py -3 .aide/scripts/aide_lite.py changelog validate`: PASS.

## Explain-Tool Checks

- `.aide/scripts/aide_lite.py`: PASS.
- `tools/xstack/run.py`: PASS.
- `tools/xstack/bundle_validate.py`: PASS.
- `tools/xstack/auditx/auditx.py`: PASS.
- `archive/quarantine/canon-spine/tools/xstack/auditx/README.md`: PASS.
- `tools/xstack/testx_all.py`: PASS.
- `scripts/dev/gate.py`: PASS.
- `scripts/ci/check_repox_rules.py`: PASS.
- Directory-level and non-tool data paths such as `tools/xstack/`, `tools/xstack/auditx/`, `repo/repox/`, and `validation/validation_engine.py`: MISSING/unsupported as direct explain-tool targets.

## Final Validation

Post-artifact validation after Q51 evidence generation:

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: TIMEOUT at 240 seconds; lingering AIDE eval processes were stopped.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN status with exit 0; warnings are missing generated controller report refs and active diff-scope warnings for `.aide` generated outputs.
- `py -3 .aide/scripts/aide_lite.py tools validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools status`: PASS; tool count 2,995, high-risk 171, unknown 854, `execution_allowed: false`, `no_apply: true`.
- `py -3 .aide/scripts/aide_lite.py tools capabilities`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots status`: PASS; root count 44, high-risk root count 43, no-apply true.
- `py -3 .aide/scripts/aide_lite.py repo validate`: PASS with warning for 1,669 unknown file classifications.
- `py -3 .aide/scripts/aide_lite.py quality validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py intent validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py git policy`: PASS.
- `py -3 .aide/scripts/aide_lite.py pack --task "Q52 Dominium Root Recycling Pilot"`: PASS; `.aide/context/latest-task-packet.md` generated and augmented with Dominium Q52 refs/constraints.
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`: PASS; about 1,298 tokens, within 3,200-token budget.
- `git diff --check`: PASS, with line-ending conversion warnings only.
- `git check-ignore .aide.local/`: PASS.
- JSON parse checks for generated Dominium and AIDE tool JSON files: PASS.
- Targeted secret scan: WARN/no secret found. Broad scan produced policy/token/test-string matches; high-confidence matches were examples or detector code, not live credentials.

## Not Run

- No legacy XStack/AuditX/RepoX/TestX command was executed directly.
- No product build, package, clean, release, or publish command was run.
