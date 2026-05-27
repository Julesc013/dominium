# COMPLETE CHAT PRESERVATION REPORT — Domino Framework and Open-Source Provider Architecture

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Domino Framework and Open-Source Provider Architecture |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial but substantial: visible chat context plus uploaded preservation prompt; not guaranteed full historical transcript or inaccessible past-chat links |
| Previously generated files available? | No previously generated downloadable package was visible before this task |
| Uploaded files or artifacts present? | Yes: `Pasted text.txt`, the preservation/export instruction prompt fileciteturn29file0 |
| Contains future plans? | Yes |
| Contains decisions? | Yes, mostly architecture decisions and accepted directions |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium to High for external project facts, licenses, repo state, library versions, and platform support |
| Extraction confidence | 4 / 5 for visible-chat substance; 3 / 5 for full-history completeness |
| Safe for later aggregation? | With caveats |
| Main limitations | I can preserve the visible conversation and uploaded prompt. I cannot guarantee access to every old chat behind the pasted “Past chat” links, hidden transcript outside current context, or future/current repo state. |

Plain-language limitation: this package is a high-fidelity preservation of the conversation that is visible in this chat context. It should not be treated as a complete extraction of every related past chat. The user pasted references to other ChatGPT conversations, but those links were not browsed or available as full transcripts here. All facts about external libraries, licenses, project status, and the `julesc013/dominium` repo should be verified before implementation.

## 1. One-Page Orientation

This chat was about how to accelerate the Dominium/Domino game-engine project by using existing open-source code without letting outside engines or libraries define the architecture. The user’s recurring concern was speed: instead of starting from nothing, could Dominium bootstrap a working engine, game client, Workbench, scripting layer, and provider ecosystem using open-source systems such as raylib, SDL2, Lua, Celestia, SpaceEngine-like references, voxel/RTS/factory games, and other modular libraries? The conversation gradually converged on a clear doctrine: use outside code aggressively, but only as replaceable providers behind first-party Domino/Dominium contracts.

The first major theme was the difference between forking a full engine and assembling a framework from modular components. The chat rejected the idea that Dominium should become a modified copy of a large engine. Instead, it preferred a framework approach: Domino should define stable service contracts, provider ABIs, capability/refusal law, profiles, tests, and deterministic simulation interfaces; a Domino engine implementation should satisfy those contracts; the Dominium game implementation should consume those contracts. This means the game should not directly include `raylib.h`, `SDL.h`, `lua.h`, or any other third-party API in its canonical layers.

The second major theme was the raylib ecosystem. The user liked raylib and asked whether its subprojects could be used: raylib itself, `rlgl`, `rlsw`, `raymath`, `raygui`, `raudio`, texture/model/font systems, and examples. The conclusion was yes, but with clear classification. `raylib` is a broad high-level provider suite. `rlgl` is a raylib-family OpenGL abstraction provider, not the final Dominium OpenGL 3.3 backend. `rlsw` is a raylib software-render provider, not the canonical Dominium reference software renderer. `raygui` is an early Workbench/debug UI provider, not UI law. `raudio` is a first audio provider. `raymath` is safe for presentation/editor math, not deterministic simulation law. Asset-loading helpers are import/preview helpers, not Dominium asset identity.

The third major theme was service-first architecture. Earlier suggestions used paths like `runtime/render/raylib`, but the conversation refined that to `runtime/<service>/providers/<provider>`. The intended services include platform, input, render, draw, audio, asset, script, UI, world, simulation, diagnostics, storage, authority, and work delegation. Provider profiles, stored in `release/profiles/` or `content/profiles/`, should select combinations such as `client.raylib`, `client.sdl2_raylib`, `workbench.raylib`, and `server.null`. Apps remain generic: `apps/client`, `apps/workbench`, `apps/server`.

The fourth major theme was reference projects. The user asked about SpaceEngine, Celestia, PCGUniverse2, Valian/pgg, and other engines/games. The answer separated “use as dependency” from “study as reference.” SpaceEngine is a design reference only. Celestia is useful but GPL-constrained. PCGUniverse2 and pgg were useful procedural-generation references but license-unclear. Larger projects such as Luanti/Minetest, OpenRA, Spring RTS, Mindustry, Freeciv, Endless Sky, Pioneer, Godot, O3DE, Torque3D, and others were classified by subsystem relevance, mostly as research material rather than bases to fork.

The fifth major theme was the intended game architecture: deterministic, sparse, distributed, and able to support arbitrary CAD-like building. The conversation developed the phrase “sparse deterministic delegated simulation.” The world should be infinite by addressability, not by simulating everything. Active cells are finite and scheduled; cold regions are seeds plus deltas. Clients may contribute processing power through work leases, but the host/server verifies results before committing state. Player/agent/NPC creations should be arbitrary at design time but compiled into bounded runtime representations: construct graphs, machine graphs, physics proxies, render proxies, and event-sourced state.

The future relevance of this chat is high. It should feed the master Project Spec Book sections on Domino Framework architecture, provider system, first-wave dependencies, Workbench strategy, scripting/modding, deterministic simulation, sparse-world architecture, client-contributed compute, CAD/machine systems, and license/provenance policy. The most important thing a future assistant must understand is that Dominium is not meant to become a raylib game, a Godot fork, or a Celestia derivative. It is meant to become a first-party framework/game system that can use those tools as replaceable providers or references.

