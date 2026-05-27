# COMPLETE CHAT PRESERVATION REPORT — Dominium OS-like Architecture, Repository Convergence, and Interface Operating Layer

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium OS-like Architecture, Repository Convergence, and Interface Operating Layer |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial |
| Previously generated files available? | No previously generated preservation files visible in this chat before this task |
| Uploaded files or artifacts present? | Yes — `Pasted text.txt` contains the preservation/export prompt for this task |
| Contains future plans? | Yes |
| Contains decisions? | Yes, mostly tentative architecture decisions and accepted directions |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium |
| Extraction confidence | 4/5 |
| Safe for later aggregation? | Yes, with caveats |
| Main limitations | I can see the visible transcript and the loaded preservation prompt. I cannot guarantee access to every historical turn if the interface omitted earlier messages. I also cannot see a `docs.zip` attachment in the currently loaded file set. Repository facts were taken from prior tool-accessed live GitHub files during this chat, but those should be treated as observations made during the chat, not necessarily current as of all future dates. |

Plain-language limitation note: this report preserves the visible conversation and the supporting repository/file evidence surfaced during the chat. It should not be treated as a complete audit of every file in `/docs` oldest-to-newest; the connector did not provide a chronological full-docs walk. It is nevertheless a high-fidelity preservation of the architectural discussion that actually occurred here.


## 1. One-Page Orientation

This chat was about rethinking Dominium from a conventional game project into a much broader, more modular, deterministic, extensible software environment. The user repeatedly asked whether the current plan was the best possible version, and the discussion evolved from GUI/binary planning, to repository restructure, to release/package strategy, to code-vs-data analysis, to an “OS-like” deterministic simulation operating environment, and finally to a unified Interface Operating Layer and Workbench platform.

The user’s underlying objective was not simply to clean folders or choose GUI frameworks. The larger goal was to preserve the long-term ambition of Dominium: a deterministic, moddable, inspectable, replayable universe platform where client, server, launcher, setup, tools, Workbench, packs, validation, release, and agent workflows all share common contracts. The user was concerned that the existing code and docs were extensive but not yet aligned with the vision, and that early wrong decisions could create brittle product architectures, GUI drift, duplicated command systems, or a repo that looked cleaner while remaining conceptually confused.

