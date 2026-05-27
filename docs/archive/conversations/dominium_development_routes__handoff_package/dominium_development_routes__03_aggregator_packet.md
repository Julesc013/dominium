# Aggregator Packet — Dominium Development Routes

## 1. Packet Metadata

* Chat label: Dominium Development Routes
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only; Project-level context labelled PROJECT-CONTEXT where used.
* Coverage: Full for visible transcript; partial/unclear for wider project.
* Confidence: 4/5
* Staleness risk: Low for chat facts; medium for external technical claims if reused.
* Merge priority: High for architecture philosophy; medium for implementation details.
* Main limitations: Very short project transcript; most technical content is assistant proposal; no code/files/engine/genre/timeline visible.

## 2. Ultra-Condensed Carry-Forward Capsule

This packet represents one short but important Dominium planning chat. It should be merged into the future Project Spec Book as a source about early technical development philosophy and component sequencing, not as a confirmed full project design. The chat’s main substantive topic was a user question asking what usual development routes apply to games like Dominium and what specific components should be worked on in which order. The prior assistant answered by proposing a route comparison and recommending a kernel-first deterministic simulation approach.

The central carry-forward item is the prior assistant’s proposal of “Route C — Kernel-First Deterministic Simulation.” This was contrasted with Route A — Content-First and Route B — Engine-First. Route A was described as fast but debt-prone. Route B was described as structurally strong but expensive and slow. Route C was proposed as a minimal deterministic simulation kernel followed by strict layering, tools, content, and scale. The exact proposal-level principle was: “Simulation precedes representation. State precedes UI. Determinism precedes performance. Data precedes content.” That sentence is the strongest compact summary of the technical philosophy from this chat.

The proposed architecture stack was: [0] Mathematical & Temporal Primitives, [1] Deterministic Simulation Kernel, [2] World Model & State Graph, [3] Systems, [4] Persistence/Replay/Sync, [5] Tooling & Introspection, [6] Presentation, [7] Content & Scenarios, [8] Distribution/Modding/Multiplayer. The proposed early tasks included fixed-point or deterministic math, time model, RNG stream partitioning, serialization primitives, tick loop, event queue, mutation rules, entity IDs/lifetimes, spatial/world graph, resources/conservation, population, economy, governance, conflict, environment, replay, save/load, debug inspectors, and later UI/content/modding/multiplayer.

The aggregator must not treat these as accepted requirements. They are prior assistant proposals. The user has not visibly confirmed Route C, strict determinism, fixed-point math, modding, multiplayer, engine choice, project scale, genre, core loop, target platforms, or implementation state. The only user-confirmed project-level need in the visible chat is that Dominium needs guidance on development routes and component order. The current user-confirmed process need is that this old chat should be packaged into reusable files for later aggregation.

The strongest next action for a future continuation assistant is to produce a Dominium Technical Roadmap v0.1 that converts the proposal into a phase-gated plan while keeping all assumptions explicit. The first verification gates should be: confirm whether Dominium is simulation-heavy, whether Route C is accepted, what the core player loop is, what deterministic replay target is required, what platforms and engine/language constraints exist, whether modding and multiplayer are real goals, and whether external files or repositories exist.

For master-spec integration, this chat should feed chapters on development philosophy, simulation kernel, deterministic replay, world model, tool-first development, presentation boundary, data/content strategy, and early risk management. It should not be merged into final requirements without corroboration from other chats or user confirmation. The aggregator should preserve the tentative status of all route and architecture recommendations, preserve rejected options as tentative assistant warnings, and mark all external game-development claims as requiring verification before use.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Route C — Kernel-First Deterministic Simulation is proposed, not confirmed. | Development route | DECISION-03 | Controls technical sequencing if accepted. | FACT about prior output; UNCERTAIN as decision | 5/5 prior output; 2/5 acceptance |
| 2 | Exact ordering principle must be preserved. | Architecture principle | DECISION-05 | Encodes the rationale for simulation-first planning. | FACT about prior output | 5/5 |
| 3 | Layer stack [0]–[8] is the main technical artifact. | Architecture stack | ARTIFACT-05 | Gives future roadmap skeleton. | FACT about prior output | 5/5 |
| 4 | Feature completion rule is proposal-level. | Quality gate | DECISION-06 | Could become acceptance criteria but modding is unconfirmed. | FACT about prior output; UNCERTAIN as requirement | 5/5 / 2/5 acceptance |
| 5 | No genre, engine, codebase, files, or timeline are visible. | Unknowns | QUESTION-02, QUESTION-05, QUESTION-13, QUESTION-14 | Prevents false project state. | FACT | 5/5 |
| 6 | Future first action: Dominium Technical Roadmap v0.1. | Next action | TASK-03 | Turns proposal into actionable plan with caveats. | INFERENCE | 4/5 |
| 7 | Future aggregation must preserve provenance and wait for all packages. | Aggregation process | DECISION-09 | Prevents premature master spec. | FACT | 5/5 |

