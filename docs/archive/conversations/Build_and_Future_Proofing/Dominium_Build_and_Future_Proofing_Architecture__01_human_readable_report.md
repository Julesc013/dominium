# COMPLETE CHAT PRESERVATION REPORT — Dominium Build and Future-Proofing Architecture

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium Build and Future-Proofing Architecture |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This visible chat only unless labelled PROJECT-CONTEXT or REPO-CONTEXT |
| Apparent access | Partial: visible current conversation, the uploaded prompt, and repo/tool results surfaced during this conversation were accessible; hidden or earlier full transcripts were not directly available. |
| Previously generated files available? | No earlier downloadable files from this chat were available before this preservation task. New files were created by this task. |
| Uploaded files or artifacts present? | Yes: `Pasted text.txt`, containing the maximum-fidelity preservation prompt. |
| Contains future plans? | Yes. It contains build-system, CMake preset, CI, AIDE/XStack, modularity, public-surface, replacement-protocol, schema, and structure plans. |
| Contains decisions? | Yes, with caveats. The chat contains firm user constraints and assistant recommendations; not every assistant recommendation was explicitly accepted by the user. |
| Contains pending tasks? | Yes. Several proposed task sequences remain pending. |
| Contains unresolved questions? | Yes. Most concern acceptance, sequencing, exact repo state, and which recommendations should become canon. |
| Staleness risk | Medium to High. Repo state, CMake/VS/toolchain facts, and CI state are time-sensitive. |
| Extraction confidence | 4/5 for the visible chat; 2–3/5 for any implied older-chat context. |
| Safe for later aggregation? | Yes, with caveats: preserve labels, do not merge assistant suggestions as decisions, and verify current repo/toolchain facts first. |
| Main limitations | The full old chat transcript was not available beyond visible context; repo facts were sampled via tool calls during the chat; some recommendations were not formally accepted by the user. |

Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.


## 1. One-Page Orientation

This chat centered on how to make Dominium durable as a serious long-term software project rather than a one-off game prototype. The user first provided a prior technical assessment about Dominium's Windows build floors, Visual Studio toolchains, XP/Win7/Win10 support, CMake presets, static CRT policy, and runtime testing requirements. That pasted material treated Dominium's canon as strict: engine in C89, game layer in C++98, deterministic fixed-point behavior, no hidden capability creep, separate artifacts per OS floor, no CRT mixing, and proof through RepoX/TestX-style governance.

The user's first active question then reframed the problem around build-system complexity. They were concerned that different machines would have different IDEs and compilers: one Windows 10 laptop might use VS2017, a desktop might carry VS2022/VS2026 plus XP toolchains, while old VMs or old hardware might host VS2010, VS2005, VC6, VC1.5, Xcode 9, CodeWarrior Pro 9, and other historical toolchains. The user asked for the best way to design CMake, CI, presets, distribution, sync, and AIDE/XStack support so Dominium could manage those varied machines and outputs without becoming chaotic.

The response treated that as a build orchestration problem, not merely a preset list. The key recommendation was that CMake should remain the canonical build executor, but `CMakePresets.json` should stop acting as a single giant catch-all for host machines, IDE names, toolchains, OS floors, renderers, distribution variants, and release status. The proposed approach was tuple-driven: declare build tuples in contracts, probe the local machine, generate local user presets, execute CMake/CTest, collect TestX/RepoX evidence, then generate distribution/package manifests. AIDE would not replace CMake; it would detect local capabilities, generate local presets, run tuple verification, and preserve evidence. XStack would remain an orchestration/governance layer, while RepoX/TestX would supply repository-policy and deterministic-runtime proof.

The second major user question widened the scope. The user said it was very important that the code be portable, modular, extensible, and reusable: not only for other games on the Domino engine, but potentially for completely different engine or game projects. They wanted the codebase to support complete replacement or rewrite of code, data, files, and directories during future refactors, and to be developed like a proper game engine or OS rather than a one-off indie repo.

