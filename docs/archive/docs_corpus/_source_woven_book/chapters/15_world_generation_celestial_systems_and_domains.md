## 15. World Generation, Celestial Systems, and Domains

World generation and celestial systems recur because the project wants large lawful worlds.

Current authority supports deterministic composition and data-driven domain boundaries.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - do not add or preserve hardcoded runtime mode branches
> - express behavior composition through profiles, bundles, law surfaces, and explicit constraints
>
> [Source: Dominium Agent Governance]

> - optional content and capabilities must remain pack- and registry-driven
> - missing packs require explicit refusal or degradation rather than hidden fallback magic
>
> [Source: Dominium Agent Governance]

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

> law surfaces, and constraints, not hardcoded runtime mode forks.
> - Explicit refusal: unsupported or invalid transitions return deterministic,
>
> [Source: Dominium / Domino]

> - Capability grants permission to attempt; law determines accept/refuse/transform.
> - Authority does not bypass law.
> - Refusals are lawful outcomes and MUST be explicit, deterministic, and auditable.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Runtime behavior MUST resolve from profile data (`ExperienceProfile`, `LawProfile`, `ParameterBundle`, optional `MissionSpec` constraints).
> - Hardcoded mode booleans/branches (for example `*_mode` runtime forks) are forbidden.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

Archive passages discuss planets, astronomy, domain packs, terrain, stars, and source verification.

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

> | Surface | Current Role | Conversation-Derived Intent | Current Caution |
> | --- | --- | --- | --- |
> | Engine / Domino | Deterministic substrate | Reusable law-bound simulation foundation | Do not collapse into product UI |
> | Game / Dominium | Domain rules and official product meaning | Invention, logistics, institutions, world systems | Gameplay remains blocked by current queue |
> | Client / Renderer | Presentation and intent issuing | Rich visualization and projection | Renderer implementation is blocked |
> | Server | Authoritative multiplayer validation | Law and authority keeper | Must preserve deterministic proof |
> | Workbench | Validation and inspection surface | Rich operator and authoring future | Broad Workbench UI is blocked |
> | Setup / Launcher | Product composition and local orchestration | Install, repair, profiles, instances | Runtime package behavior remains constrained |
> | Content / Packs | Authored payload and pack-driven composition | Mods, providers, data-driven expansion | Provider/package runtime blocked |
> | AIDE / Codex / XStack | Repo-control and patch workflow aids | Evidence-producing governance layer | No authority replacement |
>
> [Source: Full Project Picture V0]

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

> Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> 1. **Confirm acceptance boundary.** Decide which recommendations in this chat should become Dominium canon and which remain advisory.
> 2. **Verify current repo state.** Confirm the actual current HEAD, build proof, smoke tests, and outstanding warnings before acting.
> 3. **Add a public surface registry.** Define which headers, commands, schemas, protocols, and manifests are frozen/stable/internal.
> 4. **Add dependency-edge enforcement.** Convert intended module direction into a machine-readable contract.
> 5. **Add tuple build contracts and generated local presets.** Move build truth out of ad hoc preset names.
> 6. **Add ABI/header conformance tests.** Public the referenced source.
> 7. **Add the referenced source.** Old fixtures should load; unknown fields should round-trip; reserved IDs should be checked.
> 8. **Continue the referenced source.** Resolve `the referenced source` versus `the referenced source`, content pack taxonomy, and stale pack authority references.
> 9. **Document the replacement protocol.** Make whole-module rewrites safe through black-box conformance and replay/hash comparison.
> 10. **Feed this report into the master spec book aggregator.** Preserve uncertainty labels and avoid merging suggestions as decisions.
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

> - Which recommendations are decisions versus advice?
> - Write the implementation prompt for public surface registry.
> - Write the implementation prompt for tuple-driven build contracts.
> - Verify the current repo state and compare against this report.
> - Convert this chat into spec-book requirements only.
> - Build an aggregator packet from multiple chat reports.
>
> [Source: In Chat Reader Dominium Build And Future Proofing Architecture]

> C89/C++98 canon, deterministic/no hidden behavior, per-floor artifacts, no CRT mixing, tuple-driven builds, public surface registry, replacement protocol, schema compatibility harness, and the warning that recommendations are not accepted canon yet.
>
> [Source: In Chat Reader Dominium Build And Future Proofing Architecture]

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

> 1. Which recommendations here should become binding canon?
> 2. Which should remain advisory until more evidence exists?
> 3. Write the implementation prompt for `STRUCTURE-01: Public Surface Registry`.
> 4. Write the implementation prompt for `BUILD-CONTRACT-01: Tuple Build Contracts and Machine Probe`.
> 5. Verify the current repo state and compare it to the older POST-CONVERGE-09 state.
> 6. Turn the candidate requirements into a formal spec-book chapter.
> 7. Merge this package with another old-chat preservation package.
> 8. Extract only the build/toolchain requirements from this report.
> 9. Extract only the modularity/replacement/public surface requirements from this report.
> 10. Identify contradictions between this chat and later Dominium decisions.
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

The woven passages above come from 56 source documents and 96 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is aligning scientific ambition, authored content, and deterministic constraints.

Where this leaves us: worldgen work needs source verification, contracts, and queue scope before implementation.
