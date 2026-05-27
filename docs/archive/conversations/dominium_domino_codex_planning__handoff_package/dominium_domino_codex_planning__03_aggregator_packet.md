# Aggregator Packet — Dominium Domino Codex Planning

## 1. Packet Metadata

- Chat label: Dominium Domino Codex Planning
- Date anchor: 2026-05-27 Australia/Melbourne
- Source scope: THIS CHAT ONLY; PROJECT-CONTEXT labelled when used.
- Coverage: full visible-chat coverage with repo-state caveats.
- Confidence: 4/5.
- Staleness risk: medium.
- Merge priority: high.
- Main limitations: repo-specific claims require verification; generated prompt text is summarized; execution status of prompts unknown.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat is a high-value planning and handoff chat for the Dominium + Domino project. Its main contribution is not repo code but a structured sequence of architectural decisions, generated Codex prompts, and risk/verification guidance. The chat begins from the user's Extended Master Starter Prompt, which defines Domino as a deterministic ISO C89 fixed-point engine and Dominium as a portable C++98 product suite. The dominant hard constraints are dsys-only platform access, dgfx-only rendering, deterministic sim behavior, no host floating point in simulation, versioned stable ABI/file formats, and no silent breakage of old saves/mods/packs/tools.

The chat produced a phased implementation plan, then converted that plan into self-contained Codex prompts. The first six prompts define the initial Milestone-0 vertical slice: create canonical identity/product docs, enforce repo layout and CMake targets, implement deterministic numeric core, implement DOMINIUM_HOME manifest loading and launcher enumeration, add minimal deterministic sim/headless game/TLV save, and complete launcher-to-game process spawning through dsys. The execution status of these prompts is unknown and must be verified against the repo.

The chat then generated prompts for shared product interfaces: Universal CLI, Universal TUI, and Universal GUI across launcher, game, setup, and tools. It next generated prompts for shared input/state/IME and for multi-window GUI/dgfx pipelines/GPU backend detection. A third requested prompt for pack-system integration — sound, music, texture, shader packs, GUI theme packs, vector icon system, and asset streaming — was not generated. This missing prompt is one of the most important carry-forward tasks.

The other major contribution is the unified startup policy. The user explicitly wanted product executables to behave as CLI when called in a terminal and to default to GUI when double-clicked, then TUI, then CLI if earlier modes fail. The assistant recommended a policy: explicit --mode flags win; no env/config overrides in v1; dsys_running_in_terminal controls AUTO behavior; no-terminal AUTO tries GUI, then TUI, then CLI; game --server/--dedicated/--listen/--mode=headless force headless and bypass GUI/TUI. A big Codex prompt was generated for this, but it has a known design risk: if startup.c inside domino_core directly references all product-specific C++ mode wrappers, targets may fail to link. A future implementation should use a generic callback table or product-local dispatchers.

Finally, the user asked for a platform/render/API questionnaire answer based on dominium.zip/current repo. The assistant produced a refined answer, but this final package marks the repo-inspection claim as unverified because the visible chat does not provide file-tool evidence. Any aggregator or future assistant must treat platform tiers, renderer backends, target lists, and build context as candidate data until verified against the current repo/files.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | C89/C++98 language split | constraint | CONSTRAINT-01/02 | Project portability policy. | FACT | 5/5 |
| 2 | dsys/dgfx boundaries | constraint | CONSTRAINT-06/07 | Prevents platform/render leakage. | FACT | 5/5 |
| 3 | Deterministic fixed-point sim | constraint | CONSTRAINT-03/04/05 | Core engine identity. | FACT | 5/5 |
| 4 | Compatibility guarantee | decision | DECISION-08 | Protects old content and formats. | FACT | 5/5 |
| 5 | Milestone-0 six prompts | artifact | ARTIFACT-04..09 | Initial implementation sequence. | FACT | 5/5 |
| 6 | Common CLI/TUI/GUI prompts | artifact | ARTIFACT-10..12 | Shared product UX architecture. | FACT | 5/5 |
| 7 | Missing pack-system prompt | task/artifact | TASK-13/ARTIFACT-15 | Requested but not generated. | FACT | 5/5 |
| 8 | Startup policy | decision | DECISION-15/16 | User-desired executable behavior. | FACT | 5/5 |
| 9 | Startup linker risk | risk | RISK-03 | Must repair generated prompt before applying. | INFERENCE | 5/5 |
| 10 | Repo verification caveat | verification | VERIFY-01 | Prior repo claims unverified. | UNCERTAIN / UNVERIFIED | 5/5 |