The response reframed Dominium as a portable deterministic engine platform with one game mounted on top. It argued that the correct order is stable contracts first, replaceable implementations second, products third, and presentation last. It judged the current top-level structure as close to correct, especially after the repo's canonical spine and runtime naming cleanups, but said the missing layer was a mechanically enforced stability taxonomy. The proposed additions were a public surface registry, a replacement protocol, stronger private/internal boundary enforcement, dependency-edge contracts, ABI header conformance tests, schema compatibility harnesses, content-pack authority cleanup, and deeper game-rule/domain cleanup.

The preservation prompt uploaded at the end turned the whole visible chat into a documentation task. It requested a human-readable report, structured registers, a context transfer packet, spec sheet, aggregator packet, self-audit, and downloadable file package. This preservation report therefore captures the conversation's actual purpose: Dominium needs governance structures that let it scale across toolchains, platforms, games, engines, refactors, and future spec-book aggregation without turning recommendations into accidental canon.


## 2. The Story of the Conversation

### 2.1 The starting point: toolchains and compatibility floors

The chat began with the user pasting a prior technical assessment. That assessment evaluated a recommendation about Visual Studio 2022, older MSVC toolsets, XP support, SDK pinning, `_WIN32_WINNT`, static CRT linking, and per-floor build artifacts. The user context made clear that Dominium has strict existing canon: C89 engine, C++98 game layer, deterministic execution, fixed-point assumptions, RepoX/TestX governance, separate multi-floor artifacts, no CRT mixing, and no silent API creep.

The pasted material did not merely say "install VS2022." It warned that v141_xp is acceptable for MVP but not necessarily archival-perfect; that SDK pinning is mandatory; that XP support requires runtime testing, not just compilation; and that legacy toolchains such as VC7.1 or VC6 may later be needed for true archival support. It also included a repo-state assessment that the Dominium repo had improved structurally but was still not build/product/projection proven at that time.

### 2.2 The user's build-system problem

The user then stated the practical issue: Dominium would be worked on from multiple machines with different IDEs and toolchains. The user planned to replace VS2015 with VS2017 on one laptop, keep VS2022/VS2026 or XP toolchains on a desktop, and use VMs or older machines for VS2010, VS2005, VS6, VS1.5, Xcode 9, CodeWarrior Pro 9, and similar toolchains. The question was how to design the build system, CI, presets, sync, distribution, and automation so that all of this remained understandable and mechanically governed.

### 2.3 The build architecture answer

The assistant inspected the Dominium repo and docs through GitHub connector calls during the conversation. It found that the existing `CMakePresets.json` had the core smell the user was worried about: host/editor names, actual toolsets, target OS floors, renderer flags, release lanes, and local machine assumptions were mixed into one preset namespace. It also found existing docs for toolchain matrix, build matrix, verification paths, dist layout, component matrix, and CI.

The answer was that Dominium needs a build orchestration layer above CMake, not more manually curated presets. The proposed flow was: build contracts define canonical tuples; machine probes detect local capabilities; generated `CMakeUserPresets.json` exposes only what the local machine can actually build; CMake remains the build graph authority; CTest/TestX/RepoX validate; dist/package manifests preserve proof. AIDE should assist by probing, explaining, generating local presets, verifying tuples, and emitting evidence. XStack should orchestrate and enforce, not become a second build system.

### 2.4 The broader modularity question

The user then pushed beyond build mechanics. They asked what else they were missing about portability, modularity, extensibility, replacement, rewriteability, and reuse across future games and engines. They explicitly wanted Dominium to be developed like a proper OS or game-engine platform, not a one-off indie project.

The assistant checked newer repo state and current structural docs. It found that the repo had moved beyond the earlier POST-CONVERGE-09 state, including a canonical source spine collapse, pack payload moves into `content/packs`, and runtime second-level naming normalization. It cited current docs describing the final repository structure, component matrix, language strategy, code/data boundary, schema stability, and boundary enforcement.

The answer was that Dominium should be treated as a portable deterministic engine platform. The top-level structure was judged mostly right, but deeper work remained. The most important missing pieces were a public surface registry, a formal replacement protocol, stricter dependency-edge enforcement, ABI/public header conformance, schema compatibility tests, and a clearer distinction between frozen ABI, stable API, stable data contracts, and internal mutable implementation.

### 2.5 The preservation task

The final uploaded prompt requested a complete preservation package for this chat: a human-readable explanation, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, and files/ZIP package. This response completes that export task and creates downloadable files for later reading and aggregation.


