# Full Chat Report — Dominium README Ports Determinism

## 0. Report Metadata

| Field | Value |
| --- | --- |
| Chat label | Dominium README Ports Determinism |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | THIS CHAT ONLY; project-level context labelled PROJECT-CONTEXT if used. |
| Apparent coverage | Full visible chat coverage, with repository state unverified. |
| Extraction confidence | 4/5 |
| Staleness risk | Medium: repository files and future project decisions may differ. |
| Future plans present | Yes |
| Pending tasks present | Yes |
| Artifacts/files present | Yes: pasted README snapshots, Codex prompts, referenced files; no directly uploaded repo file. |
| Safe for aggregation | Yes, with caveats. |
| Main limitations | No direct repository access; final README may not be committed; /ports intent and OS/2 matrix unresolved. |

## 1. Executive Summary

This chat focused on refining the root `README.md` for the Dominium / Domino project. The project described in the visible chat is a deterministic, integer-math, multi-scale, multi-platform simulation game and engine. Domino is the deterministic simulation engine core; Dominium is the official game/runtime/tooling layer built on top of it. The user pasted a “latest README,” asked for review, asked for Codex prompts to apply corrections, pasted Codex outputs, and then refined the architecture around ports and platform degradation.

The main workstreams were README architecture, unified port structure, determinism contract refinement, data-format/save contract refinement, future normative specs, and the Codex prompt workflow itself. The initial README already contained substantial architecture: strict C89 engine core, C++98 higher layers, fixed-point numeric model, deterministic tick phases, surfaces using a 2^24 m toroidal domain, modding constraints, save format concepts, and platform/render backend lists. The assistant review identified issues that could lead to future contradictions: full-engine 286-class targets conflicting with CP/M references, overly broad floating-point language, vague future “embedded” support, duplicated platform matrices, insufficient binary plugin determinism, build metadata determinism risks, and weak data-format versioning language.

The first Codex prompt requested minimal mechanical README edits. Codex applied most changes. Those changes clarified that the full Domino engine targets 286-class-and-newer systems; CP/M-80/86 is tooling/limited frontends only; floats are banned in authoritative engine and serialization paths but allowed in tools/renderers if they never feed back; RNG streams advance only during deterministic tick phases; tick scheduling and parallel commits must be deterministic; surfaces have one vertical Page in Dominium 1.x; terrain caches are non-canonical; build numbers/timestamps are diagnostic only; binary plugins follow core determinism constraints; content-lock mismatches are fatal; and disk format versions are immutable contracts.

The major change of direction came when the user stated exactly: “i dont want ports to be stored in a seperate directory or system, all ports should work in with the same strcutre and any reduced fucntionality should gracefully degrade and not flow upstream”. This became the strongest user-level architectural requirement in the chat. The README was then revised so that all platforms build from one unified source hierarchy, platform differences are expressed through thin shims, compile-time flags, and capability tables, and functionality reductions degrade gracefully without changing canonical upstream engine/runtime behavior. The final README retains `/ports` only as optional platform metadata, build configurations, and capability descriptors, explicitly saying no code or behavior lives there. This is an assistant/Codex interpretation of the user's wording and should be verified if directory layout work continues.

The final README also states that Section 9 is the normative platform and renderer matrix. A likely unresolved contradiction remains: the intro mentions “OS/2 strata via shims,” but Section 9’s normative platform list omits OS/2. This should be fixed before treating the README as clean. Another minor issue is Section 11’s strict prohibition bullet, “No floats in simulation or core IO,” which is mostly consistent but less precise than Section 2.1. It can be tightened later to say `/engine` simulation or `/engine` IO.

The highest-priority carry-forward information is: do not reintroduce separate port trees; do not treat CP/M as full-engine capable; preserve exact no-float boundaries; preserve lockstep as canonical; preserve metadata-only `/ports` unless the user clarifies no `/ports` at all; preserve Section 9 as normative or repair its conflicts; and verify actual repository files before acting.

## 2. How to Use This Report

This report covers only this old chat. It is not a full Project Spec Book and does not summarize any external repository state beyond what was visible in the chat. Items labelled FACT were explicitly stated in the visible chat or in the user's pasted README. Items labelled INFERENCE are reasonable conclusions drawn from the visible chat. Items labelled UNCERTAIN / UNVERIFIED are unclear, incomplete, or not directly established. Items labelled PROJECT-CONTEXT come from the project context rather than the visible transcript.

Direct user statements outrank assistant suggestions. Tentative decisions remain tentative. Assistant reviews are evidence of rationale, not binding project decisions unless the user accepted them or incorporated them into the README. External-world facts, software versions, current APIs, laws, prices, schedules, or platform claims should be verified before future use. This report is intended for later master-spec aggregation and should be merged with other old-chat packages without erasing contradictions.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Source basis | Strength | Implication | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-01 | Direct, critical technical review. | Explicit user profile/instructions plus interaction pattern. | high | Future assistants should identify contradictions and risks without padding. | Risk: false reassurance or missed flaws. | FACT |
| PREFERENCE-02 | Codex-ready prompts for implementation. | Observed user requests for prompts and Codex workflow. | high | Provide copy-paste prompts with exact edits when asked. | Risk: abstract advice wastes effort. | FACT |
| PREFERENCE-03 | Rigor and fact/inference separation. | Explicit in user profile and transfer/package requests. | high | Label FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | Risk: tentative suggestions become false decisions. | FACT |
| PREFERENCE-04 | Minimal, surgical edits unless broader rewrite requested. | Observed prompt style and user workflow. | medium-high | Preserve headings/section numbers/tone by default. | Risk: Codex or assistant causes drift. | INFERENCE |
| PREFERENCE-05 | Preserve rejected and superseded options. | Explicit in context-transfer/package requests. | high | Include rejected register and avoid reintroducing old options. | Risk: repeated architectural regressions. | FACT |
| PREFERENCE-06 | No unnecessary clarifying questions when best-effort action is possible. | Explicit system/user preference context. | medium | Proceed with caveats when information is enough. | Risk: interaction slows or repeats known context. | FACT |
| PREFERENCE-07 | Strong concern for deterministic, long-term, spec-first architecture. | Visible from README and user corrections. | high | Evaluate changes against determinism, portability, and spec stability. | Risk: superficial README edits miss architecture consequences. | INFERENCE |

### 3.2 Inferred Preferences

The user appears to prefer Codex-ready implementation prompts, precise architectural language, rigorous preservation of context, and critical review of generated outputs. These are INFERENCE items based on repeated behavior in the chat.

### 3.3 Preferences Not Established by This Chat

This chat does not establish the user's preferred repository branch workflow, commit message style, exact spec filenames beyond referenced paths, exact capability descriptor format, exact stance on whether `/ports` should exist at all, or exact implementation schedule.

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Dominium / Domino README Architecture | Maintain the root README as a high-level, contract-like description of the Dominium/Domino project without making it the normative source over /docs/spec. | Final README was pasted in chat and is coherent, but actual repository state is unverified. | A stable README that orients contributors while normative specs define enforceable contracts. | active | high | 5 | FACT |
| WORKSTREAM-02 | Unified Ports and Capability-Based Degradation | Ensure all ports/platforms use one source hierarchy, with platform differences expressed through capability descriptors, compile-time flags, and thin shims only. | Final README states that /ports contains metadata/build configs/capability descriptors only and no engine/runtime source code. | No port-specific implementation trees; degraded features disable locally without flowing upstream into canonical engine/runtime behavior. | active | high | 4 | FACT |
| WORKSTREAM-03 | Determinism Contract Refinement | Define deterministic behavior boundaries for simulation, serialization, RNG, tick phases, parallel commits, networking, plugins, and build metadata. | Final README has clarified no-float boundaries, RNG phase discipline, deterministic parallel commit, lockstep-first networking, and build metadata isolation. | A formal determinism spec and tests ensuring bit-identical simulation across supported targets for the same executable, content, inputs, and timeline. | active | high | 5 | FACT |
| WORKSTREAM-04 | Data Formats, Saves, and Content Lock Contract | Define stable, explicit, deterministic engine-controlled formats for saves, regions, chunks, content locks, and replay metadata. | Final README includes immutable on-disk versions, explicit field sizes, canonical little-endian representation, no serialized pointers, and fatal content.lock mismatch behavior. | Formal data-format specs and migration policy that prevent silent reinterpretation and cross-platform layout drift. | active | high | 5 | FACT |
| WORKSTREAM-05 | Future Normative Spec Files | Translate README-level descriptions into enforceable specs under /docs/spec. | README references DIRECTORY_CONTRACT.md and MILESTONES.md, but no spec file contents were inspected in this chat. | Directory, determinism, capability, data-format, plugin, and build specs align with README decisions. | active-inferred | medium-high | 3 | INFERENCE |
| WORKSTREAM-06 | Codex Prompt Workflow | Use precise copy-paste prompts to make mechanical repository edits through Codex while minimizing unintended rewrites. | Three major Codex prompts were produced and used; Codex once introduced a duplicate top block, which was corrected by a cleanup prompt. | Future prompts remain surgical, preserve user decisions, forbid duplicate sections, and explicitly protect ports/determinism semantics. | active | medium | 5 | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — Dominium / Domino README Architecture
- Label: FACT
- Objective: Maintain the root README as a high-level, contract-like description of the Dominium/Domino project without making it the normative source over /docs/spec.
- Background: The user pasted an initial README, requested critique, then used Codex prompts to revise it.
- Current state: Final README was pasted in chat and is coherent, but actual repository state is unverified.
- Desired end state: A stable README that orients contributors while normative specs define enforceable contracts.
- Importance: high priority for continuity.
- Decisions made: DECISION-01, DECISION-02, DECISION-03, DECISION-13
- Decisions pending: QUESTION-01, QUESTION-02, QUESTION-05
- Pending tasks: TASK-01, TASK-02, TASK-04
- Constraints: CONSTRAINT-01, CONSTRAINT-12, CONSTRAINT-21
- Dependencies: Actual repository README.md, /docs/spec/DIRECTORY_CONTRACT.md, /docs/spec/MILESTONES.md
- Timeline / sequencing: Entire workstream occurred in this chat through iterative paste-review-prompt-review cycles.
- Blockers: Repository file not directly inspected., Spec files not inspected.
- Risks: RISK-01, RISK-02, RISK-07
- Artifacts: ARTIFACT-01, ARTIFACT-02, ARTIFACT-03, ARTIFACT-04, ARTIFACT-05, ARTIFACT-06, ARTIFACT-07, ARTIFACT-08
- Success criteria: README has no internal contradictions., README preserves user decisions., README remains aligned with normative specs.
- Recommended next action: Verify actual repository README.md against the final pasted README, then patch remaining contradictions.
- Verification needed: VERIFY-01, VERIFY-02, VERIFY-05
- Confidence: 5/5
- Carry-forward priority: high

