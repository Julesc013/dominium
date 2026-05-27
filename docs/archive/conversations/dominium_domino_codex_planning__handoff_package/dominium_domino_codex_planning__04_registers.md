# Registers — Dominium Domino Codex Planning

## 1. Workstream Register

| ID | Name | Status | Priority | Current state | Next action | Label | Confidence |
|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Dominium + Domino Core Architecture Continuity | active | highest | The chat established the architecture constraints in the user's Extended Master Starter Prompt and the prior transfer packet preserved them. Actual repo implementation state must be verified separately. | Verify current repo, then continue from the relevant prompt/workstream. | FACT | 5/5 |
| WORKSTREAM-02 | Milestone-0 Vertical Slice via Six Codex Prompts | active / execution uncertain | highest | Six Codex prompts were generated. It is not established in this chat whether they were executed. | Inspect repo for files from prompts 1-6 and run the golden build/test set. | FACT | 5/5 |
| WORKSTREAM-03 | Shared CLI, TUI, and GUI Layers Across Products | active / execution uncertain | high | Three Codex prompts were generated for universal CLI, TUI, and GUI. Execution status is not established. | Verify existing CLI/TUI/GUI modules and decide whether to split prompts before implementation. | FACT | 5/5 |
| WORKSTREAM-04 | Shared Input System, State Machines, and Cross-Platform IME | active / execution uncertain | high | A Codex prompt was generated. Execution status is not established. | Inspect current source/domino/input and source/domino/state before applying. | FACT | 5/5 |
| WORKSTREAM-05 | Multi-Window GUI, dgfx Pipelines, and GPU Backend Detection | active / execution uncertain | medium-high | A Codex prompt was generated. Execution status is not established. | Rewrite prompt against actual renderer headers after repo verification if necessary. | FACT | 5/5 |
| WORKSTREAM-06 | Pack System Integration Prompt | active / not yet produced | high if continuing prompt sequence | User requested this as the third prompt, but it was not generated before the conversation changed direction. | Generate missing prompt when requested; preferably verify pack docs first. | FACT | 5/5 |
| WORKSTREAM-07 | Unified Startup and Mode Dispatcher | active / prompt generated, implementation uncertain | high | Recommendations were made and a large Codex prompt was generated. It contains a known potential linker design risk. | Refine implementation design with callback table or product-local dispatcher before applying prompt. | FACT | 5/5 |
| WORKSTREAM-08 | Platform, Renderer, API Questionnaire and Repo-State Answer | active / verification required | medium-high | User pasted a questionnaire and a Codex-in-repo answer; assistant produced a refined answer but repo inspection evidence is not visible in this chat. | Inspect uploaded/current repo before relying on prior questionnaire details. | UNCERTAIN / UNVERIFIED | 3/5 |
| WORKSTREAM-09 | Chat Handoff and Report Package | active / being completed in this response | highest for this final chat task | This response creates the final package files, including report, YAML, aggregator packet, registers, reader brief, verification/audit, manifest, and ZIP. | Store package and use it as source for next chat or later aggregation. | FACT | 5/5 |

