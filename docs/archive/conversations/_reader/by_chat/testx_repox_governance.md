Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/testx_repox_governance/`
Promotion Status: not_reviewed

# Dominium TestX/RepoX Governance and Handoff Chat - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about turning the Dominium / Domino project from a large, ambitious architecture into something that could survive implementation across many parallel chats, many products, many platforms, many toolchains, and many years of future changes. The conversation was not primarily about gameplay content, graphics, or a single feature. It was about **governance**: how the repository, build system, tests, versioning, applications, content packs, IDEs, demos, services, authority models, and future language transitions should be structured so the project does not collapse into unmaintainable drift.

**FACT:** The user is building Dominium / Domino as a deterministic universe engine + game, not a conventional game project. The visible chat repeatedly framed the project as long-lived, simulation-first, deterministic, modular, and designed to survive across many operating systems, toolchains, renderers, products, and distribution models.

The chat began with versioning and build governance. The user wanted a way for the repository and CMake system to handle global build numbers, manual semantic product versions, changelogs, protocol/API/ABI versions, platform builds, packaging, updates, and distribution artifacts. Early suggestions included a global build number that would increment on every build or after successful tests. That idea later changed substantially when a newer upstream canon introduced **BUILD-ID-0**, where global build numbers are only centrally allocated for release-grade artifacts, while local/dev/CI builds use Build Instance IDs. That change is one of the most important corrections in the whole chat.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, determinism, governance, platform, release, setup_launcher, simulation, tooling, ui, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/testx_repox_governance/dominium_testx_repox_governance_handoff__human_readable_chat_report.txt`.

## What Was Decided

- FACT:** The user is building Dominium / Domino as a deterministic universe engine + game, not a conventional game project. The visible chat repeatedly framed the project as long-lived, simulation-first, deterministic, modular, and designed to survive across many operating systems, toolchains, renderers, products, and distribution models.
- The user then asked whether the implementation was industry-accepted and what could be improved. The response framed the approach as closer to game engines, operating systems, and long-lived infrastructure than typical game development. The important conclusion was that the design was not exotic, but it was unusually rigorous for games.
- The user had another chat working on content and systems, and asked for a prompt to inform that chat of everything decided so far. A similar prompt was generated for the applications/platforms/renderers chat. These prompts established authoritative boundaries:
- engine/game/content must be zero-asset and capability-driven;
- applications must be thin shells;
- build/versioning rules must not be bypassed;
- This chat then generated new prompts, `EG-TESTX` and `AP-TESTX`, to send to engine/game/content and application/platform/render teams. Those prompts required response prompts from those teams. The user pasted back their responses. Both accepted TESTX canon and identified tensions.
- Another important tension was "no silent fallback" versus renderer fallback. The application/platform response resolved this by saying explicit renderer selection must fail if unavailable, while `auto` mode can fallback only with explicit logging. This distinction became important for testability and user transparency.
- This was an important philosophical and technical decision. It allowed the project to support free downloads, demos, paid upgrades, subscriptions, services, and anti-piracy containment without creating code forks or corrupting the deterministic core.
- This was the biggest late-stage correction. It did not throw away the earlier work, but it changed the source hierarchy. Most importantly, it superseded earlier build-number ideas. Future work must now reconcile TESTX, TESTX2, TESTX3, and REPOX with BUILD-ID-0, CLEAN-2, and the APP canon.
- The final state of the conversation is that it produced a high-fidelity governance memory for this chat, but the actual repository still needs verification before changes are made.
- GBN is release-grade and centrally allocated;

## What Was Not Decided

- This topic remains unresolved in implementation because the repo snapshot showed `.dominium_build_number` and `update_build_number.cmake`, but the chat did not inspect their contents. Those files may still implement older build-number behavior. That must be verified.
- The unresolved part is implementation verification. The repo has Sol/Earth content in `data` and `game/content`; the engine must not assume those exist.
- The unresolved part is how much of TESTX is actually implemented in the repo. The repo contains many tests and scripts, but this chat did not inspect them. A rules-to-checks audit is needed.
- This remains conceptually accepted in the chat, but implementation is unverified.
- The unresolved goals are mostly implementation and verification:
- The repo already has UI IR/codegen infrastructure. The next step is to verify whether GUI/TUI truly bind to the CLI command graph and whether UI is data rather than logic.
- The user has Windows 10 + VS2022. The next step is to verify v141/v141_xp/SDK components and create isolated CMake presets for XP/Win7/Win8/Win10/Win11 builds.
- Acting before verifying repo state.
- The user also explicitly required the report style to preserve facts, inferences, uncertainties, rejected options, artifacts, timelines, risks, and visible rationale.
- This recommendation is useful for immediate practical builds but requires verification of installed components and current toolchain facts.
- Manual product SemVer is required, but the actual file layout is unverified.
- The repo has UI tooling, but this chat did not verify that GUI/TUI bind to CLI command graph or that tools are read-only by default.