## 4. Workstream Summaries

### WORKSTREAM-01 — Dominium + Domino Core Architecture Continuity
- ID: WORKSTREAM-01
- Name: Dominium + Domino Core Architecture Continuity
- Objective: Preserve and continue the architecture for Domino as deterministic C89 engine and Dominium as C++98 product suite built on it.
- Current state: The chat established the architecture constraints in the user's Extended Master Starter Prompt and the prior transfer packet preserved them. Actual repo implementation state must be verified separately.
- Desired end state: A stable deterministic engine/product suite with strict dsys/dgfx layering, versioned ABI/file formats, and compatibility-preserving products.
- Priority: highest
- Decisions: DECISION-01, DECISION-02, DECISION-03, DECISION-04, DECISION-05, DECISION-06, DECISION-07, DECISION-08
- Tasks: TASK-01, TASK-02, TASK-05
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10
- Artifacts: ARTIFACT-01, ARTIFACT-02, ARTIFACT-39
- Risks: RISK-01, RISK-02, RISK-04, RISK-08
- Open questions: QUESTION-01, QUESTION-02, QUESTION-03, QUESTION-09
- Next action: Verify current repo, then continue from the relevant prompt/workstream.

### WORKSTREAM-02 — Milestone-0 Vertical Slice via Six Codex Prompts
- ID: WORKSTREAM-02
- Name: Milestone-0 Vertical Slice via Six Codex Prompts
- Objective: Create a minimal launcher-to-game deterministic pipeline: specs, layout, numeric core, repo model, sim/TLV, launcher process spawn.
- Current state: Six Codex prompts were generated. It is not established in this chat whether they were executed.
- Desired end state: A working vertical slice: launcher discovers product manifest, spawns game, game runs deterministic headless sim, prints checksum, writes TLV save.
- Priority: highest
- Decisions: DECISION-09, DECISION-10
- Tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05, TASK-06, TASK-07
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-09
- Artifacts: ARTIFACT-04, ARTIFACT-05, ARTIFACT-06, ARTIFACT-07, ARTIFACT-08, ARTIFACT-09
- Risks: RISK-02, RISK-04, RISK-05, RISK-06, RISK-07
- Open questions: QUESTION-01, QUESTION-03, QUESTION-04, QUESTION-05
- Next action: Inspect repo for files from prompts 1-6 and run the golden build/test set.

### WORKSTREAM-03 — Shared CLI, TUI, and GUI Layers Across Products
- ID: WORKSTREAM-03
- Name: Shared CLI, TUI, and GUI Layers Across Products
- Objective: Create common CLI, TUI, and GUI frameworks used by launcher, game, setup, and tools.
- Current state: Three Codex prompts were generated for universal CLI, TUI, and GUI. Execution status is not established.
- Desired end state: Products expose common CLI/TUI/GUI paths through shared Domino components without duplicated product pipelines.
- Priority: high
- Decisions: DECISION-11, DECISION-12
- Tasks: TASK-08, TASK-09, TASK-10
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-11
- Artifacts: ARTIFACT-10, ARTIFACT-11, ARTIFACT-12
- Risks: RISK-09, RISK-10, RISK-11
- Open questions: QUESTION-10
- Next action: Verify existing CLI/TUI/GUI modules and decide whether to split prompts before implementation.

### WORKSTREAM-04 — Shared Input System, State Machines, and Cross-Platform IME
- ID: WORKSTREAM-04
- Name: Shared Input System, State Machines, and Cross-Platform IME
- Objective: Add a unified input event queue, deterministic state-machine framework, and IME abstraction shared across modes/products.
- Current state: A Codex prompt was generated. Execution status is not established.
- Desired end state: Input and IME events feed GUI/TUI through deterministic event ordering; products use common state machines.
- Priority: high
- Decisions: DECISION-13
- Tasks: TASK-11
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-06
- Artifacts: ARTIFACT-13
- Risks: RISK-12
- Open questions: QUESTION-11
- Next action: Inspect current source/domino/input and source/domino/state before applying.

