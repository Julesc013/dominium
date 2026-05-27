# Aggregator Packet — Documentation Standards and README Handoff

## 1. Packet Metadata

- Chat label: Documentation Standards and README Handoff
- Date anchor: 2026-05-27 Australia/Melbourne
- Source scope: This package covers this visible chat only. Project-level context is used only where explicitly labelled PROJECT-CONTEXT.
- Coverage: full for visible chat; partial for wider project
- Confidence: 4 / 5
- Staleness risk: medium
- Merge priority: high
- Main limitations:
  - Repository not scanned.
  - Other refactor chats unavailable.
  - Prompt artifacts are unexecuted.
  - Actual project files, license, platforms, and maturity are unverified.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat should be merged as the documentation-governance and documentation-automation packet for the larger Dominium Game project context. It did not inspect the repository and did not modify code, docs, or build files. Its value is in the standards, decisions, prompts, constraints, and future tasks it preserves.

The central documentation model established in this chat is a three-level hierarchy. Headers are the canonical location for public API contracts: purpose, parameters, ownership, nullability, aliasing, return values, errors, preconditions, postconditions, side effects, thread-safety, determinism, and ABI/layout constraints where relevant. Source files should not duplicate those contracts; they should explain implementation-specific rationale, invariants, non-obvious algorithms, overflow/bounds/aliasing safety, fixed-point math, platform quirks, compiler quirks, and OS-to-engine error mapping. External docs under docs/ should hold architecture, dependency rules, build topology, style policy, contracts, component documentation, and subsystem specs. This hierarchy should become a formal project requirement unless later chats or repository evidence supersede it.

README.md has a special role. The user explicitly wants README to function as an industry-standard public landing page until a website exists. It must serve lay users, technical readers, and contributors. It should explain what the project is, what it is not, the high-level architecture, key characteristics such as determinism and maintainability, supported platforms, repository structure, documentation map, build/usage overview, maturity/status, license, and contribution info where applicable. README must not become a deep spec, build-command manual, marketing page, or speculative roadmap.

The chat also captured a detailed documentation quality gate specification. The user wants documentation quality enforced mechanically, not socially. The chosen mechanism is a standalone Python 3 script integrated into CMake. It should traverse configurable roots, exclude generated/third-party/vendor/build/external dependency code, count C/C++ line and block comments only, measure line/word/character ratios, warn locally, and fail in CI. Exact thresholds are line count 20–40%, word count 15–30%, and character count 10–25%. The quality gate must be compiler-agnostic and must not depend on clang-tools, AST parsing, external linters, compiler warnings, or pragmas. These details are user-specified and high authority.