## Ideas Rejected, Superseded, Or Deprioritised

- build/versioning rules must not be bypassed;
- One important tension was build numbering. Earlier external guidance had suggested incrementing a build number on every configure/build. TESTX required the build number to be owned by the test system and incremented only after full test success. Later, this was superseded again by BUILD-ID-0.
- revocation/access rules that do not corrupt history or replays.
- This was the biggest late-stage correction. It did not throw away the earlier work, but it changed the source hierarchy. Most importantly, it superseded earlier build-number ideas. Future work must now reconcile TESTX, TESTX2, TESTX3, and REPOX with BUILD-ID-0, CLEAN-2, and the APP canon.
- At first, the proposed idea was a global build number that would increment frequently. That model was later weakened by TESTX, which wanted build-number increments only after test success, and then superseded by the latest upstream **BUILD-ID-0** model. Under BUILD-ID-0, there is no universal local build-number increment for every build. Instead:
- This separation matters because it lets different parts evolve independently. It also supports old binaries continuing to receive compatible updates after old OS support is dropped. The latest upstream canon made this more explicit by saying engine is C89, game is C++98, apps may use newer toolchains, but applications must not impose requirements on engine/game.
- The unresolved part is implementation verification. The repo has Sol/Earth content in `data` and `game/content`; the engine must not assume those exist.
- The user asked about DRM, anti-cheat, copy protection, and control systems. The conclusion was that these are not engine/game features. They are external control layers. They may gate access or connectivity, but must not alter authoritative simulation.
- The alternative was to keep iterating on architecture. That is now rejected unless the user explicitly reopens design. This affects every future assistant: they should audit, implement, optimize, or maintain, not re-litigate core structure.
- The alternative would be to modernize everything uniformly. That was rejected by the toolchain/legacy support goals. Applications and tools may use newer languages, but they must not impose requirements on engine/game.

## What Future Work Came From It

- That was the initial design phase. At that point, the build-number idea was still broad and aggressive: a global build number incrementing frequently.
- The user had another chat working on content and systems, and asked for a prompt to inform that chat of everything decided so far. A similar prompt was generated for the applications/platforms/renderers chat. These prompts established authoritative boundaries:
- The next major shift came when the user pasted an authoritative prompt called **TESTX** from "The Game chat." TESTX was a major governance layer: permanent verification, versioning, self-defending tests, deterministic execution, repository survey, test taxonomy, assertion tiers, comment density, blocker tracking, and changelog governance.
- This chat then generated new prompts, `EG-TESTX` and `AP-TESTX`, to send to engine/game/content and application/platform/render teams. Those prompts required response prompts from those teams. The user pasted back their responses. Both accepted TESTX canon and identified tensions.
- This chat endorsed that approach and suggested making control systems capability-gated, disabled by default, and subject to a non-interference invariant. The user then asked for a sequel mega-prompt, and **TESTX2** was generated. TESTX2 formalized:
- This mattered because the user wanted future support for such systems without enabling them by default or compromising core principles.
- Based on the tree, the response concluded that the repo already had many ingredients: UI IR/codegen, setup/launcher tooling, tests, validation scripts, platform layers, packaging, and legacy/orphaned directories. What it lacked was an explicit projection layer and enforcement model. The proposed REPOX prompt introduced:
- The user then supplied a detailed matrix for Windows, Mac, and Linux, including language modes and old/new architecture goals. REPOX was generated as a mega-prompt.
- APP-CANON0/1 and related app prompts govern the application layer;
- This was the biggest late-stage correction. It did not throw away the earlier work, but it changed the source hierarchy. Most importantly, it superseded earlier build-number ideas. Future work must now reconcile TESTX, TESTX2, TESTX3, and REPOX with BUILD-ID-0, CLEAN-2, and the APP canon.
- future archival and modding.
- The user used this chat as an integration hub. Prompts were generated for other chats, and their responses were brought back. This established that the project was not a single linear conversation; it was a coordinated multi-chat design/implementation effort.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `1`
- `primary_report`: `2`
- `reader_brief`: `1`
- `registers`: `1`
- `spec_sheet`: `1`
- `verification`: `1`

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
