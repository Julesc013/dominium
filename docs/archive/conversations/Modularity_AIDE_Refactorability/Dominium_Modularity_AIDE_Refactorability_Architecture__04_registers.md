# STRUCTURED REGISTERS — Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Stable repo constitution | Define stable top-level ownership roots and refuse future root sprawl. | Conceptually defined in chat; needs implementation. | Contracts, docs, validators, and root admission policy exist and are enforced. | active | P0 | high | FACT/INFERENCE |
| WORKSTREAM-02 | Distribution and install projection | Unify package, portable, installed, media, cache, rollback, bundle, save, and diagnostics layouts through logical roots. | Strongly described in pasted prior analysis; not verified against live repo. | One logical-root projection contract drives all physical layouts. | active | P0 | medium | FACT/UNCERTAIN |
| WORKSTREAM-03 | AIDE control plane | Use AIDE for migration, validation, evidence, queues, move maps, salvage maps, and refactor history. | User explicitly preferred AIDE over XStack-style framing. | AIDE owns restructuring workflow; old tools are wrapped and recycled. | active | P0 | high | FACT |
| WORKSTREAM-04 | Old tool/code/doc recycling | Inventory and classify XStack/AuditX/RepoX/TestX-style material instead of discarding it. | Conceptual plan only. | Useful assets kept/adapted/extracted/converted; bad names retired. | active | P1 | high | FACT/INFERENCE |
| WORKSTREAM-05 | Reusable engine/product-line architecture | Separate code by reuse level across Dominium products, future games, and unrelated engine projects. | Outlined in final architecture response. | Reusable layers isolated from Dominium-specific game rules. | active | P0 | high | FACT/INFERENCE |
| WORKSTREAM-06 | Contracts/API/ABI/schema/protocol discipline | Make public seams versioned, stable where promised, and negotiable. | Outlined as doctrine; implementation pending. | Contracts define identity and compatibility; public ABI seams are durable. | active | P0 | high | INFERENCE |
| WORKSTREAM-07 | Naming and matrix cleanup | Use clean component names with version/status/format fields separated. | Discussed in pasted component-naming analysis. | No durable names like legacy/modern/compat/XStack/gl2/vk1/dx11-as-primary. | active | P1 | medium | FACT/INFERENCE |
| WORKSTREAM-08 | Determinism, testing, and proof matrix | Create deterministic, hermetic, replayable proof systems for engine, packages, saves, protocols, and renderers. | Discussed as best practice. | Refactors and releases have reproducible proof outputs. | active | P1 | medium | INFERENCE |
| WORKSTREAM-09 | Spec-book aggregation | Preserve this chat for later merging into a master Project Spec Book. | Activated by uploaded prompt. | Human report, registers, YAML spec, aggregator packet, and ZIP exist. | active | P0 | high | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use a stable top-level root constitution rather than ad hoc root growth. | accepted direction | Repeated user concern about avoiding future restructure; assistant proposals align. | Prevents root sprawl and preserves ownership clarity. | Future roots require admission tests and validators. | WORKSTREAM-01 | high | FACT/INFERENCE |
| DECISION-02 | Treat AIDE as the restructuring control plane. | accepted by user framing | User explicitly said to transition to AIDE ASAP and recycle existing material. | AIDE provides queue, evidence, move-map, and salvage discipline. | Old XStack-style tools become transitional assets. | WORKSTREAM-03 | high | FACT |
| DECISION-03 | Recycle old tools/docs/tests rather than ignore or discard them. | accepted direction | User explicitly said there is code and docs to recycle. | Prevents loss of useful validators and policies. | Requires classification: keep/adapt/extract/convert/archive/drop. | WORKSTREAM-04 | high | FACT |
| DECISION-04 | Paths are not identity; contracts and manifests define identity. | strong recommendation | Repeated in final architecture answer. | Makes directories replaceable and data portable. | Packs, saves, schemas, modules, and packages need IDs, versions, hashes, capabilities. | WORKSTREAM-05 | high | INFERENCE |
| DECISION-05 | Design Dominium as a product-line architecture, not a one-off game. | accepted objective | User explicitly requested proper game/OS-like architecture and reusable code. | Supports reuse across products, games, and projects. | Requires stricter separation of engine/game/runtime/contracts/tools/content. | WORKSTREAM-05 | high | FACT |
| DECISION-06 | Use C89-compatible stable ABI seams, without forcing all internals to be C89. | recommendation | Assistant proposed this refinement. | Stable external seams with flexible implementation. | Public headers need opaque handles, allocators, versioned structs, error codes. | WORKSTREAM-06 | medium | INFERENCE |
| DECISION-07 | Avoid durable architecture names based on temporary tooling or status labels. | accepted direction | User disliked XStack framing; prior component naming analysis rejected legacy/modern/compat labels. | Prevents temporary migration scaffolding becoming permanent ontology. | Use boring literal names and matrix fields. | WORKSTREAM-07 | high | FACT/INFERENCE |
| DECISION-08 | Future refactors should be AIDE work units with move maps and salvage maps. | recommendation aligned with user goal | User wanted future refactors easy and quick. | Turns restructuring into a mechanical process. | Requires AIDE refactor schemas, ledgers, validators, and temporary aliases. | WORKSTREAM-03 | high | INFERENCE |
| DECISION-09 | Apps should be thin; runtime adapts host; engine/game own truth. | strong recommendation | Repeated in architecture doctrine. | Preserves portability and prevents UI/rendering/platform code owning simulation truth. | Boundary validators needed. | WORKSTREAM-05 | medium-high | INFERENCE |
| DECISION-10 | Do not promise compatibility for every internal interface. | recommendation | Final response emphasized stabilizing correct public seams only. | Avoids maintenance paralysis. | Need stability levels and deprecation policy. | WORKSTREAM-06 | medium | INFERENCE |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Implement AIDE-STRUCTURE-00 / repo constitution and refactorability framework. | P0 | U0 | User/Codex/AIDE | None beyond repo access. | Current repo tree, existing validators, project doctrine. | Root constitution, ownership slots, AIDE refactor framework, non-blocking inventory tooling. | Create committed contracts/docs/tools without moving code. | WORKSTREAM-01 | FACT/INFERENCE |
| TASK-02 | Implement AIDE-ARCH-00 / modularity and reuse constitution. | P0 | U1 | User/Codex/AIDE | AIDE-STRUCTURE-00 helpful first. | Architecture doctrine from this chat. | Dependency layers, API stability levels, C89 ABI rules, modularity docs, boundary checker. | Convert chat doctrine into repo contracts/docs. | WORKSTREAM-05 | FACT/INFERENCE |
| TASK-03 | Inventory existing XStack/AuditX/RepoX/TestX-style tooling and classify it. | P0 | U1 | AIDE/Codex | AIDE inventory scaffolding. | Live repo files, old tool directories. | Tool recycling inventory and transition plan. | Run non-invasive inventory and mark keep/adapt/extract/convert/archive/drop. | WORKSTREAM-04 | FACT |
| TASK-04 | Wrap old checks behind AIDE before renaming them. | P1 | U1 | AIDE/Codex | TASK-03. | Existing validators/tests/build checks. | AIDE task runner adapters. | Expose old checks as AIDE tasks while preserving behavior. | WORKSTREAM-03 | INFERENCE |
| TASK-05 | Define logical-root projection contracts for distribution/install/media/bundles. | P0 | U1 | AIDE/Codex | Repo access and current distribution docs. | Existing docs/contracts if present. | Machine-readable distribution layout contract and docs. | Write contract first; validators non-blocking. | WORKSTREAM-02 | INFERENCE |
| TASK-06 | Add boundary validators for apps/engine/game/runtime/contracts/content/tools. | P1 | U2 | AIDE/Codex | Dependency layer contract. | Build graph, include paths, manifests. | Report-only checker, later strict gate. | Start with detection only. | WORKSTREAM-06 | INFERENCE |
| TASK-07 | Create component/module manifest pattern. | P1 | U2 | AIDE/Codex | Stable naming and dependency rules. | Candidate modules and targets. | Module manifests with owner, provides, requires, stability, forbidden dependencies, tests. | Pilot on one renderer and one engine module. | WORKSTREAM-07 | INFERENCE |
| TASK-08 | Define portability threat checks. | P1 | U2 | AIDE/Codex | Architecture doctrine. | Compiler/platform/test matrix. | Checklist or validator for endian, width, locale, filesystem order, RNG, wall clock, FP determinism. | Add to docs and proof matrix. | WORKSTREAM-08 | INFERENCE |
| TASK-09 | Verify live repo status before executing any concrete cleanup. | P0 | U0 | User/Codex | Repo access. | Current branch, commits, CTest output, validators. | Verified baseline report. | Do not rely on pasted commit/status claims without verification. | WORKSTREAM-01 | UNCERTAIN |
| TASK-10 | Merge this package into future master Project Spec Book. | P1 | U2 | Aggregator chat/user | Other old-chat reports. | This report and ZIP. | Spec-book chapters and formal requirements candidates. | Use aggregator packet. | WORKSTREAM-09 | FACT |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Source scope is this chat only unless Project-context is explicitly labelled. | reporting | hard | Uploaded preservation prompt. | Do not merge external memories silently. | High if a future assistant overgeneralizes. | high | FACT |
| CONSTRAINT-02 | Do not treat assistant suggestions as user decisions unless accepted. | epistemic | hard | Uploaded preservation prompt. | Decision register must distinguish recommendations from accepted decisions. | High. | high | FACT |
| CONSTRAINT-03 | Future architecture should avoid root sprawl. | architecture | hard-ish | User wants to avoid repeat restructuring. | New roots refused by default. | High if no validator exists. | high | FACT/INFERENCE |
| CONSTRAINT-04 | Existing code/docs/tests should be recycled rather than ignored. | migration | hard | User explicitly stated this. | Use classification before delete/archive. | High if cleanup becomes destructive. | high | FACT |
| CONSTRAINT-05 | AIDE names must not contaminate product/runtime/game architecture. | architecture | soft-to-hard | Assistant recommendation based on user rejection of XStack framing. | AIDE remains control plane; Dominium architecture remains separate. | Medium. | medium-high | INFERENCE |
| CONSTRAINT-06 | Portability and modularity are primary design goals. | technical | hard | User explicitly stated this is very important. | Avoid hidden OS calls, hardcoded paths, unstable ABI leakage. | High. | high | FACT |
| CONSTRAINT-07 | Durable data and protocols need versioning and migration/refusal policy. | compatibility | hard-ish | Architecture doctrine. | No silent save/package/schema migration. | High. | medium-high | INFERENCE |
| CONSTRAINT-08 | Generated outputs must be quarantined. | repo hygiene | hard-ish | Repeated assistant recommendation. | Generated files go to dist/build/.aide.local or canonical fixture/archive only. | Medium. | medium | INFERENCE |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Direct, human-readable explanations first; machine-readable registers second. | output style | explicit | strong | Do not answer with only YAML or manifests. | High. | FACT |
| PREF-02 | Broad and deep architectural reasoning, not shallow folder advice. | analysis depth | explicit | strong | Explain principles, tradeoffs, big-project practices, and missing issues. | High. | FACT |
| PREF-03 | Preserve uncertainty and distinguish facts from inferences. | epistemic | explicit | strong | Use labels and do not overstate repo facts. | High. | FACT |
| PREF-04 | Avoid repeating previously rejected XStack-style ontology as durable architecture. | naming/architecture | explicit | strong | Use AIDE/control-plane vocabulary and boring project names. | Medium-high. | FACT |
| PREF-05 | Future work should be executable by Codex/AIDE with clear tasks. | workflow | inferred | strong | Provide prompts/tasks and validation outputs. | Medium. | INFERENCE |
| PREF-06 | Code should be reusable across games and projects, not one-off. | technical direction | explicit | strong | Design APIs, modules, data, tests, and directories as platform architecture. | High. | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | What is the current live repo state and which of the pasted commit/status claims remain true? | Implementation depends on baseline accuracy. | Pasted text asserted specific repo status and failures. | Live branch, CTest, validators, current root inventory. | Inspect repo with GitHub/Codex and produce baseline report. | P0 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-02 | What exact parts of old XStack/AuditX/RepoX/TestX tooling are useful? | Recycling requires classification. | User wants recycling, not ignoring. | Actual file contents and usefulness. | AIDE inventory with keep/adapt/extract/convert/archive/drop. | P0 | WORKSTREAM-04 | FACT/UNCERTAIN |
| QUESTION-03 | Which APIs deserve stable/frozen compatibility promises? | Over-stabilizing internals is costly; under-stabilizing public seams breaks reuse. | Candidate seams include C ABI, schemas, commands, saves, packages, protocols. | Actual implementation maturity and external use cases. | Define stability levels and public API declarations. | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-04 | Where should domino-engine reusable code stop and Dominium-specific game code begin? | Determines reuse for future games. | Final answer proposed reuse levels. | Actual current code ownership. | Inventory modules and classify reuse level. | P0 | WORKSTREAM-05 | INFERENCE |
| QUESTION-05 | What generated artifacts are intentionally tracked versus accidental? | Generated-output policy affects cleanup. | Pasted text references dist/artifacts and generated outputs. | Actual repository policy and files. | Generated artifact audit. | P1 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-06 | What should become formal Project Spec Book requirements versus background context? | Avoid prematurely hardening brainstorms. | This chat proposes many doctrines. | User confirmation and cross-chat consistency. | Aggregator review. | P1 | WORKSTREAM-09 | INFERENCE |

