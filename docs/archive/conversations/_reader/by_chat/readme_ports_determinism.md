Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/readme_ports_determinism/`
Promotion Status: not_reviewed

# Dominium README Architecture, Ports, and Determinism - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about refining the root `README.md` for the **Dominium / Domino** project and then preserving the resulting decisions in a form that could survive into later chats. The project, as described in the README, is a deterministic, integer-math, multi-platform simulation game and engine. **Domino** is the deterministic simulation engine core. **Dominium** is the official game, runtime, tooling, and content layer built on top of Domino. The README being discussed was not treated as the final legal or technical specification; it repeatedly stated that the authoritative contracts live under `/docs/spec`. But the README mattered because it sets the project's public architecture, contributor expectations, and the high-level rules future specs must formalize.

The chat began with the user pasting what they called the latest README. That README already had a strong direction: deterministic C89 engine core, C++98 higher layers, fixed-point math, bit-identical simulation across platforms, sparse planetary-scale surfaces, modding constraints, content locks, replay hashing, and a broad platform/rendering matrix including modern systems, retro systems, WASM, and headless servers. The first task was to review the README critically and identify contradictions or weak spots. The main early problems were that the README claimed "286-class upward" support while also mentioning CP/M-80/86, the floating-point prohibition was too broad and could accidentally ban harmless renderer/tool usage, platform lists were duplicated in different sections, plugin determinism needed to be tightened, build metadata could accidentally undermine reproducibility, and data format/versioning rules needed stronger language.

The user then asked for a prompt they could give to Codex to apply the fixes. A detailed mechanical Codex prompt was produced. Codex output was pasted back, and it mostly implemented the requested edits. The README gained more precise rules around fixed-point arithmetic, deterministic RNG, tick phases, build numbers, immutable disk versions, content-lock matching, and Section 9 as the normative platform/rendering matrix.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/readme_ports_determinism/dominium_readme_ports_determinism__human_readable_chat_report.txt`.

## What Was Decided

- The user pasted the final README after those cleanup changes. At that point, the README had the current active form: deterministic constraints clarified, ports unified under one source hierarchy, `/ports` metadata-only if retained, Section 9 normative, lockstep canonical, content-lock mismatch fatal, and disk format versions immutable.
- After the README work, the user asked for a maximum-fidelity context transfer packet. The assistant produced a long state-transfer document with sections for project inventory, decisions, tasks, constraints, open questions, artifacts, risks, and next actions.
- The central artifact was the root `README.md`. The README describes **Domino** as the deterministic engine core and **Dominium** as the official game/tooling/runtime layer. It is written as a high-level architecture document, not a low-level implementation spec.
- The conclusion reached was that the README should remain descriptive, while normative rules belong in `/docs/spec`. This was already stated in the README and preserved. The README should therefore be clear enough to guide contributors but should avoid pretending to be the final binding technical specification.
- What remains uncertain is whether the actual repository `README.md` matches the final pasted version. The chat only saw pasted text and generated prompts; it did not inspect a Git repository.
- The important distinction was between **authoritative** and **non-authoritative** code. Authoritative code mutates canonical simulation state or engine-controlled serialized formats. That code must not use floating point. The engine core and engine-controlled on-disk formats must not contain `float` or `double`.
- The chat also strengthened RNG discipline. RNG streams can only advance during deterministic tick phases. Debug overlays, UI, rendering, and other non-simulation layers must not advance engine RNG streams.
- The README already listed immutable global simulation tick phases: Input, Pre-State, Simulation Lanes, Networks, Fluids & Fields/Merge, Post-Process, and Finalize. The chat added two important constraints.
- First, future-tick scheduling must go through the Pre-State phase's queueing mechanism. This prevents individual systems from inventing ad hoc timers or mutating future state directly.
- The resolution was to distinguish full engine targets from limited tooling/frontends. The final README says the full Domino engine targets 286-class-and-newer systems. Earlier 8-bit platforms, such as CP/M-80, may have limited tooling or experimental frontends, but they do not host the complete world simulation.
- The final README reflects that by saying all platforms build from the same unified source hierarchy. Platform-specific behavior is expressed through thin shims, compile-time flags, and capability tables. Ports cannot fork or override engine/runtime systems. The `/ports` directory, if retained, contains only metadata, build configurations, and capability descriptors. It must not contain engine or runtime source code.
- The unresolved issue is whether a metadata-only `/ports` directory still violates the user's preference. The final README keeps `/ports` in a limited form, but the user's wording could mean no `/ports` directory at all. That should be clarified before writing the directory contract.

## What Was Not Decided