## 4. Workstream Summaries

### WORKSTREAM-01 — Dominium technical development route and component ordering

* ID: WORKSTREAM-01
* Name: Dominium technical development route and component ordering
* Objective: Determine usual technical/feature development routes for games like Dominium and identify components to work on in order.
* Current state: A prior assistant proposed a kernel-first deterministic simulation route and a layered phase order. The user has not visibly accepted or rejected the proposal.
* Desired end state: A confirmed Dominium technical roadmap with components, dependencies, phase gates, acceptance tests, and unresolved decisions clearly marked.
* Priority: high
* Decisions: DECISION-03, DECISION-04, DECISION-05, DECISION-06
* Tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05, TASK-06, TASK-07, TASK-08, TASK-09, TASK-10, TASK-11, TASK-12, TASK-13, TASK-14, TASK-15, TASK-16, TASK-17
* Constraints: CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-11, CONSTRAINT-12, CONSTRAINT-13, CONSTRAINT-14, CONSTRAINT-15, CONSTRAINT-16, CONSTRAINT-17, CONSTRAINT-18, CONSTRAINT-19, CONSTRAINT-20, CONSTRAINT-21
* Artifacts: ARTIFACT-01, ARTIFACT-02, ARTIFACT-04, ARTIFACT-05, ARTIFACT-06
* Risks: RISK-01, RISK-02, RISK-03, RISK-04, RISK-05, RISK-06, RISK-07
* Open questions: QUESTION-01, QUESTION-02, QUESTION-03, QUESTION-04, QUESTION-05
* Next action: Create Dominium Technical Roadmap v0.1 from the proposal, explicitly marking assumptions and open questions.

### WORKSTREAM-02 — Chat-specific context transfer and reusable handoff packaging

* ID: WORKSTREAM-02
* Name: Chat-specific context transfer and reusable handoff packaging
* Objective: Convert the existing maximum-fidelity Context Transfer Packet and visible chat context into a downloadable, reusable per-chat report package.
* Current state: This response creates Markdown/YAML reports and a ZIP archive for later reuse.
* Desired end state: A self-contained package with full report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit file, manifest, and ZIP.
* Priority: high
* Decisions: DECISION-01, DECISION-02, DECISION-07, DECISION-08
* Tasks: TASK-18, TASK-19, TASK-20
* Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-22, CONSTRAINT-23, CONSTRAINT-24, CONSTRAINT-25
* Artifacts: ARTIFACT-03, ARTIFACT-07, ARTIFACT-08, ARTIFACT-09, ARTIFACT-10, ARTIFACT-11, ARTIFACT-12, ARTIFACT-13, ARTIFACT-14, ARTIFACT-15
* Risks: RISK-08, RISK-09, RISK-10, RISK-11, RISK-12, RISK-13
* Open questions: None
* Next action: Download and store the package in a per-chat folder.

### WORKSTREAM-03 — Future aggregation into full Project Spec Book and Master Living State File

* ID: WORKSTREAM-03
* Name: Future aggregation into full Project Spec Book and Master Living State File
* Objective: Later combine multiple old-chat report packages into a full Project Spec Book and Master Living State File.
* Current state: The current prompt included a later aggregator prompt and described desired aggregation behavior. No aggregation has occurred in this chat.
* Desired end state: A future central aggregation chat ingests all packages, preserves provenance, deduplicates carefully, records conflicts, and produces a master spec/living state file.
* Priority: medium
* Decisions: DECISION-09
* Tasks: TASK-21
* Constraints: CONSTRAINT-26, CONSTRAINT-27
* Artifacts: ARTIFACT-16
* Risks: RISK-14, RISK-15, RISK-16
* Open questions: None
* Next action: When aggregating later, provide this package plus other old-chat packages to a central aggregation chat.



## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Infer chat label as 'Dominium Development Routes'. | Implemented for this package | User did not provide a chat label; main visible topic was Dominium development routes and component order. | A short filesystem-safe label was required for filenames. | All files use prefix dominium_development_routes. | WORKSTREAM-02 | 5/5 | INFERENCE |
| DECISION-02 | Use date anchor '2026-05-27 Australia/Melbourne'. | Confirmed requirement | User explicitly instructed to use that date anchor unless a more specific date existed. | Creates stable temporal reference for future aggregation. | All reports use this date anchor; no current external facts are assumed. | WORKSTREAM-02 | 5/5 | FACT |
| DECISION-03 | Route C — Kernel-First Deterministic Simulation was recommended for Dominium by prior assistant. | Assistant proposal, not user-confirmed | Prior assistant said Dominium should follow Route C. | Proposed to support determinism, scale, replay, tooling, and moddability. | Would make simulation primitives and kernel the first technical work. | WORKSTREAM-01 | 5/5 prior output occurred; 2/5 acceptance | FACT about prior output; UNCERTAIN as project decision |
| DECISION-04 | Use layer order [0] Mathematical & Temporal Primitives through [8] Distribution, Modding, Multiplayer. | Assistant proposal, not user-confirmed | Prior assistant supplied this exact layer stack. | Strict dependency layering prevents UI/content from contaminating simulation core. | Roadmap should be phase-gated and dependency-aware. | WORKSTREAM-01 | 5/5 prior output occurred; 2/5 acceptance | FACT about prior output; UNCERTAIN as project decision |
| DECISION-05 | Use principle: 'Simulation precedes representation. State precedes UI. Determinism precedes performance. Data precedes content.' | Assistant proposal, not user-confirmed | Prior assistant wrote this principle explicitly. | Intended to preserve testability, replayability, and long-term maintainability. | Future assistant should preserve this as proposal-level carry-forward. | WORKSTREAM-01 | 5/5 prior output occurred; 2/5 acceptance | FACT about prior output; UNCERTAIN as project decision |
| DECISION-06 | Feature completion rule proposed: deterministic, serializable, reproducible, inspectable, moddable. | Assistant proposal, not user-confirmed | Prior assistant listed these five completion conditions. | Raises quality bar for complex simulation features. | Could become acceptance criteria after user confirmation. | WORKSTREAM-01 | 5/5 prior output occurred; 2/5 acceptance | FACT about prior output; UNCERTAIN as project decision |
| DECISION-07 | Limit this package to this chat only. | Confirmed requirement | User explicitly said output is for THIS CHAT ONLY. | Prevents accidental whole-project summarization. | Project-level information must be labelled PROJECT-CONTEXT if used. | WORKSTREAM-02 | 5/5 | FACT |
| DECISION-08 | Create downloadable Markdown/YAML package and ZIP when file generation is available. | Implemented in this response | User explicitly requested files if file-generation/download tool is available. | Enables saving, sharing, reuse, and aggregation. | Seven files and ZIP are created. | WORKSTREAM-02 | 5/5 | FACT |
| DECISION-09 | Future aggregation should ingest per-chat packages, preserve provenance, and wait for 'ALL PACKAGES PROVIDED' before producing master outputs. | User-supplied future process; not executed here | User supplied a later aggregator prompt with these instructions. | Avoids premature merging across incomplete old-chat inputs. | Aggregator packet and YAML should be source-friendly. | WORKSTREAM-03 | 5/5 | FACT |

### Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Confirm whether Route C is accepted as Dominium's provisional development route. | High | High | User + future assistant | ARTIFACT-02, DECISION-03 | User confirmation or correction | Accepted/rejected/revised development route | Ask only if needed; otherwise proceed as provisional and label it unresolved. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| TASK-02 | Define Dominium's genre and core player loop. | High | High | User / design lead |  | Player actions, time scale, win/loss or open-ended model, core loop | Core design statement | Draft assumptions list and request correction only where needed. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| TASK-03 | Define minimum deterministic simulation slice. | High | High | Future assistant / developer | TASK-01, TASK-02 | Core loop, simulation scope | MDS v0.1 specification | Specify the smallest world simulation proving the architecture. | WORKSTREAM-01 | INFERENCE |
| TASK-04 | Define time model. | High | High | Developer | TASK-03 | Tick granularity, calendar needs, scheduling semantics | Time primitive spec | Choose provisional tick/calendar model. | WORKSTREAM-01 | INFERENCE |
| TASK-05 | Define deterministic numeric model. | High | High | Developer | TASK-03 | Range/precision requirements, platform targets | Fixed-point or controlled numeric determinism spec | Determine strictness of no-floating-point rule. | WORKSTREAM-01 | INFERENCE |
| TASK-06 | Define RNG determinism contract. | High | High | Developer | TASK-04 | Seed strategy, stream partitioning needs | RNG stream and reproducibility spec | Define seed, stream, and event-order rules. | WORKSTREAM-01 | INFERENCE |
| TASK-07 | Define entity identity and lifetime model. | High | Medium | Developer | TASK-03 | Entity categories, creation/deletion semantics | Entity ID/lifetime spec | Draft durable ID and tombstone/reuse rules. | WORKSTREAM-01 | INFERENCE |
| TASK-08 | Define event queue and state mutation rules. | High | Medium | Developer | TASK-04, TASK-07 | Ordering rules, conflict resolution, command model | Kernel mutation spec | Draft deterministic event ordering and command application rules. | WORKSTREAM-01 | INFERENCE |
| TASK-09 | Define serialization primitives and versioning. | High | Medium | Developer | TASK-07, TASK-08 | State schema, save/load needs | Serialization/version compatibility spec | Decide schema and version migration strategy. | WORKSTREAM-01 | INFERENCE |
| TASK-10 | Build headless deterministic kernel prototype. | High | Medium | Developer | TASK-04, TASK-05, TASK-06, TASK-08, TASK-09 | Language/engine decision, kernel specs | Runnable headless simulation kernel | Implement minimal seed/input/replay loop. | WORKSTREAM-01 | INFERENCE |
| TASK-11 | Build replay verification tests. | High | Medium | Developer | TASK-10 | Input traces, state hashing method | Determinism test suite | Compare tick hashes across runs. | WORKSTREAM-01 | INFERENCE |
| TASK-12 | Define world state graph. | High | Medium | Developer / designer | TASK-07, TASK-08 | Spatial model, ownership, causality requirements | World model spec | Draft cells/regions/entities/relationships model. | WORKSTREAM-01 | INFERENCE |
| TASK-13 | Define and build minimal debug inspector. | Medium | Medium | Developer | TASK-10, TASK-12 | State schema, inspection needs | CLI/text or basic visual state inspector | Start with command-line inspection and invariant reports. | WORKSTREAM-01 | INFERENCE |
| TASK-14 | Confirm core system order and scope. | Medium | Medium | User / future assistant | TASK-02, TASK-12 | Actual Dominium mechanics | Confirmed system dependency graph | Validate resource → population → economy → governance → conflict → environment order. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| TASK-15 | Define content schema after systems stabilize. | Medium | Low initially | Developer / designer | TASK-14 | Rule packs, data-driven needs | Content schema v0.1 | Delay until core systems exist unless prototype content is throwaway. | WORKSTREAM-01 | INFERENCE |
| TASK-16 | Define presentation architecture after headless prototype. | Medium | Low initially | Developer | TASK-10, TASK-13 | Simulation API, UI needs | Read-only presentation layer spec | Define command/event boundary between UI and simulation. | WORKSTREAM-01 | INFERENCE |
| TASK-17 | Define modding and multiplayer only after replay/schema foundations are clearer. | Low/Medium | Low initially | Developer | TASK-09, TASK-11, TASK-15 | Actual product goals for mods/multiplayer | Mod loading and network model decisions | Verify whether mods or multiplayer are real goals. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| TASK-18 | Create final report package files. | High | Immediate | Current assistant | Prior Context Transfer Packet, Visible chat context | User's current packaging prompt | Seven requested files plus ZIP | Completed by this response. | WORKSTREAM-02 | FACT |
| TASK-19 | Store this package in its own per-chat folder. | High | After download | User | TASK-18 | Downloaded files or ZIP | Durable local/archive copy | Save the ZIP and Markdown/YAML files together. | WORKSTREAM-02, WORKSTREAM-03 | INFERENCE |
| TASK-20 | Manually verify caveats before using report as authoritative. | High | Before acting on technical roadmap | User / future assistant | TASK-18 | This report, Project reality | Verified corrections or confirmations | Check Route C acceptance, scope, tech stack, and missing files. | WORKSTREAM-02, WORKSTREAM-01 | FACT from user process requirement + INFERENCE for content |
| TASK-21 | Use aggregator prompt later after collecting all old-chat packages. | Medium | Future | User / future aggregation assistant | Other chat packages | All per-chat report packages | Full Project Spec Book and Master Living State File | Provide packages one at a time, then say ALL PACKAGES PROVIDED. | WORKSTREAM-03 | FACT |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Do not invent facts. | Evidence/process | Hard | User packaging prompt | Unknowns must remain marked unknown. | High | 5/5 | FACT |
| CONSTRAINT-02 | Do not silently infer. | Evidence/process | Hard | User packaging prompt | Inferences must be labelled. | High | 5/5 | FACT |
| CONSTRAINT-03 | Use labels FACT, INFERENCE, UNCERTAIN / UNVERIFIED, PROJECT-CONTEXT. | Evidence/process | Hard | User packaging prompt | Important items require explicit epistemic status. | High | 5/5 | FACT |
| CONSTRAINT-04 | Do not treat assistant suggestions as user decisions unless accepted. | Evidence/process | Hard | User packaging prompt | Route C and phase order remain proposal-level. | High | 5/5 | FACT |
| CONSTRAINT-05 | Output is for this chat only. | Scope | Hard | User packaging prompt | Do not summarize entire project; label project context. | High | 5/5 | FACT |
| CONSTRAINT-06 | Preserve rejected, superseded, and deprioritized options. | Continuity | Hard | User packaging prompt | Route A/B and technical warnings must be included. | Medium | 5/5 | FACT |
| CONSTRAINT-07 | Preserve visible rationale and assumptions without revealing hidden chain-of-thought. | Safety/process | Hard | User packaging prompt | Explain why choices were proposed using visible text only. | Medium | 5/5 | FACT |
| CONSTRAINT-08 | Use structured headings, tables, stable IDs, and consistent terminology. | Formatting | Hard | User packaging prompt | All registers use requested ID pattern. | Medium | 5/5 | FACT |
| CONSTRAINT-09 | Simulation precedes representation. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Build simulation before polished UI/rendering. | Medium | 5/5 prior output; acceptance uncertain | FACT about prior output; UNCERTAIN as requirement |
| CONSTRAINT-10 | State precedes UI. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Define state model before user interface. | Medium | 5/5 prior output; acceptance uncertain | FACT about prior output; UNCERTAIN as requirement |
| CONSTRAINT-11 | Determinism precedes performance. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Correct replayable behavior should come before optimization. | Medium | 5/5 prior output; acceptance uncertain | FACT about prior output; UNCERTAIN as requirement |
| CONSTRAINT-12 | Data precedes content. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Schemas and data model should precede large content production. | Medium | 5/5 prior output; acceptance uncertain | FACT about prior output; UNCERTAIN as requirement |
| CONSTRAINT-13 | No rendering in deterministic kernel. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Keep rendering layer separate from simulation loop. | Medium | 4/5 | UNCERTAIN / UNVERIFIED as project rule |
| CONSTRAINT-14 | No UI in deterministic kernel. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | User input should become commands/events rather than direct kernel UI calls. | Medium | 4/5 | UNCERTAIN / UNVERIFIED as project rule |
| CONSTRAINT-15 | No floating point in deterministic core. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Use fixed-point or tightly controlled deterministic math if strict determinism is required. | Medium | 3/5 project fit unknown | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-16 | No OS calls in deterministic core. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Avoid nondeterministic time/filesystem/threading inputs inside simulation logic. | Medium | 4/5 | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-17 | Presentation reads state and does not mutate simulation directly. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Mutation should pass through command/event API. | Medium | 4/5 | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-18 | Each core system should run headless. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Systems can be tested without graphics. | Medium | 4/5 | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-19 | Each core system should serialize. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Save/load compatibility becomes early requirement. | Medium | 4/5 | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-20 | Each core system should replay identically. | Technical proposal | Soft/proposed until user confirms | Prior assistant output | Replay acts as correctness test. | Medium | 4/5 | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-21 | A complete feature should be deterministic, serializable, reproducible, inspectable, and moddable. | Technical quality gate proposal | Soft/proposed until user confirms | Prior assistant output | Acceptance criteria become stricter than normal feature completion. | Medium | 3/5; moddability unconfirmed | UNCERTAIN / UNVERIFIED as project rule |
| CONSTRAINT-22 | If file generation is available, create actual downloadable files and preferably a ZIP. | Output/export | Hard | User packaging prompt | Do not only paste content if files can be created. | High | 5/5 | FACT |
| CONSTRAINT-23 | Use exact requested file names with filesystem-safe chat label prefix. | Output/export | Hard | User packaging prompt | Files must follow naming pattern. | Medium | 5/5 | FACT |
| CONSTRAINT-24 | External-world facts, versions, prices, APIs, laws, schedules, products, or current events require verification before future use. | Evidence/staleness | Hard | User packaging prompt | This package should not assert current ecosystem facts without verification. | High | 5/5 | FACT |
| CONSTRAINT-25 | Future outputs should be self-contained enough that the original chat is not required unless a gap is marked. | Continuity | Hard | User packaging prompt | Reports must include enough context and caveats for reuse. | Medium | 5/5 | FACT |
| CONSTRAINT-26 | Future aggregator must preserve source provenance and not merge similar items unless evidence supports merging. | Aggregation | Hard for future aggregator prompt | User-supplied aggregator prompt | Cross-chat IDs and labels should remain traceable. | High | 5/5 | FACT |
| CONSTRAINT-27 | Future aggregator should not produce master outputs until user says 'ALL PACKAGES PROVIDED'. | Aggregation | Hard for future aggregator prompt | User-supplied aggregator prompt | Avoid premature master spec generation. | High | 5/5 | FACT |

### Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Is Route C — Kernel-First Deterministic Simulation accepted as the Dominium route? | Determines ordering of all early work. | Prior assistant recommended it. | User acceptance or revision. | User confirmation or future roadmap proceeds provisionally with label. | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | What exactly is Dominium's genre? | Architecture and feature order depend on genre and gameplay loop. | It is discussed as a game named Dominium. | 4X, grand strategy, city-builder, colony sim, RTS, hybrid, or other. | User/design statement. | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | What is the core player loop? | Defines UI needs, simulation cadence, and MVP scope. | Not specified. | Player actions, feedback loop, goals, session structure. | Design brief or user answer. | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What are target platforms? | Affects engine/language, determinism, UI, performance, distribution. | Not specified. | PC, web, mobile, console, server, cross-platform. | User confirmation. | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What engine or programming language will be used? | Implementation plan depends on tech stack. | Not specified. | Custom engine, Godot, Unity, Unreal, Rust, C++, C#, etc. | Technical decision after requirements. | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Is strict deterministic replay required, and at what level? | Full cross-platform determinism is costly and shapes every core decision. | Prior assistant proposed strict replay/determinism. | Same-machine vs cross-platform vs multiplayer-grade determinism. | User/technical requirement decision. | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Is multiplayer planned? | Network model affects replay/sync architecture. | Prior assistant mentioned multiplayer only as later phase. | Actual product requirement. | User/product decision. | Medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Is modding a core goal? | Modding affects schemas, loading, validation, and data boundaries. | Prior assistant proposed first-class mods. | User priority and scope. | User/product decision. | Medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | What is the intended simulation scale? | Determines data structures, tick rate, performance, and architecture depth. | Not specified. | Entities, agents, regions, time horizon, update frequency. | Simulation target specification. | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | What does 'world' mean in Dominium? | World model/state graph cannot be designed without domain semantics. | Prior assistant listed cells, regions, ownership, jurisdiction, causality. | Actual spatial and political/economic model. | Design spec. | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | What are Dominium's primary systems? | System ordering depends on actual mechanics. | Prior assistant proposed resources, population, economy, governance, conflict, environment. | Whether those are actual Dominium systems. | User/design confirmation. | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | What is prototype v0.1 success? | Prevents overbuilding and defines acceptance tests. | Not specified. | Minimum testable or playable milestone. | MVP definition. | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Are there existing files, repositories, or design documents? | This package may be incomplete if external artifacts exist. | No files were visible in this chat. | Whether external project docs exist elsewhere. | User upload/repo/doc reference. | Medium | WORKSTREAM-01, WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | What team size and timeline apply? | Determines realism of engine/kernel/tooling roadmap. | Not specified. | Solo, team, academic, commercial, deadline. | User confirmation. | Medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | How should other old-chat reports be merged later? | This report is intended for future aggregation. | User supplied an aggregator prompt. | Actual number and content of future packages. | Future aggregation process. | Medium | WORKSTREAM-03 | FACT + UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | User's initial Dominium development-route question | Prompt | Asked for usual development routes and specific component order. | Preserved in report | Visible chat | Yes | Exact wording: 'What are the usual development routes for games like Dominium technically and feature wise? What specific components should we work on and in which order?' | FACT |
| ARTIFACT-02 | Prior assistant Dominium roadmap answer | Output/framework | Proposed Route A/B/C, recommended Route C, provided layered architecture and phase order. | Preserved as proposal-level material | Visible chat | Yes | Must not be treated as user-confirmed decision. | FACT |
| ARTIFACT-03 | Maximum-fidelity Context Transfer Packet | Output/handoff | Preserved conversation state for a new assistant. | Existing packet consumed and normalized | Visible chat previous assistant response | Yes | This final package repairs and normalizes it. | FACT |
| ARTIFACT-04 | Route A/B/C framework | Conceptual framework | Contrasted development strategies for Dominium-like games. | Preserved | Prior assistant output | Yes | Route C proposed; Route A/B deprioritized by prior assistant. | FACT about prior output |
| ARTIFACT-05 | Layer stack [0]–[8] | Architecture outline | Described dependency hierarchy from primitives to distribution/modding/multiplayer. | Preserved as proposal | Prior assistant output | Yes | Should be verified against actual project scope. | FACT about prior output; UNCERTAIN as decision |
| ARTIFACT-06 | Feature completion rule | Quality gate proposal | Defined completed feature as deterministic, serializable, reproducible, inspectable, moddable. | Preserved as proposal | Prior assistant output | Yes | Moddability unconfirmed as requirement. | FACT about prior output; UNCERTAIN as decision |
| ARTIFACT-07 | Current packaging prompt | Prompt/process specification | Specified final package files, structure, ID patterns, and export requirements. | Implemented | Visible chat current user message | Yes | Serves as process precedent for other old chats. | FACT |
| ARTIFACT-08 | dominium_development_routes__01_full_chat_report.md | Generated Markdown report | Main human-readable report for this chat. | Created in this response | Current assistant | Yes | Primary file for human review. | FACT after creation |
| ARTIFACT-09 | dominium_development_routes__02_spec_sheet.yaml | Generated YAML spec sheet | Structured data suitable for later master spec construction. | Created in this response | Current assistant | Yes | Use for machine/aggregator processing. | FACT after creation |
| ARTIFACT-10 | dominium_development_routes__03_aggregator_packet.md | Generated Markdown packet | Compact cross-chat aggregation input. | Created in this response | Current assistant | Yes | Use in future central aggregation chat. | FACT after creation |
| ARTIFACT-11 | dominium_development_routes__04_registers.md | Generated Markdown registers | Standalone normalized tables. | Created in this response | Current assistant | Yes | Stable IDs for merge. | FACT after creation |
| ARTIFACT-12 | dominium_development_routes__05_reader_brief.md | Generated Markdown brief | Short human-readable version. | Created in this response | Current assistant | Yes | Use for quick orientation. | FACT after creation |
| ARTIFACT-13 | dominium_development_routes__06_verification_and_audit.md | Generated Markdown audit | Quality-control record and verification checklist. | Created in this response | Current assistant | Yes | Use before trusting the roadmap. | FACT after creation |
| ARTIFACT-14 | dominium_development_routes__manifest.md | Generated Markdown manifest | File list, item counts, storage guidance, package status. | Created in this response | Current assistant | Yes | Index for the package. | FACT after creation |
| ARTIFACT-15 | dominium_development_routes__handoff_package.zip | Generated ZIP archive | Convenient bundle containing all report files. | Created in this response | Current assistant | Yes | Preferred download for storage. | FACT after creation |
| ARTIFACT-16 | Later aggregator prompt supplied by user | Prompt | Instructions for combining multiple old-chat report packages into a Project Spec Book and Master Living State File. | Preserved in reports | Visible chat current user message | Yes | Not executed in this chat. | FACT |

### Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Treating assistant proposals as user decisions | Future roadmap may falsely lock in Route C or strict determinism. | High | High | Keep proposal status labels and ask/verify before formalizing. | WORKSTREAM-01 | FACT/INFERENCE |
| RISK-02 | Over-assuming Dominium genre | Wrong architecture or feature order. | High | High | Keep genre unknown; require core-loop definition. | WORKSTREAM-01 | INFERENCE |
| RISK-03 | Overbuilding deterministic infrastructure | Slow progress if the game scope is smaller than assumed. | Medium | Medium | Define minimum deterministic simulation slice before building deep tooling. | WORKSTREAM-01 | INFERENCE |
| RISK-04 | Underbuilding simulation foundations | Technical debt if Dominium is genuinely simulation-heavy. | Medium | High | Confirm scope and determinism needs early. | WORKSTREAM-01 | INFERENCE |
| RISK-05 | Premature engine/language recommendation | Tech stack mismatch with goals and constraints. | Medium | High | Delay stack choice until platforms, scope, and determinism requirements are known. | WORKSTREAM-01 | INFERENCE |
| RISK-06 | Ignoring replay/determinism cost | Hard-to-debug desyncs or impossible multiplayer/replay later. | Medium | High | Define exact determinism target and build replay tests early if accepted. | WORKSTREAM-01 | INFERENCE |
| RISK-07 | UI or content contaminates simulation logic | Reduced testability, replayability, and maintainability. | Medium | High | Use command/event boundary and headless simulation tests. | WORKSTREAM-01 | INFERENCE |
| RISK-08 | Summarization loss during chat retirement | Future assistant misses rationale, caveats, rejected options, or tasks. | Medium | High | Use this package with full report, registers, and YAML. | WORKSTREAM-02 | FACT/INFERENCE |
| RISK-09 | Over-compression of prior Context Transfer Packet | Lost nuance from proposal-level status. | Medium | Medium | This package includes audit, labels, and stable IDs. | WORKSTREAM-02 | INFERENCE |
| RISK-10 | Missing artifacts outside visible chat | Package may omit files/design docs not visible here. | Medium | Medium | Verify whether external docs/repos exist before relying on report. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-11 | Stale external-world facts | Future technical choices based on outdated engine/tool/API claims. | Medium | Medium | Verify all external facts before use; this report avoids current external claims. | WORKSTREAM-02, WORKSTREAM-01 | FACT/INFERENCE |
| RISK-12 | Malformed or difficult-to-merge package | Future aggregation becomes unreliable. | Low | Medium | Use requested filenames, stable IDs, and YAML schema. | WORKSTREAM-02, WORKSTREAM-03 | INFERENCE |
| RISK-13 | Misunderstanding user preferences | Future assistant may add fluff, omit citations, or ask unnecessary questions. | Medium | Medium | Preserve preference register and source hierarchy. | WORKSTREAM-02 | FACT/INFERENCE |
| RISK-14 | Premature cross-chat merging | Contradictions erased or unsupported master spec decisions created. | Medium | High | Aggregator must preserve provenance and wait for ALL PACKAGES PROVIDED. | WORKSTREAM-03 | FACT/INFERENCE |
| RISK-15 | Duplicate but not identical concepts across chats | Aggregator may merge items with different statuses or assumptions. | Medium | Medium | Use stable IDs per package and conflict/deduplication registers. | WORKSTREAM-03 | INFERENCE |
| RISK-16 | Project-level context contaminates chat-specific report | Report may imply facts not established in this chat. | Medium | Medium | Label Project context and keep scope limited to this chat. | WORKSTREAM-03, WORKSTREAM-02 | FACT/INFERENCE |

### Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Confirm Dominium is intended to be simulation-heavy. | Kernel-first route depends on this assumption. | User confirmation or design document | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Confirm or revise Route C recommendation. | All proposed phase ordering depends on route selection. | User decision | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Confirm determinism target. | Same-run, cross-platform, replay, and multiplayer-grade determinism imply different costs. | Technical requirements discussion | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Confirm genre and core player loop. | Feature order and MVP cannot be defined without them. | Design brief or user answer | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Confirm engine/language/platform constraints. | Implementation plan cannot be precise without tech stack constraints. | Technical decision / project constraints | High | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Confirm whether modding is a core goal. | The prior feature completion rule includes moddability, but user did not confirm it. | Product/design requirement | Medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Confirm whether multiplayer is planned. | Replay/sync priorities and network model depend on it. | Product/design requirement | Medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Check package files open correctly after download. | Generated files must be usable outside chat. | Manual file open / checksum if desired | High | WORKSTREAM-02 | FACT/INFERENCE |
| VERIFY-09 | Check whether this chat had external files not visible in transcript. | Artifact ledger says none visible; hidden/external docs may exist. | User review of project files/repo/uploads | Medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Confirm all packages are collected before running aggregator prompt. | Aggregator prompt requires waiting until all packages are provided. | User confirmation in future aggregation chat | Medium | WORKSTREAM-03 | FACT/INFERENCE |
| VERIFY-11 | Verify external game-development claims before using them as evidence. | Prior assistant gave unsourced claims about development routes; current facts may need citations. | Current official docs, postmortems, talks, technical articles | Medium | WORKSTREAM-01 | FACT from user requirement |

