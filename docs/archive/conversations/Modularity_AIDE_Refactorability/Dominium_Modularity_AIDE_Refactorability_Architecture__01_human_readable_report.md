# COMPLETE CHAT PRESERVATION REPORT — Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only, except explicitly labelled PROJECT-CONTEXT |
| Apparent access | Partial-to-good: visible current chat plus uploaded preservation prompt; not the full live repo or all prior generated files |
| Previously generated files available? | Unclear / mostly no: prior files are referenced, but not available as downloadable artifacts in this chat |
| Uploaded files or artifacts present? | Yes: `Pasted text.txt`, containing the preservation-package output contract |
| Contains future plans? | Yes |
| Contains decisions? | Yes, but many are assistant recommendations unless clearly adopted by user language |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium: repo status, commit IDs, live tooling status, and external practice references need verification before implementation |
| Extraction confidence | 4/5 for visible-chat substance; 2/5 for live repo facts and older unavailable artifacts |
| Safe for later aggregation? | With caveats |
| Main limitations | No live repo inspection in this turn; no full old-chat transcript beyond visible current conversation; prior generated files and older uploads may be unavailable/expired; several repo-status claims were pasted from earlier assistant outputs and are not independently verified here. |


This package is based on the visible current chat and the uploaded `Pasted text.txt` prompt. It does not include live repository inspection, execution of validators, or complete access to older files generated in other chats. Some older uploaded files appear unavailable or expired in the broader chat environment. Where this report mentions repo state, CTest failures, specific commit IDs, or current file paths from pasted prior assistant outputs, those are treated as **UNCERTAIN / UNVERIFIED** unless independently verified later. The package is safe for aggregation if future readers preserve these labels and do not treat every assistant recommendation as an adopted user decision.

## 1. One-Page Orientation


This chat was about making Dominium structurally durable: portable, modular, extensible, reusable across future games, and refactorable without the user having to repeat a painful top-level cleanup. The discussion began from an already-developed architectural thread about Dominium’s source layout, distribution layout, package layout, install roots, runtime roots, bundle formats, and component matrices. The user brought in several previous assistant outputs that had converged on a broad direction: Dominium should not be treated like a one-off indie project, but like a long-lived platform with a stable architecture, stable contracts, deterministic build/release/install semantics, and a repo structure that can survive multiple products, renderers, platforms, shells, and content systems.

The key early idea was that Dominium needs more than a source repo directory layout. It needs a unified logical-root model that can be projected into CI output, `.dompkg` packages, portable installs, installed desktop/server layouts, read-only media, caches, staging roots, rollback state, symbols, provenance, save bundles, instance bundles, replay bundles, and diagnostics bundles. This led to the principle that `.zip` archives, installers, portable folders, package files, media images, save bundles, and runtime installs should not invent separate semantics. They should all bind to the same logical roots, with physical paths depending on mode and mutability.

The next topic was the source repo itself. The user and assistant treated the existing root clutter as a serious architectural problem, not cosmetic untidiness. The target root set was repeatedly narrowed toward stable ownership categories: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, and generated `dist/` under strict policy. The important conclusion was that future top-level roots should be refused by default. New work should fit into existing ownership surfaces unless it truly has a separate lifecycle and long-term purpose.

A major correction happened when the user rejected the old XStack/AuditX/RepoX/TestX framing. The user wanted to transition to AIDE as soon as possible and recycle existing code/docs/tests rather than ignore them. The answer shifted from “make old checks green first, then clean” to “install AIDE as the restructuring control plane now, wrap and salvage old tools, and then drive cleanup through AIDE work units.” This became one of the central outcomes of the chat: AIDE should own inventory, classification, move maps, salvage maps, reference rewriting, validators, evidence ledgers, path aliases, shims, and refactor history.

The user then broadened the goal. The concern was not only Dominium’s current folder tree, but whether the codebase could become a proper reusable game/engine platform. The final answer introduced a product-line architecture view. Code should be split by reuse level: reusable across Dominium products, reusable across future games on the same domino/Dominium engine, and reusable across unrelated engine or game projects. That means contracts, runtime infrastructure, tooling, deterministic base engine pieces, content-addressed storage, diagnostics, packaging, schemas, tests, and AIDE machinery should be reusable beyond Dominium where possible, while `game/` should hold Dominium-specific truth.

