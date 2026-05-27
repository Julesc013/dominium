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


# STRUCTURED REGISTERS

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Dominium/Domino architectural identity | Preserve the distinction between Domino as reusable deterministic substrate and Dominium as game/product family. | Conceptually settled in this chat; repo-current status requires verification. | Contract-governed reusable substrate supporting Dominium and other games/apps. | Active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | AIDE control-plane workflow | Make AIDE the scheduler/ledger/checkpoint/repair system for bounded Codex work. | Workflow, WorkUnit, dev/main, checkpoint, and capability reality prompts were generated or discussed. | Parallel task execution with evidence-blocked main promotion. | Active | P0 | 4 | FACT |
| WORKSTREAM-03 | Product spine and queue sequencing | Continue narrow product-spine tasks while broad features remain blocked. | Package mount, replay proof, barebones shell, product spine review, presentation contract and full-gate tasks were discussed; latest execution state is user-reported, not independently verified here. | Proven command/result/view/replay/client shell leading to presentation/projection and Workbench read-only shell. | Active | P0 | 3 | UNCERTAIN / UNVERIFIED |
| WORKSTREAM-04 | Unified presentation architecture | Unify CLI, TUI/text, rendered GUI, native GUI, and headless as projections of commands/results/views. | Presentation contract completed per user report; projection conformance remains next. | One view/action/projection model shared by products and Workbench. | Active | P0 | 4 | FACT/UNVERIFIED |
| WORKSTREAM-05 | Workbench production environment | Make Workbench the visual/agentic production environment, not the authority. | Strong conceptual plan; implementation deferred until contracts/projections/read-only shell. | Progressive self-hosting Workbench that edits artifacts through document patches and evidence. | Planned | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-06 | Renderer/provider strategy | Use raylib/SDL/Lua as fenced providers under Dominium service contracts. | Detailed provider doctrine decided conceptually; implementation not yet started. | Service-first provider system with manifests, profiles, conformance tests, and third-party fences. | Planned | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-07 | Structure stabilization and full-gate cleanup | Stop broad structure cleanup; run targeted maintenance such as full-gate legacy test routing. | User requested FULL-GATE-LEGACY-TEST-ROUTE-01 next; prompt generated. | Canonical active structure with full-gate tests no longer expecting retired roots. | Active | P0 | 4 | FACT |
| WORKSTREAM-08 | Universe Explorer north-star | Build read-only Universe Explorer as first meaningful inspection product slice after presentation/projection. | Discussed as future path, not yet implementation. | Headless and then visual no-modal-loading universe inspection proving reference frames, streaming, materialization, and projection. | Planned | P2 | 3 | INFERENCE |
| WORKSTREAM-09 | Modular theme/UI/TUI/rendered system | Support modular layouts, controls, widgets, themes, OEM+ mimic styles, TUI profiles, and code-only primitive themes. | Discussed with screenshots and mockups; mostly conceptual. | Theme/control/layout/view system packable and testable across CLI/TUI/rendered/native. | Planned | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-10 | Long-range simulation/game doctrine | Preserve deep primitives, materialization, representation ladders, formalization, civilization, and failure ontology as future domain doctrine. | Discussed repeatedly but deferred. | Domain constitutions and slices after product spine and Workbench foundations. | Future | P3 | 3 | INFERENCE |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Domino is the reusable deterministic substrate; Dominium is one product/game family on it. | Accepted/active | Repeated user acceptance and later handoffs. | Allows reuse for other games and prevents Dominium-specific systems from contaminating the engine substrate. | Affects roots, APIs, provider boundaries, Workbench, packs, and future game projects. | WORKSTREAM-01 | 4 | FACT |
| DECISION-02 | Workbench is not authority; it is a production environment over contracts, commands, services, documents, patches, evidence, modules, packs, and providers. | Accepted/active | User accepted replacement of old UI/Tool Editor with Workbench platform. | Prevents a second GUI framework and keeps CLI/TUI/GUI/headless parity. | Workbench must call command/service/document/patch flows, not mutate truth privately. | WORKSTREAM-05 | 4 | FACT |
| DECISION-03 | Abandon old UI Editor / Tool Editor as final products; recycle their ideas into Workbench modules. | Accepted/active | User explicitly said old UI editor/tool editor were good general ideas but bad final products, to abandon and recycle them. | Avoids Windows-first one-off tooling and moves to cross-platform rendered tools. | Old concepts become Interface Studio, UI/HUD Sandbox, Theme Lab, Module/Pack Foundry, App Composer. | WORKSTREAM-05 | 5 | FACT |
| DECISION-04 | CLI, TUI/text, rendered GUI, OS-native GUI, and headless are projections of the same semantic command/result/view system. | Accepted/active | Repeatedly discussed and accepted. | Prevents separate implementations and enables reuse across client, server, setup, launcher, and Workbench. | Requires presentation contracts and projection conformance before rich UI. | WORKSTREAM-04 | 4 | FACT |
| DECISION-05 | Use progressive self-hosting: seed substrate first, then Workbench edits safe artifacts, then its own presentation, then products. | Accepted/active | User accepted progressive self-hosting model. | Avoids circular dependency and unsafe self-modifying Workbench. | Defines Workbench maturity ladder S0-S6. | WORKSTREAM-05 | 4 | FACT |
| DECISION-06 | Stop broad structure cleanup once canonical active structure is clean enough; use targeted maintenance lanes. | Accepted/latest plan | User shifted to full-gate legacy test routing and targeted cleanup. | Avoids cleanup spiral. | Maintenance tasks include full-gate legacy test route, pack layout canon, residual taxonomy, public ABI promotion. | WORKSTREAM-07 | 4 | FACT |
| DECISION-07 | Use AIDE as governor/ledger/checkpoint/repair system and Codex as bounded patch executor. | Accepted/active | Explicit in multiple handoff plans. | Supports parallel development without corrupting main. | Requires workflow law, WorkUnit schema, dev/main policy, checkpoint loop, capability reality ledger. | WORKSTREAM-02 | 4 | FACT |
| DECISION-08 | Development is non-blocking; promotion is evidence-blocked. | Accepted/active | Repeated as doctrine in user and assistant handoffs. | Allows progress on dev while protecting main. | Shapes branch model and testing policy. | WORKSTREAM-02 | 5 | FACT |
| DECISION-09 | Use task branches/worktrees; do not let multiple agents mutate shared dev directly. | Accepted/active | Discussed as required before larger parallelism. | Prevents conflicts and stale AIDE state. | Requires branch role policy and checkpoint loop. | WORKSTREAM-02 | 4 | FACT |
| DECISION-10 | Current mainline language doctrine moved from C89/C++98 ideas to C17 + C++17 with C-compatible ABI boundaries. | Accepted but verify live repo | User pasted synthesis stating this; earlier chat had C89/C++98 assumptions. | Improves maintainability while preserving ABI portability. | Needs live verification in CMake/build policy before final spec merge. | WORKSTREAM-01 | 3 | UNCERTAIN / UNVERIFIED |
| DECISION-11 | Use raylib/rlgl/rlsw/raygui/raudio/SDL2/Lua aggressively only as replaceable providers behind Dominium service contracts. | Accepted/conceptual | User asked what I thought; assistant agreed and refined. | Gives fast visible progress without architectural lock-in. | Provider work should follow AIDE/presentation and manifest/fence/service contract wedges. | WORKSTREAM-06 | 4 | FACT/INFERENCE |
| DECISION-12 | Do not make raylib, SDL2, Lua, or app variants define the architecture. | Accepted/conceptual | Explicitly discussed as service-first/provider-backed doctrine. | Prevents vendor-shaped directory and API lock-in. | Requires forbidden include validator and provider manifests. | WORKSTREAM-06 | 4 | FACT/INFERENCE |
| DECISION-13 | Raylib rlsw is a raylib software-provider, not the canonical Dominium software renderer. | Accepted/conceptual | Discussed and accepted in provider doctrine. | Preserves first-party reference renderer slot. | Directory split: runtime/render/providers/software vs runtime/render/providers/rlsw. | WORKSTREAM-06 | 4 | FACT/INFERENCE |
| DECISION-14 | Universe Explorer is a north-star read-only inspection product, not gameplay. | Tentative/accepted as plan | Discussed after structure cleanup as first meaningful product identity. | Proves no-modal-loading, reference frames, streaming, materialization, projection before embodiment. | Implementation should start with contracts/headless proof, not renderer/gameplay. | WORKSTREAM-08 | 3 | INFERENCE |
| DECISION-15 | Workbench should begin read-only before editing artifacts. | Accepted/active | Repeated in self-hosting safety stages. | Reduces risk and proves projection/evidence first. | First Workbench shell should inspect commands, diagnostics, artifacts, graphs, packs, status. | WORKSTREAM-05 | 4 | FACT/INFERENCE |
| DECISION-16 | Full CTest remains full-gate/T4 debt, not every-prompt gate. | Accepted/latest plan | Repeated; user wants speed on dev with full suite at main/checkpoints. | Supports parallel productivity. | Requires targeted validators, fast strict, and checkpoint policy. | WORKSTREAM-02 | 4 | FACT/UNVERIFIED |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | FULL-GATE-LEGACY-TEST-ROUTE-01 | P0 | U0 | Codex/AIDE | PRESENTATION-CONTRACT-01 complete; canonical structure clean enough | Full-gate tests still expecting retired roots; generated prompt | Audit + targeted test/validator fixes; no retired root expectations | Run/execute generated prompt | WORKSTREAM-07 | FACT |
| TASK-02 | PACK-INTERNAL-LAYOUT-CANON-01 | P1 | U1 | Codex/AIDE | Current pack layout warnings | Audit current pack-internal content layout | Decision and targeted migration/validator update | Generate prompt after or alongside full-gate cleanup | WORKSTREAM-07 | FACT/INFERENCE |
| TASK-03 | RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01 | P1 | U1 | Codex/AIDE | Structure audit warning buckets | Inspect engine/runtime residual paths such as session/serialization/foundation | Classification or targeted moves | Generate maintenance prompt | WORKSTREAM-07 | FACT/INFERENCE |
| TASK-04 | PUBLIC-HEADER-ABI-PROMOTION-01 | P1 | U1 | Codex/AIDE | Public ABI warning debt | Public surface/header promotion warnings | Classify public vs internal/provisional; reduce warnings | Generate prompt | WORKSTREAM-01 | FACT/INFERENCE |
| TASK-05 | STORAGE-PACKAGE-PROVIDER-SPLIT-01 | P1 | U1 | Codex/AIDE | Provider/package structure warnings | Current storage/package provider split uncertainty | Targeted taxonomy/contract clarification | Generate prompt | WORKSTREAM-06 | FACT/INFERENCE |
| TASK-06 | POINTER-WIDTH-SERIALIZATION-AUDIT-01 | P1 | U1 | Codex/AIDE | C17/C++17 + 64-bit policy; serialization law | Code/search audit for pointer-width serialization risks | Audit and repair tasks | Generate prompt | WORKSTREAM-01 | FACT |
| TASK-07 | PROJECTION-CONFORMANCE-01 | P0 | U1 | Codex/AIDE | PRESENTATION-CONTRACT-01 complete | Projection conformance task | Fixtures/tests proving CLI/text/rendered-placeholder/native/headless projections consume same views | Generate next mainline prompt after maintenance set or now if chosen | WORKSTREAM-04 | FACT |
| TASK-08 | ACCESSIBILITY-CONTRACT-01 | P1 | U1 | Codex/AIDE | Presentation contracts | Accessibility labels/focus/keyboard/contrast/reduced-motion law | Contracts/fixtures/validators | Generate after projection conformance | WORKSTREAM-04 | FACT |
| TASK-09 | TEXT-LOCALIZATION-CONTRACT-01 | P1 | U1 | Codex/AIDE | Presentation contracts | Text/message catalog/localization fallback law | Contracts/fixtures/validators | Generate after accessibility contract or parallel | WORKSTREAM-04 | FACT |
| TASK-10 | WORKBENCH-SHELL-READONLY-01 | P1 | U2 | Codex/AIDE | Presentation/projection conformance | Read-only Workbench shell | Command palette/status/validation/evidence/project graph surfaces, no editing | Generate once projection conformance is stable | WORKSTREAM-05 | FACT/INFERENCE |
| TASK-11 | UNIVERSE-EXPLORER-CONTRACT-01 | P1 | U2 | Codex/AIDE | Presentation/projection; read-only shell preferably | Contract for read-only universe inspection/explorer | Observer/ref frames/streaming/materialization/fidelity/provenance contracts | Generate after Workbench/read-only or as contract-only lane | WORKSTREAM-08 | INFERENCE |
| TASK-12 | UNIVERSE-EXPLORER-HEADLESS-01 | P1 | U2 | Codex/AIDE | Universe Explorer contract | Headless/null-render proof | Typed traversal/inspection/materialization/refusal evidence without renderer | Generate after contract | WORKSTREAM-08 | INFERENCE |
| TASK-13 | PROVIDER-MANIFEST-WEDGE-01 | P1 | U2 | Codex/AIDE | AIDE governance/presentation; provider doctrine | Provider descriptor law | Provider schema, examples, status vocab, relation to capability ledger | Generate after presentation/projection or as parallel low-risk lane | WORKSTREAM-06 | INFERENCE |
| TASK-14 | SERVICE-CONTRACT-WEDGE-01 | P1 | U2 | Codex/AIDE | Provider manifest wedge | Service slots for platform/input/render/draw/audio/assets/script | Service contracts and null-provider contract fixtures | Generate after provider manifest | WORKSTREAM-06 | INFERENCE |
| TASK-15 | THIRD-PARTY-FENCE-01 | P1 | U2 | Codex/AIDE | Provider manifest/service contract | Forbidden include and license/third-party validator | Boundary validator and third-party manifest policy | Generate before concrete raylib wedge | WORKSTREAM-06 | INFERENCE |
| TASK-16 | RAYLIB-PROVIDER-WEDGE-01 | P2 | U2 | Codex/AIDE | Manifest/service/fence tasks | Raylib ecosystem seed provider proof | Raylib/rlgl/rlsw/raygui/raudio provider proofs; no leakage | Generate after fences | WORKSTREAM-06 | INFERENCE |
| TASK-17 | PRODUCT-SPINE/STATUS verification before future prompts | P0 | U0 | Future assistant/user | Current chat state may be stale | Live repo status from queue/audits/log | Correct next prompt and prevent stale work | Verify before execution | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Do not turn Workbench into authority. | Architecture | Hard | Direct repeated doctrine | Workbench must use commands/services/documents/patches/evidence. | High | 5 | FACT |
| CONSTRAINT-02 | Broad Workbench UI, provider runtime, package runtime, module loader, renderer/native GUI, gameplay, release publication remain blocked until gates authorize. | Execution | Hard | Repeated queue/foundation summaries in chat | Future prompts must preserve non-goals. | High | 4 | FACT/UNVERIFIED |
| CONSTRAINT-03 | No broad structure cleanup unless validator/audit blocks next slice. | Execution | Hard/soft | Latest plan | Use targeted maintenance lanes. | Medium | 4 | FACT |
| CONSTRAINT-04 | CLI/TUI/rendered/native/headless must be projections of same command/result/view spine. | Architecture | Hard | Repeated accepted doctrine | Presentation work must avoid separate semantics per UI mode. | High | 4 | FACT |
| CONSTRAINT-05 | Third-party types must not leak into engine/game/contracts/content/saves/replays/public SDK. | Architecture | Hard | Provider doctrine | Provider code must translate to Dominium types. | High | 4 | FACT/INFERENCE |
| CONSTRAINT-06 | Full CTest is full-gate/T4 debt, not ordinary prompt gate. | Testing | Soft but important | Repeated latest plans | Dev tasks run targeted validators/fast strict; main/checkpoint more stringent. | Medium | 4 | FACT/UNVERIFIED |
| CONSTRAINT-07 | Stable identity is contractual, not path-based. | Architecture | Hard | Repeated doctrine | Use IDs/manifests/registries, not folder names, as identity. | High | 5 | FACT |
| CONSTRAINT-08 | Apps compose; runtime implements; contracts define law; content supplies authored payloads; tools validate/generate/migrate. | Architecture | Hard | Repeated doctrine | Prevents apps/tools becoming runtime or truth owners. | High | 4 | FACT |
| CONSTRAINT-09 | Development non-blocking; promotion evidence-blocked. | Process | Hard | Repeated AIDE doctrine | Dev may accept classified warnings; main requires checkpoint/evidence. | High | 4 | FACT |
| CONSTRAINT-10 | The preservation report itself is for THIS CHAT ONLY unless labelled PROJECT-CONTEXT. | Reporting | Hard | Uploaded preservation prompt | Do not merge other chat facts unlabelled. | Medium | 5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Direct, source-grounded, audit-ready answers with explicit uncertainty. | Response style | Explicit | Strong | Use FACT/INFERENCE/UNCERTAIN labels and cite uploaded/current files when used. | High | FACT |
| PREF-02 | Generate copyable Codex/AIDE prompts in one fenced block. | Prompt generation | Explicit | Strong | Future prompts should be single-block, status/context/goals/non-goals/validation/final format. | Medium | FACT |
| PREF-03 | Do not re-ask answered questions; proceed with assumptions when safe. | Interaction | Explicit/inferred | Strong | Ask only if materially blocking. | Medium | FACT/INFERENCE |
| PREF-04 | Do not restart settled doctrine. | Continuity | Explicit | Strong | Future chats should verify state but not re-litigate architecture. | High | FACT |
| PREF-05 | Preserve rejected/superseded options. | Memory | Explicit in preservation prompt | Strong | Report rejected UI Editor, native-widget-first editor, monolithic editor, broad cleanup. | Medium | FACT |
| PREF-06 | Prefer professional/OS-like engineering over one-off indie architecture. | Technical philosophy | Explicit | Strong | Design for portability, modularity, compatibility, evidence, replaceability. | High | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | What is the live repo status at the time of continuation? | The chat includes changing queue and commit state. | User reported latest tasks and statuses. | Whether subsequent Codex runs changed queue/audits after this preservation. | Verify `.aide/queue/current.toml`, latest commits, relevant audits. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Should the next executable task be FULL-GATE-LEGACY-TEST-ROUTE-01 or PROJECTION-CONFORMANCE-01? | User said first generate maintenance prompts, then replan. | FULL-GATE prompt was generated immediately before preservation request. | Whether user will run maintenance lane first or mainline projection. | Ask user or check queue after files. | P0 | WORKSTREAM-07 | FACT/UNCERTAIN |
| QUESTION-03 | Is C17/C++17 fully implemented in CMake or partially doctrinal? | Language baseline changed during chat. | Later handoffs state C17/C++17 baseline. | Live CMake/toolchain details. | Verify repo files before spec lock. | P1 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | How aggressively should provider/raylib work start relative to presentation/projection and Workbench read-only shell? | Provider strategy was accepted conceptually but timing deferred. | Recommended after AIDE/presentation/fence/manifest tasks. | Exact queue timing after maintenance tasks. | Replan after projection conformance and maintenance status. | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-05 | What is the final target for Universe Explorer as first product identity? | It is a north-star but not implemented. | Headless/read-only first, visual later, embodiment after. | How soon to schedule after read-only Workbench/presentation. | Formalize UNIVERSE-EXPLORER-CONTRACT-01 when gates allow. | P2 | WORKSTREAM-08 | INFERENCE |

