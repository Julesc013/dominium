# Install/Upgrade Risk Report

## Overall Risk

Q50 should proceed only as an upgrade dry-run with warnings. Dominium already has target-specific AIDE state and extensive doctrine/tooling. Treating it as an empty repo would risk losing target memory, queue history, golden tasks, doctrine references, generated validation evidence, and XStack governance state.

## Must Preserve

- `.aide/memory/**`.
- `.aide/queue/**`.
- `.aide/evals/**`.
- `.aide/context/latest-task-packet.md`, `.aide/context/latest-review-packet.md`, `.aide/context/dominium-doctrine-refs.md`, and compact context config.
- `.aide/reports/**` target-specific reports.
- `.aide/git/**`, `.aide/changelog/**`, `.aide/policies/**`, `.aide/verification/**`.
- `AGENTS.md` manual and managed content.
- `docs/canon/**`, `docs/planning/**`, `specs/reality/**`, `data/reality/**`, `data/planning/**`, `contracts/**`, `schema/**`, `schemas/**`.
- XStack/AuditX/RepoX/TestX systems under `tools/**`, `scripts/**`, `repo/**`, `docs/audit/**`, `data/registries/**`, `validation/**`, and CMake configuration.
- Ignored local state including `.aide.local/**`, `.dominium.local/**`, `out/**`, `dist/**`, `build/**`, and `__pycache__/**`.

## Must Avoid

- `.aide.local/**`, secrets, provider credentials, raw prompts, raw responses, local traces, and cache-only state.
- Product/source roots: `runtime/**`, `engine/**`, `game/**`, `apps/**`, `content/**`, `contracts/**`, `specs/**`, `data/**`, `tools/**`, `scripts/**`, `cmake/**`, `.github/**`.
- Branch, tag, remote, CI, release, publish, prune, clean, rollback, uninstall, or destructive build mutation.
- Blind replacement of target-specific patches, managed sections, queue packets, golden tasks, generated reports, or doctrine pointer files.

## Specific Conflicts

- Target AIDE is q24 and lacks Q36-Q48 `intent`, `repo`, `quality`, `refactor`, `roots`, `tools`, `install`, `repair`, `upgrade`, `rollback`, and `uninstall` command families.
- Target AIDE memory has stale original import paths. Q50 may refresh these only through reviewed target-local preservation logic.
- Bundle install notes say local preview no-publish and `apply_mode_available: false`.
- Existing Dominium gate systems write target evidence and require separate execution approval.

## Required Q50 Approach

- Because `.aide/` exists, Q50 should use upgrade observe/compare/plan/dry-run, not first-install apply.
- Compare the release bundle against target `.aide/` in a temp/review area outside Dominium or through an explicitly non-mutating target planner.
- Generate a conflict matrix before any future apply: keep target-specific memory/queue/evidence/golden tasks; import only additive compatible portable surfaces.
- Apply only in a future explicit apply phase with review approval.
- Use targeted sync only if already permitted by the installed AIDE behavior and Q50 prompt scope.
