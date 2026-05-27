# COMPLETE CHAT PRESERVATION REPORT — Domino/Dominium Portability, Assurance, and Future-Proof Architecture

## 0. Coverage and Reliability Assessment

| Field | Assessment |
| --- | --- |
| Chat label | Domino/Dominium Portability, Assurance, and Future-Proof Architecture |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless explicitly labelled PROJECT-CONTEXT. |
| Apparent access | Partial / visible context. I can use the visible transcript and uploaded prompt, but cannot guarantee hidden or earlier transcript access. |
| Previously generated files available? | No prior downloadable files visible before this response. |
| Uploaded files or artifacts present? | Yes. Pasted text.txt was uploaded and used. |
| Contains future plans? | Yes. DDAP, DIL levels, contracts, conformance tests, registries, validators, repo-structure work. |
| Contains decisions? | Yes, but mostly assistant recommendations plus user-stated priorities. |
| Contains pending tasks? | Yes. Architecture/validation tasks proposed; preservation package completed by this response. |
| Contains unresolved questions? | Yes. Repo state, accepted architecture, first pilot module, compatibility promises. |
| Staleness risk | Medium. |
| Extraction confidence | 4/5 for visible chat; 2/5 for unseen full-history completeness. |
| Safe for later aggregation? | With caveats. |
| Main limitations | No repo inspection; no guaranteed hidden transcript access; external standards need verification. |

Limitations: this package preserves visible current-chat context and the uploaded preservation prompt. It does not prove that hidden transcript segments, other conversations, repository files, or older generated artifacts were accessible. Broader project context is not treated as current-chat fact unless labelled.

## 1. One-Page Orientation

This chat was mainly about turning Domino/Dominium from a one-off game project into a durable, reusable engine/product platform. It began with a question about whether standards from high-assurance domains—especially DO-178B/C and adjacent secure-development, supply-chain, and metadata standards—could be used for Domino and Dominium. The proposed answer was that the project should use standards as design inputs, not as compliance targets. The useful parts are traceability, requirements-based tests, tool-impact classification, independent review, secure development, release provenance, SBOM/license metadata, and risk-based assurance. The wrong move would be claiming or pursuing avionics-style certification for a game/engine project.

The user then widened the topic. They explicitly said that portability, modularity, extensibility, reuse, refactorability, and future-proofing are very important. They want code reusable for another game on Domino, and possibly for different engine or game projects. They also want files and directories replaceable during rewrites or major refactors. The desired quality bar is closer to a proper game platform or OS-style system than a throwaway indie project.

The central proposed answer was that Domino should be a contract-governed engine platform, while Dominium should be one product built on it. The assistant’s core doctrine was “stable outside, replaceable inside.” Public contracts—headers, save formats, pack formats, replay formats, schemas, protocols, command/result APIs, capability IDs, and migration rules—should be explicit, versioned, tested, and hard to break casually. Private internals, algorithms, backend modules, and directory-internal helper files should remain replaceable.

A recurring point was that modularity is not created by folder names alone. A real module needs an owner, purpose, public contract, private implementation, declared dependencies, forbidden dependencies, fixtures, conformance tests, versioning policy, diagnostics/error policy, and replacement criteria. The replacement test is: can this directory be deleted and reimplemented against only public contracts, while passing the same conformance tests and loading the same data? If yes, the boundary is meaningful. If no, the project is probably coupled through hidden assumptions.

The chat also proposed concrete practices: public C-style API discipline; opaque handles; size/version/reserved fields in public structs; no C++ ABI across plugin boundaries; no platform handles in core APIs; stable registries for tags, opcodes, error codes, capability IDs, and format versions; deterministic simulation isolated from OS/UI/renderers/wall-clock time; conformance, migration, fuzz, replay, and layer tests; setup as a transactional system; launcher as a control plane; and tools/UI as public-contract consumers.

The final user action uploaded a preservation-package prompt. This response turns the visible chat into a human-readable report, registers, context packet, spec sheet, aggregator packet, audit, and downloadable ZIP. The main caveat is that many technical details are assistant recommendations, not explicit user-ratified decisions, and the actual repository was not inspected. A future assistant should preserve that distinction.