## 2. The Story of the Conversation

### 2.1 From “Can we use open source?” to a provider doctrine

The chat began with the user asking whether, because the project is portable, modular, and extensible, it could use existing open-source systems instead of starting from nothing. The first answer accepted that direction but drew a boundary: third-party code could accelerate execution, but it must not define Dominium law. That produced the early doctrine: fork for speed, wrap for control, test for proof, replace by boundary.

The user then stated a platform and language target: Windows 7 SP1+, macOS 10.9.5+, Linux, C17/C++17, Win32, Cocoa, SDL2, and OpenGL 3.3. The user also strongly endorsed Lua, SDL, and raylib. That shifted the conversation from abstract open-source reuse to specific first-wave providers.

### 2.2 The raylib phase

The chat spent significant time unpacking raylib. Initial suggestions put raylib under directories like `runtime/render/raylib` and `apps/client/rendered/raylib`. The user then pasted and compared refinements that pushed the architecture toward a cleaner service/provider model. The key correction was that source ownership should be service-first, not vendor-first. A renderer should not become “raylib-shaped”; instead, raylib should implement the render service as one provider.

The discussion then moved into raylib subcomponents. The user asked specifically whether `rlsw` could be used for software rendering and `rlgl` for OpenGL. The conclusion was nuanced. Yes, `rlsw` can be a raylib software-render provider, especially for headless screenshot evidence and CI, but Dominium should still own a canonical software reference renderer. Yes, `rlgl` can be an OpenGL-family provider, but a future direct `opengl33` provider should remain separate. `raymath`, `raygui`, `raudio`, `rtextures`, and `rmodels` are usable, but only in presentation/tool/import/provider layers.

### 2.3 Repo comparison phase

The user asked how raylib compared to current implementations at `julesc013/dominium`. The assistant inspected repository files through GitHub connector results. The chat found, at that time, that Dominium already had system and render abstractions such as `dsys` and `d_gfx`, plus stubs and software-backed paths. This supported the claim that the repo already had seams where raylib could fit as a concrete backend/provider. However, one important contradiction appeared later: a pasted transcript claimed the repo had already moved to C17/C++17, while a later assistant check said the visible `main` CMake still appeared to set C90/C++98. This must be verified before implementation.

### 2.4 Reference projects and open-source ecosystem phase

The user then asked about SpaceEngine, Celestia, PCGUniverse2, and Valian/pgg. The chat classified them mostly as reference projects rather than code dependencies. SpaceEngine was treated as proprietary/commercial design inspiration. Celestia was useful but GPL-constrained. PCGUniverse2 and pgg were procedural-generation references with unclear license status. Later, when the user asked about other open-source engines/games, the assistant listed projects useful by subsystem: Luanti/Minetest for sparse voxel/mod ecosystems, OpenRA/Spring/0 A.D./Freeciv/Widelands for command/ruleset/RTS/logistics patterns, Mindustry for factory graphs, Endless Sky/Pioneer/Celestia for space models, Godot/O3DE/Torque3D for editor/engine references, and raylib/SDL/Lua/SQLite/ImGui/Nuklear and similar libraries as better first-wave dependencies.

### 2.5 Sparse deterministic delegated simulation phase

The user then asked how to make the envisioned game deterministic and sparse, with clients dynamically taking load from the host and contributing processing power, while supporting arbitrary infinite building, CAD creation, machines, inventions, agents, NPCs, and other features. This produced a central conceptual architecture: infinite address space, finite active set, sparse materialization, deterministic local simulation islands, event-sourced state, client-contributed work, and host-verified authority.

The visible rationale was that clients can compute but cannot be blindly trusted. Work should be delegated through leases: a host assigns a deterministic packet, a client returns results with hashes/traces, and the host verifies by replay, quorum, spot-checking, or invariants. Arbitrary CAD designs should be free at design time but compiled to bounded runtime graphs and proxies. Players, agents, and NPCs should all mutate the world through the same command/event/build transaction system.

### 2.6 Domino Framework phase

The conversation culminated when the user said they liked the framework approach and asked whether raylib and other sources/projects could make a Domino framework that can be provided by any Domino engine implementation and any Dominium game implementation. The final architectural synthesis was: Domino Framework defines contracts and provider ABI; a Domino engine implementation provides those services; Dominium is a game implementation consuming the framework; raylib, SDL2, Lua, ImGui, raygui, raudio, rlgl, and rlsw are providers, not law. This is the main conceptual deliverable of the chat.

### 2.7 Preservation phase

Finally, the user uploaded a detailed preservation prompt and requested a maximum-fidelity report, registers, spec sheet, aggregator packet, audit, and downloadable files. This package is the response to that request.

## 3. Main Topics Discussed

### Topic 1 — Open-source bootstrap strategy

