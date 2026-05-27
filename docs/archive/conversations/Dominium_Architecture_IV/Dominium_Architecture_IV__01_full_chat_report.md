# Full Chat Report — Dominium Architecture IV

## 0. Report Metadata

| Field | Value |
|---|---|
| Chat label | Dominium Architecture IV |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only; no external web verification used. |
| Apparent coverage | Partial: visible transcript includes skipped earlier messages. |
| Extraction confidence | 4 / 5 |
| Staleness risk | Medium–High |
| Future plans present | Yes |
| Pending tasks present | Yes |
| Artifacts/files present | Textual plans and prompts only in the source chat; downloadable files are created by this report package. |
| Safe for aggregation | Yes, with caveats. |
| Main limitations | Actual repository state unverified; some transcript portions skipped; external tool/platform facts require verification. |

## 1. Executive Summary

This chat, labelled **Dominium Architecture IV**, is an architecture and implementation-planning session for the Dominium game project and its reusable Domino engine. Its highest-value contribution is the reorganisation of the project into a stable layered architecture and a phased Codex implementation plan. The user’s current preferred implementation sequence is: fully implement every ABI/API, then platform backends, then renderer backends, then setup, launcher, tools/SDKs, and finally the game. This supersedes earlier prompt sequences that started directly with platforms/renderers or earlier launcher/setup/game stubs.

The chat established a strong separation between **Domino**, the reusable engine/platform/render/sim/mod layer, and **Dominium**, the game/product/rules layer. Domino is expected to provide stable, versioned C-style ABIs/APIs such as `dsys`, `dgfx`, `daudio`, `dom_ui`, `dom_input`, `dom_core`, `dom_pkg`, `dom_inst`, `dom_sim`, `dom_canvas`, generic table/tree/view models, an event bus, and plugin/launcher extension interfaces. Dominium builds setup, launcher, tools, and game products on top of those APIs.

The platform and rendering architecture was heavily refined. Platform (`dsys`) is mandatory for all products, but renderer (`dgfx`) is optional for launcher/setup/tools unless a custom gfx canvas is needed. The game client requires gfx. UI modes are unified as `DOM_UI_NONE`, `DOM_UI_CLI`, `DOM_UI_TUI`, and `DOM_UI_GUI`, with backend flags such as `DOM_UI_BACKEND_NATIVE` and `DOM_UI_BACKEND_GFX`. This supports arbitrary presentation of common product logic through CLI, TUI, native GUI, or custom gfx GUI. Product contracts and capability matching are required so fallback and degradation are explicit and safe.

Renderer design uses a command-buffer IR consumed by many possible backends, including software reference rendering, DirectX, Vulkan, OpenGL, QuickDraw, Quartz, Metal, GDI, VESA, VGA, CGA, EGA, XGA, Hercules, MDA, and others. The soft reference renderer (`softref`) is planned as a canonical deterministic CPU implementation.

The chat also captured major game architecture decisions. Core simulation should use integers and fixed-point, not floating-point; item/material inventory counts remain whole integers. The current fixed-point palette is Q4.12, Q16.16, and Q48.16. Q4.12 is primarily a compact chunk-save/storage codec for bounded fields; runtime fields use wider types where needed. The world origin should be `0,0,0` at center and sea level. The surface is a sparse 3D grid over a 2^24 metre toroidal world with 16×16×16 chunks and a 4096-tile vertical page.

The user wants arbitrary construction, not prefab-only buildings. Vehicles, buildings, machines, static structures, moving vehicles, portable constructions, rooms, HVAC, pressure systems, and machines should all be unified as constructions/aggregates/graphs of parts made from materials. Prefabs and blueprints are templates/diffs/plans, not the primitive itself. Manual player actions and queued AI/robot/player work should share the same job pipeline.

Space and seamless transitions were also planned. Space uses Cartesian fixed-point positions plus arbitrary Keplerian on-rails orbits, optional drifts/precession, Lagrange sites, belts, rings, gas clouds, radiation belts, and graph-based routes. Full N-body dynamics are not the default. Seamless no-load transitions between surfaces, atmosphere, orbit, interiors, and arbitrary scenes are intended via reference frames, sim tiers, transition bands, streaming, and dual-representation handoff.

The chat generated extensive Codex prompt artifacts for Phases 1–6 and a roadmap for Phase 7 and beyond. Actual repository implementation remains unverified and must be checked before applying prompts.

## 2. How to Use This Report

- This report covers **only** the old chat labelled **Dominium Architecture IV**.
- Items labelled **FACT** were explicitly stated in the visible chat or are visible artifacts generated in that chat.
- Items labelled **INFERENCE** are reasonable conclusions from the visible chat but should not be treated as direct user statements.
- Items labelled **UNCERTAIN / UNVERIFIED** require confirmation before implementation or inclusion in a master spec as fact.
- Direct user statements outrank assistant suggestions.
- Tentative, superseded, and rejected options are intentionally preserved.
- External-world/software/tooling details are potentially stale as of 2026-05-27 Australia/Melbourne and must be verified before use.
- This report is intended for later aggregation into a Project Spec Book and for continuity in a new chat.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Area | Source basis | Strength | Implication | Confidence | Label |
|---|---|---|---|---|---|---|---|
| PREFERENCE-01 | Maximum-fidelity extraction and consolidation. | handoff | explicit | strong | Do not compress or omit important state. | high | FACT |
| PREFERENCE-02 | Label facts/inferences/uncertainty. | evidence | explicit | hard | Use FACT/INFERENCE/UNCERTAIN labels. | high | FACT |
| PREFERENCE-03 | No invention or silent inference. | evidence | explicit | hard | Mark assumptions and gaps. | high | FACT |
| PREFERENCE-05 | Generate Codex prompts one at a time with full context. | planning/coding | explicit | strong | Avoid broad prompt batches. | high | FACT |
| PREFERENCE-06 | Strong modularity/extensibility planning. | architecture | explicit | very strong | Plan for plugins/schemas/backends/future systems. | high | FACT |
| PREFERENCE-07 | Native OS installer/UI conventions where appropriate. | UX/platform | explicit | strong | Use MSI/pkg/deb/native widgets where possible. | high | FACT |
| PREFERENCE-08 | Renderer optional for non-game products. | architecture | explicit | strong | Launcher/setup/tools must not unnecessarily depend on gfx. | high | FACT |
| PREFERENCE-09 | Common code with arbitrary presentation. | architecture/UI | explicit | strong | Use views/actions/models/canvases. | high | FACT |
| PREFERENCE-10 | Deterministic fixed-point sim with correct calculations. | numeric/sim | explicit | strong | Check ranges and units carefully. | high | FACT |
| PREFERENCE-11 | Arbitrary construction over prefab-only design. | gameplay | explicit | strong | Use construction graph/parts; prefabs as templates. | high | FACT |
| PREFERENCE-12 | Seamless surface/space/scene transitions. | gameplay | explicit | strong | Use reference frames and tier handoff. | high | FACT |
| PREFERENCE-13 | Comprehensive dev/mod/SDK/editor tooling. | tools | explicit | strong | Include game/launcher/mod/pack/world/save editors. | high | FACT |

### 3.2 Inferred Preferences

| ID | Preference | Area | Source basis | Strength | Implication | Confidence | Label |
|---|---|---|---|---|---|---|---|
| PREFERENCE-04 | Structured, audit-ready reports/tables. | formatting | explicit/inferred | strong | Use stable IDs, registers, tables. | high | FACT |
| PREFERENCE-14 | Direct technical planning over high-level generalities. | reasoning style | inferred | moderate/strong | Provide concrete APIs, prompts, paths. | medium-high | INFERENCE |
| PREFERENCE-15 | Prefer long-term compatibility and stable ABIs. | architecture | inferred | strong | Design versioning and schemas before ecosystem grows. | medium-high | INFERENCE |

### 3.3 Preferences Not Established by This Chat

