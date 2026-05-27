Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Refactor_Architecture/`
Promotion Status: not_reviewed

# Dominium + Domino Refactor Architecture - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about turning the Dominium + Domino project from a collection of partially overlapping architecture ideas into a coherent, refactorable, future-proof structure that could be implemented by Codex and then preserved for future ChatGPT conversations.

At the highest level, the discussion separated two names and responsibilities. **Domino** is the engine. It lives under `source/domino`, provides deterministic simulation, platform abstraction, graphics rendering, input, audio, UI foundations, mod/package systems, and cross-platform support. **Dominium** is the product suite built on top of Domino. It lives under `source/dominium` and contains the user-facing products: Game, Launcher, Setup, and Tools.

The chat began as a presentation-layer architecture thread: graphics, UI, UX, asset packs, sound packs, music packs, vector/raster rendering, theming, and how everything should sit on top of existing `dsys` and `dgfx` layers. That early discussion established a strong rule: no product UI or rendering path should bypass Domino's platform and graphics abstraction layers. UI should eventually become a shared toolkit usable by the game, launcher, setup, and tools, with a vector-only fallback so the system remains functional even with no raster packs installed.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, workbench. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__human_readable_chat_report.txt`.

## What Was Decided

- The most important thing to remember is that this chat did not implement the refactor. It designed the architecture and generated prompts and handoff material. Any future assistant must verify actual repository state before assuming files were moved, prompts were applied, or code was updated.
- FACT:** This early discussion created the future UI/packs design context.
- FACT:** All products should use shared `dsys` and `dgfx`. No product-specific platform or renderer code path.
- The user wanted separate version numbers for Core, Launcher, Game, Setup, Tools, and protocols. The assistant proposed independent SemVer product versions, integer format/protocol versions, and `DomProductInfo`/introspection metadata so arbitrary mixes could degrade gracefully. The user corrected one important point: **Suite version should be the Game version**, not Core version. That became a final rule.
- FACT:** Official suite releases should conventionally ship base modpack version equal to Game/Suite version.
- FACT:** Engine logic should not hardwire strict equality. Compatibility ranges should decide validity.
- The user asked about directory structure and then made a specific correction: remove `products` under Dominium. The final source structure became:
- This is a user-stated decision and one of the most important carry-forward points.
- The user then shifted from architecture implementation to preservation. They asked for prompts that would cause Codex to generate starter prompts for future ChatGPT conversations, including an extended master starter prompt. Finally, they asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat readable version of that package.
- The final phase of the chat was therefore about preserving and explaining the architecture so it could be used later without rereading the entire conversation.
- FACT:** Domino is the engine. It belongs under `source/domino` and `include/domino`. It includes the simulation, platform abstraction, graphics IR/backends, audio, input, mod/package systems, and UI foundations.
- FACT:** Dominium is the product suite built on Domino. It belongs under `source/dominium` and contains products such as Game, Launcher, Setup, and Tools.

## What Was Not Decided

- Reliability note: Repository state, Codex execution, exact version numbers, and actual file modifications are **UNCERTAIN / UNVERIFIED** unless explicitly stated otherwise.
- The most important thing to remember is that this chat did not implement the refactor. It designed the architecture and generated prompts and handoff material. Any future assistant must verify actual repository state before assuming files were moved, prompts were applied, or code was updated.
- UNCERTAIN / UNVERIFIED:** It did not establish that this system already exists in code.
- What remains uncertain is the exact degree to which existing code currently respects that boundary. The user provided a repo tree, but this chat did not inspect or modify code directly.
- Unresolved details include exact default DOMINIUM_HOME paths per OS and exact implementation of import/GC.
- Unresolved details include exact schemas, parser choice, tests, and actual code implementation.
- The key unresolved point is implementation timing. The report preserves this architecture, but the initial Codex refactor was not supposed to rewrite the entire UI system immediately.
- Actual implementation is unresolved. This chat generated architecture and prompts, not a verified changed codebase.
- Specific unresolved goals include:
- The immediate plan is not to redesign everything again. The immediate plan is to verify current repo state and then implement the structural refactor in a controlled way.
- This matters because the chat produced prompts, but did not verify that they were applied. If Codex has not run, the next step is to run or refine the master refactor prompt. If Codex has run, the next step is the consistency pass.
- Preserve FACT / INFERENCE / UNCERTAIN labels in transfer/report contexts.