### WORKSTREAM-05 — Multi-Window GUI, dgfx Pipelines, and GPU Backend Detection
- ID: WORKSTREAM-05
- Name: Multi-Window GUI, dgfx Pipelines, and GPU Backend Detection
- Objective: Extend GUI/dgfx to logical multi-window support, render pipeline/pass/target abstractions, and backend detection/selection.
- Current state: A Codex prompt was generated. Execution status is not established.
- Desired end state: GUI windows use dsys windows and dgfx pipelines; software backend always works; GPU backends are optional and detected deterministically.
- Priority: medium-high
- Decisions: DECISION-14
- Tasks: TASK-12
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-06, CONSTRAINT-07
- Artifacts: ARTIFACT-14
- Risks: RISK-09, RISK-13
- Open questions: QUESTION-12, QUESTION-13
- Next action: Rewrite prompt against actual renderer headers after repo verification if necessary.

### WORKSTREAM-06 — Pack System Integration Prompt
- ID: WORKSTREAM-06
- Name: Pack System Integration Prompt
- Objective: Generate a Codex prompt for sound, music, texture, shader, GUI theme packs, vector icons, and asset streaming.
- Current state: User requested this as the third prompt, but it was not generated before the conversation changed direction.
- Desired end state: A self-contained Codex prompt covering versioned pack manifests, deterministic discovery/load ordering, asset streaming, vector fallback, and pack compatibility.
- Priority: high if continuing prompt sequence
- Decisions: none
- Tasks: TASK-13
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10
- Artifacts: ARTIFACT-15
- Risks: RISK-14
- Open questions: QUESTION-14, QUESTION-15
- Next action: Generate missing prompt when requested; preferably verify pack docs first.

### WORKSTREAM-07 — Unified Startup and Mode Dispatcher
- ID: WORKSTREAM-07
- Name: Unified Startup and Mode Dispatcher
- Objective: Implement product startup policy: terminal invocation uses CLI; double-click/no terminal tries GUI then TUI then CLI; explicit modes override; game server/headless flags force headless.
- Current state: Recommendations were made and a large Codex prompt was generated. It contains a known potential linker design risk.
- Desired end state: Every product has consistent startup behavior through dsys terminal detection, mode parsing, capabilities, and product entry wrappers.
- Priority: high
- Decisions: DECISION-15, DECISION-16, DECISION-17, DECISION-18, DECISION-19, DECISION-20
- Tasks: TASK-14, TASK-15, TASK-16
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-06, CONSTRAINT-12
- Artifacts: ARTIFACT-16
- Risks: RISK-03, RISK-04, RISK-15
- Open questions: QUESTION-06, QUESTION-07, QUESTION-08
- Next action: Refine implementation design with callback table or product-local dispatcher before applying prompt.

### WORKSTREAM-08 — Platform, Renderer, API Questionnaire and Repo-State Answer
- ID: WORKSTREAM-08
- Name: Platform, Renderer, API Questionnaire and Repo-State Answer
- Objective: Answer a detailed questionnaire about target platforms, renderers, APIs, completion gates, build context, and repo state.
- Current state: User pasted a questionnaire and a Codex-in-repo answer; assistant produced a refined answer but repo inspection evidence is not visible in this chat.
- Desired end state: A verified questionnaire answer based on actual repo/docs with uncertainty labels and citations/file references.
- Priority: medium-high
- Decisions: none
- Tasks: TASK-17
- Constraints: CONSTRAINT-13, CONSTRAINT-14
- Artifacts: ARTIFACT-17, ARTIFACT-18, ARTIFACT-19, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22, ARTIFACT-23
- Risks: RISK-01, RISK-02, RISK-16
- Open questions: QUESTION-01, QUESTION-02, QUESTION-12
- Next action: Inspect uploaded/current repo before relying on prior questionnaire details.

