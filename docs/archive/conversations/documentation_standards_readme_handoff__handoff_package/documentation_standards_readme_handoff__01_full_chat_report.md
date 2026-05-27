# Full Chat Report — Documentation Standards and README Handoff

## 0. Report Metadata

- Chat label: Documentation Standards and README Handoff
- Filesystem-safe label: `documentation_standards_readme_handoff`
- Generated date anchor: 2026-05-27 Australia/Melbourne
- Source scope: This package covers this visible chat only. Project-level context is used only where explicitly labelled PROJECT-CONTEXT.
- Apparent coverage: full for visible chat; partial for wider project
- Extraction confidence: 4 / 5
- Staleness risk: medium
- Future plans present: yes
- Pending tasks present: yes
- Artifacts/files present: yes
- Safe for aggregation: yes, with caveats
- Main limitations:
  - No repository was scanned in this chat.
  - No actual project files were modified before this package.
  - Other setup, launcher, and game design chats are unavailable.
  - Actual repo facts remain UNCERTAIN / UNVERIFIED until code and docs are inspected.

## 1. Executive Summary

FACT: This chat was about designing, standardizing, and packaging documentation strategy for a long-lived C/C++ systems codebase in the wider Dominium Game project context. The visible chat did not inspect the repository and did not modify any files before this final packaging task. Its concrete outputs were advisory frameworks and reusable Codex prompts for documentation generation, README overhaul, documentation quality enforcement, and post-refactor documentation reconciliation.

FACT: The user’s initial focus was how Codex should document every file in the codebase for long-term maintainability and extensibility. The conversation established a layered documentation model: public API contracts belong in headers; source files should document implementation rationale, invariants, non-obvious algorithms, and hazards; external docs should hold architecture, dependency policy, build topology, style, contracts, and subsystem specifications. This model was chosen to avoid both code-comment bloat and stale sister documentation.

FACT: The chat then refined C and C++ documentation practices. The user asked whether documentation should include metadata, arguments, complexity, destructors, modifications, memory/registers, prohibitions, requirements, dependencies, and descendants. The resulting guidance distinguished public API requirements from implementation comments, treated ownership and lifetime as mandatory for public APIs, treated register clobbers as relevant only for assembly/inline assembly, and rejected line-by-line narration. Examples were generated for C headers, POSIX-style implementation files, and C++98 classes. These examples are style references only, not repository facts.

FACT: The user then asked how to balance documentation detail against file size. The conversation introduced tiered documentation, documentation-density limits, and the concept of mechanical enforcement. This developed into a user-specified documentation ratio quality gate: a standalone Python 3 script integrated into CMake, compiler-agnostic, with local warning behavior and CI failure behavior. The specified thresholds were line comments 20–40%, comment words 15–30%, and comment characters 10–25%. The checker should count only C/C++ line and block comments and exclude generated, third-party, vendored, build, and external dependency code.

FACT: Several Codex prompts were generated. One prompt directs Codex to document every file and create/update repository docs. Another directs Codex to overhaul README.md into an industry-standard landing page. Another implements the documentation ratio quality gate. Another upgrades documentation generation to C89/C90, C++98, assembly, Markdown, and Doxygen-compatible conventions. The final and most directly relevant prompt tells Codex to scan the refactored repository, update all docs/, and overhaul README.md after setup, launcher, and game design refactors. None of these prompts were executed in this chat.

FACT: The user later stated that the project had been heavily refactored in separate setup, launcher, and game design chats. Those chats are not visible here. The current repository must therefore be treated as authoritative once inspected. Future assistants must not assume the exact directory layout, target graph, supported platforms, license, or maturity status from this chat alone.

FACT: The previous assistant produced a maximum-fidelity Context Transfer Packet. This final package normalizes that packet into stable-ID registers, a human report, a YAML spec sheet, an aggregator packet, a reader brief, a verification/audit file, and a manifest. The highest-priority next action is to inspect the actual repository, then reconcile docs/ and README.md using repo evidence before applying source/header documentation or documentation ratio enforcement.

## 2. How to Use This Report

This report covers this visible chat only. It is not a full project history and does not include the unavailable setup, launcher, or game design chats except where the user explicitly referred to them. Items labelled FACT are explicitly present in this chat. Items labelled INFERENCE are reasonable conclusions from the visible chat but should not be treated as direct user decisions unless separately confirmed. Items labelled UNCERTAIN / UNVERIFIED require repository inspection or user confirmation. Items labelled PROJECT-CONTEXT come from the surrounding project context rather than the visible transcript.

Direct user statements outrank assistant suggestions. Actual repository contents, once inspected, outrank every prompt, example, and inference in this package. Assistant-generated prompts are artifacts, not completed work. Tentative directions remain tentative until accepted by the user or verified in the repository.