## 3. Main Topics Discussed

### Topic 1 — Multi-floor build and toolchain strategy

This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed from compilation alone. Runtime testing on real or VM floors remains required.

### Topic 2 — CMake presets versus build contracts

The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.

### Topic 3 — AIDE, XStack, RepoX, and TestX roles

AIDE was positioned as a build intelligence and evidence layer. It should probe the machine, explain which tuples are available or blocked, generate local presets, run tuple verification, and record evidence. XStack should remain umbrella orchestration. RepoX should enforce repo/layout/policy truth. TestX should verify runtime/determinism/build proof. None of these should replace CMake as the native build graph authority.

### Topic 4 — Repository structure and source ownership

The chat examined whether Dominium's directory structure is good enough. The answer was that the top-level structure is now close to correct: `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`. The remaining issue is not top-level layout but second/third-level ownership clarity, public/private boundaries, and lifecycle/status words embedded in active source paths.

### Topic 5 — Portability, modularity, and reuse

The user wanted reusable code for different games on the Domino engine and possibly unrelated future engine/game projects. The answer was to freeze contracts rather than implementations. Stable ABI/API/data/protocol surfaces should be explicitly versioned and tested; implementations should be replaceable behind black-box conformance tests. This is the basis for future rewrites without breaking compatibility.

### Topic 6 — Naming policy

The chat emphasized that directory and function names should express stable ownership and responsibility, not temporary status. Names like `runtime/render/software` and `runtime/render/null` are preferable to `soft` or `stub`. Generic names like `helpers`, `utils`, `common`, `misc`, `old`, `new`, and `legacy` should be avoided in active source unless explicitly quarantined or versioned.

### Topic 7 — Schemas, protocols, and compatibility

The chat discussed schema stability, unknown-field preservation, frozen/evolving schemas, compatibility migrations, and the need to apply wire-format discipline to Dominium's saves, replays, package manifests, protocols, command IDs, registry IDs, and capability IDs. The recommendation was to add compatibility fixtures and reserved-ID checks, not rely only on documentation.

### Topic 8 — The preservation package itself

The uploaded prompt requested a complete chat preservation package with human report, registers, handoff packet, spec sheet, aggregator packet, audit, and downloadable files. This output creates that package and labels its limitations.


## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted to design a robust Dominium build system that could handle many machines, IDEs, compilers, OS floors, CMake presets, CI lanes, distribution outputs, and historical toolchains. The user also explicitly wanted Dominium's codebase to be portable, modular, extensible, reusable across future games and engines, and refactorable at the level of whole files and directories.

The final explicit goal was preservation: create a maximum-fidelity package for this chat so the user can understand it later, ask questions in this chat, merge it with other old-chat reports, and eventually build a master project spec book.

### 4.2 Inferred Goals

INFERENCE: The user is trying to prevent Dominium from accumulating accidental architecture. They want mechanical governance rather than relying on memory or assistant recommendations. They also want future assistants to stop repeating conceptual advice and instead preserve actionable structure, constraints, risks, and next tasks.

### 4.3 Goals That Changed Over Time

The conversation moved from a specific compatibility/toolchain question into a broader engineering governance question. It began with how to handle VS2017/VS2022/VS2026/legacy VMs and grew into how to structure the entire repo, public API, schema system, rewrite protocol, and project portability doctrine.

### 4.4 Goals Still Unresolved

The unresolved goals are implementation goals: deciding which recommendations become canon, adding public-surface/dependency/build contracts, validating the current live repo state, and applying the proposed cleanup tasks. The preservation package is complete, but the engineering work it describes remains pending.


## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | Treat C89 engine, C++98 game layer, deterministic execution, per-floor artifacts, no CRT mixing, and no silent API creep as locked canon for this discussion. | Established as user-provided constraint | It bounds all build and architecture recommendations. | High | FACT |
| DECISION-02 | Frame the build problem as orchestration/contracts, not just preset cleanup. | Assistant recommendation; not explicitly accepted | It prevents `CMakePresets.json` from becoming a machine-specific dumping ground. | High | INFERENCE/RECOMMENDATION |
| DECISION-03 | Keep CMake as native build authority; use AIDE/XStack around it, not instead of it. | Assistant recommendation; not explicitly accepted | It preserves industry-standard build semantics while adding governance. | High | RECOMMENDATION |
| DECISION-04 | Use tuple-driven build definitions: product + OS floor + arch + toolchain + SDK + CRT + config + renderer + package lane. | Assistant recommendation; not explicitly accepted | It makes artifacts and CI lanes explicit and auditable. | High | RECOMMENDATION |
| DECISION-05 | Treat Dominium as a portable deterministic engine platform with one game mounted on top. | Assistant recommendation; not explicitly accepted | It supports reuse across games/engines and prevents one-off project drift. | Medium-High | RECOMMENDATION |
| DECISION-06 | Keep current top-level structure broadly, but continue second/third-level cleanup and boundary enforcement. | Assistant conclusion; not explicitly accepted | It avoids disruptive top-level churn while addressing real modularity debt. | Medium | RECOMMENDATION |
| DECISION-07 | Add public-surface registry and replacement protocol. | Assistant recommendation; not explicitly accepted | It makes rewrites safe and mechanically checkable. | Medium-High | RECOMMENDATION |

The most important caution is that only DECISION-01 is clearly a user-stated constraint in this visible chat. The other items are strong recommendations produced in response to the user's requests for best practice; they should not be merged into canon unless the user later accepts them.


## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

- More hand-written CMake presets were deprioritised. The better path is generated local presets from declared build contracts.
- One universal binary or one universal preset was rejected because it violates per-floor artifacts, CRT isolation, SDK pinning, and explicit floor proof.
- AIDE replacing CMake was rejected. AIDE should orchestrate, probe, and preserve evidence; CMake remains build authority.
- Manual drag-and-drop repo moves were rejected in earlier context and preserved here as a general risk; moves must go through migration maps, validators, shims, and proof.
- Freezing implementation files/directories was rejected in favor of freezing contracts, public surfaces, protocols, schemas, IDs, and compatibility semantics.
- Generic active-source names such as `common`, `misc`, `helpers`, `old`, `new`, `legacy`, `stub`, and status-coded paths were deprioritised for canonical code.


## 7. Important Reasoning, Rationale, and Tradeoffs

The visible rationale was governed by one central tradeoff: Dominium needs long-term portability and compatibility, but the project is already complex enough that uncontrolled abstraction would make it worse. The answer was not to introduce a universal mega-framework. The answer was to separate authorities: CMake builds, contracts define support truth, machine probes describe local capability, AIDE helps with orchestration/evidence, XStack coordinates governance, RepoX enforces repository policy, TestX proves behavior, and distribution manifests preserve artifact identity.

The second major tradeoff was between freezing too much and freezing too little. Freezing implementations would block refactors; freezing nothing would destroy compatibility. The recommended compromise was to freeze public contracts and conformance tests while allowing implementations to be replaced behind them.

The third tradeoff concerned structure. The repo's top-level layout is now relatively coherent, so another large top-level reshuffle would create churn. The deeper issue is ownership and dependency clarity below that level. Therefore the recommendation was to keep the top-level spine and invest in public surface registries, dependency contracts, schema compatibility, and name cleanup.


## 8. Plans, Future Work, and Next Steps

Recommended next-action sequence:

1. **Confirm acceptance boundary.** Decide which recommendations in this chat should become Dominium canon and which remain advisory.
2. **Verify current repo state.** Confirm the actual current HEAD, build proof, smoke tests, and outstanding warnings before acting.
3. **Add a public surface registry.** Define which headers, commands, schemas, protocols, and manifests are frozen/stable/internal.
4. **Add dependency-edge enforcement.** Convert intended module direction into a machine-readable contract.
5. **Add tuple build contracts and generated local presets.** Move build truth out of ad hoc preset names.
6. **Add ABI/header conformance tests.** Public engine/runtime headers should compile under declared floors.
7. **Add schema/protocol compatibility fixtures.** Old fixtures should load; unknown fields should round-trip; reserved IDs should be checked.
8. **Continue game/content cleanup.** Resolve `game/rule` versus `game/rules`, content pack taxonomy, and stale pack authority references.
9. **Document the replacement protocol.** Make whole-module rewrites safe through black-box conformance and replay/hash comparison.
10. **Feed this report into the master spec book aggregator.** Preserve uncertainty labels and avoid merging suggestions as decisions.