## 2. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Domino engine is ISO C89. | decided | User Extended Master Starter Prompt. | Maximal portability and stable C ABI across retro/modern platforms. | Domino modules cannot use C99/C11 or C++ features. | WORKSTREAM-01 | see uncertainty | FACT |
| DECISION-02 | Dominium product/UI code may use portable C++98 subset where needed. | decided | User Extended Master Starter Prompt. | Allows product/UI structure while preserving old-platform portability. | No C++11+, exceptions, RTTI-heavy design, or modern STL assumptions unless user later changes policy. | WORKSTREAM-01 | see uncertainty | FACT |
| DECISION-03 | All platform interaction must go through dsys. | decided | User Extended Master Starter Prompt. | Prevents platform divergence and direct OS calls in products/sim/render logic. | Windowing/input/fs/process/timing abstractions belong in dsys/platform backends. | WORKSTREAM-01 | see uncertainty | FACT |
| DECISION-04 | All rendering must go through dgfx IR/backends. | decided | User Extended Master Starter Prompt. | Supports software/GPU/retro renderers without product-side native drawing. | GUI/TUI/game rendering cannot call OS-native immediate drawing APIs directly. | WORKSTREAM-01, WORKSTREAM-03, WORKSTREAM-05 | see uncertainty | FACT |
| DECISION-05 | Software renderer is mandatory baseline. | decided | User Extended Master Starter Prompt. | Deterministic baseline and fallback for retro/no-GPU targets. | GPU backends optional; soft must remain functional. | WORKSTREAM-01, WORKSTREAM-05 | see uncertainty | FACT |
| DECISION-06 | Vector-only fallback UI/pack path must always function. | decided | User Extended Master Starter Prompt. | Products must work with zero raster packs installed. | Built-in vector style/icon/theme fallback required. | WORKSTREAM-01, WORKSTREAM-03, WORKSTREAM-06 | see uncertainty | FACT |
| DECISION-07 | DOMINIUM_HOME repository model is canonical for products, mods, packs, and instances. | decided | User Extended Master Starter Prompt. | Allows multiple product/core/pack/mod versions and non-destructive imports. | Launcher/setup/tools must use repo paths and instance IDs rather than hardcoded product paths. | WORKSTREAM-01, WORKSTREAM-02 | see uncertainty | FACT |
| DECISION-08 | Backward/forward compatibility is mandatory for saves, packs, mods, tools where possible. | decided | User Extended Master Starter Prompt. | User explicitly says never break old instances/packs/mods/tools/content. | Versioned ABI/format headers, compatibility profiles, migration/read-only fallback. | WORKSTREAM-01, WORKSTREAM-06 | see uncertainty | FACT |
| DECISION-09 | First implementation should be a narrow Milestone-0 vertical slice. | recommended and implicitly accepted | Assistant recommended narrowing; user proceeded to request six Codex prompts following that path. | Avoid architecture overreach and prove core layering early. | Retro/GPU/full UI/hydrology/net delayed until skeleton works. | WORKSTREAM-02 | see uncertainty | INFERENCE |
| DECISION-10 | Codex prompts should be self-contained implementation packages. | working decision | User repeatedly requested Codex prompts; assistant generated self-contained prompts. | Codex sessions may not share context reliably. | Prompts must include constraints, assumptions, files, outputs, and scope restrictions. | WORKSTREAM-02, WORKSTREAM-03, WORKSTREAM-04, WORKSTREAM-05, WORKSTREAM-06, WORKSTREAM-07 | see uncertainty | FACT |
| DECISION-11 | CLI/TUI/GUI should be common/shared across launcher, game, setup, and tools. | decided by user request | User requested three prompts completing CLI, TUI, GUI features for each product using common components. | Avoid duplicated UI/tooling pipelines and preserve product consistency. | Common modules under Domino; product wrappers in Dominium. | WORKSTREAM-03 | see uncertainty | FACT |
| DECISION-12 | TUI and GUI must use dsys/dgfx abstractions, not direct platform drawing. | decided | User master prompt plus generated TUI/GUI prompt constraints. | Preserve strict layering and portability. | TUI outputs through dsys terminal; GUI through dgfx IR. | WORKSTREAM-03 | see uncertainty | FACT |
| DECISION-13 | Input/IME/state machine systems should be shared and deterministic. | prompt generated | Generated input/state/IME Codex prompt. | Unified event ordering and shared UI/product states reduce divergence. | GUI/TUI text inputs should consume the same event/IME model. | WORKSTREAM-04 | see uncertainty | FACT |
| DECISION-14 | GPU backend detection must always include software fallback. | prompt generated / architecture-consistent | Generated multi-window/dgfx prompt and master prompt software baseline. | Guarantee render availability and deterministic fallback. | Backend selection should be deterministic and never leave no renderer when soft can run. | WORKSTREAM-05 | see uncertainty | FACT |
| DECISION-15 | Terminal invocation with no explicit mode defaults to CLI. | decided by user request | User said binaries when 'called in the terminal uses the cli'. | Expected scripting/terminal behavior. | Startup needs dsys terminal detection and AUTO policy. | WORKSTREAM-07 | see uncertainty | FACT |
| DECISION-16 | Double-click/no-terminal launch defaults to GUI, then TUI, then CLI fallback. | decided by user request | User said double clicked in desktop explorer defaults to gui, then if that fails tui, then if that fails. | Desktop UX with degradation path. | Startup fallback chain and structural error codes needed. | WORKSTREAM-07 | see uncertainty | FACT |
| DECISION-17 | Explicit --mode flags should override AUTO heuristics. | recommended and accepted by requesting prompt | Assistant recommended; user asked for one big prompt implementing it. | Predictability and scriptability. | Mode parser runs before terminal/double-click heuristic. | WORKSTREAM-07 | see uncertainty | INFERENCE |
| DECISION-18 | Game --server/--dedicated/--listen/--mode=headless force headless and bypass GUI/TUI. | recommended and included in generated prompt | Assistant recommendation and generated startup prompt. | Server/CI determinism and no accidental UI init. | Headless is not in AUTO fallback; only explicit/server flags. | WORKSTREAM-07 | see uncertainty | INFERENCE |
| DECISION-19 | Do not add env/config startup mode overrides in v1. | recommended | Assistant recommendation response. | Avoid reproducibility/config complexity before startup core stabilizes. | Only flags and terminal-detection heuristic initially. | WORKSTREAM-07 | see uncertainty | INFERENCE |
| DECISION-20 | Fallback should occur only on structural GUI/TUI unsupported errors, not logical/content errors. | recommended | Assistant recommendation response and startup prompt. | Avoid hiding real errors behind fallback behavior. | Need distinct error codes and careful wrapper behavior. | WORKSTREAM-07 | see uncertainty | INFERENCE |
| DECISION-21 | This old chat should be exported as a downloadable multi-file report package. | decided by user request | User final request to produce files/ZIP if available. | User wants old chat reusable, shareable, aggregatable, and source material for future project spec book. | Create Markdown/YAML/ZIP package with registers and stable IDs. | WORKSTREAM-09 | see uncertainty | FACT |

## 3. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Verify actual repo state from dominium.zip or current checkout. | highest | immediate | future assistant / user tooling | none | dominium.zip or repo checkout | Verified file tree, docs, CMake targets, and prompt-execution status. | Extract/list repo and inspect key files. | WORKSTREAM-01, WORKSTREAM-02, WORKSTREAM-08 | FACT |
| TASK-02 | Determine which generated Codex prompts were executed. | highest | immediate | future assistant / user | TASK-01 | repo file tree, git status or file timestamps | Map of prompts to actual files/changes. | Search for files named in each prompt. | WORKSTREAM-02 | FACT |
| TASK-03 | Build and run golden target set. | high | early | user/Codex | TASK-01 | CMake build dir, toolchain | Build/test status for core targets. | Run CMake/Ninja targets and numeric/headless tests. | WORKSTREAM-02, WORKSTREAM-08 | INFERENCE |
| TASK-04 | Audit generated numeric core for strict C89 and deterministic overflow behavior. | high | before merge | Codex/future assistant | TASK-02 | types.h, fixed.c, rng.c | C89-compatible numeric core or issue list. | Check 64-bit typedefs, saturation constants, shifts, and no floating point in sim path. | WORKSTREAM-02 | INFERENCE |
| TASK-05 | Define endian-stable TLV IO helpers if not already present. | high | before cross-platform save reliance | Codex/future assistant | TASK-01 | DATA_FORMATS docs, sim save/load code | Stable little-endian or documented binary serialization helpers. | Inspect existing TLV/data format rules. | WORKSTREAM-01, WORKSTREAM-02 | INFERENCE |
| TASK-06 | Verify launcher→game process spawn path and manifest path handling. | high | after Milestone-0 code exists | Codex/user | TASK-02, TASK-03 | DOMINIUM_HOME test repo, product.json, built game executable | Launcher can spawn game and report exit code. | Run launcher run-game command with seed/ticks. | WORKSTREAM-02 | INFERENCE |
| TASK-07 | Keep docs/specs aligned with generated code. | medium-high | ongoing | Codex/future assistant | TASK-02 | docs, implemented headers | No drift between SPEC docs and actual code. | Diff generated headers/APIs against docs. | WORKSTREAM-01, WORKSTREAM-02 | INFERENCE |
| TASK-08 | Implement or refine common CLI framework. | medium-high | after Milestone-0 | Codex | TASK-01, TASK-02 | Universal CLI prompt, existing CLI code | Shared CLI registry and product command routing. | Inspect source/domino/cli and product CLI code. | WORKSTREAM-03 | FACT |
| TASK-09 | Implement or refine common TUI framework. | medium | after dsys terminal exists | Codex | TASK-01, TASK-08 | Universal TUI prompt, dsys terminal APIs | Shared deterministic text UI framework. | Inspect dsys terminal implementation state. | WORKSTREAM-03 | FACT |
| TASK-10 | Implement or refine common GUI framework. | medium | after dgfx/window baseline | Codex | TASK-01, TASK-12 | Universal GUI prompt, dgfx/window APIs | Shared widget/tree/style GUI through dgfx. | Inspect render/gui modules. | WORKSTREAM-03, WORKSTREAM-05 | FACT |
| TASK-11 | Implement shared input/state/IME after inspecting existing modules. | medium-high | before full TUI/GUI | Codex | TASK-01 | Input/state/IME prompt, existing input/state code | Unified event queue, state machine, IME abstraction. | Search source/domino/input and source/domino/state. | WORKSTREAM-04 | FACT |
| TASK-12 | Implement or rewrite multi-window/dgfx pipeline/backend detection prompt against actual renderer API. | medium | after dgfx baseline | Codex/future assistant | TASK-01 | Renderer headers/docs, Prompt 2 of 3 | Repo-aligned backend/pipeline/multi-window implementation plan. | Compare proposed APIs with include/domino/gfx.h and render sources. | WORKSTREAM-05 | FACT |
| TASK-13 | Generate the missing pack system integration Codex prompt. | high if continuing prompt sequence | next on that branch | future assistant | TASK-01 optional | Pack/content docs if available | Self-contained prompt for packs, themes, vector icons, shader/audio/texture assets, asset streaming. | If user asks 'next', generate prompt; if repo-specific, inspect docs first. | WORKSTREAM-06 | FACT |
| TASK-14 | Refine unified startup dispatcher design to avoid linker/circular dependency issues. | highest for startup implementation | before applying prompt | future assistant/Codex | TASK-01 | CMake target graph, product entry structure | Safe startup implementation prompt/design using callbacks or product-local dispatchers. | Inspect CMake/product target linkage. | WORKSTREAM-07 | INFERENCE |
| TASK-15 | Implement dsys_running_in_terminal for active platforms. | high | when implementing startup | Codex | TASK-14 | dsys platform layout | POSIX/WinNT/stub terminal detection. | Wire one implementation per platform in CMake. | WORKSTREAM-07 | FACT |
| TASK-16 | Implement startup mode parsing, capabilities, and product mode wrappers. | high | after dispatcher design fixed | Codex | TASK-14, TASK-15 | product CLI/TUI/GUI/headless functions | Consistent startup behavior across launcher/game/setup/tools. | Refactor product main functions. | WORKSTREAM-07 | FACT |
| TASK-17 | Produce a verified platform/render/API questionnaire answer from actual repo/docs. | medium-high | when needed for planning/spec | future assistant | TASK-01 | questionnaire, repo docs, CMake, source tree | Accurate labelled questionnaire response with file evidence. | Inspect files; do not rely solely on previous assistant answer. | WORKSTREAM-08 | FACT |
| TASK-18 | Save this chat-specific report package and ZIP for future aggregation. | highest for current task | now | assistant/user | none | this chat context, previous transfer packet | Seven report files plus ZIP download. | Download/store the generated package. | WORKSTREAM-09 | FACT |

