# COMPLETE CHAT PRESERVATION REPORT — Dominium Workbench, Presentation Spine, and Universe Explorer Planning

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium Workbench, Presentation Spine, and Universe Explorer Planning |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial-to-broad visible transcript context; not guaranteed raw/full transcript |
| Previously generated files available? | No confirmed previously generated downloadable files before this package |
| Uploaded files or artifacts present? | Yes: source.zip, screenshot bundles, multiple image mockups, pasted preservation request, pasted Universe Explorer note |
| Contains future plans? | Yes |
| Contains decisions? | Yes |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium-to-high for live repo facts and external platform facts; low for in-chat decisions |
| Extraction confidence | 4/5 |
| Safe for later aggregation? | Yes, with caveats |
| Main limitations | The full raw transcript may not be accessible; some repo-state claims were pasted from other chats and were not independently verified in this preservation pass; screenshots were used as reference but not deeply re-processed here. |

Plain-language limitation: this package reconstructs the conversation from the visible chat context and uploaded/pasted supporting files. It should be treated as a high-fidelity handoff for this chat, but not as an independently verified snapshot of the live GitHub repo. Any statement about the repo's current status, latest queue item, or latest gate should be verified before becoming formal project law.

## 1. One-Page Orientation

This chat began as a focused planning conversation about a Windows launcher UI problem and a proposed internal “Tool Editor” / “UI Editor.” The early objective was concrete: build a graphical editor that could author pixel-perfect UI definitions, generate TLV or code, use true native widgets where necessary, and fix the mangled/flickering launcher. Over the course of the chat, the plan grew and then corrected itself several times. The user clarified that Windows 10 was the immediate platform for the initial UI Editor, that the eventual tool should support Windows, macOS, and Linux, and that the UI system had to support both native-looking controls and custom rendered widgets. Early assistant output produced detailed Codex prompt plans for a Windows-only UI Editor, a future Tool Editor, TLV schema handling, codegen, layout, capability validation, and launcher/setup redesign tests.

The major turn in the conversation was the user’s rejection of the old UI Editor / Tool Editor as final products. The user concluded that those were useful general ideas but poor final architecture. The conversation then reframed the direction around a cross-platform rendered Workbench: one modular, rendered, CLI/TUI/GUI/headless-capable tools environment using the same runtime, command, renderer, UI, pack, diagnostics, and evidence systems as the client. Workbench became a production environment for building Domino and Dominium, not just an editor. It would host modules such as Validation Dashboard, Project Graph Explorer, Agent Work Board, Pack Browser, Interface Studio, Renderer Sandbox, Theme Laboratory, Release Forge, Replay/Trace Viewer, and later domain-specific labs for planet generation, terrain, machines, factories, robot bodies, spawn fabricators, fog of war, logistics, and civilization systems.

A second major theme was unification of presentation surfaces. The user wanted CLI, TUI, rendered GUI, and OS-native GUI to share code and semantics. The decision emerged that these should not be four separate systems. Instead, all products should expose the same command/result/refusal/document/view spine, while CLI, TUI, rendered GUI, native GUI, and headless modes are projections over that spine. This unifies the client, server, setup, launcher, Workbench, validators, AIDE/Codex tasks, and future admin tools.

A third major theme was portability and future-proofing. The user repeatedly emphasized that Domino should be reusable for different games, not just Dominium. The architecture therefore separated terms: components, services, providers, packs, modules, workspaces, apps, artifacts, commands, documents, patches, and evidence. The guiding idea became that path is not identity, implementation is not contract, UI is not authority, and generated output is not source truth. Reuse should be achieved through contracts, registries, commands, capabilities, modules, packs, providers, and conformance tests rather than through fragile folder references.

A fourth theme was the robot seed-civilization / universe-scale game vision. The user introduced a large pasted design about Domino as deterministic authority and Unreal or other renderers as optional high-fidelity clients, plus a robot colonization game built around motherships, nanobot construction, physical spawning, fog of war, terrain cut/fill, machine graphs, factory graphs, and civilization/infrastructure progression. The chat concluded that Workbench can and should eventually contain modules to author and test these artifacts: planet specs, field layers, terrain deltas, construction blueprints, machine graphs, factory process graphs, spawn systems, sensor/fog models, logistics/infrastructure, governance/claims, performance budgets, and universe exploration.