## 6. Possible Cross-Chat Duplicates

- Dominium genre/core loop.
- Technical roadmap and phase order.
- Engine/language selection.
- Determinism/replay/save-load requirements.
- World model/state graph.
- Economy/population/governance/conflict systems.
- Modding and multiplayer scope.
- User preference for rigorous labelled continuity.
- Future Project Spec Book aggregation workflow.

## 7. Possible Cross-Chat Conflicts

- Other chats may accept or reject Route C.
- Other chats may prioritize playable prototype or UI validation before simulation kernel.
- Other chats may establish an engine/language not present here.
- Other chats may define Dominium as less simulation-heavy.
- Other chats may make modding or multiplayer out of scope.
- Other chats may choose floating point or nondeterministic approaches for practical reasons.

## 8. Spec Book Integration Guidance

Feed this chat into chapters on architecture philosophy, development route, deterministic simulation, world model, replay/persistence, tooling, presentation boundary, data/content strategy, and risk management. Promote items to formal requirements only after confirmation or corroboration. Keep rejected options as historical warnings unless later evidence makes them irrelevant. Do not merge Route C into master requirements prematurely.

## 9. Aggregator Warnings

- Do not treat assistant proposals as accepted decisions.
- Do not invent missing design details.
- Do not erase uncertainty because the architecture answer was assertive.
- Do not assume generated files existed before this response.
- Do not treat this report as a full Dominium project summary.
- Verify external technical claims before using them as evidence.
