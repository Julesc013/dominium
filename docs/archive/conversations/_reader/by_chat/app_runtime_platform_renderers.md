Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/app_runtime_platform_renderers/`
Promotion Status: not_reviewed

# Dominium APP0 Runtime, Platform, and Renderer Architecture - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about the **Dominium / Domino project's application and runtime layer**, referred to throughout as **APP0**. The user began by giving a large implementation-oriented prompt titled **"PROMPT APP0 - RUNTIMES, APPLICATIONS, PLATFORMS & RENDERERS."** That prompt defined a strict scope: work on the **client, server, launcher, setup/installer, tools, renderers, and platform support**, while not redesigning the simulation itself. The key philosophical rule was that applications are **shells around the simulation**, not decision-makers. The authoritative game logic remains in **engine + game**.

The initial direction looked like it might become a Codex implementation prompt immediately. A first assistant response turned the APP0 prompt into a large implementation-pack prompt, including possible CMake targets, executable names, CLI flags, docs, smoke tests, and commit sequencing. The user then corrected the direction: **"First, let's discuss this before we plan or generate any prompts."** That changed the conversation from implementation-prompt generation into architectural review.

The discussion then moved into what APP0 really needs to accomplish. The user clarified that the long-term macro-prompt plan should not merely produce documentation or empty stubs. At the end of that plan, the project should have a **running executable** capable of displaying a **real, interactive, resizable window** across supported platform and renderer combinations. That clarification was important because it exposed a missing or under-specified layer: a **platform runtime layer**. A renderer alone cannot responsibly own windows, event loops, resizing, surface handles, timing, and headless support. The proposed architecture therefore separated **platform/windowing** from **rendering**: platform creates windows and surfaces; renderers consume surfaces; the client orchestrates both; the server remains headless and authoritative.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__human_readable_chat_report.txt`.

## What Was Decided

- The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do.
- The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, and introducing gameplay shortcuts. **FACT:** authoritative logic remains in engine + game.
- Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.
- The server was defined as the authoritative runtime host. It handles simulation, sharding, scheduling, law enforcement, persistence, integrity, and anti-cheat. It must be headless-capable and support AI-only autorun and MMO scale.
- The key conclusion is that the server should not depend on graphics or windowing. This matters because dedicated servers, cloud servers, and AI-only autorun must run without a GPU or display.
- The key conclusion is that the launcher must not install content or alter simulation state. That belongs to setup. This separation matters because launchers often become bloated, state-mutating, or inconsistent with installer/versioning logic.
- Tools were discussed as world inspectors, economy inspectors, replay viewers, validators, optional editors, and profilers. The important point is that tools must use the same authority rules, never bypass law, and be auditable.
- This is a distinctive part of Dominium's philosophy. Many projects treat tools as privileged by default. This chat preserved the opposite idea: tools may need elevated abilities, but those abilities must be explicit, authorized, and logged.
- This is a proposal, not a user-confirmed final design, but it follows strongly from the stated goal. The actual repository must be inspected to see whether such a layer already exists.
- The unresolved issue is the exact renderer capability schema. The chat proposed ideas but did not finalize fields, priorities, or target matrices.
- The idea is attractive because it supports broad distribution and long-term extensibility. But it is not a final decision. Dynamic plugins introduce ABI, packaging, security, and platform restrictions. Static registration may be simpler. A hybrid may be best. The repository and build system need to be inspected before deciding.
- The final part of the chat was about preserving the conversation. The user asked for a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat reader. These outputs exist to let future chats continue without losing nuance.

## What Was Not Decided

- What remains uncertain is whether the current repository already enforces these boundaries mechanically. The actual code needs inspection.
- The unresolved issue is sharding semantics. APP0 requires sharding hooks, but the chat did not decide whether shards are spatial, logical, temporal, jurisdictional, or something else. The report preserved the idea that APP0 can provide sharding plumbing without inventing simulation semantics.
- The unresolved issue is the trust and integrity model for setup. The chat did not decide whether content verification should use hashes, signatures, local manifests, network verification, or another model.
- The unresolved issue is the exact elevation/audit model. The chat did not decide how tools authenticate, request write permissions, log actions, or interact with law enforcement modules.
- The unresolved issue is the exact renderer capability schema. The chat proposed ideas but did not finalize fields, priorities, or target matrices.
- The user asked to look at the old code snapshot in project attachments. A prior assistant claimed to inspect it, but later preservation documents marked that claim as **UNCERTAIN / UNVERIFIED**.
- This became one of the most important unresolved issues. Almost every implementation question depends on the real code: directory layout, build system, languages, existing platform/render layers, client/server dependencies, and engine/game public APIs. The next real step is repository verification.
- INFERENCE:** The user wants future assistants to be epistemically careful: not inventing repository facts, not treating proposals as decisions, and not losing uncertainty.
- The exact module architecture remains unresolved. The exact platform/renderer support matrix remains unresolved. The exact relationship to the current repository remains unresolved because the old snapshot has not been verified. The exact setup trust model, tool audit model, sharding semantics, and client prediction policy remain unresolved.
- This affects the client, server, launcher, setup, and tools. The client can display and interact; the server can host authority; the launcher can start sessions; setup can install and verify; tools can inspect and audit. But none of them should invent unauthorized simulation outcomes.
- The assumption behind this decision is that engine/game code can be hosted through stable public APIs. Whether the current repo already supports that is **UNCERTAIN / UNVERIFIED**.
- The unresolved caveat is prediction. If client-side prediction is later needed, it must be designed carefully as non-authoritative and probably separated from authority-committing simulation code.

