# COMPLETE CHAT PRESERVATION REPORT — Dominium Workbench, AIDE, Presentation Spine, and Provider Strategy

## 0. Coverage and Reliability Assessment

| Field | Assessment |
| --- | --- |
| Chat label | Dominium Workbench, AIDE, Presentation Spine, and Provider Strategy |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial-to-high: visible transcript context in this conversation plus the uploaded preservation instructions; no guarantee of access to every hidden/prior artifact outside this visible chat. |
| Previously generated files available? | No previous downloadable package from this chat was available in the sandbox; this response creates a new package. |
| Uploaded files or artifacts present? | Yes: the user uploaded a text file containing the preservation-task instructions. It is cited in the final response as requested. |
| Contains future plans? | Yes |
| Contains decisions? | Yes |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | High for live repository status and current external dependencies; medium for internal doctrine; low for decisions explicitly made in this chat. |
| Extraction confidence | 4/5 for visible chat substance; 3/5 for exact live repo state because this package does not re-query the repository. |
| Safe for later aggregation? | Yes, with caveats: verify current repo state and distinguish FACT from PROJECT-CONTEXT and UNVERIFIED repo-status claims. |
| Main limitations | The report is reconstructed from the visible chat transcript and pasted status reports. Some repo facts were pasted from other chats and should be verified before operational use. |


This preservation package is based on the visible conversation plus the uploaded preservation instructions file. I can produce files in this environment, and I created a downloadable report set and ZIP. The uploaded file is the explicit preservation request and output specification for this task, not an independent evidence source about Dominium architecture. fileciteturn0file0

Important limitation: many repository-state facts in this chat came from pasted status blocks or previous assistant web checks. In this preservation report, those are retained because they were part of the chat, but they are marked as FACT only when explicitly stated in the chat and marked UNVERIFIED when they would require a fresh repository check. Future operational work must verify live repository files before acting.


## 1. One-Page Orientation

This chat was a long-running architecture and execution-planning conversation for the Dominium / Domino project. It began around a practical UI problem: the existing Windows launcher UI looked mangled and flickered, and the user wanted a graphical internal editor that could create pixel-perfect UIs for setup, launcher, game, and other tools. That early goal became much larger. Over time, the chat moved from a Windows-only “UI Editor” plan, to a broader “Tool Editor,” and finally to a more powerful and coherent concept: **Dominium Workbench**, a cross-platform rendered, modular, command-driven, agent-aware production environment for building the whole Domino/Dominium system.

The conversation’s most important shift was that Workbench stopped being “an editor” and became a userland product over the same operating-environment spine as the client, server, launcher, and setup. The user wanted all tools to reuse the actual Domino/Dominium code and data instead of becoming separate helper programs. The resulting doctrine was that CLI, TUI, rendered GUI, OS-native GUI, headless jobs, AIDE, Codex, tests, and Workbench panels should all project the same underlying command/result/refusal/document/evidence truth. UI is not authority; commands, contracts, services, providers, documents, patches, artifacts, diagnostics, and evidence are the stable center.

A large part of the chat dealt with what should be reusable and where it should live. The stable vocabulary became: **component** as source/build ownership unit; **service** as callable runtime capability; **provider** as replaceable implementation; **pack** as distributable authored payload; **module** as declared functional extension; **workspace** as user-facing Workbench composition; **app** as shipped product composition; and **artifact** as versioned persisted thing such as save, replay, pack, bundle, diagnostic, or release output. This vocabulary matters because it prevents “module” or “tool” from becoming a junk drawer.

The chat also developed a staged execution strategy. The user and assistant converged on Foundation and AIDE gates before broad Workbench implementation. The sequence evolved as pasted repo status changed: first Foundation Lock and dependency-direction repair, then package mount, replay proof, barebones client shell, product-spine review, AIDE workflow law, WorkUnit schema, dev/main policy, checkpoint loop, capability reality ledger, presentation contract, projection conformance, and then read-only Workbench. Later, after a reported successful `PRESENTATION-CONTRACT-01`, the user wanted to generate targeted maintenance prompts before continuing presentation/projection work.

Another key branch of the chat involved presentation and rendering. The user wanted a single cross-platform rendered app capable of modular themes, Workbench modules, CLI/TUI/rendered/native projections, and OEM+ OS-style mimic profiles. The conclusion was that layout, controls, themes, views, and widgets should be data-described and registry-backed. Themes should alter geometry, density, palette, typography, control metrics, and procedural drawing, not product semantics. TUI should be a first-class projection, not a toy fallback. Rendered GUI should be built on a renderer-agnostic draw-list pipeline. OS-native GUI can exist as optional projection, using Visual Studio/Xcode/GTK tooling, but it must not become canonical behavior.

