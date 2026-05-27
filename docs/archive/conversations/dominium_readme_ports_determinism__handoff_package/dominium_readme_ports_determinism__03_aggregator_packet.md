# Aggregator Packet — Dominium README Ports Determinism

## 1. Packet Metadata

* Chat label: Dominium README Ports Determinism
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: THIS CHAT ONLY.
* Coverage: full visible chat coverage; repository state unverified.
* Confidence: 4/5.
* Staleness risk: medium.
* Merge priority: high, because this chat contains explicit architecture decisions for ports and determinism.
* Main limitations: no direct repo file access; metadata-only `/ports` may not fully satisfy user intent; OS/2 conflict remains.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat refined the root README for the Dominium / Domino project and produced state-transfer material for future continuation. The user’s project, as visible in this chat, is a deterministic, integer-math, multi-platform simulation game and engine. Domino is the deterministic engine core; Dominium is the official game/runtime/tooling layer on top of it. The work was conducted through an iterative workflow: user pasted README text, assistant reviewed it, user asked for Codex prompts, Codex output was pasted back, and assistant reviewed it for contradictions or drift.

The initial README already specified a strict C89 engine core, C++98 higher layers, fixed-point Q16.16/Q4.12 numeric model, deterministic tick phases, toroidal 2^24 m surfaces, one 4096 m vertical Page, modding rules, save file structures, and platform/rendering goals. The first assistant review identified several issues: CP/M references conflicted with the “286-class upward” full-engine target; the no-float rule was too broad; “embedded” was vague; platform matrices could drift; binary plugins needed deterministic constraints; build numbers/timestamps needed to be explicitly diagnostic-only; data formats needed immutable versioning language; and `content.lock` needed fatal mismatch semantics.

The first Codex prompt requested mechanical README fixes. The resulting README clarified that the full Domino engine targets 286-class-and-newer systems, while CP/M-80/86 is tooling/limited frontends only. It narrowed no-float rules to authoritative simulation and engine-controlled serialized formats while allowing non-authoritative tools/renderers to use floats if those values never feed back. It added deterministic RNG phase discipline, deterministic future scheduling, deterministic parallel commits, one vertical Page per Surface in Dominium 1.x, non-canonical terrain caches, diagnostic-only build metadata, plugin determinism, exact `content.lock` matching, immutable disk versions, and no platform-specific packing pragmas in canonical format definitions.

The pivotal user requirement was: “i dont want ports to be stored in a seperate directory or system, all ports should work in with the same strcutre and any reduced fucntionality should gracefully degrade and not flow upstream”. This must be preserved as a top-level architecture constraint. The assistant then generated a second Codex prompt to eliminate separate port-tree semantics. The final README says all platforms build from the same unified source hierarchy; platform-specific behavior is expressed only through thin shims, compile-time flags, and capability tables; reduced functionality degrades gracefully through the capability system; and ports must never fork, override, or reimplement engine/runtime systems. The final README retains `/ports` only as optional platform metadata, build configurations, and capability descriptors, with no code or behavior. This interpretation is useful but not absolutely confirmed: the user may have meant no `/ports` directory at all.

A cleanup prompt removed Codex-introduced duplication, removed undefined “embedded,” made lockstep the canonical network model, and aligned contributing determinism language with Section 2.1. The final README is the active textual baseline, but actual repository state was not verified.

For aggregation, this chat contributes authoritative-seeming architecture decisions for: unified ports, capability-based graceful degradation, deterministic simulation boundaries, lockstep networking, data-format immutability, and Codex prompt workflow. Do not merge away the unresolved questions. The most important unresolved items are whether metadata-only `/ports` is acceptable and whether OS/2 should be added to Section 9’s normative platform matrix or removed/qualified from the intro.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | User rejected separate port directories/systems. | Requirement | DECISION-14 | Defines platform architecture. | FACT | 5 |
| 2 | Reduced functionality must degrade gracefully and not flow upstream. | Requirement | DECISION-16 | Prevents platform limitations changing canonical behavior. | FACT | 5 |
| 3 | Metadata-only /ports is current README state but needs confirmation. | Open issue | QUESTION-02 | Could be wrong if user meant no /ports at all. | UNCERTAIN / UNVERIFIED | 4 |
| 4 | OS/2 intro vs Section 9 conflict must be resolved. | Open issue | QUESTION-01 | Section 9 is normative. | FACT | 5 |
| 5 | No-float boundary is authoritative-path based, not global. | Constraint | CONSTRAINT-01 | Avoids determinism drift and overconstraint. | FACT | 5 |
| 6 | Lockstep is canonical networking model. | Decision | DECISION-12 | Rollback/prediction are runtime optimizations only. | FACT | 5 |
| 7 | Specs are normative; README is descriptive. | Decision | DECISION-02 | Future spec book should bind behavior. | FACT | 5 |
| 8 | Codex prompts must be surgical and guard against duplicate blocks. | Workflow | TASK-12 | Codex previously duplicated README content. | FACT | 5 |

