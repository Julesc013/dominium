# Dominium Workbench Full Conversation Companion Report

**Date anchor:** 2026-05-27 Australia/Melbourne  
**Scope:** This report summarizes the visible conversation and accompanies the existing preservation package.  
**Reliability note:** This is a human-readable consolidation, not a live repository audit. Repo-current statements that came from pasted material or prior-chat excerpts remain **UNVERIFIED** until checked against the live `julesc013/dominium` repo and current AIDE/validator outputs.

---

## 1. Executive Summary

This conversation started as a practical plan to build a Windows-first internal UI Editor / Tool Editor to fix the Dominium launcher UI and visually author setup, launcher, game, and tool interfaces. It then evolved into a much larger and more durable architecture: **Dominium Workbench Platform**, a cross-platform rendered, TUI-capable, CLI/headless-compatible, modular production environment for building the entire Domino/Dominium ecosystem.

The original UI Editor / Tool Editor plan is now **superseded as a final product**. It is not lost: its useful parts become Workbench capabilities, especially Interface Studio, UI/HUD Sandbox, Theme Laboratory, TUI Studio, Rendered GUI Studio, Preview Matrix, validation panels, import/export tools, and document-patch workflows.

The central decision is that Workbench must not become semantic authority. Workbench is a surface over contracts, commands, services, documents, patches, providers, packs, modules, apps, artifacts, diagnostics, evidence, tests, and replay/proof. It is the richest human/agent interface over the system, but it must not bypass command, capability, refusal, validation, document, patch, or proof law.

The second central decision is that CLI, TUI, rendered GUI, OS-native GUI, and headless automation must be **projections of the same command/result/refusal/document/view spine**. A GUI button, a TUI hotkey, a CLI command, a headless JSON job, and a future OS-native widget action should route through the same command/service path and produce the same typed result, diagnostics, refusals, logs, and evidence.

The conversation also expanded the target from “build a tool” to “build the production environment for a deterministic simulation operating environment.” Domino is the reusable substrate. Dominium is one game/product family. Workbench is the production, validation, editing, inspection, packaging, and evidence environment. AIDE governs work. Codex executes bounded patches. Contracts are law. Tests, replay, and evidence are proof.

The practical next objective, subject to live repo verification, is **COMMAND-RESULT-VIEW-SLICE-01**: prove one real command through a typed result, view contract, projection descriptor, CLI output, TUI/text output, rendered-placeholder output, diagnostics, refusals, and evidence. The Validation Dashboard remains the best first Workbench module because it is immediately useful and proves command/result/diagnostic/evidence parity without requiring full gameplay.

---

## 2. How the Conversation Developed

### 2.1 The initial UI Editor / Tool Editor phase

The first phase focused on a Windows launcher UI that looked mangled and flickered. The proposed solution was an internal graphical editor capable of designing pixel-perfect UIs and broad-strokes functionality for setup, launcher, game, and other tools. The early plan assumed Windows first, later Windows/macOS/Linux support, true OS controls where possible, CMake integration, stable file formats, generated stubs, and a visual authoring environment.

The user provided concrete details about the existing DUI system: the launcher used a TLV schema/state model, with Win32, DGFX, and null backends. The likely flicker sources were Win32 relayout on `WM_SIZE`, `RedrawWindow`, list resets/invalidates, and visibility toggles mapping to `ShowWindow` on child controls. This grounded the plan in actual existing systems rather than abstract UI-tool speculation.

The resulting old plan included canonical UI IR, deterministic TLV output, JSON mirrors, safe atomic saves, stable IDs, capability validation, layout engines, splitter/tabs/scroll widgets, action stubs, event dispatch, UI Editor GUI, Tool Editor bootstrap, import/export, CLI scripting, `ops.json`, and tests. Many Codex prompts were generated around those ideas.

### 2.2 The import/CLI/ops and launcher/setup capability-test phase

The plan was then extended so the UI Editor could import existing tool UIs, provide a CLI suitable for Codex automation, and use scripted `ops.json` changes to create logical “Minecraft-style” launcher and setup layouts. The user clarified that “Minecraft-style” referred to layout and flow, not visual skin. All controls were to remain native Win32 controls in that earlier phase.

That phase generated more Codex prompts: UI discovery/import/export, CLI validate/format/codegen, `ops.json` editing, launcher UI generation, setup UI generation, and hardening/CI. These are now **historical/superseded** but still useful as implementation material for future document/patch/CLI authoring workflows.