The conversation began from an earlier baseline: CLI should always work, TUI should be expected, and multiple native or rendered GUI shells should be thin, replaceable frontends over a stable backend/UI contract. Windows, macOS, Linux, and Android lanes were discussed, including legacy/modern toolchains and compatibility floors. The chat then moved into repository convergence: the user wanted to know whether a generic `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `tools/` style structure was enough. The answer became more nuanced: the repository should be organized by architectural ownership and contract boundaries, not by topic folders or temporary product categories. The key split became contracts, engine/kernel, game/domains, runtime/services/drivers, apps/userland products, content/packs, tools/dev tooling, and release/distribution.

A major shift happened when the user asked whether to recycle the repo into something “closer to an OS than to a game.” That became the strongest conceptual reframing. The proposed target was not a literal hardware operating system, but a deterministic simulation operating environment: a kernel-like substrate, contracts as law, services, drivers, domain modules, apps as userland shells, packages/content as mounted data, and proof/replay/release around everything. This reframing made the client no longer “the game” but one shell over the environment; the server another authoritative shell; launcher/setup/tools additional userland apps; and Workbench a major self-hosting proof surface.

The later part of the chat narrowed into UI/UX. The user presented a detailed plan for abandoning the old UI Editor / Tool Editor product and instead creating a rendered cross-platform Dominium Workbench / Tools Host. The answer refined this into a broader Interface Operating Layer: one command/result/refusal/document/event spine with multiple projections: CLI, TUI, rendered GUI, headless report mode, and optional native wrappers later. This would support launcher, setup, client HUDs, server admin, Workbench modules, validation dashboards, pack tools, modding tools, release tooling, renderer sandboxes, replay viewers, and agent work boards. The key product principle is that UI projections do not own semantics; every action goes through commands, capabilities, services, typed results, diagnostics, and evidence.

The future relevance of this chat is high. It contributes the conceptual bridge between repository convergence and product architecture. It also clarifies that the desired MVP should not be a shallow gameplay demo, but a proof spine: boot product binaries, unify command dispatch, mount/validate packages, create/load a universe, render a deterministic no-assets view, accept one lawful intent, commit state, emit event/replay/proof artifacts, and replay to the same hash. Future assistants must understand that many suggestions were architectural directions rather than fully accepted final decisions; they should preserve uncertainty, avoid overclaiming implementation status, and keep the current repo’s post-CONVERGE authority stack in mind.


## 2. The Story of the Conversation

### 2.1 Starting point: GUI and binary lanes

The chat began with a transfer-style discussion of GUI and binary rebuild strategy. The starting architecture was that every product should always support CLI, should be expected to support TUI, and may have modular GUI shells. Native GUI families would vary by host and era: Win32/WinForms/WinUI on Windows, AppKit/SwiftUI on macOS, fewer GUI families on Linux, and Android treated as a distinct mobile host family. The important conclusion was that GUI shells must remain thin adapters over the same product backend and command/UI contract used by CLI and TUI.

### 2.2 Repository restructure and convergence

The user then asked how to actually do the work, given the rough repo state. The assistant inspected live repository documentation and code through the GitHub connector. The existing docs already contained many convergence ideas: AppShell, product boundaries, entrypoint maps, future layout proposals, distribution and versioning models, and later post-CONVERGE repository layout docs. The conversation concluded that the repo was not simply missing ideas; it had too many partially overlapping architecture documents and needed convergence around a single ownership model.

The current source-root authority after the repo’s CONVERGE series was identified as `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`, with `sdk/` and `examples/` as optional future roots. The chat stressed that older stale layout docs should not override the machine-readable layout contract and post-CONVERGE docs.

### 2.3 Shipping, versions, packages, installers

The discussion moved to what binaries, executables, packages, and setups should ship. The strongest model was layered packaging: canonical `.dompkg` component packages, install profiles, assembled distribution trees, thin OS-native installer wrappers, and release manifests/index/archive records. The answer recommended public deliverables such as full bundles, server bundles, tools bundles, symbols/debug artifacts, release metadata, and component feeds. It warned not to make raw binaries the primary release unit and not to make installer wrappers own install logic.

### 2.4 Old/new platform compatibility and binary matrix

The user asked whether to ship old and modern binaries per OS, and proposed very broad support from Win95/NT4, .NET 2.0, Mac OS 8.6 Carbon, Mac OS X 10.6, Linux 3.x/GTK, and modern WinUI/AppKit lanes. The assistant accepted the compatibility-lane idea but rejected the universal all-products/all-era matrix as too broad. The better model was legacy/compat/modern lanes with explicit support tiers. In particular, `.NET 2.0` was discouraged as an old Windows default; Win32 C/C++ was preferred for old setup/server surfaces.

### 2.5 What current code really does

The user asked how the current repo code actually works: code vs data, hardcoded vs data-driven, modularity, extensibility, modding, and alignment with archived documentation. The assistant inspected key repo files: client CMake, client main, client shell, command registries, session pipeline/stage registry, runtime app, engine/game CMake, product registry, code/data report, modularity proof, audio and render backends. The conclusion was blunt: current code is modular by build/source architecture and partly data-driven through registries/contracts/packs, but not yet deeply moddable or runtime-extensible from boot to playable world. The client has many hard-coded transitional slices: CLI help, command descriptors, session stages, interaction objects, UI overlay, software glyphs, and null audio. The vision is present in docs and scaffolding, but runtime proof remains partial.

### 2.6 OS-like reframing

The user then proposed recycling everything into a system closer to an OS than a game. This was treated as the strongest reframing: Dominium should be a deterministic simulation operating environment, not literally an OS and not merely a game engine. The analogy mapped OS concepts to Dominium concepts: kernel, syscalls, processes, drivers, filesystem, packages, users/permissions, shell, services, logs. The proposed architecture became contracts + engine/kernel + services + drivers + domains + apps + packs + proof/release.

### 2.7 Workbench and interface platform

The user then introduced a new specific direction: abandon the old UI Editor / Tool Editor and build a cross-platform rendered Domino/Dominium tools environment using the same runtime, renderer, UI, command, pack, and data systems as the client. The assistant accepted this but tightened it: the Workbench should be a modular userland tools host, not a monolithic editor, and shipped tool modules should not live under repo-only `tools/`. A critical correction was that AppShell currently says rendered mode is client-only, so rendered mode must become product-declared by capability and contract.

The final refinement was even broader: the Workbench should not be the platform; it should be the largest proof surface for a reusable Interface Operating Layer. That layer provides one command/result/refusal/document/event spine and projects it into CLI, TUI, rendered GUI, headless JSON/report mode, and optional native wrappers. The guaranteed UI floor should work without assets, GPU, icons, fonts, sounds, themes, or optional modules. Richer assets can later be validated, packable, and replaceable.


## 3. Main Topics Discussed

### Topic 1 — GUI and frontend architecture

The chat discussed how Dominium should handle GUI across products and platforms. The conclusion was that CLI is mandatory, TUI is expected, and GUI shells are modular adapters. This avoids forcing one universal GUI framework across all host eras. Windows can have Win32/WinForms/WinUI lanes; macOS can have AppKit/SwiftUI lanes; Linux should have fewer GUI families; Android is separate. The important memory is that GUI technology is not product architecture. Product behavior belongs behind shared commands/contracts.

### Topic 2 — Repository convergence and ownership

The repo discussion established that physical layout should reflect architectural ownership, not simulation topics or product history. The current target roots are apps, engine, game, runtime, contracts, content, docs, tests, tools, scripts, cmake, external, release, and archive. Domain roots should split across contracts/game/content/docs/tests. The current post-CONVERGE docs are the layout authority; older docs may be historical or stale. This topic matters because platform/render/native GUI expansion should not proceed over root-folder chaos.

### Topic 3 — Shipping, versioning, packaging, and distribution

The chat discussed shipping bundles and packages. The best model was deterministic component packages, install profiles, assembled bundles, thin setup wrappers, manifests, release indexes, archive history, and offline verification. Versioning should stay layered: suite version, product version, protocol/schema/format versions, semantic contract hashes, build IDs, artifact hashes, release-control-plane IDs, target families, and exact target descriptors. The conversation rejected treating filenames or one SemVer string as truth.

### Topic 4 — Platform and binary compatibility lanes

The user explored very old and modern targets. The answer kept the compatibility-lane strategy but warned against making every product ship every lane. The future should distinguish official, compatibility, experimental, and preservation/retro targets. Old Windows should use native Win32 where possible rather than .NET 2.0. macOS old-host support implies frozen toolchains. Linux target descriptors must include more than kernel version.

### Topic 5 — Current code/data reality

A central part of the chat examined how the current code actually behaves. The repo has native product targets and libraries, but product boot proof remains partial. Engine/game/runtime/client boundaries exist at build level. Data registries exist. However, runtime command dispatch is not yet fully unified, UI is minimal, audio is null, and many client surfaces are hard-coded. Current code is scaffold-heavy and doctrine-rich, but not yet a fully data-driven MVP.

### Topic 6 — OS-like deterministic simulation environment

The biggest conceptual change was viewing Dominium as a deterministic simulation operating environment. Engine becomes kernel-like substrate; contracts become system law; runtime services become OS services; drivers are platform/render/audio/input/network/storage adapters; game domains are installed domain modules; apps are userland shells; packs are mounted data; replay/proof/release wrap the whole system. This framing integrates the ambitions better than “game plus engine.”

### Topic 7 — Workbench / Studio / Tools Host

The old UI Editor/Tool Editor idea was superseded by a modular Dominium Workbench. The Workbench should be rendered, cross-platform, and built on the same runtime as the client. It should have a module registry, command palette, diagnostics/log panels, validation dashboard, pack browser, UI/HUD sandbox, renderer sandbox, replay/trace viewer, release forge, agent work board, and later material/process editors. It should not be a Visual Studio replacement or one giant editor.

### Topic 8 — Interface Operating Layer

The final topic turned the Workbench idea into a general Interface Operating Layer. The core is one command/result/refusal/document/event spine with projections into CLI, TUI, rendered GUI, headless report mode, and native wrappers later. Everything user-visible should pass through command/capability/service/result/diagnostic/evidence paths. The no-assets GUI becomes the guaranteed floor, not a weak fallback. The Workbench becomes the largest dogfooding surface for this layer.


## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted to determine whether the current architecture was the best possible version; how to refactor the repo; what binaries, setups, packages, and distributions to ship; how modular/data-driven the current code is; whether the code aligns with the project vision; whether Dominium should be more OS-like than game-like; and whether the Workbench/UI direction could produce a complete cross-product interface platform.

### 4.2 Inferred Goals

INFERENCE: The user wanted long-term architectural leverage rather than short-term MVP shortcuts. The recurring concerns were modularity, extensibility, compatibility, modding, future-proofing, robustness, auditability, data-driven behavior, and avoiding duplicated GUI/product logic. The user also appears to want a foundation that can become self-hosting in spirit: a Workbench that uses Dominium systems to create, validate, package, and prove Dominium artifacts.

### 4.3 Goals That Changed Over Time

The goal changed from “which GUI/binary lanes should we use?” to “how should the repo converge?” to “how does code actually work?” to “should Dominium be an OS-like deterministic operating environment?” to “can we build a unified Interface Operating Layer?” The trajectory moved upward in abstraction while becoming more concrete about proof requirements.

### 4.4 Goals Still Unresolved

The unresolved goals are implementation-level. The repo still needs command dispatch unification, product boot proof, portable projection proof, AppShell rendered-mode law update, Workbench module contracts, document/patch/result/refusal schemas, and a boot-to-replay MVP. It also needs continued exception retirement, CTest/RepoX remediation, and verification of current build status.


## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | CLI mandatory, TUI expected, GUI modular | Accepted direction | Prevents product behavior from being owned by GUI frameworks | High | FACT |
| DECISION-02 | GUI shells must be thin over shared contracts | Accepted direction | Prevents feature drift and duplicate product architectures | High | FACT/INFERENCE |
| DECISION-03 | Repo structure should follow ownership boundaries | Accepted direction | Avoids domain/root chaos and supports future validation | High | FACT |
| DECISION-04 | Use post-CONVERGE roots as current layout authority | Accepted as repo fact | Prevents stale docs from overriding current contract | High | FACT |
| DECISION-05 | Treat Dominium as deterministic simulation operating environment | Strong accepted direction | Better fits kernel/contracts/services/drivers/domains/apps/packs model | Medium-high | INFERENCE |
| DECISION-06 | Workbench should be modular Tools Host, not monolithic editor | Accepted direction | Avoids old UI Editor mistake | High | FACT/INFERENCE |
| DECISION-07 | Interface Operating Layer should underlie all products | Strong direction | Makes CLI/TUI/rendered/headless projections share semantics | Medium-high | INFERENCE |
| DECISION-08 | Rendered mode must become product-declared, not client-only | Proposed requirement | Required for Workbench rendered GUI to be lawful | Medium | INFERENCE |
| DECISION-09 | Shipped tool modules should not live under repo-only `tools/` | Proposed requirement aligned with repo docs | Prevents runtime dependency on developer tooling | High | FACT/INFERENCE |
| DECISION-10 | No-assets GUI is guaranteed floor | Accepted direction | Ensures recovery/product usability without optional assets | High | FACT/INFERENCE |
| DECISION-11 | Package/distribution should be layered and deterministic | Accepted direction | Supports offline verification, rollback, reproducibility | High | FACT |
| DECISION-12 | Avoid arbitrary native plugins early | Proposed direction | Reduces trust/safety/replay risks | Medium | INFERENCE |


### Decision explanations

**DECISION-01 — CLI mandatory, TUI expected, GUI modular.** This was part of the initial architecture baseline and was repeatedly reaffirmed. It matters because every product must remain operable in recovery/headless/automation contexts. GUI is allowed but not authoritative.

**DECISION-02 — Thin GUI shells over shared contracts.** The chat consistently rejected GUI families becoming separate product architectures. This affects client, launcher, setup, server admin, tools, and Workbench modules.

**DECISION-03 — Repo ownership layout.** The user pushed for repository convergence; the discussion established that folders should map to ownership and contract boundaries. This decision is final enough to guide work, but details remain subject to machine-readable layout contracts.

**DECISION-04 — Current post-CONVERGE authority.** The final audit and layout target docs define current roots and authority stack. Older docs remain context but not current physical-layout authority.

**DECISION-05 — OS-like deterministic operating environment.** The user proposed this framing and the assistant endorsed it. It is not a literal OS decision; it is a conceptual architecture decision. It should be formalized before implementation.

**DECISION-06 — Workbench modular host.** The user explicitly accepted the idea of one integrated environment with many focused modules. This supersedes the old UI Editor / Tool Editor final-product plan.

**DECISION-07 — Interface Operating Layer.** The final UI discussion generalized Workbench into a cross-product interface platform. This is a strong direction, but it should be formalized as doctrine and contract work before being treated as implemented.

**DECISION-08 — Rendered mode product-declared.** This was an assistant correction based on AppShell docs. It is necessary because current AppShell docs say rendered mode is client-only. User has not yet separately confirmed the doctrine change, so treat it as a required proposed decision.

**DECISION-09 — Keep shipped modules out of repo-only `tools/`.** This follows repo ownership rules. The Workbench’s shipped modules should live under `apps/tools/modules/` or equivalent, while developer validators/codegen/audit tooling remains under `tools/`.

**DECISION-10 — No-assets GUI floor.** The UI baseline doc already requires a zero-asset GUI floor. The chat expanded this into a product-grade primitive UI system.

**DECISION-11 — Deterministic layered packaging.** The chat recommended component packages, install profiles, distribution trees, thin installer wrappers, release manifests and indexes. This aligns with release/distribution docs.

**DECISION-12 — Avoid arbitrary native plugins early.** This is a risk-management choice. Early modules should be built-in or data-described; later IPC/WASM/script/native extensions require trust and sandbox policy.


## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

1. **One universal GUI framework for all hosts.** Rejected because long-lived Dominium needs native/near-native families and compatibility lanes.
2. **One GUI per OS version.** Rejected as matrix explosion. The better model is compatibility lanes and visual profiles.
3. **Generic game repo layout without Dominium-specific ownership rules.** Superseded by ownership-root and domain-split doctrine.
4. **Old UI Editor → Tool Editor as final product.** Superseded by modular Dominium Workbench and later Interface Operating Layer.
5. **One monolithic “everything editor.”** Rejected. The Workbench should be a shell plus modules.
6. **OS-native widgets as the core tools strategy.** Deprioritized. Rendered UI using Dominium runtime should be first; native wrappers later.
7. **Visual Studio/Xcode replacement as immediate goal.** Rejected. Workbench is self-hosting in spirit, not a full IDE replacement.
8. **.NET 2.0 as old Windows GUI default.** Rejected/deprioritized in favor of native Win32 for old setup/server surfaces.
9. **Raw binaries as primary release unit.** Rejected in favor of deterministic package/profile/bundle/release-manifest model.
10. **Arbitrary native plugin marketplace early.** Deprioritized until trust/capability/sandbox law exists.
11. **Treating the client as the game.** Superseded by client as userland shell over deterministic operating environment.
12. **Treating Workbench as the whole platform.** Superseded by Interface Operating Layer; Workbench is a host/proof surface.


## 7. Important Reasoning, Rationale, and Tradeoffs

The central tradeoff was between short-term visible functionality and long-term architectural leverage. The user repeatedly asked whether the plan could be more modular, future-proof, optimized, robust, reliable, useful, and powerful. The answer consistently favored building shared contracts and proof paths before expanding product surfaces.

The repo’s current state shaped the reasoning. It already has rich documentation, validators, contracts, registries, and build targets, but current runtime code remains partially hard-coded. Therefore, the best strategy is not greenfield invention nor continuing the old product/UI plan; it is recycling existing code through stronger contracts, services, generated descriptors, and proof gates.

Another tradeoff was between data-driven runtime flexibility and deterministic portability. The conversation did not recommend arbitrary scripting everywhere. It recommended descriptor-driven systems, validation, deterministic code generation, static/built-in modules first, and richer plugin forms only after trust/capability policy matures.

For UI, the tradeoff was between polish through assets and guaranteed recoverability. The chat chose a strong no-assets floor: built-in primitives, text, layout, and software rendering should produce a complete product-grade experience even when packs/themes/fonts/GPU/sound are missing. Richer assets are optional validated packs later.

For repository architecture, the tradeoff was between intuitive names and actual ownership. The chat chose ownership and contract boundaries over topical roots. That is less immediately pretty, but it prevents architecture drift and makes validators possible.


## 8. Plans, Future Work, and Next Steps

### 8.1 Immediate proof-spine work

1. Remediate or classify remaining RepoX/CTest drift.
2. Repair canonical verify test discovery.
3. Ensure native product binaries boot.
4. Fix or classify setup Python bridge compatibility, missing `dist/bin/dom`, and server CLI arg forwarding.
5. Prove portable projection assembly with required manifests.
6. Rerun product boot and portable projection proof.

These are blocking because current docs still classify product boot and portable projection proof as partial or blocked.

### 8.2 Interface-law work

1. Write `INTERFACE-LAW-00`.
2. Update AppShell rendered-mode law so rendered mode is product-declared.
3. Define command/result/refusal/document/patch/module/theme/diagnostic/evidence schemas.
4. Ensure UI projections do not own product semantics.

### 8.3 Command-service unification

Create one dispatch path used by CLI, TUI, rendered GUI, and headless report mode. Acceptance test: same command, same result, same refusal, same diagnostics, different presentation.

### 8.4 Workbench shell

Build a minimal rendered Workbench shell with software renderer, module registry, command palette, console overlay, log/diagnostics panel, and first module.

### 8.5 First modules

Recommended order: Validation Dashboard, Pack Browser, Renderer Sandbox, UI/HUD Sandbox, Replay/Trace Viewer, Release Forge, Agent Work Board.

### 8.6 Boot-to-replay MVP

The true MVP should boot, mount a base package, load/create a world, render a deterministic view, accept one intent, commit a lawful transition, emit event/replay/proof, and replay to the same hash.


## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

- The user wants direct, source-grounded, audit-ready answers.
- The user wants uncertainty labels and correction of incorrect framing.
- The user wants human-readable explanations, not only machine-readable handoffs.
- This preservation task specifically required FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels, stable IDs, registers, spec sheets, an aggregator packet, self-audit, and downloadable files if tools are available.
- The source scope is this chat only unless external project context is labelled.
- Future facts involving platforms, software support, toolchains, APIs, laws, schedules, prices, current roles, etc. require verification.

### 9.2 Inferred Constraints and Preferences

- INFERENCE: The user prefers architectural correctness over quick demos.
- INFERENCE: The user wants future assistants to preserve reasoning and not collapse tentative ideas into final decisions.
- INFERENCE: The user values modularity, extensibility, determinism, compatibility, and long-term maintainability.
- INFERENCE: The user wants usable product concepts, not just abstract architecture.

### 9.3 Uncertain or Unestablished Preferences

- UNCERTAIN: Whether the user wants to rename `engine` conceptually to `kernel` in code, or only use kernel as a conceptual layer.
- UNCERTAIN: Whether the final public product name should be Dominium Workbench, Dominium Studio, Domino Workbench, or something else.
- UNCERTAIN: How aggressive the next actual code refactor should be versus staged adapters and codegen.


## 10. Files, Artifacts, Outputs, and Prompts

Important artifacts in or referenced by this chat:

1. **Uploaded `Pasted text.txt`.** Contains the preservation/export prompt that generated this package.
2. **Repo docs inspected during chat.** Key examples: AppShell constitution, GUI baseline, repo layout target, ownership rules, domain split rules, final convergence audit, post-CONVERGE next steps, versioning/distribution docs, code/data report, modularity proof, product boot proof.
3. **GitHub repository references.** The repo `Julesc013/dominium` was inspected via GitHub connector.
4. **Conceptual artifacts produced in chat.** These include proposed architectures, matrices, lane plans, Workbench modules, Interface Operating Layer, boot-to-replay MVP, and structured roadmaps.
5. **This preservation package.** Newly generated files and ZIP at the end of this task.

No prior downloadable handoff ZIP from this chat was visible before this task. The earlier user mentioned a `docs.zip`, but no such file was available in the currently loaded file set.


## 11. Open Questions and Unresolved Issues

1. Should `engine` remain the physical name while being conceptually treated as kernel, or should a future rename be considered?
2. What exact schema should define `module_descriptor_v1`?
3. How should rendered-mode capability law be updated without breaking existing AppShell doctrine?
4. Which command registry becomes the single runtime authority?
5. How should existing hard-coded client commands, session stages, and interaction definitions be externalized?
6. What is the first real Workbench module: Validation Dashboard or Pack Browser?
7. Which product boot blockers are still current after the latest repo commits?
8. How much of the current game/domain code should be salvaged into domain interpreters versus rewritten?
9. What plugin tiers are acceptable after built-in/data-described modules?
10. What is the exact boot-to-replay MVP artifact set?
11. How should future reports from other old chats be reconciled against this one?


## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

Future assistants might overstate implementation status. Much of this chat defines direction, not completed code. Product boot and portable projection proof were partial/blocked in inspected docs.

A future assistant might treat Workbench as the platform. The correct model is Interface Operating Layer as platform; Workbench is a major host/proof surface.

A future assistant might recreate the old UI Editor mistake by building a monolithic GUI-only tool. The correct model is command/document/result-driven modules with CLI/TUI/rendered/headless parity.

A future assistant might put shipped runtime modules under repo-only `tools/`. The ownership rules prohibit runtime/product code depending on developer tooling.

A future assistant might ignore the rendered-mode law conflict. Current AppShell docs say rendered mode is client-only; Workbench needs a deliberate law update.

A future assistant might treat all old platform compatibility targets as near-term release targets. The chat distinguished official, compatibility, experimental, and preservation lanes.

A future assistant might forget the no-assets floor. The UI must work without optional assets, fonts, GPU, sound, themes, modules, or packs.

A future assistant might merge tentative assistant proposals as user decisions. Preserve status labels.


## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat should feed several chapters of a future Project Spec Book:

- Repository and ownership architecture.
- Deterministic simulation operating environment doctrine.
- AppShell and product shell model.
- Interface Operating Layer and UI/UX platform doctrine.
- Workbench/productivity environment design.
- Packaging/versioning/distribution model.
- Platform/binary compatibility lanes.
- Code-vs-data and modding/extensibility strategy.
- MVP/proof spine and boot-to-replay definition.
- Risk management and rejected options.

The unique contribution is the synthesis: Dominium should not be framed only as a game or editor suite; it should be a deterministic operating environment with a reusable interface layer. This likely overlaps with other chats on worldgen, domain realism, UI tools, release packaging, and repo convergence. Conflicts to watch: product names, physical directory names, toolchain/platform targets, and how aggressive the OS-like refactor should be.


## 14. What I Should Remember

- Dominium’s strongest architecture is a deterministic simulation operating environment, not just a game.
- The current source-root authority is post-CONVERGE: apps, engine, game, runtime, contracts, content, docs, tests, tools, scripts, cmake, external, release, archive.
- GUI shells must not own product semantics.
- CLI, TUI, rendered GUI, and headless modes should project the same command/result/refusal/document spine.
- Workbench should be a modular userland app over the Interface Operating Layer, not a monolithic editor.
- No-assets rendered UI is the guaranteed floor, not a weak fallback.
- Current code is scaffold-rich but not yet fully data-driven or deeply moddable at runtime.
- Product boot proof, portable projection proof, command unification, and AppShell law updates remain critical.
- Treat many items as direction unless the user explicitly accepted them as final.


## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- “Explain the difference between Dominium as a game, engine, OS-like environment, and Interface Operating Layer.”
- “What were the most important shifts in direction across this chat?”

### 15.2 Decisions
- “Which decisions are final enough to implement, and which need confirmation?”
- “What does rendered-mode product-declared law need to say?”

### 15.3 Tasks and Next Actions
- “Turn the next-action sequence into concrete PR-sized tasks.”
- “Draft INTERFACE-LAW-00.”

### 15.4 Artifacts and Files
- “Which repo docs should be promoted into the master spec book?”
- “Which files from this preservation package should I combine with other chat reports?”

### 15.5 Risks and Verification
- “Audit the risk that Workbench becomes another monolithic editor.”
- “What repository facts need re-verification before coding?”

### 15.6 Future Spec Book / Aggregation
- “Convert this report into a master-spec chapter outline.”
- “Compare this chat’s decisions against another old-chat report.”

### 15.7 Deep-Dive Questions Specific to This Chat
- “Design `module_descriptor_v1`.”
- “Design the unified command/result/refusal model.”
- “Design the no-assets UI control set.”
- “Define the boot-to-replay MVP acceptance tests.”


## 16. Compact Human Summary

This chat was about turning Dominium from a sprawling game/engine/tooling project into a coherent deterministic platform. The user repeatedly asked whether the plan was the best possible version and pushed for more modularity, extensibility, robustness, future-proofing, compatibility, data-driven behavior, and utility. The discussion began with GUI and binary strategy, moved through repo convergence and distribution packaging, audited current code vs data reality, reframed the project as something closer to an operating environment than a game, then focused on a unified Workbench and finally a full Interface Operating Layer.

The earliest baseline was that all products must have CLI, should have TUI, and may have modular GUIs. GUI shells should be thin adapters over the same backend/UI contract. That led into platform lanes: Windows legacy/compat/modern, macOS AppKit/SwiftUI/legacy toolchain, Linux reduced GUI family count, and Android as a distinct host family. The chat rejected one universal GUI framework and one GUI per OS version.

The repository discussion established that Dominium should be organized by ownership and contracts, not by topic folders. The post-CONVERGE layout authority uses roots such as `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `tools/`, `release/`, and `archive/`. Domain work must split into contracts, implementation, content, docs, and tests. Older layout docs may be historical but should not override machine-readable contracts.

