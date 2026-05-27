# Registers — Documentation Standards and README Handoff

## 1. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Per-file C/C++/assembly documentation standard | Define and later apply a consistent documentation standard for every non-trivial C, C++, header, and assembly file. | A standard was designed in conversation and encoded in Codex prompts. It has not been applied to a repository in this chat. | Every non-trivial source/header/assembly file has structured documentation appropriate to its role; public contracts live in headers; implementation rationale lives in source files. | active, not executed in this chat | high | 4 | FACT / INFERENCE |
| WORKSTREAM-02 | External docs/ technical documentation structure | Establish or reconcile authoritative technical documentation under docs/. | Desired structure was specified. Actual docs were not inspected or changed in this chat. | docs/ accurately describes architecture, dependencies, contracts, style, build topology, components, documentation standards, and material subsystem specs. | active, not executed in this chat | highest | 4 | FACT / INFERENCE |
| WORKSTREAM-03 | Root README as public landing page and technical hub | Rewrite or restructure root README.md so it works for lay users, technical readers, and future contributors. | A focused README prompt and a later integrated refactor-reconciliation prompt were generated. README was not modified in this chat. | README.md stands alone as the project's temporary public landing page until a website exists and links into detailed docs. | active, not executed in this chat | highest | 5 | FACT |
| WORKSTREAM-04 | Documentation ratio quality gate | Add a compiler-agnostic CMake-integrated Python checker that measures comment density and enforces min/max ratios. | The user supplied a detailed specification; an implementation-ready Codex prompt was generated. No script or CMake changes were made in this chat. | scripts/doc_ratio_check.py exists; CMake has doc_ratio_check; local builds warn; CI builds fail on violations; docs explain the standard. | active, separate implementation workstream | high | 5 | FACT |
| WORKSTREAM-05 | Standards-aligned Codex prompt optimization | Upgrade documentation-generation prompts to be stricter, deterministic, and aligned with C89/C90, C++98, assembly, Markdown, and Doxygen-compatible conventions. | A stricter prompt was generated. It contains one known typo: 'Determininism guarantees remembered' / 'Determinism guarantees remembered' should be corrected to 'Determinism guarantees' before reuse. | A clean, standards-aligned Codex prompt controls documentation-only codebase passes without behavior changes. | active artifact, requires minor correction | medium | 4 | FACT |
| WORKSTREAM-06 | Post-refactor documentation reconciliation | Scan the current repository after heavy setup/launcher/game refactors and make docs/ plus README consistent with actual code. | A consolidated Codex prompt was generated. No repository scan occurred in this chat. | All docs reflect current setup, launcher, engine, game, tool, and build structure, with no contradictions or stale references. | active, highest next-action candidate | highest | 4 for user intent; 2 for actual repo details | FACT / UNCERTAIN |
| WORKSTREAM-07 | Reusable per-chat report package and aggregation handoff | Convert the prior Context Transfer Packet into a downloadable, shareable report package for this individual chat. | This package is being generated from the previous Context Transfer Packet plus visible chat context. | A set of Markdown/YAML files and a ZIP archive usable by humans, future assistants, aggregators, and future Project Spec Book construction. | active in current response; complete if files are successfully created | highest for this response | 5 | FACT |