## 4. Workstream Summaries

### WORKSTREAM-01 — Dominium / Domino README Architecture
* Objective: Maintain the root README as a high-level, contract-like description of the Dominium/Domino project without making it the normative source over /docs/spec.
* Current state: Final README was pasted in chat and is coherent, but actual repository state is unverified.
* Desired end state: A stable README that orients contributors while normative specs define enforceable contracts.
* Priority: high
* Decisions: DECISION-01, DECISION-02, DECISION-03, DECISION-13
* Tasks: TASK-01, TASK-02, TASK-04
* Constraints: CONSTRAINT-01, CONSTRAINT-12, CONSTRAINT-21
* Artifacts: ARTIFACT-01, ARTIFACT-02, ARTIFACT-03, ARTIFACT-04, ARTIFACT-05, ARTIFACT-06, ARTIFACT-07, ARTIFACT-08
* Risks: RISK-01, RISK-02, RISK-07
* Open questions: QUESTION-01, QUESTION-02, QUESTION-05
* Next action: Verify actual repository README.md against the final pasted README, then patch remaining contradictions.

### WORKSTREAM-02 — Unified Ports and Capability-Based Degradation
* Objective: Ensure all ports/platforms use one source hierarchy, with platform differences expressed through capability descriptors, compile-time flags, and thin shims only.
* Current state: Final README states that /ports contains metadata/build configs/capability descriptors only and no engine/runtime source code.
* Desired end state: No port-specific implementation trees; degraded features disable locally without flowing upstream into canonical engine/runtime behavior.
* Priority: high
* Decisions: DECISION-14, DECISION-15, DECISION-16, DECISION-17
* Tasks: TASK-03, TASK-05, TASK-06, TASK-07
* Constraints: CONSTRAINT-12, CONSTRAINT-13, CONSTRAINT-14, CONSTRAINT-15, CONSTRAINT-16
* Artifacts: ARTIFACT-05, ARTIFACT-06, ARTIFACT-08
* Risks: RISK-02, RISK-03, RISK-04, RISK-05
* Open questions: QUESTION-02, QUESTION-03, QUESTION-04
* Next action: Confirm /ports semantics if directory work begins; then formalize in DIRECTORY_CONTRACT.md and capability-system spec.

### WORKSTREAM-03 — Determinism Contract Refinement
* Objective: Define deterministic behavior boundaries for simulation, serialization, RNG, tick phases, parallel commits, networking, plugins, and build metadata.
* Current state: Final README has clarified no-float boundaries, RNG phase discipline, deterministic parallel commit, lockstep-first networking, and build metadata isolation.
* Desired end state: A formal determinism spec and tests ensuring bit-identical simulation across supported targets for the same executable, content, inputs, and timeline.
* Priority: high
* Decisions: DECISION-05, DECISION-06, DECISION-07, DECISION-08, DECISION-09, DECISION-10, DECISION-11, DECISION-12, DECISION-18, DECISION-19
* Tasks: TASK-08, TASK-10
* Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-11
* Artifacts: ARTIFACT-02, ARTIFACT-03, ARTIFACT-08
* Risks: RISK-06, RISK-08, RISK-09
* Open questions: QUESTION-06, QUESTION-07, QUESTION-08, QUESTION-05
* Next action: Create or update a formal determinism spec from the README rules.

### WORKSTREAM-04 — Data Formats, Saves, and Content Lock Contract
* Objective: Define stable, explicit, deterministic engine-controlled formats for saves, regions, chunks, content locks, and replay metadata.
* Current state: Final README includes immutable on-disk versions, explicit field sizes, canonical little-endian representation, no serialized pointers, and fatal content.lock mismatch behavior.
* Desired end state: Formal data-format specs and migration policy that prevent silent reinterpretation and cross-platform layout drift.
* Priority: high
* Decisions: DECISION-20, DECISION-21, DECISION-22, DECISION-23
* Tasks: TASK-09, TASK-11
* Constraints: CONSTRAINT-17, CONSTRAINT-18, CONSTRAINT-19, CONSTRAINT-20
* Artifacts: ARTIFACT-02, ARTIFACT-08, ARTIFACT-12
* Risks: RISK-10, RISK-11
* Open questions: QUESTION-09, QUESTION-10, QUESTION-11
* Next action: Draft data format/versioning spec and content-lock verification spec.

