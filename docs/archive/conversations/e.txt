GPT-5.5 Pro • build 2026-05-25

# Human-Readable Chat Report — Dominium README Architecture, Ports, and Determinism

## 1. One-Page Orientation

This chat was mainly about refining the root `README.md` for the **Dominium / Domino** project and then preserving the resulting decisions in a form that could survive into later chats. The project, as described in the README, is a deterministic, integer-math, multi-platform simulation game and engine. **Domino** is the deterministic simulation engine core. **Dominium** is the official game, runtime, tooling, and content layer built on top of Domino. The README being discussed was not treated as the final legal or technical specification; it repeatedly stated that the authoritative contracts live under `/docs/spec`. But the README mattered because it sets the project’s public architecture, contributor expectations, and the high-level rules future specs must formalize.

The chat began with the user pasting what they called the latest README. That README already had a strong direction: deterministic C89 engine core, C++98 higher layers, fixed-point math, bit-identical simulation across platforms, sparse planetary-scale surfaces, modding constraints, content locks, replay hashing, and a broad platform/rendering matrix including modern systems, retro systems, WASM, and headless servers. The first task was to review the README critically and identify contradictions or weak spots. The main early problems were that the README claimed “286-class upward” support while also mentioning CP/M-80/86, the floating-point prohibition was too broad and could accidentally ban harmless renderer/tool usage, platform lists were duplicated in different sections, plugin determinism needed to be tightened, build metadata could accidentally undermine reproducibility, and data format/versioning rules needed stronger language.

The user then asked for a prompt they could give to Codex to apply the fixes. A detailed mechanical Codex prompt was produced. Codex output was pasted back, and it mostly implemented the requested edits. The README gained more precise rules around fixed-point arithmetic, deterministic RNG, tick phases, build numbers, immutable disk versions, content-lock matching, and Section 9 as the normative platform/rendering matrix.

The most important change came after that. The user corrected the port architecture directly: they did **not** want ports stored in a separate directory or system; all ports should work within the same structure, and reduced functionality should gracefully degrade without flowing upstream. That statement changed the architecture from “ports as per-target build flows under `/ports/<target>/`” to “all platforms share one unified source hierarchy.” In the final README, platform differences are expressed through capability descriptors, compile-time flags, and thin shims. Ports must not fork, override, or reimplement engine/runtime systems. Reduced features degrade locally through the capability system and must not alter canonical simulation behavior. This is the most important project-specific decision from the chat.

A subtle unresolved issue remained. The final README still contains a `/ports` directory, but only as optional metadata, build configuration, and capability descriptors, with no code or behavior. That was the assistant/Codex interpretation of the user’s requirement. It may be acceptable, but it is not fully verified. The user’s wording could also mean no `/ports` directory at all. Another unresolved issue is that the intro mentions “OS/2 strata via shims,” while Section 9 says it is the normative platform matrix and does not list OS/2. That contradiction needs to be resolved before treating the README as stable.

The later part of the chat shifted from README work to preservation. The user asked for a maximum-fidelity context transfer packet, then a downloadable report package, then an in-chat reader version of the package. Those outputs were created to make this chat reusable for a future assistant or future Project Spec Book aggregation. The substance to carry forward is not the package format itself; it is the architectural state: deterministic engine boundaries, unified port strategy, capability-based graceful degradation, spec-first documentation, and the remaining verification tasks.

A future assistant should understand that this chat is not just a README editing session. It records a major architectural correction: **do not let ports become separate systems**. It also records the project’s current determinism boundaries: no floats in authoritative simulation or engine-controlled formats, but floats are allowed in non-authoritative renderers/tools if they never feed back into canonical state. The next practical work is to verify the actual repository README, resolve the OS/2/platform-matrix inconsistency, confirm whether metadata-only `/ports` is acceptable, and then update the normative specs—especially `DIRECTORY_CONTRACT.md` and a capability-system specification.

---

## 2. The Story of the Conversation

### The chat began with a README review

The user opened by pasting the latest `README.md` for **DOMINIUM & DOMINO**. The README described a deterministic, multi-scale, multi-platform simulation game and engine. Its central promise was bit-identical simulation across modern systems, legacy systems, future systems, and headless/server nodes. It described fixed-point numeric formats, deterministic tick phases, planetary-scale surface coordinates, save formats, modding rules, content locks, renderers, platform support, and contribution constraints.

The first assistant response did not rewrite the README. It reviewed it critically. The critique identified the strongest parts and the places likely to cause future contradictions. The largest early issue was platform scope: the README said the engine should execute on “286-class upward” hardware but also listed CP/M-80/86. That created a contradiction because CP/M-80 implies earlier 8-bit systems that cannot reasonably host the complete engine. The suggested resolution was to say that the full Domino engine targets 286-class-and-newer systems, while earlier 8-bit platforms may host limited tooling or experimental frontends only.

A second important issue was the floating-point rule. The README originally said no floating point in any simulation or IO code path. That was too broad. It could accidentally ban valid renderer, editor, or analysis-tool uses of floating point even when those floats do not affect canonical simulation state. The suggested correction was to ban floating point specifically in code that mutates canonical simulation state or engine-controlled serialized formats, while allowing floats in tools, renderers, and non-authoritative analysis as long as float-derived values never flow back into engine state or save formats.

