# Full Chat Report — Dominium APP0 Runtime, Platform, and Renderer Architecture

## 0. Report Metadata

| Field | Value |
|---|---|
| Chat label | Dominium APP0 Runtime, Platform, and Renderer Architecture |
| Filesystem-safe label | `dominium_app0_runtime_platform_renderers` |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Generated timestamp | 2026-05-27 14:48:47 Australia/Melbourne |
| Source scope | THIS CHAT ONLY, with PROJECT-CONTEXT explicitly labelled where used |
| Apparent coverage | Full visible chat coverage; project attachments were not inspected by this package |
| Extraction confidence | 4 / 5 |
| Staleness risk | Medium, because graphics API/platform/toolchain claims and prior links require future verification |
| Future plans present | Yes |
| Pending tasks present | Yes |
| Artifacts/files present | Yes, mainly prompts/outputs/references; no repository files were created before this final package |
| Safe for aggregation | Yes, with caveats |
| Main limitations | Actual old repo snapshot was not inspected here; prior assistant repo-inspection claim is unverified; assistant proposals are not user decisions unless explicitly accepted; external API/platform facts require future verification |

## 1. Executive Summary

This chat was about the Dominium / Domino project’s APP0 layer: runtimes, applications, platforms, renderers, and executable support. The original user-provided APP0 prompt established a strict boundary: work on the application and runtime layer only, without redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, or adding gameplay shortcuts. The authoritative simulation remains in engine + game, while applications are replaceable shells and orchestrators. The core applications in scope are client, server, launcher, setup/installer, and tools.

The first assistant response generated a large Codex-style implementation prompt for APP0, including targets, CLI flags, CMake options, docs, smoke tests, and commit sequencing. The user then redirected the process: before planning or generating further prompts, they wanted discussion. The later discussion identified that APP0’s high-level philosophy was sound but mechanically under-specified. Important missing design items included enforcement of authority boundaries through include/link rules, client prediction policy, renderer capability granularity, server sharding semantics, and setup/content trust semantics.

The user then clarified the end-state expectation for the macro-prompt plan: it should ultimately produce a running executable capable of opening a real, interactive, resizable window across each supported platform and renderer combination. This changed the practical architecture requirements. A platform runtime layer was proposed as a missing or at least under-formalized layer: platform creates windows, pumps events, handles resize, exposes native surface handles, and provides timing; renderers consume surfaces and never create windows; the client orchestrates platform and renderer; the server remains headless and authoritative.

The user granted write permission to docs plus render, platform, application, client, and server, and asked whether engine/game write permission is required. The prior answer was tentative: APP0 should not require engine/game writes if engine/game already expose sufficient public boundaries. That answer is not verified against actual code. It must be checked by inspecting the old repository snapshot before any implementation plan relies on it.

The renderer discussion expanded beyond the initial APP0 list. The user mentioned null renderer, software renderer, D3D7, D3D9, D3D11, D3D12, Vulkan, GL1 through GL4, Metal, Windows, Linux, macOS, PC, Mac, Xbox, PlayStation, Nintendo Switch, Intel, AMD, NVIDIA, and vintage systems. The recommended architecture was not to model renderers by GPU vendor, but by API/backend/capability family. Proposed categories included native APIs, translation layers, software/virtual/CI backends, support classes such as canonical/compatibility/experimental, and vintage capability tiers R0 through R5. These are proposals, not confirmed final requirements.

The user then asked whether this was the best possible design and requested use of the old code snapshot in project attachments. A prior assistant claimed to inspect a snapshot and proposed an advanced architecture: applications over a runtime framework, modules for render/platform/audio/network/filesystem/input, engine/game below that, render devices instead of renderer monoliths, a framegraph, module manifests, capability negotiation, and static executable cores plus optional dynamic modules. However, this report treats the snapshot-inspection claim as UNCERTAIN / UNVERIFIED. The next assistant must inspect the actual files before making repo-specific claims.

The most important carry-forward item is that APP0 is not just “make stubs”; it is the foundation for a long-term plug-and-play runtime architecture. The future assistant must preserve authority boundaries, not conflate platform with renderer, not treat assistant proposals as accepted decisions, and not generate new Codex prompts until the user explicitly asks after repository verification.

## 2. How to Use This Report

This report covers this old chat only. It should not be treated as a complete Dominium Project specification. Use it as one source package for later aggregation with other old-chat reports.

Uncertain items must not be treated as facts. Items labelled **FACT** come from explicit user statements or visible chat outputs. Items labelled **INFERENCE** are reasonable conclusions from this chat but were not explicitly finalized by the user. Items labelled **UNCERTAIN / UNVERIFIED** are incomplete, unclear, stale, or not directly established. Items labelled **PROJECT-CONTEXT** come from project/system/user-profile context rather than the visible transcript.

Direct user statements outrank assistant suggestions. Assistant proposals such as the platform runtime layer, support classes, module architecture, capability tiers, and framegraph should be considered design candidates until the user confirms them or verified code constraints require them.

This report is intended for later master-spec aggregation. A future aggregator should preserve IDs, labels, uncertainty, and source provenance rather than merging similar items prematurely.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Source basis | Strength | Implication for future assistants | Risk if misunderstood | Label |
|---|---|---|---|---|---|---|
| PREFERENCE-01 | Prefer maximum-fidelity state transfer over normal summaries | User requested maximum-fidelity Context Transfer Packet and final package | strong | Preserve details, uncertainty, registers, artifacts, and next actions. | Lossy summaries would force re-explanation. | FACT |
| PREFERENCE-02 | Prefer discussion before prompt generation | User said to discuss before planning or generating prompts | strong | Do not jump to Codex prompts without explicit request. | Premature prompt generation may misalign architecture. | FACT |
| PREFERENCE-03 | Prefer robust, modular, extensible architecture | User asked for intelligent, intuitive, robust, compatible, optimized, moddable, modular, extensible design | strong | Evaluate designs by long-term maintainability and plug-and-play capability. | Overly minimal scaffolds may be insufficient. | FACT |
| PREFERENCE-04 | Prefer plug-and-play and mix-and-match code/data | User wants to mix and match code without rewriting or duplication | strong | Use interfaces, modules, capability descriptors, and shared code paths. | Monolithic designs would conflict with goal. | FACT |
| PREFERENCE-05 | Prefer broad binary/platform/renderer distribution | User wants same executable or set of executables across supported systems | strong | Design packaging/modules/selection for breadth. | Naive per-combination binaries may cause matrix explosion. | FACT |
| PREFERENCE-06 | Prefer epistemic labels and no invented facts | User package prompt and prior preferences | strong | Use FACT/INFERENCE/UNCERTAIN labels and avoid unsupported claims. | Overconfidence damages future aggregation. | FACT |

### 3.2 Inferred Preferences

| ID | Preference | Source basis | Strength | Implication for future assistants | Risk if misunderstood | Label |
|---|---|---|---|---|---|---|

No separate inferred-only preferences were needed beyond the explicit statements and project-context preferences in this package. The main practical inference is that the user prefers robust long-term architecture over quick stubs.

### 3.3 Preferences Not Established by This Chat

| ID | Preference | Source basis | Strength | Implication for future assistants | Risk if misunderstood | Label |
|---|---|---|---|---|---|---|
| PREFERENCE-07 | Interested in computer science and rigorous facts | User profile outside visible chat | medium | Technical depth and rigor are appropriate. | Should not overfit if not relevant. | PROJECT-CONTEXT |
| PREFERENCE-08 | Wants response prefix with model and timestamp | User profile outside visible chat | medium | Prefix final responses accordingly. | May be omitted by future assistants if system conflicts. | PROJECT-CONTEXT |