- No final preferred scripting language or VM is established. Label: UNCERTAIN / UNVERIFIED.
- No final manifest/schema file format is established. Label: UNCERTAIN / UNVERIFIED.
- No final default UPS value is established. Label: UNCERTAIN / UNVERIFIED.
- No final accepted list of “minimum features” for every retro platform/renderer is established. Label: UNCERTAIN / UNVERIFIED.

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Domino engine | Reusable engine/core/platform/render/sim/mod foundation. | Architecture specified; Phase 1 ABI/API prompts generated; actual implementation unverified. | Stable reusable engine layer for Dominium and future projects. | active/planned | P0 | high | FACT |
| WORKSTREAM-02 | Dominium product/game layer | Game-specific rules/products built on Domino. | Planned with headers/stubs prompts; implementation unverified. | Setup, launcher, tools, and game products implemented over Domino. | active/planned | P0 | high | FACT |
| WORKSTREAM-03 | Repository structure | Maintain consistent repo layout for engine, products, data, tools, docs, tests. | Planned/adopted in chat; actual repo unknown. | Buildable repo with planned `include/`, `source/`, `docs/`, `data/`, `tools/`, `scripts/`, `cmake/`, `tests/` layout. | active | P0 | high | FACT |
| WORKSTREAM-04 | ABI/API spine | Implement stable public ABIs/APIs first. | Phase 1 prompts generated. | Common service spine for setup, launcher, tools, game, mods, and SDKs. | active Phase 1 | P0 | high | FACT |
| WORKSTREAM-05 | Platform API and backends | Implement `dsys` and backends for target OS/platforms. | Backend prompt template and platform parameter list generated. | Capability-described platform backends including Win32, Win16, DOS, CP/M, Carbon, Cocoa, X11, Wayland, POSIX, SDL1, SDL2, null. | planned Phase 2 | P0 | high | FACT |
| WORKSTREAM-06 | Renderer API and backends | Implement `dgfx` IR and renderer backends. | Renderer template, vtable prompt, and softref prompt generated. | Renderer matrix with software, modern GPU, Apple, Windows, and retro backends, each advertising capabilities. | planned Phase 3 | P0 | high | FACT |
| WORKSTREAM-07 | Audio API and backends | Provide sound abstraction with null and real backends. | Stub ABI planned; detailed real backend prompts not generated. | Game and tools can use audio via `daudio`, with null fallback. | planned | P1 | medium | FACT |
| WORKSTREAM-08 | Unified UI system | Present products in NONE/CLI/TUI/GUI with native and/or gfx backends. | Designed; stub prompt generated. | Common UI layer for setup, launcher, tools, and optional game menus. | planned | P0 | high | FACT |
| WORKSTREAM-09 | Product contracts and runtime selection | Describe products once and bind available sys/gfx/audio/ui drivers through capability matching. | Designed; not yet implemented. | Predictable backend selection and controlled fallback/failure. | planned | P0 | high | FACT |
| WORKSTREAM-10 | Packages, instances, mods, packs | Manage installed versions, packages, mods, packs, and configured instances. | ABI and persistence prompt generated; manifest/schema unresolved. | Single package/instance system used by setup, launcher, tools, and game. | planned | P0 | high | FACT |
| WORKSTREAM-11 | Setup product | Install, repair, uninstall, and verify Dominium across platforms. | Phase 4 prompts generated. | Setup core plus Windows MSI/EXE, macOS pkg/dmg/app, Linux deb/rpm/run, and retro installers. | planned Phase 4 | P1 | high | FACT |
| WORKSTREAM-12 | Launcher product | Common launcher core and shells for instance/package/mod/tool management. | Phase 5 prompts generated. | CLI/TUI/GUI launcher with extension hooks and optional gfx canvases. | planned Phase 5 | P1 | high | FACT |
| WORKSTREAM-13 | Tools and SDKs | Provide development tools, editors, and SDK surfaces for game/mod/pack/launcher creation. | Phase 6 prompts generated. | `dominium-tools`, asset compiler, packer, replay/test tools, world/save/game/launcher editors, GUI editor host, SDK exports. | planned Phase 6 | P1 | high | FACT |
| WORKSTREAM-14 | Game product | Build playable Dominium client and later deep simulation. | Phase 7+ roadmap generated; detailed prompt batch pending. | Deterministic playable core with construction, machines, networks, save/replay, later environment/space/AI/economy. | planned Phase 7+ | P0/P1 | high | FACT |
| WORKSTREAM-15 | Numeric, units, time, determinism | Define fixed-point/integer units and UPS/FPS separation. | Architecture specified; implementation pending. | Central numeric policy and deterministic fixed-step sim. | foundational | P0 | high | FACT |
| WORKSTREAM-16 | World/environment fields | Use generic fields for terrain, atmosphere, hydrology, climate, pollution, radiation, geology. | Planned; old concrete terrain/hydro prompts superseded by generic primitives. | Modular field/substance/reservoir/network domain systems. | planned later | P1 | high | FACT |
| WORKSTREAM-17 | Construction, vehicles, machines | Unify buildings, vehicles, machines, portable/static/moving structures as constructions made of parts/materials. | Concept specified; implementation later. | Arbitrary construction/destruction/blueprints across static and moving assemblies. | planned | P0/P1 | high | FACT |
| WORKSTREAM-18 | Space, orbits, seamless transitions | Support Keplerian on-rails space and seamless surface/space/interior transitions. | Architecture specified; implementation later. | Reference-frame/tiered transitions, space graph/sites, vehicles/stations/satellites and orbital gameplay. | planned | P1 | high | FACT |
| WORKSTREAM-19 | Actors, AI, jobs, knowledge | Support player/AI actors, jobs, life support, comms, fog-of-war, knowledge transmission. | Conceptual; some earlier prompts; implementation later. | Actors/brains/jobs/knowledge integrated with construction/world/economy. | planned | P1/P2 | high | FACT |
| WORKSTREAM-20 | Economy, markets, politics | Model markets, trade, companies/factions, law/policy, politics. | Planned later. | Deterministic goods/market/faction systems integrated with logistics/jobs. | planned later | P2 | medium-high | FACT |
| WORKSTREAM-21 | Plugin, schema, scripting, event infrastructure | Long-term extensibility through plugin ABIs, schemas, event bus, optional deterministic scripting. | Plugin/event ABI planned; schema/scripting choices unresolved. | Third-party content/logic/launcher extensions via stable APIs and versioned schemas. | planned | P1 | high | FACT |
| WORKSTREAM-22 | Save, replay, determinism harness | Persist/replay/test deterministic simulations. | Planned; replay/test tools prompt generated. | Save/load, replay recording/inspection, tick hashes and deterministic tests. | planned | P1 | high | FACT |
| WORKSTREAM-23 | Multiplayer/distributed sim | Future lockstep/authoritative multiplayer and servers. | Phase 10 roadmap only. | Headless server, command streams, desync detection, launcher server browser. | future | P2 | medium | FACT |
| WORKSTREAM-24 | Ports, retro editions, hardening | Modern/retro builds, profiling, save compatibility, documentation. | Future Phase 12 plan. | Stable ports with documented caps and long-term maintenance. | future | P2 | medium-high | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — Domino engine
- Label: FACT
- Objective: Reusable engine/core/platform/render/sim/mod foundation.
- Background: Captured from visible chat architecture and prompt planning for Domino engine.
- Current state: Architecture specified; Phase 1 ABI/API prompts generated; actual implementation unverified.
- Desired end state: Stable reusable engine layer for Dominium and future projects.
- Importance: Priority P0; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: active/planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Stable reusable engine layer for Dominium and future projects.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-02 — Dominium product/game layer
- Label: FACT
- Objective: Game-specific rules/products built on Domino.
- Background: Captured from visible chat architecture and prompt planning for Dominium product/game layer.
- Current state: Planned with headers/stubs prompts; implementation unverified.
- Desired end state: Setup, launcher, tools, and game products implemented over Domino.
- Importance: Priority P0; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: active/planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Setup, launcher, tools, and game products implemented over Domino.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-03 — Repository structure
- Label: FACT
- Objective: Maintain consistent repo layout for engine, products, data, tools, docs, tests.
- Background: Captured from visible chat architecture and prompt planning for Repository structure.
- Current state: Planned/adopted in chat; actual repo unknown.
- Desired end state: Buildable repo with planned `include/`, `source/`, `docs/`, `data/`, `tools/`, `scripts/`, `cmake/`, `tests/` layout.
- Importance: Priority P0; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: active; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Buildable repo with planned `include/`, `source/`, `docs/`, `data/`, `tools/`, `scripts/`, `cmake/`, `tests/` layout.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-04 — ABI/API spine
- Label: FACT
- Objective: Implement stable public ABIs/APIs first.
- Background: Captured from visible chat architecture and prompt planning for ABI/API spine.
- Current state: Phase 1 prompts generated.
- Desired end state: Common service spine for setup, launcher, tools, game, mods, and SDKs.
- Importance: Priority P0; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: active Phase 1; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Common service spine for setup, launcher, tools, game, mods, and SDKs.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-05 — Platform API and backends
- Label: FACT
- Objective: Implement `dsys` and backends for target OS/platforms.
- Background: Captured from visible chat architecture and prompt planning for Platform API and backends.
- Current state: Backend prompt template and platform parameter list generated.
- Desired end state: Capability-described platform backends including Win32, Win16, DOS, CP/M, Carbon, Cocoa, X11, Wayland, POSIX, SDL1, SDL2, null.
- Importance: Priority P0; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned Phase 2; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Capability-described platform backends including Win32, Win16, DOS, CP/M, Carbon, Cocoa, X11, Wayland, POSIX, SDL1, SDL2, null.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-06 — Renderer API and backends
- Label: FACT
- Objective: Implement `dgfx` IR and renderer backends.
- Background: Captured from visible chat architecture and prompt planning for Renderer API and backends.
- Current state: Renderer template, vtable prompt, and softref prompt generated.
- Desired end state: Renderer matrix with software, modern GPU, Apple, Windows, and retro backends, each advertising capabilities.
- Importance: Priority P0; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned Phase 3; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Renderer matrix with software, modern GPU, Apple, Windows, and retro backends, each advertising capabilities.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-07 — Audio API and backends
- Label: FACT
- Objective: Provide sound abstraction with null and real backends.
- Background: Captured from visible chat architecture and prompt planning for Audio API and backends.
- Current state: Stub ABI planned; detailed real backend prompts not generated.
- Desired end state: Game and tools can use audio via `daudio`, with null fallback.
- Importance: Priority P1; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Game and tools can use audio via `daudio`, with null fallback.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: medium
- Carry-forward priority: P1