Other issues were also identified: repeated platform lists could drift, plugins needed stronger deterministic constraints, build numbers and timestamps should never influence simulation, data formats needed immutable versioning, and mod/content mismatches should be fatal instead of silently tolerated.

### The first Codex prompt converted critique into README edits

The user then asked for a prompt they could give to Codex. A detailed patch prompt was produced. It instructed Codex to apply minimal edits to the existing README without changing headings, section order, or tone.

That prompt asked Codex to:

* clarify 286-class support and CP/M limitations;
* narrow the no-floating-point rule;
* add deterministic RNG-stream discipline;
* strengthen tick phasing and deterministic parallelism language;
* clarify that each Surface owns one vertical Page in Dominium 1.x;
* mark terrain caches as non-canonical;
* add a disclaimer that `DIRECTORY_CONTRACT.md` is authoritative;
* ensure build numbers/timestamps are diagnostic only;
* bind binary plugins to the same determinism constraints as core;
* make `content.lock` mismatches fatal until reconciled;
* strengthen data-format versioning and packing rules;
* make Section 9 the normative platform/renderer matrix;
* clarify installer save locations.

The user then pasted Codex’s output. That output mostly applied the intended fixes correctly. The assistant reviewed it and said it was coherent, with only minor remaining issues: vague “embedded” wording, vague lockstep/rollback wording, and a contributing-section determinism bullet that could drift from Section 2.1.

### The user changed the port architecture direction

The next major development was not a minor cleanup. The user stated that they did not want ports stored in a separate directory or system. Their exact wording was:

> “i dont want ports to be stored in a seperate directory or system, all ports should work in with the same strcutre and any reduced fucntionality should gracefully degrade and not flow upstream”

This was the most important correction in the chat. It changed the README’s port model. Before this, the README still had language suggesting retro platforms might have build flows under `/ports/<target>/`. The user rejected that architecture. The new requirement was that all ports/platforms must use the same structure. Reduced functionality is acceptable, but it must degrade locally and must not push changes upstream into canonical engine/runtime behavior.

A second Codex prompt was then produced to integrate this requirement. It told Codex to remove the idea that ports live in separate directory trees and to rewrite the README so that all platforms share one unified source tree. It allowed `/ports` only as optional metadata and build configuration, not an alternate implementation directory. It also required capability descriptors/tables and thin shims as the mechanism for platform variance.

### Codex introduced a duplicate block, then it was cleaned up

The user pasted Codex’s output after the port prompt. The output correctly added the unified-source and metadata-only port language, but it also introduced a duplicated top section: two overlapping “This repository includes” blocks. The assistant identified that duplication and produced a cleanup prompt.

That cleanup prompt instructed Codex to remove the redundant block, remove undefined “embedded” from the future systems list, replace vague “lockstep/rollback” wording with lockstep-first canonical networking language, and update the contributing determinism bullet to refer back to Section 2.1 instead of maintaining a separate formulation.

The user pasted the final README after those cleanup changes. At that point, the README had the current active form: deterministic constraints clarified, ports unified under one source hierarchy, `/ports` metadata-only if retained, Section 9 normative, lockstep canonical, content-lock mismatch fatal, and disk format versions immutable.

### The chat then shifted into preservation and packaging

After the README work, the user asked for a maximum-fidelity context transfer packet. The assistant produced a long state-transfer document with sections for project inventory, decisions, tasks, constraints, open questions, artifacts, risks, and next actions.

The user then asked to turn that packet into a downloadable report package. Files were generated: a full chat report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit file, manifest, and ZIP archive. Later, the user asked to inspect the package inside the chat without downloading files. An in-chat reader version was produced, listing workstreams, decisions, tasks, constraints, artifacts, open questions, and risks.

The current request is different again: the user does not want another handoff, YAML, register dump, or file index. They want a plain-language report explaining the substance of the conversation. That is what this document is.

---

## 3. Main Topics We Discussed

### Topic 1 — The Dominium / Domino README as a project contract

The central artifact was the root `README.md`. The README describes **Domino** as the deterministic engine core and **Dominium** as the official game/tooling/runtime layer. It is written as a high-level architecture document, not a low-level implementation spec.

The reason the README mattered is that it sets expectations for all future contributors and future specs. If the README says platforms can diverge, contributors may build divergent ports. If it says no floats too broadly, tools and renderers may become unnecessarily constrained. If it says Section 9 is normative, then every other platform mention must match it. The README is not merely marketing; it is steering project architecture.

The conclusion reached was that the README should remain descriptive, while normative rules belong in `/docs/spec`. This was already stated in the README and preserved. The README should therefore be clear enough to guide contributors but should avoid pretending to be the final binding technical specification.

What remains uncertain is whether the actual repository `README.md` matches the final pasted version. The chat only saw pasted text and generated prompts; it did not inspect a Git repository.

### Topic 2 — Determinism boundaries

The project’s core promise is deterministic simulation. The README already required fixed-point arithmetic and deterministic tick phases, but the chat refined the boundary of that determinism.

The important distinction was between **authoritative** and **non-authoritative** code. Authoritative code mutates canonical simulation state or engine-controlled serialized formats. That code must not use floating point. The engine core and engine-controlled on-disk formats must not contain `float` or `double`.