Use this package as source material for a future master Project Spec Book, but preserve provenance labels. Do not merge similar items from other chats without evidence. Do not erase contradictions. Do not treat stale or external-world claims as current without verification.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Source basis | Strength | Implication | Risk | Label |
|---|---|---|---|---|---|---|
| PREF-01 | Straightforward, critical, low-fluff communication. | User profile/instructions in this chat context | strong | Future assistants should provide direct, precise answers without praise or soft filler. | May produce over-soft or vague responses. | FACT |
| PREF-02 | Correctly cited, rigorously checked facts. | User profile says interest in correctly cited sources and rigorously tested facts. | strong | Use repo evidence for project facts; verify current external facts when needed. | Future docs may overstate unverified claims. | FACT |
| PREF-03 | Second- and third-order thinking. | User profile. | medium/strong | Expose implications, risks, and downstream effects of documentation decisions. | May miss maintainability consequences. | FACT |
| PREF-05 | Mechanically enforced standards over social/process-only standards. | User said documentation quality should be enforced mechanically, not socially. | strong | Prefer scripts/CI gates where appropriate. | Future assistant may offer weak policy-only solution. | FACT |
| PREF-06 | README must work for laypeople and technicians. | User explicitly requested layman-understandable and technician-detailed README. | strong | Use layered explanations and avoid jargon without explanation. | README may become too technical or too shallow. | FACT |
| PREF-07 | Preserve tentative status and rejected options. | User gave rules for context transfer and packaging. | strong | Do not collapse brainstorms into decisions. | Future aggregation may encode false requirements. | FACT |
| PREF-08 | No speculation or invented project facts. | Repeated in user and generated prompts. | strong | Require repo scan before claims. | Docs may hallucinate features/platforms. | FACT |
| PREF-09 | Desire for future aggregation into a Project Spec Book. | Current request says package should later combine into reports and source material for a Project Spec Book. | strong | Use stable IDs, registers, YAML, and provenance labels. | Later merger will lose traceability. | FACT |
| PREF-10 | Exact file/package outputs when requested. | Current request enumerates files and ZIP behavior. | strong | Create actual files when tools are available. | User may not be able to save/reuse package. | FACT |

### 3.2 Inferred Preferences

| ID | Preference | Source basis | Strength | Implication | Risk | Label |
|---|---|---|---|---|---|---|
| PREF-04 | Deterministic, implementation-ready prompts. | User repeatedly asked for Codex prompts with exact constraints. | strong | Prompts should be copy-paste-ready and non-interactive. | Vague prompts may cause Codex drift. | INFERENCE |

### 3.3 Preferences Not Established by This Chat

| Item | Status | Implication |
|---|---|---|
| Exact preferred repository documentation generator | UNCERTAIN / UNVERIFIED | Do not assume Doxygen is installed or required. |
| Exact README visual style | UNCERTAIN / UNVERIFIED | Use neutral industry-standard Markdown unless repo style says otherwise. |
| Exact commit workflow for Codex | UNCERTAIN / UNVERIFIED | Prompts requested commits, but actual environment may require patches instead. |
| Whether source/header documentation should happen before docs reconciliation | UNCERTAIN / UNVERIFIED | Latest direction favors repo/docs reconciliation first. |

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Per-file C/C++/assembly documentation standard | Define and later apply a consistent documentation standard for every non-trivial C, C++, header, and assembly file. | A standard was designed in conversation and encoded in Codex prompts. It has not been applied to a repository in this chat. | Every non-trivial source/header/assembly file has structured documentation appropriate to its role; public contracts live in headers; implementation rationale lives in source files. | active, not executed in this chat | high | 4 | FACT / INFERENCE |
| WORKSTREAM-02 | External docs/ technical documentation structure | Establish or reconcile authoritative technical documentation under docs/. | Desired structure was specified. Actual docs were not inspected or changed in this chat. | docs/ accurately describes architecture, dependencies, contracts, style, build topology, components, documentation standards, and material subsystem specs. | active, not executed in this chat | highest | 4 | FACT / INFERENCE |
| WORKSTREAM-03 | Root README as public landing page and technical hub | Rewrite or restructure root README.md so it works for lay users, technical readers, and future contributors. | A focused README prompt and a later integrated refactor-reconciliation prompt were generated. README was not modified in this chat. | README.md stands alone as the project's temporary public landing page until a website exists and links into detailed docs. | active, not executed in this chat | highest | 5 | FACT |
| WORKSTREAM-04 | Documentation ratio quality gate | Add a compiler-agnostic CMake-integrated Python checker that measures comment density and enforces min/max ratios. | The user supplied a detailed specification; an implementation-ready Codex prompt was generated. No script or CMake changes were made in this chat. | scripts/doc_ratio_check.py exists; CMake has doc_ratio_check; local builds warn; CI builds fail on violations; docs explain the standard. | active, separate implementation workstream | high | 5 | FACT |
| WORKSTREAM-05 | Standards-aligned Codex prompt optimization | Upgrade documentation-generation prompts to be stricter, deterministic, and aligned with C89/C90, C++98, assembly, Markdown, and Doxygen-compatible conventions. | A stricter prompt was generated. It contains one known typo: 'Determininism guarantees remembered' / 'Determinism guarantees remembered' should be corrected to 'Determinism guarantees' before reuse. | A clean, standards-aligned Codex prompt controls documentation-only codebase passes without behavior changes. | active artifact, requires minor correction | medium | 4 | FACT |
| WORKSTREAM-06 | Post-refactor documentation reconciliation | Scan the current repository after heavy setup/launcher/game refactors and make docs/ plus README consistent with actual code. | A consolidated Codex prompt was generated. No repository scan occurred in this chat. | All docs reflect current setup, launcher, engine, game, tool, and build structure, with no contradictions or stale references. | active, highest next-action candidate | highest | 4 for user intent; 2 for actual repo details | FACT / UNCERTAIN |
| WORKSTREAM-07 | Reusable per-chat report package and aggregation handoff | Convert the prior Context Transfer Packet into a downloadable, shareable report package for this individual chat. | This package is being generated from the previous Context Transfer Packet plus visible chat context. | A set of Markdown/YAML files and a ZIP archive usable by humans, future assistants, aggregators, and future Project Spec Book construction. | active in current response; complete if files are successfully created | highest for this response | 5 | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — Per-file C/C++/assembly documentation standard

