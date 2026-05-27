# Registers — Dominium APP0 Runtime, Platform, and Renderer Architecture

## 1. Workstream Register

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

## 2. Decision Register

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

## 3. Task Register

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

## 4. Constraint Register

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
| CONSTRAINT-21 | Start responses with model/date/time prefix | formatting | soft/hard per user preference | User profile/context | Future assistant should preserve the requested format when possible. | low | 4 | PROJECT-CONTEXT |

## 5. User Preference Register

| ID | Preference | Category | Source basis | Strength | Implication | Risk | Label |
|---|---|---|---|---|---|---|---|
| PREFERENCE-01 | Prefer maximum-fidelity state transfer over normal summaries | explicit | User requested maximum-fidelity Context Transfer Packet and final package | strong | Preserve details, uncertainty, registers, artifacts, and next actions. | Lossy summaries would force re-explanation. | FACT |
| PREFERENCE-02 | Prefer discussion before prompt generation | explicit | User said to discuss before planning or generating prompts | strong | Do not jump to Codex prompts without explicit request. | Premature prompt generation may misalign architecture. | FACT |
| PREFERENCE-03 | Prefer robust, modular, extensible architecture | explicit | User asked for intelligent, intuitive, robust, compatible, optimized, moddable, modular, extensible design | strong | Evaluate designs by long-term maintainability and plug-and-play capability. | Overly minimal scaffolds may be insufficient. | FACT |
| PREFERENCE-04 | Prefer plug-and-play and mix-and-match code/data | explicit | User wants to mix and match code without rewriting or duplication | strong | Use interfaces, modules, capability descriptors, and shared code paths. | Monolithic designs would conflict with goal. | FACT |
| PREFERENCE-05 | Prefer broad binary/platform/renderer distribution | explicit | User wants same executable or set of executables across supported systems | strong | Design packaging/modules/selection for breadth. | Naive per-combination binaries may cause matrix explosion. | FACT |
| PREFERENCE-06 | Prefer epistemic labels and no invented facts | explicit | User package prompt and prior preferences | strong | Use FACT/INFERENCE/UNCERTAIN labels and avoid unsupported claims. | Overconfidence damages future aggregation. | FACT |
| PREFERENCE-07 | Interested in computer science and rigorous facts | project-context | User profile outside visible chat | medium | Technical depth and rigor are appropriate. | Should not overfit if not relevant. | PROJECT-CONTEXT |
| PREFERENCE-08 | Wants response prefix with model and timestamp | project-context | User profile outside visible chat | medium | Prefix final responses accordingly. | May be omitted by future assistants if system conflicts. | PROJECT-CONTEXT |

## 6. Open Questions Register

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

## 7. Artifact Ledger

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

## 8. Rejected / Superseded Options Register

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

## 9. Risk Register

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

## 10. Verification Queue

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

## 11. Timeline Register

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

## 12. Spec Book Contribution Register

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
