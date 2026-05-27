# COMPLETE CHAT PRESERVATION REPORT — Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, and Product-Spine Planning

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, and Product-Spine Planning |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial-to-broad visible context: I can see the current conversation state, user-provided handoffs, uploaded preservation instructions, and much of the transcript, but not a guaranteed raw complete line-by-line export of every prior turn. |
| Previously generated files available? | No previously generated downloadable package is visible in `/mnt/data`; many prompts and handoff texts were generated in-chat. |
| Uploaded files or artifacts present? | Yes: screenshots/mockups and `Pasted text.txt` preservation instruction are present; older screenshots are referenced in chat. |
| Contains future plans? | Yes |
| Contains decisions? | Yes |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | High for live repo and external software status; medium for project doctrine; low for in-chat decision history. |
| Extraction confidence | 4/5 for visible chat themes and decisions; 3/5 for exact current repo state; 2/5 for any omitted/skipped early messages. |
| Safe for later aggregation? | Yes, with caveats |
| Main limitations | No raw full transcript export; live repo facts are user-reported and may be stale; some earlier turns were summarized/skipped; uploaded images are preserved as references but not exhaustively analyzed here. |

Plain-language limitations: this preservation package is based on the visible current chat context and user-provided handoff material. It is not a fresh clone of the repo and not a forensic transcript with line numbers. Where the chat discussed live repo state, I preserve what was said and mark verification items. Where assistant recommendations evolved into accepted user plans, I treat them as accepted only when the user clearly endorsed or operationalized them. External facts about raylib, SDL, Lua, GitHub, and the live repo should be verified before implementation.



## 1. One-Page Orientation

This chat was a long, architecture-heavy planning conversation for Dominium, Domino, AIDE, and the proposed Workbench. It began around a concrete tooling problem: the Windows launcher UI looked mangled and flickered, and the user wanted a visual internal “Tool Editor” or “UI Editor” that could design pixel-perfect UIs for setup, launcher, game, and tools. Over time, that concrete UI tooling goal was deliberately replaced by a much broader and more durable architecture: a cross-platform, rendered, modular Dominium Workbench that would act as a production environment for the entire project rather than a one-off editor.

The user’s deeper aim was not just to make a GUI editor. They wanted the codebase to be portable, modular, extensible, replaceable, and professional-grade: closer to an operating environment or serious game engine platform than an indie one-off. The chat therefore expanded into a general doctrine for how Dominium should be structured: Domino as reusable deterministic substrate, Dominium as a product/game family on that substrate, Workbench as a production, validation, editing, packaging, inspection, evidence, and agent-control environment, and AIDE as the repo/task/checkpoint control plane. The most repeated idea was that the center of the system must not be a folder, an app, a renderer, a UI, a vendor library, or a tool. The center must be contracts, commands, services, documents, patches, providers, modules, packs, artifacts, diagnostics, evidence, tests, and replay/proof.

The discussion repeatedly corrected itself. Early plans had Windows-only UI Editor phases, TLV generation, Minecraft-style launcher/setup layout tests, and native Win32 previews. Those ideas were later judged useful as inspiration but wrong as final products. The user explicitly said the old UI Editor and Tool Editor should be abandoned and recycled. The replacement became “Dominium Workbench Platform”: one coherent cross-platform rendered app with many modules, workspaces, themes, provider profiles, and projections, all sharing the same command/result/refusal/document spine as the client, launcher, setup, server, CLI, TUI, and headless modes.

A second major line of discussion was repo governance and development process. The project’s queue evolved through Foundation Lock, product-spine slices, package mount, replay proof, barebones client shell, product-spine review, presentation contracts, and targeted cleanup. The final process doctrine became: development is non-blocking, promotion is evidence-blocked. AIDE should manage task branches, WorkUnits, blockers, repair tasks, checkpoint branches, warning dispositions, capability reality status, and main promotion; Codex should execute bounded patch tasks. Full CTest should not be the everyday prompt gate, but should remain release/full-gate debt.

A third line of discussion covered reusable presentation architecture: CLI, TUI/text, rendered GUI, OS-native GUI, and headless reports should be projections of the same semantic view/action model. Workbench should eventually author views, layouts, widgets, TUI panels, rendered UI documents, themes, workspaces, HUDs, setup/launcher screens, and evidence/test artifacts by editing structured documents through patches, not by hardcoding one-off GUI code.

A fourth line covered provider strategy. The user asked whether to use raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua. The conclusion was yes, aggressively, but only as fenced, replaceable providers behind first-party Dominium service contracts. Dominium should own commands, saves, replays, packs, UI documents, provider law, asset identity, and simulation law; raylib/SDL/Lua should provide early window/input/render/audio/asset/script/UI implementations.

The chat’s future relevance is high. It records not only current task order but the rationale for avoiding architecture drift: no GUI-only truth, no vendor-shaped architecture, no Workbench as authority, no broad structure cleanup after the structure became clean enough, no gameplay before product/projection foundations, and no false claims about fixture-only or stubbed capabilities. A future assistant must treat this as a planning and continuity package, verify the live repo before acting, and continue with narrow, evidence-backed prompts rather than restarting doctrine.



## 2. The Story of the Conversation

### 2.1 From mangled launcher UI to a proposed UI Editor

The conversation began with a practical problem: the current Windows launcher UI was mangled and flickered. The user wanted a graphical internal UI creation tool capable of visually designing pixel-perfect UIs and broad-strokes functionality for setup, launcher, game, and other tools. The early framing assumed a Windows-first UI Editor that could generate TLV directly and eventually feed a fuller Tool Editor. The user answered batches of questions about target systems, language constraints, current DUI/TLV backends, native widgets, DPI, and launcher flicker sources.