- Label: FACT / INFERENCE
- Objective: Define and later apply a consistent documentation standard for every non-trivial C, C++, header, and assembly file.
- Background: The user asked what Codex should document for each file, including metadata, functions, definitions, dependencies, destructors, memory/registers, requirements, and prohibitions.
- Current state: A standard was designed in conversation and encoded in Codex prompts. It has not been applied to a repository in this chat.
- Desired end state: Every non-trivial source/header/assembly file has structured documentation appropriate to its role; public contracts live in headers; implementation rationale lives in source files.
- Importance: Long-term maintainability, explicit invariants, and extensibility depend on stable contracts and discoverable boundaries.
- Decisions made: DECISION-01, DECISION-02, DECISION-03, DECISION-17
- Decisions pending: TASK-14
- Pending tasks: TASK-14
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-11, CONSTRAINT-12
- Dependencies: Repository access; Public/private API identification; Existing comment conventions
- Timeline / sequencing: After repository scan and after docs reconciliation if the user chooses to apply source/header comments.
- Blockers: Repository was not scanned in this chat.
- Risks: RISK-04, RISK-05, RISK-06
- Artifacts: ARTIFACT-01, ARTIFACT-02, ARTIFACT-03, ARTIFACT-04, ARTIFACT-05, ARTIFACT-08, ARTIFACT-11
- Success criteria: Every non-trivial file has a structured header.; Every public API symbol is documented once in headers.; Runtime behavior remains unchanged.
- Recommended next action: Scan the repo, identify public APIs, then apply documentation rules only where needed.
- Verification needed: VERIFY-10, VERIFY-11, VERIFY-13
- Confidence: 4
- Carry-forward priority: high

### WORKSTREAM-02 — External docs/ technical documentation structure

- Label: FACT / INFERENCE
- Objective: Establish or reconcile authoritative technical documentation under docs/.
- Background: The user wanted durable documentation beyond per-file comments, especially after major setup/launcher/game refactors.
- Current state: Desired structure was specified. Actual docs were not inspected or changed in this chat.
- Desired end state: docs/ accurately describes architecture, dependencies, contracts, style, build topology, components, documentation standards, and material subsystem specs.
- Importance: Architecture, dependency policy, extension recipes, and build topology are cross-file concerns that become stale unless centralized.
- Decisions made: DECISION-01, DECISION-05, DECISION-13, DECISION-14
- Decisions pending: TASK-04, TASK-06, TASK-07, TASK-08, TASK-09
- Pending tasks: TASK-04, TASK-06, TASK-07, TASK-08, TASK-09
- Constraints: CONSTRAINT-01, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10
- Dependencies: Repository scan; Existing docs inventory; CMake target graph; Component inventory
- Timeline / sequencing: Immediate next major workstream if continuing this chat's work.
- Blockers: No repository inspection occurred in this chat.; Other refactor chats are unavailable.
- Risks: RISK-01, RISK-02, RISK-03, RISK-10
- Artifacts: ARTIFACT-08, ARTIFACT-12, ARTIFACT-13, ARTIFACT-14
- Success criteria: docs/ matches current code.; No stale paths.; No contradictions among README, ARCHITECTURE, DEPENDENCIES, and COMPONENTS.
- Recommended next action: Run a repo comprehension pass, then reconcile docs/ against code and CMake.
- Verification needed: VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-07, VERIFY-08
- Confidence: 4
- Carry-forward priority: highest

### WORKSTREAM-03 — Root README as public landing page and technical hub