## 2. The Story of the Conversation

### Opening: standards as inspiration, not compliance

The chat began with the user pasting a standards-focused answer originally framed around Eureka and asking whether similar ideas could be used for Domino and Dominium. The answer developed into a recommendation: borrow assurance patterns, but do not claim or pursue DO-178C or similar compliance.

### Expansion: from assurance to platform architecture

The user then clarified that the real concern was broader: all code should be portable, modular, extensible, reusable, replaceable, and future-proof. This shifted the conversation from standards to the whole structure of the engine/product ecosystem.

### Concrete architecture

The assistant proposed treating Domino as a reusable engine/runtime/toolchain and Dominium as one product built on it. It proposed stable public contracts, replaceable internals, conformance tests, versioned data formats, deterministic simulation boundaries, explicit naming rules, and a target ownership-based repository layout.

### Preservation checkpoint

The user then uploaded a maximum-fidelity preservation prompt. The task became preserving this chat into a package suitable for human reading and future aggregation. This response is that package.

## 3. Main Topics Discussed

### Topic 1 — Standards-informed assurance

The chat proposed using standards such as DO-178C, NIST SSDF, OWASP ASVS, SLSA, and SPDX as design inputs only. The proposed internal version is DDAP v0 with DIL levels. Uncertainty: user has not explicitly ratified DDAP.

### Topic 2 — Domino as reusable engine and Dominium as product

The user’s explicit reuse requirement led to the proposed split: Domino is engine/runtime/toolchain; Dominium is one product using Domino. Domino should not depend on Dominium.

### Topic 3 — Stable contracts and replaceable internals

The main doctrine was stable outside, replaceable inside. Public contracts and persistent formats are stable; internals remain free to change.

### Topic 4 — Directory structure and module ownership

A target tree was proposed: include/, contracts/, source/domino/, source/dominium/, tests/conformance/, tests/migration/, tests/fuzz/, tools/validators/, docs/architecture/, docs/assurance/. This is a candidate, not a repo-verified plan.

### Topic 5 — Public API/ABI discipline

The proposed rules include opaque handles, size/version/reserved fields, explicit allocator ownership, project-owned primitive types, no C++ ABI at plugin boundaries, no platform types in core APIs, and lifecycle labels.

### Topic 6 — Data compatibility

Saves, packs, replays, protocols, and schemas need versioning, registries, migration tests, hashes/signatures where appropriate, and no reuse of released IDs.

### Topic 7 — Determinism and replay

Simulation should be isolated from wall-clock time, OS APIs, UI, renderer backends, and unordered platform-specific behavior. Replay equality should be testable.

### Topic 8 — Testing and validators

Conformance tests prove replaceability. High-trust paths need valid, invalid, malformed, old-version, future-version, migration, roundtrip, determinism, and negative-permission tests.

### Topic 9 — Setup, launcher, tools, and UI boundaries

Setup should be transactional; launcher should orchestrate; tools should use public contracts; UI should use command/result/view-model contracts.

### Topic 10 — Preservation and aggregation

The uploaded prompt required this preservation report, registers, spec sheet, aggregator packet, audit, files, and ZIP.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user wanted to know whether standards can be used wisely for Domino/Dominium. The user also explicitly wanted portability, modularity, extensibility, reuse, replaceability, proper-game/OS-grade structure, better directories, better names, better APIs, better schemas, and future-proof/backward-compatible design. The uploaded prompt explicitly requested a maximum-fidelity preservation package.

### 4.2 Inferred Goals

The user likely wants these outputs to feed a future master Project Spec Book and prevent long-chat context loss.

### 4.3 Goals That Changed Over Time

The conversation widened from standards to full engine architecture, then shifted to preservation/export.

### 4.4 Goals Still Unresolved