The early plan produced a sequence of Codex prompts: repo scan, canonical UI IR, TLV I/O, capability system, layout engine, splitter/tabs/scroll widgets, action codegen, Phase A UI Editor, Tool Editor bootstrap, flicker fixes, tests/docs, CLI import/export/ops scripting, and Minecraft-style launcher/setup logical layout tests. Screenshots were uploaded and used to define “Minecraft-style” as logical layout rather than graphical skin. These early outputs are preserved as artifacts, but they were later superseded.

### 2.2 Replacing UI Editor/Tool Editor with Workbench

The user then corrected the direction: OS-native SDK GUI design can be handled by first-party tools like Visual Studio and Xcode. What Dominium really needs is a cross-platform rendered tools environment using the same CLI, TUI, rendered GUI, renderer, command, pack, and runtime services as the client. The old UI Editor/Tool Editor became examples of the wrong final product: too Windows-first, too editor-specific, and too disconnected from the runtime. Their ideas should be recycled as Workbench modules, not preserved as the architecture.

This became the Dominium Workbench Platform: an integrated but modular production environment. Its purpose is not just to inspect Dominium but to build it—code, contracts, data, packs, UI/HUDs, themes, tests, artifacts, releases, and AIDE/Codex work units. Workbench must not own semantics. It must operate over commands, documents, patches, validation, diagnostics, evidence, and providers.

### 2.3 Generalizing UI across CLI, TUI, rendered GUI, native GUI, and headless

A large part of the chat established that all product surfaces should share one semantic spine. CLI, TUI/text, rendered GUI, OS-native GUI, and headless reports are projections of the same commands, typed results, diagnostics, refusals, evidence, documents, views, and actions. This was applied to client, launcher, setup, server, Workbench, AIDE, and future modules. The TUI was explicitly framed as a first-class deterministic, keyboard-first projection, not a toy ASCII fallback.

The rendered GUI system was framed as a data-described, themeable, renderer-agnostic system. Layouts, controls, themes, widgets, workspaces, HUDs, and views should be documents. Themes should be token-driven and packable. The user explored OEM+ mimic themes for Windows, Linux, and macOS styles, and primitive-only themes that require no external assets.

### 2.4 Repo governance, AIDE, queues, and product spine

The conversation then became strongly repo-governance oriented. It established a sequence around Foundation Lock, product-spine slices, AIDE workflow law, WorkUnit schemas, dev/main/checkpoint policy, checkpoint loop, capability reality ledger, presentation contracts, projection conformance, Workbench read-only shell, and universe explorer contracts. The user repeatedly pasted current status summaries and requested next prompts. The assistant generated numerous Codex prompts, including STATUS-RECONCILE-02, AIDE-WORKFLOW-LAW-01, AIDE-WORKUNIT-SCHEMA-01, AIDE-DEV-MAIN-POLICY-01, AIDE-CHECKPOINT-LOOP-01, AIDE-CAPABILITY-REALITY-LEDGER-01, and FULL-GATE-LEGACY-TEST-ROUTE-01.

A key process doctrine emerged: development is non-blocking, promotion is evidence-blocked. AIDE should manage parallel task branches, dirty worktree classification, blockers, repair tasks, checkpoints, and main promotion. Full CTest remains full-gate debt, not everyday prompt validation.

### 2.5 Provider strategy and raylib/SDL/Lua

Later, the user introduced a transcript about raylib/SDL/Lua. The result was a provider doctrine: use raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua aggressively, but only behind Dominium-owned service contracts. Directory structure should be service-first—runtime/render/providers/raylib, runtime/input/providers/sdl2, etc.—not vendor-first. Apps must remain generic, with profiles selecting providers. Third-party types must be fenced out of engine, game, contracts, content, saves, replays, packs, command/result schemas, and public SDK. Raylib is a seed provider suite, not the architecture.

### 2.6 Final state before preservation

At the point of this preservation request, the latest user-provided state said PRESENTATION-CONTRACT-01 had completed with warnings, and the user wanted to generate maintenance prompts first: FULL-GATE-LEGACY-TEST-ROUTE-01, PACK-INTERNAL-LAYOUT-CANON-01, RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01, PUBLIC-HEADER-ABI-PROMOTION-01, STORAGE-PACKAGE-PROVIDER-SPLIT-01, and POINTER-WIDTH-SERIALIZATION-AUDIT-01, before replanning the next mainline sequence. The assistant generated FULL-GATE-LEGACY-TEST-ROUTE-01 immediately before the user requested this preservation package.



## 3. Main Topics Discussed

### Topic 1 — Launcher UI, DUI/TLV, and the old UI Editor plan

FACT: The chat began with a plan to solve a mangled/flickering launcher UI and build an internal UI authoring tool. The user described an existing Dominium UI schema/state system using TLV and backends such as Win32 common controls, DGFX, and null. Early answers explored native widgets, custom rendering, DPI, layout, action codegen, and flicker mitigation. The conclusion changed: the specific UI Editor/Tool Editor product was superseded, but its concepts—visual layout, property inspector, canonical documents, CLI scripting, codegen, validation, preview—were preserved as future Workbench modules.

### Topic 2 — Dominium Workbench as the replacement product

FACT: The user accepted that the old UI Editor/Tool Editor were good general ideas but bad final products. The new direction became a cross-platform rendered Workbench that uses the same runtime, renderer, UI, command, pack, and diagnostics systems as the client. It should be one coherent shell with many modules and workspaces, not a monolithic editor. It should support human graphical work, CLI/TUI workflows, Codex/AIDE agent work, validation, preview, testing, release, pack/mod creation, and eventual self-hosting.

### Topic 3 — Unified command/result/view/projection architecture

