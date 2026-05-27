Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: promotion_review_board_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_synthesis
Promotion Status: not_promoted
Source Class: conversation_corpus_synthesis


# Promotion Review Board v0

This board converts raw promotion candidates into bounded review items. It does not patch or promote live docs.

## Counts

- Total candidates: `135`
- `architecture_doc_candidate`: `16`
- `archive_only`: `9`
- `blocked_by_queue`: `10`
- `contract_candidate`: `11`
- `docs_clarification_candidate`: `1`
- `insufficient_evidence`: `53`
- `needs_user_decision`: `12`
- `planning_doc_candidate`: `1`
- `reject_as_noise`: `19`
- `schema_candidate`: `3`

## Review Items

### `PROMOTE-0001` - `needs_user_decision`

- Source conversation: `advanced_simulation_infrastructure`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it.

### `PROMOTE-0002` - `reject_as_noise`

- Source conversation: `advanced_simulation_infrastructure`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Finally, the chat shifted into archival mode: it produced a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat reader version. Those later outputs preserved the discussion for future aggregation.

### `PROMOTE-0003` - `architecture_doc_candidate`

- Source conversation: `advanced_simulation_infrastructure`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: [INFERENCE] The conclusion was not a finalized implementation but a working architecture: each simulation domain should be deterministic, fixed-point, content-driven, versioned, replayable, and integrated through clear read/write boundaries.

### `PROMOTE-0004` - `architecture_doc_candidate`

- Source conversation: `app_runtime_platform_renderers`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do.

### `PROMOTE-0005` - `blocked_by_queue`

- Source conversation: `app_runtime_platform_renderers`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: blocked queue scope
- Queue risk: `blocked`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, and introducing gameplay shortcuts. **FACT:** authoritative logic remains in engine + game.

### `PROMOTE-0006` - `needs_user_decision`

- Source conversation: `app_runtime_platform_renderers`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.

### `PROMOTE-0007` - `schema_candidate`

