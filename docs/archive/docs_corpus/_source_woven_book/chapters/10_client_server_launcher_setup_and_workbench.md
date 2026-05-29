## 10. Client, Server, Launcher, Setup, and Workbench

Product shells are how operators meet the substrate, but they remain downstream of truth.

Current docs identify product surfaces while queue state keeps broad implementation constrained.

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> - do not add or preserve hardcoded runtime mode branches
> - express behavior composition through profiles, bundles, law surfaces, and explicit constraints
>
> [Source: Dominium Agent Governance]

> - authoritative truth mutation must occur through lawful deterministic Process execution
> - UI, render, operator, tooling, or convenience layers must not mutate truth directly
>
> [Source: Dominium Agent Governance]

> - truth is authoritative
> - perception and observation are filtered views
> - rendering is presentation only
> - later governance and tool work must not collapse those layers
>
> [Source: Dominium Agent Governance]

> Dominium is a deterministic, contract-governed simulation game and operating
> environment built on the Domino deterministic substrate.
>
> [Source: Dominium / Domino]

> The project is about invention, production, logistics, economics, settlement,
> trust, communication, and institutional power emerging from lawful simulation
> rather than scripted outcomes. Commands, processes, packs, capabilities,
> diagnostics, evidence, and replay proof are first-class surfaces. Invalid action
> must refuse explicitly; hidden fallback behavior is not part of the model.
>
> [Source: Dominium / Domino]

> Dominium is the official game, product, and domain layer on top of Domino. It
> defines rules, process meaning, law targets, domain interpretation, authored
> content use, and product composition.
>
> [Source: Dominium / Domino]

The archive preserves rich Workbench, launcher, setup, and command-surface ideas.

> Domino is the deterministic substrate. Dominium is the official game, product, and domain layer. Workbench is a governed validation and inspection environment. Setup and launcher compose product instances. Tools validate, generate, audit, and migrate. Contracts and schema law define public identity and compatibility meaning.
>
> [Source: Full Project Picture V0]