### WORKSTREAM-02 — Unified Ports and Capability-Based Degradation
- Label: FACT
- Objective: Ensure all ports/platforms use one source hierarchy, with platform differences expressed through capability descriptors, compile-time flags, and thin shims only.
- Background: The user explicitly rejected ports being stored in a separate directory or system.
- Current state: Final README states that /ports contains metadata/build configs/capability descriptors only and no engine/runtime source code.
- Desired end state: No port-specific implementation trees; degraded features disable locally without flowing upstream into canonical engine/runtime behavior.
- Importance: high priority for continuity.
- Decisions made: DECISION-14, DECISION-15, DECISION-16, DECISION-17
- Decisions pending: QUESTION-02, QUESTION-03, QUESTION-04
- Pending tasks: TASK-03, TASK-05, TASK-06, TASK-07
- Constraints: CONSTRAINT-12, CONSTRAINT-13, CONSTRAINT-14, CONSTRAINT-15, CONSTRAINT-16
- Dependencies: Directory contract spec, Capability descriptor spec, Build system enforcement
- Timeline / sequencing: Created after the user's explicit correction about ports and graceful degradation.
- Blockers: Unverified whether metadata-only /ports fully satisfies user intent.
- Risks: RISK-02, RISK-03, RISK-04, RISK-05
- Artifacts: ARTIFACT-05, ARTIFACT-06, ARTIFACT-08
- Success criteria: No engine/runtime source under /ports., No alternate platform implementation trees., Capability system handles reduced functionality.
- Recommended next action: Confirm /ports semantics if directory work begins; then formalize in DIRECTORY_CONTRACT.md and capability-system spec.
- Verification needed: VERIFY-04, VERIFY-06, VERIFY-07
- Confidence: 4/5
- Carry-forward priority: high

### WORKSTREAM-03 — Determinism Contract Refinement
- Label: FACT
- Objective: Define deterministic behavior boundaries for simulation, serialization, RNG, tick phases, parallel commits, networking, plugins, and build metadata.
- Background: Initial README had strong determinism goals but needed narrower float boundaries and stronger ordering guarantees.
- Current state: Final README has clarified no-float boundaries, RNG phase discipline, deterministic parallel commit, lockstep-first networking, and build metadata isolation.
- Desired end state: A formal determinism spec and tests ensuring bit-identical simulation across supported targets for the same executable, content, inputs, and timeline.
- Importance: high priority for continuity.
- Decisions made: DECISION-05, DECISION-06, DECISION-07, DECISION-08, DECISION-09, DECISION-10, DECISION-11, DECISION-12, DECISION-18, DECISION-19
- Decisions pending: QUESTION-06, QUESTION-07, QUESTION-08, QUESTION-05
- Pending tasks: TASK-08, TASK-10
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-11
- Dependencies: DETERMINISM.md spec, Replay hash algorithm, RNG stream format, CI tests
- Timeline / sequencing: Most changes were added in the first Codex prompt and cleanup prompt.
- Blockers: No implementation or spec files were inspected.
- Risks: RISK-06, RISK-08, RISK-09
- Artifacts: ARTIFACT-02, ARTIFACT-03, ARTIFACT-08
- Success criteria: Same inputs/content produce same state hashes across targets., Debug/render/UI cannot perturb engine state., Rollback/prediction converges to lockstep.
- Recommended next action: Create or update a formal determinism spec from the README rules.
- Verification needed: VERIFY-08, VERIFY-09, VERIFY-10
- Confidence: 5/5
- Carry-forward priority: high

### WORKSTREAM-04 — Data Formats, Saves, and Content Lock Contract
- Label: FACT
- Objective: Define stable, explicit, deterministic engine-controlled formats for saves, regions, chunks, content locks, and replay metadata.
- Background: Initial README included TLV design; assistant suggested adding stronger versioning and packing constraints.
- Current state: Final README includes immutable on-disk versions, explicit field sizes, canonical little-endian representation, no serialized pointers, and fatal content.lock mismatch behavior.
- Desired end state: Formal data-format specs and migration policy that prevent silent reinterpretation and cross-platform layout drift.
- Importance: high priority for continuity.
- Decisions made: DECISION-20, DECISION-21, DECISION-22, DECISION-23
- Decisions pending: QUESTION-09, QUESTION-10, QUESTION-11
- Pending tasks: TASK-09, TASK-11
- Constraints: CONSTRAINT-17, CONSTRAINT-18, CONSTRAINT-19, CONSTRAINT-20
- Dependencies: Format specs, Migration tooling, Content hash algorithm
- Timeline / sequencing: Added through the first Codex prompt and retained through final README.
- Blockers: Actual binary layout specs not provided.
- Risks: RISK-10, RISK-11
- Artifacts: ARTIFACT-02, ARTIFACT-08, ARTIFACT-12
- Success criteria: Existing format versions remain immutable., Big-endian/legacy targets can read/write canonical formats., Content mismatches are detected before simulation.
- Recommended next action: Draft data format/versioning spec and content-lock verification spec.
- Verification needed: VERIFY-11, VERIFY-12
- Confidence: 5/5
- Carry-forward priority: high

### WORKSTREAM-05 — Future Normative Spec Files
- Label: INFERENCE
- Objective: Translate README-level descriptions into enforceable specs under /docs/spec.
- Background: README repeatedly says specs are normative and behavioral/format changes require spec updates.
- Current state: README references DIRECTORY_CONTRACT.md and MILESTONES.md, but no spec file contents were inspected in this chat.
- Desired end state: Directory, determinism, capability, data-format, plugin, and build specs align with README decisions.
- Importance: medium-high priority for continuity.
- Decisions made: DECISION-02
- Decisions pending: QUESTION-03, QUESTION-04, QUESTION-09
- Pending tasks: TASK-05, TASK-06, TASK-08, TASK-09
- Constraints: CONSTRAINT-21
- Dependencies: Existing docs/spec files, User confirmation on /ports semantics
- Timeline / sequencing: Logical next phase after README stabilization.
- Blockers: Actual specs not reviewed.
- Risks: RISK-12
- Artifacts: ARTIFACT-13, ARTIFACT-14
- Success criteria: Every README-level architectural claim has a normative spec home.
- Recommended next action: If continuing beyond README, start with DIRECTORY_CONTRACT.md and capability-system spec.
- Verification needed: VERIFY-02, VERIFY-03
- Confidence: 3/5
- Carry-forward priority: medium-high

### WORKSTREAM-06 — Codex Prompt Workflow
- Label: FACT
- Objective: Use precise copy-paste prompts to make mechanical repository edits through Codex while minimizing unintended rewrites.
- Background: The user asks the assistant for Codex prompts, runs Codex externally, then pastes outputs back for review.
- Current state: Three major Codex prompts were produced and used; Codex once introduced a duplicate top block, which was corrected by a cleanup prompt.
- Desired end state: Future prompts remain surgical, preserve user decisions, forbid duplicate sections, and explicitly protect ports/determinism semantics.
- Importance: medium priority for continuity.
- Decisions made: DECISION-24
- Decisions pending: none recorded
- Pending tasks: TASK-12
- Constraints: CONSTRAINT-22, CONSTRAINT-23
- Dependencies: Latest README baseline, User's intended next edit
- Timeline / sequencing: Used throughout the visible chat.
- Blockers: No repo diff available.
- Risks: RISK-01, RISK-13
- Artifacts: ARTIFACT-03, ARTIFACT-05, ARTIFACT-07
- Success criteria: Codex output matches requested scope., Rejected options are not reintroduced., No duplicated sections.
- Recommended next action: For any new edit, generate a targeted prompt with explicit no-change boundaries.
- Verification needed: VERIFY-13
- Confidence: 5/5
- Carry-forward priority: medium


## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | User pasted initial latest README. | Established baseline Dominium/Domino README. | Started review of deterministic engine/game architecture. | historical | 5 |
| 2 | Assistant critiqued initial README. | Identified CP/M/286 contradiction, float scope issue, platform list drift, plugin/build/data-format gaps. | Created rationale for first Codex prompt. | historical | 5 |
| 3 | User asked for Codex prompt. | Task shifted from review to implementation prompt. | Codex workflow established. | historical | 5 |
| 4 | Assistant produced first mechanical Codex prompt. | Specified exact edits for hardware, floats, RNG, tick phases, Page/Surface, directory overview, build numbers, plugins, formats, platform matrix, installer paths. | Prompt became ARTIFACT-03. | historical | 5 |
| 5 | User pasted Codex output after first prompt. | README mostly applied fixes. | Enabled review and next refinements. | historical | 5 |
| 6 | Assistant reviewed Codex output. | Found output clean but noted residual embedded/network/contributing issues. | Generated optional cleanup trajectory. | historical | 5 |
| 7 | User clarified ports must not be separate directory/system and must gracefully degrade without upstream flow. | Major architectural correction. | Created unified-source/capability-system workstream. | active | 5 |
| 8 | Assistant produced unified ports Codex prompt. | Encoded all platforms sharing source hierarchy, /ports metadata-only, capability degradation. | Prompt became ARTIFACT-06. | historical | 5 |
| 9 | User pasted Codex output after ports prompt. | Ports semantics entered README but Codex introduced duplicate top block. | Revealed Codex failure mode. | historical | 5 |
| 10 | Assistant produced cleanup prompt. | Removed duplicate block, removed embedded, lockstep canonical, contributing points to Section 2.1. | Prompt became ARTIFACT-07. | historical | 5 |
| 11 | User pasted final README. | Established current textual baseline. | Final README is active artifact, repo-unverified. | active | 5 |
| 12 | Assistant reviewed final README. | Confirmed ports unification and noted minor issues; missed OS/2 mismatch. | Review informed previous context transfer. | historical | 4 |
| 13 | User requested maximum-fidelity Context Transfer Packet. | Assistant produced long state-transfer packet. | Became ARTIFACT-09. | historical | 5 |
| 14 | User requested final downloadable report package. | Current task: normalize, audit, export files and ZIP. | Creates ARTIFACT-15. | active | 5 |

## 7. Decisions

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

The highest-impact decisions are DECISION-14 through DECISION-17: the port architecture must use one unified source hierarchy, no divergent platform implementation trees, and graceful capability-based degradation. These decisions are grounded in the user's explicit correction and must outrank any earlier README wording that implied separate port build flows. DECISION-05 through DECISION-12 define the determinism contract and should also be preserved exactly, especially the distinction between authoritative engine paths and non-authoritative renderer/tool usage of floats. DECISION-15 remains partially uncertain because the README's metadata-only `/ports` directory may or may not fully satisfy the user's statement that ports should not be stored in a separate directory or system.

## 8. Pending Tasks and Next Actions

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

### 8.1 Recommended Task Order

1. TASK-01: verify actual repository `README.md`.
2. TASK-02: resolve the OS/2 contradiction.
3. TASK-03: confirm metadata-only `/ports` if directory/spec work is next.
4. TASK-05 and TASK-06: update directory contract and capability spec.
5. TASK-08 and TASK-09: create determinism and data-format specs.
6. TASK-07, TASK-10, TASK-11: add enforcement and lower-level algorithms/processes.

### 8.2 Blocked Tasks

TASK-05 and TASK-06 are blocked or risky until QUESTION-02 is resolved. TASK-10 and TASK-11 depend on formal spec choices not established in this chat.

### 8.3 Quick Wins

TASK-02 and TASK-04 are small README cleanup patches. TASK-12 is immediately applicable to any future Codex prompt.

### 8.4 Tasks Requiring Verification

TASK-01, TASK-03, TASK-05, TASK-06, TASK-07, TASK-08, TASK-09, TASK-10, and TASK-11 require repository, spec, or user verification before finalizing.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

See CONSTRAINT-01 through CONSTRAINT-21.

### 9.2 Soft Preferences

See CONSTRAINT-22 and user preference register.

### 9.3 Technical Constraints

The key technical constraints are strict C89 for `/engine`, C++98 for higher layers, fixed-point authoritative simulation, deterministic tick phases, canonical little-endian disk formats, unified source hierarchy, metadata-only `/ports` if retained, and capability-based degradation.

### 9.4 Time / Resource Constraints

No concrete timeline or resource constraints were established in this chat.

### 9.5 Legal / Ethical / Safety Constraints

The README discusses licensing as TBD/per-pack, but no legal final decision was made in this chat. Future legal claims require verification against `/docs/legal/LICENCE.md`.

### 9.6 Evidence / Citation Requirements

The user generally prefers fact-checking and sources, but this chat used only visible pasted text. No web sources were used.

### 9.7 Formatting / Output Requirements

The current request required this package to use stable IDs, structured headings, tables, downloadable files if possible, and labels for fact/inference/uncertainty/project context.

### 9.8 Things to Avoid

Do not reintroduce separate port trees, full CP/M simulation, undefined embedded support, vague lockstep/rollback language, silent disk-version reinterpretation, or unbounded no-floats language that incorrectly bans non-authoritative renderer/tool floats.

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

## 10. Open Questions and Unresolved Issues

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

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Ports as separate directory trees or separate systems. | rejected | User explicitly rejected ports stored in separate directory/system. | final unless user reverses | Only if user explicitly changes architecture. | WORKSTREAM-02 | FACT |
| REJECTED-02 | /ports/<target>/ containing retro build flows or source code. | superseded/rejected | Unified source hierarchy and metadata-only /ports replaced it. | final in README subject to /ports clarification | If user rejects /ports entirely, replace metadata-only directory too. | WORKSTREAM-02 | FACT |
| REJECTED-03 | Per-platform alternate engine implementations. | rejected | Violates unified codebase and determinism. | final | Never for canonical engine. | WORKSTREAM-02 | FACT |
| REJECTED-04 | Reduced platform functionality changing upstream behavior. | rejected | User said reduced functionality should gracefully degrade and not flow upstream. | final | Never for canonical behavior. | WORKSTREAM-02 | FACT |
| REJECTED-05 | CP/M-80 hosting complete world simulation. | rejected | README clarifies full engine targets 286+ and CP/M is limited tooling/frontends. | final | Only if future noncanonical experiments are defined. | WORKSTREAM-01 | FACT |
| REJECTED-06 | Undefined embedded target in intro. | superseded | Removed by cleanup prompt and final README. | final for current README | Reintroduce only with precise definition. | WORKSTREAM-01 | FACT |
| REJECTED-07 | Blanket no-floats language without authoritative-boundary carveout. | superseded | Section 2.1 now allows floats in tools/renderers if no feedback. | final unless user chooses stricter policy | If tools become authoritative writers, revisit boundary. | WORKSTREAM-03 | FACT |
| REJECTED-08 | Vague 'Network layer manages deterministic lockstep/rollback'. | superseded | Replaced by lockstep-first canonical wording. | final | If networking architecture changes. | WORKSTREAM-03 | FACT |
| REJECTED-09 | Multiple independent platform/backend lists across README sections. | superseded | Section 9 became normative matrix. | final | If generated docs can sync lists automatically. | WORKSTREAM-01 | FACT |
| REJECTED-10 | Build number or timestamp affecting simulation/engine formats. | rejected | README says diagnostic only. | final | Never for canonical state/formats. | WORKSTREAM-03 | FACT |
| REJECTED-11 | Silent reinterpretation of existing disk format versions. | rejected | Immutable disk-version contract. | final | Never. | WORKSTREAM-04 | FACT |
| REJECTED-12 | Binary plugins using system time/RNG/threads/floats affecting simulation. | rejected | Plugin determinism rules. | final | Never for deterministic plugins. | WORKSTREAM-03 | FACT |
| REJECTED-13 | Duplicate top-level repository-includes block. | rejected/superseded | Codex introduced it; cleanup prompt removed it. | final | Never intentionally duplicate. | WORKSTREAM-06 | FACT |

Preserving these prevents repeated work because the chat explicitly moved away from separate ports, vague networking, undefined embedded targets, and overly broad float restrictions. Future assistants should check this register before proposing architecture changes.

## 12. Artifact Ledger

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

## 13. Rationale and Assumptions

The visible rationale behind the README changes was to make the document precise enough to prevent future contributors or Codex from weakening determinism, fragmenting platform support, or drifting from normative specs. The strongest rationale came from the user’s explicit ports statement: platform constraints should degrade locally and should not flow upstream into canonical code. The no-floats change was not a weakening of determinism; it was a boundary clarification so that non-authoritative tools/renderers can use floats while engine state and engine-controlled formats remain deterministic. The lockstep-first network wording prevents rollback/prediction from becoming alternate simulation truth. Immutable disk versions prevent long-term save incompatibility and silent reinterpretation.

Assumptions include: the user likely wants future spec files to formalize README claims; Codex is the intended editing agent; and the final pasted README is close to the repository state. These assumptions are not repository facts. The actual repo must be checked.

## 14. Risks and Failure Modes

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

## 15. Verification Queue

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

## 16. Spec Book Contribution Notes

Likely future Project Spec Book chapters fed by this chat:
- Architecture Overview: Domino vs Dominium separation.
- Determinism Contract: fixed-point, RNG, tick phases, lockstep, build metadata.
- Platform and Portability Model: unified source hierarchy, capability descriptors, graceful degradation.
- Repository Directory Contract: metadata-only `/ports` if retained, no port source trees.
- Data Format and Save Contract: TLV, immutable versions, content.lock, canonical endian/layout.
- Modding and Plugin Contract: deterministic scripts/plugins, no binary patching, ABI constraints.
- Build and Release Model: diagnostic build metadata, retro/constrained capability builds.
- Contributor Rules: spec-first changes, tests, no platform forks.