Preferences not established in this visible chat include exact coding style, specific C/C++ standard, preferred build generator, exact module ABI, exact OS version minimums, exact renderer priority order, and exact packaging format.

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | APP0 application/runtime layer | Define and eventually implement the application/runtime layer only: client, server, launcher, setup/installer, tools, platform support, and renderers. | APP0 exists as a user-provided prompt and was expanded once into a Codex-style implementation pack. No actual repository modifications are established by this chat. | All APP0 applications and runtime layers are clearly defined, responsibility boundaries are non-overlapping, rendering is isolated, servers are authoritative, supported platforms are cleanly handled, and docs explain the architecture. | active | critical | 5 | FACT |
| WORKSTREAM-02 | Client runtime and real window bring-up | Produce a client executable that can open a real, interactive, resizable window while remaining non-authoritative. | Desired end state was stated by the user. Actual client code is unverified because the old repository snapshot was not inspected in this visible chat. | A client that orchestrates platform runtime, renderer selection, input capture, audio/UI/network placeholders as needed, observer clocks, and a clean presentation loop without sim authority. | active | critical | 5 | FACT |
| WORKSTREAM-03 | Server runtime | Define and scaffold or implement a headless-capable authoritative server runtime. | APP0 requirements are clear. Existing server implementation is unverified. | Server is authoritative, headless-capable, supports AI-only autorun, sharding hooks, scheduling, persistence hooks, law enforcement, and integrity/anti-cheat hooks without renderer/window dependencies. | active | critical | 5 | FACT |
| WORKSTREAM-04 | Renderer architecture and capability model | Create a renderer architecture supporting null, software, Direct3D generations, Vulkan, OpenGL generations, Metal, and possible translation/software/virtual backends through capability-driven selection. | User stated Dominium has or should have null, software, and multiple hardware renderer families. Actual code presence is unverified. | Renderer backends are replaceable, capability-described, policy-selected, isolated from simulation, and do not create windows. | active | critical | 5 | FACT |
| WORKSTREAM-05 | Platform runtime and window/presentation services | Introduce or formalize a platform runtime layer for windows, events, resize, native surfaces, timing, filesystem/process/dylib services, and headless operation. | A prior assistant proposed this as the missing layer needed for real windows. Actual platform code is unverified. | Platform creates windows and surfaces; renderers consume opaque surface handles; client orchestrates both; server can remain headless. | active | critical | 4 | INFERENCE |
| WORKSTREAM-06 | Launcher orchestration | Define launcher responsibilities for instance/profile selection, capability detection, and session orchestration. | APP0 requirements are clear. Existing launcher code is unverified. | Launcher detects capabilities, selects profiles/instances, and launches client/server/setup/tools without installing content or mutating simulation state. | active | high | 5 | FACT |
| WORKSTREAM-07 | Setup / installer / integrity layer | Define setup responsibilities for engine/content installation, version management, and integrity validation. | APP0 requirements are clear. Trust model and actual implementation are unresolved. | Setup manages install/verify/repair/versioning through manifests and integrity checks without embedding simulation logic. | active | high | 5 | FACT |
| WORKSTREAM-08 | Tools: inspectors, validator, replay viewer, editor, profiler | Define tools that inspect, validate, replay, profile, or optionally edit worlds while respecting the same authority/law model. | APP0 requirements are clear. Actual tools and their authority boundaries are unverified. | Tools are auditable and never bypass law; write/elevated operations are explicit, authorized, and logged. | active | high | 5 | FACT |
| WORKSTREAM-09 | Distribution, modules, plugins, and mix-and-match architecture | Design a modular runtime/package architecture that lets code and data be plugged, mixed, matched, and distributed across many platforms/renderers with minimal duplication. | The user explicitly requested plug-and-play, mix-and-match, broad binary distribution. Module/component architecture was proposed but not accepted as final. | Per-platform/per-architecture packages with stable executable cores and optional/static or dynamic backend modules selected by capability and policy. | active | high | 4 | INFERENCE |
| WORKSTREAM-10 | Old repository snapshot integration and verification | Inspect the old code snapshot/project attachments and make future architecture/prompt work fit the actual codebase. | User requested inspection. A prior assistant claimed to inspect it, but that claim is unverified in this visible chat and must not be relied on without re-checking. | Verified repository inventory: actual tree, build system, languages, existing render/platform/client/server code, engine/game APIs, docs, and tests. | active | critical | 5 | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — APP0 application/runtime layer

- Label: FACT
- Objective: Define and eventually implement the application/runtime layer only: client, server, launcher, setup/installer, tools, platform support, and renderers.
- Background: The user positioned APP0 as part of the Dominium/Domino project and explicitly limited it to the application and runtime layer.
- Current state: APP0 exists as a user-provided prompt and was expanded once into a Codex-style implementation pack. No actual repository modifications are established by this chat.
- Desired end state: All APP0 applications and runtime layers are clearly defined, responsibility boundaries are non-overlapping, rendering is isolated, servers are authoritative, supported platforms are cleanly handled, and docs explain the architecture.
- Importance: This layer determines how the simulation is hosted, displayed, packaged, launched, and inspected without corrupting engine/game authority.
- Decisions made: DECISION-01: APP0 scope is application/runtime layer only, DECISION-02: Applications are shells and orchestrators, not decision-makers, DECISION-03: Authoritative logic remains in engine + game, DECISION-09: Discuss before generating more prompts, DECISION-10: Current write permission includes render, platform, application, client, server, and docs
- Decisions pending: See related open questions and proposed decisions; do not treat proposals as accepted.
- Pending tasks: TASK-05: Map current dependency graph, TASK-06: Define authority/layer boundary map, TASK-12: Draft revised repo-specific APP0 architecture plan, TASK-13: Generate revised Codex implementation prompts only when requested, TASK-14: Implement null/headless runtime smoke path
- Constraints: CONSTRAINT-01: Do not redesign simulation rules, CONSTRAINT-02: Do not alter content definitions, CONSTRAINT-03: Do not change life/civ/economy logic, CONSTRAINT-04: Do not introduce gameplay shortcuts, CONSTRAINT-05: Applications are shells around the simulation, CONSTRAINT-06: All authoritative logic remains in engine + game, CONSTRAINT-15: Current allowed write areas are render, platform, application, client, server, and docs, CONSTRAINT-16: Do not generate prompts before discussion unless user asks
- Dependencies: Actual repository files, build system, public APIs, and user confirmation where indicated.
- Timeline / sequencing: Verify repository first; then formalize boundaries; then design interfaces; then implement or prompt implementation.
- Blockers: Unverified code snapshot and unresolved design choices.
- Risks: See risk register.
- Artifacts: ARTIFACT-01: User APP0 prompt: Runtimes, Applications, Platforms & Renderers, ARTIFACT-02: Assistant APP0 implementation pack, ARTIFACT-03: User process correction: discuss before prompts, ARTIFACT-13: Previously generated Context Transfer Packet
- Success criteria: Must satisfy APP0 acceptance criteria and any later user-confirmed executable/window/distribution goals.
- Recommended next action: Proceed only after repository verification and boundary map are completed.
- Verification needed: VERIFY-05: Engine/game public APIs, VERIFY-10: Current docs/app content, VERIFY-11: Existing tests and smoke paths
- Confidence: 5 / 5
- Carry-forward priority: critical

### WORKSTREAM-02 — Client runtime and real window bring-up

- Label: FACT
- Objective: Produce a client executable that can open a real, interactive, resizable window while remaining non-authoritative.
- Background: APP0 defined client responsibilities and prohibitions; the user later clarified the final macro-plan should yield a running windowed executable.
- Current state: Desired end state was stated by the user. Actual client code is unverified because the old repository snapshot was not inspected in this visible chat.
- Desired end state: A client that orchestrates platform runtime, renderer selection, input capture, audio/UI/network placeholders as needed, observer clocks, and a clean presentation loop without sim authority.
- Importance: This is the first user-visible proof that platform/runtime/render architecture works.
- Decisions made: DECISION-05: Client is non-authoritative, DECISION-14: Bring up null/software paths before GPU backends
- Decisions pending: See related open questions and proposed decisions; do not treat proposals as accepted.
- Pending tasks: TASK-15: Implement software renderer window path, TASK-16: Implement client presentation loop
- Constraints: CONSTRAINT-07: Client must not simulate authoritative state, CONSTRAINT-08: Client must not bypass law or invent data
- Dependencies: Actual repository files, build system, public APIs, and user confirmation where indicated.
- Timeline / sequencing: Verify repository first; then formalize boundaries; then design interfaces; then implement or prompt implementation.
- Blockers: Unverified code snapshot and unresolved design choices.
- Risks: See risk register.
- Artifacts: ARTIFACT-05: User executable-window goal
- Success criteria: Must satisfy APP0 acceptance criteria and any later user-confirmed executable/window/distribution goals.
- Recommended next action: Proceed only after repository verification and boundary map are completed.
- Verification needed: VERIFY-08: Client/server current dependencies
- Confidence: 5 / 5
- Carry-forward priority: critical

### WORKSTREAM-03 — Server runtime

- Label: FACT
- Objective: Define and scaffold or implement a headless-capable authoritative server runtime.
- Background: APP0 specified server responsibilities and requirements.
- Current state: APP0 requirements are clear. Existing server implementation is unverified.
- Desired end state: Server is authoritative, headless-capable, supports AI-only autorun, sharding hooks, scheduling, persistence hooks, law enforcement, and integrity/anti-cheat hooks without renderer/window dependencies.
- Importance: Authoritative server boundaries are essential for MMO scale, anti-cheat, persistence, and deterministic simulation hosting.
- Decisions made: DECISION-06: Server is authoritative and headless-capable
- Decisions pending: See related open questions and proposed decisions; do not treat proposals as accepted.
- Pending tasks: TASK-21: Define sharding semantics or explicitly label as plumbing only
- Constraints: CONSTRAINT-09: Server must be authoritative and headless-capable
- Dependencies: Actual repository files, build system, public APIs, and user confirmation where indicated.
- Timeline / sequencing: Verify repository first; then formalize boundaries; then design interfaces; then implement or prompt implementation.
- Blockers: Unverified code snapshot and unresolved design choices.
- Risks: See risk register.
- Artifacts: See artifact ledger.
- Success criteria: Must satisfy APP0 acceptance criteria and any later user-confirmed executable/window/distribution goals.
- Recommended next action: Proceed only after repository verification and boundary map are completed.
- Verification needed: VERIFY-09: Whether server currently depends on graphics/window code
- Confidence: 5 / 5
- Carry-forward priority: critical

### WORKSTREAM-04 — Renderer architecture and capability model