### WORKSTREAM-09 — Chat Handoff and Report Package
- ID: WORKSTREAM-09
- Name: Chat Handoff and Report Package
- Objective: Transform the existing Context Transfer Packet and visible chat into a downloadable report package for future aggregation and continuation.
- Current state: This response creates the final package files, including report, YAML, aggregator packet, registers, reader brief, verification/audit, manifest, and ZIP.
- Desired end state: A reusable per-chat package that can be saved, shared, aggregated, and used to continue work without re-explaining this chat.
- Priority: highest for this final chat task
- Decisions: DECISION-21
- Tasks: TASK-18
- Constraints: CONSTRAINT-13, CONSTRAINT-15, CONSTRAINT-16
- Artifacts: ARTIFACT-24, ARTIFACT-25, ARTIFACT-26, ARTIFACT-27, ARTIFACT-28, ARTIFACT-29, ARTIFACT-30, ARTIFACT-31
- Risks: RISK-17, RISK-18
- Open questions: none
- Next action: Store package and use it as source for next chat or later aggregation.


## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Label |
|---|---|---|---|
| DECISION-01 | Domino engine is ISO C89. | decided | FACT |
| DECISION-02 | Dominium product/UI code may use portable C++98 subset where needed. | decided | FACT |
| DECISION-03 | All platform interaction must go through dsys. | decided | FACT |
| DECISION-04 | All rendering must go through dgfx IR/backends. | decided | FACT |
| DECISION-05 | Software renderer is mandatory baseline. | decided | FACT |
| DECISION-06 | Vector-only fallback UI/pack path must always function. | decided | FACT |
| DECISION-07 | DOMINIUM_HOME repository model is canonical for products, mods, packs, and instances. | decided | FACT |
| DECISION-08 | Backward/forward compatibility is mandatory for saves, packs, mods, tools where possible. | decided | FACT |
| DECISION-09 | First implementation should be a narrow Milestone-0 vertical slice. | recommended and implicitly accepted | INFERENCE |
| DECISION-10 | Codex prompts should be self-contained implementation packages. | working decision | FACT |
| DECISION-11 | CLI/TUI/GUI should be common/shared across launcher, game, setup, and tools. | decided by user request | FACT |
| DECISION-12 | TUI and GUI must use dsys/dgfx abstractions, not direct platform drawing. | decided | FACT |
| DECISION-13 | Input/IME/state machine systems should be shared and deterministic. | prompt generated | FACT |
| DECISION-14 | GPU backend detection must always include software fallback. | prompt generated / architecture-consistent | FACT |
| DECISION-15 | Terminal invocation with no explicit mode defaults to CLI. | decided by user request | FACT |
| DECISION-16 | Double-click/no-terminal launch defaults to GUI, then TUI, then CLI fallback. | decided by user request | FACT |
| DECISION-17 | Explicit --mode flags should override AUTO heuristics. | recommended and accepted by requesting prompt | INFERENCE |
| DECISION-18 | Game --server/--dedicated/--listen/--mode=headless force headless and bypass GUI/TUI. | recommended and included in generated prompt | INFERENCE |
| DECISION-19 | Do not add env/config startup mode overrides in v1. | recommended | INFERENCE |
| DECISION-20 | Fallback should occur only on structural GUI/TUI unsupported errors, not logical/content errors. | recommended | INFERENCE |
| DECISION-21 | This old chat should be exported as a downloadable multi-file report package. | decided by user request | FACT |

### Task Register