### 2.3 The pivot to Workbench

The user then rejected the old UI Editor / Tool Editor as final products. The user wanted cross-platform tools that use the same CLI, TUI, and rendered GUI systems as the client, not tools dependent on OS-native widgets. OS-native tools like Visual Studio and Xcode remain useful, but they are not the core presentation platform. This changed the plan from a UI editor to a **Workbench Platform**.

The new goal became a cross-platform rendered Workbench app: one app, many modules, many workspaces, many themes, many renderer backends, and one shared command/document/patch/evidence spine. This Workbench would eventually be used to build Domino, Dominium, packs, modules, UI, themes, tests, releases, and AIDE/Codex work units.

### 2.4 The unified presentation spine

The conversation then focused on how all apps could share CLI, TUI, rendered GUI, OS-native GUI, and headless behavior. The conclusion was that each product should declare which presentation modes it supports, but all products should share the same semantic command/result/refusal/document/view model.

This avoids four independent implementations for the same behavior. A validation command should produce one result schema and then be projected as CLI table/JSON, TUI panel, rendered dashboard, native list/detail, and headless report.

### 2.5 Workbench as production environment

The user emphasized that Workbench is not only for inspection. It should be the integrated environment for building the entire project: code, data, contracts, packs, modules, UIs, themes, renderer tests, sounds, release artifacts, and agentic workflows. The Workbench should support human development, agent work, CLI/TUI/rendered workflows, and evidence/proof.

This led to the idea of Workbench as:

- Command OS.
- Creation Studio.
- Evidence Notebook.
- System Graph.
- Preview/Sandbox.
- Agent Control Board.
- Release Forge.

The user-facing large tools became **workspaces** rather than base modules: Project Graph Explorer, Interface Studio, Module/Pack Foundry, App Composer, Release Forge, Universe Explorer, and so on. These are built from smaller reusable modules, views, documents, commands, services, validators, inspectors, graph views, preview canvases, evidence panels, and patch/diff viewers.

### 2.6 Modular UI, themes, TUI, and renderer

The conversation then described how layout, controls, themes, styles, views, and projections should be modular. The answer was a layered UI architecture: view model, view document, style/theme tokens, runtime controls/widgets/layouts, and renderer backend. Themes are data/token/control-skin profiles, not renderer backends or product logic. Renderers consume draw lists and do not know about products, commands, or OS theme identities.

The user explored OEM+ theme profiles inspired by Windows, Linux desktops, and macOS eras. The answer was that code-only primitive rendering can support useful themes such as barebones, instrument, kernel, paper, terminal, blueprint, phosphor, gridline, tactical, ledger, cartographic, and high contrast. Richer icons, textures, fonts, sounds, and photoreal elements can become optional packs.

The TUI was also treated as a first-class projection. It should not be a second-class ASCII clone; it should be the deterministic, keyboard-first, low-dependency projection of the same operating environment.

### 2.7 Engineering law and repo future-proofing

The user then asked about portability, modularity, extensibility, naming, schemas, protocols, ABI, APIs, and directory structure. The discussion established that the real problem is not just folders; it is engineering law. Public surfaces, ABI rules, schemas, protocols, commands, diagnostics, artifacts, capabilities, providers, modules, packs, replacements, versions, deprecations, tests, and evidence must all be contract-governed.

A precise vocabulary was adopted:

- Component = source/build ownership unit.
- Service = callable runtime capability.
- Provider = replaceable implementation.
- Pack = distributable authored payload.
- Module = declared functional extension unit.
- Workspace = large user-facing Workbench composition.
- App = shipped product composition.
- Artifact = versioned persisted output/input.

The key warning is that paths are not identity. Stable identity lives in contracts, registries, manifests, IDs, schemas, and artifacts. Implementations can be replaced.

### 2.8 Self-hosting ladder

The user asked how to build Workbench and then use it to build itself and everything else. The answer was **progressive self-hosting**:

1. Hand-code seed substrate.
2. Define commands/results/refusals/diagnostics/documents/views/patches.
3. Prove CLI/TUI/rendered/headless projection for one command.
4. Build minimal Workbench shell.
5. Workbench edits safe non-critical artifacts.
6. Workbench edits its own layout/theme/module documents.
7. Workbench builds product UIs, modules, packs, app compositions, releases, and agent work units.