The shipping discussion recommended deterministic layers: `.dompkg` packages, install profiles, assembled bundles, thin installer wrappers, release manifests, release indexes, archive history, and offline verification. Versioning must remain layered: suite/product/protocol/schema/format/semantic-contract/build/artifact/release/target descriptors. Filenames are projections, not truth.

The code audit concluded that the current repo is modular at source/build level and partly data-driven through registries and validators, but not yet a fully data-driven moddable runtime. The client still has hard-coded help, command descriptors, session stages, UI overlay, interaction definitions, and null audio. Product boot and portable projection proof were partial or blocked in inspected docs.

The biggest conceptual shift was accepting the user’s “closer to an OS than a game” idea, with precision: Dominium should be a deterministic simulation operating environment, not a literal OS. Engine becomes kernel-like substrate; contracts become law; runtime services provide commands/packages/world/replay/diagnostics; drivers handle platform/render/audio/input/network/storage; domains are installed interpreters; apps are userland shells; packs are mounted data; proof/replay/release wrap everything.

The Workbench discussion superseded the old UI Editor / Tool Editor plan. The best product is a modular Dominium Workbench: one rendered tools host, many modules, same runtime as client, same command/result/refusal model as CLI/TUI/headless. However, the final refinement was broader: the Workbench is not the platform; the Interface Operating Layer is. The layer provides one command/result/refusal/document/event spine and projections into CLI, TUI, rendered GUI, headless reports, and native wrappers later.

The most important next step is not a pretty GUI. It is law and proof: update AppShell rendered-mode capability law, unify command dispatch, define typed result/refusal/document/patch/module schemas, prove product boot, then build a minimal Workbench shell with Validation Dashboard and Pack Browser. The best MVP is a boot-to-replay proof: mount package, create/load world, render deterministic view, submit one intent, commit state, emit event/replay/proof, and replay to same hash.