## 23. Artifact Ledger

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

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Visual drag-and-drop cleanup of root folders | rejected | Would break paths, build, tests, package identity, and authority semantics. | final unless repo becomes trivial | Only reconsider for tiny isolated folders with move map and proof. | WORKSTREAM-01 | FACT/INFERENCE |
| REJECTED-02 | XStack/AuditX/RepoX/TestX as durable architecture ontology | rejected/superseded | User disliked it; names are temporary scaffolding. | mostly final | May remain in history/ledgers during transition. | WORKSTREAM-03 | FACT |
| REJECTED-03 | Discarding old tools/docs/tests during AIDE transition | rejected | User explicitly wants recycling. | final | Only drop after classification and evidence. | WORKSTREAM-04 | FACT |
| REJECTED-04 | Perfect structure that never changes | superseded | Unrealistic; better target is stable top-level roots plus cheap internal refactors. | final as framing | N/A. | WORKSTREAM-01 | INFERENCE |
| REJECTED-05 | Using paths as identity | rejected | Makes moves/refactors break artifacts. | final as doctrine | N/A. | WORKSTREAM-05 | INFERENCE |
| REJECTED-06 | Stabilizing every internal interface forever | deprioritized | Too costly; stabilize public seams and let internals evolve. | tentative but strong | Revisit per API if external dependents emerge. | WORKSTREAM-06 | INFERENCE |
| REJECTED-07 | Component IDs based on legacy/modern/compat/universal or version-coded names | rejected direction | Creates naming debt and mixes axes. | strong | Use only as status/version fields where needed. | WORKSTREAM-07 | FACT/INFERENCE |

