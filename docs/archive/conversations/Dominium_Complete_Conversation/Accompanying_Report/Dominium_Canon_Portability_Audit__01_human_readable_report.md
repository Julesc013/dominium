# COMPLETE CHAT PRESERVATION REPORT — Dominium Canon, Repository Alignment, and Portability Doctrine

## 0. Coverage and Reliability Assessment

| Field | Assessment |
| --- | --- |
| Chat label | Dominium Canon, Repository Alignment, and Portability Doctrine |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial: current visible conversation plus uploaded preservation prompt; not guaranteed full hidden historical transcript |
| Previously generated files available? | No earlier generated downloads in this chat; this response creates files |
| Uploaded files or artifacts present? | Yes: `Pasted text.txt` preservation prompt |
| Contains future plans? | Yes |
| Contains decisions? | Yes, but some are assistant recommendations and must remain labelled |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium: live repo state and external examples can change |
| Extraction confidence | 4/5 for visible chat; 2/5 for any unavailable prior context |
| Safe for later aggregation? | With caveats |
| Main limitations | No full local checkout/test run; current repo inspection was partial; some project context comes from system memory and must be labelled PROJECT-CONTEXT |

Plain-language limitation summary: I can preserve the visible current conversation, the uploaded `Pasted text.txt` prompt, and the repository evidence already inspected through the GitHub connector in this session. I cannot guarantee access to every older hidden transcript, expired upload, or external file from other chats. Where this report uses project-level memory about Dominium’s broader architecture, it is labelled PROJECT-CONTEXT or treated as background rather than direct proof.

## 1. One-Page Orientation

This chat was about preserving and re-grounding Dominium’s architecture around a very old constitutional contract, then checking whether the current GitHub repository still follows that contract, and finally broadening the question into a platform-engineering doctrine for portability, modularity, extensibility, reuse, future-proofing, and long-term compatibility.

The chat began with the user pasting the old “DOMINIUM CONSTITUTIONAL ARCHITECTURE & EXECUTION CONTRACT v1” and the old “CANONICAL GLOSSARY v1”. Those documents defined Dominium as a deterministic universe simulation platform built around Domino as a C89 deterministic engine, Dominium as a C++98 game layer, product applications such as Client/Server/Setup/Launcher, and XStack as a governance layer. The v1 ontology reduced all systems to Assemblies, Fields, Processes, Agents, and Law. It also insisted on fixed-point authoritative math, named RNG streams, thread-count invariance, replay hash equivalence, explicit AuthorityContext, LawProfile-driven behavior rather than runtime mode flags, and TruthModel → PerceivedModel → RenderModel separation. The glossary locked the vocabulary around terms such as Authority, LawProfile, Lens, Process, SessionSpec, UniverseIdentity, UniverseState, Macro Capsule, SRZ, XStack, RepoX, TestX, AuditX, CompatX, SecureX, and related concepts.

The user then asked how the current GitHub repository `julesc013/dominium` aligned with that old v1 contract and glossary, asking specifically: what do the docs say, and what does the code do? The assistant inspected the live repository through the GitHub connector. The main finding was that the old v1 contract and glossary had not been discarded; they had been materialized into repo canon under `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`. The repo also had a newer canon-index regime saying prompts themselves are not authoritative unless materialized as canonical documents. This mattered because it changed the authority model: the old pasted prompt is historically important, but the repo version of the contract is the operational source of truth. The audit found strong alignment in documents, schemas, registries, governance, deterministic build constraints, and client session-pipeline code, but only partial implementation of the full runtime gameplay model. Survival fields and processes exist as registries; full agent gameplay loops, MMO/SRZ distributed runtime, embodiment, and other advanced systems were still described as deferred or future work.