The most important stable principles were: paths are not identity; contracts and manifests define identity; apps are thin; runtime owns host adaptation; engine owns deterministic substrate; game owns Dominium-specific rules; durable APIs need stability levels; C89-compatible ABI seams should be used for stable boundaries without forcing every internal implementation to be C89; schemas and protocols must be versioned; capability negotiation should replace platform-era assumptions; generated outputs must be quarantined; and every future refactor should be mechanical, evidence-backed, and reversible.

This chat contributes a high-level architecture constitution and refactorability doctrine for Dominium. It should feed directly into a future Project Spec Book section on repository architecture, reusable engine architecture, runtime/platform modularity, packaging/install semantics, AIDE governance, API/ABI stability, schemas/protocols, deterministic data, testing, and compatibility policy. Its main limitation is that several concrete repo-status claims came from pasted earlier outputs and were not verified against the live repository in this turn.


## 2. The Story of the Conversation


The conversation opened with the user pasting a prior analysis about Dominium’s distribution and install layouts. That analysis argued that the source repository is only one layer. Dominium also needs canonical layouts for release build output, compressed packages, portable installs, installed layouts, instances and saves, bundles, diagnostics, caches, staging, rollback, symbols, provenance, and media. The core idea was that all these physical layouts should be projections of one logical virtual-root contract. The user then pasted another prior analysis about root convergence. That analysis treated the live repository as cluttered, with many roots mixing ownership levels, and proposed a staged convergence program around a stable source layout, distribution layout, runtime/install layout, and mechanical enforcement.

The next pasted section focused on component naming. It argued that Dominium should support many platforms, renderers, shells, package types, and presentation qualities, but should avoid names like `compat`, `universal`, `legacy`, `modern`, `gl2`, `vk1`, `dx11`, `winui3`, and `portable_zip` as primary component IDs. The better pattern was to name the component by what it is, then put version, support status, host age, package format, and constraints into matrix fields. This led to a clean modular architecture model: fixed contracts, runtime components, product entrypoints, and domain/content components.

The user asked whether this was the best possible direction. The response accepted the broad direction but strengthened it: the goal should be a contract-driven projection system, not just a directory plan. The answer added machine-readable contracts, a projection model, split host/platform axes, evidence levels in matrix rows, refusal codes, generated artifact policy, thin-app enforcement, a truth pipeline, capability negotiation, a minimum viable proof path, and migration safety rules.

The user then pasted another prior analysis about remaining root clutter and CTest/AuditX/RepoX blockers. That analysis recommended not doing visual folder cleanup and instead stabilizing failing checks before root exception cleanup. The user objected to the XStack/AuditX/RepoX/TestX framing and said they wanted to transition to AIDE as soon as possible while recycling existing code and docs. This changed the direction of the plan. The response agreed that the old names were temporary scaffolding and should not become durable architecture. It proposed AIDE as the control plane, with old tools inventoried, wrapped, adapted, renamed, archived, or retired through evidence-backed work units.

The user then asked whether this was truly the best plan and emphasized not wanting to go through the restructuring headache again. The answer refined the objective: the aim is not a perfect structure that never changes, but a stable top-level constitution plus a refactor operating system. Future internal movement should be cheap because it is scripted, validated, reversible, and driven by AIDE move maps and salvage maps. This produced the idea of `AIDE-STRUCTURE-00`, a repo constitution and refactorability framework.

Finally, the user made the broadest request: Dominium code must be portable, modular, extensible, reusable for another game on the same engine, and potentially reusable for different engine or game projects. The user wanted to know what was missing, what practices apply generally and specifically, whether the directory structure and names were the best they could be, what major engineering organizations do, and how to maximize future-proofing and backwards compatibility. The response reframed Dominium as a product-line architecture rather than a single game. It proposed explicit reuse levels, stricter internal structure for `contracts/`, `engine/`, `game/`, `runtime/`, `apps/`, `content/`, and `release/`, and detailed practices for ABI design, API stability, schemas, protocols, naming, target-based builds, dependency visibility, component manifests, data design, tests, compatibility, AIDE-driven refactors, portability threats, determinism, memory, errors, logging, concurrency, serialization, and host abstraction.

The final user action was uploading a preservation-package prompt. That prompt requested a maximum-fidelity preservation report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, downloadable files, and a final in-chat reader. This package is the result.


## 3. Main Topics Discussed

### Topic 1 — Unified layout projection system

The chat repeatedly distinguished source layout from distribution/build output, packages, portable installs, installed layouts, media, caches, rollback roots, symbols, bundles, saves, and diagnostics. The conclusion was that these should not be separate semantic inventions. They should be physical projections of a shared virtual-root contract. This matters because `.zip`, `.dompkg`, installer, media image, and runtime folder semantics can otherwise drift apart. The uncertainty is that the exact contract file names and root names still need implementation against the live repo.

