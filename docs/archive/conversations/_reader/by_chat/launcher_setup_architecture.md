Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Launcher_Setup_Architecture/`
Promotion Status: not_reviewed

# Dominium Launcher and Setup Architecture - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was about designing the **Dominium launcher, setup system, runtime integration model, and surrounding user-facing infrastructure**. It began from a broad architectural philosophy for the Dominium project: keep the simulation core deterministic, boring, portable, and C89; put explicit APIs between layers; use versioned formats; make mods data-first; and prevent tools, launcher, and runtime code from drifting into separate incompatible implementations. From that starting point, the conversation progressively narrowed into a concrete system design for how users install, launch, configure, mod, supervise, and manage Dominium.

The central problem was not "how do we open a game window?" It was how to build a long-lived ecosystem around the game without corrupting the deterministic engine or creating hidden coupling. The launcher needed to be powerful enough to manage multiple instances, installs, mods, settings, logs, profiles, news, changelogs, and future ecosystem features, while the game itself still had to run perfectly well without it. The setup system likewise needed to support normal users, portable users, system administrators, CI, and custom deployments without forcing every code path into a single fragile installer.

A major early conclusion was that Dominium should use **one codebase but multiple binaries**. The assistant proposed, and the user continued from, the idea that setup, launcher, and game should be separate executables rather than one monolithic executable. The visible rationale was practical: setup may need elevated privileges, the launcher is a long-running management application, and the game/runtime must remain performance- and determinism-sensitive. Separate binaries preserve privilege boundaries and crash isolation while still sharing libraries, manifests, and conventions.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__human_readable_chat_report.txt`.

## What Was Decided

- The chat also produced multiple Codex work-order prompts and finally a downloadable report package. Those artifacts are useful, but the substance is the architecture: keep engine deterministic, keep setup/launcher/runtime boundaries explicit, make the launcher optional and modular, use a strong process/instance model, and now implement the launcher over dsys/dgfx rather than ad hoc platform UI stacks.
- FACT:** The user's initial architecture text emphasized:
- The assistant responded by stress-testing this philosophy. It pointed out determinism risks around Lua, plugins, time sources, and ABI details, and suggested more explicit contracts for file headers, TLV sections, runtime CLI capabilities, plugin exported symbols, and setup/launcher boundaries. These were assistant proposals, not all user-stated decisions, but the user continued building on that direction.
- The next important refinement was the user's explicit statement that the launcher should be capable of supervising, but the game must always run perfectly fine with no launcher. This prevented the design from turning into a launcher-dependent ecosystem.
- INFERENCE:** The user accepted this direction by continuing the conversation and later asking for the entire system to be detailed. However, not every proposed ABI field should be treated as final until implemented or confirmed.
- The user then requested a maximum-fidelity Context Transfer Packet, followed by a final downloadable report package, followed by an in-chat reader version of that package. The assistant generated the package and then rendered its structured contents in chat.
- Uncertainty:** The final language boundary for setup remains unresolved after the later C89/dsys/dgfx launcher direction.
- Conclusion reached:** Launcher integration is optional and additive. Runtime binaries must not require launcher metadata.
- Uncertainty:** Accounts/social/wiki/forum/direct messaging are future-facing and were not converted into the final five-tab implementation plan.
- The user wanted setup to work with defaults or fully customized deployments. The assistant proposed a central setup configuration model with defaults, CLI overrides, config/answer files, and non-interactive behavior.
- Conclusion reached:** Setup must have both simple default flows and fully explicit flows.
- The user fixed the launcher's tabs as News, Changes, Mods, Instances, and Settings. The user also made clear each tab must support full interaction.

## What Was Not Decided