- Label: FACT
- Objective: Create a renderer architecture supporting null, software, Direct3D generations, Vulkan, OpenGL generations, Metal, and possible translation/software/virtual backends through capability-driven selection.
- Background: The user asked how to support Windows, Linux, macOS, PC, Mac, Xbox, PlayStation, Nintendo Switch, Intel, AMD, NVIDIA, vintage systems, etc.
- Current state: User stated Dominium has or should have null, software, and multiple hardware renderer families. Actual code presence is unverified.
- Desired end state: Renderer backends are replaceable, capability-described, policy-selected, isolated from simulation, and do not create windows.
- Importance: Renderer architecture controls compatibility, portability, performance, distribution size, and long-term extensibility.
- Decisions made: DECISION-04: Rendering never affects simulation, DECISION-13: Renderers should not create windows, DECISION-15: Do not model renderers by GPU vendor, DECISION-16: Use support classes: canonical, compatibility, experimental, DECISION-17: Use capability tiers R0–R5 for vintage/modern support, DECISION-19: Consider render device + framegraph architecture
- Decisions pending: See related open questions and proposed decisions; do not treat proposals as accepted.
- Pending tasks: TASK-08: Define renderer capability schema, TASK-09: Define support classes and target matrix, TASK-17: Add renderer selection policy, TASK-18: Add GPU backends incrementally
- Constraints: CONSTRAINT-10: Rendering never affects simulation, CONSTRAINT-11: Renderer selection must be capability-driven and policy-driven
- Dependencies: Actual repository files, build system, public APIs, and user confirmation where indicated.
- Timeline / sequencing: Verify repository first; then formalize boundaries; then design interfaces; then implement or prompt implementation.
- Blockers: Unverified code snapshot and unresolved design choices.
- Risks: See risk register.
- Artifacts: ARTIFACT-09: User renderer/platform/vintage/consoles question, ARTIFACT-10: Assistant renderer/platform taxonomy answer, ARTIFACT-15: Prior external reference links about graphics APIs/tools
- Success criteria: Must satisfy APP0 acceptance criteria and any later user-confirmed executable/window/distribution goals.
- Recommended next action: Proceed only after repository verification and boundary map are completed.
- Verification needed: VERIFY-06: Existing renderers and renderer ownership of windows, VERIFY-12: External graphics API/backend facts, VERIFY-14: Vintage target list
- Confidence: 5 / 5
- Carry-forward priority: critical

### WORKSTREAM-05 — Platform runtime and window/presentation services

- Label: INFERENCE
- Objective: Introduce or formalize a platform runtime layer for windows, events, resize, native surfaces, timing, filesystem/process/dylib services, and headless operation.
- Background: The user wants real windows across renderer/platform combinations. This cannot be implemented cleanly inside renderers.
- Current state: A prior assistant proposed this as the missing layer needed for real windows. Actual platform code is unverified.
- Desired end state: Platform creates windows and surfaces; renderers consume opaque surface handles; client orchestrates both; server can remain headless.
- Importance: Separating platform from rendering prevents API duplication and preserves headless/server portability.
- Decisions made: DECISION-12: Introduce or formalize a platform runtime layer
- Decisions pending: See related open questions and proposed decisions; do not treat proposals as accepted.
- Pending tasks: TASK-07: Define minimal platform runtime contract
- Constraints: General APP0 authority and scope constraints apply.
- Dependencies: Actual repository files, build system, public APIs, and user confirmation where indicated.
- Timeline / sequencing: Verify repository first; then formalize boundaries; then design interfaces; then implement or prompt implementation.
- Blockers: Unverified code snapshot and unresolved design choices.
- Risks: See risk register.
- Artifacts: ARTIFACT-06: Assistant platform runtime proposal
- Success criteria: Must satisfy APP0 acceptance criteria and any later user-confirmed executable/window/distribution goals.
- Recommended next action: Proceed only after repository verification and boundary map are completed.
- Verification needed: VERIFY-07: Existing platform layer responsibilities
- Confidence: 4 / 5
- Carry-forward priority: critical

### WORKSTREAM-06 — Launcher orchestration

- Label: FACT
- Objective: Define launcher responsibilities for instance/profile selection, capability detection, and session orchestration.
- Background: APP0 explicitly separated launcher from setup/installer.
- Current state: APP0 requirements are clear. Existing launcher code is unverified.
- Desired end state: Launcher detects capabilities, selects profiles/instances, and launches client/server/setup/tools without installing content or mutating simulation state.
- Importance: The launcher is the front door for runtime selection and distribution policy but must not become an installer or authority layer.
- Decisions made: DECISION-07: Launcher must not install content or mutate simulation state
- Decisions pending: See related open questions and proposed decisions; do not treat proposals as accepted.
- Pending tasks: None specifically listed beyond verification and later implementation planning.
- Constraints: CONSTRAINT-12: Launcher must not alter simulation state or install content
- Dependencies: Actual repository files, build system, public APIs, and user confirmation where indicated.
- Timeline / sequencing: Verify repository first; then formalize boundaries; then design interfaces; then implement or prompt implementation.
- Blockers: Unverified code snapshot and unresolved design choices.
- Risks: See risk register.
- Artifacts: See artifact ledger.
- Success criteria: Must satisfy APP0 acceptance criteria and any later user-confirmed executable/window/distribution goals.
- Recommended next action: Proceed only after repository verification and boundary map are completed.
- Verification needed: See verification queue.
- Confidence: 5 / 5
- Carry-forward priority: high

### WORKSTREAM-07 — Setup / installer / integrity layer

- Label: FACT
- Objective: Define setup responsibilities for engine/content installation, version management, and integrity validation.
- Background: APP0 separated setup from launcher.
- Current state: APP0 requirements are clear. Trust model and actual implementation are unresolved.
- Desired end state: Setup manages install/verify/repair/versioning through manifests and integrity checks without embedding simulation logic.
- Importance: Installer/versioning/integrity boundaries are required for reproducible packages, mods, multiplayer trust, and anti-cheat support.
- Decisions made: None finalized in this chat beyond general APP0 constraints.
- Decisions pending: See related open questions and proposed decisions; do not treat proposals as accepted.
- Pending tasks: TASK-19: Define setup trust/integrity model
- Constraints: CONSTRAINT-13: Setup installs content/engine, manages versions, validates integrity
- Dependencies: Actual repository files, build system, public APIs, and user confirmation where indicated.
- Timeline / sequencing: Verify repository first; then formalize boundaries; then design interfaces; then implement or prompt implementation.
- Blockers: Unverified code snapshot and unresolved design choices.
- Risks: See risk register.
- Artifacts: See artifact ledger.
- Success criteria: Must satisfy APP0 acceptance criteria and any later user-confirmed executable/window/distribution goals.
- Recommended next action: Proceed only after repository verification and boundary map are completed.
- Verification needed: VERIFY-15: Setup trust model requirements
- Confidence: 5 / 5
- Carry-forward priority: high

### WORKSTREAM-08 — Tools: inspectors, validator, replay viewer, editor, profiler

- Label: FACT
- Objective: Define tools that inspect, validate, replay, profile, or optionally edit worlds while respecting the same authority/law model.
- Background: APP0 explicitly lists world inspector, economy inspector, replay viewer, optional editor, and profiler.
- Current state: APP0 requirements are clear. Actual tools and their authority boundaries are unverified.
- Desired end state: Tools are auditable and never bypass law; write/elevated operations are explicit, authorized, and logged.
- Importance: Tools are essential for development and mods, but they can corrupt the simulation model if treated as unrestricted god-mode utilities.
- Decisions made: DECISION-08: Tools must obey authority/law and be auditable
- Decisions pending: See related open questions and proposed decisions; do not treat proposals as accepted.
- Pending tasks: TASK-20: Define tools elevation and audit model
- Constraints: CONSTRAINT-14: Tools must use same authority rules and be auditable
- Dependencies: Actual repository files, build system, public APIs, and user confirmation where indicated.
- Timeline / sequencing: Verify repository first; then formalize boundaries; then design interfaces; then implement or prompt implementation.
- Blockers: Unverified code snapshot and unresolved design choices.
- Risks: See risk register.
- Artifacts: See artifact ledger.
- Success criteria: Must satisfy APP0 acceptance criteria and any later user-confirmed executable/window/distribution goals.
- Recommended next action: Proceed only after repository verification and boundary map are completed.
- Verification needed: VERIFY-16: Tools law/elevation model
- Confidence: 5 / 5
- Carry-forward priority: high

### WORKSTREAM-09 — Distribution, modules, plugins, and mix-and-match architecture

- Label: INFERENCE
- Objective: Design a modular runtime/package architecture that lets code and data be plugged, mixed, matched, and distributed across many platforms/renderers with minimal duplication.
- Background: The user wants binaries that run on as many architectures/platforms/renderers as possible in the same executable or set of executables for supported systems.
- Current state: The user explicitly requested plug-and-play, mix-and-match, broad binary distribution. Module/component architecture was proposed but not accepted as final.
- Desired end state: Per-platform/per-architecture packages with stable executable cores and optional/static or dynamic backend modules selected by capability and policy.
- Importance: This is the long-term answer to compatibility, modding, portability, and extensibility.
- Decisions made: DECISION-18: Consider runtime modules/plugins/manifests for plug-and-play distribution
- Decisions pending: See related open questions and proposed decisions; do not treat proposals as accepted.
- Pending tasks: TASK-10: Decide static vs dynamic module strategy, TASK-11: Design module manifests and ABI/versioning
- Constraints: General APP0 authority and scope constraints apply.
- Dependencies: Actual repository files, build system, public APIs, and user confirmation where indicated.
- Timeline / sequencing: Verify repository first; then formalize boundaries; then design interfaces; then implement or prompt implementation.
- Blockers: Unverified code snapshot and unresolved design choices.
- Risks: See risk register.
- Artifacts: ARTIFACT-11: User request for smarter architecture and old snapshot integration, ARTIFACT-12: Assistant advanced runtime/module/framegraph/component architecture answer
- Success criteria: Must satisfy APP0 acceptance criteria and any later user-confirmed executable/window/distribution goals.
- Recommended next action: Proceed only after repository verification and boundary map are completed.
- Verification needed: VERIFY-04: Programming languages and ABI feasibility, VERIFY-13: Console SDK feasibility, VERIFY-17: Whether dynamic modules are acceptable for distribution, VERIFY-18: Exact intended binary distribution model
- Confidence: 4 / 5
- Carry-forward priority: high