| ID | Task | Priority | Next step | Label |
|---|---|---|---|---|
| TASK-01 | Verify actual repo state from dominium.zip or current checkout. | highest | Extract/list repo and inspect key files. | FACT |
| TASK-02 | Determine which generated Codex prompts were executed. | highest | Search for files named in each prompt. | FACT |
| TASK-03 | Build and run golden target set. | high | Run CMake/Ninja targets and numeric/headless tests. | INFERENCE |
| TASK-04 | Audit generated numeric core for strict C89 and deterministic overflow behavior. | high | Check 64-bit typedefs, saturation constants, shifts, and no floating point in sim path. | INFERENCE |
| TASK-05 | Define endian-stable TLV IO helpers if not already present. | high | Inspect existing TLV/data format rules. | INFERENCE |
| TASK-06 | Verify launcher→game process spawn path and manifest path handling. | high | Run launcher run-game command with seed/ticks. | INFERENCE |
| TASK-07 | Keep docs/specs aligned with generated code. | medium-high | Diff generated headers/APIs against docs. | INFERENCE |
| TASK-08 | Implement or refine common CLI framework. | medium-high | Inspect source/domino/cli and product CLI code. | FACT |
| TASK-09 | Implement or refine common TUI framework. | medium | Inspect dsys terminal implementation state. | FACT |
| TASK-10 | Implement or refine common GUI framework. | medium | Inspect render/gui modules. | FACT |
| TASK-11 | Implement shared input/state/IME after inspecting existing modules. | medium-high | Search source/domino/input and source/domino/state. | FACT |
| TASK-12 | Implement or rewrite multi-window/dgfx pipeline/backend detection prompt against actual renderer API. | medium | Compare proposed APIs with include/domino/gfx.h and render sources. | FACT |
| TASK-13 | Generate the missing pack system integration Codex prompt. | high if continuing prompt sequence | If user asks 'next', generate prompt; if repo-specific, inspect docs first. | FACT |
| TASK-14 | Refine unified startup dispatcher design to avoid linker/circular dependency issues. | highest for startup implementation | Inspect CMake/product target linkage. | INFERENCE |
| TASK-15 | Implement dsys_running_in_terminal for active platforms. | high | Wire one implementation per platform in CMake. | FACT |
| TASK-16 | Implement startup mode parsing, capabilities, and product mode wrappers. | high | Refactor product main functions. | FACT |
| TASK-17 | Produce a verified platform/render/API questionnaire answer from actual repo/docs. | medium-high | Inspect files; do not rely solely on previous assistant answer. | FACT |
| TASK-18 | Save this chat-specific report package and ZIP for future aggregation. | highest for current task | Download/store the generated package. | FACT |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Label |
|---|---|---|---|---|
| CONSTRAINT-01 | Domino engine code must be ISO C89/C90. | language | hard | FACT |
| CONSTRAINT-02 | Dominium product/UI code must be portable C++98 where needed. | language | hard | FACT |
| CONSTRAINT-03 | Simulation must be deterministic across supported OS/architectures. | determinism | hard | FACT |
| CONSTRAINT-04 | Core simulation uses fixed-point/integer numeric formats including u8/i8/u16/i16/u32/i32/u64/i64/q4_12/q16_16/q24_8/q48_16. | numeric | hard | FACT |
| CONSTRAINT-05 | No host floating point inside deterministic simulation logic. | determinism | hard | FACT |
| CONSTRAINT-06 | All platform-specific interactions route through dsys. | layering | hard | FACT |
| CONSTRAINT-07 | All rendering routes through dgfx IR/backend abstraction. | layering | hard | FACT |
| CONSTRAINT-08 | Vector-only fallback must always work. | UI/assets | hard | FACT |
| CONSTRAINT-09 | Old saves, packs, mods, instances, and tools must not silently break. | compatibility | hard | FACT |
| CONSTRAINT-10 | DOMINIUM_HOME repository layout supports multiple coexisting versions and non-destructive import. | repo/model | hard | FACT |
| CONSTRAINT-11 | GUI/TUI/CLI product logic should be shared, not duplicated. | architecture | hard | FACT |
| CONSTRAINT-12 | Startup explicit mode flags override AUTO; no-terminal launch tries GUI/TUI/CLI; terminal launch uses CLI. | startup behavior | hard for user desired behavior; implementation details pending | FACT |
| CONSTRAINT-13 | Repo-specific claims must be verified against files before future use. | evidence | hard for future accuracy | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-14 | External-world facts/software versions/APIs/current state require verification before future use. | evidence/staleness | hard | FACT |
| CONSTRAINT-15 | This final package is scoped to this chat only. | scope | hard | FACT |
| CONSTRAINT-16 | Final package must preserve tentative status, rejected options, artifacts, risks, contradictions, and stable IDs. | reporting/output | hard | FACT |

