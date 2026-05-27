# Aggregator Packet — Dominium Codex Platform Renderer API Plan

## 1. Packet Metadata

- Chat label: Dominium Codex Platform Renderer API Plan
- Date anchor: 2026-05-27 Australia/Melbourne
- Source scope: THIS CHAT ONLY
- Coverage: full for visible chat context and previous Context Transfer Packet; repo contents unverified
- Confidence: 4/5
- Staleness risk: medium
- Merge priority: high
- Main limitations: uploaded repo archive was not inspected; prompt plans are not implementation evidence; future AAA material is roadmap unless confirmed.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat was about turning a large Dominium/Domino engine architecture effort into ready-to-run Codex prompts and then preserving the entire chat state as a reusable handoff package. The concrete product of the chat is not engine code; it is an implementation plan for Codex CLI / VS Code Codex running GPT-5.2 inside the repository at `c:\Inbox\Git Repos\dominium`. The Codex runtime constraints were explicit: Windows, full filesystem access, approval policy NEVER, network enabled but no dependency downloads unless explicitly approved, and the repository must remain buildable after each prompt.

The user first requested a prompt pack for finishing platforms, renderers, and APIs. After an initial questionnaire and a detailed user answer, the user uploaded `/mnt/data/dominium.zip`. The prior assistant did not actually inspect the archive before producing prompt plans, so all repo-specific claims remain verification items unless they came directly from the user. The user then supplied a separate existing “MASTER CODEX PROMPT PLAN” of prompts 1-14 for deterministic engine-core refactoring. That master plan covers invariants, typed packets/TLV registries, deterministic scheduler phases, fields/events/messages, representation ladders, arbitrary placement, TRANS/STRUCT/DECOR, agents, graph toolkit, domains/frames/propagators, knowledge/fog/comms, and determinism regression. Later work explicitly assumes those master prompts are implemented, but this assumption is unverified.

The central active workstream is the final post-master prompt pack for platforms/renderers/APIs/product completion. Earlier assistant-generated platform/render packs, post-engine prompts 15-24, and revised prompts 15-28 were superseded. The active pack has nine larger prompts, because the user prefers fewer larger GPT-5.2 Codex runs. Prompt 1 enforces C89/C++98 baselines and ABI/vtable facades. Prompt 2 implements the capability registry, determinism grades, and launcher profiles. Prompt 3 adds CMake presets, generated config headers, null platform/renderer backends, and build metadata. Prompt 4 completes Tier-1 Win32 and Win32-headless system facets plus `domino_sys_smoke`. Prompt 5 completes the soft D0 reference renderer, DX9 present path, and `dgfx_demo`. Prompt 6 gates Tier-2 platforms/renderers for compile correctness. Prompt 7 unifies TLV-as-ABI and net handshakes. Prompt 8 adds launcher and game GUI smoke tests plus the final verify script. Prompt 9 adds changelog/release-note tooling and final polish.

The highest-impact decisions were user-mandated: Domino core remains ISO C89 forever; Dominium layer remains C++98 forever; newer standards are optional acceleration only; runtime language-standard switching is rejected; public ABI uses C ABI, POD structs, explicit function tables, and interface structs beginning with `u32 abi_version` and `u32 struct_size`; every evolvable subsystem uses a facade/backend architecture; capability registry selection must be deterministic and inspectable; determinism grades D0/D1/D2 are formalized; lockstep strict requires D0; serialization/assets/saves/replays are public ABI via a chunked/TLV container with skip-unknown and migrations; networking handshakes include build/schema/determinism/content hashes; and Codex must make detailed commits throughout.

The chat also explored future AAA readiness: advanced graphics, audio, input, AI, navigation, terrain, vehicles, economy, combat, weather, online systems, tools, setup/download, modding, and scripting. These are roadmap/spec-book candidates, not immediate implementation scope. The crucial preservation rule is that future advanced features must live behind extensions, capability flags, data formats, and compiled artifacts, not by bloating deterministic core APIs or allowing presentation output to affect authoritative simulation.

A future assistant must not lose the active nine-prompt pack, the C89/C++98 and ABI constraints, the commit discipline, the unverified status of repo inspection, or the distinction between accepted requirements and brainstorming.