The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
| --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use standards as design inputs, not literal compliance targets. | Assistant recommendation; not explicitly user-ratified. | Useful assurance patterns should be borrowed; external certification wrappers are misaligned. | 4 | INFERENCE / assistant recommendation |
| DECISION-02 | Separate Domino as reusable engine/runtime/toolchain from Dominium as one product built on it. | Assistant recommendation aligned with explicit user goal. | Engine/product separation prevents product assumptions contaminating reusable code. | 5 | FACT goal + INFERENCE architecture |
| DECISION-03 | Stable public contracts, replaceable internals. | Assistant recommendation; not separately accepted after answer. | Preserves compatibility while allowing deep refactors. | 4 | assistant recommendation |
| DECISION-04 | Do not make every internal function/header stable. | Assistant recommendation. | Freezing internals creates accidental compatibility burdens. | 4 | assistant recommendation |
| DECISION-05 | Use internal DIL-0 through DIL-5 levels for assurance gates. | Assistant recommendation; not user-confirmed. | Applies rigor only where trust/persistence/authority/external impact exists. | 4 | assistant recommendation |
| DECISION-06 | Prioritise assurance for saves, packs, replay, authority, updater/installer, multiplayer, and mod trust. | Assistant recommendation. | Failures here can corrupt data, break compatibility, or undermine trust/security. | 4 | assistant recommendation |
| DECISION-07 | Use conformance tests as proof of replaceability. | Assistant recommendation. | Replacement must be objectively testable. | 4 | assistant recommendation |
| DECISION-08 | Treat data evolution as seriously as code evolution. | Assistant recommendation. | Long-lived projects often fail through broken data compatibility. | 4 | assistant recommendation |
| DECISION-09 | Do not present this package as guaranteed full transcript extraction. | Decision in this package. | Preservation must be honest about source scope. | 5 | FACT / UNCERTAIN scope |

### DECISION-01 — Use standards as design inputs, not literal compliance targets.

Status: Assistant recommendation; not explicitly user-ratified.

Basis: User asked whether standards could be used for Domino/Dominium; assistant answered yes, but not as certification/compliance.

Rationale: Useful assurance patterns should be borrowed; external certification wrappers are misaligned.

Implications: Creates DDAP-style internal profile rather than compliance claim.

Caveat: carry forward as `INFERENCE / assistant recommendation`.

### DECISION-02 — Separate Domino as reusable engine/runtime/toolchain from Dominium as one product built on it.

Status: Assistant recommendation aligned with explicit user goal.

Basis: User explicitly wanted reuse for another game and other engine/game projects.

Rationale: Engine/product separation prevents product assumptions contaminating reusable code.

Implications: Domino should not depend on Dominium; Dominium consumes public contracts.

Caveat: carry forward as `FACT goal + INFERENCE architecture`.

### DECISION-03 — Stable public contracts, replaceable internals.

Status: Assistant recommendation; not separately accepted after answer.

Basis: Assistant framed this as the core doctrine.

Rationale: Preserves compatibility while allowing deep refactors.

Implications: Public headers/formats/protocols/tests stable; algorithms/private modules replaceable.

Caveat: carry forward as `assistant recommendation`.

### DECISION-04 — Do not make every internal function/header stable.

Status: Assistant recommendation.

Basis: Assistant warned against making all internal headers public or stable.

Rationale: Freezing internals creates accidental compatibility burdens.

Implications: Need explicit public/private split and lifecycle labels.

Caveat: carry forward as `assistant recommendation`.

### DECISION-05 — Use internal DIL-0 through DIL-5 levels for assurance gates.

Status: Assistant recommendation; not user-confirmed.

Basis: Assistant proposed levels for experiments through external-impacting systems.

Rationale: Applies rigor only where trust/persistence/authority/external impact exists.

Implications: DIL-3+ receives stronger evidence/tests/review; UI/content stays lighter.

Caveat: carry forward as `assistant recommendation`.

### DECISION-06 — Prioritise assurance for saves, packs, replay, authority, updater/installer, multiplayer, and mod trust.

Status: Assistant recommendation.

Basis: Assistant identified highest-value targets.

Rationale: Failures here can corrupt data, break compatibility, or undermine trust/security.

Implications: These paths need versioning, validation, negative tests, review gates, audit evidence.