The most important final state is that Workbench should be built by progressive self-hosting. It does not build everything from nothing. First come the foundation gates and command/result/view/projection slice. Then package mounting, replay proof, barebones client shell, and minimal Workbench shell. Then Workbench modules begin editing safe artifacts. Later Workbench edits its own layouts, themes, modules, app compositions, packs, and eventually creates AIDE/Codex work units for code changes. The chat’s lasting contribution is a unified architecture for building the project through the same systems that the project itself will expose to players, modders, developers, servers, tools, agents, and future games.

## 2. The Story of the Conversation

### 2.1 Original UI Editor / Tool Editor phase
The chat opened with the user asking for help designing an internal “Tool Editor” that could visually design pixel-perfect UIs and broad-strokes functionality for setup, launcher, game, and other tools. The first questions focused on platforms, languages, native widgets, editor UX, output files, codegen, and dependency constraints. The user supplied details about the existing Dominium UI/DUI TLV system, Win32/DGFX/null backends, likely flicker paths, and current launcher files.

A Windows-first plan emerged: Phase A would be a minimal Windows UI Editor to generate canonical TLV; Phase B would be a fuller Tool Editor that edits DUI schemas/states directly. Detailed Codex prompts were generated for scaffolding, IR, TLV, capability validation, layout, widgets, action codegen, UI Editor, Tool Editor bootstrap, Win32 batching/flicker fixes, and hardening. Later the user expanded the UI Editor requirements to include import/export of existing tools, a headless CLI/ops.json interface for Codex, and “Minecraft-style” logical launcher/setup layouts using native controls only.

### 2.2 Pivot away from native-widget editor products
The user then determined that the old UI Editor and Tool Editor were good general ideas but bad final products. This pivot was central. The plan moved away from OS-native widget authoring as the core direction. The user wanted cross-platform tools using the same CLI/TUI/rendered GUI path as the client, rendered by software first and hardware later, not reliant on a specific OS SDK or native widgets.

The discussion reframed the product as Dominium Workbench: one rendered, modular, command-driven development environment for building Domino, Dominium, packs, modules, UI, tests, themes, assets, releases, and agent workflows. The Workbench would be an integrated shell, not a monolithic editor.

### 2.3 Unified product surfaces and presentation spine
The conversation then developed a general rule: all apps should share the same command/result/refusal/document/view spine. CLI, TUI, rendered GUI, headless mode, and optional OS-native GUI should be projections of that spine, not independent implementations. This addressed client, server, launcher, setup, Workbench, validators, future tools, and native SDK GUI bridges.

OS-native GUI authoring with Visual Studio/Xcode remained valid, but native GUI was demoted to an optional projection. Rendered GUI became the core shared route for client and Workbench. TUI was treated as a first-class low-dependency projection, not a toy fallback. CLI/headless remained mandatory for automation, tests, AIDE, and Codex.

### 2.4 Workbench modules and workspaces
The user proposed early Workbench modules: Project Editor, UI Editor, Module Editor, and App Editor. The conversation refined these into larger user-facing workspaces built from smaller reusable modules and services. Names evolved into Project Graph Explorer, Interface Studio, Module/Pack Foundry, App Composer, Validation Dashboard, Agent Work Board, Pack Browser, Renderer/Theme Laboratory, Build/Test Console, Release Forge, Replay/Trace Viewer, and later domain-specific labs.

A vocabulary split emerged: component, service, provider, pack, module, workspace, app, artifact. This prevents “module” from becoming a junk drawer. Workbench modules are one consumer of the general module system, not the general module system itself.

### 2.5 UI, theme, renderer, and TUI architecture
The conversation specified a modular UI stack: view model, view document, layout, control registry, widget registry, style tokens, theme profiles, projection adapters, and renderer draw lists. The renderer should consume primitives like rects, text, lines, images, clips, alpha, patterns, and 9-slice commands; it should not know about modules or product semantics.