### WORKSTREAM-08 — Unified UI system
- Label: FACT
- Objective: Present products in NONE/CLI/TUI/GUI with native and/or gfx backends.
- Background: Captured from visible chat architecture and prompt planning for Unified UI system.
- Current state: Designed; stub prompt generated.
- Desired end state: Common UI layer for setup, launcher, tools, and optional game menus.
- Importance: Priority P0; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Common UI layer for setup, launcher, tools, and optional game menus.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-09 — Product contracts and runtime selection
- Label: FACT
- Objective: Describe products once and bind available sys/gfx/audio/ui drivers through capability matching.
- Background: Captured from visible chat architecture and prompt planning for Product contracts and runtime selection.
- Current state: Designed; not yet implemented.
- Desired end state: Predictable backend selection and controlled fallback/failure.
- Importance: Priority P0; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Predictable backend selection and controlled fallback/failure.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-10 — Packages, instances, mods, packs
- Label: FACT
- Objective: Manage installed versions, packages, mods, packs, and configured instances.
- Background: Captured from visible chat architecture and prompt planning for Packages, instances, mods, packs.
- Current state: ABI and persistence prompt generated; manifest/schema unresolved.
- Desired end state: Single package/instance system used by setup, launcher, tools, and game.
- Importance: Priority P0; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Single package/instance system used by setup, launcher, tools, and game.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-11 — Setup product
- Label: FACT
- Objective: Install, repair, uninstall, and verify Dominium across platforms.
- Background: Captured from visible chat architecture and prompt planning for Setup product.
- Current state: Phase 4 prompts generated.
- Desired end state: Setup core plus Windows MSI/EXE, macOS pkg/dmg/app, Linux deb/rpm/run, and retro installers.
- Importance: Priority P1; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned Phase 4; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Setup core plus Windows MSI/EXE, macOS pkg/dmg/app, Linux deb/rpm/run, and retro installers.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P1

### WORKSTREAM-12 — Launcher product
- Label: FACT
- Objective: Common launcher core and shells for instance/package/mod/tool management.
- Background: Captured from visible chat architecture and prompt planning for Launcher product.
- Current state: Phase 5 prompts generated.
- Desired end state: CLI/TUI/GUI launcher with extension hooks and optional gfx canvases.
- Importance: Priority P1; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned Phase 5; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: CLI/TUI/GUI launcher with extension hooks and optional gfx canvases.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P1

### WORKSTREAM-13 — Tools and SDKs
- Label: FACT
- Objective: Provide development tools, editors, and SDK surfaces for game/mod/pack/launcher creation.
- Background: Captured from visible chat architecture and prompt planning for Tools and SDKs.
- Current state: Phase 6 prompts generated.
- Desired end state: `dominium-tools`, asset compiler, packer, replay/test tools, world/save/game/launcher editors, GUI editor host, SDK exports.
- Importance: Priority P1; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned Phase 6; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: `dominium-tools`, asset compiler, packer, replay/test tools, world/save/game/launcher editors, GUI editor host, SDK exports.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P1

### WORKSTREAM-14 — Game product
- Label: FACT
- Objective: Build playable Dominium client and later deep simulation.
- Background: Captured from visible chat architecture and prompt planning for Game product.
- Current state: Phase 7+ roadmap generated; detailed prompt batch pending.
- Desired end state: Deterministic playable core with construction, machines, networks, save/replay, later environment/space/AI/economy.
- Importance: Priority P0/P1; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned Phase 7+; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Deterministic playable core with construction, machines, networks, save/replay, later environment/space/AI/economy.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0/P1

### WORKSTREAM-15 — Numeric, units, time, determinism
- Label: FACT
- Objective: Define fixed-point/integer units and UPS/FPS separation.
- Background: Captured from visible chat architecture and prompt planning for Numeric, units, time, determinism.
- Current state: Architecture specified; implementation pending.
- Desired end state: Central numeric policy and deterministic fixed-step sim.
- Importance: Priority P0; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: foundational; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Central numeric policy and deterministic fixed-step sim.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0

### WORKSTREAM-16 — World/environment fields
- Label: FACT
- Objective: Use generic fields for terrain, atmosphere, hydrology, climate, pollution, radiation, geology.
- Background: Captured from visible chat architecture and prompt planning for World/environment fields.
- Current state: Planned; old concrete terrain/hydro prompts superseded by generic primitives.
- Desired end state: Modular field/substance/reservoir/network domain systems.
- Importance: Priority P1; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned later; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Modular field/substance/reservoir/network domain systems.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P1

### WORKSTREAM-17 — Construction, vehicles, machines
- Label: FACT
- Objective: Unify buildings, vehicles, machines, portable/static/moving structures as constructions made of parts/materials.
- Background: Captured from visible chat architecture and prompt planning for Construction, vehicles, machines.
- Current state: Concept specified; implementation later.
- Desired end state: Arbitrary construction/destruction/blueprints across static and moving assemblies.
- Importance: Priority P0/P1; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Arbitrary construction/destruction/blueprints across static and moving assemblies.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P0/P1

### WORKSTREAM-18 — Space, orbits, seamless transitions
- Label: FACT
- Objective: Support Keplerian on-rails space and seamless surface/space/interior transitions.
- Background: Captured from visible chat architecture and prompt planning for Space, orbits, seamless transitions.
- Current state: Architecture specified; implementation later.
- Desired end state: Reference-frame/tiered transitions, space graph/sites, vehicles/stations/satellites and orbital gameplay.
- Importance: Priority P1; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Reference-frame/tiered transitions, space graph/sites, vehicles/stations/satellites and orbital gameplay.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P1

### WORKSTREAM-19 — Actors, AI, jobs, knowledge
- Label: FACT
- Objective: Support player/AI actors, jobs, life support, comms, fog-of-war, knowledge transmission.
- Background: Captured from visible chat architecture and prompt planning for Actors, AI, jobs, knowledge.
- Current state: Conceptual; some earlier prompts; implementation later.
- Desired end state: Actors/brains/jobs/knowledge integrated with construction/world/economy.
- Importance: Priority P1/P2; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Actors/brains/jobs/knowledge integrated with construction/world/economy.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P1/P2

### WORKSTREAM-20 — Economy, markets, politics
- Label: FACT
- Objective: Model markets, trade, companies/factions, law/policy, politics.
- Background: Captured from visible chat architecture and prompt planning for Economy, markets, politics.
- Current state: Planned later.
- Desired end state: Deterministic goods/market/faction systems integrated with logistics/jobs.
- Importance: Priority P2; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned later; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Deterministic goods/market/faction systems integrated with logistics/jobs.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: medium-high
- Carry-forward priority: P2

### WORKSTREAM-21 — Plugin, schema, scripting, event infrastructure
- Label: FACT
- Objective: Long-term extensibility through plugin ABIs, schemas, event bus, optional deterministic scripting.
- Background: Captured from visible chat architecture and prompt planning for Plugin, schema, scripting, event infrastructure.
- Current state: Plugin/event ABI planned; schema/scripting choices unresolved.
- Desired end state: Third-party content/logic/launcher extensions via stable APIs and versioned schemas.
- Importance: Priority P1; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Third-party content/logic/launcher extensions via stable APIs and versioned schemas.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P1

### WORKSTREAM-22 — Save, replay, determinism harness
- Label: FACT
- Objective: Persist/replay/test deterministic simulations.
- Background: Captured from visible chat architecture and prompt planning for Save, replay, determinism harness.
- Current state: Planned; replay/test tools prompt generated.
- Desired end state: Save/load, replay recording/inspection, tick hashes and deterministic tests.
- Importance: Priority P1; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: planned; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Save/load, replay recording/inspection, tick hashes and deterministic tests.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: high
- Carry-forward priority: P1

### WORKSTREAM-23 — Multiplayer/distributed sim
- Label: FACT
- Objective: Future lockstep/authoritative multiplayer and servers.
- Background: Captured from visible chat architecture and prompt planning for Multiplayer/distributed sim.
- Current state: Phase 10 roadmap only.
- Desired end state: Headless server, command streams, desync detection, launcher server browser.
- Importance: Priority P2; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: future; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Headless server, command streams, desync detection, launcher server browser.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: medium
- Carry-forward priority: P2

### WORKSTREAM-24 — Ports, retro editions, hardening
- Label: FACT
- Objective: Modern/retro builds, profiling, save compatibility, documentation.
- Background: Captured from visible chat architecture and prompt planning for Ports, retro editions, hardening.
- Current state: Future Phase 12 plan.
- Desired end state: Stable ports with documented caps and long-term maintenance.
- Importance: Priority P2; this workstream is needed for the planned Dominium/DoMino implementation unless explicitly future/deferred.
- Decisions made: See Decision Register for related decisions.
- Decisions pending: See Open Questions Register where applicable.
- Pending tasks: See Task Register for implementation prompts and verification tasks.
- Constraints: See Constraint Register; most relevant constraints include Domino/Dominium separation, deterministic sim, versioned ABIs, and capability-based degradation where applicable.
- Dependencies: Depends on earlier foundational phases unless this is itself foundational.
- Timeline / sequencing: future; use main phase order unless user changes it.
- Blockers: Actual repository state and unresolved schema/toolchain decisions where applicable.
- Risks: See Risk Register.
- Artifacts: See Artifact Ledger; prompts/plans exist for many workstreams.
- Success criteria: Stable ports with documented caps and long-term maintenance.
- Recommended next action: Continue from the current roadmap; verify repo state before applying prompts.
- Verification needed: Actual implementation state is unverified for all workstreams.
- Confidence: medium-high
- Carry-forward priority: P2


## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Current relevance | Confidence | Label |
|---|---|---|---|---|---|
| TIMELINE-01 | Initial plan: platforms/renderers, launcher, setup, game. | Superseded by later phase order. | historical | high | FACT |
| TIMELINE-02 | Repo structure and Domino/Dominium split established. | Current foundation. | active | high | FACT |
| TIMELINE-03 | Package/mod/pack/instance system developed conceptually. | Current foundation. | active | high | FACT |
| TIMELINE-04 | Multiple earlier Codex prompts for runtime/launcher/setup/game/ECS/world were generated. | Useful but partly superseded. | historical/reference | high | FACT |
| TIMELINE-05 | User paused and asked for deeper modularity before implementing Phase 2.5+. | Major pivot. | active context | high | FACT |
| TIMELINE-06 | Generic primitives fields/substances/reservoirs/networks replaced ad hoc terrain/hydro model. | Current system design. | active | high | FACT |
| TIMELINE-07 | Numeric/unit policy refined and corrected. | Current requirement. | active | high | FACT |
| TIMELINE-08 | Space/orbit model refined from logical-only to Keplerian on-rails plus graph/sites. | Current requirement. | active | high | FACT |
| TIMELINE-09 | Construction model refined to arbitrary construction graphs. | Current requirement. | active | high | FACT |
| TIMELINE-10 | Platform/render/UI/common product architecture defined. | Current foundation. | active | high | FACT |
| TIMELINE-11 | Layer/interface list L0–L12 produced. | Current architecture artifact. | active | high | FACT |
| TIMELINE-12 | Implementation order reset to ABIs/APIs, platforms, renderers, setup, launcher, tools, game. | Current roadmap. | active | high | FACT |
| TIMELINE-13 | Phase 1 prompts generated. | Current action artifacts. | active | high | FACT |
| TIMELINE-14 | Platform backend prompt template generated. | Current action artifact. | active | high | FACT |
| TIMELINE-15 | Renderer backend prompt template and softref/vtable prompts generated. | Current action artifact. | active | high | FACT |
| TIMELINE-16 | Setup Phase 4 prompts generated. | Current action artifact. | active | high | FACT |
| TIMELINE-17 | Launcher Phase 5 prompts generated. | Current action artifact. | active | high | FACT |
| TIMELINE-18 | Tools Phase 6 prompts generated. | Current action artifact. | active | high | FACT |
| TIMELINE-19 | Phase 7+ game roadmap generated. | Current future plan. | active | high | FACT |
| TIMELINE-20 | Context transfer/extraction requested and produced. | Current handoff context. | active | high | FACT |

## 7. Decisions

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Name reusable engine/core layer Domino. | final | User said engine/core/platforms will be called Domino engine. | Reuse across Dominium and other projects. | Use `include/domino`, `source/domino`, Domino-prefixed APIs. | WORKSTREAM-01 | high | FACT |
| DECISION-02 | Separate Dominium game/product layer from Domino engine. | final | Repeated repo/layer discussions. | Avoid game-specific lock-in in engine. | Use `include/dominium`, `source/dominium`, product/rules split. | WORKSTREAM-02 | high | FACT |
| DECISION-03 | Current main sequence: ABIs/APIs first, then platforms, renderers, setup, launcher, tools, game. | final/current | User explicitly proposed this order. | Stable interfaces should precede implementations/products. | Use this roadmap unless changed. | WORKSTREAM-04 | high | FACT |
| DECISION-04 | Use versioned C ABI structs with `struct_size` and `struct_version`. | final | ABI conventions in chat. | Future compatibility for tools/plugins/products. | All public boundary structs follow the pattern. | WORKSTREAM-04 | high | FACT |
| DECISION-05 | Platform is mandatory; renderer optional for launcher/setup/tools unless gfx canvas/custom UI needed. | final | User explicitly requested this. | Native/CLI/TUI operation without renderer dependency. | Product contracts distinguish required/optional gfx. | WORKSTREAM-08 | high | FACT |
| DECISION-06 | Game client requires gfx renderer. | final/tentative | Assistant stated and user continued; not directly contradicted. | A game client is graphical; CLI fallback would not be the same product. | Game hard-fails if no suitable renderer. | WORKSTREAM-14 | medium | INFERENCE |
| DECISION-07 | Unify GUI as `DOM_UI_GUI` with backend flags for native/gfx. | final | User asked to unify GUI modes; design accepted. | Avoid separate native/custom mode explosion. | UI mode and implementation backend are distinct. | WORKSTREAM-08 | high | FACT |
| DECISION-08 | Use product contracts and capability matching for runtime backend selection. | final | Discussion of arbitrary platform/renderer combos. | Controlled fallback and failure. | Implement `dom_product_contract`, `dom_select_runtime`. | WORKSTREAM-09 | high | FACT |
| DECISION-09 | Graceful degradation must be explicit per product. | final | Discussion of fallback danger. | Avoid half-broken functionality. | Required/optional features and fallback modes in contracts. | WORKSTREAM-09 | high | FACT |
| DECISION-10 | Expose product logic through commands, queries, tables, trees, views, canvases. | final | Common launcher/API discussions. | Same code can present in CLI/TUI/native/gfx. | Implement model/view APIs and canvas builders. | WORKSTREAM-04 | high | FACT |
| DECISION-11 | Use renderer command-buffer IR consumed by backends. | final | Rendering architecture discussion. | Backend independence, replay/logging/remote rendering. | Implement `dgfx_cmd_buffer` and opcodes. | WORKSTREAM-06 | high | FACT |
| DECISION-12 | Use Q4.12, Q16.16, Q48.16 plus integer aliases as core numeric palette. | final | Numeric discussions and correction. | Avoid redundant formats and misuse. | Implement `dnumeric.h` with semantic aliases. | WORKSTREAM-15 | high | FACT |
| DECISION-13 | Inventory/item/material storage counts are whole integers only. | final | User explicitly stated core gameplay systems and item storage should be whole integers. | Economy/BOM clarity. | No fractional item stacks/costs. | WORKSTREAM-15 | high | FACT |
| DECISION-14 | Treat Q4.12 as chunk-save/storage codec for bounded fields, not primary runtime. | final | q4.12 discussion. | Avoid runtime range/precision limits. | Decode into runtime Q16.16/Q48.16. | WORKSTREAM-15 | high | FACT |
| DECISION-15 | Use signed world coordinates with `0,0,0` at world center and sea level. | final | User explicitly requested center/sea origin. | Semantic coordinates and signed deltas. | `TileCoord`, `TileHeight`, toroidal wrapping. | WORKSTREAM-16 | high | FACT |
| DECISION-16 | Use Cartesian space positions; polar/spherical only derived for UI/indexing. | final | Space coordinate discussion. | Avoid trig/wrap/singularity/nonlinear resolution problems. | `SpacePos` uses Q48.16 x/y/z. | WORKSTREAM-18 | high | FACT |
| DECISION-17 | Support arbitrary Keplerian on-rails orbits with optional drifts/precession. | final | User requested arbitrary Keplerian orbits. | Realistic-feeling, cheap deterministic space. | `OrbitComponent` and orbit engine. | WORKSTREAM-18 | high | FACT |
| DECISION-18 | Do not implement full N-body dynamics as default core mechanic. | final | Visible rationale in space discussion. | Too complex/expensive; not needed for goals. | Use tags/scripted effects/approximations for resonances/black holes etc. | WORKSTREAM-18 | medium-high | FACT |
| DECISION-19 | Unify vehicles, buildings, machines, portable/static/moving constructions as construction graphs. | final | User asked abstraction; assistant design accepted in flow. | Avoid parallel incompatible systems. | Parts/materials/graphs/frames/mobility components. | WORKSTREAM-17 | high | FACT |
| DECISION-20 | Prefabs/blueprints are templates, not primitive building system. | final | User clarified they do not mean prefab structures as primary. | Arbitrary construction is primary. | Blueprints compose actual construction primitives. | WORKSTREAM-17 | high | FACT |
| DECISION-21 | Blueprints/planners are diffs/operations compiled to jobs. | final | Blueprint discussion. | Planning without immediate sim mutation; supports saving drafts. | Blueprint ops and job graph. | WORKSTREAM-17 | high | FACT |
| DECISION-22 | Player immediate work and queued work share job pipeline. | final | User explicitly wanted both simultaneous/manual and queued execution. | Deterministic common path for players, robots, humans. | Direct action is a pre-assigned job. | WORKSTREAM-19 | high | FACT |
| DECISION-23 | Use OS-native setup packaging where possible. | final | User explicitly wanted MSI/EXE, Linux/macOS expected style. | User trust/expected OS integration. | Setup core plus thin native wrappers. | WORKSTREAM-11 | high | FACT |
| DECISION-24 | Launcher is described by views/actions/models, not hardcoded per shell. | final | Common launcher discussion. | CLI/TUI/GUI share logic. | `dom_launch` core and `dom_view` models. | WORKSTREAM-12 | high | FACT |
| DECISION-25 | Launcher and game extensions use package/plugin systems. | final/planned | Launcher extension prompts. | Third-party customization. | `DOM_PKG_LAUNCHER_UI`, `launcher_ext_vtable`, `dom_mod_vtable`. | WORKSTREAM-21 | high | FACT |
| DECISION-26 | Tools and SDKs are first-class products. | final | User explicitly requested dev tools/editors/SDKs. | Modding/dev ecosystem. | `dominium-tools`, editors, SDK export. | WORKSTREAM-13 | high | FACT |
| DECISION-27 | Generate Codex prompts one subsystem/backend/product at a time. | final workflow | User requested one-at-a-time full context; assistant reinforced. | Avoid tangled outputs. | Sequential prompts with bounded scope. | WORKSTREAM-04 | high | FACT |
| DECISION-28 | Use reference frames and sim tiers for seamless transitions. | final concept | Seamless transitions discussion. | No-load surface/space/interior transitions. | Frame/tier manager and dual-representation handoff. | WORKSTREAM-18 | high | FACT |
| DECISION-29 | Defer deep environment/space/economy systems until after playable core. | planned/final sequencing | Phase 7+ roadmap. | Avoid scope explosion. | Phase 7 first; Phase 8/9 later. | WORKSTREAM-14 | medium-high | FACT |
| DECISION-30 | Preserve superseded options and uncertainty in handoff/extraction. | final for handoff | User’s explicit extraction rules. | Prevents false continuity. | All report items labelled/statused. | WORKSTREAM-24 | high | FACT |