However, renderers, tools, launcher code, and non-authoritative analysis may use floats internally if those float-derived values never flow back into engine state or engine-controlled file formats. This distinction matters because renderers and tooling can remain practical without undermining deterministic simulation.

The chat also strengthened RNG discipline. RNG streams can only advance during deterministic tick phases. Debug overlays, UI, rendering, and other non-simulation layers must not advance engine RNG streams.

The conclusion was a more precise determinism contract: strict where it affects simulation, flexible where it does not. The remaining work is to formalize this in specs and tests, including exact RNG algorithms, replay hash algorithms, and state serialization rules.

### Topic 3 — Tick phasing and deterministic parallelism

The README already listed immutable global simulation tick phases: Input, Pre-State, Simulation Lanes, Networks, Fluids & Fields/Merge, Post-Process, and Finalize. The chat added two important constraints.

First, future-tick scheduling must go through the Pre-State phase’s queueing mechanism. This prevents individual systems from inventing ad hoc timers or mutating future state directly.

Second, parallel execution is allowed only when it operates on disjoint subsets of state and commits results in a globally deterministic order. This allows parallelism without sacrificing bit-identical behavior.

The reason this mattered is that deterministic engines often fail not because of obvious random numbers, but because of subtle ordering differences: thread scheduling, map iteration order, future event queues, or timing-dependent commits. The README needed language that blocked those failure modes.

### Topic 4 — Hardware targets and CP/M

The initial README said the engine should execute on decades of hardware, “286-class upward,” but it also listed CP/M-80/86. That created ambiguity. CP/M-80 implies 8-bit systems, which are not realistic full simulation hosts for this engine.

The resolution was to distinguish full engine targets from limited tooling/frontends. The final README says the full Domino engine targets 286-class-and-newer systems. Earlier 8-bit platforms, such as CP/M-80, may have limited tooling or experimental frontends, but they do not host the complete world simulation.

This matters because it prevents overpromising. It also keeps “cross-era hardware” meaningful without making the architecture impossible.

### Topic 5 — The port architecture correction

This was the decisive topic. The user rejected the idea that ports should live in a separate directory or separate system. They wanted all ports to work within the same structure, with reduced functionality gracefully degrading and not flowing upstream.

The final README reflects that by saying all platforms build from the same unified source hierarchy. Platform-specific behavior is expressed through thin shims, compile-time flags, and capability tables. Ports cannot fork or override engine/runtime systems. The `/ports` directory, if retained, contains only metadata, build configurations, and capability descriptors. It must not contain engine or runtime source code.

This matters because it prevents the project from becoming many loosely related ports. The user wants one canonical engine/runtime structure that adapts outward to platform limitations, rather than platform limitations pushing changes inward into core design.

The unresolved issue is whether a metadata-only `/ports` directory still violates the user’s preference. The final README keeps `/ports` in a limited form, but the user’s wording could mean no `/ports` directory at all. That should be clarified before writing the directory contract.

### Topic 6 — Capability-based graceful degradation

Once the user rejected separate port systems, capability-based degradation became the mechanism for supporting weaker platforms. The idea is that platform limitations should be described declaratively: available renderers, input capabilities, storage limits, memory constraints, audio support, windowing features, and so on. Missing features should disable themselves or degrade gracefully.

The key requirement is that degradation must not alter canonical simulation semantics. A DOS or Win16 frontend may have reduced rendering fidelity or simpler UX, but it must not change engine state, save formats, ordering rules, or simulation results.

This connects directly to future spec work. A capability-system spec is needed. It should define what descriptors can express, what they cannot express, and how they are validated. There is a risk that capability descriptors become “behavior by proxy” if they are too powerful. They should describe platform capabilities, not redefine simulation.

### Topic 7 — Data formats, saves, and content locks

The README already described engine-controlled formats: integer math, fixed-point positions, little-endian canonical representation, TLV chunk sections, and no serialized pointers. The chat strengthened that into a long-term compatibility contract.

The final README says existing on-disk versions are immutable contracts. Any behavioral or layout change requires a new on-disk version and a documented migration path. It also says canonical format definitions cannot rely on platform-specific struct packing pragmas. Disk layouts must be defined in terms of explicit field sizes.

The `content.lock` file was also strengthened. It lists exact content packs and mod versions by id/version/hash. On loading a universe, the engine verifies that the active content set exactly matches `content.lock`; mismatches are fatal until reconciled.

This matters because deterministic simulation is not only about CPU math. If content registries, save formats, or chunk layouts vary silently, determinism breaks. The remaining work is to define exact binary layouts, hash algorithms, CRC choices, TLV encoding, and reconciliation processes.

### Topic 8 — Networking model

The original README had a vague phrase: “Network layer manages deterministic lockstep/rollback.” The cleanup prompt replaced this with a clearer rule: the canonical network model is deterministic lockstep. Rollback and prediction, when used by runtimes, must converge to the same state as pure lockstep for the same inputs and content.

This matters because rollback can otherwise be interpreted as an alternate simulation model. The final wording makes lockstep the reference truth and rollback/prediction runtime optimizations that must converge.

The unresolved work is to define the actual network protocol, prediction model, rollback window, reconciliation logic, and state-hash validation.

### Topic 9 — Codex as the edit implementation tool