## 23. Artifact Ledger

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

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Old Windows-only UI Editor as final product | Superseded | Too narrow, native-widget-first, not cross-platform/reusable; replaced by Workbench modules. | Final for final product; ideas recycled | Temporary for bootstrap only if ever needed. | WORKSTREAM-05 | FACT |
| REJECTED-02 | Tool Editor as monolithic editor | Superseded | Would become separate architecture; replaced by modular Workbench Platform. | Final as monolithic product | Could reappear as workspace/module concept only. | WORKSTREAM-05 | FACT |
| REJECTED-03 | Workbench as authority/center of architecture | Rejected | Contracts/commands/services/providers/packs/artifacts/proof are center; Workbench is surface. | Final | Reconsider only as UX language, not architecture. | WORKSTREAM-05 | FACT |
| REJECTED-04 | Broad root/directory rewrites after structure became clean enough | Deprioritized | Risk of cleanup spiral; remaining work targeted. | Current plan, not forever | If validators show blockers. | WORKSTREAM-07 | FACT |
| REJECTED-05 | Raylib-shaped architecture or apps/client/rendered/raylib variants | Rejected | Vendor/provider must not define architecture. | Final | Temporary proof folders allowed with retirement notes. | WORKSTREAM-06 | FACT/INFERENCE |
| REJECTED-06 | Pure C99 or pure C++11 as mainline baseline | Rejected/superseded | C17+C++17 with C-compatible ABI deemed better fit. | Tentative until live build verified | If platform/toolchain evidence contradicts. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |

## 25. Risk Register

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

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Live repo task queue and audit status. | Many user-pasted statuses changed over time. | GitHub/repo files: .aide/queue/current.toml, audits, log. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | C17/C++17 baseline in current CMake/toolchain docs. | Earlier chat had C89/C++98; later says C17/C++17. | CMakeLists, toolchain docs, foundation audit. | P1 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Whether FULL-GATE-LEGACY-TEST-ROUTE-01 has been run. | It was generated, but execution unknown. | Repo commit/audit search. | P0 | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Whether AIDE workflow layer prompts have all landed. | Some reportedly passed in pasted summaries; may be stale. | AIDE audits and queue. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Third-party current facts for raylib, SDL, Lua. | External software versions/support/licensing may change. | Official project docs/releases before implementation. | P2 | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | Launcher/UI Editor start | User sought graphical UI editor for mangled/flickering launcher UI. | Initial problem and early requirements. | Historical/superseded but concepts reused. | 4 |
| 02 | Phase A/B UI Editor/Tool Editor prompt plan | Generated multi-prompt implementation plan for UI Editor and Tool Editor. | Provided concrete early approach. | Superseded; artifact context. | 4 |
| 03 | Import/CLI/ops and Minecraft-style tests | UI Editor plan expanded to import existing tools, CLI scripting, and launcher/setup layout tests. | Introduced automation and structural UI testing. | Recycled into Workbench/presentation ideas. | 4 |
| 04 | Abandon old editor as final product | User stated old UI/tool editor should be abandoned/recycled. | Major pivot. | Active doctrine. | 5 |
| 05 | Dominium Workbench Platform | Workbench becomes production/validation/editing/agent environment. | Core architecture. | Active. | 5 |
| 06 | Unified CLI/TUI/rendered/native/headless projections | All UIs become projections of same semantic spine. | Prevents drift. | Presentation contract completed per user report. | 4 |
| 07 | AIDE/Codex workflow | AIDE as governor, Codex as bounded executor; task branches/checkpoints. | Enables parallel dev safely. | Active. | 4 |
| 08 | Provider/raylib strategy | Use raylib/SDL/Lua as fenced providers. | Accelerates visible progress without lock-in. | Planned. | 4 |
| 09 | Structure stabilization and full-gate debt | Stop broad cleanup; run targeted maintenance. | Keeps moving without cleanup spiral. | Current maintenance lane. | 4 |
| 10 | Preservation request | User requested maximum-fidelity preservation package. | This output. | Active. | 5 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Architecture doctrine | Domino/Dominium/Workbench/AIDE roles and stable identity law. | DECISION-01, DECISION-02, DECISION-07 | Requirement | 4 | Core spec chapter. |
| Workbench product strategy | Workbench as modular production environment and progressive self-hosting ladder. | WORKSTREAM-05, DECISION-05 | Requirement/context | 4 | Implementation later. |
| Presentation/UI system | Unified CLI/TUI/rendered/native/headless projection doctrine. | WORKSTREAM-04, DECISION-04 | Requirement | 4 | Needs projection conformance. |
| Provider strategy | Raylib/SDL/Lua fenced provider doctrine. | WORKSTREAM-06, DECISION-11-13 | Requirement/context | 4 | External facts verify before implementation. |
| AIDE process | Development non-blocking, promotion evidence-blocked, WorkUnit/checkpoint model. | WORKSTREAM-02, DECISION-07-09 | Requirement | 4 | Partly implemented per user reports. |
| Maintenance queue | Targeted full-gate/pack/taxonomy/ABI/storage/pointer audits. | TASK-01-06 | Open issue/tasks | 4 | Current next execution. |
| Long-range game doctrine | Deep primitives, materialization, representation ladders, formalization, civilization. | WORKSTREAM-10 | Background/context | 3 | Future domain spec. |

# 29. Context Transfer Packet for a Future Chat

## 29.1 Ultra-Condensed Bootstrap Brief

This chat preserved the transition from a Windows-first UI Editor plan to the larger Dominium Workbench architecture. The user originally wanted an internal graphical UI tool to fix and redesign launcher/setup/game/tool UIs. Early prompts planned a Phase A UI Editor and Phase B Tool Editor with TLV documents, layout engines, CLI scripting, import/export, and action codegen. Later, the user explicitly rejected that as a final product and replaced it with Dominium Workbench: a cross-platform rendered production environment using the same command, UI, renderer, pack, diagnostics, and evidence systems as the client.

The settled doctrine is that Domino is the reusable deterministic substrate; Dominium is one game/product family; Workbench is the production/validation/editing/inspection/packaging/evidence environment; AIDE is the repo/control-plane harness; Codex is a bounded patch executor; contracts are law; tests/replay/evidence are proof. Workbench is not authority. It designs artifacts; runtime executes artifacts; contracts constrain artifacts; content packages artifacts; apps consume artifacts; tests prove artifacts; AIDE governs changes; Codex patches code.

CLI, TUI/text, rendered GUI, OS-native GUI, and headless are projections of the same command/result/refusal/document/view/action model. Presentation work must precede rich Workbench or renderer implementation. The latest reported state says PRESENTATION-CONTRACT-01 completed with warnings; PROJECTION-CONFORMANCE-01 is next mainline, but the user chose to first generate targeted maintenance prompts: FULL-GATE-LEGACY-TEST-ROUTE-01, PACK-INTERNAL-LAYOUT-CANON-01, RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01, PUBLIC-HEADER-ABI-PROMOTION-01, STORAGE-PACKAGE-PROVIDER-SPLIT-01, and POINTER-WIDTH-SERIALIZATION-AUDIT-01. FULL-GATE-LEGACY-TEST-ROUTE-01 was already generated.

Important caveat: all live repo claims must be verified before action. This preservation package records chat state, not a fresh repo audit.

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences labelled as such.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

## 29.3 Operating Rules for Future Assistants

Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not assume access to the old chat. Verify stale facts before relying on them. Do not restart doctrine. Do not re-ask answered questions unless material. Do not treat assistant suggestions as user decisions. Do not repeat rejected UI Editor/Tool Editor final-product paths. Continue with narrow, evidence-backed prompts.

## 29.4 Active Workstreams

Active workstreams are AIDE workflow/process, product spine/presentation, targeted structure/full-gate maintenance, Workbench platform, provider/raylib strategy, and future Universe Explorer planning.

## 29.5 Current Priorities

1. Verify live repo state.
2. Run/review FULL-GATE-LEGACY-TEST-ROUTE-01.
3. Generate remaining targeted maintenance prompts.
4. Continue to PROJECTION-CONFORMANCE-01.
5. Preserve broad blockers.

## 29.6 Current Open Questions

The most important open questions are live repo status, whether generated prompts were executed, how C17/C++17 appears in live build files, and exact timing of provider/raylib work relative to projection and Workbench.

## 29.7 Recommended First Action

If continuing this old chat: ask to generate PACK-INTERNAL-LAYOUT-CANON-01 or ask to review whether FULL-GATE-LEGACY-TEST-ROUTE-01 has been executed.


# 30. Spec Sheet