### Highest-impact decisions

- **DECISION-03:** The current authoritative implementation sequence is ABIs/APIs first, then platforms, renderers, setup, launcher, tools, and game.
- **DECISION-05 / DECISION-07 / DECISION-08:** Platform, UI, renderer, and product contracts are separated so products can run under arbitrary backend combinations.
- **DECISION-12 through DECISION-15:** Numeric and world coordinate policy anchors deterministic simulation and future save/replay/multiplayer.
- **DECISION-19 through DECISION-22:** Arbitrary construction and jobs unify buildings, vehicles, machines, and player/AI execution.
- **DECISION-28:** Seamless surface/space/interior transitions require reference frames and sim tiers.

## 8. Pending Tasks and Next Actions

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Verify actual repository state before applying prompts. | P0 | U0/U1 | User/future assistant | Repository access | File tree, build output | Accurate implementation context | Inspect repo and build config. | WORKSTREAM-03 | FACT |
| TASK-02 | Apply Phase 1.1.1 Domino ABI prompt. | P0 | U1 | User/Codex | Repo verified | Prompt 1.1.1 | Engine headers and stubs | Run after repo inspection. | WORKSTREAM-04 | FACT |
| TASK-03 | Apply Phase 1.1.2 Dominium ABI prompt. | P0 | U1 | User/Codex | Phase 1.1.1 | Prompt 1.1.2 | Dominium headers/stubs | Run after Domino ABI prompt. | WORKSTREAM-02 | FACT |
| TASK-04 | Implement `dsys` stub. | P0 | U1 | User/Codex | sys header | Prompt 1.2.1 | Platform stub backend | Run prompt. | WORKSTREAM-05 | FACT |
| TASK-05 | Implement gfx/audio/ui/input stubs. | P0 | U1 | User/Codex | headers | Prompt 1.2.2 | Null render/audio, UI/input stubs | Run prompt. | WORKSTREAM-06 | FACT |
| TASK-06 | Implement core/pkg/inst/sim/canvas/model/event/plugin stubs. | P0 | U1 | User/Codex | Core headers | Prompt 1.2.3 | In-memory service spine | Run prompt. | WORKSTREAM-04 | FACT |
| TASK-07 | Implement event bus and core commands/queries. | P0 | U1 | User/Codex | Service spine | Prompt 1.3.1 | Working dispatcher/events | Run prompt. | WORKSTREAM-04 | FACT |
| TASK-08 | Implement package/instance persistence. | P0 | U1 | User/Codex | Core dispatch; schema choice | Prompt 1.3.2 | Filesystem package/instance registries | Run after confirming manifest approach. | WORKSTREAM-10 | FACT |
| TASK-09 | Hook Dominium sim into Domino sim. | P1 | U1 | User/Codex | Core/sim | Prompt 1.3.3 | Sim orchestration shell | Run prompt. | WORKSTREAM-14 | FACT |
| TASK-10 | Implement canvas builders. | P1 | U1 | User/Codex | dgfx IR and sim stubs | Prompt 1.3.4 | Basic scene command buffers | Run prompt. | WORKSTREAM-06 | FACT |
| TASK-11 | Implement table/tree/view baseline models. | P0/P1 | U1 | User/Codex | pkg/inst | Prompt 1.3.5 | Launcher/tool data models | Run prompt. | WORKSTREAM-04 | FACT |
| TASK-12 | Implement platform backends one at a time. | P0 | U2 | User/Codex | `dsys` vtable | Platform template and toolchains | Real `dsys` backends | Start Win32, SDL2, POSIX/X11. | WORKSTREAM-05 | FACT |
| TASK-13 | Implement renderer vtable and softref. | P0 | U2 | User/Codex | `dgfx` ABI | Renderer Prompt A/B | Renderer backend selector and reference renderer | Run Prompt A then B. | WORKSTREAM-06 | FACT |
| TASK-14 | Implement remaining renderer backends. | P1 | U2/U3 | User/Codex | softref/vtable | Backend templates/APIs | Renderer matrix | Implement one backend per prompt. | WORKSTREAM-06 | FACT |
| TASK-15 | Implement setup core and CLI. | P1 | U2 | User/Codex | pkg/inst/platform | Phase 4.1 prompt | Setup engine and CLI | Run Phase 4.1. | WORKSTREAM-11 | FACT |
| TASK-16 | Implement OS setup wrappers/installers. | P1 | U2/U3 | User/Codex | setup core; packaging tools | Phase 4.2-4.5 prompts | Native installers/wrappers | Verify external tools, then run prompts. | WORKSTREAM-11 | FACT |
| TASK-17 | Implement launcher core. | P1 | U2 | User/Codex | core models/pkg/inst | Phase 5.1 prompt | UI-agnostic launcher core | Run Phase 5.1. | WORKSTREAM-12 | FACT |
| TASK-18 | Implement launcher CLI/TUI/GUI. | P1 | U2 | User/Codex | launcher core; ui/gfx | Phase 5.2-5.4 prompts | Launcher shells | Run in order. | WORKSTREAM-12 | FACT |
| TASK-19 | Implement launcher extension hooks. | P1 | U2 | User/Codex | plugin/package system | Phase 5.5 prompt | Launcher mod/pack extension support | Run Phase 5.5. | WORKSTREAM-12 | FACT |
| TASK-20 | Implement tool framework. | P1 | U2 | User/Codex | core APIs | Phase 6.1 prompt | `dominium-tools` host | Run Phase 6.1. | WORKSTREAM-13 | FACT |
| TASK-21 | Implement core dev tools. | P1 | U2/U3 | User/Codex | tool framework | Phase 6.2 prompt | assetc/pack/replay/test | Run Phase 6.2. | WORKSTREAM-13 | FACT |
| TASK-22 | Implement editor backends. | P1 | U3 | User/Codex | schemas/data APIs | Phase 6.3 prompt | world/save/game/launcher edit APIs | Run after schema decision. | WORKSTREAM-13 | FACT |
| TASK-23 | Implement GUI editor host. | P2 | U3 | User/Codex | editor backends; UI/gfx | Phase 6.4 prompt | Unified editor GUI | Run later. | WORKSTREAM-13 | FACT |
| TASK-24 | Generate detailed Phase 7 Codex prompts. | P1 | U2 | Future assistant | Phase 7 roadmap | User request | Game implementation prompt batch | Do when user asks to continue game phase. | WORKSTREAM-14 | FACT |
| TASK-25 | Define content/schema format and migrations. | P0/P1 | U1/U2 | User/future | Package/content plans | Format decision | Stable schemas and validation | Decide before editor/mod work. | WORKSTREAM-21 | INFERENCE |
| TASK-26 | Choose scripting VM/tier. | P2 | U3 | User/future | Plugin/event system | Requirements | Script layer plan | Evaluate later. | WORKSTREAM-21 | UNCERTAIN / UNVERIFIED |
| TASK-27 | Verify external packaging/platform/render tool details. | P1 | U2 | User/future assistant | External docs | Current web/toolchain docs | Updated assumptions | Verify before implementation. | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| TASK-28 | Define save/replay format. | P1 | U2/U3 | User/future | Game/world schemas | Format/requirements | Save/replay spec | Do before save editor/game save implementation. | WORKSTREAM-22 | UNCERTAIN / UNVERIFIED |
| TASK-29 | Define construction storage and graph format. | P1 | U2/U3 | User/future | Construction design | Data structure/performance criteria | Construction runtime spec | Do before Phase 7 construction implementation. | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |

### 8.1 Recommended Task Order

1. Verify actual repository tree/build state.
2. Apply Phase 1 ABI/API prompts in order.
3. Implement platform backend vtable and selected modern platform backends.
4. Implement renderer vtable and softref.
5. Proceed to setup, launcher, tools, and finally game according to current roadmap.

### 8.2 Blocked Tasks

- Package/instance persistence is blocked on manifest/schema decisions if a final format is required immediately.
- Editor backends are blocked on data/save/schema formats.
- Retro backends are blocked on toolchain/API verification.
- Phase 7 game prompts are blocked only by user request and desired granularity, but implementation depends on earlier phases.

### 8.3 Quick Wins

- Verify repo tree.
- Create `dnumeric.h` / core ABI headers.
- Implement null `dsys`, null `dgfx`, null `daudio`.
- Implement in-memory `dom_core` dispatch and package/instance tables.
- Create softref renderer after `dgfx` vtable.

### 8.4 Tasks Requiring Verification

