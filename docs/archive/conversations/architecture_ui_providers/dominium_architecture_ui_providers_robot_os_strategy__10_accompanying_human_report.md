# Accompanying Human-Readable Report — Dominium Architecture, UI, Providers, and Robot OS Strategy

Date anchor: 2026-05-27 Australia/Melbourne  
Scope: This chat and the preservation package generated from it.  
Purpose: This companion report is meant to be read beside the larger preservation package. It restates the substance of the whole conversation in a more narrative and implementation-oriented form, with emphasis on what was discussed, what was decided, what was deferred, what remains uncertain, and what should happen next.

---

## 1. Executive Summary

This conversation converged several separate Dominium planning threads into one coherent architecture and design direction.

At the beginning, the focus was technical: how to rebuild the GUI and binary surface of Dominium so that every product works through CLI, every product has a TUI path or deterministic TUI stub, and GUI support is modular rather than becoming duplicated product architecture. That led into repository structure, product-shell boundaries, platform families, renderer support, native/OEM+ applications, and build/distribution strategy.

The discussion then broadened into the project’s deeper architectural doctrine: Dominium should be built like a long-lived platform or OS-grade game engine project, not a one-off indie codebase. The core pattern became **service-first, provider-backed, profile-selected, contract-governed, third-party-fenced, evidence-tested**. In plain terms: Dominium owns the stable service contracts and data law; external or replaceable implementations satisfy those contracts as providers; product profiles select valid provider combinations; validators and tests enforce the boundaries.

The project baseline also changed during the conversation. Instead of continuing to optimize around C89/C++98 and very old host targets, the user established a new mainline floor: **C17 + C++17**, targeting **Windows 7 SP1+, Mac OS X 10.9.5+, and Linux**. That substantially changed the renderer plan. Old fixed-function renderers such as OpenGL 1.1 and OpenGL 2.1, and old Direct3D generations such as DirectX 5/7/8/9, can now be deferred indefinitely as research or back-port lanes. The first direct hardware renderer should be OpenGL 3.3, followed by Direct3D 11, then Metal, Vulkan, and Direct3D 12 later. The raylib ecosystem can be used aggressively as an early visible provider suite, but it must remain fenced behind Dominium service contracts.

The conversation also produced a strong UI architecture. CLI, TUI, rendered GUI, native GUI, headless, and future immersive/VR interfaces should not become separate systems. They should be projections of the same command/action/result/document/view/patch model. Workbench becomes the authoring environment for these UI documents: views, widgets, layouts, themes, HUDs, workspaces, TUI panels, rendered screens, and validation artifacts.

The largest game-design pivot was explicit: Dominium should be a **robotic seed-civilisation game**, not a labour-management game. Players are robots or machine consciousnesses. A mothership provides knowledge, starter resources, spawn fabrication, and an AI planner. The planet is generated from science-bound parameters. Players survey, mine, refine, fabricate, build cities, construct spawn labs, automate industry, and eventually terraform or build megaprojects. The simulation emphasizes energy, materials, machines, logistics, sensors, permissions, heat, maintenance, and infrastructure, not human worker NPCs.

The final UX synthesis is that the game should feel like a **robot operating system**. The player boots into an OS-like shell, enters a universe, downloads consciousness into a fabricated robot body, and uses the same UI code for menus, Workbench, CLI, TUI, rendered HUD, native shells, and eventually VR. UI customization should be deep and player-driven, but it must obey diegetic epistemics: sensors, network latency, permissions, confidence, staleness, fog-of-war, backups, and protected warnings.

The strongest immediate next actions are:

1. Build **PROVIDER-WEDGE-01**: provider manifests, forbidden include checks, null providers, raylib/rlgl/rlsw/raygui/raudio providers, SDL2/Lua preparation, and first client/workbench/server profiles.
2. Build **ROBOT-OS-WEDGE-01**: one shared view such as `view.node.status`, projected through command, text, rendered OS, and body HUD surfaces.
3. Extract the robotic seed-civilisation and Robot OS material into formal design/spec documents.
4. Verify stale external facts before implementation: raylib, SDL2, Lua, Windows 7 SP1, Mac OS X 10.9.5, OpenGL 3.3, Direct3D 11, toolchains, licenses, and the live repo tree.

---

## 2. What This Conversation Was Trying to Solve