### WORKSTREAM-10 — Old repository snapshot integration and verification

- Label: FACT
- Objective: Inspect the old code snapshot/project attachments and make future architecture/prompt work fit the actual codebase.
- Background: The user specifically asked to look at the old code snapshot in ChatGPT project attachments.
- Current state: User requested inspection. A prior assistant claimed to inspect it, but that claim is unverified in this visible chat and must not be relied on without re-checking.
- Desired end state: Verified repository inventory: actual tree, build system, languages, existing render/platform/client/server code, engine/game APIs, docs, and tests.
- Importance: Without verification, implementation prompts risk using wrong paths, wrong build assumptions, or invalid dependency boundaries.
- Decisions made: DECISION-11: Engine/game write access is not needed for APP0 if public boundaries already suffice, DECISION-20: Inspect old repo snapshot before repo-specific prompts
- Decisions pending: See related open questions and proposed decisions; do not treat proposals as accepted.
- Pending tasks: TASK-01: Inspect old code snapshot/project attachments, TASK-02: Verify actual top-level repo layout, TASK-03: Verify build system, languages, and toolchains, TASK-04: Verify engine/game public APIs
- Constraints: General APP0 authority and scope constraints apply.
- Dependencies: Actual repository files, build system, public APIs, and user confirmation where indicated.
- Timeline / sequencing: Verify repository first; then formalize boundaries; then design interfaces; then implement or prompt implementation.
- Blockers: Unverified code snapshot and unresolved design choices.
- Risks: See risk register.
- Artifacts: ARTIFACT-11: User request for smarter architecture and old snapshot integration, ARTIFACT-12: Assistant advanced runtime/module/framegraph/component architecture answer, ARTIFACT-16: Old code snapshot / project attachments
- Success criteria: Must satisfy APP0 acceptance criteria and any later user-confirmed executable/window/distribution goals.
- Recommended next action: Inspect old code snapshot and verify repository facts.
- Verification needed: VERIFY-01: Actual old repo snapshot/project attachments, VERIFY-02: Top-level directory tree and naming, VERIFY-03: Build system and presets
- Confidence: 5 / 5
- Carry-forward priority: critical

## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | User supplied APP0 prompt | Established runtime/application/platform/renderer scope and hard boundaries. | Defined the project fragment to preserve. | active | 5 |
| 2 | Assistant produced APP0 implementation pack | Expanded APP0 into possible Codex prompt with targets, docs, tests, CLI, CMake, commit plan. | Useful artifact but not final; later user asked to discuss first. | reference only | 5 |
| 3 | User requested discussion before prompts | Changed process from prompt generation to architectural discussion. | Prevents premature implementation planning. | active | 5 |
| 4 | Assistant critiqued APP0 | Identified missing mechanical enforcement, prediction, capability schema, sharding semantics, trust model. | Created design checklist. | active | 4 |
| 5 | User stated final macro-plan executable-window goal | Expanded desired outcome to real interactive resizable windows across platform/renderer combinations. | Introduced platform runtime necessity. | active | 5 |
| 6 | Assistant proposed platform runtime layer | Separated OS window/event/surface/time layer from renderer and engine. | Strong candidate architecture. | active | 4 |
| 7 | User granted write permissions | Allowed docs plus render/platform/application/client/server; asked if engine/game needed. | Defined implementation boundary. | active | 5 |
| 8 | Assistant answered engine/game not needed if boundaries suffice | Tentative answer requiring verification against actual code. | Must not be treated as proof. | active with caveat | 3 |
| 9 | User broadened renderer/platform question | Asked about D3D generations, Vulkan, GL generations, Metal, OSes, consoles, vendors, vintage systems. | Prompted broader taxonomy. | active | 5 |
| 10 | Assistant proposed renderer/platform taxonomy | Suggested API/backend families, translation backends, software/virtual paths, support classes, R0-R5 tiers. | Useful but not user-accepted as final. | proposal | 4 |
| 11 | User asked for smarter architecture and repo integration | Requested old snapshot inspection and maximum wisdom/modularity/packaging. | Shifted toward component/module architecture and repo-specific verification. | active | 5 |
| 12 | Assistant proposed advanced module/framegraph/component architecture | Suggested runtime framework, modules, render devices, framegraph, manifests, static core + dynamic modules. | Proposal; claimed repo inspection unverified. | proposal | 3 |
| 13 | User requested maximum-fidelity Context Transfer Packet | Asked for state transfer for new chat. | Produced previous transfer packet. | completed | 5 |
| 14 | User requested final downloadable report package | Asked to audit, normalize, repair, export Markdown/YAML/ZIP package for this chat only. | Current response creates package. | active/completed by this output | 5 |

## 7. Decisions

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | APP0 scope is application/runtime layer only | accepted / hard | User APP0 prompt | Prevents simulation/content/gameplay changes while building executables and platform support. | Future work should stay in render/platform/application/client/server/docs unless permission expands. | WORKSTREAM-01 | 5 | FACT |
| DECISION-02 | Applications are shells and orchestrators, not decision-makers | accepted / hard | User APP0 prompt | Keeps apps replaceable and optional around the simulation. | Apps host and orchestrate but do not own authoritative decisions. | WORKSTREAM-01 | 5 | FACT |
| DECISION-03 | Authoritative logic remains in engine + game | accepted / hard | User APP0 prompt | Protects simulation authority and prevents client/tool/runtime drift. | Engine/game are treated as authority black boxes for APP0. | WORKSTREAM-01 | 5 | FACT |
| DECISION-04 | Rendering never affects simulation | accepted / hard | User APP0 prompt | Required for determinism and authority boundaries. | Renderer timing/output must not influence sim state. | WORKSTREAM-04 | 5 | FACT |
| DECISION-05 | Client is non-authoritative | accepted / hard | User APP0 prompt | Avoids cheating/divergence and law bypass. | Prediction, if later added, must remain explicitly non-authoritative. | WORKSTREAM-02 | 5 | FACT |
| DECISION-06 | Server is authoritative and headless-capable | accepted / hard | User APP0 prompt | Enables dedicated servers, MMO scale, and AI-only autorun. | Server must not depend on renderer/windowing. | WORKSTREAM-03 | 5 | FACT |
| DECISION-07 | Launcher must not install content or mutate simulation state | accepted / hard | User APP0 prompt | Keeps launcher as session orchestrator only. | Setup owns installation; engine/server own authority. | WORKSTREAM-06 | 5 | FACT |
| DECISION-08 | Tools must obey authority/law and be auditable | accepted / hard | User APP0 prompt | Prevents inspectors/editors from becoming hidden god-mode paths. | Tool writes/elevation need explicit authorization and logging. | WORKSTREAM-08 | 5 | FACT |
| DECISION-09 | Discuss before generating more prompts | accepted at that time | User said: “First, let's discuss this before we plan or generate any prompts.” | User wanted architectural discussion before prompt generation. | Do not generate new Codex prompts until user asks. | WORKSTREAM-01 | 5 | FACT |
| DECISION-10 | Current write permission includes render, platform, application, client, server, and docs | accepted / current | User explicitly granted these areas. | Defines allowed modification areas for future implementation. | Avoid engine/game writes unless permission changes. | WORKSTREAM-01 | 5 | FACT |
| DECISION-11 | Engine/game write access is not needed for APP0 if public boundaries already suffice | tentative / unverified | Prior assistant answer; not verified against code. | APP0 should host existing authority rather than refactor it. | Must verify engine/game public APIs before relying on this. | WORKSTREAM-10 | 3 | UNCERTAIN / UNVERIFIED |
| DECISION-12 | Introduce or formalize a platform runtime layer | proposed / strong | Assistant proposal after user stated windowed executable goal. | Real windows require OS/window/event/surface abstraction separate from renderers. | Platform layer should own windows, events, resize, timing, surface handles. | WORKSTREAM-05 | 4 | INFERENCE |
| DECISION-13 | Renderers should not create windows | proposed / strong | Assistant proposal based on platform/render separation. | Avoids duplication and preserves portability/headless operation. | Renderers consume platform surface handles. | WORKSTREAM-04 | 4 | INFERENCE |
| DECISION-14 | Bring up null/software paths before GPU backends | proposed / strong | Assistant proposal during executable-window discussion. | Software validates windowing/presentation before GPU complexity. | First success state should be window clears/resizes/closes cleanly. | WORKSTREAM-02 | 4 | INFERENCE |
| DECISION-15 | Do not model renderers by GPU vendor | proposed / strong | Assistant renderer/platform taxonomy answer. | GPU vendors are adapter/driver metadata, not renderer APIs. | Use API/backend/capability descriptors instead. | WORKSTREAM-04 | 4 | INFERENCE |
| DECISION-16 | Use support classes: canonical, compatibility, experimental | proposed | Assistant renderer/platform taxonomy answer. | Prevents support matrix explosion. | Needs user confirmation before becoming formal spec. | WORKSTREAM-04 | 3 | INFERENCE |
| DECISION-17 | Use capability tiers R0–R5 for vintage/modern support | proposed | Assistant renderer/platform taxonomy answer. | Allows vintage systems to be described by capability rather than one-off nostalgia targets. | Needs user confirmation and mapping to real targets. | WORKSTREAM-04 | 3 | INFERENCE |
| DECISION-18 | Consider runtime modules/plugins/manifests for plug-and-play distribution | proposed | Assistant advanced architecture answer. | Addresses user desire for mix-and-match code and broad binaries. | Requires ABI/versioning/package design before implementation. | WORKSTREAM-09 | 3 | INFERENCE |
| DECISION-19 | Consider render device + framegraph architecture | proposed | Assistant advanced architecture answer. | Reduces backend duplication across D3D/Vulkan/Metal/GL/software. | Likely staged after minimal APP0 unless user elevates priority. | WORKSTREAM-04 | 3 | INFERENCE |
| DECISION-20 | Inspect old repo snapshot before repo-specific prompts | required next action | User asked to look at old snapshot; prior inspection claim unverified. | Prevents wrong paths/build assumptions. | Next assistant should verify actual files first. | WORKSTREAM-10 | 5 | FACT |

