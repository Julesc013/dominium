# Dominium Source-Woven Project Book

A human-readable compilation of current docs, archive context, and conversation source passages

Status: DERIVED. Authority Class: advisory_synthesis. Promotion Status: not_promoted.

This book is a source-woven reader. It uses original human-readable source passages from current docs, archive reports, and the conversation corpus, then places those passages into topic chapters with light editorial bridges. It is not canon, it does not promote archive claims, and it does not open blocked work.

## How to Read This Book

Read the chapters as a guided compilation. The quoted passages preserve source wording where it helps the reader understand the project. The short bridges explain why a group of passages belongs together and where authority boundaries matter.

## Authority and Source Rules

Current repository authority still comes from canon, glossary, AGENTS, contract and schema law, current queue state, validated repo artifacts, and current docs according to the authority order. Archive and conversation material remain historical or advisory unless a later explicit promotion task changes that.

## Reading Paths

For a quick orientation, read Part I and Chapter 23. For architecture, read Parts II and III. For simulation and world model context, read Part IV. For decisions, blocked scope, and next work, read Part V. Use the source map PDF when you need full paths, block IDs, or source-family coverage.

The conversation archive is represented across the woven chapters rather than dumped as transcripts. Machine-readable packets, manifests, and registers are represented in the source map and reports, not as main-body prose.


# Part I - The Project


## 1. Dominium in One View

Dominium is easiest to read as a layered project: a deterministic substrate, an official domain layer, product surfaces, and governed tooling all held apart by authority rules.

The current sources set the initial boundary.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

The archive then widens the view without changing the authority order.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

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

> Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> 1. context loaded,
> 2. top active priorities,
> 3. key constraints,
> 4. open questions,
> 5. contradictions or uncertainties,
> 6. recommended next action.
>
> [Source: Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture]

The woven passages above come from 53 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The useful tension is that the project is ambitious, but current permission remains narrow.

Where this leaves us: Dominium is a broad project only because its layers stay disciplined.


## 2. Why the Project Exists

The project exists to make complex worlds emerge from lawful process rather than from ad hoc scripting.

Current orientation material describes a project built around refusal, evidence, and deterministic process.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

Conversation material supplies the larger product and simulation desire behind that machinery.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
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

> Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> 1. context loaded,
> 2. top active priorities,
> 3. key constraints,
> 4. open questions,
> 5. contradictions or uncertainties,
> 6. recommended next action.
>
> [Source: Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture]

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

The woven passages above come from 51 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is between long-horizon intent and the present queue.

Where this leaves us: the ambition is preserved, but future feature work still needs a smaller lawful task.


## 3. The Core Mental Model

The core mental model is the separation of truth, perception, rendering, and operation.

Current doctrine makes truth authoritative and mutation process-bound.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

The conversations repeatedly test that model against Workbench, UI, providers, packs, and world simulation.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
>
> [Source: DOCS Current Project Picture]

> External platform, SDK, renderer, language baseline, release, provider, package runtime, and implementation claims must be rechecked. The synthesis should use those old claims to identify questions, not to assert current facts.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The most important caution is that only DECISION-01 is clearly a user-stated constraint in this visible chat. The other items are strong recommendations produced in response to the user's requests for best practice; they should not be merged into canon unless the user later accepts them.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> C89/C++98 canon, deterministic/no hidden behavior, per-floor artifacts, no CRT mixing, tuple-driven builds, public surface registry, replacement protocol, schema compatibility harness, and the warning that recommendations are not accepted canon yet.
>
> [Source: In Chat Reader Dominium Build And Future Proofing Architecture]

The woven passages above come from 52 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The risk appears whenever a convenience layer is allowed to become an authority layer.

Where this leaves us: every later surface has to say whether it owns truth, observes truth, presents truth, or operates the repo.


## 4. Current Truth and Historical Evidence

The docs corpus is not a flat library. It contains current truth, historical context, derived reports, and advisory conversation evidence.

Current authority starts with canon, glossary, AGENTS, contracts, schema law, queue state, and validated repo artifacts.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

Archive and conversation material are valuable because they preserve design memory and unresolved decisions.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
>
> [Source: DOCS Current Project Picture]

> - Conversation files represented: 761
> - Generated conversation reports represented: 131
> - Conversation export files represented: 10
>
> [Source: DOCS Conversation Corpus Integration]