This avoids the circular trap of expecting Workbench to build itself before the substrate exists.

### 2.9 Universe Explorer and the robot seed-civilization game

The final major expansion connected Workbench to the actual game direction. Universe Explorer was framed as a lawful inspection/materialization/reference-frame proof surface, not a renderer/free-camera demo. It should prove scale continuity, no modal loading, reference frames, materialization, representation ladders, interest sets, fidelity, provenance, renderer purity, and evidence.

The user then introduced a robot seed-civilization game concept: robotic player avatars, mothership knowledge and constrained fabrication, physical spawn labs, nanobot construction, terrain cut/fill, field layers, machine graphs, factories, fog-of-war through sensors, logistics, cities, claims, governance, and civilization. The answer was that Workbench modules and workspaces can build this if they author real runtime artifacts.

Proposed Workbench spaces include Universe Explorer, Star System/Planet Generator Lab, Field Layer Stack Editor, Cut/Fill Terrain Delta Lab, Construction Blueprint Studio, Machine Graph Lab, Factory/Process Graph Editor, Robot Body/Spawn Fabricator Lab, Mothership Planner, Sensor/Fog-of-War Lab, Logistics/Infrastructure Planner, City/Civilization Planner, Governance/Claims/Permissions Lab, Performance/Complexity Budget Lab, and Renderer/External Bridge Lab.

---

## 3. What Was Decided

### 3.1 Final product direction

**Decision:** Old UI Editor and Tool Editor are superseded as final products.  
**Replacement:** Dominium Workbench Platform.  
**Reason:** The old plan risked becoming a separate one-off tool architecture. Workbench can instead prove and reuse the same systems as the client, launcher, setup, server, and future tools.

### 3.2 Workbench authority boundary

**Decision:** Workbench is not authority.  
**Reason:** If Workbench mutates files, truth, or product behavior directly, it will drift from CLI/headless/TUI/runtime semantics. Workbench must issue commands, produce patches, preview, validate, commit transactions, and record evidence.

### 3.3 Unified presentation spine

**Decision:** CLI, TUI, rendered GUI, OS-native GUI, and headless are projections of the same command/result/refusal/document/view model.  
**Reason:** This lets one command and one result schema drive every interface. It prevents duplicated logic and lets Workbench modules be reused by client, launcher, setup, server, and tools.

### 3.4 Native GUI role

**Decision:** OS-native GUI is optional projection, not the core architecture.  
**Reason:** Visual Studio, Xcode, Win32, AppKit, GTK, etc. remain useful for OS SDK native shells, but the cross-platform rendered Workbench/client path should not depend on them.

### 3.5 TUI role

**Decision:** TUI is first-class.  
**Reason:** It supports servers, SSH, recovery, setup fallback, CI, low-end systems, accessibility, and agent supervision. It must project the same commands and results as GUI/CLI.

### 3.6 Renderer and theme model

**Decision:** Software renderer first; hardware renderers later. Themes are token/control-skin/layout-metric profiles. Renderer consumes draw lists only.  
**Reason:** This maximizes portability, testability, and reuse.

### 3.7 Vocabulary and modularity

**Decision:** Use the component/service/provider/pack/module/workspace/app/artifact vocabulary.  
**Reason:** It prevents `module`, `tool`, and `component` from becoming vague junk drawers.

### 3.8 Progressive self-hosting

**Decision:** Workbench should become self-hosting gradually.  
**Reason:** It avoids circular bootstrapping and prevents unsafe self-modification.

### 3.9 Universe Explorer role

**Decision/recommendation:** Universe Explorer should be a lawful inspection/materialization proof, not a free-camera renderer demo.  
**Reason:** It should prove Dominium’s reality doctrine and multiscale representation system.

---

## 4. What Was Superseded or Put Off for Later

### Superseded

- Windows-first UI Editor as final product.
- Native-widget Tool Editor as final product.
- GUI-only authoring workflows.
- Tooling that does not use the runtime/client presentation systems.
- Rendering-focused Universe Explorer without command/materialization/refinement law.

### Recycled

- Visual layout authoring.
- Import/export.
- UI documents.
- CLI automation.
- `ops.json`-style command scripts.
- Codegen/stubs.
- Validation panels.
- Property inspectors.
- Hierarchy trees.
- Launcher/setup logical layout tests.

