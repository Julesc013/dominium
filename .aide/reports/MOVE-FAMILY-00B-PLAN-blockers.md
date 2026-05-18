# MOVE-FAMILY-00B-PLAN Blockers

Status: DRAFT
Last Reviewed: 2026-05-17

## File-Level Blockers

None.

All three tracked files under `ide/manifests/**` are classifiable as projection contract metadata and have proposed target paths under `contracts/projection/ide/**`.

## Gate Requirements

Apply remains blocked until a later gate explicitly approves:

- creating `contracts/projection/ide/**`;
- moving all three tracked manifest source files;
- updating required current references;
- narrowing `.gitignore` so generated IDE output stays ignored;
- retiring the `ide` layout exception only after `git ls-files ide` is empty and validators pass.

## Warning-Only Conditions

- `contracts/projection/ide/**` is a planned scoped contract slot, not an existing path.
- Generated projection output references to `ide/manifests/*.projection.json` may remain if they are documented as generated/local output.
- Historical audit evidence may continue to reference old paths.

## No-Apply Confirmation

No files were moved, deleted, renamed, or rewritten by this task.