Unique contributions from this chat are the explicit user rejection of separate ports and the refined float/lockstep/data-format boundaries. Overlapping topics likely duplicated in other chats include deterministic engine design, world scale, platform matrix, modding, and repository layout. Conflicts to watch for: any later chat that proposes per-platform source trees, engine forks, or `/ports/<target>/` source directories conflicts with this chat unless the user explicitly reversed the decision.

Formal requirement candidates: all DECISION and CONSTRAINT entries labelled FACT, especially DECISION-14 through DECISION-17 and CONSTRAINT-12 through CONSTRAINT-16. Background context candidates: the iterative Codex workflow and historical prompt artifacts. Needs user confirmation: QUESTION-02 about `/ports` existence and QUESTION-01 about OS/2.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | User rejected separate port directories/systems. | Requirement | Highest-priority architecture correction. | Future assistants may reintroduce port forks. | FACT | 5 |
| 2 | All platforms share one source hierarchy. | Decision | Core port model. | Fragmented implementations. | FACT | 5 |
| 3 | Capability-based graceful degradation must not flow upstream. | Requirement | Protects canonical behavior. | Low-end targets mutate engine semantics. | FACT | 5 |
| 4 | /ports is metadata/build config/capability only if retained. | Current README state | Prevents source code under /ports. | Could violate user intent or invite forks. | UNCERTAIN / UNVERIFIED | 4 |
| 5 | Verify whether user wants no /ports directory at all. | Open question | Critical before directory contract. | Wrong repo structure could be formalized. | UNCERTAIN / UNVERIFIED | 5 |
| 6 | No floats in /engine or engine-controlled formats; non-authoritative layers may use floats with no feedback. | Constraint | Precise determinism boundary. | Over- or under-constraining implementation. | FACT | 5 |
| 7 | Canonical networking is deterministic lockstep. | Decision | Rollback/prediction cannot become alternate truth. | Desync-prone net architecture. | FACT | 5 |
| 8 | OS/2 intro vs Section 9 conflict exists. | Open issue | README inconsistency. | Normative matrix drift. | FACT | 5 |
| 9 | Specs are normative; README is descriptive. | Decision | Prevents README/spec authority confusion. | Spec drift. | FACT | 5 |
| 10 | Codex can introduce duplicate sections. | Risk | Observed failure mode. | Bad future patches. | FACT | 5 |
| 11 | CP/M-80/86 is tooling/limited frontend only. | Decision | Avoids full-engine 8-bit contradiction. | Unrealistic target claims. | FACT | 5 |
| 12 | content.lock mismatch is fatal until reconciled. | Decision | Registry determinism. | Silent mod/content mismatch. | FACT | 5 |
| 13 | Disk versions are immutable contracts. | Decision | Long-term format stability. | Save corruption/drift. | FACT | 5 |
| 14 | Build metadata diagnostic only. | Decision | Reproducible simulation. | Hashes/state affected by timestamp/build number. | FACT | 5 |
| 15 | Future Codex prompts must be surgical. | Workflow | Avoids broad unintended rewrites. | Architecture regression. | INFERENCE | 5 |

## 18. What Future Assistants Must Not Assume

- Do not assume the final README is committed to the repository.
- Do not assume `/ports` metadata-only fully satisfies the user; verify if directory work depends on it.
- Do not assume OS/2 is supported merely because the intro mentions it.
- Do not assume CP/M-80/86 can host the complete world simulation.
- Do not assume floats are banned everywhere; non-authoritative floats are allowed under strict no-feedback rules.
- Do not assume exact RNG/hash/TLV/content-hash algorithms exist.
- Do not assume referenced spec files exist or match README.
- Do not assume assistant suggestions are user decisions unless incorporated into the README or accepted by the user.
- Do not assume this chat covers the entire Dominium project.

## 19. Recommended Next Action

If continuing this chat’s work alone: verify the actual repository README, then patch the OS/2 inconsistency and optionally tighten Section 11’s float shorthand. If work is moving into specs, first confirm whether metadata-only `/ports` is acceptable, then update `DIRECTORY_CONTRACT.md` and create a capability-system spec.

If aggregating this chat with other reports: ingest the workstreams, decisions, constraints, rejected options, and verification queue; do not merge port architecture with any conflicting later chat unless the user explicitly reversed this decision.

User verification needed before acting: QUESTION-01 and QUESTION-02.

## 20. Appendix: Possibly Relevant Details

### 20.1 Exact user port requirement

> i dont want ports to be stored in a seperate directory or system, all ports should work in with the same strcutre and any reduced fucntionality should gracefully degrade and not flow upstream

### 20.2 Exact Codex Prompt 1 — Initial Mechanical README Fixes

```text
You are editing the root `README.md` for the Dominium/Domino project.

Goal: apply the following **mechanical, minimal** edits to the existing README without changing its overall structure, headings, or tone. Preserve all existing section numbers and headings. Do not introduce new top-level sections. Only modify text where explicitly requested.

Work directly on the existing `README.md` in the repo.

---

## 1. Hardware target clarification (286 vs CP/M)

1. Locate the bullet in Section **1. Project Vision** that currently says:

> Execute on decades of hardware (286-class upward)

Immediately after this line, insert a new sentence:

> The full Domino engine targets 286-class-and-newer systems. Limited tooling and experimental frontends may exist for earlier 8-bit platforms (for example, CP/M-80), but they do not host the complete world simulation.

2. Ensure that any later references to CP/M-80/86 are consistent with this constraint (they are tooling or limited frontends, not full engine simulation hosts). Do not remove CP/M from the platform lists; just keep the semantics consistent with the new sentence.

---

## 2. Floating point constraints – narrow the scope

In Section **2.1 Determinism**, update the floating-point rules:

1. Find the bullet that currently says:

> No floating point in any simulation or IO code path.
>   - No `float` or `double` in `/engine` or serialized formats.
>   - All continuous quantities are fixed-point integers: …

Replace that entire bullet with:

> No floating point is allowed in any code that mutates canonical simulation state or engine-controlled serialized formats.
>   - No `float` or `double` in `/engine` or in any engine-controlled on-disk formats.
>   - All continuous quantities are fixed-point integers:  
>     - Runtime: **Q16.16** (`fix32`) for general simulation.  
>     - Save-local positional: **Q4.12** (`fix16`) for coordinates inside 16 m chunks.  
>     - Accumulators and reductions use 64-bit ints where needed.

2. Immediately after that bullet, add a new bullet:

> Tools, renderers, and non-authoritative analysis may use floating point freely, as long as float-derived values never flow back into engine state or engine-controlled file formats.

3. In the same section, under **RNG discipline**, after the existing bullets, append one more bullet:

> RNG streams are only advanced during deterministic tick phases; debug, UI, and rendering layers must not advance engine RNG streams.

---

## 3. Tick phasing and parallelism constraints

In Section **2.2 Tick Phasing and Ordering**:

1. After the list of phases (1–7) and the existing paragraphs about parallelism, append two short paragraphs:

> Any operation that schedules work for a future tick (timers, delayed spawns, transport completions) must do so via the Pre-State phase’s queueing mechanism; no system may directly mutate future-tick state.
>
> Parallel execution within a phase may only operate on disjoint subsets of state and must commit results in a globally deterministic order (for example, by sort-by-ID before commit).

Keep formatting consistent with the surrounding text.

---

## 4. Spatial hierarchy clarifications (Page/Surface)

In Section **2.3 Spatial Hierarchy (Technical Scale)**:

1. Under the **2^12 m – Page** bullet, change it to:

> **2^12 m - Page**  
> 4096 m; vertical domain per surface. For Dominium, Z in [-Page/2, +Page/2).

2. Immediately after that Page bullet (before the Segment bullet), insert:

> Each Surface owns exactly one vertical Page in Dominium 1.x. Additional shells, deep volumes, or orbital shells are represented as separate Surfaces or logical spaces, not by extending Z beyond this range.

3. In the **Chunks** bullet (where you describe 16×16×16 m and 32³ terrain caches), append one sentence:

> Terrain caches are derived, non-canonical acceleration structures; they are never the primary definition of terrain on disk.

4. In the introductory paragraph to Section 2.3 (where you define Plank/Point/Step/etc.), leave the naming as-is, but do not introduce any references to physical Planck units. No change other than the additions above.

---

## 5. Directory overview vs contract

In Section **3. Repository Overview**, at the very top of the section (just after the `## 3. Repository Overview` heading and before the line “Top-level structure (conceptual):”), insert a short disclaimer:

> This section is a high-level overview only. The authoritative and machine-checkable directory layout and semantics are defined in `/docs/spec/DIRECTORY_CONTRACT.md`. In any conflict, the spec file is the source of truth.

Do not otherwise change the directory listing.

---

## 6. Build numbers and determinism

In Section **4. Building**, subsection **4.1 Modern Platforms**, after the paragraph:

> On every successful build:
> 
> - Global build number incremented in `.dominium_build_number`.
> - Generated header written at `build/generated/dom_build_version.h` with:  
>   - Major/minor/patch  
>   - Build number  
>   - Git commit hash (if available)  
>   - Timestamp (for diagnostics; not used in simulation)