## 2. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Use both in-code documentation and external docs. | Accepted direction | Repeated assistant outputs; user continued to request prompts based on this model. | In-code contracts stay close to APIs; external docs cover architecture and policy. | Prevents using only comments or only sister files. | WORKSTREAM-01; WORKSTREAM-02 | 4 | FACT / INFERENCE |
| DECISION-02 | Headers are canonical for public API contracts. | Accepted direction | Repeated in generated prompts and not contradicted. | Callers consume headers; source duplication causes drift. | Public functions/types should be documented in headers only. | WORKSTREAM-01 | 4 | FACT / INFERENCE |
| DECISION-03 | Source files document implementation rationale, invariants, and hazards, not public contracts. | Accepted direction | Repeated in best-practice and prompt outputs. | Keeps source comments high-signal and avoids duplicate contract text. | Source comments should explain why, not restate what. | WORKSTREAM-01 | 4 | FACT / INFERENCE |
| DECISION-04 | README.md should be a public landing page and technical navigation hub. | User-directed | User explicitly requested a complete high/low-level summary, industry/consumer standard, and lay/technical readability. | README is the public front door until a website exists. | README must be accessible, accurate, non-marketing, and linked to docs. | WORKSTREAM-03 | 5 | FACT |
| DECISION-05 | docs/ should hold architecture, dependencies, contracts, style, build overview, components, and subsystem specs. | Accepted direction | Generated prompts defined this docs structure; user did not reject it. | Cross-cutting information belongs outside individual source files. | Create/update docs only after verifying repo reality. | WORKSTREAM-02 | 4 | FACT / INFERENCE |
| DECISION-06 | Documentation quality should be mechanically enforced. | User-directed | User explicitly said documentation quality should be enforced mechanically, not socially. | Mechanisms reduce drift and make standards testable. | Introduce documentation quality gate. | WORKSTREAM-04 | 5 | FACT |
| DECISION-07 | Use standalone Python 3 script for documentation ratio checking. | User-directed | User specified Python 3 for portability and parsing ease. | Compiler-agnostic and portable across MSVC/GCC/Linux/Windows. | Create scripts/doc_ratio_check.py. | WORKSTREAM-04 | 5 | FACT |
| DECISION-08 | Integrate documentation ratio checker through CMake custom target. | User-directed | User specified CMake custom target and Python3 find_package. | Fits existing build system and avoids compiler-specific diagnostics. | Modify top-level CMakeLists.txt. | WORKSTREAM-04 | 5 | FACT |
| DECISION-09 | Local builds warn; CI builds fail on documentation ratio violations. | User-directed | User specified warnings locally and hard failures in CI. | Balances developer workflow and enforcement. | Need robust CI detection through ENV{CI}. | WORKSTREAM-04 | 5 | FACT |
| DECISION-10 | Do not use compiler warnings, pragmas, clang-tools, AST parsing, or external linters for doc ratio enforcement. | User-directed | Explicit non-goals and implementation strategy. | Avoids compiler/toolchain coupling and external dependencies. | Use heuristic parser only. | WORKSTREAM-04 | 5 | FACT |
| DECISION-11 | Adopt documentation ratio thresholds: lines 20–40%, words 15–30%, chars 10–25%. | User-directed | User supplied exact thresholds. | Detects underdocumentation and overcommenting. | Checker must enforce these unless user revises them. | WORKSTREAM-04 | 5 | FACT |
| DECISION-12 | Exclude generated, third-party, vendored, build, and external dependency code from documentation ratios. | User-directed | User defined exclusions. | External/generated code should not affect project documentation health. | Need path filters and tuning. | WORKSTREAM-04 | 5 | FACT |
| DECISION-13 | Post-refactor docs/ and README pass must not change runtime or build behavior. | Prompt-defined direction | Latest Codex prompt says files to modify are docs/** and README.md only. | Docs reconciliation should not destabilize code. | Separate from quality-gate workstream, which does modify build files. | WORKSTREAM-06 | 5 | FACT |
| DECISION-14 | Add COMPONENTS.md and BUILD_OVERVIEW.md if missing and supported by repo structure. | Assistant-added recommendation accepted by continuation | Latest prompt included these to handle setup/launcher/game separation. | Prevents README bloat and clarifies refactored component boundaries. | Only create if consistent with actual repo. | WORKSTREAM-02; WORKSTREAM-06 | 4 | INFERENCE |
| DECISION-15 | Codex prompts should be deterministic, explicit, non-interactive, and contain no placeholders/TODOs/speculation. | User-directed and repeated | User requested implementation-ready prompts with no ambiguity; prompts repeated these rules. | Reduces risk of Codex inventing facts or leaving incomplete docs. | Future prompts should remain self-contained. | WORKSTREAM-05; WORKSTREAM-06 | 5 | FACT |
| DECISION-16 | Produce a reusable per-chat report package with stable IDs and downloadable files. | User-directed | Current user request gives exact file list and ID pattern. | Enables future aggregation and spec-book construction. | Create Markdown/YAML files and ZIP. | WORKSTREAM-07 | 5 | FACT |
| DECISION-17 | File headers should not include authors, dates, or change logs. | Accepted direction | Repeated in documentation standard prompts. | Git tracks history; embedded historical metadata goes stale. | File headers focus on responsibility, dependencies, invariants, and extension points. | WORKSTREAM-01 | 4 | FACT / INFERENCE |

## 3. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Inspect the current repository after refactors. | highest | immediate | New chat / Codex | Repo access | File tree, CMakeLists, README, docs, source files | Verified architecture and component inventory | Start here before writing repo-specific docs. | WORKSTREAM-06 | FACT |
| TASK-02 | Identify top-level components and products. | highest | immediate | Codex | TASK-01 | Actual directories and targets | Component map including setup/launcher/engine/game if present | Do not assume component names without repo evidence. | WORKSTREAM-06 | FACT |
| TASK-03 | Identify CMake build graph and primary targets. | high | high | Codex | TASK-01 | All CMakeLists.txt | Build overview and target ownership map | Use CMake files as evidence. | WORKSTREAM-02; WORKSTREAM-06 | FACT |
| TASK-04 | Reconcile all docs/** files with current code. | highest | high | Codex | TASK-01; TASK-02; TASK-03 | Existing docs and code | Updated docs with stale claims removed | Use Prompt A.5 as base. | WORKSTREAM-02; WORKSTREAM-06 | FACT |
| TASK-05 | Overhaul README.md into public landing page and technical hub. | highest | high | Codex | TASK-04 or concurrent evidence scan | Current project facts, license, platforms, docs links | Industry-standard README | Rewrite only with verifiable repo evidence. | WORKSTREAM-03; WORKSTREAM-06 | FACT |
| TASK-06 | Create or update docs/COMPONENTS.md if component structure supports it. | high | high | Codex | TASK-02 | Component map | Component overview doc | Only create for actual components. | WORKSTREAM-02; WORKSTREAM-06 | INFERENCE |
| TASK-07 | Create or update docs/BUILD_OVERVIEW.md. | high | medium | Codex | TASK-03 | CMake target graph | High-level build topology doc | Avoid long command tutorial. | WORKSTREAM-02; WORKSTREAM-06 | INFERENCE |
| TASK-08 | Update ARCHITECTURE, DEPENDENCIES, CONTRACTS, and STYLE docs. | high | high | Codex | TASK-01; TASK-02; TASK-03 | Code organization and current docs | Accurate core documentation set | Keep canonical facts in one place. | WORKSTREAM-02 | FACT / INFERENCE |
| TASK-09 | Create SPEC_<SUBSYSTEM>.md files only for material subsystems. | medium | medium | Codex | TASK-01; TASK-02 | Subsystem inventory | Subsystem specs | Do not invent subsystems. | WORKSTREAM-02 | FACT / INFERENCE |
| TASK-10 | Implement scripts/doc_ratio_check.py. | high | separate | Codex | Repo access; source roots | User spec from this chat | Python comment-ratio checker | Use Prompt A.3. | WORKSTREAM-04 | FACT |
| TASK-11 | Integrate doc_ratio_check into CMake. | high | separate | Codex | TASK-10; CMake structure | Top-level CMakeLists.txt | doc_ratio_check target and cache variables | Ensure local warn / CI fail behavior. | WORKSTREAM-04 | FACT |
| TASK-12 | Document documentation ratio standard. | high | separate | Codex | TASK-10; TASK-11 | Thresholds and CMake variables | docs/DOCUMENTATION_STANDARDS.md and README link | Explain drift detector purpose. | WORKSTREAM-04 | FACT |
| TASK-13 | Verify documentation ratio checker behavior. | medium | after implementation | Codex | TASK-10; TASK-11 | Configured build and script invocations | Evidence warn mode exits 0 and CI mode exits nonzero on violations | Do not weaken thresholds to pass. | WORKSTREAM-04 | FACT |
| TASK-14 | Apply per-file source/header/assembly documentation standard. | medium/high | later | Codex | TASK-01; public API map | Source/header files | Structured comments without behavior changes | Use corrected Prompt A.4 or A.1. | WORKSTREAM-01 | FACT / INFERENCE |
| TASK-15 | Correct typo in upgraded standards prompt before reuse. | medium | before prompt reuse | User/new chat | Prompt A.4 |  | Correct prompt text | Replace erroneous determinism line. | WORKSTREAM-05 | FACT |
| TASK-16 | Aggregate this package with other old-chat packages later. | medium | later | User / aggregator chat | Reports from other old chats |  | Master project spec and living state file | Use aggregator prompt from current user text or future equivalent. | WORKSTREAM-07 | FACT |
| TASK-17 | Store the generated package files together. | high | after creation | User | Created files and ZIP |  | Saved package folder/ZIP | Keep Markdown and YAML together for later aggregation. | WORKSTREAM-07 | FACT |

## 4. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Do not change runtime behavior. | process | hard | User and generated prompts | Documentation passes must not alter logic, control flow, algorithms, APIs, or data layouts. | high | 5 | FACT |
| CONSTRAINT-02 | Do not refactor code. | process | hard | User and prompts | No cleanup or restructuring during documentation tasks. | high | 5 | FACT |
| CONSTRAINT-03 | Do not rename symbols, files, or targets during documentation-only work. | process | hard | Prompts | Preserve API/linkage and project layout. | high | 5 | FACT |
| CONSTRAINT-04 | Do not reorder statements, declarations, logic, or includes. | process | hard | Prompts | Minimize semantic/build risk. | medium | 5 | FACT |
| CONSTRAINT-05 | Do not introduce new dependencies during documentation-only pass. | technical | hard | Prompts | Avoid adding Doxygen/clang tools unless separately requested. | medium | 5 | FACT |
| CONSTRAINT-06 | No speculation, roadmap, or invented features. | evidence | hard | User/prompts | Docs and README must describe current repo only. | high | 5 | FACT |
| CONSTRAINT-07 | No TODOs or placeholders in generated docs/prompts. | quality | hard | User/prompts | Outputs must be complete or explicitly mark unknowns. | medium | 5 | FACT |
| CONSTRAINT-08 | No marketing hype or aspirational language. | style | hard | User/prompts | README should be credible and neutral. | medium | 5 | FACT |
| CONSTRAINT-09 | One canonical home per fact. | architecture | hard | Prompts | Avoid contradictions and duplication. | high | 4 | FACT / INFERENCE |
| CONSTRAINT-10 | README is overview/navigation, not deep spec. | format | hard | User/prompts | Detailed architecture and build info should live in docs/. | medium | 5 | FACT |
| CONSTRAINT-11 | C89/C90 and C++98 compatibility must be respected in documentation examples and assumptions. | technical | hard | User/prompts | Avoid C99/C++11 assumptions in generated examples or standards. | medium | 5 | FACT |
| CONSTRAINT-12 | Assembly documentation must include ABI/calling convention/register/stack details when assembly exists. | technical | conditional hard | Prompts | Assembly requires low-level contracts not needed for ordinary C/C++. | medium | 4 | FACT / INFERENCE |
| CONSTRAINT-13 | Documentation ratio checker must use Python 3 with no third-party imports. | technical | hard | User spec | Keep portable and dependency-free. | medium | 5 | FACT |
| CONSTRAINT-14 | Documentation ratio checker must be heuristic, not AST-level. | technical | hard | User non-goals | No clang-tools or full parser. | low | 5 | FACT |
| CONSTRAINT-15 | Documentation ratio checker must count only // and /* ... */ comments. | technical | hard | User definition | Do not count generated docs or Markdown as code comments. | medium | 5 | FACT |
| CONSTRAINT-16 | Generated, third-party, vendored, build, and external dependency code must be excluded from documentation ratios. | technical | hard | User definition | Avoid false enforcement on non-project code. | high | 5 | FACT |
| CONSTRAINT-17 | Local documentation ratio violations warn and exit success. | build | hard | User spec | Developer builds should not fail locally. | high | 5 | FACT |
| CONSTRAINT-18 | CI documentation ratio violations hard fail. | build | hard | User spec | CI blocks drift. | high | 5 | FACT |
| CONSTRAINT-19 | Do not alter license text. | legal/documentation | hard | README prompt | README may link or state license but must not change terms. | high | 5 | FACT |
| CONSTRAINT-20 | Quality gate must be compiler-agnostic. | technical | hard | User spec | No MSVC/GCC diagnostic tricks. | medium | 5 | FACT |
| CONSTRAINT-21 | CMake must find Python3 interpreter for quality gate. | technical | hard | User spec | Use find_package(Python3 COMPONENTS Interpreter). | medium | 5 | FACT |
| CONSTRAINT-22 | Documentation ratio thresholds are fixed unless user revises them. | standard | hard | User spec | Lines 20–40%, words 15–30%, chars 10–25%. | medium | 5 | FACT |
| CONSTRAINT-23 | Docs reconciliation modifies docs/** and README.md only. | process | hard | Latest prompt | Do not change source/build during that pass. | high | 5 | FACT |
| CONSTRAINT-24 | Repo evidence outranks prior chat/prompt assumptions. | evidence | hard | Current handoff rules | Actual code is authoritative after scan. | high | 5 | FACT |
| CONSTRAINT-25 | Final package must use stable IDs. | format | hard | Current user request | All registers use WORKSTREAM, DECISION, TASK, etc. | medium | 5 | FACT |
| CONSTRAINT-26 | Important items must be labelled FACT, INFERENCE, UNCERTAIN / UNVERIFIED, or PROJECT-CONTEXT. | evidence | hard | Current user request | Prevents unsupported facts from entering future spec. | high | 5 | FACT |
| CONSTRAINT-27 | This package covers this chat only, not the whole project. | scope | hard | Current user request | Do not summarize unseen project context as fact. | high | 5 | FACT |
| CONSTRAINT-28 | If files are not actually created, do not claim downloads exist. | artifact | hard | Current user request | Final response must match actual file creation. | high | 5 | FACT |

## 5. User Preference Register

| ID | Preference | Source category | Source basis | Strength | Implication for future assistants | Risk if misunderstood | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Straightforward, critical, low-fluff communication. | explicit | User profile/instructions in this chat context | strong | Future assistants should provide direct, precise answers without praise or soft filler. | May produce over-soft or vague responses. | FACT |
| PREF-02 | Correctly cited, rigorously checked facts. | explicit | User profile says interest in correctly cited sources and rigorously tested facts. | strong | Use repo evidence for project facts; verify current external facts when needed. | Future docs may overstate unverified claims. | FACT |
| PREF-03 | Second- and third-order thinking. | explicit | User profile. | medium/strong | Expose implications, risks, and downstream effects of documentation decisions. | May miss maintainability consequences. | FACT |
| PREF-04 | Deterministic, implementation-ready prompts. | inferred from repeated requests | User repeatedly asked for Codex prompts with exact constraints. | strong | Prompts should be copy-paste-ready and non-interactive. | Vague prompts may cause Codex drift. | INFERENCE |
| PREF-05 | Mechanically enforced standards over social/process-only standards. | explicit in quality gate prompt | User said documentation quality should be enforced mechanically, not socially. | strong | Prefer scripts/CI gates where appropriate. | Future assistant may offer weak policy-only solution. | FACT |
| PREF-06 | README must work for laypeople and technicians. | explicit | User explicitly requested layman-understandable and technician-detailed README. | strong | Use layered explanations and avoid jargon without explanation. | README may become too technical or too shallow. | FACT |
| PREF-07 | Preserve tentative status and rejected options. | explicit in current packaging request | User gave rules for context transfer and packaging. | strong | Do not collapse brainstorms into decisions. | Future aggregation may encode false requirements. | FACT |
| PREF-08 | No speculation or invented project facts. | explicit | Repeated in user and generated prompts. | strong | Require repo scan before claims. | Docs may hallucinate features/platforms. | FACT |
| PREF-09 | Desire for future aggregation into a Project Spec Book. | explicit | Current request says package should later combine into reports and source material for a Project Spec Book. | strong | Use stable IDs, registers, YAML, and provenance labels. | Later merger will lose traceability. | FACT |
| PREF-10 | Exact file/package outputs when requested. | explicit | Current request enumerates files and ZIP behavior. | strong | Create actual files when tools are available. | User may not be able to save/reuse package. | FACT |

## 6. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | What is the exact project name used in the repository? | README title, docs identity, and package cross-references require exact naming. | PROJECT-CONTEXT says wider project is Dominium Game. | Repository project() name and README title were not inspected. | Inspect CMakeLists.txt, README, repository metadata, and license. | high | WORKSTREAM-03; WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | What are the actual top-level directories after refactor? | Docs map and component docs must match current layout. | User mentioned setup, launcher, and game design refactors. | Actual directory tree is unknown. | Inspect repository tree. | high | WORKSTREAM-02; WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Which components are libraries and which are executables? | Architecture and build overview depend on target types. | Project uses CMake. | Target graph unknown. | Inspect all CMakeLists.txt files. | high | WORKSTREAM-02; WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | Which platforms are actually supported? | README supported platform claims must be accurate. | Quality gate context mentioned MSVC Windows, GCC Linux, possibly MinGW. | Runtime/platform support unknown. | Inspect build files, platform code, CI configs, and docs. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What is the actual license? | README license section must link/state correct license without changing terms. | License should not be altered. | License file/content unknown. | Inspect LICENSE or equivalent. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | What is the project maturity/status? | README status section requires evidence. | No explicit stable/experimental status in visible chat. | Actual status unknown. | Inspect README, docs, release tags, issue tracker if available. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Which docs files currently exist? | Avoid duplication and preserve useful existing content. | Desired docs list exists. | Actual docs inventory unknown. | Inspect docs/. | high | WORKSTREAM-02; WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Which subsystem specs are warranted? | Creating specs for non-existent subsystems invents architecture. | Specs should exist only for material subsystems. | Subsystem list unknown. | Inspect source layout and CMake targets. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | Are setup/, launcher/, engine/, game/, tools/, and tests real directories? | Latest prompt assumes these as possible components but code must verify. | User said setup/launcher/game refactors occurred. | Actual names/locations unknown. | Inspect repo tree. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | Does the repo already use Doxygen-style comments or another convention? | New docs should preserve style where possible. | Doxygen-compatible style was recommended. | Existing convention unknown. | Inspect headers and docs tooling. | medium | WORKSTREAM-01; WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | Are there assembly files? | Assembly docs require special ABI/register treatment. | Scope includes assembly where present. | Existence unknown. | Search for .asm, .s, .S files. | medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Are documentation ratio thresholds initially passable? | CI gate might fail immediately. | Thresholds are specified. | Current ratios unknown. | Run checker in warn mode after implementation. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | What CI environment variables are available? | Fail/warn mode detection relies on CI variable. | Proposed ENV{CI} detection. | CI provider/config unknown. | Inspect CI configs. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | What paths should be excluded from documentation ratios? | Wrong exclusions distort quality metrics. | Default excludes were proposed. | Actual generated/vendor/build paths unknown. | Inspect repo and generated paths. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | Are there generated files inside source roots? | Quality gate and doc pass must not touch/generated code. | Generated code excluded in principle. | Location unknown. | Inspect repo and build outputs. | medium | WORKSTREAM-01; WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-16 | Should source/header docs be applied before or after docs/ reconciliation? | Order affects consistency. | Latest next-action favors docs reconciliation first. | User has not explicitly ordered all workstreams. | User confirmation or project planning. | medium | WORKSTREAM-01; WORKSTREAM-06 | INFERENCE |
| QUESTION-17 | Should Codex commit changes, or should it only produce patches? | Generated prompts requested commits; execution environment may vary. | Prompts specify commit sequences. | User's actual Codex workflow unknown. | Ask user or adapt to tooling. | medium | ALL | UNCERTAIN / UNVERIFIED |
| QUESTION-18 | Which claims from other setup/launcher/game design chats are authoritative? | Current chat cannot see those details. | User said refactors occurred there. | Exact decisions from those chats unknown. | Use their future report packages or inspect repo. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |

## 7. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Per-file documentation strategy answer | advisory output | Defined what to document and where. | generated, not executed | Assistant response early in chat | yes | Conceptual basis for later prompts. | FACT |
| ARTIFACT-02 | C/C++ documentation best practices answer | advisory output | Defined inline/block/header/source documentation rules. | generated, not executed | Assistant response | yes | Best-practice rationale. | FACT |
| ARTIFACT-03 | dsys_file.h example | example code/documentation | Showed structured C header/API docs. | example only | Assistant response | style reference only | Not a repo file or project fact. | FACT |
| ARTIFACT-04 | dsys_file_posix.c example | example code/documentation | Showed implementation rationale comments. | example only | Assistant response | style reference only | Not a repo file. | FACT |
| ARTIFACT-05 | arena.hpp / arena.cpp examples | example code/documentation | Showed C++98 class/ownership/no-throw documentation. | example only | Assistant response | style reference only | Not repo files. | FACT |
| ARTIFACT-06 | Detail vs file-size guidance | advisory output | Introduced tiered documentation and bloat-control ideas. | generated, not executed | Assistant response | yes | Later formal ratios supersede advisory ranges. | FACT |
| ARTIFACT-07 | README landing page Codex prompt | prompt | Rewrite README as industry-standard landing page. | generated, not executed | Assistant response | yes, but partly superseded by ARTIFACT-12 | Useful if only README is being modified. | FACT |
| ARTIFACT-08 | Codex prompt to document every file | prompt | Full source/header/docs documentation pass. | generated, not executed | Assistant response | yes | Use after repo scan and typo-free standards alignment. | FACT |
| ARTIFACT-09 | Documentation ratio quality gate Codex prompt | prompt | Implement Python checker, CMake integration, and docs. | generated, not executed | Assistant response | yes | Primary artifact for WORKSTREAM-04. | FACT |
| ARTIFACT-10 | User-provided documentation ratio specification | specification | Defined mechanical documentation gate requirements and thresholds. | input, not implementation | User message | yes | Highest authority for WORKSTREAM-04. | FACT |
| ARTIFACT-11 | Upgraded international-standards documentation prompt | prompt | Stricter docs-only prompt aligned with C89/C90, C++98, assembly, Markdown. | generated, not executed; contains typo | Assistant response | yes, after correction | Correct determinism typo before reuse. | FACT |
| ARTIFACT-12 | Post-refactor docs reconciliation and README overhaul prompt | prompt | Scan repo, update docs/**, overhaul README, check consistency. | generated, not executed | Assistant response | yes | Most direct next-action prompt. | FACT |
| ARTIFACT-13 | docs/COMPONENTS.md | proposed file | Explain setup/launcher/engine/game components. | not created in this chat | Prompt artifact | yes if repo supports it | Do not create if components do not exist. | INFERENCE |
| ARTIFACT-14 | docs/BUILD_OVERVIEW.md | proposed file | High-level CMake/build topology without README bloat. | not created in this chat | Prompt artifact | yes if repo supports it | Should derive from actual CMake. | INFERENCE |
| ARTIFACT-15 | scripts/doc_ratio_check.py | proposed file | Standalone Python comment-ratio checker. | not created in this chat | Prompt artifact | yes if implementing quality gate | Must follow user CLI/threshold spec. | FACT |
| ARTIFACT-16 | docs/DOCUMENTATION_STANDARDS.md | proposed file | Formal documentation ratio and standards explanation. | not created in this chat | Prompt artifact | yes if implementing quality gate | Should explain drift detector purpose. | FACT |
| ARTIFACT-17 | Context Transfer Packet | handoff text | Maximum-fidelity transfer summary for this old chat. | generated in prior assistant response | Current visible chat | yes | Used as source for this package. | FACT |
| ARTIFACT-18 | Full chat report Markdown | generated file | Main human-readable report for this chat. | created by this response if file generation succeeds | Current task | yes | File 1 in package. | FACT |
| ARTIFACT-19 | Spec sheet YAML | generated file | Structured data for future master spec book. | created by this response if file generation succeeds | Current task | yes | File 2 in package. | FACT |
| ARTIFACT-20 | Aggregator packet Markdown | generated file | Compact packet for cross-chat aggregation. | created by this response if file generation succeeds | Current task | yes | File 3 in package. | FACT |
| ARTIFACT-21 | Registers Markdown | generated file | Standalone stable-ID tables. | created by this response if file generation succeeds | Current task | yes | File 4 in package. | FACT |
| ARTIFACT-22 | Reader brief Markdown | generated file | Short human-readable summary. | created by this response if file generation succeeds | Current task | yes | File 5 in package. | FACT |
| ARTIFACT-23 | Verification and audit Markdown | generated file | Reliability assessment and manual verification checklist. | created by this response if file generation succeeds | Current task | yes | File 6 in package. | FACT |
| ARTIFACT-24 | Manifest Markdown and ZIP archive | generated file/archive | Package index and downloadable bundle. | created by this response if file generation succeeds | Current task | yes | File 7 plus ZIP. | FACT |

## 8. Rejected / Superseded Options Register

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Maintain all documentation only in separate sister files. | rejected as sole strategy | Contracts drift when separated from APIs. | final as sole strategy | Reconsider only for generated reference docs extracted from source comments. | WORKSTREAM-01 | FACT / INFERENCE |
| REJECTED-02 | Maintain all documentation only in source/header comments. | rejected as sole strategy | Architecture, dependency policies, and extension recipes need external docs. | final as sole strategy | Never as complete solution; external docs still needed. | WORKSTREAM-02 | FACT / INFERENCE |
| REJECTED-03 | Duplicate full function documentation in both headers and source files. | rejected | Creates contradictions and bloat. | final | Only reconsider for source-only exported APIs with no header. | WORKSTREAM-01 | FACT / INFERENCE |
| REJECTED-04 | Comment every line or narrate obvious control flow. | rejected | Low-signal comments obscure code and inflate file size. | final | Never for production docs; possible only for teaching material outside repo. | WORKSTREAM-01 | FACT / INFERENCE |
| REJECTED-05 | Include authors, dates, or change logs in file headers. | rejected | Git tracks history; embedded metadata goes stale. | final | Reconsider only if legal/project policy requires it. | WORKSTREAM-01 | FACT / INFERENCE |
| REJECTED-06 | Document register usage for ordinary C/C++ functions. | rejected | Compiler manages registers; useful only for assembly/inline asm/ABI-sensitive code. | final | Reconsider for assembly or inline asm. | WORKSTREAM-01 | FACT / INFERENCE |
| REJECTED-07 | Use compiler warnings or pragmas for documentation enforcement. | rejected | Not compiler-agnostic; violates user spec. | final | Do not reconsider for this quality gate. | WORKSTREAM-04 | FACT |
| REJECTED-08 | Use clang-tools or AST-level parsing for documentation ratio checking. | rejected | User declared it a non-goal and wanted no external linters. | final unless user revises constraints | Reconsider only if user changes tooling requirements. | WORKSTREAM-04 | FACT |
| REJECTED-09 | Enforce documentation ratios inside third-party, vendored, generated, or build-artifact code. | rejected | These files are not project-authored docs responsibility. | final | Only reconsider if code becomes first-party. | WORKSTREAM-04 | FACT |
| REJECTED-10 | Have the doc-ratio checker auto-generate or modify comments. | rejected | Checker is a measurement gate; auto-generation was a non-goal. | final | Separate tool only if user requests later. | WORKSTREAM-04 | FACT |
| REJECTED-11 | Put long procedural build tutorials in README. | rejected | README should be a high-level landing page; detailed build docs belong elsewhere. | final for README | Use BUILD_OVERVIEW or build docs for commands. | WORKSTREAM-03 | FACT / INFERENCE |
| REJECTED-12 | Use marketing slogans or hype in README. | rejected | User requested neutral, professional, industry-standard docs. | final | Never unless user deliberately asks for marketing copy. | WORKSTREAM-03 | FACT |
| REJECTED-13 | Include speculative roadmap/features in README/docs. | rejected | Docs must reflect existing code only. | final | Only include if repo has authoritative roadmap and user approves. | WORKSTREAM-03; WORKSTREAM-06 | FACT |
| REJECTED-14 | Create subsystem specs for non-existent subsystems. | rejected | Would invent architecture and mislead future maintainers. | final | Create only when repo evidence supports a material subsystem. | WORKSTREAM-02 | FACT / INFERENCE |

## 9. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Future assistant assumes repository was scanned in this chat. | False repo claims and bad docs. | medium | high | State repeatedly that no repo scan occurred; require repo inspection first. | WORKSTREAM-02; WORKSTREAM-06 | FACT |
| RISK-02 | Future README overclaims features/platforms/maturity. | Public credibility loss and misleading users. | medium | high | Use only repo evidence; mark unknowns. | WORKSTREAM-03 | FACT |
| RISK-03 | Docs preserve stale pre-refactor architecture. | Contributors follow wrong component boundaries. | medium | high | Reconcile every docs statement against code and CMake. | WORKSTREAM-02; WORKSTREAM-06 | FACT |
| RISK-04 | Source documentation bloats files with obvious narration. | Reduced readability and maintainability. | medium | medium | Keep source comments to rationale/hazards; use header contracts. | WORKSTREAM-01 | FACT / INFERENCE |
| RISK-05 | Header/source contract duplication creates drift. | Contradictory API behavior after changes. | medium | high | Header is canonical; source does not restate contracts. | WORKSTREAM-01 | FACT / INFERENCE |
| RISK-06 | Codex changes code while adding documentation. | Runtime/build regression. | medium | high | Use hard no-refactor/no-logic-change constraints and inspect diffs. | WORKSTREAM-01; WORKSTREAM-06 | FACT |
| RISK-07 | Documentation ratio gate fails CI immediately. | Build blockage before code is documented enough. | medium | medium/high | Run warn mode first; document escape hatch; do not silently weaken thresholds. | WORKSTREAM-04 | FACT / INFERENCE |
| RISK-08 | Heuristic parser miscounts comments in edge cases. | False warnings or failures. | medium | medium | Document limitations; keep parser simple; tune only if observed. | WORKSTREAM-04 | FACT |
| RISK-09 | Path exclusions miss generated/vendor code. | Ratios distorted by non-project files. | medium | medium | Inspect repo and tune DOC_RATIO_EXCLUDES. | WORKSTREAM-04 | FACT |
| RISK-10 | Other setup/launcher/game chat decisions are unavailable. | This chat lacks exact refactor details. | high | medium/high | Use repo evidence and/or later packages from those chats. | WORKSTREAM-06 | FACT |
| RISK-11 | README becomes too technical or too shallow. | Fails either lay users or engineers. | medium | medium | Layer sections: plain overview, architecture, docs map. | WORKSTREAM-03 | FACT |
| RISK-12 | Documentation ratios incentivize low-quality filler comments. | Numerical compliance without real maintainability. | medium | medium | Document ratios as drift detector; retain qualitative standards. | WORKSTREAM-04 | FACT / INFERENCE |
| RISK-13 | Known typo in standards prompt causes prompt-quality issue. | Minor confusion in Codex run. | low | low/medium | Correct before reuse. | WORKSTREAM-05 | FACT |
| RISK-14 | Package over-compresses prompt artifacts. | Future assistant loses exact wording that matters. | low | medium | Include full prompt bank or clear artifact references. | WORKSTREAM-07 | FACT |
| RISK-15 | Future aggregator treats assistant suggestions as user decisions. | False master spec requirements. | medium | high | Use labels and status fields; preserve tentative status. | WORKSTREAM-07 | FACT |

## 10. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Actual project name. | Needed for README/docs identity. | Inspect CMake project(), README title, repo metadata. | high | WORKSTREAM-03; WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Actual top-level directory tree. | Needed for docs map and component docs. | Inspect repository tree. | high | WORKSTREAM-02; WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Actual CMake target graph. | Needed for build overview and dependency docs. | Inspect all CMakeLists.txt files. | high | WORKSTREAM-02; WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | License file and terms. | README must link/state license accurately. | Inspect LICENSE or equivalent. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Supported platforms. | Avoid overclaiming README/platform docs. | Inspect platform code, CMake, CI, docs. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Project maturity/status. | README status must be evidence-based. | Inspect docs, releases, issue tracker if available. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Existing docs inventory. | Avoid duplicate or conflicting docs. | Inspect docs/. | high | WORKSTREAM-02; WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Existing docs stale references. | Identify outdated paths/components after refactor. | Search docs for old names and paths. | high | WORKSTREAM-02; WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Existing README content. | Preserve accurate useful content while overhauling. | Read README.md. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Public/private API boundary. | Needed before documenting every public symbol. | Inspect include directories, export macros, build targets. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Existing documentation/comment style. | New comments should preserve project conventions. | Inspect representative headers/sources. | medium | WORKSTREAM-01; WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Source roots for doc-ratio checker. | Defaults src/include may be wrong. | Inspect repo tree and CMake source lists. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Assembly file existence and conventions. | Assembly docs only apply if files exist. | Search .asm/.s/.S files. | medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Generated/vendor/build path exclusions. | Needed for ratio gate correctness. | Inspect repo directories and generated output paths. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | CI environment conventions. | Needed for local warn / CI fail detection. | Inspect CI config files. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-16 | Initial documentation ratios. | Determines whether CI gate will fail immediately. | Run checker in warn mode after implementation. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-17 | Python availability in build environments. | CMake gate depends on Python3 interpreter. | Check developer/CI toolchains. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-18 | Corrected standards prompt before reuse. | Known typo exists in generated prompt. | Manually edit Prompt A.4 line. | medium | WORKSTREAM-05 | FACT |
| VERIFY-19 | Created package files exist and open. | Needed for this response's artifact claim. | Check /mnt/data package outputs. | high | WORKSTREAM-07 | FACT |
| VERIFY-20 | ZIP contains all requested files. | Needed for downloadable package integrity. | Inspect ZIP manifest/listing. | high | WORKSTREAM-07 | FACT |

## 11. Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | User asked what Codex should document for every file and whether docs belong in sister files or file/function headers. | The conversation shifted from broad documentation desire to architecture of documentation placement. | Established WORKSTREAM-01 and WORKSTREAM-02. | still relevant | 5 |
| 2 | Assistant recommended documenting metadata, responsibilities, APIs, dependencies, invariants, threading, error model, ownership, versioning, and extension points. | Defined initial documentation scope. | Became basis for Codex prompt A.1. | still relevant | 5 |
| 3 | User asked for typical best practices for C/C++ inline and block docs, including args, complexity, destructors, memory/registers, prohibitions, dependencies, and descendants. | Expanded scope to detailed documentation taxonomy. | Clarified what to include and omit. | still relevant | 5 |
| 4 | Assistant described file-level, header/API, source, inline, and assembly documentation rules. | Introduced header-as-contract and source-as-rationale split. | Major durable decision set. | still relevant | 5 |
| 5 | User asked for an example of the documentation style. | Requested concrete form. | Needed for prompt/style grounding. | historical/reference | 5 |
| 6 | Assistant generated documented examples for dsys_file.h, dsys_file_posix.c, arena.hpp, and arena.cpp. | Provided style examples only, not repo facts. | Artifacts preserved as examples. | reference only | 5 |
| 7 | User asked how to balance detail and file size. | Introduced bloat control and ratios idea. | Led toward mechanical quality gate. | still relevant | 5 |
| 8 | Assistant proposed tiered docs, comment-ratio bounds, anchors, and CI linting. | Established file-size discipline concept. | Advisory ranges later superseded by formal ratio spec. | partly superseded | 4 |
| 9 | User asked for a Codex prompt to document every file and create/update docs including README. | Moved from strategy to execution prompts. | Produced ARTIFACT-08. | still relevant | 5 |
| 10 | Assistant produced a Codex prompt for full documentation pass. | Captured source/header/docs standard in prompt form. | Prompt preserved in packet. | still relevant | 5 |
| 11 | User asked for README to be a complete high/low-level project summary and industry/consumer-standard landing page. | Created README-specific workstream. | WORKSTREAM-03 established. | still relevant | 5 |
| 12 | Assistant generated focused README overhaul Codex prompt. | Defined README structure and tone. | Later partly superseded by post-refactor prompt. | reference/superseded in part | 5 |
| 13 | User provided detailed spec for documentation ratio quality gate in CMake. | Created mechanical enforcement workstream. | WORKSTREAM-04 established with exact thresholds. | still relevant | 5 |
| 14 | Assistant converted that spec into a GPT-5.2 Codex execution prompt. | Produced ARTIFACT-09. | Prompt remains implementation-ready but unexecuted. | still relevant | 5 |
| 15 | User asked to optimize the documentation prompt for international standards. | Raised prompt rigor and standard alignment. | WORKSTREAM-05 established. | still relevant | 5 |
| 16 | Assistant generated stricter standards-aligned prompt, with one known typo. | Produced ARTIFACT-11. | Requires correction before reuse. | still relevant with caveat | 4 |
| 17 | User said project was heavily refactored in setup, launcher, and game design chats and asked for a prompt to scan repo, update all docs, and overhaul README. | Shifted next action toward repo reconciliation rather than generic docs generation. | WORKSTREAM-06 established. | highest relevance | 5 |
| 18 | Assistant generated consolidated post-refactor docs reconciliation and README prompt. | Produced ARTIFACT-12, the most direct next-action prompt. | Latest unexecuted prompt. | highest relevance | 5 |
| 19 | User requested maximum-fidelity Context Transfer Packet. | Created handoff summary for new chat. | ARTIFACT-17 generated. | source for this package | 5 |
| 20 | User requested final downloadable, shareable, reusable report package for this old chat. | Current task created WORKSTREAM-07. | This package is the output. | current | 5 |

## 12. Spec Book Contribution Register

| ID | Contribution | Spec book destination | Status | Verification needed | Label |
|---|---|---|---|---|---|
| SPEC-CONTRIB-01 | Header/source/docs documentation hierarchy | Documentation Standards chapter | candidate formal requirement | Compare against repo style and other chat decisions. | FACT / INFERENCE |
| SPEC-CONTRIB-02 | README as public landing page | Public Documentation / README chapter | candidate formal requirement | Verify actual README and user-facing positioning. | FACT |
| SPEC-CONTRIB-03 | Python/CMake documentation ratio quality gate | Tooling and Quality Gates chapter | candidate formal requirement | Implement and test in repo before finalizing. | FACT |
| SPEC-CONTRIB-04 | docs/ structure including architecture, dependencies, contracts, style, build overview, components, and specs | Repository Documentation chapter | candidate formal requirement | Verify existing docs and actual components. | FACT / INFERENCE |
| SPEC-CONTRIB-05 | Post-refactor docs reconciliation process | Maintenance Process chapter | candidate procedure | Verify current repo and other refactor chat packages. | FACT |
| SPEC-CONTRIB-06 | Stable-ID report packaging method | Project State Management chapter | process artifact | Apply consistently across old-chat packages. | FACT |