### Topic 2 — Stable source repo constitution

The target top-level layout stabilized around `.aide/`, `.github/`, `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, and generated `dist/`. The purpose is to make root ownership long-lived and prevent future root sprawl. The most important rule is that new top-level roots are refused by default unless they pass a strict lifecycle and ownership test.

### Topic 3 — AIDE as restructuring control plane

The user objected to the XStack/AuditX/RepoX/TestX framing and wanted AIDE adopted quickly. The resulting plan made AIDE the repo-native control plane for inventory, task queues, policies, move maps, salvage maps, evidence ledgers, validation, and refactor history. Existing tools should be recycled, not discarded. This is central to future refactorability.

### Topic 4 — Product-line architecture and reuse levels

The final discussion broadened Dominium from a single game to a reusable platform. Code should be separated by whether it is reusable across Dominium products, reusable across games on the same domino/Dominium engine, or reusable across unrelated engine/game projects. This changes where code belongs: reusable infrastructure should live in `contracts/`, `engine/base/`, `runtime/`, or `tools/`, while Dominium-specific rules belong in `game/`.

### Topic 5 — Contracts, API, ABI, schemas, and protocols

The chat emphasized that durable identity and compatibility should live in contracts and manifests, not paths. Public seams need stability levels. C89-compatible ABI headers are valuable for stable boundaries, using opaque handles, explicit allocators, versioned structs, and stable error codes. Schemas and protocols need versioning, negotiation, compatibility ranges, refusal codes, and migration policy.

### Topic 6 — Naming and component matrices

The chat rejected names based on era, temporary project status, support status, or implementation-version encoding. Components should have boring literal names such as `opengl`, `direct3d`, `vulkan`, `software`, `win32`, `posix`, `cocoa`, `portable`, `installed`, with version/status/format fields carried separately. This reduces long-term naming debt.

### Topic 7 — Build, dependency, and visibility discipline

The discussion proposed target-based CMake and module boundaries rather than path mythology. Public headers, private headers, allowed dependencies, and forbidden dependencies should be explicit. Apps must remain thin. Engine must not depend on game/apps/runtime UI. Runtime adapts host/platform/rendering without owning simulation truth.

### Topic 8 — Determinism, data, compatibility, and testing

The chat stressed deterministic serialization, named RNGs, no wall-clock dependency in simulation, no filesystem ordering dependence, schema round-trip tests, replay tests, package verification tests, migration tests, renderer parity tests, and hermetic tests. Compatibility should be promised only for selected public seams, not every internal implementation.

### Topic 9 — Preservation and aggregation

The uploaded prompt converted the conversation into a preservation task. It requires a human-readable report first, then registers, spec sheet, aggregator packet, self-audit, and downloadable files. This final package is intended to be merged later with old-chat reports into a master Project Spec Book.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted Dominium’s code and architecture to be portable, modular, extensible, reusable for other games on the same engine, and reusable where possible for different engine or game projects. The user also explicitly wanted to avoid repeating a painful restructuring process and wanted future full refactors to be as quick and easy as possible. The user wanted AIDE adopted quickly as the restructuring control plane and wanted existing code/docs/tests recycled rather than ignored.

### 4.2 Inferred Goals

The conversation implies a goal of turning Dominium into a long-lived product-line platform rather than a single-game repository. It also implies a desire for auditability: decisions should be grounded, visible, mechanically enforceable, and later aggregatable into a master spec. The user appears to value stable boundaries, explicit compatibility policy, and practical Codex/AIDE tasks.

### 4.3 Goals That Changed Over Time

The initial focus was directory and distribution structure. It then widened to component naming, repository convergence, AIDE governance, refactorability, and finally broad software engineering doctrine for reusable engine/platform development. The most important change was the rejection of the XStack-style framing and the shift toward AIDE as the near-term control plane.

### 4.4 Goals Still Unresolved

The live repo still needs verification. The exact AIDE files, contracts, validators, and migration tasks must be implemented. It remains unresolved which existing roots and tools map to which final homes, which APIs become stable, which code is reusable across products/games/projects, and which prior assistant recommendations should become formal requirements after user review.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered / basis | Confidence | Label |
| --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use a stable top-level root constitution rather than ad hoc root growth. | accepted direction | Repeated user concern about avoiding future restructure; assistant proposals align. | WORKSTREAM-01 | high |
| DECISION-02 | Treat AIDE as the restructuring control plane. | accepted by user framing | User explicitly said to transition to AIDE ASAP and recycle existing material. | WORKSTREAM-03 | high |
| DECISION-03 | Recycle old tools/docs/tests rather than ignore or discard them. | accepted direction | User explicitly said there is code and docs to recycle. | WORKSTREAM-04 | high |
| DECISION-04 | Paths are not identity; contracts and manifests define identity. | strong recommendation | Repeated in final architecture answer. | WORKSTREAM-05 | high |
| DECISION-05 | Design Dominium as a product-line architecture, not a one-off game. | accepted objective | User explicitly requested proper game/OS-like architecture and reusable code. | WORKSTREAM-05 | high |
| DECISION-06 | Use C89-compatible stable ABI seams, without forcing all internals to be C89. | recommendation | Assistant proposed this refinement. | WORKSTREAM-06 | medium |
| DECISION-07 | Avoid durable architecture names based on temporary tooling or status labels. | accepted direction | User disliked XStack framing; prior component naming analysis rejected legacy/modern/compat labels. | WORKSTREAM-07 | high |
| DECISION-08 | Future refactors should be AIDE work units with move maps and salvage maps. | recommendation aligned with user goal | User wanted future refactors easy and quick. | WORKSTREAM-03 | high |
| DECISION-09 | Apps should be thin; runtime adapts host; engine/game own truth. | strong recommendation | Repeated in architecture doctrine. | WORKSTREAM-05 | medium-high |
| DECISION-10 | Do not promise compatibility for every internal interface. | recommendation | Final response emphasized stabilizing correct public seams only. | WORKSTREAM-06 | medium |

### DECISION-01 — Use a stable top-level root constitution rather than ad hoc root growth.

Status: accepted direction. Basis: Repeated user concern about avoiding future restructure; assistant proposals align. Rationale: Prevents root sprawl and preserves ownership clarity. Implications: Future roots require admission tests and validators. Related workstream: WORKSTREAM-01. Confidence: high. Label: FACT/INFERENCE. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

### DECISION-02 — Treat AIDE as the restructuring control plane.

Status: accepted by user framing. Basis: User explicitly said to transition to AIDE ASAP and recycle existing material. Rationale: AIDE provides queue, evidence, move-map, and salvage discipline. Implications: Old XStack-style tools become transitional assets. Related workstream: WORKSTREAM-03. Confidence: high. Label: FACT. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

### DECISION-03 — Recycle old tools/docs/tests rather than ignore or discard them.

Status: accepted direction. Basis: User explicitly said there is code and docs to recycle. Rationale: Prevents loss of useful validators and policies. Implications: Requires classification: keep/adapt/extract/convert/archive/drop. Related workstream: WORKSTREAM-04. Confidence: high. Label: FACT. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

### DECISION-04 — Paths are not identity; contracts and manifests define identity.

Status: strong recommendation. Basis: Repeated in final architecture answer. Rationale: Makes directories replaceable and data portable. Implications: Packs, saves, schemas, modules, and packages need IDs, versions, hashes, capabilities. Related workstream: WORKSTREAM-05. Confidence: high. Label: INFERENCE. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

### DECISION-05 — Design Dominium as a product-line architecture, not a one-off game.

Status: accepted objective. Basis: User explicitly requested proper game/OS-like architecture and reusable code. Rationale: Supports reuse across products, games, and projects. Implications: Requires stricter separation of engine/game/runtime/contracts/tools/content. Related workstream: WORKSTREAM-05. Confidence: high. Label: FACT. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

### DECISION-06 — Use C89-compatible stable ABI seams, without forcing all internals to be C89.

Status: recommendation. Basis: Assistant proposed this refinement. Rationale: Stable external seams with flexible implementation. Implications: Public headers need opaque handles, allocators, versioned structs, error codes. Related workstream: WORKSTREAM-06. Confidence: medium. Label: INFERENCE. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

### DECISION-07 — Avoid durable architecture names based on temporary tooling or status labels.

Status: accepted direction. Basis: User disliked XStack framing; prior component naming analysis rejected legacy/modern/compat labels. Rationale: Prevents temporary migration scaffolding becoming permanent ontology. Implications: Use boring literal names and matrix fields. Related workstream: WORKSTREAM-07. Confidence: high. Label: FACT/INFERENCE. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

### DECISION-08 — Future refactors should be AIDE work units with move maps and salvage maps.

Status: recommendation aligned with user goal. Basis: User wanted future refactors easy and quick. Rationale: Turns restructuring into a mechanical process. Implications: Requires AIDE refactor schemas, ledgers, validators, and temporary aliases. Related workstream: WORKSTREAM-03. Confidence: high. Label: INFERENCE. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

### DECISION-09 — Apps should be thin; runtime adapts host; engine/game own truth.

Status: strong recommendation. Basis: Repeated in architecture doctrine. Rationale: Preserves portability and prevents UI/rendering/platform code owning simulation truth. Implications: Boundary validators needed. Related workstream: WORKSTREAM-05. Confidence: medium-high. Label: INFERENCE. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

### DECISION-10 — Do not promise compatibility for every internal interface.

Status: recommendation. Basis: Final response emphasized stabilizing correct public seams only. Rationale: Avoids maintenance paralysis. Implications: Need stability levels and deprecation policy. Related workstream: WORKSTREAM-06. Confidence: medium. Label: INFERENCE. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

### REJECTED-01 — Visual drag-and-drop cleanup of root folders

Status: rejected. It was rejected/superseded because Would break paths, build, tests, package identity, and authority semantics. Finality: final unless repo becomes trivial. Reconsider conditions: Only reconsider for tiny isolated folders with move map and proof.. Related workstream: WORKSTREAM-01. Label: FACT/INFERENCE.

### REJECTED-02 — XStack/AuditX/RepoX/TestX as durable architecture ontology

Status: rejected/superseded. It was rejected/superseded because User disliked it; names are temporary scaffolding. Finality: mostly final. Reconsider conditions: May remain in history/ledgers during transition.. Related workstream: WORKSTREAM-03. Label: FACT.

### REJECTED-03 — Discarding old tools/docs/tests during AIDE transition

Status: rejected. It was rejected/superseded because User explicitly wants recycling. Finality: final. Reconsider conditions: Only drop after classification and evidence.. Related workstream: WORKSTREAM-04. Label: FACT.

### REJECTED-04 — Perfect structure that never changes

Status: superseded. It was rejected/superseded because Unrealistic; better target is stable top-level roots plus cheap internal refactors. Finality: final as framing. Reconsider conditions: N/A.. Related workstream: WORKSTREAM-01. Label: INFERENCE.

### REJECTED-05 — Using paths as identity

Status: rejected. It was rejected/superseded because Makes moves/refactors break artifacts. Finality: final as doctrine. Reconsider conditions: N/A.. Related workstream: WORKSTREAM-05. Label: INFERENCE.

### REJECTED-06 — Stabilizing every internal interface forever

Status: deprioritized. It was rejected/superseded because Too costly; stabilize public seams and let internals evolve. Finality: tentative but strong. Reconsider conditions: Revisit per API if external dependents emerge.. Related workstream: WORKSTREAM-06. Label: INFERENCE.

### REJECTED-07 — Component IDs based on legacy/modern/compat/universal or version-coded names

Status: rejected direction. It was rejected/superseded because Creates naming debt and mixes axes. Finality: strong. Reconsider conditions: Use only as status/version fields where needed.. Related workstream: WORKSTREAM-07. Label: FACT/INFERENCE.

## 7. Important Reasoning, Rationale, and Tradeoffs

The visible rationale centered on avoiding architectural lock-in and path fragility. A neat folder tree alone does not make code reusable or portable. The durable solution requires contracts, manifests, APIs, build targets, validators, and AIDE-managed refactor machinery. The main tradeoff is between rigidity and flexibility: if every internal interface is frozen, the project becomes hard to evolve; if no seam is stable, future games, tools, saves, packs, and integrations cannot rely on anything. The proposed answer is to stabilize public seams and durable data formats, while allowing internals to change behind tests, migrations, and compatibility policies.

A second tradeoff is between immediate cleanup and preserving working checks. The user rejected throwing away old tools. The better path is wrap-before-rename: inventory existing tools, call them through AIDE, classify them, then migrate names and paths after their value is preserved. Another tradeoff is naming clarity versus historical continuity. Names like XStack or AuditX may be useful as migration history but should not become long-term product architecture.

The project’s portability goal creates specific constraints: deterministic engine code must avoid hidden OS calls, unnamed randomness, wall-clock dependence, filesystem-order dependence, unversioned binary formats, and public implementation structs. Runtime should adapt the host; engine/game truth should remain host-independent. The user’s deeper concern is not just this refactor, but preventing future architectural debt from accumulating unseen.

## 8. Plans, Future Work, and Next Steps

The recommended path is to implement AIDE-backed architecture contracts before moving large amounts of code. The highest-value next tasks are: verify live repo state; create the repo constitution/refactorability framework; create the modularity and reuse constitution; inventory and wrap old XStack-style tooling; define logical-root projection contracts; add non-blocking boundary validators; and only then perform ownership extraction waves.

Recommended next-action sequence:

1. **TASK-09** — Verify live repo baseline: current branch, root inventory, validators, CTest status, generated artifacts.
2. **TASK-01** — Implement AIDE-STRUCTURE-00: root constitution, ownership slots, AIDE refactor framework, move/salvage map schemas, inventory tooling.
3. **TASK-03** — Inventory old XStack/AuditX/RepoX/TestX-style tools and classify them.
4. **TASK-04** — Wrap old checks behind AIDE without changing behavior.
5. **TASK-02** — Implement AIDE-ARCH-00: modularity/reuse doctrine, dependency layers, C89 ABI rules, API stability levels, boundary checker.
6. **TASK-05** — Define distribution/install/media/bundle projection contracts.
7. **TASK-06/TASK-07/TASK-08** — Add boundary validators, component manifests, and portability/determinism proof checks.
8. Use AIDE work units for actual cleanup, with move maps, salvage maps, validators, evidence, and shim retirement.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user wants human-readable explanation first, not only machine-readable artifacts. The user wants broad/deep reasoning and does not want to repeat restructuring pain. The user explicitly wants portable, modular, extensible, reusable code, and wants AIDE adoption plus recycling of existing code/docs/tests.

### 9.2 Inferred Constraints and Preferences

The user prefers source-grounded, audit-ready decisions; bounded uncertainty; explicit task prompts; and reusable engineering doctrine. Future assistants should avoid shallow affirmation and should distinguish accepted user decisions from assistant recommendations.

### 9.3 Uncertain or Unestablished Preferences

It is not yet established which specific compatibility promises the user wants to make for each API, save format, protocol, or package format. It is also not established how much generated output should be tracked in the repo. These need future decisions after repo verification.

## 10. Files, Artifacts, Outputs, and Prompts

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Pasted text.txt | uploaded prompt | Defines required preservation package structure and rules. | available in this chat | user upload | yes | Must be treated as active instruction for this turn. | FACT |
| ARTIFACT-02 | Prior distribution/install layout analysis pasted by user | pasted assistant output | Provided logical-root projection doctrine and layout examples. | visible in chat, not independently verified | user-pasted text | yes | Use as chat content; repo/doc claims need verification. | FACT/UNCERTAIN |
| ARTIFACT-03 | Prior convergence/root cleanup analysis pasted by user | pasted assistant output | Provided staged repo convergence and root allowlist plan. | visible in chat, not independently verified | user-pasted text | yes | Some specific live repo claims are unverified. | FACT/UNCERTAIN |
| ARTIFACT-04 | Prior component naming/matrix analysis pasted by user | pasted assistant output | Defined clean component naming doctrine. | visible in chat | user-pasted text | yes | Should inform spec-book naming/matrix chapter. | FACT |
| ARTIFACT-05 | AIDE transition prompt/task proposal | assistant-generated prompt | Suggested AIDE-00 bootstrap and recycling plan. | visible in chat | assistant response | yes, with user review | Prompt is recommendation, not executed. | INFERENCE |
| ARTIFACT-06 | AIDE-STRUCTURE-00 prompt | assistant-generated prompt | Defines repo constitution/refactorability framework task. | visible in chat | assistant response | yes | Candidate next Codex/AIDE task. | INFERENCE |
| ARTIFACT-07 | AIDE-ARCH-00 prompt | assistant-generated prompt | Defines modularity and reuse constitution task. | visible in chat | assistant response | yes | Candidate next Codex/AIDE task. | INFERENCE |
| ARTIFACT-08 | This preservation package | generated files + ZIP | Preserves this chat for reading, handoff, aggregation, and future spec-book work. | created in this turn | assistant generated | yes | Contains report, registers, context packet, spec sheet, aggregator packet, audit, reader brief. | FACT |

Important caveat: the only current uploaded file available for this task is `Pasted text.txt`, which contains the preservation-package prompt. Earlier generated handoff files, ZIP packages, or uploaded docs referenced in prior conversation are not available in this chat unless the user re-uploads them.

## 11. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | What is the current live repo state and which of the pasted commit/status claims remain true? | Implementation depends on baseline accuracy. | Pasted text asserted specific repo status and failures. | Live branch, CTest, validators, current root inventory. | Inspect repo with GitHub/Codex and produce baseline report. | P0 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-02 | What exact parts of old XStack/AuditX/RepoX/TestX tooling are useful? | Recycling requires classification. | User wants recycling, not ignoring. | Actual file contents and usefulness. | AIDE inventory with keep/adapt/extract/convert/archive/drop. | P0 | WORKSTREAM-04 | FACT/UNCERTAIN |
| QUESTION-03 | Which APIs deserve stable/frozen compatibility promises? | Over-stabilizing internals is costly; under-stabilizing public seams breaks reuse. | Candidate seams include C ABI, schemas, commands, saves, packages, protocols. | Actual implementation maturity and external use cases. | Define stability levels and public API declarations. | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-04 | Where should domino-engine reusable code stop and Dominium-specific game code begin? | Determines reuse for future games. | Final answer proposed reuse levels. | Actual current code ownership. | Inventory modules and classify reuse level. | P0 | WORKSTREAM-05 | INFERENCE |
| QUESTION-05 | What generated artifacts are intentionally tracked versus accidental? | Generated-output policy affects cleanup. | Pasted text references dist/artifacts and generated outputs. | Actual repository policy and files. | Generated artifact audit. | P1 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-06 | What should become formal Project Spec Book requirements versus background context? | Avoid prematurely hardening brainstorms. | This chat proposes many doctrines. | User confirmation and cross-chat consistency. | Aggregator review. | P1 | WORKSTREAM-09 | INFERENCE |

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats assistant recommendations as user decisions. | Spec book hardens tentative ideas incorrectly. | medium | high | Keep labels and require user confirmation for major implementation commitments. | WORKSTREAM-09 | FACT |
| RISK-02 | Live repo claims from pasted text are stale or wrong. | Codex tasks may target wrong blockers or paths. | medium | high | Verify repo state before implementation. | WORKSTREAM-01 | UNCERTAIN |
| RISK-03 | AIDE becomes another mythology instead of a control plane. | Product architecture polluted by workflow names. | medium | medium-high | Keep AIDE under `.aide/`, `tools/aide/`, docs/aide; do not name runtime/game concepts after it. | WORKSTREAM-03 | INFERENCE |
| RISK-04 | Old validators are renamed before being wrapped. | Regression detection lost. | medium | high | Wrap before rename; preserve behavior first. | WORKSTREAM-04 | INFERENCE |
| RISK-05 | Root constitution becomes too rigid. | Useful evolution blocked. | low-medium | medium | Allow root admission test with high bar and validator update. | WORKSTREAM-01 | INFERENCE |
| RISK-06 | Compatibility promises are too broad. | Maintenance burden and slow evolution. | medium | medium-high | Define stability levels; stabilize only public seams. | WORKSTREAM-06 | INFERENCE |
| RISK-07 | Reusable code remains tangled with Dominium-specific game rules. | Future games/projects cannot reuse the engine cleanly. | medium-high | high | Classify modules by reuse level and enforce dependencies. | WORKSTREAM-05 | FACT/INFERENCE |
| RISK-08 | Generated artifacts leak into source roots. | Repo becomes hard to reason about and refactor. | medium | medium | Generated-output policy and validator. | WORKSTREAM-01 | INFERENCE |

The most serious risk is that a future assistant treats this chat as if it verified the live repo. It did not. The second serious risk is that it hardens every assistant suggestion into a requirement. Several items are strong recommendations aligned with user goals, but still require implementation review. Future chats must preserve labels and verify stale facts.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat contributes the architecture constitution layer: stable source layout, logical-root projection, AIDE governance, product-line reuse, modular engine/runtime/game separation, API/ABI/schema/protocol discipline, naming doctrine, generated-output policy, and refactorability workflow. It should feed future chapters on repo architecture, AIDE operations, engine modularity, distribution/install layout, API stability, portability, determinism, testing, and compatibility. It overlaps with other Dominium architecture chats and may conflict if earlier chats used different root names, older XStack terminology, or more specific platform/render priorities.

## 14. What I Should Remember

- The goal is not a perfect layout that never changes. The goal is stable top-level ownership plus mechanical, reversible internal refactors.
- AIDE should become the refactor/control plane now, not after all old XStack-style tooling is magically cleaned up.
- Existing tools/docs/tests should be inventoried and recycled, not discarded.
- Paths are not identity. Contracts, manifests, IDs, versions, hashes, and capabilities define identity.
- Dominium should be designed as a product-line architecture: reusable across products, future games on the same engine, and some unrelated engine projects where possible.
- `game/` should contain Dominium-specific truth. Reusable engine/runtime/tooling/contracts should not be trapped there.
- Stable C-style ABI seams are useful for durability, but internal implementation should remain flexible.
- Future assistants must verify live repo state before implementing cleanup.
- The best next action is AIDE-STRUCTURE-00 plus live repo baseline verification.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat

- Explain the difference between source layout, install layout, package layout, and AIDE refactor layout.
- Summarize the single most important architecture doctrine from this chat.

### 15.2 Decisions

- Which decisions in this chat were clearly accepted by me, and which are still assistant recommendations?
- Which compatibility promises should be made stable first?

### 15.3 Tasks and Next Actions

- Turn AIDE-STRUCTURE-00 into a Codex-ready implementation prompt.
- Turn AIDE-ARCH-00 into a shorter first-pass task that cannot break the build.

### 15.4 Artifacts and Files

- Extract the generated prompts from this report into a standalone implementation queue.
- Create a shorter checklist from the artifact ledger.

### 15.5 Risks and Verification

- What live repo facts must be verified before running Codex?
- Which pasted repo-status claims are most likely stale?

### 15.6 Future Spec Book / Aggregation

- Convert this chat into formal requirements for the master Project Spec Book.
- Compare this chat against another Dominium architecture report and identify conflicts.

### 15.7 Deep-Dive Questions Specific to This Chat

- Define a reusable engine/module boundary model for Dominium.
- Design the exact `contracts/repo/root_constitution.toml` schema.
- Design the exact AIDE move-map and salvage-map schema.

## 16. Compact Human Summary

This chat was about preventing Dominium from becoming a one-off, fragile game repository. The user wanted a structure and engineering doctrine strong enough for a proper long-lived game or OS-like project: portable, modular, extensible, reusable, backwards-compatible where appropriate, and easy to refactor in the future. The conversation began from earlier architecture outputs about repository layout, distribution/install layouts, package formats, runtime roots, component matrices, and root cleanup. The initial answer was that Dominium needs more than one folder tree: it needs a logical-root projection system. Source repo layout, build output, packages, portable installs, installed layouts, media, saves, instances, bundles, diagnostics, cache, staging, rollback, symbols, and provenance should all be governed by shared contracts rather than invented separately.

The source repo target stabilized around a small constitutional root set: `.aide/`, `.github/`, `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, and generated `dist/` only under strict policy. The user’s concern was not simply aesthetic clutter; it was future portability and refactorability. The answer was that root sprawl should be refused by default and new top-level roots should pass a strict admission test.

