Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/ui_editor_tool_editor_planning/`
Promotion Status: not_reviewed

# Dominium UI Editor and Tool Editor Planning - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was about designing a long-term UI authoring system for the **Dominium / Domino** project. The immediate practical problem was that the current Windows launcher UI "looks mangled and flickers." The broader goal was much larger: create an internal graphical toolchain that can visually design and maintain user interfaces for the launcher, setup program, game, and other Dominium tools, while preserving native platform behavior and long-term portability.

The conversation began with the user asking for help as a product designer, software architect, and prompt engineer. The user wanted the assistant to refine requirements, choose a practical tech stack, and eventually produce implementation prompts for another GPT-5.2 Codex-style coding agent. The intended output was not code written in this chat, but detailed, copy-paste-ready prompts that could be used to guide implementation inside the repository.

A crucial project fact emerged early: **FACT:** Dominium already has an in-tree UI system called **DUI**, based on a **TLV schema/state system**. The user described existing backends: a Win32 backend using common controls through `comctl32`, a DGFX backend using the Domino DGFX renderer and DSYS event pump, and a null backend for headless use. The user named important files such as `launcher_ui_v1.tlv`, `gen_launcher_ui_schema_v1.py`, `dom_launcher_app.cpp`, `dom_launcher_actions.cpp`, `dom_launcher_catalog.cpp`, `dui_win32.c`, `dui_dgfx.c`, and `dui_null.c`. **UNCERTAIN / UNVERIFIED:** Those files were named but not inspected in this chat.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, tooling, ui, workbench, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/ui_editor_tool_editor_planning/dominium_ui_editor_tool_editor_planning__human_readable_chat_report.txt`.

## What Was Decided

- The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.
- This was one of the most important structure decisions in the chat. It prevented the initial implementation from becoming too broad while preserving the long-term goal. The UI Editor would be a bootstrap tool, not the final architecture.
- The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical layout description, and the user accepted it as useful. Future work should inspect the bundles before claiming exact screenshot fidelity.
- The final state of the conversation is therefore not "the tool is built," but "the architecture, constraints, prompt plans, and continuation state have been carefully documented."
- The most important technical discovery was that the project already has a UI system. **FACT:** The user described the current launcher GUI as the Dominium UI, or DUI, schema/state system using TLV. It has at least three backends: Win32 common controls through `comctl32`, DGFX through Domino's renderer/event pump, and a null backend.
- What remains uncertain is the actual state of the code. The user named files, but the chat did not inspect the repository. A future assistant must verify exact paths, build targets, TLV parser implementation, and current launcher behavior.
- FACT:** The user explicitly chose to make the UI Editor first. This first tool is a minimal Windows-only editor that can visually edit layouts and generate TLV directly. **FACT:** The Tool Editor comes later and is intended to become the full first-class DUI authoring environment.
- This matters because the final Tool Editor is too large to build as the first move. The UI Editor is a bootstrap tool. It should become capable enough to create the Tool Editor's own UI. Then the Tool Editor can eventually edit itself, the setup program, the launcher, the game, and other tools.
- The tension here is that the user wants the final Tool Editor to avoid hardcoded limitations. The assistant recommended allowing a minimal hardcoded docking substrate in the earliest Tool Editor version if necessary, but this remains tentative. The user clearly prefers the eventual Tool Editor to be free of hardcoded limitations.
- Native widgets were a recurring theme. **FACT:** The user wanted true OS controls, not merely native-looking custom rendering. This means real Win32 controls on Windows, and eventually platform-native controls on other systems where possible.
- This topic matters because the UI Editor must be powerful enough to build the future Tool Editor. A simple absolute-position-only editor would not be enough for complex tool layouts. Splitters, tabs, and scroll panels became especially important because the Tool Editor itself needs hierarchy panes, property inspectors, canvas areas, logs, tabs, and scrollable panels.
- This is a strong planned design, but some details remain assistant recommendations rather than explicit user-confirmed decisions. Future implementation should preserve that uncertainty if writing a formal spec.

## What Was Not Decided

- The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.
- The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical layout description, and the user accepted it as useful. Future work should inspect the bundles before claiming exact screenshot fidelity.
- What remains uncertain is the actual state of the code. The user named files, but the chat did not inspect the repository. A future assistant must verify exact paths, build targets, TLV parser implementation, and current launcher behavior.
- Unresolved details include the actual TLV wire format, migration strategy from `launcher_ui_v1.tlv`, and how much legacy data can be preserved during import.
- The unresolved risk is implementation complexity. Real native tab controls, splitter behavior, and scroll panels can be nontrivial in a child-HWND Win32 UI.
- This is a strong planned design, but some details remain assistant recommendations rather than explicit user-confirmed decisions. Future implementation should preserve that uncertainty if writing a formal spec.
- The unresolved issue is that the uploaded screenshot bundles were not inspected. The logical specs are accepted planning artifacts, not verified screenshot extractions.
- The exact scope of IDE-native live editing remains unresolved. The assistant proposed preview hosts, but it is not confirmed whether that fully satisfies the user's desire to use Visual Studio, Xcode, and Linux GUI tools.
- The exact first implementation status is unresolved. The chat generated prompts but did not show Codex execution results.
- UNCERTAIN / INFERENCE:** The assistant generated a preview-host strategy. It was a reasonable way to integrate Visual Studio, Xcode, and Linux tools while preserving DUI TLV as canonical. But the user did not confirm whether this satisfies "utilising all GUI tools available in each IDE."
- The sixth tradeoff was IDE-native editing. Visual Studio and Xcode have their own native designer ecosystems, but those do not naturally edit DUI TLV. The preview-host proposal preserves DUI as canonical while using IDE build/run/watch loops. This is practical but may not fully satisfy a desire for direct IDE designer manipulation. That is why it remains unresolved.
- What must happen before it: verify launcher/setup build targets and loader integration points.