## 4. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Domino engine code must be ISO C89/C90. | language | hard | User master prompt; root CMake pasted by user also sets C_STANDARD 90. | Avoid C99/C11 constructs, C++ in Domino, mixed declarations if strict, and non-portable types unless abstracted. | high | 5/5 | FACT |
| CONSTRAINT-02 | Dominium product/UI code must be portable C++98 where needed. | language | hard | User master prompt; pasted root CMake sets CXX_STANDARD 98. | Avoid C++11+, exceptions if policy forbids, modern STL constructs, std::snprintf portability assumptions. | medium-high | 5/5 | FACT |
| CONSTRAINT-03 | Simulation must be deterministic across supported OS/architectures. | determinism | hard | User master prompt. | Fixed timestep, deterministic RNG, deterministic scheduling and serialization; UI/render/platform must not change sim state. | high | 5/5 | FACT |
| CONSTRAINT-04 | Core simulation uses fixed-point/integer numeric formats including u8/i8/u16/i16/u32/i32/u64/i64/q4_12/q16_16/q24_8/q48_16. | numeric | hard | User explicit correction before Prompt 1. | Numeric core must define and consistently use these formats; 64-bit under strict C89 needs special handling. | high | 5/5 | FACT |
| CONSTRAINT-05 | No host floating point inside deterministic simulation logic. | determinism | hard | User master prompt. | No float/double math in sim/world/replay/net deterministic paths. | high | 5/5 | FACT |
| CONSTRAINT-06 | All platform-specific interactions route through dsys. | layering | hard | User master prompt. | Products and deterministic core must not call OS APIs directly. | medium-high | 5/5 | FACT |
| CONSTRAINT-07 | All rendering routes through dgfx IR/backend abstraction. | layering | hard | User master prompt. | No product/game OS-native drawing; GUI produces draw list/IR. | medium-high | 5/5 | FACT |
| CONSTRAINT-08 | Vector-only fallback must always work. | UI/assets | hard | User master prompt. | GUI/theme/icon systems cannot require raster packs. | medium | 5/5 | FACT |
| CONSTRAINT-09 | Old saves, packs, mods, instances, and tools must not silently break. | compatibility | hard | User master prompt. | Need versioned formats, compatibility profiles, migration/read-only/incompatible decisions. | high | 5/5 | FACT |
| CONSTRAINT-10 | DOMINIUM_HOME repository layout supports multiple coexisting versions and non-destructive import. | repo/model | hard | User master prompt. | Launcher/setup/pkg code must resolve products/mods/packs/instances through repo model. | medium | 5/5 | FACT |
| CONSTRAINT-11 | GUI/TUI/CLI product logic should be shared, not duplicated. | architecture | hard | User master prompt and explicit common-components request. | Common modules with product wrappers; avoid separate behavior pipelines. | medium | 5/5 | FACT |
| CONSTRAINT-12 | Startup explicit mode flags override AUTO; no-terminal launch tries GUI/TUI/CLI; terminal launch uses CLI. | startup behavior | hard for user desired behavior; implementation details pending | User startup request and accepted assistant prompt. | Requires terminal detection, mode parser, fallback error classification. | medium | 5/5 | FACT |
| CONSTRAINT-13 | Repo-specific claims must be verified against files before future use. | evidence | hard for future accuracy | User requested repo/doc-derived data; previous inspection claim unverified in visible chat. | Future assistant must inspect dominium.zip/current checkout before acting on repo details. | high | 5/5 | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-14 | External-world facts/software versions/APIs/current state require verification before future use. | evidence/staleness | hard | User final package rules and system web-verification requirement. | Do not rely on stale toolchain/API claims without checking. | medium | 5/5 | FACT |
| CONSTRAINT-15 | This final package is scoped to this chat only. | scope | hard | User final request. | Do not summarize the whole project beyond context visible in this chat; label project context. | medium | 5/5 | FACT |
| CONSTRAINT-16 | Final package must preserve tentative status, rejected options, artifacts, risks, contradictions, and stable IDs. | reporting/output | hard | User final request. | Report files must include registers and not flatten uncertainty. | medium | 5/5 | FACT |