Finally, the chat considered third-party acceleration. The user pasted advice about raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua. The accepted doctrine was service-first and provider-backed: use these aggressively as seed providers, but fence their types so they do not leak into engine, game, contracts, content, saves, replays, pack schemas, or public SDK. Provider choices should live in profiles; apps stay generic.

The future relevance of this chat is high. It records the architecture behind Workbench, AIDE, provider strategy, presentation contracts, self-hosting, TUI/rendered GUI unification, and near-term task order. A future assistant must understand that the project is no longer looking for a one-off UI editor. It is building a deterministic, contract-governed, modular simulation operating environment where Workbench becomes the production environment over shared law, services, providers, packs, modules, views, and evidence.


## 2. The Story of the Conversation

### 2.1 From UI Editor to Tool Editor

The chat opened with a practical product-design/software-architecture task: the current Windows launcher UI was mangled and flickered. The user wanted a graphical UI creation tool to design pixel-perfect UIs and broad-strokes functionality for setup, launcher, game, and other tools. Early questions established that the project had an in-tree DUI schema/state system using TLV, with Win32 common-control, DGFX custom-render, and null backends. The first chosen plan was a minimal Windows-only UI Editor that generated TLV directly, followed later by a more powerful Tool Editor that would edit DUI schemas/states directly and instantiate preview backends.

The assistant and user generated an 11-prompt implementation plan for this old approach, including repo scaffolding, canonical UI IR, TLV I/O, capability validation, layout engine, splitter/tabs/scroll widgets, action codegen, Phase A UI Editor, Tool Editor bootstrap, flicker fixes, and hardening. That plan then expanded into six UI Editor extension prompts covering discovery/import/export, CLI modes, ops.json scripting, Minecraft-style logical launcher/setup layouts, setup layout, and hardening. The user clarified that “Minecraft-style” meant logical layout using native Win32 controls, not graphical skinning.

### 2.2 Abandoning UI Editor / Tool Editor as final products

The user then redirected the plan. They concluded that the old UI Editor and Tool Editor were good general ideas but bad final products. Instead, they wanted cross-platform tools using the same CLI, TUI, and rendered GUI as the client, not OS-native SDK widgets. This led to the idea of Dominium Workbench: a rendered modular tools host and production environment over the same runtime architecture as the client.

The assistant agreed and proposed an integrated Workbench shell with focused modules rather than one monolithic editor. The user and assistant refined this into “Dominium Workbench Platform,” a modular userland operating environment for inspecting, editing, validating, simulating, previewing, packaging, and proving Dominium systems. Workbench would not own semantics; it would host capability-scoped modules over shared commands, documents, packages, validation, render, diagnostics, and replay services.

### 2.3 Generalizing Workbench into the project production environment

The user emphasized that Workbench was not merely an inspector or command dashboard. As sole developer, they wanted to use it to build the entire Domino/Dominium project: code, data, packs, UI, graphics, sounds, tests, releases, and agent work. The plan expanded to include Command OS, Creation Studio, Evidence Notebook, System Graph, Preview/Sandbox, Agent Control Board, and Release Forge. Workbench became the “visual and agentic production environment” for Domino/Dominium.

A strong rule emerged: every GUI/TUI action should map to a command; every edit should be a patch; every operation should produce diagnostics/evidence. This enables human GUI work, CLI work, TUI work, headless work, and Codex/AIDE work to converge instead of drifting into separate systems.

### 2.4 Modular UI, themes, OEM+ style, TUI, and rendering

The user wanted modular layouts, controls, themes, styles, views, and OEM+ native-style rendered theme profiles. The conversation concluded that UI should be separated into view model, view document, style/theme tokens, runtime UI components, and renderer backend. Layouts should be data-driven; controls should be semantic; themes should be token overlays; views should project typed documents/results; controls/widgets should have projection implementations for CLI/TUI/rendered/native.

The user supplied mockups and TUI design advice. The TUI doctrine became: terminal-native projection of the same operating environment, not a separate ASCII version. It should support command palette, module launcher, project tree, inspector, diagnostics, logs, validation reports, pack browser, setup wizard, server console, client tactical fallback, and agent work board. The TUI should be fast, exact, trustworthy, and always available.

Rendered GUI would use software renderer first, hardware later, and could support primitive-only theme families such as Barebones, Instrument, Blueprint, Paper, Phosphor, Tactical, High Contrast, and TUI-rendered hybrid. Rich assets, exact OS mimicry, audio, fonts, textures, and advanced icons could be optional packs.