```yaml
spec_sheet:
  metadata:
    chat_label: Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, and Product-Spine Planning
    date_anchor: 2026-05-27 Australia/Melbourne
    source_scope: This chat only unless labelled PROJECT-CONTEXT
    apparent_coverage: Partial-to-broad visible context, not raw complete transcript export
    confidence_1_to_5: 4
    staleness_risk: High for live repo/external software, medium for doctrine
    safe_for_aggregation: yes_with_caveats
    main_limitations:
    - No guaranteed full raw transcript
    - Live repo status not freshly verified
    - Some early turns summarized/skipped
    - Screenshots not fully analyzed
  summary:
    one_sentence: This chat transformed a UI editor idea into a broad Dominium Workbench/AIDE/provider/presentation architecture
      and task queue.
    short_brief: A long planning chat about replacing old UI tooling with Workbench, unifying presentations, governing Codex/AIDE
      parallel development, fencing third-party providers, and planning targeted maintenance plus projection work.
    main_topics:
    - UI Editor supersession
    - Workbench Platform
    - AIDE workflow
    - Presentation/projection architecture
    - Provider/raylib strategy
    - Structure/full-gate maintenance
    - Universe Explorer north-star
    main_outputs:
    - Multiple Codex prompts
    - Handoff material
    - This preservation package
    highest_priority_carry_forward:
    - Verify live repo state
    - Run/review FULL-GATE-LEGACY-TEST-ROUTE-01
    - Generate remaining maintenance prompts
    - Proceed to PROJECTION-CONFORMANCE-01
  source_rules:
    labels_used:
    - FACT
    - INFERENCE
    - UNCERTAIN / UNVERIFIED
    - PROJECT-CONTEXT
    conflict_rules:
    - Live repo evidence wins over pasted status
    - Direct user decisions outrank assistant suggestions
    - Accepted decisions outrank brainstorms
    staleness_rules:
    - Current repo/software facts require verification before implementation
  user_preferences:
    explicit:
    - Direct, source-grounded, audit-ready answers with explicit uncertainty.
    - Generate copyable Codex/AIDE prompts in one fenced block.
    - Do not re-ask answered questions; proceed with assumptions when safe.
    - Do not restart settled doctrine.
    - Preserve rejected/superseded options.
    - Prefer professional/OS-like engineering over one-off indie architecture.
    inferred:
    - Do not re-ask answered questions; proceed with assumptions when safe.
    uncertain_or_not_established:
    - Exact current repo state
    - Exact final provider implementation timing
  workstreams:
  - id: WORKSTREAM-01
    name: Dominium/Domino architectural identity
    label: FACT/INFERENCE
    objective: Preserve the distinction between Domino as reusable deterministic substrate and Dominium as game/product family.
    current_state: Conceptually settled in this chat; repo-current status requires verification.
    desired_end_state: Contract-governed reusable substrate supporting Dominium and other games/apps.
    status: Active
    priority: P0
    background: See human report sections 1-8
    decisions_made:
    - DECISION-01
    - DECISION-10
    decisions_pending: []
    tasks:
    - TASK-04
    - TASK-06
    constraints:
    - CONSTRAINT-01
    - CONSTRAINT-02
    - CONSTRAINT-03
    - CONSTRAINT-04
    - CONSTRAINT-05
    - CONSTRAINT-06
    - CONSTRAINT-07
    - CONSTRAINT-08
    - CONSTRAINT-09
    - CONSTRAINT-10
    dependencies: []
    timeline: See timeline register
    blockers: []
    risks:
    - RISK-08
    artifacts:
    - ARTIFACT-01
    - ARTIFACT-02
    - ARTIFACT-03
    - ARTIFACT-04
    - ARTIFACT-05
    - ARTIFACT-06
    - ARTIFACT-07
    - ARTIFACT-08
    success_criteria: []
    next_action: See task register
    verification_needed:
    - VERIFY-02
    confidence: '4'
  - id: WORKSTREAM-02
    name: AIDE control-plane workflow
    label: FACT
    objective: Make AIDE the scheduler/ledger/checkpoint/repair system for bounded Codex work.
    current_state: Workflow, WorkUnit, dev/main, checkpoint, and capability reality prompts were generated or discussed.
    desired_end_state: Parallel task execution with evidence-blocked main promotion.
    status: Active
    priority: P0
    background: See human report sections 1-8
    decisions_made:
    - DECISION-07
    - DECISION-08
    - DECISION-09
    - DECISION-16
    decisions_pending: []
    tasks: []
    constraints:
    - CONSTRAINT-01
    - CONSTRAINT-02
    - CONSTRAINT-03
    - CONSTRAINT-04
    - CONSTRAINT-05
    - CONSTRAINT-06
    - CONSTRAINT-07
    - CONSTRAINT-08
    - CONSTRAINT-09
    - CONSTRAINT-10
    dependencies: []
    timeline: See timeline register
    blockers: []
    risks:
    - RISK-05
    - RISK-06
    artifacts:
    - ARTIFACT-01
    - ARTIFACT-02
    - ARTIFACT-03
    - ARTIFACT-04
    - ARTIFACT-05
    - ARTIFACT-06
    - ARTIFACT-07
    - ARTIFACT-08
    success_criteria: []
    next_action: See task register
    verification_needed:
    - VERIFY-04
    confidence: '4'
  - id: WORKSTREAM-03
    name: Product spine and queue sequencing
    label: UNCERTAIN / UNVERIFIED
    objective: Continue narrow product-spine tasks while broad features remain blocked.
    current_state: Package mount, replay proof, barebones shell, product spine review, presentation contract and full-gate
      tasks were discussed; latest execution state is user-reported, not independently verified here.
    desired_end_state: Proven command/result/view/replay/client shell leading to presentation/projection and Workbench read-only
      shell.
    status: Active
    priority: P0
    background: See human report sections 1-8
    decisions_made: []
    decisions_pending: []
    tasks:
    - TASK-17
    constraints:
    - CONSTRAINT-01
    - CONSTRAINT-02
    - CONSTRAINT-03
    - CONSTRAINT-04
    - CONSTRAINT-05
    - CONSTRAINT-06
    - CONSTRAINT-07
    - CONSTRAINT-08
    - CONSTRAINT-09
    - CONSTRAINT-10
    dependencies: []
    timeline: See timeline register
    blockers: []
    risks:
    - RISK-01
    artifacts:
    - ARTIFACT-01
    - ARTIFACT-02
    - ARTIFACT-03
    - ARTIFACT-04
    - ARTIFACT-05
    - ARTIFACT-06
    - ARTIFACT-07
    - ARTIFACT-08
    success_criteria: []
    next_action: See task register
    verification_needed:
    - VERIFY-01
    confidence: '3'
  - id: WORKSTREAM-04
    name: Unified presentation architecture
    label: FACT/UNVERIFIED
    objective: Unify CLI, TUI/text, rendered GUI, native GUI, and headless as projections of commands/results/views.
    current_state: Presentation contract completed per user report; projection conformance remains next.
    desired_end_state: One view/action/projection model shared by products and Workbench.
    status: Active
    priority: P0
    background: See human report sections 1-8
    decisions_made:
    - DECISION-04
    decisions_pending: []
    tasks:
    - TASK-07
    - TASK-08
    - TASK-09
    constraints:
    - CONSTRAINT-01
    - CONSTRAINT-02
    - CONSTRAINT-03
    - CONSTRAINT-04
    - CONSTRAINT-05
    - CONSTRAINT-06
    - CONSTRAINT-07
    - CONSTRAINT-08
    - CONSTRAINT-09
    - CONSTRAINT-10
    dependencies: []
    timeline: See timeline register
    blockers: []
    risks:
    - RISK-02
    artifacts:
    - ARTIFACT-01
    - ARTIFACT-02
    - ARTIFACT-03
    - ARTIFACT-04
    - ARTIFACT-05
    - ARTIFACT-06
    - ARTIFACT-07
    - ARTIFACT-08
    success_criteria: []
    next_action: See task register
    verification_needed: []
    confidence: '4'
  - id: WORKSTREAM-05
    name: Workbench production environment
    label: FACT/INFERENCE
    objective: Make Workbench the visual/agentic production environment, not the authority.
    current_state: Strong conceptual plan; implementation deferred until contracts/projections/read-only shell.
    desired_end_state: Progressive self-hosting Workbench that edits artifacts through document patches and evidence.
    status: Planned
    priority: P1
    background: See human report sections 1-8
    decisions_made:
    - DECISION-02
    - DECISION-03
    - DECISION-05
    - DECISION-15
    decisions_pending: []
    tasks:
    - TASK-10
    constraints:
    - CONSTRAINT-01
    - CONSTRAINT-02
    - CONSTRAINT-03
    - CONSTRAINT-04
    - CONSTRAINT-05
    - CONSTRAINT-06
    - CONSTRAINT-07
    - CONSTRAINT-08
    - CONSTRAINT-09
    - CONSTRAINT-10
    dependencies: []
    timeline: See timeline register
    blockers: []
    risks: []
    artifacts:
    - ARTIFACT-01
    - ARTIFACT-02
    - ARTIFACT-03
    - ARTIFACT-04
    - ARTIFACT-05
    - ARTIFACT-06
    - ARTIFACT-07
    - ARTIFACT-08
    success_criteria: []
    next_action: See task register
    verification_needed: []
    confidence: '4'
  - id: WORKSTREAM-06
    name: Renderer/provider strategy
    label: FACT/INFERENCE
    objective: Use raylib/SDL/Lua as fenced providers under Dominium service contracts.
    current_state: Detailed provider doctrine decided conceptually; implementation not yet started.
    desired_end_state: Service-first provider system with manifests, profiles, conformance tests, and third-party fences.
    status: Planned
    priority: P1
    background: See human report sections 1-8
    decisions_made:
    - DECISION-11
    - DECISION-12
    - DECISION-13
    decisions_pending: []
    tasks:
    - TASK-05
    - TASK-13
    - TASK-14
    - TASK-15
    - TASK-16
    constraints:
    - CONSTRAINT-01
    - CONSTRAINT-02
    - CONSTRAINT-03
    - CONSTRAINT-04
    - CONSTRAINT-05
    - CONSTRAINT-06
    - CONSTRAINT-07
    - CONSTRAINT-08
    - CONSTRAINT-09
    - CONSTRAINT-10
    dependencies: []
    timeline: See timeline register
    blockers: []
    risks:
    - RISK-03
    artifacts:
    - ARTIFACT-01
    - ARTIFACT-02
    - ARTIFACT-03
    - ARTIFACT-04
    - ARTIFACT-05
    - ARTIFACT-06
    - ARTIFACT-07
    - ARTIFACT-08
    success_criteria: []
    next_action: See task register
    verification_needed:
    - VERIFY-05
    confidence: '4'
  - id: WORKSTREAM-07
    name: Structure stabilization and full-gate cleanup
    label: FACT
    objective: Stop broad structure cleanup; run targeted maintenance such as full-gate legacy test routing.
    current_state: User requested FULL-GATE-LEGACY-TEST-ROUTE-01 next; prompt generated.
    desired_end_state: Canonical active structure with full-gate tests no longer expecting retired roots.
    status: Active
    priority: P0
    background: See human report sections 1-8
    decisions_made:
    - DECISION-06
    decisions_pending: []
    tasks:
    - TASK-01
    - TASK-02
    - TASK-03
    constraints:
    - CONSTRAINT-01
    - CONSTRAINT-02
    - CONSTRAINT-03
    - CONSTRAINT-04
    - CONSTRAINT-05
    - CONSTRAINT-06
    - CONSTRAINT-07
    - CONSTRAINT-08
    - CONSTRAINT-09
    - CONSTRAINT-10
    dependencies: []
    timeline: See timeline register
    blockers: []
    risks:
    - RISK-04
    artifacts:
    - ARTIFACT-01
    - ARTIFACT-02
    - ARTIFACT-03
    - ARTIFACT-04
    - ARTIFACT-05
    - ARTIFACT-06
    - ARTIFACT-07
    - ARTIFACT-08
    success_criteria: []
    next_action: See task register
    verification_needed:
    - VERIFY-03
    confidence: '4'
  - id: WORKSTREAM-08
    name: Universe Explorer north-star
    label: INFERENCE
    objective: Build read-only Universe Explorer as first meaningful inspection product slice after presentation/projection.
    current_state: Discussed as future path, not yet implementation.
    desired_end_state: Headless and then visual no-modal-loading universe inspection proving reference frames, streaming,
      materialization, and projection.
    status: Planned
    priority: P2
    background: See human report sections 1-8
    decisions_made:
    - DECISION-14
    decisions_pending: []
    tasks:
    - TASK-11
    - TASK-12
    constraints:
    - CONSTRAINT-01
    - CONSTRAINT-02
    - CONSTRAINT-03
    - CONSTRAINT-04
    - CONSTRAINT-05
    - CONSTRAINT-06
    - CONSTRAINT-07
    - CONSTRAINT-08
    - CONSTRAINT-09
    - CONSTRAINT-10
    dependencies: []
    timeline: See timeline register
    blockers: []
    risks:
    - RISK-07
    artifacts:
    - ARTIFACT-01
    - ARTIFACT-02
    - ARTIFACT-03
    - ARTIFACT-04
    - ARTIFACT-05
    - ARTIFACT-06
    - ARTIFACT-07
    - ARTIFACT-08
    success_criteria: []
    next_action: See task register
    verification_needed: []
    confidence: '3'
  - id: WORKSTREAM-09
    name: Modular theme/UI/TUI/rendered system
    label: FACT/INFERENCE
    objective: Support modular layouts, controls, widgets, themes, OEM+ mimic styles, TUI profiles, and code-only primitive
      themes.
    current_state: Discussed with screenshots and mockups; mostly conceptual.
    desired_end_state: Theme/control/layout/view system packable and testable across CLI/TUI/rendered/native.
    status: Planned
    priority: P1
    background: See human report sections 1-8
    decisions_made: []
    decisions_pending: []
    tasks: []
    constraints:
    - CONSTRAINT-01
    - CONSTRAINT-02
    - CONSTRAINT-03
    - CONSTRAINT-04
    - CONSTRAINT-05
    - CONSTRAINT-06
    - CONSTRAINT-07
    - CONSTRAINT-08
    - CONSTRAINT-09
    - CONSTRAINT-10
    dependencies: []
    timeline: See timeline register
    blockers: []
    risks: []
    artifacts:
    - ARTIFACT-01
    - ARTIFACT-02
    - ARTIFACT-03
    - ARTIFACT-04
    - ARTIFACT-05
    - ARTIFACT-06
    - ARTIFACT-07
    - ARTIFACT-08
    success_criteria: []
    next_action: See task register
    verification_needed: []
    confidence: '4'
  - id: WORKSTREAM-10
    name: Long-range simulation/game doctrine
    label: INFERENCE
    objective: Preserve deep primitives, materialization, representation ladders, formalization, civilization, and failure
      ontology as future domain doctrine.
    current_state: Discussed repeatedly but deferred.
    desired_end_state: Domain constitutions and slices after product spine and Workbench foundations.
    status: Future
    priority: P3
    background: See human report sections 1-8
    decisions_made: []
    decisions_pending: []
    tasks: []
    constraints:
    - CONSTRAINT-01
    - CONSTRAINT-02
    - CONSTRAINT-03
    - CONSTRAINT-04
    - CONSTRAINT-05
    - CONSTRAINT-06
    - CONSTRAINT-07
    - CONSTRAINT-08
    - CONSTRAINT-09
    - CONSTRAINT-10
    dependencies: []
    timeline: See timeline register
    blockers: []
    risks: []
    artifacts:
    - ARTIFACT-01
    - ARTIFACT-02
    - ARTIFACT-03
    - ARTIFACT-04
    - ARTIFACT-05
    - ARTIFACT-06
    - ARTIFACT-07
    - ARTIFACT-08
    success_criteria: []
    next_action: See task register
    verification_needed: []
    confidence: '3'
  decisions:
  - id: DECISION-01
    decision: Domino is the reusable deterministic substrate; Dominium is one product/game family on it.
    status: Accepted/active
    label: FACT
    evidence_or_basis: Repeated user acceptance and later handoffs.
    rationale: Allows reuse for other games and prevents Dominium-specific systems from contaminating the engine substrate.
    implications: Affects roots, APIs, provider boundaries, Workbench, packs, and future game projects.
    related_workstreams:
    - WORKSTREAM-01
    uncertainty: FACT
  - id: DECISION-02
    decision: Workbench is not authority; it is a production environment over contracts, commands, services, documents, patches,
      evidence, modules, packs, and providers.
    status: Accepted/active
    label: FACT
    evidence_or_basis: User accepted replacement of old UI/Tool Editor with Workbench platform.
    rationale: Prevents a second GUI framework and keeps CLI/TUI/GUI/headless parity.
    implications: Workbench must call command/service/document/patch flows, not mutate truth privately.
    related_workstreams:
    - WORKSTREAM-05
    uncertainty: FACT
  - id: DECISION-03
    decision: Abandon old UI Editor / Tool Editor as final products; recycle their ideas into Workbench modules.
    status: Accepted/active
    label: FACT
    evidence_or_basis: User explicitly said old UI editor/tool editor were good general ideas but bad final products, to abandon
      and recycle them.
    rationale: Avoids Windows-first one-off tooling and moves to cross-platform rendered tools.
    implications: Old concepts become Interface Studio, UI/HUD Sandbox, Theme Lab, Module/Pack Foundry, App Composer.
    related_workstreams:
    - WORKSTREAM-05
    uncertainty: FACT
  - id: DECISION-04
    decision: CLI, TUI/text, rendered GUI, OS-native GUI, and headless are projections of the same semantic command/result/view
      system.
    status: Accepted/active
    label: FACT
    evidence_or_basis: Repeatedly discussed and accepted.
    rationale: Prevents separate implementations and enables reuse across client, server, setup, launcher, and Workbench.
    implications: Requires presentation contracts and projection conformance before rich UI.
    related_workstreams:
    - WORKSTREAM-04
    uncertainty: FACT
  - id: DECISION-05
    decision: 'Use progressive self-hosting: seed substrate first, then Workbench edits safe artifacts, then its own presentation,
      then products.'
    status: Accepted/active
    label: FACT
    evidence_or_basis: User accepted progressive self-hosting model.
    rationale: Avoids circular dependency and unsafe self-modifying Workbench.
    implications: Defines Workbench maturity ladder S0-S6.
    related_workstreams:
    - WORKSTREAM-05
    uncertainty: FACT
  - id: DECISION-06
    decision: Stop broad structure cleanup once canonical active structure is clean enough; use targeted maintenance lanes.
    status: Accepted/latest plan
    label: FACT
    evidence_or_basis: User shifted to full-gate legacy test routing and targeted cleanup.
    rationale: Avoids cleanup spiral.
    implications: Maintenance tasks include full-gate legacy test route, pack layout canon, residual taxonomy, public ABI
      promotion.
    related_workstreams:
    - WORKSTREAM-07
    uncertainty: FACT
  - id: DECISION-07
    decision: Use AIDE as governor/ledger/checkpoint/repair system and Codex as bounded patch executor.
    status: Accepted/active
    label: FACT
    evidence_or_basis: Explicit in multiple handoff plans.
    rationale: Supports parallel development without corrupting main.
    implications: Requires workflow law, WorkUnit schema, dev/main policy, checkpoint loop, capability reality ledger.
    related_workstreams:
    - WORKSTREAM-02
    uncertainty: FACT
  - id: DECISION-08
    decision: Development is non-blocking; promotion is evidence-blocked.
    status: Accepted/active
    label: FACT
    evidence_or_basis: Repeated as doctrine in user and assistant handoffs.
    rationale: Allows progress on dev while protecting main.
    implications: Shapes branch model and testing policy.
    related_workstreams:
    - WORKSTREAM-02
    uncertainty: FACT
  - id: DECISION-09
    decision: Use task branches/worktrees; do not let multiple agents mutate shared dev directly.
    status: Accepted/active
    label: FACT
    evidence_or_basis: Discussed as required before larger parallelism.
    rationale: Prevents conflicts and stale AIDE state.
    implications: Requires branch role policy and checkpoint loop.
    related_workstreams:
    - WORKSTREAM-02
    uncertainty: FACT
  - id: DECISION-10
    decision: Current mainline language doctrine moved from C89/C++98 ideas to C17 + C++17 with C-compatible ABI boundaries.
    status: Accepted but verify live repo
    label: UNCERTAIN / UNVERIFIED
    evidence_or_basis: User pasted synthesis stating this; earlier chat had C89/C++98 assumptions.
    rationale: Improves maintainability while preserving ABI portability.
    implications: Needs live verification in CMake/build policy before final spec merge.
    related_workstreams:
    - WORKSTREAM-01
    uncertainty: UNCERTAIN / UNVERIFIED
  - id: DECISION-11
    decision: Use raylib/rlgl/rlsw/raygui/raudio/SDL2/Lua aggressively only as replaceable providers behind Dominium service
      contracts.
    status: Accepted/conceptual
    label: FACT/INFERENCE
    evidence_or_basis: User asked what I thought; assistant agreed and refined.
    rationale: Gives fast visible progress without architectural lock-in.
    implications: Provider work should follow AIDE/presentation and manifest/fence/service contract wedges.
    related_workstreams:
    - WORKSTREAM-06
    uncertainty: FACT/INFERENCE
  - id: DECISION-12
    decision: Do not make raylib, SDL2, Lua, or app variants define the architecture.
    status: Accepted/conceptual
    label: FACT/INFERENCE
    evidence_or_basis: Explicitly discussed as service-first/provider-backed doctrine.
    rationale: Prevents vendor-shaped directory and API lock-in.
    implications: Requires forbidden include validator and provider manifests.
    related_workstreams:
    - WORKSTREAM-06
    uncertainty: FACT/INFERENCE
  - id: DECISION-13
    decision: Raylib rlsw is a raylib software-provider, not the canonical Dominium software renderer.
    status: Accepted/conceptual
    label: FACT/INFERENCE
    evidence_or_basis: Discussed and accepted in provider doctrine.
    rationale: Preserves first-party reference renderer slot.
    implications: 'Directory split: runtime/render/providers/software vs runtime/render/providers/rlsw.'
    related_workstreams:
    - WORKSTREAM-06
    uncertainty: FACT/INFERENCE
  - id: DECISION-14
    decision: Universe Explorer is a north-star read-only inspection product, not gameplay.
    status: Tentative/accepted as plan
    label: INFERENCE
    evidence_or_basis: Discussed after structure cleanup as first meaningful product identity.
    rationale: Proves no-modal-loading, reference frames, streaming, materialization, projection before embodiment.
    implications: Implementation should start with contracts/headless proof, not renderer/gameplay.
    related_workstreams:
    - WORKSTREAM-08
    uncertainty: INFERENCE
  - id: DECISION-15
    decision: Workbench should begin read-only before editing artifacts.
    status: Accepted/active
    label: FACT/INFERENCE
    evidence_or_basis: Repeated in self-hosting safety stages.
    rationale: Reduces risk and proves projection/evidence first.
    implications: First Workbench shell should inspect commands, diagnostics, artifacts, graphs, packs, status.
    related_workstreams:
    - WORKSTREAM-05
    uncertainty: FACT/INFERENCE
  - id: DECISION-16
    decision: Full CTest remains full-gate/T4 debt, not every-prompt gate.
    status: Accepted/latest plan
    label: FACT/UNVERIFIED
    evidence_or_basis: Repeated; user wants speed on dev with full suite at main/checkpoints.
    rationale: Supports parallel productivity.
    implications: Requires targeted validators, fast strict, and checkpoint policy.
    related_workstreams:
    - WORKSTREAM-02
    uncertainty: FACT/UNVERIFIED
  tasks:
  - id: TASK-01
    task: FULL-GATE-LEGACY-TEST-ROUTE-01
    priority: P0
    urgency: U0
    owner: Codex/AIDE
    dependencies:
    - PRESENTATION-CONTRACT-01 complete; canonical structure clean enough
    inputs_needed:
    - Full-gate tests still expecting retired roots; generated prompt
    expected_output: Audit + targeted test/validator fixes; no retired root expectations
    next_step: Run/execute generated prompt
    related_workstreams:
    - WORKSTREAM-07
    label: FACT
    confidence: 4
  - id: TASK-02
    task: PACK-INTERNAL-LAYOUT-CANON-01
    priority: P1
    urgency: U1
    owner: Codex/AIDE
    dependencies:
    - Current pack layout warnings
    inputs_needed:
    - Audit current pack-internal content layout
    expected_output: Decision and targeted migration/validator update
    next_step: Generate prompt after or alongside full-gate cleanup
    related_workstreams:
    - WORKSTREAM-07
    label: FACT/INFERENCE
    confidence: 4
  - id: TASK-03
    task: RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01
    priority: P1
    urgency: U1
    owner: Codex/AIDE
    dependencies:
    - Structure audit warning buckets
    inputs_needed:
    - Inspect engine/runtime residual paths such as session/serialization/foundation
    expected_output: Classification or targeted moves
    next_step: Generate maintenance prompt
    related_workstreams:
    - WORKSTREAM-07
    label: FACT/INFERENCE
    confidence: 4
  - id: TASK-04
    task: PUBLIC-HEADER-ABI-PROMOTION-01
    priority: P1
    urgency: U1
    owner: Codex/AIDE
    dependencies:
    - Public ABI warning debt
    inputs_needed:
    - Public surface/header promotion warnings
    expected_output: Classify public vs internal/provisional; reduce warnings
    next_step: Generate prompt
    related_workstreams:
    - WORKSTREAM-01
    label: FACT/INFERENCE
    confidence: 4
  - id: TASK-05
    task: STORAGE-PACKAGE-PROVIDER-SPLIT-01
    priority: P1
    urgency: U1
    owner: Codex/AIDE
    dependencies:
    - Provider/package structure warnings
    inputs_needed:
    - Current storage/package provider split uncertainty
    expected_output: Targeted taxonomy/contract clarification
    next_step: Generate prompt
    related_workstreams:
    - WORKSTREAM-06
    label: FACT/INFERENCE
    confidence: 4
  - id: TASK-06
    task: POINTER-WIDTH-SERIALIZATION-AUDIT-01
    priority: P1
    urgency: U1
    owner: Codex/AIDE
    dependencies:
    - C17/C++17 + 64-bit policy; serialization law
    inputs_needed:
    - Code/search audit for pointer-width serialization risks
    expected_output: Audit and repair tasks
    next_step: Generate prompt
    related_workstreams:
    - WORKSTREAM-01
    label: FACT
    confidence: 4
  - id: TASK-07
    task: PROJECTION-CONFORMANCE-01
    priority: P0
    urgency: U1
    owner: Codex/AIDE
    dependencies:
    - PRESENTATION-CONTRACT-01 complete
    inputs_needed:
    - Projection conformance task
    expected_output: Fixtures/tests proving CLI/text/rendered-placeholder/native/headless projections consume same views
    next_step: Generate next mainline prompt after maintenance set or now if chosen
    related_workstreams:
    - WORKSTREAM-04
    label: FACT
    confidence: 4
  - id: TASK-08
    task: ACCESSIBILITY-CONTRACT-01
    priority: P1
    urgency: U1
    owner: Codex/AIDE
    dependencies:
    - Presentation contracts
    inputs_needed:
    - Accessibility labels/focus/keyboard/contrast/reduced-motion law
    expected_output: Contracts/fixtures/validators
    next_step: Generate after projection conformance
    related_workstreams:
    - WORKSTREAM-04
    label: FACT
    confidence: 4
  - id: TASK-09
    task: TEXT-LOCALIZATION-CONTRACT-01
    priority: P1
    urgency: U1
    owner: Codex/AIDE
    dependencies:
    - Presentation contracts
    inputs_needed:
    - Text/message catalog/localization fallback law
    expected_output: Contracts/fixtures/validators
    next_step: Generate after accessibility contract or parallel
    related_workstreams:
    - WORKSTREAM-04
    label: FACT
    confidence: 4
  - id: TASK-10
    task: WORKBENCH-SHELL-READONLY-01
    priority: P1
    urgency: U2
    owner: Codex/AIDE
    dependencies:
    - Presentation/projection conformance
    inputs_needed:
    - Read-only Workbench shell
    expected_output: Command palette/status/validation/evidence/project graph surfaces, no editing
    next_step: Generate once projection conformance is stable
    related_workstreams:
    - WORKSTREAM-05
    label: FACT/INFERENCE
    confidence: 4
  - id: TASK-11
    task: UNIVERSE-EXPLORER-CONTRACT-01
    priority: P1
    urgency: U2
    owner: Codex/AIDE
    dependencies:
    - Presentation/projection; read-only shell preferably
    inputs_needed:
    - Contract for read-only universe inspection/explorer
    expected_output: Observer/ref frames/streaming/materialization/fidelity/provenance contracts
    next_step: Generate after Workbench/read-only or as contract-only lane
    related_workstreams:
    - WORKSTREAM-08
    label: INFERENCE
    confidence: 4
  - id: TASK-12
    task: UNIVERSE-EXPLORER-HEADLESS-01
    priority: P1
    urgency: U2
    owner: Codex/AIDE
    dependencies:
    - Universe Explorer contract
    inputs_needed:
    - Headless/null-render proof
    expected_output: Typed traversal/inspection/materialization/refusal evidence without renderer
    next_step: Generate after contract
    related_workstreams:
    - WORKSTREAM-08
    label: INFERENCE
    confidence: 4
  - id: TASK-13
    task: PROVIDER-MANIFEST-WEDGE-01
    priority: P1
    urgency: U2
    owner: Codex/AIDE
    dependencies:
    - AIDE governance/presentation; provider doctrine
    inputs_needed:
    - Provider descriptor law
    expected_output: Provider schema, examples, status vocab, relation to capability ledger
    next_step: Generate after presentation/projection or as parallel low-risk lane
    related_workstreams:
    - WORKSTREAM-06
    label: INFERENCE
    confidence: 4
  - id: TASK-14
    task: SERVICE-CONTRACT-WEDGE-01
    priority: P1
    urgency: U2
    owner: Codex/AIDE
    dependencies:
    - Provider manifest wedge
    inputs_needed:
    - Service slots for platform/input/render/draw/audio/assets/script
    expected_output: Service contracts and null-provider contract fixtures
    next_step: Generate after provider manifest
    related_workstreams:
    - WORKSTREAM-06
    label: INFERENCE
    confidence: 4
  - id: TASK-15
    task: THIRD-PARTY-FENCE-01
    priority: P1
    urgency: U2
    owner: Codex/AIDE
    dependencies:
    - Provider manifest/service contract
    inputs_needed:
    - Forbidden include and license/third-party validator
    expected_output: Boundary validator and third-party manifest policy
    next_step: Generate before concrete raylib wedge
    related_workstreams:
    - WORKSTREAM-06
    label: INFERENCE
    confidence: 4
  - id: TASK-16
    task: RAYLIB-PROVIDER-WEDGE-01
    priority: P2
    urgency: U2
    owner: Codex/AIDE
    dependencies:
    - Manifest/service/fence tasks
    inputs_needed:
    - Raylib ecosystem seed provider proof
    expected_output: Raylib/rlgl/rlsw/raygui/raudio provider proofs; no leakage
    next_step: Generate after fences
    related_workstreams:
    - WORKSTREAM-06
    label: INFERENCE
    confidence: 4
  - id: TASK-17
    task: PRODUCT-SPINE/STATUS verification before future prompts
    priority: P0
    urgency: U0
    owner: Future assistant/user
    dependencies:
    - Current chat state may be stale
    inputs_needed:
    - Live repo status from queue/audits/log
    expected_output: Correct next prompt and prevent stale work
    next_step: Verify before execution
    related_workstreams:
    - WORKSTREAM-03
    label: UNCERTAIN / UNVERIFIED
    confidence: 4
  constraints:
  - id: CONSTRAINT-01
    constraint: Do not turn Workbench into authority.
    type: Architecture
    hard_or_soft: Hard
    source_or_basis: Direct repeated doctrine
    implication: Workbench must use commands/services/documents/patches/evidence.
    violation_risk: High
    label: FACT
    confidence: '5'
  - id: CONSTRAINT-02
    constraint: Broad Workbench UI, provider runtime, package runtime, module loader, renderer/native GUI, gameplay, release
      publication remain blocked until gates authorize.
    type: Execution
    hard_or_soft: Hard
    source_or_basis: Repeated queue/foundation summaries in chat
    implication: Future prompts must preserve non-goals.
    violation_risk: High
    label: FACT/UNVERIFIED
    confidence: '4'
  - id: CONSTRAINT-03
    constraint: No broad structure cleanup unless validator/audit blocks next slice.
    type: Execution
    hard_or_soft: Hard/soft
    source_or_basis: Latest plan
    implication: Use targeted maintenance lanes.
    violation_risk: Medium
    label: FACT
    confidence: '4'
  - id: CONSTRAINT-04
    constraint: CLI/TUI/rendered/native/headless must be projections of same command/result/view spine.
    type: Architecture
    hard_or_soft: Hard
    source_or_basis: Repeated accepted doctrine
    implication: Presentation work must avoid separate semantics per UI mode.
    violation_risk: High
    label: FACT
    confidence: '4'
  - id: CONSTRAINT-05
    constraint: Third-party types must not leak into engine/game/contracts/content/saves/replays/public SDK.
    type: Architecture
    hard_or_soft: Hard
    source_or_basis: Provider doctrine
    implication: Provider code must translate to Dominium types.
    violation_risk: High
    label: FACT/INFERENCE
    confidence: '4'
  - id: CONSTRAINT-06
    constraint: Full CTest is full-gate/T4 debt, not ordinary prompt gate.
    type: Testing
    hard_or_soft: Soft but important
    source_or_basis: Repeated latest plans
    implication: Dev tasks run targeted validators/fast strict; main/checkpoint more stringent.
    violation_risk: Medium
    label: FACT/UNVERIFIED
    confidence: '4'
  - id: CONSTRAINT-07
    constraint: Stable identity is contractual, not path-based.
    type: Architecture
    hard_or_soft: Hard
    source_or_basis: Repeated doctrine
    implication: Use IDs/manifests/registries, not folder names, as identity.
    violation_risk: High
    label: FACT
    confidence: '5'
  - id: CONSTRAINT-08
    constraint: Apps compose; runtime implements; contracts define law; content supplies authored payloads; tools validate/generate/migrate.
    type: Architecture
    hard_or_soft: Hard
    source_or_basis: Repeated doctrine
    implication: Prevents apps/tools becoming runtime or truth owners.
    violation_risk: High
    label: FACT
    confidence: '4'
  - id: CONSTRAINT-09
    constraint: Development non-blocking; promotion evidence-blocked.
    type: Process
    hard_or_soft: Hard
    source_or_basis: Repeated AIDE doctrine
    implication: Dev may accept classified warnings; main requires checkpoint/evidence.
    violation_risk: High
    label: FACT
    confidence: '4'
  - id: CONSTRAINT-10
    constraint: The preservation report itself is for THIS CHAT ONLY unless labelled PROJECT-CONTEXT.
    type: Reporting
    hard_or_soft: Hard
    source_or_basis: Uploaded preservation prompt
    implication: Do not merge other chat facts unlabelled.
    violation_risk: Medium
    label: FACT
    confidence: '5'
  open_questions:
  - id: QUESTION-01
    question: What is the live repo status at the time of continuation?
    why_it_matters: The chat includes changing queue and commit state.
    known: User reported latest tasks and statuses.
    unknown: Whether subsequent Codex runs changed queue/audits after this preservation.
    resolution_path: Verify `.aide/queue/current.toml`, latest commits, relevant audits.
    priority: P0
    related_workstreams:
    - WORKSTREAM-03
    label: UNCERTAIN / UNVERIFIED
  - id: QUESTION-02
    question: Should the next executable task be FULL-GATE-LEGACY-TEST-ROUTE-01 or PROJECTION-CONFORMANCE-01?
    why_it_matters: User said first generate maintenance prompts, then replan.
    known: FULL-GATE prompt was generated immediately before preservation request.
    unknown: Whether user will run maintenance lane first or mainline projection.
    resolution_path: Ask user or check queue after files.
    priority: P0
    related_workstreams:
    - WORKSTREAM-07
    label: FACT/UNCERTAIN
  - id: QUESTION-03
    question: Is C17/C++17 fully implemented in CMake or partially doctrinal?
    why_it_matters: Language baseline changed during chat.
    known: Later handoffs state C17/C++17 baseline.
    unknown: Live CMake/toolchain details.
    resolution_path: Verify repo files before spec lock.
    priority: P1
    related_workstreams:
    - WORKSTREAM-01
    label: UNCERTAIN / UNVERIFIED
  - id: QUESTION-04
    question: How aggressively should provider/raylib work start relative to presentation/projection and Workbench read-only
      shell?
    why_it_matters: Provider strategy was accepted conceptually but timing deferred.
    known: Recommended after AIDE/presentation/fence/manifest tasks.
    unknown: Exact queue timing after maintenance tasks.
    resolution_path: Replan after projection conformance and maintenance status.
    priority: P1
    related_workstreams:
    - WORKSTREAM-06
    label: INFERENCE
  - id: QUESTION-05
    question: What is the final target for Universe Explorer as first product identity?
    why_it_matters: It is a north-star but not implemented.
    known: Headless/read-only first, visual later, embodiment after.
    unknown: How soon to schedule after read-only Workbench/presentation.
    resolution_path: Formalize UNIVERSE-EXPLORER-CONTRACT-01 when gates allow.
    priority: P2
    related_workstreams:
    - WORKSTREAM-08
    label: INFERENCE
  rejected_or_superseded_options:
  - id: REJECTED-01
    option: Old Windows-only UI Editor as final product
    status: Superseded
    reason: Too narrow, native-widget-first, not cross-platform/reusable; replaced by Workbench modules.
    final_or_tentative: Final for final product; ideas recycled
    reconsider_conditions: Temporary for bootstrap only if ever needed.
    related_workstreams:
    - WORKSTREAM-05
    label: FACT
  - id: REJECTED-02
    option: Tool Editor as monolithic editor
    status: Superseded
    reason: Would become separate architecture; replaced by modular Workbench Platform.
    final_or_tentative: Final as monolithic product
    reconsider_conditions: Could reappear as workspace/module concept only.
    related_workstreams:
    - WORKSTREAM-05
    label: FACT
  - id: REJECTED-03
    option: Workbench as authority/center of architecture
    status: Rejected
    reason: Contracts/commands/services/providers/packs/artifacts/proof are center; Workbench is surface.
    final_or_tentative: Final
    reconsider_conditions: Reconsider only as UX language, not architecture.
    related_workstreams:
    - WORKSTREAM-05
    label: FACT
  - id: REJECTED-04
    option: Broad root/directory rewrites after structure became clean enough
    status: Deprioritized
    reason: Risk of cleanup spiral; remaining work targeted.
    final_or_tentative: Current plan, not forever
    reconsider_conditions: If validators show blockers.
    related_workstreams:
    - WORKSTREAM-07
    label: FACT
  - id: REJECTED-05
    option: Raylib-shaped architecture or apps/client/rendered/raylib variants
    status: Rejected
    reason: Vendor/provider must not define architecture.
    final_or_tentative: Final
    reconsider_conditions: Temporary proof folders allowed with retirement notes.
    related_workstreams:
    - WORKSTREAM-06
    label: FACT/INFERENCE
  - id: REJECTED-06
    option: Pure C99 or pure C++11 as mainline baseline
    status: Rejected/superseded
    reason: C17+C++17 with C-compatible ABI deemed better fit.
    final_or_tentative: Tentative until live build verified
    reconsider_conditions: If platform/toolchain evidence contradicts.
    related_workstreams:
    - WORKSTREAM-01
    label: UNCERTAIN / UNVERIFIED
  artifacts:
  - id: ARTIFACT-01
    name_or_description: Prompt UU1–UU6 plan for UI Editor import/CLI/ops/Minecraft launcher/setup tests
    type: Prompt plan
    purpose: Earlier plan for old UI Editor toolchain.
    status: Superseded/recycled
    origin: This chat
    carry_forward: Yes, as rejected/superseded context
    notes: Ideas became Workbench modules and CLI/presentation concepts.
    label: FACT
  - id: ARTIFACT-02
    name_or_description: Final UI Editor implementation prompt with import/CLI/Minecraft tests
    type: Codex prompt
    purpose: Implementation prompt for old Phase A UI Editor.
    status: Superseded
    origin: This chat
    carry_forward: Yes, as historical artifact
    notes: Shows why old approach was abandoned.
    label: FACT
  - id: ARTIFACT-03
    name_or_description: Screenshots/mockups of Workbench themes/modules
    type: Images
    purpose: Visual references for OEM+ themes, modules, TUI, Workbench surfaces.
    status: Reference only
    origin: Uploaded in chat
    carry_forward: 'Yes'
    notes: Used to derive modular theme/workspace concepts, not exact design requirements.
    label: FACT
  - id: ARTIFACT-04
    name_or_description: AIDE/Workbench/product-spine handoff prompt
    type: Handoff text
    purpose: Long carry-forward prompt summarizing repo state and next tasks.
    status: Important
    origin: This chat
    carry_forward: 'Yes'
    notes: Should inform future chat bootstrap; live repo must still be verified.
    label: FACT
  - id: ARTIFACT-05
    name_or_description: 'Codex prompts: STATUS-RECONCILE-02, AIDE-WORKFLOW-LAW-01, AIDE-WORKUNIT-SCHEMA-01, AIDE-DEV-MAIN-POLICY-01,
      AIDE-CHECKPOINT-LOOP-01, AIDE-CAPABILITY-REALITY-LEDGER-01'
    type: Codex prompts
    purpose: Detailed prompts for AIDE workflow layer.
    status: Generated
    origin: This chat
    carry_forward: 'Yes'
    notes: Some reportedly executed later; verify live repo.
    label: FACT
  - id: ARTIFACT-06
    name_or_description: 'Codex prompt: FULL-GATE-LEGACY-TEST-ROUTE-01'
    type: Codex prompt
    purpose: Targeted full-gate stale-root cleanup prompt.
    status: Generated immediately before preservation request
    origin: This chat
    carry_forward: 'Yes'
    notes: Potential next execution depending on user plan.
    label: FACT
  - id: ARTIFACT-07
    name_or_description: User-uploaded Pasted text.txt preservation instruction
    type: Uploaded file
    purpose: Maximum-fidelity preservation package instructions.
    status: Active input
    origin: Uploaded file
    carry_forward: 'Yes'
    notes: Primary instruction for this response.
    label: FACT
  - id: ARTIFACT-08
    name_or_description: This preservation package files and zip
    type: Generated export
    purpose: Downloadable report/register/spec/handoff files created by this response.
    status: Created now
    origin: This response
    carry_forward: 'Yes'
    notes: Use for aggregation and future chat transfer.
    label: FACT
  risks:
  - id: RISK-01
    risk: Future assistant treats stale repo status as current.
    consequence: Wrong prompts, duplicate tasks, stale queues.
    likelihood: Medium
    severity: High
    mitigation: Always verify live repo before current-status decisions.
    related_workstreams:
    - WORKSTREAM-03
    label: UNCERTAIN / UNVERIFIED
  - id: RISK-02
    risk: Workbench implementation starts before projection conformance.
    consequence: Separate UI semantics, later rewrite.
    likelihood: Medium
    severity: High
    mitigation: Require presentation/projection contracts first.
    related_workstreams:
    - WORKSTREAM-04
    label: FACT/INFERENCE
  - id: RISK-03
    risk: Raylib/SDL/Lua provider types leak into stable contracts or game state.
    consequence: Vendor lock-in, replay/save instability.
    likelihood: Medium
    severity: High
    mitigation: Forbidden include/type validator and provider fences.
    related_workstreams:
    - WORKSTREAM-06
    label: FACT/INFERENCE
  - id: RISK-04
    risk: Full CTest debt remains ignored too long.
    consequence: Release gate remains blocked.
    likelihood: Medium
    severity: Medium
    mitigation: Targeted full-gate legacy test routing and debt ledger.
    related_workstreams:
    - WORKSTREAM-07
    label: FACT/UNVERIFIED
  - id: RISK-05
    risk: Capability status overclaimed.
    consequence: Docs/Workbench say implemented when only fixture/stub exists.
    likelihood: High
    severity: High
    mitigation: Capability Reality Ledger.
    related_workstreams:
    - WORKSTREAM-02
    label: FACT
  - id: RISK-06
    risk: Parallel Codex tasks conflict on coordinator files.
    consequence: Queue/status corruption.
    likelihood: Medium
    severity: High
    mitigation: Coordinator ownership rules and checkpoint loop.
    related_workstreams:
    - WORKSTREAM-02
    label: FACT
  - id: RISK-07
    risk: Universe Explorer free-camera becomes implicit gameplay movement.
    consequence: Wrong gameplay model and authority leakage.
    likelihood: Low-Medium
    severity: High
    mitigation: Separate observer inspection authority from embodied actor authority.
    related_workstreams:
    - WORKSTREAM-08
    label: INFERENCE
  - id: RISK-08
    risk: Preservation report overstates decisions from assistant suggestions.
    consequence: Bad spec aggregation.
    likelihood: Medium
    severity: High
    mitigation: Label decisions accepted by user vs assistant suggestions.
    related_workstreams:
    - WORKSTREAM-01
    label: FACT
  verification_queue:
  - id: VERIFY-01
    item: Live repo task queue and audit status.
    why_verification_needed: Many user-pasted statuses changed over time.
    suggested_source_type: 'GitHub/repo files: .aide/queue/current.toml, audits, log.'
    priority: P0
    related_workstreams:
    - WORKSTREAM-03
    label: UNCERTAIN / UNVERIFIED
  - id: VERIFY-02
    item: C17/C++17 baseline in current CMake/toolchain docs.
    why_verification_needed: Earlier chat had C89/C++98; later says C17/C++17.
    suggested_source_type: CMakeLists, toolchain docs, foundation audit.
    priority: P1
    related_workstreams:
    - WORKSTREAM-01
    label: UNCERTAIN / UNVERIFIED
  - id: VERIFY-03
    item: Whether FULL-GATE-LEGACY-TEST-ROUTE-01 has been run.
    why_verification_needed: It was generated, but execution unknown.
    suggested_source_type: Repo commit/audit search.
    priority: P0
    related_workstreams:
    - WORKSTREAM-07
    label: UNCERTAIN / UNVERIFIED
  - id: VERIFY-04
    item: Whether AIDE workflow layer prompts have all landed.
    why_verification_needed: Some reportedly passed in pasted summaries; may be stale.
    suggested_source_type: AIDE audits and queue.
    priority: P1
    related_workstreams:
    - WORKSTREAM-02
    label: UNCERTAIN / UNVERIFIED
  - id: VERIFY-05
    item: Third-party current facts for raylib, SDL, Lua.
    why_verification_needed: External software versions/support/licensing may change.
    suggested_source_type: Official project docs/releases before implementation.
    priority: P2
    related_workstreams:
    - WORKSTREAM-06
    label: UNCERTAIN / UNVERIFIED
  spec_book_notes:
    likely_sections:
    - Architecture doctrine
    - Workbench
    - AIDE workflow
    - Presentation/projection
    - Provider strategy
    - Task queue
    - Domain future doctrine
    unique_contributions:
    - Transition from UI Editor to Workbench
    - Provider-fenced raylib strategy
    - AIDE parallel dev doctrine
    possible_duplicates_with_other_chats:
    - Dominium operating environment doctrine
    - Foundation Lock
    - World simulation primitives
    conflicts_to_watch_for:
    - Language baseline
    - Live queue state
    - Provider timing
    formal_requirements_candidates:
    - Workbench not authority
    - Presentation projections share semantic spine
    - Third-party types fenced
    - Promotion evidence-blocked
    background_context_candidates:
    - Minecraft-style logical layouts
    - Theme mockups
    - Long-range civilization/fabrication dreams
    needs_user_confirmation:
    - Live repo state
    - Next prompt order if maintenance vs projection
  final_recommendations:
    next_action_if_continuing_this_chat: Review/execute FULL-GATE-LEGACY-TEST-ROUTE-01 or generate PACK-INTERNAL-LAYOUT-CANON-01.
    next_action_for_aggregator: Merge this package under Workbench/AIDE/presentation/provider architecture chapters.
    user_checks_required:
    - Verify live repo before execution
    - Confirm whether latest prompts have been run

```