FACT: A central conclusion was that CLI, TUI/text, rendered GUI, OS-native GUI, and headless reports should not be separate semantic implementations. They should be projections of the same commands, typed results, documents, views, diagnostics, refusals, evidence, and actions. This doctrine underpins presentation contracts, projection conformance, Workbench, launcher/setup/client/server reuse, and future OS-native UI.

### Topic 4 — AIDE as control plane and Codex as patch executor

FACT: AIDE was defined as a repo/control-plane harness that manages task state, queue state, evidence, blockers, repair tasks, branches, checkpoints, and promotion. Codex is a bounded patch executor. Development can be non-blocking on dev, but main promotion must be evidence-blocked. This led to a series of AIDE prompts: workflow law, WorkUnit schema, dev/main policy, checkpoint loop, and capability reality ledger.

### Topic 5 — Provider/service architecture and third-party acceleration

FACT: The user explored raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua. The conclusion was to use them aggressively as seed providers while keeping Dominium service contracts first-party. Raylib can provide early visible rendering, Workbench UI, assets, and audio, but cannot define simulation, replay, saves, commands, UI law, packs, or public SDK. Provider choices belong in profiles, not app directory names.

### Topic 6 — Themes, TUI, rendered GUI, and OEM+ mimic styles

FACT: The chat covered modular themes, style tokens, control skins, layout metrics, TUI themes, primitive-only rendered themes, and OEM+ OS-style mimic profiles for Windows, Linux, and macOS. The goal is not legal/pixel-perfect copying of proprietary assets but a rendered, modular, packable system that can mimic layout/geometry/density/control language and support modder expectations.

### Topic 7 — Repo structure, full-gate cleanup, and targeted maintenance

FACT: The chat repeatedly emphasized that top-level structure was now clean enough and broad structure cleanup should stop. Remaining work should be targeted: full-gate legacy test routing, pack-internal layout canon, runtime/engine residual taxonomy, public header ABI promotion, storage/package provider split, and pointer-width serialization audit. FULL-GATE-LEGACY-TEST-ROUTE-01 was generated as the next maintenance prompt.

### Topic 8 — Universe Explorer as future product north-star

INFERENCE: The user and assistant converged on a possible first meaningful product identity: a read-only Universe Explorer proving 1:1-scale inspection, no-modal-loading, reference frames, streaming, sparse materialization, fidelity degradation, provenance, and renderer purity. It should begin headlessly and read-only, then become visual, and only later transition toward embodiment/gameplay.



## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted to preserve and understand this entire chat; build a durable future-proof architecture; make Workbench into a production environment; reuse all code/data/modules/packs across client, server, setup, launcher, Workbench, and future Domino games; use Codex/AIDE efficiently; support CLI/TUI/rendered/native projections; and avoid one-off indie-project architecture.

### 4.2 Inferred Goals

INFERENCE: The user wants to avoid losing months of architectural reasoning, prevent future assistants from restarting old debates, and convert the chat into material for a master Project Spec Book. The user also wants to accelerate development with parallel Codex tasks without sacrificing repo integrity.

### 4.3 Goals That Changed Over Time

The original goal was a Windows UI Editor to fix the launcher. That changed into a modular cross-platform Workbench. The goal of native widgets changed into optional OS-native projections, while rendered GUI became a first-party portable path. The goal of folder cleanup changed into targeted maintenance once structure became clean enough. The goal of raylib usage changed from possible dependency to seed provider suite behind service contracts.

### 4.4 Goals Still Unresolved

Unresolved goals include confirming live repo state, executing pending maintenance and projection prompts, building read-only Workbench, implementing provider manifests/fences, building raylib provider wedge, proving Universe Explorer headlessly/visually, and eventually building authoring/self-hosting modules.


## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
| --- | --- | --- | --- | --- | --- |
| DECISION-01 | Domino is the reusable deterministic substrate; Dominium is one product/game family on it. | Accepted/active | Allows reuse for other games and prevents Dominium-specific systems from contaminating the engine substrate. | 4 | FACT |
| DECISION-02 | Workbench is not authority; it is a production environment over contracts, commands, services, documents, patches, evidence, modules, packs, and providers. | Accepted/active | Prevents a second GUI framework and keeps CLI/TUI/GUI/headless parity. | 4 | FACT |
| DECISION-03 | Abandon old UI Editor / Tool Editor as final products; recycle their ideas into Workbench modules. | Accepted/active | Avoids Windows-first one-off tooling and moves to cross-platform rendered tools. | 5 | FACT |
| DECISION-04 | CLI, TUI/text, rendered GUI, OS-native GUI, and headless are projections of the same semantic command/result/view system. | Accepted/active | Prevents separate implementations and enables reuse across client, server, setup, launcher, and Workbench. | 4 | FACT |
| DECISION-05 | Use progressive self-hosting: seed substrate first, then Workbench edits safe artifacts, then its own presentation, then products. | Accepted/active | Avoids circular dependency and unsafe self-modifying Workbench. | 4 | FACT |
| DECISION-06 | Stop broad structure cleanup once canonical active structure is clean enough; use targeted maintenance lanes. | Accepted/latest plan | Avoids cleanup spiral. | 4 | FACT |
| DECISION-07 | Use AIDE as governor/ledger/checkpoint/repair system and Codex as bounded patch executor. | Accepted/active | Supports parallel development without corrupting main. | 4 | FACT |
| DECISION-08 | Development is non-blocking; promotion is evidence-blocked. | Accepted/active | Allows progress on dev while protecting main. | 5 | FACT |
| DECISION-09 | Use task branches/worktrees; do not let multiple agents mutate shared dev directly. | Accepted/active | Prevents conflicts and stale AIDE state. | 4 | FACT |
| DECISION-10 | Current mainline language doctrine moved from C89/C++98 ideas to C17 + C++17 with C-compatible ABI boundaries. | Accepted but verify live repo | Improves maintainability while preserving ABI portability. | 3 | UNCERTAIN / UNVERIFIED |
| DECISION-11 | Use raylib/rlgl/rlsw/raygui/raudio/SDL2/Lua aggressively only as replaceable providers behind Dominium service contracts. | Accepted/conceptual | Gives fast visible progress without architectural lock-in. | 4 | FACT/INFERENCE |
| DECISION-12 | Do not make raylib, SDL2, Lua, or app variants define the architecture. | Accepted/conceptual | Prevents vendor-shaped directory and API lock-in. | 4 | FACT/INFERENCE |
| DECISION-13 | Raylib rlsw is a raylib software-provider, not the canonical Dominium software renderer. | Accepted/conceptual | Preserves first-party reference renderer slot. | 4 | FACT/INFERENCE |
| DECISION-14 | Universe Explorer is a north-star read-only inspection product, not gameplay. | Tentative/accepted as plan | Proves no-modal-loading, reference frames, streaming, materialization, projection before embodiment. | 3 | INFERENCE |
| DECISION-15 | Workbench should begin read-only before editing artifacts. | Accepted/active | Reduces risk and proves projection/evidence first. | 4 | FACT/INFERENCE |
| DECISION-16 | Full CTest remains full-gate/T4 debt, not every-prompt gate. | Accepted/latest plan | Supports parallel productivity. | 4 | FACT/UNVERIFIED |