### 2.5 Engineering law and reusable architecture

The user then asked about portability, modularity, extensibility, replacing directories and code, and building like a proper game/OS rather than a one-off project. The assistant proposed an engineering constitution: Domino as reusable substrate, Dominium as product family, every boundary contract-defined, versioned, capability-checked, test-proven, and replaceable. Important practices included stable C-compatible ABI, service interfaces, provider contracts, module/pack tiers, generated artifact policy, dependency-direction validators, schema/protocol versioning, deterministic data formats, structured refusals, and compatibility corpus.

This led to the vocabulary split: component, service, provider, pack, module, workspace, app, artifact. Workbench modules were framed as one consumer of the general module system, not the general module system itself.

### 2.6 AIDE, queues, status, and prompt sequencing

A major segment focused on AIDE and Codex workflow. The project had a queue of tasks such as Foundation Lock, Package Mount Slice, Replay Proof Slice, Barebones Client Shell, Product Spine Review, AIDE Workflow Law, WorkUnit Schema, Dev/Main Policy, Checkpoint Loop, Capability Reality Ledger, Presentation Contract, Projection Conformance, and later Workbench/Explorer tasks.

The user pasted status reports indicating tasks completed and queue corrections needed. The assistant generated detailed Codex/AIDE prompts for `STATUS-RECONCILE-02`, `AIDE-WORKFLOW-LAW-01`, `AIDE-WORKUNIT-SCHEMA-01`, `AIDE-DEV-MAIN-POLICY-01`, `AIDE-CHECKPOINT-LOOP-01`, `AIDE-CAPABILITY-REALITY-LEDGER-01`, and `FULL-GATE-LEGACY-TEST-ROUTE-01`. These prompts emphasized allowed paths, forbidden paths, non-goals, validation, blocker handling, dirty worktree handling, and final response format.

### 2.7 Providers, raylib, SDL2, Lua, and future visual progress

The user pasted later advice about using raylib ecosystem libraries, SDL2, and Lua. The final doctrine was to use raylib aggressively as a seed provider suite but only behind Dominium service contracts. `rlsw` is a raylib ecosystem software provider, not the Dominium canonical software renderer. `rlgl` is a raylib GL-abstraction provider, not the final OpenGL law. Raygui is early Workbench/debug UI provider, not UI law. SDL2 remains useful for host/input/audio. Lua can be a pinned script provider but must not define the mod ABI.

### 2.8 Final state of the chat

At the end, the user uploaded a preservation task requesting a complete chat preservation report, registers, spec sheet, aggregator packet, self-audit, and downloadable files. This report and package are the response to that final request.


## 3. Main Topics Discussed

### Topic 1 — Launcher UI problem and original UI Editor plan

The chat began with the launcher UI looking mangled and flickering. The early solution was a Windows-only Phase A UI Editor, followed by a more ambitious Tool Editor. The UI Editor would edit existing DUI/TLV definitions, use Win32 native controls for preview, and produce canonical TLV plus generated action stubs. This mattered because launcher/setup UI was an immediate product pain and a good test of the existing DUI system.

Conclusion: the UI Editor plan was useful as a bootstrapping concept but later superseded as a final product.

### Topic 2 — DUI/TLV, schema/state, and UI runtime architecture

The chat established that the existing launcher used a DUI schema/state system with TLV and backends for Win32 common controls, DGFX custom rendering, and null/headless. Early architecture options revolved around whether to extend DUI directly, introduce an authoring IR, or build a minimal direct-TLV editor. The user accepted a canonical edit model and deterministic TLV/JSON output before later abandoning the old editor product path.

Conclusion: the useful pieces remain: canonical UI documents, action bindings, validation, import/export, CLI scripting, preview, layout engine, and codegen. They become Workbench modules/services rather than a standalone UI Editor.

### Topic 3 — Workbench as production environment

The conversation’s largest conceptual shift was from “editor” to “Workbench.” The user wanted one rendered cross-platform app using the same client/runtime code, capable of building and testing Domino/Dominium artifacts. Workbench became a modular production environment with command palette, module registry, project graph, validation, agent board, pack browser, UI/HUD sandbox, renderer sandbox, release forge, and future authoring tools.

Conclusion: Workbench is not authority; it operates the system. It should expose commands, documents, patches, diagnostics, evidence, modules, packs, providers, and workspaces.

### Topic 4 — Unified CLI/TUI/rendered/native/headless presentation