## 5. User Preference Register

| ID | Preference | Source basis | Strength | Implication | Risk | Label |
|---|---|---|---|---|---|---|
| PREF-01 | Direct, technical, concise responses with no filler. | User profile/instructions in chat context. | high | Future assistants should avoid hype, soft asks, and conversational padding. | Responses may feel evasive or bloated. | FACT |
| PREF-02 | Use rigorous, verified, cited facts where factual claims matter. | User profile says correctly cited sources and rigorously tested facts; final request demands verification labels. | high | Inspect repo/files/web where required; label uncertainty. | Unverified claims may be mistaken for decisions/facts. | FACT |
| PREF-03 | Prefer second- and third-order architectural thinking. | User profile. | medium-high | Discuss implications, risks, dependencies, and future-proofing. | Overly shallow implementation prompts may create rework. | FACT |
| PREF-04 | Generate self-contained Codex prompts for implementation work. | User repeatedly requested prompts to give to Codex. | high within this chat | Future prompts should include scope, constraints, file paths, output expectations. | Codex may lack context and implement incorrectly. | INFERENCE |
| PREF-05 | Do not ask unnecessary clarifying questions; make best-effort recommendations. | User instruction profile and developer instruction favor best effort. | high | Proceed with reasonable assumptions while labelling them. | Work may stall on avoidable questions. | FACT / PROJECT-CONTEXT |
| PREF-06 | Start each message with model version and build date. | User instruction profile. | high | Future assistant should use this format unless higher-priority instructions conflict. | User formatting preference violated. | FACT |
| PREF-07 | Preserve maximum-fidelity context across chats. | Current and prior context-transfer requests. | high | Reports should be structured, auditable, and downloadable when possible. | Loss of prior decisions/prompts/tasks. | FACT |
| PREF-08 | Be critical by default, especially about over-broad scope and implementation risks. | User profile says be critical by default; assistant recommendations followed this. | high | Flag architectural risks and prompt design flaws rather than just comply superficially. | Risky prompts may be executed without safeguards. | FACT |

## 6. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Which generated Codex prompts have actually been applied to the repo? | Avoid duplicate/conflicting code and determine true implementation state. | Prompts were generated in this chat. | Execution status and resulting file changes. | Inspect repo/git state for files and diffs. | highest | WORKSTREAM-02, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | What is the actual current repo structure and target list in dominium.zip/current checkout? | Implementation prompts must match actual files and CMake targets. | User says dominium.zip is up to date; user pasted some tree/CMake/target data. | Whether pasted data matches current repo; previous inspection claim not proven. | Open/extract repo and inspect key files. | highest | WORKSTREAM-01, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Does the repo already contain files from prompts 1-6? | Determines whether to implement, repair, or skip Milestone-0 tasks. | File names were specified in prompts. | Actual existence/content. | Search for docs/SPEC_IDENTITY.md, include/domino/core/fixed.h, repo.h, sim.h, etc. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | How should strict C89 support exact 64-bit types and q48_16 across retro compilers? | User requires u64/i64/q48_16, but ISO C89 lacks long long. | Generated prompt suggested compiler-guarded long long, which is not ISO C89. | Existing repo policy for 64-bit portability. | Inspect existing type headers/docs; decide emulation or compiler-extension policy. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Should TLV save format be native-endian temporarily or endian-stable immediately? | Cross-platform save compatibility is a core requirement. | Prompt 5 allowed native-endian for Milestone 0; project requires compatibility. | Existing data format endian rules. | Inspect docs/DATA_FORMATS.md and TLV code. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Where should startup mode dispatch live to avoid C/C++ linker issues? | Generated prompt risks unresolved symbols from domino_core to all product wrappers. | Startup prompt proposed startup.c in Domino calling product-specific C++ functions. | Actual target linkage and best design. | Inspect CMake; prefer callback table or product-local dispatcher. | highest | WORKSTREAM-07 | INFERENCE |
| QUESTION-07 | Should Windows products be console-subsystem, windows-subsystem, or dual wrapper binaries? | Affects terminal detection and double-click UX. | User wants one executable behavior; assistant noted Windows subsystem concerns. | Final packaging/build choice. | User/build-system decision after inspecting packaging targets. | high | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Should future startup mode overrides via env/config be supported? | Affects mode precedence and reproducibility. | Assistant recommended no env/config in v1. | User's long-term preference. | Defer until config system stabilizes or user requests. | low | WORKSTREAM-07 | INFERENCE |
| QUESTION-09 | What are final Tier 1/2/3 platform priorities? | Prevents overbuilding retro/GPU targets before core platforms work. | Master prompt lists a huge matrix; questionnaire answer proposes tiers. | Confirmed priority order after repo verification. | Verify docs and ask/confirm only if needed. | medium | WORKSTREAM-01, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | Should common CLI/TUI/GUI prompts be applied as broad prompts or split into smaller implementation prompts? | Large prompts risk inconsistent code. | Prompts exist and are broad. | Repo maturity and existing modules. | Inspect current modules and decide module-by-module. | medium | WORKSTREAM-03 | INFERENCE |
| QUESTION-11 | How complete are current input/state/IME modules? | Generated prompt may overwrite or duplicate existing work. | Prompt was generated; prior repo answer mentioned input/IME modules but unverified. | Actual module content. | Inspect source/domino/input and source/domino/state. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Which render backends are actually wired and which are only source-tree stubs? | Backend detection/pipeline prompt must match implementation reality. | Prior answer lists soft/DX/GL/Metal/Vulkan/retro, but verification needed. | Actual build wiring and API shape. | Inspect render docs, source/domino/render, CMake. | high | WORKSTREAM-05, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Is D3D12 in scope? | Questionnaire included D3D12, but master prompt emphasized DX7/9/11. | D3D12 appeared in questionnaire, not clearly in master prompt. | Repo/docs current stance. | Inspect render docs and ask user if needed. | medium | WORKSTREAM-05, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | What pack format(s) should the missing pack-system prompt target: TLV, JSON metadata, or both? | Pack integration must preserve compatibility and deterministic load order. | User master prompt mentions TLV or JSON metadata and versioned pack format. | Existing repo implementation/docs. | Inspect content/pack docs and source. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | How should shader packs be represented across multiple render backends? | Shader packs interact with dgfx backend pipelines and offline/runtime compilation. | User wants shader packs included; prior answer says toolchains not vendored but unverified. | Allowed shader languages/artifacts and pack compatibility rules. | Inspect render docs and decide per backend. | medium-high | WORKSTREAM-06, WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |

## 7. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Extended Master Starter Prompt — Dominium + Domino | user project spec | Canonical project constraints and architecture context. | active source material | User first message in chat | yes | Includes role/tone, global identity, repo layout, platform matrix, dsys, dgfx, UI/packs, product model, versioning, repo model, sim/modding/rendering constraints. | FACT |
| ARTIFACT-02 | Assistant acknowledgement of master prompt | assistant response | Restated key constraints to operate under. | historical | Assistant response after user master prompt | limited | Useful as early confirmation, but user prompt outranks it. | FACT |
| ARTIFACT-03 | Forward plan phases 0-12 | plan | Roadmap from docs/specs to replay/networking. | planning reference | Assistant response to 'generate a plan going forwards' | yes | Phase list included specs, layout, dsys, dgfx, UI, repo model, launcher, game, tools, packs, retro, replay/net, docs/examples. | FACT |
| ARTIFACT-04 | Codex Prompt 1 — SPEC_IDENTITY + SPEC_PRODUCTS | Codex prompt | Create two canonical spec docs only. | generated, execution unknown | Assistant | yes | Files: docs/SPEC_IDENTITY.md, docs/SPEC_PRODUCTS.md. | FACT |
| ARTIFACT-05 | Codex Prompt 2 — Repo layout, CMake skeleton, core/product targets | Codex prompt | Create canonical layout, CMake, stub core/product code. | generated, execution unknown | Assistant | yes | Defines include/source layout and targets domino_core, dominium_game, dominium_launcher. | FACT |
| ARTIFACT-06 | Codex Prompt 3 — Deterministic numeric core + test harness | Codex prompt | Implement types/fixed/rng and domino_numeric_test. | generated, execution unknown | Assistant | yes | Requires audit for strict C89 and saturation correctness. | FACT |
| ARTIFACT-07 | Codex Prompt 4 — DOMINIUM_HOME repo model + launcher enumeration | Codex prompt | Implement repo.h/repo.c, product.json subset, launcher printout. | generated, execution unknown | Assistant | yes | Hardcoded platform path and minimal JSON parser require future cleanup. | FACT |
| ARTIFACT-08 | Codex Prompt 5 — Deterministic sim + headless game + TLV save | Codex prompt | Implement minimal d_world, deterministic ticks, checksum, TLV, game headless flags. | generated, execution unknown | Assistant | yes | Native-endian TLV and RNG state load details need review. | FACT |
| ARTIFACT-09 | Codex Prompt 6 — Launcher to game process spawn via dsys | Codex prompt | Add process API and launcher run-game command. | generated, execution unknown | Assistant | yes | C++98 formatting and path duplication risks. | FACT |
| ARTIFACT-10 | Prompt A — Universal CLI Layer | Codex prompt | Shared CLI framework across launcher/game/setup/tools. | generated, execution unknown | Assistant | yes | Includes command registry and product command lists. | FACT |
| ARTIFACT-11 | Prompt B — Universal TUI Layer | Codex prompt | Shared dsys-terminal-based TUI framework. | generated, execution unknown | Assistant | yes | Adds dsys_terminal_* API and text widgets. | FACT |
| ARTIFACT-12 | Prompt C — Universal GUI Layer | Codex prompt | Shared dgfx-based GUI framework and vector style pack. | generated, execution unknown | Assistant | yes | Adds GUI primitives, widgets, style, product GUI modes. | FACT |
| ARTIFACT-13 | Prompt — Shared Input System + State Machines + Cross-Platform IME | Codex prompt | Unified input events, state machines, IME abstraction. | generated, execution unknown | Assistant | yes | First of requested three advanced prompts. | FACT |
| ARTIFACT-14 | Prompt — Multi-window GUI + dgfx Pipelines + GPU Backend Detection | Codex prompt | Logical multi-window GUI, dgfx pipeline/pass/target APIs, backend selection. | generated, execution unknown | Assistant | yes | Second of requested advanced prompts. | FACT |
| ARTIFACT-15 | Missing Prompt — Pack system integration | requested but not generated | Would cover sound/music/texture/shader/theme packs, vector icons, asset streaming. | not yet produced | User request | yes | Likely next prompt if continuing that sequence. | FACT |
| ARTIFACT-16 | Prompt — Unified Startup / Mode Dispatcher | Codex prompt | Implement CLI/default terminal and GUI→TUI→CLI desktop fallback across products. | generated, execution unknown | Assistant | yes, with design fixes | Known linker-risk due startup.c referencing all product wrappers. | FACT |
| ARTIFACT-17 | User questionnaire: Platforms, Renderers, APIs, Completion, Repo/build context | user prompt/questionnaire | Collect detailed repo/platform/render/API facts. | answered but verification required | User | yes | Should be answered again from verified repo if used for spec. | FACT |
| ARTIFACT-18 | User-pasted Codex-in-repo questionnaire answer | pasted output | Candidate answer filled from repo/docs by Codex in repo. | unverified candidate data | User paste | yes with uncertainty | Includes platform tiers, subsystem table, renderers, APIs, build context. | FACT |
| ARTIFACT-19 | Assistant refined questionnaire answer | assistant output | Further filled platform/render/API/build answer. | unverified candidate data | Assistant | yes with verification caveat | Claimed repo extraction/inspection but visible trace absent. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-20 | User-pasted root CMakeLists.txt | file content excerpt | Build context reference. | pasted; current repo validity unverified | User/Codex answer | yes | Sets C90/C++98, adds source/domino, source/dominium, source/tests. | FACT |
| ARTIFACT-21 | User-pasted source/CMakeLists.txt | file content excerpt | Aggregated source layout reference. | pasted; current repo validity unverified | User/Codex answer | yes | Adds domino, dominium, tools subdirs. | FACT |
| ARTIFACT-22 | User-pasted source tree excerpt | file tree excerpt | Repo structure reference. | pasted; current repo validity unverified | User/Codex answer | yes | Shows source/domino modules including app/audio/cli/gui/input/render/state/tui etc. | FACT |
| ARTIFACT-23 | User-pasted docs/OVERVIEW_ARCHITECTURE.md excerpt | documentation excerpt | Architecture context and repo layout reference. | pasted; current repo validity unverified | User/Codex answer | yes | Mentions Domino C89, Dominium C++98, DOMINIUM_HOME layout, common layer. | FACT |
| ARTIFACT-24 | Context Transfer Packet from prior assistant | handoff document | Maximum-fidelity continuity state for new chat. | source for this final package | Assistant previous response | yes | This final package audits and normalizes it. | FACT |
| ARTIFACT-25 | dominium_domino_codex_planning__01_full_chat_report.md | generated file | Main human-readable report for this chat. | created by this response | Assistant final packaging | yes | Primary report. | FACT |
| ARTIFACT-26 | dominium_domino_codex_planning__02_spec_sheet.yaml | generated file | Structured YAML for later spec-book construction. | created by this response | Assistant final packaging | yes | Aggregator-ready structured data. | FACT |
| ARTIFACT-27 | dominium_domino_codex_planning__03_aggregator_packet.md | generated file | Compact merge packet for future aggregation. | created by this response | Assistant final packaging | yes | Use when combining multiple chats. | FACT |
| ARTIFACT-28 | dominium_domino_codex_planning__04_registers.md | generated file | Standalone normalized registers. | created by this response | Assistant final packaging | yes | Tables for workstreams/decisions/tasks/etc. | FACT |
| ARTIFACT-29 | dominium_domino_codex_planning__05_reader_brief.md | generated file | Short human-readable brief. | created by this response | Assistant final packaging | yes | Fast onboarding. | FACT |
| ARTIFACT-30 | dominium_domino_codex_planning__06_verification_and_audit.md | generated file | Audit and residual risk record. | created by this response | Assistant final packaging | yes | QC file. | FACT |
| ARTIFACT-31 | dominium_domino_codex_planning__manifest.md | generated file | Package manifest and item counts. | created by this response | Assistant final packaging | yes | Lists files and counts. | FACT |
| ARTIFACT-32 | dominium_domino_codex_planning__handoff_package.zip | generated ZIP | Bundled downloadable package. | created by this response | Assistant final packaging | yes | Contains all seven files. | FACT |
| ARTIFACT-33 | Copy-paste bootstrap prompt from previous transfer packet | prompt text | Start a new chat with continuity from this one. | included in previous packet and adapted in reports | Assistant previous response | yes | Useful for new assistant setup. | FACT |
| ARTIFACT-34 | Later aggregator prompt supplied by user | prompt text | Future central aggregation of many old chat packages into spec book/living state file. | user-supplied in final request | User | yes | Should be used when all packages are collected. | FACT |