A major correction came when the user objected to XStack/AuditX/RepoX/TestX-style framing. The user wanted AIDE adopted quickly and existing code/docs/tests recycled rather than ignored. This shifted the plan: AIDE should become the restructuring control plane now. Existing old tools should be inventoried, wrapped, classified, adapted, renamed, or archived through AIDE. They should not be deleted blindly, and their temporary names should not leak into durable Dominium architecture.

The deepest part of the chat reframed Dominium as product-line architecture. Code should be separated by reuse level: reusable across Dominium products, reusable across future games on the same domino/Dominium engine, and reusable across unrelated projects. This implies a strict split: `contracts/` for stable seams and identity; `engine/` for reusable deterministic substrate and domino engine; `game/` for Dominium-specific rules; `runtime/` for host/platform/render/audio/input/network/storage/UI adaptation; `apps/` for thin entrypoints; `content/` for authored data; `release/` for recipes; `tools/` and `.aide/` for validation and refactor machinery.

The most important doctrine is that paths are not identity. Durable things need IDs, versions, schemas, manifests, hashes, capabilities, compatibility ranges, and migration/refusal policy. Public APIs need stability levels. Stable C89-compatible ABI seams are useful, using opaque handles, explicit allocators, versioned structs, and stable error codes, but internals should remain flexible. Schemas and protocols need version negotiation and capability negotiation. Tests should be deterministic and hermetic. Generated outputs should be quarantined. Future refactors should run through AIDE inventory, move maps, salvage maps, reference rewriting, validators, build/test proof, evidence ledgers, and shim retirement.

The best next action is to verify live repo state, then implement AIDE-STRUCTURE-00 and AIDE-ARCH-00 as non-invasive control-plane and architecture-constitution tasks. Do not start broad moves until contracts and inventories exist. Do not trust pasted repo-status claims without verification. Do not treat every assistant recommendation here as an accepted decision. Preserve the uncertainty labels when merging this chat into the future Project Spec Book.