See Section 15 Verification Queue.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | What would violate it | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Domino core should be C89. | technical | hard | Architecture/prompts | Use portable C; avoid C++/modern C in core. | C++ features or nonportable language features in core. | high | FACT |
| CONSTRAINT-02 | No floating-point in deterministic sim. | technical | hard | Numeric policy discussions | Use fixed-point/integer for sim state/calculations. | Frame-time floats or platform math in sim. | high | FACT |
| CONSTRAINT-03 | Public engine headers must not include OS/graphics API headers. | technical | hard | Platform/render ABI discussions | Backends isolate platform-specific headers. | Win32/Xlib/GL includes in public core headers. | high | FACT |
| CONSTRAINT-04 | ABI boundary structs need size/version metadata. | technical | hard | ABI conventions | Compatibility with plugins/tools/future versions. | Unversioned ABI structs crossing boundaries. | high | FACT |
| CONSTRAINT-05 | Inventory/material counts are whole integers only. | technical/gameplay | hard | User explicit | Items, BOMs, storage use integer counts. | Fractional item stacks/costs. | high | FACT |
| CONSTRAINT-06 | Q4.12 is storage codec for bounded dense values, not primary runtime. | technical | hard | Numeric discussion | Decode into runtime fixed formats. | Using q4.12 for unbounded runtime state. | high | FACT |
| CONSTRAINT-07 | Use q48.16 only where high range/sparse totals need it. | technical | soft/hard by context | Numeric discussion | Avoid dense memory overhead. | q48.16 per tile/cell fields. | high | FACT |
| CONSTRAINT-08 | Renderer is optional for launcher/setup/tools beyond optional canvases. | architecture | hard preference | User explicit | Products can run CLI/TUI/native UI. | Requiring gfx just to list/manage instances. | high | FACT |
| CONSTRAINT-09 | Game client requires suitable renderer. | architecture/product | hard for game client | Accepted design | Fail clearly if no gfx backend. | Pretending CLI/TUI is full game client. | medium | INFERENCE |
| CONSTRAINT-10 | Fallback/degradation must be declared per product. | architecture | hard design rule | Degradation discussion | Use product contracts. | Silent failure/hidden fallback. | high | FACT |
| CONSTRAINT-11 | All products should use common core APIs, not duplicate logic per UI shell. | architecture | hard design rule | Launcher/common code discussion | Shells present views/actions only. | Separate CLI/TUI/GUI logic implementations. | high | FACT |
| CONSTRAINT-12 | Setup wrappers should not reimplement install logic. | architecture/product | hard design rule | Setup plan | OS installers call setup core/CLI. | MSI/pkg/deb duplicating divergent layout rules. | high | FACT |
| CONSTRAINT-13 | Use one Codex prompt per subsystem/backend/product stage. | workflow | strong preference | User and prompt planning | Keep changes bounded. | Batching all backends/products in one prompt. | high | FACT |
| CONSTRAINT-14 | Do not treat assistant suggestions as user decisions unless accepted/built upon. | evidence | hard | Handoff instructions | Preserve uncertainty. | Promoting brainstorms to facts. | high | FACT |
| CONSTRAINT-15 | External-world/software/tool details require verification before use. | evidence/staleness | hard | Handoff rules/date anchor | Use current sources before implementing packaging/platform details. | Using stale WiX/macOS/Linux/SDK info as current. | high | FACT |
| CONSTRAINT-16 | Do not summarise the whole Project; this report covers this chat only. | scope | hard | User handoff instructions | Avoid cross-chat contamination. | Adding unlabelled external project memory. | high | FACT |
| CONSTRAINT-17 | Preserve rejected/superseded options and changes of direction. | handoff | hard | User handoff instructions | Avoid repeated work and false continuity. | Deleting old options from handoff. | high | FACT |
| CONSTRAINT-18 | Products should be describable once and run under arbitrary supported backend combos. | architecture | hard goal | User explicit | Product contract/config approach. | Hardcoding products per platform/renderer. | high | FACT |
| CONSTRAINT-19 | Construction system must support arbitrary construction, not only prefabs. | gameplay | hard goal | User explicit | Parts/construction graph primary. | Prefab-only building system. | high | FACT |
| CONSTRAINT-20 | Seamless transitions/no load screens are desired for surfaces/space/scenes. | gameplay | strong goal | User explicit | Use frames/streaming/tier handoff. | Hard scene boundaries/load transitions as only option. | high | FACT |

### 9.2 Soft Preferences

Soft preferences are embedded in the table above where marked soft/strong preference. The strongest soft preferences are native OS appearance for installers/tools where possible, comprehensive tooling, and long-term extensibility.

### 9.3 Technical Constraints

Key technical constraints: C89 Domino core, no floats in deterministic sim, no public OS/gfx header leakage, versioned ABI structs, fixed-point numeric palette, integer item counts, capability-based backend selection.

### 9.4 Time / Resource Constraints

No calendar deadlines were established. Sequencing constraints are stronger than time constraints.

### 9.5 Legal / Ethical / Safety Constraints

No legal/safety policy constraints specific to game content were discussed. Licensing for external dependencies is unverified and should be audited.

### 9.6 Evidence / Citation Requirements

For this report: label facts/inferences/uncertainty. For future external facts: verify current tool/framework/platform details before use.

### 9.7 Formatting / Output Requirements

The user requested structured headings, tables, stable IDs, and consistent terminology.

### 9.8 Things to Avoid

- Do not turn brainstorms into decisions.
- Do not assume actual code exists.
- Do not reintroduce rejected options without noting status.
- Do not force renderer dependency into launcher/setup/tools.
- Do not implement game systems before stable ABIs unless user changes roadmap.

## 10. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | What is the actual repository state? | Prompts depend on files/build state. | Architecture/prompts exist. | Which files/code actually exist. | Inspect repo/build. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | What final schema/data format should be used? | Packages, mods, tools, editors need it. | JSON/TOML/INI placeholders discussed. | Final format and migrations. | User decision/schema prototype. | P0/P1 | WORKSTREAM-21 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | What scripting VM/tier should be used? | Mods/automation/sandboxing. | Lua/Wren/custom mentioned. | Final VM and deterministic policy. | Evaluate options. | P2 | WORKSTREAM-21 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What is final default UPS? | Sim timing/tuning. | Arbitrary UPS supported; examples vary. | Default and per-save policy. | User/spec decision. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What does README define for scale? | Unit consistency. | Visible chat has 2^24m/chunks/origin. | README details not visible. | Inspect README. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | What are Carbon OS APIs? | Backend implementation. | Carbon OS target mentioned. | Actual syscalls/toolchain. | Project docs/user info. | P1 | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What does fully implement mean for retro/limited backends? | Acceptance criteria. | Caps/fallbacks planned. | Minimum supported features per target. | Capability matrix. | P1 | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Should public ABI use `double` readouts in `dom_sim_state`? | Potential conflict with no-float policy. | Examples used `double` for public readout. | Boundary exception/fixed alternative. | Design decision. | P1 | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | How should plugins work on platforms without dynamic loading? | Mod portability. | Static registration suggested. | Concrete mechanism. | Plugin loader spec. | P1 | WORKSTREAM-21 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | What is exact package manifest format and dependency range syntax? | Package system implementation. | Manifest fields known. | Syntax/version range semantics. | Package spec. | P0/P1 | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | How to store/update huge construction graphs? | Performance and arbitrary construction. | Construction graph concept known. | Data structure/LOD/update algorithms. | Construction runtime prototype/spec. | P1 | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | What are exact surface/air/high-atmo/orbit transition thresholds? | Seamless vehicle transitions. | Conceptual tiers/bands. | Numeric thresholds/criteria. | Frame/tier/vehicle spec. | P1/P2 | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | What current tools/framework versions should be used for packaging/render/platform? | External implementation details may be stale. | Names of tools/APIs known. | Current commands/best practices. | Current documentation verification. | P1 | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | What licensing constraints apply to dependencies? | Distribution/legal risk. | Potential deps listed. | License compatibility. | Dependency/license audit. | P1/P2 | WORKSTREAM-24 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | What detailed Phase 7 prompts are wanted next? | Next roadmap step. | Phase 7 roadmap exists. | Granularity/order desired. | User request. | P1 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| QUESTION-16 | What multiplayer protocol will be used? | Future networked sim. | Lockstep/authoritative discussed. | Concrete protocol. | Later design. | P3 | WORKSTREAM-23 | UNCERTAIN / UNVERIFIED |

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Starting with platforms/renderers before ABIs/APIs. | superseded | User later changed sequence to ABIs first. | final current plan | If ABIs already implemented and verified. | WORKSTREAM-04 | FACT |
| REJECTED-02 | Making launcher/setup/tools require renderers by default. | rejected | User wants renderer optional and native/text modes. | final as default | Custom gfx-only tool/launcher skins. | WORKSTREAM-08 | FACT |
| REJECTED-03 | Separate GUI modes for native GUI and gfx GUI. | rejected/superseded | User asked to unify GUI mode. | final | Only if UI architecture changes significantly. | WORKSTREAM-08 | FACT |
| REJECTED-04 | Full signed/unsigned fixed-point type matrix as first-class API. | rejected | Redundant and encourages misuse. | mostly final | Unsigned storage codecs like U4.12. | WORKSTREAM-15 | FACT |
| REJECTED-05 | q48.16 everywhere including dense fields. | rejected | Too much memory overhead. | final | Sparse/reservoir/global totals. | WORKSTREAM-15 | FACT |
| REJECTED-06 | Milli-unit q64.0/q32.0 as universal representation. | rejected | Wasteful and less flexible for flows. | final | Specific integer diagnostics/counters. | WORKSTREAM-15 | FACT |
| REJECTED-07 | Polar/spherical authoritative space coordinates. | rejected | Trig/wrap/singularity/nonlinear resolution problems. | final | UI display/orbital shell indexing. | WORKSTREAM-18 | FACT |
| REJECTED-08 | Full N-body space simulation by default. | rejected | Too costly/complex; Kepler on-rails sufficient. | final for core | Optional advanced mod/system. | WORKSTREAM-18 | FACT |
| REJECTED-09 | Continuous thrust integration globally for space travel. | deprioritised | Use burns/on-rails; local bubbles for docking. | final for global | Local 6DOF maneuvering/docking. | WORKSTREAM-18 | FACT |
| REJECTED-10 | Prefab-only building system. | rejected | User wants arbitrary construction. | final | Prefabs remain templates/blueprints. | WORKSTREAM-17 | FACT |
| REJECTED-11 | One giant Codex prompt for all systems/backends. | rejected | Likely to tangle implementation. | final workflow | Avoid; keep prompts bounded. | WORKSTREAM-04 | FACT |
| REJECTED-12 | Full generic meta-UI framework now. | deprioritised | Diminishing returns; minimal views/actions sufficient. | tentative | Rich editor UI later if needed. | WORKSTREAM-08 | FACT |

