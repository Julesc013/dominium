Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/launcher_app_layer/`
Promotion Status: not_reviewed

# Dominium Launcher Application-Layer Handoff - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about turning the **Dominium Launcher** from a broad architectural idea into a properly bounded, enforceable, application-layer product inside the larger **Dominium / Domino** project. The conversation began with a practical launcher question: whether the latest post-Plan 8 system could support a **single cross-platform launcher** with a **common codebase**, **native OS elements**, and **little or no renderer**, similar in spirit to older fast, native-feeling Minecraft launchers. From there, the discussion grew into a much larger effort to define where launcher code belongs, what it is allowed to do, how it interacts with setup, engine, game, tools, packs, UI, CMake, VS2026, RepoX, TestX, and future documentation.

The user's underlying goal was not just "make a launcher." The goal was to prevent the launcher from becoming an architectural dumping ground. The launcher needed to be modular, extensible, native-feeling where appropriate, shared across platforms where possible, and deeply integrated with installed-state manifests, mods, packs, profiles, compatibility checks, launch flows, diagnostics, and future UI systems. At the same time, it had to respect hard project boundaries: the engine must remain pure, setup must remain the only installation/mutation authority, and applications must never contain gameplay logic or mutate authoritative simulation state.

Early in the conversation, some ideas were explored that later became obsolete. For example, there was an early suggestion that Visual Studio and Xcode projects could be hand-authored as canonical shells. That was later superseded by the user's applied Codex prompts, which made **CMake the authoritative build system** and required Visual Studio projects to be generated through CMake presets. There was also an early standalone `dominium-launcher/` directory tree with `core/source`, `adapters`, `schemas`, and `cli`. That was later replaced by a product-first monorepo structure where `launcher/` is one top-level product alongside `engine/`, `game/`, `client/`, `server/`, `setup/`, `tools/`, `libs/`, and `schema/`.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/launcher_app_layer/dominium_launcher_app_layer_handoff__human_readable_chat_report.txt`.

## What Was Decided

- Someone reading this report should understand one central thing: this chat is not about inventing new launcher features anymore. It is about preserving boundaries, making the launcher implementation explicit, and ensuring future work happens on top of verified code rather than vague architectural memory.
- There was also an early suggestion to create a `DUI` facade, a Dominium UI abstraction, to support native widgets and fallback rendering. This idea was useful as a conceptual stepping stone but was not ultimately locked as a final requirement in the form originally suggested. Later application-layer canon emphasized **UI IR**, **command graphs**, and **binding validation** rather than a specific `DUI` facade design.
- This phase mattered because it framed the launcher not as a menu program but as a **control plane** for installed products, packs, profiles, compatibility, and launch contracts. However, later canon tightened the permitted communication routes: cross-product communication must go through `schema/` and `libs/contracts`, not arbitrary plugin conventions.
- This later became one of the clearest examples of a superseded path. The user subsequently pasted applied Codex prompts that explicitly required CMake to generate the Visual Studio solution/projects and stated that hand-written `.vcxproj` files must not be the authoritative build. Therefore, all earlier "manual IDE projects as canonical" advice is no longer current.
- That product-first direction was then finalized by a later user prompt defining the canonical repo structure.
- The second was a final purity and contract-ownership repair prompt. It required engine purity, moved cross-product contracts to `libs/contracts/include/dom_contracts`, evicted non-engine content from `engine/`, and hardened sanity scripts.
- This changed the correct future behavior. The next assistant must not redesign. It must implement, audit, maintain, document, verify, and harden.
- The user asked for a maximum-fidelity Context Transfer Packet. That packet was produced. Then the user asked for a final downloadable report package, which was created. Then the user asked to inspect that package in-chat, and an in-chat reader version was produced.
- FACT:** The user wanted one common launcher codebase, native OS elements, and minimal rendering.
- A central boundary was the separation between setup and launcher.
- FACT:** Setup is the only install mutation authority.
- The final application canon later phrased this as: **CLI is canonical; GUI/TUI are views over the same command graph.

## What Was Not Decided

- These prompts matter because they superseded earlier advice. They also created a new practical priority: verify that the applied prompts actually succeeded.
- This changed the correct future behavior. The next assistant must not redesign. It must implement, audit, maintain, document, verify, and harden.
- This matters because it prevents platform-specific drift. If CLI has `verify`, GUI must not implement a different hidden version of `verify`. If GUI has a pack enable flow, it should map to the same command/intent as CLI and TUI.
- The final purity prompt required those to be moved or quarantined. However, actual repo success remains unverified in this chat.
- The important change is that the conversation moved from "What architecture should we use?" to "Architecture is locked; how do we verify and harden the implementation?"
- The largest unresolved goal is verifying the actual repo. The user stated that two Codex prompts were applied, but this chat did not independently verify the filesystem, build, tests, scripts, or launcher docs.
- Another unresolved goal is confirming whether the launcher hardening prompt has been applied.
- A third unresolved goal is confirming whether command graph, UI IR, binding validation, zero-pack tests, RepoX changelog display, and BUILD-ID mismatch refusal are implemented.
- This decision depends on CMake and script enforcement. It remains operationally unverified until the current repo is checked.
- The launcher may expose repair or verify entry points in the sense that it can invoke setup through a contract, but it must not perform install mutation itself. This separation protects auditability and prevents hidden mutation.
- This decision reflects the state of the project: after major refactors and applied prompts, the next risk is planning on assumptions. The correct move is to audit, document, verify, and harden the current launcher implementation.
- stale or unverified repository assumptions,

