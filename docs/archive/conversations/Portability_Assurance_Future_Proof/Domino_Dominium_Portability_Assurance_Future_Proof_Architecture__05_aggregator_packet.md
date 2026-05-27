# Aggregator Packet — Domino/Dominium Portability, Assurance, and Future-Proof Architecture

## Packet Metadata

* Chat label: Domino/Dominium Portability, Assurance, and Future-Proof Architecture
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: visible current chat plus uploaded prompt; PROJECT-CONTEXT only if labelled
* Coverage: partial visible context
* Confidence: 4/5 for visible chat
* Staleness risk: medium
* Merge priority: high
* Main limitations: actual repo not inspected; many architecture points are assistant recommendations.

## Ultra-Condensed Carry-Forward Capsule

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

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Portability/modularity/extensibility/reuse are explicit user requirements. | preference/constraint | PREF-04 | Primary design driver. | FACT | 5 |
| P0 | Domino should be reusable and not depend on Dominium. | architecture candidate | DECISION-02 / CONSTRAINT-03 | Prevents one-off coupling. | recommendation | 4 |
| P0 | Stable public contracts, replaceable internals. | architecture doctrine | DECISION-03 | Supports deep refactors/backward compatibility. | assistant recommendation | 4 |
| P0 | Persistent data compatibility policy. | requirement candidate | DECISION-08 / TASK-06 | Protects saves, packs, mods, replays, protocols. | assistant recommendation | 4 |
| P1 | Conformance tests prove modularity. | testing doctrine | DECISION-07 / TASK-04 | Makes replacement objective. | assistant recommendation | 4 |
| P1 | Actual repo inspection required. | verification | VERIFY-03 | Proposed tree must be checked. | VERIFY | 5 |

## Workstream Summaries

### WORKSTREAM-01 — Standards-informed assurance profile
* Objective: Define a Domino/Dominium Assurance Profile that borrows useful assurance ideas without compliance claims.
* Current state: Assistant proposed DDAP v0 and DIL levels; not yet user-ratified.
* Desired end state: Written internal profile with levels, gates, schemas, validators, and adoption rules.
* Priority: P1
* Next action: review and pilot concrete implementation.

### WORKSTREAM-02 — Portable engine platform boundary
* Objective: Keep Domino reusable across games/projects through stable contracts and replaceable internals.
* Current state: User explicitly prioritised portability, modularity, extensibility, reuse, and replaceability.
* Desired end state: Domino usable without Dominium, with public contracts and no accidental product dependency.
* Priority: P0
* Next action: review and pilot concrete implementation.

### WORKSTREAM-03 — Directory/module structure and ownership
* Objective: Organise repo around ownership, public contracts, private implementation, tests, and replacement criteria.
* Current state: Assistant proposed a tightened tree and module.toml pattern.
* Desired end state: Dependency direction and module ownership are explicit and checked.
* Priority: P1
* Next action: review and pilot concrete implementation.

### WORKSTREAM-04 — Persistent data and compatibility
* Objective: Make saves/packs/replays/protocols/schemas versioned, migratable, and safe.
* Current state: Assistant proposed TLV/chunk registries, no-ID-reuse, migration tests.
* Desired end state: Versioned formats with registries, fixtures, migration tools, validation.
* Priority: P0
* Next action: review and pilot concrete implementation.

### WORKSTREAM-05 — Determinism and replay
* Objective: Make deterministic state transition and replay validation architectural features.
* Current state: Assistant proposed fixed tick, RNG streams, no OS/time in simulation, replay equality tests.
* Desired end state: Replay harness and determinism rules enforced by tests/layers.
* Priority: P1
* Next action: review and pilot concrete implementation.

### WORKSTREAM-06 — Conformance, validation, and tooling
* Objective: Make modularity mechanically testable.
* Current state: Assistant proposed conformance tests, fuzzing, layer checkers, validators, AIDE/XStack enforcement.
* Desired end state: Automated validators for APIs, schemas, layers, release gates, module replacement.
* Priority: P1
* Next action: review and pilot concrete implementation.

### WORKSTREAM-07 — Setup, launcher, tools, and UI boundaries
* Objective: Keep setup/launcher/tools/UI as contract consumers, not privileged engine internals.
* Current state: Assistant proposed setup transaction flow and semantic command/result UI layer.
* Desired end state: Thin surfaces consume same contracts and respect authority rules.
* Priority: P2
* Next action: review and pilot concrete implementation.

### WORKSTREAM-08 — Chat preservation and spec-book aggregation
* Objective: Preserve this chat into human-readable and structured artifacts.
* Current state: User uploaded preservation prompt requiring report, registers, spec sheet, aggregator packet, audit, files and ZIP.
* Desired end state: Downloadable package plus in-chat reader with caveats.
* Priority: P0
* Next action: review and pilot concrete implementation.