Preserving these prevents repeated work because many were explicitly considered and set aside: renderer-mandatory launchers, prefab-only construction, polar authoritative space, universal q48.16 storage, and broad Codex prompts are all likely to recur unless documented.

## 12. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Top-level repo tree | plan | Define directories | planned/adopted | User-provided tree and assistant refinements | yes | Includes docs/external/include/source/data/tools/scripts/cmake/tests | FACT |
| ARTIFACT-02 | Domino/Dominium layer split | framework | Separate engine and game/product layers | active | Architecture discussion | yes | Core organizing principle | FACT |
| ARTIFACT-03 | ABI/API layer list L0–L12 | framework/spec | Define public interface stack | generated | Layer/interface request | yes | Core future handoff material | FACT |
| ARTIFACT-04 | Prompt 1.1.1 | prompt | Domino engine ABI headers/stubs | generated | Phase 1 prompts | yes | Current Phase 1 artifact | FACT |
| ARTIFACT-05 | Prompt 1.1.2 | prompt | Dominium game ABI headers/stubs | generated | Phase 1 prompts | yes | Current Phase 1 artifact | FACT |
| ARTIFACT-06 | Prompt 1.2.1 | prompt | `dsys` stub | generated | Phase 1 prompts | yes | Current Phase 1 artifact | FACT |
| ARTIFACT-07 | Prompt 1.2.2 | prompt | `dgfx`/`daudio`/`dom_ui`/`dom_input` stubs | generated | Phase 1 prompts | yes | Current Phase 1 artifact | FACT |
| ARTIFACT-08 | Prompt 1.2.3 | prompt | `dom_core`/pkg/inst/sim/canvas/models/events/plugin stubs | generated | Phase 1 prompts | yes | Current Phase 1 artifact | FACT |
| ARTIFACT-09 | Prompts 1.3.1–1.3.5 | prompt group | Core logic, persistence, sim, canvas, models | generated | Phase 1.3 prompts | yes | Current Phase 1 artifacts | FACT |
| ARTIFACT-10 | Generic dsys backend prompt template | prompt/template | Implement platform backends | generated | Platform continuation | yes | Use one per platform | FACT |
| ARTIFACT-11 | Platform parameter table | table/checklist | Parameters for Win32/Win16/DOS/CPM/etc | generated | Platform continuation | yes | Includes retro constraints | FACT |
| ARTIFACT-12 | Generic renderer backend prompt template | prompt/template | Implement renderer backends | generated | Renderer continuation | yes | Use one per renderer | FACT |
| ARTIFACT-13 | Renderer parameter table | table/checklist | Renderer backend list/caps | generated | Renderer continuation | yes | Includes modern/Apple/retro/software | FACT |
| ARTIFACT-14 | Renderer vtable prompt | prompt | Implement `dgfx_backend_vtable` | generated | Prompt A | yes | Phase 3 foundation | FACT |
| ARTIFACT-15 | Softref renderer prompt | prompt | Implement reference software renderer | generated | Prompt B | yes | Canonical renderer | FACT |
| ARTIFACT-16 | Phase 4 setup prompts | prompt group | Setup core and OS installers | generated | Setup phase | yes | Current Phase 4 artifacts | FACT |
| ARTIFACT-17 | Phase 5 launcher prompts | prompt group | Launcher core/shells/extensions | generated | Launcher phase | yes | Current Phase 5 artifacts | FACT |
| ARTIFACT-18 | Phase 6 tools prompts | prompt group | Tool framework/tools/editors | generated | Tools phase | yes | Current Phase 6 artifacts | FACT |
| ARTIFACT-19 | Phase 7+ roadmap | plan | Game and beyond | generated | Game phase planning | yes | Prompts not yet detailed | FACT |
| ARTIFACT-20 | Numeric policy spec content | spec plan | Units/Q formats/determinism | generated | Numeric discussion | yes | Needs formalization | FACT |
| ARTIFACT-21 | Construction abstraction spec content | spec plan | Unified constructions/vehicles/buildings | generated | Construction discussion | yes | High-value design | FACT |
| ARTIFACT-22 | Seamless transition plan | spec plan | Frames, tiers, handoff | generated | Transition discussion | yes | High-value design | FACT |
| ARTIFACT-23 | OC-1 Discovery Inventory | report | Discovery inventory of this chat | generated | Handoff process | yes | Used to make this package | FACT |
| ARTIFACT-24 | Context Transfer Packet | report | Maximum-fidelity state transfer | generated | Handoff process | yes | Base for final package | FACT |
| ARTIFACT-25 | Final report package files | generated documents | Downloadable package created by this response | created now | Current task | yes | Markdown/YAML/ZIP | FACT |

## 13. Rationale and Assumptions

### Visible rationale

- ABIs/APIs first because stable boundaries reduce churn and allow products/backends to be implemented cleanly.
- Domino/Dominium split because the engine should be reusable for other games/projects.
- Renderer optionality for launcher/setup/tools because platform-native or text presentation can perform core functions without gfx.
- Product contracts because graceful degradation must be explicit.
- Render IR because it decouples rendering semantics from backend APIs and enables logging/replay/remote rendering.
- Fixed-point/integer policy because determinism, replay, and multiplayer depend on identical sim results across platforms.
- q4.12 as storage codec because it is compact but too limited for broad runtime state.
- Keplerian on-rails orbits because they provide realistic-feeling space cheaply and deterministically.
- Unified construction graph because vehicles/buildings/machines/rooms/networks/destruction need to interoperate.
- Blueprint ops/jobs because planning and immediate/queued execution share one deterministic path.

### Assumptions

- The repo can be adapted to the proposed layout. UNCERTAIN / UNVERIFIED.
- CMake can support the planned backend/product matrix. UNCERTAIN / UNVERIFIED.
- Current Codex can follow the generated prompts as written. UNCERTAIN / UNVERIFIED.
- Retro targets can be meaningful through limited capabilities/stubs. UNCERTAIN / UNVERIFIED.
- External packaging/rendering/platform tools are available/current. UNCERTAIN / UNVERIFIED.

## 14. Risks and Failure Modes

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Treating prompt-generated plans as already implemented. | Future assistant may assume code exists. | medium | high | Verify repo state before acting. | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| RISK-02 | Over-abstraction makes project unbuildable. | Complexity slows implementation. | medium | high | Limit abstraction to vtables/caps/contracts/plugins/schemas/events. | WORKSTREAM-01 | FACT |
| RISK-03 | Platform/renderer leakage into public/core code. | Portability failure. | medium | high | Enforce backend isolation. | WORKSTREAM-05 | FACT |
| RISK-04 | Implicit graceful degradation. | Half-broken products. | medium | high | Use product contracts and clear failure modes. | WORKSTREAM-09 | FACT |
| RISK-05 | Floating-point/frame-time leakage into sim. | Replay/multiplayer desync. | medium | critical | Use fixed-point/fixed-step sim. | WORKSTREAM-15 | FACT |
| RISK-06 | Dense storage uses too-large numeric formats. | Memory/performance failure. | medium | high | Tiered storage/runtime numeric policy. | WORKSTREAM-15 | FACT |
| RISK-07 | Retro targets overpromised. | Unsupported windows/processes/3D. | high | medium/high | Caps, stubs, scoped retro installers/backends. | WORKSTREAM-05 | FACT |
| RISK-08 | Renderer semantics diverge across backends. | Inconsistent visuals/tools. | medium | medium/high | softref canonical IR semantics and caps. | WORKSTREAM-06 | FACT |
| RISK-09 | Codex prompts too broad. | Broken/tangled repo changes. | high | high | One prompt per backend/subsystem. | WORKSTREAM-04 | FACT |
| RISK-10 | Save/schema incompatibility later. | Broken mods/saves/tools. | medium | high | Versioned schemas, migration rules. | WORKSTREAM-21 | FACT |
| RISK-11 | Duplicated product logic per shell. | CLI/TUI/GUI drift. | medium | high | Common core, views/actions/models. | WORKSTREAM-12 | FACT |
| RISK-12 | Game scope explosion before playable core. | No shippable core. | high | high | Phase 7 playable core first; deep systems later. | WORKSTREAM-14 | INFERENCE |
| RISK-13 | External tooling assumptions stale. | Installer/backend implementation errors. | medium | medium/high | Verify current docs/tools before coding. | WORKSTREAM-11 | FACT |
| RISK-14 | Handoff over-compression loses key prompt artifacts. | Future work repeats/reverts decisions. | medium | high | Preserve artifact ledger and superseded options. | WORKSTREAM-24 | FACT |

