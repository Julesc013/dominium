Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/dominium_domino_codex_planning/`
Promotion Status: not_reviewed

# Dominium + Domino Codex Planning and Handoff - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about preserving and developing the implementation plan for the **Dominium + Domino** project. **FACT:** The user began by giving an extended master prompt that defined the architecture, philosophy, constraints, and product model for Dominium and Domino. In that project model, **Domino** is the deterministic, fixed-point, ISO C89 engine layer, and **Dominium** is the C++98 product suite built on top of it. The product suite includes the game, launcher, setup tool, and development tools such as modcheck and future editors. The chat's early work was to turn that broad architecture into a practical forward plan and then into self-contained Codex prompts that could be used to implement the project incrementally.

The most important problem this chat tried to solve was **scope control**. The user's initial architecture covered a very large target: deterministic simulation, many platform backends, many renderers, retro targets, GUI/TUI/CLI product shells, packs, mods, setup, replay, networking, hydrology, climate, AI/jobs, power/fluid/logic networks, and compatibility rules. The assistant recommended not trying to build everything at once. The central implementation idea became a **Milestone-0 vertical slice**: prove the architecture with the smallest useful chain first. That chain was launcher -> repository/manifest -> game product -> deterministic headless simulation -> checksum/save file. Everything else would be layered on afterward.

From that recommendation, the chat produced a sequence of **six Codex prompts**. These prompts were not merely rough suggestions; they were written as copy-paste implementation instructions for Codex. They covered: creating canonical docs, setting up the repo/CMake skeleton, implementing fixed-point numeric types and deterministic RNG, adding the DOMINIUM_HOME repo model and product manifests, building a minimal deterministic sim with TLV save/load, and wiring launcher-to-game process spawning through dsys. **FACT:** These prompts were generated in the chat. **UNCERTAIN / UNVERIFIED:** The chat does not establish that the prompts were actually executed against the repository.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, workbench, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/dominium_domino_codex_planning/dominium_domino_codex_planning__human_readable_chat_report.txt`.

## What Was Decided

- INFERENCE:** The user accepted this direction in practice, because the next request was to generate Codex prompts to implement each step fully. The user did not explicitly say, "I formally approve the Milestone-0 plan," but they proceeded to ask for prompts based on it.
- The user then asked for recommendations. The assistant recommended a clean startup policy: explicit flags first, no environment/config override in v1, terminal detection through dsys, generic AUTO behavior, product-specific headless handling for the game, build-time GUI/TUI capabilities, and structural error codes for fallback. The user accepted this enough to request a "one big Codex prompt" to implement it.
- However, the later context transfer packet treated that inspection claim as **UNCERTAIN / UNVERIFIED**. This was careful and correct: within the visible chat, there was no reliable tool trace proving the repo had actually been inspected. Therefore, future assistants must verify `dominium.zip` or the active checkout before relying on the platform/render/API answer.
- The core topic was the architecture of the Dominium + Domino project. **FACT:** The user defined Domino as a deterministic, fixed-point, C89 engine layer and Dominium as a C++98 product suite. This matters because every implementation decision had to respect those boundaries.
- The conclusions were clear: future code must not bypass dsys or dgfx, deterministic sim must not use host floating-point, product code should not directly call OS APIs, and old content must not silently break. These are not just preferences; they are the governing rules of the project.
- The numeric core was central because deterministic simulation depends on it. The generated prompt specified fixed-point types, deterministic RNG, saturating arithmetic, and a numeric test harness.
- The unresolved complication is C89 portability. Standard C89 does not provide `long long`, but `u64`, `i64`, and `q48_16` require 64-bit representation. Future work must decide whether to allow compiler extensions, emulate 64-bit values for strict retro targets, or define platform tiers with conditional support.
- Prompt 4 translated this into a minimal repo manifest system. It proposed product manifests, compatibility profile fields, and a launcher path that loads a primary game product. This was important because the launcher->game relationship is central to Dominium as a product suite.
- The unresolved issue is that the prompt's minimal manifest parser and hardcoded platform path are only a starting point. A real implementation must generalize product discovery, avoid duplicated path logic, and preserve compatibility/versioning rules.
- This topic matters because GUI/TUI text and input behavior must be portable and deterministic. The proposed input system normalizes raw dsys events into deterministic Domino input events. The state machine framework gives products a common way to manage screens and workflows. The IME layer abstracts platform-specific text composition.
- The unresolved issue is API alignment. The prompt proposed new APIs, but the actual repo's dgfx API may already differ. The final report therefore recommends verifying current render headers and backend code before applying the prompt.
- This is important because packs are central to Dominium's content architecture. The user's master prompt required vector fallback, raster skins, sound/music packs, asset formats, pack discovery/versioning/dependencies, overrides, and fallback rules.

## What Was Not Decided