The conversation was driven by one repeated problem: Dominium must not become an accidental pile of product-specific code, renderer-specific code, framework-specific GUI surfaces, or directory-structure accidents. The user wanted a project that could survive complete rewrites, replacement of providers, new renderers, new tools, new games built on Domino, future back-ports, and future platform expansions.

The technical problem was therefore not just “which GUI framework?” or “which renderer?” The deeper problem was how to define architectural ownership so the project can grow for years without locking itself into one framework, one platform, one renderer, one UI style, or one game-specific implementation.

The design problem was similar. The game needed a premise that explains the mechanics instead of fighting them. By choosing robotic seed civilisation, the project gains diegetic explanations for HUDs, blueprints, construction markers, fog-of-war, spawning, automation, and missing human labour. The UI/UX can then become the player’s machine operating system rather than a conventional game menu layer.

---

## 3. Chronological Development of the Chat

### 3.1 GUI and binary rebuild baseline

The chat began with a transfer knowledge base about rebuilding Dominium’s GUIs and binaries from scratch. The starting doctrine was:

- CLI is mandatory.
- TUI is expected.
- GUI is optional/modular.
- GUI shells attach to shared product backends.
- Host integration, visual profile, and product logic stay separate.
- There should not be one universal GUI framework or one GUI per OS version.

Products in scope included setup, launcher, client, server, and tools.

### 3.2 Live repository context

The user then pointed to `julesc013/dominium` as the latest live implementation baseline. The response treated repo docs and code as the implementation source of truth where available and connected the discussion to existing AppShell, UI-mode, release, component-matrix, and layout-convergence concepts.

### 3.3 Directory structure convergence

The user described the repository as a “jumped mess” and wanted fewer, more intuitive top-level folders. The conversation first proposed a generic industry-style tree, then refined it into a Dominium-specific ownership layout. The key doctrine became:

- Top-level folders should answer “what architectural layer owns this?”
- They should not answer “what topic is this?”
- Domain material must be split by content type: code, schema, registry, data, docs, fixtures, packs.
- Product app folders should contain thin entrypoints, not product truth.
- Runtime and AppShell should be separate concepts.
- Contracts, schemas, registries, protocols, capabilities, stability, replay, and ABI belong under contracts.

Later pasted audit material stated that the top-level roots were largely cleaned, with residual issues in schema taxonomy, pack internal layout, runtime/engine residual taxonomy, AIDE state classification, and report bundle integrity.

### 3.4 Platform and renderer planning

The discussion then moved to supported platforms and renderers. Early planning included a large matrix of null, software, OpenGL, Direct3D, Metal, Vulkan, Win32, Cocoa, X11, Wayland, SDL, AppKit, GTK, WinForms, SwiftUI, WinUI, Qt, Android, and old/retro lanes.

As the language and platform floor changed to C17/C++17 and Windows 7 SP1 / Mac OS X 10.9.5 / Linux, the plan narrowed. Old fixed-function and pre-Windows-7 renderer paths were deprioritized. OpenGL 3.3 became the first direct hardware renderer, Direct3D 11 became the first Windows-specific hardware renderer, and Metal/Vulkan/DX12 became later lanes.

### 3.5 Software renderer and vector2d correction

The user questioned `vector2d` and whether it should be covered by `soft`. The conclusion was that `vector2d` should not be a renderer backend. It belongs to a renderer-independent drawing/canvas layer. The software renderer is a CPU framebuffer backend used for fallback, golden tests, CI, screenshots, evidence generation, and proof that UI does not require GPU APIs.

### 3.6 General coding and architecture practices

The user asked what practices would make the project truly portable, modular, extensible, and future-proof. The answer introduced stable contracts, replaceable implementations, semantic IDs separate from paths, versioned ABI/API boundaries, chunked file formats, migration tests, provider conformance tests, naming discipline, public header standards, forbidden include checks, and evidence-based support claims.

### 3.7 Shared UI and Workbench architecture

The user then explored how CLI, TUI, rendered GUI, and OS-native GUI could share behavior. The final model was a shared command/action/result/document/view/patch/projection spine. Workbench should edit Dominium UI documents and preview/validate them through different projections. It should not edit provider-specific objects as source of truth.

### 3.8 Raylib, SDL2, Lua, and provider architecture