The user wanted OEM+ theme profiles that mimic OS-native styles for Windows, Linux, and macOS eras. The plan accepted this as a strong system test: theme profiles are data/control-skin/layout metric packs, not renderer backends and not copied proprietary assets. Built-in primitive-only themes such as barebones, instrument, paper, terminal, blueprint, high contrast, tactical, phosphor, ledger, and gridline can work without external assets.

TUI received a detailed doctrine: it should be a terminal-native projection of the same operating environment, with panels, tables, split panes, command input, diagnostics, logs, server/admin views, setup recovery, launcher TUI, client strategic fallback, Agent Work Board, and Replay Viewer. It should support Unicode and ASCII fallback and always preserve the command/result/refusal spine.

### 2.6 Engineering law and foundation gates
The user then pushed for portability, modularity, extensibility, and replaceability like a proper game/OS-scale project rather than a one-off indie tool. The conversation developed engineering principles: public surfaces, API/ABI canon, dependency direction, command surfaces, diagnostics, artifact identity, schema/protocol evolution, capability/refusal law, provider model, document/patch/transaction law, module composition law, replacement protocol, version/deprecation law, mod/pack trust model, and portability matrix.

Several queue plans were discussed. Later pasted context stated that foundation scaffolding had happened and the active blocker or next task had changed over time. The final preserved task sequence settled around the need to proceed with COMMAND-RESULT-VIEW-SLICE-01, subject to whatever current gate status applies, because that slice is the bridge between command services and projection/UI/Workbench authoring.

### 2.7 Universe Explorer and game systems
The final phase introduced a Universe Explorer and then a robot seed-civilization game vision. Universe Explorer was framed as the first lawful window into the world, not the world itself. It should prove reference frames, materialization, inspection, no modal loading, fidelity degradation, representation continuity, interest sets, and renderer purity.

The robot seed-civilization direction then introduced player robots, mothership knowledge and constraints, nanobot construction actuators, physical spawn fabricators, terrain cut/fill, field layers, machine graph compilers, factory/process graphs, fog-of-war/sensor models, logistics, infrastructure, governance/claims, and planet generation labs. The answer concluded that Workbench modules and workspaces can be created to build all of this, but they should produce artifacts the actual runtime consumes.

## 3. Main Topics Discussed

### Topic 1 — Original Windows UI Editor and Tool Editor
The chat began with a practical UI tool design. The user wanted a Windows launcher UI fixed and an internal editor capable of producing pixel-perfect, DPI-aware, extensible UI definitions. We explored native Win32 widgets, DUI TLV, codegen, layout engines, stable IDs, canonical TLV, JSON mirrors, action stubs, and imports. This was later superseded as a final product direction but remains relevant as background for Interface Studio and presentation artifact authoring.

### Topic 2 — Dominium Workbench Platform
Workbench became the replacement for UI Editor/Tool Editor. It is a cross-platform, rendered, modular, command-driven production environment. It is not a monolithic IDE or GUI-only editor. It hosts modules and workspaces over shared services, commands, documents, patches, providers, packs, diagnostics, and evidence. It should eventually let a sole developer and agents build code, data, packs, UI, themes, tests, release artifacts, and future games.

### Topic 3 — Unified CLI/TUI/Rendered/Native Presentation Spine
A major conclusion was that all apps should expose one command/result/refusal/document/view spine. CLI, TUI, rendered GUI, OS-native GUI, and headless operation are projections. This preserves semantic parity and reuse across client, server, launcher, setup, Workbench, validators, and future tools. Native GUI remains optional; rendered GUI and TUI are shared runtime surfaces.

### Topic 4 — Modular UI/Layout/Control/Theme/Renderer System
The chat specified a data-driven UI architecture: layouts as data, controls as registered capabilities, themes as token overlays, widgets as compositions, views as typed result/document projections, and renderers as primitive draw-list consumers. OEM+ mimic themes for Windows, macOS, and Linux were identified as an ambitious but valuable test of renderer/UI extensibility.

### Topic 5 — TUI as First-Class Projection
TUI should be a deterministic, keyboard-first, low-dependency projection of the operating environment. It supports the same modules and commands as GUI where practical. It is especially useful for servers, SSH, recovery, setup, CI, agent workflows, and low-end systems. It should not be treated as a second-class ASCII clone.