> - `architecture` (45 conversations): system boundaries, product shape, the referenced source, and repository structure. Sources: Dominium Advanced Simulation and Infrastructure Architecture, Dominium APP0 Runtime, Platform, and Renderer Architecture, Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning, Dominium/Domino Architecture and Codex Prompt Roadmap, Dominium Architecture, UI, Providers, and Robot OS Strategy.
> - `content` (45 conversations): packs, mods, authored payload, GUI/content boundaries, and provider/content separation. Sources: Dominium Advanced Simulation and Infrastructure Architecture, Dominium APP0 Runtime, Platform, and Renderer Architecture, Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning, Dominium/Domino Architecture and Codex Prompt Roadmap, Dominium Architecture, UI, Providers, and Robot OS Strategy.
> - `ui` (45 conversations): presentation, tools, editor concepts, perceived model surfaces, and command/result display. Sources: Dominium Advanced Simulation and Infrastructure Architecture, Dominium APP0 Runtime, Platform, and Renderer Architecture, Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning, Dominium/Domino Architecture and Codex Prompt Roadmap, Dominium Architecture, UI, Providers, and Robot OS Strategy.
> - `governance` (44 conversations): authority order, canon, contracts, refusal, review gates, and agent operation. Sources: Dominium Advanced Simulation and Infrastructure Architecture, Dominium APP0 Runtime, Platform, and Renderer Architecture, [Dominium Architecture, Application Layer, TestX, and CodeHygiene.
>
> [Source: Full Project Picture V0]

> - README.md describes Dominium as a deterministic, contract-governed simulation game and operating environment built on the Domino deterministic substrate.
> - the referenced source binds determinism, process-only mutation, law-gated authority, no runtime mode flags, pack-driven integration, explicit refusal, and truth/perceived/render separation.
> - the referenced source defines vocabulary such as Engine, Client, AuthorityContext, Domain, Derived artifact, and Contract.
> - AGENTS.md and the referenced source keep archived conversations below canon, glossary, governance, contracts, current queue, and validated repo artifacts.
> - .aide/queue/current.toml currently blocks broad feature work including: `broad_workbench_ui`, `gameplay`, `native_gui`, `package_runtime`, `provider_runtime`, `release_publication`, `renderer_implementation`, `runtime_module_loader`.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> External platform, SDK, renderer, language baseline, release, provider, package runtime, and implementation claims must be rechecked. The synthesis should use those old claims to identify questions, not to assert current facts.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - It does not promote archive claims.
> - It does not rewrite canon, contracts, schema, implementation, release, or queue state.
> - It does not open blocked renderer, gameplay, provider runtime, package runtime, broad Workbench UI, native GUI, or release publication work.
>
> [Source: DOCS Current Project Picture]

> | Blocked Scope | Authority Source | Matching Docs Paths | Examples | Disposition |
> | --- | --- | --- | --- | --- |
> | broad_workbench_ui | .aide/queue/current.toml | 1 | the referenced source | blocked_by_current_queue |
> | runtime_module_loader | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
>
> [Source: DOCS Blocked Scope Alignment]

> | DOC-DECIDE-BLOCK-0001 | queue | Should broad Workbench UI remain closed until a later queue phase explicitly opens it? | future_queue_decision | high | defer |
> | DOC-DECIDE-BLOCK-0002 | queue | Should renderer implementation remain blocked? | future_queue_decision | high | defer |
> | DOC-DECIDE-BLOCK-0003 | queue | Should provider/package runtime work remain blocked? | future_queue_decision | high | defer |
> | DOC-DECIDE-BLOCK-0004 | queue | Should release publication remain blocked? | future_queue_decision | high | defer |
>
> [Source: DOCS Decision Docket]

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep.
> 2. Build complexity comes from many machines and historical toolchains.
> 3. More hand-written presets are not the optimal solution.
> 4. Build truth should live in tuple contracts.
> 5. Local machine probes should generate local `CMakeUserPresets.json`.
> 6. CMake remains build authority.
> 7. AIDE should probe/explain/generate/verify/record evidence.
> 8. XStack orchestrates; RepoX/TestX enforce/prove.
> 9. Dist/package manifests should preserve artifact identity.
> 10. Dominium should be treated as an engine platform, not a one-off game.
> 11. Freeze contracts, not implementations.
> 12. The current top-level repo spine is close to right.
> 13. Deeper boundaries and naming still need cleanup.
> 14. Public surface registry is a key missing mechanism.
> 15. Replacement protocol is a key missing mechanism.
> 16. Dependency-edge enforcement is needed.
> 17. ABI/header conformance tests are needed.
> 18. Schema/protocol compatibility fixtures are needed.
> 19. Many recommendations are not yet accepted decisions.
> 20. Verify live repo state before implementation.
>
> [Source: Reader Brief Dominium Build And Future Proofing Architecture]

> 1. **User confirmation:** identify which recommendations in this chat should become binding Dominium canon.
> 2. **Repo verification:** check current HEAD, CI status, build presets, CMake configure/build/CTest, layout validators, component matrix validators, and product/projection proof status.
> 3. **Choose first structural task:** either:
> - `STRUCTURE-01: Public Surface Registry`, or
> - `BUILD-CONTRACT-01: Tuple Build Contract and Machine Probe`.
> 4. **Create a narrow implementation prompt:** explicitly forbid feature work and scope creep.
> 5. **Run validators and record evidence:** preserve results in AIDE/RepoX/TestX-compatible form.
> 6. **Feed this handoff into the master spec-book aggregator.**
>
> [Source: Accompanying Human Readable Detailed Conversation Report]

> This report covers only this old chat and the previously generated context transfer packet visible in this chat. It is not a whole-project summary. Where Project context appears, it is labelled PROJECT-CONTEXT. Direct user statements outrank assistant proposals. Assistant-generated astronomical data, constants, calendar names, implementation-language claims, and codebase assumptions require verification before implementation. Tentative decisions remain tentative. This report is intended for future aggregation into a full Project Spec Book and for a new assistant to continue without asking the user to repeat this chat.
>
> [Source: Full Chat Report Dominium Chronology & Celestial Systems]

> - Label: FACT / INFERENCE
> - Objective: Define celestial bodies, structures, regions, systems, and sites for gameplay across Earth, Sol, Milky Way, and universe scales without redundant simulation.
> - Background: The chat began with the user asking what celestial bodies/systems to include in a logical universe simulation without too much redundancy. The user then specified gameplay scales: Earth, Sol, Milky Way, and universe.
> - Current state: Scope and classification were defined conceptually: explicit, procedural, or parametric; Sol system is highest fidelity; Milky Way has a real-system backbone plus procedural expansion; universe is mostly parametric.
> - Desired end state: A data-driven celestial registry integrated with simulation, navigation, gameplay mechanics, time, governance, and knowledge/fog-of-war systems.
> - Importance: Celestial content defines map scope, simulation fidelity, gameplay locations, calendars, hazards, and long-term expansion.
> - Decisions made: DECISION-01, DECISION-02, DECISION-03
> - Decisions pending: QUESTION-07, QUESTION-08, QUESTION-09
> - Pending tasks: TASK-02, TASK-18
> - Constraints: CONSTRAINT-11, CONSTRAINT-12
> - Dependencies: Versioned constants/ephemerides, Verified astronomical data, Plan G integration
> - Timeline / sequencing: Defined early, refined after Sol system and celestial scope questions.
> - Blockers: Unverified astronomy details, No access in this chat to the actual Plan G codebase or full chat.
> - Risks: RISK-07, RISK-08
> - Artifacts: ARTIFACT-01, ARTIFACT-02, ARTIFACT-03, ARTIFACT-04, ARTIFACT-16
> - Success criteria: Sol system is deep and explicit; Milky Way/universe stay performant; explicit objects are gameplay-relevant.
> - Recommended next action: Verify celestial lists, then convert into data schemas with fidelity classes.
> - Verification needed: VERIFY-01, VERIFY-02, VERIFY-03
> - Confidence: medium-high
> - Carry-forward priority: high
>
> [Source: Full Chat Report Dominium Chronology & Celestial Systems]

> - DECISION-01: Game operates across Earth, Sol, Milky Way, and universe scales. [FACT]
> - DECISION-02: Sol system receives maximum explicit detail. [FACT]
> - DECISION-03: Celestial content uses explicit/procedural/parametric classification. [INFERENCE]
> - DECISION-04: Atomic Continuous Time (ACT) is authoritative simulation time. [FACT]
> - DECISION-05: Use coordinate frames BST, GCT, and CPT above ACT. [FACT]
> - DECISION-06: Calendars are pure renderers and never affect physics. [FACT]
> - DECISION-07: Leap seconds are display-only and absent from core time. [FACT]
> - DECISION-08: Proper time is derived only; calendars render coordinate time. [FACT]
> - DECISION-09: Earth supports Gregorian, Julian, Islamic, Hebrew, Chinese, Persian, Holocene, Metric/French Revolutionary calendars. [FACT]
> - DECISION-10: Perfect Earth Calendar has 13 months ? 28 days and Monday-Sunday weeks. [FACT]
> - DECISION-11: Perfect Earth Calendar month order is March through February with Undecember as 11th month. [FACT]
> - DECISION-12: HPC-E Year Day and Leap Day are appended after February; canonical mode is undated and compatibility mode may use Feb 29/30. [FACT / INFERENCE]
> - DECISION-13: Default world date anchor is Gregorian January 1, 2000 AD. [FACT]
> - DECISION-14: Player spawn time is local sunrise at spawn location. [FACT]
> - DECISION-15: Player starts with no clock/calendar/date HUD. [FACT]
>
> [Source: Reader Brief Dominium Chronology & Celestial Systems]

> - Completeness rating: 4/5.
> - Reliability rating: 4/5 for user-stated design decisions; 2-3/5 for assistant-generated astronomy/constants/non-Earth names until verified.
> - Aggregation readiness rating: 4/5.
> - Main remaining uncertainty sources:
> - Actual Plan G/The Game architecture not visible in this chat.
> - Scientific data and constants were not externally verified here.
> - HPC-E leap rule remains unresolved.
> - Non-Earth calendar names/cycles need user confirmation.
> - Some assistant-generated prompt artifacts may be superseded by this package.
>
> [Source: Verification And Audit Dominium Chronology & Celestial Systems]

> This chat, labelled **Dominium Architecture I**, is a retired architecture/specification chat for the **Dominium Game** project. The visible thread is not a normal project-planning chat; it is primarily a long-running specification-generation session meant to prepare Dominium for automated implementation with **Codex 5.1 Max**. The user's explicit workflow changed during the chat: the initial idea was for Codex to read a full transcript and compile a complete v3 "book of volumes," but the user later decided that Codex could not reliably read the entire context at once. The workflow therefore shifted to creating a **set of `.txt` implementation-spec prompt files**, one per file in the intended repository tree.
>
> [Source: Full Chat Report Dominium Architecture I]

> Core decisions that must not be lost: Dominium's simulation core is intended to be deterministic and replay/lockstep safe; UTF-8 is canonical internally; retro ASCII/ANSI/SFN fallbacks are required for old platforms; semantic versioning must be `major.minor.patch`; build numbers/dates must not appear in filenames but must appear in metadata; systems must not depend on platform/render/UI/audio; dynamic allocation is prohibited in deterministic tick/hot paths; and generated file specs must include requirements, prohibitions, dependencies, functions, declarations, and implementation expectations.
>
> [Source: Full Chat Report Dominium Architecture I]

> This chat also contains important risks. The visible context is only partial because many earlier messages are collapsed. Top-level docs, legal/policy docs, context MDs, cross-dependencies, volume specs, and possibly early engine files are referenced but not fully visible. Several assistant-generated specs contradict one another or use inconsistent APIs. The most important conflicts are duplicate and incompatible specs for `dweather`, `dhydro`, and `dai_core`; inconsistent memory API names; inconsistent serialization API names; C89/C++98 claims that are violated by C99/C++11 constructs; and unverified platform/library support claims. These are not final decisions; they must be carried forward as unresolved issues requiring canonicalisation before implementation.
>
> [Source: Full Chat Report Dominium Architecture I]

The woven passages above come from 50 source documents and 96 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that the desired operator experience is clearer than the currently authorized implementation surface.

Where this leaves us: Workbench is product intent and operator design, not a hidden authority layer.