- Label: FACT
- Objective: Rewrite or restructure root README.md so it works for lay users, technical readers, and future contributors.
- Background: The user explicitly requested a complete high- and low-level summary, industry/consumer-standard presentation, and at-a-glance usefulness.
- Current state: A focused README prompt and a later integrated refactor-reconciliation prompt were generated. README was not modified in this chat.
- Desired end state: README.md stands alone as the project's temporary public landing page until a website exists and links into detailed docs.
- Importance: README is the first public contact point and must prevent misinterpretation by users, engineers, and contributors.
- Decisions made: DECISION-04, DECISION-13, DECISION-15
- Decisions pending: TASK-05
- Pending tasks: TASK-05
- Constraints: CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-19, CONSTRAINT-24
- Dependencies: Actual project name; License; Supported platforms; Build outputs; Current docs
- Timeline / sequencing: Should be done after or during docs/ reconciliation so README links and claims are accurate.
- Blockers: Project facts were not verified from repo in this chat.
- Risks: RISK-02, RISK-03, RISK-11
- Artifacts: ARTIFACT-07, ARTIFACT-12
- Success criteria: A non-technical reader understands the project quickly.; An engineer can assess architecture and where to read further.; README contains no speculative or stale claims.
- Recommended next action: Inspect actual README, code, CMake, license, and docs; then rewrite against evidence.
- Verification needed: VERIFY-01, VERIFY-04, VERIFY-05, VERIFY-06, VERIFY-09
- Confidence: 5
- Carry-forward priority: highest

### WORKSTREAM-04 — Documentation ratio quality gate

- Label: FACT
- Objective: Add a compiler-agnostic CMake-integrated Python checker that measures comment density and enforces min/max ratios.
- Background: The user wants documentation quality enforced mechanically rather than socially.
- Current state: The user supplied a detailed specification; an implementation-ready Codex prompt was generated. No script or CMake changes were made in this chat.
- Desired end state: scripts/doc_ratio_check.py exists; CMake has doc_ratio_check; local builds warn; CI builds fail on violations; docs explain the standard.
- Importance: It detects documentation drift, underdocumentation, and overcommenting across a long-lived codebase.
- Decisions made: DECISION-06, DECISION-07, DECISION-08, DECISION-09, DECISION-10, DECISION-11, DECISION-12
- Decisions pending: TASK-10, TASK-11, TASK-12, TASK-13
- Pending tasks: TASK-10, TASK-11, TASK-12, TASK-13
- Constraints: CONSTRAINT-13, CONSTRAINT-14, CONSTRAINT-15, CONSTRAINT-16, CONSTRAINT-17, CONSTRAINT-18, CONSTRAINT-20, CONSTRAINT-21, CONSTRAINT-22
- Dependencies: Top-level CMakeLists.txt; Actual source roots; CI environment variables; Python availability
- Timeline / sequencing: Can be implemented independently after docs reconciliation or before source documentation pass.
- Blockers: Actual repo source roots and CI conventions unverified.
- Risks: RISK-07, RISK-08, RISK-09, RISK-12
- Artifacts: ARTIFACT-09, ARTIFACT-15, ARTIFACT-16
- Success criteria: Warns locally and exits 0.; Fails in CI when ratios violate thresholds.; Excludes generated/vendor/build code.; Thresholds documented as drift detectors.
- Recommended next action: Use the implementation prompt only after verifying source roots and CMake structure.
- Verification needed: VERIFY-12, VERIFY-14, VERIFY-15, VERIFY-16, VERIFY-17
- Confidence: 5
- Carry-forward priority: high

### WORKSTREAM-05 — Standards-aligned Codex prompt optimization

- Label: FACT
- Objective: Upgrade documentation-generation prompts to be stricter, deterministic, and aligned with C89/C90, C++98, assembly, Markdown, and Doxygen-compatible conventions.
- Background: The user asked to optimize a previous prompt and conform strictly to international code documentation standards for project languages and documentation formats.
- Current state: A stricter prompt was generated. It contains one known typo: 'Determininism guarantees remembered' / 'Determinism guarantees remembered' should be corrected to 'Determinism guarantees' before reuse.
- Desired end state: A clean, standards-aligned Codex prompt controls documentation-only codebase passes without behavior changes.
- Importance: Prompt quality directly affects whether Codex preserves semantics and avoids documentation bloat.
- Decisions made: DECISION-15, DECISION-17
- Decisions pending: TASK-15
- Pending tasks: TASK-15
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-11, CONSTRAINT-12
- Dependencies: Existing repo style; User choice to run source/header docs pass
- Timeline / sequencing: Before any source/header documentation Codex run.
- Blockers: Known typo must be corrected.
- Risks: RISK-13
- Artifacts: ARTIFACT-11
- Success criteria: Prompt is typo-free, deterministic, and does not invite semantic code changes.
- Recommended next action: Correct the known typo and reuse only with repo-aware constraints.
- Verification needed: VERIFY-18
- Confidence: 4
- Carry-forward priority: medium

### WORKSTREAM-06 — Post-refactor documentation reconciliation

- Label: FACT / UNCERTAIN
- Objective: Scan the current repository after heavy setup/launcher/game refactors and make docs/ plus README consistent with actual code.
- Background: The user stated the project had been heavily refactored in setup, launcher, and game design chats. Those chats are not visible here.
- Current state: A consolidated Codex prompt was generated. No repository scan occurred in this chat.
- Desired end state: All docs reflect current setup, launcher, engine, game, tool, and build structure, with no contradictions or stale references.
- Importance: Refactors make old docs misleading; docs must be synchronized before future assistants or contributors rely on them.
- Decisions made: DECISION-13, DECISION-14, DECISION-15
- Decisions pending: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05
- Pending tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05
- Constraints: CONSTRAINT-01, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-24
- Dependencies: Repository access; Existing docs; CMakeLists; File tree; Actual refactored components
- Timeline / sequencing: Should be the first repo-facing action in a new chat.
- Blockers: Refactor chats unavailable; repo not inspected here.
- Risks: RISK-01, RISK-02, RISK-03, RISK-10, RISK-11
- Artifacts: ARTIFACT-12
- Success criteria: docs/ matches code.; README works as public landing page.; No runtime or build behavior changes.
- Recommended next action: Use Prompt A.5, but require Codex to treat repo evidence as authoritative and chat history as non-authoritative.
- Verification needed: VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-07, VERIFY-08, VERIFY-09
- Confidence: 4 for user intent; 2 for actual repo details
- Carry-forward priority: highest