The highest-impact decisions are DECISION-01 through DECISION-10. They are direct APP0/user constraints and define the allowed scope, authority model, and current write boundaries. DECISION-11 is important but unverified: it says engine/game writes should not be needed for APP0 if adequate public APIs already exist. This must not be used as a factual claim until the code is inspected. DECISION-12 through DECISION-19 are architecture proposals, not finalized user decisions. They should guide discussion, not be inserted into a formal spec without confirmation.

## 8. Pending Tasks and Next Actions

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Inspect old code snapshot/project attachments | critical | immediate | future assistant | Access to attachments or files | Old repo archive/files | Verified repository inventory | Open and inspect the actual snapshot before planning implementation. | WORKSTREAM-10 | FACT | 5 |
| TASK-02 | Verify actual top-level repo layout | critical | immediate | future assistant | TASK-01 | Directory tree | FACT-based tree and naming map | Resolve app/apps/application and render/platform/client/server paths. | WORKSTREAM-10 | FACT | 5 |
| TASK-03 | Verify build system, languages, and toolchains | critical | immediate | future assistant | TASK-01 | Build files, source extensions, presets | Build constraints and implementation language assumptions | Locate CMake or other build definitions and compiler targets. | WORKSTREAM-10 | FACT | 5 |
| TASK-04 | Verify engine/game public APIs | critical | immediate | future assistant | TASK-01 | Headers/source/docs | Decision on whether APP0 can avoid engine/game writes | Find init/tick/shutdown/observer/read-only/public interfaces. | WORKSTREAM-10 | FACT | 5 |
| TASK-05 | Map current dependency graph | critical | high | future assistant | TASK-02,TASK-03 | Build files/includes/link targets | Boundary risk map | Identify current render/platform/app/client/server/engine/game dependencies. | WORKSTREAM-01 | INFERENCE | 4 |
| TASK-06 | Define authority/layer boundary map | critical | high | future assistant | TASK-05 | Verified repo graph | Allowed dependency and include rules | Draft explicit layer diagram and forbidden dependencies. | WORKSTREAM-01 | INFERENCE | 4 |
| TASK-07 | Define minimal platform runtime contract | critical | high | future assistant | TASK-06 | Windowing/presentation needs | Platform interface proposal | Specify window, event, resize, surface, time contracts. | WORKSTREAM-05 | INFERENCE | 4 |
| TASK-08 | Define renderer capability schema | critical | high | future assistant | TASK-07 | Backend inventory | Capability descriptor and selection model | Define API family, version, surface, feature tier, software/hardware/headless flags. | WORKSTREAM-04 | INFERENCE | 4 |
| TASK-09 | Define support classes and target matrix | high | high | user + assistant | TASK-08 | Target platform priorities | Canonical/compatibility/experimental matrix | Present support classes for user confirmation. | WORKSTREAM-04 | INFERENCE | 4 |
| TASK-10 | Decide static vs dynamic module strategy | high | high | user + assistant | TASK-03,TASK-08 | Distribution requirements | Module strategy decision | Compare static registration, dynamic plugins, and hybrid model. | WORKSTREAM-09 | INFERENCE | 4 |
| TASK-11 | Design module manifests and ABI/versioning | high | medium | future assistant | TASK-10 | Language/toolchain/package constraints | Stable module model draft | Define module identity, capabilities, version compatibility, loading rules. | WORKSTREAM-09 | INFERENCE | 3 |
| TASK-12 | Draft revised repo-specific APP0 architecture plan | high | medium | future assistant | TASK-01 through TASK-11 | Verified facts and decisions | Implementation sequence and boundaries | Produce plan before any Codex prompt. | WORKSTREAM-01 | INFERENCE | 4 |
| TASK-13 | Generate revised Codex implementation prompts only when requested | medium | blocked | future assistant | TASK-12 and user request | Architecture plan | Prompt set for implementation | Wait for explicit user request before prompt generation. | WORKSTREAM-01 | FACT | 5 |
| TASK-14 | Implement null/headless runtime smoke path | future | medium | implementation agent | TASK-12 | Repo code | Executable status path | Add or verify headless/null initialization paths. | WORKSTREAM-01 | INFERENCE | 3 |
| TASK-15 | Implement software renderer window path | future | medium | implementation agent | TASK-07,TASK-08,TASK-12 | Platform + render code | Resizable window clearing or blitting via software renderer | Build universal baseline before GPU backends. | WORKSTREAM-02 | INFERENCE | 3 |
| TASK-16 | Implement client presentation loop | future | medium | implementation agent | TASK-15 | Client/platform/render interfaces | Interactive resizable client executable | Add event pump, resize handling, close, frame loop. | WORKSTREAM-02 | INFERENCE | 3 |
| TASK-17 | Add renderer selection policy | future | medium | implementation agent | TASK-08,TASK-16 | Capability schema | auto/override renderer selection | Implement policy-driven backend selection. | WORKSTREAM-04 | INFERENCE | 3 |
| TASK-18 | Add GPU backends incrementally | future | medium | implementation agent | TASK-17 | SDKs/platform surfaces | D3D/VK/GL/Metal backends staged by platform | Start with one GPU backend after software success. | WORKSTREAM-04 | INFERENCE | 3 |
| TASK-19 | Define setup trust/integrity model | high | medium | user + assistant | TASK-10 | Package/content rules | Hash/signature/manifest/versioning model | Resolve before serious installer implementation. | WORKSTREAM-07 | INFERENCE | 4 |
| TASK-20 | Define tools elevation and audit model | high | medium | user + assistant | TASK-06 | Authority/law requirements | Tool authorization/audit policy | Resolve before write-capable editors/tools. | WORKSTREAM-08 | INFERENCE | 4 |
| TASK-21 | Define sharding semantics or explicitly label as plumbing only | medium | medium | user + assistant | Server architecture | Simulation/server requirements | Sharding policy or APP0 stub boundary | Avoid accidental MMO semantic assumptions. | WORKSTREAM-03 | INFERENCE | 4 |

### 8.1 Recommended Task Order

1. TASK-01 through TASK-04: inspect the snapshot, tree, build system, languages, and engine/game APIs.
2. TASK-05 and TASK-06: map dependency graph and formalize authority/layer boundaries.
3. TASK-07 and TASK-08: define platform runtime contract and renderer capability schema.
4. TASK-09 through TASK-11: decide support classes and module strategy.
5. TASK-12: produce a repo-specific APP0 architecture plan.
6. TASK-13: generate revised Codex prompts only if the user asks.
7. TASK-14 through TASK-18: implement in stages, starting with null/software/window path and only then GPU backends.
8. TASK-19 through TASK-21: resolve setup trust, tool audit/elevation, and server sharding semantics.

### 8.2 Blocked Tasks

TASK-12 and all implementation tasks are blocked on repository verification. TASK-13 is also blocked on explicit user request for prompt generation.

### 8.3 Quick Wins

- Create a verified directory tree inventory.
- Identify current build system and source languages.
- Search for renderer/window coupling.
- Search for server graphical dependencies.
- Compare existing docs against APP0 required docs.

### 8.4 Tasks Requiring Verification