For aggregation, the core fact is that this chat converged on a final active nine-prompt Codex plan after several earlier plans were superseded. The active pack starts after an assumed master deterministic engine refactor plan. It is not a generic summary; it is a precise set of implementation instructions for Codex under Windows with no approvals and no dependency downloads. The most important technical decisions are the non-negotiable language and ABI constraints: Domino core remains C89, Dominium remains C++98, optional modern standards cannot be required for correctness, and all important ABI boundaries use C ABI, POD structs, function tables, and `abi_version`/`struct_size` headers.

The package should merge into a future Project Spec Book as the canonical source for platform/render/API completion workflow, not as proof of completed code. It should also feed sections on build discipline, smoke testing, release notes/changelog process, and long-term extensibility.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Final 9-prompt active Codex pack | plan | WORKSTREAM-02 | Latest implementation plan. | FACT | 5 |
| 2 | C89/C++98 baseline forever | constraint | CONSTRAINT-06/07 | Core compatibility invariant. | FACT | 5 |
| 3 | Stable C ABI/POD/vtable boundaries | decision | DECISION-05/06 | Plugin/module safety. | FACT | 5 |
| 4 | Facade/backend + central capability registry | architecture | DECISION-07/08 | Extensible modular backend selection. | FACT | 5 |
| 5 | D0/D1/D2 determinism and lockstep D0 | determinism | DECISION-09/10 | Replay/network correctness. | FACT | 5 |
| 6 | TLV serialization as ABI | serialization | DECISION-11 | Long-term save/asset compatibility. | FACT | 5 |
| 7 | Git commit discipline | process | DECISION-15 | Changelog generation. | FACT | 5 |
| 8 | Repo archive unverified caveat | uncertainty | RISK-01 | Prevents false implementation claims. | UNCERTAIN / UNVERIFIED | 5 |

## 4. Workstream Summaries

### WORKSTREAM-01: Master deterministic engine-core refactor prompts 1-14
- Objective: Establish deterministic core primitives: packets, scheduler, fields/events, LOD, arbitrary placement, TRANS, STRUCT, DECOR, agents, graph toolkit, domains/frames/propagators, knowledge/fog/comms, and regression hardening.
- Current state: User pasted this as an existing pending prompt plan. Later post-14 work assumes it has been implemented for planning purposes, but actual repo implementation is unverified.
- Desired end state: A deterministic, quantized, replayable, non-grid-bound engine core with regression tests and no new gameplay semantics.
- Priority: high
- Decisions: No floats in deterministic core., No grid assumptions., Everything parametric, quantized, deterministic, replayable.
- Tasks: VERIFY-01, TASK-01
- Constraints: CONSTRAINT-12, CONSTRAINT-13, CONSTRAINT-14
- Artifacts: ARTIFACT-02
- Risks: RISK-01, RISK-02
- Open questions: see Open Questions Register.
- Next action: Verify repository state if implementation-specific actions are needed.

### WORKSTREAM-02: Post-master platforms/renderers/APIs/product completion prompt pack
- Objective: Produce and preserve a ready-to-run Codex prompt pack to complete platforms, renderers, APIs, build/test infrastructure, and basic launcher/game GUI smoke tests.
- Current state: Final active prompt pack contains nine large prompts, each with git commit discipline and verification gates.
- Desired end state: A repository state with enforced baseline language/ABI rules, facaded DSYS/DGFX APIs, central capability registry, Win32/Win32-headless Tier-1 platform completion, soft/DX9 Tier-1 renderer completion, Tier-2 gating, TLV-as-ABI, launcher/game GUI smokes, verify script, and changelog tooling.
- Priority: critical
- Decisions: Use final 9-prompt pack as active plan., Each prompt requires multiple changelog-ready git commits.
- Tasks: TASK-02, TASK-03, TASK-04, TASK-05, TASK-06, TASK-07, TASK-08, TASK-09, TASK-10
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-11
- Artifacts: ARTIFACT-07, ARTIFACT-08, ARTIFACT-09, ARTIFACT-10, ARTIFACT-11, ARTIFACT-12, ARTIFACT-13, ARTIFACT-14, ARTIFACT-15
- Risks: RISK-01, RISK-03, RISK-04, RISK-05
- Open questions: see Open Questions Register.
- Next action: Run Prompt 1 in Codex or, if already run, continue with the next unexecuted prompt.