### Open Questions Register

| ID | Question | Priority | Resolution path | Label |
|---|---|---|---|---|
| QUESTION-01 | Which generated Codex prompts have actually been applied to the repo? | highest | Inspect repo/git state for files and diffs. | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | What is the actual current repo structure and target list in dominium.zip/current checkout? | highest | Open/extract repo and inspect key files. | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Does the repo already contain files from prompts 1-6? | high | Search for docs/SPEC_IDENTITY.md, include/domino/core/fixed.h, repo.h, sim.h, etc. | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | How should strict C89 support exact 64-bit types and q48_16 across retro compilers? | high | Inspect existing type headers/docs; decide emulation or compiler-extension policy. | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Should TLV save format be native-endian temporarily or endian-stable immediately? | high | Inspect docs/DATA_FORMATS.md and TLV code. | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Where should startup mode dispatch live to avoid C/C++ linker issues? | highest | Inspect CMake; prefer callback table or product-local dispatcher. | INFERENCE |
| QUESTION-07 | Should Windows products be console-subsystem, windows-subsystem, or dual wrapper binaries? | high | User/build-system decision after inspecting packaging targets. | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Should future startup mode overrides via env/config be supported? | low | Defer until config system stabilizes or user requests. | INFERENCE |
| QUESTION-09 | What are final Tier 1/2/3 platform priorities? | medium | Verify docs and ask/confirm only if needed. | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | Should common CLI/TUI/GUI prompts be applied as broad prompts or split into smaller implementation prompts? | medium | Inspect current modules and decide module-by-module. | INFERENCE |
| QUESTION-11 | How complete are current input/state/IME modules? | medium | Inspect source/domino/input and source/domino/state. | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Which render backends are actually wired and which are only source-tree stubs? | high | Inspect render docs, source/domino/render, CMake. | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Is D3D12 in scope? | medium | Inspect render docs and ask user if needed. | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | What pack format(s) should the missing pack-system prompt target: TLV, JSON metadata, or both? | high | Inspect content/pack docs and source. | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | How should shader packs be represented across multiple render backends? | medium-high | Inspect render docs and decide per backend. | UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact | Type | Status | Carry forward | Label |
|---|---|---|---|---|---|
| ARTIFACT-01 | Extended Master Starter Prompt — Dominium + Domino | user project spec | active source material | yes | FACT |
| ARTIFACT-02 | Assistant acknowledgement of master prompt | assistant response | historical | limited | FACT |
| ARTIFACT-03 | Forward plan phases 0-12 | plan | planning reference | yes | FACT |
| ARTIFACT-04 | Codex Prompt 1 — SPEC_IDENTITY + SPEC_PRODUCTS | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-05 | Codex Prompt 2 — Repo layout, CMake skeleton, core/product targets | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-06 | Codex Prompt 3 — Deterministic numeric core + test harness | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-07 | Codex Prompt 4 — DOMINIUM_HOME repo model + launcher enumeration | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-08 | Codex Prompt 5 — Deterministic sim + headless game + TLV save | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-09 | Codex Prompt 6 — Launcher to game process spawn via dsys | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-10 | Prompt A — Universal CLI Layer | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-11 | Prompt B — Universal TUI Layer | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-12 | Prompt C — Universal GUI Layer | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-13 | Prompt — Shared Input System + State Machines + Cross-Platform IME | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-14 | Prompt — Multi-window GUI + dgfx Pipelines + GPU Backend Detection | Codex prompt | generated, execution unknown | yes | FACT |
| ARTIFACT-15 | Missing Prompt — Pack system integration | requested but not generated | not yet produced | yes | FACT |
| ARTIFACT-16 | Prompt — Unified Startup / Mode Dispatcher | Codex prompt | generated, execution unknown | yes, with design fixes | FACT |
| ARTIFACT-17 | User questionnaire: Platforms, Renderers, APIs, Completion, Repo/build context | user prompt/questionnaire | answered but verification required | yes | FACT |
| ARTIFACT-18 | User-pasted Codex-in-repo questionnaire answer | pasted output | unverified candidate data | yes with uncertainty | FACT |
| ARTIFACT-19 | Assistant refined questionnaire answer | assistant output | unverified candidate data | yes with verification caveat | UNCERTAIN / UNVERIFIED |
| ARTIFACT-20 | User-pasted root CMakeLists.txt | file content excerpt | pasted; current repo validity unverified | yes | FACT |
| ARTIFACT-21 | User-pasted source/CMakeLists.txt | file content excerpt | pasted; current repo validity unverified | yes | FACT |
| ARTIFACT-22 | User-pasted source tree excerpt | file tree excerpt | pasted; current repo validity unverified | yes | FACT |
| ARTIFACT-23 | User-pasted docs/OVERVIEW_ARCHITECTURE.md excerpt | documentation excerpt | pasted; current repo validity unverified | yes | FACT |
| ARTIFACT-24 | Context Transfer Packet from prior assistant | handoff document | source for this final package | yes | FACT |
| ARTIFACT-25 | dominium_domino_codex_planning__01_full_chat_report.md | generated file | created by this response | yes | FACT |
| ARTIFACT-26 | dominium_domino_codex_planning__02_spec_sheet.yaml | generated file | created by this response | yes | FACT |
| ARTIFACT-27 | dominium_domino_codex_planning__03_aggregator_packet.md | generated file | created by this response | yes | FACT |
| ARTIFACT-28 | dominium_domino_codex_planning__04_registers.md | generated file | created by this response | yes | FACT |
| ARTIFACT-29 | dominium_domino_codex_planning__05_reader_brief.md | generated file | created by this response | yes | FACT |
| ARTIFACT-30 | dominium_domino_codex_planning__06_verification_and_audit.md | generated file | created by this response | yes | FACT |
| ARTIFACT-31 | dominium_domino_codex_planning__manifest.md | generated file | created by this response | yes | FACT |
| ARTIFACT-32 | dominium_domino_codex_planning__handoff_package.zip | generated ZIP | created by this response | yes | FACT |
| ARTIFACT-33 | Copy-paste bootstrap prompt from previous transfer packet | prompt text | included in previous packet and adapted in reports | yes | FACT |
| ARTIFACT-34 | Later aggregator prompt supplied by user | prompt text | user-supplied in final request | yes | FACT |