append a new paragraph:

> Build numbers and timestamps are diagnostic only and never appear in engine-controlled formats or influence simulation behaviour. Different builds of the same commit must still produce bit-identical simulation results for the same inputs and content.

No other changes in this section.

---

## 7. Modding and binary plugins determinism

In Section **6. Modding**:

1. Find the bullet that starts:

> Binary plugins (when allowed) must use the documented C plugin ABI and are versioned separately.

After that sentence, append:

> Binary plugins are bound by the same determinism constraints as the core: no direct use of system time, system RNG, threads that mutate engine state outside tick phases, or floating point in any path that affects simulation state.

2. In the description of `content.lock` earlier in the README (Section **7.1 Save File Structure**, where you describe `content.lock` as listing exact content packs and mod versions), add one clarifying sentence at the end of that bullet:

Locate:

> `content.lock` -> lists exact content packs and mod versions (id/version/hash); used to reconstruct registries deterministically.

Append:

> On loading a universe, the engine verifies that the active content set exactly matches `content.lock`; mismatches are treated as fatal until reconciled.

---

## 8. Data format versioning and packing

In Section **7. Data Formats**:

1. Under the “Explicit versioning” sub-bullet, after:

> File headers contain magic plus version  
> Chunk sections are TLV (type-length-version) so new sections can be added without breaking older readers

add another sub-bullet:

> Existing on-disk versions are immutable contracts. Any behavioural or layout change requires a new on-disk version and a documented migration path; silently changing the meaning of an existing version is forbidden.

2. After the bullet:

> Alignment/padding rules documented; no implicit compiler padding relied upon

add:

> No reliance on platform-specific struct packing pragmas is allowed in the canonical format definitions; disk layouts are specified in terms of explicit field sizes, and implementations must conform to those layouts.

Keep indentation consistent.

---

## 9. Platform + renderer matrix becomes normative

In Section **9. Platform + Renderer Matrix**:

1. At the very start of the section, immediately after the `## 9. Platform + Renderer Matrix` heading and before the first sentence, insert:

> This section is the normative matrix for platform and renderer targets. Other references to platforms or renderers in this README are descriptive; in any conflict, this matrix defines the supported set.

2. Ensure that the platform list here includes everything you currently list elsewhere (SDL1, SDL2, Win32, Win16, Win32s, Win9x, NT3–11, macOS 7–9 Classic/Carbon, macOS X+, POSIX, X11, Wayland, DOS, CP/M-80/86, Linux/BSD, Android) and that this list is not contradicted by earlier bullets. If there are minor naming inconsistencies between earlier lists and Section 9, standardize the naming to match Section 9 and adjust earlier sections to refer generically to “platform backends (see Section 9)” rather than maintain independent lists.

Concretely:
- In Sections **2.4 Universal Modularity** and **2.5 Platform Breadth**, do not maintain full independent platform lists; either keep them high-level or explicitly say “see Section 9 for the full platform/render matrix” while keeping the rest of the text intact.

---

## 10. Installer, launcher, and save locations

In Section **10. Installer + Launcher**:

1. After the three installation modes bullets (“Portable”, “Per-user”, “All-users”) and the paragraph describing setup/installer, insert a short paragraph that clarifies where saves live:

> In ‘per-user’ and ‘all-users’ modes, universes, saves, and per-user configs are stored outside the installation tree in user-specific locations (for example, under profile directories). In ‘portable’ mode, all data lives under a single directory tree alongside the binaries.

2. Do not introduce platform-specific paths; keep it conceptual.

---

## 11. Keep everything else unchanged

Do not change:

- Headings or section numbers.
- The overall order of sections.
- The general tone and style of the document.

Only apply the edits described above. If you need to standardize minor wording to keep lists consistent (especially for platforms and renderers in Sections 2.4, 2.5, and 9), do so minimally and in favour of Section 9 being the authoritative list.

```

### 20.3 Exact Codex Prompt 2 — Unified Ports

```text
# CODEX PROMPT — Integrate Ports Into Unified Structure

You are editing the existing root `README.md` for the Dominium/Domino project.

**Goal:** remove the idea that ports live in separate directory trees and instead rewrite the README so that:

1. All platforms share one unified source tree.  
2. Retro/limited platforms compile from the **same code** using compile-time feature flags and capability manifests.  
3. No port is allowed to maintain an alternative structure or parallel variant of the code.  
4. `/ports/` becomes optional *metadata and build-config only*, not an alternate implementation directory.  
5. All functionality reductions are handled through **graceful degradation** and capability detection, without impacting upstream code paths.  
6. The engine and runtime never rely on per-port divergences.

Make the following specific changes:

---

## **1. Rewrite any language suggesting ports use separate directories or parallel systems**

Locate all text in the README that currently states or implies:

- Ports live in `/ports/<target>/`
- Ports contain separate code paths or separate source trees
- Retro targets have “their own build flows”
- Ports are built as discrete, segregated systems

Replace those statements with wording that conveys:

- All ports compile from the **same unified directory hierarchy**.
- Ports consist only of:
  - build configurations  
  - capability descriptors  
  - minimal platform shims where required  
- Ports never fork or override canonical structure.
- Degraded features disable themselves automatically when platform capability tables indicate they are unavailable.

Use clear language such as:

> All platforms build from the same source tree. Ports do not maintain separate code or directory structures. Platform-specific behaviour is expressed only through thin shims, compile-time flags, and capability tables, never through divergent implementations.

---

## **2. Update Section 2.4 (“Universal Modularity”) + Section 2.5 (“Platform Breadth”)**

Add explicit statements:

- All backends must operate inside the same codebase and follow the same directory contracts.
- Missing features degrade gracefully without altering engine behaviour.
- Ports cannot introduce platform-specific behaviour that modifies canonical simulation semantics.
- Ports must never fork or reimplement engine or runtime systems.

---

## **3. Replace the entire “Retro Platforms” subsection in Section 4.2**

Remove the idea of “Retro build flows under `/ports/<target>/`”.

Replace that subsection with:

> Retro and constrained platforms compile the same engine and runtime code via capability-restricted builds. All platform variance is expressed through capability tables and minimal shims for windowing, IO, and input. No platform has a separate directory tree or alternate engine implementation.

Add:

> The `/ports/` directory contains only platform metadata, build configurations, and capability descriptors. It must not contain engine or runtime source code.

---

## **4. Replace or modify the Section 9 “Platform + Renderer Matrix” introduction**

Add a sentence:

> All platforms and renderers use a single unified codebase. Any platform lacking features degrades gracefully through the capability system; no port maintains separate divergent source trees.

---

## **5. Modify the Repository Overview accordingly**

In Section 3 (“Repository Overview”):

- Remove or rewrite references to `/ports` as if they contain “per-platform source”.
- Replace with:

> `/ports` — optional platform metadata, capability descriptors, and build configurations. No code or behaviour lives here; all platforms share the same source hierarchy.

---

## **6. Clarify in Section 11 (“Contributing”)**

Add one bullet:

> No platform may introduce or maintain divergent code paths outside the allowed platform-shim and capability system. All ports must operate within the single unified directory structure and must not fork or override upstream components.

---

## **7. Do not change anything else**

- Keep headings, section numbers, tone, and style.
- Apply only the changes explicitly listed above.
- Do not restructure the README beyond these modifications.

---

**Perform these edits and output the updated README.**

```

### 20.4 Exact Codex Prompt 3 — Cleanup

```text
You are editing the existing root README.md for the Dominium/Domino project that I just pasted.

Goal: apply a small set of targeted cleanups and clarifications. Do NOT change headings, section numbers, overall tone, or the ports/unified-structure semantics you already added. Only make the edits described below.

---

1. Remove the duplicated “Dominium is a game…” block near the top

