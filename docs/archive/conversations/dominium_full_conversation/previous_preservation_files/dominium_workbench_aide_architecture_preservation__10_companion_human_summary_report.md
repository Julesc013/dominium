# Companion Human-Readable Detailed Summary and Report

**Chat label:** Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, and Product-Spine Planning  
**Date anchor:** 2026-05-27 Australia/Melbourne  
**Source scope:** This chat only, plus explicitly identified uploaded/generated files from this chat.  
**Reliability note:** This is a companion report to the preservation package already generated in this chat. It is a human-readable narrative and decision/tradeoff explanation, not a raw transcript. Live repository state, external software status, and package/library versions must be verified before implementation.

---

## 1. What this conversation became

This conversation began as a practical UI tooling discussion and became a broad architectural planning thread for Dominium, Domino, Workbench, AIDE, presentation/projection systems, provider strategy, and the next product-spine development path.

The original problem was concrete: the Windows launcher UI looked broken, and the user wanted an internal visual editor that could design pixel-perfect UIs for launcher, setup, game, and tools. Early discussion therefore focused on a Windows-first UI Editor, a later Tool Editor, DUI/TLV documents, Win32/DGFX/null backends, native controls, layout engines, code generation, JSON mirrors, CLI scripting, import/export, and launcher/setup design tests.

That original plan was progressively superseded. The user recognized that a Windows-first UI Editor and later Tool Editor were good temporary ideas but bad final products. Visual Studio, Xcode, and other OS SDK tools already exist for native widgets. What Dominium actually needs is a cross-platform rendered tools environment that uses the same runtime, command system, renderer, presentation layer, pack/module system, evidence system, diagnostics, and AIDE/Codex workflow as the client and other products. That became the Dominium Workbench Platform.

The final product concept is therefore not “an editor.” It is a production environment: a rendered, modular, command-driven, agent-aware system that can inspect, validate, edit, preview, package, test, prove, and eventually help build the entire Domino/Dominium project. It is intended to become the interface through which the user, AIDE, and Codex can work on code, data, packs, modules, themes, UIs, tests, artifacts, release plans, and eventually the client/game itself.

The most important correction made throughout the conversation is this:

> Workbench is not authority. It is a surface over contracts, commands, services, documents, patches, providers, packs, modules, artifacts, diagnostics, evidence, tests, and replay/proof.

That doctrine prevents Workbench from becoming a second source of truth or another one-off UI framework. The runtime executes artifacts. Contracts constrain artifacts. Content packages artifacts. Apps consume artifacts. Tests and evidence prove artifacts. AIDE governs work. Codex executes bounded patches.

---

## 2. The central architecture

The conversation converged on a stable conceptual split:

```text
Domino    = reusable deterministic substrate
Dominium  = game/product family on Domino
Workbench = production, validation, editing, inspection, packaging, and evidence environment
AIDE      = repo/control-plane harness
Codex     = bounded patch executor
Contracts = law
Diagnostics / tests / replay / evidence = proof
```

This split matters because the user wants a professional-grade, future-proof project, not a one-off indie architecture. Domino should be reusable for other games and engine projects. Dominium is one product family. Workbench is a product built over the same substrate, not a separate toolchain. AIDE manages repo workflow and evidence. Codex makes bounded changes.

The enduring spine is:

```text
intent
→ command
→ capability/refusal check
→ service or deterministic process
→ result | document | snapshot
→ diagnostics/evidence
→ view/action model
→ projection
→ shell
```

Every serious surface should eventually route through this spine: CLI, TUI/text, rendered GUI, OS-native GUI, headless reports, Workbench panels, CI, AIDE, and Codex workflows. This avoids the common failure mode where a GUI button, terminal command, native dialog, and test script each implement subtly different semantics.

The composition spine is related:

```text
app descriptor
+ profile
+ packs
+ modules
+ providers
+ platform
+ renderer
+ trust policy
+ capabilities
→ composition resolver
→ selected providers
→ mounted packs
→ enabled modules
→ capability set
→ refusals/degradations
→ lockfiles
→ evidence packet
```

This is what allows apps to remain generic and provider choices to live in profiles rather than app directory names.

---

## 3. How the UI plan changed

### 3.1 Original UI Editor / Tool Editor

The first plan was to build a Phase A Windows UI Editor, then a more complete Tool Editor. The initial prompt plan included repo scaffolding, UI IR, TLV I/O, capabilities, layout, new widgets, action codegen, editor UI, Tool Editor bootstrap, flicker fixes, import/export, CLI ops scripting, and launcher/setup redesign tests.

This was useful because it forced many concrete decisions:

- TLV would be the canonical UI document format.
- JSON mirrors were useful for diffs and review.
- Stable action keys and generated user stubs were important.
- UI definitions should be universal and reusable.
- The system needed import/export and CLI/headless automation for Codex.
- Layout, property inspection, hierarchy editing, validation, and preview remained important concepts.

But this plan was not retained as the final product.

### 3.2 Why it was superseded

The user explicitly moved away from a native-widget-first editor. The old editor path risked building one Windows-first tool that was separate from the runtime and would later require a second refactor. It would have solved the launcher UI problem but not proven the client, renderer, pack, module, command, projection, evidence, and AIDE workflows.

The replacement was Workbench: one modular production shell with many modules. The old UI Editor becomes Interface Studio or UI/HUD Sandbox inside Workbench. The old Tool Editor becomes Workbench shell plus module system. Codegen, import/export, validation, live preview, property inspector, and hierarchy tree become reusable services/views/modules.

---

## 4. Workbench as production environment

Workbench is intended to be the user’s main environment for building Dominium and later other Domino-based projects. It should not open as “an editor with panels.” It should open around intent:

```text
What are you building, inspecting, fixing, running, packaging, or proving?
```

The user and assistant converged on a Workbench made of:

- Command OS
- Creation Studio
- Evidence Notebook
- System/Project Graph
- Preview/Sandbox
- Agent Control Board
- Release Forge

Workbench should eventually support modules/workspaces such as:

- Validation Dashboard
- Project Graph Explorer
- Agent Work Board
- Pack Browser
- Component Matrix Viewer
- Theme Laboratory
- Renderer Sandbox
- Interface Studio
- Layout Studio
- TUI Studio
- Rendered GUI Studio
- Module / Pack Foundry
- App Composer
- Release Forge
- Replay / Trace Viewer
- Asset / Sound Lab
- World / Scenario Lab
- Material / Process Lab

The important implementation rule is that these are not hardcoded mini-apps. They should be assembled from reusable services, commands, document types, patches, views, projections, widgets, layouts, and evidence outputs.

The first useful Workbench should be read-only. It should inspect commands, views, diagnostics, artifacts, packs, project graph, validation reports, capabilities, and provider status. Only after this should it edit sample artifacts, then non-critical content artifacts, then copies of its own layout/theme/workspace docs, then live Workbench presentation docs, and finally generate module/app skeletons and AIDE/Codex work units.

---

## 5. Unified CLI, TUI, rendered GUI, native GUI, and headless projection

A major result of the conversation was the presentation/projection doctrine. CLI, TUI/text, rendered GUI, OS-native GUI, and headless reports are not separate behavior systems. They are projections of semantic views over typed commands/results/documents.

A command such as `tools.validation.run` should produce a typed result and diagnostics. That result can be projected as:

- CLI table or JSON
- TUI panel / cell buffer
- rendered GUI dashboard
- OS-native list/detail view
- headless report/evidence artifact

This means the UI architecture needs:

- command contracts
- result schemas
- refusal/diagnostic codes
- view contracts
- action bindings
- projection descriptors
- accessibility contracts
- localization/text contracts
- conformance fixtures

This is why `PRESENTATION-CONTRACT-01` and `PROJECTION-CONFORMANCE-01` matter. They prevent GUI, TUI, CLI, native UI, and headless surfaces from drifting.

The TUI was treated as a serious first-class projection. It should support panels, tables, trees, forms, tabs, split panes, logs, timelines, maps, command input, keyboard navigation, Unicode box drawing with ASCII fallback, and limited color themes. It is useful for servers, SSH, CI, recovery, accessibility, and AIDE/Codex workflows.

The rendered GUI should be data-described and renderer-agnostic. The renderer should receive resolved draw commands; it should not know what a validation dashboard, pack browser, or Workbench module is.

---

## 6. Themes, widgets, layouts, and visual style

The user explored many visual directions through uploaded images and pasted design reports: dark technical dashboards, OS-native mimic styles, TUI instrument boards, paper/blueprint/terminal themes, Windows/Mac/Linux OEM+ profiles, and primitive-only renderer themes.

The final doctrine is:

> Layouts are data. Controls are registered capabilities. Themes are token overlays. Styles reference semantic tokens. Views project typed documents/results. Panels bind commands, not implementation functions. Modules declare capabilities and document types. Renderers draw; they do not own UI semantics. Apps compose projections; they do not own product logic.

Themes should affect geometry, density, palette, typography, line style, control metrics, procedural glyphs, and chrome. They must not change product semantics.