These now belong in Workbench modules and services.

### Deferred

- Arbitrary third-party native plugins.
- Full OS-native GUI authoring as core Workbench behavior.
- Full Interface Studio before command/result/view/projection proof.
- Full Universe Explorer before package/replay/client/workbench foundations.
- Full robot civilization simulation before field layers, terrain deltas, machine graphs, and proof systems exist.
- Exact final physical directory structure while repo layout remains under review.

---

## 5. The Architecture We Converged On

The final conceptual architecture is:

```text
Contracts define law.
Services execute behavior.
Commands expose behavior.
Documents hold editable state.
Patches mutate state lawfully.
Providers replace implementations.
Packs distribute authored payloads.
Modules declare capabilities.
Workspaces present workflows.
Apps compose products.
Artifacts preserve evidence and state.
Tests prove invariants.
AIDE governs repo work.
Codex executes bounded patches.
Workbench operates the system.
```

The key integration chain is:

```text
User input / script / agent
→ command
→ capability/refusal law
→ service
→ document patch or typed result
→ diagnostics/evidence
→ view model
→ projection:
     CLI
     TUI
     rendered GUI
     OS-native GUI
→ same artifacts, same logs, same proof
```

Workbench fits here as the rich human/agent projection and authoring environment.

---

## 6. How CLI, TUI, Rendered GUI, Native GUI, and Headless Integrate

The shared truth is not a button or widget. The shared truth is a command/result/document/view contract.

Example:

```text
command: tools.validation.run
result: validation_run_result.v1
view: view.validation.summary
```

This can project as:

- CLI table or JSON.
- TUI panel.
- Rendered dashboard.
- Native list/detail view.
- Headless report/evidence packet.

Each projection has different affordances but the same semantics. This is how Workbench modules, server tools, setup, launcher, and client debug surfaces can reuse the same systems.

---

## 7. How the Rendered GUI Is Built

The rendered GUI pipeline is:

```text
command/result/document state
→ view model
→ UI document / workspace layout
→ layout engine
→ style/theme resolver
→ control tree
→ draw command list
→ renderer backend
```

The renderer only knows primitives:

- rectangles,
- lines,
- text,
- images/bitmaps eventually,
- clipping,
- alpha,
- patterns,
- gradients,
- 9-slice-like panels,
- screenshot/capture.

The renderer does not know what a Validation Dashboard, Pack Browser, Windows XP theme, or Workbench module is. This keeps the renderer reusable by client, setup, launcher, server admin surfaces, Workbench, and future games.

---

## 8. How the TUI Is Built

TUI is a projection over the same views and commands. It uses:

- panels,
- split panes,
- tabs,
- tables,
- trees,
- forms,
- log views,
- command line,
- status bars,
- keyboard navigation,
- Unicode box drawing with ASCII fallback,
- limited color.

The TUI is not a toy fallback. It is the deterministic, keyboard-first, low-dependency surface for servers, recovery, SSH, CI, accessibility, AIDE/Codex supervision, setup fallback, launcher fallback, and client strategic/debug fallback.

---

## 9. How Workbench Modules and Workspaces Work

A module contributes:

- commands,
- documents,
- views,
- editors,
- inspectors,
- preview panes,
- validators,
- import/export definitions,
- patch generators,
- test fixtures,
- agent task templates,
- UI panels.

A workspace is a large user-facing composition made from modules and services.

Examples:

- Project Graph Explorer.
- Interface Studio.
- Module / Pack Foundry.
- App Composer.
- Release Forge.
- Agent Control Workspace.
- Renderer / Theme Laboratory.
- Replay / Trace Workspace.
- Universe Explorer.

Smaller reusable modules include:

- Command Browser.
- Document Inspector.
- Patch/Diff Viewer.
- Validation Runner.
- Diagnostics Viewer.
- Evidence Viewer.
- Pack Browser.
- Provider Browser.
- Capability Matrix Viewer.
- Theme Previewer.
- Renderer Test Panel.
- Asset Browser.
- Project Graph View.
- Build/Job Console.
- Agent Task Queue.

---

## 10. How Workbench Builds Itself and Everything Else

The self-hosting staircase is:

