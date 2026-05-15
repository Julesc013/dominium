# Repo State

## Identity

- Repo root: `C:/Inbox/Git Repos/dominium`.
- Expected identity: `julesc013/dominium`.
- Remote: `origin https://github.com/Julesc013/dominium.git`.
- Identity result: confirmed as Dominium.

## Git State

- Branch: `main`.
- HEAD at start: `752918d4f281aad12cdb6e892d39460172155e34`.
- Upstream relation at start: `main...origin/main [ahead 6]`.
- Starting dirty state: clean (`git status --short` returned no paths before Q49 commands).
- Local/remote branches observed: `main`, `origin/main`, `origin/HEAD -> origin/main`, `origin/recovery/mega-13cb8ca7`.
- Tags observed: `canon-clean-2`, `safety/mega-13cb8ca7`.
- Recent history confirms AIDE-related commits above `origin/main`, including `aide(dominium): refresh final validation artifacts`.

## Ignored And Local State

- `.aide.local/` ignore check: PASS (`git check-ignore .aide.local/` returned `.aide.local/`).
- `.aide.local/` tracked paths: none (`git ls-files .aide.local` returned no paths).
- `.aide.local.example/**` is tracked example state and must be preserved.
- Ignored local/generated paths observed include `.dominium.local/`, `out/`, `dist/docs/`, `dist/sym/`, `dist/sys/`, many `__pycache__/` folders, and `.aide/scripts/__pycache__/`.
- These ignored paths are not Q49 evidence and must not be committed, cleaned, moved, or treated as AIDE install candidates.

## Q49 Working Tree Notes

- Q49 generated or updated only AIDE-scoped artifacts: the Q49 queue packet, compact `.aide/reports/dominium-*` reports, the Q50 latest task packet, latest review packet, golden-task run reports, git helper plan, and changelog previews.
- No product/source/doctrine/tool files were modified.
- No branch, tag, remote, CI, release, publish, prune, clean, or destructive build operation was run.

## Safe And Unsafe Commands

- Safe commands run: git inspection, `.aide.local` ignore check, AIDE doctor/validate/test/selftest/eval/verify/review-pack, AIDE commit check, AIDE git policy/plan, AIDE changelog preview, AIDE pack, read-only release bundle hash/listing checks, targeted secret scan.
- Discovered but not run as Q49 validators: `python scripts/dev/gate.py verify`, AuditX scan/verify/enforce, grouped TestX runners, RepoX checks, CMake configure/build/test lanes. These systems can write `.xstack_cache`, `docs/audit/**`, build/output roots, or other target evidence and require a separate explicit validation phase.