The user then reframed the issue around engineering quality: they wanted the code to be portable, modular, extensible, reusable for other games on the same Domino engine, reusable for different engine or game projects, and replaceable down to files and directories if a rewrite/refactor is needed. They explicitly said the project should be developed like a proper game or OS, not a one-off indie project. The assistant’s answer converted that into a doctrine: stable contracts, replaceable implementations, deterministic behavior, portable projections, and no accidental authority from paths, tools, UIs, or prompts. The answer emphasized that the goal is not to freeze every file, but to make every boundary explicit, versioned, testable, and replaceable. It identified the ownership-based source layout as broadly right: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`. It also identified remaining cleanup debt and recommended finishing ownership-contract convergence rather than starting a grand rewrite.

The unique value of this chat is that it bridges three layers: old constitutional intent, current repository reality, and future engineering doctrine. It is not merely a summary of Dominium’s game design. It is a portability and governance checkpoint: what is canon, what is implemented, what remains declarative, what structure should remain, what structure still needs cleanup, and what practices should govern future coding.

## 2. The Story of the Conversation

The conversation opened with a deliberate reconstitution of canon. The user supplied an old self-contained constitutional architecture prompt for Dominium and Domino. The assistant acknowledged it as authoritative within the conversation. The user then supplied a canonical glossary v1.0.0, and the assistant acknowledged that the glossary constrained future terms.

The next substantive turn asked for an alignment audit against the live GitHub repository. This changed the task from “accept the old constitution” to “measure the current repo against it.” The assistant used the GitHub connector to inspect `Julesc013/dominium`, including `README.md`, `docs/STATUS_NOW.md`, `docs/architecture/ARCH0_CONSTITUTION.md`, `docs/architecture/CANON_INDEX.md`, `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/ARCHITECTURE.md`, `docs/XSTACK.md`, `CMakeLists.txt`, client session-pipeline code, RNG code, world/sim code, survival registries, experience profiles, law profiles, and schemas for SessionSpec and AuthorityContext. The resulting assessment was nuanced: the repo strongly preserved the v1 constitution and glossary at the documentation and contract layer, but the implementation was not yet a full realization of the old vision. The repo had deterministic scaffolding, schema/registry discipline, C90/C++98 build constraints, XStack-style governance, and a real deterministic session pipeline. However, advanced gameplay and distributed-scale claims were mostly still future-facing.

The final major turn shifted from “does it align?” to “what practices should we follow to make it robust for decades?” The user asked for broad and deep guidance on portability, modularity, extensibility, structure, file names, function names, schemas, protocols, APIs, big-company practices, future-proofing, backward compatibility, and prior related discussions. The assistant inspected newer repo layout/naming documents including `ARCH_REPO_LAYOUT.md`, `REPO_LAYOUT_TARGET.md`, `contracts/repo/layout.contract.toml`, `contracts/repo/naming.contract.toml`, `OWNERSHIP_RULES.md`, `no_src_source_policy.md`, `file_naming.md`, `module_layout.md`, `language_ownership.md`, and `POST_CONVERGE_NEXT_STEPS.md`. The answer concluded that the current ownership-root model is directionally right, while cleanup remains unfinished. It recommended stabilizing contracts rather than implementations, using explicit module descriptors, stable C89 ABI boundaries, versioned schemas and protocols, command/refusal spines, generated-artifact reproducibility, a second “minimal game on Domino” reuse proof, and strict separation of engine/game/runtime/apps/contracts/content/tools.

This preservation task was then uploaded as `Pasted text.txt`. It requested a maximum-fidelity report package for the current chat, with human-readable explanation first, structured registers, context-transfer packet, spec sheet, aggregator packet, self-audit, and downloadable files.

## 3. Main Topics Discussed

### Topic 1 — Old v1 Constitutional Architecture

The old v1 contract established the original architecture language: Domino as deterministic C89 engine, Dominium as C++98 game layer, applications as product surfaces, and XStack as governance. It came up because the user needed old custom instructions restored or preserved. The most important conclusion was not merely “this old prompt exists,” but that its concepts remain central: determinism, Process-only mutation, LawProfile and AuthorityContext, no omniscience, no mode flags, data-defined domains, and explicit governance.

Uncertainty: the raw pasted prompt is not the current repo authority unless materialized in repo canon. The later audit found that it had in fact been materialized under `docs/canon/constitution_v1.md`.

### Topic 2 — Canonical Glossary and Terminology Control

The glossary bound terms such as Authority, Law, Process, Lens, SessionSpec, UniverseIdentity, Macro Capsule, SRZ, RepoX, TestX, AuditX, CompatX, SecureX, and related terms. It matters because future assistants must not use sloppy synonyms like “mode” where the canon requires ExperienceProfile or LawProfile. This topic directly supports modularity because stable vocabulary is part of stable architecture.

### Topic 3 — Current Repository Alignment

The user asked what the current GitHub repo says and what the code does. The audit found strong documentation/contract alignment, meaningful deterministic code scaffolding, and partial runtime implementation. Key repo docs said v1 canon and glossary are current canonical docs; the README and status pages are derived/provisional; and the repo contains a large canon index. Code inspection found C90/C++98 build settings, deterministic RNG stream support, tile-world save/load/checksum code, a deterministic client session pipeline, and registry-defined survival slice data.

The critical conclusion was: **the repo has strong architecture scaffolding, but the full game/platform vision is not yet implemented.**

### Topic 4 — Portability, Modularity, and Extensibility Doctrine

The user then asked what practices would make the code reusable for other games and even other engine projects. The assistant answered that the correct goal is not to make all files permanent, but to make boundaries explicit and stable. The doctrine became: stable contracts, replaceable implementations, deterministic behavior, portable projections, and no accidental authority from paths/tools/UIs/prompts.

### Topic 5 — Repository Layout and Naming

The chat inspected repo layout/naming documents and concluded that the active ownership-root structure is broadly right: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`. Generic roots like `src/`, `source/`, `common/`, `shared`, and `misc` were rejected because they hide ownership.