### Risk Register

| ID | Risk | Severity | Mitigation | Label |
|---|---|---|---|---|
| RISK-01 | Unverified repo-state claims are treated as verified facts. | high | Inspect dominium.zip/current repo and label facts with file evidence. | UNCERTAIN / UNVERIFIED |
| RISK-02 | Generated prompts are mistaken for implemented code. | high | Check repo for generated files before continuing. | INFERENCE |
| RISK-03 | Startup dispatcher in domino_core references all product C++ wrappers and causes unresolved symbols. | high | Use callback-table/generic dispatcher or product-local dispatcher instead. | INFERENCE |
| RISK-04 | Strict C89 and C++98 are violated by generated snippets. | high | Audit for long long, std::snprintf, declarations, and modern constructs. | INFERENCE |
| RISK-05 | q48_16/u64/i64 implementation relies on non-C89 compiler extensions without clear fallback. | high | Define portability policy or emulation for strict C89 targets. | INFERENCE |
| RISK-06 | Native-endian TLV save/load conflicts with cross-platform compatibility. | high | Introduce endian-stable TLV helpers early. | INFERENCE |
| RISK-07 | Minimal JSON manifest parser is brittle. | medium | Constrain manifest subset or replace with robust deterministic parser/TLV manifest. | INFERENCE |
| RISK-08 | Layering violations introduced by Codex. | high | Each prompt must explicitly restate dsys/dgfx boundaries and reviews must enforce them. | INFERENCE |
| RISK-09 | Broad GUI/TUI/dgfx prompts overreach existing API maturity. | medium-high | Split prompts after repo inspection. | INFERENCE |
| RISK-10 | GUI/TUI product logic diverges from CLI behavior. | medium-high | Use shared state machines and product action models. | INFERENCE |
| RISK-11 | GUI directly depends on raster/theme packs and breaks vector-only fallback. | medium | Ensure built-in vector style/icon pack remains mandatory. | INFERENCE |
| RISK-12 | IME/input event timing contaminates deterministic sim. | high | Input event streams are deterministic per frame; sim RNG isolated from UI systems. | INFERENCE |
| RISK-13 | Backend detection or GUI timing uses nondeterministic environment values for sim-affecting choices. | high | Keep render/UI backend separate from sim; fixed tick and deterministic input stream. | INFERENCE |
| RISK-14 | Pack-system prompt becomes too broad and under-specified. | medium-high | Split pack prompt or define pack manifest and deterministic load order first. | INFERENCE |
| RISK-15 | Windows/macOS packaging realities break one-binary startup assumptions. | medium-high | Decide Windows subsystem and macOS bundle strategy after repo/build inspection. | INFERENCE |
| RISK-16 | Questionnaire answer carries stale/external software-version claims. | medium | Re-verify current docs/toolchains before using. | UNCERTAIN / UNVERIFIED |
| RISK-17 | This final report package over-compresses generated prompts. | medium | Report preserves prompt objectives, files, constraints, APIs, and risks; original chat remains ideal source for exact wording. | INFERENCE |
| RISK-18 | Future aggregator merges recommendations as decisions. | high | Use labels/status fields and preserve uncertainty. | FACT |

