# STRUCTURED REGISTERS — Domino/Dominium Portability, Assurance, and Future-Proof Architecture

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Standards-informed assurance profile | Define a Domino/Dominium Assurance Profile that borrows useful assurance ideas without compliance claims. | Assistant proposed DDAP v0 and DIL levels; not yet user-ratified. | Written internal profile with levels, gates, schemas, validators, and adoption rules. | Proposed | P1 | 4 | INFERENCE / assistant recommendation |
| WORKSTREAM-02 | Portable engine platform boundary | Keep Domino reusable across games/projects through stable contracts and replaceable internals. | User explicitly prioritised portability, modularity, extensibility, reuse, and replaceability. | Domino usable without Dominium, with public contracts and no accidental product dependency. | Active concern | P0 | 5 | FACT / INFERENCE |
| WORKSTREAM-03 | Directory/module structure and ownership | Organise repo around ownership, public contracts, private implementation, tests, and replacement criteria. | Assistant proposed a tightened tree and module.toml pattern. | Dependency direction and module ownership are explicit and checked. | Proposed | P1 | 4 | assistant recommendation |
| WORKSTREAM-04 | Persistent data and compatibility | Make saves/packs/replays/protocols/schemas versioned, migratable, and safe. | Assistant proposed TLV/chunk registries, no-ID-reuse, migration tests. | Versioned formats with registries, fixtures, migration tools, validation. | Proposed | P0 | 4 | assistant recommendation |
| WORKSTREAM-05 | Determinism and replay | Make deterministic state transition and replay validation architectural features. | Assistant proposed fixed tick, RNG streams, no OS/time in simulation, replay equality tests. | Replay harness and determinism rules enforced by tests/layers. | Proposed | P1 | 4 | assistant recommendation |
| WORKSTREAM-06 | Conformance, validation, and tooling | Make modularity mechanically testable. | Assistant proposed conformance tests, fuzzing, layer checkers, validators, AIDE/XStack enforcement. | Automated validators for APIs, schemas, layers, release gates, module replacement. | Proposed | P1 | 4 | assistant recommendation / PROJECT-CONTEXT for AIDE |
| WORKSTREAM-07 | Setup, launcher, tools, and UI boundaries | Keep setup/launcher/tools/UI as contract consumers, not privileged engine internals. | Assistant proposed setup transaction flow and semantic command/result UI layer. | Thin surfaces consume same contracts and respect authority rules. | Proposed | P2 | 4 | assistant recommendation |
| WORKSTREAM-08 | Chat preservation and spec-book aggregation | Preserve this chat into human-readable and structured artifacts. | User uploaded preservation prompt requiring report, registers, spec sheet, aggregator packet, audit, files and ZIP. | Downloadable package plus in-chat reader with caveats. | Completed by this response | P0 | 5 | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use standards as design inputs, not literal compliance targets. | Assistant recommendation; not explicitly user-ratified. | User asked whether standards could be used for Domino/Dominium; assistant answered yes, but not as certification/compliance. | Useful assurance patterns should be borrowed; external certification wrappers are misaligned. | Creates DDAP-style internal profile rather than compliance claim. | WORKSTREAM-01 | 4 | INFERENCE / assistant recommendation |
| DECISION-02 | Separate Domino as reusable engine/runtime/toolchain from Dominium as one product built on it. | Assistant recommendation aligned with explicit user goal. | User explicitly wanted reuse for another game and other engine/game projects. | Engine/product separation prevents product assumptions contaminating reusable code. | Domino should not depend on Dominium; Dominium consumes public contracts. | WORKSTREAM-02 | 5 | FACT goal + INFERENCE architecture |
| DECISION-03 | Stable public contracts, replaceable internals. | Assistant recommendation; not separately accepted after answer. | Assistant framed this as the core doctrine. | Preserves compatibility while allowing deep refactors. | Public headers/formats/protocols/tests stable; algorithms/private modules replaceable. | WORKSTREAM-02 | 4 | assistant recommendation |
| DECISION-04 | Do not make every internal function/header stable. | Assistant recommendation. | Assistant warned against making all internal headers public or stable. | Freezing internals creates accidental compatibility burdens. | Need explicit public/private split and lifecycle labels. | WORKSTREAM-02 | 4 | assistant recommendation |
| DECISION-05 | Use internal DIL-0 through DIL-5 levels for assurance gates. | Assistant recommendation; not user-confirmed. | Assistant proposed levels for experiments through external-impacting systems. | Applies rigor only where trust/persistence/authority/external impact exists. | DIL-3+ receives stronger evidence/tests/review; UI/content stays lighter. | WORKSTREAM-01 | 4 | assistant recommendation |
| DECISION-06 | Prioritise assurance for saves, packs, replay, authority, updater/installer, multiplayer, and mod trust. | Assistant recommendation. | Assistant identified highest-value targets. | Failures here can corrupt data, break compatibility, or undermine trust/security. | These paths need versioning, validation, negative tests, review gates, audit evidence. | WORKSTREAM-04 / WORKSTREAM-06 | 4 | assistant recommendation |
| DECISION-07 | Use conformance tests as proof of replaceability. | Assistant recommendation. | Assistant stated stable interface without conformance suite is only a promise. | Replacement must be objectively testable. | tests/conformance becomes first-class repo area. | WORKSTREAM-06 | 4 | assistant recommendation |
| DECISION-08 | Treat data evolution as seriously as code evolution. | Assistant recommendation. | Assistant emphasized saves/packs/schemas/protocols and no tag reuse. | Long-lived projects often fail through broken data compatibility. | Need registries, fixtures, migration tests, compatibility policy. | WORKSTREAM-04 | 4 | assistant recommendation |
| DECISION-09 | Do not present this package as guaranteed full transcript extraction. | Decision in this package. | Visible context and uploaded prompt are available; hidden transcript/repo are not guaranteed. | Preservation must be honest about source scope. | Safe for aggregation only with caveats. | WORKSTREAM-08 | 5 | FACT / UNCERTAIN scope |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Create DDAP v0 document defining DIL-0 through DIL-5 and adoption rules. | P1 | U1 | Project maintainer / future assistant | User approval; standards verification | Current repo, architecture notes, standards map | docs/assurance/ddap.md or control/assurance/ASSURANCE_PROFILE.md | Draft outline and apply to high-trust subsystems. | WORKSTREAM-01 | assistant recommendation |
| TASK-02 | Define public API/ABI policy for Domino. | P0 | U1 | Project maintainer | Clarify language/toolchain targets | Existing headers, target platforms, plugin requirements | docs/architecture/public-api-policy.md plus include/domino conventions | List current public/private boundaries. | WORKSTREAM-02 | assistant recommendation |
| TASK-03 | Create contracts/registries for stable IDs: error codes, TLV tags, capabilities, opcodes, subsystem IDs. | P0 | U1 | Project maintainer | Initial format decisions | Current save/pack/protocol drafts | contracts/registries/*.toml | Draft registries with reserved ranges/no-reuse. | WORKSTREAM-04 | assistant recommendation |
| TASK-04 | Add conformance test area and first replacement tests. | P1 | U1 | Project maintainer / test harness | At least one public API boundary | API specs, fixtures, golden outputs | tests/conformance/ with executable replacement criteria | Start with pack validator or save reader. | WORKSTREAM-06 | assistant recommendation |
| TASK-05 | Add layer checker / forbidden include checker. | P1 | U1 | Project maintainer / tooling | Layering policy | Directory map and allowed dependencies | scripts/check_layers.py or equivalent CI gate | Encode Domino-must-not-depend-on-Dominium rule. | WORKSTREAM-03 | assistant recommendation |
| TASK-06 | Write data-evolution policy for saves, packs, schemas, protocols, and replays. | P0 | U1 | Project maintainer | Persistent format strategy | Format drafts, versioning constraints | docs/architecture/data-evolution-policy.md | Define no-ID-reuse and migration fixture rules. | WORKSTREAM-04 | assistant recommendation |
| TASK-07 | Build deterministic replay comparison harness. | P1 | U2 | Engine/test maintainer | Simulation reducer and serialization design | Tick model, RNG strategy, canonical state serializer | replay_compare tool and platform equality tests | Define minimal canonical state snapshot. | WORKSTREAM-05 | assistant recommendation |
| TASK-08 | Define module.toml ownership/replacement metadata. | P2 | U2 | Architecture/tooling | Directory structure stabilization | Module list, owners, dependencies, public headers | module.toml schema and examples | Pilot with render.soft or pack validator. | WORKSTREAM-03 | assistant recommendation |
| TASK-09 | Separate setup transaction engine from gameplay and launcher. | P2 | U2 | Setup/installer maintainer | Install layout and release format decisions | Installer/updater goals, rollback model | PLAN→STAGE→VERIFY→COMMIT→RECEIPT→ROLLBACK contract | Draft setup architecture note. | WORKSTREAM-07 | assistant recommendation |
| TASK-10 | Preserve current chat as report package and ZIP. | P0 | U0 | Assistant | Visible chat context and uploaded prompt | Current transcript context, Pasted text.txt prompt | Markdown/YAML files plus ZIP package | Completed in this response. | WORKSTREAM-08 | FACT |
| TASK-11 | Verify external standards and cited practices before formalising spec language. | P1 | U2 | Future assistant / maintainer | Internet/source access | Official standards pages and current docs | Verified standards mapping with citations | Use official sources where possible. | WORKSTREAM-01 | VERIFY |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Source scope for preservation is this chat only unless labelled PROJECT-CONTEXT. | reporting | hard | Uploaded preservation prompt | Do not merge other chat history silently. | Aggregator may treat external memory as current-chat fact. | 5 | FACT |
| CONSTRAINT-02 | Do not invent facts or turn assistant suggestions into user decisions. | epistemic | hard | Uploaded preservation prompt | Mark DDAP and structure recommendations as proposed unless ratified. | Spec book may encode tentative ideas as canonical. | 5 | FACT |
| CONSTRAINT-03 | Domino must not depend on Dominium. | architecture | recommended hard | Assistant recommendation based on user reuse goal | Engine folders/headers/tests/contracts avoid product dependencies. | Engine becomes one-off Dominium code. | 4 | assistant recommendation |
| CONSTRAINT-04 | Dominium should consume Domino through public contracts. | architecture | recommended hard | Assistant recommendation | No private engine internals in product code. | Refactors become unsafe and coupling spreads. | 4 | assistant recommendation |
| CONSTRAINT-05 | Public ABI structs should use size/version/reserved fields and opaque handles. | API/ABI | recommended hard for public ABI | Assistant recommendation | Public C interfaces are evolvable. | Binary/source incompatibility and frozen layouts. | 4 | assistant recommendation |
| CONSTRAINT-06 | No persistent ID/tag/opcode/error code reuse after release. | data compatibility | recommended hard | Assistant recommendation | Maintain registries and reserve deleted IDs. | Silent data corruption and incompatible saves/mods/protocols. | 4 | assistant recommendation |
| CONSTRAINT-07 | Simulation should not directly depend on wall-clock time, OS APIs, UI, renderer, or platform backends. | determinism | recommended hard for authoritative simulation | Assistant recommendation | Use deterministic inputs/host services. | Nondeterministic replay and desync. | 4 | assistant recommendation |
| CONSTRAINT-08 | No generated output becomes trusted without validation. | assurance/security | recommended hard for DIL-3+ | Assistant DDAP/AIDE recommendation | Generated code/schemas/packs/build outputs need validators/review gates. | Unreviewed generated artifacts corrupt trusted state. | 4 | assistant recommendation |
| CONSTRAINT-09 | Human-readable report must remain understandable without downloading files. | reporting | hard | Uploaded preservation prompt | Final answer must include reader guide/file index. | User cannot inspect chat quickly. | 5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Human-readable explanation first, not only machine-readable registers. | reporting | explicit | high | Use prose narrative and explain why decisions/recommendations matter. | User receives another unusable handoff artifact. | FACT |
| PREF-02 | Direct, source-grounded, audit-ready answers with uncertainty labels. | communication | explicit via user profile and preservation prompt | high | Mark FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT and avoid overclaiming. | False certainty reduces usefulness. | FACT / PROJECT-CONTEXT |
| PREF-03 | Broad and deep architectural thinking rather than narrow implementation trivia. | technical guidance | explicit | high | Discuss code, data, tools, APIs, schemas, tests, docs, build systems. | Answer misses user’s main concern. | FACT |
| PREF-04 | Portability, modularity, extensibility, reuse, and replaceability are central values. | architecture | explicit | very high | Prioritize stable contracts, replacement criteria, data compatibility. | Project becomes one-off indie-style codebase. | FACT |
| PREF-05 | Avoid certification cosplay and over-bureaucratizing ordinary gameplay/content. | assurance | inferred | medium | High rigor only for trust-bearing paths. | Project slows down or cargo-cults standards. | INFERENCE |
| PREF-06 | Preserve artifacts and make output usable for future spec-book aggregation. | preservation | explicit | high | Create registers, spec sheet, aggregator packet, audit, ZIP. | Future aggregation loses context. | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Is DDAP v0 accepted as project direction or only a recommendation pending user review? | Determines whether DIL levels become canonical governance. | Assistant recommended DDAP; user has not explicitly accepted it. | User’s final acceptance and desired strictness. | Ask user to approve, revise, or reject DDAP. | P1 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-02 | What is the current actual repo structure? | Directory recommendations were not based on repo inspection. | Only proposed structures and PROJECT-CONTEXT memories are available. | Actual files, build scripts, and current coupling. | Inspect repo or have user provide tree. | P0 | WORKSTREAM-03 | UNCERTAIN |
| QUESTION-03 | Which public boundaries must be stable first? | Stabilizing too much too early freezes bad design; too little undermines portability. | Assistant recommended public headers, formats, protocols, command/result APIs. | Which systems are mature enough to freeze. | Define experimental/stable/deprecated lifecycle policy and boundary list. | P1 | WORKSTREAM-02 | UNCERTAIN |
| QUESTION-04 | How strict should C89/C++98 portability be across all code? | Portability rules depend on toolchains/platforms. | PROJECT-CONTEXT says C89 engine and C++98 shells; current user asked portability but did not restate versions. | Whether all current work enforces this now. | User confirms target platform/toolchain matrix. | P1 | WORKSTREAM-02 | PROJECT-CONTEXT / UNCERTAIN |
| QUESTION-05 | What should be the first pilot module for conformance/replacement testing? | A concrete pilot prevents abstract architecture only. | Assistant suggested pack validator, save reader, or render.soft. | Which module exists and is easiest to isolate. | Choose one module and write module.toml + fixtures + tests. | P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-06 | What exact compatibility promises should be made for saves, packs, mods, and protocols? | Compatibility guarantees define future burden and user trust. | Assistant recommended versioning and no ID reuse. | Support window, migration guarantees, breaking-change process. | Write compatibility policy with tiers. | P0 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-07 | Which external standards claims need verification before formal spec use? | Standards change and some references are high-level/paywalled. | Prior assistant cited several standards and practices. | Current exact wording/applicability. | Verify against official/current sources before normative text. | P2 | WORKSTREAM-01 | VERIFY |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | User-pasted standards/DO-178B/C/Eureka analysis | prompt content | Frame whether standards-inspired assurance could apply to Domino/Dominium. | Referenced; not independently verified here. | User message | Yes, as background and verification input. | Contains external standards claims/links needing verification. | FACT / VERIFY |
| ARTIFACT-02 | Assistant response: DDAP/DIL standards-informed assurance answer | generated chat output | Proposed project-native assurance profile and high-trust paths. | Produced; recommendations not explicitly ratified. | Assistant | Yes, with tentative label. | Includes DIL levels, repo impact, AIDE enforcement, boundary conditions. | assistant recommendation |
| ARTIFACT-03 | User question on portability, modularity, extensibility, replaceability, future-proofing | user instruction / design goal | Defines main architectural concern of the chat. | Explicit user requirement/preference. | User message | Yes, high priority. | Core source for platform doctrine. | FACT |
| ARTIFACT-04 | Assistant response: contract-governed engine platform answer | generated chat output | Proposed stable contracts, replaceable internals, repo tree, naming, schema, determinism, testing. | Produced; recommendations not explicitly ratified. | Assistant | Yes, as architecture draft. | Contains many candidate requirements/tasks. | assistant recommendation |
| ARTIFACT-05 | Pasted text.txt preservation mega-prompt | uploaded file | Instructs assistant to create complete preservation package and ZIP. | Loaded and used. | User upload | Yes, as method/template. | Source for current preservation task. | FACT |
| ARTIFACT-06 | Generated preservation package files | generated files | Preserve this chat in human-readable and machine-aggregatable form. | Created by this response. | Assistant file export | Yes. | Includes manifest, report, context packet, spec sheet, registers, aggregator packet, reader brief, audit, future-chat prompt, in-chat reader, ZIP. | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Claim or pursue DO-178C compliance for Domino/Dominium. | Rejected by assistant recommendation. | Misaligned with game/engine project and implies certification obligations. | Tentative unless external safety-critical use emerges. | Only reconsider for regulated safety-critical external use. | WORKSTREAM-01 | assistant recommendation |
| REJECTED-02 | Apply heavy assurance to every line of code and all gameplay/content/UI. | Rejected/deprioritised by assistant recommendation. | Would slow creative iteration and overburden low-risk work. | Likely final for ordinary content/UI. | Reconsider only if subsystem becomes trust-bearing. | WORKSTREAM-01 | assistant recommendation |
| REJECTED-03 | Freeze all internal APIs/functions for compatibility. | Rejected by assistant recommendation. | Internal stability preserves bad designs and blocks refactoring. | Likely final doctrine. | Only for intentionally public/plugin APIs. | WORKSTREAM-02 | assistant recommendation |
| REJECTED-04 | Use directory structure alone as proof of modularity. | Rejected implicitly. | Folders need contracts, dependencies, tests, replacement criteria. | Likely final doctrine. | None; structure remains necessary but insufficient. | WORKSTREAM-03 | assistant recommendation |
| REJECTED-05 | Persist data by dumping raw C structs. | Rejected by assistant recommendation. | Not portable across compilers/endian/alignment/schema evolution. | Final for long-lived data. | Only for temporary debug snapshots marked nonportable. | WORKSTREAM-04 | assistant recommendation |
| REJECTED-06 | Let setup/launcher/gameplay/tooling freely share privileged internals. | Rejected by assistant recommendation. | Collapses boundaries and makes refactors/security/audits harder. | Likely final. | Internal diagnostic privileged mode only if explicit. | WORKSTREAM-07 | assistant recommendation |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats recommendations as user-approved decisions. | Spec book may encode unratified advice as canon. | Medium | High | Keep status labels; ask user to approve/reject DDAP and target structure. | WORKSTREAM-08 | UNCERTAIN |
| RISK-02 | Architecture becomes certification cosplay. | Paperwork without real assurance; slowed development. | Medium | Medium | Use project-native DIL levels; restrict heavy gates to trust paths. | WORKSTREAM-01 | assistant recommendation |
| RISK-03 | Portability remains aspirational without conformance tests. | Modules cannot actually be replaced; hidden coupling accumulates. | High | High | Create tests/conformance and replacement criteria. | WORKSTREAM-06 | assistant recommendation |
| RISK-04 | Data formats evolve without registries and migration tests. | Old saves/mods/packs/replays break or corrupt silently. | Medium | High | No-ID-reuse, registries, golden fixtures, migration tests. | WORKSTREAM-04 | assistant recommendation |
| RISK-05 | Dominium-specific assumptions leak into Domino. | Domino becomes unreusable. | Medium | High | Layer checker; no Domino->Dominium dependencies. | WORKSTREAM-02 | assistant recommendation |
| RISK-06 | Public API is frozen too early. | Bad early designs become compatibility burdens. | Medium | Medium | Use experimental/stable/deprecated lifecycle labels and promotion reviews. | WORKSTREAM-02 | assistant recommendation |
| RISK-07 | External standards claims become stale/inaccurate. | Spec book cites incorrect/outdated standards framing. | Medium | Medium | Verification queue before normative incorporation. | WORKSTREAM-01 | VERIFY |
| RISK-08 | Preservation package overstates access. | Aggregator assumes complete extraction when only visible context was available. | Medium | Medium | State coverage limitations clearly. | WORKSTREAM-08 | FACT / UNCERTAIN |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current official status/wording of DO-178C family and FAA AC 20-115D. | Prior answer cited regulatory standards; formal spec needs official wording. | FAA, RTCA, EUROCAE official sources. | P2 | WORKSTREAM-01 | VERIFY |
| VERIFY-02 | NIST SSDF, OWASP ASVS, SLSA, SPDX, ISO/IEC references and versions. | Security/supply-chain mappings can change. | NIST CSRC, OWASP, SLSA.dev, SPDX/ISO official sources. | P2 | WORKSTREAM-01 | VERIFY |
| VERIFY-03 | Actual Domino/Dominium repository structure and file names. | Directory recommendations were not based on repo inspection. | Repo tree, GitHub/working copy, build files. | P0 | WORKSTREAM-03 | VERIFY |
| VERIFY-04 | Current language/toolchain/platform targets, including C89/C++98 strictness. | Portability rules depend on targets. | Project README/build config/user confirmation. | P1 | WORKSTREAM-02 | VERIFY |
| VERIFY-05 | Existing persistent data formats/schemas/save/pack/replay/protocol plans. | Compatibility policy must match real formats. | contracts/, docs/, source code, generated artifacts. | P0 | WORKSTREAM-04 | VERIFY |
| VERIFY-06 | Whether other old-chat reports conflict with this chat. | Master spec must merge without contradictions. | Other preservation packages and aggregator. | P1 | WORKSTREAM-08 | VERIFY |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | User pasted standards analysis about Eureka/DO-178B/C and related standards. | Set up question: can similar standards help Domino/Dominium? | Moved assurance standards into project architecture discussion. | Basis for DDAP recommendation. | 5 |
| 02 | User asked if using/following these standards for Domino/Dominium is wise. | Assistant reframed as architecture decision, not certification. | Avoided accidental compliance/certification framing. | DDAP remains standards-inspired, not compliance-claiming. | 5 |
| 03 | Assistant proposed DDAP v0 and DIL levels. | Project-native assurance profile proposed. | Allows selective rigor for high-trust paths. | Candidate governance workstream. | 4 |
| 04 | User broadened to portability/modularity/extensibility/reuse/future-proofing. | Problem expanded from assurance to whole-engine platform architecture. | Became main substance of chat. | Core source for engine-platform doctrine. | 5 |
| 05 | Assistant proposed stable outside/replaceable inside and concrete practices. | Detailed architecture draft emerged. | Provides candidate requirements for future spec book. | Main carry-forward architecture content. | 4 |
| 06 | User uploaded Pasted text.txt preservation mega-prompt. | Task switched to preservation/export. | This response creates bridge from chat to docs. | Defines export package. | 5 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Architecture Doctrine | Contract-governed engine platform; stable external contracts with replaceable internals. | DECISION-02, DECISION-03, WORKSTREAM-02 | Requirement candidate after user approval | 4 | Must not imply all internals are stable. |
| Assurance and Governance | DDAP v0, DIL levels, high-trust path gates. | DECISION-01, DECISION-05, WORKSTREAM-01 | Open issue / requirement candidate | 4 | Needs user ratification and standards verification. |
| Repository Structure | Ownership-based tree with include/, contracts/, source/domino, source/dominium, tests/conformance, tools/validators. | WORKSTREAM-03, TASK-05, TASK-08 | Open issue until repo inspected | 3 | Proposed target tree, not verified against actual repo. |
| API/ABI Policy | Opaque handles, size/version structs, no C++ ABI at plugin boundary, lifecycle labels. | DECISION-03, CONSTRAINT-05, TASK-02 | Requirement candidate | 4 | Toolchain/platform targets need confirmation. |
| Data Compatibility | No ID reuse; versioned saves/packs/replays/protocols; registries; migration tests. | DECISION-08, CONSTRAINT-06, TASK-03, TASK-06 | Requirement candidate | 4 | High priority. |
| Testing and Validation | Conformance tests as proof of modularity; fuzz/malformed/migration/replay tests. | DECISION-07, WORKSTREAM-06, TASK-04 | Requirement candidate | 4 | Needs first pilot module. |
| Determinism and Replay | Simulation isolation from OS/time/UI/rendering; replay equality harness. | WORKSTREAM-05, CONSTRAINT-07, TASK-07 | Requirement candidate | 4 | Depends on actual sim architecture. |
| Setup/Launcher/Tools/UI | Setup as transaction engine; launcher as control plane; tools/UI as contract consumers. | WORKSTREAM-07, TASK-09, REJECTED-06 | Context / requirement candidate | 4 | May overlap with setup/launcher chats. |