The first topic was whether Dominium should use existing open-source systems to accelerate development. The chat concluded that this is desirable, but only if third-party code is treated as replaceable scaffolding or providers. The preferred approach is not to fork a full engine and gradually mutate it, because that risks inheriting the engine’s object model, editor workflow, build system, content format, and architectural assumptions. The framework approach gives more control and better alignment with Dominium’s portability/modularity/extensibility goals.

Future work should convert this into a dependency policy: use permissive/weak-copyleft libraries as providers where appropriate; use GPL/proprietary/unclear projects as research references unless explicitly quarantined; require provider manifests, license manifests, and conformance tests.

### Topic 2 — raylib ecosystem as first visible provider suite

raylib came up because the user liked it and because it provides a fast way to get windows, input, rendering, audio, assets, and tooling visible. The conversation concluded that raylib should be used heavily, but only under `runtime/<service>/providers/<provider>` and proof/experiment areas. `raylib.h` and related headers should be forbidden from framework public headers, contracts, game law, content, saves, replays, and public SDK.

`rlsw` can help with headless and CPU rendering, but not as canonical deterministic reference renderer. `rlgl` can help as OpenGL-family provider, but not as final direct `opengl33`. `raygui` can bootstrap Workbench/debug panels, but Workbench documents remain first-party. `raudio` can be audio provider. `raymath` is safe for render/editor math only. Asset import helpers can load/preview images/models/fonts/audio, but Dominium asset identity must remain first-party.

### Topic 3 — SDL2 and Lua

SDL2 was treated as complementary to raylib, not a replacement or afterthought. SDL2 should be a platform/input/audio provider, and profiles can combine SDL2 platform/input with raylib/rlgl rendering. Lua was accepted as a good scripting provider for packs, mods, CLI, Workbench automation, scenario hooks, and debug tooling. The important caveat is that Lua must be pinned and hidden behind `dominium.script.v1` or equivalent. Mods should target Dominium’s script API, not the raw Lua ABI.

### Topic 4 — Service-first/provider-first architecture

This became the central architectural theme. The conversation refined earlier vendor-shaped paths into service-first paths. The stable pattern is:

```text
runtime/<service>/providers/<provider>
contracts/provider
contracts/capability
contracts/schema/runtime/<service>
release/profiles/*.toml
apps/client, apps/workbench, apps/server remain generic
```

The reason is that service identity is first-party and provider implementation is replaceable. This allows multiple engine implementations and multiple provider profiles to run the same game implementation.

### Topic 5 — Domino Framework / Domino Engine / Dominium Game split

The final synthesis separated framework, engine, and game. Domino Framework is the stable API/contract/provider system. A Domino engine implementation satisfies it. Dominium is a game implementation using it. This is likely the most important conceptual result of the chat. It means the project can produce one reference engine and later allow alternate engines to run the same game or allow other games to run on the same framework.

### Topic 6 — Current Dominium repository fit

The chat inspected `julesc013/dominium` and found evidence of existing abstractions such as system and graphics layers, stubs, and soft-backed backends. The finding was that raylib could fill concrete provider gaps without replacing the architecture. However, current repo facts are stale/uncertain and must be verified, especially the C17/C++17 vs C90/C++98 baseline contradiction.

### Topic 7 — Reference projects

The user asked about SpaceEngine, Celestia, PCGUniverse2, pgg, and later other open-source engines/games. The conclusion was that these are valuable mostly as research/reference material. They can inform worldgen, catalogs, addons, space navigation, terrain LOD, voxel worlds, RTS command systems, factory graphs, mod ecosystems, and editor designs. They should not be blindly vendored or forked because of license, stack, or architecture mismatch.

### Topic 8 — Sparse deterministic delegated simulation

The user’s large game vision requires an architecture where the world is infinite by addressability but finite by active simulation. The chat proposed activity states such as cold, warm, scheduled, active, and hot. It also proposed cells/islands/constructs as units of scheduling and authority. Clients can contribute compute, but state changes must be host-verified. This topic should become a formal spec chapter.

### Topic 9 — CAD, machines, arbitrary inventions

The chat addressed the user’s desire for arbitrary creation systems, machines, and inventions. The core conclusion was that raw arbitrary CAD geometry cannot be simulated forever everywhere. Designs must compile into bounded runtime forms: construct graphs, machine graphs, port graphs, physics proxies, damage graphs, and render proxies. Players, agents, and NPCs should all submit build intents through the same transaction system.

### Topic 10 — Preservation and aggregation

The final topic is this package. The user requested a preservation report that is human-readable first, with registers, spec sheet, aggregator packet, self-audit, and downloadable files. This report preserves the visible chat, not any inaccessible past-chat transcripts.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted to speed up Dominium development by using existing open-source systems. The conversation addressed this by comparing framework vs fork approaches and converging on modular providers.

The user explicitly wanted Lua support for modules/packs/mods/CLI and maybe all scriptable layers. The chat addressed this by recommending a pinned Lua provider behind a Dominium script API.

The user explicitly wanted SDL2 and raylib support. The chat addressed this by assigning SDL2 to platform/input/audio and raylib to visible rendering/tooling/provider suite.

The user explicitly wanted to know whether raylib subprojects like `rlsw`, `rlgl`, `raymath`, `raygui`, and `raudio` could be used. The chat answered yes with boundaries.