### WORKSTREAM-07 — Reusable per-chat report package and aggregation handoff

- Label: FACT
- Objective: Convert the prior Context Transfer Packet into a downloadable, shareable report package for this individual chat.
- Background: The user explicitly requested final package files with stable IDs, registers, a spec sheet, an aggregator packet, a reader brief, verification/audit, and a manifest.
- Current state: This package is being generated from the previous Context Transfer Packet plus visible chat context.
- Desired end state: A set of Markdown/YAML files and a ZIP archive usable by humans, future assistants, aggregators, and future Project Spec Book construction.
- Importance: Prevents loss of decisions, prompts, constraints, and unresolved tasks when retiring this chat.
- Decisions made: DECISION-16
- Decisions pending: TASK-16, TASK-17
- Pending tasks: TASK-16, TASK-17
- Constraints: CONSTRAINT-25, CONSTRAINT-26, CONSTRAINT-27, CONSTRAINT-28
- Dependencies: Prior Context Transfer Packet; Visible chat transcript
- Timeline / sequencing: Immediate current task.
- Blockers: None if file generation succeeds.
- Risks: RISK-14, RISK-15
- Artifacts: ARTIFACT-17, ARTIFACT-18, ARTIFACT-19, ARTIFACT-20, ARTIFACT-21, ARTIFACT-22, ARTIFACT-23, ARTIFACT-24
- Success criteria: All requested files exist.; ZIP archive exists if possible.; Final response provides download links and caveats.
- Recommended next action: Save package files and use them in a future aggregation workflow.
- Verification needed: VERIFY-19, VERIFY-20
- Confidence: 5
- Carry-forward priority: highest


## 6. Chronological Timeline

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

## 7. Decisions

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

### Highest-impact decisions

DECISION-02 and DECISION-03 are the core maintainability split: headers hold public contracts; source files explain implementation rationale. DECISION-04 defines README.md as a public-facing landing page, not a deep technical manual. DECISION-06 through DECISION-12 define the mechanical documentation quality gate and must be preserved if that workstream is implemented. DECISION-13 prevents the post-refactor docs reconciliation pass from accidentally modifying runtime or build behavior. DECISION-16 is specific to this final packaging task and preserves the chat for future aggregation.

## 8. Pending Tasks and Next Actions

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

### 8.1 Recommended Task Order

1. TASK-01: Inspect the current repository.
2. TASK-02 and TASK-03: Identify components and CMake build graph.
3. TASK-04 and TASK-05: Reconcile docs/ and overhaul README.
4. TASK-06 through TASK-09: Add/update structural docs only where repo evidence supports them.
5. TASK-10 through TASK-13: Implement documentation ratio quality gate as a separate build/tooling workstream.
6. TASK-14: Apply source/header/assembly documentation standard after architecture docs and public API boundaries are verified.
7. TASK-15: Correct the typo in the upgraded standards prompt before reuse.

### 8.2 Blocked Tasks

- TASK-04, TASK-05, TASK-06, TASK-07, TASK-08, TASK-09, TASK-10, TASK-11, TASK-12, TASK-13, and TASK-14 are blocked by repository inspection.
- TASK-16 requires packages from other old chats.

### 8.3 Quick Wins

- Correct Prompt A.4 typo: replace `Determinism guarantees remembered` with `Determinism guarantees`.
- Save this package ZIP and Markdown/YAML files together.
- Use ARTIFACT-12 as the next repository-facing prompt once repo access is available.

### 8.4 Tasks Requiring Verification

Tasks requiring repo verification: TASK-01 through TASK-14 except TASK-15 and TASK-17.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