The chat repeatedly refined a presentation doctrine: CLI, TUI, rendered GUI, native GUI, headless reports, Workbench panels, tests, and AIDE workflows should all project the same command/result/refusal/document/evidence truth. OS-native GUI may be optional, built via Visual Studio/Xcode/GTK paths, but not canonical.

Conclusion: presentation is a projection layer. This led to `PRESENTATION-CONTRACT-01` and `PROJECTION-CONFORMANCE-01` as essential next tasks.

### Topic 5 — TUI as first-class projection

The user pasted detailed TUI design advice. The TUI should be a deterministic, keyboard-first, low-dependency projection suitable for servers, setup recovery, CI, SSH, accessibility, debugging, AIDE/Codex workflows, and users who prefer terminals. It should include panels, split panes, tables, trees, command input, logs, status bars, and degraded ASCII fallback.

Conclusion: TUI is not second-class. It should share the same semantic view/action model as CLI and rendered GUI.

### Topic 6 — Themes, OEM+ style, and code-only UI richness

The user wanted a rendered GUI capable of mimicking Windows, macOS, and Linux styles through OEM+ theme profiles. The discussion established that many useful styles can be generated code-only through primitives: fills, borders, lines, patterns, gradients, text, procedural glyphs, and layout metrics. Richer fidelity can come later through packs/assets.

Conclusion: themes are data-packable token/control-skin profiles. They change appearance and metrics, not product semantics.

### Topic 7 — Engineering law for portability, modularity, and replaceability

The user asked how to build the project like a serious game/OS rather than a one-off indie project. The response developed broad coding/architecture practices: stable ABI, contracts, versioned schemas, service/provider boundaries, dependency-direction validation, modular packs/modules, patch/transaction systems, structured diagnostics/refusals, generated artifact policy, compatibility corpus, and conformance tests.

Conclusion: future-proofing depends more on contract-governed boundaries than on folders alone.

### Topic 8 — Module, pack, service, provider, app vocabulary

The conversation settled on strict terminology. Component is source/build ownership; service is callable runtime capability; provider is replaceable implementation; pack is authored distributable payload; module is declared functional extension; workspace is Workbench composition; app is shipped product composition; artifact is persisted versioned output/input.

Conclusion: this vocabulary is central and should be preserved.

### Topic 9 — AIDE/Codex workflow and parallel development

A large part of the chat focused on AIDE as scheduler/ledger/gatekeeper and Codex as bounded patch executor. The user wanted to run parallel Codex tasks on `/dev` while keeping `/main` evidence-blocked. The assistant generated prompts for AIDE workflow law, WorkUnit schemas, dev/main policy, checkpoint loop, and capability reality ledger.

Conclusion: development is non-blocking; promotion is evidence-blocked. Large parallelism requires AIDE workflow controls.

### Topic 10 — Product spine, replay proof, barebones client, and Universe Explorer

As task state evolved, the plan moved from product-spine slices toward presentation/projection and eventually a read-only Workbench/Client Universe Explorer. The explorer is a north-star product slice: a lawful read-only universe inspection/navigation surface proving reference frames, no modal loading, streaming/degradation, sparse materialization, and provenance before gameplay or embodiment.

Conclusion: Universe Explorer is valid as a future product-spine direction, but must enter through contracts, headless proof, and read-only projection, not broad renderer/gameplay work.

### Topic 11 — Raylib/SDL2/Lua provider strategy

Later discussion refined use of raylib, rlsw, rlgl, raygui, raudio, SDL2, and Lua. The final doctrine is service-first/provider-backed/profile-selected/third-party-fenced/evidence-tested. Raylib can accelerate visible progress but must not define architecture.

Conclusion: third-party libraries are seed providers, not law.


## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted to solve the damaged launcher UI, build UI/tools capable of visually designing interfaces and functionality, support Windows/Linux/macOS cross-platform tools, reuse client/runtime code in tools, create modular and extensible rendered GUI/TUI/CLI surfaces, and use Workbench to build the entire Domino/Dominium project. Later explicit goals included preserving the entire chat, producing a handoff package, and generating bounded Codex prompts in correct sequence.

### 4.2 Inferred Goals

INFERENCE: The user is trying to prevent architecture drift and avoid a future in which the project becomes a collection of disconnected tools, UIs, and one-off scripts. The repeated emphasis on portability, modularity, replaceability, and reuse suggests a desire for a professional, long-lived platform architecture where every subsystem can be tested, replaced, and reused for other games or engine projects.

### 4.3 Goals That Changed Over Time