The user explicitly wanted a deterministic sparse game architecture where clients contribute compute and players/agents/NPCs can build arbitrary/infinite things. The chat addressed this with sparse deterministic delegated simulation, work leases, host verification, and CAD-to-runtime graph compilation.

The user explicitly wanted a preservation/export package for this chat. This output addresses that.

### 4.2 Inferred Goals

The user appears to want a long-lived, auditable project spec that can survive chat transitions and aggregation. The preservation prompt confirms this.

The user appears to want architecture that remains portable across older desktop systems and future render/platform providers. This was inferred from the platform floor and repeated concern with portability/modularity/extensibility.

The user appears to want a clean distinction between reusable framework, engine implementation, and game implementation. This became explicit later but was also implied by the framework approach.

### 4.3 Goals That Changed Over Time

The conversation began as “Can we use open source to avoid starting from nothing?” It evolved into a much more precise doctrine: “Build a Domino Framework with service contracts and providers, and use raylib/SDL2/Lua as first providers.”

Early directory ideas were more vendor-shaped. Later they became service-first. Early raylib use was described as `runtime/render/raylib`; later the refined pattern became `runtime/render/providers/raylib`.

The idea of using open-source games shifted from potential code reuse to reference/research material due to license and architecture risks.

### 4.4 Goals Still Unresolved

The exact first implementation branch, versions, and dependency pins are unresolved. The exact Domino Framework ABI is unresolved. The exact Lua version is unresolved. The current repository baseline must be verified. The formal policy for GPL/LGPL/unclear license material is unresolved. The sparse simulation and CAD systems need formal specs and prototypes.

## 5. Decisions Made and Why

### Decision overview

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | Use open-source code primarily through a framework/provider approach, not by mutating one large fork. | Accepted direction | Preserves Dominium law and allows replaceability. | 4 | FACT/INFERENCE |
| DECISION-02 | raylib should be used heavily as the first visible provider suite. | Accepted direction | Fast client, Workbench, rendering, audio, import preview. | 5 | FACT |
| DECISION-03 | Dominium/Domino contracts, simulation, replay, saves, packs, commands, UI documents, provider law remain first-party. | Accepted doctrine | Avoids lock-in and supports deterministic/replayable game law. | 5 | FACT/INFERENCE |
| DECISION-04 | Use service-first runtime layout: runtime/<service>/providers/<provider>. | Accepted direction | Avoids vendor-shaped architecture. | 5 | FACT/INFERENCE |
| DECISION-05 | Profiles select provider combinations; apps should remain generic. | Accepted direction | Avoids product forks per backend. | 4 | FACT/INFERENCE |
| DECISION-06 | Keep SDL2 as a first-wave provider, not a fallback afterthought. | Accepted direction | Gives stable platform/input/audio substrate. | 4 | FACT/INFERENCE |
| DECISION-07 | Use Lua, but pin the Lua provider and expose Dominium script API separately. | Accepted direction | Prevents raw Lua ABI from becoming mod law. | 4 | FACT/INFERENCE |
| DECISION-08 | rlsw can be used as a raylib software-render provider, but not as Dominium canonical reference renderer. | Recommended; likely accepted direction | Maintains first-party deterministic evidence path. | 4 | FACT/INFERENCE |
| DECISION-09 | rlgl can be used as OpenGL-family provider, but should not be named as final opengl33 law. | Recommended; likely accepted direction | Preserves future direct OpenGL provider. | 4 | FACT/INFERENCE |
| DECISION-10 | SpaceEngine, Celestia, PCGUniverse2, and pgg should mainly be reference material, not direct code dependencies. | Recommended | Avoids legal and architectural contamination. | 4 | FACT/INFERENCE |
| DECISION-11 | For sparse/infinite game design, use infinite address space with finite active set and deterministic cells. | Recommended design doctrine | Makes infinite/arbitrary world computationally feasible. | 4 | INFERENCE |
| DECISION-12 | Clients may contribute compute but should not be blindly trusted as authoritative. | Recommended doctrine | Prevents cheating/desync in distributed compute. | 4 | INFERENCE |
| DECISION-13 | Arbitrary CAD creations should compile into bounded runtime representations. | Recommended doctrine | Separates design-time freedom from runtime tractability. | 4 | INFERENCE |
| DECISION-14 | Create a full preservation package for this chat. | Explicit user instruction | Allows aggregation and future continuation. | 5 | FACT |

### Decision explanations

The main accepted direction was the framework/provider approach. The user explicitly said they liked the framework approach and asked whether it could be used to make a Domino framework provided by any engine implementation and consumed by any Dominium game implementation. This makes sense because it lets the project use raylib and other libraries quickly without baking them into game law.

The raylib decision was also directionally accepted. The user repeatedly expressed enthusiasm for raylib and asked about using as much of raylib infrastructure as possible. The caveat is that raylib is a provider suite, not architecture. This affects rendering, audio, input, asset preview, and Workbench bootstrap.

The service-first layout decision matters because it prevents vendor-shaped directories and product variants. A profile can choose raylib or SDL2 providers without making a separate client architecture.