### Topic 6 — Engineering Constitution / Foundation Queue
The user wanted portability and replaceability like a proper OS or large game engine. The discussion produced a foundation law queue: public surfaces, ABI/API, dependency direction, commands, diagnostics, artifact identity, schemas/protocols, document/patch/transactions, capabilities/refusals, providers, modules, replacement protocols, version/deprecation, mod/pack trust, and portability. This is intended to keep Domino reusable beyond Dominium.

### Topic 7 — Modules, Packs, Providers, Apps, Workspaces
The chat clarified vocabulary. Components are source/build ownership units. Services are callable runtime capabilities. Providers are replaceable implementations. Packs are distributable authored payloads. Modules are declared functional extension units. Workspaces are large Workbench compositions. Apps are shipped product compositions. Artifacts are versioned persisted things. This vocabulary is essential for avoiding future architecture drift.

### Topic 8 — Progressive Self-Hosting
Workbench should not build itself from nothing. It should start from a hand-coded seed substrate, then prove commands/results/views/projections, then minimal Workbench shell, then safe artifact editing, then editing its own layouts/themes/modules, then product UIs, packs, modules, releases, and agent WorkUnits. This avoids circular bootstrapping.

### Topic 9 — Universe Explorer
Universe Explorer was framed as a lawful inspection/materialization/reference-frame proof, not a free-camera renderer demo. It should prove scale continuity, reference-frame correctness, no modal loading, explicit materialization, renderer purity, representation auditability, and evidence export. It should initially be a Workbench module/workspace and later support client/worldgen/server/admin/replay tools.

### Topic 10 — Robot Seed-Civilization Game Systems
The game direction evolved toward robot avatars seeded by a mothership, physical spawn fabrication, nanobot construction as lawful actuator, field-layer planets, sparse cut/fill terrain, machine graphs, factories as process graphs, sensor/fog truth models, infrastructure/logistics, and civilization building without simulating human labor NPCs first. Workbench modules can author/test these artifacts.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals
- Build or plan tools to create and improve Dominium UIs.
- Replace defective launcher UI/flicker with a better architecture.
- Build a cross-platform tools environment using the same CLI/TUI/rendered GUI stack as the client.
- Make the system modular, portable, extensible, reusable for other Domino-based games and even other engine projects.
- Support graphical and agentic development through Workbench, AIDE, and Codex.
- Unify code/data/modules/packs/apps/themes across client, server, setup, launcher, and tools.
- Build Workbench modules that can author the actual game systems and runtime artifacts.

### 4.2 Inferred Goals
- Avoid another directory/refactor disaster by establishing governance first.
- Make Workbench a test harness for the client architecture.
- Make modder/player expectations first-class: themes, packs, modules, UI/HUD authoring, game system extension.
- Avoid vendor/editor lock-in while still using Visual Studio/Xcode for native GUI work where useful.

### 4.3 Goals That Changed Over Time
The goal changed from a Windows-first TLV UI Editor to a cross-platform rendered Workbench. Native-widget UI authoring was deprioritized as the final product direction, while rendered GUI, TUI, command surfaces, modules, packs, documents, patches, evidence, and progressive self-hosting became the core.

### 4.4 Goals Still Unresolved
- Exact current repo gate status must be verified before implementation.
- Exact final directory layout remains under review.
- Presentation contract details are not fully specified.
- Module/pack/provider runtime loading trust model remains staged.
- Workbench implementation order after COMMAND-RESULT-VIEW-SLICE-01 remains dependent on review.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | Abandon old UI Editor/Tool Editor as final products; recycle concepts into Workbench modules | Accepted | Prevents Windows/native-widget one-off tool drift | High | FACT |
| DECISION-02 | Build Dominium Workbench Platform as modular rendered production environment | Accepted conceptually | Gives one reusable production surface for project, tools, modules, packs, agent work | High | FACT/INFERENCE |
| DECISION-03 | Center architecture on contracts/commands/services/documents/patches/providers/packs/modules/artifacts/proof, not Workbench | Accepted | Keeps Workbench as surface, not authority | High | FACT |
| DECISION-04 | CLI, TUI, rendered GUI, OS-native GUI, and headless are projections of one spine | Accepted | Enables reuse and prevents GUI-only semantics | High | FACT |
| DECISION-05 | OS-native GUI remains optional projection; rendered GUI is core shared path | Accepted | Lets Visual Studio/Xcode remain useful without defining the core architecture | High | FACT |
| DECISION-06 | TUI is first-class, not fallback-only | Accepted | Supports server/admin/CI/recovery/SSH/low-end/agent workflows | High | FACT |
| DECISION-07 | Use progressive self-hosting | Accepted | Avoids circular “Workbench builds itself from nothing” | High | FACT |
| DECISION-08 | Use module/pack/provider/app/workspace vocabulary | Accepted | Prevents module/tool/pack junk-drawer confusion | High | FACT |
| DECISION-09 | Build code-only primitive themes first; richer packs/assets optional | Accepted conceptually | Ensures portable baseline and modder extensibility | Medium-high | FACT/INFERENCE |
| DECISION-10 | Universe Explorer should be lawful inspection/materialization proof, not renderer demo | Accepted in assistant recommendation; user asked follow-up | Important for scale and world truth doctrine | Medium | INFERENCE |

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