The goal changed from a Windows UI Editor to a full Workbench platform. The early goal was immediate UI repair and graphical editing. The later goal became a cross-platform rendered production environment, agent-control surface, module/pack/app composer, and self-hosting authoring tool. Another shift was from OS-native widgets to rendered, provider-backed UI, with native SDK GUIs optional projections.

### 4.4 Goals Still Unresolved

The Workbench is not implemented. Presentation/projection conformance is only beginning. Provider runtime, package runtime, module loader, renderer implementation, native GUI, Universe Explorer, gameplay, and self-hosting authoring remain future work. Repo live state must always be verified before assuming a queued task is done.


## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
| --- | --- | --- | --- | --- | --- |
| DECISION-01 | Abandon old UI Editor/Tool Editor as final products; recycle ideas into Workbench modules. | Accepted | Avoid one-off Windows/native editor architecture. | High | FACT |
| DECISION-02 | Dominium Workbench is a modular production environment, not authority. | Accepted | Prevents GUI/tool drift; keeps contracts/commands/services central. | High | FACT |
| DECISION-03 | CLI/TUI/rendered/native/headless are projections of one semantic spine. | Accepted | Enables reuse across apps, tests, Workbench, AIDE, and products. | High | FACT |
| DECISION-04 | Use progressive self-hosting. | Accepted | Avoids circular bootstrap. | High | FACT |
| DECISION-05 | Use service/provider/profile vocabulary and strict module/pack/app terms. | Accepted | Prevents taxonomy collapse. | High | FACT |
| DECISION-06 | Use AIDE as governor/ledger/scheduler and Codex as bounded patch executor. | Accepted | Enables parallel dev without corrupting main. | High | FACT |
| DECISION-07 | Use raylib/SDL2/Lua as providers, not architecture. | Accepted conceptually | Accelerates visible progress without lock-in. | Medium-High | FACT/UNVERIFIED for implementation |
| DECISION-08 | Stop broad structure cleanup once canonical structure passes; use targeted maintenance lanes. | Accepted conceptually | Avoids churn after structure became credible. | Medium-High | FACT/PROJECT-CONTEXT |
| DECISION-09 | Universe Explorer is a read-only/headless proof before visual/gameplay. | Accepted conceptually | Proves scale/refinement/reference frames without broad gameplay. | Medium | FACT |
| DECISION-10 | Full CTest remains full-gate/T4 debt, not normal prompt gate. | Accepted from pasted status | Keeps dev loop practical. | Medium | PROJECT-CONTEXT/UNVERIFIED |


### DECISION-01 — Abandon old UI Editor / Tool Editor as final products

The user explicitly said the old UI Editor and Tool Editor were good general ideas but bad actual final products, and should be abandoned and recycled. The retained pieces are UI documents, CLI scripting, import/export, validation, preview, codegen, layout, theme, and property editing. These become Workbench modules and services. Alternative considered: continue with a Windows-only UI Editor followed by full Tool Editor. Revisit only if a tiny one-off tool is needed as a temporary bridge.

### DECISION-02 — Workbench is production environment, not authority

Workbench should operate the system, not define truth. This decision protects the project from GUI-only behavior and allows CLI/TUI/headless/AIDE to use the same commands and results. Workbench edits artifacts through documents/patches/transactions.

### DECISION-03 — Unified projection model

CLI, TUI, rendered GUI, native GUI, headless reports, Workbench panels, tests, and AIDE workflows should all present typed results/documents/refusals/evidence from one command spine. This supports reuse and prevents duplicated product logic.

### DECISION-04 — Progressive self-hosting

Workbench should not build itself from nothing. It starts from hand-coded seed substrate, then edits safe artifacts, then its own themes/layouts, then modules/apps/packs, and later orchestrates AIDE/Codex code work.

### DECISION-05 — Strict vocabulary split

The terms component/service/provider/pack/module/workspace/app/artifact were adopted to avoid future junk drawers. This affects directory structure, manifests, contracts, and Workbench UX.

### DECISION-06 — AIDE governs, Codex executes

AIDE should manage task packets, context, policies, evidence, blockers, branch roles, dev/main promotion, and repair/resume work. Codex executes bounded patch tasks. This enables parallel development while keeping main evidence-blocked.

### DECISION-07 — Third-party libraries as providers

Raylib, SDL2, Lua, and related libraries are accelerators. The project should use them aggressively but fence their types behind Dominium service contracts and provider manifests.

### DECISION-08 — Stop broad structure cleanup after structure is credible

Once the active structure passes hard gates, broad cleanup should stop. Remaining work should be targeted: full-gate legacy test routing, pack layout canon, residual taxonomy, ABI promotion, storage/package/provider split.

