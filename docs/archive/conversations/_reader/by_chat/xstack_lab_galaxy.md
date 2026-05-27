Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/xstack_lab_galaxy/`
Promotion Status: not_reviewed

# Dominium XStack and Lab Galaxy Handoff - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about turning a very large, complex Dominium development conversation into a stable, reusable handoff, while preserving the architectural decisions and operational context needed to continue work without re-explaining everything. The conversation sat at the intersection of three big themes: **Dominium / Domino as a deterministic universe simulation/game**, **XStack as a portable agentic development and governance suite**, and **the reported completion of a 13-prompt "Lab Galaxy" substrate in a later chat**.

FACT: The user is building Dominium / Domino, a deterministic universe simulation/game project. The project doctrine throughout the chat emphasized determinism, replayability, process-only mutation, named RNG streams, law-governed authority, and a strict separation between **TruthModel**, **PerceivedModel**, and **RenderModel**. Domino is treated as the deterministic engine layer, while Dominium is the game/application layer. The system is intended to support long-term ambitions like galaxy-scale navigation, Sol and Earth detail, survival gameplay, modular realism packs, future multiplayer/SRZ scaling, and even speculative domains like biology, chemistry, psychology, magic, and social systems - but always through modular packs, solver tiers, budgets, and law/profile contracts rather than hardcoded one-off systems.

FACT: A major emotional and practical driver of the conversation was the user's frustration with agentic development failing on mechanical blockers. Earlier in the overall project, Codex runs had repeatedly stopped at entry gates, missing tool paths, RepoX/TestX/AuditX failures, or trivial automation issues. The user explicitly did not want future assistants to ask "Do you want me to fix this?" when the answer was obviously yes. That frustration led to a doctrine that mechanical failures should be repaired autonomously, while only genuinely semantic or architectural ambiguities should require escalation. This became the philosophical basis for UAEP-style prompt prefixes, ControlX, and the broader XStack governance layer.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, release, timekeeping, tooling, ui, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/xstack_lab_galaxy/dominium_xstack_lab_galaxy_handoff__human_readable_chat_report.txt`.

## What Was Decided

- and XStack must serve development rather than development serving XStack.
- After the transcript appeared, the user asked for a maximum-fidelity Context Transfer Packet. The assistant produced one, with sections such as workstreams, decisions, tasks, constraints, open questions, risks, artifacts, and verification queue. Then the user asked to turn that into a downloadable report package. The assistant created Markdown/YAML files and a ZIP archive.
- Finally, the user asked not for another package, but for an in-chat reader version of the package. The assistant rendered a structured in-chat reader. The user then asked for this current response: a human-readable, intuitive narrative report.
- The final state of the conversation is therefore not "we are ready to code the next feature." It is: **we have a large handoff/report package that captures the state, but the next real action is repository verification and consistency audit.
- The conclusion was that Dominium's architecture must preserve determinism, replayability, epistemic boundaries, and modularity. This remains a binding direction, but actual repository implementation must still be verified.
- XStack became a central topic because the user needed reliable autonomous development. It was not just a testing layer; it was a development control substrate. RepoX enforces invariants, TestX proves behavior, AuditX detects drift, ControlX orchestrates, PerformX monitors budgets/performance, CompatX handles schema migration, SecureX handles trust/security, and gate/tools/xstack/run provide execution surfaces.
- The key conclusion was that XStack must be **portable and removable**. It should be possible to use XStack in other projects or remove it from Dominium without breaking runtime. This is still one of the biggest constraints and must be verified.
- The conclusion was that docs should be layered: README for accessibility; architecture docs for technical explanation; canon/glossary/contracts for binding doctrine. The 13-prompt transcript reports that docs/canon and many architecture/contract docs were created, but this must be verified.
- The chat repeatedly returned to modes: survival, hardcore, creative, lab, observer, spectator, editor, godmode, sandbox. The key decision was that "modes" should not exist as code branches. They should be human-facing labels for combinations of profiles and parameters.
- The final phase was about preserving this chat for future use. The user first requested a maximum-fidelity Context Transfer Packet, then a downloadable report package, then an in-chat reader, and finally this human-readable narrative report. The goal was to make the chat reusable for future assistants and later master Project Spec Book construction.
- INFERENCE: The user likely wants to resume productive development after verifying the substrate. The next likely feature area is survival or Lab Galaxy refinement, but the user has not made a final decision in this visible chat.
- FACT: The decision to avoid hardcoded modes was accepted repeatedly. The user and assistant discussed survival, hardcore, creative, observer, lab, spectator, editor, godmode, and sandbox. The conclusion was that code should not contain `survival_mode`, `creative_mode`, or similar toggles. Instead, the system should use profiles and law/parameter bundles.

## What Was Not Decided