The user used Codex externally to apply README changes. The assistant’s role was to generate prompts and review outputs. This became a workflow topic in its own right.

The chat demonstrated that Codex can apply surgical edits, but also that it can introduce accidental duplicated content. After the port-architecture prompt, Codex duplicated the intro/repository-includes block. That was caught and fixed with a cleanup prompt.

The lesson is that future Codex prompts should be explicit: preserve headings, do not add sections unless requested, do not duplicate existing content, and preserve specific architecture decisions.

### Topic 10 — Report packaging and state transfer

After the README work, the user requested a maximum-fidelity context transfer packet. Then they requested a downloadable package. Then they requested an in-chat reader. Those outputs were meant to preserve this chat for future aggregation and future spec-book construction.

The important point is not the file packaging itself. The important point is that the chat produced a reusable record of decisions, open issues, risks, and artifacts. This current report is a human-readable explanation of that record.

---

## 4. What We Were Trying to Achieve

### Explicit goals stated by the user

The first explicit goal was to review and improve the latest README. The user pasted the README and accepted critique. Then they asked for a Codex prompt to make the fixes.

The second explicit goal was architectural: ports should not be stored in a separate directory or system. All ports should work with the same structure, and reduced functionality should degrade gracefully without flowing upstream. This was not merely a wording preference; it changed the intended repository architecture.

The third explicit goal was preservation. The user asked for a maximum-fidelity context transfer packet, then a final downloadable report package, then an in-chat reader, and now this human-readable narrative report. The goal was to avoid having to re-explain the chat later.

### Inferred goals

It is reasonable to infer that the user wanted the README to become a stable foundation for future specs and implementation. The repeated use of Codex prompts suggests the user wanted changes to be actionable, not just conceptual. The focus on deterministic constraints, ports, and directory structure suggests the user cares about preventing future contributors or assistants from introducing architectural drift.

This is an inference, not a directly stated goal. The user did not say “I want a future Project Spec Book from this README” during the README editing turns, but later report-package prompts explicitly referenced future spec-book aggregation.

### Goals that changed over time

The conversation began as a README critique. It became a Codex prompt-writing workflow. It then changed into an architectural correction about ports. Finally, it became a preservation and reporting exercise.

The port architecture goal changed the most. Initially, the README still allowed a mental model where retro ports had their own build flows under `/ports/<target>`. The user rejected that model, and the README direction changed to unified source hierarchy plus capability-based degradation.

### Goals that remain unresolved

The major unresolved goal is deciding exactly what “no separate ports directory/system” means physically in the repository. The final README allows `/ports` as metadata-only. That may satisfy the user, but it is not confirmed. If the user meant no `/ports` directory at all, the README still needs another revision.

Another unresolved goal is making the README and normative specs align. The README says specs are authoritative, but those specs were not inspected in this chat.

---

## 5. Decisions Made and Why

The most important decisions fall into five groups: project hierarchy, determinism, port architecture, data formats, and workflow.

### Project hierarchy decisions

**FACT: Domino is the deterministic simulation engine core, and Dominium is the official game/tooling layer built on top.**
This was already in the README and preserved throughout. It matters because it separates generic engine capabilities from game-specific content and tooling. It also prevents game logic from creeping into the engine core.

**FACT: The README is descriptive, while `/docs/spec` files are normative.**
This decision was already present in the README and reinforced by later edits. It makes sense because the README is too high-level to be a binding implementation contract. The implication is that future work must update `DIRECTORY_CONTRACT.md`, `MILESTONES.md`, and likely new specs for determinism, data formats, and capabilities.

### Hardware and platform scope decisions

**FACT: The full Domino engine targets 286-class-and-newer systems.**
This decision resolved the contradiction created by CP/M mentions. The alternative would have been claiming full simulation support on CP/M-80-class systems, which would overpromise. The chosen decision allows CP/M-80/86 to remain as limited tooling or frontend targets without pretending they can host full simulation.

**FACT: Undefined “embedded” future support was removed from the intro.**
The alternative was to keep “embedded” vague. Removing it made the README more precise. It could be revisited later if the project defines exactly what embedded means.

### Determinism decisions

**FACT: Floating point is banned in authoritative simulation mutation paths and engine-controlled serialized formats.**
This is central. It preserves deterministic behavior across compilers, ISAs, and old systems.

**FACT: Floating point is allowed in tools, renderers, and non-authoritative analysis if it never feeds back into engine state or engine-controlled formats.**
This is the balancing decision. The alternative was a blanket no-floats policy, but that would overconstrain renderers and tools. The chosen boundary manages the real risk—authoritative state contamination—without banning harmless non-authoritative usage.

**FACT: RNG streams advance only during deterministic tick phases.**
This prevents debug, rendering, UI, or other incidental layers from changing simulation state.

**FACT: Tick phases are immutable, future-tick scheduling goes through Pre-State, and parallel commits must be deterministic.**
These choices manage subtle nondeterminism risks: ordering, thread scheduling, and ad hoc timers.

**FACT: Lockstep is the canonical network model. Rollback and prediction must converge to pure lockstep.**
The alternative was vague “lockstep/rollback,” which could imply two equally authoritative network models. The chosen wording makes lockstep the reference behavior.

### Port architecture decisions