| ID | Constraint | Type | Source / basis | Practical implication | Violation risk | Label |
|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Do not change runtime behavior. | process | User and generated prompts | Documentation passes must not alter logic, control flow, algorithms, APIs, or data layouts. | high | FACT |
| CONSTRAINT-02 | Do not refactor code. | process | User and prompts | No cleanup or restructuring during documentation tasks. | high | FACT |
| CONSTRAINT-03 | Do not rename symbols, files, or targets during documentation-only work. | process | Prompts | Preserve API/linkage and project layout. | high | FACT |
| CONSTRAINT-04 | Do not reorder statements, declarations, logic, or includes. | process | Prompts | Minimize semantic/build risk. | medium | FACT |
| CONSTRAINT-05 | Do not introduce new dependencies during documentation-only pass. | technical | Prompts | Avoid adding Doxygen/clang tools unless separately requested. | medium | FACT |
| CONSTRAINT-06 | No speculation, roadmap, or invented features. | evidence | User/prompts | Docs and README must describe current repo only. | high | FACT |
| CONSTRAINT-07 | No TODOs or placeholders in generated docs/prompts. | quality | User/prompts | Outputs must be complete or explicitly mark unknowns. | medium | FACT |
| CONSTRAINT-08 | No marketing hype or aspirational language. | style | User/prompts | README should be credible and neutral. | medium | FACT |
| CONSTRAINT-09 | One canonical home per fact. | architecture | Prompts | Avoid contradictions and duplication. | high | FACT / INFERENCE |
| CONSTRAINT-10 | README is overview/navigation, not deep spec. | format | User/prompts | Detailed architecture and build info should live in docs/. | medium | FACT |
| CONSTRAINT-11 | C89/C90 and C++98 compatibility must be respected in documentation examples and assumptions. | technical | User/prompts | Avoid C99/C++11 assumptions in generated examples or standards. | medium | FACT |
| CONSTRAINT-13 | Documentation ratio checker must use Python 3 with no third-party imports. | technical | User spec | Keep portable and dependency-free. | medium | FACT |
| CONSTRAINT-14 | Documentation ratio checker must be heuristic, not AST-level. | technical | User non-goals | No clang-tools or full parser. | low | FACT |
| CONSTRAINT-15 | Documentation ratio checker must count only // and /* ... */ comments. | technical | User definition | Do not count generated docs or Markdown as code comments. | medium | FACT |
| CONSTRAINT-16 | Generated, third-party, vendored, build, and external dependency code must be excluded from documentation ratios. | technical | User definition | Avoid false enforcement on non-project code. | high | FACT |
| CONSTRAINT-17 | Local documentation ratio violations warn and exit success. | build | User spec | Developer builds should not fail locally. | high | FACT |
| CONSTRAINT-18 | CI documentation ratio violations hard fail. | build | User spec | CI blocks drift. | high | FACT |
| CONSTRAINT-19 | Do not alter license text. | legal/documentation | README prompt | README may link or state license but must not change terms. | high | FACT |
| CONSTRAINT-20 | Quality gate must be compiler-agnostic. | technical | User spec | No MSVC/GCC diagnostic tricks. | medium | FACT |
| CONSTRAINT-21 | CMake must find Python3 interpreter for quality gate. | technical | User spec | Use find_package(Python3 COMPONENTS Interpreter). | medium | FACT |
| CONSTRAINT-22 | Documentation ratio thresholds are fixed unless user revises them. | standard | User spec | Lines 20–40%, words 15–30%, chars 10–25%. | medium | FACT |
| CONSTRAINT-23 | Docs reconciliation modifies docs/** and README.md only. | process | Latest prompt | Do not change source/build during that pass. | high | FACT |
| CONSTRAINT-24 | Repo evidence outranks prior chat/prompt assumptions. | evidence | Current handoff rules | Actual code is authoritative after scan. | high | FACT |
| CONSTRAINT-25 | Final package must use stable IDs. | format | Current user request | All registers use WORKSTREAM, DECISION, TASK, etc. | medium | FACT |
| CONSTRAINT-26 | Important items must be labelled FACT, INFERENCE, UNCERTAIN / UNVERIFIED, or PROJECT-CONTEXT. | evidence | Current user request | Prevents unsupported facts from entering future spec. | high | FACT |
| CONSTRAINT-27 | This package covers this chat only, not the whole project. | scope | Current user request | Do not summarize unseen project context as fact. | high | FACT |
| CONSTRAINT-28 | If files are not actually created, do not claim downloads exist. | artifact | Current user request | Final response must match actual file creation. | high | FACT |

### 9.2 Soft Preferences

No soft preferences were established as binding requirements. The communication preferences in Section 3 are strong but not project code requirements unless user makes them formal.

### 9.3 Technical Constraints

Relevant technical constraints include CONSTRAINT-11 through CONSTRAINT-22.

### 9.4 Time / Resource Constraints

No explicit deadline was stated. Resource constraint: repository was not available or inspected in this chat.

### 9.5 Legal / Ethical / Safety Constraints

CONSTRAINT-19: do not alter license text.

### 9.6 Evidence / Citation Requirements

CONSTRAINT-24: repo evidence outranks prior chat assumptions. External-world facts, current software/API behavior, prices, laws, schedules, or institutional rules require verification before use.

### 9.7 Formatting / Output Requirements

CONSTRAINT-25 through CONSTRAINT-28 govern this package. Prompt outputs should remain deterministic, stable-ID based, and non-interactive.

### 9.8 Things to Avoid

Avoid all rejected options in Section 11, especially speculative README claims, duplicated header/source contracts, compiler-specific quality enforcement, and documentation of non-existent subsystems.

## 10. Open Questions and Unresolved Issues

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

## 11. Rejected, Superseded, or Deprioritised Options

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

Preserving rejected options prevents future assistants from proposing the same discarded patterns: comments-only documentation, sister-files-only documentation, compiler-warning enforcement, AST-based tooling, marketing README tone, speculative roadmap content, and subsystem specs for architecture that has not been verified.

## 12. Artifact Ledger

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

## 13. Rationale and Assumptions

The visible rationale behind the major choices is straightforward. Header documentation was prioritized because API consumers read headers and need contracts near declarations. Source comments were narrowed to rationale and hazards because duplicated contract prose becomes stale. External docs were retained because architecture and dependency policy span files and cannot be represented cleanly in comments alone. README was elevated to landing-page status because the user explicitly needs a public-facing summary before a website exists. Documentation ratios were introduced as a drift detector because the user wants mechanically enforced discipline rather than reliance on reviewer memory.

Key assumptions:
- The repository uses headers as public API boundaries. This remains UNCERTAIN / UNVERIFIED until inspected.
- The repository has enough architecture to justify docs/ structure. This is likely but unverified.
- The project uses CMake and targets MSVC/GCC in the quality-gate context because the user explicitly stated that for the codebase.
- Python 3 is available or can be found by CMake. This must be verified in actual environments.
- Setup, launcher, and game refactors exist because the user stated they occurred, but their exact effects are unknown.

## 14. Risks and Failure Modes

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

## 15. Verification Queue

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

## 16. Spec Book Contribution Notes

Likely future Project Spec Book sections:
- Documentation Philosophy and Standards
- Source/Header Commenting Rules
- README and Public Documentation Strategy
- Repository Documentation Architecture
- CMake Quality Gates and Tooling
- Documentation Ratio Standard
- Prompting/Automation Rules for Codex
- Refactor Documentation Synchronization

Unique contributions from this chat:
- The header/source/docs documentation hierarchy.
- The documentation ratio quality gate specification.
- README-as-landing-page requirements.
- The post-refactor docs reconciliation prompt.
- Stable prompt artifacts for future Codex execution.

Likely duplicates with other chats:
- Setup, launcher, and game architecture details.
- Build system specifics.
- Supported platforms and release/maturity status.
- Project purpose and user-facing description.

Conflicts to watch for:
- Other chats may define different component names or boundaries.
- Other chats may already specify docs structure or README tone.
- Later repo state may supersede all prompt assumptions.
- Quality gate thresholds may need staged adoption if current code fails badly.

Items that should become formal requirements:
- No speculative docs.
- Headers as public API contract authority.
- Source comments only for rationale/hazards.
- README as landing page and navigation hub.
- Local warn / CI fail documentation quality gate, if implemented.
- Exclusion of third-party/generated/build code from documentation metrics.

Items that should remain background context:
- Example `dsys_file` and `arena` snippets.
- Advisory pre-quality-gate comment ratio ranges.
- Assistant-generated prompt wording unless accepted or executed.

Items needing user confirmation:
- Whether to run docs reconciliation before source/header doc pass.
- Whether to implement the quality gate immediately.
- Whether Codex should commit changes or produce patches in the actual workflow.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | No repository was scanned or modified in this chat. | Fact boundary | Prevents false assumptions. | Bad docs based on nonexistent verification. | FACT | 5 |
| 2 | Actual repository contents must be authoritative once inspected. | Evidence rule | Refactors occurred outside this chat. | Old prompts may contradict current code. | FACT | 5 |
| 3 | Headers are canonical homes for public API contracts. | Decision | Prevents duplicated contracts. | API docs drift. | FACT / INFERENCE | 4 |
| 4 | Source files should document implementation rationale and hazards only. | Decision | Controls bloat and duplication. | Unreadable comments and contradictions. | FACT / INFERENCE | 4 |
| 5 | README must serve lay users and technicians as a landing page. | User requirement | Public front door until website exists. | README too shallow or too technical. | FACT | 5 |
| 6 | docs/ should contain architecture, dependencies, contracts, style, build overview, components, and subsystem specs as supported by repo evidence. | Architecture direction | Keeps deep docs out of README. | Docs fragmentation or bloat. | FACT / INFERENCE | 4 |
| 7 | Documentation quality gate thresholds are exact user-provided numbers. | Requirement | Mechanical enforcement depends on them. | Incorrect CI behavior or weak standard. | FACT | 5 |
| 8 | Local doc-ratio violations warn; CI violations fail. | Requirement | Workflow balance. | Developer disruption or weak enforcement. | FACT | 5 |
| 9 | No AST/clang/compiler-warning enforcement for doc ratios. | Rejected option | User explicitly excluded it. | Unwanted dependency/tooling complexity. | FACT | 5 |
| 10 | Latest next-action prompt is post-refactor docs reconciliation, not immediate source comment insertion. | Sequencing | User mentioned heavy refactors. | Source docs could codify stale architecture. | FACT / INFERENCE | 4 |
| 11 | Correct typo in standards prompt before reuse. | Artifact caveat | Known defect. | Prompt quality issue. | FACT | 5 |
| 12 | Do not treat assistant prompts as executed work. | Fact boundary | No files changed in chat. | False project state. | FACT | 5 |

## 18. What Future Assistants Must Not Assume

- Do not assume the actual project name beyond PROJECT-CONTEXT unless repo confirms it.
- Do not assume `setup/`, `launcher/`, `engine/`, `game/`, `tools/`, or `tests/` directories exist.
- Do not assume supported platforms beyond evidence from repo/build files.
- Do not assume project maturity.
- Do not assume license.
- Do not assume README currently contains accurate facts.
- Do not assume docs/ exists or matches desired structure.
- Do not assume Codex prompts were executed.
- Do not assume CMake source roots are `src` and `include`.
- Do not assume documentation ratio thresholds are currently passable.
- Do not assume Doxygen is installed or desired as tooling.
- Do not assume other old chats agree with this one.

## 19. Recommended Next Action

If continuing this chat's work alone: inspect the current repository, then run the post-refactor docs reconciliation and README overhaul plan using ARTIFACT-12.

If aggregating this chat with other chat reports: ingest this package as the documentation/governance packet, mark repo-specific facts as unverified, and compare its assumptions against setup, launcher, game design, build, and project-spec packages.

User verification needed before acting: confirm whether the next actual implementation should be docs/README reconciliation, source/header documentation insertion, or documentation ratio quality gate implementation.

## 20. Appendix: Possibly Relevant Details

### Appendix A — Prompt Bank Preservation

This chat generated multiple Codex prompts. They were not executed in this chat.

#### ARTIFACT-08 — Full-file documentation prompt

Purpose: direct Codex to scan source/header/assembly files, add/normalize file headers and API documentation, create/update docs/, and update README without behavior changes.

Critical wording preserved:
- "Your task is documentation only. DO NOT change runtime behavior, logic, algorithms, or APIs except where required to add comments, doc blocks, or documentation files."
- "Headers are contracts."
- "DO NOT repeat this documentation in source files."
- "Source files may document only invariants, non-obvious algorithms/arithmetic, overflow/bounds/aliasing safety, rationale, platform/compiler quirks, and OS-to-engine error mapping."
- "No change logs. No authors. No dates."
- "Every public API symbol is documented exactly once (in headers)."

#### ARTIFACT-07 — README landing page prompt

Purpose: rewrite root README.md as a complete, accurate, high-signal overview for lay readers and engineers.

Critical wording preserved:
- "Do NOT speculate beyond what the code and existing docs support."
- "The README must communicate the project’s purpose in under 30 seconds of reading."
- Required sections included project name, high-level overview, key features, architecture overview, supported platforms, intended audience, design constraints, repository structure, documentation map, build/usage overview, project status, license, and contributing/contact if applicable.
- Prohibitions included no emojis, no marketing slogans, no speculative roadmap unless already documented, and no duplication of detailed specs already in docs/.

#### ARTIFACT-09 — Documentation ratio quality gate prompt

Purpose: implement a standalone Python 3 checker and CMake target.

Critical requirements preserved:
- Create `scripts/doc_ratio_check.py`.
- Modify top-level `CMakeLists.txt`.
- Create or update `docs/DOCUMENTATION_STANDARDS.md`.
- Update README to link to the documentation standard.
- Count only `//` and `/* ... */` comments.
- Exclude generated code, third-party/vendored code, build artifacts, and external dependencies.
- Thresholds: line count 20–40%, word count 15–30%, character count 10–25%.
- Local mode warns and exits zero; CI mode fails on violations.
- No AST-level parsing, clang-tools, compiler warnings, pragmas, or external linters.
- CMake variables required: `DOC_RATIO_ENABLE`, `DOC_RATIO_ROOTS`, `DOC_RATIO_EXCLUDES`, `DOC_RATIO_EXTS`, `DOC_RATIO_MIN_LINE`, `DOC_RATIO_MAX_LINE`, `DOC_RATIO_MIN_WORD`, `DOC_RATIO_MAX_WORD`, `DOC_RATIO_MIN_CHAR`, `DOC_RATIO_MAX_CHAR`.

#### ARTIFACT-11 — Upgraded standards prompt

Purpose: align the documentation-generation prompt with C89/C90, C++98, assembly, Doxygen-compatible comments, Markdown docs, and ASCII-safe source compatibility.

Known correction:
- Replace the erroneous line `- Determinism guarantees remembered` with `- Determinism guarantees`.

#### ARTIFACT-12 — Latest post-refactor docs reconciliation prompt

This is the most directly relevant next-action prompt. It instructed Codex to:
- Read the entire repository.
- Treat current code and directory structure as authoritative.
- Assume significant recent refactors across setup/, launcher/, engine/, and game/.
- Modify only `docs/**` and `README.md`.
- Reconcile documentation with current reality.
- Ensure `docs/README.md`, `ARCHITECTURE.md`, `DEPENDENCIES.md`, `CONTRACTS.md`, `STYLE.md`, `BUILD_OVERVIEW.md`, `COMPONENTS.md`, and material `SPEC_<SUBSYSTEM>.md` files exist and are accurate.
- Rewrite README.md as a public landing page and documentation hub.
- Ensure naming/path consistency and no contradictions between README, ARCHITECTURE, DEPENDENCIES, and COMPONENTS.
- Make no runtime or build behavior changes.