### WORKSTREAM-03: API architecture: stable ABI, facades, backends, capabilities, determinism
- Objective: Make DSYS/DGFX and other evolvable systems modular, versioned, extensible, deterministic, and C89/C++98-compliant.
- Current state: Architecture was designed in discussion and embedded into Prompts 1-3 and later prompts.
- Desired end state: Every cross-module/plugin boundary is C ABI/POD/versioned; every evolvable subsystem uses baseline facade plus selectable backends; central registry controls backend selection and determinism grades.
- Priority: critical
- Decisions: C ABI only across boundaries., Every interface begins with abi_version and struct_size., Capability registry and D0/D1/D2 determinism are mandatory., Launcher profiles select features/backends, not language standards.
- Tasks: TASK-02, TASK-03, TASK-04
- Constraints: CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-15, CONSTRAINT-16
- Artifacts: ARTIFACT-09, ARTIFACT-10, ARTIFACT-11, ARTIFACT-12, ARTIFACT-13
- Risks: RISK-04, RISK-05, RISK-06
- Open questions: see Open Questions Register.
- Next action: Execute Prompt 1 and Prompt 2.

### WORKSTREAM-04: AAA future readiness roadmap
- Objective: Reserve clean architectural slots for advanced future game/engine features beyond the current prompt pack.
- Current state: Brainstormed extensively; not fully converted into implementation prompts except for extension slots in renderer/audio and general architecture constraints.
- Desired end state: Dominium can evolve over years toward AAA-grade graphics, audio, AI, navigation, terrain, vehicles, economy, combat, weather, online systems, tools, modding, and setup/distribution without architectural rewrites.
- Priority: medium-high
- Decisions: Advanced features should be extensions/capability-gated, not core API bloat., Presentation output must not feed deterministic sim.
- Tasks: TASK-11
- Constraints: CONSTRAINT-12, CONSTRAINT-13, CONSTRAINT-14, CONSTRAINT-16
- Artifacts: ARTIFACT-20
- Risks: RISK-07, RISK-08
- Open questions: see Open Questions Register.
- Next action: Do not implement now; preserve as future Project Spec Book material.

### WORKSTREAM-05: Chat-specific handoff/report packaging
- Objective: Produce a downloadable, shareable, reusable report package for this old chat, suitable for future aggregation and Project Spec Book construction.
- Current state: This current response creates the requested files and ZIP package.
- Desired end state: Seven report files plus a ZIP, with stable IDs, registers, YAML spec sheet, aggregator packet, reader brief, audit, and manifest.
- Priority: high
- Decisions: Chat label inferred as Dominium Codex Platform Renderer API Plan., Date anchor is 2026-05-27 Australia/Melbourne., Scope is this chat only.
- Tasks: TASK-12
- Constraints: CONSTRAINT-17, CONSTRAINT-18, CONSTRAINT-19
- Artifacts: ARTIFACT-01, ARTIFACT-21, ARTIFACT-22, ARTIFACT-23, ARTIFACT-24, ARTIFACT-25, ARTIFACT-26, ARTIFACT-27
- Risks: RISK-09, RISK-10
- Open questions: see Open Questions Register.
- Next action: Download and store the ZIP and individual files.



## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Label | Related |
| --- | --- | --- | --- | --- |
| DECISION-01 | Use C89 for Domino core forever. | decided | FACT | WORKSTREAM-03 |
| DECISION-02 | Use C++98 for Dominium layer forever. | decided | FACT | WORKSTREAM-03 |
| DECISION-03 | C99/C11/C++11+ are optional acceleration layers only. | decided | FACT | WORKSTREAM-03 |
| DECISION-04 | Reject runtime language-standard switching. | decided | FACT | WORKSTREAM-03 |
| DECISION-05 | All ABI-relevant boundaries use C ABI, POD structs, explicit function tables. | decided | FACT | WORKSTREAM-03 |
| DECISION-06 | Every interface struct begins with u32 abi_version and u32 struct_size. | decided | FACT | WORKSTREAM-03 |
| DECISION-07 | Use facade + backend architecture for all evolvable subsystems. | decided | FACT | WORKSTREAM-03 |
| DECISION-08 | Use a centralized capability registry for backend selection. | decided | FACT | WORKSTREAM-03 |
| DECISION-09 | Use determinism grades D0/D1/D2. | decided | FACT | WORKSTREAM-03 |
| DECISION-10 | Lockstep strict requires D0 only. | decided | FACT | WORKSTREAM-03 |
| DECISION-11 | Treat serialization/assets/saves/replays as public ABI. | decided | FACT | WORKSTREAM-02 |
| DECISION-12 | Networking handshake must include build/schema/determinism/content hashes. | decided | FACT | WORKSTREAM-02 |
| DECISION-13 | Launcher profiles select feature profiles/backends, not language standards. | decided | FACT | WORKSTREAM-02 |
| DECISION-14 | Final active plan is the 9-prompt post-master pack. | decided | FACT | WORKSTREAM-02 |
| DECISION-15 | Codex must make detailed commits throughout. | decided | FACT | WORKSTREAM-02 |
| DECISION-16 | Tier-1 platform completion focuses on Win32 and Win32 headless. | decided | FACT | WORKSTREAM-02 |
| DECISION-17 | Software renderer is D0 reference backend. | decided | FACT | WORKSTREAM-02 |
| DECISION-18 | DX9 is Tier-1 runtime-present backend. | decided | FACT | WORKSTREAM-02 |
| DECISION-19 | Tier-2 platforms/renderers are gated and compile-correct in current pack. | decided with caveat | FACT | WORKSTREAM-02 |
| DECISION-20 | Launcher and game need basic GUI smoke tests. | decided | FACT | WORKSTREAM-02 |
| DECISION-21 | Future AAA features are extension/capability slots, not immediate implementation scope. | decided for current plan | INFERENCE | WORKSTREAM-04 |
| DECISION-22 | This report package chat label is inferred as Dominium Codex Platform Renderer API Plan. | decided for packaging | INFERENCE | WORKSTREAM-05 |

### Task Register

| ID | Task | Priority | Next step | Label |
| --- | --- | --- | --- | --- |
| TASK-01 | Verify whether MASTER prompts 1-14 were implemented in the repository. | high | Inspect repo; run searches/builds. | UNCERTAIN / UNVERIFIED |
| TASK-02 | Run or hand off final Prompt 1. | critical | Execute in Codex at repo path. | FACT |
| TASK-03 | Run final Prompt 2. | critical | Execute after Prompt 1 passes. | FACT |
| TASK-04 | Run final Prompt 3. | high | Execute after Prompt 2 passes. | FACT |
| TASK-05 | Run final Prompt 4. | high | Execute and verify both platforms. | FACT |
| TASK-06 | Run final Prompt 5. | high | Execute and verify soft hash + DX9 demo. | FACT |
| TASK-07 | Run final Prompt 6. | medium-high | Execute gating and optional backend compile checks. | FACT |
| TASK-08 | Run final Prompt 7. | high | Execute and run regression tests. | FACT |
| TASK-09 | Run final Prompt 8. | critical | Execute; scripts\build_codex_verify.bat must pass. | FACT |
| TASK-10 | Run final Prompt 9. | medium | Execute after done gates pass. | FACT |
| TASK-11 | Preserve AAA future feature roadmap for later Project Spec Book. | medium | Do not implement now unless user asks. | FACT |
| TASK-12 | Create final downloadable chat report package. | high | Generate files and links. | FACT |
| TASK-13 | Resolve DSYS vs domino_sys policy if repo conflict occurs. | high | Use Prompt 1 stop-and-ask. | FACT |
| TASK-14 | Resolve smoke UI text strategy if needed. | medium | Use stop-and-ask. | FACT |
| TASK-15 | Confirm exact launcher/game target names. | high | Use Prompt 8 stop-and-ask if unknown. | FACT |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Label |
| --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Codex runtime OS is Windows. | runtime | hard | FACT |
| CONSTRAINT-02 | Repo path is c:\Inbox\Git Repos\dominium. | runtime | hard | FACT |
| CONSTRAINT-03 | Approval policy is NEVER. | process | hard | FACT |
| CONSTRAINT-04 | Network enabled but no dependency downloads unless explicitly approved. | dependency | hard | FACT |
| CONSTRAINT-05 | Repo must remain buildable after each prompt. | build | hard | FACT |
| CONSTRAINT-06 | Domino core ISO C89 baseline forever. | language | hard | FACT |
| CONSTRAINT-07 | Dominium layer C++98 baseline forever. | language | hard | FACT |
| CONSTRAINT-08 | Modern standards are optional acceleration only. | language | hard | FACT |
| CONSTRAINT-09 | No runtime language-standard switching. | compatibility | hard | FACT |
| CONSTRAINT-10 | Stable ABI uses C ABI, POD, no C++ boundary types. | ABI | hard | FACT |
| CONSTRAINT-11 | Every interface begins with u32 abi_version and u32 struct_size. | ABI | hard | FACT |
| CONSTRAINT-12 | No floating point in deterministic core. | determinism | hard | FACT |
| CONSTRAINT-13 | No grid assumptions in core placement/world systems. | simulation | hard | FACT |
| CONSTRAINT-14 | No tolerance solvers in deterministic core. | determinism | hard | FACT |
| CONSTRAINT-15 | Lockstep strict requires D0 bit-exact backends for lockstep-relevant subsystems. | determinism | hard | FACT |
| CONSTRAINT-16 | Serialization formats are public ABI. | compatibility | hard | FACT |
| CONSTRAINT-17 | This report covers this chat only. | reporting | hard | FACT |
| CONSTRAINT-18 | Important items must be labelled FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | reporting | hard | FACT |
| CONSTRAINT-19 | Create downloadable files and ZIP if tools available. | reporting | hard | FACT |
| CONSTRAINT-20 | Preserve superseded/rejected/deprioritised options. | reporting | hard | FACT |
| CONSTRAINT-21 | Direct user statements outrank assistant suggestions. | evidence | hard | FACT |
| CONSTRAINT-22 | No new third-party dependencies in prompts unless approved. | dependency | hard | FACT |
| CONSTRAINT-23 | Prefer fewer larger Codex prompts. | process | soft/hard for plan | FACT |
| CONSTRAINT-24 | Codex commits throughout with detailed bodies. | process | hard | FACT |