**FACT: All platforms build from the same unified source hierarchy.**
This was directly driven by the user’s correction. It is one of the most important decisions.

**FACT: Ports cannot fork, override, or reimplement engine/runtime systems.**
This follows from the same user requirement. It prevents per-platform codebases.

**FACT: Reduced functionality must degrade gracefully through capability systems and must not flow upstream.**
This preserves canonical engine behavior while allowing weaker platforms to run reduced renderers/UX.

**UNCERTAIN / UNVERIFIED: `/ports` as metadata-only is the current README state, but may not be fully accepted.**
The assistant/Codex interpreted the user’s requirement as allowing `/ports` for metadata, build configs, and capability descriptors only. The user has not explicitly confirmed that this is acceptable. This decision should be revisited before writing the directory contract.

### Data-format decisions

**FACT: Existing on-disk versions are immutable contracts.**
This prevents silent reinterpretation of old saves. Any layout or behavior change requires a new version and migration path.

**FACT: Canonical format definitions cannot rely on platform-specific struct packing pragmas.**
This protects cross-compiler and cross-platform disk layout stability.

**FACT: `content.lock` mismatches are fatal until reconciled.**
This prevents “user-friendly” silent loading with mismatched mods/content, which would break deterministic registries.

**FACT: Terrain caches and microgrids are non-canonical.**
Canonical world geometry comes from procedural phi, edits, volumes, and state; caches can be rebuilt.

### Workflow decisions

**INFERENCE: Future Codex prompts should be surgical and explicit about what not to change.**
This is inferred from the chat’s workflow and from Codex’s duplicated-block mistake. It is not a formal project decision, but it is a strong process lesson.

---

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

The most important rejected idea was **separate port systems or per-target source trees**. This was rejected explicitly by the user. The reason is that separate port systems would fragment the project, create divergent behavior, and let platform limitations flow upstream into the canonical architecture. This rejection should be treated as final unless the user explicitly changes direction.

A related rejected idea was **retro build flows under `/ports/<target>` containing source or alternative implementations**. The final README superseded this with metadata-only `/ports`, assuming `/ports` is retained at all. This rejection is final for source code and behavior, but the existence of `/ports` itself remains uncertain.

Another rejected idea was **per-platform alternate engine implementations**. This would violate deterministic reproducibility and the unified source hierarchy. It should not be reintroduced for the canonical project.

The idea that **CP/M-80 could host the complete world simulation** was rejected by clarification. CP/M-80/86 may remain in the platform discussion only as limited tooling or frontend support, not a full simulation host.

The vague phrase **“embedded”** was removed from the future systems list. It was not necessarily rejected forever, but it was rejected as undefined README wording. It should only return if the project defines what embedded target class means.

The original blanket phrase **“no floating point in any simulation or IO code path”** was superseded. The better rule is no floating point in authoritative mutation paths or engine-controlled formats. This is important because future assistants should not “simplify” the rule back into “no floats anywhere.”

The vague networking statement **“lockstep/rollback”** was superseded by lockstep-first language. Rollback remains allowed, but not as an alternate canonical model.

Silent reinterpretation of disk versions, build timestamps affecting simulation, binary plugins using nondeterministic APIs, and duplicate README sections were all rejected or superseded.

---

## 7. Important Reasoning and Rationale

The visible reasoning throughout the chat was about preventing future ambiguity. The README was already ambitious, but ambitious architecture fails if its terms are loose. “Cross-platform” can mean “many separate ports” or “one canonical core adapted outward.” The user clarified they wanted the latter. “No floats” can mean “no floats anywhere” or “no floats in authoritative state paths.” The chat refined it to the latter. “Lockstep/rollback” can mean two models or one reference model plus optimizations. The chat made lockstep canonical.

The main tradeoff in the determinism discussion was strictness versus practicality. A blanket no-floats rule sounds clean, but it can make renderers, editors, and analysis tools unnecessarily difficult. The chosen rule is stricter where it matters and looser where it does not. That is why the “no feedback into engine state or engine-controlled formats” boundary matters so much.

The main tradeoff in the port discussion was platform breadth versus architectural unity. Supporting DOS, Win16, macOS Classic, WASM, and modern systems could tempt a project into separate per-platform codebases. The user explicitly rejected that. The chosen approach is capability-based degradation: platforms can differ in what they expose, but not in canonical engine semantics.

The data-format reasoning was about long-term survivability. If on-disk versions can silently change meaning, old saves become unreliable. If compiler struct packing defines disk layout, cross-platform stability breaks. If content mismatches are tolerated, registries may diverge. The chosen rules avoid those risks.

The Codex workflow reasoning was practical. Codex is useful for mechanical edits, but it needs guardrails. The duplicate block it introduced became evidence that future prompts should explicitly forbid duplication and unrelated rewrites.

---

## 8. Plans, Future Work, and Next Steps

The first next step is to verify the actual repository `README.md` against the final pasted README. The chat only used pasted text. If the repository differs, future work should start from the actual file, not from memory.

The second next step is to resolve the OS/2 inconsistency. The intro says legacy systems include “OS/2 strata via shims,” but Section 9 says it is the normative platform matrix and does not list OS/2. There are two clean options: add OS/2 strata to Section 9 with the correct qualification, or remove/qualify the intro mention. This should be a small README patch.