- But this chat did not verify the repository. That became one of the most important unresolved issues.
- This is one of the most important outputs associated with this chat, but it is also one of the most uncertain because it is user-reported from another chat and not verified directly here. The user explicitly wanted it audited for completion and consistency.
- INFERENCE: The user also wanted to prevent future assistants from flattening nuance. They repeatedly asked for maximum fidelity, uncertainty labels, rejected options, contradictions, and rationale. This implies a strong preference for preserving complexity rather than oversimplifying.
- INFERENCE: The user likely wants to resume productive development after verifying the substrate. The next likely feature area is survival or Lab Galaxy refinement, but the user has not made a final decision in this visible chat.
- 4. From documentation to verifying a new 13-prompt substrate.
- The biggest unresolved goal is verifying the actual repository. The package says what was reported, but not what is proven. Another unresolved goal is deciding what comes next: survival, Lab Galaxy UX, distributed SRZ, or documentation polish.
- The main assumption behind all of this is that the repo can actually enforce these contracts. That remains unverified in this chat.
- The best next step is to verify the actual repository state. This matters because the long 13-prompt transcript is not proof. The user explicitly does not know whether everything was truly implemented.
- Because the user cares about XStack portability, the new assistant should verify that runtime can build/run without `tools/xstack` and that engine/game/client/server do not import or depend on it.
- FACT: The user asked for FACT / INFERENCE / UNCERTAIN labels.
- This matters because future work depends on whether the 13-prompt changes are committed, pushed, or still local. The transcript reports a clean branch ahead by 10 commits, but this chat did not verify it.
- Before merging into a master spec, the aggregator should preserve uncertainty and verify the actual repository.

## Ideas Rejected, Superseded, Or Deprioritised

- INFERENCE: The user also wanted to prevent future assistants from flattening nuance. They repeatedly asked for maximum fidelity, uncertainty labels, rejected options, contradictions, and rationale. This implies a strong preference for preserving complexity rather than oversimplifying.
- FACT: The user explicitly said they wanted XStack to be a portable agentic development suite that could be removed with no impact on code/data/runtime. This decision is foundational. XStack can validate the repo, but runtime must not depend on it.
- The alternative - embedding XStack into game/engine runtime - was rejected because it would destroy portability and contaminate production code.
- FACT: The user rejected verification that takes hours during local/agentic development. The solution was a stratified verification model: FAST for normal iteration, STRICT for structural checks, FULL/FULL_ALL for deeper or release-like checks. The visible rationale was that governance should behave like an incremental compiler, not a CI system.
- FACT: The user asked about many realism demands: accurate skies, day/night, weather, climate, trees, animals, diseases, anatomical injury, arbitrary crafting, and performance limits. The conclusion was that these should be supported by domain packs, solver tiers, affordance graphs, budget/fidelity policies, observation kernels, and refusal contracts. Global full-detail simulation everywhere was rejected.
- This idea was rejected because it would create brittle code branches. It was considered only because normal games often use "Survival Mode," "Creative Mode," and similar labels. The final architecture allows those labels for users but not as code logic.
- This was rejected after the user experienced huge delays. Full checks were too expensive and made autonomous development impractical. The replacement was FAST/STRICT/FULL with caching and sharding.
- This was rejected because the user wants XStack to be portable and removable. XStack should validate and orchestrate development, but engine/game/client/server should not need it to run.
- This was rejected because README should be accessible. Deep doctrine belongs in canon/architecture docs. This is final for documentation UX.
- This was deprioritised, not permanently rejected. The concern was deterministic complexity. The preferred early approach is a session restart boundary for changing experiences/laws.

## What Future Work Came From It

- That problem drove much of the XStack discussion. The assistant and user discussed how to prevent future agents from treating old or bad prompts as literal stop conditions. This led to principles such as:
- prompts are untrusted input,
- The conversation then focused heavily on XStack. The user wanted RepoX, TestX, AuditX, ControlX, PerformX, CompatX, and SecureX to be robust, modular, extensible, and fast. The assistant helped plan or generate many prompts around this. The important architectural outcome was that XStack should behave like a compiler or incremental build system, not like a CI pipeline that reruns everything after every edit.
- Repeated gate calls from prompts needed to short-circuit or cache.
- Later, the user reported that in a new chat they had run a sequence of 13 prompts. They pasted or uploaded a transcript. That transcript became a major source for the handoff package.
- The 13 prompts reportedly implemented, in order:
- After the transcript appeared, the user asked for a maximum-fidelity Context Transfer Packet. The assistant produced one, with sections such as workstreams, decisions, tasks, constraints, open questions, risks, artifacts, and verification queue. Then the user asked to turn that into a downloadable report package. The assistant created Markdown/YAML files and a ZIP archive.
- The conclusion was that docs should be layered: README for accessibility; architecture docs for technical explanation; canon/glossary/contracts for binding doctrine. The 13-prompt transcript reports that docs/canon and many architecture/contract docs were created, but this must be verified.
- Survival, for example, should be an ExperienceProfile + LawProfile + ParameterBundle, not `survival_mode`. Hardcore should be a stricter law/parameter delta. Creative and Lab should be law/profile deltas. This conclusion affects all future gameplay work.
- The future survival vertical slice was discussed in detail: needs, hydration, energy, exposure, resources, gathering, crafting, shelter, death persistence, deterministic saves, and diegetic feedback. This is a future plan, not something established as complete in the 13-prompt transcript.
- The later 13-prompt transcript reportedly implemented a deterministic Lab Galaxy substrate. This included galaxy/Sol/Earth packs, navigation, camera/time processes, UI descriptors, interest regions, SRZ-ready scheduling, and deterministic packaging.
- The conclusion was not to implement all realism immediately. Instead, the architecture should support optional future packs and graceful degradation through budgets/fidelity, macro capsules, and interest regions.

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