# Aggregator Packet — Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, and Product-Spine Planning

## Packet Metadata

* Chat label: Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, and Product-Spine Planning
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial-to-broad visible context, not raw full transcript
* Confidence: 4/5 for doctrine; 3/5 for live repo state
* Staleness risk: High for live repo/external software
* Merge priority: High
* Main limitations: verify live repo state and execution of latest prompts.

## Ultra-Condensed Carry-Forward Capsule

This chat is one of the central Dominium architecture-planning conversations. It began with a practical UI problem: the launcher UI was mangled and flickering, and the user wanted a Windows-first UI Editor / Tool Editor. Early turns produced detailed Codex prompts for a Phase A UI Editor, TLV/JSON document handling, layout engine, import/export, CLI ops scripting, and launcher/setup layout tests. That plan was later explicitly superseded. The user said the old UI Editor and Tool Editor were good ideas but bad final products, and they should be abandoned and recycled.

The replacement is Dominium Workbench Platform: a cross-platform rendered, modular, command-driven, agent-aware production environment for building Dominium and Domino artifacts. Workbench is not authority. It is a surface over contracts, commands, services, documents, patches, providers, packs, modules, artifacts, evidence, tests, and AIDE. Domino is the reusable deterministic substrate; Dominium is the game/product family; AIDE is the repo/control-plane harness; Codex is a bounded patch executor.