- Source conversation: `app_testx_codehygiene`
- Proposed target path: `schema/** or schemas/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: A large set of prompts was then generated to lock down architecture, determinism, performance, schema governance, rendering, epistemic UI, sharding, interest sets, and fidelity projection. This became the Phase 1 hardening layer. Additional audit prompts were introduced to ensure consistency before proceeding into life, civilization, war, content, agents, tools, mods, and final long-term policy.

### `PROMOTE-0008` - `reject_as_noise`

- Source conversation: `app_testx_codehygiene`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Because the chat was huge, the user asked for a maximum-fidelity context transfer packet. Then they asked for downloadable report files. Then they asked for an in-chat reader. Finally, they asked for this human-readable explanatory report. This final report is meant to let a future assistant or human understand the substance without re-reading the whole conversation.

### `PROMOTE-0009` - `contract_candidate`

- Source conversation: `app_testx_codehygiene`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: The central project is a deterministic universe engine/game. The user's ambition is not just a normal game but a world runtime that can represent everything from a single-room scenario to an AI-only universe to an MMO. The project is meant to support real-world defaults, arbitrary modding, procedural and defined content, strong epistemics, and long-term replayability.

### `PROMOTE-0010` - `insufficient_evidence`

- Source conversation: `architecture_codex_prompts`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The most important thing to remember is this: **this chat is the architectural and implementation-roadmap backbone for Dominium/Domino, but it is not an implementation log**. It should be preserved as a design/specification source and as a prompt library, while actual code and current facts must be verified separately.

### `PROMOTE-0011` - `insufficient_evidence`

- Source conversation: `architecture_codex_prompts`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: FACT: The user opened by pasting an "Extended Master Starter Prompt - Dominium + Domino." That prompt established the role of the assistant as a senior engine architect and defined the main project philosophy. Domino was described as a deterministic, fixed-point, C89 engine portable across old and modern OS/architecture combinations. Dominium was described as the product suite built on top of Domino.

### `PROMOTE-0012` - `archive_only`

- Source conversation: `architecture_codex_prompts`
- Proposed target path: `docs/archive/conversations/**`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: FACT: The user asked, succinctly, how a player would build a complete machine workshop. The assistant described a progression: extract raw materials, process them into industrial materials, produce mechanical components, produce electrical components, establish power distribution, establish logistics, assemble machine frames and machines, add measurement/control tooling, then scale horizontally and vertically.

### `PROMOTE-0013` - `insufficient_evidence`

- Source conversation: `architecture_ui_providers`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The language baseline decision matters because it changes what old renderers and toolchains matter. C17/C++17 reduces the need to design around C89/C++98 constraints but does not remove the need for C-compatible ABI boundaries. The system floor decision similarly moves many older renderers and OS targets into research/back-port categories.

### `PROMOTE-0014` - `insufficient_evidence`

- Source conversation: `architecture_ui_providers`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.

### `PROMOTE-0015` - `blocked_by_queue`

- Source conversation: `architecture_ui_providers`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: blocked queue scope
- Queue risk: `blocked`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.

### `PROMOTE-0016` - `archive_only`

- Source conversation: `Build_and_Future_Proofing`
- Proposed target path: `docs/archive/conversations/**`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.

### `PROMOTE-0017` - `reject_as_noise`

- Source conversation: `Build_and_Future_Proofing`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The final uploaded prompt requested a complete preservation package for this chat: a human-readable explanation, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, and files/ZIP package. This response completes that export task and creates downloadable files for later reading and aggregation.

### `PROMOTE-0018` - `archive_only`

- Source conversation: `Build_and_Future_Proofing`
- Proposed target path: `docs/archive/conversations/**`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The final explicit goal was preservation: create a maximum-fidelity package for this chat so the user can understand it later, ask questions in this chat, merge it with other old-chat reports, and eventually build a master project spec book.

### `PROMOTE-0019` - `insufficient_evidence`

- Source conversation: `canonical_structure_and_framework`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: This produced a pattern: generate a large Codex/AIDE task, the user ran it or reported a result, then the assistant evaluated what was truly fixed versus what was only validator/document churn. The user eventually demanded a one-shot "actual final cleanup" prompt because previous passes had sometimes added validators without moving directories. That prompt explicitly required real `git mv` routing, not just reports.

### `PROMOTE-0020` - `blocked_by_queue`

- Source conversation: `canonical_structure_and_framework`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: blocked queue scope
- Queue risk: `blocked`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The final provider directory doctrine became service-first: `runtime/<service>/providers/<provider>/`, not `runtime/<vendor>/<service>/`. Provider choices belong in `release/profiles/` or `content/profiles/`, not app path names. External code belongs under `external/upstream/` or `external/vendor/`, but the repo should choose one convention.

### `PROMOTE-0021` - `schema_candidate`

- Source conversation: `canonical_structure_and_framework`
- Proposed target path: `schema/** or schemas/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: Packs are distributable authored payloads. The preferred pack layout became category-based, such as `content/packs/<category>/<pack_id>/`. Pack IDs must not depend on paths. Saves and replays must use stable IDs, schema versions, canonical serialization, deterministic hashes, and explicit migration/refusal policies. Backward compatibility must be a compatibility corpus plus tests, not intention.

### `PROMOTE-0022` - `insufficient_evidence`

- Source conversation: `Chronology_Celestial_Systems`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: This reinforced the core celestial-content rule: locations should exist explicitly when they change player decisions.

### `PROMOTE-0023` - `insufficient_evidence`

- Source conversation: `Chronology_Celestial_Systems`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: This became the spatial foundation for later time/calendar decisions because every major body or region could potentially have its own local time, calendar, or operational standard.

### `PROMOTE-0024` - `needs_user_decision`

- Source conversation: `Chronology_Celestial_Systems`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.

### `PROMOTE-0025` - `needs_user_decision`

- Source conversation: `development_routes`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict determinism matters, whether replay or multiplayer are goals, whether modding matters, and what the actual game loop is. Until then, the kernel-first plan should be treated as a strong provisional proposal, not a final specification.

### `PROMOTE-0026` - `insufficient_evidence`

- Source conversation: `development_routes`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The first answer was assertive. It stated that Dominium must follow Route C and described the route as the only viable one for Dominium. Later parts of the chat corrected the status of that claim. FACT: the assistant made that recommendation. UNCERTAIN / UNVERIFIED: the recommendation was not validated with external sources in the chat and was not explicitly accepted by the user.

### `PROMOTE-0027` - `archive_only`

- Source conversation: `development_routes`
- Proposed target path: `docs/archive/conversations/**`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The initial technical answer proposed a layered stack. It started with mathematical and temporal primitives, then moved into the deterministic simulation kernel, then world state, systems, persistence and replay, tooling, presentation, content, and finally distribution, modding, and multiplayer.

### `PROMOTE-0028` - `needs_user_decision`

- Source conversation: `documentation_standards_readme`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions.

### `PROMOTE-0029` - `contract_candidate`

- Source conversation: `documentation_standards_readme`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: `FACT:` The chat established that public API contracts should live in headers.

### `PROMOTE-0030` - `insufficient_evidence`

- Source conversation: `documentation_standards_readme`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: `FACT:` Source files should document implementation rationale, non-obvious invariants, and hazards.

### `PROMOTE-0031` - `reject_as_noise`

- Source conversation: `Dominium_Architecture_I`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: During this stage, the work was still broadly about "the project spec." The user wanted a comprehensive description of the game and its technical systems. The assistant produced large design documents, but many of those earlier contents are not visible in the retained transcript. This is important because the final report package marks those earlier outputs as referenced but not fully recovered.

### `PROMOTE-0032` - `architecture_doc_candidate`

- Source conversation: `Dominium_Architecture_I`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in filenames. Instead, those details should live in metadata. This became part of the future build/package design.

### `PROMOTE-0033` - `insufficient_evidence`

- Source conversation: `Dominium_Architecture_I`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The key change came when the user decided that Codex could not read the entire conversation at once. **FACT:** The user said they would copy and paste the transcript with timestamps and would not edit it manually, but because Codex could not read the whole context at once, they would not bother asking Codex to compile a full book directly from the whole chat.

### `PROMOTE-0034` - `reject_as_noise`

- Source conversation: `Dominium_Architecture_II`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The last part of the chat was handoff extraction. The user asked for discovery inventory, structured registers, a context transfer packet, and then a downloadable package. The generated package captured the chat's workstreams, decisions, tasks, constraints, open questions, artifacts, risks, and verification items. This current report is a plain-language explanation of that substance.

### `PROMOTE-0035` - `architecture_doc_candidate`

- Source conversation: `Dominium_Architecture_II`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The entire conversation is anchored by the requirement that Dominium must run deterministically. This means the same initial state and same inputs must produce the same state across machines, compilers, operating systems, and eventually retro and modern platforms.

### `PROMOTE-0036` - `insufficient_evidence`

- Source conversation: `Dominium_Architecture_II`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The chat discussed fixed tick phases, virtual lanes, merge order, command buffers, event queues, and deterministic serialization. The simulation must not depend on render FPS, wall-clock time, OS scheduler behaviour, GPU state, or floating-point quirks. This explains many later decisions: C89 core, integer/fixed-point math, no sim floats, no platform headers in simulation, and renderer as pure observer.

### `PROMOTE-0037` - `insufficient_evidence`

- Source conversation: `Dominium_Architecture_III`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The view system then expanded beyond the launcher. **FACT:** The user wants instant zoom to any scale, instant switching between top-down 2D and first-person 3D, and arbitrary cameras for free cam, map viewing, content creation, HUD cameras, CCTV, overlays, windows, and offscreen targets. These are client/render-side concerns, not simulation concerns.

### `PROMOTE-0038` - `architecture_doc_candidate`

- Source conversation: `Dominium_Architecture_III`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: This context matters because the rest of the conversation happened inside those constraints. The launcher could not become a dumping ground for OS-specific behavior, sim mutation, renderer decisions, or nondeterministic game-state changes. It had to fit the project's deterministic layering.

### `PROMOTE-0039` - `insufficient_evidence`

- Source conversation: `Dominium_Architecture_III`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user then uploaded `dominium.7z`, saying it was the git repository as of that moment. **FACT:** The prior assistant said it could not open `.7z` archives in that environment. That means the actual repository state remained unverified at that stage. This became important later, because many implementation ideas were discussed without confirmed access to the repo contents.

### `PROMOTE-0040` - `insufficient_evidence`

- Source conversation: `Dominium_Architecture_IV`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The reusable engine layer was named **Domino**. This became one of the most important naming and architectural decisions in the chat. Domino is the engine/core/platform/sim/mod layer, reusable for other games and projects. Dominium is the game/product layer built on it.

### `PROMOTE-0041` - `insufficient_evidence`

- Source conversation: `Dominium_Architecture_IV`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Blueprints are plans or diffs: place element, remove element, modify terrain, place machine, connect network, etc. When accepted, they generate jobs. Manual player actions and queued work for humans, robots, or other agents should use the same job pipeline. This matters because it keeps replay, AI, and automation consistent.

### `PROMOTE-0042` - `insufficient_evidence`

- Source conversation: `Dominium_Architecture_IV`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user then asked how to structure Codex prompts. The final high-level roadmap became:

### `PROMOTE-0043` - `needs_user_decision`

- Source conversation: `Dominium_Complete_Conversation`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still follows that contract, and finally broadening the question into a platform-engineering doctrine for portability, modularity, extensibility, reuse, future-proofing, and long-term compatibility.

### `PROMOTE-0044` - `contract_candidate`

- Source conversation: `Dominium_Complete_Conversation`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: The glossary bound terms such as Authority, Law, Process, Lens, SessionSpec, UniverseIdentity, Macro Capsule, SRZ, RepoX, TestX, AuditX, CompatX, SecureX, and related terms. It matters because future assistants must not use sloppy synonyms like "mode" where the canon requires ExperienceProfile or LawProfile. This topic directly supports modularity because stable vocabulary is part of stable architecture.

### `PROMOTE-0045` - `insufficient_evidence`

- Source conversation: `Dominium_Complete_Conversation`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Uncertainty: during this preservation pass, a potential inconsistency appeared: some docs claim product roots moved under `apps/`, while an earlier inspected code path under root `client/` was available and `apps/client` was not fetched successfully. This must be verified against the current physical tree.

### `PROMOTE-0046` - `insufficient_evidence`

- Source conversation: `dominium_domino_codex_planning`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: INFERENCE:** The user accepted this direction in practice, because the next request was to generate Codex prompts to implement each step fully. The user did not explicitly say, "I formally approve the Milestone-0 plan," but they proceeded to ask for prompts based on it.

### `PROMOTE-0047` - `insufficient_evidence`

- Source conversation: `dominium_domino_codex_planning`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user then asked for recommendations. The assistant recommended a clean startup policy: explicit flags first, no environment/config override in v1, terminal detection through dsys, generic AUTO behavior, product-specific headless handling for the game, build-time GUI/TUI capabilities, and structural error codes for fallback. The user accepted this enough to request a "one big Codex prompt" to implement it.

### `PROMOTE-0048` - `reject_as_noise`

- Source conversation: `dominium_domino_codex_planning`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: However, the later context transfer packet treated that inspection claim as **UNCERTAIN / UNVERIFIED**. This was careful and correct: within the visible chat, there was no reliable tool trace proving the repo had actually been inspected. Therefore, future assistants must verify `dominium.zip` or the active checkout before relying on the platform/render/API answer.

### `PROMOTE-0049` - `blocked_by_queue`

- Source conversation: `dominium_full_conversation`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: blocked queue scope
- Queue risk: `blocked`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: A future assistant must understand that this chat is not simply about UI. It records the architecture for how Dominium should build itself: through contracts, commands, services, providers, documents, patches, modules, packs, apps, workspaces, diagnostics, evidence, AIDE, Codex, and eventually Workbench.

### `PROMOTE-0050` - `architecture_doc_candidate`

- Source conversation: `dominium_full_conversation`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The user then redirected the entire plan. They argued that native OS widget GUI tools already exist through Visual Studio, Xcode, etc. The project needed a cross-platform rendered tool environment that uses the same CLI, TUI, and rendered GUI systems as the client. The old UI Editor and Tool Editor were good exploratory ideas but bad final products. This produced the Dominium Workbench concept.

### `PROMOTE-0051` - `insufficient_evidence`

- Source conversation: `dominium_full_conversation`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The discussion then moved into AIDE. The user wanted to automate as much as possible through Codex and AIDE. We developed a task operating model: AIDE creates WorkUnits, tracks attempts, blockers, evidence, repairs, resumes, checkpoints, and promotion decisions. Codex executes bounded tasks. Development can continue with classified partials and repairable blockers; promotion to main requires evidence.

### `PROMOTE-0052` - `reject_as_noise`

- Source conversation: `dominium_setup`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Near the end, the chat shifted into preservation mode. The user asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat reader version of that package. Those outputs preserved the decisions, tasks, constraints, artifacts, rejected options, and verification queue for future assistants or aggregation into a larger Project Spec Book.

### `PROMOTE-0053` - `archive_only`

- Source conversation: `dominium_setup`
- Proposed target path: `docs/archive/conversations/**`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: These directory trees were not final, but they mattered because they exposed the user's preference for simple, shallow, logical structures and native IDE workflows that do not become the source of truth.

### `PROMOTE-0054` - `planning_doc_candidate`

- Source conversation: `dominium_setup`
- Proposed target path: `docs/planning/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The user later asked where to create Visual Studio and Xcode apps after opening the repo as a folder. The assistant advised that Visual Studio and Xcode projects should be generated through CMake, not hand-authored or treated as authoritative source files. This decision became consistent with later Codex prompts.

### `PROMOTE-0055` - `contract_candidate`

- Source conversation: `Domino_Dominium_Workbench`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: The original UI Editor / Tool Editor plan is now **superseded as a final product**. It is not lost: its useful parts become Workbench capabilities, especially Interface Studio, UI/HUD Sandbox, Theme Laboratory, TUI Studio, Rendered GUI Studio, Preview Matrix, validation panels, import/export tools, and document-patch workflows.

### `PROMOTE-0056` - `blocked_by_queue`

- Source conversation: `Domino_Dominium_Workbench`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: blocked queue scope
- Queue risk: `blocked`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The central decision is that Workbench must not become semantic authority. Workbench is a surface over contracts, commands, services, documents, patches, providers, packs, modules, apps, artifacts, diagnostics, evidence, tests, and replay/proof. It is the richest human/agent interface over the system, but it must not bypass command, capability, refusal, validation, document, patch, or proof law.

### `PROMOTE-0057` - `blocked_by_queue`

- Source conversation: `Domino_Dominium_Workbench`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: blocked queue scope
- Queue risk: `blocked`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The second central decision is that CLI, TUI, rendered GUI, OS-native GUI, and headless automation must be **projections of the same command/result/refusal/document/view spine**. A GUI button, a TUI hotkey, a CLI command, a headless JSON job, and a future OS-native widget action should route through the same command/service path and produce the same typed result, diagnostics, refusals, logs, and evidence.

### `PROMOTE-0058` - `insufficient_evidence`

- Source conversation: `domino_engine_refactor_prompts`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: FACT:** The Domino engine must be ISO C89. The Dominium UI/tools layer must be portable C++98. Engine code must not use OS APIs. Determinism matters, so floats are disallowed in deterministic paths. The engine must avoid platform-dependent behavior and hardcoded game semantics. Everything should be content-driven.

### `PROMOTE-0059` - `contract_candidate`

- Source conversation: `domino_engine_refactor_prompts`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: This became one of the central architectural ideas of the chat. It makes behavior extensible without giving minds direct write access to the world. A mod can add new sensors, observations, intents, capabilities, or actions, but state mutation still passes through a deterministic pipeline.

### `PROMOTE-0060` - `reject_as_noise`

- Source conversation: `domino_engine_refactor_prompts`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: After the architecture and prompts were created, the user asked for a maximum-fidelity context transfer packet. The assistant produced one. The user then asked for a downloadable report package; the assistant generated package files and a ZIP. The user later asked for an in-chat reader version of that package, and finally requested this current human-readable explanatory report.

### `PROMOTE-0061` - `insufficient_evidence`

- Source conversation: `engine_baseline_architecture`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: This corrected the plan. The final sequencing became: first **Milestone 0: Make the baseline path honest**. That means fixing server/runtime circular import, CLI forwarding, `session_create -> session_boot`, missing time-anchor policy registry, and making the strict local playtest validator pass. Only after that should the builder/destruction lab begin.

### `PROMOTE-0062` - `reject_as_noise`

- Source conversation: `engine_baseline_architecture`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The final user action uploaded `Pasted text.txt`, a detailed instruction prompt requiring a full preservation report, structured registers, spec sheet, aggregator packet, self-audit, and downloadable file package for this chat. That request is the current task.

### `PROMOTE-0063` - `architecture_doc_candidate`

- Source conversation: `engine_baseline_architecture`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The central architecture distinction was that Domino should be a reusable deterministic simulation substrate, while Dominium should be one game/product layer built on it. This came up immediately when the user asked for a total description of the project. It mattered because the user wants the code to be reusable for future games and possibly other engine projects.

### `PROMOTE-0064` - `insufficient_evidence`

- Source conversation: `Foundation_Workbench_Codex`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: After the root skeleton improved, the assistant and user recognized that the deeper problem was no longer top-level directories. The problem became semantic duplication and governance: what is public, what is private, what is stable, what is provisional, what is generated, what is a fixture, what must stay compatible, what can be replaced, and what proof is required.

### `PROMOTE-0065` - `blocked_by_queue`

- Source conversation: `Foundation_Workbench_Codex`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: blocked queue scope
- Queue risk: `blocked`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The key conclusion was that Workbench is not the general module system; it is one consumer of the module/command/service/provider/pack/artifact system. Workbench must not call private tools directly. It must route through registered commands and typed results, diagnostics, refusals, views, and evidence.

### `PROMOTE-0066` - `contract_candidate`

- Source conversation: `Foundation_Workbench_Codex`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: The topic came up because the project needed a model that could support world simulation, modding, tooling, Workbench, release, portability, and future games without repeating endless refactors. The conclusion was that stable contracts and semantic IDs must be separated from replaceable private implementation.

### `PROMOTE-0067` - `reject_as_noise`

- Source conversation: `Framework_Open_Source_Provider`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Finally, the user uploaded a detailed preservation prompt and requested a maximum-fidelity report, registers, spec sheet, aggregator packet, audit, and downloadable files. This package is the response to that request.

### `PROMOTE-0068` - `insufficient_evidence`

- Source conversation: `Framework_Open_Source_Provider`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: This became the central architectural theme. The conversation refined earlier vendor-shaped paths into service-first paths. The stable pattern is:

### `PROMOTE-0069` - `blocked_by_queue`

- Source conversation: `Framework_Open_Source_Provider`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: blocked queue scope
- Queue risk: `blocked`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The chat inspected `julesc013/dominium` and found evidence of existing abstractions such as system and graphics layers, stubs, and soft-backed backends. The finding was that raylib could fill concrete provider gaps without replacing the architecture. However, current repo facts are stale/uncertain and must be verified, especially the C17/C++17 vs C90/C++98 baseline contradiction.

### `PROMOTE-0070` - `insufficient_evidence`

- Source conversation: `gui_binary_content`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: That was an important change of direction. It meant the assistant's polished prompt should not be treated as final. The work needed conceptual discussion first. The assistant then analyzed CONTENT0 and identified several issues that could cause bad assumptions to become embedded if Codex acted too soon.

### `PROMOTE-0071` - `insufficient_evidence`

- Source conversation: `gui_binary_content`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: what start scenarios must explicitly exclude,

### `PROMOTE-0072` - `insufficient_evidence`

- Source conversation: `gui_binary_content`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: This shifted the content work from "populate required files" to "design a scalable content representation system." It also made clear that procedural generation and defined data are not enemies in the user's vision. The desired architecture must allow them to coexist.

### `PROMOTE-0073` - `architecture_doc_candidate`

- Source conversation: `Language_Platform_Architecture`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The 32-bit question followed. The answer was to make full native products 64-bit and keep 32-bit as constrained or projection support only. The key caveat was not to make native pointer size part of game law. Save, replay, network, IDs, and renderer IR must use fixed-width types and never serialize size_t, long, uintptr_t, or raw pointers.

### `PROMOTE-0074` - `contract_candidate`

- Source conversation: `Language_Platform_Architecture`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: The user then consolidated a broad future plan around Domino, Dominium, Workbench, AIDE, contracts, tests, replay, and evidence. The answer agreed that the plan was strong, but identified missing central pieces: composition resolver, lockfiles, compatibility corpus, trust/permissions, virtual filesystem roots, performance budgets, and stable public-surface promotion rules.

### `PROMOTE-0075` - `blocked_by_queue`

- Source conversation: `Language_Platform_Architecture`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: blocked queue scope
- Queue risk: `blocked`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Finally, the user pasted advice favoring C99 or C++11 due to raylib/SDL and legacy targets. The answer rejected a pivot. Raylib and SDL2 being C APIs only means provider boundaries should be C-callable; it does not force the whole engine or game to C99. The final recommendation remained C17 + C++17, with raylib/SDL2 treated as providers and with external deployment claims placed into the verification queue.

### `PROMOTE-0076` - `needs_user_decision`

- Source conversation: `launcher_app_layer`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Someone reading this report should understand one central thing: this chat is not about inventing new launcher features anymore. It is about preserving boundaries, making the launcher implementation explicit, and ensuring future work happens on top of verified code rather than vague architectural memory.

### `PROMOTE-0077` - `archive_only`

- Source conversation: `launcher_app_layer`
- Proposed target path: `docs/archive/conversations/**`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: There was also an early suggestion to create a `DUI` facade, a Dominium UI abstraction, to support native widgets and fallback rendering. This idea was useful as a conceptual stepping stone but was not ultimately locked as a final requirement in the form originally suggested. Later application-layer canon emphasized **UI IR**, **command graphs**, and **binding validation** rather than a specific `DUI` facade design.

### `PROMOTE-0078` - `schema_candidate`

- Source conversation: `launcher_app_layer`
- Proposed target path: `schema/** or schemas/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: This phase mattered because it framed the launcher not as a menu program but as a **control plane** for installed products, packs, profiles, compatibility, and launch contracts. However, later canon tightened the permitted communication routes: cross-product communication must go through `schema/` and `libs/contracts`, not arbitrary plugin conventions.

### `PROMOTE-0079` - `reject_as_noise`

- Source conversation: `Launcher_Setup_Architecture`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The chat also produced multiple Codex work-order prompts and finally a downloadable report package. Those artifacts are useful, but the substance is the architecture: keep engine deterministic, keep setup/launcher/runtime boundaries explicit, make the launcher optional and modular, use a strong process/instance model, and now implement the launcher over dsys/dgfx rather than ad hoc platform UI stacks.

### `PROMOTE-0080` - `insufficient_evidence`

- Source conversation: `Launcher_Setup_Architecture`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: FACT:** The user's initial architecture text emphasized:

### `PROMOTE-0081` - `contract_candidate`

- Source conversation: `Launcher_Setup_Architecture`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: The assistant responded by stress-testing this philosophy. It pointed out determinism risks around Lua, plugins, time sources, and ABI details, and suggested more explicit contracts for file headers, TLV sections, runtime CLI capabilities, plugin exported symbols, and setup/launcher boundaries. These were assistant proposals, not all user-stated decisions, but the user continued building on that direction.

### `PROMOTE-0082` - `reject_as_noise`

- Source conversation: `Modularity_AIDE_Refactorability`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The final user action was uploading a preservation-package prompt. That prompt requested a maximum-fidelity preservation report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, downloadable files, and a final in-chat reader. This package is the result.

### `PROMOTE-0083` - `insufficient_evidence`

- Source conversation: `Modularity_AIDE_Refactorability`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user objected to the XStack/AuditX/RepoX/TestX framing and wanted AIDE adopted quickly. The resulting plan made AIDE the repo-native control plane for inventory, task queues, policies, move maps, salvage maps, evidence ledgers, validation, and refactor history. Existing tools should be recycled, not discarded. This is central to future refactorability.

### `PROMOTE-0084` - `architecture_doc_candidate`

- Source conversation: `Modularity_AIDE_Refactorability`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The discussion proposed target-based CMake and module boundaries rather than path mythology. Public headers, private headers, allowed dependencies, and forbidden dependencies should be explicit. Apps must remain thin. Engine must not depend on game/apps/runtime UI. Runtime adapts host/platform/rendering without owning simulation truth.

### `PROMOTE-0085` - `insufficient_evidence`

- Source conversation: `omega_xi_pi_architecture_future`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The final strategic direction before this preservation request was to run a ?-series: snapshot intake, reality extraction, blueprint reconciliation, foundation readiness, and final prompt synthesis. This is needed because plans must now be mapped onto current repo reality rather than executed abstractly. The next chat should pick up there.

### `PROMOTE-0086` - `insufficient_evidence`

- Source conversation: `omega_xi_pi_architecture_future`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user later reported Xi completion. The enduring lesson is that prompt instructions are not enough; architecture must be machine-readable and enforced.

### `PROMOTE-0087` - `insufficient_evidence`

- Source conversation: `omega_xi_pi_architecture_future`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: 4. Preserve all plans, tasks, constraints, risks, decisions, artifacts, and future directions across chats.

### `PROMOTE-0088` - `architecture_doc_candidate`

- Source conversation: `OS_Interface_Repo_Architecture`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: DECISION-01 - CLI mandatory, TUI expected, GUI modular.** This was part of the initial architecture baseline and was repeatedly reaffirmed. It matters because every product must remain operable in recovery/headless/automation contexts. GUI is allowed but not authoritative.

### `PROMOTE-0089` - `contract_candidate`

- Source conversation: `OS_Interface_Repo_Architecture`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: DECISION-02 - Thin GUI shells over shared contracts.** The chat consistently rejected GUI families becoming separate product architectures. This affects client, launcher, setup, server admin, tools, and Workbench modules.

### `PROMOTE-0090` - `contract_candidate`

- Source conversation: `OS_Interface_Repo_Architecture`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: DECISION-03 - Repo ownership layout.** The user pushed for repository convergence; the discussion established that folders should map to ownership and contract boundaries. This decision is final enough to guide work, but details remain subject to machine-readable layout contracts.

### `PROMOTE-0091` - `reject_as_noise`

- Source conversation: `platform_renderer_api_plan`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The chat ended by generating a maximum-fidelity transfer packet, then a downloadable report package, then an in-chat reader version. The main thing to remember is this: **the active artifact is the final 9-prompt post-master Codex plan, but it is a plan, not evidence that the code exists. The repo must be inspected before execution.

### `PROMOTE-0092` - `insufficient_evidence`

- Source conversation: `platform_renderer_api_plan`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: These ideas became the architectural heart of the final plan.

### `PROMOTE-0093` - `insufficient_evidence`

- Source conversation: `platform_renderer_api_plan`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Stable ABI boundaries must use C ABI, POD structs, explicit function tables, and `u32 abi_version` plus `u32 struct_size` first.

### `PROMOTE-0094` - `insufficient_evidence`

- Source conversation: `platform_support`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: FACT: That early answer was generated by the assistant, not stated by the user as a final decision. It matters because it introduced a very broad portability ambition, but it was later superseded by more practical platform planning. It should now be treated as historical context or possible research scope, not as a controlling product commitment.

### `PROMOTE-0095` - `insufficient_evidence`

- Source conversation: `platform_support`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user then supplied a detailed inventory covering PlayStation, Xbox, Nintendo, PC handhelds, Android devices, Apple devices, Web platforms, AR, VR, and cross-cutting software targets. This inventory became the central artifact of the chat.

### `PROMOTE-0096` - `insufficient_evidence`

- Source conversation: `platform_support`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: FACT: The user's list included legacy and current consoles, handhelds, firmware/OS names, Android software variants, Apple OSes, Web runtimes, AR/VR hardware, XR platforms, and graphics/runtime APIs. FACT: It was a list of desired coverage or consideration, not a final statement that every item must receive full parity support.

### `PROMOTE-0097` - `needs_user_decision`

- Source conversation: `Portability_Assurance_Future_Proof`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.

### `PROMOTE-0098` - `insufficient_evidence`

- Source conversation: `Portability_Assurance_Future_Proof`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Status: Assistant recommendation; not separately accepted after answer.

### `PROMOTE-0099` - `insufficient_evidence`

- Source conversation: `Portability_Assurance_Future_Proof`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Rationale: Replacement must be objectively testable.

### `PROMOTE-0100` - `docs_clarification_candidate`

- Source conversation: `readme_ports_determinism`
- Proposed target path: `README.md or docs/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The user pasted the final README after those cleanup changes. At that point, the README had the current active form: deterministic constraints clarified, ports unified under one source hierarchy, `/ports` metadata-only if retained, Section 9 normative, lockstep canonical, content-lock mismatch fatal, and disk format versions immutable.

### `PROMOTE-0101` - `reject_as_noise`

- Source conversation: `readme_ports_determinism`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: After the README work, the user asked for a maximum-fidelity context transfer packet. The assistant produced a long state-transfer document with sections for project inventory, decisions, tasks, constraints, open questions, artifacts, risks, and next actions.

### `PROMOTE-0102` - `architecture_doc_candidate`

- Source conversation: `readme_ports_determinism`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The central artifact was the root `README.md`. The README describes **Domino** as the deterministic engine core and **Dominium** as the official game/tooling/runtime layer. It is written as a high-level architecture document, not a low-level implementation spec.

### `PROMOTE-0103` - `insufficient_evidence`

- Source conversation: `Refactor_Architecture`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The most important thing to remember is that this chat did not implement the refactor. It designed the architecture and generated prompts and handoff material. Any future assistant must verify actual repository state before assuming files were moved, prompts were applied, or code was updated.

### `PROMOTE-0104` - `archive_only`

- Source conversation: `Refactor_Architecture`
- Proposed target path: `docs/archive/conversations/**`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: FACT:** This early discussion created the future UI/packs design context.

### `PROMOTE-0105` - `architecture_doc_candidate`

- Source conversation: `Refactor_Architecture`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: FACT:** All products should use shared `dsys` and `dgfx`. No product-specific platform or renderer code path.

### `PROMOTE-0106` - `insufficient_evidence`

- Source conversation: `Refactor_Control_Plane`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user then asked about optimizing prompts for GPT-5.3/GPT-5.4 and later supplied advice about harness engineering. That advice argued that teams succeed by engineering the environment around agents: tools, docs, linters, feedback loops, memory, and observability. The conversation accepted the core point: the model is not the whole system; the harness is the multiplier.

### `PROMOTE-0107` - `insufficient_evidence`

- Source conversation: `Refactor_Control_Plane`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The Grug Brained Developer became a design filter: avoid complexity, avoid premature abstraction, do small safe refactors, prefer integration tests, invest in logging, and respect existing structures before tearing them down. This influenced the decision to narrow AIDE and not overbuild runtime/hosts too early.

### `PROMOTE-0108` - `archive_only`

- Source conversation: `Refactor_Control_Plane`
- Proposed target path: `docs/archive/conversations/**`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user eventually named AIDE: Automated Integrated Development Environment. The accepted split became: XStack remains Dominium's strict local governance/proof profile; AIDE becomes the portable public layer. AIDE would live in its own repo, be usable as a standalone repo pack, later as CLI/app/extensions, and eventually perhaps a runtime/service/host system.

### `PROMOTE-0109` - `insufficient_evidence`

- Source conversation: `Release_Identity_and_Versioning`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user then objected to versioning policy drift in real products and expressed concern about SemVer's "1.x forever" failure mode. The first proposed answer was a four-part public version scheme, `GEN.EPOCH.FEATURE.PATCH`, meant to avoid fake major bumps. That idea was useful as an intermediate step but later became less central because XStack already has GBN for dense build history and separate build identity.

### `PROMOTE-0110` - `insufficient_evidence`

- Source conversation: `Release_Identity_and_Versioning`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The conversation then moved into how this might fit XStack. The model shifted from "better public version number" to "layered identity model." The assistant recommended preserving per-product versions, a global build number, build IDs, compatibility versions, and suite versions as separate layers. This became the foundation for later decisions.

### `PROMOTE-0111` - `insufficient_evidence`

- Source conversation: `Release_Identity_and_Versioning`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user suggested that suites might use a separate consumer-facing or marketing version, while each component could use stricter SemVer. The chat accepted this as a mature pattern: suites are curated bundles, while components may have technical versions. The model was refined to avoid synchronized fake versioning and to avoid treating a suite major version as universal breakage.

### `PROMOTE-0112` - `architecture_doc_candidate`

- Source conversation: `testx_repox_governance`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: FACT:** The user is building Dominium / Domino as a deterministic universe engine + game, not a conventional game project. The visible chat repeatedly framed the project as long-lived, simulation-first, deterministic, modular, and designed to survive across many operating systems, toolchains, renderers, products, and distribution models.

### `PROMOTE-0113` - `needs_user_decision`

- Source conversation: `testx_repox_governance`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user then asked whether the implementation was industry-accepted and what could be improved. The response framed the approach as closer to game engines, operating systems, and long-lived infrastructure than typical game development. The important conclusion was that the design was not exotic, but it was unusually rigorous for games.

### `PROMOTE-0114` - `architecture_doc_candidate`

- Source conversation: `testx_repox_governance`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: The user had another chat working on content and systems, and asked for a prompt to inform that chat of everything decided so far. A similar prompt was generated for the applications/platforms/renderers chat. These prompts established authoritative boundaries:

### `PROMOTE-0115` - `architecture_doc_candidate`

- Source conversation: `Timekeeping_and_2038_Resilience`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: A future assistant should understand that this chat contributes a time architecture doctrine for Dominium: **ACT is authority; DSYS time is runtime-only; observer clocks are derived; civil/astronomical time is projection-only; wall-clock time must never drive authoritative ordering.

### `PROMOTE-0116` - `insufficient_evidence`

- Source conversation: `Timekeeping_and_2038_Resilience`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: What remains uncertain is the precise target list of legacy machines/toolchains and how far compatibility must go, especially for 16-bit compilers with weak or absent 64-bit arithmetic.

### `PROMOTE-0117` - `reject_as_noise`

- Source conversation: `Timekeeping_and_2038_Resilience`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The final topic is this export task. The user requested a human-readable report first, followed by registers, spec prep, context-transfer packet, aggregator packet, self-audit, and files. This package is designed to let the chat be read later without reopening the full transcript and to support merger into a larger Dominium spec book.

### `PROMOTE-0118` - `reject_as_noise`

- Source conversation: `UE6_Domino_Deterministic_Universe`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: FACT: This package preserves the currently visible chat about whether Dominium should use UE6, UE5, Domino, Unreal, or a custom engine layer for a highly ambitious deterministic solar-system-scale game. It also preserves the current uploaded prompt as an artifact because it defines this preservation task.

### `PROMOTE-0119` - `insufficient_evidence`

- Source conversation: `UE6_Domino_Deterministic_Universe`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: That response also introduced a rule that shaped the rest of the chat: Unreal should render and host Dominium, but Unreal should not define Dominium. That was the first major conceptual decision point. It reframed Dominium not as an engine project in the narrow sense, but as a portable game/simulation system with replaceable frontends.

### `PROMOTE-0120` - `blocked_by_queue`

- Source conversation: `UE6_Domino_Deterministic_Universe`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: blocked queue scope
- Queue risk: `blocked`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Conclusion: machine gameplay must be designed as a scalable graph simulation, not as unrestricted physics.

### `PROMOTE-0121` - `needs_user_decision`

- Source conversation: `ui_editor_tool_editor_planning`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.

### `PROMOTE-0122` - `insufficient_evidence`

- Source conversation: `ui_editor_tool_editor_planning`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: This was one of the most important structure decisions in the chat. It prevented the initial implementation from becoming too broad while preserving the long-term goal. The UI Editor would be a bootstrap tool, not the final architecture.

### `PROMOTE-0123` - `needs_user_decision`

- Source conversation: `ui_editor_tool_editor_planning`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical layout description, and the user accepted it as useful. Future work should inspect the bundles before claiming exact screenshot fidelity.

### `PROMOTE-0124` - `archive_only`

- Source conversation: `Universe_Explorer_Planning`
- Proposed target path: `docs/archive/conversations/**`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The pasted discussion on trees, screws, pottery, axes, chairs, tables, and machines established that the player should manipulate material, geometry, constraints, processes, tools, stations, and affordances. The conclusion is that "item classes" must not be the truth substrate. Recipes and blueprints can exist, but as higher-order formalizations.

### `PROMOTE-0125` - `needs_user_decision`

- Source conversation: `Universe_Explorer_Planning`
- Proposed target path: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: A major theme was that useful local inventions must become portable, standardized, industrialized, and institutionally adopted. The repo now has a Formalization Chain spec and Player Desire Acceptance Map that strongly preserve this. The future work is making this playable: drafting, measuring, testing, blueprinting, certifying, teaching, manufacturing, maintaining, and revising designs.

### `PROMOTE-0126` - `contract_candidate`

- Source conversation: `Universe_Explorer_Planning`
- Proposed target path: `contracts/** or docs/reference/contracts/** after authority review`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: authority review plus targeted schema/contract parser and FAST
- Recommended next action: `hold_or_review`
- Claim: Workbench was treated as the likely first surface for the Universe Explorer, but only if it remains projection, not authority. The repo queue says `PRESENTATION-CONTRACT-01` is next, with `PROJECTION-CONFORMANCE-01` as alternate. The conclusion was that presentation/projection contracts must come before building UI or renderer features.

### `PROMOTE-0127` - `insufficient_evidence`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user noted that earlier prompts were hard to copy because they were not always contained in one code block, and that prompts should better handle dirty worktrees and concurrent tasks. From then on, generated prompts included detailed dirty worktree handling, allowed/forbidden paths, non-goals, validation, blocker classification, and commit/final-response formats.

### `PROMOTE-0128` - `insufficient_evidence`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The final recommended sequence was: finish replay proof and barebones client, run product spine review, then begin limited parallel dev. Larger parallel waves should wait until minimum AIDE workflow law exists.

### `PROMOTE-0129` - `reject_as_noise`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The user then requested this full preservation package so a new chat could continue without re-explaining everything. This final handoff is itself part of the preservation output.

### `PROMOTE-0130` - `insufficient_evidence`

- Source conversation: `World_Architecture`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: The future relevance of this chat is high. It should feed directly into the future project spec book and into a corrected implementation prompt. But it should not be treated as final implementation detail everywhere. Many high-level decisions are settled, but solver formulas, exact file encoding details, build system integration, actual repository layout, and some numerical representations still require verification.

### `PROMOTE-0131` - `architecture_doc_candidate`

- Source conversation: `World_Architecture`
- Proposed target path: `docs/architecture/** after target selection`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: source check, authority-order check, link check, generated output validator, FAST
- Recommended next action: `create_microtask`
- Claim: Before reading the rest of this report, remember this: this chat's central contribution is not one isolated feature. It is a whole design philosophy for Dominium's world engine. The game should be deterministic, fixed-point, sparse, modular, content-driven, and field-based. Chunks are not the world. Chunks are just how the world is cached, meshed, streamed, and saved.

### `PROMOTE-0132` - `insufficient_evidence`

- Source conversation: `World_Architecture`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: This comparison was not a final technical dependency, but it helped clarify the design goal: Dominium should not simply copy any one of these systems. It should combine their useful elements while avoiding their limits.

### `PROMOTE-0133` - `insufficient_evidence`

- Source conversation: `xstack_lab_galaxy`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: and XStack must serve development rather than development serving XStack.

### `PROMOTE-0134` - `reject_as_noise`

- Source conversation: `xstack_lab_galaxy`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: After the transcript appeared, the user asked for a maximum-fidelity Context Transfer Packet. The assistant produced one, with sections such as workstreams, decisions, tasks, constraints, open questions, risks, artifacts, and verification queue. Then the user asked to turn that into a downloadable report package. The assistant created Markdown/YAML files and a ZIP archive.

### `PROMOTE-0135` - `reject_as_noise`

- Source conversation: `xstack_lab_galaxy`
- Proposed target path: `none`
- Current authority support: not yet verified against target docs
- Current authority conflict: none detected by triage
- Queue risk: `none_detected`
- Validation required: preserve as archive evidence; no live target validation
- Recommended next action: `hold_or_review`
- Claim: Finally, the user asked not for another package, but for an in-chat reader version of the package. The assistant rendered a structured in-chat reader. The user then asked for this current response: a human-readable, intuitive narrative report.