### Open Questions Register

| ID | Question | Priority | Label |
| --- | --- | --- | --- |
| QUESTION-01 | Were MASTER prompts 1-14 actually implemented in the repo? | high | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Which DSYS API is authoritative if dsys_* and domino_sys_* conflict? | high | FACT |
| QUESTION-03 | Which headers are baseline-visible? | high | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | Do public headers currently contain C99/C++11 constructs? | high | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What are exact launcher and game target/executable names? | high | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Is there an existing UI toolkit? | medium | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What is Tier-1 UI text strategy? | medium | FACT |
| QUESTION-08 | Win32 path encoding policy: UTF-8 or UTF-16 internally? | medium | FACT |
| QUESTION-09 | Minimum process feature: spawn+wait or stdout/stderr capture now? | medium | FACT |
| QUESTION-10 | Minimum networking facet: TCP only or TCP+UDP? | medium | FACT |
| QUESTION-11 | Which legacy file formats must remain readable immediately? | high | FACT |
| QUESTION-12 | Does an existing networking join path exist? | medium | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Is full Tier-2 runtime completion required now or is compile-gated coverage acceptable? | medium | INFERENCE |
| QUESTION-14 | Should D3D12 be added in a later prompt phase? | low | FACT |
| QUESTION-15 | Does existing changelog format need preservation? | low | FACT |

### Artifact Ledger

