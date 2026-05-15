# Validation

## Git And Local Checks

- `git remote -v`: PASS; origin points at `https://github.com/Julesc013/dominium.git`.
- `git rev-parse --show-toplevel`: PASS; `C:/Inbox/Git Repos/dominium`.
- `git status --short` at start: PASS; clean.
- `git status --branch --short`: PASS; `main...origin/main [ahead 6]`.
- `git branch --all`: PASS.
- `git rev-parse HEAD`: PASS; `752918d4f281aad12cdb6e892d39460172155e34`.
- `git tag --list`: PASS; `canon-clean-2`, `safety/mega-13cb8ca7`.
- `git diff --check` at start: PASS.
- `git check-ignore .aide.local/`: PASS.
- `git ls-files .aide.local`: PASS; no tracked paths.
- `git diff --check` after writing Q49 artifacts: PASS, with line-ending notices for existing generated AIDE files only.

## Existing AIDE Checks

- `py -3 .aide/scripts/aide_lite.py version`: PASS; q24.
- `py -3 .aide/scripts/aide_lite.py show-config`: PASS.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with review-packet reference warnings.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 25/25 golden tasks.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN. Final pre-commit run reported 11 warnings: 4 missing controller/gateway/provider status references from the generated review packet, 6 diff-scope warnings for generated changelog/git helper outputs, and 1 diff-scope warning for the Q49 queue packet while the active latest task packet is Q50.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS output; latest review packet written.
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS.
- `py -3 .aide/scripts/aide_lite.py git policy`: PASS.
- `py -3 .aide/scripts/aide_lite.py git plan`: blocked by dirty Q49 worktree; dry-run only, no mutation.
- `py -3 .aide/scripts/aide_lite.py changelog preview`: WARN, 14 malformed commits in recent range.
- `py -3 .aide/scripts/aide_lite.py changelog validate`: NOT RUN/UNSUPPORTED.
- `py -3 .aide/scripts/aide_lite.py pack --task "Q50 Dominium Fresh Install / Upgrade from Stable AIDE Pack"`: PASS.
- Generated JSON parse checks: PASS for `.aide/changelog/changelog.preview.json`, `.aide/evals/runs/latest-golden-tasks.json`, and `.aide/git/latest-helper-plan.json`.

## Unsupported Q36-Q48 Target Commands

The following returned unsupported command errors in target AIDE q24 and are recorded as missing capabilities, not Q49 validation failures:

- `intent validate`
- `repo validate`
- `quality validate`
- `refactor validate`
- `roots validate`
- `tools validate`
- `install validate`
- `repair validate`
- `upgrade validate`
- `rollback validate`
- `uninstall validate`

## Release Bundle Checks

- Dist discovery: PASS; selected `C:/Inbox/Git Repos/aide/.aide/release/dist`.
- Checksums: PASS for zip, tar.gz, manifest, install notes, changelog preview, release notes preview, release assets, and release provenance.
- Manifest read: PASS.
- Install notes read: PASS.
- Zip listing: PASS, 634 entries, no forbidden path matches.
- Tar.gz listing: PASS, 634 entries, no forbidden path matches.
- Extraction into Dominium: NOT RUN by design.

## Secret Scan

- Targeted scan run over `.aide`, root docs, `docs`, `specs`, `data`, `contracts`, `tools`, `scripts`, and `.gitignore`.
- Broad scan produced many policy/example/test/code matches.
- High-confidence scan produced 21 matches, reviewed as policy text, test fixtures, code variables, or false positives; no actual secret was identified.

## Dominium Product/Gate Validation

- XStack/gate/TestX/AuditX/RepoX/CMake validators were discovered but not run in Q49 because they can write target audit/cache/build outputs and were outside this evidence-only preflight.
- Contract/schema impact: none.