The strongest blocker is acceptance and verification: the user needs to decide what becomes binding, and the live repo state should be checked again before implementation.


## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

- Engine is C89; game is C++98.
- Determinism, fixed-point behavior, and no hidden behavior are central constraints.
- Multi-floor builds must be separate artifacts.
- No CRT mixing.
- No silent API creep.
- RepoX/TestX governance matters.
- Human-readable explanations are preferred over machine-only handoffs.
- The preservation output must distinguish FACT, INFERENCE, UNCERTAIN/UNVERIFIED, and PROJECT-CONTEXT.

### 9.2 Inferred Constraints and Preferences

- The user values auditability over speed.
- The user dislikes vague architecture advice without next actions.
- The user wants future assistants to preserve tentative status and not over-canonize recommendations.
- The user wants project structure that can survive major rewrites.

### 9.3 Uncertain or Unestablished Preferences

- Whether all recommended structural tasks should be implemented now is not established.
- Whether the proposed build tuple naming scheme should become official is not yet established.
- Whether the current top-level structure is final-final or merely best current target remains subject to user decision and repo evidence.


## 10. Files, Artifacts, Outputs, and Prompts

| ID | Artifact | Type | Purpose | Preserve? |
|---|---|---|---|---|
| ARTIFACT-01 | Initial pasted GPT-5.2/GPT-5.5 build/toolchain and repo-state analysis | In-chat pasted context | Set the build/governance problem frame | Yes |
| ARTIFACT-02 | Assistant build-system answer | In-chat report | Proposed tuple-driven build architecture | Yes |
| ARTIFACT-03 | Assistant modularity/future-proofing answer | In-chat report | Proposed public-surface/replacement/structure doctrine | Yes |
| ARTIFACT-04 | `Pasted text.txt` | Uploaded prompt | Requested this preservation package | Yes |
| ARTIFACT-05 | GitHub connector snapshots of Dominium docs | Repo context surfaced in chat | Supported claims about structure, matrix, language, schema, and boundary docs | Yes, but verify freshness |
| ARTIFACT-06 | This generated handoff package | Downloadable files/ZIP | Preservation, aggregation, and future-chat continuation | Yes |

No pre-existing downloadable files from this chat were available before this task. The downloadable files listed in the final section were created by the preservation task.


## 11. Open Questions and Unresolved Issues

1. Which assistant recommendations from this chat should become binding Dominium canon?
2. What is the exact current live repo HEAD and validation state after the latest commits?
3. Should the public surface registry be implemented before or after build tuple contracts?
4. What exact support floors are intended for MVP versus archival/research lanes?
5. Which schemas/protocols are truly frozen, and which are still evolving?
6. Which code surfaces must be reusable for non-Dominium future engine projects?
7. How should future master spec aggregation reconcile overlap with earlier Dominium chats?
8. What should be the immediate next implementation prompt after this preservation task?


## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

- A future assistant may treat recommendations as final decisions. Mitigation: preserve labels and require explicit user acceptance.
- A future assistant may rely on stale repo state. Mitigation: verify live HEAD, docs, and CI before implementation.
- A future assistant may over-focus on folder names and miss contract/interface stability. Mitigation: start with public surface registry and dependency contracts.
- A future assistant may generate more abstract doctrine instead of actionable tasks. Mitigation: use the task register.
- A future assistant may merge this with other chats without preserving conflicts. Mitigation: use the aggregator packet and conflict warnings.
- A future assistant may confuse CMake/AIDE/XStack roles. Mitigation: CMake builds; AIDE orchestrates/probes; XStack coordinates; RepoX/TestX enforce/prove.


## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat contributes two major chapters to a future Dominium project spec book:

1. **Build, Toolchain, CI, and Distribution Governance.** It defines the need for tuple-driven builds, machine probes, generated local presets, toolchain/floor evidence, and per-artifact manifests.
2. **Portability, Modularity, and Replacement Architecture.** It defines the need for public-surface registries, stable ABI/API/schema/protocol contracts, no reachable internals, dependency-edge enforcement, and rewrite-by-conformance.

