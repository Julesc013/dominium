# Reader Brief — Dominium Application/TestX/CodeHygiene Handoff

## What This Chat Was About

This retired chat consolidated a large amount of Dominium / Domino planning into current carry-forward state for application-layer implementation, testing/version/changelog governance, code hygiene, and chat handoff packaging. The project itself is a deterministic universe engine/game, but this chat’s latest active focus is no longer core simulation design. The latest user-pasted PROJECT-CONTEXT says architecture is closed and canon locked; future work should implement, audit, optimise, and maintain within canon.

The most important current artifact is APP-UNIFIED-CANON, which unifies setup/launcher/application-layer plans. It requires a pure application contract layer (`libs/contracts`), a shared appcore (`libs/appcore`), a single canonical command graph, declarative UI IR, setup as install authority, launcher as reference app, thin client/server, read-only tools, RepoX/TestX integration, accessibility/localisation, and strict failure behavior.

The chat also produced TESTX, a replacement for TEST0, to create long-lived tests, assertions, comment-density checks, blocker crossrefs, version/build/changelog automation, and git discipline. CODEHYGIENE-X addresses hardcoded taxonomies, magic numbers, `CUSTOM/OTHER` enums, admin/cheat flags, and data/code boundary enforcement.

Generated prompts are not proof of repository implementation. The next chat must inspect repo/source/docs before claiming files exist.

## Most Important Things to Know

- Architecture is closed; do not redesign.
- Core ontology from latest bootstrap: Assemblies, Fields, Processes, Agents, Law.
- Engine is C89; game is C++98.
- Apps may use newer toolchains but cannot impose them on engine/game.
- Applications are orchestration shells only.
- CLI is canonical.
- UI is data (UI IR), never business logic.
- Setup is the only install mutation authority.
- Launcher is the reference application.
- Tools are read-only by default.
- Apps must run with zero content packs.
- RepoX is source of truth for build/changelog/compatibility.
- No manual changelog editing.
- BUILD-ID-0 semantics supersede earlier build-number plans.
- TESTX supersedes TEST0.
- CODEHYGIENE-X is current hygiene plan.
- Verify actual repo state before implementation.

## Active Plans or Workstreams

- Application layer implementation.
- Testing/version/changelog governance.
- Source-code hygiene/data-code boundary.
- Docs/canon/package handoff.
- Content/data later in separate chat.

## Decisions Already Made

- APP-UNIFIED-CANON is latest application plan.
- CLI canonical; GUI/TUI are views.
- Setup handles install/repair/rollback; launcher does not duplicate setup logic.
- Tools default read-only.
- Changelogs generated automatically.
- Hardcoded open taxonomies should migrate to data/registries.

## Pending Tasks

- Verify which prompts were actually executed.
- Inspect repository for `libs/contracts`, `libs/appcore`, RepoX, TestX, VALIDATE-0.
- Generate concrete application implementation prompt if continuing app work.
- Run or adapt TESTX.
- Run or adapt CODEHYGIENE-X.
- Store this package for aggregation.

## Open Questions

- Which generated prompts ran?
- Does CANON_INDEX.md exist?
- Where are RepoX/TestX/VALIDATE-0 files?
- Are app contract/appcore directories present?
- How are `DOMINIUM_RUN_ROOT` and `DOMINIUM_HOME` finalized?

## Files / Artifacts / Prompts to Preserve

- APP-UNIFIED-CANON
- TESTX
- CODEHYGIENE-X
- DOCS0
- CANON0 / REALITY0 / LIFE0+ / CIV0+ / FUTURE0
- Latest user-pasted global bootstrap
- Latest user-pasted application bootstrap
- This final report package

## What to Verify Before Acting

- Actual repo state.
- Actual docs/canon files.
- Actual RepoX/TestX/VALIDATE-0 commands.
- Whether BUILD-ID-0 is implemented.
- Whether APP-CANON1/APP-AUTO-0/APP-UI-BIND-0 docs exist.

## Best Next Step

Open a new chat with the bootstrap prompt and this package. If continuing application work, inspect repo or ask for source/docs, then generate a concrete Codex prompt to implement `libs/contracts` and `libs/appcore` according to APP-UNIFIED-CANON.
