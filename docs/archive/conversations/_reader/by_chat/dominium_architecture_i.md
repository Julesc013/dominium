Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Dominium_Architecture_I/`
Promotion Status: not_reviewed

# Dominium Architecture I - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

**FACT:** This chat was mainly about turning the developing architecture of the **Dominium Game** into a form that could be carried forward into automated coding and later Project-level consolidation. It was not a normal design discussion by the end. It became a long-running specification-production session, where the user repeatedly asked for detailed Markdown documents and then for one `.txt` implementation-spec prompt per planned repository file.

The central problem the user was trying to solve was context size. **FACT:** The user originally wanted Codex to read a transcript of the entire conversation and generate a complete "book of volumes" describing the whole project, then start coding. That plan changed. The user explicitly recognised that Codex could not reliably read the whole conversation at once. The new strategy became: create a modular set of files, each one dedicated to a specific source file, document, schema, script, or test. These files would tell Codex exactly how to implement that part of the project without needing to ingest the whole chat.

The project itself, **Dominium**, is a deterministic, data-driven simulation game. **FACT:** The repository structure discussed in this chat includes `engine/`, `platform/`, `render/`, `audio/`, `systems/`, `game/`, `ui/`, `launcher/`, `mods/`, `tools/`, `data/`, `tests/`, and `scripts/`. The visible conversation generated detailed implementation-spec text for many files across those layers. The strongest visible design themes are determinism, replayability, strict layering, save/load stability, lockstep multiplayer compatibility, data-driven content, retro/modern platform support, UTF-8 localisation, and eventual automated implementation.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__human_readable_chat_report.txt`.

## What Was Decided

- During this stage, the work was still broadly about "the project spec." The user wanted a comprehensive description of the game and its technical systems. The assistant produced large design documents, but many of those earlier contents are not visible in the retained transcript. This is important because the final report package marks those earlier outputs as referenced but not fully recovered.
- The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in filenames. Instead, those details should live in metadata. This became part of the future build/package design.
- The key change came when the user decided that Codex could not read the entire conversation at once. **FACT:** The user said they would copy and paste the transcript with timestamps and would not edit it manually, but because Codex could not read the whole context at once, they would not bother asking Codex to compile a full book directly from the whole chat.
- The user provided a large `devspec/` file tree. It included top-level docs, engine, platform, render, audio, systems, game, UI, launcher, mods, tools, data, tests, and scripts. Then the user changed one important thing: **FACT:** they decided to skip the top-level `.txt` files because the original Markdown docs already existed in `/docs/...`.
- The game layer began with `g_core.h`, `g_core.cpp`, and `g_world.h`. The user then shifted to handoff/report work before `g_world.cpp` was produced. **FACT:** The next strict-order file is therefore `game/g_world.cpp.txt`.
- The final generated package contains seven report files and a ZIP archive. The latest user request asks for a human-readable explanation rather than another machine-readable packet. This current report is therefore the narrative version: it explains what happened, what mattered, and what should be remembered.
- FACT:** The whole chat revolves around the Dominium Game project. Dominium is described through its architecture: a deterministic, cross-platform simulation game with industrial, economic, logistics, climate, terrain, AI, research, and modding systems. The user was not merely asking for isolated code snippets. They were building a full software architecture.
- The most important conclusion is that determinism is central. Systems are repeatedly specified to avoid hidden randomness, OS timers, platform dependence, uncontrolled floating point, and runtime allocation during simulation ticks. The visible rationale is that the project needs replay, save/load, and likely lockstep multiplayer compatibility. This requirement affects nearly every generated spec.
- What remains uncertain is the exact final scope of all simulation systems. Many systems were described in ambitious terms, but not all details are final or internally consistent. The systems layer especially needs canonicalisation before coding.
- The Codex workflow is one of the most important topics. **FACT:** The user wanted to use Codex 5.1 Max to implement the project. Initially, the idea was that Codex would read a full transcript and generate a complete project book. That approach was later superseded because the user recognised that Codex could not read the whole context at once.
- The key later decision was to skip top-level `.txt` devspec files because original Markdown files already existed in `/docs/...`. The visible chat does not show the full content of those docs. They should be preserved as referenced artifacts, but their exact content is **UNCERTAIN / UNVERIFIED**.
- The user explicitly asked about localisation and whether UTF-8 Unicode should be used. The visible output and later specs established a clear direction: **FACT:** UTF-8 is canonical internally. At the same time, the project wants to preserve compatibility with retro platforms, so ASCII/ANSI/SFN fallbacks are part of the design.

## What Was Not Decided