- Windows-only native UI Editor as final product: superseded. It remains useful as historical bootstrap thinking but not final direction.
- Tool Editor as separate all-in-one editor: superseded by Workbench platform and modules.
- OS SDK native widgets as core cross-platform tool strategy: deprioritized. Native GUI remains optional projection.
- Renderer/free-camera universe as first world implementation: rejected in favor of lawful Universe Explorer.
- Workbench as architecture center: rejected. Contracts/commands/services/proof are the center.
- Arbitrary native plugins early: deferred until trust/sandbox/capability law matures.
- Pixel-perfect proprietary OS theme reproduction: rejected as unsafe/unnecessary; OEM+ mimic through generic assets/tokens is acceptable.

## 7. Important Reasoning, Rationale, and Tradeoffs

The visible rationale centered on avoiding architectural drift. A tool that directly edits private state or owns semantics would become another isolated subsystem. A command/result/refusal spine lets CLI, TUI, GUI, headless, tests, and agents share behavior. A document/patch/transaction model lets visual edits and agent patches remain auditable. A provider/capability/refusal model keeps platforms, renderers, storage, input, UI, and modules replaceable. A pack/module/app descriptor system lets future games and mods reuse Domino without hardcoding Dominium-specific assumptions.

The major tradeoff is upfront governance versus implementation speed. The chat repeatedly balanced not over-governing the project against preventing another refactor disaster. The chosen strategy is foundation first, then narrow product slices. Workbench comes after command/result/view/projection proof because otherwise it would build UI over unstable semantics.

## 8. Plans, Future Work, and Next Steps

Current best near-term sequence, subject to repo verification:

1. `COMMAND-RESULT-VIEW-SLICE-01` — prove one real command, typed result, view contract, projection descriptors, CLI/text/rendered-placeholder parity, diagnostics/evidence.
2. `PHASE-REVIEW-02` — assess whether presentation/projection law is adequate.
3. `PACKAGE-MOUNT-SLICE-01` or `PRESENTATION-CONTRACT-01` depending on the review.
4. `REPLAY-PROOF-SLICE-01`.
5. `BAREBONES-CLIENT-SHELL-01`.
6. `WORKBENCH-SHELL-01`.
7. First Workbench modules: Validation Dashboard, Project Graph Explorer, Agent Work Board, Pack Browser.
8. Later authoring modules: Interface Studio, Theme Laboratory, Renderer Sandbox, Module/Pack Foundry, App Composer, Release Forge.
9. Later world/game modules: Universe Explorer, Field Layer Stack Editor, Planet Generator Lab, Terrain Delta Lab, Construction Blueprint Studio, Machine Graph Lab.

If the live repo still has dependency-direction blockers, repair those before product slices.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences
- User wants rigorous, source-grounded, direct, audit-ready answers.
- User wants modularity, portability, extensibility, replaceability, backwards compatibility, and reuse across other Domino games/projects.
- User does not want one-off indie project practices.
- User values CLI/TUI/rendered/native/headless parity.
- User wants Workbench to build real artifacts consumed by runtime, not pretty mockups.
- User wants AIDE/Codex work to be visible, structured, governed, and evidence-producing.