```text
1. Build command/result/refusal spine by hand.
2. Build document/patch/transaction spine by hand.
3. Build CLI projection by hand.
4. Build TUI projection enough for validation dashboard.
5. Build software-rendered draw-list and primitive controls.
6. Build rendered validation dashboard.
7. Use validation dashboard to monitor future work.
8. Build project graph viewer.
9. Use project graph viewer to understand/repair architecture.
10. Build theme lab + renderer sandbox.
11. Use them to harden rendered UI and themes.
12. Build Interface Studio.
13. Use Interface Studio to build Workbench panels.
14. Use Interface Studio to build launcher/setup/client/server UI docs.
15. Build Module/Pack Foundry.
16. Use it to create modules/packs/themes/templates.
17. Build App Composer.
18. Use it to assemble client/launcher/setup/server/workbench variants.
19. Build Agent Work Board.
20. Use it to create/review AIDE/Codex work units.
21. Build Release Forge.
22. Use it to package and prove releases.
```

This is progressive self-hosting. Workbench does not build itself from nothing. It gradually gains authority over safer artifact classes.

---

## 11. Workbench Modules for the Robot Seed-Civilization Game

The robot seed-civilization game direction is compatible with Workbench if game content is represented as real runtime artifacts.

Key Workbench spaces:

- Universe Explorer.
- Star System / Planet Generator Lab.
- Field Layer Stack Editor.
- Cut / Fill / Terrain Delta Lab.
- Construction Blueprint Studio.
- Machine Graph Compiler / Lab.
- Factory / Process Graph Editor.
- Robot Body / Spawn Fabricator Lab.
- Mothership Planner.
- Sensor / Fog-of-War Lab.
- Logistics / Infrastructure Planner.
- City / Civilization Planner.
- Governance / Claims / Permissions Lab.
- Performance / Complexity Budget Lab.
- Renderer / Unreal or external bridge lab.

These should produce artifacts that the runtime actually consumes:

- planet specs,
- field layer stacks,
- terrain delta operations,
- construction plans,
- machine graphs,
- factory graphs,
- spawn lab descriptors,
- mothership policies,
- sensor/fog policies,
- logistics graphs,
- claim policies,
- complexity budgets,
- render snapshots,
- evidence packets.

---

## 12. What Was Done in the Conversation

The conversation produced:

1. Multiple old UI Editor Codex prompts and prompt plans.
2. UU1–UU6 prompt plans for UI import/CLI/ops/launcher/setup tests.
3. A VS/Xcode/Linux IDE live-editing prompt.
4. A major architecture pivot to Workbench.
5. A full Workbench/product/presentation doctrine.
6. A TUI doctrine.
7. Theme and renderer architecture.
8. A component/service/provider/pack/module/workspace/app vocabulary.
9. Progressive self-hosting doctrine.
10. Universe Explorer doctrine.
11. Robot seed-civilization Workbench module roadmap.
12. A previous detailed preservation package with reports, registers, spec sheet, aggregator packet, and ZIP.
13. This companion summary package and ZIP.

---

## 13. What Was Put Off for Later

Items explicitly or implicitly delayed:

- Full Workbench GUI implementation.
- Interface Studio.
- Theme Laboratory.
- Renderer Sandbox.
- Universe Explorer 0.
- Third-party module/plugin runtime.
- Arbitrary native plugin support.
- Full OS-native GUI projection system.
- Full visual UI/HUD editing.
- Full robot civilization simulation.
- Unreal/external renderer bridge.
- Full package/mod trust runtime.
- Exact final folder layout.
- Exact final Workbench app classification.
- Current live repo gate verification.

---

## 14. What Is Missing or Needs More Thought

The plan is strong, but several important systems need formal specs:

1. **Presentation contract**  
   The minimal schema linking commands/results/documents to CLI/TUI/rendered/native/headless projections.

2. **View/action binding model**  
   How actions are exposed, validated, and mapped across modes.

3. **Document/patch/transaction runtime**  
   The safe mutation model for Workbench, CLI, TUI, agents, and migrations.

4. **Projection conformance tests**  
   Golden CLI output, TUI cell buffers, rendered layout trees/screenshots, and native view descriptors.

5. **Module conformance kits**  
   Modules need tests beyond descriptors.

6. **Provider conformance kits**  
   Renderers, storage, package loaders, input systems, etc. need standard conformance tests.

7. **Project graph service**  
   Workbench needs a system graph connecting files, contracts, commands, services, modules, packs, apps, tests, artifacts, and evidence.

