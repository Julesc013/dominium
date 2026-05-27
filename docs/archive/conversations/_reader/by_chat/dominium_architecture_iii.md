Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Dominium_Architecture_III/`
Promotion Status: not_reviewed

# Dominium Architecture III: Launcher, Platform, Renderer, and Handoff Architecture - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about turning Dominium's launcher from a vague "startup UI" into a coherent, portable, extensible subsystem that fits the wider deterministic simulation architecture. The user began with the idea of tackling the launcher first, then progressively refined the requirements until the conversation covered launcher architecture, platform and renderer backends, cross-platform entry scripts, software rendering, camera/view systems, input bindings, platform support tiers, capability matrices, and finally the preservation of this chat as a reusable handoff package.

The most important background is that Dominium is not an ordinary modern game project. **FACT:** The user framed it as a deterministic, fixed-step simulation codebase with C89/C++98-era constraints. `/engine/core` and `/engine/sim` are C89, deterministic, platform-agnostic, and must not use floats. Rendering, audio, platform, UI, launcher, and tooling must not contaminate the deterministic sim. That shaped every architectural choice in the chat. The launcher could be flexible and platform-aware, but it could not blur boundaries or mutate core simulation state.

The conversation began with a launcher UI idea: common tabs such as **News, Changes, Mods, Instances, Accounts, Settings**, and bottom selectors for account, instance, platform, renderer, graphical/headless mode, and client/server role. The initial goal was to decide what the launcher should look like and how it should relate to the rest of the game. The user then clarified a major point: **FACT:** launcher settings should be used to execute separate **client or server binaries**. That means the launcher is not an in-process mode switcher. It is a process-launching configuration frontend.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, determinism, governance, platform, release, setup_launcher, simulation, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`.

## What Was Decided

- The view system then expanded beyond the launcher. **FACT:** The user wants instant zoom to any scale, instant switching between top-down 2D and first-person 3D, and arbitrary cameras for free cam, map viewing, content creation, HUD cameras, CCTV, overlays, windows, and offscreen targets. These are client/render-side concerns, not simulation concerns.
- This context matters because the rest of the conversation happened inside those constraints. The launcher could not become a dumping ground for OS-specific behavior, sim mutation, renderer decisions, or nondeterministic game-state changes. It had to fit the project's deterministic layering.
- The user then uploaded `dominium.7z`, saying it was the git repository as of that moment. **FACT:** The prior assistant said it could not open `.7z` archives in that environment. That means the actual repository state remained unverified at that stage. This became important later, because many implementation ideas were discussed without confirmed access to the repo contents.
- The user clarified: **FACT:** "The settings selected in the launcher will be used to execute client or server binaries."
- The user then specified another important constraint: **FACT:** the launcher backend should be C89, while frontend code for each binary can use C++98. The user also said client/server binaries can have single-system support.
- A **C89 launcher backend/core** owns logical decisions.
- The final direction became:
- The conversation then refined the renderer design. The assistant had discussed `vector_soft`, but the user rejected the idea of having a separate vector-only renderer. **FACT:** The user asked whether instead Dominium could have "just software renderers" capable of vector graphics and graphics using texture files on all systems as a fallback.
- These ideas were accepted as direction by continued user refinement, but implementation remains future work.
- This created one of the main unresolved issues. DX12 was discussed earlier, but omitted from the latest renderer list. X11 and Wayland were discussed earlier, but the latest platform categories are POSIX, SDL1, SDL2, and Native. Therefore, the final status is:
- The user then asked for a Codex prompt to implement and document this. That means the keybinding map was accepted enough to become implementation material, but it should still be documented as a default binding specification rather than an immutable law.
- The prior assistant summarized these files as containing two different launcher concepts: an engine-rendered launcher view and a native Win32 launcher. It also claimed the CMake file built the Win32 source for non-Windows targets. However, this report must preserve that as **UNCERTAIN / UNVERIFIED**, because the files were not re-inspected during final packaging.

## What Was Not Decided