The user pasted prior-chat material arguing for raylib use. The final synthesis was more refined: raylib, rlgl, rlsw, raygui, raudio, rtextures, rmodels, SDL2, and Lua should be used aggressively as providers, but fenced. Dominium owns the service contracts, packets, UI documents, saves, replays, packs, assets, commands, and game law.

### 3.9 Robotic seed-civilisation game design

The user introduced a decisive game-design direction: Dominium should be a robotic seed-civilisation game, not a labour-management game. The player is a robot avatar or machine consciousness. The mothership is the source of knowledge, early spawn fabrication, starter resources, and AI planning. The planet is procedurally generated from science-bound parameters. Gameplay centers on exploration, surveying, mining, refining, fabrication, city-building, spawn labs, logistics, automation, terraforming, and megaprojects.

### 3.10 Robot OS UI/UX

The final design step was to connect the robotic premise to UI/UX. The player should feel like they are booting into an operating system. They can use command, text, rendered, native, or immersive shells. When embodied in a robot body, the same UI system becomes the HUD. Custom themes, layouts, widgets, workspaces, terminals, HUDs, and accessibility profiles become packable artifacts. The UI must obey sensor knowledge, permissions, staleness, latency, confidence, fog-of-war, and protected warning classes.

### 3.11 Preservation package

The user then uploaded a preservation prompt requiring a maximum-fidelity report and export package. The prior package was generated with human-readable report, context transfer packet, spec sheet, registers, aggregator packet, reader brief, verification/audit file, bootstrap prompt, in-chat reader, and a ZIP package. This companion report extends that package and rebundles it.

---

## 4. Major Decisions and Their Status

### 4.1 Accepted or explicit decisions

1. **Dominium should use service-first/provider-backed/profile-selected architecture.**  
   Status: accepted synthesis.  
   Reason: allows raylib/SDL/Lua/native APIs/custom renderers to be used without becoming core law.

2. **C17 + C++17 is now the mainline baseline.**  
   Status: explicit user statement.  
   Reason: updates code practices and deprecates older C89/C++98 constraints.

3. **Current main platform floor is Windows 7 SP1, Mac OS X 10.9.5, and Linux.**  
   Status: explicit user statement; external details still need verification.  
   Reason: sets renderer/toolchain priorities.

4. **OpenGL 3.3 should come before Direct3D 11 for direct renderer work.**  
   Status: accepted direction.  
   Reason: helps early Mac/Linux/Windows cross-platform shader work.

5. **Direct3D 11 should be the primary Direct3D baseline.**  
   Status: accepted direction.  
   Reason: Windows 7 support makes older DirectX generations unnecessary for first-wave.

6. **OpenGL 1.1/2.1 and Direct3D 5/7/8/9 can be deferred indefinitely.**  
   Status: explicit user direction.  
   Reason: new platform floor allows shader-first architecture.

7. **`vector2d` should not be a renderer backend.**  
   Status: accepted synthesis.  
   Reason: vector/drawing/canvas is a layer above render backends.

8. **raylib ecosystem is seed provider suite, not engine architecture.**  
   Status: accepted synthesis.  
   Reason: fast progress without lock-in.

9. **Workbench edits Dominium UI documents, not raygui/raylib/provider objects.**  
   Status: accepted synthesis.  
   Reason: keeps UI portable across CLI/TUI/rendered/native/immersive projections.

10. **Dominium is a robotic seed-civilisation game, not a labour-management game.**  
    Status: explicit user decision.  
    Reason: resolves HUD, spawning, automation, labour, fog-of-war, construction, and lore tensions.

11. **The UI should feel like a customizable Robot OS.**  
    Status: explicit user direction and accepted synthesis.  
    Reason: makes menus, Workbench, HUD, and diegetic epistemics one coherent system.

12. **Third-party types must not cross into contracts, saves, replays, packs, game law, or public SDK.**  
    Status: accepted hard constraint.  
    Reason: prevents long-term contamination.

### 4.2 Important tentative or unresolved decisions

- Exact Lua provider version: `lua54` vs `lua55` remains unresolved.
- Exact Linux baseline remains unresolved.
- Unreal’s future role remains unresolved.
- First playable vertical slice remains unresolved.
- Exact official-server UI customization rules remain unresolved.
- Exact consciousness backup/disconnect/body persistence rules remain unresolved.

---

## 5. What Was Put Off for Later

The conversation intentionally deferred several things.

### 5.1 Old renderers and retro platforms

Deferred indefinitely or moved to research/back-port:

- OpenGL 1.1
- OpenGL 2.1
- Direct3D 5, 7, 8, 9
- Windows 2000/XP/Vista-specific paths
- DOS, Win16, Win9x
- Carbon/classic Mac/PowerPC
- old fixed-function-first graphics

These are not deleted as ideas. They are simply not first-wave architecture.

### 5.2 Direct native/custom providers

Custom Win32, Cocoa, X11, Wayland, direct OpenGL 3.3, Direct3D 11, Metal, and Vulkan providers can be implemented later. Their service slots should exist from day one, but raylib/SDL2 can provide the first working implementations.

### 5.3 Advanced language standards

C23, C++20, C++23, C++26, and bare-metal/custom-all-the-way-down paths are future research/tool/provider lanes, not current mainline baseline.

### 5.4 Full Workbench editor

A full Interface Studio, Theme Lab, Renderer Sandbox, and HUD editor are later steps. The first proof should be much smaller: a shared `view.node.status` or validation dashboard projected through command/text/rendered surfaces.

### 5.5 Deep world simulation systems

Full climate, hydrology, groundwater, landslides, ecology, atmospheric chemistry, and advanced terraforming are later field systems. The early gameplay should focus on surveying, cut/fill, material movement, construction validation, power, logistics, spawn labs, and machine graphs.

---

## 6. Open Questions

1. **Lua 5.4 or 5.5?**  
   Need to pin one provider and define `dominium.script.v1` separately.

2. **What is the exact Linux baseline?**  
   Need glibc/toolchain/windowing baseline and packaging expectations.

3. **How will Unreal fit later, if at all?**  
   Prior discussion mentioned Unreal for local presentation, but the current first provider wedge is raylib/SDL2. This needs strategic clarification.

4. **What is the first playable vertical slice?**  
   Candidate: boot OS → node status → body link → survey → mine → refine → fabricate → build simple power/storage/spawn component.

5. **What UI customization is allowed on official servers?**  
   Needs a threat model for themes, layouts, scripts, automation, overlays, macros, and protected warnings.

6. **How exactly do consciousness backup, disconnect, and body persistence work?**  
   This is core to the Robot OS fantasy and server fairness.

7. **What is the current live repo truth?**  
   The pasted repo audit said structure is mostly clean with warnings. Future work should verify the actual current repo before applying old cleanup tasks.

---

## 7. Risks and Failure Modes

### 7.1 Technical risks

- raylib becomes architecture rather than provider.
- SDL2/raylib/Lua types leak into contracts or saves.
- Apps become provider-specific variants instead of generic products.
- Software renderer is skipped and OpenGL becomes the correctness baseline.
- Workbench edits provider-specific objects instead of Dominium documents.
- Support claims are made without build/boot/smoke/conformance evidence.
- Repo structure regresses into topic or vendor roots.

### 7.2 Design risks

- Robotic seed civilisation becomes too broad and never reaches a playable loop.
- Nanotech becomes magic construction and invalidates logistics.
- The mothership invalidates progression by fabricating too much.
- Machine/city simulation becomes too detailed too early.
- Field layers are not separated by conservation requirements.

### 7.3 UI/UX risks

- Deep customization becomes cheating.
- Themes hide critical warnings.
- Fog-of-war is visual only, not server-authoritative.
- TUI/CLI/rendered/native shells diverge semantically.
- Robot OS becomes decorative rather than tied to permissions, sensors, latency, backups, and confidence.

---

## 8. Best Immediate Implementation Plan

### 8.1 PROVIDER-WEDGE-01

Purpose: establish provider architecture without letting raylib/SDL/Lua contaminate core law.

Deliverables:

- `contracts/provider/provider.schema.json`
- `contracts/capability/provider_capability.schema.json`
- third-party manifests and license records
- forbidden include validator
- null providers
- raylib provider
- rlgl provider
- rlsw provider
- raygui provider
- raudio provider
- raylib asset import provider
- client/workbench/server profiles

Acceptance tests:

- Client opens a window.
- Workbench opens a simple rendered UI.
- Rect/text/debug scene draws.
- One image loads.
- One audio smoke plays.
- rlsw or memory framebuffer exports an image.
- Server/headless runs with null providers.
- Deterministic sim/replay path does not depend on raylib.
- Forbidden include validator passes.

### 8.2 ROBOT-OS-WEDGE-01