### 9.2 Inferred Constraints and Preferences
- Prefer contracts and validators over prose-only docs.
- Prefer data-driven UI/theme/module/packs where safe.
- Prefer code-only baseline with optional packs for richer assets.
- Prefer foundation gates before broad Workbench implementation.

### 9.3 Uncertain or Unestablished Preferences
- Exact naming of final Workbench product.
- Exact final paths while repo layout remains under review.
- Exact degree of native GUI support per app.
- Exact renderer backend priority beyond software-first.

## 10. Files, Artifacts, Outputs, and Prompts

Important artifacts from the chat include:

- `source.zip`: uploaded repo/source snapshot; used early for UI/DUI context but not deeply preserved here.
- `SetupC.zip` and `LauncherC.zip`: uploaded screenshot bundles for setup/launcher logical layout references.
- Multiple image mockups: visual references for Workbench modules, themes, TUI, UI/UX directions.
- `Pasted markdown.md`: the user’s detailed preservation-package instructions for this response.
- `Pasted text.txt`: a pasted Universe Explorer / reference-frame / materialization note used in the later discussion.
- Generated in-chat Codex prompts: Prompt 1–11 for old UI Editor plan, UU1–UU6 for import/CLI/ops/launcher/setup/hardening, IDE live-editing prompt, and many planning prompt sequences.
- This preservation package: new downloadable Markdown/YAML/ZIP files created by this task.

## 11. Open Questions and Unresolved Issues

- What is the verified current repo gate status?
- Has `COMMAND-RESULT-VIEW-SLICE-01` already started, or is it next?
- Does dependency-direction strict still block Foundation Closeout?
- What exact physical directories will be used once repo layout review stabilizes?
- What minimal projection descriptor schema should be adopted?
- What is the earliest practical Workbench rendered shell milestone?
- How should Workbench module descriptors interact with general module descriptors?
- What sandbox/trust model will eventually allow third-party modules?
- How soon should Universe Explorer become a Workbench module?

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

Future assistants might incorrectly restart the old UI Editor/Tool Editor plan, treat Workbench as authority, treat GUI as the primary semantics, ignore TUI/CLI/headless parity, overclaim current repo status, lock directory paths prematurely, conflate modules with packs/providers/services, or build Universe Explorer as a renderer demo. Avoid this by preserving the central spine: contracts → commands → services → documents/patches → providers → packs/modules/apps → artifacts/evidence → tests/gates.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat contributes the Workbench doctrine, presentation spine, UI/theme/rendering architecture, module/pack/app/provider terminology, progressive self-hosting plan, TUI doctrine, OEM+ theme strategy, engineering-law framing, and Workbench modules for robot seed-civilization systems. It should feed spec-book chapters on Workbench Platform, Presentation Architecture, Module/Packs/Providers, Engineering Governance, UI/Theme/Renderer, TUI, AIDE/Codex Workflow, Universe Explorer, and Robot Seed-Civilization Design.

## 14. What I Should Remember

- The old UI Editor / Tool Editor was superseded as a final product.
- Workbench is the new production environment, but it is not authority.
- CLI, TUI, rendered GUI, native GUI, and headless must be projections of the same command/result/refusal/document/view system.
- TUI is first-class.
- Rendered GUI uses software renderer first and hardware later.
- Themes are data/token/control-skin profiles; OEM+ mimic is allowed without copied proprietary assets.
- Everything edited should become a document patch validated and committed with evidence.
- Modules, packs, providers, apps, workspaces, artifacts, services, and components are distinct.
- Progressive self-hosting is the only safe bootstrapping path.
- Universe Explorer should prove lawful inspection/materialization, not just free camera rendering.
- Workbench can author game systems if those systems are real runtime artifacts.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- “Explain the difference between module, pack, provider, service, component, workspace, app, and artifact again with examples.”
- “What parts of the old UI Editor plan should be recycled into Interface Studio?”

### 15.2 Decisions
- “Which decisions are final versus tentative?”
- “What would cause us to revisit the Workbench-first direction?”

### 15.3 Tasks and Next Actions
- “Write the Codex/AIDE prompt for COMMAND-RESULT-VIEW-SLICE-01.”
- “Write the no-apply plan for PRESENTATION-CONTRACT-01.”