| ID | Artifact | Type | Status | Carry forward | Label |
| --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Previous maximum-fidelity Context Transfer Packet | report | consumed and repaired | yes | FACT |
| ARTIFACT-02 | MASTER CODEX PROMPT PLAN prompts 1-14 | prompt plan | assumed prerequisite; implementation unverified | yes | FACT |
| ARTIFACT-03 | /mnt/data/dominium.zip | uploaded repo archive | uploaded; contents unverified in this chat | yes | FACT |
| ARTIFACT-04 | Initial questionnaire and user answers | planning input | used | yes | FACT |
| ARTIFACT-05 | Initial assistant platform/render prompt pack 1-14 | prompt plan | superseded | historical | FACT |
| ARTIFACT-06 | Post-engine plan prompts 15-24 | prompt plan | superseded | historical | FACT |
| ARTIFACT-07 | User injected mandatory constraints | requirements text | integrated | yes | FACT |
| ARTIFACT-08 | Revised post-14 prompts 15-28 | prompt plan | superseded | historical | FACT |
| ARTIFACT-09 | Final Prompt 1 — Baseline enforcement + ABI/vtable + facades + commits | Codex prompt | active | yes | FACT |
| ARTIFACT-10 | Final Prompt 2 — Capability registry + determinism grades + launcher profiles | Codex prompt | active | yes | FACT |
| ARTIFACT-11 | Final Prompt 3 — CMake switchboard + presets + null backends + build metadata | Codex prompt | active | yes | FACT |
| ARTIFACT-12 | Final Prompt 4 — Tier-1 platform Win32/win32_headless + system smoke | Codex prompt | active | yes | FACT |
| ARTIFACT-13 | Final Prompt 5 — Tier-1 renderer soft + DX9 + dgfx_demo | Codex prompt | active | yes | FACT |
| ARTIFACT-14 | Final Prompt 6 — Tier-2 platform/render gating + compile correctness | Codex prompt | active | yes | FACT |
| ARTIFACT-15 | Final Prompt 7 — TLV-as-ABI + net handshake + schema IDs + tests | Codex prompt | active | yes | FACT |
| ARTIFACT-16 | Final Prompt 8 — Launcher/game GUI smoke + verify script | Codex prompt | active | yes | FACT |
| ARTIFACT-17 | Final Prompt 9 — Changelog pipeline + release notes automation | Codex prompt | active | yes | FACT |
| ARTIFACT-18 | README-style bootstrap prompt for new chat | prompt | created in transfer packet | yes | FACT |
| ARTIFACT-19 | Manual verification checklist | checklist | created in transfer packet | yes | FACT |
| ARTIFACT-20 | AAA future feature roadmap | brainstorm/architecture notes | not current implementation scope | yes | FACT |
| ARTIFACT-21 | dominium_codex_platform_renderer_api_plan__01_full_chat_report.md | generated report file | created now | yes | FACT |
| ARTIFACT-22 | dominium_codex_platform_renderer_api_plan__02_spec_sheet.yaml | generated YAML file | created now | yes | FACT |
| ARTIFACT-23 | dominium_codex_platform_renderer_api_plan__03_aggregator_packet.md | generated report file | created now | yes | FACT |
| ARTIFACT-24 | dominium_codex_platform_renderer_api_plan__04_registers.md | generated registers file | created now | yes | FACT |
| ARTIFACT-25 | dominium_codex_platform_renderer_api_plan__05_reader_brief.md | generated brief | created now | yes | FACT |
| ARTIFACT-26 | dominium_codex_platform_renderer_api_plan__06_verification_and_audit.md | generated audit file | created now | yes | FACT |
| ARTIFACT-27 | dominium_codex_platform_renderer_api_plan__manifest.md | generated manifest | created now | yes | FACT |
| ARTIFACT-28 | dominium_codex_platform_renderer_api_plan__handoff_package.zip | generated zip | created now | yes | FACT |

### Risk Register