### DECISION-01 — Domino is the reusable deterministic substrate; Dominium is one product/game family on it.

Status: Accepted/active. Basis: Repeated user acceptance and later handoffs.. Rationale: Allows reuse for other games and prevents Dominium-specific systems from contaminating the engine substrate. Implications: Affects roots, APIs, provider boundaries, Workbench, packs, and future game projects. Caveat/label: FACT.
### DECISION-02 — Workbench is not authority; it is a production environment over contracts, commands, services, documents, patches, evidence, modules, packs, and providers.

Status: Accepted/active. Basis: User accepted replacement of old UI/Tool Editor with Workbench platform.. Rationale: Prevents a second GUI framework and keeps CLI/TUI/GUI/headless parity. Implications: Workbench must call command/service/document/patch flows, not mutate truth privately. Caveat/label: FACT.
### DECISION-03 — Abandon old UI Editor / Tool Editor as final products; recycle their ideas into Workbench modules.

Status: Accepted/active. Basis: User explicitly said old UI editor/tool editor were good general ideas but bad final products, to abandon and recycle them.. Rationale: Avoids Windows-first one-off tooling and moves to cross-platform rendered tools. Implications: Old concepts become Interface Studio, UI/HUD Sandbox, Theme Lab, Module/Pack Foundry, App Composer. Caveat/label: FACT.
### DECISION-04 — CLI, TUI/text, rendered GUI, OS-native GUI, and headless are projections of the same semantic command/result/view system.

Status: Accepted/active. Basis: Repeatedly discussed and accepted.. Rationale: Prevents separate implementations and enables reuse across client, server, setup, launcher, and Workbench. Implications: Requires presentation contracts and projection conformance before rich UI. Caveat/label: FACT.
### DECISION-05 — Use progressive self-hosting: seed substrate first, then Workbench edits safe artifacts, then its own presentation, then products.

Status: Accepted/active. Basis: User accepted progressive self-hosting model.. Rationale: Avoids circular dependency and unsafe self-modifying Workbench. Implications: Defines Workbench maturity ladder S0-S6. Caveat/label: FACT.
### DECISION-06 — Stop broad structure cleanup once canonical active structure is clean enough; use targeted maintenance lanes.

Status: Accepted/latest plan. Basis: User shifted to full-gate legacy test routing and targeted cleanup.. Rationale: Avoids cleanup spiral. Implications: Maintenance tasks include full-gate legacy test route, pack layout canon, residual taxonomy, public ABI promotion. Caveat/label: FACT.
### DECISION-07 — Use AIDE as governor/ledger/checkpoint/repair system and Codex as bounded patch executor.

Status: Accepted/active. Basis: Explicit in multiple handoff plans.. Rationale: Supports parallel development without corrupting main. Implications: Requires workflow law, WorkUnit schema, dev/main policy, checkpoint loop, capability reality ledger. Caveat/label: FACT.
### DECISION-08 — Development is non-blocking; promotion is evidence-blocked.

Status: Accepted/active. Basis: Repeated as doctrine in user and assistant handoffs.. Rationale: Allows progress on dev while protecting main. Implications: Shapes branch model and testing policy. Caveat/label: FACT.
### DECISION-09 — Use task branches/worktrees; do not let multiple agents mutate shared dev directly.

Status: Accepted/active. Basis: Discussed as required before larger parallelism.. Rationale: Prevents conflicts and stale AIDE state. Implications: Requires branch role policy and checkpoint loop. Caveat/label: FACT.
### DECISION-10 — Current mainline language doctrine moved from C89/C++98 ideas to C17 + C++17 with C-compatible ABI boundaries.

Status: Accepted but verify live repo. Basis: User pasted synthesis stating this; earlier chat had C89/C++98 assumptions.. Rationale: Improves maintainability while preserving ABI portability. Implications: Needs live verification in CMake/build policy before final spec merge. Caveat/label: UNCERTAIN / UNVERIFIED.
### DECISION-11 — Use raylib/rlgl/rlsw/raygui/raudio/SDL2/Lua aggressively only as replaceable providers behind Dominium service contracts.