## Compact Registers for Merge

### Decision Register
| ID | Decision | Status | Label |
| --- | --- | --- | --- |
| DECISION-01 | Use standards as design inputs, not literal compliance targets. | Assistant recommendation; not explicitly user-ratified. | INFERENCE / assistant recommendation |
| DECISION-02 | Separate Domino as reusable engine/runtime/toolchain from Dominium as one product built on it. | Assistant recommendation aligned with explicit user goal. | FACT goal + INFERENCE architecture |
| DECISION-03 | Stable public contracts, replaceable internals. | Assistant recommendation; not separately accepted after answer. | assistant recommendation |
| DECISION-04 | Do not make every internal function/header stable. | Assistant recommendation. | assistant recommendation |
| DECISION-05 | Use internal DIL-0 through DIL-5 levels for assurance gates. | Assistant recommendation; not user-confirmed. | assistant recommendation |
| DECISION-06 | Prioritise assurance for saves, packs, replay, authority, updater/installer, multiplayer, and mod trust. | Assistant recommendation. | assistant recommendation |
| DECISION-07 | Use conformance tests as proof of replaceability. | Assistant recommendation. | assistant recommendation |
| DECISION-08 | Treat data evolution as seriously as code evolution. | Assistant recommendation. | assistant recommendation |
| DECISION-09 | Do not present this package as guaranteed full transcript extraction. | Decision in this package. | FACT / UNCERTAIN scope |

### Task Register
| ID | Task | Priority | Urgency | Related workstream | Label |
| --- | --- | --- | --- | --- | --- |
| TASK-01 | Create DDAP v0 document defining DIL-0 through DIL-5 and adoption rules. | P1 | U1 | WORKSTREAM-01 | assistant recommendation |
| TASK-02 | Define public API/ABI policy for Domino. | P0 | U1 | WORKSTREAM-02 | assistant recommendation |
| TASK-03 | Create contracts/registries for stable IDs: error codes, TLV tags, capabilities, opcodes, subsystem IDs. | P0 | U1 | WORKSTREAM-04 | assistant recommendation |
| TASK-04 | Add conformance test area and first replacement tests. | P1 | U1 | WORKSTREAM-06 | assistant recommendation |
| TASK-05 | Add layer checker / forbidden include checker. | P1 | U1 | WORKSTREAM-03 | assistant recommendation |
| TASK-06 | Write data-evolution policy for saves, packs, schemas, protocols, and replays. | P0 | U1 | WORKSTREAM-04 | assistant recommendation |
| TASK-07 | Build deterministic replay comparison harness. | P1 | U2 | WORKSTREAM-05 | assistant recommendation |
| TASK-08 | Define module.toml ownership/replacement metadata. | P2 | U2 | WORKSTREAM-03 | assistant recommendation |
| TASK-09 | Separate setup transaction engine from gameplay and launcher. | P2 | U2 | WORKSTREAM-07 | assistant recommendation |
| TASK-10 | Preserve current chat as report package and ZIP. | P0 | U0 | WORKSTREAM-08 | FACT |
| TASK-11 | Verify external standards and cited practices before formalising spec language. | P1 | U2 | WORKSTREAM-01 | VERIFY |

### Constraint Register
| ID | Constraint | Type | Hard/soft | Label |
| --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Source scope for preservation is this chat only unless labelled PROJECT-CONTEXT. | reporting | hard | FACT |
| CONSTRAINT-02 | Do not invent facts or turn assistant suggestions into user decisions. | epistemic | hard | FACT |
| CONSTRAINT-03 | Domino must not depend on Dominium. | architecture | recommended hard | assistant recommendation |
| CONSTRAINT-04 | Dominium should consume Domino through public contracts. | architecture | recommended hard | assistant recommendation |
| CONSTRAINT-05 | Public ABI structs should use size/version/reserved fields and opaque handles. | API/ABI | recommended hard for public ABI | assistant recommendation |
| CONSTRAINT-06 | No persistent ID/tag/opcode/error code reuse after release. | data compatibility | recommended hard | assistant recommendation |
| CONSTRAINT-07 | Simulation should not directly depend on wall-clock time, OS APIs, UI, renderer, or platform backends. | determinism | recommended hard for authoritative simulation | assistant recommendation |
| CONSTRAINT-08 | No generated output becomes trusted without validation. | assurance/security | recommended hard for DIL-3+ | assistant recommendation |
| CONSTRAINT-09 | Human-readable report must remain understandable without downloading files. | reporting | hard | FACT |