## 8. Rejected / Superseded Options Register

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Build all platforms, renderers, and systems at once. | deprioritised | Assistant warned it would likely stall the project; user proceeded with narrower prompts. | tentative until Milestone 0 works | After vertical slice and core tests are stable. | WORKSTREAM-01, WORKSTREAM-02 | INFERENCE |
| REJECTED-02 | Start with hydrology, AI, ECS, networking, or complex worldgen before numeric determinism. | deprioritised | Deterministic scaffolding must come first. | tentative sequencing decision | After deterministic core/sim/replay tests exist. | WORKSTREAM-02 | INFERENCE |
| REJECTED-03 | Build a huge flat dsys/dgfx abstraction before exercising it. | deprioritised | Over-abstract API risk; vertical slices should drive API growth. | tentative design strategy | When real backend needs require expanded APIs. | WORKSTREAM-02, WORKSTREAM-05 | INFERENCE |
| REJECTED-04 | Use env/config startup mode override in v1. | deferred | Adds precedence and reproducibility complexity. | not final; v1 only | After stable config/instance system exists. | WORKSTREAM-07 | INFERENCE |
| REJECTED-05 | Fallback from GUI/TUI on logical/content/config errors. | rejected in recommendation | Would hide real errors and create confusing behavior. | should remain final unless user changes policy | Only if user explicitly requests permissive fallback. | WORKSTREAM-07 | INFERENCE |
| REJECTED-06 | Include headless in AUTO startup fallback. | rejected in recommendation | Headless is server/explicit mode, not a UI fallback. | tentative but strong | Dedicated server shortcut UX requirements. | WORKSTREAM-07 | INFERENCE |
| REJECTED-07 | Duplicate CLI/TUI/GUI behavior pipelines per product. | rejected by architecture | Violates common-components and no-duplication requirements. | final unless architecture changes | Never without explicit user override. | WORKSTREAM-03 | FACT |
| REJECTED-08 | Use OS-native product drawing directly. | rejected by user constraint | Violates dgfx abstraction. | final | Never unless user changes master architecture. | WORKSTREAM-03, WORKSTREAM-05 | FACT |
| REJECTED-09 | Use C++11+ for product code. | rejected by user constraint | Dominium product code is C++98 portable subset. | final for current project policy | Only if user changes language policy. | WORKSTREAM-01 | FACT |
| REJECTED-10 | Use floating-point in deterministic simulation. | rejected by user constraint | Fixed-point deterministic sim required. | final | Never for deterministic sim; tooling/debug conversions may be separate if isolated. | WORKSTREAM-01, WORKSTREAM-02 | FACT |
| REJECTED-11 | Allow build-time network downloads for dependencies. | rejected / requires verification | Prior questionnaire answer said repo BUILDING forbids downloads; must verify before using as fact. | tentative until repo docs verified | If repo docs/user explicitly allow downloads. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| REJECTED-12 | Treat assistant recommendations as final user decisions automatically. | rejected by current packaging rules | User explicitly says not to turn brainstorms into decisions or treat assistant suggestions as user decisions unless accepted. | final for reporting methodology | Never for evidence labelling. | WORKSTREAM-09 | FACT |