The chat also separated code-only themes from asset-rich themes. With only code and a software raster/vector renderer, Dominium can still support serious styles: barebones, instrument, kernel, terminal, blueprint, paper, cartographic, relay, ledger, tactical, phosphor, gridline, high contrast, data science, and TUI-rendered. Richer exact-looking OS mimicry, icons, textures, fonts, sounds, and photoreal panels require optional packs/assets or procedural asset systems.

---

## 7. AIDE and Codex workflow

Another central part of the chat was AIDE. AIDE is the control plane. Codex is the bounded patch executor. The user wants to run many automated tasks efficiently but without letting stale queues, dirty worktrees, partial work, and false claims corrupt the project.

The doctrine became:

```text
Development is non-blocking.
Promotion is evidence-blocked.
```

AIDE should manage:

- branch roles
- task lifecycle states
- WorkUnit schemas
- blocker taxonomy
- repair/resume policy
- dev/main/checkpoint policy
- checkpoint loop
- capability reality ledger
- warning dispositions
- evidence packets
- dirty worktree classification
- parallel task ownership

Generated prompts included:

- `STATUS-RECONCILE-02`
- `AIDE-WORKFLOW-LAW-01`
- `AIDE-WORKUNIT-SCHEMA-01`
- `AIDE-DEV-MAIN-POLICY-01`
- `AIDE-CHECKPOINT-LOOP-01`
- `AIDE-CAPABILITY-REALITY-LEDGER-01`

The branch model is:

```text
origin/main       promoted truth
origin/dev        integration branch
task/<task-id>    isolated work branch
repair/<task-id>  repair branch
checkpoint/<id>   proof/promotion branch
```

AIDE is also expected to prevent overclaiming. The Capability Reality Ledger should distinguish planned, specified, fixture-only, stubbed, implemented, tested, exposed, release-supported, and retired statuses.

---

## 8. Repo structure and maintenance posture

The chat repeatedly returned to repo structure. The ultimate root model became:

```text
apps/
engine/
game/
runtime/
contracts/
content/
docs/
tests/
tools/
scripts/
cmake/
external/
release/
archive/
```

The conclusion was not that every internal directory is perfect. The conclusion was that top-level structure and active-path cleanup became clean enough that broad structure refactors should stop. Remaining cleanup should be targeted.

The user later selected a maintenance sequence before continuing product work:

1. `FULL-GATE-LEGACY-TEST-ROUTE-01`
2. `PACK-INTERNAL-LAYOUT-CANON-01`
3. `RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01`
4. `PUBLIC-HEADER-ABI-PROMOTION-01`
5. `STORAGE-PACKAGE-PROVIDER-SPLIT-01`
6. `POINTER-WIDTH-SERIALIZATION-AUDIT-01`

`FULL-GATE-LEGACY-TEST-ROUTE-01` was generated immediately before this preservation request. Its purpose is to route or retire full-gate tests still expecting old roots, without weakening the canonical structure hard gate or recreating retired roots.

---

## 9. Provider strategy: raylib, SDL2, Lua, and future providers

The chat’s provider strategy became precise.

Use raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua aggressively for speed. But keep Dominium service contracts first-party.

Good structure:

```text
runtime/render/providers/raylib/
runtime/render/providers/rlgl/
runtime/render/providers/rlsw/
runtime/platform/providers/sdl2/
runtime/input/providers/sdl2/
runtime/audio/providers/raudio/
runtime/script/providers/lua54/ or lua55/
```

Bad structure:

```text
runtime/raylib/render/
apps/client/rendered/raylib/
contracts/raylib/
content/modules/
top-level profiles/
top-level labs/
```

Provider choices belong in release or content profiles, not app identities. Apps stay generic.

Raylib is a seed provider suite. SDL2 is a first-wave host/input/audio provider. Lua is a pinned script provider behind `dominium.script.v1`, not a raw mod ABI. rlsw is raylib’s software renderer provider; Dominium should still reserve a first-party `software` renderer as the canonical reference/fallback. rlgl is a raylib OpenGL-family abstraction provider; a future `opengl33` provider can be first-party.

The provider path should start with manifest/fence/conformance law before implementation:

- `PROVIDER-MANIFEST-WEDGE-01`
- `SERVICE-CONTRACT-WEDGE-01`
- `THIRD-PARTY-FENCE-01`
- `PROVIDER-STRUCTURE-CANON-01`
- `RAYLIB-PROVIDER-WEDGE-01`

---

## 10. Universe Explorer and product north-star