### 15.4 Artifacts and Files
- “List every prompt generated in this chat and what it was for.”
- “Create a compact artifact map from this preservation package.”

### 15.5 Risks and Verification
- “What repo-current facts in this chat must be verified before implementation?”
- “What are the top 10 ways Workbench could accidentally become architectural authority?”

### 15.6 Future Spec Book / Aggregation
- “Which sections of a master Project Spec Book should this chat feed?”
- “What overlaps should be reconciled with other chats?”

### 15.7 Deep-Dive Questions Specific to This Chat
- “Design the minimal presentation descriptor schema.”
- “Design the Validation Dashboard vertical slice.”
- “Design the Field Layer Stack Editor artifact model.”

## 16. Compact Human Summary

This chat began with a concrete UI tooling problem: the Dominium launcher UI looked mangled and flickered, and the user wanted a Windows-first UI Editor / Tool Editor to author pixel-perfect UIs and generate DUI/TLV code. We explored that plan in detail: platform choices, native widgets, canonical TLV, JSON mirrors, layouts, stable IDs, action codegen, import/export, CLI ops scripts, launcher/setup redesign tests, and Codex prompt plans.

The plan then changed substantially. The user concluded that the old UI Editor and Tool Editor were useful ideas but not good final products. The conversation moved toward a cross-platform rendered Workbench: one modular production environment using the same CLI, TUI, rendered GUI, command, pack, diagnostics, renderer, and evidence systems as the client. Workbench should not be a Visual Studio clone, not a native-widget-first editor, and not a one-off GUI app. It should be a modular shell over shared services and commands.

The central architectural conclusion was that CLI, TUI, rendered GUI, OS-native GUI, and headless execution should all be projections of the same command/result/refusal/document/view system. This applies to client, server, launcher, setup, Workbench, validators, AIDE/Codex workflows, and future admin/modding tools. Workbench becomes the richest projection and authoring environment, but it is not semantic authority.

The chat also established a vocabulary and modularity model. Components are source/build ownership units. Services are callable runtime capabilities. Providers are replaceable implementations. Packs are authored distributable payloads. Modules are functional extension units. Workspaces are user-facing Workbench compositions. Apps are product compositions. Artifacts are persisted versioned things. This vocabulary prevents “module” from becoming a junk drawer.

The UI architecture became data-driven and renderer-neutral: view models, view documents, layout engines, controls, widgets, style tokens, themes, and projection descriptors are separate. The rendered GUI should use a software renderer baseline and later hardware backends. TUI is a first-class projection. OS-native GUI is optional and should still call the command/view spine. Themes can mimic OEM+ Windows/macOS/Linux styles through generic tokens, metrics, and skins without copying proprietary assets.

The user also emphasized portability and future-proofing. The project should be built like a proper OS/game engine, not a one-off indie project. This led to engineering-law queues around public surface registry, API/ABI canon, dependency direction, commands, diagnostics, artifact identity, schemas/protocols, document/patch/transaction law, capabilities/refusals, providers, module composition, replacement, versioning, mod/pack trust, and portability.

Later, the discussion connected Workbench to game systems. The user introduced a universe-scale/robot seed-civilization concept: players are robots seeded by a mothership, using nanobots, fabricators, physical spawn labs, field-layer planets, terrain cut/fill, machine graphs, factories, fog-of-war sensors, logistics, infrastructure, governance, and civilization-scale development. The conclusion was that Workbench modules can build all of this if they author runtime-consumed artifacts rather than mockups. Important future modules include Universe Explorer, Planet Generator Lab, Field Layer Stack Editor, Terrain Delta Lab, Construction Blueprint Studio, Machine Graph Lab, Factory Graph Editor, Spawn Fabricator Lab, Fog-of-War Lab, Logistics Planner, City/Civilization Planner, and Governance/Claims Lab.

The best next step is not a big Workbench GUI. It is the smallest projection proof: COMMAND-RESULT-VIEW-SLICE-01, unless the live repo gate still requires dependency-direction repair first. That slice should prove one real command, typed result, view contract, projection descriptors, CLI output, TUI/text output, rendered-placeholder output, diagnostics, and evidence. This is the bridge from foundation law to future Workbench, client, launcher, setup, server, and game UI. 