## Ideas Rejected, Superseded, Or Deprioritised

- The conversation spent significant effort on safe data handling. The user selected the safest proposed approach: a canonical in-memory document model that writes deterministic TLV. This rejected direct TLV byte patching.
- FACT:** The user selected the canonical edit model. The reasoning was maintainability and safe data handling. Direct TLV byte patching was rejected because it is brittle. A separate hand-edited JSON source was not selected because the user did not see the need for manual editing if a UI Editor exists.
- This matters because Phase A is Windows-only, but the schema must not become Windows-only.
- This affects UU4 and UU5. Future assistants must not introduce custom styling unless the user later changes the requirement.
- This was superseded by the user's repeated requirement that the Tool Editor and tools eventually support all systems/products. Windows-first is a bootstrapping tactic, not the final architecture.
- This was rejected because it is unsafe and hard to maintain. The canonical IR approach was chosen instead.
- This was rejected explicitly by the user. The launcher/setup tests should copy logical layout patterns, not visual skin.
- This was rejected by the clarification that launcher/setup should use native Win32 widgets only. Owner-draw or custom styling would undermine the purpose of testing the native-widget pipeline.
- This was not explicitly argued as a formal rejected item by the user, but the entire direction of the chat makes it a rejected or deprioritized path. The project has DUI; the user wants native controls, offline-compatible dependencies, and in-tree tooling. External framework replacement would conflict with those constraints.
- The sixth tradeoff was IDE-native editing. Visual Studio and Xcode have their own native designer ecosystems, but those do not naturally edit DUI TLV. The preview-host proposal preserves DUI as canonical while using IDE build/run/watch loops. This is practical but may not fully satisfy a desire for direct IDE designer manipulation. That is why it remains unresolved.

## What Future Work Came From It

- The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.
- Once the architecture was clear, the user asked for a prompt plan that could implement everything in fewer than a dozen Codex prompts. The assistant created an 11-prompt implementation sequence:
- The user then asked "Next" repeatedly, and the assistant generated each of those prompts in detail. These prompts are important artifacts, but they are not evidence that implementation occurred.
- This led to a second prompt plan: UU1 through UU6. These prompts extended the UI Editor with discovery/import/export, CLI modes, `ops.json` scripted editing, launcher UI generation, setup UI generation, and determinism/CI hardening.
- Before the launcher/setup prompts, the user clarified that "Minecraft style" meant logical layout only, not graphical design. This was crucial. The assistant had to avoid custom styling, skins, or owner-drawn controls. The launcher and setup tests were about structure: header areas, side navigation, main content tabs, news panels, wizard steps, progress pages, footer buttons, and similar interaction flow.
- The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical layout description, and the user accepted it as useful. Future work should inspect the bundles before claiming exact screenshot fidelity.
- The final state of the conversation is therefore not "the tool is built," but "the architecture, constraints, prompt plans, and continuation state have been carefully documented."
- The discussion also identified likely flicker causes. The Win32 backend is mostly child HWND controls and does not use custom painting. Flicker likely comes from resize relayout, redraw calls, list refresh invalidation, and visibility toggles. This later led to a planned prompt for structural Win32 batching and coalesced relayout.
- What remains uncertain is the actual state of the code. The user named files, but the chat did not inspect the repository. A future assistant must verify exact paths, build targets, TLV parser implementation, and current launcher behavior.
- For Phase A, the UI Editor is much simpler: Windows only, system DPI only, design scale 100%. For the Tool Editor, the user wants per-monitor DPI with fallback and multiple design scales. The difference between these scopes is important. Future assistants should not accidentally impose the Tool Editor's full DPI/scale requirements on the first UI Editor.
- This topic matters because the UI Editor must be powerful enough to build the future Tool Editor. A simple absolute-position-only editor would not be enough for complex tool layouts. Splitters, tabs, and scroll panels became especially important because the Tool Editor itself needs hierarchy panes, property inspectors, canvas areas, logs, tabs, and scrollable panels.
- The planned event system uses a unified C-compatible `domui_event` structure. This lets Win32, DGFX, null, and future backends dispatch events consistently. The stable action key strategy also supports Codex automation: a script can bind `launcher.nav.play` to a button without needing to know a C++ function pointer or numeric ID in advance.

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