It should not be merged as a list of final decisions. Much of it is recommendation-level material. The spec-book aggregator should convert user-stated constraints into requirements, assistant recommendations into candidate requirements, and repo facts into verified references only after current repo validation.


## 14. What I Should Remember

- The chat's central thesis is that Dominium needs contract-governed portability, not more ad hoc presets or folders.
- The build-system answer was tuple-driven: contracts define what can be built; machines are probed; local presets are generated; CMake builds; TestX/RepoX prove; dist manifests preserve evidence.
- The modularity answer was contract-driven: freeze ABI/API/schema/protocol/public surfaces, not implementation files.
- The current top-level structure appears close to correct, but second/third-level names and boundaries still need cleanup.
- A public surface registry and replacement protocol are the most important missing architecture mechanisms.
- The user constraints around C89/C++98, determinism, no CRT mixing, per-floor artifacts, and no silent API creep must not be diluted.
- Do not merge assistant recommendations into canon without user acceptance.


## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- What are the three most important architecture ideas from this chat?
- Which parts of this chat are FACT versus assistant recommendation?

### 15.2 Decisions
- Which recommendations should I explicitly accept as Dominium canon?
- Which decisions are still only tentative?

### 15.3 Tasks and Next Actions
- Write the next implementation prompt for `STRUCTURE-01: Public Surface Registry`.
- Write the next implementation prompt for tuple-driven build contracts and generated local presets.

### 15.4 Artifacts and Files
- Explain the generated ZIP package and which file I should use for aggregation.
- Turn the context transfer packet into a shorter bootstrap prompt.

### 15.5 Risks and Verification
- What live repo facts should I verify before implementing these tasks?
- What is the risk of doing build tuple work before public surface registry work?

### 15.6 Future Spec Book / Aggregation
- Convert this chat into spec-book chapter headings.
- Extract only formal requirement candidates from this chat.

### 15.7 Deep-Dive Questions Specific to This Chat
- Design the `contracts/public_surface` schema.
- Design the `contracts/build` tuple schema.
- Design a replacement protocol for rewriting a runtime backend without breaking compatibility.


## 16. Compact Human Summary

This chat was about making Dominium structurally durable. It began with a pasted analysis of Windows toolchains and compatibility floors, including VS2022 as a possible host for older MSVC toolsets, v141/v141_xp for practical XP-era builds, stricter historical toolchains for archival lanes, SDK pinning, static CRT requirements, and runtime testing across OS floors. That material framed Dominium as a project with strict canon: C89 engine, C++98 game, deterministic fixed-point execution, per-floor artifacts, no CRT mixing, no hidden behavior, and RepoX/TestX governance.

The user's first active question asked how to handle many different development machines and toolchains without making CMake presets and CI unmanageable. The answer was that Dominium needs build orchestration above CMake, not a larger hand-maintained preset file. CMake should remain the build executor, but build truth should live in declared tuples: product, OS floor, architecture, toolchain, SDK, CRT, build config, renderer, and package lane. A machine probe should detect what a given laptop, desktop, VM, or CI runner can actually build, then generate local `CMakeUserPresets.json` entries. AIDE should help probe, explain, generate, verify, and record evidence. XStack should orchestrate. RepoX and TestX should enforce and prove. Distribution outputs should carry manifests that identify exactly what was built and under what contract.

The user's second question broadened the concern from build mechanics to the whole codebase. They wanted code that could be reused for other games on the Domino engine, or even different engine/game projects, and they wanted complete future rewrites of files/directories to be possible without destroying compatibility. The answer was that Dominium should be treated as a portable deterministic engine platform with one game mounted on it. The correct order is stable contracts first, replaceable implementations second, products third, presentation last.

The repo's top-level structure was judged close to correct: `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`. The remaining problem is deeper: public/private boundaries, dependency direction, schema compatibility, naming, and replacement protocols. The most important proposed additions were a public surface registry, a dependency-edge contract, ABI header conformance tests, schema compatibility fixtures, a replacement protocol, and further game/content cleanup.

The final uploaded prompt asked for this preservation package. The key thing to preserve is that most architecture proposals are recommendations, not accepted user decisions yet. The next best action is to decide which recommendations become canon, then implement either `STRUCTURE-01: Public Surface Registry` or the build tuple contract work, after verifying the current live repo state.