Caveat: carry forward as `assistant recommendation`.

### DECISION-07 — Use conformance tests as proof of replaceability.

Status: Assistant recommendation.

Basis: Assistant stated stable interface without conformance suite is only a promise.

Rationale: Replacement must be objectively testable.

Implications: tests/conformance becomes first-class repo area.

Caveat: carry forward as `assistant recommendation`.

### DECISION-08 — Treat data evolution as seriously as code evolution.

Status: Assistant recommendation.

Basis: Assistant emphasized saves/packs/schemas/protocols and no tag reuse.

Rationale: Long-lived projects often fail through broken data compatibility.

Implications: Need registries, fixtures, migration tests, compatibility policy.

Caveat: carry forward as `assistant recommendation`.

### DECISION-09 — Do not present this package as guaranteed full transcript extraction.

Status: Decision in this package.

Basis: Visible context and uploaded prompt are available; hidden transcript/repo are not guaranteed.

Rationale: Preservation must be honest about source scope.

Implications: Safe for aggregation only with caveats.

Caveat: carry forward as `FACT / UNCERTAIN scope`.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

### REJECTED-01 — Claim or pursue DO-178C compliance for Domino/Dominium.

Status: Rejected by assistant recommendation.

Reason: Misaligned with game/engine project and implies certification obligations.

Reconsideration: Only reconsider for regulated safety-critical external use.

### REJECTED-02 — Apply heavy assurance to every line of code and all gameplay/content/UI.

Status: Rejected/deprioritised by assistant recommendation.

Reason: Would slow creative iteration and overburden low-risk work.

Reconsideration: Reconsider only if subsystem becomes trust-bearing.

### REJECTED-03 — Freeze all internal APIs/functions for compatibility.

Status: Rejected by assistant recommendation.

Reason: Internal stability preserves bad designs and blocks refactoring.

Reconsideration: Only for intentionally public/plugin APIs.

### REJECTED-04 — Use directory structure alone as proof of modularity.

Status: Rejected implicitly.

Reason: Folders need contracts, dependencies, tests, replacement criteria.

Reconsideration: None; structure remains necessary but insufficient.

### REJECTED-05 — Persist data by dumping raw C structs.

Status: Rejected by assistant recommendation.

Reason: Not portable across compilers/endian/alignment/schema evolution.

Reconsideration: Only for temporary debug snapshots marked nonportable.

### REJECTED-06 — Let setup/launcher/gameplay/tooling freely share privileged internals.

Status: Rejected by assistant recommendation.

Reason: Collapses boundaries and makes refactors/security/audits harder.

Reconsideration: Internal diagnostic privileged mode only if explicit.

## 7. Important Reasoning, Rationale, and Tradeoffs

The main tradeoff was between long-term rigor and practical development. The user wants platform/OS-grade discipline, but Domino/Dominium is not an avionics certification program. The assistant therefore proposed borrowing assurance practices only where they manage real project risk: saves, packs, replay, release integrity, authority boundaries, installers, mod trust, and multiplayer.

Another tradeoff was between stability and refactorability. Stability is necessary for reuse and backward compatibility, but too much stability too early freezes bad design. The answer therefore separated stable public contracts from replaceable private internals.

A third tradeoff was between folder organization and real modularity. The assistant argued that folder names are secondary to contracts, dependency rules, tests, fixtures, and replacement criteria.

## 8. Plans, Future Work, and Next Steps

Recommended next-action sequence:

1. Ratify or revise the doctrine: standards-informed not compliance-claiming; Domino separate from Dominium; stable outside/replaceable inside; data compatibility as first-class.
2. Inspect the actual repo tree, headers, build files, schemas, formats, tests, and dependency leaks.
3. Define public/private/experimental/stable/deprecated boundaries.
4. Draft public-api-policy.md, data-evolution-policy.md, layering.md, and ddap.md.
5. Add registries for stable IDs and formats.
6. Choose one conformance-test pilot, preferably pack validator or save reader.
7. Add layer checker and schema validators.
8. Build migration and malformed-input fixtures.
9. Use DIL gates only for trust-bearing paths.
10. Feed this package into the master Project Spec Book with caveats.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user explicitly required human-readable preservation, uncertainty labels, no invented facts, no silent inference, and no treating assistant recommendations as user decisions. The user explicitly values portability, modularity, extensibility, reuse, replaceability, future-proofing, and proper long-lived engineering.