## Ideas Rejected, Superseded, Or Deprioritised

- future assistants repeating rejected ideas.
- This superseded earlier structures involving `source/dominium/products`. It is one of the clearest user decisions in the chat.
- Early discussion considered unifying headless, CLI, TUI, and GUI modes into one application. That idea was not wrong, but it was superseded when the user asked for separate product binaries. The final model keeps mode selection within each product, especially Game, but not a single binary for all products.
- Separate client and server binaries were considered because the Game has client and server roles. This was rejected as the default because it increases build and compatibility complexity. It may be reconsidered for a minimal dedicated-server distribution, but only as a wrapper or specialized build, not as the default architecture.
- A separate demo product was rejected. It would duplicate Game behavior and complicate saves, mods, and compatibility. Demo should be content/profile gating through a demo base pack and instance flag.
- Installing Domino separately from Dominium was rejected. The visible reason was avoiding shared-runtime version conflicts. A future developer SDK is acceptable, but not a global player-facing runtime.
- Using `source/engine` instead of `source/domino` was rejected because it hides the named engine identity and conflicts with `include/domino`.
- Hardwiring base mod version equal to Game version inside engine logic was rejected. It should be a release convention, not a loader invariant.
- Using `x64` was rejected because the user disliked its ambiguity. Explicit tags should be used.
- This was deprioritised, not permanently rejected. The UI/packs architecture is large and should be handled after the structural source/product/versioning refactor is stable.

## What Future Work Came From It

- This chat was mainly about turning the Dominium + Domino project from a collection of partially overlapping architecture ideas into a coherent, refactorable, future-proof structure that could be implemented by Codex and then preserved for future ChatGPT conversations.
- The most important thing to remember is that this chat did not implement the refactor. It designed the architecture and generated prompts and handoff material. Any future assistant must verify actual repository state before assuming files were moved, prompts were applied, or code was updated.
- The user opened with a long "new thread" prompt framing this as the **Graphics / UI / UX / Packs Architecture Thread** for Dominium + Domino. The explicit scope was visual and audio presentation: rendering architecture, UI framework, graphics packs, sound packs, music packs, theming, skinning, pack composition, overrides, fallbacks, and how all of that should map onto existing `dsys` and `dgfx`.
- FACT:** This early discussion created the future UI/packs design context.
- The assistant then produced a master Codex refactor prompt that instructed Codex how to move files, add compat/platform headers, add product metadata and `--introspect-json`, unify Game modes, implement DOMINIUM_HOME, actions, setup import/GC, packaging naming, and docs updates.
- The user asked what Codex still did not know. The assistant audited missing topics. Then the user asked for phases from scratch; the assistant produced a phased roadmap. Then the user asked whether all phases could be merged into one big prompt; the assistant generated a larger combined refactoring prompt. Then the user requested a post-refactor consistency prompt; the assistant produced one.
- The user then shifted from architecture implementation to preservation. They asked for prompts that would cause Codex to generate starter prompts for future ChatGPT conversations, including an extended master starter prompt. Finally, they asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat readable version of that package.
- The final phase of the chat was therefore about preserving and explaining the architecture so it could be used later without rereading the entire conversation.
- The assistant recommended moving rules under `source/dominium/game/rules`, because rules are game/content-specific rather than a separate product. That specific move is an assistant recommendation incorporated into the Codex prompts. It is strongly aligned with the discussion, but it is more properly labelled **INFERENCE** unless the user later explicitly confirms it.
- Each product should use shared Domino systems. They should not contain their own platform/rendering implementations. The Game product handles runtime play/server modes. Launcher is the suite hub. Setup installs/imports/repairs/uninstalls. Tools aggregates modcheck and future tools.
- The chat began with UI and graphics packs. That material remained important but became later-phase relative to the source refactor.
- The future UI system should:

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