## Ideas Rejected, Superseded, Or Deprioritised

- The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**.
- The key conclusion is that the launcher must not install content or alter simulation state. That belongs to setup. This separation matters because launchers often become bloated, state-mutating, or inconsistent with installer/versioning logic.
- The unresolved issue is the exact renderer capability schema. The chat proposed ideas but did not finalize fields, priorities, or target matrices.
- FACT:** The APP0 prompt explicitly states that the client must not simulate authoritative state, bypass law, or invent data.
- FACT:** The APP0 prompt says the launcher must not install content itself, while setup installs engine/content, manages versions, and validates integrity.
- The idea of immediately turning APP0 into implementation prompts was superseded by the user's correction. The initial implementation pack remains useful, but the process changed. This rejection is final until the user explicitly asks for prompts again.
- This was rejected as an architectural direction, though the rejection is technically an assistant proposal rather than a user-finalized rule. It was rejected because it couples rendering APIs to OS-specific windowing and makes headless/server support harder.
- Starting with Vulkan, Direct3D, Metal, or OpenGL before proving the platform/window/software path was deprioritized. The reason is practical: GPU APIs add complexity, and bugs become hard to attribute. A software renderer path gives a simpler first success state.
- This idea was rejected conceptually. Intel, AMD, NVIDIA, and Apple are not renderer APIs. They are adapter/driver vendors under API families. Modelling vendors as renderers would duplicate logic and explode the support matrix.
- This was rejected or at least deprioritized. The user asked about vintage systems, but the proposed answer was to support vintage through capability tiers rather than individual promises. That avoids an unbounded list of old systems.

## What Future Work Came From It

- The conversation started when the user provided a structured prompt called **APP0 - Runtimes, Applications, Platforms & Renderers**. It was addressed to **GPT-5.2 Codex** and framed as part of the ongoing **Dominium / Domino project**. The prompt's purpose was to build executable and platform support correctly while staying inside the application/runtime layer.
- The initial APP0 prompt established several hard rules. The assistant was not allowed to redesign simulation rules, alter content definitions, change life/civilization/economy logic, or introduce gameplay shortcuts. This mattered because Dominium appears to have a strong distinction between **authoritative simulation/game logic** and the shells that host, display, launch, inspect, or distribute that logic.
- A first assistant response converted the user's APP0 prompt into a large implementation pack. It proposed repository shapes, CMake targets, executable names, renderer backends, CLI flags, smoke tests, and a commit sequence. It was useful as an implementation artifact, but it was premature relative to the user's actual desired process.
- The user immediately corrected the direction: **"First, let's discuss this before we plan or generate any prompts."** That was an important change. It meant the user did not want a Codex prompt yet. They wanted to reason about the architecture before locking implementation instructions.
- The user then explained that by the end of the macro-prompt plan, the project should have a **running executable** capable of displaying an **interactive and resizable window** for each supported platform and renderer combination. This made the discussion more concrete. APP0 was no longer just about docs and stubs; it had to create a real runtime path.
- The user then stated that future implementation would have permission to modify `render`, `platform`, `application`, `client`, `server`, and docs. They asked whether this was enough or whether `engine` and `game` also needed write access.
- The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do.
- Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.
- The final part of the chat was about preserving the conversation. The user asked for a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat reader. These outputs exist to let future chats continue without losing nuance.
- This matters because the conversation contains both hard requirements and speculative proposals. A future assistant must know which is which.
- The user also explicitly wanted discussion before generating further prompts. This goal mattered because architecture mistakes in this layer would become hard to undo.
- Later, the user explicitly stated a stronger end goal: by the end of the macro-prompt plan, there should be a running executable capable of displaying an interactive, resizable window on each supported platform and renderer combination. That made the project more concrete and forced discussion of platform runtime, renderer selection, and bring-up sequence.

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