### 9.2 Inferred Constraints and Preferences

The user likely wants spec-book-ready artifacts and dislikes compressed summaries that lose rationale.

### 9.3 Uncertain or Unestablished Preferences

It is not yet established whether the user accepts the exact DDAP/DIL structure, exact directory tree, exact naming prefixes, or exact C89/C++98 enforcement scope.

## 10. Files, Artifacts, Outputs, and Prompts

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | User-pasted standards/DO-178B/C/Eureka analysis | prompt content | Frame whether standards-inspired assurance could apply to Domino/Dominium. | Referenced; not independently verified here. | User message | Yes, as background and verification input. | Contains external standards claims/links needing verification. | FACT / VERIFY |
| ARTIFACT-02 | Assistant response: DDAP/DIL standards-informed assurance answer | generated chat output | Proposed project-native assurance profile and high-trust paths. | Produced; recommendations not explicitly ratified. | Assistant | Yes, with tentative label. | Includes DIL levels, repo impact, AIDE enforcement, boundary conditions. | assistant recommendation |
| ARTIFACT-03 | User question on portability, modularity, extensibility, replaceability, future-proofing | user instruction / design goal | Defines main architectural concern of the chat. | Explicit user requirement/preference. | User message | Yes, high priority. | Core source for platform doctrine. | FACT |
| ARTIFACT-04 | Assistant response: contract-governed engine platform answer | generated chat output | Proposed stable contracts, replaceable internals, repo tree, naming, schema, determinism, testing. | Produced; recommendations not explicitly ratified. | Assistant | Yes, as architecture draft. | Contains many candidate requirements/tasks. | assistant recommendation |
| ARTIFACT-05 | Pasted text.txt preservation mega-prompt | uploaded file | Instructs assistant to create complete preservation package and ZIP. | Loaded and used. | User upload | Yes, as method/template. | Source for current preservation task. | FACT |
| ARTIFACT-06 | Generated preservation package files | generated files | Preserve this chat in human-readable and machine-aggregatable form. | Created by this response. | Assistant file export | Yes. | Includes manifest, report, context packet, spec sheet, registers, aggregator packet, reader brief, audit, future-chat prompt, in-chat reader, ZIP. | FACT |

## 11. Open Questions and Unresolved Issues

### QUESTION-01 — Is DDAP v0 accepted as project direction or only a recommendation pending user review?

Why it matters: Determines whether DIL levels become canonical governance.

Known: Assistant recommended DDAP; user has not explicitly accepted it.

Unknown: User’s final acceptance and desired strictness.

Resolution path: Ask user to approve, revise, or reject DDAP.

### QUESTION-02 — What is the current actual repo structure?

Why it matters: Directory recommendations were not based on repo inspection.

Known: Only proposed structures and PROJECT-CONTEXT memories are available.

Unknown: Actual files, build scripts, and current coupling.

Resolution path: Inspect repo or have user provide tree.

### QUESTION-03 — Which public boundaries must be stable first?

Why it matters: Stabilizing too much too early freezes bad design; too little undermines portability.

Known: Assistant recommended public headers, formats, protocols, command/result APIs.

Unknown: Which systems are mature enough to freeze.

Resolution path: Define experimental/stable/deprecated lifecycle policy and boundary list.

### QUESTION-04 — How strict should C89/C++98 portability be across all code?

Why it matters: Portability rules depend on toolchains/platforms.

Known: PROJECT-CONTEXT says C89 engine and C++98 shells; current user asked portability but did not restate versions.

Unknown: Whether all current work enforces this now.

Resolution path: User confirms target platform/toolchain matrix.

### QUESTION-05 — What should be the first pilot module for conformance/replacement testing?

Why it matters: A concrete pilot prevents abstract architecture only.

