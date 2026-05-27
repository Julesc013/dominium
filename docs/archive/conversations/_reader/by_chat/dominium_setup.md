Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/dominium_setup/`
Promotion Status: not_reviewed

# Dominium Setup Architecture and Handoff - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about designing, correcting, and preserving the **Dominium / Domino Setup system**: the installer, updater, verifier, rollback, repair, uninstall, packaging, and distribution layer for the larger Dominium project. The key point is that this was **not** a launcher UI chat, not an engine-design chat, and not a gameplay/simulation-design chat. It focused on the application-layer product called `setup/`, whose job is to install and maintain the rest of the software safely and deterministically.

The user's goal evolved over the conversation. At first, the discussion was broad and architectural: how should a cross-platform installer work for Windows, macOS, Linux, Steam/Epic, package managers, and legacy platforms? The user wanted a setup system that could support modern Windows through Visual Studio, Windows 9x through Watcom or similar legacy toolchains, macOS X and classic macOS, Linux package managers, Steam/Epic-style distribution, web installers, consoles, retro systems, offline installs, network installs, update checking, package customization, repair, uninstall, downgrade, and rollback. The goal was not just to make an installer executable; it was to define a **deployment control plane** with deterministic behavior, audit logs, reversible transactions, clean installed-state ownership, and long-term survivability.

As the chat progressed, the discussion moved from early directory sketches to a much stricter canonical repository model. Earlier ideas used structures like `setup/adapters/`, `setup/packaging/`, `core/source/`, and platform-specific subtrees. Those were useful exploration steps, but they were later **superseded**. The user introduced a locked repository structure with top-level products such as `engine/`, `game/`, `client/`, `server/`, `launcher/`, `setup/`, `tools/`, `libs/`, `schema/`, `docs/`, `ci/`, `sdk/`, and `legacy/`. Under that model, the setup product has a fixed layout: `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages`, `setup/platform`, `setup/tests`, and `setup/ui`. That canonical structure became the ground truth.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/dominium_setup/dominium_setup_handoff__human_readable_chat_report.txt`.

## What Was Decided

- Near the end, the chat shifted into preservation mode. The user asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat reader version of that package. Those outputs preserved the decisions, tasks, constraints, artifacts, rejected options, and verification queue for future assistants or aggregation into a larger Project Spec Book.
- These directory trees were not final, but they mattered because they exposed the user's preference for simple, shallow, logical structures and native IDE workflows that do not become the source of truth.
- The user later asked where to create Visual Studio and Xcode apps after opening the repo as a folder. The assistant advised that Visual Studio and Xcode projects should be generated through CMake, not hand-authored or treated as authoritative source files. This decision became consistent with later Codex prompts.
- Finally, the user retired the chat and asked for a maximum-fidelity context transfer packet. The assistant produced one. The user then asked for a downloadable shareable report package. The assistant created Markdown/YAML/report files and a ZIP. The user then asked for an in-chat reader version of the package, and the assistant rendered the package contents directly into the conversation.
- The central topic was the setup system itself. It was discussed because the user needed a robust installer/updater/verifier capable of supporting many platforms, distribution channels, legacy environments, package managers, and future update flows.
- FACT: The setup system was repeatedly defined as the only component allowed to install files, modify system/installation state, own installed-file metadata, repair installs, verify artifacts, uninstall, downgrade, upgrade, and roll back. This is the most important architectural rule from the chat.
- The reason this mattered is that Dominium / Domino is a long-lived deterministic system. If launchers, engines, tools, package scripts, or platform installers each had their own install logic, the result would be untestable, non-deterministic, and difficult to audit. The setup system needed to be a central authority so that installed state, ownership, rollback, and verification all remain coherent.
- What remains uncertain is the actual current implementation state in the repository after the applied Codex prompts. The design is clear, but the repo must still be inspected.
- FACT: The final canonical repository structure has top-level products such as `engine/`, `game/`, `client/`, `server/`, `launcher/`, `setup/`, `tools/`, `libs/`, `schema/`, `docs/`, `ci/`, `sdk/`, and `legacy/`.
- FACT: The final canonical setup layout uses `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages`, `setup/platform`, `setup/tests`, and `setup/ui`.
- FACT: The assistant recommended C/C++ and Visual Studio Desktop Development with C++ for setup execution. The reasoning was based on the user's stated requirements: legacy Windows, Windows 9x support, macOS/Linux portability, offline installs, stable ABI, deterministic behavior, and long-term survivability.
- FACT: The target state was that engine should contain only engine-owned public headers under `engine/include/domino`, engine modules, render code, tests, and CMake. Cross-product contracts should move to `libs/contracts/include/dom_contracts`.

## What Was Not Decided

- FACT: The setup system was repeatedly defined as the only component allowed to install files, modify system/installation state, own installed-file metadata, repair installs, verify artifacts, uninstall, downgrade, upgrade, and roll back. This is the most important architectural rule from the chat.
- What remains uncertain is the actual current implementation state in the repository after the applied Codex prompts. The design is clear, but the repo must still be inspected.
- FACT: The final canonical setup layout uses `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages`, `setup/platform`, `setup/tests`, and `setup/ui`.
- The unresolved part is whether the actual repository now matches this canonical layout.
- UNCERTAIN / UNVERIFIED: Exact Visual Studio 2026 behavior and toolchain details should be verified in the current environment before relying on them.
- UNCERTAIN / UNVERIFIED: The user stated the prompts were applied, but this chat did not show the final repository tree or build results.
- UNCERTAIN / UNVERIFIED: The actual schema files under `schema/setup/` need to be checked.
- Several goals remain unresolved because the actual repo was not inspected here. We do not know whether the applied Codex prompts fully succeeded, whether setup builds, whether schemas exist, whether `libs/contracts` is complete, or whether setup/launcher CLI smoke tests pass.
- FACT: The chat repeatedly established that setup is the only component allowed to install, upgrade, downgrade, repair, verify, uninstall, roll back, and own installed-file metadata.
- FACT: The final setup layout is `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages`, `setup/platform`, `setup/tests`, and `setup/ui`.
- This affects future application work, but some exact implementation paths remain unverified.
- Another tradeoff was between broad future support and current implementation scope. The architecture allows legacy platforms, storefronts, and offline/online acquisition, but many implementation details remain unverified. The chat preserved those as goals without pretending they are already implemented.

