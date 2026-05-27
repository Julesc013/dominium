Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/development_routes/`
Promotion Status: not_reviewed

# Dominium Development Routes and Continuity Preservation - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat had two main phases. The first phase was a technical planning discussion about **Dominium Game**. The user asked what the usual development routes are for games like Dominium, both technically and feature-wise, and what specific components should be worked on in what order. The answer given in that phase proposed that Dominium should be treated not primarily as a normal game with features layered on top, but as a potentially complex simulation system whose foundations need to be built carefully before content, user interface, graphics, multiplayer, or polish.

The central proposal from that first phase was that Dominium should follow a **kernel-first deterministic simulation route**. In plain terms, this means starting with the smallest reliable simulation core: time, deterministic math, random number generation, event ordering, state mutation, serialization, and replay. Only after that would the project move upward into world state, economy, population, governance, conflict, tools, presentation, content, modding, multiplayer, and distribution. The prior assistant described this with the principle: **"Simulation precedes representation. State precedes UI. Determinism precedes performance. Data precedes content."**

That technical recommendation matters because it shapes the whole development philosophy. A content-first game starts by making playable features, then refactors later. An engine-first project builds broad infrastructure before proving the game. The proposed Dominium route was different: build a deterministic simulation kernel first, because if Dominium is meant to be a deep world simulation, fragile foundations would make later systems difficult to test, replay, debug, serialize, synchronize, or mod.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, release, simulation, timekeeping, tooling, ui, workbench, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/development_routes/dominium_development_routes__human_readable_chat_report.txt`.

## What Was Decided

- Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict determinism matters, whether replay or multiplayer are goals, whether modding matters, and what the actual game loop is. Until then, the kernel-first plan should be treated as a strong provisional proposal, not a final specification.
- The first answer was assertive. It stated that Dominium must follow Route C and described the route as the only viable one for Dominium. Later parts of the chat corrected the status of that claim. FACT: the assistant made that recommendation. UNCERTAIN / UNVERIFIED: the recommendation was not validated with external sources in the chat and was not explicitly accepted by the user.
- The initial technical answer proposed a layered stack. It started with mathematical and temporal primitives, then moved into the deterministic simulation kernel, then world state, systems, persistence and replay, tooling, presentation, content, and finally distribution, modding, and multiplayer.
- The user then asked to turn the Context Transfer Packet and visible chat context into a final downloadable, shareable, reusable report package. This was a packaging and normalization task. The user specified exact output files: a full chat report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit file, manifest, and ZIP package.
- After the downloadable package was generated, the user asked not to create another handoff package but to render the package contents into a readable, navigable in-chat report. This led to an "IN-CHAT REPORT READER" response. That response explained the package contents, the workstreams, decisions, tasks, constraints, artifacts, risks, verification queue, and next questions.
- The final state of the conversation is therefore: the chat has produced an architectural proposal for Dominium, converted that proposal into preservation artifacts, rendered those artifacts back into an in-chat reader format, and now requires a plain-English briefing that explains the substance and significance of the conversation.
- FACT: these three routes were discussed.
- FACT: Route C was recommended by the assistant.
- UNCERTAIN / UNVERIFIED: Route C was not accepted by the user as final.
- This topic connects to future work because choosing the route determines the order of implementation. If Route C is accepted, work begins with simulation primitives and determinism rather than UI or content.
- The conclusion reached was not a final project specification, but a strong assistant proposal for how Dominium should be organized if it is indeed a simulation-heavy game.
- A central technical idea was determinism. In this context, determinism means that the same initial state and inputs should produce the same simulation result. This matters for replay, debugging, testing, save/load, multiplayer synchronization, and reproducibility.

## What Was Not Decided

- The first answer was assertive. It stated that Dominium must follow Route C and described the route as the only viable one for Dominium. Later parts of the chat corrected the status of that claim. FACT: the assistant made that recommendation. UNCERTAIN / UNVERIFIED: the recommendation was not validated with external sources in the chat and was not explicitly accepted by the user.
- The assistant produced a large Context Transfer Packet. It preserved the technical route proposal, the caveats around its uncertainty, the proposed phase order, the open questions, the risks, the artifacts, and the next actions.
- The assistant created those files and reported that the chat label was inferred as **Dominium Development Routes**. The package was said to be safe for aggregation **with caveats**. The main caveats were that the substantive project transcript was short, Route C was not user-confirmed, and Dominium's genre, core loop, stack, implementation state, files, platforms, team, and timeline were not established.
- UNCERTAIN / UNVERIFIED: Route C was not accepted by the user as final.
- UNCERTAIN / UNVERIFIED: the required level of determinism for Dominium was not established. It might need full cross-platform deterministic replay, or it might only need ordinary save/load correctness, or something between those extremes.
- The outputs included a Context Transfer Packet and a downloadable package with multiple files. The files are less important than the purpose: preserve the exact status of the discussion, including uncertainty and assistant-proposal status, so future assistants do not accidentally distort the project.
- The second explicit goal was to preserve the chat before retirement. The user did not want a normal summary. They wanted a maximum-fidelity transfer packet that would prevent loss of decisions, constraints, unresolved issues, rationale, and next actions. This was addressed by the Context Transfer Packet.
- Some goals changed over time. The chat began as architecture guidance, became a state-transfer task, became a packaging task, became an in-chat inspection task, and now becomes a plain-English briefing task. The underlying continuity goal stayed consistent: preserve the useful substance without losing uncertainty.
- The chat-specific reporting decisions were more settled. The user explicitly required that the package be limited to this chat, use labels for fact/inference/uncertainty, preserve assistant suggestions as suggestions, and avoid inventing facts. These are firm process decisions because they came directly from the user.
- The user's strongest visible concern is epistemic discipline: do not invent, do not silently infer, do not promote suggestions into decisions, and do not erase uncertainty.
- Before building anything, the project needs a clearer definition of Dominium. The first unresolved technical step is to define the genre and core player loop. This matters because a grand strategy game, colony sim, city-builder, RTS, political simulator, and economic simulation all imply different state models and time scales.
- The largest unresolved issue is whether Dominium is actually simulation-heavy enough to justify the proposed kernel-first deterministic route. The assistant assumed that kind of complexity, but the visible conversation does not prove it. The user needs to confirm or correct that assumption.