Uncertainty: during this preservation pass, a potential inconsistency appeared: some docs claim product roots moved under `apps/`, while an earlier inspected code path under root `client/` was available and `apps/client` was not fetched successfully. This must be verified against the current physical tree.

### Topic 6 — API, ABI, Schema, and Protocol Practices

The assistant recommended stable public C-compatible APIs for Domino, opaque handles, explicit struct sizes, no platform types in engine headers, explicit allocator/lifetime ownership, deterministic error/refusal codes, and no C++ ABI exposure across long-term stable boundaries. It also recommended versioned schemas, registries, manifests, save/replay formats, compatibility matrices, and migration/refusal rules.

### Topic 7 — Preservation and Aggregation

The uploaded prompt requested this full preservation package. It requires a human-readable report, registers, context transfer packet, spec sheet, aggregator packet, self-audit, exported files, and an in-chat reader.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The explicit goals were to restore/preserve old Dominium canon, assess current repository alignment, understand what the docs and code actually say/do, and identify practices to make the code portable, modular, extensible, replaceable, future-proof, and backward compatible.

### 4.2 Inferred Goals

The inferred goal is to prevent Dominium from becoming a one-off fragile indie codebase. The user wants a durable platform architecture closer to a game engine/product family or OS-style codebase, where pieces can be replaced without breaking identity, compatibility, or determinism.

### 4.3 Goals That Changed Over Time

The chat moved from accepting old canon, to auditing live repo reality, to producing broad engineering doctrine, to preserving the whole exchange for later aggregation.

### 4.4 Goals Still Unresolved

Unresolved goals include verifying the latest physical repo tree, proving runtime implementation maturity, formalizing public ABI/API boundaries, completing layout/naming cleanup, and building a second Domino-based product to prove reuse.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
| --- | --- | --- | --- | --- | --- |
| DECISION-01 | Treat old v1 Constitution and Glossary as the comparison baseline for this chat. | Accepted in-chat; repo authority later refined. | Provides baseline for audit but must not override repo-materialized canon in live repo. | 4 | FACT |
| DECISION-02 | Prefer repo-materialized canonical documents over raw prompts for current repository authority. | Established by audit; not directly stated by user, but supported by repo docs. | Future work should cite `docs/canon/*` and canon index, not raw chat memory alone. | 4 | FACT/INFERENCE |
| DECISION-03 | Use ownership-based source roots instead of generic `src/`/`source/` layout. | Recommended and supported by current repo naming/layout docs. | Preserve `apps/ engine/ game/ runtime/ contracts/ content/ ...` model. | 4 | FACT/INFERENCE |
| DECISION-04 | Do not freeze all code; freeze contracts and make implementations replaceable. | Assistant recommendation; user intent strongly supports it. | Directs future architecture toward ABI/schema/protocol boundaries. | 4 | INFERENCE |
| DECISION-05 | Treat survival/runtime gameplay as not fully implemented yet despite strong declarative scaffold. | Audit conclusion, not a user decision. | Avoid overstating implementation maturity. | 4 | INFERENCE |
| DECISION-06 | Create this preservation package with human-readable report plus structured exports. | Triggered by uploaded preservation prompt. | This answer creates the artifact set. | 5 | FACT |