Near the end, a future product-spine direction emerged: a read-only Workbench/Client Universe Explorer. This would be a seamless 1:1-scale universe inspection and navigation surface proving continuous observer movement, reference-frame switching, no visible modal loading, streaming/sparse materialization, fidelity degradation, universe graph inspection, projection correctness, renderer purity, provenance, and refusal visibility.

The plan is not to jump into gameplay or a free camera. The Explorer should start as a contract, then a headless proof, then a minimal visual proof, then no-modal-loading and streaming hardening, then reference-frame and materialization proof, then interactive inspection, and only later embodiment.

The key line:

> The Explorer is not the world. The Explorer is the first lawful window into the world.

This matters because Dominium’s long-term ambition—large-scale realistic world/civilization simulation—requires representation ladders, sparse materialization, frame correctness, and evidence/refusal visibility before embodied gameplay.

---

## 11. Current task state and near-term path

The latest user-reported state before preservation said `PRESENTATION-CONTRACT-01` completed with `PASS_WITH_WARNINGS`, creating contract-only presentation law and read-only inspection descriptors. The user then chose to generate the six targeted maintenance prompts first, then replan the mainline sequence.

The active requested order is:

Maintenance lane:

```text
A. FULL-GATE-LEGACY-TEST-ROUTE-01
B. PACK-INTERNAL-LAYOUT-CANON-01
C. RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01
D. PUBLIC-HEADER-ABI-PROMOTION-01
E. STORAGE-PACKAGE-PROVIDER-SPLIT-01
F. POINTER-WIDTH-SERIALIZATION-AUDIT-01
```

Then mainline replanning:

```text
1. PROJECTION-CONFORMANCE-01
2. ACCESSIBILITY-CONTRACT-01
3. TEXT-LOCALIZATION-CONTRACT-01
4. WORKBENCH-SHELL-READONLY-01
5. UNIVERSE-EXPLORER-CONTRACT-01
6. UNIVERSE-EXPLORER-HEADLESS-01
7. PROVIDER-MANIFEST-WEDGE-01
8. SERVICE-CONTRACT-WEDGE-01
9. THIRD-PARTY-FENCE-01
10. RAYLIB-PROVIDER-WEDGE-01
11. UNIVERSE-EXPLORER-VISUAL-01
```

`FULL-GATE-LEGACY-TEST-ROUTE-01` has already been generated.

---

## 12. What remains unresolved

Key unresolved issues:

- Verify live repo state before running any prompt.
- Determine whether `FULL-GATE-LEGACY-TEST-ROUTE-01` has been run.
- Generate `PACK-INTERNAL-LAYOUT-CANON-01` next if live state supports it.
- Verify whether C17/C++17 baseline is fully reflected in build files.
- Decide when provider wedge work begins relative to Universe Explorer headless proof.
- Decide how fast to parallelize after the current maintenance prompts.
- Confirm exact location and naming conventions for profiles, provider manifests, and experiments.
- Avoid treating fixture-only or contract-only work as implemented runtime.

---

## 13. Risk summary

The main risks are:

1. A future assistant treats stale repo/task status as current.
2. Workbench is built as a separate GUI framework rather than a projection over commands/views.
3. Raylib/SDL/Lua leak into engine/game/contracts/content and become architecture.
4. TUI/CLI/rendered/native drift into separate semantic systems.
5. Full-gate tests are weakened instead of properly routed or retired.
6. Universe Explorer becomes gameplay/free-camera authority too early.
7. AIDE/Codex parallel work corrupts queue/status files or mixes unrelated changes.
8. Fixture-only surfaces are described as implemented.

Mitigation: verify repo state, keep evidence labels, use AIDE workflow, preserve non-goals, keep Workbench read-only first, provider-fence third-party code, and require conformance/projection tests.

---

## 14. Final recommendation

The correct next action is to verify live repo state and then proceed with the targeted maintenance sequence. Since `FULL-GATE-LEGACY-TEST-ROUTE-01` was already generated, the most natural next prompt request is:

```text
Generate PACK-INTERNAL-LAYOUT-CANON-01.
```

After the six maintenance prompts are generated and/or executed, replan the mainline sequence beginning with `PROJECTION-CONFORMANCE-01`.

The overall direction remains:

```text
Targeted maintenance
→ projection conformance
→ accessibility/localization contracts
→ read-only Workbench
→ Universe Explorer contract/headless proof
→ provider manifests/service contracts/fences
→ raylib provider wedge
→ visual Explorer
→ authoring Workbench
→ embodiment/gameplay/domain systems
```

The most important thing not to lose is that Workbench is the production interface, but the authority is still contracts, commands, services, documents, patches, providers, packs, modules, artifacts, diagnostics, evidence, tests, and replay/proof.