The SDL2 and Lua decisions matter because they balance speed with portability and extensibility. SDL2 gives a stable platform/input/audio substrate. Lua gives scripting, but the chat decided raw Lua version should not define mod law.

The sparse deterministic delegated simulation decisions are design doctrines, not implemented decisions. They are accepted as the recommended direction but still need formal proof and prototypes.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Forking a full engine as the main architecture. | Deprioritised | Would overwrite Dominium law and create lock-in. | Tentative but strong | Reconsider only for isolated prototype or tool, not canonical core. | WORKSTREAM-01 | FACT/INFERENCE |
| REJECTED-02 | Letting raylib define game architecture. | Rejected | raylib should be provider, not law. | Strong | Never reconsider unless project goal changes. | WORKSTREAM-04 | FACT |
| REJECTED-03 | Placing provider identity into app folder names such as apps/client/rendered/raylib. | Superseded | Profiles should select providers; apps remain generic. | Strong | Temporary proof apps may exist under proof/experiments. | WORKSTREAM-03 | FACT/INFERENCE |
| REJECTED-04 | Top-level labs/ or profiles/ roots as main architecture. | Deprioritised | Could reopen top-level-root sprawl; prefer content/profiles or release/profiles and tools/experiments. | Tentative | Reconsider if repo governance adopts those roots deliberately. | WORKSTREAM-03 | INFERENCE |
| REJECTED-05 | Using rlsw as canonical Dominium software renderer. | Rejected | rlsw is raylib ecosystem provider; Dominium reference should be first-party. | Strong | Could be temporary fallback but not proof law. | WORKSTREAM-04 | FACT/INFERENCE |
| REJECTED-06 | Using rlgl as the final direct opengl33 provider. | Rejected/superseded | rlgl is raylib abstraction; direct opengl33 should be separate. | Strong | rlgl can implement first OpenGL-family provider. | WORKSTREAM-04 | FACT/INFERENCE |
| REJECTED-07 | Trusting client-contributed simulation results without verification. | Rejected | Cheating/desync risk. | Strong | Only in local trusted sandbox/co-op if explicitly chosen. | WORKSTREAM-09 | INFERENCE |
| REJECTED-08 | Simulating every arbitrary object everywhere continuously. | Rejected | Impossible/unbounded; sparse activation required. | Strong | Local dense simulation can exist in bounded active cells. | WORKSTREAM-09 | INFERENCE |
| REJECTED-09 | Copying code from proprietary/GPL/unclear-license projects by default. | Rejected | License and architecture risk. | Strong | Reconsider only with explicit license strategy/quarantine. | WORKSTREAM-08 | FACT/INFERENCE |

The most important rejected idea is using a full engine fork as the project’s main foundation. It was rejected because it would likely make Dominium inherit the full engine’s assumptions. The second important rejected idea is allowing raylib to become the engine architecture. The chat repeatedly preserved the boundary: use raylib heavily, but only behind providers.

A more subtle superseded idea was app-variant architecture. Early structures such as `apps/client/rendered/raylib` were useful for proof bootstraps, but the stronger model is generic apps plus provider profiles.

Another rejected idea was using external reference projects directly without license review. This matters because later assistants might see Celestia, PCGUniverse2, pgg, or SpaceEngine and assume code can be copied. The chat did not authorize that.

## 7. Important Reasoning, Rationale, and Tradeoffs

The central tradeoff was speed versus architectural control. The user wanted fast progress. The answer was to use existing libraries, but only behind first-party service contracts. This keeps the project from getting stuck in a third-party object model or rendering/input/save system.

Another tradeoff was convenience versus determinism. raylib, SDL2, Lua, and physics/rendering helpers are convenient, but deterministic simulation cannot depend on wall-clock time, raw floating-point platform differences, uncontrolled Lua execution, GPU physics, thread races, or arbitrary library internals. Therefore rendering/audio/UI are non-authoritative providers, while simulation commands, state hashes, replay, and save law remain first-party.

A third tradeoff was arbitrary creativity versus finite runtime cost. The user wants arbitrary CAD-style creations and machines. The answer was not to restrict design-time creativity, but to compile designs into bounded runtime structures.

A fourth tradeoff was client-contributed compute versus trust. Clients can help with meshing, planning, simulation proposals, and non-authoritative work, but valuable state must be verified by the host/server.

A fifth tradeoff was open-source reuse versus licensing risk. Permissive libraries can be providers. GPL/proprietary/unclear projects should be research references unless the project deliberately adopts a compatible license/quarantine strategy.

## 8. Plans, Future Work, and Next Steps

The main implementation path is:

1. Verify repo baseline and dependency versions.
2. Create Domino Framework/provider ABI skeleton.
3. Add null providers and validators.
4. Add raylib/rlgl/rlsw/raygui/raudio providers.
5. Add SDL2 platform/input/audio provider.
6. Add Lua script provider.
7. Add profiles: client.raylib, client.sdl2_raylib, workbench.raylib, server.null.
8. Add conformance tests and deterministic replay/state hash tests.
9. Develop worldgen/sparse simulation/CAD schemas and prototypes.

