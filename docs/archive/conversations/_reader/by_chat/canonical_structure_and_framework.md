Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/canonical_structure_and_framework/`
Promotion Status: not_reviewed

# Dominium Canonical Architecture, Repository Foundation, and Provider Model - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was an extended architecture, repository-structure, and project-governance conversation for the Dominium game/project. The user's core concern was that months of planning and refactoring had stalled actual development and that the repository had repeatedly grown new root directories, duplicate taxonomies, generic `src/`/`source/` wrappers, and unclear ownership boundaries. The user wanted to force the project toward a durable, future-proof structure before building Workbench, the client, the engine, the game systems, modules, packs, renderers, and provider integrations.

The conversation evolved from immediate directory cleanup into a much larger design model. The early problem was physical: too many roots, duplicate structures, vague names, product-specific code in reusable places, pack payloads mixed with package contracts, schemas organized around old roots, tests and docs mirroring obsolete paths, and tools acting like a second source tree. The user repeatedly challenged weak or over-broad directory proposals, especially ones that reintroduced `src/`, new top-level roots, long product names, status words like `legacy`/`modern`, and vendor-shaped structure.

The durable architectural answer that emerged was that the top-level root model should remain small and closed: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`, plus project/tooling roots like `.aide/`, `.github/`, and `.vscode/`. Generated/local roots such as `.dominium.local/`, `build/`, `out/`, `dist/`, `artifacts/`, and `reports/` must not become active source authority. The most important naming and ownership rule became: no new top-level roots unless a root contract intentionally allows them; no first-party `src/` or `source/`; no generic junk drawers like `core`, `shared`, `common`, `misc`, `lib`, or `data` in active source.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, workbench, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `38` source files. The primary extracted source is `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`.

## What Was Decided

- This produced a pattern: generate a large Codex/AIDE task, the user ran it or reported a result, then the assistant evaluated what was truly fixed versus what was only validator/document churn. The user eventually demanded a one-shot "actual final cleanup" prompt because previous passes had sometimes added validators without moving directories. That prompt explicitly required real `git mv` routing, not just reports.
- The final provider directory doctrine became service-first: `runtime/<service>/providers/<provider>/`, not `runtime/<vendor>/<service>/`. Provider choices belong in `release/profiles/` or `content/profiles/`, not app path names. External code belongs under `external/upstream/` or `external/vendor/`, but the repo should choose one convention.
- Packs are distributable authored payloads. The preferred pack layout became category-based, such as `content/packs/<category>/<pack_id>/`. Pack IDs must not depend on paths. Saves and replays must use stable IDs, schema versions, canonical serialization, deterministic hashes, and explicit migration/refusal policies. Backward compatibility must be a compatibility corpus plus tests, not intention.
- INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly different engine implementations.
- The closed root model was the most emotionally and technically important decision. The user repeatedly objected to root proliferation; the final root set became the anchor for all later advice. This decision affects every future proposal: if a concept can fit under an existing root, it should not become a new top-level root.
- The no-`src` rule was also critical. The user considered repeated `src/` and `source/` folders as a central symptom of bad architecture. The final doctrine is that ownership directories are already source roots; implementation should live under meaningful module/subsystem folders, not generic `src` wrappers.
- The framework-boundary decision rejected a top-level `framework/` root. The accepted model is that Domino Framework exists as public surfaces, ABI headers, contracts, and provider/service law. This prevents root sprawl while still supporting SDK/export concepts later.
- The provider model decision was a major response to raylib/SDL/Lua discussions. Third-party libraries should be providers behind first-party service contracts. They can accelerate visible progress but must not own saved data, game law, public ABI, or content schemas.
- The central tradeoff was between speed and long-term architectural integrity. The user wanted immediate progress after months of structure work, but also wanted to avoid repeating the same cleanup cycle. The resulting strategy became: enforce enough structure to prevent collapse, then proceed with narrow governed product slices instead of waiting for every possible governance layer to be perfect.
- Another major tradeoff was between stable APIs and replaceable internals. The chat rejected the idea that every folder or private helper must be stable. Instead, stable identity lives in contracts, manifests, registries, public headers, artifact IDs, and compatibility tests. Private directories and implementations can move or be rewritten if public surfaces and compatibility proofs remain intact.
- The Workbench discussion involved a similar tradeoff. The user wanted powerful authoring workspaces, but the architecture must not make Workbench a privileged bypass. Therefore, Workbench modules and workspaces should operate through the same commands, views, actions, documents, diagnostics, and evidence packets that CLI, CI, headless, server, and future apps use.
- The user wants future assistants not to treat assistant brainstorms as accepted decisions unless accepted by the user.