- Uncertainty:** The exact repository layout and existing implementation were not inspected in this chat.
- Uncertainty:** The final language boundary for setup remains unresolved after the later C89/dsys/dgfx launcher direction.
- Uncertainty:** The exact mapping into runtime binaries remains unverified.
- Uncertainty:** Accounts/social/wiki/forum/direct messaging are future-facing and were not converted into the final five-tab implementation plan.
- Uncertainty:** Earlier setup designs used JSON manifests. Later dsys/dgfx architecture leaned toward TLV `.dmeta` files.
- Uncertainty:** Actual plugin ABI details and dynamic loading support depend on dsys/repo APIs.
- Uncertainty:** Actual dsys/dgfx APIs were not inspected.
- Conclusion reached:** This chat is now documented and can be merged later, but with caveats.
- INFERENCE:** The user wanted to avoid later assistant confusion by preserving rejected options, uncertainties, and changes of direction.
- The unresolved goals are mostly implementation-definition questions:
- The main assumption throughout is that the underlying project either already has, or will have, the shared libraries and platform abstractions described. That assumption is unverified in this chat.
- The user wants strict engineering tone, detailed reasoning, and preservation of uncertainty. In this specific request, the user asked for prose rather than a register dump.

## Ideas Rejected, Superseded, Or Deprioritised

- Conclusion reached:** Launcher integration is optional and additive. Runtime binaries must not require launcher metadata.
- This was later partly superseded by the dsys/dgfx model, but the separation remains conceptually useful.
- INFERENCE:** The user wanted to avoid later assistant confusion by preserving rejected options, uncertainties, and changes of direction.
- Affects:** Every later system. Launcher and setup must not call into engine internals.
- This was considered when the user asked whether setup, launcher, and game could be one. The assistant rejected it as the default because it mixes privileges and responsibilities. Setup may require admin/system changes; launcher should be a normal-user supervisor; the game should be independent and runtime-focused.
- When discussing CLI and headless operation, the assistant argued against launching independent OS console windows by default. The reason was that they break centralized log aggregation and do not generalize to Linux/mac text-only environments, SSH, DOS, or CP/M.
- This remains rejected as the default, though an explicit external-console/debug option could still be useful.
- The user explicitly rejected this by requiring direct executable running and no-launcher operation. This is final unless the user reverses it.
- This was rejected because it violates the deterministic engine boundary. The launcher should read manifests/metadata and communicate with runtimes through explicit contracts, not inspect simulation internals.
- This became superseded by the latest dsys/dgfx direction. Earlier ideas involving direct GUI/TUI libraries are no longer the active launcher path. The launcher should render through dgfx and receive platform/input/process services through dsys.

## What Future Work Came From It

- The chat also produced multiple Codex work-order prompts and finally a downloadable report package. Those artifacts are useful, but the substance is the architecture: keep engine deterministic, keep setup/launcher/runtime boundaries explicit, make the launcher optional and modular, use a strong process/instance model, and now implement the launcher over dsys/dgfx rather than ad hoc platform UI stacks.
- The user asked how many prompts would be needed for Codex to implement the system. The assistant recommended four main prompts:
- An optional fifth prompt was suggested for runtime CLI/capabilities. The user then asked for the prompts one by one, and the assistant generated them. These prompts were detailed and implementation-oriented, but they reflected the earlier C++98/shared-library approach.
- This is the most important change of direction in the chat. Earlier prompts remain useful historical material, but the latest launcher implementation direction is dsys/dgfx.
- This came up because the user wanted Codex and future implementation work to avoid hidden coupling and future incompatibilities. The assistant expanded the idea into repo layout, file format patterns, CLI contracts, plugin ABIs, and migration/testing expectations.
- Uncertainty:** Accounts/social/wiki/forum/direct messaging are future-facing and were not converted into the final five-tab implementation plan.
- This was the late major shift. The user provided a detailed new prompt stating that all dsys and dgfx backends exist and that the launcher should use them.
- INFERENCE:** The user wanted a future-proof architecture that Codex could implement in stages without repeatedly re-deciding the system design.
- INFERENCE:** The user wanted the outputs to become source material for a future Project Spec Book.
- At first, the goal was general architecture alignment. It then became user-facing launcher behavior. It then expanded into install/setup and all-in-one launcher management. It then became staged Codex implementation prompts. Finally, it shifted to a specific C89 dsys/dgfx launcher architecture.
- Affects:** UI structure, module order, implementation prompts.
- The user's philosophy favors versioned TLV files. Earlier generated prompts used JSON for practical manifest/config examples. The dsys/dgfx architecture then referenced `.dmeta` TLV-style files.

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