TASK-01 through TASK-08 and TASK-17 through TASK-18 require direct code or external API verification before implementation.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Do not redesign simulation rules | scope | hard | User APP0 prompt | Runtime work must not change simulation behavior. | high | 5 | FACT |
| CONSTRAINT-02 | Do not alter content definitions | scope | hard | User APP0 prompt | APP0 should not modify game content/data definitions. | medium | 5 | FACT |
| CONSTRAINT-03 | Do not change life/civ/economy logic | scope | hard | User APP0 prompt | Keep life/civilization/economy logic out of runtime refactor. | high | 5 | FACT |
| CONSTRAINT-04 | Do not introduce gameplay shortcuts | scope | hard | User APP0 prompt | Avoid temporary client/server hacks that alter game behavior. | high | 5 | FACT |
| CONSTRAINT-05 | Applications are shells around the simulation | architecture | hard | User APP0 prompt | Apps orchestrate but do not decide authority. | medium | 5 | FACT |
| CONSTRAINT-06 | All authoritative logic remains in engine + game | architecture | hard | User APP0 prompt | Runtime layers must call into authority, not replace it. | high | 5 | FACT |
| CONSTRAINT-07 | Client must not simulate authoritative state | architecture/security | hard | User APP0 prompt | Client prediction, if any, must be non-authoritative. | high | 5 | FACT |
| CONSTRAINT-08 | Client must not bypass law or invent data | architecture/security | hard | User APP0 prompt | Client cannot forge state or ignore law systems. | high | 5 | FACT |
| CONSTRAINT-09 | Server must be authoritative and headless-capable | architecture | hard | User APP0 prompt | Server cannot depend on window/render paths. | high | 5 | FACT |
| CONSTRAINT-10 | Rendering never affects simulation | architecture | hard | User APP0 prompt | No render timing/output enters authoritative state. | high | 5 | FACT |
| CONSTRAINT-11 | Renderer selection must be capability-driven and policy-driven | architecture | hard | User APP0 prompt | Backend selection cannot be a hardcoded single path. | medium | 5 | FACT |
| CONSTRAINT-12 | Launcher must not alter simulation state or install content | architecture | hard | User APP0 prompt | Launcher is orchestration-only. | medium | 5 | FACT |
| CONSTRAINT-13 | Setup installs content/engine, manages versions, validates integrity | architecture | hard | User APP0 prompt | Setup owns installation/integrity workflows. | medium | 5 | FACT |
| CONSTRAINT-14 | Tools must use same authority rules and be auditable | architecture/security | hard | User APP0 prompt | Tools need authorization/audit; no silent bypass. | high | 5 | FACT |
| CONSTRAINT-15 | Current allowed write areas are render, platform, application, client, server, and docs | permission | hard/current | User follow-up | Future implementation should avoid engine/game writes unless permission changes. | high | 5 | FACT |
| CONSTRAINT-16 | Do not generate prompts before discussion unless user asks | process | hard/current | User follow-up | New assistant should continue discussion/verification first. | medium | 5 | FACT |
| CONSTRAINT-17 | This package covers this chat only | reporting | hard | User package request | Do not summarize entire project unless labelled PROJECT-CONTEXT. | medium | 5 | FACT |
| CONSTRAINT-18 | Important items must be labelled FACT, INFERENCE, UNCERTAIN / UNVERIFIED, or PROJECT-CONTEXT | reporting | hard | User package request | Future report aggregation should preserve epistemic status. | medium | 5 | FACT |
| CONSTRAINT-19 | Do not treat assistant suggestions as user decisions unless accepted | reporting/process | hard | User package request | Proposals remain tentative. | high | 5 | FACT |
| CONSTRAINT-20 | External-world/API/platform claims require future verification | evidence | hard | User package request | Prior API links should not be treated as current facts without re-checking. | medium | 5 | FACT |

### 9.2 Soft Preferences

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-21 | Start responses with model/date/time prefix | formatting | soft/hard per user preference | User profile/context | Future assistant should preserve the requested format when possible. | low | 4 | PROJECT-CONTEXT |

### 9.3 Technical Constraints

Technical constraints include keeping server headless, keeping rendering isolated from simulation, separating platform/window services from renderers, using capability/policy-based renderer selection, and avoiding engine/game writes under current permission.

### 9.4 Time / Resource Constraints

No explicit timeline or resource budget was established in this chat.

### 9.5 Legal / Ethical / Safety Constraints

Console support was mentioned but not scoped. Console SDKs and platform-specific requirements are not verified and should be treated as private/proprietary adapter territory until confirmed.

### 9.6 Evidence / Citation Requirements

External-world facts about APIs, products, software support, OS support, legal requirements, or current platform capabilities require future verification before use.

### 9.7 Formatting / Output Requirements

This package itself must use Markdown/YAML files, stable IDs, and epistemic labels. The user also has a PROJECT-CONTEXT preference for model/date/time prefixes.

### 9.8 Things to Avoid

Avoid prompt generation before verification, engine/game edits without permission, renderer-created windows, GPU-first bring-up, GPU-vendor renderer families, unbounded vintage promises, flat support matrices, launcher installing content, and tools bypassing law.

## 10. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | What is the actual current repository structure? | Architecture and prompts must match real paths. | Prior assistant claimed a tree; user referenced old snapshot. | Actual files were not inspected in this visible chat. | Inspect project attachments/repo snapshot. | critical | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Is the canonical application directory app, apps, or application? | Implementation prompts and permissions use different names. | APP0 implementation pack used apps; user granted application; prior claimed snapshot had app. | Actual tree and intended naming. | Inspect repo and ask user if needed. | critical | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | What build system and languages does the repo use? | CMake/C/C++ assumptions may be wrong. | Prior prompt assumed CMake and C/C++ style examples. | Actual build system/languages/toolchains. | Inspect root build files and source extensions. | critical | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | Do engine/game expose stable public host APIs? | Determines whether APP0 can avoid engine/game writes. | Assistant said engine/game writes unnecessary if boundaries exist. | Actual init/tick/shutdown/observer APIs. | Inspect headers/source/docs. | critical | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Do null/software/hardware renderers already exist in code? | Avoid duplicating/refactoring wrong abstractions. | User said Dominium has null/software and hardware renderers, but code status unverified. | Actual render implementation status. | Inspect render code. | critical | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Does a platform layer already exist? | Determines whether to introduce, formalize, or refactor platform runtime. | User granted platform; assistant proposed missing layer. | Actual platform code and responsibilities. | Inspect platform directory. | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Should modules be dynamic plugins, static registrations, or hybrid? | Affects distribution, ABI, build complexity, and compatibility. | User wants plug-and-play; assistant proposed dynamic modules. | User has not accepted a specific strategy. | Analyze repo/toolchains and present tradeoffs. | high | WORKSTREAM-09 | INFERENCE |
| QUESTION-08 | What is the module ABI/versioning policy? | Needed for long-term plugin compatibility. | Module manifests proposed. | No ABI decision exists. | Design after language/build verification. | high | WORKSTREAM-09 | INFERENCE |
| QUESTION-09 | Which platforms are canonical, compatibility, or experimental? | Testing and support matrix must be bounded. | Windows/Linux/macOS/headless are APP0; consoles/vintage were asked about. | Exact platform versions/architectures unclear. | User confirmation and code feasibility analysis. | high | WORKSTREAM-04 | INFERENCE |
| QUESTION-10 | Which renderers are canonical vs compatibility vs experimental? | Prevents renderer support explosion. | D3D/VK/GL/Metal/software/null discussed. | Priority and exact versions undecided. | Create matrix for user confirmation. | high | WORKSTREAM-04 | INFERENCE |
| QUESTION-11 | What is the vintage support policy? | Vintage systems can consume unlimited effort. | Capability tiers R0–R5 proposed. | Actual target vintage systems unknown. | User decision after matrix proposal. | medium | WORKSTREAM-04 | INFERENCE |
| QUESTION-12 | Are consoles in near-term scope or architecture-only? | Console SDKs require private adapters and legal constraints. | Xbox/PlayStation/Nintendo Switch mentioned by user. | SDK access and target priority unknown. | Ask user or mark experimental/private. | medium | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | What is the setup trust/integrity model? | Installer and multiplayer trust depend on it. | Setup must validate integrity. | Hash/signature/manifest/network trust unspecified. | Design trust model. | high | WORKSTREAM-07 | INFERENCE |
| QUESTION-14 | What is the tools authorization/elevation model? | Tools must obey law yet may need write/edit powers. | APP0 says tools must be auditable and lawful. | How to authorize elevated tool actions. | Design policy with user. | high | WORKSTREAM-08 | INFERENCE |
| QUESTION-15 | What are sharding semantics? | Server MMO design depends on shard model. | APP0 says server supports sharding. | Spatial/logical/temporal/jurisdictional semantics unknown. | Label APP0 as plumbing or design later. | medium | WORKSTREAM-03 | INFERENCE |
| QUESTION-16 | Is client-side prediction or rollback planned? | Client architecture may need simulation-adjacent code. | Client cannot be authoritative. | Prediction/rollback location and authority rules unknown. | Defer or explicitly reserve layer. | medium | WORKSTREAM-02 | INFERENCE |
| QUESTION-17 | What shader/pipeline abstraction should be used? | Cross-renderer duplication depends on it. | Shader IR/framegraph proposed. | Actual rendering needs/toolchains unknown. | Render architecture design after repo inspection. | medium | WORKSTREAM-04 | INFERENCE |
| QUESTION-18 | What asset/data pipeline exists? | Platform variants and mods may need compiled assets. | Data/schema directories were claimed but unverified. | Actual asset/data pipeline unknown. | Inspect repo. | medium | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Generate more prompts immediately | rejected / superseded by discussion | User explicitly asked to discuss before planning/generating prompts. | final until user asks for prompts | When user explicitly requests prompt generation. | WORKSTREAM-01 | FACT |
| REJECTED-02 | Let renderer backends create windows | rejected by architecture proposal | Would couple render APIs to OS windowing and break portability/headless separation. | strong but pending formal acceptance | Only for throwaway prototype, not architecture. | WORKSTREAM-04 | INFERENCE |
| REJECTED-03 | Start with GPU renderer before platform/software baseline | deprioritized | GPU complexity would obscure window/event/presentation bugs. | strong but pending formal acceptance | After null/software window path works. | WORKSTREAM-02 | INFERENCE |
| REJECTED-04 | Model renderers by GPU vendor | rejected by assistant proposal | Intel/AMD/NVIDIA are vendors/adapters/drivers, not renderer APIs. | strong | Only use vendor metadata for profiling/workarounds/extensions. | WORKSTREAM-04 | INFERENCE |
| REJECTED-05 | Promise every vintage system individually | rejected by assistant proposal | Creates unbounded compatibility burden. | tentative | Use capability tiers instead. | WORKSTREAM-04 | INFERENCE |
| REJECTED-06 | Flat OS × renderer × vendor support matrix | rejected by assistant proposal | Combinatorial explosion. | tentative | Use descriptors, capability tiers, and support classes. | WORKSTREAM-04 | INFERENCE |
| REJECTED-07 | Launcher installs content | rejected by APP0 | APP0 says launcher must not install content itself. | final unless user changes architecture | Never under current APP0. | WORKSTREAM-06 | FACT |
| REJECTED-08 | Tools bypass law because they are development utilities | rejected by APP0 | APP0 says tools must use same authority rules, never bypass law, and be auditable. | final unless user changes architecture | Use explicit logged elevation instead. | WORKSTREAM-08 | FACT |
| REJECTED-09 | Treat prior assistant repo-inspection claim as reliable | rejected for package purposes | The current visible chat cannot verify the claimed snapshot inspection. | final until actual files are inspected | Reconsider after direct file verification. | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| REJECTED-10 | Assume engine/game edits are impossible forever | rejected as overstatement | Current permission excludes them, but future user permission could change if APIs are insufficient. | final as current-scope constraint only | Reconsider after repo verification and user approval. | WORKSTREAM-01 | INFERENCE |