### Open Questions Register
| ID | Question / issue | Priority | Label |
| --- | --- | --- | --- |
| QUESTION-01 | Is DDAP v0 accepted as project direction or only a recommendation pending user review? | P1 | UNCERTAIN |
| QUESTION-02 | What is the current actual repo structure? | P0 | UNCERTAIN |
| QUESTION-03 | Which public boundaries must be stable first? | P1 | UNCERTAIN |
| QUESTION-04 | How strict should C89/C++98 portability be across all code? | P1 | PROJECT-CONTEXT / UNCERTAIN |
| QUESTION-05 | What should be the first pilot module for conformance/replacement testing? | P1 | UNCERTAIN |
| QUESTION-06 | What exact compatibility promises should be made for saves, packs, mods, and protocols? | P0 | UNCERTAIN |
| QUESTION-07 | Which external standards claims need verification before formal spec use? | P2 | VERIFY |

### Artifact Ledger
| ID | Artifact / file / prompt / output | Type | Carry forward? | Label |
| --- | --- | --- | --- | --- |
| ARTIFACT-01 | User-pasted standards/DO-178B/C/Eureka analysis | prompt content | Yes, as background and verification input. | FACT / VERIFY |
| ARTIFACT-02 | Assistant response: DDAP/DIL standards-informed assurance answer | generated chat output | Yes, with tentative label. | assistant recommendation |
| ARTIFACT-03 | User question on portability, modularity, extensibility, replaceability, future-proofing | user instruction / design goal | Yes, high priority. | FACT |
| ARTIFACT-04 | Assistant response: contract-governed engine platform answer | generated chat output | Yes, as architecture draft. | assistant recommendation |
| ARTIFACT-05 | Pasted text.txt preservation mega-prompt | uploaded file | Yes, as method/template. | FACT |
| ARTIFACT-06 | Generated preservation package files | generated files | Yes. | FACT |

### Risk Register
| ID | Risk / failure mode | Likelihood | Severity | Mitigation | Label |
| --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats recommendations as user-approved decisions. | Medium | High | Keep status labels; ask user to approve/reject DDAP and target structure. | UNCERTAIN |
| RISK-02 | Architecture becomes certification cosplay. | Medium | Medium | Use project-native DIL levels; restrict heavy gates to trust paths. | assistant recommendation |
| RISK-03 | Portability remains aspirational without conformance tests. | High | High | Create tests/conformance and replacement criteria. | assistant recommendation |
| RISK-04 | Data formats evolve without registries and migration tests. | Medium | High | No-ID-reuse, registries, golden fixtures, migration tests. | assistant recommendation |
| RISK-05 | Dominium-specific assumptions leak into Domino. | Medium | High | Layer checker; no Domino->Dominium dependencies. | assistant recommendation |
| RISK-06 | Public API is frozen too early. | Medium | Medium | Use experimental/stable/deprecated lifecycle labels and promotion reviews. | assistant recommendation |
| RISK-07 | External standards claims become stale/inaccurate. | Medium | Medium | Verification queue before normative incorporation. | VERIFY |
| RISK-08 | Preservation package overstates access. | Medium | Medium | State coverage limitations clearly. | FACT / UNCERTAIN |

### Verification Queue
| ID | Item requiring verification | Priority | Label |
| --- | --- | --- | --- |
| VERIFY-01 | Current official status/wording of DO-178C family and FAA AC 20-115D. | P2 | VERIFY |
| VERIFY-02 | NIST SSDF, OWASP ASVS, SLSA, SPDX, ISO/IEC references and versions. | P2 | VERIFY |
| VERIFY-03 | Actual Domino/Dominium repository structure and file names. | P0 | VERIFY |
| VERIFY-04 | Current language/toolchain/platform targets, including C89/C++98 strictness. | P1 | VERIFY |
| VERIFY-05 | Existing persistent data formats/schemas/save/pack/replay/protocol plans. | P0 | VERIFY |
| VERIFY-06 | Whether other old-chat reports conflict with this chat. | P1 | VERIFY |

## Possible Cross-Chat Duplicates

Platform/render/backend separation; setup/launcher/distribution architecture; AIDE/XStack governance; C89/C++98 portability; save/pack/replay/protocol contracts.

## Possible Cross-Chat Conflicts

Exact directory structure, client/server as modes vs top-level products, strictness of toolchain targets, DDAP naming versus other governance schemes.

## Spec Book Integration Guidance

Feed this into architecture doctrine, API/ABI policy, data compatibility, conformance testing, determinism, assurance governance, and setup/launcher/tool boundaries. Do not prematurely merge exact folder names or levels without repo inspection and user approval.

## Aggregator Warnings

Do not treat assistant recommendations as final user decisions. Do not assume the repo matches the proposed structure. Preserve recommendation/status labels.