> | Surface | Role |
> | --- | --- |
> | the referenced source/** | derived synthesis and project picture |
> | the referenced source/** | decision docket |
> | the referenced source/** | promotion review backlog |
> | the referenced source/** | conversation-vs-repo crosswalk |
> | the referenced source/** | contradictions, staleness, uncertainty |
> | the referenced source/** | conversation book bundle |
>
> [Source: DOCS Conversation Corpus Integration]

> | Blocked Scope | Authority Source | Matching Docs Paths | Examples | Disposition |
> | --- | --- | --- | --- | --- |
> | broad_workbench_ui | .aide/queue/current.toml | 1 | the referenced source | blocked_by_current_queue |
> | runtime_module_loader | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
>
> [Source: DOCS Blocked Scope Alignment]

> | Decision ID | Source/Finding | Question | Decision Type | Risk | Recommended Default |
> | --- | --- | --- | --- | --- | --- |
>
> [Source: DOCS Decision Docket]

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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

The woven passages above come from 53 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is accidental promotion: a polished old idea can sound current when it is not.

Where this leaves us: use the archive to understand the project, then promote only through explicit review.


# Part II - Architecture


## 5. The System Stack

The system stack is a set of responsibility boundaries rather than a file listing.

Current docs separate substrate, domain meaning, products, runtime services, contracts, content, tools, and documentation.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

Older sources describe the same stack with more future-facing language.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
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

> Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> 1. context loaded,
> 2. top active priorities,
> 3. key constraints,
> 4. open questions,
> 5. contradictions or uncertainties,
> 6. recommended next action.
>
> [Source: Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture]

> - Which recommendations are decisions versus advice?
> - Write the implementation prompt for public surface registry.
> - Write the implementation prompt for tuple-driven build contracts.
> - Verify the current repo state and compare against this report.
> - Convert this chat into spec-book requirements only.
> - Build an aggregator packet from multiple chat reports.
>
> [Source: In Chat Reader Dominium Build And Future Proofing Architecture]

The woven passages above come from 54 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that adjacent roots can look interchangeable even when their authority is different.

Where this leaves us: growth should extend the stack without collapsing ownership.


## 6. Domino, Dominium, Runtime, Products, and Tools

Domino and Dominium are linked, but they are not synonyms.

Current sources make Domino the reusable deterministic substrate and Dominium the official product/domain layer.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

The archive adds client, server, launcher, setup, Workbench, and automation ambitions.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
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

> Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> 1. context loaded,
> 2. top active priorities,
> 3. key constraints,
> 4. open questions,
> 5. contradictions or uncertainties,
> 6. recommended next action.
>
> [Source: Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture]

The woven passages above come from 52 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is product ambition versus substrate authority.

Where this leaves us: products and tools can project or operate the substrate, but they do not replace it.


## 7. Law, Capability, Refusal, and Evidence

Law and capability are how the project turns possibility into allowed action.

Current doctrine requires explicit refusal and no hidden fallback behavior.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

Archive passages show the same rule pressed into packs, providers, Workbench, assistant workflows, and future product surfaces.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
>
> [Source: DOCS Current Project Picture]

> This map combines current repo orientation with conversation-derived design intent. When they differ, current repo authority wins.
>
> [Source: Full Project Picture V0]

> | Blocked Scope | Authority Source | Matching Docs Paths | Examples | Disposition |
> | --- | --- | --- | --- | --- |
> | broad_workbench_ui | .aide/queue/current.toml | 1 | the referenced source | blocked_by_current_queue |
> | runtime_module_loader | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
>
> [Source: DOCS Blocked Scope Alignment]

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The most important caution is that only DECISION-01 is clearly a user-stated constraint in this visible chat. The other items are strong recommendations produced in response to the user's requests for best practice; they should not be merged into canon unless the user later accepts them.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

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

> **Chat label:** Dominium Build and Future-Proofing Architecture
> **Date anchor:** 2026-05-27 Australia/Melbourne
> **Scope:** This report covers the visible conversation and the preservation task that produced the accompanying handoff files. It does **not** claim complete access to any earlier hidden or retired chats.
> **Epistemic note:** Items marked **FACT** were explicitly present in this conversation or in the provided/pasted material. Items marked **INFERENCE** are reasonable conclusions from the discussion. Items marked **RECOMMENDATION** are assistant proposals that should not be treated as accepted Dominium canon unless the user later confirms them.
>
> [Source: Accompanying Human Readable Detailed Conversation Report]

The woven passages above come from 55 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is making refusal clear without making the system opaque.

Where this leaves us: a future feature should be able to name its authority source, refusal path, and evidence trail.


## 8. Determinism, Replay, and Provenance

Determinism is both a runtime rule and an audit strategy.

Current sources require named randomness, stable ordering, replay equivalence, and provenance.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

The archive adds proof gates, evidence artifacts, portability concerns, and release trust.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The second major tradeoff was between freezing too much and freezing too little. Freezing implementations would block refactors; freezing nothing would destroy compatibility. The recommended compromise was to freeze public contracts and conformance tests while allowing implementations to be replaced behind them.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> 1. context loaded,
> 2. top active priorities,
> 3. key constraints,
> 4. open questions,
> 5. contradictions or uncertainties,
> 6. recommended next action.
>
> [Source: Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture]

The woven passages above come from 52 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that some attractive features become unsafe if they cannot explain their replay behavior.

Where this leaves us: validation is part of architecture, not a later checklist.


## 9. Contracts, Schemas, Packs, and Compatibility

Contracts and schemas preserve public meaning across time.

Current material requires explicit identity, versioning, migration, refusal, and compatibility discipline.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
>
> [Source: Dominium Agent Governance]

> - optional content and capabilities must remain pack- and registry-driven
> - missing packs require explicit refusal or degradation rather than hidden fallback magic
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

Conversation sources expand that into provider choices, package composition, modding surfaces, and release identity.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The audit layer contains review triggers, not resolved contradictions. The main risk classes are conversation claims against current queue restrictions, stale external/platform claims, old the referenced source, and conversation-vs-conversation disagreements.
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

> Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> 1. context loaded,
> 2. top active priorities,
> 3. key constraints,
> 4. open questions,
> 5. contradictions or uncertainties,
> 6. recommended next action.
>
> [Source: Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture]

> - Which recommendations are decisions versus advice?
> - Write the implementation prompt for public surface registry.
> - Write the implementation prompt for tuple-driven build contracts.
> - Verify the current repo state and compare against this report.
> - Convert this chat into spec-book requirements only.
> - Build an aggregator packet from multiple chat reports.
>
> [Source: In Chat Reader Dominium Build And Future Proofing Architecture]

The woven passages above come from 57 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is separating current contract law from future packaging ambition.

Where this leaves us: packs are current doctrine; provider/package runtime claims still need review.


# Part III - Product and Operator Surfaces


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


## 11. UI, Renderer, Native GUI, and Presentation Boundaries

Presentation is downstream of truth and perception.

Current doctrine says rendering presents; it does not mutate truth.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

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

The conversation archive contains extensive UI, renderer, native GUI, and universe-exploration intent.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
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

> Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> 1. context loaded,
> 2. top active priorities,
> 3. key constraints,
> 4. open questions,
> 5. contradictions or uncertainties,
> 6. recommended next action.
>
> [Source: Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture]

The woven passages above come from 54 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that those ideas are useful precisely because they remain blocked until the queue opens them.

Where this leaves us: future renderer work must protect truth/perception/render separation before it becomes product work.


## 12. AIDE, Codex, Automation, and Repo Governance

AIDE, Codex, and automation are governed helpers, not alternate project authorities.

AGENTS defines bounded work, validation expectations, protected paths, and forbidden moves.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

The archive records repeated work to make assistant operation portable, evidence-rich, and reviewable.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
>
> [Source: DOCS Current Project Picture]

> - Conversation files represented: 761
> - Generated conversation reports represented: 131
> - Conversation export files represented: 10
>
> [Source: DOCS Conversation Corpus Integration]

> | Surface | Role |
> | --- | --- |
> | the referenced source/** | derived synthesis and project picture |
> | the referenced source/** | decision docket |
> | the referenced source/** | promotion review backlog |
> | the referenced source/** | conversation-vs-repo crosswalk |
> | the referenced source/** | contradictions, staleness, uncertainty |
> | the referenced source/** | conversation book bundle |
>
> [Source: DOCS Conversation Corpus Integration]

> | Blocked Scope | Authority Source | Matching Docs Paths | Examples | Disposition |
> | --- | --- | --- | --- | --- |
> | broad_workbench_ui | .aide/queue/current.toml | 1 | the referenced source | blocked_by_current_queue |
> | runtime_module_loader | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
>
> [Source: DOCS Blocked Scope Alignment]

> | Decision ID | Source/Finding | Question | Decision Type | Risk | Recommended Default |
> | --- | --- | --- | --- | --- | --- |
>
> [Source: DOCS Decision Docket]

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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

The woven passages above come from 53 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that generated outputs can look authoritative because they are polished.

Where this leaves us: automation may expose evidence and perform bounded edits, but it cannot silently become canon.


## 13. Documentation, Archive, and Conversation Corpus

The archive is the project's memory system.

Current docs-corpus outputs classify the tree, authority layers, drift, decisions, and promotion candidates.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

The conversation corpus adds preserved design intent, old handoffs, contradictions, reader pages, and reports.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
>
> [Source: DOCS Current Project Picture]

> - Conversation files represented: 761
> - Generated conversation reports represented: 131
> - Conversation export files represented: 10
>
> [Source: DOCS Conversation Corpus Integration]

> | Surface | Role |
> | --- | --- |
> | the referenced source/** | derived synthesis and project picture |
> | the referenced source/** | decision docket |
> | the referenced source/** | promotion review backlog |
> | the referenced source/** | conversation-vs-repo crosswalk |
> | the referenced source/** | contradictions, staleness, uncertainty |
> | the referenced source/** | conversation book bundle |
>
> [Source: DOCS Conversation Corpus Integration]

> | Blocked Scope | Authority Source | Matching Docs Paths | Examples | Disposition |
> | --- | --- | --- | --- | --- |
> | broad_workbench_ui | .aide/queue/current.toml | 1 | the referenced source | blocked_by_current_queue |
> | runtime_module_loader | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
>
> [Source: DOCS Blocked Scope Alignment]

> | Decision ID | Source/Finding | Question | Decision Type | Risk | Recommended Default |
> | --- | --- | --- | --- | --- | --- |
>
> [Source: DOCS Decision Docket]

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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

The woven passages above come from 53 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is turning that memory into useful reading without making it current truth.

Where this leaves us: ordinary readers get woven chapters; auditors get source maps and appendices.


# Part IV - Simulation and World Model


## 14. Reality, Space, Time, Scale, and Existence

Reality, space, time, scale, and existence are simulation concerns before they are presentation concerns.

Current law supplies deterministic process, event-driven change, truth/perception separation, and provenance.

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - do not add or preserve hardcoded runtime mode branches
> - express behavior composition through profiles, bundles, law surfaces, and explicit constraints
>
> [Source: Dominium Agent Governance]

> - authoritative truth mutation must occur through lawful deterministic Process execution
> - UI, render, operator, tooling, or convenience layers must not mutate truth directly
>
> [Source: Dominium Agent Governance]

> - schema or compatibility work: `schema/**`, `the referenced source/**`, compat metadata
> - release or control-plane work: `the referenced source/**`, `the referenced source`, release and update registries
> - runtime extraction work: relevant runtime roots plus ownership review and bridge law
> - bridge or ownership-sensitive work: `the referenced source` before binding to overlapping roots
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

> Workbench is the richest operator environment for validation, evidence,
> inspection, and later editing workflows. It consumes the same contracts and
> services as other products; it is not an authority layer.
>
> [Source: Dominium / Domino]

> - Capability grants permission to attempt; law determines accept/refuse/transform.
> - Authority does not bypass law.
> - Refusals are lawful outcomes and MUST be explicit, deterministic, and auditable.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

The archive adds visitability, temporal resilience, large-scale representation, and 2038-style timekeeping concerns.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

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

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
>
> [Source: DOCS Current Project Picture]

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

> - Whether all recommended structural tasks should be implemented now is not established.
> - Whether the proposed build tuple naming scheme should become official is not yet established.
> - Whether the current top-level structure is final-final or merely best current target remains subject to user decision and repo evidence.
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

The woven passages above come from 52 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that long-horizon world design can outrun present domain authority.

Where this leaves us: future domain work should classify claims before attaching them to gameplay or rendering.


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


## 16. Civilization, Economy, Logistics, and Institutions

Civilization-scale simulation is one of the clearest ambitions in the conversation corpus.

Current orientation names production, logistics, economics, settlement, trust, communication, and institutions as important phenomena.

> - do not add or preserve hardcoded runtime mode branches
> - express behavior composition through profiles, bundles, law surfaces, and explicit constraints
>
> [Source: Dominium Agent Governance]

> - schema or compatibility work: `schema/**`, `the referenced source/**`, compat metadata
> - release or control-plane work: `the referenced source/**`, `the referenced source`, release and update registries
> - runtime extraction work: relevant runtime roots plus ownership review and bridge law
> - bridge or ownership-sensitive work: `the referenced source` before binding to overlapping roots
>
> [Source: Dominium Agent Governance]

> - `planning`: sequencing, checkpoints, inventories, dependency maps, gates, and continuity work
> - `doctrine_spec`: normative constitutional, contract, or specification work
> - `governance`: agent, operator, instruction, refusal, and review-surface work
> - `semantic_domain`: reality, domain, capability, representation, formalization, or bridge work
> - `runtime_platform`: kernel, component, event, service, persistence, sandbox, or platform-boundary work
> - `release_control_plane`: release, build, versioning, identity, trust, archive, publication, or control-plane work
> - `packaging_checkpointing`: bundle, report, manifest, and checkpoint-curation work
> - `validation_audit`: verification, consistency, evidence, audit, and proof work
> - `refactor_convergence`: physical convergence, replacement, merge-later, or structure-normalization work
>
> [Source: Dominium Agent Governance]

> The project is about invention, production, logistics, economics, settlement,
> trust, communication, and institutional power emerging from lawful simulation
> rather than scripted outcomes. Commands, processes, packs, capabilities,
> diagnostics, evidence, and replay proof are first-class surfaces. Invalid action
> must refuse explicitly; hidden fallback behavior is not part of the model.
>
> [Source: Dominium / Domino]

> law surfaces, and constraints, not hardcoded runtime mode forks.
> - Explicit refusal: unsupported or invalid transitions return deterministic,
>
> [Source: Dominium / Domino]

> Content is authored data, not runtime law. Packs and registries describe optional
> content, capabilities, compatibility, activation, and distribution surfaces.
> Missing optional content must degrade or refuse explicitly.
>
> [Source: Dominium / Domino]

> - Runtime behavior MUST resolve from profile data (`ExperienceProfile`, `LawProfile`, `ParameterBundle`, optional `MissionSpec` constraints).
> - Hardcoded mode booleans/branches (for example `*_mode` runtime forks) are forbidden.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - New content and capability surfaces integrate through packs and registries.
> - Packs are data-only and namespaced; executable code inside packs is forbidden.
> - Missing optional packs MUST produce deterministic refusal or deterministic degradation.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

Conversation passages add seed civilizations, infrastructure, signals, institutions, power, and social feedback loops.

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

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

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

> - Label: FACT
> - Objective: Produce downloadable, shareable, reusable report files for this individual old chat.
> - Background: The current user request asks to turn the existing Context Transfer Packet into a final downloadable package for this individual chat.
> - Current state: Active in this response; package generated from the visible chat and previous transfer packet.
> - Desired end state: Markdown/YAML/ZIP package saved and usable for later aggregation.
> - Importance: highest
> - Decisions made: Use chat-specific scope; create report/YAML/aggregator/register/brief/audit/manifest files; create ZIP if tools are available.
> - Decisions pending: None for package generation, except residual manual verification after download.
> - Pending tasks: TASK-01, TASK-02.
> - Constraints: CONSTRAINT-01 through CONSTRAINT-05, CONSTRAINT-19, CONSTRAINT-20.
> - Dependencies: Visible chat context and the previously generated Context Transfer Packet.
> - Timeline / sequencing: Current final task after OC-1 and context transfer packet.
> - Blockers: None for file creation; full historical accuracy limited by skipped context.
> - Risks: RISK-01, RISK-09, RISK-10.
> - Artifacts: This report package files.
> - Success criteria: Downloadable Markdown/YAML/ZIP package exists and is safe for aggregation with caveats.
> - Recommended next action: Download and store the package; use it to bootstrap new chat.
> - Verification needed: Manual review of generated files and missing skipped-context gaps.
> - Confidence: high
> - Carry-forward priority: highest
>
> [Source: Full Chat Report Dominium Architecture I]

> - Label: PROJECT-CONTEXT / FACT
> - Objective: Carry forward the architecture of the Dominium deterministic simulation/game project.
> - Background: Dominium Game is the larger project context; the visible chat focuses on architecture/spec/coding-prep, not a whole project summary.
> - Current state: Architecture/specification phase; many implementation-spec prompts generated.
> - Desired end state: Complete source tree implemented and validated from specs.
> - Importance: highest
> - Decisions made: Determinism, UTF-8, semantic versioning, per-file specs, strict layers.
> - Decisions pending: Platform support tiers and canonical APIs.
> - Pending tasks: TASK-10, TASK-21, TASK-22.
> - Constraints: CONSTRAINT-07 through CONSTRAINT-17.
> - Dependencies: All downstream workstreams.
> - Timeline / sequencing: Active throughout the chat.
> - Blockers: Unfinished specs and contradictions.
> - Risks: RISK-02 through RISK-07, RISK-11 through RISK-15.
> - Artifacts: Spec v3, devspecs, docs.
> - Success criteria: Project can proceed to implementation and deterministic tests.
> - Recommended next action: Either continue specs or canonicalise before coding.
> - Verification needed: External support, legal docs, Codex capabilities.
> - Confidence: high
> - Carry-forward priority: highest
>
> [Source: Full Chat Report Dominium Architecture I]

> - Label: FACT
> - Objective: Create one .txt implementation-spec prompt per repo file for Codex 5.1 Max.
> - Background: See inventory and registers; this workstream is established by the visible file list or generated specs.
> - Current state: Generated through the referenced source; many later files remain pending.
> - Desired end state: Complete devspec tree covering every listed file.
> - Importance: highest
> - Decisions made: See decision register for related decisions.
> - Decisions pending: See open questions and tasks.
> - Pending tasks: See task register.
> - Constraints: See constraint register.
> - Dependencies: Related generated specs and upstream the referenced source.
> - Timeline / sequencing: Follows strict file order.
> - Blockers: Unresolved conflicts or incomplete generation if noted.
> - Risks: See risk register.
> - Artifacts: See artifact ledger.
> - Success criteria: Complete, consistent, Codex-ready specs and eventual implementation.
> - Recommended next action: Continue strict order or canonicalise as appropriate.
> - Verification needed: Verify external assumptions and inspect skipped/referenced docs if needed.
> - Confidence: high
> - Carry-forward priority: high
>
> [Source: Full Chat Report Dominium Architecture I]

> - FACT: This report covers only the visible content of the old chat labelled **Dominium Architecture II** and the already-produced Context Transfer Packet in that chat.
> - FACT: It should not be treated as a whole-Project summary.
> - FACT: Uncertain items must not be promoted to facts during future aggregation.
> - FACT: Direct user statements outrank assistant suggestions.
> - FACT: Assistant suggestions are only final when accepted by the user or clearly continued from by the user.
> - FACT: External-world/toolchain/API/legal facts require verification before future use.
> - FACT: This report is intended to be combined later with similar reports from other retired chats.
>
> [Source: Full Chat Report Dominium Architecture Ii]

> - Label: FACT
> - Objective: Consolidate architecture and Codex-facing instructions into a coherent source of truth.
> - Background: The chat identified spec drift from earlier generated volumes and moved toward binding docs and codegen addenda.
> - Current state: V4 replacements for BUILDING.md, SPEC_CORE.md, DATA_FORMATS.md, and DIRECTORY_CONTEXT.md were generated in this chat; actual on-disk application is unverified.
> - Desired end state: The four docs plus the referenced source.
> - Importance: Blocks reliable implementation and future aggregation.
> - Decisions made:
> - the referenced source, not a new CODEGEN_ADDENDUM.md.
> - Actual user-provided file names and tree win over earlier generic names.
> - Decisions pending:
> - Verify whether generated V4 docs were applied to disk.
> - Reconcile any lingering references to /the referenced source.
> - Pending tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05
> - Constraints: CONSTRAINT-07, CONSTRAINT-11, CONSTRAINT-12
> - Dependencies: ARTIFACT-19, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22, ARTIFACT-23
> - Timeline / sequencing: Immediate, before Codex implementation.
> - Blockers:
> - Actual repo state unknown.
> - Risks: RISK-01, RISK-02
> - Artifacts: ARTIFACT-19, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22, ARTIFACT-23
> - Success criteria:
> - Four key docs align with actual file tree and dev addenda.
> - Recommended next action: Run the Codex consistency pass or manually verify the four docs.
> - Verification needed: See verification queue where applicable.
> - Confidence: high
> - Carry-forward priority: P0
>
> [Source: Full Chat Report Dominium Architecture Ii]

The woven passages above come from 47 source documents and 96 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that those ideas are rich but mostly not yet implementation scope.

Where this leaves us: they define pressure that the architecture should be able to bear later.


## 17. Content, Providers, Modding, and Data-Driven Extension

Content extension is supposed to be governed, not magical.

Current doctrine favors packs, registries, explicit capabilities, compatibility rules, and deterministic refusal.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
>
> [Source: Dominium Agent Governance]

> - optional content and capabilities must remain pack- and registry-driven
> - missing packs require explicit refusal or degradation rather than hidden fallback magic
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

The archive expands this into providers, package runtime, open-source provider choices, authoring, and modding workflows.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
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

> Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> - Which recommendations are decisions versus advice?
> - Write the implementation prompt for public surface registry.
> - Write the implementation prompt for tuple-driven build contracts.
> - Verify the current repo state and compare against this report.
> - Convert this chat into spec-book requirements only.
> - Build an aggregator packet from multiple chat reports.
>
> [Source: In Chat Reader Dominium Build And Future Proofing Architecture]

The woven passages above come from 56 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that pack doctrine is current while provider/package runtime is not broadly open.

Where this leaves us: extension work should separate data-driven content from blocked runtime-provider ambitions.


# Part V - Decisions and Roadmap


## 18. What Is Settled

Some principles are settled strongly enough to shape every later task.

Current authority supports process-only mutation, profiles over mode flags, pack-driven integration, truth/perception/render separation, explicit refusal, and validation discipline.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

Conversation evidence often reinforces those decisions by showing the same pressure from different directions.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
>
> [Source: DOCS Current Project Picture]

> - Conversation files represented: 761
> - Generated conversation reports represented: 131
> - Conversation export files represented: 10
>
> [Source: DOCS Conversation Corpus Integration]

> | Surface | Role |
> | --- | --- |
> | the referenced source/** | derived synthesis and project picture |
> | the referenced source/** | decision docket |
> | the referenced source/** | promotion review backlog |
> | the referenced source/** | conversation-vs-repo crosswalk |
> | the referenced source/** | contradictions, staleness, uncertainty |
> | the referenced source/** | conversation book bundle |
>
> [Source: DOCS Conversation Corpus Integration]

> | Blocked Scope | Authority Source | Matching Docs Paths | Examples | Disposition |
> | --- | --- | --- | --- | --- |
> | broad_workbench_ui | .aide/queue/current.toml | 1 | the referenced source | blocked_by_current_queue |
> | runtime_module_loader | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
>
> [Source: DOCS Blocked Scope Alignment]

> | Decision ID | Source/Finding | Question | Decision Type | Risk | Recommended Default |
> | --- | --- | --- | --- | --- | --- |
>
> [Source: DOCS Decision Docket]

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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

The woven passages above come from 53 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that agreement in archive material still does not change the authority source.

Where this leaves us: settled principles should simplify later review, not bypass it.


## 19. What Is Still Open

Open decisions are the reason this material remains evidence rather than doctrine.

Current reports identify user decisions, future queue decisions, and source verification needs.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> - respect explicit schema identity, version, stability, migration, and refusal obligations
> - do not perform silent migrations or compatibility reinterpretation
> - update contract-facing docs when behavior or compatibility meaning changes
>
> [Source: Dominium Agent Governance]

> - `planning`: sequencing, checkpoints, inventories, dependency maps, gates, and continuity work
> - `doctrine_spec`: normative constitutional, contract, or specification work
> - `governance`: agent, operator, instruction, refusal, and review-surface work
> - `semantic_domain`: reality, domain, capability, representation, formalization, or bridge work
> - `runtime_platform`: kernel, component, event, service, persistence, sandbox, or platform-boundary work
> - `release_control_plane`: release, build, versioning, identity, trust, archive, publication, or control-plane work
> - `packaging_checkpointing`: bundle, report, manifest, and checkpoint-curation work
> - `validation_audit`: verification, consistency, evidence, audit, and proof work
> - `refactor_convergence`: physical convergence, replacement, merge-later, or structure-normalization work
>
> [Source: Dominium Agent Governance]

> repo documentation.
> - `tests/`: contract, invariant, smoke, integration, fixture, and proof suites.
> - `tools/`: repo-only validation, packaging, migration, release, audit, and
>
> [Source: Dominium / Domino]

> Old docs are retained for provenance, but canon, glossary, AGENTS, active
> contracts, current queue state, and reviewed audits outrank stale references.
>
> [Source: Dominium / Domino]

Archive and conversation passages often offer plausible answers, but not final authority.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
>
> [Source: DOCS Current Project Picture]

> - Conversation files represented: 761
> - Generated conversation reports represented: 131
> - Conversation export files represented: 10
>
> [Source: DOCS Conversation Corpus Integration]

> | Surface | Role |
> | --- | --- |
> | the referenced source/** | derived synthesis and project picture |
> | the referenced source/** | decision docket |
> | the referenced source/** | promotion review backlog |
> | the referenced source/** | conversation-vs-repo crosswalk |
> | the referenced source/** | contradictions, staleness, uncertainty |
> | the referenced source/** | conversation book bundle |
>
> [Source: DOCS Conversation Corpus Integration]

> | Blocked Scope | Authority Source | Matching Docs Paths | Examples | Disposition |
> | --- | --- | --- | --- | --- |
> | broad_workbench_ui | .aide/queue/current.toml | 1 | the referenced source | blocked_by_current_queue |
> | runtime_module_loader | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
>
> [Source: DOCS Blocked Scope Alignment]

> | Decision ID | Source/Finding | Question | Decision Type | Risk | Recommended Default |
> | --- | --- | --- | --- | --- | --- |
>
> [Source: DOCS Decision Docket]

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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

The woven passages above come from 53 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is between preserving useful answers and avoiding silent promotion.

Where this leaves us: the book should help readers identify decisions before trying to resolve them.


## 20. What Is Blocked

Blocked scope is part of the project picture.

Current queue state does not open broad Workbench UI, renderer implementation, native GUI, provider runtime, package runtime, gameplay, or release publication.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

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

> - `contracts/`: machine-readable, version-pinned, compatibility-sensitive law.
> - `content/`: authored packs, profiles, datasets, fixtures-as-content, assets,
>
> [Source: Dominium / Domino]

> repo documentation.
> - `tests/`: contract, invariant, smoke, integration, fixture, and proof suites.
> - `tools/`: repo-only validation, packaging, migration, release, audit, and
>
> [Source: Dominium / Domino]

Historical sources often talk about those areas because they preserve product intent.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> 1. context loaded,
> 2. top active priorities,
> 3. key constraints,
> 4. open questions,
> 5. contradictions or uncertainties,
> 6. recommended next action.
>
> [Source: Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture]

The woven passages above come from 54 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that future usefulness can be mistaken for present permission.

Where this leaves us: every later prompt should state blocked areas before implementation language.


## 21. Contradictions and Drift

The corpus preserves drift because it preserves time.

Current authority order is what prevents old planning, generated summaries, and conversation claims from overriding present repo truth.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
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

Archive passages reveal conflicts around scope, release, provider boundaries, renderer readiness, and old architecture language.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
>
> [Source: DOCS Current Project Picture]

> - Conversation files represented: 761
> - Generated conversation reports represented: 131
> - Conversation export files represented: 10
>
> [Source: DOCS Conversation Corpus Integration]

> | Surface | Role |
> | --- | --- |
> | the referenced source/** | derived synthesis and project picture |
> | the referenced source/** | decision docket |
> | the referenced source/** | promotion review backlog |
> | the referenced source/** | conversation-vs-repo crosswalk |
> | the referenced source/** | contradictions, staleness, uncertainty |
> | the referenced source/** | conversation book bundle |
>
> [Source: DOCS Conversation Corpus Integration]

> | Blocked Scope | Authority Source | Matching Docs Paths | Examples | Disposition |
> | --- | --- | --- | --- | --- |
> | broad_workbench_ui | .aide/queue/current.toml | 1 | the referenced source | blocked_by_current_queue |
> | runtime_module_loader | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
>
> [Source: DOCS Blocked Scope Alignment]

> | Decision ID | Source/Finding | Question | Decision Type | Risk | Recommended Default |
> | --- | --- | --- | --- | --- | --- |
>
> [Source: DOCS Decision Docket]

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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

The woven passages above come from 53 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that smoothing those conflicts would make the book easier but less accurate.

Where this leaves us: contradictions are review signals, not failures to hide.


## 22. Prerequisites and Sequencing

Sequencing is the discipline that keeps ambition useful.

Current state points toward narrow command/result, package-mount, projection conformance, validation, and review work before broad feature expansion.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
> Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
> Binding Sources: `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`, `the referenced source`
>
> [Source: Dominium Agent Governance]

> - generated mirrors or vendor-specific instruction surfaces
> - the natural-language task bridge
> - the XStack task catalog
> - MCP exposure contracts
> - the final hardened agent safety policy
>
> [Source: Dominium Agent Governance]

> AIDE and Codex are repo/control-plane harnesses and bounded patch execution
> surfaces. They help operate the repository; they do not replace canon,
> contracts, validation, or evidence.
>
> [Source: Dominium / Domino]

> - `contracts/`: machine-readable, version-pinned, compatibility-sensitive law.
> - `content/`: authored packs, profiles, datasets, fixtures-as-content, assets,
>
> [Source: Dominium / Domino]

> repo documentation.
> - `tests/`: contract, invariant, smoke, integration, fixture, and proof suites.
> - `tools/`: repo-only validation, packaging, migration, release, audit, and
>
> [Source: Dominium / Domino]

> - Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
> - Required updates: documentation surface exists, but current canon ownership is not explicit
> - Cross-check with: `the referenced source` and `the referenced source`.
>
> [Source: Dominium Documentation]

Historical roadmaps add useful orderings around Workbench, release, providers, docs promotion, and domains.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
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

> * Completeness rating: 4/5 for visible chat.
> * Reliability rating: 4/5 for visible chat; lower for implied older context.
> * Human-readability rating: 4/5.
> * Aggregation-readiness rating: 4/5 with caveats.
> * Main uncertainty sources: inaccessible older full transcript, evolving repo state, unaccepted recommendations, potentially stale external toolchain facts.
> * Manual review before merge: Yes. The user should mark which recommendations become canon.
>
> [Source: Verification And Audit Dominium Build And Future Proofing Architecture]

> 1. context loaded,
> 2. top active priorities,
> 3. key constraints,
> 4. open questions,
> 5. contradictions or uncertainties,
> 6. recommended next action.
>
> [Source: Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture]

The woven passages above come from 54 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is that the same future may be desirable in several orders but only one order may be safe now.

Where this leaves us: future tasks should name prerequisites before changing behavior.


## 23. Recommended Next Steps

The next best work is selective review and controlled promotion, not another dump.

Current authority permits derived documentation and narrow governed tasks, not sweeping promotion.

> - Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
> - Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
> - Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
> - Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
>
> [Source: Dominium Agent Governance]

> - Truth is authoritative state.
> - Perception is a law/authority/lens-filtered projection.
> - Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> - Canonical commit key: `(phase_id, task_id, sub_index)`.
> - Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.
>
> [Source: Dominium Constitutional Architecture & Execution Contract V1]

> Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
>
> [Source: Foundation Lock]

> - respect explicit schema identity, version, stability, migration, and refusal obligations
> - do not perform silent migrations or compatibility reinterpretation
> - update contract-facing docs when behavior or compatibility meaning changes
>
> [Source: Dominium Agent Governance]

> - `planning`: sequencing, checkpoints, inventories, dependency maps, gates, and continuity work
> - `doctrine_spec`: normative constitutional, contract, or specification work
> - `governance`: agent, operator, instruction, refusal, and review-surface work
> - `semantic_domain`: reality, domain, capability, representation, formalization, or bridge work
> - `runtime_platform`: kernel, component, event, service, persistence, sandbox, or platform-boundary work
> - `release_control_plane`: release, build, versioning, identity, trust, archive, publication, or control-plane work
> - `packaging_checkpointing`: bundle, report, manifest, and checkpoint-curation work
> - `validation_audit`: verification, consistency, evidence, audit, and proof work
> - `refactor_convergence`: physical convergence, replacement, merge-later, or structure-normalization work
>
> [Source: Dominium Agent Governance]

> repo documentation.
> - `tests/`: contract, invariant, smoke, integration, fixture, and proof suites.
> - `tools/`: repo-only validation, packaging, migration, release, audit, and
>
> [Source: Dominium / Domino]

> Old docs are retained for provenance, but canon, glossary, AGENTS, active
> contracts, current queue state, and reviewed audits outrank stale references.
>
> [Source: Dominium / Domino]

The source-woven book and source map give reviewers enough material to choose small follow-ups deliberately.

> 1. Keep this synthesis advisory and archive-scoped.
> 2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
> 3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
> 4. Patch live docs only through narrow promotion tasks with named source claims and validation.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Advisory: yes
> - Current authority: no
> - Promotion status: not promoted
> - Use: design intent, review backlog, decision and promotion candidates
> - Non-use: canon, contract/schema, implementation, release, or queue override
>
> [Source: DOCS Conversation Corpus Integration]

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

> Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.
>
> [Source: DOCS Current Project Picture]

> Open for derived archive work: reading, synthesis, crosswalks, contradiction review, promotion triage, and narrow docs-only planning. Blocked by current queue: broad Workbench UI, runtime module loader, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication.
>
> [Source: Full Project Picture V0]

> The raw queue contains `135` generated candidates in PROMOTION_QUEUE.md. Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.
>
> [Source: Dominium Conversation Corpus Synthesis Book V0]

> - Project orientation: `README.md`
> - Documentation taxonomy: `the referenced source`
> - Canon: `the referenced source`
> - Glossary: `the referenced source`
> - Agent governance: `AGENTS.md`
> - Queue state: `.aide/queue/current.toml`
> - Foundation status: `the referenced source`
>
> [Source: DOCS Current Project Picture]

> - Read the docs corpus as a map.
> - Use archive material for provenance and review.
> - Use generated contradictions and promotion queues to plan later tasks.
> - Start later live-doc patches only through explicit narrow promotion tasks.
>
> [Source: DOCS Current Project Picture]

> - Conversation files represented: 761
> - Generated conversation reports represented: 131
> - Conversation export files represented: 10
>
> [Source: DOCS Conversation Corpus Integration]

> | Surface | Role |
> | --- | --- |
> | the referenced source/** | derived synthesis and project picture |
> | the referenced source/** | decision docket |
> | the referenced source/** | promotion review backlog |
> | the referenced source/** | conversation-vs-repo crosswalk |
> | the referenced source/** | contradictions, staleness, uncertainty |
> | the referenced source/** | conversation book bundle |
>
> [Source: DOCS Conversation Corpus Integration]

> | Blocked Scope | Authority Source | Matching Docs Paths | Examples | Disposition |
> | --- | --- | --- | --- | --- |
> | broad_workbench_ui | .aide/queue/current.toml | 1 | the referenced source | blocked_by_current_queue |
> | runtime_module_loader | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
>
> [Source: DOCS Blocked Scope Alignment]

> | Decision ID | Source/Finding | Question | Decision Type | Risk | Recommended Default |
> | --- | --- | --- | --- | --- | --- |
>
> [Source: DOCS Decision Docket]

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

> The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
>
> [Source: Complete Chat Preservation Report Dominium Build And Future Proofing Architecture]

The woven passages above come from 53 source documents and 98 selected semantic blocks. Full paths and block identifiers are kept in the source map so the chapter can remain readable.

The tension is deciding which preserved knowledge deserves live-doc promotion and which should remain archive evidence.

Where this leaves us: read the book, inspect the source map where needed, triage decisions, and promote only in narrow waves.


# Appendices

## Appendix A - Chapter Source Notes

These notes provide compact traceability for the woven chapters. They are intentionally separated from the main reading flow.

### 1. Dominium in One View
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15953` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03177` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03178` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03179` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03184` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03189` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03240` - `docs/archive/audit/COUPLE0_RETRO_AUDIT.md` - Couple 0 Retro Consistency Audit
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03247` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit

### 2. Why the Project Exists
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15953` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03288` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03537` - `docs/archive/audit/DISASTER_TEST0_RETRO_AUDIT.md` - Disaster Test 0 Retro Audit
- `SWB-03879` - `docs/archive/audit/EARTH3_RETRO_AUDIT.md` - Earth 3 Retro Audit
- `SWB-03881` - `docs/archive/audit/EARTH3_RETRO_AUDIT.md` - Earth 3 Retro Audit
- `SWB-03882` - `docs/archive/audit/EARTH3_RETRO_AUDIT.md` - Earth 3 Retro Audit
- `SWB-03889` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03890` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03891` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03898` - `docs/archive/audit/EARTH5_RETRO_AUDIT.md` - Earth 5 Retro Audit
- `SWB-03899` - `docs/archive/audit/EARTH5_RETRO_AUDIT.md` - Earth 5 Retro Audit
- `SWB-03900` - `docs/archive/audit/EARTH5_RETRO_AUDIT.md` - Earth 5 Retro Audit
- `SWB-03906` - `docs/archive/audit/EARTH6_RETRO_AUDIT.md` - Earth 6 Retro Audit
- `SWB-03907` - `docs/archive/audit/EARTH6_RETRO_AUDIT.md` - Earth 6 Retro Audit
- `SWB-03908` - `docs/archive/audit/EARTH6_RETRO_AUDIT.md` - Earth 6 Retro Audit
- `SWB-03913` - `docs/archive/audit/EARTH7_RETRO_AUDIT.md` - Earth 7 Retro Audit
- `SWB-03917` - `docs/archive/audit/EARTH7_RETRO_AUDIT.md` - Earth 7 Retro Audit
- `SWB-03920` - `docs/archive/audit/EARTH8_RETRO_AUDIT.md` - Earth 8 Retro Audit
- `SWB-03926` - `docs/archive/audit/EARTH9_RETRO_AUDIT.md` - Earth 9 Retro Audit
- `SWB-03927` - `docs/archive/audit/EARTH9_RETRO_AUDIT.md` - Earth 9 Retro Audit

### 3. The Core Mental Model
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37185` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13984` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09358` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09454` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09506` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09792` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09925` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10024` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10033` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10036` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Deterministic Solar System Architecture
- `SWB-10040` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Deterministic Solar System Architecture
- `SWB-10043` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10044` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10048` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03174` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03177` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03184` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03189` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03197` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline

### 4. Current Truth and Historical Evidence
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00055` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15945` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15947` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15955` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03154` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03160` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline

### 5. The System Stack
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15953` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03178` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03179` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03184` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03189` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03200` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline
- `SWB-03240` - `docs/archive/audit/COUPLE0_RETRO_AUDIT.md` - Couple 0 Retro Consistency Audit
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03247` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03254` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit

### 6. Domino, Dominium, Runtime, Products, and Tools
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03178` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03179` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03184` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03189` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03257` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03259` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03282` - `docs/archive/audit/CTRL2_RETRO_AUDIT.md` - Ctrl2 Retro Consistency Audit
- `SWB-03287` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03288` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit

### 7. Law, Capability, Refusal, and Evidence
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13948` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09358` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09454` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09507` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09925` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10024` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10033` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10036` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Deterministic Solar System Architecture
- `SWB-10040` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Deterministic Solar System Architecture
- `SWB-10043` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10044` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10048` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10107` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03174` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03177` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03184` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03189` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03197` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline
- `SWB-03199` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline
- `SWB-03200` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline
- `SWB-03240` - `docs/archive/audit/COUPLE0_RETRO_AUDIT.md` - Couple 0 Retro Consistency Audit

### 8. Determinism, Replay, and Provenance
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00055` - `README.md` - Dominium / Domino
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37185` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09361` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09454` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09460` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09604` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09925` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10024` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10033` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03174` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03177` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03184` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03189` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03197` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline
- `SWB-03199` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline

### 9. Contracts, Schemas, Packs, and Compatibility
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00016` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37185` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13982` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15953` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09498` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09791` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09937` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10033` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03179` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03192` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03200` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline
- `SWB-03240` - `docs/archive/audit/COUPLE0_RETRO_AUDIT.md` - Couple 0 Retro Consistency Audit
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03247` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03254` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03257` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03282` - `docs/archive/audit/CTRL2_RETRO_AUDIT.md` - Ctrl2 Retro Consistency Audit
- `SWB-03287` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit

### 10. Client, Server, Launcher, Setup, and Workbench
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00013` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00014` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00015` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-23669` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23683` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37185` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13984` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15953` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09454` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09604` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09925` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09928` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10024` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10043` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10048` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10053` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10107` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10118` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10125` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10195` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `SWB-10200` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `SWB-10204` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `SWB-10258` - `docs/archive/conversations/Dominium_Complete_Conversation/dominium_related_file/Dominium_Conversation_Complete_Companion_Report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Conversation Complete Pre
- `SWB-10262` - `docs/archive/conversations/Dominium_Complete_Conversation/dominium_related_file/Dominium_Conversation_Complete_Companion_Report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Conversation Complete Pre
- `SWB-10292` - `docs/archive/conversations/Dominium_Complete_Conversation/dominium_related_file/Dominium_Conversation_Complete_Companion_Report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Conversation Complete Pre
- `SWB-10304` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__01_accompanying_human_readable_detailed_report.md` - Accompanying Human Readable Detailed Report Dominium / Domino Conversation Preservation
- `SWB-10308` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__01_accompanying_human_readable_detailed_report.md` - Accompanying Human Readable Detailed Report Dominium / Domino Conversation Preservation
- `SWB-10309` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__01_accompanying_human_readable_detailed_report.md` - Accompanying Human Readable Detailed Report Dominium / Domino Conversation Preservation
- `SWB-10338` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__human_readable_detailed_summary.md` - Dominium / Domino Complete Conversation Companion Report
- `SWB-10340` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__human_readable_detailed_summary.md` - Dominium / Domino Complete Conversation Companion Report
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03178` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03179` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03184` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03189` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03257` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03259` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03287` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03288` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03291` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03309` - `docs/archive/audit/CTRL5_RETRO_AUDIT.md` - Ctrl5 Retro Consistency Audit
- `SWB-03310` - `docs/archive/audit/CTRL5_RETRO_AUDIT.md` - Ctrl5 Retro Consistency Audit
- `SWB-03339` - `docs/archive/audit/CTRL8_RETRO_AUDIT.md` - Ctrl8 Retro Audit

### 11. UI, Renderer, Native GUI, and Presentation Boundaries
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00014` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00015` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23666` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23675` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09508` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09928` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10043` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10048` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10053` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10107` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10118` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10125` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10144` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_conversation_report.md` - Accompanying Human Readable Detailed Summary And Report Entire Conversation
- `SWB-10188` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03178` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03192` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03254` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03257` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03259` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03282` - `docs/archive/audit/CTRL2_RETRO_AUDIT.md` - Ctrl2 Retro Consistency Audit
- `SWB-03287` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit

### 12. AIDE, Codex, Automation, and Repo Governance
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00055` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15945` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15947` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15955` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03154` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03160` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline

### 13. Documentation, Archive, and Conversation Corpus
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00055` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15945` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15947` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15955` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03154` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03160` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline

### 14. Reality, Space, Time, Scale, and Existence
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-00013` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00014` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00021` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00055` - `README.md` - Dominium / Domino
- `SWB-23668` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23669` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37185` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37191` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37184` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00089` - `docs/README.md` - Dominium Documentation
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13984` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15953` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09363` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09367` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09454` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09460` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09506` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09507` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09644` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09792` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09925` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10024` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10033` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10036` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Deterministic Solar System Architecture
- `SWB-10040` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Deterministic Solar System Architecture
- `SWB-10043` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10044` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10048` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10107` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10118` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10125` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10144` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_conversation_report.md` - Accompanying Human Readable Detailed Summary And Report Entire Conversation
- `SWB-10174` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_conversation_report.md` - Accompanying Human Readable Detailed Summary And Report Entire Conversation
- `SWB-10187` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `SWB-10188` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03174` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03177` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03184` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03189` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03197` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline
- `SWB-03199` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03247` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit

### 15. World Generation, Celestial Systems, and Domains
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00013` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00016` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00060` - `README.md` - Dominium / Domino
- `SWB-23668` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23669` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23674` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37185` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37193` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00089` - `docs/README.md` - Dominium Documentation
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13984` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15953` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13950` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09363` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09454` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09460` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09498` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09506` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09507` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09644` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09791` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09925` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10024` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10033` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10036` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Deterministic Solar System Architecture
- `SWB-10040` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Deterministic Solar System Architecture
- `SWB-10043` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10044` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10048` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10107` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10118` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10125` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10144` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_conversation_report.md` - Accompanying Human Readable Detailed Summary And Report Entire Conversation
- `SWB-10174` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_conversation_report.md` - Accompanying Human Readable Detailed Summary And Report Entire Conversation
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03179` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03282` - `docs/archive/audit/CTRL2_RETRO_AUDIT.md` - Ctrl2 Retro Consistency Audit
- `SWB-03288` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03321` - `docs/archive/audit/CTRL6_RETRO_AUDIT.md` - Ctrl6 Retro Audit
- `SWB-03341` - `docs/archive/audit/CTRL8_RETRO_AUDIT.md` - Ctrl8 Retro Audit
- `SWB-03537` - `docs/archive/audit/DISASTER_TEST0_RETRO_AUDIT.md` - Disaster Test 0 Retro Audit
- `SWB-03645` - `docs/archive/audit/DIST_EXECUTION_PRECHECK.md` - Dist Execution Precheck
- `SWB-03879` - `docs/archive/audit/EARTH3_RETRO_AUDIT.md` - Earth 3 Retro Audit
- `SWB-03880` - `docs/archive/audit/EARTH3_RETRO_AUDIT.md` - Earth 3 Retro Audit
- `SWB-03881` - `docs/archive/audit/EARTH3_RETRO_AUDIT.md` - Earth 3 Retro Audit
- `SWB-03889` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03890` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03891` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03898` - `docs/archive/audit/EARTH5_RETRO_AUDIT.md` - Earth 5 Retro Audit

### 16. Civilization, Economy, Logistics, and Institutions
- `SWB-00013` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00021` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00022` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00060` - `README.md` - Dominium / Domino
- `SWB-00077` - `README.md` - Dominium / Domino
- `SWB-23669` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23674` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23676` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37185` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37184` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-23713` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13984` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15953` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13950` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09506` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09507` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09508` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09644` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09792` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09925` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10024` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10033` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10036` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Deterministic Solar System Architecture
- `SWB-10040` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Deterministic Solar System Architecture
- `SWB-10043` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10044` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10048` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10107` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10118` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10125` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10144` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_conversation_report.md` - Accompanying Human Readable Detailed Summary And Report Entire Conversation
- `SWB-10174` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_conversation_report.md` - Accompanying Human Readable Detailed Summary And Report Entire Conversation
- `SWB-10187` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `SWB-10188` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `SWB-10192` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `SWB-10258` - `docs/archive/conversations/Dominium_Complete_Conversation/dominium_related_file/Dominium_Conversation_Complete_Companion_Report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Conversation Complete Pre
- `SWB-10261` - `docs/archive/conversations/Dominium_Complete_Conversation/dominium_related_file/Dominium_Conversation_Complete_Companion_Report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Conversation Complete Pre
- `SWB-10262` - `docs/archive/conversations/Dominium_Complete_Conversation/dominium_related_file/Dominium_Conversation_Complete_Companion_Report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Conversation Complete Pre
- `SWB-10308` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__01_accompanying_human_readable_detailed_report.md` - Accompanying Human Readable Detailed Report Dominium / Domino Conversation Preservation
- `SWB-10309` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__01_accompanying_human_readable_detailed_report.md` - Accompanying Human Readable Detailed Report Dominium / Domino Conversation Preservation
- `SWB-10325` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__01_accompanying_human_readable_detailed_report.md` - Accompanying Human Readable Detailed Report Dominium / Domino Conversation Preservation
- `SWB-10340` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__human_readable_detailed_summary.md` - Dominium / Domino Complete Conversation Companion Report
- `SWB-10341` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__human_readable_detailed_summary.md` - Dominium / Domino Complete Conversation Companion Report
- `SWB-10354` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__human_readable_detailed_summary.md` - Dominium / Domino Complete Conversation Companion Report
- `SWB-10414` - `docs/archive/conversations/Dominium_Complete_Conversation/existing_complete_preservation_package/Dominium_Complete_Conversation_Preservation__00_consolidated_package_index.md` - Consolidated Package Index Dominium Complete Conversation Preservation
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03288` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03537` - `docs/archive/audit/DISASTER_TEST0_RETRO_AUDIT.md` - Disaster Test 0 Retro Audit
- `SWB-03879` - `docs/archive/audit/EARTH3_RETRO_AUDIT.md` - Earth 3 Retro Audit
- `SWB-03881` - `docs/archive/audit/EARTH3_RETRO_AUDIT.md` - Earth 3 Retro Audit
- `SWB-03882` - `docs/archive/audit/EARTH3_RETRO_AUDIT.md` - Earth 3 Retro Audit
- `SWB-03889` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03890` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03891` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03898` - `docs/archive/audit/EARTH5_RETRO_AUDIT.md` - Earth 5 Retro Audit
- `SWB-03899` - `docs/archive/audit/EARTH5_RETRO_AUDIT.md` - Earth 5 Retro Audit
- `SWB-03900` - `docs/archive/audit/EARTH5_RETRO_AUDIT.md` - Earth 5 Retro Audit
- `SWB-03906` - `docs/archive/audit/EARTH6_RETRO_AUDIT.md` - Earth 6 Retro Audit
- `SWB-03907` - `docs/archive/audit/EARTH6_RETRO_AUDIT.md` - Earth 6 Retro Audit
- `SWB-03908` - `docs/archive/audit/EARTH6_RETRO_AUDIT.md` - Earth 6 Retro Audit
- `SWB-03913` - `docs/archive/audit/EARTH7_RETRO_AUDIT.md` - Earth 7 Retro Audit
- `SWB-03917` - `docs/archive/audit/EARTH7_RETRO_AUDIT.md` - Earth 7 Retro Audit
- `SWB-03920` - `docs/archive/audit/EARTH8_RETRO_AUDIT.md` - Earth 8 Retro Audit
- `SWB-03926` - `docs/archive/audit/EARTH9_RETRO_AUDIT.md` - Earth 9 Retro Audit
- `SWB-03927` - `docs/archive/audit/EARTH9_RETRO_AUDIT.md` - Earth 9 Retro Audit

### 17. Content, Providers, Modding, and Data-Driven Extension
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00016` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37185` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09454` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09460` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09498` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09604` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09791` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09937` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09939` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10033` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10036` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Deterministic Solar System Architecture
- `SWB-10043` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10048` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03179` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03192` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03200` - `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md` - Control Plane Final Baseline
- `SWB-03240` - `docs/archive/audit/COUPLE0_RETRO_AUDIT.md` - Couple 0 Retro Consistency Audit
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03247` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03254` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03282` - `docs/archive/audit/CTRL2_RETRO_AUDIT.md` - Ctrl2 Retro Consistency Audit

### 18. What Is Settled
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00055` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15945` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15947` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15955` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03154` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03160` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline

### 19. What Is Still Open
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00018` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00022` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00068` - `README.md` - Dominium / Domino
- `SWB-00082` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15945` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15947` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15955` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03154` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03160` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline

### 20. What Is Blocked
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00014` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00015` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00045` - `README.md` - Dominium / Domino
- `SWB-00067` - `README.md` - Dominium / Domino
- `SWB-00068` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23666` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23675` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13950` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09507` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09644` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09928` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10043` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10048` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10054` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10107` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10118` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10125` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03170` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03178` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03192` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03254` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03257` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03282` - `docs/archive/audit/CTRL2_RETRO_AUDIT.md` - Ctrl2 Retro Consistency Audit
- `SWB-03287` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03288` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03310` - `docs/archive/audit/CTRL5_RETRO_AUDIT.md` - Ctrl5 Retro Consistency Audit
- `SWB-03321` - `docs/archive/audit/CTRL6_RETRO_AUDIT.md` - Ctrl6 Retro Audit
- `SWB-03335` - `docs/archive/audit/CTRL8_RETRO_AUDIT.md` - Ctrl8 Retro Audit
- `SWB-03353` - `docs/archive/audit/CTRL9_RETRO_AUDIT.md` - Ctrl9 Retro Audit

### 21. Contradictions and Drift
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00046` - `README.md` - Dominium / Domino
- `SWB-00054` - `README.md` - Dominium / Domino
- `SWB-00055` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15945` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15947` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15955` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03154` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03160` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline

### 22. Prerequisites and Sequencing
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00001` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00004` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00056` - `README.md` - Dominium / Domino
- `SWB-00067` - `README.md` - Dominium / Domino
- `SWB-00068` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23665` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23675` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-37185` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13950` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09603` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09604` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09925` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-10023` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10024` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `SWB-10032` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Deterministic Solar System Architecture
- `SWB-10036` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Deterministic Solar System Architecture
- `SWB-10043` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10048` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10062` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar Syste
- `SWB-10107` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-10125` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md` - Accompanying Human Readable Complete Conversation Report Dominium Deterministic Solar Syst
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-03176` - `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md` - Control Plane Enforcement Baseline (ctrl 9)
- `SWB-03190` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03192` - `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md` - Control Plane Engine Baseline
- `SWB-03245` - `docs/archive/audit/CTRL0_RETRO_AUDIT.md` - Ctrl0 Retro Consistency Audit
- `SWB-03256` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03257` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03263` - `docs/archive/audit/CTRL10_RETRO_AUDIT.md` - Ctrl10 Retro Audit
- `SWB-03282` - `docs/archive/audit/CTRL2_RETRO_AUDIT.md` - Ctrl2 Retro Consistency Audit
- `SWB-03287` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03288` - `docs/archive/audit/CTRL3_RETRO_AUDIT.md` - Ctrl3 Retro Consistency Audit
- `SWB-03310` - `docs/archive/audit/CTRL5_RETRO_AUDIT.md` - Ctrl5 Retro Consistency Audit
- `SWB-03335` - `docs/archive/audit/CTRL8_RETRO_AUDIT.md` - Ctrl8 Retro Audit
- `SWB-03341` - `docs/archive/audit/CTRL8_RETRO_AUDIT.md` - Ctrl8 Retro Audit
- `SWB-03645` - `docs/archive/audit/DIST_EXECUTION_PRECHECK.md` - Dist Execution Precheck
- `SWB-03708` - `docs/archive/audit/DOCS_AUDIT_PROMPT0.md` - DOCS Audit (prompt 0)
- `SWB-03891` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03893` - `docs/archive/audit/EARTH4_RETRO_AUDIT.md` - Earth 4 Retro Audit
- `SWB-03897` - `docs/archive/audit/EARTH5_RETRO_AUDIT.md` - Earth 5 Retro Audit

### 23. Recommended Next Steps
- `SWB-00036` - `AGENTS.md` - Dominium Agent Governance
- `SWB-23672` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23678` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-37181` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-00018` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00022` - `AGENTS.md` - Dominium Agent Governance
- `SWB-00068` - `README.md` - Dominium / Domino
- `SWB-00082` - `README.md` - Dominium / Domino
- `SWB-00087` - `docs/README.md` - Dominium Documentation
- `SWB-00088` - `docs/README.md` - Dominium Documentation
- `SWB-23664` - `docs/canon/constitution_v1.md` - Dominium Constitutional Architecture & Execution Contract V1
- `SWB-23696` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-23703` - `docs/canon/glossary_v1.md` - Dominium Canonical Glossary V1.0.0
- `SWB-37183` - `docs/repo/FOUNDATION_LOCK.md` - Foundation Lock
- `SWB-13986` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15946` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-13949` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13951` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13987` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15950` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-13952` - `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md` - Full Project Picture V0
- `SWB-13985` - `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md` - Dominium Conversation Corpus Synthesis Book V0
- `SWB-15951` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15952` - `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md` - DOCS Current Project Picture
- `SWB-15945` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15947` - `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md` - DOCS Conversation Corpus Integration
- `SWB-15949` - `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md` - DOCS Blocked Scope Alignment
- `SWB-15955` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-15956` - `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` - DOCS Decision Docket
- `SWB-09328` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09344` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09345` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `SWB-09392` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `SWB-09396` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md` - Verification And Audit Dominium Build And Future Proofing Architecture
- `SWB-09399` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt Dominium Build And Future Proofing Architecture
- `SWB-09403` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09404` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `SWB-09405` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09411` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09440` - `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `SWB-09469` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09471` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md` - Full Chat Report Dominium Chronology & Celestial Systems
- `SWB-09481` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `SWB-09489` - `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md` - Verification And Audit Dominium Chronology & Celestial Systems
- `SWB-09494` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09496` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09497` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md` - Full Chat Report Dominium Architecture I
- `SWB-09512` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09513` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `SWB-09524` - `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md` - Verification And Audit Dominium Architecture I
- `SWB-09536` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09539` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09540` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md` - Full Chat Report Dominium Architecture Ii
- `SWB-09547` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `SWB-09556` - `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Ii
- `SWB-09560` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09565` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09571` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iii
- `SWB-09577` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `SWB-09588` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09590` - `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iii
- `SWB-09597` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09601` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09602` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md` - Full Chat Report Dominium Architecture Iv
- `SWB-09612` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `SWB-09621` - `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md` - Verification And Audit Dominium Architecture Iv
- `SWB-09630` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09634` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09636` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Do
- `SWB-09682` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09683` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09689` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `SWB-09715` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09748` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09773` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignme
- `SWB-09777` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `SWB-09782` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09783` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09790` - `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `SWB-09918` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-09923` - `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `SWB-02337` - `docs/archive/STATUS_NOW.md` - Status Now
- `SWB-02456` - `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md` - Anti Cheat Framework Baseline
- `SWB-02536` - `docs/archive/audit/APPSHELL_IPC_BASELINE.md` - Appshell Ipc Baseline
- `SWB-02577` - `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md` - Archive Policy Baseline
- `SWB-02627` - `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md` - Arch Audit Fix Plan
- `SWB-02670` - `docs/archive/audit/AUDITX_BASELINE_REPORT.md` - Auditx Baseline Report
- `SWB-02688` - `docs/archive/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md` - Baseline Universe 0 Retro Audit
- `SWB-02826` - `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md` - Cap Negotiation Baseline
- `SWB-02878` - `docs/archive/audit/CHEM4_RETRO_AUDIT.md` - Chem 4 Retro Consistency Audit
- `SWB-03044` - `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md` - Meta Compute 0 Baseline
- `SWB-03147` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03149` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03151` - `docs/archive/audit/CONTROL_IR_BASELINE.md` - Control Ir Baseline
- `SWB-03154` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03160` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03161` - `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md` - Control Negotiation Baseline
- `SWB-03169` - `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` - Control Plane Constitution Baseline


## Appendix B - Source Block Index

The full source block index is available in the source map PDF and in `SOURCE_BLOCKS.yml`. Major topic tags represented in woven blocks include: docs, renderer, authority, determinism, runtime, contracts, world, product, release, packs, identity, tooling, civilization, workbench, blocked.

## Appendix C - Omitted and Reference-Only Material

Machine-like archives, duplicate blocks, and low-value registers are represented in the source map rather than printed as main prose.

- `AGENTS.md` - reference_only; Dominium Agent Governance
- `AGENTS.md` - reference_only; Dominium Agent Governance
- `AGENTS.md` - reference_only; Dominium Agent Governance
- `AGENTS.md` - reference_only; Dominium Agent Governance
- `AGENTS.md` - reference_only; Dominium Agent Governance
- `AGENTS.md` - reference_only; Dominium Agent Governance
- `AGENTS.md` - reference_only; Dominium Agent Governance
- `README.md` - reference_only; Dominium / Domino
- `README.md` - reference_only; Dominium / Domino
- `README.md` - reference_only; Dominium / Domino
- `README.md` - reference_only; Dominium / Domino
- `README.md` - reference_only; Dominium / Domino
- `README.md` - reference_only; Dominium / Domino
- `README.md` - excluded_duplicate; Dominium / Domino
- `README.md` - reference_only; Dominium / Domino
- `README.md` - reference_only; Dominium / Domino
- `docs/README.md` - excluded_duplicate; Dominium Documentation
- `docs/README.md` - reference_only; Dominium Documentation
- `docs/apps/CLIENT_IDE_START_POINTS.md` - excluded_duplicate; Client Ide Start Points
- `docs/apps/CLIENT_READONLY_INTEGRATION.md` - excluded_duplicate; Client Read Only Integration
- `docs/apps/CLIENT_RENDERER_UI.md` - excluded_duplicate; Client Renderer UI
- `docs/apps/CLIENT_UI_LAYER.md` - excluded_duplicate; Client UI Layer
- `docs/apps/CLI_CONTRACTS.md` - excluded_duplicate; CLI Contracts
- `docs/apps/CLI_CONTRACTS.md` - excluded_duplicate; CLI Contracts
- `docs/apps/CLI_CONTRACTS.md` - excluded_duplicate; CLI Contracts
- `docs/apps/COMMAND_GRAPH_CAMERA_AND_BLUEPRINT.md` - excluded_duplicate; Command Graph: Camera And Blueprint
- `docs/apps/COMMAND_GRAPH_CAMERA_AND_BLUEPRINT.md` - excluded_duplicate; Command Graph: Camera And Blueprint
- `docs/apps/COMMAND_GRAPH_CAMERA_AND_BLUEPRINT.md` - excluded_duplicate; Command Graph: Camera And Blueprint
- `docs/apps/COMPATIBILITY_ENFORCEMENT.md` - excluded_duplicate; Compatibility Enforcement
- `docs/apps/ENGINE_GAME_DIAGNOSTICS.md` - excluded_duplicate; Engine/game Diagnostics
- `docs/apps/GUI_MODE.md` - excluded_duplicate; GUI Mode
- `docs/apps/HEADLESS_AND_ZERO_PACK.md` - excluded_duplicate; Headless And Zero Pack Boot
- `docs/apps/IDE_WORKFLOW.md` - excluded_duplicate; Ide Workflow
- `docs/apps/NATIVE_UI_POLICY.md` - excluded_duplicate; Native UI Policy
- `docs/apps/OBSERVABILITY_PIPELINES.md` - excluded_duplicate; Observability Pipelines
- `docs/apps/PRODUCT_BOUNDARIES.md` - excluded_duplicate; Product Boundaries
- `docs/apps/READONLY_ADAPTER.md` - excluded_duplicate; Read Only Adapter
- `docs/apps/RUNTIME_LOOP.md` - excluded_duplicate; Runtime Loop Contract
- `docs/apps/TESTX_COMPLIANCE.md` - excluded_duplicate; Testx Compliance (apr0)
- `docs/apps/TIMING_AND_CLOCKS.md` - excluded_duplicate; Timing And Clock Domains
- `docs/apps/TOOLS_OBSERVABILITY.md` - excluded_duplicate; Tools Observability
- `docs/apps/TOOLS_UI_POLICY.md` - excluded_duplicate; Tools UI Policy
- `docs/apps/TUI_MODE.md` - excluded_duplicate; TUI Mode
- `docs/apps/client/CLIENT_COMMAND_GRAPH.md` - excluded_duplicate; Client Command Graph
- `docs/apps/client/CLIENT_FLOW.md` - excluded_duplicate; Client Flow
- `docs/apps/client/CLIENT_FLOW.md` - excluded_duplicate; Client Flow
- `docs/apps/client/CLIENT_LIFECYCLE_PIPELINE.md` - excluded_duplicate; Client Lifecycle Pipeline
- `docs/apps/client/CLIENT_LIFECYCLE_PIPELINE.md` - excluded_duplicate; Client Lifecycle Pipeline
- `docs/apps/client/CLIENT_LIFECYCLE_PIPELINE.md` - excluded_duplicate; Client Lifecycle Pipeline
- `docs/apps/client/CLIENT_SETTINGS.md` - excluded_duplicate; Client Settings
- `docs/apps/client/CLIENT_SETTINGS.md` - excluded_duplicate; Client Settings
- `docs/apps/client/CLIENT_UI_AND_FLOW.md` - excluded_duplicate; Client UI And Flow
- `docs/apps/client/CLI_TUI_GUI_PARITY.md` - excluded_duplicate; CLI TUI GUI Parity
- `docs/apps/client/CLI_TUI_GUI_PARITY.md` - excluded_duplicate; CLI TUI GUI Parity
- `docs/apps/client/SERVER_DISCOVERY.md` - excluded_duplicate; Server Discovery
- `docs/apps/client/SERVER_DISCOVERY.md` - excluded_duplicate; Server Discovery
- `docs/apps/client/SESSION_READY_AND_RUNNING.md` - excluded_duplicate; Session Ready And Running
- `docs/apps/client/SESSION_READY_AND_RUNNING.md` - excluded_duplicate; Session Ready And Running
- `docs/apps/client/SESSION_SPEC_AND_AUTHORITY_CONTEXT.md` - excluded_duplicate; Sessionspec And Authoritycontext
- `docs/apps/client/SESSION_TRANSITION_WORKSPACE.md` - excluded_duplicate; Session Transition Workspace
- `docs/apps/client/WORLD_MANAGER.md` - excluded_duplicate; World Manager
- `docs/apps/client/WORLD_MANAGER.md` - excluded_duplicate; World Manager
- `docs/apps/client/WORLD_MANAGER.md` - excluded_duplicate; World Manager
- `docs/apps/launcher/LAUNCHER_SETTINGS.md` - excluded_duplicate; Launcher Settings
- `docs/apps/launcher/LAUNCHER_SETTINGS.md` - excluded_duplicate; Launcher Settings
- `docs/apps/server/LOCAL_SINGLEPLAYER_MODEL.md` - excluded_duplicate; Local Singleplayer Model
- `docs/apps/server/LOCAL_SINGLEPLAYER_MODEL.md` - excluded_duplicate; Local Singleplayer Model
- `docs/apps/server/SERVER_MVP_BASELINE.md` - excluded_duplicate; Server Mvp Baseline
- `docs/apps/server/SERVER_MVP_BASELINE.md` - excluded_duplicate; Server Mvp Baseline
- `docs/apps/server/SERVER_MVP_BASELINE.md` - excluded_duplicate; Server Mvp Baseline
- `docs/apps/server/SERVER_SETTINGS.md` - excluded_duplicate; Server Settings
- `docs/apps/setup/SETUP_SETTINGS.md` - excluded_duplicate; Setup Settings
- `docs/apps/setup/SETUP_SETTINGS.md` - excluded_duplicate; Setup Settings
- `docs/apps/setup/SETUP_SETTINGS.md` - excluded_duplicate; Setup Settings
- `docs/architecture/ADAPTER_PATTERN.md` - excluded_duplicate; Adapter Pattern
- `docs/architecture/ADOPTION_PROTOCOL.md` - excluded_duplicate; Adopt0 Adoption Protocol
- `docs/architecture/AI_AND_DELEGATED_AUTONOMY_MODEL.md` - excluded_duplicate; Ai And Delegated Autonomy Model (aia0)
- `docs/architecture/AI_AND_DELEGATED_AUTONOMY_MODEL.md` - excluded_duplicate; Ai And Delegated Autonomy Model (aia0)
- `docs/architecture/AI_AND_DELEGATED_AUTONOMY_MODEL.md` - excluded_duplicate; Ai And Delegated Autonomy Model (aia0)
- `docs/architecture/AI_BUDGET_MODEL.md` - excluded_duplicate; Ai Budget Model (ai0)
- `docs/architecture/AI_INTENT_MODEL.md` - excluded_duplicate; Ai Intent Model (ai0)
- `docs/architecture/ANTI_CHEAT_AS_LAW.md` - excluded_duplicate; Anti Cheat As Law (omni0)
- `docs/architecture/ANTI_ENTROPY_RULES.md` - excluded_duplicate; Anti Entropy Rules (entropy0)
- `docs/architecture/APPLICATION_CONTRACTS.md` - excluded_duplicate; Application Contracts (summary)
- `docs/architecture/APP_CANON0.md` - excluded_duplicate; Application Layer Canon (app Canon0)
- `docs/architecture/APP_CANON1.md` - excluded_duplicate; Application Layer Canon (app Canon1)
- `docs/architecture/ARCH0_CONSTITUTION.md` - excluded_duplicate; Arch0 Constitution
- `docs/architecture/ARCHITECTURE.md` - excluded_duplicate; Architecture (high Level)
- `docs/architecture/ARCHITECTURE_LAYERS.md` - excluded_duplicate; Architecture Layers
- `docs/architecture/ARCHIVAL_AND_PERMANENCE.md` - excluded_duplicate; Archival And Permanence (exist2)
- `docs/architecture/ARCH_BUILD_ENFORCEMENT.md` - excluded_duplicate; Arch Build Enforcement Build And Boundary Lockdown (enf2)
- `docs/architecture/ARCH_CHANGE_PROCESS.md` - excluded_duplicate; Architectural Change Process (future0)
- `docs/architecture/ARCH_ENFORCEMENT.md` - excluded_duplicate; Architecture Enforcement Law (enf0)
- `docs/architecture/ARCH_SPEC_OWNERSHIP.md` - excluded_duplicate; Arch Spec Ownership Spec Responsibility Model
- `docs/architecture/ARTIFACT_LIFECYCLE.md` - excluded_duplicate; Artifact Lifecycle
- `docs/architecture/ARTIFACT_MODEL.md` - excluded_duplicate; Artifact Model (lib 4)
- `docs/architecture/ARTIFACT_MODEL.md` - excluded_duplicate; Artifact Model (lib 4)
- `docs/architecture/ARTIFACT_MODEL.md` - excluded_duplicate; Artifact Model (lib 4)
- `docs/architecture/ARTIFACT_MODEL.md` - excluded_duplicate; Artifact Model (lib 4)
- `docs/architecture/AUDITABILITY_AND_DISCLOSURE.md` - excluded_duplicate; Auditability And Disclosure (testx2)
- `docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md` - excluded_duplicate; Authority And Entitlements (testx3)
- `docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md` - excluded_duplicate; Authority And Omnipotence (omni0)
- `docs/architecture/AUTHORITY_IN_REALITY.md` - excluded_duplicate; Authority In Reality (reality0)
- `docs/architecture/AUTHORITY_MODEL.md` - excluded_duplicate; Authority Model (canon0)
- `docs/architecture/BOUNDARY_ENFORCEMENT.md` - excluded_duplicate; Boundary Enforcement
- `docs/architecture/BUDGET_POLICY.md` - excluded_duplicate; Budget Policy V1
- `docs/architecture/BUDGET_POLICY.md` - excluded_duplicate; Budget Policy V1
- `docs/architecture/BUDGET_POLICY.md` - excluded_duplicate; Budget Policy V1
- `docs/architecture/BUDGET_POLICY.md` - excluded_duplicate; Budget Policy V1
- `docs/architecture/BUDGET_POLICY.md` - excluded_duplicate; Budget Policy V1
- `docs/architecture/BUGREPORT_MODEL.md` - excluded_duplicate; Bugreport Bundle Model (bug 0)
- `docs/architecture/CANONICAL_SYSTEM_MAP.md` - excluded_duplicate; Canonical System Map (canon0)
- `docs/architecture/CANONICAL_SYSTEM_MAP.md` - reference_only; Canonical System Map (canon0)
- `docs/architecture/CANONICAL_SYSTEM_MAP.md` - reference_only; Canonical System Map (canon0)
- `docs/architecture/CANONICAL_SYSTEM_MAP.md` - reference_only; Canonical System Map (canon0)
- `docs/architecture/CANON_CUT_LINE.md` - excluded_duplicate; Canon Cut Line (cons 0)
- `docs/architecture/CANON_INDEX.md` - excluded_duplicate; Canon Index (clean 2)
- `docs/architecture/CANON_INDEX.md` - excluded_duplicate; Canon Index (clean 2)
- `docs/architecture/CAPABILITY_BASELINES.md` - excluded_duplicate; Capability Baselines (capbase0)
- `docs/architecture/CAPABILITY_ONLY_CANON.md` - excluded_duplicate; Capability Only Canon
- `docs/architecture/CHANGELOG_ARCH.md` - excluded_duplicate; Architecture Changelog (clean1)
- `docs/architecture/CHANGE_PROTOCOL.md` - excluded_duplicate; Change Protocol (arch0 Binding)
- `docs/architecture/CHEATS_ARE_JUST_LAWS.md` - excluded_duplicate; Cheats Are Just Laws (omni1)
- `docs/architecture/CHECKPOINTING_MODEL.md` - excluded_duplicate; Checkpointing Model (mmo 2)
- `docs/architecture/CHECKPOINTS.md` - excluded_duplicate; Acceptance Checkpoints (chk0)
- `docs/architecture/CHECKPOINTS.md` - excluded_duplicate; Acceptance Checkpoints (chk0)
- `docs/architecture/CIVILIZATION_MODEL.md` - excluded_duplicate; Civilization Model (civ0+)
- `docs/architecture/CODE_DATA_BOUNDARY.md` - excluded_duplicate; Code/data Boundary (codehygiene X)
- `docs/architecture/CODE_KNOWLEDGE_BOUNDARY.md` - excluded_duplicate; Code Knowledge Boundary (codeknow0)
- `docs/architecture/COLLAPSE_AND_DECAY.md` - excluded_duplicate; Collapse And Decay (civ0+)
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md` - excluded_duplicate; Collapse/expand Contract (scale0)
- `docs/architecture/COLLAPSE_EXPAND_SOLVERS.md` - excluded_duplicate; Collapse Expand Solvers
- `docs/architecture/COMPATIBILITY_MODEL.md` - excluded_duplicate; Compatibility Model (ops1)
- `docs/architecture/COMPLEXITY_AND_SCALE.md` - excluded_duplicate; Complexity And Scale
- `docs/architecture/COMPLEXITY_AND_SCALE.md` - excluded_duplicate; Complexity And Scale
- `docs/architecture/COMPONENTS.md` - excluded_duplicate; Components
- `docs/architecture/CONFLICT_AND_WAR_MODEL.md` - excluded_duplicate; Conflict And War Model (war0)
- `docs/architecture/CONFLICT_AND_WAR_MODEL.md` - excluded_duplicate; Conflict And War Model (war0)
- `docs/architecture/CONSTANT_COST_GUARANTEE.md` - excluded_duplicate; Constant Cost Guarantee (scale3)
- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md` - excluded_duplicate; Content And Storage Model (stor0 / Lib 0)
- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md` - excluded_duplicate; Content And Storage Model (stor0 / Lib 0)
- `docs/architecture/CONTRACTS_INDEX.md` - excluded_duplicate; Contracts Index (const0)
- `docs/architecture/CONTRACTS_INDEX.md` - excluded_duplicate; Contracts Index (const0)
- `docs/architecture/CONTRACTS_INDEX.md` - excluded_duplicate; Contracts Index (const0)
- `docs/architecture/CONTROL_LAYERS.md` - excluded_duplicate; Control Layers (testx2)
- `docs/architecture/CRASH_RECOVERY.md` - excluded_duplicate; Crash Recovery (mmo 2)
- `docs/architecture/CROSS_SHARD_LOG.md` - excluded_duplicate; Cross Shard Log (mmo0)
- `docs/architecture/DEATH_AND_CONTINUITY.md` - excluded_duplicate; Death And Continuity (life0+)
- `docs/architecture/DECAY_EROSION_REGEN.md` - excluded_duplicate; Decay, Erosion, Regeneration (terrain0)
- `docs/architecture/DEMO_AND_TOURIST_MODEL.md` - excluded_duplicate; Demo And Tourist Model (testx3)
- `docs/architecture/DEPRECATION_AND_QUARANTINE.md` - excluded_duplicate; Deprecation And Quarantine
- `docs/architecture/DEPRECATION_LIFECYCLE.md` - excluded_duplicate; Deprecation Lifecycle
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md` - excluded_duplicate; Deterministic Ordering Policy (order0)
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md` - excluded_duplicate; Deterministic Ordering Policy (order0)
- `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md` - excluded_duplicate; Deterministic Reduction Rules (exec0b)
- `docs/architecture/DIRECTORY_CONTEXT.md` - excluded_duplicate; Dominium Directory Context (authoritative)
- `docs/architecture/DIRECTORY_CONTEXT.md` - excluded_duplicate; Dominium Directory Context (authoritative)
- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md` - excluded_duplicate; Distributed Simulation Model (mmo Srz)
- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md` - excluded_duplicate; Distributed Simulation Model (mmo Srz)
- `docs/architecture/DISTRIBUTED_TIME_MODEL.md` - excluded_duplicate; Distributed Time Model (mmo0)
- `docs/architecture/DISTRIBUTION_AND_STOREFRONTS.md` - excluded_duplicate; Distribution And Storefronts (testx3)
- `docs/architecture/DISTRIBUTION_LAYOUT.md` - excluded_duplicate; Distribution Layout (dist0)
- `docs/architecture/DISTRIBUTION_PROFILES.md` - excluded_duplicate; Distribution Profiles (testx2)
- `docs/architecture/DOMAIN_JURISDICTIONS_AND_LAW.md` - excluded_duplicate; Domain Jurisdictions And Law (domain2)
- `docs/architecture/DOMAIN_SHARDING_AND_STREAMING.md` - excluded_duplicate; Domain Sharding And Streaming (domain3)
- `docs/architecture/DOMAIN_VOLUMES.md` - excluded_duplicate; Domain Volumes (domain0)
- `docs/architecture/DUPLICATION_DETECTION_RULES.md` - excluded_duplicate; Duplication Detection Rules
- `docs/architecture/ECONOMIC_MODEL.md` - excluded_duplicate; Economic Model (econ0)
- `docs/architecture/ECONOMIC_MODEL.md` - excluded_duplicate; Economic Model (econ0)
- `docs/architecture/ECONOMIC_MODEL.md` - excluded_duplicate; Economic Model (econ0)
- `docs/architecture/ECONOMIC_MODEL.md` - excluded_duplicate; Economic Model (econ0)
- `docs/architecture/ECONOMY_AND_LOGISTICS.md` - excluded_duplicate; Economy And Logistics (civ0+)
- `docs/architecture/ENERGY_MODEL.md` - excluded_duplicate; Energy Model (energy0)
- `docs/architecture/ENERGY_MODEL.md` - excluded_duplicate; Energy Model (energy0)
- `docs/architecture/ENERGY_MODEL.md` - excluded_duplicate; Energy Model (energy0)
- `docs/architecture/ENERGY_MODEL.md` - excluded_duplicate; Energy Model (energy0)
- `docs/architecture/ENFORCEMENT_ESCALATION.md` - excluded_duplicate; Enforcement And Escalation (omni2)
- `docs/architecture/EPISTEMICS_AND_SCALED_MMO.md` - excluded_duplicate; Epistemics And Scaled Mmo (epi Scale)
- `docs/architecture/EPISTEMICS_AND_SCALED_MMO.md` - excluded_duplicate; Epistemics And Scaled Mmo (epi Scale)
- `docs/architecture/EPISTEMICS_MODEL.md` - excluded_duplicate; Epistemics Model (epi0)
- `docs/architecture/EPISTEMICS_MODEL.md` - excluded_duplicate; Epistemics Model (epi0)
- `docs/architecture/EXECUTION_MODEL.md` - excluded_duplicate; Execution Model (canon0)
- `docs/architecture/EXECUTION_REORDERING_POLICY.md` - excluded_duplicate; Execution Reordering Policy (exec0b)
- `docs/architecture/EXECUTION_SUBSTRATE_AUDIT.md` - excluded_duplicate; Exec Audit0 Execution Substrate Audit
- `docs/architecture/EXISTENCE_AND_REALITY.md` - excluded_duplicate; Existence And Reality (exist0)
- `docs/architecture/EXISTENCE_LIFECYCLE.md` - excluded_duplicate; Existence Lifecycle (exist0)
- `docs/architecture/EXOTIC_TRAVEL_AND_REALITY.md` - excluded_duplicate; Exotic Travel And Reality (travel2)
- `docs/architecture/EXPLORATION_METRICS.md` - excluded_duplicate; Exploration Metrics (w1)
- `docs/architecture/EXPLORATION_METRICS.md` - excluded_duplicate; Exploration Metrics (w1)
- `docs/architecture/EXPLORATION_SCALING_PROOF.md` - excluded_duplicate; Exploration Scaling Proof (w1)
- `docs/architecture/EXTEND_VS_CREATE.md` - excluded_duplicate; Extend Vs Create (cons 0)
- `docs/architecture/EXTENSION_MAP.md` - excluded_duplicate; Extension Map (5 10 Year Horizon)
- `docs/architecture/EXTENSION_MAP.md` - excluded_duplicate; Extension Map (5 10 Year Horizon)
- `docs/architecture/EXTENSION_RULES.md` - excluded_duplicate; Extension Rules (future0)
- `docs/architecture/FABRICATION_MODEL.md` - excluded_duplicate; Fabrication Model (fab0)
- `docs/architecture/FLOAT_POLICY.md` - excluded_duplicate; Floating Point Policy (deter 0)
- `docs/architecture/FLOWSYSTEM_STANDARD.md` - excluded_duplicate; Flowsystem Standard
- `docs/architecture/FLUIDS_MODEL.md` - excluded_duplicate; Fluids Model (fluids0)
- `docs/architecture/FLUIDS_MODEL.md` - excluded_duplicate; Fluids Model (fluids0)
- `docs/architecture/FORKING_AND_PROVIDES_MODEL.md` - excluded_duplicate; Forking And Provides Model (lib 5)
- `docs/architecture/FORKING_AND_PROVIDES_MODEL.md` - excluded_duplicate; Forking And Provides Model (lib 5)
- `docs/architecture/FORKING_AND_PROVIDES_MODEL.md` - excluded_duplicate; Forking And Provides Model (lib 5)
- `docs/architecture/FORKING_AND_PROVIDES_MODEL.md` - excluded_duplicate; Forking And Provides Model (lib 5)
- `docs/architecture/FORKING_AND_PROVIDES_MODEL.md` - excluded_duplicate; Forking And Provides Model (lib 5)
- `docs/architecture/FUTURE_COMPATIBILITY_AND_ARCH.md` - excluded_duplicate; Future Compatibility And Architecture Targets (repox)
- `docs/architecture/FUTURE_PROOFING.md` - excluded_duplicate; Future Proofing (future0)
- `docs/architecture/GENERATED_CODE_POLICY.md` - excluded_duplicate; Generated Code Policy (repox)
- `docs/architecture/GLOBAL_ID_MODEL.md` - excluded_duplicate; Global ID Model (mmo0)
- `docs/architecture/GLOSSARY.md` - excluded_duplicate; Architecture Glossary
- `docs/architecture/GOVERNANCE_AND_INSTITUTIONS.md` - excluded_duplicate; Governance And Institutions (civ0+)
- `docs/architecture/GUI_BASELINE.md` - excluded_duplicate; GUI Baseline (zero Asset)
- `docs/architecture/HARDWARE_EVOLUTION_STRATEGY.md` - excluded_duplicate; Hardware Evolution Strategy (hwcaps0)
- `docs/architecture/HAZARDS_MODEL.md` - excluded_duplicate; Hazards Model (hazard0)
- `docs/architecture/HAZARDS_MODEL.md` - excluded_duplicate; Hazards Model (hazard0)
- `docs/architecture/HAZARDS_MODEL.md` - excluded_duplicate; Hazards Model (hazard0)
- `docs/architecture/HAZARDS_MODEL.md` - excluded_duplicate; Hazards Model (hazard0)
- `docs/architecture/HISTORY_AND_CIVILIZATION_MODEL.md` - excluded_duplicate; History And Civilization Model (hist0)
- `docs/architecture/IDENTITY_ACROSS_TIME.md` - excluded_duplicate; Identity Across Time (life0+)
- `docs/architecture/ID_AND_NAMESPACE_RULES.md` - excluded_duplicate; ID And Namespace Rules (idns0)
- `docs/architecture/INDEXING_POLICY.md` - excluded_duplicate; Indexing Policy (index0)
- `docs/architecture/INFORMATION_MODEL.md` - excluded_duplicate; Information Model (info0)
- `docs/architecture/INFORMATION_MODEL.md` - excluded_duplicate; Information Model (info0)
- `docs/architecture/INFORMATION_MODEL.md` - excluded_duplicate; Information Model (info0)
- `docs/architecture/INFORMATION_MODEL.md` - excluded_duplicate; Information Model (info0)
- `docs/architecture/INSTALLER_CONTRACT.md` - excluded_duplicate; Installer Contract (dist1)
- `docs/architecture/INSTALL_MODEL.md` - excluded_duplicate; Install Model (ops0 / Lib 1)
- `docs/architecture/INSTALL_MODEL.md` - excluded_duplicate; Install Model (ops0 / Lib 1)
- `docs/architecture/INSTALL_MODEL.md` - excluded_duplicate; Install Model (ops0 / Lib 1)
- `docs/architecture/INSTALL_MODEL.md` - excluded_duplicate; Install Model (ops0 / Lib 1)
- `docs/architecture/INSTANCE_MODEL.md` - excluded_duplicate; Instance Model (ops0 / Lib 2)
- `docs/architecture/INSTANCE_MODEL.md` - excluded_duplicate; Instance Model (ops0 / Lib 2)
- `docs/architecture/INSTANCE_MODEL.md` - excluded_duplicate; Instance Model (ops0 / Lib 2)
- `docs/architecture/INSTITUTIONS_AND_GOVERNANCE_MODEL.md` - excluded_duplicate; Institutions And Governance Model (gov0)
- `docs/architecture/INSTITUTIONS_AND_GOVERNANCE_MODEL.md` - excluded_duplicate; Institutions And Governance Model (gov0)
- `docs/architecture/INSTITUTIONS_AND_GOVERNANCE_MODEL.md` - excluded_duplicate; Institutions And Governance Model (gov0)
- `docs/architecture/INTEREST_MODEL.md` - excluded_duplicate; Interest Model (scale0)
- `docs/architecture/INVARIANTS.md` - excluded_duplicate; Invariants (canon0)
- `docs/architecture/INVARIANTS_AND_TOLERANCES.md` - excluded_duplicate; Invariants And Tolerances (scale0)
- `docs/architecture/INVARIANT_REGISTRY.md` - excluded_duplicate; Invariant Registry
- `docs/architecture/JOIN_RESYNC_CONTRACT.md` - excluded_duplicate; Join And Resync Contract (mmo0)
- `docs/architecture/KNOWLEDGE_AND_SKILLS_MODEL.md` - excluded_duplicate; Knowledge And Skills Model (kns0)
- `docs/architecture/KNOWLEDGE_AND_SKILLS_MODEL.md` - excluded_duplicate; Knowledge And Skills Model (kns0)
- `docs/architecture/KNOWLEDGE_AND_SKILLS_MODEL.md` - excluded_duplicate; Knowledge And Skills Model (kns0)
- `docs/architecture/KNOWLEDGE_AND_SKILLS_MODEL.md` - excluded_duplicate; Knowledge And Skills Model (kns0)
- `docs/architecture/KNOWN_BLOCKERS.md` - excluded_duplicate; Known Blockers
- `docs/architecture/KNOWN_WARNINGS.md` - excluded_duplicate; Known Warnings
- `docs/architecture/LANGUAGE_STRATEGY.md` - excluded_duplicate; Language Strategy
- `docs/architecture/LAUNCHER_CONTRACT.md` - excluded_duplicate; Launcher Contract (dist2)
- `docs/architecture/LAW_AND_META_LAW.md` - excluded_duplicate; Law And Meta Law Split (lawmeta0)
- `docs/architecture/LAW_ENFORCEMENT_POINTS.md` - excluded_duplicate; Law Enforcement Points (exec0c)
- `docs/architecture/LEGACY_SUPPORT_MODEL.md` - excluded_duplicate; Legacy Support Model (ops1)
- `docs/architecture/LEGACY_SUPPORT_STRATEGY.md` - excluded_duplicate; Legacy Support Strategy (repox)
- `docs/architecture/LIFE_AND_POPULATION.md` - excluded_duplicate; Life And Population (life0+)
- `docs/architecture/LIVE_EVOLUTION_MODEL.md` - excluded_duplicate; Live Evolution Model (ops1)
- `docs/architecture/LOCKFILES.md` - excluded_duplicate; Lockfiles (lock0 / Lib 0)
- `docs/architecture/LOCKLIST.md` - excluded_duplicate; Locklist (gov0)
- `docs/architecture/MACRO_TIME_MODEL.md` - excluded_duplicate; Macro Time Model (scale0)
- `docs/architecture/MIGRATION_TEMPLATE.md` - excluded_duplicate; Migration Template
- `docs/architecture/MIGRATION_TEMPLATE.md` - excluded_duplicate; Migration Template
- `docs/architecture/MMO_COMPATIBILITY.md` - excluded_duplicate; Mmo Compatibility (mmo0)
- `docs/architecture/MMO_SAFETY_MODEL.md` - excluded_duplicate; Mmo Safety Model (mmo0)
- `docs/architecture/MODES_AS_PROFILES.md` - excluded_duplicate; Modes As Profiles
- `docs/architecture/MODPACK_FORMAT.md` - excluded_duplicate; Modpack Format (modpack0)
- `docs/architecture/MODULE_BOUNDARIES_v1.md` - excluded_duplicate; Module Boundaries V1
- `docs/architecture/MOD_ECOSYSTEM_RULES.md` - excluded_duplicate; Mod Ecosystem Rules (mod0)
- `docs/architecture/MOVEMENT_AS_LOGISTICS.md` - excluded_duplicate; Movement As Logistics (travel1)
- `docs/architecture/NAMESPACING_RULES.md` - excluded_duplicate; Namespacing Rules (ns0)
- `docs/architecture/NETWORKGRAPH_STANDARD.md` - excluded_duplicate; Networkgraph Standard
- `docs/architecture/NON_INTERFERENCE.md` - excluded_duplicate; Control Non Interference (testx2)
- `docs/architecture/NO_MAGIC_TELEPORTS.md` - excluded_duplicate; No Magic Teleports (travel2)
- `docs/architecture/NO_TELEPORTATION_EXCEPT_BY_CONTRACT.md` - excluded_duplicate; No Teleportation Except By Contract (travel0)
- `docs/architecture/OPS_TRANSACTION_MODEL.md` - excluded_duplicate; Ops Transaction Model (ops0)
- `docs/architecture/OVERVIEW_ARCHITECTURE.md` - excluded_duplicate; Dominium Architecture Overview
- `docs/architecture/PACK_FORMAT.md` - excluded_duplicate; Pack Format (ups1)
- `docs/architecture/PERFORMANCE_METRICS.md` - excluded_duplicate; Performance Metrics (perf1)
- `docs/architecture/PERFORMANCE_METRICS.md` - excluded_duplicate; Performance Metrics (perf1)
- `docs/architecture/PERFORMANCE_PROOF.md` - excluded_duplicate; Performance Proof (perf1)
- `docs/architecture/PERFORMANCE_PROOF.md` - excluded_duplicate; Performance Proof (perf1)
- `docs/architecture/PIRACY_CONTAINMENT.md` - excluded_duplicate; Piracy Containment (testx3)
- `docs/architecture/PLATFORM_RESPONSIBILITY.md` - excluded_duplicate; Platform Responsibility (platform Perfect 0)
- `docs/architecture/PLATFORM_RESPONSIBILITY.md` - excluded_duplicate; Platform Responsibility (platform Perfect 0)
- `docs/architecture/POST_CLEAN_2_STATUS.md` - excluded_duplicate; Post Clean 2 Status
- `docs/architecture/PROCESS_ONLY_MUTATION.md` - excluded_duplicate; Process Only State Mutation (proc0)
- `docs/architecture/PRODUCT_SHELL_CONTRACT.md` - excluded_duplicate; Product Shell Contract (shell0)
- `docs/architecture/PROJECTION_LIFECYCLE.md` - excluded_duplicate; Projection Lifecycle (repox)
- `docs/architecture/PROJECT_EXECUTION_BASELINE.md` - excluded_duplicate; Project Execution Baseline (mega Handoff)
- `docs/architecture/REALITY_FLOW.md` - excluded_duplicate; Reality Flow (reality0)
- `docs/architecture/REALITY_LAYER.md` - excluded_duplicate; Reality Layer (reality0)
- `docs/architecture/REALITY_MODEL.md` - excluded_duplicate; Reality Model (canon0)
- `docs/architecture/REDUCTION_MODEL.md` - excluded_duplicate; Reduction Model (deter 0)
- `docs/architecture/REDUCTION_MODEL.md` - excluded_duplicate; Reduction Model (deter 0)
- `docs/architecture/REFINEMENT_CONTRACTS.md` - excluded_duplicate; Refinement Contracts (exist1)
- `docs/architecture/REFRACTOR_STAGE.md` - excluded_duplicate; Refactor Stage Notes
- `docs/architecture/REFUSAL_AND_EXPLANATION_MODEL.md` - excluded_duplicate; Refusal And Explanation Model (omni2)
- `docs/architecture/REFUSAL_SEMANTICS.md` - excluded_duplicate; Refusal Semantics (refuse0)
- `docs/architecture/REGISTRY_PATTERN.md` - excluded_duplicate; Registry Pattern (category B)
- `docs/architecture/RENDERER_RESPONSIBILITY.md` - excluded_duplicate; Renderer Responsibility (renderer Perfect 0)
- `docs/architecture/REPLAY_AND_TIME_ASYMMETRY.md` - excluded_duplicate; Replay And Time Asymmetry (time3)
- `docs/architecture/REPLAY_FORMAT.md` - excluded_duplicate; Replay Format (replay1)
- `docs/architecture/REPORT_GAME_ARCH_DECISIONS.md` - excluded_duplicate; Report Game Arch Decisions
- `docs/architecture/REPOSITORY_STRUCTURE_v1.md` - excluded_duplicate; Repository Structure V1
- `docs/architecture/REPOX_AUTOMATION_MODEL.md` - excluded_duplicate; Repox Automation Model (repox Auto 0)
- `docs/architecture/REPO_INTENT.md` - excluded_duplicate; Repository Intent (clean1)
- `docs/architecture/REPO_NAV.md` - excluded_duplicate; Repository Navigation (nav0)
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md` - excluded_duplicate; Repo Ownership And Projections (repox)
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md` - excluded_duplicate; Repo Ownership And Projections (repox)
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md` - excluded_duplicate; Repo Ownership And Projections (repox)
- `docs/architecture/RETRO_CONSISTENCY_AUDIT_FRAMEWORK.md` - excluded_duplicate; Retro Consistency Audit Framework
- `docs/architecture/RISK_AND_LIABILITY_MODEL.md` - excluded_duplicate; Risk And Liability Model (risk0)
- `docs/architecture/RISK_AND_LIABILITY_MODEL.md` - excluded_duplicate; Risk And Liability Model (risk0)
- `docs/architecture/RISK_AND_LIABILITY_MODEL.md` - excluded_duplicate; Risk And Liability Model (risk0)
- `docs/architecture/RNG_MODEL.md` - excluded_duplicate; Rng Model (deter 0)
- `docs/architecture/RNG_MODEL.md` - excluded_duplicate; Rng Model (deter 0)
- `docs/architecture/RNG_MODEL.md` - excluded_duplicate; Rng Model (deter 0)
- `docs/architecture/ROLLING_UPDATES.md` - excluded_duplicate; Rolling Updates (mmo 2)
- `docs/architecture/ROOT_ARCHITECTURE.md` - excluded_duplicate; Dominium Architecture
- `docs/architecture/ROOT_ARCHITECTURE.md` - excluded_duplicate; Dominium Architecture
- `docs/architecture/ROOT_ARCHITECTURE.md` - excluded_duplicate; Dominium Architecture
- `docs/architecture/ROOT_ARCHITECTURE.md` - excluded_duplicate; Dominium Architecture
- `docs/architecture/ROOT_ARCHITECTURE.md` - excluded_duplicate; Dominium Architecture
- `docs/architecture/ROOT_ARCHITECTURE.md` - excluded_duplicate; Dominium Architecture
- `docs/architecture/ROOT_ARCHITECTURE.md` - excluded_duplicate; Dominium Architecture
- `docs/architecture/ROOT_ARCHITECTURE.md` - excluded_duplicate; Dominium Architecture
- `docs/architecture/SANDBOX_MODEL.md` - excluded_duplicate; Sandbox Model (ops0)
- `docs/architecture/SAVE_FORMAT.md` - excluded_duplicate; Save Format (save1)
- `docs/architecture/SAVE_MODEL.md` - excluded_duplicate; Save Model (save2 / Lib 3)
- `docs/architecture/SAVE_MODEL.md` - excluded_duplicate; Save Model (save2 / Lib 3)
- `docs/architecture/SAVE_MODEL.md` - excluded_duplicate; Save Model (save2 / Lib 3)
- `docs/architecture/SAVE_PIPELINE.md` - excluded_duplicate; Save Pipeline (save0)
- `docs/architecture/SCALE_AND_COMPLEXITY.md` - excluded_duplicate; Scale And Complexity (future0)
- `docs/architecture/SCALING_COMPATIBILITY.md` - excluded_duplicate; Scaling Compatibility (scale0)
- `docs/architecture/SCALING_MODEL.md` - excluded_duplicate; Scaling Model (scale0)
- `docs/architecture/SCHEMA_CHANGE_NOTES.md` - excluded_duplicate; Schema Change Notes
- `docs/architecture/SCHEMA_CHANGE_NOTES.md` - excluded_duplicate; Schema Change Notes
- `docs/architecture/SCHEMA_CHANGE_NOTES.md` - excluded_duplicate; Schema Change Notes
- `docs/architecture/SCHEMA_CHANGE_NOTES.md` - excluded_duplicate; Schema Change Notes
- `docs/architecture/SCHEMA_CHANGE_NOTES.md` - excluded_duplicate; Schema Change Notes
- `docs/architecture/SCHEMA_STABILITY.md` - excluded_duplicate; Schema Stability (clean1)
- `docs/architecture/SEMANTIC_STABILITY_POLICY.md` - excluded_duplicate; Semantic Stability Policy (stab0)
- `docs/architecture/SERVICES_AND_PRODUCTS.md` - excluded_duplicate; Services And Products (testx3)
- `docs/architecture/SETUP_TRANSACTION_MODEL.md` - excluded_duplicate; Setup Transaction Model (ops0 Setup)
- `docs/architecture/SHARD_LIFECYCLE.md` - excluded_duplicate; Shard Lifecycle (mmo 2)
- `docs/architecture/SHIM_SUNSET_PLAN.md` - excluded_duplicate; Shim Sunset Plan
- `docs/architecture/SHIM_SUNSET_PLAN.md` - excluded_duplicate; Shim Sunset Plan
- `docs/architecture/SIGNAL_MODEL.md` - excluded_duplicate; Signal Model (signal0)
- `docs/architecture/SIGNAL_MODEL.md` - excluded_duplicate; Signal Model (signal0)
- `docs/architecture/SIGNAL_MODEL.md` - excluded_duplicate; Signal Model (signal0)
- `docs/architecture/SLICE_0_CONTRACT.md` - excluded_duplicate; Slice 0 Contract
- `docs/architecture/SLICE_1_CONTRACT.md` - excluded_duplicate; Slice 1 Contract
- `docs/architecture/SLICE_2_CONTRACT.md` - excluded_duplicate; Slice 2 Contract
- `docs/architecture/SLICE_2_CONTRACT.md` - excluded_duplicate; Slice 2 Contract
- `docs/architecture/SPACE_AND_BOUNDS.md` - excluded_duplicate; Space And Bounds (domain0)
- `docs/architecture/SPACE_TIME_EXISTENCE.md` - excluded_duplicate; Space, Time, And Existence (reality0)
- `docs/architecture/SPECTATOR_AND_AUDIT_MODES.md` - excluded_duplicate; Spectator And Audit Modes (time3)
- `docs/architecture/SPECTATOR_TO_GODMODE.md` - excluded_duplicate; Spectator To Godmode (omni0)
- `docs/architecture/SRZ_MODEL.md` - excluded_duplicate; Simulation Responsibility Zones (srz0)
- `docs/architecture/SRZ_MODEL.md` - excluded_duplicate; Simulation Responsibility Zones (srz0)
- `docs/architecture/STANDARDS_AND_META_SYSTEMS_MODEL.md` - excluded_duplicate; Standards And Meta Systems Model (std0)
- `docs/architecture/STANDARDS_AND_META_SYSTEMS_MODEL.md` - excluded_duplicate; Standards And Meta Systems Model (std0)
- `docs/architecture/STANDARDS_AND_META_SYSTEMS_MODEL.md` - excluded_duplicate; Standards And Meta Systems Model (std0)
- `docs/architecture/STANDARDS_AND_META_SYSTEMS_MODEL.md` - excluded_duplicate; Standards And Meta Systems Model (std0)
- `docs/architecture/STRUCTURAL_STABILITY_MODEL.md` - excluded_duplicate; Structural Stability Model (terrain0)
- `docs/architecture/SYSTEM_TOPOLOGY_MAP.md` - excluded_duplicate; System Topology Map
- `docs/architecture/SYSTEM_TOPOLOGY_MAP.md` - excluded_duplicate; System Topology Map
- `docs/architecture/SYSTEM_TOPOLOGY_MAP.md` - excluded_duplicate; System Topology Map
- `docs/architecture/SYS_CAPS_AND_EXEC_POLICY.md` - excluded_duplicate; Syscaps And Execution Policy (hwcaps0)
- `docs/architecture/TERMINOLOGY_GLOSSARY.md` - excluded_duplicate; Terminology Glossary
- `docs/architecture/TERRAIN_COORDINATES.md` - excluded_duplicate; Terrain Coordinates (terrain0)
- `docs/architecture/TERRAIN_FIELDS.md` - excluded_duplicate; Terrain Field Stack (terrain0)
- `docs/architecture/TERRAIN_FIELDS.md` - excluded_duplicate; Terrain Field Stack (terrain0)
- `docs/architecture/TERRAIN_MACRO_CAPSULE.md` - excluded_duplicate; Terrain Macro Capsule (terrain0)
- `docs/architecture/TERRAIN_OVERLAYS.md` - excluded_duplicate; Terrain Overlays (terrain0)
- `docs/architecture/TERRAIN_PROVIDER_CHAIN.md` - excluded_duplicate; Terrain Provider Chain (terrain0)
- `docs/architecture/TERRAIN_TRUTH_MODEL.md` - excluded_duplicate; Terrain Truth Model (terrain0)
- `docs/architecture/THERMAL_MODEL.md` - excluded_duplicate; Thermal Model (thermal0)
- `docs/architecture/THERMAL_MODEL.md` - excluded_duplicate; Thermal Model (thermal0)
- `docs/architecture/THREAT_MODEL.md` - excluded_duplicate; Threat Model (testx2)
- `docs/architecture/TIMELINE_FORKS_AND_HISTORY.md` - excluded_duplicate; Timeline Forks And History (exist2)
- `docs/architecture/TIME_DILATION_WITHOUT_TIME_WARP.md` - excluded_duplicate; Time Dilation Without Time Warp (time2)
- `docs/architecture/TIME_PERCEPTION_VS_SIMULATION.md` - excluded_duplicate; Time Perception Vs Simulation (time2)
- `docs/architecture/TOOLS_AS_CAPABILITIES.md` - excluded_duplicate; Tools As Capabilities (omni1)
- `docs/architecture/TRANSITION_PLAYBOOK.md` - excluded_duplicate; Transition Playbook (lang1)
- `docs/architecture/TRAVEL_AND_MOVEMENT.md` - excluded_duplicate; Travel And Movement (travel0)
- `docs/architecture/TRAVEL_CAPACITY_AND_COST.md` - excluded_duplicate; Travel Capacity And Cost (travel1)
- `docs/architecture/TRAVEL_CAPACITY_AND_COST.md` - excluded_duplicate; Travel Capacity And Cost (travel1)
- `docs/architecture/TRUST_AND_LEGITIMACY_MODEL.md` - excluded_duplicate; Trust, Reputation, And Legitimacy Model (trust0)
- `docs/architecture/TRUST_AND_LEGITIMACY_MODEL.md` - excluded_duplicate; Trust, Reputation, And Legitimacy Model (trust0)
- `docs/architecture/TRUST_AND_LEGITIMACY_MODEL.md` - excluded_duplicate; Trust, Reputation, And Legitimacy Model (trust0)
- `docs/architecture/TRUST_AND_LEGITIMACY_MODEL.md` - excluded_duplicate; Trust, Reputation, And Legitimacy Model (trust0)
- `docs/architecture/UI_BINDING_MODEL.md` - excluded_duplicate; UI Binding Model (app UI Bind 0)
- `docs/architecture/UNIT_SYSTEM_POLICY.md` - excluded_duplicate; Unit System Policy (unit0)
- `docs/architecture/UNKNOWN_UNKNOWNS.md` - excluded_duplicate; Unknown Unknowns (future0)
- `docs/architecture/UPDATE_MODEL.md` - excluded_duplicate; Update Model (ops0)
- `docs/architecture/UPGRADE_AND_CONVERSION.md` - excluded_duplicate; Upgrade And Conversion (testx3)
- `docs/architecture/VISITABILITY_AND_REFINEMENT.md` - excluded_duplicate; Visitability And Refinement (reality0)
- `docs/architecture/VISITABILITY_CONSISTENCY.md` - excluded_duplicate; Visitability Consistency (exist1)
- `docs/architecture/WHAT_THIS_IS.md` - excluded_duplicate; What This Project Is (canon0)
- `docs/architecture/WHAT_THIS_IS_NOT.md` - excluded_duplicate; What This Project Is Not (canon0)
- `docs/architecture/WHY_ECONOMIES_DONT_FAKE.md` - excluded_duplicate; Why Economies Don't Fake (civ0+)
- `docs/architecture/WHY_NPCS_DONT_POP.md` - excluded_duplicate; Why Npcs Don't Pop (life0+)
- ... 13336 more omitted or reference-only blocks in `SOURCE_BLOCKS.yml`.