## 9. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Unverified repo-state claims are treated as verified facts. | Future prompts/code may target wrong files/platforms/APIs. | medium-high | high | Inspect dominium.zip/current repo and label facts with file evidence. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| RISK-02 | Generated prompts are mistaken for implemented code. | Duplicate work, conflicts, or missed implementation gaps. | high | high | Check repo for generated files before continuing. | WORKSTREAM-02, WORKSTREAM-03, WORKSTREAM-04, WORKSTREAM-05, WORKSTREAM-07 | INFERENCE |
| RISK-03 | Startup dispatcher in domino_core references all product C++ wrappers and causes unresolved symbols. | Build/link failure for tests or individual product targets. | medium | high | Use callback-table/generic dispatcher or product-local dispatcher instead. | WORKSTREAM-07 | INFERENCE |
| RISK-04 | Strict C89 and C++98 are violated by generated snippets. | Build portability failure and policy violation. | medium-high | high | Audit for long long, std::snprintf, declarations, and modern constructs. | WORKSTREAM-02, WORKSTREAM-07 | INFERENCE |
| RISK-05 | q48_16/u64/i64 implementation relies on non-C89 compiler extensions without clear fallback. | Retro/compiler portability failure. | medium | high | Define portability policy or emulation for strict C89 targets. | WORKSTREAM-02 | INFERENCE |
| RISK-06 | Native-endian TLV save/load conflicts with cross-platform compatibility. | Old/cross-platform saves may not load deterministically. | medium | high | Introduce endian-stable TLV helpers early. | WORKSTREAM-02 | INFERENCE |
| RISK-07 | Minimal JSON manifest parser is brittle. | Manifest parsing fails on valid but differently formatted JSON or edge cases. | medium | medium | Constrain manifest subset or replace with robust deterministic parser/TLV manifest. | WORKSTREAM-02 | INFERENCE |
| RISK-08 | Layering violations introduced by Codex. | Product code may call OS APIs or render APIs directly, undermining portability. | medium | high | Each prompt must explicitly restate dsys/dgfx boundaries and reviews must enforce them. | WORKSTREAM-01, WORKSTREAM-03, WORKSTREAM-05 | INFERENCE |
| RISK-09 | Broad GUI/TUI/dgfx prompts overreach existing API maturity. | Large inconsistent changes and build failures. | medium-high | medium-high | Split prompts after repo inspection. | WORKSTREAM-03, WORKSTREAM-05 | INFERENCE |
| RISK-10 | GUI/TUI product logic diverges from CLI behavior. | Bugs and incompatible product workflows. | medium | medium-high | Use shared state machines and product action models. | WORKSTREAM-03, WORKSTREAM-04 | INFERENCE |
| RISK-11 | GUI directly depends on raster/theme packs and breaks vector-only fallback. | Products fail without optional assets. | medium | medium | Ensure built-in vector style/icon pack remains mandatory. | WORKSTREAM-03, WORKSTREAM-06 | INFERENCE |
| RISK-12 | IME/input event timing contaminates deterministic sim. | Sim results differ by platform/UI mode. | low-medium | high | Input event streams are deterministic per frame; sim RNG isolated from UI systems. | WORKSTREAM-04 | INFERENCE |
| RISK-13 | Backend detection or GUI timing uses nondeterministic environment values for sim-affecting choices. | Different render backend may alter sim behavior. | low-medium | high | Keep render/UI backend separate from sim; fixed tick and deterministic input stream. | WORKSTREAM-05 | INFERENCE |
| RISK-14 | Pack-system prompt becomes too broad and under-specified. | Asset loading, shader packs, audio packs, and streaming become inconsistent. | medium-high | medium-high | Split pack prompt or define pack manifest and deterministic load order first. | WORKSTREAM-06 | INFERENCE |
| RISK-15 | Windows/macOS packaging realities break one-binary startup assumptions. | Double-click vs terminal detection may not behave as intended. | medium | medium-high | Decide Windows subsystem and macOS bundle strategy after repo/build inspection. | WORKSTREAM-07 | INFERENCE |
| RISK-16 | Questionnaire answer carries stale/external software-version claims. | Platform/render/API plan may rely on outdated build facts. | medium | medium | Re-verify current docs/toolchains before using. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| RISK-17 | This final report package over-compresses generated prompts. | Future assistant may need original chat to recover exact prompt text. | low-medium | medium | Report preserves prompt objectives, files, constraints, APIs, and risks; original chat remains ideal source for exact wording. | WORKSTREAM-09 | INFERENCE |
| RISK-18 | Future aggregator merges recommendations as decisions. | Spec Book may incorrectly formalize tentative suggestions. | medium | high | Use labels/status fields and preserve uncertainty. | WORKSTREAM-09 | FACT |

## 10. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Open/extract dominium.zip or current checkout. | Repo-specific claims in the chat are not independently verified here. | file inspection | highest | WORKSTREAM-01, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Inspect root CMakeLists.txt, source CMake files, and CMakePresets.json. | Build target and language-standard claims depend on actual files. | repo files | highest | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Search for files specified by prompts 1-6. | Need know whether prompts were executed. | repo file tree | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Build golden target set and run numeric/headless tests. | Determine current build health and determinism baseline. | CMake/Ninja/test run | high | WORKSTREAM-02 | INFERENCE |
| VERIFY-05 | Inspect numeric typedef/fixed-point implementation for C89 compliance. | u64/i64/q48_16 under ISO C89 is unresolved. | source review | high | WORKSTREAM-02 | INFERENCE |
| VERIFY-06 | Inspect existing CLI/TUI/GUI/input/state modules before applying common-framework prompts. | Avoid overwriting or duplicating existing implementation. | repo file inspection | medium-high | WORKSTREAM-03, WORKSTREAM-04 | INFERENCE |
| VERIFY-07 | Inspect dgfx/render headers and backend implementation names. | Multi-window/pipeline/backend prompt may not match actual API. | repo file inspection | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Inspect content/pack/data format docs before generating pack-system prompt. | Pack prompt should target actual repo formats and compatibility rules. | repo docs/source inspection | high | WORKSTREAM-06 | INFERENCE |
| VERIFY-09 | Inspect CMake target graph before implementing startup dispatcher. | Avoid unresolved product wrapper symbols from shared core. | CMake/source review | highest | WORKSTREAM-07 | INFERENCE |
| VERIFY-10 | Verify platform tier/render backend claims in docs/source. | Prior questionnaire answer is unverified in this packaging task. | docs/source inspection | medium-high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Verify third-party library/vendor/toolchain claims. | External-world/software-version facts can become stale. | repo external dir, docs, build environment | medium | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Download and store the generated report package files/ZIP. | Ensure handoff package persists outside this retired chat. | user local storage | high | WORKSTREAM-09 | FACT |