Right after the first “This repository includes:” list (the one with:

- **Domino Engine** - deterministic C89 simulation core and IO
- **Dominium Game Runtime(s)** ...
- **Content Packs** ...
- **Tools & Editors** ...
- **Ports** - platform metadata, capability descriptors, and build configurations ...
- **Specifications** ...
- **Modding API & SDK** ...

there is a second redundant block that starts with:

> Dominium is a game running on the Domino engine.  
> The official game is one compatible implementation atop it.  
> Determinism permeates physics, AI, networks, world updates, rendering order, mod execution, and replay.

and then has a second “This repository includes:” list with slightly different wording.

Delete this entire second block, from the line:

> Dominium is a game running on the Domino engine.

down through the end of the second “This repository includes:” bullet list (ending at the line that mentions `**Modding API** — deterministic, forward-compatible, sandboxed`).

Keep only the first “This repository includes:” block.

---

2. Clarify “Future systems” and remove undefined “embedded”

In the introductory list near the top, find the bullet:

- `- Future systems (WASM/Web, consoles, embedded)`

Replace it with:

- `- Future systems (WASM/Web and consoles via frontends built on the same engine ABI)`

Do not reintroduce “embedded” anywhere else.

---

3. Make the network model explicitly lockstep-first

In Section “5. Running”, subsection “5.1 Headless Server”, at the end of that subsection there is a sentence:

> Network layer manages deterministic lockstep/rollback.

Replace that entire sentence with:

> The canonical network model is deterministic lockstep. Rollback and prediction (when used by runtimes) must always converge to the same state as pure lockstep for the same inputs and content.

Do not change anything else in 5.1 or 5.2.

---

4. Make the contributing determinism bullet point back to Section 2.1

In Section “11. Contributing”, there is a bullet that currently reads:

> **Determinism preserved** - no floats in `/engine`; no nondeterministic APIs (system time, threads, I/O) in core or scripted interfaces.

Replace that bullet with:

> **Determinism preserved** - changes must not violate the determinism rules defined in Section 2.1 (no floats in engine-facing simulation paths, and no nondeterministic APIs such as system time, threads, or uncontrolled I/O in core or scripted interfaces).

Leave all other bullets in Section 11 as they are, including the later “Strict prohibitions” block and the ports/unified-structure bullet.

---

5. Do not change anything else

Do not add or remove any other text. Do not modify the ports/unified source tree semantics, the `/ports` description, or any of the determinism/scale/format details beyond what is explicitly described above.

Apply only these edits and output the updated README.md.

```

### 20.5 Final README Snapshot Pasted by User

```markdown
# DOMINIUM & DOMINO

## A Deterministic, Multi-Scale, Multi-Platform Simulation Game and Engine

Dominium on Domino is a **fully deterministic**, **integer-math**, **platform-agnostic**, **modular** engine and game designed to run identically across:


- Modern systems (Windows NT family, Linux, macOS X)
- Legacy systems (Win9x, Win3.x, Win16, DOS, macOS 7-9, OS/2 strata via shims)
- Future systems (WASM/Web and consoles via frontends built on the same engine ABI)
- Headless/server nodes (single or clustered)

**Domino** is the deterministic simulation engine core.  
**Dominium** is the official game and tooling layer running on top of Domino.

The official game is *one* compatible implementation atop Domino. Determinism permeates:

- Physics and environmental simulation
- AI and job systems
- Networks (power, fluids, logic)
- World updates and chunk streaming
- Mod execution and scripting
- Replay and desync detection

This repository includes:

- **Domino Engine** - deterministic C89 simulation core and IO
- **Dominium Game Runtime(s)** - content-agnostic gameplay logic on top of Domino
- **Content Packs** - first-party data packs (materials, recipes, worldgen, assets)
- **Tools & Editors** - world tools, asset pipelines, debug/inspection tools
- **Ports** - platform metadata, capability descriptors, and build configurations for DOS, Win3.x, Win9x, macOS Classic, WASM, etc.; all build from the same unified source tree
- **Specifications** - binding behaviour contracts (determinism, formats, APIs)
- **Modding API & SDK** - deterministic, forward-compatible, sandboxed extension layer

All behaviour derives from written specifications. No code exists without a contract.

---

## 1. Project Vision

Dominium aims to:

1. **Produce universally reproducible simulation**  
   Any two machines, of any era or ISA, must yield identical state per tick, given the same executable, content set, inputs, and timeline.
2. **Handle extreme spatial scales with a single coherent hierarchy**  
   From sub-meter structural detail to full planetary surfaces:  
   - Fixed technical scale (see Section 2.3) from 1/65,536 m ("Plank") up to 16,777,216 m ("Surface").  
   - Planet surfaces are 2^24 m toroidal squares with +/-2048 m vertical range.
3. **Execute on decades of hardware (286-class upward)**  
   The full Domino engine targets 286-class-and-newer systems. Limited tooling and experimental frontends may exist for earlier 8-bit platforms (for example, CP/M-80), but they do not host the complete world simulation.  
   - Core simulation stays within strict C89, fixed-point integer math.  
   - Older targets may reduce *fidelity* of rendering and UX, but never alter simulation results.
4. **Be maximally modifiable without weakening determinism**  
   - Content packs and mods extend registries and scripts.  
   - Mods cannot change core rules, floating-point behaviour, or ordering guarantees.
5. **Support interchangeable 2D/3D vector and raster renderers at runtime**  
   - Rendering is treated as a pure projection of deterministic world state.  
   - Multiple backends: modern (GL/VK/DX/Metal), retro (VGA/EGA/MDA), vector, software.
6. **Model surface + orbital domains with discrete, graph-based mechanics**  
   - Planetary surfaces use continuous fields + discrete constructions.  
   - Orbital/space simulation uses rails-based orbital graphs, transfer arcs, docking graphs.
7. **Provide a unified construction system**  
   - Block components, slabs, vectors (rails/roads/pipes/tunnels), cut/fill, multi-layer buildings.  
   - All grounded in the same world coordinate and segmentation scheme.
8. **Maintain strict separation between physical surfaces and logical orbital/space graphs**  
   - Surfaces are continuous 3D fields (phi, materials, media).  
   - Orbits are discrete graph nodes/edges with integer dynamics.
9. **Allow deterministic clustered multiplayer**  
   - Lockstep or rollback-based synchronization at tick level.  
   - Servers and clients operate under the same simulation contract.
10. **Provide engineering clarity for multi-decade viability**  
    - Formats and APIs are versioned and documented.  
    - Migration paths are explicit; no silent breakage.

Dominium is engineered to outlive its original hardware.

---

## 2. Core Philosophy

### 2.1 Determinism

Hard constraints for the **engine core** (`/engine`):

- **No floating point is allowed in any code that mutates canonical simulation state or engine-controlled serialized formats.**
  - No `float` or `double` in `/engine` or in any engine-controlled on-disk formats.
  - All continuous quantities are fixed-point integers:  
    - Runtime: **Q16.16** (`fix32`) for general simulation.  
    - Save-local positional: **Q4.12** (`fix16`) for coordinates inside 16 m chunks.  
    - Accumulators and reductions use 64-bit ints where needed.
- Tools, renderers, and non-authoritative analysis may use floating point freely, as long as float-derived values never flow back into engine state or engine-controlled file formats.
- **World addressing:**  
  - Surfaces: 2^24 m x 2^24 m toroidal square.  
  - Vertical range: single Page of 4096 m (Z in [-2048, +2048)).  
  - Horizontal space segmented into 256x256 segments (2^8 per axis), each 2^16 m wide.  
  - Runtime positions: `SimPos = {segment_x, segment_y, Q16.16 local x, Q16.16 local y, Q16.16 z}`.
- **Deterministic ordering across phases:**  
  - Input, pre-state, ECS systems, networks, fluids, merge, postprocess, finalize.  
  - Entity processing order is stable (ascending EntityId).  
  - Network nodes/edges processed in stable ID order.
- **RNG discipline:**  
  - Procedural content uses stateless coordinate hashing (function of seeds + coordinates).  
  - Time-evolving solvers (weather, hydrology, AI) use named RNG streams (`RNGId` to `RNGState`).  
  - RNG states are fully serialized in metadata and are independent of chunk load order.  
  - RNG streams are only advanced during deterministic tick phases; debug, UI, and rendering layers must not advance engine RNG streams.
- **Replay and hashing:**  
  - Replay streams record input events and timing.  
  - Engine can recompute state hashes per tick for validation.  
  - Cross-platform builds must agree on hashes for the same content/universe.

The **runtime/renderer/launcher** layers may use floats internally, but they never feed float-derived values back into engine state or save files.

### 2.2 Tick Phasing and Ordering

The global simulation tick has **immutable phases** in the engine:

1. **Input**  
   - External commands sampled/applied as canonical events.  
   - Network inbound events reconciled to tick boundary.
2. **Pre-State**  
   - Resolve queued structural changes (spawns/despawns, worldgen openings).  
   - Apply configuration changes scheduled from previous ticks.
3. **Simulation Lanes (ECS systems)**  
   - Movement and kinematics  
   - AI and job systems  
   - Machines and production graphs  
   - Local scripts (deterministic subset)  
   - All run in defined, static order over entity IDs.
4. **Networks**  
   - Electrical networks solved (voltage/current).  
   - Hydraulic networks solved (pressure/flow).  
   - Logic/signal networks updated (combinational and sequential).  
   - Network order is fixed and independent of spatial streaming.
5. **Fluids & Fields / Merge**  
   - FluidSpaces (rooms, tanks, pipes) compartments updated.  
   - Atmo/hydro macroscopic grids stepped.  
   - ThermalSpaces updated.  
   - Merges consistent with network outputs and ECS.
6. **Post-Process**  
   - Rebuild spatial acceleration structures.  
   - Mark chunks dirty for meshing.  
   - Schedule IO and mesh jobs (purely cache effects).
7. **Finalize**  
   - Prepare state for next tick (RNG states stored, logs emitted).  
   - Replay/event logs flushed.

No system may reorder or bypass phases. Parallelism is allowed only within phases, and only for tasks that do not mutate shared state (for example, meshing, IO) or that commit in a fixed, serialized order.

Any operation that schedules work for a future tick (timers, delayed spawns, transport completions) must do so via the Pre-State phase's queueing mechanism; no system may directly mutate future-tick state.

Parallel execution within a phase may only operate on disjoint subsets of state and must commit results in a globally deterministic order (for example, by sort-by-ID before commit).

### 2.3 Spatial Hierarchy (Technical Scale)

The engine uses a **single, unified, metric scale hierarchy** for space and time references, tuned for the simulation needs. All units are metres and conceptually cubic (3D), even if stored sparsely.

- **2^-16 m - Plank**  
  Minimal unit for internal precision (not directly exposed to gameplay). Useful for fine SDF and field resolution.
- **2^-12 m - Point**  
  Sub-millimetre resolution for exact geometry and collision math where needed.
- **2^-8 m - Step**  
  1/256 m; base save precision for static positions (`Q?.8`/`Q4.12`), about 3.9 mm granularity.
- **2^-4 m - Sixteenth**  
  1/16 m; used for fine local grids, ramps, detailed building layout.
- **2^0 m - Block**  
  1 m; primary gameplay block/tile unit (for building placement, grids).
- **2^4 m - Chunk**  
  16 m; core cubic chunk unit for streaming and meshing.  
  - Chunks are 16x16x16 m.  
  - Terrain caches: 32^3 samples (0.5 m spacing). Terrain caches are derived, non-canonical acceleration structures; they are never the primary definition of terrain on disk.
- **2^8 m - Region**  
  256 m; groups 16x16 chunks in X/Y. Basic hydrology and environment cell size.
- **2^12 m - Page**  
  4096 m; vertical domain per surface. For Dominium, Z in [-Page/2, +Page/2).  
  Each Surface owns exactly one vertical Page in Dominium 1.x. Additional shells, deep volumes, or orbital shells are represented as separate Surfaces or logical spaces, not by extending Z beyond this range.
- **2^16 m - Segment**  
  65,536 m; horizontal segments. Each of the 256x256 segments maps directly to Q16.16 integer part.
- **2^20 m - Sector**  
  1,048,576 m; used to define atmo/hydro grids and logical LOD partitions.
- **2^24 m - Surface**  
  16,777,216 m; full horizontal extent of a surface, toroidally wrapped.

Surfaces are **sparse collections** of chunks and fields:

- No monolithic global 3D array exists.
- Geometry is defined by procedural functions plus local overrides and volumes.
- Underground structures and multi-level constructs are represented via SDF/fields and object/volume graphs, not by fixed layered tiles.

### 2.4 Universal Modularity

All subsystems are **hot-swappable** at the configuration/content level, behind stable contracts:

- **Rendering backends** (see Section 9 for the full matrix)  
  - Software rasterizers  
  - Vector renderers  
  - OpenGL 1.x/2.x, DirectX 9/11/12, Vulkan 1.x  
  - VGA/EGA/CGA/MDA/Hercules, VESA modes  
  - QuickDraw, Carbon/Quartz, Metal, WinG (where appropriate)  
  - Headless (no rendering)
- **Audio backends**  
  - Configurable abstraction per platform.
- **Platform backends** (see Section 9 for the full platform/render matrix)
- **Tools and data packs**  
  - Share common IO and registry libraries from `/engine`.
- **Scripting**  
  - Deterministic subset of Lua or a custom "Dominium Script".  
  - No direct access to system clock, threads, real RNG, or floating point.

Backends adapt to core contracts, never the reverse.

All backends must operate inside the same codebase and adhere to the same directory contracts. Missing features degrade gracefully through the capability system without altering engine behaviour, and ports cannot introduce platform-specific behaviour that modifies canonical simulation semantics or reimplements engine/runtime systems.

### 2.5 Platform Breadth

Engine core compiles under:

- **Strict C89** (no compiler extensions, no non-portable assumptions).
- **No libc extensions** in the core (only a well-defined subset of `stdlib`/`string` etc.).

Higher layers:

- Runtime, launcher, tools: **C++98** only, with a constrained subset of STL where allowed.
- Platform-specific behaviour is contained in:  
  - `/runtime/` (frontends)  
  - `/launcher/`  
  - `/tools/`  
  - Platform shims configured via `/ports/` metadata (minimal glue only; no engine/runtime code lives there)

All platforms must adhere to the same engine ABI and file formats.

All platforms build from the same unified source hierarchy. Platform-specific behaviour is expressed only through thin shims, compile-time flags, and capability tables; ports must never fork or override engine or runtime systems.

---

## 3. Repository Overview

This section is a high-level overview only. The authoritative and machine-checkable directory layout and semantics are defined in `/docs/spec/DIRECTORY_CONTRACT.md`. In any conflict, the spec file is the source of truth.

Top-level structure (conceptual):

- `/docs` - specifications, formats, policies, style, building
- `/engine` - deterministic engine core (C89, fixed-point, no floats)
- `/runtime` - high-level game runtimes (C++98 frontends; e.g., CLI, SDL, editor)
- `/content` - official content packs (materials, recipes, worldgen, assets)
- `/mods` - third-party deterministic mods and content packs
- `/tools` - editors, converters, inspection tools, pipelines
- `/tests` - unit tests, replay determinism tests, integration and performance tests
- `/external` - vendored dependencies (Lua subset, platform libs, zlib, etc.)
- `/build` - build trees, generated headers, CI artefacts
- `/package` - installer scripts, retro media images and packaging
- `/scripts` - automation, CI helpers, migration tools
- `/ports` - optional platform metadata, capability descriptors, and build configurations. No code or behaviour lives here; all platforms share the same source hierarchy.

Within `/docs/spec/` the authoritative directory contract lives in:

- `/docs/spec/DIRECTORY_CONTRACT.md`

This README is descriptive; the spec files are normative.

---

## 4. Building

### 4.1 Modern Platforms

Primary workflow: **CMake** targeting modern compilers.

```bash
mkdir build
cd build
cmake ..
cmake --build .
```

Core expectations:

- `/engine` builds as a C89 static library (for example, `libdom_engine.a`).
- `/runtime/dom_cli` and `/runtime/dom_sdl` (or equivalent) link against `libdom_engine`.
- `/tools` link against engine IO libraries for format access.

On every successful build:

- Global build number incremented in `.dominium_build_number`.
- Generated header written at `build/generated/dom_build_version.h` with:  
  - Major/minor/patch  
  - Build number  
  - Git commit hash (if available)  
  - Timestamp (for diagnostics; not used in simulation)

Build numbers and timestamps are diagnostic only and never appear in engine-controlled formats or influence simulation behaviour. Different builds of the same commit must still produce bit-identical simulation results for the same inputs and content.

### 4.2 Retro Platforms

Retro and constrained platforms compile the same engine and runtime code via capability-restricted builds. All platform variance is expressed through capability tables and minimal shims for windowing, IO, and input. No platform has a separate directory tree or alternate engine implementation.

The `/ports/` directory contains only platform metadata, build configurations, and capability descriptors. It must not contain engine or runtime source code.

---

## 5. Running

### 5.1 Headless Server

Typical headless binary (example naming):

```bash
./dom_cli --universe path/to/universe --surface 0 --ticks 0 --listen 0.0.0.0:PORT
```

- `--universe`: path to universe directory (root of saves).
- `--surface`: surface id/index to simulate.
- `--ticks`: number of ticks to run (0 = run indefinitely).

The canonical network model is deterministic lockstep. Rollback and prediction (when used by runtimes) must always converge to the same state as pure lockstep for the same inputs and content.

### 5.2 Client

Typical client binary (example):

```bash
./dom_sdl --universe path/to/universe --surface 0
```

- Client connects to a server (local or remote) or runs in local-only mode.
- Rendering backend selected via config/CLI.
- All game state is driven by engine state; no client-side simulation divergence is allowed.

The launcher is optional:

- The game must run with direct invocation of runtime binaries.
- Launcher provides orchestration, configuration UI, and multi-instance management but has no simulation semantics.
- Clients and servers operate in deterministic lockstep; divergences (desync) are detected via state hashes and can be replayed/debugged.

---

## 6. Modding

A mod is a content plus optional code bundle with strict contracts.

Typical mod layout:

- `mod.json`  
  - Mod id (UUID/namespace), version, author  
  - Dependencies (other mods/content packs)  
  - Required engine/runtime version
- `content/`  
  - Prefabs, materials, recipes, worldgen configs  
  - Deterministic data tables (JSON/binary formats)
- `scripts/`  
  - Deterministic Lua subset or Dominium Script  
  - No direct I/O, time, threads, or random; all via engine-provided APIs
- `assets/`  
  - Textures, sprites, meshes, audio, etc. (where applicable)

Loading order:

- Base content packs
- Official DLC packs
- Mods, ordered by stable UUID and dependency resolution

Mods may:

- Register new materials, recipes, volume types.
- Register new worldgen recipes and solvers (via deterministic APIs).
- Extend gameplay systems as long as they obey engine deterministic interfaces.

Mods may not:

- Patch binaries or change the engine's fixed-point formats.
- Introduce nondeterministic behaviour (no real RNG, no system time).
- Violate directory contracts or bypass engine IO.
- Binary plugins (when allowed) must use the documented C plugin ABI and are versioned separately. Binary plugins are bound by the same determinism constraints as the core: no direct use of system time, system RNG, threads that mutate engine state outside tick phases, or floating point in any path that affects simulation state.

---

## 7. Data Formats

All engine-controlled formats obey:

- Integer math only
- Fixed-point positions (Q16.16 and Q4.12)
- All physical quantities stored as scaled integers
- Explicit layout  
  - Packed C structs with explicit field sizes  
  - Alignment/padding rules documented; no implicit compiler padding relied upon  
  - No reliance on platform-specific struct packing pragmas is allowed in the canonical format definitions; disk layouts are specified in terms of explicit field sizes, and implementations must conform to those layouts.
- Little-endian canonical representation  
  - All multi-byte fields are little-endian on disk  
  - Platforms must convert as needed
- Explicit versioning  
  - File headers contain magic plus version  
  - Chunk sections are TLV (type-length-version) so new sections can be added without breaking older readers  
  - Existing on-disk versions are immutable contracts. Any behavioural or layout change requires a new on-disk version and a documented migration path; silently changing the meaning of an existing version is forbidden.
- No pointers in serialized data  
  - All references are via IDs or relative indices  
  - No raw memory addresses appear in files
- Integrity and replay metadata  
  - Optional CRCs on sections or entire files  
  - Replay hashes and tick markers embedded in metadata for validation

### 7.1 Save File Structure (Universe / Surface / Region / Chunk)

A save "universe" directory contains:

- `universe.meta` -> UniverseMeta (version, universe_seed, etc.)
- `content.lock` -> lists exact content packs and mod versions (id/version/hash); used to reconstruct registries deterministically. On loading a universe, the engine verifies that the active content set exactly matches `content.lock`; mismatches are treated as fatal until reconciled.

Per-surface directories:

- `surface_<id>.meta` -> SurfaceMeta (seed, recipe id, RNG states, etc.)
- `regions/` -> region files with chunk blobs

Region file structure:

- RegionHeader  
  - Magic `REGN`  
  - Version  
  - Chunk count  
  - Array of `ChunkEntry { ChunkKey3D, offset, length }`
- Followed by `chunk_count` chunk blobs.

Each chunk blob:

- Sequence of `ChunkSectionHeader` plus payload blocks:  
  - `CHUNK_SEC_TERRAIN_OVERRIDES` (1)  
  - `CHUNK_SEC_OBJECTS` (2)  
  - `CHUNK_SEC_EDIT_OPS` (3)  
  - `CHUNK_SEC_LOCAL_VOLUMES` (4)  
  - `CHUNK_SEC_LOCAL_ENV_STATE` (5)  
  - `CHUNK_SEC_LOCAL_NET_STATE` (6)  
  - `>=1000` reserved for mod and future sections

Chunk/subchunk "microgrids" exist only as caches for meshing and local physics; the canonical world geometry is the combination of:

- Procedural phi from recipes
- Edit operations
- Volume instances
- Fluid/thermal and network state

Saves contain:

- Entity/component state
- Network state (pressures, voltages, flows)
- FluidSpaces/ThermalSpaces state (if applicable)
- Prefab references and overrides
- Messages/events queued across ticks
- Chunk overrides and EditOps
- Optional replay delta logs for time travel/debugging

---

## 8. Surface + Space Architecture

Two primary domains exist, sharing the same core engine but different solvers and representations.

### 8.1 Physical Domains (Surfaces)

- Planet surfaces (2^24 m toroidal squares)
- Underground volumes (caves, strata, basins)
- Oceans, lakes, rivers, canals
- Sparse terrain fields (signed distance fields, material fields)
- Structural microgrids (buildings, slabs, supports)
- Vector networks: rails (trains, trams), roads, conveyors, pipes/tunnels
- Cut/fill terrain layers and excavation volumes

Physical space is:

- Defined by fields (phi, materials, media) at arbitrary points.
- Sampled via deterministic functions and local overrides.
- Connected to discrete constructions (objects, volumes, networks).

### 8.2 Logical Domains (Orbital/Space)

- Discrete orbital tracks and arcs
- Transfer windows/manoeuvre graphs
- Docking graphs (stations, platforms, vehicles)
- Asteroid belts as discrete resource graphs
- Stations, ships, satellites
- Lagrange nodes and special points

Deterministic transfers:

- Orbital mechanics treated as a rails-based graph simulation (integer time steps, precomputed or integer-integrated ephemerides).
- Space simulation uses integer time, integer/fixed ephemeris and positions, no uncontrolled floating-point dynamics.
- Transitions between surface and space domains are well-defined ports and graph edges (elevators, launch pads, space elevators, etc.), always deterministic and reversible.

---

## 9. Platform + Renderer Matrix

This section is the normative matrix for platform and renderer targets. Other references to platforms or renderers in this README are descriptive; in any conflict, this matrix defines the supported set. All platforms and renderers use a single unified codebase; any platform lacking features degrades gracefully through the capability system, and no port maintains separate divergent source trees.

Dominium supports a matrix of platform backends and renderers.

Platforms: SDL1, SDL2, Win32, Win16, Win32s, Win9x, NT3-11, macOS 7-9 (Classic/Carbon), macOS X+, POSIX, X11, Wayland, DOS, CP/M-80/86 (tooling/limited frontends), Linux/BSD, Android.

Renderers: software rasterizers, vector renderers, OpenGL 1.x/2.x, DirectX 9/11/12, Vulkan 1.x, VGA/EGA/CGA/MDA/Hercules, VESA modes, QuickDraw, Carbon/Quartz, Metal, WinG (where appropriate).

Any platform can run any compatible renderer or headless mode and use the same save files. Renderers are pure consumers of engine state; they never change simulation results.

---

## 10. Installer + Launcher

Three installation modes:

- **Portable** - everything under a single directory; no system-wide registry entries or global config.
- **Per-user** - engine/runtime binaries shared; user-specific saves, configs, mods under profile directories.
- **All-users** - system-wide installation for multi-user environments; shared content; per-user saves and mods.

Setup/installer provides install, repair, uninstall. Repair audits manifest vs actual files; restores missing or corrupted core assets and binaries but does not overwrite user saves or mods.

In "per-user" and "all-users" modes, universes, saves, and per-user configs are stored outside the installation tree in user-specific locations (for example, under profile directories). In "portable" mode, all data lives under a single directory tree alongside the binaries.

Launcher manages:

- Multiple installed versions and ports
- Multiple universes and surfaces
- Mods and content packs
- Tools and editors
- Accounts, stats, and playtime tracking (non-intrusive)
- Server discovery and network browsing

Standard scripts (per platform; names may vary):

- `setup` -> installer/repair/uninstaller wrapper
- `dominium` -> launcher binary

The game runtime can always be executed directly; the launcher is never mandatory.

---

## 11. Contributing

Contributions must satisfy:

- **Determinism preserved** - changes must not violate the determinism rules defined in Section 2.1 (no floats in engine-facing simulation paths, and no nondeterministic APIs such as system time, threads, or uncontrolled I/O in core or scripted interfaces).
- **C89/C++98 compliance** - `/engine` uses C89 only; `/runtime`, `/launcher`, `/tools` use C++98; limited STL as documented.
- **Specification-first changes** - behavioural or format changes require spec updates in `/docs/spec/` before or alongside code; directory contracts and data formats must be updated.
- **Tests** - new features require unit tests where reasonable, replay determinism tests (hashes/states over fixed sequences), integration tests for new systems or formats.
- **Documentation** - README and relevant docs updated for new public features; internal developer notes updated for non-public changes.
- No platform may introduce or maintain divergent code paths outside the allowed platform-shim and capability system. All ports must operate within the single unified directory structure and must not fork or override upstream components.
- **Strict prohibitions:**  
  - No floats in simulation or core IO.  
  - No platform API calls from `/engine`.  
  - No game logic in `/engine` - only generic engine capabilities.  
  - No hidden global state that affects determinism.

---

## 12. License

Licensing is tiered:

- **Engine core (Domino)** - target: permissive open source (exact license TBD); allows linking into proprietary runtimes while preserving open engine.
- **Game assets (Dominium content)** - proprietary or Creative Commons (for example, CC-BY-NC) per pack; exact terms per content pack documented.
- **Tools** - open source where possible (likely same as engine).
- **Mods** - owned by their authors; distribution terms per mod; determinism rules still enforced by engine.

Authoritative legal text: `/docs/legal/LICENCE.md` and related legal documents.

---

## 13. Status

- **Completed / Solidified:** deterministic kernel specification; fixed-point numeric model and world scale hierarchy; world addressing scheme (Segments/Regions/Chunks/Pages); ECS foundation and entity ID rules; canonical phasing/order of simulation tick; basic serialization design (TLV, Region/Chunk, Universe/Surface meta); preliminary chunk/subchunk world formats; content registry design (materials, recipes, volumes); mod loading and ordering model; platform and renderer abstraction frameworks (design-level).
- **In Development / Planned:** full renderer integration across multiple backends; cut/fill terrain implementation over SDF plus EditOps; hydrology and atmosphere solvers (macro fields); FluidSpaces and compartmental fluid/thermal systems; orbital logistics and space/rail graphs; worker/robot and agent AI stacks; deterministic clustered server infrastructure; editor suite (terrain, networks, buildings, systems); retro platform parity (DOS, Win3.x, Win9x, macOS Classic, etc.); unified launcher ecosystem for all ports and runtimes.

Concrete implementation status is tracked in `/docs/spec/MILESTONES.md` and the issue tracker/project boards.

---

## 14. Community

Documentation: `/docs/design/` and `/docs/spec/`  
Roadmap: `/docs/spec/MILESTONES.md`  
Issues and tasks: GitHub issue tracker and project boards

Community infrastructure: Discord, dev-blog, and mailing lists to be formalized once the core engine is sufficiently stable.

---

## 15. Acknowledgements

Dominium draws influence from deterministic simulation traditions in games and scientific computing; retro engineering practices emphasizing hardware frugality and predictable behaviour; long-term archival design philosophies and format stability; the modding communities of sandbox and factory games.

---

## 16. Final Note

Dominium is an attempt at a universal deterministic simulation engine and game ecosystem:

- Cross-era hardware
- Perfect or near-perfect reproducibility
- Planetary plus orbital scale
- Unlimited but safe mod extensibility
- Long-term archival survivability

This README will evolve as the specifications advance. The definitive rules, formats, and behaviour contracts always reside in `/docs/spec`.

```