### WORKSTREAM-05 — Future Normative Spec Files
* Objective: Translate README-level descriptions into enforceable specs under /docs/spec.
* Current state: README references DIRECTORY_CONTRACT.md and MILESTONES.md, but no spec file contents were inspected in this chat.
* Desired end state: Directory, determinism, capability, data-format, plugin, and build specs align with README decisions.
* Priority: medium-high
* Decisions: DECISION-02
* Tasks: TASK-05, TASK-06, TASK-08, TASK-09
* Constraints: CONSTRAINT-21
* Artifacts: ARTIFACT-13, ARTIFACT-14
* Risks: RISK-12
* Open questions: QUESTION-03, QUESTION-04, QUESTION-09
* Next action: If continuing beyond README, start with DIRECTORY_CONTRACT.md and capability-system spec.

### WORKSTREAM-06 — Codex Prompt Workflow
* Objective: Use precise copy-paste prompts to make mechanical repository edits through Codex while minimizing unintended rewrites.
* Current state: Three major Codex prompts were produced and used; Codex once introduced a duplicate top block, which was corrected by a cleanup prompt.
* Desired end state: Future prompts remain surgical, preserve user decisions, forbid duplicate sections, and explicitly protect ports/determinism semantics.
* Priority: medium
* Decisions: DECISION-24
* Tasks: TASK-12
* Constraints: CONSTRAINT-22, CONSTRAINT-23
* Artifacts: ARTIFACT-03, ARTIFACT-05, ARTIFACT-07
* Risks: RISK-01, RISK-13
* Open questions: 
* Next action: For any new edit, generate a targeted prompt with explicit no-change boundaries.


## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Domino is the deterministic simulation engine core; Dominium is the official game/runtime/tooling layer. | decided | README intro | Separates kernel from game/tooling layer. | Allows one compatible implementation atop Domino; other uses remain possible. | WORKSTREAM-01 | 5 | FACT |
| DECISION-02 | README is descriptive; files under /docs/spec are normative. | decided | README Section 3 and final note | Prevents README from being sole enforceable contract. | Specs must be updated to bind behavior and formats. | WORKSTREAM-01, WORKSTREAM-05 | 5 | FACT |
| DECISION-03 | Full Domino engine targets 286-class-and-newer systems; earlier 8-bit systems may host only limited tooling/frontends. | decided | README Section 1.3 | Resolves CP/M vs full-engine contradiction. | CP/M-80 cannot host complete world simulation. | WORKSTREAM-01 | 5 | FACT |
| DECISION-04 | Undefined embedded future target was removed from README. | decided | Cleanup prompt and final README | Avoids overpromising unsupported embedded scope. | Future systems are WASM/Web and consoles via ABI frontends. | WORKSTREAM-01 | 5 | FACT |
| DECISION-05 | No floating point is allowed in code mutating canonical simulation state or engine-controlled serialized formats. | decided | README 2.1 | Preserves deterministic simulation and formats. | Engine-facing simulation paths must use integer/fixed-point math. | WORKSTREAM-03 | 5 | FACT |
| DECISION-06 | No float/double in /engine or engine-controlled on-disk formats. | decided | README 2.1 | Hardens engine determinism. | CI/code review should reject floats in these areas. | WORKSTREAM-03 | 5 | FACT |
| DECISION-07 | Tools, renderers, and non-authoritative analysis may use floats if float-derived values never feed back into engine state/formats. | decided | README 2.1 | Avoids overconstraining non-authoritative layers. | Requires clear dataflow boundaries. | WORKSTREAM-03 | 5 | FACT |
| DECISION-08 | RNG streams only advance during deterministic tick phases; debug/UI/rendering cannot advance engine RNG. | decided | README 2.1 | Prevents non-sim layers perturbing state. | RNG stream access must be controlled. | WORKSTREAM-03 | 5 | FACT |
| DECISION-09 | The global simulation tick has immutable phases. | decided | README 2.2 | Stable phase order is a determinism foundation. | No system can reorder or bypass phases. | WORKSTREAM-03 | 5 | FACT |
| DECISION-10 | Future-tick scheduling must go through Pre-State queueing. | decided | README 2.2 | Avoids ad hoc timers and future mutations. | Systems need a canonical queue mechanism. | WORKSTREAM-03 | 5 | FACT |
| DECISION-11 | Parallel execution must use disjoint state subsets and deterministic commit order. | decided | README 2.2 | Allows parallelism without nondeterministic state changes. | Commit order should be globally stable, e.g. sort-by-ID. | WORKSTREAM-03 | 5 | FACT |
| DECISION-12 | Canonical network model is deterministic lockstep; rollback/prediction must converge to pure lockstep. | decided | README 5.1 | Clarifies rollback as runtime optimization, not alternate truth. | Network protocol/spec must treat lockstep as reference. | WORKSTREAM-03 | 5 | FACT |
| DECISION-13 | One vertical Page per Surface in Dominium 1.x; extra shells/deep volumes/orbital shells use separate Surfaces or logical spaces. | decided | README 2.3 | Bounds vertical addressing. | Prevents silent extension of Z range. | WORKSTREAM-01 | 5 | FACT |
| DECISION-14 | All platforms build from the same unified source hierarchy. | decided | User port statement; README 2.5, 4.2, 9, 11 | User rejected separate port systems. | No per-platform forks or alternate source trees. | WORKSTREAM-02 | 5 | FACT |
| DECISION-15 | /ports contains only optional platform metadata, build configurations, and capability descriptors; no code or behavior. | current README state | README 3 and 4.2 | Assistant/Codex interpretation of user's no-separate-ports preference. | Directory contract must forbid engine/runtime source there. | WORKSTREAM-02 | 4 | UNCERTAIN / UNVERIFIED |
| DECISION-16 | Reduced functionality degrades gracefully through capability system without altering engine behavior. | decided | User statement; README 2.4, 2.5, 4.2, 9 | Prevents low-end platform limitations from changing canonical semantics. | Capability descriptors become critical architecture. | WORKSTREAM-02 | 5 | FACT |
| DECISION-17 | Ports cannot fork, override, or reimplement engine/runtime systems. | decided | README 2.4, 2.5, 4.2, 11 | Preserves unified codebase and determinism. | CI/specs should prohibit divergent platform systems. | WORKSTREAM-02 | 5 | FACT |
| DECISION-18 | Build numbers and timestamps are diagnostic only and cannot affect simulation or engine-controlled formats. | decided | README 4.1 | Prevents build metadata from breaking reproducibility. | Build system must keep diagnostics out of canonical state/files. | WORKSTREAM-03 | 5 | FACT |
| DECISION-19 | Binary plugins are bound by the same determinism constraints as the core. | decided | README 6 | Prevents plugin nondeterminism. | Plugin ABI/sandbox must forbid time/RNG/threads/floats affecting sim. | WORKSTREAM-03 | 5 | FACT |
| DECISION-20 | Existing on-disk versions are immutable contracts; changes require new version and migration path. | decided | README 7 | Supports long-term archival stability. | No silent reinterpretation of old data. | WORKSTREAM-04 | 5 | FACT |
| DECISION-21 | No reliance on platform-specific struct packing pragmas in canonical format definitions. | decided | README 7 | Prevents compiler/platform layout drift. | Disk layouts must be explicit field-size layouts. | WORKSTREAM-04 | 5 | FACT |
| DECISION-22 | content.lock mismatch is fatal until reconciled. | decided | README 7.1 | Ensures deterministic registry reconstruction. | Loader must reject mismatched active content sets. | WORKSTREAM-04 | 5 | FACT |
| DECISION-23 | Terrain caches/microgrids are non-canonical; canonical geometry is procedural phi plus edits, volumes, fluid/thermal/network state. | decided | README 2.3 and 7.1 | Prevents derived caches from defining world state. | Caches can be rebuilt deterministically. | WORKSTREAM-04 | 5 | FACT |
| DECISION-24 | Codex prompts should be surgical, copy-pasteable, and explicit about what must not change. | decided in workflow | Repeated prompt style and cleanup after Codex duplication | Minimizes unintended rewrites. | Future prompts should include no-duplication and preserve-semantics clauses. | WORKSTREAM-06 | 5 | INFERENCE |

### Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Verify actual repository README.md against final pasted README. | high | medium | User/Codex/new assistant if repo is provided | ARTIFACT-08 | Repository access or pasted current README | Confirmation or diff of README state. | Compare repo file with final pasted snapshot. | WORKSTREAM-01 | FACT |
| TASK-02 | Resolve OS/2 intro vs Section 9 normative matrix inconsistency. | high | medium | User/Codex | TASK-01 | Decision whether OS/2 is supported/limited/descriptive | Small README patch adding OS/2 to Section 9 or removing/qualifying it in intro. | Generate a surgical Codex prompt. | WORKSTREAM-01 | FACT |
| TASK-03 | Confirm whether metadata-only /ports is acceptable or whether no /ports directory should exist. | high | medium | User |  | User confirmation | Clear repository-layout decision. | Ask only if directory/spec work depends on it. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| TASK-04 | Tighten Section 11 strict float shorthand if desired. | medium | low | Codex | TASK-01 | Final README | Change 'No floats in simulation or core IO' to precise /engine wording. | Optional Codex prompt. | WORKSTREAM-01, WORKSTREAM-03 | INFERENCE |
| TASK-05 | Create/update /docs/spec/DIRECTORY_CONTRACT.md to enforce unified structure and metadata-only /ports if retained. | high | medium | Codex/dev | TASK-03 | Existing DIRECTORY_CONTRACT.md if present | Normative directory contract. | Prompt Codex after /ports semantics are confirmed. | WORKSTREAM-02, WORKSTREAM-05 | INFERENCE |
| TASK-06 | Create capability-system spec. | high | medium | Codex/dev | TASK-03, TASK-05 | Desired descriptor schema | Specification for capability tables/descriptors and graceful degradation. | Draft /docs/spec/CAPABILITY_SYSTEM.md or equivalent. | WORKSTREAM-02, WORKSTREAM-05 | INFERENCE |
| TASK-07 | Add CI/build guard preventing engine/runtime source under /ports if metadata-only /ports is retained. | medium | low | Codex/dev | TASK-05 | Allowed file types under /ports | Automated enforcement check. | Define allowed extensions and forbidden source patterns. | WORKSTREAM-02 | INFERENCE |
| TASK-08 | Create formal determinism spec. | high | medium | Codex/dev | TASK-01 | README 2.1/2.2/5.1/11 | DETERMINISM.md or equivalent. | Generate prompt from README rules. | WORKSTREAM-03, WORKSTREAM-05 | INFERENCE |
| TASK-09 | Create formal data format/versioning spec. | high | medium | Codex/dev | TASK-01 | README Section 7 and any existing format docs | Disk layout, TLV, versioning, migration policy spec. | Generate prompt. | WORKSTREAM-04, WORKSTREAM-05 | INFERENCE |
| TASK-10 | Define replay hash and RNG algorithms/specification. | medium | medium | Codex/dev | TASK-08 | Desired algorithms or existing implementation | State hash/RNG stream spec. | Add to determinism spec. | WORKSTREAM-03 | INFERENCE |
| TASK-11 | Define content.lock verification and reconciliation process. | medium | medium | Codex/dev | TASK-09 | Content registry/hash design | Loader behavior and reconciliation spec. | Add to data/content spec. | WORKSTREAM-04 | INFERENCE |
| TASK-12 | For future Codex edits, include explicit no-duplication and preserve-semantics clauses. | medium | ongoing | Assistant/new chat | ARTIFACT-07 | Next edit objective | Scoped Codex prompt. | Apply prompt style from this chat. | WORKSTREAM-06 | FACT |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | No floating point in code that mutates canonical simulation state or engine-controlled serialized formats. | determinism | hard | README 2.1 | Use integer/fixed-point in authoritative paths. | high | 5 | FACT |
| CONSTRAINT-02 | No float/double in /engine or engine-controlled on-disk formats. | code/format | hard | README 2.1 | Engine code and canonical formats must be float-free. | high | 5 | FACT |
| CONSTRAINT-03 | Tools/renderers/non-authoritative analysis may use floats only if results never feed back into engine state or engine-controlled formats. | boundary | hard | README 2.1 | Requires strict dataflow separation. | high | 5 | FACT |
| CONSTRAINT-04 | World surfaces are 2^24 m x 2^24 m toroidal squares. | world model | hard | README 2.1/2.3 | World addressing must match fixed dimensions. | medium | 5 | FACT |
| CONSTRAINT-05 | Each Surface owns exactly one vertical Page in Dominium 1.x. | world model | hard | README 2.3 | Do not extend Z range; use separate surfaces/logical spaces. | medium | 5 | FACT |
| CONSTRAINT-06 | Simulation tick phases are immutable. | simulation order | hard | README 2.2 | No system can reorder/bypass phases. | high | 5 | FACT |
| CONSTRAINT-07 | RNG streams advance only during deterministic tick phases. | RNG | hard | README 2.1 | Debug/UI/render cannot perturb RNG state. | high | 5 | FACT |
| CONSTRAINT-08 | Parallel execution must commit in globally deterministic order. | parallelism | hard | README 2.2 | Sort/serialize commits deterministically. | high | 5 | FACT |
| CONSTRAINT-09 | Canonical network model is deterministic lockstep. | networking | hard | README 5.1 | Rollback/prediction must converge to lockstep. | high | 5 | FACT |
| CONSTRAINT-10 | Build numbers/timestamps are diagnostic only and never affect simulation or engine-controlled formats. | build determinism | hard | README 4.1 | Keep build metadata out of authoritative state/files. | medium | 5 | FACT |
| CONSTRAINT-11 | Binary plugins follow core determinism constraints. | plugin | hard | README 6 | Plugin ABI must forbid nondeterministic effects. | high | 5 | FACT |
| CONSTRAINT-12 | All platforms build from one unified source hierarchy. | architecture | hard | User statement; README 2.5/4.2/9/11 | No platform forks. | high | 5 | FACT |
| CONSTRAINT-13 | /ports contains no engine/runtime source code or behavior if retained. | repository layout | hard | README 3/4.2 | Only metadata/build configs/capability descriptors. | high | 4 | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-14 | Reduced functionality degrades gracefully through capability system and does not flow upstream. | architecture | hard | User statement; README | Low-end limitations must not change canonical semantics. | high | 5 | FACT |
| CONSTRAINT-15 | Ports cannot fork, override, or reimplement engine/runtime systems. | architecture | hard | README 2.4/2.5/11 | Platform-specific behavior must remain at shims/capabilities. | high | 5 | FACT |
| CONSTRAINT-16 | All platforms adhere to same engine ABI and file formats. | ABI/format | hard | README 2.5 | No per-platform file/ABI divergence. | high | 5 | FACT |
| CONSTRAINT-17 | Engine-controlled formats are little-endian canonical. | format | hard | README 7 | Platforms convert as needed. | medium | 5 | FACT |
| CONSTRAINT-18 | Existing on-disk versions are immutable contracts. | format versioning | hard | README 7 | Changes require new versions and migration path. | medium | 5 | FACT |
| CONSTRAINT-19 | No platform-specific struct packing pragmas in canonical format definitions. | format layout | hard | README 7 | Use explicit field-size disk layouts. | medium | 5 | FACT |
| CONSTRAINT-20 | content.lock active content set must match exactly or loading is fatal until reconciled. | content determinism | hard | README 7.1 | No silent mod/content mismatch. | medium | 5 | FACT |
| CONSTRAINT-21 | Behavioral or format changes require spec updates before or alongside code. | documentation/spec | hard | README 11 | Specs must stay aligned with implementation. | medium | 5 | FACT |
| CONSTRAINT-22 | Future Codex prompts should preserve headings, section numbers, tone, and explicit no-change boundaries unless user requests otherwise. | workflow | soft | Prompt style in chat | Prevents broad unintended rewrites. | medium | 5 | INFERENCE |
| CONSTRAINT-23 | Future reports must label FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT and preserve rejected options. | reporting | hard | User final package request | Prevents state-transfer corruption. | high | 5 | FACT |

### Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Should OS/2 strata via shims be added to Section 9’s normative platform matrix or removed/qualified from the intro? | Section 9 says it is normative; intro lists OS/2 while Section 9 omits it. | Intro includes OS/2 strata via shims; Section 9 lists platforms without OS/2. | Whether OS/2 is intended supported, limited, or merely descriptive. | User decision or repository target list. | high | WORKSTREAM-01 | FACT |
| QUESTION-02 | Does the user accept metadata-only /ports, or want no /ports directory at all? | User said ports should not be stored in a separate directory or system. | Final README retains /ports as metadata-only and says no code/behavior lives there. | Whether that fully matches user intent. | User clarification before directory contract work. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Where should platform shims physically live if /ports has no code? | Directory contract needs exact locations. | README says platform-specific behavior is in /runtime, /launcher, /tools and shims are configured via /ports metadata. | Precise subdirectories and boundaries. | DIRECTORY_CONTRACT.md design. | high | WORKSTREAM-02, WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What is the capability descriptor schema? | Graceful degradation depends on it. | README mentions capability tables/descriptors. | Fields, file format, compile-time vs runtime handling, validation. | Capability-system spec. | high | WORKSTREAM-02, WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Should Section 11 strict prohibition 'No floats in simulation or core IO' be tightened to /engine-specific wording? | Avoids ambiguity with Section 2.1 float carveout. | Section 2.1 is precise; Section 11 has older shorthand. | Whether user wants this wording patch. | Optional README cleanup. | medium | WORKSTREAM-01, WORKSTREAM-03 | INFERENCE |
| QUESTION-06 | What exact state-hash algorithm is intended? | Replay/desync validation needs precise hash. | README says engine can recompute state hashes per tick. | Algorithm, fields included, endian/order details. | Determinism spec. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What exact RNG algorithms and stream formats are intended? | RNG reproducibility depends on algorithm and serialization. | README mentions stateless coordinate hashing and named RNG streams. | Algorithms, seed derivation, state layout. | Determinism/RNG spec. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | How is rollback implemented while lockstep remains canonical? | Networking/runtime architecture needs details. | README says rollback/prediction must converge to pure lockstep. | Protocol and reconciliation details. | Network spec. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | What exact TLV and binary layout definitions are intended? | Data format specs need exact fields and encodings. | README describes region/chunk headers and sections conceptually. | Concrete field widths, alignment, endian conversion. | Format spec. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | What CRC/content hash algorithms are intended? | Integrity and content.lock verification depend on them. | README mentions optional CRCs and id/version/hash. | Algorithms and canonical input bytes. | Format/content spec. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | Should 'Packed C structs' wording be revised to avoid conflict with no packing pragmas? | Could confuse implementers. | README says packed C structs with explicit sizes and also no platform-specific struct packing pragmas. | Preferred wording: canonical packed layouts vs compiler-packed structs. | Optional README/spec wording patch. | low-medium | WORKSTREAM-04 | INFERENCE |

### Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Initial README pasted by user | pasted document | Baseline for critique and first prompt | superseded | User first message | yes, historical | Contained original architecture and initial contradictions. | FACT |
| ARTIFACT-02 | Assistant critique of initial README | review output | Identify structural issues and proposed fixes | superseded but rationale-active | Assistant response | yes | Included CP/M/286, float scope, platform drift, plugin determinism, build metadata, format versioning. | FACT |
| ARTIFACT-03 | First Codex prompt for mechanical README fixes | prompt | Apply initial surgical README fixes | used | Assistant response to user request | yes | Preserved in previous context packet appendix. | FACT |
| ARTIFACT-04 | Codex output after first prompt | pasted README | Intermediate README with most fixes applied | superseded | User pasted | yes, historical | Reviewed as mostly correct. | FACT |
| ARTIFACT-05 | User port architecture requirement | user statement | Major design correction | active | User message | yes, highest priority | Exact wording preserved in report. | FACT |
| ARTIFACT-06 | Second Codex prompt: Integrate Ports Into Unified Structure | prompt | Encode unified source hierarchy and capability degradation | used | Assistant response | yes | Preserved in packet appendix. | FACT |
| ARTIFACT-07 | Cleanup Codex prompt after duplicate block | prompt | Remove duplication, remove embedded, lockstep-first, align contributing bullet | used | Assistant response | yes | Preserved in packet appendix. | FACT |
| ARTIFACT-08 | Final README pasted by user | pasted document | Current textual baseline | active but repo-unverified | User last README paste | yes, primary artifact | Should be compared to actual README.md. | FACT |
| ARTIFACT-09 | Previous maximum-fidelity Context Transfer Packet | handoff document | State transfer for new chat | source for this package | Assistant response before current request | yes | This package normalizes and repairs it. | FACT |
| ARTIFACT-10 | README root file | repository file reference | Actual target file | unverified | Referenced by prompts and user workflow | yes | No direct file access in chat. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-11 | /docs/spec/DIRECTORY_CONTRACT.md | referenced spec file | Normative directory contract | unverified | README reference | yes | Should encode /ports and unified source hierarchy. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-12 | content.lock | referenced save artifact | Locks exact content/mod versions and hashes | design artifact | README Section 7.1 | yes | Mismatch fatal until reconciled. | FACT |
| ARTIFACT-13 | /docs/spec/MILESTONES.md | referenced spec/status file | Tracks implementation status | unverified | README reference | yes | No contents reviewed. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-14 | .dominium_build_number and build/generated/dom_build_version.h | referenced build artifacts | Diagnostic build versioning | unverified | README Section 4.1 | yes | Must not affect simulation/formats. | FACT |
| ARTIFACT-15 | This final report package | generated package | Downloadable per-chat archival package | created in current turn | Assistant file generation | yes | Markdown/YAML/ZIP files. | FACT |

### Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Codex may introduce duplicated sections or broad rewrites again. | Loss of coherence and hidden contradictions. | medium | medium | Prompts must explicitly forbid duplication and out-of-scope edits. | WORKSTREAM-06 | FACT |
| RISK-02 | OS/2 intro mention conflicts with normative Section 9 matrix omission. | Platform support ambiguity. | high | medium | Patch README or confirm OS/2 status. | WORKSTREAM-01 | FACT |
| RISK-03 | Metadata-only /ports may not satisfy user's 'no separate directory' intent. | Future directory contract may encode wrong structure. | medium | high | Confirm with user before directory spec work. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-04 | Future contributor interprets /ports as source-code location. | Port forks could reappear. | medium | high | Directory contract and CI should forbid source/behavior under /ports. | WORKSTREAM-02 | INFERENCE |
| RISK-05 | Capability degradation could become behavior by proxy if descriptors are too powerful. | Platform limitations may flow upstream indirectly. | medium | high | Keep descriptors declarative and non-semantic; define strict schema. | WORKSTREAM-02 | INFERENCE |
| RISK-06 | Future assistant overcompresses determinism to 'no floats anywhere'. | Unnecessary constraints on renderers/tools. | medium | medium | Preserve Section 2.1 boundary exactly. | WORKSTREAM-03 | INFERENCE |
| RISK-07 | Future assistant treats README as normative over specs. | Spec drift and false authority. | medium | medium | Preserve README descriptive/spec normative hierarchy. | WORKSTREAM-01 | FACT |
| RISK-08 | Build metadata accidentally leaks into engine-controlled files or hashes. | Breaks reproducibility. | low-medium | high | Audit build system and generated files. | WORKSTREAM-03 | INFERENCE |
| RISK-09 | Debug/UI/rendering accidentally advance RNG streams. | Invisible desyncs. | medium | high | Restrict engine RNG API to deterministic tick phases. | WORKSTREAM-03 | INFERENCE |
| RISK-10 | Packed C struct wording may lead to compiler-packing reliance. | Cross-platform disk layout bugs. | medium | medium | Clarify canonical layout independent of compiler pragmas. | WORKSTREAM-04 | INFERENCE |
| RISK-11 | content.lock reconciliation process undefined. | Users may be blocked without recovery path or implement ad hoc bypasses. | medium | medium | Define reconciliation tooling and policy. | WORKSTREAM-04 | INFERENCE |
| RISK-12 | README-level decisions not transferred into normative specs. | Future code may implement inconsistent behavior. | medium | high | Create/update specs after README stabilizes. | WORKSTREAM-05 | INFERENCE |
| RISK-13 | Future Codex prompt may reintroduce rejected options due to missing context. | Repeated work and architecture regression. | medium | medium | Use this package as bootstrap and include rejected options in prompts. | WORKSTREAM-06 | INFERENCE |
| RISK-14 | State-transfer report may be treated as proof of repository state. | New assistant may assume changes were committed. | medium | medium | Verify actual files before editing or relying on repo state. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |

### Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Actual repository README.md matches final pasted README. | Final pasted text may not be committed or may have changed. | Repository file/diff. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | /docs/spec/DIRECTORY_CONTRACT.md exists and matches README source-tree rules. | README says it is authoritative; contents not inspected. | Repository file. | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | /docs/spec/MILESTONES.md exists and matches status claims. | README references it for concrete implementation status. | Repository file. | medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | User accepts metadata-only /ports rather than no /ports directory. | User's wording may reject any separate ports directory. | User confirmation. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | OS/2 platform status. | Intro and Section 9 conflict. | User decision or platform target list. | high | WORKSTREAM-01 | FACT |
| VERIFY-06 | No engine/runtime source files live under /ports if retained. | Needed to enforce metadata-only semantics. | Repository tree/CI. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Capability descriptors are declarative and cannot alter canonical behavior. | Prevents degradation flowing upstream. | Spec/build review. | medium-high | WORKSTREAM-02 | INFERENCE |
| VERIFY-08 | Build numbers/timestamps cannot enter engine-controlled formats or simulation state. | README demands diagnostic-only metadata. | Build scripts/generated file review. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Tools/renderers cannot feed float-derived values into engine state/formats. | Section 2.1 boundary requires enforcement. | Code review/dataflow/spec. | medium-high | WORKSTREAM-03 | INFERENCE |
| VERIFY-10 | RNG streams are inaccessible to debug/UI/render layers outside deterministic phases. | Prevent desyncs. | API/spec review. | medium-high | WORKSTREAM-03 | INFERENCE |
| VERIFY-11 | Data format specs avoid compiler packing dependence. | README bans platform-specific packing pragmas. | Format spec and C implementation review. | medium | WORKSTREAM-04 | INFERENCE |
| VERIFY-12 | content.lock exact-match and reconciliation behavior are specified. | Avoid ad hoc user-friendly bypasses. | Content/loader spec. | medium | WORKSTREAM-04 | INFERENCE |
| VERIFY-13 | Future Codex output contains no duplicate sections and preserves unified-ports semantics. | Codex previously introduced duplicate block. | Manual diff/review. | ongoing | WORKSTREAM-06 | FACT |

## 6. Possible Cross-Chat Duplicates

Likely duplicates with other chats: deterministic simulation design, fixed-point numeric model, world scale hierarchy, repository structure, platform matrix, modding rules, save formats, launcher/installer design, and spec-first policy.

## 7. Possible Cross-Chat Conflicts

Watch for later or earlier chats that propose separate `/ports/<target>` source trees, port-specific engine forks, full CP/M simulation, global no-floats everywhere, rollback as canonical networking, or any platform-specific save format differences.

## 8. Spec Book Integration Guidance

This chat should feed chapters on architecture overview, determinism, ports/platforms, capability system, directory contract, data formats/saves, modding/plugins, build metadata, and contributor rules. Requirements labelled FACT can be candidates for formal requirements. INFERENCE and UNCERTAIN items should remain as notes until verified. Do not formalize metadata-only `/ports` without resolving QUESTION-02.

## 9. Aggregator Warnings

Do not treat this chat as proof of committed repository state. Do not erase the OS/2 contradiction. Do not assume metadata-only `/ports` is fully accepted. Do not reintroduce separate port systems. Do not collapse the no-floats rule into a global ban. Preserve the exact user port statement as a source anchor.