## 11. Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | User provided Extended Master Starter Prompt for Dominium + Domino. | Established architecture, constraints, products, repo layout, platform/render/sim/modding model. | This became the primary source for all later planning. | Highest; future assistants must preserve it. | 5/5 |
| 2 | Assistant acknowledged the constraints. | Restated Domino C89, Dominium C++98, dsys/dgfx, determinism, product stack. | Established operating frame. | Historical; user prompt outranks acknowledgement. | 5/5 |
| 3 | User requested a forward plan. | Assistant produced a phased roadmap from docs to replay/net. | Created initial implementation order. | Useful planning reference. | 5/5 |
| 4 | User asked for recommendations. | Assistant recommended narrowing to Milestone 0, prioritizing determinism, postponing retro/full UI/net. | Prevented scope overreach. | Still relevant as risk-control rationale. | 5/5 |
| 5 | User requested six Codex prompts and reminded numeric formats. | Assistant began self-contained Codex prompt series; numeric formats included u8/i8/u16/i16/u32/i32/u64/i64/q4_12/q16_16/q24_8/q48_16. | Moved from planning to executable prompt packages. | High; prompt inventory and numeric constraints must carry forward. | 5/5 |
| 6 | Prompt 1 generated. | Docs-only SPEC_IDENTITY/SPEC_PRODUCTS prompt. | Canonical docs first. | Implementation/execution unknown; verify repo. | 5/5 |
| 7 | Prompt 2 generated. | Repo layout/CMake skeleton/core/product targets prompt. | Buildable skeleton. | Verify execution. | 5/5 |
| 8 | Prompt 3 generated. | Deterministic numeric core/test harness prompt. | Determinism foundation. | Audit for C89 details. | 5/5 |
| 9 | Prompt 4 generated. | DOMINIUM_HOME repo/product manifest/launcher enumeration prompt. | Launcher-product discovery foundation. | Verify and possibly harden parser/path logic. | 5/5 |
| 10 | Prompt 5 generated. | Minimal deterministic sim/headless game/TLV save prompt. | First working sim result. | Verify save/endian/RNG state. | 5/5 |
| 11 | Prompt 6 generated. | Launcher process spawn via dsys prompt. | Completes Milestone-0 pipeline. | Verify platform spawn/path behavior. | 5/5 |
| 12 | User requested three prompts for CLI/TUI/GUI across products. | Assistant generated universal CLI, TUI, GUI prompts. | Move from headless/CLI skeleton toward product UX modes. | Execution unknown; inspect before applying. | 5/5 |
| 13 | User requested prompts for input/state/IME; multi-window/dgfx/backend detection; pack system. | Assistant generated first two prompts only. | Expanded common systems and rendering architecture. | Missing pack prompt is a carry-forward task. | 5/5 |
| 14 | User specified one-binary startup behavior. | Assistant designed terminal CLI vs double-click GUI/TUI/CLI fallback policy. | Defines product executable UX. | High; implementation prompt exists but needs linker-risk fix. | 5/5 |
| 15 | User asked what else must be considered before Codex prompt. | Assistant identified edge cases: mode semantics, platform packaging, logging, determinism, product quirks, build flags. | Prevented premature implementation. | Risk/control guidance for startup implementation. | 5/5 |
| 16 | User asked for recommendations on startup. | Assistant recommended explicit flags first, no env/config v1, terminal heuristic, product-specific rules, error codes, capability masks. | Clarified startup policy. | High but some items are recommendations, not formal user decisions. | 5/5 |
| 17 | User requested one big Codex prompt for startup. | Assistant generated unified startup/mode dispatcher prompt. | Actionable implementation plan. | Use with design repair; do not apply blindly. | 5/5 |
| 18 | User asked platform/render/API questionnaire and mentioned dominium.zip current repo. | Assistant provided refined answer; repo inspection claim is unverified in visible context. | Created candidate repo/build context. | Requires verification before use. | 3/5 |
| 19 | User requested maximum-fidelity Context Transfer Packet. | Assistant produced transfer packet with registers and handoff. | Retire chat while preserving continuity. | Source material for this package. | 5/5 |
| 20 | User requested final downloadable report package. | This response creates seven files and ZIP with stable IDs/registers. | Make chat-specific package reusable and aggregatable. | Final output of this chat. | 5/5 |

## 12. Spec Book Contribution Register

| Category | Item |
|---|---|
| likely_sections | Architecture Overview |
| likely_sections | Language and Determinism Policy |
| likely_sections | Repository and DOMINIUM_HOME Model |
| likely_sections | Build and Toolchain Policy |
| likely_sections | Platform Abstraction (dsys) |
| likely_sections | Rendering Architecture (dgfx) |
| likely_sections | Product Model: Launcher/Game/Setup/Tools |
| likely_sections | Startup and Mode Dispatch Policy |
| likely_sections | CLI/TUI/GUI Shared Interfaces |
| likely_sections | Input, State, and IME Systems |
| likely_sections | Pack and Content System |
| likely_sections | Compatibility and Versioning |
| likely_sections | Implementation Milestones and Codex Prompt Workflow |
| likely_sections | Risk and Verification Policy |
| unique_contributions | Detailed Codex prompt sequence for Milestone 0. |
| unique_contributions | Unified startup behavior policy for terminal vs double-click launches. |
| unique_contributions | Identification of startup dispatcher linker risk. |
| unique_contributions | Missing pack-system prompt as explicit carry-forward item. |
| unique_contributions | Questionnaire workflow and caveat about repo-state verification. |
| possible_duplicates_with_other_chats | Master architecture constraints may appear in many chats. |
| possible_duplicates_with_other_chats | Platform/render matrix likely overlaps with repo/docs-focused chats. |
| possible_duplicates_with_other_chats | Codex prompt sequences may be copied into implementation chats. |
| possible_duplicates_with_other_chats | Startup CLI/TUI/GUI policy may overlap product UX chats. |
| conflicts_to_watch_for | C89 vs long long/64-bit implementation strategy. |
| conflicts_to_watch_for | Native-endian TLV in early prompt vs cross-platform save compatibility. |
| conflicts_to_watch_for | Monolithic domino_core vs modular domino_sys/domino_gfx target architecture. |
| conflicts_to_watch_for | Windows one-binary UX vs console/windows subsystem build mode. |
| conflicts_to_watch_for | D3D12 mention in questionnaire vs master prompt backends. |
| formal_requirements_candidates | Domino C89, Dominium C++98. |
| formal_requirements_candidates | dsys-only platform access. |
| formal_requirements_candidates | dgfx-only rendering. |
| formal_requirements_candidates | terminal => CLI; no-terminal => GUI->TUI->CLI startup policy. |
| formal_requirements_candidates | game headless/server flags bypass UI. |
| formal_requirements_candidates | stable versioned ABI/data formats and no silent old-content breakage. |
| formal_requirements_candidates | vector-only fallback always available. |
| background_context_candidates | Assistant-generated roadmap phases. |
| background_context_candidates | Prompt inventory and sequencing. |
| background_context_candidates | Questionnaire answer candidate details pending verification. |
| needs_user_confirmation | Final platform tier priorities. |
| needs_user_confirmation | Windows subsystem/bundle strategy. |
| needs_user_confirmation | Whether env/config startup mode overrides are desired later. |
| needs_user_confirmation | D3D12 scope. |
| needs_user_confirmation | Pack format and shader pack strategy. |
