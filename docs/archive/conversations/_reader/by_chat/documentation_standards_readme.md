Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/documentation_standards_readme/`
Promotion Status: not_reviewed

# Documentation Standards, README Strategy, and Handoff Packaging - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was about turning documentation from an informal afterthought into a disciplined, enforceable part of a long-lived C/C++ systems project. The broader project context is `PROJECT-CONTEXT: Dominium Game`, but this chat itself did not inspect the repository, modify files, or verify the current codebase. Its value is that it established documentation architecture, Codex execution prompts, a README strategy, a documentation quality-gate plan, and a reusable handoff/report package for later aggregation.

The conversation began with a practical question: the user wanted Codex to generate documentation for every file, including metadata, functions, definitions, dependencies, and related information, and wanted to know whether that documentation should live in separate sister files or in file/function headers. The answer developed into a layered documentation model. The key distinction was that different kinds of information belong in different places. Public API contracts should live in headers because that is where callers look. Source files should explain implementation rationale, invariants, and hazards, not duplicate public API contracts. External `docs/` files should explain architecture, dependency rules, subsystem design, build structure, and extension recipes. README should serve as the public-facing landing page and navigation hub.

The user then refined the problem by asking about C/C++ documentation best practices: block comments, inline comments, metadata, arguments, complexity, destructors, modifications, memory, registers, prohibitions, requirements, dependencies, and "descendants." The resulting position was that documentation should focus on contracts and non-obvious constraints, not narration. Public APIs need documentation of ownership, lifetime, nullability, aliasing, error behavior, preconditions, postconditions, side effects, thread-safety, determinism, and ABI/layout constraints where relevant. Complexity should be documented only when performance-critical or non-obvious. Register usage is generally irrelevant for normal C/C++ but important for assembly or inline assembly. File headers should describe ownership, responsibilities, dependencies, prohibitions, invariants, threading, error model, determinism, versioning/ABI/data-format issues, and extension points.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__human_readable_chat_report.txt`.

## What Was Decided

- The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions.
- `FACT:` The chat established that public API contracts should live in headers.
- `FACT:` Source files should document implementation rationale, non-obvious invariants, and hazards.
- `FACT:` External docs should cover architecture, dependency rules, extension recipes, and subsystem-level explanations.
- `FACT:` The examples were generated in the chat.
- `FACT:` They were not claimed to exist in the repository.
- This was a major decision: README should not be the full spec. It should orient readers and point them to the deeper docs.
- The final phase of the chat moved away from project documentation and into preserving the chat itself. The user requested a maximum-fidelity Context Transfer Packet, then requested that it be turned into a final downloadable/shareable report package. That package was created and included a full report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit file, manifest, and ZIP archive.
- The user then asked to inspect the package inside the chat without downloading. An in-chat reader version was produced, listing and explaining workstreams, decisions, tasks, constraints, preferences, open questions, artifacts, risks, verification items, and timeline.
- `FACT:` The chat did not decide that all documentation should live in sister files.
- `FACT:` The chat did not decide that all documentation should live in comments.
- `FACT:` The chosen direction was hybrid.

## What Was Not Decided

- The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions.
- The chat began with the user asking how to have Codex generate documentation for every file in the project. The user wanted metadata, functions, definitions, dependencies, and other maintainability information documented. The core uncertainty was placement: should documentation live in separate sister files, or should it live in file headers and function headers?
- `UNCERTAIN / UNVERIFIED:` Whether the project has similarly named files or modules is unknown.
- What remains uncertain is how the actual project currently organizes public headers, internal headers, and docs. That must be verified from the repository.
- What remains unverified is the actual project name, supported platforms, license, maturity, and current repository layout. Those cannot be responsibly written without inspecting the repo.
- The decision depends on an assumption: that the project's public APIs are declared in headers. That is likely for a C/C++ codebase, but the actual public/private boundary is still unverified.
- What must happen first: verify source roots, exclusions, CMake structure, CI environment variables, and Python availability.
- What could go wrong: treating assistant suggestions as final requirements or merging contradictory chat claims without preserving uncertainty.
- `FACT:` The user wants facts checked and uncertainty preserved.
- `INFERENCE:` The user values preserving rejected options and uncertainty because they expect to aggregate many old chats later.
- `UNCERTAIN / UNVERIFIED:` Actual repository language standards, compiler settings, source roots, and assembly presence still need verification.
- This is one of the most concrete artifacts. It describes how Codex should create a Python checker, integrate it into CMake, document it, and verify behavior.

