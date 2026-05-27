# Aggregator Packet — Dominium Workbench, Presentation Spine, and Universe Explorer Planning

## Packet Metadata
* Chat label: Dominium Workbench, Presentation Spine, and Universe Explorer Planning
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: partial-to-broad visible transcript context
* Confidence: 4/5
* Staleness risk: medium-high for current repo facts
* Merge priority: high
* Main limitations: current repo state unverified; some items pasted from other chats; screenshots are reference not formal spec.

## Ultra-Condensed Carry-Forward Capsule
This chat is a major pivot point. It began with a Windows UI Editor / Tool Editor plan for Dominium launcher/setup/game UI authoring and evolved into a much larger architecture: Dominium Workbench Platform. The old UI Editor/Tool Editor should be abandoned as final products and recycled into Workbench modules. Workbench is a cross-platform rendered/TUI/CLI/headless production environment for building Domino/Dominium code, data, packs, modules, themes, UI/HUD, tests, releases, and AIDE/Codex work. It is not semantic authority; the center is contracts, commands, services, documents, patches, providers, packs, modules, apps, artifacts, diagnostics, evidence, and proof.

The core product-surface decision is that CLI, TUI, rendered GUI, OS-native GUI, and headless are projections of one command/result/refusal/document/view spine. Native GUI remains optional and can be built with OS SDK tools, but the core shared presentation system is command/view/projection-based. TUI is first-class. Rendered GUI uses software renderer first, then hardware backends later. UI is data-described: layouts, controls, widgets, themes, style tokens, view bindings, projection descriptors, and renderer draw lists.

The chat created or refined vocabulary: component/source unit, service/callable runtime capability, provider/replaceable implementation, pack/distributable authored payload, module/functional extension unit, workspace/user-facing Workbench composition, app/product composition, artifact/versioned persisted item. Workbench modules should be small and composable; big things like Project Graph Explorer, Interface Studio, Module/Pack Foundry, App Composer, Release Forge, and Universe Explorer are workspaces composed from smaller views, services, documents, patches, validators, graph views, inspectors, preview canvases, and evidence panels.

Progressive self-hosting is the safe build model: hand-coded seed substrate -> command/result/document/view contracts -> CLI/TUI/rendered proof -> minimal Workbench -> Workbench edits safe artifacts -> Workbench edits its own layouts/themes/modules -> Workbench builds product UIs, modules, packs, releases, and agent WorkUnits. The important near-term slice is COMMAND-RESULT-VIEW-SLICE-01, subject to current repo gate verification. It should prove one real command, typed result, view contract, projection descriptors, CLI output, TUI/text output, rendered-placeholder output, diagnostics, and evidence. It is the bridge to Workbench, client UI, setup, launcher, server admin, and future presentation systems.

The chat also introduced a future game/world direction: Universe Explorer and robot seed-civilization. Universe Explorer should be a lawful inspection/materialization/reference-frame proof, not a renderer demo. Robot seed-civilization systems can be authored through Workbench modules: Planet Generator Lab, Field Layer Stack Editor, Cut/Fill Terrain Delta Lab, Construction Blueprint Studio, Machine Graph Lab, Factory Graph Editor, Robot Body/Spawn Fabricator Lab, Mothership Planner, Sensor/Fog-of-War Lab, Logistics/Infrastructure Planner, City/Civilization Planner, Governance/Claims Lab, Performance Budget Lab, and External Renderer Bridge Lab.

## Top Carry-Forward Items
| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Workbench is projection, not authority | Decision | DECISION-02 | Prevents GUI drift | FACT | 5 |
| P0 | Unified command/result/refusal/document/view spine | Decision | DECISION-03 | Enables reuse across modes/products | FACT | 5 |
| P0 | Verify current repo state | Task | TASK-01 | Avoid stale next action | VERIFY | 5 |
| P0 | COMMAND-RESULT-VIEW-SLICE-01 | Task | TASK-02 | First presentation proof | INFERENCE | 4 |
| P1 | Progressive self-hosting | Decision | DECISION-09 | Safe bootstrapping | FACT | 5 |

## Workstream Summaries
See Workstream Register in file 04. Highest-value workstreams: Foundation, Presentation Spine, Workbench Platform, UI/Theme/Renderer, Modules/Packs/Providers, Progressive Self-Hosting, Universe Explorer.

## Compact Registers for Merge
Use the registers file as canonical compact table source. Merge DECISION-01 through DECISION-10 and WORKSTREAM-01 through WORKSTREAM-10. Treat current repo status as VERIFY, not fact.

## Possible Cross-Chat Duplicates
- Foundation Lock / Queue A/B/C discussions.
- Dominium Operating Environment doctrine.
- Workbench Platform planning.
- Universe Explorer planning.
- Robot seed-civilization / Unreal split discussions.

## Possible Cross-Chat Conflicts
- Current repo status and next task ordering may differ across chats.
- Directory structure may have changed.
- C89/C++98 earlier assumptions were superseded by later C17/C++17 pasted context.
- Old native UI Editor prompts conflict with Workbench direction if treated as active.

## Spec Book Integration Guidance
Feed into chapters: Workbench Platform, Presentation System, UI/Theme/Renderer, TUI, Engineering Governance, Module/Pack/App Model, AIDE/Codex Workflow, Universe Explorer, Robot Seed-Civilization. Formalize only accepted decisions; preserve old UI Editor plans as superseded background.

## Aggregator Warnings
Do not treat all assistant-generated prompts as accepted implementation plans. Do not treat repo-current status as independently verified. Do not merge old UI Editor/Tool Editor as current final products. Do not make Workbench the architecture center.