The third next step is to clarify `/ports`. The final README says `/ports` exists only for metadata, build configs, and capability descriptors. That may satisfy the user’s statement, but it might not. If the user truly wants no `/ports` directory at all, the README and future directory contract need to change.

After that, the likely future work is spec writing. The most natural first spec is `DIRECTORY_CONTRACT.md`, because the README already says it is authoritative and because the port-directory question directly affects it. That spec should define where platform shims live, what `/ports` may contain if retained, and what is forbidden.

The next likely spec is a capability-system spec. It should define descriptors/tables, valid fields, validation rules, and the principle that capabilities cannot alter canonical simulation semantics.

A determinism spec should also follow. It should formalize no-float boundaries, RNG access, tick phases, parallel commits, lockstep networking, replay hashes, and build metadata isolation.

A data-format/versioning spec should formalize TLV encoding, explicit field sizes, endian conversion, disk versioning, migration policy, content-lock matching, and reconciliation behavior.

Possible blockers include the unresolved `/ports` question, missing access to actual repository files, and unspecified algorithms for RNG, state hashing, CRCs, and content hashing.

---

## 9. Constraints, Preferences, and Non-Negotiables

### Explicit constraints from the chat

The project constraints are strong. The engine core is C89, fixed-point, and deterministic. No floats are allowed in `/engine` or engine-controlled on-disk formats. No platform APIs belong in `/engine`. No game logic belongs in `/engine`. No hidden global state may affect determinism.

All platforms must use the same engine ABI and file formats. Ports must not fork or override engine/runtime systems. Reduced functionality must degrade gracefully and locally. This is not optional; it came from the user’s direct correction.

The reporting constraints later in the chat were also explicit: preserve facts, inferences, uncertainty, rejected options, contradictions, artifacts, prompts, and rationale. Do not invent. Do not silently infer. Do not treat assistant suggestions as user decisions unless accepted.

### Inferred preferences

The user appears to prefer precise, surgical, implementation-ready prompts over general advice. This is inferred from repeated requests for Codex prompts and the way they pasted outputs back for review.

The user also appears to prefer architecture that resists future drift. This is inferred from the focus on determinism, ports, directory structure, and spec-first documentation.

### Communication preferences

The user’s profile and instructions emphasize bluntness, rigor, directness, and fact-checking. In this chat, they repeatedly asked for high-fidelity state preservation and explicitly rejected over-compressed summaries. Future assistants should avoid vague reassurance and instead give concrete analysis, caveats, and next actions.

### Things future assistants should avoid

They should not reintroduce separate port trees, treat CP/M as a full simulation target, broaden “no floats” into “no floats anywhere,” treat rollback as an alternate canonical network model, or assume the pasted README is committed. They should not let `/ports` become a source-code directory unless the user explicitly changes direction.

---

## 10. Files, Artifacts, Outputs, and Prompts Mentioned or Created

The first important artifact was the user’s initial pasted README. It was the baseline for all review and editing. It is now superseded, but it remains useful historically because it shows what changed.

The second artifact was the assistant’s critique of that README. It identified the problems that the first Codex prompt addressed: CP/M/286 ambiguity, float-scope problems, platform-list duplication, plugin determinism, build metadata, data format versioning, and content-lock matching.

The third artifact was the first Codex prompt. It was a detailed mechanical edit prompt for the README. It should be preserved because it shows the intended changes and the prompt style that worked.

The fourth artifact was Codex’s first output, pasted by the user. It became an intermediate README. It was mostly successful but later superseded.

The fifth and most important artifact was the user’s direct port requirement: no separate port directory/system, same structure for all ports, graceful degradation, and no upstream flow. This is not just an artifact; it is a core requirement.

The sixth artifact was the second Codex prompt, which integrated unified ports. It rewrote the README’s port model around shared source hierarchy, capability descriptors, and metadata-only `/ports`.

The seventh artifact was Codex’s second output, which added the desired port language but also introduced duplicate README content. This matters as a warning about Codex failure modes.

The eighth artifact was the cleanup prompt. It removed the duplicate block, removed “embedded,” made lockstep canonical, and aligned the contributing determinism bullet with Section 2.1.

The ninth artifact was the final README pasted by the user. It is the current textual baseline, but it is unverified against the actual repository.

The later artifacts were the context transfer packet, downloadable report package, and in-chat report reader. These preserve the state of the chat for future assistants and aggregation.

Referenced but unverified repository artifacts include `README.md`, `/docs/spec/DIRECTORY_CONTRACT.md`, `/docs/spec/MILESTONES.md`, `.dominium_build_number`, `build/generated/dom_build_version.h`, and `content.lock`.

---

## 11. Open Questions and Unresolved Issues

The most important unresolved issue is the `/ports` question. The user explicitly said they did not want ports stored in a separate directory or system. The final README keeps `/ports`, but only as metadata/build-config/capability descriptors with no code or behavior. This may satisfy the intent, but it is not confirmed. Resolving this matters before editing `DIRECTORY_CONTRACT.md`.

The second major unresolved issue is OS/2. The intro lists “OS/2 strata via shims” under legacy systems. Section 9 says it is the normative platform matrix, but OS/2 is absent there. This creates an internal contradiction. The fix is simple but requires a decision: add OS/2 to Section 9 or remove/qualify it in the intro.