Several Codex prompts were generated as artifacts but never executed. The most important next-action prompt is the post-refactor documentation reconciliation prompt. The user stated that setup, launcher, and game design were heavily refactored in other chats. Those chats are unavailable, so the future assistant must inspect the actual repository before making repo-specific claims. The latest prompt tells Codex to scan the entire repo, treat current code and directory structure as authoritative, update every file under docs/, and overhaul README.md, while modifying only docs/** and README.md. It also proposes COMPONENTS.md and BUILD_OVERVIEW.md as additional structural docs if supported by the repository.

A future aggregator must not treat assistant suggestions as user decisions unless the user accepted or operationalized them. It must not assume the project name, top-level directories, supported platforms, license, maturity, CMake targets, docs structure, or source roots from this chat. Those facts remain UNCERTAIN / UNVERIFIED until repository evidence or other chat packages confirm them. The only PROJECT-CONTEXT fact carried here is that the wider project context is Dominium Game.

The most important unresolved issue is sequencing. The latest direction suggests doing repository/docs reconciliation before inserting source/header comments or implementing the quality gate, because heavy refactors may have invalidated old docs. However, the user has not explicitly selected which implementation workstream should be run first after packaging. The safest next action is repository inspection followed by docs/ and README reconciliation using the post-refactor prompt.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | No repository was scanned or modified in this chat. | Fact boundary | VERIFY-01..VERIFY-20 | Prevents false project-state assumptions. | FACT | 5 |
| 2 | Actual repository contents must be authoritative once inspected. | Evidence rule | CONSTRAINT-24 | Refactors occurred outside this visible chat. | FACT | 5 |
| 3 | Headers should hold public API contracts. | Decision | DECISION-02 | Core documentation architecture. | FACT / INFERENCE | 4 |
| 4 | Source files should document rationale/hazards only. | Decision | DECISION-03 | Prevents duplication and bloat. | FACT / INFERENCE | 4 |
| 5 | README should be public landing page and docs hub. | User requirement | DECISION-04 | User explicitly requested this. | FACT | 5 |
| 6 | Docs reconciliation after refactor is the highest next repo-facing action. | Task/workstream | WORKSTREAM-06 | User said setup/launcher/game refactors happened. | FACT | 5 |
| 7 | Documentation ratio quality gate thresholds and behavior are exact user requirements. | Requirement | WORKSTREAM-04 | Mechanical enforcement depends on these details. | FACT | 5 |
| 8 | Generated prompts are artifacts, not executed changes. | Artifact rule | ARTIFACT-07..ARTIFACT-12 | Prevents false assumptions. | FACT | 5 |
| 9 | Prompt A.4 has a known typo and must be corrected before reuse. | Artifact caveat | TASK-15 | Avoid propagating defect. | FACT | 5 |
| 10 | Future aggregation must preserve labels and uncertainty. | Aggregation rule | CONSTRAINT-26 | Avoids turning brainstorms into decisions. | FACT | 5 |

## 4. Workstream Summaries

### WORKSTREAM-01 — Per-file C/C++/assembly documentation standard

- Objective: Define and later apply a consistent documentation standard for every non-trivial C, C++, header, and assembly file.
- Current state: A standard was designed in conversation and encoded in Codex prompts. It has not been applied to a repository in this chat.
- Desired end state: Every non-trivial source/header/assembly file has structured documentation appropriate to its role; public contracts live in headers; implementation rationale lives in source files.
- Priority: high
- Decisions: DECISION-01, DECISION-02, DECISION-03, DECISION-17
- Tasks: TASK-14
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-11, CONSTRAINT-12
- Artifacts: ARTIFACT-01, ARTIFACT-02, ARTIFACT-03, ARTIFACT-04, ARTIFACT-05, ARTIFACT-08, ARTIFACT-11
- Risks: RISK-04, RISK-05, RISK-06
- Open questions: VERIFY-10, VERIFY-11, VERIFY-13
- Next action: Scan the repo, identify public APIs, then apply documentation rules only where needed.

### WORKSTREAM-02 — External docs/ technical documentation structure

- Objective: Establish or reconcile authoritative technical documentation under docs/.
- Current state: Desired structure was specified. Actual docs were not inspected or changed in this chat.
- Desired end state: docs/ accurately describes architecture, dependencies, contracts, style, build topology, components, documentation standards, and material subsystem specs.
- Priority: highest
- Decisions: DECISION-01, DECISION-05, DECISION-13, DECISION-14
- Tasks: TASK-04, TASK-06, TASK-07, TASK-08, TASK-09
- Constraints: CONSTRAINT-01, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10
- Artifacts: ARTIFACT-08, ARTIFACT-12, ARTIFACT-13, ARTIFACT-14
- Risks: RISK-01, RISK-02, RISK-03, RISK-10
- Open questions: VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-07, VERIFY-08
- Next action: Run a repo comprehension pass, then reconcile docs/ against code and CMake.

### WORKSTREAM-03 — Root README as public landing page and technical hub

- Objective: Rewrite or restructure root README.md so it works for lay users, technical readers, and future contributors.
- Current state: A focused README prompt and a later integrated refactor-reconciliation prompt were generated. README was not modified in this chat.
- Desired end state: README.md stands alone as the project's temporary public landing page until a website exists and links into detailed docs.
- Priority: highest
- Decisions: DECISION-04, DECISION-13, DECISION-15
- Tasks: TASK-05
- Constraints: CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-19, CONSTRAINT-24
- Artifacts: ARTIFACT-07, ARTIFACT-12
- Risks: RISK-02, RISK-03, RISK-11
- Open questions: VERIFY-01, VERIFY-04, VERIFY-05, VERIFY-06, VERIFY-09
- Next action: Inspect actual README, code, CMake, license, and docs; then rewrite against evidence.

### WORKSTREAM-04 — Documentation ratio quality gate

- Objective: Add a compiler-agnostic CMake-integrated Python checker that measures comment density and enforces min/max ratios.
- Current state: The user supplied a detailed specification; an implementation-ready Codex prompt was generated. No script or CMake changes were made in this chat.
- Desired end state: scripts/doc_ratio_check.py exists; CMake has doc_ratio_check; local builds warn; CI builds fail on violations; docs explain the standard.
- Priority: high
- Decisions: DECISION-06, DECISION-07, DECISION-08, DECISION-09, DECISION-10, DECISION-11, DECISION-12
- Tasks: TASK-10, TASK-11, TASK-12, TASK-13
- Constraints: CONSTRAINT-13, CONSTRAINT-14, CONSTRAINT-15, CONSTRAINT-16, CONSTRAINT-17, CONSTRAINT-18, CONSTRAINT-20, CONSTRAINT-21, CONSTRAINT-22
- Artifacts: ARTIFACT-09, ARTIFACT-15, ARTIFACT-16
- Risks: RISK-07, RISK-08, RISK-09, RISK-12
- Open questions: VERIFY-12, VERIFY-14, VERIFY-15, VERIFY-16, VERIFY-17
- Next action: Use the implementation prompt only after verifying source roots and CMake structure.

### WORKSTREAM-05 — Standards-aligned Codex prompt optimization

- Objective: Upgrade documentation-generation prompts to be stricter, deterministic, and aligned with C89/C90, C++98, assembly, Markdown, and Doxygen-compatible conventions.
- Current state: A stricter prompt was generated. It contains one known typo: 'Determininism guarantees remembered' / 'Determinism guarantees remembered' should be corrected to 'Determinism guarantees' before reuse.
- Desired end state: A clean, standards-aligned Codex prompt controls documentation-only codebase passes without behavior changes.
- Priority: medium
- Decisions: DECISION-15, DECISION-17
- Tasks: TASK-15
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-11, CONSTRAINT-12
- Artifacts: ARTIFACT-11
- Risks: RISK-13
- Open questions: VERIFY-18
- Next action: Correct the known typo and reuse only with repo-aware constraints.

### WORKSTREAM-06 — Post-refactor documentation reconciliation

- Objective: Scan the current repository after heavy setup/launcher/game refactors and make docs/ plus README consistent with actual code.
- Current state: A consolidated Codex prompt was generated. No repository scan occurred in this chat.
- Desired end state: All docs reflect current setup, launcher, engine, game, tool, and build structure, with no contradictions or stale references.
- Priority: highest
- Decisions: DECISION-13, DECISION-14, DECISION-15
- Tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05
- Constraints: CONSTRAINT-01, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-24
- Artifacts: ARTIFACT-12
- Risks: RISK-01, RISK-02, RISK-03, RISK-10, RISK-11
- Open questions: VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-07, VERIFY-08, VERIFY-09
- Next action: Use Prompt A.5, but require Codex to treat repo evidence as authoritative and chat history as non-authoritative.

### WORKSTREAM-07 — Reusable per-chat report package and aggregation handoff

- Objective: Convert the prior Context Transfer Packet into a downloadable, shareable report package for this individual chat.
- Current state: This package is being generated from the previous Context Transfer Packet plus visible chat context.
- Desired end state: A set of Markdown/YAML files and a ZIP archive usable by humans, future assistants, aggregators, and future Project Spec Book construction.
- Priority: highest for this response
- Decisions: DECISION-16
- Tasks: TASK-16, TASK-17
- Constraints: CONSTRAINT-25, CONSTRAINT-26, CONSTRAINT-27, CONSTRAINT-28
- Artifacts: ARTIFACT-17, ARTIFACT-18, ARTIFACT-19, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22, ARTIFACT-23, ARTIFACT-24
- Risks: RISK-14, RISK-15
- Open questions: VERIFY-19, VERIFY-20
- Next action: Save package files and use them in a future aggregation workflow.



## 5. Registers for Merge

### Decision Register

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

### Task Register

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

### Constraint Register

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

### Open Questions Register

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

### Artifact Ledger

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

### Risk Register

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

### Verification Queue

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

## 6. Possible Cross-Chat Duplicates

- Setup, launcher, and game architecture details.
- Build target and CMake topology.
- Supported platforms.
- Project maturity/status.
- Project purpose and user-facing description.
- Documentation structure and README design.
- Quality-gate tooling if discussed in build/tooling chats.

## 7. Possible Cross-Chat Conflicts

- Other chats may define different component names or ownership boundaries.
- Later repository state may contradict proposed docs filenames.
- Another chat may already establish README text or public positioning.
- Another chat may choose a different order for implementing docs reconciliation vs source comments vs quality gate.
- Existing project docs may already have standards that differ from these prompts.

## 8. Spec Book Integration Guidance

Feed this packet into chapters on documentation standards, README/public documentation, docs/ architecture, Codex automation, and build/tooling quality gates. Convert only user-directed or repo-verified items into formal requirements. Keep examples and assistant-generated prompt drafts as background unless the user explicitly adopts them. Do not merge repo-specific claims until repository or other chat packages confirm them.

## 9. Aggregator Warnings

- Do not infer repo facts from prompt examples.
- Do not treat unexecuted prompts as implemented changes.
- Do not erase the distinction between docs reconciliation and quality gate implementation.
- Do not forget the known typo in Prompt A.4.
- Do not merge this package as a complete project spec; it is documentation-governance context for one old chat.