### Verification Queue

| ID | Verification item | Priority | Suggested source | Label |
|---|---|---|---|---|
| VERIFY-01 | Open/extract dominium.zip or current checkout. | highest | file inspection | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Inspect root CMakeLists.txt, source CMake files, and CMakePresets.json. | highest | repo files | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Search for files specified by prompts 1-6. | high | repo file tree | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Build golden target set and run numeric/headless tests. | high | CMake/Ninja/test run | INFERENCE |
| VERIFY-05 | Inspect numeric typedef/fixed-point implementation for C89 compliance. | high | source review | INFERENCE |
| VERIFY-06 | Inspect existing CLI/TUI/GUI/input/state modules before applying common-framework prompts. | medium-high | repo file inspection | INFERENCE |
| VERIFY-07 | Inspect dgfx/render headers and backend implementation names. | high | repo file inspection | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Inspect content/pack/data format docs before generating pack-system prompt. | high | repo docs/source inspection | INFERENCE |
| VERIFY-09 | Inspect CMake target graph before implementing startup dispatcher. | highest | CMake/source review | INFERENCE |
| VERIFY-10 | Verify platform tier/render backend claims in docs/source. | medium-high | docs/source inspection | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Verify third-party library/vendor/toolchain claims. | medium | repo external dir, docs, build environment | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Download and store the generated report package files/ZIP. | high | user local storage | FACT |

## 6. Possible Cross-Chat Duplicates

- Master architecture constraints may appear in many chats.
- Platform/render matrix likely overlaps with repo/docs-focused chats.
- Codex prompt sequences may be copied into implementation chats.
- Startup CLI/TUI/GUI policy may overlap product UX chats.

## 7. Possible Cross-Chat Conflicts

- C89 vs long long/64-bit implementation strategy.
- Native-endian TLV in early prompt vs cross-platform save compatibility.
- Monolithic domino_core vs modular domino_sys/domino_gfx target architecture.
- Windows one-binary UX vs console/windows subsystem build mode.
- D3D12 mention in questionnaire vs master prompt backends.

## 8. Spec Book Integration Guidance

- Feed this chat into chapters covering architecture, determinism/language policy, dsys, dgfx, product model, startup UX, prompt workflow, and verification policy.
- Promote hard user constraints to formal requirements.
- Keep assistant recommendations as rationale/context unless later user confirmation exists.
- Do not merge questionnaire repo facts into final spec until current repo files are inspected.
- Do not formalize missing pack-system implementation details until the prompt is generated and verified.

## 9. Aggregator Warnings

- Do not assume generated prompts were executed.
- Do not assume prior assistant repo inspection was real or complete.
- Do not treat native-endian TLV or long long C89 handling as final.
- Preserve the missing pack-system prompt as an open task.
- Preserve the startup dispatcher linker-risk caveat.