Another unresolved issue is where platform shims physically live if `/ports` contains no code. The README says platform-specific behavior is contained in `/runtime`, `/launcher`, and `/tools`, with shims configured via `/ports` metadata. The exact directory contract is not defined.

The capability system itself is unresolved. The README names capability tables/descriptors but does not define schema, validation, or limits. This matters because capability descriptors must not become a hidden behavior system.

The determinism algorithms are unresolved. The README mentions replay hashes and RNG streams, but not exact algorithms, serialization formats, or hash input definitions.

Data-format details are unresolved. The README describes region/chunk structures conceptually but not exact binary layout, TLV encoding, CRC algorithms, content hashes, or migration tooling.

Finally, the actual repository state is unverified. The final README was pasted in chat, but no repository file was inspected.

---

## 12. Risks, Failure Modes, and Things Future Chats Might Get Wrong

A future assistant might treat metadata-only `/ports` as fully confirmed. That would be unsafe. It should be marked unresolved until the user confirms it or the directory contract is explicitly accepted.

A future assistant might reintroduce separate port systems, especially if it sees a `/ports` directory and assumes it should contain per-target code. That would violate the user’s clearest architecture correction.

A future assistant might collapse the floating-point rule into “no floats anywhere.” That would be wrong. The correct rule is no floats in authoritative simulation or engine-controlled formats; non-authoritative renderers/tools may use floats if there is no feedback.

Another risk is treating rollback as an alternate canonical network model. The final README makes lockstep canonical and rollback/prediction convergent optimizations.

A future assistant might assume the final README is committed to the repository. It is not verified. The actual file must be checked before making further edits.

A future assistant might ignore the OS/2 inconsistency because it is small. But because Section 9 is normative, small platform-list mismatches matter.

Codex could also repeat its earlier failure and duplicate README sections. Future prompts should explicitly prevent broad rewrites and duplication.

A future aggregator might merge this chat into a project spec too aggressively. In particular, `/ports` metadata-only should not become a final formal requirement until the user confirms that retaining `/ports` is acceptable.

---

## 13. What This Chat Contributes to the Larger Project

This chat contributes a refined architectural baseline for the Dominium/Domino README. It should inform a future Project Spec Book in several areas.

For the architecture overview, it contributes the Domino/Dominium separation and the README/spec hierarchy.

For the determinism chapter, it contributes the no-float boundary, RNG discipline, tick-phase rules, deterministic parallel commits, lockstep-first networking, and build metadata isolation.

For the platform/portability chapter, it contributes the most unique material: all platforms must share one source hierarchy, ports must not fork or override engine/runtime systems, and reduced functionality must degrade locally through capability systems without affecting canonical behavior.

For the repository layout chapter, it contributes the unresolved metadata-only `/ports` model and the need to formalize it in `DIRECTORY_CONTRACT.md`.

For the data-format chapter, it contributes immutable disk versions, explicit layouts, no platform-specific packing pragmas, little-endian canonical representation, and fatal `content.lock` mismatch.

For the mod/plugin chapter, it contributes the rule that binary plugins are bound by the same determinism constraints as core.

Some material likely overlaps with other chats: world scale hierarchy, save formats, deterministic tick phases, modding, and platform matrix. The unique part is the user’s port correction and the resulting capability-based degradation model.

The biggest conflict to watch for in other chats is any older plan that placed per-platform code, build flows, or alternative implementations under `/ports/<target>`. That should be treated as superseded unless the user later reverses course.

---

## 14. What I Should Remember

* The main artifact was the Dominium/Domino root README.
* The README is descriptive; `/docs/spec` is normative.
* Domino is the deterministic engine core; Dominium is the official game/runtime/tooling layer.
* The full engine targets 286-class-and-newer systems.
* CP/M-80/86 is limited tooling/frontends only, not complete world simulation.
* Undefined “embedded” was removed from the future systems list.
* No floats are allowed in `/engine` or engine-controlled on-disk formats.
* Floats are allowed in non-authoritative tools/renderers only if they never feed back into engine state or engine-controlled formats.
* RNG streams may only advance during deterministic tick phases.
* Tick phases are immutable, future-tick scheduling goes through Pre-State, and parallel commits must be deterministic.
* Lockstep is the canonical network model; rollback/prediction must converge to lockstep.
* The user explicitly rejected separate port directories/systems.
* All platforms should share one unified source hierarchy.
* Reduced platform functionality must degrade gracefully and must not flow upstream.
* The final README keeps `/ports` as metadata-only, but this may need confirmation.
* OS/2 appears in the intro but not in Section 9’s normative platform matrix; this is unresolved.
* Existing disk versions are immutable contracts.
* `content.lock` mismatches are fatal until reconciled.
* Codex can help with mechanical edits but must be constrained to avoid duplication and semantic drift.
* The next practical step is to verify the actual repository README, resolve OS/2, and clarify `/ports`.

---

## 15. Best Questions I Can Ask Next in This Chat