The chat established that CLI, TUI/text, rendered GUI, OS-native GUI, and headless are projections of the same semantic command/result/refusal/document/view/action spine. Presentation contracts and projection conformance must precede rich Workbench UI. The TUI is first-class. Rendered GUI is a portable, themeable, data-described system, not a native widget replacement. OS-native GUI can exist as optional projection.

AIDE’s workflow doctrine became: development is non-blocking; promotion is evidence-blocked. Task branches/worktrees feed dev, checkpoints prove waves, and main receives evidence-backed promotions. Capability Reality Ledger prevents fixture/stub/planned surfaces from being called implemented.

The chat also produced a third-party provider doctrine: raylib/rlgl/rlsw/raygui/raudio/SDL2/Lua should be used aggressively as replaceable providers, but Dominium owns service contracts, commands, saves, replays, packs, UI documents, provider law, and asset identity. Apps remain generic; profiles select providers; third-party types are fenced from engine/game/contracts/content/saves/replays/public SDK.

Latest user-reported state: PRESENTATION-CONTRACT-01 completed with PASS_WITH_WARNINGS. User wants to generate maintenance prompts first: FULL-GATE-LEGACY-TEST-ROUTE-01, PACK-INTERNAL-LAYOUT-CANON-01, RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01, PUBLIC-HEADER-ABI-PROMOTION-01, STORAGE-PACKAGE-PROVIDER-SPLIT-01, POINTER-WIDTH-SERIALIZATION-AUDIT-01. FULL-GATE-LEGACY-TEST-ROUTE-01 has already been generated in this chat. After that, return to PROJECTION-CONFORMANCE-01 and the read-only Workbench/Universe Explorer/provider sequence.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Verify live repo state before current-status prompts | Verification | VERIFY-01 | Task queue changed many times. | UNCERTAIN / UNVERIFIED | 3 |
| P0 | Continue targeted maintenance: full-gate/pack/taxonomy/ABI/storage/pointer audits | Task sequence | TASK-01..06 | Current user-selected next path. | FACT | 4 |
| P0 | Preserve Workbench-not-authority doctrine | Decision | DECISION-02 | Prevents GUI drift. | FACT | 5 |
| P0 | Preserve projection-unification doctrine | Decision | DECISION-04 | Unifies CLI/TUI/rendered/native/headless. | FACT | 4 |
| P1 | Provider strategy: raylib/SDL/Lua as fenced providers | Decision | DECISION-11 | Speeds progress without lock-in. | FACT/INFERENCE | 4 |