| ID | Risk | Severity | Mitigation | Label |
| --- | --- | --- | --- | --- |
| RISK-01 | Repo-specific claims may be wrong because uploaded zip was not inspected. | high | Verify repo/archive before implementation-specific claims. | UNCERTAIN / UNVERIFIED |
| RISK-02 | MASTER prompts 1-14 may not actually be implemented. | high | Run verification searches/builds before execution. | UNCERTAIN / UNVERIFIED |
| RISK-03 | Final pack may not satisfy 'fully complete' for Tier-2 runtime backends. | medium-high | Clarify if user reopens scope; add future runtime prompts. | INFERENCE |
| RISK-04 | Baseline header checker may flag many existing violations. | high | Use stop-and-ask if rewriting/moving/deleting declarations needs policy. | INFERENCE |
| RISK-05 | Legacy DSYS vs new DSYS surface conflict. | high | Keep legacy shim or ask policy per Prompt 1. | FACT |
| RISK-06 | Backend determinism grades may be hard to prove. | high | Default uncertain optimized/platform-specific backends to D2 until proven. | INFERENCE |
| RISK-07 | AAA brainstorm could be mistaken as current scope. | medium | Label future features as roadmap/spec candidates only. | FACT |
| RISK-08 | Advanced presentation features could contaminate deterministic sim. | high | Keep presentation non-authoritative; use caps/extensions. | INFERENCE |
| RISK-09 | Report package may over-compress exact prompt text. | medium | Preserve active prompt IDs and key requirements; refer to chat context for exact text if needed. | INFERENCE |
| RISK-10 | Generated report may treat assistant suggestions as accepted decisions. | medium | Labels distinguish FACT/INFERENCE; future aggregator must preserve uncertainty. | FACT |
| RISK-11 | DX9 availability/toolchain mismatch. | medium | CMake detection and clear errors; system SDK only. | INFERENCE |
| RISK-12 | Smoke UI text requirement may exceed renderer IR subset. | medium | Use rectangles or ask text strategy. | FACT |
| RISK-13 | TLV migration scope unknown. | high | Inventory formats before conversion. | FACT |
| RISK-14 | Verify script may be Windows-only. | medium | Accept for current Windows Codex; add POSIX scripts later if needed. | INFERENCE |
| RISK-15 | Stale external software/toolchain facts. | medium | Reverify CMake/toolchain/SDK status before future use. | UNCERTAIN / UNVERIFIED |
| RISK-16 | Future aggregation may merge superseded plans incorrectly. | high | Use rejected/superseded register. | FACT |

### Verification Queue

| ID | Item | Priority | Label |
| --- | --- | --- | --- |
| VERIFY-01 | Inspect repo/archive to confirm MASTER prompts 1-14 implementation. | high | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Run initial CMake configure/build in repo. | high | FACT |
| VERIFY-03 | Search DSYS/DGFX callsites. | high | FACT |
| VERIFY-04 | Confirm exact launcher/game target names. | high | FACT |
| VERIFY-05 | Run baseline header checker once implemented. | high | FACT |
| VERIFY-06 | Print capability registry selection audit. | high | FACT |
| VERIFY-07 | Run domino_sys_smoke for win32 and win32_headless. | high | FACT |
| VERIFY-08 | Run soft renderer hash test and dgfx_demo. | high | FACT |
| VERIFY-09 | Run Tier-2 incompatible-selection configure tests. | medium-high | FACT |
| VERIFY-10 | Run TLV/handshake regression tests. | high | FACT |
| VERIFY-11 | Run scripts\build_codex_verify.bat after Prompt 8. | critical | FACT |
| VERIFY-12 | Confirm which AAA roadmap items become formal future requirements. | medium | INFERENCE |
| VERIFY-13 | Verify generated report files and ZIP are downloadable/readable. | high | FACT |
| VERIFY-14 | Check whether existing CHANGELOG format exists. | low-medium | FACT |

## 6. Possible Cross-Chat Duplicates

- Master engine-core prompts 1-14.
- Determinism specifications.
- TRANS/STRUCT/DECOR planning.
- Future AAA graphics/audio/input/AI roadmap.
- Platform/render target matrix.
- Build and CI verification scripts.

## 7. Possible Cross-Chat Conflicts

- Later chats may revise platform/render priorities.
- Later chats may actually inspect the repo and contradict file/path assumptions from this chat.
- Later chats may demand full Tier-2 runtime completion rather than compile-gated coverage.
- Other chats may have different CMake preset names or changelog formats.

## 8. Spec Book Integration Guidance

Feed this chat into chapters on language baselines, ABI, facades/backends, capability registry, determinism, serialization, networking handshake, build matrix, platform/render completion, product smoke tests, release/changelog process, and future AAA roadmap. Formalize user-mandated constraints. Keep future AAA feature lists as roadmap/background unless confirmed. Preserve superseded plan history in an appendix or decision log.

## 9. Aggregator Warnings

Do not merge superseded prompt packs into active implementation scope. Do not treat assistant suggestions as user decisions unless later accepted. Do not assume the uploaded repo was inspected. Do not convert brainstormed AAA features into immediate requirements. Do not erase the compile-gated Tier-2 caveat.