## Ideas Rejected, Superseded, Or Deprioritised

- This later became one of the clearest examples of a superseded path. The user subsequently pasted applied Codex prompts that explicitly required CMake to generate the Visual Studio solution/projects and stated that hand-written `.vcxproj` files must not be the authoritative build. Therefore, all earlier "manual IDE projects as canonical" advice is no longer current.
- These prompts matter because they superseded earlier advice. They also created a new practical priority: verify that the applied prompts actually succeeded.
- This changed the correct future behavior. The next assistant must not redesign. It must implement, audit, maintain, document, verify, and harden.
- The future connection is straightforward: keep the launcher core common, but allow platform-specific native shells under `launcher/platform/...`. Do not put business logic in those shells.
- This matters because it prevents platform-specific drift. If CLI has `verify`, GUI must not implement a different hidden version of `verify`. If GUI has a pack enable flow, it should map to the same command/intent as CLI and TUI.
- The engine must not include launcher, setup, tools, or `dom_contracts`. It must export only engine public API under `engine/include/domino`. Earlier contamination examples included `engine/include/dsu`, `engine/include/dui`, `engine/launcher_core_launcher`, `engine/setup_core_setup`, `engine/source`, and `engine/external/xxhash`.
- Launcher must display generated changelogs, warn about incompatibilities, and refuse mismatches loudly. It must not manually edit changelogs or invent compatibility defaults.
- The decisions below are not all equal. Some are user-locked canon. Some are assistant recommendations that were later accepted indirectly by the user's framing. Some are superseded. I will label them carefully.
- The launcher may expose repair or verify entry points in the sense that it can invoke setup through a contract, but it must not perform install mutation itself. This separation protects auditability and prevents hidden mutation.
- FACT:** The later application canon states UI must be defined via UI IR/declarative layer and must not embed business logic.

## What Future Work Came From It

- Someone reading this report should understand one central thing: this chat is not about inventing new launcher features anymore. It is about preserving boundaries, making the launcher implementation explicit, and ensuring future work happens on top of verified code rather than vague architectural memory.
- The user started by asking whether the latest system, after Plan 8, could support a common launcher for all operating systems with one shared codebase, native OS elements, and minimal rendering. The user attached several screenshots of older Minecraft launchers as visual examples and referenced a Plan 8 prompt file and a repo archive.
- The user then asked how to make the entire system more modular and extensible, especially with existing systems, mods, and packs. The answer proposed a data-first approach: facades, registries, versioned contracts, TLV/schema-based manifests, declarative settings, pack tasks, and rare executable plugins only when unavoidable.
- This phase mattered because it framed the launcher not as a menu program but as a **control plane** for installed products, packs, profiles, compatibility, and launch contracts. However, later canon tightened the permitted communication routes: cross-product communication must go through `schema/` and `libs/contracts`, not arbitrary plugin conventions.
- The response executed Phase 1 of that prompt and described the launcher core as a deterministic control-plane library. This included modules like manifest parsing, discovery, catalog building, profile policy, integrity checks, resolution, launch planning, execution, and audit logging. It also defined host service vtables, opaque handles, deterministic ordering rules, error models, and safety assumptions.
- That Phase 1 answer remains useful, but only after being rebased into the later canonical repo structure.
- This later became one of the clearest examples of a superseded path. The user subsequently pasted applied Codex prompts that explicitly required CMake to generate the Visual Studio solution/projects and stated that hand-written `.vcxproj` files must not be the authoritative build. Therefore, all earlier "manual IDE projects as canonical" advice is no longer current.
- Later, the user objected that `source` subdirectories inside top-level source directories felt counterintuitive and asked about future tools and components beyond launcher, setup, and game. This led to the product-first model: top-level directories should represent long-lived products, not layers.
- That product-first direction was then finalized by a later user prompt defining the canonical repo structure.
- The user supplied an authoritative prompt stating that the repo had undergone a major structural refactor and the filesystem was now canonical. This was a turning point.
- This prompt also locked dependency rules: launcher may depend on `libs/`, engine public API, game metadata/launch contracts only, schema, and contracts. It may not depend on setup internals, engine internals, or tools internals.
- The user later pasted two large Codex prompts that had already been applied.

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