## Workstream Summaries

See Workstream Register in File 04. Active workstreams: architecture identity, AIDE workflow, product spine, presentation, Workbench, provider strategy, maintenance, Universe Explorer, theme/UI system, long-range simulation doctrine.

## Compact Registers for Merge

Use sections 17–28 in the registers file.

## Possible Cross-Chat Duplicates

Dominium operating environment doctrine, Foundation Lock, AIDE workflow, Workbench, deep primitives, Universe Explorer, provider strategy, and presentation contracts likely overlap other chats.

## Possible Cross-Chat Conflicts

Language baseline C89/C++98 vs C17/C++17; exact current repo queue; whether provider/raylib work starts before or after projection conformance; whether full CTest remains T4 debt.

## Spec Book Integration Guidance

Formalize Workbench/AIDE/presentation/provider doctrine as requirements. Preserve old UI Editor and Tool Editor as superseded context, not current architecture. Verify live repo state before merging current task statuses.

## Aggregator Warnings

Do not treat user-reported repo statuses as eternally current. Do not assume generated prompts were executed. Do not turn conceptual Universe Explorer into current implementation. Do not make raylib the architecture.


# SELF-AUDIT AND REVISION

## 32. Adversarial Self-Audit

| Issue | Severity | Correction needed | Correction applied? | Residual risk |
|---|---|---|---|---|
| No raw full transcript export is available. | High | Mark coverage partial and avoid claiming exhaustive transcript extraction. | Yes | Some early details may be omitted. |
| Live repo state may be stale. | High | Put repo status in verification queue. | Yes | Future assistant must verify. |
| Assistant suggestions may be mistaken for user decisions. | High | Only mark user-accepted or operationalized plans as FACT decisions. | Yes | Some acceptance inferred from user continuing plan. |
| Long chat may contain more artifacts than listed. | Medium | Preserve major prompts/uploads and mark ledger non-exhaustive if necessary. | Yes | Minor prompts may be omitted. |
| Screenshots not exhaustively analyzed. | Medium | Mark them as visual references rather than full requirements. | Yes | Future spec may need separate visual audit. |
| C17/C++17 baseline uncertain. | Medium | Label VERIFY-02. | Yes | Requires repo check. |
| The report is long but still compressed relative to full chat. | Medium | Created files and substantial in-chat version. | Yes | User may ask for deeper sections. |