Status: Accepted/conceptual. Basis: User asked what I thought; assistant agreed and refined.. Rationale: Gives fast visible progress without architectural lock-in. Implications: Provider work should follow AIDE/presentation and manifest/fence/service contract wedges. Caveat/label: FACT/INFERENCE.
### DECISION-12 — Do not make raylib, SDL2, Lua, or app variants define the architecture.

Status: Accepted/conceptual. Basis: Explicitly discussed as service-first/provider-backed doctrine.. Rationale: Prevents vendor-shaped directory and API lock-in. Implications: Requires forbidden include validator and provider manifests. Caveat/label: FACT/INFERENCE.
### DECISION-13 — Raylib rlsw is a raylib software-provider, not the canonical Dominium software renderer.

Status: Accepted/conceptual. Basis: Discussed and accepted in provider doctrine.. Rationale: Preserves first-party reference renderer slot. Implications: Directory split: runtime/render/providers/software vs runtime/render/providers/rlsw. Caveat/label: FACT/INFERENCE.
### DECISION-14 — Universe Explorer is a north-star read-only inspection product, not gameplay.

Status: Tentative/accepted as plan. Basis: Discussed after structure cleanup as first meaningful product identity.. Rationale: Proves no-modal-loading, reference frames, streaming, materialization, projection before embodiment. Implications: Implementation should start with contracts/headless proof, not renderer/gameplay. Caveat/label: INFERENCE.
### DECISION-15 — Workbench should begin read-only before editing artifacts.

Status: Accepted/active. Basis: Repeated in self-hosting safety stages.. Rationale: Reduces risk and proves projection/evidence first. Implications: First Workbench shell should inspect commands, diagnostics, artifacts, graphs, packs, status. Caveat/label: FACT/INFERENCE.
### DECISION-16 — Full CTest remains full-gate/T4 debt, not every-prompt gate.

Status: Accepted/latest plan. Basis: Repeated; user wants speed on dev with full suite at main/checkpoints.. Rationale: Supports parallel productivity. Implications: Requires targeted validators, fast strict, and checkpoint policy. Caveat/label: FACT/UNVERIFIED.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

### REJECTED-01 — Old Windows-only UI Editor as final product

Status: Superseded. It was considered because it addressed a real need, but it was rejected or superseded because too narrow, native-widget-first, not cross-platform/reusable; replaced by workbench modules. Reconsideration: Temporary for bootstrap only if ever needed.. Related workstream: WORKSTREAM-05. Label: FACT.
### REJECTED-02 — Tool Editor as monolithic editor

Status: Superseded. It was considered because it addressed a real need, but it was rejected or superseded because would become separate architecture; replaced by modular workbench platform. Reconsideration: Could reappear as workspace/module concept only.. Related workstream: WORKSTREAM-05. Label: FACT.
### REJECTED-03 — Workbench as authority/center of architecture

Status: Rejected. It was considered because it addressed a real need, but it was rejected or superseded because contracts/commands/services/providers/packs/artifacts/proof are center; workbench is surface. Reconsideration: Reconsider only as UX language, not architecture.. Related workstream: WORKSTREAM-05. Label: FACT.
### REJECTED-04 — Broad root/directory rewrites after structure became clean enough

Status: Deprioritized. It was considered because it addressed a real need, but it was rejected or superseded because risk of cleanup spiral; remaining work targeted. Reconsideration: If validators show blockers.. Related workstream: WORKSTREAM-07. Label: FACT.
### REJECTED-05 — Raylib-shaped architecture or apps/client/rendered/raylib variants

Status: Rejected. It was considered because it addressed a real need, but it was rejected or superseded because vendor/provider must not define architecture. Reconsideration: Temporary proof folders allowed with retirement notes.. Related workstream: WORKSTREAM-06. Label: FACT/INFERENCE.
### REJECTED-06 — Pure C99 or pure C++11 as mainline baseline

Status: Rejected/superseded. It was considered because it addressed a real need, but it was rejected or superseded because c17+c++17 with c-compatible abi deemed better fit. Reconsideration: If platform/toolchain evidence contradicts.. Related workstream: WORKSTREAM-01. Label: UNCERTAIN / UNVERIFIED.


## 7. Important Reasoning, Rationale, and Tradeoffs

The dominant tradeoff was speed versus architectural contamination. The user wanted fast progress, visual tools, and agentic development, but not at the cost of making temporary tools permanent architecture. The recurring solution was to split identity from implementation: commands, contracts, documents, packs, modules, services, and provider manifests are stable; individual folders, renderers, libraries, UI skins, and Workbench panels are replaceable.

A second tradeoff was governance versus motion. Too little governance had already produced cleanup debt; too much governance risked stalling the project. The compromise became a queue model: Foundation and product-spine contracts first, then narrow slices, then limited parallel dev on task branches, then checkpointed promotion. Full CTest remains a release/full-gate concern rather than a prompt-by-prompt requirement.

A third tradeoff was native GUI versus rendered portability. The user recognized that Visual Studio/Xcode/AppKit/Win32 tooling already exists for OS SDK GUI work. The unique Dominium value is a rendered, cross-platform, modular presentation system shared by the client, Workbench, launcher, setup, server, CLI/TUI/headless, and future mods.

A fourth tradeoff was third-party acceleration versus engine independence. Raylib, SDL2, and Lua can speed up the first visible product slices; they become safe only if fenced behind Dominium service contracts and conformance tests. This preserves replaceability while allowing practical progress.



## 8. Plans, Future Work, and Next Steps