## 15. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Actual repo tree and build state. | Implementation prompts depend on reality. | Repo inspection/build logs. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | README-defined scale/unit details. | User referenced existing README scale. | Project README. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | WiX/MSI/Burn current tooling. | Packaging commands may be stale. | Current WiX/Microsoft docs. | P1 | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | macOS pkgbuild/productbuild/notarization. | Apple requirements change. | Apple docs/current tooling. | P1 | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Linux deb/rpm/AppImage/run packaging details. | Distro/tool policy varies. | Debian/Fedora/AppImage docs. | P1 | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | SDL1/SDL2 availability/targets. | Library/toolchain support varies. | SDL docs/package availability. | P2 | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Wayland backend feasibility/current APIs. | Wayland specifics evolve. | Wayland docs/toolkits. | P2 | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Vulkan/MoltenVK current support. | SDK/platform details may change. | Vulkan/MoltenVK docs. | P2 | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | DirectX 7/9/11 SDK availability. | Legacy SDK issues. | Microsoft SDK docs/toolchains. | P2 | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | QuickDraw/Carbon/macOS Classic toolchains. | Retro Mac tooling niche. | Retro toolchain docs. | P3 | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Win16/DOS/CPM compilers and memory limits. | Backend feasibility. | Target toolchains/emulators. | P2 | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Carbon OS API/toolchain. | Custom platform not described. | Carbon OS docs/files/user info. | P1 | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Dependency licenses. | Distribution/legal compatibility. | License audit. | P2 | WORKSTREAM-24 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Schema/data format choice. | Implementation needs concrete format. | User decision/spec. | P0/P1 | WORKSTREAM-21 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | Scripting VM choice. | Modding architecture. | VM evaluation. | P2 | WORKSTREAM-21 | UNCERTAIN / UNVERIFIED |
| VERIFY-16 | Renderer IR payload layouts. | All renderers need stable semantics. | Spec review/prototype. | P1 | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-17 | Public ABI `double` use in sim state. | Could conflict with no-float rule. | Design review. | P1 | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-18 | Save/replay file format. | Tools/game need it. | Spec/prototype. | P1 | WORKSTREAM-22 | UNCERTAIN / UNVERIFIED |
| VERIFY-19 | Construction storage/graph format. | Arbitrary construction depends on it. | Prototype/spec. | P1 | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-20 | Exact acceptance criteria for “fully implement every platform/renderer”. | Scope control. | Capability matrix/user confirmation. | P1 | WORKSTREAM-05/06 | UNCERTAIN / UNVERIFIED |

## 16. Spec Book Contribution Notes

Likely Project Spec Book sections:

| ID | Likely section | Contribution | Spec status | Label |
|---|---|---|---|---|
| SPEC-01 | Engine Architecture | Domino/Dominium split, ABI/API layers, product contracts. | formal requirement candidate | FACT |
| SPEC-02 | Platform Abstraction | `dsys`, platform backends, capability matrix. | formal requirement candidate | FACT |
| SPEC-03 | Renderer Abstraction | `dgfx` IR, softref, backend matrix. | formal requirement candidate | FACT |
| SPEC-04 | UI Architecture | UI modes/backends, native/gfx/CLI/TUI presentation. | formal requirement candidate | FACT |
| SPEC-05 | Package/Instance/Mod System | Package kinds, instance load order, launcher/game/tool packages. | formal requirement candidate | FACT |
| SPEC-06 | Setup and Distribution | Setup core, native installers, install scopes. | formal requirement candidate but current external details need verification | FACT |
| SPEC-07 | Launcher Product | Common launcher core, views/actions/models, extension hooks. | formal requirement candidate | FACT |
| SPEC-08 | Tools and SDKs | Tool host, dev tools, editors, SDK exports. | formal requirement candidate | FACT |
| SPEC-09 | Numeric and Determinism Policy | Fixed-point/integer units, UPS/FPS separation. | formal requirement candidate | FACT |
| SPEC-10 | World and Simulation | Grid/chunks/fields/environment/space/seamless transitions. | formal requirement candidate with pending specifics | FACT |
| SPEC-11 | Construction and Vehicles | Unified arbitrary construction graph model. | formal requirement candidate | FACT |
| SPEC-12 | Space and Orbits | Kepler on rails, sites, belts, transitions. | formal requirement candidate | FACT |
| SPEC-13 | Future Systems | Actors, AI, life support, economy, politics, multiplayer. | background and future requirements; needs confirmation as implementation approaches | FACT |

Unique contributions from this chat:
- Current implementation phase order.
- Comprehensive ABI/API stack.
- Product-contract/capability runtime model.
- Renderer optionality and unified UI model.
- Renderer backend matrix and prompt strategy.
- Setup/launcher/tools prompt plans.
- Arbitrary construction and seamless transition architecture.
- Numeric policy and world/space unit decisions.

Likely duplicates with other chats:
- Repo structure.
- Package/mod/pack concepts.
- World/space/environment systems.
- Launcher/setup/game plans.
- Tools/SDK ideas.

Conflicts to watch for:
- Earlier sequences that place platforms/renderers before ABIs/APIs.
- Earlier ECS/world prompts that hard-code terrain/hydro before generic primitives.
- Any other chat choosing different units/Q formats.
- Any other chat choosing a different data/manifest format.

Items needing user confirmation before becoming formal requirements:
- Scripting VM.
- Schema format.
- Default UPS.
- Exact retro platform minimum capabilities.
- Exact save/replay format.
- Construction graph storage format.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | ABIs/APIs first current roadmap | decision | This is the latest sequencing decision. | Future work may follow superseded order. | FACT | high |
| 2 | Domino/Dominium separation | architecture | Core reusable engine vs game layer. | Engine/game coupling. | FACT | high |
| 3 | Renderer optional for launcher/setup/tools | requirement | Enables native/text/headless operation. | Unnecessary backend dependency. | FACT | high |
| 4 | Unified UI mode/backend model | architecture | Allows native/custom GUI under one GUI mode. | UI mode explosion. | FACT | high |
| 5 | Product contracts/capability matching | architecture | Safe graceful degradation. | Silent broken fallbacks. | FACT | high |
| 6 | Render command-buffer IR | architecture | Renderer independence and tools. | Backend-specific rendering leaks. | FACT | high |
| 7 | Q4.12/Q16.16/Q48.16 numeric policy | technical | Deterministic sim and storage discipline. | Unit/range errors. | FACT | high |
| 8 | Integer-only inventory counts | gameplay/technical | Economy consistency. | Fractional item bugs. | FACT | high |
| 9 | 0,0,0 center/sea-level origin | world spec | Core coordinate convention. | World coordinate confusion. | FACT | high |
| 10 | Cartesian SpacePos + Keplerian orbits | space spec | Cheap deterministic space. | Wrong physics model. | FACT | high |
| 11 | Construction graph unifies vehicles/buildings/machines | gameplay architecture | Arbitrary construction and mobility. | Parallel incompatible systems. | FACT | high |
| 12 | Blueprints/plans compile to jobs | gameplay architecture | Unified manual/queued execution. | Duplicated build paths. | FACT | high |
| 13 | OS-native setup wrappers over setup core | distribution | Expected platform UX without logic divergence. | Inconsistent installs. | FACT | high |
| 14 | Launcher as views/actions/models | product architecture | Common CLI/TUI/GUI launcher. | Shell drift. | FACT | high |
| 15 | Tools/SDKs are first-class products | ecosystem | Modding/dev workflows. | Tooling afterthought. | FACT | high |
| 16 | Phase 7 playable core before deep systems | roadmap | Prevents scope explosion. | No playable baseline. | FACT | medium-high |
| 17 | External-world/tool details require verification | evidence | Avoid stale implementation instructions. | Broken setup/backend implementation. | FACT | high |
| 18 | Actual repo state unverified | caveat | Prevents false assumptions. | Applying prompts blindly. | UNCERTAIN / UNVERIFIED | high |
| 19 | Generated prompts are artifacts to preserve | artifact | They are implementation plan source material. | Loss of concrete work orders. | FACT | high |
| 20 | Preserve superseded options | handoff | Avoid repeating rejected designs. | Architecture regression. | FACT | high |

## 18. What Future Assistants Must Not Assume

- Do not assume any generated prompt has been run.
- Do not assume repository files match proposed paths.
- Do not assume external packaging/rendering tools are current.
- Do not assume a scripting VM has been chosen.
- Do not assume JSON/TOML/INI was finalized.
- Do not assume default UPS has been finalized.
- Do not assume retro platforms can fully support GUI/windows/3D/processes.
- Do not assume public ABI `double` usage is acceptable without review.
- Do not assume earlier Phase 2.5–7 prompts are the current sequence.
- Do not assume assistant suggestions are user decisions unless accepted in flow or explicitly stated.

## 19. Recommended Next Action

If continuing this chat’s work alone:
1. Verify actual repo state.
2. Then apply or adapt Phase 1 prompts beginning with Domino ABI headers/stubs.

If aggregating with other chat reports:
1. Merge by workstream and ID.
2. Preserve conflicting/superseded roadmap variants.
3. Confirm current roadmap with user before producing master spec.

User verification needed before acting:
- Confirm whether to proceed with Phase 1 implementation prompts or generate detailed Phase 7 prompts.
- Confirm actual repo state.
- Confirm schema/data format if package/instance persistence is imminent.

## 20. Appendix: Possibly Relevant Details

- All products should be able to run with `dom_core` and product contracts.
- Launcher/setup/tools should use `dom_ui` and generic models; game primarily uses `dgfx`.
- Setup wrappers should be thin adapters over setup core.
- Renderer backends should implement all IR commands where possible, stubbing/fallbacking where not possible and reporting caps accurately.
- Platform backends should report features accurately; limited/retro platforms should not pretend to support windows/processes.
- Tools include both CLI tools and GUI editor host.
- Game Phase 7 target: create a new world, move camera, place basic machines/belts/power, save/load, replay, configurable UPS, debug stats.