The first concrete wedge should be `DOMINO-FRAMEWORK-WEDGE-01`: framework headers, provider registry, profile loader, null providers, raylib providers, and validation tools. The expected output is a server-null profile that runs deterministic ticks and a client-raylib profile that opens a window and renders non-authoritative presentation.

Risks include stale repo assumptions, platform floor incompatibility, license mistakes, third-party type leakage, and overbuilding sparse/CAD systems before a minimal deterministic cell simulator exists.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user requires source-grounded, audit-ready, uncertainty-labelled responses. The preservation prompt explicitly requires FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT labels, no invented facts, no treating brainstorms as decisions, and no over-compression. The prompt also requires a human-readable report first and downloadable files if possible fileciteturn29file0.

Technical constraints explicitly mentioned include Windows 7 SP1+, macOS 10.9.5+, Linux, C17/C++17, Win32, Cocoa, SDL2, and OpenGL 3.3.

### 9.2 Inferred Constraints and Preferences

The user prefers modular architecture over monolithic engine forks. The user prefers long-term portability, extensibility, and replaceability. The user cares about preserving reasoning and rejected options for future aggregation.

### 9.3 Uncertain or Unestablished Preferences

The exact project license is not established here. The exact dependency versions are not established. The exact tolerance for GPL/LGPL code is not established. The exact first implementation branch is not established.

## 10. Files, Artifacts, Outputs, and Prompts

The main uploaded artifact is `Pasted text.txt`, containing the preservation task prompt and output requirements fileciteturn29file0. Before this task, no generated report/ZIP package was visible in this chat. This response creates the requested package.

Important in-chat artifacts include the raylib deep-dive outputs, directory structure proposals, provider manifest examples, the julesc013/dominium repo comparison findings, open-source project classifications, sparse deterministic delegated simulation architecture, and Domino Framework wedge proposal.

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Pasted text.txt preservation prompt | Uploaded file / prompt | Defines required preservation package, sections, files, and labels. | Available in this chat | User upload | Yes | Primary instruction artifact for this task. fileciteturn29file0 | FACT |
| ARTIFACT-02 | Prior assistant raylib/provider architecture messages | In-chat outputs | Developed service-first provider doctrine, raylib/SDL/Lua role, directory structures. | Visible in chat context | This chat | Yes | Substantive source for report. | FACT |
| ARTIFACT-03 | GitHub inspection snippets for julesc013/dominium | Tool results in chat | Compared current repo dsys/dgfx stubs and possible CMake baseline. | Visible in chat context; freshness uncertain | GitHub connector during chat | Yes, with verification | Use as historical inspection, not current truth. | UNCERTAIN/UNVERIFIED |
| ARTIFACT-04 | Lists of external projects and reference links | In-chat lists | SpaceEngine, Celestia, PCGUniverse2, pgg, open-source engines/games. | Visible in chat | User and assistant messages | Yes | Feed research/reference lane. | FACT |
| ARTIFACT-05 | DOMINO-FRAMEWORK-WEDGE-01 proposal | Plan/output | First implementation wedge for framework/provider architecture. | Proposed, not implemented | Assistant suggestion accepted directionally | Yes | Should become task/epic. | INFERENCE |
| ARTIFACT-06 | PROVIDER-WEDGE / RENDER-WEDGE / SCRIPT-WEDGE naming | Plan/output | Staged implementation plan. | Proposed, not implemented | Assistant outputs | Yes | Useful for backlog. | INFERENCE |
| ARTIFACT-07 | This preservation package files | Generated files | Markdown/YAML/ZIP handoff package. | Created by current response | Assistant file export | Yes | Use for aggregation and future continuation. | FACT |

## 11. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Which exact versions of raylib, SDL2, Lua, raygui, ImGui, and related libraries should be pinned? | Platform floors and API stability depend on versions. | The conversation recommended using them. | Exact versions and compatibility with Win7/macOS 10.9.5. | Verify upstream release notes and build tests. | P0 | WORKSTREAM-04 | UNCERTAIN/UNVERIFIED |
| QUESTION-02 | Is Dominium repo main branch actually C17/C++17 or still C90/C++98? | Build baseline affects raylib and framework. | Earlier assistant inspection found possible C90/C++98 contradiction; later transcript claimed C17/C++17. | Current branch truth. | Inspect current repo branch before implementation. | P0 | WORKSTREAM-07 | UNCERTAIN/UNVERIFIED |
| QUESTION-03 | Should the canonical Lua provider be lua54 or lua55? | Script ABI and mod compatibility. | Lua should be pinned and hidden behind dominium.script.v1. | Specific series choice. | Compare maturity, compatibility, platform support. | P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-04 | What is the first minimal Domino Framework ABI? | Blocks implementation. | Concept defined but not specified fully. | Exact structs/functions/services. | Draft DOMINO-FRAMEWORK-WEDGE-01 header. | P0 | WORKSTREAM-02 | INFERENCE |
| QUESTION-05 | What first provider profile should be implemented: client.raylib, client.sdl2_raylib, or server.null? | Implementation order. | All were proposed. | Priority/order and acceptance tests. | Choose wedge scope. | P0 | WORKSTREAM-02 | INFERENCE |
| QUESTION-06 | How strict must deterministic simulation be across platforms? | Affects math, threads, providers. | Determinism required at sim/command layer, not render/audio/UI. | Exact determinism class and tolerated divergence. | Define determinism spec. | P0 | WORKSTREAM-09 | INFERENCE |
| QUESTION-07 | What license policy will Dominium adopt for GPL/LGPL/unclear-license references? | Code reuse boundaries. | Reference-only default recommended. | Formal project legal policy. | Write license/provenance policy. | P1 | WORKSTREAM-08 | UNCERTAIN |
| QUESTION-08 | What is the minimal CAD construct graph for first implementation? | Arbitrary invention system is broad. | Graph/ports/machine model proposed. | First component set and compile pipeline. | Define CAD-WEDGE-01. | P1 | WORKSTREAM-10 | INFERENCE |
| QUESTION-09 | How will client-contributed work be verified and what trust tiers exist? | Distributed compute feasibility and security. | Work lease/quorum/spot-check model proposed. | Exact verification policy. | Prototype host/client lease smoke. | P0 | WORKSTREAM-09 | INFERENCE |