The immediate future work from the latest state in this chat is a maintenance set followed by mainline projection and Workbench planning. The user explicitly said to generate first: FULL-GATE-LEGACY-TEST-ROUTE-01, PACK-INTERNAL-LAYOUT-CANON-01, RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01, PUBLIC-HEADER-ABI-PROMOTION-01, STORAGE-PACKAGE-PROVIDER-SPLIT-01, and POINTER-WIDTH-SERIALIZATION-AUDIT-01. FULL-GATE-LEGACY-TEST-ROUTE-01 was generated immediately before this preservation task.

After maintenance and replan, the user listed the sequence: PROJECTION-CONFORMANCE-01, ACCESSIBILITY-CONTRACT-01, TEXT-LOCALIZATION-CONTRACT-01, WORKBENCH-SHELL-READONLY-01, UNIVERSE-EXPLORER-CONTRACT-01, UNIVERSE-EXPLORER-HEADLESS-01, PROVIDER-MANIFEST-WEDGE-01, SERVICE-CONTRACT-WEDGE-01, THIRD-PARTY-FENCE-01, RAYLIB-PROVIDER-WEDGE-01, and UNIVERSE-EXPLORER-VISUAL-01. PRESENTATION-CONTRACT-01 was already reported complete before that list.

Recommended next-action sequence in this chat:

1. Execute or review FULL-GATE-LEGACY-TEST-ROUTE-01.
2. Generate PACK-INTERNAL-LAYOUT-CANON-01.
3. Generate RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01.
4. Generate PUBLIC-HEADER-ABI-PROMOTION-01.
5. Generate STORAGE-PACKAGE-PROVIDER-SPLIT-01.
6. Generate POINTER-WIDTH-SERIALIZATION-AUDIT-01.
7. Replan based on live repo state.
8. Continue to PROJECTION-CONFORMANCE-01.

Major dependencies: live repo state must be verified; broad feature blockers must remain; full CTest debt should be tracked, not hidden; presentation contracts should precede Workbench and renderer implementation; provider fences should precede raylib implementation.


## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

- CONSTRAINT-01: Do not turn Workbench into authority. Practical implication: Workbench must use commands/services/documents/patches/evidence.
- CONSTRAINT-02: Broad Workbench UI, provider runtime, package runtime, module loader, renderer/native GUI, gameplay, release publication remain blocked until gates authorize. Practical implication: Future prompts must preserve non-goals.
- CONSTRAINT-03: No broad structure cleanup unless validator/audit blocks next slice. Practical implication: Use targeted maintenance lanes.
- CONSTRAINT-04: CLI/TUI/rendered/native/headless must be projections of same command/result/view spine. Practical implication: Presentation work must avoid separate semantics per UI mode.
- CONSTRAINT-05: Third-party types must not leak into engine/game/contracts/content/saves/replays/public SDK. Practical implication: Provider code must translate to Dominium types.
- CONSTRAINT-06: Full CTest is full-gate/T4 debt, not ordinary prompt gate. Practical implication: Dev tasks run targeted validators/fast strict; main/checkpoint more stringent.
- CONSTRAINT-07: Stable identity is contractual, not path-based. Practical implication: Use IDs/manifests/registries, not folder names, as identity.
- CONSTRAINT-08: Apps compose; runtime implements; contracts define law; content supplies authored payloads; tools validate/generate/migrate. Practical implication: Prevents apps/tools becoming runtime or truth owners.
- CONSTRAINT-09: Development non-blocking; promotion evidence-blocked. Practical implication: Dev may accept classified warnings; main requires checkpoint/evidence.
- CONSTRAINT-10: The preservation report itself is for THIS CHAT ONLY unless labelled PROJECT-CONTEXT. Practical implication: Do not merge other chat facts unlabelled.

### 9.2 Inferred Constraints and Preferences

- The user wants maximal continuity and minimal repeated re-explanation. Future assistants should treat this preservation package and the generated handoffs as continuity artifacts.
- The user values engineering discipline over short-term demos, but still wants speed through parallel Codex/AIDE work.

### 9.3 Uncertain or Unestablished Preferences

- Exact final degree of raylib/SDL/Lua usage is conceptual until provider tasks are run.
- Exact live repo state after this preservation task is unverified.


## 10. Files, Artifacts, Outputs, and Prompts

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Prompt UU1–UU6 plan for UI Editor import/CLI/ops/Minecraft launcher/setup tests | Prompt plan | Earlier plan for old UI Editor toolchain. | Superseded/recycled | This chat | Yes, as rejected/superseded context | Ideas became Workbench modules and CLI/presentation concepts. | FACT |
| ARTIFACT-02 | Final UI Editor implementation prompt with import/CLI/Minecraft tests | Codex prompt | Implementation prompt for old Phase A UI Editor. | Superseded | This chat | Yes, as historical artifact | Shows why old approach was abandoned. | FACT |
| ARTIFACT-03 | Screenshots/mockups of Workbench themes/modules | Images | Visual references for OEM+ themes, modules, TUI, Workbench surfaces. | Reference only | Uploaded in chat | Yes | Used to derive modular theme/workspace concepts, not exact design requirements. | FACT |
| ARTIFACT-04 | AIDE/Workbench/product-spine handoff prompt | Handoff text | Long carry-forward prompt summarizing repo state and next tasks. | Important | This chat | Yes | Should inform future chat bootstrap; live repo must still be verified. | FACT |
| ARTIFACT-05 | Codex prompts: STATUS-RECONCILE-02, AIDE-WORKFLOW-LAW-01, AIDE-WORKUNIT-SCHEMA-01, AIDE-DEV-MAIN-POLICY-01, AIDE-CHECKPOINT-LOOP-01, AIDE-CAPABILITY-REALITY-LEDGER-01 | Codex prompts | Detailed prompts for AIDE workflow layer. | Generated | This chat | Yes | Some reportedly executed later; verify live repo. | FACT |
| ARTIFACT-06 | Codex prompt: FULL-GATE-LEGACY-TEST-ROUTE-01 | Codex prompt | Targeted full-gate stale-root cleanup prompt. | Generated immediately before preservation request | This chat | Yes | Potential next execution depending on user plan. | FACT |
| ARTIFACT-07 | User-uploaded Pasted text.txt preservation instruction | Uploaded file | Maximum-fidelity preservation package instructions. | Active input | Uploaded file | Yes | Primary instruction for this response. | FACT |
| ARTIFACT-08 | This preservation package files and zip | Generated export | Downloadable report/register/spec/handoff files created by this response. | Created now | This response | Yes | Use for aggregation and future chat transfer. | FACT |