## Ideas Rejected, Superseded, Or Deprioritised

- The rejected approach was line-by-line narration. Comments like "increment counter" or "loop over items" were considered noise.
- `INFERENCE:` The user wants to avoid future archaeology. They do not want to repeatedly rediscover architecture from code or old conversations.
- The alternative-full function docs in both `.h` and `.c/.cpp`-was rejected because it creates duplicated contract text.
- This decision depends heavily on repo verification. The README must not claim platforms, maturity, features, or structure that cannot be verified.
- This idea was rejected as a sole strategy. Separate docs are valuable for architecture, but API contracts belong near code. If function ownership rules or preconditions live only in an external document, they are likely to drift.
- This was also rejected as a sole strategy. Comments are not the right place for full architecture, subsystem design, build topology, or dependency policy.
- This was rejected because duplicated contracts rot. If a function's error behavior changes in the header but the source comment is not updated, future maintainers will not know which is correct.
- Narrating obvious control flow was rejected because it increases file size without increasing understanding. Comments should explain why code is the way it is, not restate what the syntax says.
- These were rejected because Git already tracks history. Embedded author/date metadata stales and adds noise.
- This was rejected because C/C++ compilers manage registers. Register clobber documentation is useful for assembly, inline assembly, or ABI-sensitive code, not normal C/C++ functions.

## What Future Work Came From It

- The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions.
- This became the foundation for nearly every later prompt and plan.
- The user then asked for a prompt that Codex could use to read through every file and insert, append, amend, or create documentation, including inline comments, block comments, and docs/README content.
- That prompt was the first large artifact in the chat. It was execution-ready but not executed here.
- The assistant converted this into a Codex prompt. The proposed deliverables were:
- The user then provided the earlier documentation prompt and asked to optimize it to conform more strictly to international code documentation standards for the relevant languages and documentation formats. A stricter prompt was generated, aligned with ISO C89/C90, C++98, assembly, Doxygen-compatible structured comments, Markdown docs, and ASCII-safe source compatibility.
- There was one known defect in that prompt: a typo line, `Determininism guarantees remembered` / `Determinism guarantees remembered`, depending on the preserved version. The report package later marked that as something to correct before reusing the prompt.
- Later, the user said the project had been heavily refactored in the setup, launcher, and game design chats. They wanted a prompt to scan the repository, read the code, ensure every file in `docs/` was consistent and up to date, and overhaul README in an industry-standard format that could serve as a landing page until a website exists.
- This prompt also added two documents the user had not explicitly requested but which were judged useful: `COMPONENTS.md` and `BUILD_OVERVIEW.md`. These were not presented as guaranteed project facts; they were suggested as useful if supported by the actual repository.
- The final phase of the chat moved away from project documentation and into preserving the chat itself. The user requested a maximum-fidelity Context Transfer Packet, then requested that it be turned into a final downloadable/shareable report package. That package was created and included a full report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit file, manifest, and ZIP archive.
- The user then asked to inspect the package inside the chat without downloading. An in-chat reader version was produced, listing and explaining workstreams, decisions, tasks, constraints, preferences, open questions, artifacts, risks, verification items, and timeline.
- The conclusion was not "document everything maximally." The conclusion was "document the information that future maintainers cannot safely infer from code alone."

## Important Artifacts

- `handoff`: `1`
- `manifest`: `1`
- `primary_report`: `2`
- `reader_brief`: `1`
- `registers`: `1`
- `spec_sheet`: `1`
- `verification`: `1`

## Verification Needed

- Verify every implementation, platform, tooling, release, and queue claim against current repo artifacts.
- Treat external platform or SDK claims as stale until independently checked.
- Treat old language-baseline claims as historical unless they match current `README.md` and current contracts.
- Do not infer current authority from the existence of this archive package.

## Candidate Promotions

Candidate promotions, if any, are recorded in `_promotion/PROMOTION_QUEUE.md`. This page does not promote claims.

## Do Not Assume

- Do not assume this conversation established current repo truth.
- Do not assume generated package reports are canonical.
- Do not assume old prompts were executed.
- Do not assume unresolved items are safe to implement.
- Do not use this package to open blocked work without stronger current authority.