8. **Localization/accessibility contracts**  
   String IDs, keyboard focus, screen reader labels, contrast, reduced motion, large text, and TUI fallback should not be bolted on late.

9. **Asset/license/provenance model**  
   Theme packs, sound packs, icon packs, and mod packs need origin/license/hash/provenance metadata.

10. **Security/trust model**  
   Data-only packs first, built-in compiled modules second, external adapters later, sandboxed plugins later, arbitrary native plugins last if ever.

11. **Performance budgets**  
   Every renderer/UI/module/game artifact should eventually expose sim/render/network/storage/pathfinding/expansion budgets.

12. **Rollback/recovery model**  
   For Workbench edits, package changes, releases, save migrations, and agent patches.

---

## 15. Key Risks

### 15.1 Workbench becomes authority

If Workbench directly mutates source, runtime truth, or product behavior, it breaks the whole doctrine. It must issue commands and patches and rely on services, validation, and evidence.

### 15.2 UI modes drift

If CLI/TUI/rendered/native/headless paths are built independently, products will diverge. Projection contracts and parity tests prevent this.

### 15.3 Modules become a junk drawer

Without strict vocabulary, modules will absorb services, providers, apps, packs, and workspaces. The component/service/provider/pack/module/workspace/app/artifact split prevents this.

### 15.4 Repo-current facts go stale

Several queue/foundation/current-state claims came from pasted context from other chats. They must be verified before implementation.

### 15.5 Universe Explorer becomes a renderer demo

If built as a free camera first, it may violate materialization, reference frame, interest, and truth/render separation. It must be a lawful inspection/projection surface.

### 15.6 Theme mimicry crosses legal lines

OEM+ mimic themes should use generic tokens and assets, not copied proprietary OS fonts/icons/textures/wallpapers.

---

## 16. Best Current Next Action

The safest immediate next action is:

```text
Verify current live repo status and task gate state.
```

If gates allow, proceed with:

```text
COMMAND-RESULT-VIEW-SLICE-01
```

Minimum proof:

```text
registered command
→ typed result schema
→ view contract
→ projection descriptor
→ CLI output
→ TUI/text output
→ rendered-placeholder output
→ diagnostics/refusals/evidence
```

Recommended first command:

```text
dominium.validation.run
```

Recommended first Workbench module:

```text
Validation Dashboard
```

This is the smallest useful bridge from governance and command infrastructure to Workbench, TUI, rendered GUI, client shell, setup, launcher, and server admin surfaces.

---

## 17. Human-Readable Decision Table

| Decision | Status | Why it matters |
|---|---|---|
| Old UI Editor/Tool Editor no longer final products | Accepted | Avoids one-off native editor architecture |
| Workbench is the new production environment | Accepted | Unifies human, agent, CLI, TUI, GUI, modules, packs, releases |
| Workbench is not authority | Accepted | Preserves determinism, reuse, validation, evidence |
| CLI/TUI/rendered/native/headless share one spine | Accepted | Prevents duplicated product logic |
| TUI is first-class | Accepted | Supports servers, recovery, CI, SSH, agents |
| Rendered GUI uses software-first draw-list renderer | Accepted direction | Portable/testable baseline before GPU |
| Native GUI is optional projection | Accepted | Keeps OS SDK tools useful but non-authoritative |
| Themes are data/token/control-skin profiles | Accepted direction | Moddable and renderer-neutral |
| Modules/packs/providers/apps/workspaces are distinct | Accepted direction | Prevents taxonomy drift |
| Workbench self-hosts progressively | Accepted | Avoids circular bootstrap |
| Universe Explorer is lawful inspection proof | Recommended | Prevents renderer/free-camera trap |

---

## 18. Reader Guidance

If you want to continue this work, do not restart with UI Editor. Start from Workbench and the presentation spine.

If you need a short formulation:

> Dominium Workbench is the visual, TUI, CLI, and agentic production environment for building Domino/Dominium artifacts. It edits documents through patches, validates through contracts, previews through projections, packages through packs, and proves work through evidence. It is not authority; contracts and runtime services are authority.

If you need the immediate task:

> Verify repo state, then generate `COMMAND-RESULT-VIEW-SLICE-01`.

If you need the long-term target:

> Build Workbench modules and workspaces that can author every real runtime artifact used by client, server, launcher, setup, Workbench, packs, mods, themes, Universe Explorer, and robot seed-civilization gameplay systems.