1. “Explain the `/ports` ambiguity and give me the cleanest architecture options.”
2. “Give me a Codex prompt to fix the OS/2 Section 9 inconsistency.”
3. “Draft the `DIRECTORY_CONTRACT.md` language implied by this chat.”
4. “Write a capability-system spec outline based on the port decision.”
5. “Explain the determinism boundary in a way I can paste into a spec.”
6. “What exact README sentences are still risky or ambiguous?”
7. “Which decisions from this chat should become formal requirements?”
8. “Which items are unsafe to merge into a Project Spec Book without confirmation?”
9. “Generate a checklist for reviewing Codex output against this chat’s decisions.”
10. “Summarize the final README changes compared with the original README.”

---

## 16. Final Plain-English Summary

This chat was about making the Dominium/Domino README more precise, more internally consistent, and more resistant to future architectural drift. The README described a deterministic, integer-math, multi-platform simulation game and engine. Domino is the engine core; Dominium is the official game/runtime/tooling layer. The user wanted the README reviewed, then wanted Codex prompts to apply fixes, then later wanted all decisions preserved in handoff/report form.

The first major phase was critique. The README was already strong, but several risks were identified. It claimed 286-class support while also mentioning CP/M-80/86. It banned floating point too broadly. It had repeated platform/backend lists that could drift. It needed stronger wording around plugin determinism, build metadata, content locks, and immutable data formats. The assistant proposed fixes, and the user asked for a Codex prompt. That prompt instructed Codex to apply surgical README edits: clarify CP/M as limited tooling/frontends, narrow the no-float rule, add RNG discipline, strengthen tick-phase and parallelism wording, mark terrain caches non-canonical, make build numbers diagnostic only, make content-lock mismatches fatal, and make Section 9 the normative platform/rendering matrix.

Codex produced a mostly correct revised README. The assistant reviewed it and identified only minor remaining issues. Then the user made the most important correction of the whole chat: they did not want ports stored in a separate directory or system. All ports should work within the same structure, and reduced functionality should degrade gracefully without flowing upstream. This changed the architecture. The project should not have separate per-platform source trees or alternate implementations. All platforms should build from one unified source hierarchy. Platform differences should be expressed through thin shims, compile-time flags, and capability descriptors. Reduced rendering or UX fidelity is acceptable, but canonical simulation behavior must not change.

A second Codex prompt encoded this unified-ports architecture. It allowed `/ports` only as optional metadata, capability descriptors, and build configurations, with no engine/runtime source code or behavior. Codex applied the port language but accidentally duplicated part of the top README. A cleanup prompt removed the duplicate block, removed undefined “embedded,” made lockstep the canonical network model, and aligned the contributing determinism bullet with Section 2.1.

The final README now says the full engine targets 286-class-and-newer systems, while CP/M-80/86 is limited tooling/frontends only. It says no floating point is allowed in canonical simulation mutation paths or engine-controlled serialized formats, and no `float` or `double` in `/engine` or engine-controlled on-disk formats. It allows floats in tools/renderers/non-authoritative analysis only if they never feed back into engine state or engine-controlled formats. RNG streams advance only during deterministic tick phases. Tick phases are immutable. Parallel commits must be deterministic. The canonical network model is lockstep, and rollback/prediction must converge to lockstep.

The final README also says existing disk versions are immutable contracts, layout changes require new versions and migration paths, platform-specific struct packing pragmas cannot define canonical formats, and `content.lock` mismatches are fatal until reconciled. It says all platforms build from the same unified source hierarchy, ports cannot fork or override engine/runtime systems, and `/ports` contains only metadata/build configs/capability descriptors if retained.

Two important issues remain unresolved. First, the user’s wording may mean they do not want a `/ports` directory at all, not even metadata-only. The final README keeps `/ports` in a restricted form, but this should be confirmed before writing the directory contract. Second, the intro mentions “OS/2 strata via shims,” but Section 9 is the normative platform matrix and does not list OS/2. That contradiction needs a small README patch.

After the README work, the user asked for preservation outputs: a maximum-fidelity context transfer packet, a downloadable report package, and an in-chat reader. Those were created to make this chat reusable later. But the substance to remember is the architecture: deterministic engine boundaries, spec-first documentation, unified ports, capability-based degradation, lockstep-first networking, immutable data formats, and the unresolved `/ports` and OS/2 questions.

The next assistant should not reintroduce separate port systems, should not treat CP/M as a full simulation host, should not simplify the float rule incorrectly, should not assume the final README is committed, and should not merge metadata-only `/ports` into a future spec without confirmation. The best next action is to verify the actual repository `README.md`, resolve the OS/2 mismatch, confirm `/ports` semantics, and then update `DIRECTORY_CONTRACT.md` and a capability-system spec.

# Reader Status

* Chat title: Dominium README Architecture, Ports, and Determinism
* Report type: human-readable explanatory report
* Main value of this chat: it captures the README refinement and the user’s major architectural correction that ports must use one unified structure with graceful capability-based degradation.
* Most important decision: all platforms/ports must share one unified source hierarchy; ports must not become separate systems or divergent implementations.
* Most important unresolved issue: whether metadata-only `/ports` is acceptable or whether the user wants no `/ports` directory at all.
* Most important next action: verify the repository README, then resolve the OS/2 platform-matrix inconsistency and clarify `/ports` before editing normative specs.
* Safe to use for later aggregation: with caveats
* Main caveats: actual repository files were not inspected; referenced spec files were not verified; `/ports` semantics remain partly uncertain; OS/2 appears in the intro but not in Section 9’s normative matrix.