Preserving rejected and deprioritised options prevents future assistants from repeating earlier mistakes: generating prompts too early, coupling windows to renderers, building GPU backends before a software baseline, modelling renderers by vendor, overpromising vintage systems, or treating tools as god-mode.

## 12. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | User APP0 prompt: Runtimes, Applications, Platforms & Renderers | prompt | Defines APP0 scope, responsibilities, constraints, docs, and acceptance criteria. | primary source | User | yes | Preserve exact key wording; this is the root artifact. | FACT |
| ARTIFACT-02 | Assistant APP0 implementation pack | generated prompt/output | Expanded APP0 into possible Codex implementation plan with targets, CLI flags, CMake options, docs, tests, commit plan. | not accepted as final | Assistant | yes, with caution | Use only after repo-specific repair; it used apps/ while user later granted application/. | FACT |
| ARTIFACT-03 | User process correction: discuss before prompts | chat statement | Changed direction away from immediate prompt generation. | accepted process constraint | User | yes | Exact wording: “First, let's discuss this before we plan or generate any prompts.” | FACT |
| ARTIFACT-04 | Assistant APP0 conceptual critique | analysis/output | Identified missing enforcement, prediction policy, renderer capability schema, sharding semantics, setup trust model. | proposal/critique | Assistant | yes | Useful design checklist, not all decisions. | FACT |
| ARTIFACT-05 | User executable-window goal | chat statement | Expanded final macro-plan target to real interactive resizable windows per platform/renderer combo. | active goal | User | yes | Drives need for platform runtime and software renderer path. | FACT |
| ARTIFACT-06 | Assistant platform runtime proposal | architecture proposal | Introduced platform layer for windows/events/surfaces/timing separate from rendering. | proposal | Assistant | yes | Strong candidate architecture; verify existing platform code first. | INFERENCE |
| ARTIFACT-07 | User write-permission statement | chat statement | Granted write access to render, platform, application, client, server, and docs. | active constraint | User | yes | Engine/game not granted. | FACT |
| ARTIFACT-08 | Assistant engine/game permission answer | analysis/output | Said APP0 does not require engine/game writes if public boundaries suffice. | tentative/unverified | Assistant | yes, with warning | Must verify actual engine/game APIs. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-09 | User renderer/platform/vintage/consoles question | chat statement | Asked about D3D7/9/11/12, Vulkan, GL1-4, Metal, Windows/Linux/macOS/PC/Mac/consoles/vendors/vintage systems. | active architecture prompt | User | yes | Sets broad compatibility/modularity concern. | FACT |
| ARTIFACT-10 | Assistant renderer/platform taxonomy answer | architecture proposal | Proposed backend families, translation backends, software/virtual backends, platform tiers, support classes, vintage R0-R5 tiers. | proposal | Assistant | yes | Requires verification/user confirmation before spec formalization. | INFERENCE |
| ARTIFACT-11 | User request for smarter architecture and old snapshot integration | chat statement | Asked whether design is best possible and requested inspection of old code snapshot/project attachments. | active requirement | User | yes | Triggers TASK-01. | FACT |
| ARTIFACT-12 | Assistant advanced runtime/module/framegraph/component architecture answer | architecture proposal | Proposed runtime framework, modules, render devices, framegraph, module manifests, capability negotiation, DCM. | proposal; repo-inspection claim unverified | Assistant | yes, with caution | Do not treat claimed repo tree as fact until verified. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-13 | Previously generated Context Transfer Packet | handoff text | Maximum-fidelity transfer packet summarizing the chat before final package generation. | source for this package | Assistant | yes | This package repairs/normalizes it. | FACT |
| ARTIFACT-14 | Current final report package | generated files | Downloadable Markdown/YAML/ZIP package for this old chat. | created by current response | Assistant | yes | Includes report, spec sheet, aggregator packet, registers, brief, audit, manifest. | FACT |
| ARTIFACT-15 | Prior external reference links about graphics APIs/tools | links/references | Links cited in prior assistant answer for D3D12, WebGPU, ANGLE, MoltenVK, Zink, WARP, SwiftShader, Mesa, Vulkan, SDL. | unverified in this package | Assistant | optional | External API/platform facts require future web verification. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-16 | Old code snapshot / project attachments | file/source to inspect | Actual repo state needed for integration. | not inspected in this package | User/project attachments | yes | Critical verification target. | UNCERTAIN / UNVERIFIED |

## 13. Rationale and Assumptions

The visible rationale behind the major choices is preservation of authority, portability, and long-term modularity. APP0’s authority rule exists because clients, launchers, setup tools, renderers, and development tools can otherwise become hidden paths for simulation mutation. The platform/runtime split was proposed because a real windowed executable requires OS event loops and surface handles, which should not be owned by rendering APIs. The null/software-first path was proposed because it validates platform, presentation, and event-loop behavior before GPU-specific complexity.

The renderer taxonomy was proposed to avoid the OS/API/vendor matrix explosion. Backend families should be described by API and capabilities rather than by GPU vendor. Support classes and R0–R5 tiers are visible attempts to handle modern, legacy, vintage, and experimental targets without promising every combination equally.

The module/component architecture was proposed to satisfy the user’s plug-and-play distribution goal. However, it assumes that the language/build system can support stable interfaces or plugin boundaries and that the user accepts the complexity. This must be verified before it becomes implementation law.

The largest stale or unverified assumption is that the old repo snapshot has the structure previously claimed by a prior assistant. This package intentionally does not rely on that claim.

## 14. Risks and Failure Modes

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Repo hallucination or stale snapshot assumption | Bad architecture/prompt paths and invalid implementation steps. | medium | high | Inspect actual attachments before repo-specific claims. | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| RISK-02 | Treating assistant proposals as accepted decisions | Future spec could overstate tentative architecture. | medium | high | Preserve labels and request user confirmation for proposed items. | WORKSTREAM-01 | FACT |
| RISK-03 | Authority leakage into client/tools/runtime | Could corrupt simulation, law, anti-cheat, or determinism. | medium | critical | Hard dependency boundaries, audit/elevation model, no sim authority in apps. | WORKSTREAM-01 | FACT |
| RISK-04 | Renderer/window coupling | Would duplicate code and harm platform portability. | medium | high | Platform owns windows/surfaces/events; renderers consume surfaces. | WORKSTREAM-04 | INFERENCE |
| RISK-05 | GPU-backend-first complexity | Slow progress and hard-to-debug startup failures. | medium | medium | Bring up null/software/window path first. | WORKSTREAM-02 | INFERENCE |
| RISK-06 | Support matrix explosion | Unbounded OS/API/vendor/vintage/console combinations. | high | high | Use support classes, capability tiers, descriptors, and policy selection. | WORKSTREAM-04 | INFERENCE |
| RISK-07 | Plugin ABI instability | Dynamic modules may break across versions. | medium | high | Versioned manifests, stable C ABI or explicit compatibility policy. | WORKSTREAM-09 | INFERENCE |
| RISK-08 | Overpromising vintage/consoles | Legal/toolchain/SDK limitations may be ignored. | medium | high | Mark vintage/console as compatibility or experimental until verified. | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| RISK-09 | Setup trust model gap | Content/version integrity may be weak or inconsistent. | medium | high | Define hashes/signatures/manifests and repair semantics. | WORKSTREAM-07 | INFERENCE |
| RISK-10 | Tool god-mode shortcuts | Editors/inspectors could bypass law. | medium | high | Require authorization and auditable logs. | WORKSTREAM-08 | FACT |
| RISK-11 | Engine/game public API insufficiency | APP0 may be blocked without engine/game permission. | unknown | high | Verify APIs; ask user before expanding permissions. | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| RISK-12 | Package summarization loss | Future assistant may miss nuanced constraints or tentative status. | medium | medium | Use this package’s stable IDs and labels. | WORKSTREAM-01 | FACT |
| RISK-13 | External API/platform fact staleness | Graphics/toolchain facts can change. | medium | medium | Reverify external links and API support before implementation. | WORKSTREAM-04 | FACT |
| RISK-14 | Launcher/setup responsibility confusion | Launcher may accidentally install or mutate content. | low | medium | Keep launcher orchestration-only and setup install-only. | WORKSTREAM-06 | FACT |
| RISK-15 | Sharding ambiguity | Server hooks may imply semantics not yet chosen. | medium | medium | Label APP0 sharding as plumbing unless semantics are explicitly designed. | WORKSTREAM-03 | INFERENCE |