## What Was Not Decided

- INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly different engine implementations.
- A persistent uncertainty is the exact current repo state. The user supplied many status reports and directory exports, but several exports were internally inconsistent or stale at various points. The chat therefore repeatedly emphasized structure report integrity and verification before trusting tree analyses.
- 1. Verify fast-strict/RepoX/structure report status from a clean current export.
- The user dislikes vague reassurance and wants uncertainty labelled.
- UNCERTAIN: The final exact convention for `external/upstream` versus `external/vendor` should be checked against current repo policy.
- UNCERTAIN: Whether Lua should be pinned to 5.4 or 5.5 is not settled in this chat.
- UNCERTAIN: Whether pack-internal `content/` directories are legitimate pack law or legacy remains to be verified.
- User-reported commits and status summaries: these include commits like `6e0dd93`, `1406490`, `3243fab`, `ce9ca`, and others. Treat them as FACTs reported in the chat, but verify live repo state before acting.
- Is full CTest currently green? The chat repeatedly says no or not run; verify before any release/trust claim.
- Are stale AuditX/identity evidence and launcher marker debt still blocking fast strict? User reports changed over time; verify live.
- Is the final live queue pointing to `PROJECTION-CONFORMANCE-01`, `PRESENTATION-CONTRACT-01`, or a maintenance task? Verify current `.aide/queue/current.toml`.
- Should `external/upstream` or `external/vendor` be canonical? Verify current repo convention.

## Ideas Rejected, Superseded, Or Deprioritised

- Packs are distributable authored payloads. The preferred pack layout became category-based, such as `content/packs/<category>/<pack_id>/`. Pack IDs must not depend on paths. Saves and replays must use stable IDs, schema versions, canonical serialization, deterministic hashes, and explicit migration/refusal policies. Backward compatibility must be a compatibility corpus plus tests, not intention.
- The framework-boundary decision rejected a top-level `framework/` root. The accepted model is that Domino Framework exists as public surfaces, ABI headers, contracts, and provider/service law. This prevents root sprawl while still supporting SDK/export concepts later.
- The provider model decision was a major response to raylib/SDL/Lua discussions. Third-party libraries should be providers behind first-party service contracts. They can accelerate visible progress but must not own saved data, game law, public ABI, or content schemas.
- Another major tradeoff was between stable APIs and replaceable internals. The chat rejected the idea that every folder or private helper must be stable. Instead, stable identity lives in contracts, manifests, registries, public headers, artifact IDs, and compatibility tests. Private directories and implementations can move or be rewritten if public surfaces and compatibility proofs remain intact.
- The Workbench discussion involved a similar tradeoff. The user wanted powerful authoring workspaces, but the architecture must not make Workbench a privileged bypass. Therefore, Workbench modules and workspaces should operate through the same commands, views, actions, documents, diagnostics, and evidence packets that CLI, CI, headless, server, and future apps use.
- 2. If fast-strict is blocked, repair stale generated evidence/markers first.
- 4. Do not run broad structure cleanup unless a validator reports hard active-path blockers.
- Formal requirements candidates include: no top-level root sprawl; no first-party `src/source`; path is not identity; public surfaces must be registered; apps compose, runtime implements, contracts define; provider implementations must not leak third-party types across stable boundaries; full release proof requires full-gate green.
- The repo's top-level root model is settled; do not redesign it casually.
- Do not trust stale structure exports; validate report bundle integrity.