## Ideas Rejected, Superseded, Or Deprioritised

- The current user request refines that again. The user now explicitly says they do not want another machine-readable handoff, YAML spec sheet, register dump, or file index. They want a human-readable narrative report explaining the whole chat in plain language. That is the purpose of this report.
- The first was **content-first development**. This means building gameplay and content quickly, discovering what is fun, then refactoring technical foundations later. The assistant described this as fast for feedback but risky for long-term stability. It was not permanently rejected by the user, but it was deprioritized by the assistant.
- The second was **engine-first development**. This means building broad engine infrastructure and tools before making much content or gameplay. The assistant described this as technically strong but expensive and potentially slow. Again, this was not user-rejected; it was assistant-deprioritized.
- The outputs included a Context Transfer Packet and a downloadable package with multiple files. The files are less important than the purpose: preserve the exact status of the discussion, including uncertainty and assistant-proposal status, so future assistants do not accidentally distort the project.
- The idea of treating mods as a late afterthought was implicitly rejected by the assistant, which proposed first-class moddability. But modding itself is not established as a user requirement. If Dominium does not require modding, that part of the feature-completion rule should be weakened.
- The user's strongest visible concern is epistemic discipline: do not invent, do not silently infer, do not promote suggestions into decisions, and do not erase uncertainty.
- Another risk is over-assuming what Dominium is. The name and project context do not establish the genre, simulation scale, platform, or mechanics. Future assistants must not invent those details.
- The way to avoid these risks is simple: preserve labels, preserve caveats, confirm core assumptions, and do not convert assistant-generated architecture into formal requirements until the user accepts it.
- Potential conflicts could arise if another chat already chose an engine, adopted a content-first prototype strategy, deprioritized determinism, rejected modding, or defined Dominium as a smaller/non-simulation project. Those conflicts should be preserved, not erased.
- Content-first and engine-first routes were considered and deprioritized by the assistant, not permanently rejected by the user.

## What Future Work Came From It

- The conversation therefore produced both a **substantive technical proposal** and a **continuity-preservation workflow**. The technical proposal concerns how Dominium might be built. The preservation workflow concerns how the ideas from this chat should be carried forward into future chats and eventually into a larger **Project Spec Book** or **Master Living State File**.
- Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict determinism matters, whether replay or multiplayer are goals, whether modding matters, and what the actual game loop is. Until then, the kernel-first plan should be treated as a strong provisional proposal, not a final specification.
- After the initial planning answer, the user said the chat was being retired and asked for a **maximum-fidelity Context Transfer Packet**. This changed the task. The goal was no longer to continue designing Dominium directly. The goal became preserving everything necessary for a future assistant to continue without making the user repeat context.
- The assistant produced a large Context Transfer Packet. It preserved the technical route proposal, the caveats around its uncertainty, the proposed phase order, the open questions, the risks, the artifacts, and the next actions.
- The user then asked to turn the Context Transfer Packet and visible chat context into a final downloadable, shareable, reusable report package. This was a packaging and normalization task. The user specified exact output files: a full chat report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit file, manifest, and ZIP package.
- After the downloadable package was generated, the user asked not to create another handoff package but to render the package contents into a readable, navigable in-chat report. This led to an "IN-CHAT REPORT READER" response. That response explained the package contents, the workstreams, decisions, tasks, constraints, artifacts, risks, verification queue, and next questions.
- This topic connects to future work because choosing the route determines the order of implementation. If Route C is accepted, work begins with simulation primitives and determinism rather than UI or content.
- Future work must decide how strict determinism really needs to be. Full determinism can be valuable, but it can also impose cost and complexity.
- This topic matters because the user is trying to build a larger multi-chat project memory. The chat itself became not only a design discussion but also a unit of archival evidence for future aggregation.
- The outputs included a Context Transfer Packet and a downloadable package with multiple files. The files are less important than the purpose: preserve the exact status of the discussion, including uncertainty and assistant-proposal status, so future assistants do not accidentally distort the project.
- The user also supplied a later aggregator prompt. This established a future process in which multiple old-chat report packages would be combined into a full Project Spec Book and Master Living State File.
- This chat contributes one piece to that future spec book: early architectural route selection and sequencing for Dominium.

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