## Ideas Rejected, Superseded, Or Deprioritised

- Near the end, the chat shifted into preservation mode. The user asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat reader version of that package. Those outputs preserved the decisions, tasks, constraints, artifacts, rejected options, and verification queue for future assistants or aggregation into a larger Project Spec Book.
- These directory trees were not final, but they mattered because they exposed the user's preference for simple, shallow, logical structures and native IDE workflows that do not become the source of truth.
- The user then gave a strict system-role prompt saying the repository had undergone a major structural refactor and that the filesystem was now canonical ground truth. This superseded earlier structures. The locked top-level products became:
- This became a decisive turning point. Earlier `setup/adapters`, `setup/packaging`, and `core/source` structures became historical and superseded. The assistant amended Plan S to match the new canonical structure and later produced an authoritative Phase 2 directory tree under that model.
- This prompt is important because it bridges the gap between architectural planning and implementation cleanup. It says: do not redesign setup; finish, document, and align what exists.
- Initially, assistant and user explored structures with `setup/core`, `setup/adapters`, `setup/packaging`, `tests`, and `docs`. The user suggested refinements like `winnt`, `macosc`, and `source`. Later, those ideas were superseded when the user introduced a canonical repository structure.
- Near the end, the user pasted broader application-layer canon. It stated that applications are orchestration shells, content-agnostic, rule-agnostic, authority-agnostic, and must not contain gameplay logic. CLI is canonical. GUI and TUI are views over the same command graph. UI is data via UI IR. Tools are read-only by default. RepoX/TestX and BUILD-ID-0 govern metadata, validation, changelogs, and releases.
- This matters because the user is building a large project across multiple chats and wants to later combine old-chat reports into a full Project Spec Book. This chat contributes setup architecture, canonical layout history, repository enforcement context, and warnings about superseded options.
- Several goals remain unresolved because the actual repo was not inspected here. We do not know whether the applied Codex prompts fully succeeded, whether setup builds, whether schemas exist, whether `libs/contracts` is complete, or whether setup/launcher CLI smoke tests pass.
- This decision superseded earlier directory trees. It was made because the repository had undergone a larger refactor, and the user explicitly said the filesystem was fixed ground truth.

## What Future Work Came From It

- Near the end, the chat shifted into preservation mode. The user asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat reader version of that package. Those outputs preserved the decisions, tasks, constraints, artifacts, rejected options, and verification queue for future assistants or aggregation into a larger Project Spec Book.
- The first major input was a detailed master prompt for the **Dominium / Domino Setup & Installation System**. It said this chat was about setup, installation, packaging, distribution, and uninstallation across supported platforms. It explicitly excluded launcher UI work. The setup system was described as a deterministic deployment control plane, not a simple GUI wizard or a store/DRM mechanism.
- The assistant responded with **Phase 1: Setup Core Architecture**, proposing modules such as manifest parsing, resolution, planning, transaction execution, filesystem/path policy, installed-state, logging, and a platform interface. This was the first conceptual baseline.
- The user then asked for a "plan of plans" called **Plan S**, with subplans S-1, S-2, S-3, and so on. The assistant produced a structured setup roadmap. It covered governance, setup core architecture, manifest schema, installed-state schema, transaction engine, filesystem policy, audit logging, CLI, Windows/macOS/Linux adapters, Steam integration, distribution pipeline, side-by-side upgrades, tests, and documentation.
- At that stage, the plan was still mostly abstract and platform-oriented. It was useful because it separated the work into durable phases, but later repository changes made some of its directory assumptions obsolete.
- The user later asked where to create Visual Studio and Xcode apps after opening the repo as a folder. The assistant advised that Visual Studio and Xcode projects should be generated through CMake, not hand-authored or treated as authoritative source files. This decision became consistent with later Codex prompts.
- The user then gave a strict system-role prompt saying the repository had undergone a major structural refactor and that the filesystem was now canonical ground truth. This superseded earlier structures. The locked top-level products became:
- This became a decisive turning point. Earlier `setup/adapters`, `setup/packaging`, and `core/source` structures became historical and superseded. The assistant amended Plan S to match the new canonical structure and later produced an authoritative Phase 2 directory tree under that model.
- The assistant then produced a Phase 3 schema plan under the new assumptions, covering install plan schemas, installed-state schemas, verification reports, audit logs, and the schema-only setup/launcher handoff.
- This prompt is important because it bridges the gap between architectural planning and implementation cleanup. It says: do not redesign setup; finish, document, and align what exists.
- The central topic was the setup system itself. It was discussed because the user needed a robust installer/updater/verifier capable of supporting many platforms, distribution channels, legacy environments, package managers, and future update flows.
- What remains uncertain is the actual current implementation state in the repository after the applied Codex prompts. The design is clear, but the repo must still be inspected.

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