### Decision explanations

- **DECISION-01:** The old v1 contract/glossary were accepted as the baseline for this chat because the user supplied them as the old ground truth and asked later questions against them.
- **DECISION-02:** The live repo audit refined authority: the repo-materialized canon files and canon index are stronger for current repository work than raw prompts.
- **DECISION-03:** Ownership-root layout was preferred because it encodes who owns a file or subsystem, while generic `src`/`source` hides responsibility.
- **DECISION-04:** Stable contracts plus replaceable implementations best satisfy the user’s desire for rewrites/refactors without losing compatibility.
- **DECISION-05:** The repo should not be described as fully implementing the old v1 vision yet; many systems are still declarative, scaffolded, or deferred.
- **DECISION-06:** The uploaded preservation prompt directly requested a package, so this response creates one.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Treat raw chat prompts as stronger than repo-materialized canon. | Superseded | Repo canon index says prompts are execution artifacts unless materialized. | Final for current repo authority unless canon changes. | Only reconsider if repo authority order changes. | WORKSTREAM-01 | FACT |
| REJECTED-02 | Use generic `src/` or `source/` root as the active layout. | Rejected/superseded | Current naming/no-src policy says ownership roots are active model. | Final for new active source work. | Only reconsider by explicit repo contract amendment. | WORKSTREAM-04 | FACT |
| REJECTED-03 | Treat docs and registries as proof that full gameplay is implemented. | Rejected as unsafe | Audit separated docs/schema from code behavior. | Final as epistemic discipline. | Reconsider after runtime tests prove behavior. | WORKSTREAM-02 | INFERENCE |
| REJECTED-04 | Perform a grand rewrite/refactor without gated ownership migration. | Deprioritised | Would risk breaking identity, imports, ABI, and compatibility. | Tentative; controlled rewrites remain allowed. | Only after contracts/tests/migration plan exist. | WORKSTREAM-04 | INFERENCE |

## 7. Important Reasoning, Rationale, and Tradeoffs

The main tradeoff is between stability and replaceability. The user wants code and directories to be fully replaceable, but also wants long-term compatibility. The resolution is to stabilize contracts, identifiers, schemas, save/replay formats, command/refusal protocols, and tests while allowing implementations and storage paths to move behind those boundaries.

Another tradeoff is between a clean theoretical structure and the current repo’s transitional debt. The current ownership-root target is good, but the repo still has cleanup work. The safe path is not broad movement by directory name; it is gated move/refactor batches with identity preservation, shims where needed, strict validators, and proof outputs.

A third tradeoff is between docs ambition and runtime proof. The docs are far ahead, which is acceptable for planning, but dangerous if treated as implementation fact. Future work must always separate “declared contract,” “schema/registry exists,” “code exists,” “tests pass,” and “product behavior proven.”

## 8. Plans, Future Work, and Next Steps

Recommended next-action sequence:

1. Verify the current physical repo tree against layout docs and `contracts/repo/layout.contract.toml`.
2. Run or inspect strict layout/root validators and active exception ledger.
3. Build a public API/ABI inventory for Domino, Dominium, runtime services, tools, and data contracts.
4. Audit survival/runtime Process execution to separate registry declarations from implemented behavior.
5. Create a compatibility policy map for schemas, saves, replays, packs, command packets, and ABI.
6. Add a second minimal Domino product/game as a reuse proof.
7. Continue move/refactor cleanup in small gated batches only.
8. Merge this chat into the master Project Spec Book using the aggregator packet, not by copying every assistant recommendation as a requirement.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Determinism remains primary: fixed-point authoritative math, named RNG, replay/hash equivalence, thread-count invariance. | Technical/canon | Hard | Old v1 contract and live repo constitution | Do not introduce nondeterministic authoritative behavior. | High | 5 | FACT |
| CONSTRAINT-02 | Process-only mutation and law-gated authority. | Technical/canon | Hard | v1 and live constitution | All authoritative state changes must route through processes and AuthorityContext/LawProfile. | High | 5 | FACT |
| CONSTRAINT-03 | No runtime mode flags; behavior derives from ExperienceProfile/LawProfile/ParameterBundle. | Technical/canon | Hard | v1 and live constitution | Avoid `*_mode` gameplay branches and mode-specific logic forks. | Medium | 5 | FACT |
| CONSTRAINT-04 | TruthModel → PerceivedModel → RenderModel separation. | Architecture | Hard | v1 and repo docs | Renderer/runtime must not access or mutate truth directly. | High | 5 | FACT |
| CONSTRAINT-05 | Ownership-root layout; no new generic `src`/`source`/`common`/`shared`/`misc` buckets. | Repository structure | Hard for new work | Naming/layout contracts | New files must be placed by ownership and role. | Medium | 4 | FACT |
| CONSTRAINT-06 | Source repo layout is not install/package/runtime projection layout. | Repository/distribution | Hard | Layout docs and no-src policy | Do not infer runtime store/save/export roots from source roots. | Medium | 4 | FACT |
| CONSTRAINT-07 | Content/packs must not contain untrusted executable authority. | Security/architecture | Hard | Pack-driven integration doctrine | Future extension code needs separate trust/capability contract. | High | 4 | INFERENCE |
| CONSTRAINT-08 | Human-readable explanation must come before machine-readable handoff in preservation tasks. | Communication | Hard for this task | Uploaded preservation prompt | This output must be understandable without downloading files. | Medium | 5 | FACT |

### 9.2 Inferred Constraints and Preferences

The user likely wants future assistants to challenge weak framing, preserve uncertainty, avoid shallow “best practice” lists, and focus on decisions that survive future rewrites.

### 9.3 Uncertain or Unestablished Preferences

It is not established whether the user wants to prioritize repo cleanup, API formalization, or second-product reuse proof first. That should be resolved by a future task selection.

## 10. Files, Artifacts, Outputs, and Prompts

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | DOMINIUM CONSTITUTIONAL ARCHITECTURE & EXECUTION CONTRACT v1 | Pasted prompt/doc | Baseline architecture contract for chat comparison. | Used in chat; repo has canonical materialized version. | User pasted in current chat | Yes | Treat raw prompt as baseline but repo canon as current authority. | FACT |
| ARTIFACT-02 | DOMINIUM CANONICAL GLOSSARY v1.0.0 | Pasted prompt/doc | Vocabulary authority for current chat. | Used in chat; repo has canonical materialized version. | User pasted in current chat | Yes | Preserve definitions and deprecated/reserved words. | FACT |
| ARTIFACT-03 | Repository alignment audit answer | Chat output | Compared live repo docs/code to old v1. | Produced in chat, not a file until this package. | Assistant | Yes | Key finding: strong docs/schema alignment, partial implementation. | FACT |
| ARTIFACT-04 | Portability/modularity/future-proofing doctrine answer | Chat output | Broad guidance on coding practices and repo structure. | Produced in chat, not a file until this package. | Assistant | Yes | Contains recommendations; not all are user decisions. | FACT |
| ARTIFACT-05 | Uploaded `Pasted text.txt` | Uploaded text file | Mega prompt instructing this preservation/export task. | Current attachment read successfully. | User upload | Yes | This task’s direct instruction source. | FACT |
| ARTIFACT-06 | GitHub connector source observations | Connector output | Evidence from repo files used for audit. | Available in current chat through citations; not a local repo checkout. | Assistant/tool | Yes | Partial because not full tree/local test run. | FACT |