The most blocking unresolved issues are repo baseline verification, exact dependency pins, minimal framework ABI, provider profile order, deterministic simulation spec, and license policy.

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Future assistant treats recommendations as final decisions. | Spec may overcommit. | Medium | High | Use status labels: accepted direction vs proposed vs unresolved. | All | FACT/INFERENCE |
| RISK-02 | Third-party libraries leak into public contracts. | Long-term lock-in, save/replay breakage. | Medium | High | Forbidden include validator and provider manifests. | WORKSTREAM-03 | FACT/INFERENCE |
| RISK-03 | C17/C++17 baseline assumed without repo verification. | Build failures or wrong plan. | Medium | High | Verify current branch before implementation. | WORKSTREAM-07 | UNCERTAIN/UNVERIFIED |
| RISK-04 | raylib/SDL/Lua current versions may not support stated old OS floors. | Platform target failure. | Medium | High | Pin/test exact versions on Win7/macOS 10.9.5/Linux. | WORKSTREAM-04 | UNCERTAIN/UNVERIFIED |
| RISK-05 | GPL/unclear-license project code copied accidentally. | Legal contamination. | Low-medium | High | Research-only lane, license validator, provenance policy. | WORKSTREAM-08 | FACT/INFERENCE |
| RISK-06 | Distributed client compute becomes cheat vector. | Invalid world state/economy/combat. | High if unmitigated | High | Host verification, work leases, state hashes, trust tiers. | WORKSTREAM-09 | INFERENCE |
| RISK-07 | Arbitrary CAD runtime becomes computationally unbounded. | Performance collapse/desync. | High if raw CAD simulated | High | Compile to bounded graphs/proxies and enforce budgets. | WORKSTREAM-10 | INFERENCE |
| RISK-08 | Report overstates access to full chat or past-chat links. | Bad aggregation. | Medium | Medium | State source limitation; use this chat only. | WORKSTREAM-11 | FACT |
| RISK-09 | External facts go stale. | Wrong dependency/legal choices. | High over time | Medium-high | Verification queue before implementation. | All | FACT |

A future assistant might incorrectly say “we decided to use raylib as the engine.” The correct statement is that raylib is a first visible provider suite. Another common mistake would be to treat every assistant proposal as a user decision. Several items are recommended directions, not implemented decisions.

A future assistant might also rely on stale external facts or repository inspections. Dependency versions, OS floors, repo CMake state, and licenses must be verified.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Framework architecture | Domino Framework API, engine implementation, game implementation split. | DECISION-01, DECISION-14, WORKSTREAM-02 | Requirement | 5 | Central spec chapter. |
| Provider system | Service-first runtime providers, manifests, profiles, conformance tests. | DECISION-03..05, WORKSTREAM-03 | Requirement | 5 | Core architecture. |
| First-wave dependencies | raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua. | DECISION-02, DECISION-06..09 | Requirement/context with verification | 4 | Needs version/platform checks. |
| License/provenance | Reference-only lane for GPL/proprietary/unclear projects. | DECISION-10, CONSTRAINT-07 | Requirement | 4 | Should become legal/provenance policy. |
| Sparse deterministic simulation | Infinite address space, finite active set, work leases, host verification. | DECISION-11..13, WORKSTREAM-09 | Requirement/open issue | 4 | Needs formal protocols. |
| CAD/invention system | CAD documents compile into bounded construct/machine graphs. | DECISION-13, WORKSTREAM-10 | Requirement/open issue | 4 | Needs first component model. |
| Workbench direction | Workbench edits Dominium documents, not raygui objects; uses providers. | WORKSTREAM-04, WORKSTREAM-10 | Requirement/context | 4 | Ties UI documents to tooling. |
| Preservation/aggregation | This chat is converted into report, registers, spec sheet, ZIP. | WORKSTREAM-11 | Context | 5 | Feeds master spec book. |

This chat contributes the high-level architecture for the Domino Framework and provider system. It also contributes first-wave dependency strategy, research/reference project classification, sparse deterministic delegated simulation, and CAD/machine system framing. These should become formal chapters in a master Project Spec Book.