- The user then uploaded `dominium.7z`, saying it was the git repository as of that moment. **FACT:** The prior assistant said it could not open `.7z` archives in that environment. That means the actual repository state remained unverified at that stage. This became important later, because many implementation ideas were discussed without confirmed access to the repo contents.
- This created one of the main unresolved issues. DX12 was discussed earlier, but omitted from the latest renderer list. X11 and Wayland were discussed earlier, but the latest platform categories are POSIX, SDL1, SDL2, and Native. Therefore, the final status is:
- DX12 is **UNCERTAIN / UNVERIFIED** and should not be assumed.
- X11/Wayland placement is unresolved.
- The prior assistant summarized these files as containing two different launcher concepts: an engine-rendered launcher view and a native Win32 launcher. It also claimed the CMake file built the Win32 source for non-Windows targets. However, this report must preserve that as **UNCERTAIN / UNVERIFIED**, because the files were not re-inspected during final packaging.
- This is final as a user-stated product goal. Feasibility still requires verification.
- Those outputs are important artifacts, but they are not the substance of the design. Their purpose is to preserve this chat's decisions, uncertainty, and future work for later aggregation into a master Project Spec Book.
- What remains uncertain is not the constraint itself, but how existing repository code currently enforces it. That requires code inspection.
- Uncertainty remains around how the uploaded launcher code currently maps to this desired UI. The prior assistant said the uploaded native launcher had different tabs, including Console and missing Accounts, but this must be verified.
- Uncertainty remains around aliases. Earlier names such as `dom-launcher` and `dom-setup` might be kept as aliases, but that was not finalized.
- The major unresolved issue is taxonomy: how exactly POSIX, SDL1, SDL2, and Native map to Win32, Cocoa, Carbon, X11, Wayland, headless, and retro platforms.
- The unresolved part is feasibility. Supporting Linux 2.4, Mac OS 8.5, Windows 3, and MS-DOS requires separate toolchain research. The chat did not verify that every target can be built.

## Ideas Rejected, Superseded, Or Deprioritised

- The conversation then refined the renderer design. The assistant had discussed `vector_soft`, but the user rejected the idea of having a separate vector-only renderer. **FACT:** The user asked whether instead Dominium could have "just software renderers" capable of vector graphics and graphics using texture files on all systems as a fallback.
- The conclusion was that the public fallback renderer should be `software`, not `vector_soft`. This software renderer should support both vector-only and full textured graphics. All other renderers should also support vector and graphics modes, so missing files or performance constraints do not break rendering.
- This matters because future assistants must not implement launcher logic directly in Win32 widgets, Cocoa classes, SDL callbacks, or modern C++ code.
- Uncertainty remains around aliases. Earlier names such as `dom-launcher` and `dom-setup` might be kept as aliases, but that was not finalized.
- This affects binary naming and script dispatch. It also makes capability filtering more important, because the launcher must not offer binaries that do not exist or cannot run.
- The assistant explored minimal bootstrap backends. **FACT:** The user later rejected this direction and said to use the full single implementation.
- This idea was effectively rejected when the user clarified that launcher settings execute client/server binaries. It might have been simpler for a small project, but it conflicts with the multi-binary platform/render strategy. The rejection is final unless the project later changes direction.
- The user allowed client/server binaries to be single-system. That deprioritised a universal game binary. This can be reconsidered only if the project later wants plugin-based platform/render backends.
- The conversation explored minimal launcher backends for OS compatibility. The user later rejected this and chose full single implementations. This rejection is final for now, although extreme Tier 3 support might force specialized paths later.
- `vector_soft` was superseded by `software`. This is final. Future assistants should not reintroduce `vector_soft` as a public renderer unless the user changes their mind.

## What Future Work Came From It

- The assistant generated script templates and Codex prompts for these. Those prompts should be treated as implementation artifacts, not proof that code was actually changed.
- These ideas were accepted as direction by continued user refinement, but implementation remains future work.
- The user then asked for a Codex prompt to implement and document this. That means the keybinding map was accepted enough to become implementation material, but it should still be documented as a default binding specification rather than an immutable law.
- The final phase of the chat was meta-work: extracting this chat into handoff forms. The user asked for OC-1 discovery inventory, then OC-2 registers, then a maximum-fidelity Context Transfer Packet, then a downloadable report package, then an in-chat reader version, and now this human-readable explanatory report.
- Those outputs are important artifacts, but they are not the substance of the design. Their purpose is to preserve this chat's decisions, uncertainty, and future work for later aggregation into a master Project Spec Book.
- This matters because future assistants must not implement launcher logic directly in Win32 widgets, Cocoa classes, SDL callbacks, or modern C++ code.
- The user later reversed this. The final decision was to remove minimal versions and use full single implementations. This means the architecture should not split platform/render backends into minimal and full variants unless future technical constraints force it.
- This remains a future implementation plan.
- The user asked what keybindings should be, especially F1 through F12. A canonical map was proposed and then converted into a Codex implementation prompt at the user's request.
- This matters because it standardizes future UI/game/editor behavior. It also ties into the view-mode work: F4 became the view mode cycle key.
- The keymap should be treated as accepted direction, but future implementation may still need adjustment after testing.
- This topic is important but uncertain. The files exist, but their contents were not verified during the final packaging step. Future work must inspect them before acting.

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