## 11. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Which repo layout state is current where docs claim product roots moved but earlier fetched code still appeared under root `client/`? | This affects source-layout truth and cleanup planning. | Docs say `apps/` is canonical; earlier code fetch succeeded under `client/`; `apps/client` fetch failed in this session. | Whether the connector saw stale docs, old paths, branch drift, or unresolved repo inconsistency. | Run full tree listing/local checkout validation. | P0 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-02 | How much of the survival vertical slice is implemented as runtime Process execution rather than registries? | Determines implementation maturity. | Fields/process IDs/law profiles exist in registries. | Concrete process executor/handlers/tests status. | Inspect game/runtime process code and tests. | P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-03 | What are the exact public API/ABI boundaries for Domino vs Dominium vs runtime? | Needed for reuse and backward compatibility. | General doctrine and some headers exist. | Formal ABI stability map and public/private header inventory. | Create/API audit and contract map. | P1 | WORKSTREAM-05 | INFERENCE |
| QUESTION-04 | What remaining bad roots/exceptions exist today? | Necessary before feature expansion/refactors. | Docs mention exceptions and cleanup waves. | Current exact count/status at HEAD. | Run strict layout validators and read exception ledger. | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-05 | What should become formal requirements in the master Project Spec Book vs background context? | Prevents over-formalizing suggestions. | This chat contains both accepted canon and assistant recommendations. | User acceptance of specific practices beyond high-level preference. | Aggregator review with labels preserved. | P1 | WORKSTREAM-08 | INFERENCE |
| QUESTION-06 | Should a second minimal Domino product be built now or after layout cleanup? | Determines next practical proof. | Assistant recommended it as reuse proof. | User/project priority and current build readiness. | Decision by project owner after current blockers reviewed. | P2 | WORKSTREAM-07 | UNCERTAIN |

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Treating repo docs as fully implemented behavior. | Overstates maturity and causes bad planning. | Medium | High | Separate docs/schema/code/test status. | WORKSTREAM-02 | FACT/INFERENCE |
| RISK-02 | Treating assistant recommendations as accepted decisions. | Spec book may formalize unapproved practices. | Medium | High | Use decision status and labels. | WORKSTREAM-08 | FACT |
| RISK-03 | Breaking semantic IDs during path cleanup. | Saves/packs/contracts/replays may become incompatible. | Medium | High | Path moves must preserve IDs unless explicit migration. | WORKSTREAM-04 | INFERENCE |
| RISK-04 | Creating new generic buckets during refactor. | Ownership ambiguity returns. | Medium | Medium | Use layout/naming contracts and validators. | WORKSTREAM-04 | FACT/INFERENCE |
| RISK-05 | Hidden coupling prevents Domino reuse by other games. | Engine becomes Dominium-specific. | Medium | High | Add second minimal product reuse proof. | WORKSTREAM-07 | INFERENCE |
| RISK-06 | Runtime/platform/UI layers gain truth authority. | Violates canon and harms multiplayer fairness/determinism. | Medium | High | Enforce Truth/Perceived/Render and command/refusal spine. | WORKSTREAM-03 | FACT/INFERENCE |
| RISK-07 | Current preservation is incomplete because full historical transcript is unavailable. | Future aggregation may miss context outside visible chat. | Medium | Medium | State coverage limitation and use PROJECT-CONTEXT labels. | WORKSTREAM-08 | FACT |

Main prevention rule: do not compress this chat into “repo mostly aligns with canon.” The more precise takeaway is: **canon/docs/schemas/gates are strong, runtime implementation is partial, layout direction is good, cleanup remains, and future-proofing requires stable contracts plus replaceable implementations.**

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Architecture Constitution | Use v1 Constitution/Glossary and live repo canon hierarchy as foundational source hierarchy. | DECISION-01, DECISION-02 | Requirement/context | 4 | Preserve repo-materialized canon as stronger than raw prompts. |
| Repository Layout and Ownership | Ownership-root layout and no-src/source policy. | DECISION-03, CONSTRAINT-05 | Requirement | 4 | Verify current tree/exception status before finalizing. |
| Portability and API Doctrine | Stable contracts, replaceable implementations, C ABI, schema/protocol versioning. | DECISION-04, TASK-02, TASK-03 | Requirement candidate | 3 | Some parts are assistant recommendations, not explicit user decisions. |
| Implementation Status | Docs/schema strong; runtime gameplay partial; advanced systems deferred. | DECISION-05, QUESTION-02 | Open issue/context | 4 | Avoid overstating current implementation. |
| Governance and Verification | Use XStack/RepoX/TestX/AuditX and strict validators as gates. | CONSTRAINTS, TASK-06 | Requirement/context | 4 | Latest status must be verified. |
| Reuse Proof | Add second minimal game/product on Domino. | TASK-04 | Open issue/requirement candidate | 3 | Needs user/project prioritization. |