## What Future Work Came From It

- This produced a pattern: generate a large Codex/AIDE task, the user ran it or reported a result, then the assistant evaluated what was truly fixed versus what was only validator/document churn. The user eventually demanded a one-shot "actual final cleanup" prompt because previous passes had sometimes added validators without moving directories. That prompt explicitly required real `git mv` routing, not just reports.
- INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly different engine implementations.
- The closed root model was the most emotionally and technically important decision. The user repeatedly objected to root proliferation; the final root set became the anchor for all later advice. This decision affects every future proposal: if a concept can fit under an existing root, it should not become a new top-level root.
- The Workbench discussion involved a similar tradeoff. The user wanted powerful authoring workspaces, but the architecture must not make Workbench a privileged bypass. Therefore, Workbench modules and workspaces should operate through the same commands, views, actions, documents, diagnostics, and evidence packets that CLI, CI, headless, server, and future apps use.
- The strongest immediate maintenance tasks are: refresh stale generated evidence, repair launcher pack-verification marker debt if still blocking fast strict, run or audit full CTest/T4 failures, and classify remaining full-gate failures by cause. The task names discussed include `FULL-GATE-GENERATED-EVIDENCE-REFRESH-01`, `FAST-STRICT-EVIDENCE-MARKER-REPAIR-01`, and `FULL-CTEST-AUDIT-NONPATH-01`.
- Mainline tasks discussed include `PRESENTATION-CONTRACT-01`, `PROJECTION-CONFORMANCE-01`, `COMMAND-RESULT-VIEW-SLICE-01`, `PACKAGE-MOUNT-SLICE-01`, and `WORKBENCH-VALIDATION-SLICE-01`. The rule is to prove narrow slices before broad UI, gameplay, renderer, provider runtime, or package runtime expansion.
- The user wants structure to support modularity, portability, extensibility, reuse, modding, backwards compatibility, and future replacement.
- The user strongly prefers actual execution/move prompts over endless micro-planning when structure is blocking work.
- The user wants future assistants not to treat assistant brainstorms as accepted decisions unless accepted by the user.
- INFERENCE: The user prefers aggressive cleanup when structural debt is blocking product work, but increasingly accepts targeted tasks once structure is credible.
- `dominium_canonical_handoff.md` and `dominium_canonical_handoff.txt`: earlier generated handoff files summarizing a major phase of the repository/architecture discussion. Preserve and compare with this preservation package.
- Is the final live queue pointing to `PROJECTION-CONFORMANCE-01`, `PRESENTATION-CONTRACT-01`, or a maintenance task? Verify current `.aide/queue/current.toml`.

## Important Artifacts

- `handoff`: `4`
- `json`: `4`
- `manifest`: `2`
- `markdown`: `6`
- `primary_report`: `2`
- `prompt`: `2`
- `reader_brief`: `4`
- `registers`: `2`
- `source_input`: `1`
- `spec_sheet`: `2`
- `text`: `2`
- `verification`: `3`
- `zip`: `4`

## Verification Needed

- Verify every implementation, platform, tooling, release, and queue claim against current repo artifacts.
- Treat external platform or SDK claims as stale until independently checked.
- Treat old language-baseline claims as historical unless they match current `README.md` and current contracts.
- Do not infer current authority from the existence of this archive package.

## Candidate Promotions

Candidate promotions, if any, are recorded in `_promotion/PROMOTION_QUEUE.md`. This page does not promote claims.

## Do Not Assume

- Do not assume this conversation established current repo truth.
- Do not assume generated package reports are canonical.
- Do not assume old prompts were executed.
- Do not assume unresolved items are safe to implement.
- Do not use this package to open blocked work without stronger current authority.