- The most important things to remember are: the project's strict architecture constraints, the Milestone-0 prompt sequence, the later shared CLI/TUI/GUI/input/render prompt sequences, the missing pack-system prompt, the unified startup policy, the unresolved repo-verification issue, and the need to treat generated prompts as plans rather than proof of implementation.
- The assistant generated the first two prompts. The third was never produced because the conversation changed direction. That missing third prompt remains an important unresolved item.
- However, the later context transfer packet treated that inspection claim as **UNCERTAIN / UNVERIFIED**. This was careful and correct: within the visible chat, there was no reliable tool trace proving the repo had actually been inspected. Therefore, future assistants must verify `dominium.zip` or the active checkout before relying on the platform/render/API answer.
- What remains uncertain is how much of this architecture already exists in the current repo and how much is still planned. The chat produced prompts and plans, but it did not prove execution.
- The unresolved issue is whether those prompts were ever run and whether the generated code, if any, conforms to the project's strict C89/C++98 and determinism requirements.
- The unresolved complication is C89 portability. Standard C89 does not provide `long long`, but `u64`, `i64`, and `q48_16` require 64-bit representation. Future work must decide whether to allow compiler extensions, emulate 64-bit values for strict retro targets, or define platform tiers with conditional support.
- The unresolved issue is that the prompt's minimal manifest parser and hardcoded platform path are only a starting point. A real implementation must generalize product discovery, avoid duplicated path logic, and preserve compatibility/versioning rules.
- The unresolved issue is whether the prompts are too broad and whether the existing repo already has overlapping modules. Future work should inspect the repo before applying these prompts.
- What remains uncertain is how much of this already exists in the repo and how realistic cross-platform IME is for early implementation. IME is often platform-specific and complex, so the generated prompt should probably be applied carefully or split.
- The unresolved issue is API alignment. The prompt proposed new APIs, but the actual repo's dgfx API may already differ. The final report therefore recommends verifying current render headers and backend code before applying the prompt.
- The unresolved work is to generate this prompt, ideally after inspecting actual content/pack docs and source files. The prompt should probably be staged, because pack integration touches content loading, dependency resolution, audio, rendering, shader compilation, GUI themes, vector icons, and streaming.
- This topic remains important but unresolved in implementation. The policy is strong, but the implementation prompt needs repair to avoid linking problems. The safer approach is to keep the generic mode-selection algorithm independent of product-specific symbols, likely through callback tables or product-local dispatchers.

## Ideas Rejected, Superseded, Or Deprioritised

- The conclusions were clear: future code must not bypass dsys or dgfx, deterministic sim must not use host floating-point, product code should not directly call OS APIs, and old content must not silently break. These are not just preferences; they are the governing rules of the project.
- The most important rejected idea was trying to build the entire architecture at once. It was not rejected because it was wrong; it was rejected because it was too broad for the first implementation pass. The assistant recommended focusing on a Milestone-0 vertical slice first. This rejection is temporary. After the vertical slice works, broader platform/render/sim systems become relevant again.
- Starting with complex systems such as hydrology, AI/jobs, ECS, networking, or full worldgen was also deprioritized. The rationale was that these systems depend on deterministic numeric, RNG, tick, save/load, and replay foundations. Building them before the foundations would create hidden instability.
- A huge up-front dsys/dgfx abstraction was also deprioritized. The assistant recommended growing those APIs through real use cases. This avoids architecture becoming abstract but untested.
- The idea of falling back from GUI/TUI to another mode on any error was rejected in the recommendation. Only structural unsupported errors should trigger fallback. If the GUI launches successfully but encounters a real content/config error, hiding that by dropping to TUI or CLI would make debugging harder.
- Including headless as part of AUTO startup fallback was also rejected. Headless is a game/server mode, not a user interface fallback. It should be explicit or triggered by server flags.
- Duplicated product-specific CLI/TUI/GUI pipelines were rejected because they conflict with the user's shared-common-components goal.
- OS-native product drawing was rejected by the master architecture because all rendering must go through dgfx.
- C++11+ and floating-point deterministic sim were rejected by the user's constraints.
- Old saves, mods, packs, tools, and instances must not silently break.

## What Future Work Came From It

- The most important things to remember are: the project's strict architecture constraints, the Milestone-0 prompt sequence, the later shared CLI/TUI/GUI/input/render prompt sequences, the missing pack-system prompt, the unified startup policy, the unresolved repo-verification issue, and the need to treat generated prompts as plans rather than proof of implementation.
- The user then asked for a plan going forward. The assistant produced a phased plan covering specification consolidation, directory/CMake layout, dsys, dgfx, UI core, DOMINIUM_HOME metadata, launcher v0, game v0, tools, packs, retro backends, replay/networking, and documentation/examples.
- INFERENCE:** The user accepted this direction in practice, because the next request was to generate Codex prompts to implement each step fully. The user did not explicitly say, "I formally approve the Milestone-0 plan," but they proceeded to ask for prompts based on it.
- The user asked for six Codex prompts and reminded the assistant about supported numeric formats: `U8`, `I8`, `U16`, `I16`, `Q4.12`, `U32`, `I32`, `q16.16`, `Q24.8`, `u64`, `i64`, `q48.16`, and similar formats. That correction mattered because it broadened the numeric core beyond only Q16.16/Q24.8.
- The assistant then generated six long prompts:
- 1. **Prompt 1** created `SPEC_IDENTITY.md` and `SPEC_PRODUCTS.md`, documentation only.
- 2. **Prompt 2** created the canonical repo layout, CMake skeleton, core headers, and product stubs.
- 3. **Prompt 3** implemented deterministic numeric core types, fixed-point operations, RNG, and a numeric test harness.
- 4. **Prompt 4** added the DOMINIUM_HOME repo model, product manifest loading, and launcher enumeration.
- 5. **Prompt 5** added a minimal deterministic sim, headless game loop, checksum, and TLV save/load.
- 6. **Prompt 6** added dsys process spawning and made the launcher run the game.
- These prompts were written as implementation tasks for Codex. They included file paths, APIs, CMake changes, example code, and output expectations. The purpose was to allow Codex to operate with enough context even in a separate session.

## Important Artifacts

- `manifest`: `1`
- `markdown`: `1`
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