## 11. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | What is the live repo status at the time of continuation? | The chat includes changing queue and commit state. | User reported latest tasks and statuses. | Whether subsequent Codex runs changed queue/audits after this preservation. | Verify `.aide/queue/current.toml`, latest commits, relevant audits. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Should the next executable task be FULL-GATE-LEGACY-TEST-ROUTE-01 or PROJECTION-CONFORMANCE-01? | User said first generate maintenance prompts, then replan. | FULL-GATE prompt was generated immediately before preservation request. | Whether user will run maintenance lane first or mainline projection. | Ask user or check queue after files. | P0 | WORKSTREAM-07 | FACT/UNCERTAIN |
| QUESTION-03 | Is C17/C++17 fully implemented in CMake or partially doctrinal? | Language baseline changed during chat. | Later handoffs state C17/C++17 baseline. | Live CMake/toolchain details. | Verify repo files before spec lock. | P1 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | How aggressively should provider/raylib work start relative to presentation/projection and Workbench read-only shell? | Provider strategy was accepted conceptually but timing deferred. | Recommended after AIDE/presentation/fence/manifest tasks. | Exact queue timing after maintenance tasks. | Replan after projection conformance and maintenance status. | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-05 | What is the final target for Universe Explorer as first product identity? | It is a north-star but not implemented. | Headless/read-only first, visual later, embodiment after. | How soon to schedule after read-only Workbench/presentation. | Formalize UNIVERSE-EXPLORER-CONTRACT-01 when gates allow. | P2 | WORKSTREAM-08 | INFERENCE |

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats stale repo status as current. | Wrong prompts, duplicate tasks, stale queues. | Medium | High | Always verify live repo before current-status decisions. | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| RISK-02 | Workbench implementation starts before projection conformance. | Separate UI semantics, later rewrite. | Medium | High | Require presentation/projection contracts first. | WORKSTREAM-04 | FACT/INFERENCE |
| RISK-03 | Raylib/SDL/Lua provider types leak into stable contracts or game state. | Vendor lock-in, replay/save instability. | Medium | High | Forbidden include/type validator and provider fences. | WORKSTREAM-06 | FACT/INFERENCE |
| RISK-04 | Full CTest debt remains ignored too long. | Release gate remains blocked. | Medium | Medium | Targeted full-gate legacy test routing and debt ledger. | WORKSTREAM-07 | FACT/UNVERIFIED |
| RISK-05 | Capability status overclaimed. | Docs/Workbench say implemented when only fixture/stub exists. | High | High | Capability Reality Ledger. | WORKSTREAM-02 | FACT |
| RISK-06 | Parallel Codex tasks conflict on coordinator files. | Queue/status corruption. | Medium | High | Coordinator ownership rules and checkpoint loop. | WORKSTREAM-02 | FACT |
| RISK-07 | Universe Explorer free-camera becomes implicit gameplay movement. | Wrong gameplay model and authority leakage. | Low-Medium | High | Separate observer inspection authority from embodied actor authority. | WORKSTREAM-08 | INFERENCE |
| RISK-08 | Preservation report overstates decisions from assistant suggestions. | Bad spec aggregation. | Medium | High | Label decisions accepted by user vs assistant suggestions. | WORKSTREAM-01 | FACT |


## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat should feed several chapters of a future master Project Spec Book. It contributes the clearest articulation of the Workbench replacement plan; the AIDE/Codex development process; unified presentation architecture; provider/service/fence strategy; modular theme/UI/TUI/rendered GUI doctrine; and the transition from broad cleanup to targeted maintenance plus product-spine slices.

Formal requirement candidates include: Workbench must not be authority; CLI/TUI/rendered/native/headless must project the same command/result/view model; third-party libraries must be providers behind service contracts; capability reality status must distinguish planned/specified/fixture/stubbed/implemented/tested/exposed/release_supported; and promotion to main must be evidence-blocked.

Background context includes the abandoned UI Editor/Tool Editor plan, Minecraft-style launcher/setup logical layouts, OEM+ theme aspirations, TUI design mockups, and long-range world simulation doctrine. These should not all become immediate requirements.

Verification before merge: live repo status, C17/C++17 baseline, current queue, and whether latest generated prompts have run.



## 14. What I Should Remember

- The chat’s center of gravity moved from a Windows UI Editor to a cross-platform Dominium Workbench Platform.
- Workbench is an interface over contracts, commands, documents, patches, services, providers, packs, modules, artifacts, diagnostics, and evidence. It is not authority.
- AIDE is the coordination system; Codex is the patch executor. Development should be non-blocking; promotion should be evidence-blocked.
- The old UI Editor/Tool Editor plan is superseded but not wasted; it becomes Interface Studio, UI/HUD Sandbox, Theme Lab, Module/Pack Foundry, and App Composer modules.
- The immediate current path in this chat is maintenance and projection: full-gate legacy test routing, pack layout canon, runtime/engine residual taxonomy, public ABI promotion, storage/package provider split, pointer-width audit, then projection conformance.
- Raylib/SDL/Lua are accelerators, not architecture. They belong behind Dominium-owned service contracts and provider manifests.
- Universe Explorer is a future read-only inspection north-star, not gameplay and not free-camera movement authority.
- The biggest live risk is stale repo status; verify before generating current-state prompts.



## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- “Explain why the old UI Editor plan was abandoned and how its ideas survive in Workbench.”
- “Summarize the difference between Workbench as surface and contracts/services as system center.”

### 15.2 Decisions
- “Which decisions in this chat are final, and which are only tentative?”
- “What decision would most likely need revisiting if the live repo contradicts our assumed queue state?”

### 15.3 Tasks and Next Actions
- “Generate PACK-INTERNAL-LAYOUT-CANON-01 next.”
- “Make a dependency map showing which maintenance prompts can run in parallel.”

### 15.4 Artifacts and Files
- “List all Codex prompts generated in this chat and their intended execution order.”
- “Which uploaded images influenced the Workbench/theme direction?”

### 15.5 Risks and Verification
- “What should be verified in the repo before executing the next prompt?”
- “What are the highest-risk false implementation claims to avoid?”

### 15.6 Future Spec Book / Aggregation
- “Which parts of this report should become formal requirements in the Project Spec Book?”
- “What overlaps should I expect with other old-chat reports?”

### 15.7 Deep-Dive Questions Specific to This Chat
- “Design the first read-only Workbench shell slice using the presentation contract.”
- “Write the provider manifest doctrine as formal requirements.”
- “Explain the Universe Explorer headless proof as a task sequence.”



## 16. Compact Human Summary

This chat began as a practical tool/UI problem and became one of the central architecture-planning conversations for Dominium. The original issue was that the Windows launcher UI looked mangled and flickered, and the user wanted a graphical Tool Editor/UI Editor to design pixel-perfect UIs and broad functionality for launcher, setup, game, and tools. Early discussion produced a detailed UI Editor plan: Windows-first editor, canonical UI IR, TLV/JSON output, layout engine, capability system, code generation, CLI scripting, import/export, and launcher/setup layout tests. That plan was useful but later superseded.

The major turning point was the user’s recognition that the old UI Editor and Tool Editor were good ideas but wrong final products. The user wanted a cross-platform rendered tools environment using the same systems as the client, not a Windows-native one-off editor. This became the Dominium Workbench Platform: one coherent shell with many modules and workspaces, built on the same command, document, patch, view, projection, renderer, pack, diagnostics, and evidence spine as the rest of Dominium.

The core architectural doctrine became: Domino is the reusable deterministic substrate; Dominium is a game/product family built on it; Workbench is the production environment; AIDE is the repo/control-plane harness; Codex is a bounded patch executor; contracts are law; tests/replay/evidence are proof. Workbench must not be authority. It should design artifacts, while runtime executes artifacts, contracts constrain them, content packages them, apps consume them, tests prove them, AIDE governs changes, and Codex patches code.

The chat repeatedly unified CLI, TUI/text, rendered GUI, native GUI, and headless operation. These are not separate products or separate behavioral systems. They are projections of the same command/result/refusal/document/view/action model. This is essential for client, server, launcher, setup, Workbench, AIDE, and future modding. The TUI was framed as a serious low-dependency deterministic interface, not a toy fallback. The rendered GUI was framed as a cross-platform data-described UI system with layouts, controls, themes, widget compositions, workspaces, HUDs, and theme packs.

Another major theme was development governance. The chat moved through many repo-state plans: Foundation Lock, package mount, replay proof, barebones client shell, product spine review, AIDE workflow law, WorkUnit schema, dev/main policy, checkpoint loop, and capability reality ledger. The doctrine became: development is non-blocking; promotion is evidence-blocked. Dev can accumulate classified work and warnings, but main should receive only checkpointed, evidence-backed states. Full CTest remains release/full-gate debt; fast strict and targeted validators are normal task gates.

The provider strategy was also clarified. Raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua should be used aggressively to accelerate visible progress. However, they must be replaceable providers behind Dominium service contracts. Dominium owns commands, views, assets, saves, replays, packs, modules, provider law, and simulation law. Third-party types must not leak into engine, game, contracts, content, save/replay formats, pack schemas, public SDK, or deterministic domain law. Apps must remain generic; profiles select providers.

By the final state of the chat, PRESENTATION-CONTRACT-01 had reportedly completed with warnings, and the user wanted a targeted maintenance sequence before continuing: FULL-GATE-LEGACY-TEST-ROUTE-01, PACK-INTERNAL-LAYOUT-CANON-01, RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01, PUBLIC-HEADER-ABI-PROMOTION-01, STORAGE-PACKAGE-PROVIDER-SPLIT-01, and POINTER-WIDTH-SERIALIZATION-AUDIT-01. FULL-GATE-LEGACY-TEST-ROUTE-01 was generated immediately before this preservation task. After those, the plan returns to PROJECTION-CONFORMANCE-01, ACCESSIBILITY-CONTRACT-01, TEXT-LOCALIZATION-CONTRACT-01, WORKBENCH-SHELL-READONLY-01, Universe Explorer contracts, provider manifest/service/fence/raylib wedges, and later visual Explorer.

The most important preservation point is that this chat records a mature architecture doctrine and transition plan. It should not be reduced to a list of prompts. Future assistants must understand why the plan changed: from one-off editor to reusable Workbench, from UI widgets to semantic projections, from folder structure to contracts/proof, from direct Codex execution to AIDE-governed task branches, and from vendor libraries to fenced providers. The best next action is to continue the targeted maintenance sequence, starting with or reviewing FULL-GATE-LEGACY-TEST-ROUTE-01, then generate the remaining maintenance prompts, verify the live repo, and proceed to projection conformance only when current status supports it.