Known: Assistant suggested pack validator, save reader, or render.soft.

Unknown: Which module exists and is easiest to isolate.

Resolution path: Choose one module and write module.toml + fixtures + tests.

### QUESTION-06 — What exact compatibility promises should be made for saves, packs, mods, and protocols?

Why it matters: Compatibility guarantees define future burden and user trust.

Known: Assistant recommended versioning and no ID reuse.

Unknown: Support window, migration guarantees, breaking-change process.

Resolution path: Write compatibility policy with tiers.

### QUESTION-07 — Which external standards claims need verification before formal spec use?

Why it matters: Standards change and some references are high-level/paywalled.

Known: Prior assistant cited several standards and practices.

Unknown: Current exact wording/applicability.

Resolution path: Verify against official/current sources before normative text.

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

### RISK-01 — Future assistant treats recommendations as user-approved decisions.

Consequence: Spec book may encode unratified advice as canon.

Likelihood/severity: Medium / High

Mitigation: Keep status labels; ask user to approve/reject DDAP and target structure.

### RISK-02 — Architecture becomes certification cosplay.

Consequence: Paperwork without real assurance; slowed development.

Likelihood/severity: Medium / Medium

Mitigation: Use project-native DIL levels; restrict heavy gates to trust paths.

### RISK-03 — Portability remains aspirational without conformance tests.

Consequence: Modules cannot actually be replaced; hidden coupling accumulates.

Likelihood/severity: High / High

Mitigation: Create tests/conformance and replacement criteria.

### RISK-04 — Data formats evolve without registries and migration tests.

Consequence: Old saves/mods/packs/replays break or corrupt silently.

Likelihood/severity: Medium / High

Mitigation: No-ID-reuse, registries, golden fixtures, migration tests.

### RISK-05 — Dominium-specific assumptions leak into Domino.

Consequence: Domino becomes unreusable.

Likelihood/severity: Medium / High

Mitigation: Layer checker; no Domino->Dominium dependencies.

### RISK-06 — Public API is frozen too early.

Consequence: Bad early designs become compatibility burdens.

Likelihood/severity: Medium / Medium

Mitigation: Use experimental/stable/deprecated lifecycle labels and promotion reviews.

### RISK-07 — External standards claims become stale/inaccurate.

Consequence: Spec book cites incorrect/outdated standards framing.

Likelihood/severity: Medium / Medium

Mitigation: Verification queue before normative incorporation.

### RISK-08 — Preservation package overstates access.

Consequence: Aggregator assumes complete extraction when only visible context was available.

Likelihood/severity: Medium / Medium

Mitigation: State coverage limitations clearly.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat contributes architecture doctrine, assurance framing, API/ABI policy candidates, data-compatibility doctrine, conformance testing requirements, determinism/replay principles, and setup/launcher/tool/UI boundary principles. It should feed future spec-book chapters but should not be merged as final canon without checking recommendation status and actual repo state.

## 14. What I Should Remember

- The explicit user requirement is portable, modular, extensible, reusable, replaceable, future-proof code.
- The strongest proposed doctrine is stable public contracts with replaceable internals.
- Domino should be reusable engine/runtime/toolchain; Dominium should be one product using it.
- Modularity must be proven by conformance tests, not just folders.
- Data compatibility is as important as code compatibility.
- Saves, packs, replays, schemas, protocols, IDs, and migrations need policy from the beginning.
- Standards should inform the project but not become compliance claims.
- DDAP/DIL is proposed, not yet user-ratified.
- The actual repo was not inspected.
- The best next action is repo boundary audit plus first policy/registry/conformance pilot.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
1. Explain stable-outside/replaceable-inside in simpler terms.
2. Which recommendations are strongest and which are speculative?

### 15.2 Decisions
3. Which recommendations should become project canon?
4. Should DDAP/DIL be accepted, revised, or rejected?

### 15.3 Tasks and Next Actions
5. Convert the task register into a first-month implementation plan.
6. Pick the best first conformance-test pilot.