Purpose: prove the UI model with one shared view.

Suggested first view:

```text
view.node.status
```

It displays:

- identity
- current node
- universe
- backup age
- available bodies
- link quality
- known sensor map
- warnings
- available actions

Project it as:

- command output
- text panel
- rendered OS screen
- body HUD panel

Acceptance:

- Same data source and actions across projections.
- No UI projection reads private state directly.
- Critical warnings cannot be hidden.
- Source/confidence/staleness metadata can be shown.

### 8.3 ROBOTIC-SEED-SPEC-01

Purpose: extract the game design doctrine into a formal spec.

Core chapters:

- player identity and bodies
- mothership economy
- spawn labs
- sensor/fog epistemics
- nanotech construction
- field layer stack
- machine graph compiler
- city progression
- AI planner tasks
- official/private/single-player modes

### 8.4 UI-CUSTOMIZATION-SAFETY-01

Purpose: define what UI mods can and cannot do.

Must cover:

- themes
- layouts
- widgets
- command aliases
- scripts/macros
- automation
- protected alert classes
- official server restrictions
- accessibility guarantees

---

## 9. What Future Assistants Must Not Forget

- The user does not want a shallow summary; preserve nuance and decisions.
- The game is now a robotic seed-civilisation game.
- The UI is now a Robot OS concept, not just HUD skins.
- CLI/TUI/rendered/native/immersive are projections, not separate products.
- raylib/SDL/Lua are providers, not architecture.
- Services are first-party; providers are replaceable.
- Profiles select providers; apps stay generic.
- Third-party types must not cross into contracts, saves, replays, packs, game law, or public SDK.
- OpenGL 3.3 and D3D11 are the first direct hardware renderer priorities under the new floor.
- Old renderers/platforms are deferred, not erased.
- Workbench is an artifact authoring environment for UI/docs/views/themes/layouts/widgets, not a one-off editor.
- Fog-of-war, UI data, and map knowledge must be epistemically constrained by sensors, permissions, confidence, staleness, and network paths.

---

## 10. Contents of the Updated Bundle

This updated bundle contains the previously generated preservation package plus this new companion report and checksum/index file.

Included core files:

1. `00_manifest.md` — package inventory and status.
2. `01_human_readable_report.md` — full preservation report sections 0–16.
3. `02_context_transfer_packet.md` — handoff for a new chat.
4. `03_spec_sheet.yaml` — structured YAML-style spec sheet.
5. `04_registers.md` — workstreams, decisions, tasks, risks, artifacts, verification queue, timeline.
6. `05_aggregator_packet.md` — compact packet for future master aggregation.
7. `06_reader_brief.md` — shorter human brief.
8. `07_verification_and_audit.md` — audit and verification queue.
9. `08_future_chat_bootstrap_prompt.md` — prompt for starting a continuation chat.
10. `09_in_chat_reader.md` — package guide and question menu.
11. `10_accompanying_human_report.md` — this companion report.
12. `11_bundle_index_and_checksums.md` — updated bundle index and hashes.
13. Previous handoff ZIP — preserved as an included prior package.
14. Source prompt `Pasted text.txt` — included as source material.

---

## 11. Most Useful Follow-Up Questions

1. Turn PROVIDER-WEDGE-01 into a Codex-ready implementation issue.
2. Turn ROBOT-OS-WEDGE-01 into a concrete file-by-file implementation plan.
3. Extract the robotic seed-civilisation material into a formal design spec.
4. Extract the Robot OS UX material into a formal UI/UX spec.
5. Design `view.node.status` in detail.
6. Define provider manifest schemas and validators.
7. Define protected alert classes for official servers.
8. Define the first playable gameplay loop.
9. Verify raylib/SDL2/Lua/toolchain/platform facts with current sources.
10. Compare this report to another old-chat preservation report for conflicts.

---

## 12. Final Status

This companion report confirms the core conclusions of the previous preservation package and adds a cleaner readable narrative around the entire conversation. It should be bundled with the original preservation files and used as a fast orientation document before reading the larger registers/spec files.

Extraction confidence remains high but not perfect: some source material came from pasted prior-chat transcripts rather than raw direct access to all old chats, and external/library/toolchain/platform facts require current verification before implementation.

Best next action: create a concrete implementation spec for PROVIDER-WEDGE-01 and ROBOT-OS-WEDGE-01.