## 14. What I Should Remember

- Dominium should not become a raylib game or a fork of another engine. It should become a contract-governed framework/game system.
- The framework/provider approach is the central conclusion.
- raylib is useful now, but only as providers: raylib, rlgl, rlsw, raygui, raudio, asset import.
- SDL2 and Lua remain first-wave providers.
- Third-party types must not enter contracts, game law, content, saves, replays, or public SDK.
- Profiles select providers; apps stay generic.
- External games/engines are mostly reference material, not code bases to copy.
- The world architecture should be sparse, deterministic, delegated, and host-verified.
- Arbitrary CAD creations should compile into bounded runtime graphs.
- The next practical step is a minimal Domino Framework/provider wedge with null and raylib providers.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat

- Explain the difference between Domino Framework, Domino engine implementation, and Dominium game implementation.
- Explain why raylib is a provider suite rather than the engine architecture.
- Summarize the service-first/provider-first directory model.

### 15.2 Decisions

- Which decisions in this chat are explicit user-accepted decisions versus assistant recommendations?
- Which decisions should become formal requirements in the spec book?
- Which decisions need user confirmation before implementation?

### 15.3 Tasks and Next Actions

- Draft the exact `DOMINO-FRAMEWORK-WEDGE-01` file tree and PR checklist.
- Draft the first provider ABI header in C.
- Draft the forbidden-include validator.

### 15.4 Artifacts and Files

- Show me the artifact ledger and explain which artifacts should feed the master spec book.
- Generate the provider manifest templates for raylib, SDL2, Lua, and null providers.

### 15.5 Risks and Verification

- Verify the current `julesc013/dominium` CMake language baseline.
- Build a verification checklist for raylib/SDL2/Lua platform support.
- Create a license/provenance policy for reference projects.

### 15.6 Future Spec Book / Aggregation

- Convert this package into a spec-book chapter outline.
- Identify likely duplicates/conflicts with other old chats.

### 15.7 Deep-Dive Questions Specific to This Chat

- Design the sparse deterministic work-lease protocol.
- Design the first CAD construct graph schema.
- Design the `client.raylib` and `server.null` profiles.

## 16. Compact Human Summary

This chat established how Dominium should accelerate development without losing its own architecture. The user wanted to know whether existing open-source systems could be used instead of starting from nothing. The answer evolved into a clear framework/provider doctrine: use open-source libraries and projects heavily, but only through first-party Domino contracts and replaceable providers.

The central architectural conclusion is that Domino should be a framework: it defines stable contracts, service APIs, provider manifests, profiles, capability/refusal law, conformance tests, and deterministic simulation boundaries. A Domino engine implementation provides those services. Dominium is one game implementation that consumes them. Providers such as raylib, SDL2, Lua, raygui, raudio, rlgl, rlsw, ImGui, and others implement specific services, but they do not define the game’s law.

raylib was the most deeply discussed dependency. The chat concluded that raylib should be used aggressively because it can quickly provide a visible client, Workbench panels, drawing, audio, asset preview, and screenshots. But raylib must be fenced. `rlsw` can be a raylib software-render provider but not the canonical Dominium reference renderer. `rlgl` can be an OpenGL-family provider but not the final direct `opengl33` provider. `raygui` can bootstrap tools but not define UI documents. `raudio` can provide early audio. `raymath` is only for editor/render math, not deterministic simulation. Asset loaders are import/preview helpers, not Dominium asset law.

SDL2 remains important as a first-wave platform/input/audio provider. Lua is a good scripting provider for packs, mods, CLI, Workbench automation, and scenario hooks, but it must be pinned and hidden behind a Dominium script API such as `dominium.script.v1`. The raw Lua ABI should not become mod law.

The conversation also evaluated external projects. SpaceEngine, Celestia, PCGUniverse2, and Valian/pgg can help as references, but not as direct dependencies by default. Celestia is GPL-constrained. SpaceEngine is proprietary. PCGUniverse2 and pgg had unclear license status in the chat. Other open-source games and engines such as Luanti, OpenRA, Spring, Mindustry, Freeciv, Endless Sky, Pioneer, Godot, O3DE, and Torque3D are valuable mostly as research references for subsystems: voxel worlds, command simulation, factories, rulesets, space content, editor architecture, and plugin ecosystems.

The user’s broader game vision led to a second major architecture: sparse deterministic delegated simulation. The game should be infinite by addressability, not by simulating everything everywhere. The active world should be partitioned into cells/islands/constructs. Cold regions are procedural seeds plus saved deltas. Active cells tick deterministically. Clients may contribute compute, but only through work leases whose outputs are verified by the host/server before becoming authoritative. Player/agent/NPC creations can be arbitrary at design time, but must compile into bounded runtime structures: construct graphs, machine graphs, physics proxies, render proxies, and event-sourced state.

The most important next action is to implement `DOMINO-FRAMEWORK-WEDGE-01`: framework headers, provider ABI, null providers, raylib providers, provider manifests, profiles, and validators. The immediate blocker is verification: confirm the actual repo language baseline, dependency versions, platform floors, and license constraints before implementing.