### 15.4 Artifacts and Files
7. Which generated file should I use for a future chat bootstrap?
8. Extract only formal requirement candidates.

### 15.5 Risks and Verification
9. What could go wrong if we freeze public APIs too early?
10. Which standards claims need verification?

### 15.6 Future Spec Book / Aggregation
11. Which spec-book chapters should this feed into?
12. What overlaps with other Dominium chats?

### 15.7 Deep-Dive Questions Specific to This Chat
13. Draft public-api-policy.md.
14. Draft data-evolution-policy.md.
15. Draft ASSURANCE_PROFILE.md.
16. Turn the “20 laws” into CI checks.

## 16. Compact Human Summary

This chat is a major architecture checkpoint for Domino/Dominium. It first asked whether standards such as DO-178B/C and related security/supply-chain frameworks should influence the project. The proposed answer was yes, but only as design input. Domino/Dominium should not claim aviation, automotive, medical, or industrial compliance. It should borrow useful patterns: traceability, requirements-based tests, tool-impact classification, review independence, secure-development practices, release provenance, SBOM/license metadata, and risk-based assurance.

The internal version proposed was DDAP v0, using DIL levels from low-risk experiments to external-impacting systems. Most ordinary game/content/UI work should stay light. Stronger controls should apply to trust-bearing paths such as saves, packs, mod loading, replay, authority/capability logic, installers/updaters, signed releases, multiplayer authority, native/offline clients, and automated execution. This is a recommendation, not yet a user-ratified decision.

The user then clarified the deeper issue: all code should be portable, modular, extensible, reusable, replaceable, and future-proof. The user wants Domino reused for other games and possibly other engine/game projects. They want files and directories replaceable during major rewrites. The desired standard is a proper long-lived platform, closer to OS-grade discipline than a one-off indie project.

The assistant’s strongest doctrine was stable outside, replaceable inside. Public contracts and persistent formats should be stable, versioned, documented, and tested. Internal implementation code should remain free to change. Public contracts include headers, save formats, pack formats, replay formats, protocols, schemas, command/result APIs, capability IDs, error codes, and migration rules. Private internals include helper files, algorithms, backend details, and non-public structs.

The conversation emphasized that directory structure is not enough. A real module needs an owner, purpose, public contract, private implementation, declared dependencies, forbidden dependencies, fixtures, conformance tests, versioning policy, diagnostics/error policy, and replacement criteria. The replacement test is whether a directory can be deleted and reimplemented against only public contracts while still passing the same tests and loading the same data.

Several concrete repo ideas were proposed: include/domino, include/dominium, contracts, source/domino, source/dominium, tests/conformance, tests/migration, tests/fuzz, tools/validators, docs/architecture, and docs/assurance. These are proposals; the actual repo was not inspected.

API/ABI discipline was a major theme: opaque handles, desc structs with size/version/reserved fields, explicit allocator ownership, project-owned integer types, no platform handles in core APIs, no exposed private structs, no public bitfields, no C++ ABI across plugin boundaries, no global singleton state, and lifecycle labels such as experimental, stable, deprecated, internal, and removed.

Persistent data compatibility was treated as central. The assistant rejected raw struct dumps for long-lived saves. Instead it recommended versioned, endian-explicit, chunked/TLV-based formats with magic values, format IDs, writer versions, minimum reader versions, schema IDs, chunk tables, hashes, optional signatures, migration paths, unknown-field policies, and reserved ID registries. Released IDs should never be reused.

Testing was framed as the proof of modularity. Unit tests are insufficient. The project needs contract tests, conformance tests, golden tests, replay tests, migration tests, fuzz tests, fault-injection tests, platform tests, layer tests, build-matrix tests, performance budgets, and security tests. High-trust paths require valid, invalid, old-version, future-version, malformed, roundtrip, migration, determinism, and negative-permission fixtures.

The uploaded prompt requested this preservation package. The main caveat is that the package preserves visible chat context and the uploaded prompt, not a guaranteed hidden full transcript or inspected repository. The best next action is to inspect the actual repo and turn the strongest recommendations into a small set of enforceable policies and one conformance-test pilot.
