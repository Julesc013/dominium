Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: needs_user_decision_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_synthesis
Promotion Status: not_promoted
Source Class: conversation_corpus_synthesis


# Needs User Decision v0

These raw candidates either touch blocked scope or frame unresolved future work. They require user or repo-authority review before any promotion.

## `PROMOTE-0001` - `advanced_simulation_infrastructure`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it.

## `PROMOTE-0005` - `app_runtime_platform_renderers`

- Classification: `blocked_by_current_queue`
- Blocked scopes: `gameplay`
- Reason: The claim touches currently blocked scope: gameplay.
- Claim: The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, and introducing gameplay shortcuts. **FACT:** authoritative logic remains in engine + game.

## `PROMOTE-0006` - `app_runtime_platform_renderers`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.

## `PROMOTE-0015` - `architecture_ui_providers`

- Classification: `blocked_by_current_queue`
- Blocked scopes: `provider_runtime`
- Reason: The claim touches currently blocked scope: provider_runtime.
- Claim: The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.

## `PROMOTE-0020` - `canonical_structure_and_framework`

- Classification: `blocked_by_current_queue`
- Blocked scopes: `provider_runtime`
- Reason: The claim touches currently blocked scope: provider_runtime.
- Claim: The final provider directory doctrine became service-first: `runtime/<service>/providers/<provider>/`, not `runtime/<vendor>/<service>/`. Provider choices belong in `release/profiles/` or `content/profiles/`, not app path names. External code belongs under `external/upstream/` or `external/vendor/`, but the repo should choose one convention.

## `PROMOTE-0024` - `Chronology_Celestial_Systems`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.

## `PROMOTE-0025` - `development_routes`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict determinism matters, whether replay or multiplayer are goals, whether modding matters, and what the actual game loop is. Until then, the kernel-first plan should be treated as a strong provisional proposal, not a final specification.

## `PROMOTE-0028` - `documentation_standards_readme`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions.

## `PROMOTE-0043` - `Dominium_Complete_Conversation`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still follows that contract, and finally broadening the question into a platform-engineering doctrine for portability, modularity, extensibility, reuse, future-proofing, and long-term compatibility.

## `PROMOTE-0049` - `dominium_full_conversation`

- Classification: `blocked_by_current_queue`
- Blocked scopes: `provider_runtime`
- Reason: The claim touches currently blocked scope: provider_runtime.
- Claim: A future assistant must understand that this chat is not simply about UI. It records the architecture for how Dominium should build itself: through contracts, commands, services, providers, documents, patches, modules, packs, apps, workspaces, diagnostics, evidence, AIDE, Codex, and eventually Workbench.

## `PROMOTE-0056` - `Domino_Dominium_Workbench`

- Classification: `blocked_by_current_queue`
- Blocked scopes: `provider_runtime`
- Reason: The claim touches currently blocked scope: provider_runtime.
- Claim: The central decision is that Workbench must not become semantic authority. Workbench is a surface over contracts, commands, services, documents, patches, providers, packs, modules, apps, artifacts, diagnostics, evidence, tests, and replay/proof. It is the richest human/agent interface over the system, but it must not bypass command, capability, refusal, validation, document, patch, or proof law.

## `PROMOTE-0057` - `Domino_Dominium_Workbench`

- Classification: `blocked_by_current_queue`
- Blocked scopes: `native_gui`
- Reason: The claim touches currently blocked scope: native_gui.
- Claim: The second central decision is that CLI, TUI, rendered GUI, OS-native GUI, and headless automation must be **projections of the same command/result/refusal/document/view spine**. A GUI button, a TUI hotkey, a CLI command, a headless JSON job, and a future OS-native widget action should route through the same command/service path and produce the same typed result, diagnostics, refusals, logs, and evidence.

## `PROMOTE-0065` - `Foundation_Workbench_Codex`

- Classification: `blocked_by_current_queue`
- Blocked scopes: `provider_runtime`
- Reason: The claim touches currently blocked scope: provider_runtime.
- Claim: The key conclusion was that Workbench is not the general module system; it is one consumer of the module/command/service/provider/pack/artifact system. Workbench must not call private tools directly. It must route through registered commands and typed results, diagnostics, refusals, views, and evidence.

## `PROMOTE-0069` - `Framework_Open_Source_Provider`

- Classification: `blocked_by_current_queue`
- Blocked scopes: `provider_runtime`
- Reason: The claim touches currently blocked scope: provider_runtime.
- Claim: The chat inspected `julesc013/dominium` and found evidence of existing abstractions such as system and graphics layers, stubs, and soft-backed backends. The finding was that raylib could fill concrete provider gaps without replacing the architecture. However, current repo facts are stale/uncertain and must be verified, especially the C17/C++17 vs C90/C++98 baseline contradiction.

## `PROMOTE-0075` - `Language_Platform_Architecture`

- Classification: `blocked_by_current_queue`
- Blocked scopes: `provider_runtime`
- Reason: The claim touches currently blocked scope: provider_runtime.
- Claim: Finally, the user pasted advice favoring C99 or C++11 due to raylib/SDL and legacy targets. The answer rejected a pivot. Raylib and SDL2 being C APIs only means provider boundaries should be C-callable; it does not force the whole engine or game to C99. The final recommendation remained C17 + C++17, with raylib/SDL2 treated as providers and with external deployment claims placed into the verification queue.

## `PROMOTE-0076` - `launcher_app_layer`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: Someone reading this report should understand one central thing: this chat is not about inventing new launcher features anymore. It is about preserving boundaries, making the launcher implementation explicit, and ensuring future work happens on top of verified code rather than vague architectural memory.

## `PROMOTE-0097` - `Portability_Assurance_Future_Proof`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.

## `PROMOTE-0113` - `testx_repox_governance`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: The user then asked whether the implementation was industry-accepted and what could be improved. The response framed the approach as closer to game engines, operating systems, and long-lived infrastructure than typical game development. The important conclusion was that the design was not exotic, but it was unusually rigorous for games.

## `PROMOTE-0120` - `UE6_Domino_Deterministic_Universe`

- Classification: `blocked_by_current_queue`
- Blocked scopes: `gameplay`
- Reason: The claim touches currently blocked scope: gameplay.
- Claim: Conclusion: machine gameplay must be designed as a scalable graph simulation, not as unrestricted physics.

## `PROMOTE-0121` - `ui_editor_tool_editor_planning`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.

## `PROMOTE-0123` - `ui_editor_tool_editor_planning`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical layout description, and the user accepted it as useful. Future work should inspect the bundles before claiming exact screenshot fidelity.

## `PROMOTE-0125` - `Universe_Explorer_Planning`

- Classification: `needs_user_decision`
- Blocked scopes: `none`
- Reason: The claim frames unresolved future work or a decision boundary.
- Claim: A major theme was that useful local inventions must become portable, standardized, industrialized, and institutionally adopted. The repo now has a Formalization Chain spec and Player Desire Acceptance Map that strongly preserve this. The future work is making this playable: drafting, measuring, testing, blueprinting, certifying, teaching, manufacturing, maintaining, and revising designs.