## 14. What I Should Remember

- The old v1 contract and glossary remain central, but current repo authority is materialized canon, not raw prompts.
- The current repo has strong deterministic/governance/schema scaffolding.
- The current repo should not be overstated as a complete runtime implementation of all v1 goals.
- The ownership-root layout is broadly right and better than a generic `src/` tree.
- The project should stabilize contracts and IDs, not file paths or implementation details.
- Portability depends on C-compatible public boundaries, no platform leakage into engine truth, data-driven domains, versioned schemas, and stable save/replay formats.
- The safest next technical move is a current repo layout/API/implementation audit, not a broad rewrite.
- This chat should feed the master spec book’s architecture, repository layout, API doctrine, governance, and implementation-status sections.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- “Give me the shortest accurate version of the repo alignment audit.”
- “What did this chat prove, and what did it only infer?”

### 15.2 Decisions
- “Which recommendations are actual decisions and which are only assistant suggestions?”
- “Which decisions should become formal requirements in the master spec book?”

### 15.3 Tasks and Next Actions
- “Turn the next-action sequence into a Codex task prompt.”
- “Create a gated plan for verifying current repo layout and exceptions.”

### 15.4 Artifacts and Files
- “Explain each file in the preservation package.”
- “Extract only the aggregator packet from this package.”

### 15.5 Risks and Verification
- “What are the biggest ways future assistants could overstate implementation maturity?”
- “What must be verified before claiming the repo has completed layout convergence?”

### 15.6 Future Spec Book / Aggregation
- “Which sections of a Dominium Project Spec Book should this chat feed?”
- “Convert the decisions and constraints into formal spec requirements.”

### 15.7 Deep-Dive Questions Specific to This Chat
- “Design the second minimal Domino product reuse proof.”
- “Draft a public C89 Domino ABI contract.”
- “Audit the survival vertical slice from registry to runtime execution.”

## 16. Compact Human Summary

This chat re-grounded Dominium around its old v1 constitution and glossary, then checked the current GitHub repository against that old canon, and finally broadened into a doctrine for building Dominium as a reusable platform rather than a one-off game. The old v1 contract defined Dominium as a deterministic universe simulation built on the Domino C89 engine, with a C++98 game layer, product applications, and XStack governance. It required deterministic math, named RNG streams, thread-count invariance, replay equivalence, LawProfile-driven behavior, AuthorityContext gating, Process-only mutation, no omniscience, and TruthModel → PerceivedModel → RenderModel separation. The glossary supplied canonical vocabulary and deprecated sloppy mode-flag terminology.

The live repository audit found that these old ideas have been materialized in repo canon, especially `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`. It also found a newer rule: raw prompts are not authoritative unless materialized as canonical docs. The repo has strong documentation, schema, registry, build, and governance alignment, including C90/C++98 build discipline, XStack/RepoX/TestX/AuditX scaffolding, deterministic RNG code, world save/load/checksum scaffolding, SessionSpec and AuthorityContext schemas, and a deterministic client session pipeline. But the implementation is not yet the full old v1 vision. Survival exists strongly as registries and LawProfiles; full agent gameplay loops, embodiment, MMO-scale distributed authority runtime, and other advanced systems remain incomplete, deferred, or future-facing.

The later portability discussion established the most important engineering doctrine: the project should not try to freeze all code and directories. It should freeze contracts, semantic IDs, public APIs, save/replay formats, schemas, command/refusal protocols, and verification gates, while making implementations replaceable. The current ownership-root layout is broadly the right direction: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`. Generic roots such as `src`, `source`, `common`, `shared`, and `misc` should not be used for active code because they hide ownership.

The most important unresolved issue is to verify the current physical repo tree and active exceptions. The docs say convergence has moved product roots under `apps/`, but current inspection in this session produced a possible inconsistency around old `client/` paths. That should be checked with a full tree listing or local checkout. Other priorities are to formalize stable API/ABI boundaries, audit which survival/gameplay processes are actually implemented, define data compatibility/migration rules, and eventually add a second minimal Domino-based product as a reuse proof.

The best next action is a current-state structural audit: tree layout, exception ledger, public API inventory, schema/version inventory, and runtime implementation proof. Only after that should broad cleanup or feature expansion proceed.