## 15. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Actual old repo snapshot/project attachments | Needed because user asked to integrate with old code and prior assistant inspection is unverified. | Direct file/attachment inspection | critical | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Top-level directory tree and naming | Must resolve app/apps/application mismatch. | Filesystem tree | critical | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Build system and presets | CMake and target assumptions are unverified. | Build files and CI config | critical | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Programming languages and ABI feasibility | Module/plugin strategy depends on language/toolchain. | Source extensions and compiler config | critical | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Engine/game public APIs | Determines whether engine/game writes are avoidable. | Headers/source/docs | critical | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Existing renderers and renderer ownership of windows | Determines refactor scope and coupling. | render directory/source search | critical | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Existing platform layer responsibilities | Determines whether to introduce or refactor platform runtime. | platform directory/source search | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Client/server current dependencies | Need detect authority/render/platform coupling. | Build graph/include graph | critical | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Whether server currently depends on graphics/window code | Server must be headless. | Build/link dependency inspection | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Current docs/app content | Avoid duplicating or contradicting existing docs. | docs directory inspection | medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Existing tests and smoke paths | Needed for APP0 acceptance/testing. | tests/CI inspection | medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | External graphics API/backend facts | Prior citations may be stale. | Official API/vendor/project docs via web | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Console SDK feasibility | Console support requires special access and constraints. | User confirmation and SDK/legal status | medium | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Vintage target list | Capability tiers need mapping to actual desired vintage systems. | User confirmation | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | Setup trust model requirements | Security/integrity semantics unresolved. | User/design discussion | high | WORKSTREAM-07 | INFERENCE |
| VERIFY-16 | Tools law/elevation model | Tools must be lawful and auditable but write behavior is unspecified. | User/design discussion | high | WORKSTREAM-08 | INFERENCE |
| VERIFY-17 | Whether dynamic modules are acceptable for distribution | Plugin loading may be complicated by platforms/consoles/security. | User/design discussion and toolchain review | high | WORKSTREAM-09 | INFERENCE |
| VERIFY-18 | Exact intended binary distribution model | User wants same executable or set, but packaging details are open. | User confirmation | high | WORKSTREAM-09 | FACT |

## 16. Spec Book Contribution Notes

| Likely chapter / section | Unique contribution from this chat | Status |
|---|---|---|
| Spec section: Application/runtime architecture | APP0 application/client/server/launcher/setup/tools boundaries and philosophy | formal requirement candidates |
| Spec section: Authority boundaries | Engine/game authority, client/tool/server constraints, law/audit rules | formal requirement candidates |
| Spec section: Platform runtime | Window/event/surface/time layer separate from renderer | needs verification and user confirmation |
| Spec section: Renderer architecture | Null/software/GPU/translation/software-virtual backend taxonomy, capability tiers, selection policy | proposal to refine |
| Spec section: Distribution and modules | Static core plus dynamic or hybrid module model, manifests, capability negotiation | proposal to refine |
| Spec section: Tooling governance | Tools obey authority/law and audit actions | formal requirement candidate |
| Spec section: Setup/trust/integrity | Install/version/verify/repair responsibilities and open trust model | requires design |
| Spec section: Server runtime | Headless authoritative server, AI-only autorun, sharding hooks | formal requirement candidates with open sharding semantics |

Formal requirement candidates from this chat include APP0 authority boundaries, application responsibilities, server headless authority, launcher/setup separation, tool audit/law constraints, and rendering isolation. Items that should remain proposals until confirmed include dynamic modules, framegraph, shader IR, R0–R5 tiers, and canonical/compatibility/experimental support classes. Items that need verification include all repo-specific structure, current code, existing APIs, and external API/platform details.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | APP0 is runtime/application/platform/render only | scope | Prevents simulation/gameplay drift | Future assistant may modify engine/game rules | FACT | 5 |
| 2 | Engine + game remain authoritative | authority | Core Dominium boundary | Authority leakage | FACT | 5 |
| 3 | Applications are orchestrators, not decision-makers | architecture | Keeps apps replaceable | Runtime logic could become gameplay logic | FACT | 5 |
| 4 | Rendering never affects simulation | architecture | Determinism and correctness | Render timing could influence sim | FACT | 5 |
| 5 | Server is authoritative and headless-capable | server | Dedicated/MMO/AI autorun support | Server could depend on graphics | FACT | 5 |
| 6 | Client is non-authoritative | client | Security and law boundary | Cheating/divergence | FACT | 5 |
| 7 | Launcher must not install or mutate simulation | launcher | Separation of concerns | Launcher/setup confusion | FACT | 5 |
| 8 | Tools must obey law and be auditable | tools | No hidden god-mode | Tool corruption of state | FACT | 5 |
| 9 | Current write access excludes engine/game | permission | Implementation boundary | Unauthorized edits | FACT | 5 |
| 10 | Real interactive resizable window is desired macro-plan end state | goal | Drives platform/runtime design | Stubs may be mistaken for enough | FACT | 5 |
| 11 | Inspect old code snapshot before repo-specific prompts | process | Avoids hallucinated paths | Bad implementation prompt | FACT | 5 |
| 12 | Prior repo-inspection claim is unverified | uncertainty | Avoid false facts | Wrong tree/build assumptions | UNCERTAIN / UNVERIFIED | 5 |
| 13 | Platform and renderer should be separate | architecture proposal | Portability/headless support | Renderer-window coupling | INFERENCE | 4 |
| 14 | Null/software path before GPU backends | sequencing proposal | Faster reliable bring-up | GPU-first complexity | INFERENCE | 4 |
| 15 | Do not model renderers by GPU vendor | architecture proposal | Avoids duplication | Vendor-matrix explosion | INFERENCE | 4 |
| 16 | Module/plugin architecture is proposed, not decided | status | Avoids overcommitting | Spec may include unaccepted complexity | INFERENCE | 3 |
| 17 | Support classes and R0–R5 tiers are proposed, not decided | status | Avoids overclaiming support | Overpromised platforms | INFERENCE | 3 |
| 18 | External graphics/API facts require re-verification | evidence | APIs and support change | Stale specs | FACT | 5 |

## 18. What Future Assistants Must Not Assume

- Do not assume the old repository tree claimed by the prior assistant is accurate.
- Do not assume CMake is the actual build system until verified.
- Do not assume the code is C or C++ until verified.
- Do not assume `apps/`, `app/`, or `application/` is canonical until verified.
- Do not assume engine/game APIs are adequate until inspected.
- Do not assume engine/game edits are permitted.
- Do not assume dynamic plugins are accepted.
- Do not assume framegraph or shader IR is required for APP0.
- Do not assume all renderer/platform/vintage/consoles are canonical support targets.
- Do not assume external API support details are current.
- Do not assume tools may bypass law.
- Do not assume prompt generation is desired before user asks.

## 19. Recommended Next Action

If continuing this chat’s work alone: inspect the old code snapshot/project attachments and produce a verified repository inventory with labels.

If aggregating this chat with other chat reports: preserve this package as the APP0/runtime-platform-renderer architecture source, but mark module/framegraph/support-tier ideas as proposals until cross-chat evidence or user confirmation supports them.

User verification needed before acting: confirm whether the next step should be repository inspection, architecture refinement, or prompt generation after inspection.

## 20. Appendix: Possibly Relevant Details

### A. Exact APP0 title and intent

```text
PROMPT APP0 — RUNTIMES, APPLICATIONS, PLATFORMS & RENDERERS
TARGET: GPT-5.2 CODEX
SCOPE: ENGINE / CLIENT / SERVER / LAUNCHER / SETUP / RENDERERS
INTENT: BUILD EXECUTABLES AND PLATFORM SUPPORT CORRECTLY
```

### B. APP0 hard prohibitions

```text
You MUST NOT:
- redesign simulation rules
- alter content definitions
- change life/civ/economy logic
- introduce gameplay shortcuts
```

### C. APP0 application philosophy

```text
Applications are:
- shells around the simulation
- orchestrators, not decision-makers
- replaceable and optional

All authoritative logic remains in engine + game.
```

### D. APP0 docs required

```text
docs/app/
- CLIENT.md
- SERVER.md
- RENDERERS.md
- LAUNCHER.md
- SETUP.md
- TOOLS.md
- PLATFORM_SUPPORT.md
```

### E. Prior platform contract proposal

```text
platform_init()
platform_shutdown()

platform_window_create(params)
platform_window_destroy(handle)

platform_window_poll_events()
platform_window_get_size()
platform_window_should_close()

platform_get_draw_surface()
platform_get_time_ns()
```

### F. Prior advanced module manifest example

```json
{
  "type": "render_device",
  "api": "vulkan",
  "tier": 5,
  "platforms": ["windows", "linux"],
  "priority": 100
}
```

### G. Prior capability tiers proposal

| Tier | Meaning |
|---|---|
| R0 | null/headless |
| R1 | pure software |
| R2 | fixed-function GL1/D3D7-class |
| R3 | programmable basic D3D9/GL2/GLES2-class |
| R4 | modern baseline D3D11/GL3/Vulkan 1.0/Metal 2-class |
| R5 | advanced modern D3D12/Vulkan 1.2+/Metal 3-class |