- What remains uncertain is the exact final scope of all simulation systems. Many systems were described in ambitious terms, but not all details are final or internally consistent. The systems layer especially needs canonicalisation before coding.
- What remains uncertain is the current real-world status and capabilities of "Codex 5.1 Max." That is an external tool fact and requires verification before future use.
- The key later decision was to skip top-level `.txt` devspec files because original Markdown files already existed in `/docs/...`. The visible chat does not show the full content of those docs. They should be preserved as referenced artifacts, but their exact content is **UNCERTAIN / UNVERIFIED**.
- This affects `dlocale`, font rendering, platform path handling, data locale JSON files, mod APIs, UI, and documentation. The unresolved part is exactly how much retro support is actually feasible. Claims about old OSes, toolchains, SDL2, OpenGL, Direct3D, and macOS versions require external verification.
- A large portion of the chat consisted of producing specs for those files. Each spec was meant to tell Codex how to implement that file. The conclusion is that the repository architecture is broad but structured. The unresolved issue is that many later files remain pending.
- The unresolved issue is API consistency. Generated specs for memory and serialization are inconsistent across files, and some platform/render specs contain outdated or unverified external assumptions.
- The most important unresolved issue is duplication and contradiction. `dweather`, `dhydro`, and `dai_core` were generated in more than one form. The package does not choose a final version. A future assistant should not implement any of those blindly.
- The user decided to skip the top-level `.txt` files because original Markdown docs already exist in `/docs/...`. This decision is final for the current workflow, but it depends on those docs actually existing and being current. That is **UNCERTAIN / UNVERIFIED** because the docs were not inspected in this chat.
- The user explicitly required that the final handoff/report preserve facts, decisions, preferences, rejected options, unresolved issues, artifacts, and rationale. The user required labels for FACT, INFERENCE, UNCERTAIN / UNVERIFIED, and PROJECT-CONTEXT. The user required that assistant suggestions not be treated as user decisions unless accepted.
- All artifacts should feed into the future Project Spec Book only after uncertainty and contradictions are handled. The file-spec prompts are especially important, but they require API cleanup before implementation.
- The most important unresolved issue is canonicalisation. `dweather`, `dhydro`, and `dai_core` each have duplicate conflicting specs. A future assistant needs to compare the versions and either select one or merge them carefully.
- The next unresolved issue is core API consistency. `dmem` and `dserialize` are used inconsistently across generated specs. This must be fixed before coding.

## Ideas Rejected, Superseded, Or Deprioritised

- The Codex workflow is one of the most important topics. **FACT:** The user wanted to use Codex 5.1 Max to implement the project. Initially, the idea was that Codex would read a full transcript and generate a complete project book. That approach was later superseded because the user recognised that Codex could not read the whole context at once.
- The user made this decision directly. All components/packages and the complete game use major.minor.patch semantic versioning. Build numbers and dates do not go into filenames. They belong in metadata.
- This is the central workflow decision. The alternative was a giant transcript/book approach. It was superseded because Codex cannot read the whole conversation at once. The per-file prompt strategy makes the project modular and automation-friendly.
- Some decisions are explicitly not made. The chat generated multiple versions of certain specs. A future assistant must not pretend those conflicts are resolved. In particular, `dweather`, `dhydro`, and `dai_core` need canonicalisation.
- The first major superseded idea was the full transcript/book plan. The user originally imagined Codex reading the entire conversation and creating a complete book of volumes. That idea was reasonable because the conversation had accumulated a lot of context, but it was superseded when the user recognised Codex's context limitations. The replacement was per-file `.txt` specs.
- The second deprioritised idea was regenerating top-level `.txt` files. The original file tree included them, but the user later said top-level docs could be skipped because originals already existed in `/docs/...`. This should not be repeated unless those docs are missing or stale.
- The third rejected idea was putting build metadata in filenames. The user explicitly rejected this. Build metadata belongs in metadata, not filenames.
- These rejected paths matter because future assistants might otherwise re-suggest them. They should be preserved to prevent repeated work.
- The assistant-generated specs sometimes overreached or became inconsistent. The final report package therefore identifies not only what was generated, but also what needs correction. This is important: the generated specs are not final code. They are architecture drafts.
- The user explicitly required that the final handoff/report preserve facts, decisions, preferences, rejected options, unresolved issues, artifacts, and rationale. The user required labels for FACT, INFERENCE, UNCERTAIN / UNVERIFIED, and PROJECT-CONTEXT. The user required that assistant suggestions not be treated as user decisions unless accepted.

## What Future Work Came From It

- The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in filenames. Instead, those details should live in metadata. This became part of the future build/package design.
- The user then gave the "big task": create a set of `.txt` files, one for each file in the git directory, telling Codex how to implement it. These were not intended to be source files themselves. They were implementation-instruction files: requirements, prohibitions, dependencies, functions, declarations, and design constraints. This became the dominant workstream of the chat.
- After the spec-generation work, the user changed the task again: the chat was being retired. The user asked for an OC-1 discovery inventory, then a maximum-fidelity Context Transfer Packet, then a downloadable package with Markdown/YAML reports, then an in-chat reader version of that package. Those handoff tasks did not continue project design; they preserved the state of the chat.
- The conclusion was to create one `.txt` implementation-spec prompt per repository file. Each prompt would tell Codex how to implement that file without needing the entire conversation. This became the main practical output of the chat.
- What remains uncertain is the current real-world status and capabilities of "Codex 5.1 Max." That is an external tool fact and requires verification before future use.
- This is a formal packaging/build policy. It should feed into future build scripts, package manifests, release metadata, and possibly save/replay compatibility metadata.
- The most important unresolved issue is duplication and contradiction. `dweather`, `dhydro`, and `dai_core` were generated in more than one form. The package does not choose a final version. A future assistant should not implement any of those blindly.
- The user explicitly wanted Codex to help with implementation. This goal drove the conversation toward file-specific implementation prompts.
- INFERENCE:** The user wanted future assistants or Codex instances to continue without needing repeated explanations. This is inferred from the detailed transfer packet instructions.
- INFERENCE:** The user wanted the project to become structured enough to support both automated coding and future human review.
- The biggest changed goal was the Codex intake strategy. The earlier goal was to have Codex read the whole transcript and create a full book. The later goal was to make modular context files and per-file prompts.
- Another change was from generating project specs to preserving the chat. The final phase no longer aimed to produce Dominium source specs; it aimed to package this chat's knowledge.

## Important Artifacts

- `manifest`: `1`
- `markdown`: `1`
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