## 33. Corrections Applied

- Added explicit caveats about partial access and stale repo state.
- Separated accepted decisions from inferences and tentative plans.
- Preserved rejected/superseded old UI Editor/Tool Editor plans.
- Added verification items for live repo and C17/C++17 baseline.
- Added artifact ledger entries for generated prompts and uploaded preservation file.

## 34. Final Reliability Assessment

* Completeness rating: 4/5 for visible chat substance; 3/5 for raw transcript fidelity.
* Reliability rating: 4/5 for decisions and doctrine; 3/5 for live repo/task execution state.
* Human-readability rating: 4/5.
* Aggregation-readiness rating: 4/5 with caveats.
* Main remaining uncertainty sources: live repo status, skipped earlier turns, whether latest generated prompts were executed, exact CMake/language baseline, external library current facts.
* Manual review before merging: recommended.


# 35. File Export Package

Files were created in `/mnt/data` and bundled into a ZIP package.

# In-Chat Reader — Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, and Product-Spine Planning

This package preserves the chat as a human-readable report plus structured registers, context transfer, spec sheet, aggregator packet, and verification/audit materials.

Read first:
1. File 06 Reader Brief for a quick overview.
2. File 01 Human-Readable Report for the full story.
3. File 04 Registers for actionable IDs.
4. File 02 Context Transfer Packet when starting a new chat.
5. File 03 Spec Sheet and File 05 Aggregator Packet for merging with other reports.

Safest next actions:
- Verify live repo state.
- Confirm whether FULL-GATE-LEGACY-TEST-ROUTE-01 has been run.
- Generate PACK-INTERNAL-LAYOUT-CANON-01 if not.
- Preserve Workbench/AIDE/provider/presentation doctrines.

Question menu:
- What did we decide about Workbench?
- What replaced the old UI Editor plan?
- Which prompts were generated?
- Which tasks are next?
- What needs verification before implementation?
- Which parts should go into the master spec book?