- What remains uncertain is whether the actual repository `README.md` matches the final pasted version. The chat only saw pasted text and generated prompts; it did not inspect a Git repository.
- The unresolved issue is whether a metadata-only `/ports` directory still violates the user's preference. The final README keeps `/ports` in a limited form, but the user's wording could mean no `/ports` directory at all. That should be clarified before writing the directory contract.
- The unresolved work is to define the actual network protocol, prediction model, rollback window, reconciliation logic, and state-hash validation.
- The major unresolved goal is deciding exactly what "no separate ports directory/system" means physically in the repository. The final README allows `/ports` as metadata-only. That may satisfy the user, but it is not confirmed. If the user meant no `/ports` directory at all, the README still needs another revision.
- Another unresolved goal is making the README and normative specs align. The README says specs are authoritative, but those specs were not inspected in this chat.
- UNCERTAIN / UNVERIFIED: `/ports` as metadata-only is the current README state, but may not be fully accepted.
- A related rejected idea was **retro build flows under `/ports/<target>` containing source or alternative implementations**. The final README superseded this with metadata-only `/ports`, assuming `/ports` is retained at all. This rejection is final for source code and behavior, but the existence of `/ports` itself remains uncertain.
- The first next step is to verify the actual repository `README.md` against the final pasted README. The chat only used pasted text. If the repository differs, future work should start from the actual file, not from memory.
- Possible blockers include the unresolved `/ports` question, missing access to actual repository files, and unspecified algorithms for RNG, state hashing, CRCs, and content hashing.
- The reporting constraints later in the chat were also explicit: preserve facts, inferences, uncertainty, rejected options, contradictions, artifacts, prompts, and rationale. Do not invent. Do not silently infer. Do not treat assistant suggestions as user decisions unless accepted.
- The user's profile and instructions emphasize bluntness, rigor, directness, and fact-checking. In this chat, they repeatedly asked for high-fidelity state preservation and explicitly rejected over-compressed summaries. Future assistants should avoid vague reassurance and instead give concrete analysis, caveats, and next actions.
- The ninth artifact was the final README pasted by the user. It is the current textual baseline, but it is unverified against the actual repository.

## Ideas Rejected, Superseded, Or Deprioritised

- The important distinction was between **authoritative** and **non-authoritative** code. Authoritative code mutates canonical simulation state or engine-controlled serialized formats. That code must not use floating point. The engine core and engine-controlled on-disk formats must not contain `float` or `double`.
- The chat also strengthened RNG discipline. RNG streams can only advance during deterministic tick phases. Debug overlays, UI, rendering, and other non-simulation layers must not advance engine RNG streams.
- The reason this mattered is that deterministic engines often fail not because of obvious random numbers, but because of subtle ordering differences: thread scheduling, map iteration order, future event queues, or timing-dependent commits. The README needed language that blocked those failure modes.
- The resolution was to distinguish full engine targets from limited tooling/frontends. The final README says the full Domino engine targets 286-class-and-newer systems. Earlier 8-bit platforms, such as CP/M-80, may have limited tooling or experimental frontends, but they do not host the complete world simulation.
- This was the decisive topic. The user rejected the idea that ports should live in a separate directory or separate system. They wanted all ports to work within the same structure, with reduced functionality gracefully degrading and not flowing upstream.
- The final README reflects that by saying all platforms build from the same unified source hierarchy. Platform-specific behavior is expressed through thin shims, compile-time flags, and capability tables. Ports cannot fork or override engine/runtime systems. The `/ports` directory, if retained, contains only metadata, build configurations, and capability descriptors. It must not contain engine or runtime source code.
- Once the user rejected separate port systems, capability-based degradation became the mechanism for supporting weaker platforms. The idea is that platform limitations should be described declaratively: available renderers, input capabilities, storage limits, memory constraints, audio support, windowing features, and so on. Missing features should disable themselves or degrade gracefully.
- The key requirement is that degradation must not alter canonical simulation semantics. A DOS or Win16 frontend may have reduced rendering fidelity or simpler UX, but it must not change engine state, save formats, ordering rules, or simulation results.
- The lesson is that future Codex prompts should be explicit: preserve headings, do not add sections unless requested, do not duplicate existing content, and preserve specific architecture decisions.
- The port architecture goal changed the most. Initially, the README still allowed a mental model where retro ports had their own build flows under `/ports/<target>`. The user rejected that model, and the README direction changed to unified source hierarchy plus capability-based degradation.

## What Future Work Came From It

- The user then asked for a prompt they could give to Codex. A detailed patch prompt was produced. It instructed Codex to apply minimal edits to the existing README without changing headings, section order, or tone.
- That prompt asked Codex to:
- The user pasted Codex's output after the port prompt. The output correctly added the unified-source and metadata-only port language, but it also introduced a duplicated top section: two overlapping "This repository includes" blocks. The assistant identified that duplication and produced a cleanup prompt.
- That cleanup prompt instructed Codex to remove the redundant block, remove undefined "embedded" from the future systems list, replace vague "lockstep/rollback" wording with lockstep-first canonical networking language, and update the contributing determinism bullet to refer back to Section 2.1 instead of maintaining a separate formulation.
- After the README work, the user asked for a maximum-fidelity context transfer packet. The assistant produced a long state-transfer document with sections for project inventory, decisions, tasks, constraints, open questions, artifacts, risks, and next actions.
- What remains uncertain is whether the actual repository `README.md` matches the final pasted version. The chat only saw pasted text and generated prompts; it did not inspect a Git repository.
- The project's core promise is deterministic simulation. The README already required fixed-point arithmetic and deterministic tick phases, but the chat refined the boundary of that determinism.
- The chat also strengthened RNG discipline. RNG streams can only advance during deterministic tick phases. Debug overlays, UI, rendering, and other non-simulation layers must not advance engine RNG streams.
- The README already listed immutable global simulation tick phases: Input, Pre-State, Simulation Lanes, Networks, Fluids & Fields/Merge, Post-Process, and Finalize. The chat added two important constraints.
- First, future-tick scheduling must go through the Pre-State phase's queueing mechanism. This prevents individual systems from inventing ad hoc timers or mutating future state directly.
- The reason this mattered is that deterministic engines often fail not because of obvious random numbers, but because of subtle ordering differences: thread scheduling, map iteration order, future event queues, or timing-dependent commits. The README needed language that blocked those failure modes.
- This connects directly to future spec work. A capability-system spec is needed. It should define what descriptors can express, what they cannot express, and how they are validated. There is a risk that capability descriptors become "behavior by proxy" if they are too powerful. They should describe platform capabilities, not redefine simulation.

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