## 25. Risk Register

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

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current live repo head, branch, validator status, and CTest status. | Pasted status may be stale/unverified. | GitHub/Codex live repo inspection. | P0 | WORKSTREAM-01 | UNCERTAIN |
| VERIFY-02 | Existence and contents of docs referenced in pasted analyses, such as VIRTUAL_PATHS, INSTALL_MODEL, DIST_TREE_CONTRACT, PKG_FORMAT. | They underpin distribution recommendations. | Live repo or uploaded docs snapshot. | P0 | WORKSTREAM-02 | UNCERTAIN |
| VERIFY-03 | Actual XStack/AuditX/RepoX/TestX paths and behavior. | Recycling plan depends on contents. | Repo inventory and test runs. | P0 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-04 | Current component matrix names and statuses. | Naming cleanup should target actual files. | Repo search. | P1 | WORKSTREAM-07 | UNCERTAIN |
| VERIFY-05 | External best-practice references used in prior answer. | Could be stale or context-dependent. | Official docs for CMake, Bazel, Chromium, Linux, SemVer, Google Testing. | P2 | WORKSTREAM-05 | UNCERTAIN |
| VERIFY-06 | Which prior generated files or old uploads are unavailable/expired. | Artifact ledger completeness depends on availability. | Conversation file list / user re-upload. | P1 | WORKSTREAM-09 | UNCERTAIN |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | User pasted prior distribution/install layout analysis. | Established need for multiple physical layouts unified by virtual roots. | Shifted beyond source folder cleanup. | Foundational for layout projection. | high |
| 2 | User pasted prior repo convergence analysis. | Framed root clutter as ownership and enforcement problem. | Suggested stable source layout and validators. | Feeds root constitution. | high for chat content; medium for live repo claims |
| 3 | User pasted prior component naming analysis. | Rejected version/status/era-coded component IDs. | Supports modular renderer/platform/package architecture. | Feeds matrix cleanup. | high |
| 4 | Assistant strengthened plan with contracts, projection model, evidence levels, refusal codes, proof path. | Moved from folders to contract-driven architecture. | Became core doctrine. | high |
| 5 | User rejected XStack-style framing and asked for AIDE transition and recycling. | Changed strategy from old-tool-first to AIDE-control-plane-first. | Central correction. | high |
| 6 | Assistant proposed AIDE bootstrap, recycling inventory, wrap-before-rename, salvage maps. | Established AIDE as refactor OS. | Candidate next action. | high |
| 7 | User asked how to avoid future headaches. | Goal became stable roots plus cheap future refactors, not perfect immutability. | Led to AIDE-STRUCTURE-00. | high |
| 8 | User asked broad/deep portability/modularity/reuse question. | Expanded scope to proper game/OS-like architecture and product-line reuse. | Led to AIDE-ARCH-00 and detailed engineering practices. | high |
| 9 | User uploaded preservation-package prompt. | Converted chat into report/export task. | This output fulfills that request. | high |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Repo Architecture | Stable root constitution, forbidden roots, ownership slots, root admission policy. | DECISION-01, WORKSTREAM-01 | requirement | high | Must verify live repo before applying. |
| AIDE Governance | AIDE as control plane for refactors, evidence, queues, move/salvage maps. | DECISION-02, WORKSTREAM-03 | requirement/context | high | Do not let AIDE names enter product architecture. |
| Modular Engine Architecture | Reuse levels across products/games/projects; engine/game/runtime/contracts separation. | DECISION-05, WORKSTREAM-05 | requirement | high | Needs module inventory. |
| Distribution/Install Layout | Logical-root projection model for packages, installs, media, bundles, cache, rollback. | WORKSTREAM-02 | requirement/open issue | medium | Repo docs need verification. |
| API/ABI/Schemas/Protocols | Versioned public seams, C ABI rules, stability levels, capability negotiation. | WORKSTREAM-06 | requirement | medium-high | Requires design review per API. |
| Testing and Determinism | Hermetic, deterministic proof matrix; save/replay/package/schema tests. | WORKSTREAM-08 | requirement | medium | Specific test implementation still open. |
| Naming Doctrine | Boring component names; versions/status in fields; retire XStack-style names. | WORKSTREAM-07 | requirement/context | high | Needs current matrix audit. |