### DECISION-09 — Universe Explorer as read-only proof path

Universe Explorer is a future north-star product slice but should begin as read-only/headless inspection. It must not become gameplay or renderer authority.

### DECISION-10 — Full CTest as full-gate debt

The chat repeatedly treated fast strict and targeted validators as normal task gates, while full CTest remains release/full-gate debt unless explicitly run and passed. This makes Codex throughput practical while preserving release rigor.


## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

The Windows-only UI Editor as final product was superseded. It is still useful as a historical bridge idea, but final architecture should be Workbench modules over shared services. A native-widget-first Tool Editor was also superseded because the user wants rendered cross-platform tools using client/runtime code. OS-native GUI design is not abandoned; it becomes optional projection using Visual Studio/Xcode/GTK-style tooling.

A monolithic everything editor was rejected. The accepted form is one integrated Workbench shell built from small reusable modules, services, commands, documents, views, and workspaces.

A raylib-shaped architecture was rejected. Raylib is useful, but source structure must be service-first: `runtime/<service>/providers/<provider>`, not `runtime/raylib/<service>`. App variants like `apps/client/rendered/raylib` were rejected as long-term architecture.

Broad structure cleanup was deprioritised after the active structure reportedly passed hard gate checks. Remaining cleanup should be targeted maintenance.

Pure C89/C++98 was superseded by a C17/C++17 baseline in pasted repo status. This must be verified in live repo before operational use.

Broad gameplay, renderer implementation, native GUI, module loader, provider runtime, release publication, and full Workbench UI were repeatedly deferred until appropriate gates.


## 7. Important Reasoning, Rationale, and Tradeoffs

The dominant tradeoff was speed versus architectural durability. The user wants rapid progress using Codex/AIDE and third-party libraries, but also wants the project to be reusable, replaceable, deterministic, and professional. The compromise is narrow vertical slices, provider-backed acceleration, and evidence-gated promotion.

Another tradeoff was GUI richness versus semantic safety. Workbench should eventually be visual and powerful, but if it directly mutates files or calls private tools, it will become a second authority. The adopted solution is document/patch/transaction flow.

The UI discussion balanced OS-native familiarity with cross-platform rendered control. Native SDK GUIs remain useful, but the core Workbench/client UI should be rendered and service-backed to support themes, TUI parity, and modding.

Parallel development was treated as desirable but dangerous. The visible rationale was that `/dev` can accumulate classified partial progress, but `/main` must remain evidence-backed. This leads to task branches, repair branches, checkpoint branches, and promotion decisions.

The third-party provider discussion balanced visible progress against lock-in. Raylib/SDL/Lua are valuable because they provide quick windows, rendering, input, audio, assets, scripting, and UI; but their types must not enter stable contracts or deterministic truth.


## 8. Plans, Future Work, and Next Steps

The latest immediate sequence in this chat ended with a generated `FULL-GATE-LEGACY-TEST-ROUTE-01` prompt. The user had just reported `PRESENTATION-CONTRACT-01` complete and wanted to generate a maintenance batch before replanning.

Recommended short-term sequence from the chat:

1. Generate and run maintenance prompts:
   - `FULL-GATE-LEGACY-TEST-ROUTE-01`
   - `PACK-INTERNAL-LAYOUT-CANON-01`
   - `RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01`
   - `PUBLIC-HEADER-ABI-PROMOTION-01`
   - `STORAGE-PACKAGE-PROVIDER-SPLIT-01`
   - `POINTER-WIDTH-SERIALIZATION-AUDIT-01`
2. Replan after the maintenance batch.
3. Continue mainline product/presentation sequence:
   - `PROJECTION-CONFORMANCE-01`
   - `ACCESSIBILITY-CONTRACT-01`
   - `TEXT-LOCALIZATION-CONTRACT-01`
   - `WORKBENCH-SHELL-READONLY-01`
   - `UNIVERSE-EXPLORER-CONTRACT-01`
   - `UNIVERSE-EXPLORER-HEADLESS-01`
   - `PROVIDER-MANIFEST-WEDGE-01`
   - `SERVICE-CONTRACT-WEDGE-01`
   - `THIRD-PARTY-FENCE-01`
   - `RAYLIB-PROVIDER-WEDGE-01`
   - `UNIVERSE-EXPLORER-VISUAL-01`

Each task should be narrow, with allowed/forbidden paths, non-goals, validation, blocker handling, and final response format. Broad Workbench UI, renderer/gameplay/native GUI, provider runtime, package runtime, module loader, and release publication remain blocked until gates authorize them.


## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user prefers direct, source-grounded, audit-ready answers with explicit uncertainty. They want decisions preserved, rejected ideas recorded, and tentative items not promoted to final decisions. They repeatedly asked for copy-paste-ready prompts in single code blocks. They want the project to be portable, modular, extensible, deterministic, replaceable, and reusable for other games or engines.

### 9.2 Inferred Constraints and Preferences

INFERENCE: The user values architectural continuity and dislikes repeating settled debates. They prefer long, complete handoffs over terse summaries. They want future chats to continue from current queue status and verify live repo state before acting.

### 9.3 Uncertain or Unestablished Preferences

UNCERTAIN: Exact preferred path names may change as the repo evolves. Live repository queue state may have advanced after this preservation package. The actual CMake language baseline should be verified.


## 10. Files, Artifacts, Outputs, and Prompts

Important artifacts from this chat include the generated prompt series for the old UI Editor plan, the UU1–UU6 UI Editor extension prompts, the final UI Editor prompt with import/CLI/Minecraft tests, many Workbench/AIDE/product-spine prompt blocks, and the final generated `FULL-GATE-LEGACY-TEST-ROUTE-01` prompt.

The user uploaded a text file containing the preservation instruction set for this task. This response creates a new preservation package with Markdown, YAML, and ZIP outputs.

No previous downloadable package from this chat was available in the sandbox at the time of this response. The present response creates:

- manifest
- human-readable report
- context transfer packet
- spec sheet
- structured registers
- aggregator packet
- reader brief
- verification/audit file
- future chat bootstrap prompt
- in-chat reader
- ZIP bundle


## 11. Open Questions and Unresolved Issues

The biggest unresolved issue is live repo state: future work must verify whether the generated prompts have been run and whether the queue has advanced. Another unresolved issue is the exact implementation order after the maintenance batch. The user wants to run maintenance prompts first, then replan.

Technical open questions include how soon provider manifests should be implemented relative to projection conformance, how to split raylib provider wedge into manifest/service/fence/implementation tasks, which Lua version to pin, whether `external/upstream` or `external/vendor` matches repo convention, and how full-gate tests should be routed without weakening active structure gates.

Workbench remains unresolved at the implementation level: read-only first is agreed, but exact UI shell design, renderer path, modules, and self-hosting milestones remain future tasks.


## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

A future assistant might restart the UI Editor/Tool Editor plan as if it were still current. It might treat Workbench as authority or a monolithic editor. It might claim raylib/SDL/Lua implementation support when only provider doctrine exists. It might assume pasted repo status is current without checking live files. It might run broad structure cleanup after the structure is already clean enough. It might treat full CTest debt as normal prompt blocker or, conversely, claim full CTest is green without evidence.

The main mitigation is to verify live repo state, preserve labels, and keep using bounded prompts with allowed paths, forbidden paths, non-goals, validation, blocker handling, and explicit final response format.


## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat should feed several chapters of a future Project Spec Book: Workbench Platform, AIDE/Codex Workflow, Presentation Architecture, UI/TUI/Rendered GUI Systems, Provider Architecture, Engineering Constitution, Module/Pack/App Vocabulary, Progressive Self-Hosting, TUI Doctrine, Theme/OEM+ Style System, and Product-Spine Execution Plan.

It contributes especially valuable context about why the project moved away from a one-off UI Editor and toward a unified production environment. It also provides concrete prompt templates and task sequencing that can be reused.

Before merging into a master spec, all repo-status claims should be verified. The doctrine is reusable; the live task status is perishable.


## 14. What I Should Remember

- The old UI Editor / Tool Editor plan is superseded as final product, but its ideas become Workbench modules/services.
- Workbench is the production environment over the system, not authority.
- CLI, TUI, rendered GUI, OS-native GUI, headless, Workbench, AIDE, and tests should all project the same command/result/refusal/document/evidence truth.
- Development is non-blocking; promotion is evidence-blocked.
- AIDE governs queues, blockers, work units, evidence, checkpoints, and dev/main policy; Codex executes bounded patches.
- Themes, layouts, controls, widgets, and views should be modular and data-described.
- TUI is a first-class projection.
- Raylib/SDL2/Lua are providers, not architecture.
- Full CTest remains full-gate debt unless verified otherwise.
- Broad Workbench UI, renderer, native GUI, gameplay, provider runtime, package runtime, module loader, and release publication remain blocked until gates authorize them.
- The last generated prompt in this chat was `FULL-GATE-LEGACY-TEST-ROUTE-01`.


## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat

- “Explain again why we abandoned the old UI Editor / Tool Editor path.”
- “What is the difference between Workbench, AIDE, and Codex?”

### 15.2 Decisions

- “Which decisions from this chat are final versus tentative?”
- “Which decisions depend on live repo verification?”

### 15.3 Tasks and Next Actions

- “Generate `PACK-INTERNAL-LAYOUT-CANON-01`.”
- “Generate the next maintenance prompt after `FULL-GATE-LEGACY-TEST-ROUTE-01`.”
- “Replan after the maintenance batch.”

### 15.4 Artifacts and Files

- “List every Codex prompt generated in this chat.”
- “Which artifacts from this package should feed a master Project Spec Book?”

### 15.5 Risks and Verification

- “What repo-state claims from this chat need fresh verification?”
- “What could a future assistant misunderstand most badly?”

### 15.6 Future Spec Book / Aggregation

- “Convert this preservation report into formal spec-book chapters.”
- “Compare this chat’s doctrine against another old chat report.”

### 15.7 Deep-Dive Questions Specific to This Chat

- “Deep-dive the presentation/projection architecture.”
- “Deep-dive the provider strategy for raylib/SDL2/Lua.”
- “Deep-dive the progressive self-hosting ladder.”


## 16. Compact Human Summary

This chat began with a practical UI problem: the Dominium launcher UI was broken-looking and flickery. The original plan was to build a Windows-only UI Editor that could visually design DUI/TLV UIs, then later a full Tool Editor. That early plan became a detailed prompt sequence, including schema/IR, TLV I/O, layout, action codegen, import/export, CLI scripting, and launcher/setup redesign tests. But the user later changed direction decisively: the old UI Editor and Tool Editor were not the right final products.

The better plan became Dominium Workbench: a cross-platform rendered, modular, command-driven, agent-aware production environment that uses the same runtime, renderer, UI, command, package, diagnostics, evidence, and provider systems as the client. Workbench is not a separate GUI framework and not authority. It is the richest human/agent interface over the same contracts and services used by CLI, TUI, headless, native GUI, setup, launcher, server, client, and tests.

A central doctrine emerged: everything meaningful should go through commands, typed results, refusals, diagnostics, documents, patches, services, providers, packs, modules, artifacts, views, and projections. GUI actions should map to commands. Edits should become document patches. Results should produce evidence. AIDE governs task state and proof; Codex executes bounded patches. Development can move quickly on dev/task branches, but promotion to main is evidence-blocked.

The chat also developed a strong UI architecture. CLI, TUI, rendered GUI, OS-native GUI, and headless output are projections of the same semantic view model. TUI is first-class, not a toy fallback. Rendered UI should be data-described through layouts, controls, themes, style tokens, widgets, and workspace documents. Themes can be code-only at first, using rectangles, lines, text, hatching, gradients, and procedural glyphs. Rich assets, textures, fonts, sounds, and exact OS-mimic profiles can come later through packs.

The conversation established a reusable vocabulary: component, service, provider, pack, module, workspace, app, artifact. This distinction prevents architectural junk drawers. Workbench modules are not the general module system; they are one consumer of it.

The repo/task planning thread evolved through many reported states. Foundation Lock passed with warnings; package mount, replay proof, barebones client, product-spine review, AIDE workflow law, WorkUnit schema, dev/main policy, checkpoint loop, capability reality ledger, and presentation contract were discussed as completed or queued at different points. Because repo status changes rapidly, future assistants must verify live files before assuming current status. The last user-provided status said `PRESENTATION-CONTRACT-01` completed, and the user wanted to generate maintenance prompts first: full-gate legacy test routing, pack internal layout canon, runtime/engine residual taxonomy, public header ABI promotion, storage/package provider split, and pointer-width serialization audit. The assistant generated `FULL-GATE-LEGACY-TEST-ROUTE-01`.

A later strategic thread established how to use third-party libraries. Raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua should be used aggressively as seed providers, but not allowed to define architecture. Dominium owns service contracts, data formats, commands, views, saves, replays, packs, modules, and asset identity. Providers implement replaceable backends. Profiles select providers. Apps remain generic.

The most important next action inside this old chat is to continue generating the requested maintenance prompts after `FULL-GATE-LEGACY-TEST-ROUTE-01`, or to replan after that maintenance batch. The most important preservation requirement is to carry forward the doctrine: Workbench designs artifacts; runtime executes artifacts; contracts constrain artifacts; content packages artifacts; apps consume artifacts; tests prove artifacts; AIDE governs changes; Codex patches code.
