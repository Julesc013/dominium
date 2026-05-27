

---

# FILE: dominium_full_conversation_companion_report__00_manifest.md

# Manifest — Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion

Date anchor: 2026-05-27 Australia/Melbourne

This package is an accompanying human-readable companion report for the long Dominium/Domino/Workbench/AIDE planning conversation. It supplements the earlier preservation package already created in this chat and bundles the earlier reports, screenshots/mockups, uploaded preservation instruction, and this new companion report into one archive.

## Files created in this companion package

| File | Purpose |
|---|---|
| `dominium_full_conversation_companion_report__00_manifest.md` | Manifest for the companion package. |
| `dominium_full_conversation_companion_report__01_complete_human_report.md` | Main human-readable detailed report of the whole conversation. |
| `dominium_full_conversation_companion_report__02_decision_task_risk_registers.md` | Condensed structured registers for decisions, workstreams, tasks, risks, and verification. |
| `dominium_full_conversation_companion_report__03_current_plan_and_prompt_queue.md` | Current practical execution plan and prompt queue as of the end of the visible conversation. |
| `dominium_full_conversation_companion_report__04_specbook_bridge.md` | How this chat should feed into a future master Project Spec Book. |
| `dominium_full_conversation_companion_report__05_verification_checklist.md` | Verification queue and stale fact checklist. |
| `dominium_full_conversation_companion_report__06_artifact_index.md` | Index of previous generated files and visual/source artifacts bundled in the ZIP. |
| `dominium_full_conversation_companion_report__07_reader_brief.md` | Shorter reader brief for quick review. |
| `dominium_full_conversation_companion_report__FULL_COMBINED_REPORT.md` | All companion report files combined into one Markdown file. |
| `dominium_full_conversation_companion_report__handoff_package.zip` | ZIP containing this companion package, previous preservation package files, screenshots/mockups, and uploaded instruction text. |

## Included supporting material in the ZIP

- Previous preservation files named `dominium_workbench_aide_architecture_preservation__*`.
- Earlier package files named `Dominium_Workbench_AIDE_Presentation_Provider_Strategy__*` if present.
- Uploaded screenshot/mockup images from May 18, 2026, if present in `/mnt/data`.
- The uploaded `Pasted text.txt` preservation instruction.

## Caveats

- This is a reconstruction from visible conversation context plus generated files available in the sandbox. It is not a forensic raw transcript export.
- Live repository status must still be verified before executing the next Codex prompt.
- External software facts about raylib, SDL2, Lua, CMake, language baselines, and OS support should be verified before becoming formal requirements.



---

# FILE: dominium_full_conversation_companion_report__01_complete_human_report.md

# Complete Human-Readable Companion Report — Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless explicitly labelled PROJECT-CONTEXT. |
| Apparent access | Partial-to-broad visible context. The current chat includes a very large visible transcript, user-provided handoffs, generated prompts, uploaded screenshots, uploaded preservation instructions, and prior generated report files. It is not guaranteed to include every skipped early turn verbatim. |
| Previously generated files available? | Yes. Earlier preservation packages and report files are present in `/mnt/data`. |
| Uploaded files/artifacts present? | Yes. The uploaded preservation instruction, multiple screenshots/mockups, and prior generated packages are visible in the sandbox. |
| Contains future plans? | Yes. The chat contains extensive near-term, medium-term, and long-term roadmaps. |
| Contains decisions? | Yes. Several major architectural decisions were accepted or revised. |
| Contains pending tasks? | Yes. The latest user-selected maintenance tasks and future queue are preserved. |
| Contains unresolved questions? | Yes. Live repo status, execution state of prompts, full-gate debt, and sequencing decisions require verification. |
| Staleness risk | High for live repo/current software status; medium for roadmap sequencing; low for settled chat doctrine. |
| Extraction confidence | 4/5 for visible chat substance; 3/5 for live repo status. |
| Safe for later aggregation? | Yes, with caveats. |
| Main limitations | No raw full transcript export, some early turns were summarized/skipped, external repo/software facts may be stale, and screenshots were treated as design references rather than formal specs. |

### Plain-language limitations

This companion report preserves the meaning, decisions, and task plan of the conversation as visible in this chat. It is not a line-by-line transcript. Where the chat discussed the live `julesc013/dominium` repo, those statements should be treated as **UNCERTAIN / UNVERIFIED** until checked against the repository. Where the user pasted status reports from Codex or another chat, those are preserved as **FACT stated in chat**, not independently verified facts unless separately checked.

## 1. One-Page Orientation

This conversation records a major architectural transition in the Dominium project. It began with an immediate practical concern: the existing Windows launcher UI looked broken, flickered, and needed a better way to design UIs. The initial direction was to create a Windows-first UI Editor and eventually a Tool Editor that could visually design pixel-perfect UIs and generate TLV-based layouts/code. That early plan was explored in depth: TLV schemas, UI IR, deterministic JSON mirrors, layout engines, Win32/DGFX/null backends, action code generation, import/export, CLI scripting, native widget previews, and launcher/setup redesign tests were all discussed and turned into prompt plans.

Over the course of the chat, the user corrected the direction. The old UI Editor/Tool Editor path was judged useful as an idea but wrong as a final architecture. OS-native GUI design can rely on first-party tools such as Visual Studio and Xcode where appropriate. Dominium’s real internal tooling should instead prove and reuse the same runtime, command, rendering, UI, package, and diagnostic systems that the client and other products need. This led to the replacement concept: **Dominium Workbench Platform**.

Workbench is the central product concept of this chat. It is not a monolithic IDE and not an authority over the project. It is a cross-platform rendered, modular, command-driven, agent-aware production environment. It should eventually let the user and agents build the entire project: code scaffolds, packs, modules, UI/HUD documents, themes, renderer tests, release artifacts, diagnostics, evidence packets, AIDE/Codex work units, and product compositions. Its design doctrine is: Workbench designs artifacts; runtime executes artifacts; contracts constrain artifacts; content packages artifacts; apps consume artifacts; tests prove artifacts; AIDE governs changes; Codex patches code.

The second major outcome was an AIDE development model. The chat established that **development should be non-blocking, promotion should be evidence-blocked**. This means work can accumulate on task branches and dev with classified partials or warnings, but main should only receive checkpointed, evidence-backed promotion. Codex is a bounded patch executor; AIDE is a scheduler, context compiler, evidence ledger, blocker classifier, repair/resume generator, checkpoint coordinator, and promotion gatekeeper. A series of AIDE prompts were generated or planned: workflow law, WorkUnit schema, dev/main policy, checkpoint loop, and capability reality ledger.

The third major outcome was a unified presentation doctrine. CLI, TUI/text, rendered GUI, OS-native GUI, and headless reports must not become separate product implementations. They are projections over the same semantic spine: command/result/refusal/document/view/action/diagnostic/evidence. The TUI is a serious first-class projection. The rendered GUI is a backend-agnostic system of layouts, controls, widgets, style tokens, themes, view documents, draw lists, and provider-backed renderers. OS-native widgets remain optional projections, not core semantics.

The fourth major outcome was a service-first provider strategy. The chat concluded that raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and related libraries can be used aggressively, but only as replaceable providers behind Dominium service contracts. Dominium owns contracts, packets, saves, replays, packs, UI documents, asset identity, provider law, and simulation law. Third-party types must not leak into engine, game, contracts, content, pack schemas, save/replay formats, command/result schemas, or public SDK surfaces.

By the end, the project direction had moved from broad structure cleanup to targeted maintenance and product-spine development. The user reported that `PRESENTATION-CONTRACT-01` had completed with `PASS_WITH_WARNINGS`, then selected six targeted maintenance prompts to generate before replanning: `FULL-GATE-LEGACY-TEST-ROUTE-01`, `PACK-INTERNAL-LAYOUT-CANON-01`, `RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01`, `PUBLIC-HEADER-ABI-PROMOTION-01`, `STORAGE-PACKAGE-PROVIDER-SPLIT-01`, and `POINTER-WIDTH-SERIALIZATION-AUDIT-01`. The last generated prompt in the visible chat was `FULL-GATE-LEGACY-TEST-ROUTE-01`.

A future assistant must understand that this chat is not simply about UI. It records the architecture for how Dominium should build itself: through contracts, commands, services, providers, documents, patches, modules, packs, apps, workspaces, diagnostics, evidence, AIDE, Codex, and eventually Workbench.

## 2. The Story of the Conversation

### 2.1 The initial problem: launcher UI and the old UI Editor concept

The conversation began with the user wanting a product designer/software architect/prompt engineer to help design an internal graphical UI creation tool. The immediate pain point was the Dominium Windows launcher UI: it looked mangled and flickered. The user wanted a tool that could visually design pixel-perfect UIs and broad-strokes functionality for setup, launcher, game, and tools.

Early discussion clarified target operating systems, the current DUI/TLV schema/state system, and the existing backends: Win32 common controls, DGFX, and null. The user wanted true native controls where possible, custom rendering only where necessary, and eventually universal UI definitions across products. We discussed DPI scaling, canonical TLV, deterministic JSON mirrors, codegen, event binding, flicker causes, and bootstrap phases.

A large prompt plan followed: repo scaffolding, canonical UI IR, TLV I/O, capability system, layout engine, splitter/tabs/scroll widgets, action codegen, Phase A UI Editor, Tool Editor bootstrap, Win32 batching/flicker fixes, tests, docs, and capability tests through launcher/setup redesigns.

### 2.2 UI Editor gains CLI/import/export and launcher/setup tests

The user then asked for the UI Editor to import existing tools and modify their UIs, expose a CLI so Codex could automate designs, and use the UI Editor to create launcher/setup designs similar to Minecraft’s logical layout. The key correction was that “Minecraft-style” meant logical layout, not graphical skin: native Win32 widgets only, structured around header/sidebar/tabs/footer for launcher and wizard-style pages for setup. We generated prompts for UI discovery/import/export, CLI modes, `ops.json` scripts, launcher generation, setup generation, and hardening.

### 2.3 The pivot: old editors are not the final product

The user then redirected the entire plan. They argued that native OS widget GUI tools already exist through Visual Studio, Xcode, etc. The project needed a cross-platform rendered tool environment that uses the same CLI, TUI, and rendered GUI systems as the client. The old UI Editor and Tool Editor were good exploratory ideas but bad final products. This produced the Dominium Workbench concept.

### 2.4 Workbench becomes the production environment

Workbench was defined as a rendered, modular, command-driven userland tools environment over the same spine as the client. It should not be one giant editor. It should be one shell with modules and workspaces. Workspaces include Project Graph Explorer, Interface Studio, Module/Pack Foundry, App Composer, Release Forge, Agent Control Workspace, Renderer/Theme Laboratory, and Replay/Trace Workspace. Smaller reusable modules include validation runner, pack browser, command browser, document inspector, patch/diff viewer, evidence viewer, renderer test panel, theme previewer, and asset browser.

The user stressed that as the sole developer, they want to use Workbench and tool modules to actually build the entire Domino/Dominium project. That expanded Workbench from a command dashboard into a visual/agentic production environment: a place to create code scaffolds, data, packs, UI, graphics, sounds, tests, release artifacts, and AIDE/Codex work units. The governing loop became: intent → plan → generate/edit → preview/simulate → validate/test → patch/commit/package → evidence → next action.

### 2.5 AIDE and parallel development

The discussion then moved into AIDE. The user wanted to automate as much as possible through Codex and AIDE. We developed a task operating model: AIDE creates WorkUnits, tracks attempts, blockers, evidence, repairs, resumes, checkpoints, and promotion decisions. Codex executes bounded tasks. Development can continue with classified partials and repairable blockers; promotion to main requires evidence.

This led to generated prompts: `STATUS-RECONCILE-02`, `AIDE-WORKFLOW-LAW-01`, `AIDE-WORKUNIT-SCHEMA-01`, `AIDE-DEV-MAIN-POLICY-01`, `AIDE-CHECKPOINT-LOOP-01`, and `AIDE-CAPABILITY-REALITY-LEDGER-01`. The user wanted to run AIDE workflow, WorkUnit schema, and dev/main policy concurrently on the same machine via separate Codex tasks.

### 2.6 Presentation architecture, TUI, rendered GUI, themes, and Workbench authoring

The conversation then formalized presentation. CLI, TUI, rendered GUI, native GUI, headless reports, Workbench panels, AIDE, CI, launcher, setup, client, and server should all project the same command/result/refusal/document/view/action/evidence model. The TUI should be a serious keyboard-first terminal projection, not an ASCII toy. Rendered GUI should be a data-described UI system built from layout engines, semantic controls, widget compositions, style tokens, theme profiles, draw-list renderers, and projection conformance tests.

The user shared images as references for Workbench themes and modules. These were interpreted as visual/mood and layout examples: GNOME-like command studio, macOS-like release forge, Win11 UI/HUD sandbox, pack browser, agent work board, XP/Win7-style boards, worldgen lab, TUI studio, and primitive-only themes. The conclusion was that one cross-platform Workbench app can mix and match module + workspace layout + theme + renderer + platform capability.

### 2.7 Provider strategy: raylib, SDL2, Lua

Later, the chat incorporated raylib, rlsw, rlgl, raygui, raudio, SDL2, and Lua. The core doctrine became: use these aggressively, but only as replaceable providers. Dominium owns service contracts. Providers satisfy those contracts. Profiles select providers. Third-party types are fenced. Apps stay generic. Workbench edits Dominium documents, not raylib objects.

This prompted a provider structure: `runtime/<service>/providers/<provider>`, `contracts/provider`, `contracts/capability`, `contracts/schema/runtime/<service>`, `release/profiles`, `content/profiles`, and `external/upstream`. The plan explicitly rejected `runtime/raylib/render`, `apps/client/rendered/raylib`, `contracts/raylib`, top-level `profiles`, and top-level `labs`.

### 2.8 Product spine, structure cleanup, and current maintenance path

The final part of the conversation dealt with repo status and task queue. The user pasted status reports indicating that `PRESENTATION-CONTRACT-01` completed with warnings, and then chose to generate six maintenance prompts before replanning. `FULL-GATE-LEGACY-TEST-ROUTE-01` was generated. This preservation task followed.

## 3. Main Topics Discussed

### Topic 1 — UI Editor / Tool Editor bootstrap plan

The early UI Editor plan was a structured attempt to fix the launcher UI and build a tool for UI authoring. It covered DUI/TLV, native widgets, Win32 preview, deterministic TLV/JSON, layout, validation, codegen, `ops.json`, import/export, and launcher/setup generation. The conclusion was that these are useful components but not the final product architecture. They should become Workbench modules and services.

### Topic 2 — Dominium Workbench Platform

Workbench became the central product concept. It is a cross-platform rendered production environment, not a monolithic editor. It hosts workspaces and modules over contracts, commands, documents, patches, services, providers, packs, artifacts, evidence, and tests. It eventually self-hosts by editing its own safe artifacts first, then product UIs, packs, modules, apps, and AIDE work units.

### Topic 3 — AIDE/Codex workflow and parallel development

AIDE should govern work; Codex should execute bounded patches. The chat designed branch roles, lifecycle states, WorkUnit schemas, blocker taxonomy, dirty worktree policy, dev/main promotion, checkpoint loops, and capability reality ledger. The key doctrine is non-blocking dev and evidence-blocked promotion.

### Topic 4 — Unified presentation/projection system

CLI, TUI, rendered GUI, OS-native GUI, and headless output should all project the same command/result/document/view/action model. This enables reuse across client, server, launcher, setup, Workbench, tests, CI, and AIDE.

### Topic 5 — TUI as first-class projection

The TUI should be a deterministic, keyboard-first, low-dependency projection of the operating environment. It should use panels, tables, trees, forms, logs, status bars, progress meters, and command input. It should support server/admin, setup recovery, CI, SSH, accessibility, and agent workflows.

### Topic 6 — Rendered GUI, themes, and Workbench UX

The rendered GUI must be backend-agnostic. Layouts, controls, widgets, themes, styles, views, and workspaces should be modular and extensible. Themes include first-party primitive-only profiles and OEM+ mimic profiles. The GUI should be task-first, command-backed, evidence-visible, and projection-neutral.

### Topic 7 — Provider strategy

Use raylib/SDL2/Lua as seed providers. Keep service identity first-party and provider implementation replaceable. Fence third-party types. Add provider manifests, service contracts, forbidden include validators, and conformance tests before implementation wedges.

### Topic 8 — Repo structure and maintenance

The chat concluded not to restart broad structure cleanup. Active structure is good enough; remaining issues should be targeted maintenance. The immediate generated maintenance prompt was `FULL-GATE-LEGACY-TEST-ROUTE-01`.

### Topic 9 — Universe Explorer

Universe Explorer became a future north-star: a read-only product/Workbench/Client slice for seamless inspection of universe-scale data, reference frames, materialization, streaming, fidelity degradation, and provenance. It should start contract-first and headless before visual implementation or embodiment.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

- Fix the launcher UI problem by creating better UI tooling.
- Build tools that can help create setup, launcher, game, and future tools.
- Support cross-platform CLI, TUI, rendered GUI, and optional native GUI.
- Make code reusable for other Domino-based games and different engine projects.
- Preserve all decisions, tasks, prompts, constraints, files, and artifacts in a downloadable package.
- Automate as much as possible with Codex/AIDE without losing governance.
- Develop visually with Workbench as soon as the foundation allows.

### 4.2 Inferred Goals

INFERENCE: The user wants to stop losing context across long chats and future assistants. The user also wants a professional-grade architecture more like a serious engine/platform/OS project than a one-off indie game. The user wants a single system where tools are also tests of the engine/client architecture.

### 4.3 Goals That Changed Over Time

The first goal was a UI Editor. That changed to a Workbench Platform. The first idea of native widget UI tooling changed to rendered cross-platform UI tooling. Broad repo structure cleanup changed to targeted maintenance. Raylib changed from possible engine dependency to seed provider suite.

### 4.4 Goals Still Unresolved

The live repo state must be verified before executing future prompts. Full-gate debt remains. Workbench shell is not implemented. Provider runtime, package runtime, module loader, renderer, native GUI, gameplay, and Universe Explorer remain future work.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | Supersede UI Editor/Tool Editor as final products. | Accepted | Avoids one-off tooling architecture. | 5 | FACT |
| DECISION-02 | Make Workbench the production environment. | Accepted | Unifies tool, UI, agent, pack, module, app, release workflows. | 5 | FACT |
| DECISION-03 | Workbench is not authority. | Accepted | Prevents GUI/tool drift from contracts/services. | 5 | FACT |
| DECISION-04 | AIDE governs, Codex patches. | Accepted | Enables safe automation. | 5 | FACT |
| DECISION-05 | Development non-blocking, promotion evidence-blocked. | Accepted | Supports parallel dev without corrupting main. | 5 | FACT |
| DECISION-06 | CLI/TUI/rendered/native/headless are projections. | Accepted | Enables reuse across apps. | 5 | FACT |
| DECISION-07 | Use raylib/SDL/Lua as providers, not architecture. | Accepted conceptually | Gives speed without lock-in. | 4 | FACT/INFERENCE |
| DECISION-08 | Stop broad structure cleanup. | Accepted | Avoids churn after structure is good enough. | 4 | FACT |
| DECISION-09 | Run targeted maintenance before replanning. | Accepted | User explicitly selected six maintenance prompts. | 5 | FACT |
| DECISION-10 | Build Workbench read-only first. | Accepted conceptually | Safer progressive self-hosting. | 4 | FACT/INFERENCE |

### Explanation of major decisions

The Workbench decision was the largest architectural correction. The old UI Editor plan could have solved the immediate launcher problem, but it would not have proven the client/runtime stack. Workbench makes the tools use the same systems they help produce.

The AIDE decision was driven by the scale of the project. Once many Codex tasks run in parallel, stale queues, dirty worktrees, partial branches, and unclear blockers become first-order risks. AIDE gives those states names and evidence requirements.

The projection decision was driven by portability and reuse. If CLI, TUI, rendered GUI, and native GUI are implemented separately, they will drift. If they are projections of the same command/result/view system, all products share semantics.

The provider decision was driven by speed and long-term independence. Raylib/SDL/Lua can accelerate development, but Dominium must own the contracts.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

| ID | Option | Status | Reason | Reconsider conditions |
|---|---|---|---|---|
| REJECTED-01 | Windows-only UI Editor as final tool. | Superseded | Too narrow and not client/runtime proof. | As a temporary bootstrap or Workbench module only. |
| REJECTED-02 | Monolithic Tool Editor. | Superseded | Would become separate architecture. | Never as final architecture. |
| REJECTED-03 | Workbench as central authority. | Rejected | Contracts/services/proof must remain authority. | Not expected. |
| REJECTED-04 | Broad root cleanup forever. | Deprioritized | Structure good enough; targeted maintenance now. | If validators block narrow slices. |
| REJECTED-05 | Raylib-shaped app/runtime directories. | Rejected | Vendor-shaped architecture creates lock-in. | Only as temporary proof folders. |
| REJECTED-06 | Pure C99 / pure C++11 baseline. | Rejected conceptually | C17+C++17 with C ABI better for scale. | Verify if live repo requires otherwise. |

## 7. Important Reasoning, Rationale, and Tradeoffs

The main tradeoff was speed versus structural integrity. The user wants visible progress, but not at the cost of another rewrite spiral. The final doctrine uses providers and profiles to get speed while preserving replaceability.

A second tradeoff was governance versus momentum. A project with this many moving parts can stall under too much governance, but without enough, it risks false claims and hidden coupling. The compromise is fast strict and targeted validators on dev, and stronger checkpoint/full-gate proof for main.

A third tradeoff was UI richness versus semantic safety. Workbench should eventually be visual and powerful, but it must first be read-only and command-backed. Visual editing comes only after document/patch/presentation/projection law.

A fourth tradeoff was native GUI versus rendered portability. Native GUIs can exist as optional projections and can use Visual Studio/Xcode tooling, but the core cross-platform Workbench must be rendered through Dominium’s own document/view/control/theme/render system.

## 8. Plans, Future Work, and Next Steps

### Immediate user-selected maintenance path

1. `FULL-GATE-LEGACY-TEST-ROUTE-01` — generated immediately before this preservation request. It routes/retired full-gate tests that still expect old roots.
2. `PACK-INTERNAL-LAYOUT-CANON-01` — decide/canonicalize pack-internal layout.
3. `RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01` — classify residual runtime/engine taxonomy.
4. `PUBLIC-HEADER-ABI-PROMOTION-01` — reduce ABI/public header promotion warning debt.
5. `STORAGE-PACKAGE-PROVIDER-SPLIT-01` — clarify storage/package provider boundaries.
6. `POINTER-WIDTH-SERIALIZATION-AUDIT-01` — audit `size_t`, pointers, pointer-width-dependent serialization risks.

### Mainline after maintenance/replanning

1. `PROJECTION-CONFORMANCE-01`.
2. `ACCESSIBILITY-CONTRACT-01`.
3. `TEXT-LOCALIZATION-CONTRACT-01`.
4. `WORKBENCH-SHELL-READONLY-01`.
5. `UNIVERSE-EXPLORER-CONTRACT-01`.
6. `UNIVERSE-EXPLORER-HEADLESS-01`.
7. `PROVIDER-MANIFEST-WEDGE-01`.
8. `SERVICE-CONTRACT-WEDGE-01`.
9. `THIRD-PARTY-FENCE-01`.
10. `RAYLIB-PROVIDER-WEDGE-01`.
11. `UNIVERSE-EXPLORER-VISUAL-01`.

### Recommended next action

Verify live repo state, then review/run `FULL-GATE-LEGACY-TEST-ROUTE-01`, then generate `PACK-INTERNAL-LAYOUT-CANON-01` if the queue/status supports the maintenance lane.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit constraints and preferences

- Use source-grounded, audit-ready answers.
- Preserve uncertainty labels.
- Do not silently infer.
- Do not turn brainstorms into decisions.
- Do not treat assistant suggestions as accepted decisions unless the user accepted them.
- Create actual downloadable files if tools are available.
- Include a human-readable report in-chat even if files are generated.
- Do not restart settled doctrine unnecessarily.
- Use exact, bounded Codex prompts.

### 9.2 Inferred constraints and preferences

- The user prefers professional-grade modular architecture over quick hacks.
- The user values long-term reuse for future games and engines.
- The user wants a system that can support human and agentic development together.

### 9.3 Uncertain preferences

- Exact balance between maintenance and product-spine work after the six maintenance tasks.
- Exact timing of provider implementation relative to Universe Explorer.
- Exact format of future master Project Spec Book.

## 10. Files, Artifacts, Outputs, and Prompts

Artifacts include uploaded screenshots/mockups, preservation instruction text, earlier preservation packages, generated prompt plans, generated Codex prompts, and this companion report package. The most important generated prompt immediately before preservation was `FULL-GATE-LEGACY-TEST-ROUTE-01`.

The screenshots should be preserved as visual references, not treated as formal specs. The prior preservation package should be preserved because it contains sections and structured registers already generated. This companion package bundles those files and adds a more direct accompanying report.

## 11. Open Questions and Unresolved Issues

| ID | Question | Why it matters | Resolution path |
|---|---|---|---|
| QUESTION-01 | What is the live repo state after this chat? | Determines next prompt. | Inspect repo, `.aide/queue/current.toml`, audits. |
| QUESTION-02 | Has `FULL-GATE-LEGACY-TEST-ROUTE-01` been executed? | Determines next maintenance prompt. | Check commits/audits. |
| QUESTION-03 | Is C17+C++17 fully implemented in build files? | Affects portability and provider plan. | Verify CMake/toolchain docs. |
| QUESTION-04 | When should raylib provider work start? | Affects speed vs governance. | After provider manifest/service/fence tasks. |
| QUESTION-05 | How soon should Universe Explorer enter implementation? | Affects product identity. | After projection/workbench read-only and headless contract proof. |

## 12. Risks and Failure Modes

Future chats could easily misunderstand this conversation by treating Workbench as a GUI framework, treating raylib as the engine, resuming broad structure cleanup, skipping projection conformance, or assuming live repo status from stale pasted reports. The mitigation is to verify repo state first, preserve the contract/service/projection/provider distinctions, and follow the task queue.

## 13. Contribution to Future Spec Book

This chat should feed the following spec book chapters:

- Workbench Platform.
- AIDE/Codex development process.
- Presentation/projection architecture.
- Provider strategy and third-party fencing.
- TUI/rendered GUI/theme design.
- Progressive self-hosting.
- Product-spine task sequencing.
- Universe Explorer north-star.
- Maintenance/full-gate debt strategy.

Formal requirements candidates include: Workbench is not authority; third-party providers are fenced; CLI/TUI/rendered/native/headless are projections; development non-blocking/promotion evidence-blocked; every visual edit becomes a document patch; provider capabilities require evidence.

## 14. What I Should Remember

- The old UI Editor/Tool Editor plan is superseded.
- Workbench is a production environment over contracts/services/proof, not authority.
- AIDE governs work; Codex executes bounded patches.
- CLI, TUI, rendered GUI, OS-native GUI, and headless are projections of one semantic spine.
- Raylib/SDL/Lua are providers, not architecture.
- Broad structure cleanup should stop; targeted maintenance remains.
- The next immediate maintenance prompt after `FULL-GATE-LEGACY-TEST-ROUTE-01` is likely `PACK-INTERNAL-LAYOUT-CANON-01`, pending live repo verification.

## 15. Best Follow-Up Questions

- “Generate PACK-INTERNAL-LAYOUT-CANON-01.”
- “What did we decide about Workbench self-hosting?”
- “List all pending generated prompts and their order.”
- “What must be verified in the live repo before continuing?”
- “Turn the provider/raylib doctrine into formal requirements.”
- “Create a Project Spec Book chapter outline from this conversation.”
- “Which maintenance tasks can run in parallel?”
- “What should the first read-only Workbench shell actually show?”
- “What is the difference between provider profiles and content profiles?”
- “What are the top risks if we skip projection conformance?”

## 16. Compact Human Summary

This conversation records a major architectural evolution for Dominium. It began with a concrete launcher UI problem: the current Windows launcher looked bad and flickered. The first proposed solution was a Windows-first UI Editor followed by a Tool Editor, using the existing DUI/TLV system, Win32 previews, layout engines, codegen, CLI scripting, import/export, and launcher/setup layout generation. That path was explored deeply and converted into many prompts, but it was later judged wrong as a final product.

The user reframed the goal. Instead of building a one-off editor, Dominium needs a cross-platform rendered Workbench that uses the same systems as the client, server, launcher, setup, CLI, TUI, and headless tools. Workbench should not be authority; it should be the rich production environment over contracts, commands, services, documents, patches, providers, packs, modules, diagnostics, evidence, and tests. It should eventually help the user and agents build the whole project: code scaffolds, packs, modules, themes, UI/HUDs, tests, releases, AIDE/Codex work units, and future Domino-based games.

AIDE became the governance system. Codex is a bounded patch executor. AIDE is the scheduler, context compiler, blocker classifier, evidence ledger, repair/resume generator, checkpoint coordinator, and promotion gatekeeper. The central doctrine is: development is non-blocking, promotion is evidence-blocked. Dev and task branches can hold classified partials and warnings; main requires evidence-backed checkpoints.

The UI architecture became projection-based. CLI, TUI/text, rendered GUI, OS-native GUI, and headless outputs should all present the same command/result/refusal/document/view/action/diagnostic/evidence model. The TUI is first-class. Rendered GUI is a modular system of layouts, semantic controls, widgets, themes, style tokens, draw lists, and renderer providers. OS-native GUI is optional projection, not semantic authority.

The provider strategy became service-first. Raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua can be used aggressively, but only as replaceable providers. Dominium owns service contracts, provider law, commands, saves, replays, packs, UI documents, and asset identity. Third-party types must not leak into stable law or public SDK surfaces.

The current end state is targeted maintenance plus product-spine continuation. The user reported `PRESENTATION-CONTRACT-01` complete with warnings, then selected six maintenance tasks before replanning: full-gate legacy test routing, pack internal layout canon, runtime/engine residual taxonomy, public header ABI promotion, storage/package provider split, and pointer-width serialization audit. `FULL-GATE-LEGACY-TEST-ROUTE-01` was generated immediately before this preservation task.

The best next action is to verify live repo state, then review or run `FULL-GATE-LEGACY-TEST-ROUTE-01`, then generate `PACK-INTERNAL-LAYOUT-CANON-01` if status supports it.



---

# FILE: dominium_full_conversation_companion_report__02_decision_task_risk_registers.md

# Structured Registers — Dominium Full Conversation Companion

## Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Workbench Platform | Build a modular production environment over Dominium contracts/services. | Planned; validation/static/projection slices discussed. | Read-only then authoring Workbench that builds artifacts and products. | Active future | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | AIDE/Codex Process | Safely automate development. | Workflow prompts generated; some reported done. | Task branches, dev integration, checkpoint main promotion. | Active | P0 | 4 | FACT |
| WORKSTREAM-03 | Presentation Architecture | Unify CLI/TUI/rendered/native/headless. | `PRESENTATION-CONTRACT-01` reported complete. | Projection conformance and read-only shell. | Active | P0 | 4 | FACT stated in chat |
| WORKSTREAM-04 | Provider Strategy | Use third-party libraries as replaceable providers. | Doctrine established. | Provider manifests/fences/conformance and raylib wedge. | Planned | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-05 | Maintenance/Full-Gate Debt | Resolve targeted structural/test debt. | Six maintenance tasks selected; first prompt generated. | Full-gate debt reduced without broad cleanup. | Active | P0 | 4 | FACT |
| WORKSTREAM-06 | Universe Explorer | Prove read-only seamless universe inspection. | Conceptual north-star. | Headless proof then visual explorer. | Future | P1 | 3 | INFERENCE |
| WORKSTREAM-07 | UI/TUI/Theme System | Modular layouts, controls, themes, TUI/rendered profiles. | Conceptual architecture settled. | Theme Lab, Interface Studio, Renderer Sandbox. | Future | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-08 | Product Apps | Reuse same modules/packs/UI across client/server/launcher/setup. | Barebones/product-spine discussion. | Apps as thin compositions over shared services. | Active/future | P1 | 4 | FACT/INFERENCE |

## Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Supersede old UI Editor/Tool Editor as final products. | Accepted | User explicitly said abandon/recycle them. | Avoid one-off Windows-first editor architecture. | Recycle ideas into Workbench modules. | WORKSTREAM-01 | 5 | FACT |
| DECISION-02 | Workbench is not authority. | Accepted | Repeated in chat. | Prevent GUI/tools from bypassing contracts. | Workbench uses commands/services/documents/patches. | WORKSTREAM-01 | 5 | FACT |
| DECISION-03 | AIDE governs, Codex patches. | Accepted | Repeated in plans. | Enables parallel automation safely. | Create WorkUnits, checkpoints, evidence. | WORKSTREAM-02 | 5 | FACT |
| DECISION-04 | Development non-blocking, promotion evidence-blocked. | Accepted | User handoff/plan. | Speeds dev while protecting main. | dev/task branches vs main/checkpoints. | WORKSTREAM-02 | 5 | FACT |
| DECISION-05 | Presentation modes are projections. | Accepted | Repeated doctrine. | Prevent separate CLI/TUI/GUI implementations. | Projection contract/conformance required. | WORKSTREAM-03 | 5 | FACT |
| DECISION-06 | Use raylib/SDL/Lua as providers. | Accepted conceptually | User asked and accepted doctrine. | Fast progress without lock-in. | Provider manifests/fencing needed. | WORKSTREAM-04 | 4 | FACT/INFERENCE |
| DECISION-07 | Stop broad structure cleanup. | Accepted | User/current plans. | Avoid churn after structure is clean enough. | Run targeted maintenance tasks. | WORKSTREAM-05 | 4 | FACT |
| DECISION-08 | Workbench starts read-only. | Accepted conceptually | Assistant recommendation accepted in later plan. | Avoid unsafe self-hosting. | Workbench shell read-only before authoring. | WORKSTREAM-01 | 4 | INFERENCE |

## Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Verify live repo state. | P0 | U0 | Human/Codex | None | repo checkout | current queue/audits/status | inspect before next task | all | UNCERTAIN |
| TASK-02 | Run/review FULL-GATE-LEGACY-TEST-ROUTE-01. | P0 | U0 | Codex | Presentation complete | generated prompt | stale full-gate paths routed | generate next maintenance prompt | WORKSTREAM-05 | FACT |
| TASK-03 | Generate PACK-INTERNAL-LAYOUT-CANON-01. | P0 | U1 | Assistant/Codex | TASK-02 or live approval | status | prompt/report | execute if selected | WORKSTREAM-05 | FACT |
| TASK-04 | PROJECTION-CONFORMANCE-01. | P0 | U1 | Codex | presentation contract | schemas/fixtures | proof of projection parity | continue UI path | WORKSTREAM-03 | FACT |
| TASK-05 | WORKBENCH-SHELL-READONLY-01. | P1 | U2 | Codex | projection conformance | runtime/app context | read-only Workbench shell | validate usefulness | WORKSTREAM-01 | INFERENCE |
| TASK-06 | PROVIDER-MANIFEST-WEDGE-01. | P1 | U2 | Codex | AIDE/presentation path | provider doctrine | provider schemas/manifests | service/fence wedge | WORKSTREAM-04 | INFERENCE |
| TASK-07 | UNIVERSE-EXPLORER-CONTRACT-01. | P1 | U2 | Codex | Workbench/read-only/projection | explorer doctrine | contract-only explorer spec | headless proof | WORKSTREAM-06 | INFERENCE |

## Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Treat stale repo status as current. | Wrong next prompt. | Medium | High | Verify live repo. | all | FACT/INFERENCE |
| RISK-02 | Build Workbench UI too early. | Parallel UI system. | Medium | High | Complete projection conformance first. | WORKSTREAM-01 | INFERENCE |
| RISK-03 | Raylib types leak into contracts/engine/game. | Provider lock-in. | Medium | High | Forbidden include/type validators. | WORKSTREAM-04 | INFERENCE |
| RISK-04 | Full-gate debt hidden as pass. | False readiness. | Medium | High | Keep warning/T4 status explicit. | WORKSTREAM-05 | FACT/INFERENCE |
| RISK-05 | Assistant suggestions treated as decisions. | Spec corruption. | Medium | Medium | Use labels and decision evidence. | all | FACT |
| RISK-06 | Screenshots treated as specs. | Overfitted UI. | Medium | Medium | Treat as references/moodboards only. | WORKSTREAM-07 | INFERENCE |

## Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Live `.aide/queue/current.toml`. | Determines next prompt. | repo file | P0 | all | UNCERTAIN |
| VERIFY-02 | Execution status of maintenance prompts. | Avoid duplicate work. | git log/audits | P0 | WORKSTREAM-05 | UNCERTAIN |
| VERIFY-03 | C17/C++17 baseline. | Affects provider/build policy. | CMake/docs | P1 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-04 | Full CTest debt status. | Affects release readiness. | test reports | P1 | WORKSTREAM-05 | UNCERTAIN |
| VERIFY-05 | Existing prior preservation files completeness. | Affects aggregation. | file package | P2 | archival | UNCERTAIN |



---

# FILE: dominium_full_conversation_companion_report__03_current_plan_and_prompt_queue.md

# Current Plan and Prompt Queue — Dominium Companion Report

## Current immediate state from this chat

The user reported `PRESENTATION-CONTRACT-01` as `PASS_WITH_WARNINGS` and then selected six maintenance tasks to generate before replanning. The assistant generated `FULL-GATE-LEGACY-TEST-ROUTE-01` immediately before the preservation request.

## Immediate maintenance sequence

1. `FULL-GATE-LEGACY-TEST-ROUTE-01` — generated. Route/retire full-gate tests still expecting retired roots.
2. `PACK-INTERNAL-LAYOUT-CANON-01` — decide and enforce pack-internal layout law.
3. `RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01` — classify residual runtime/engine taxonomy warnings.
4. `PUBLIC-HEADER-ABI-PROMOTION-01` — burn down public header ABI promotion debt.
5. `STORAGE-PACKAGE-PROVIDER-SPLIT-01` — clarify storage/package/provider boundaries.
6. `POINTER-WIDTH-SERIALIZATION-AUDIT-01` — audit pointer-width-dependent persistence/serialization risks.

## Mainline after maintenance/replanning

1. `PROJECTION-CONFORMANCE-01`
2. `ACCESSIBILITY-CONTRACT-01`
3. `TEXT-LOCALIZATION-CONTRACT-01`
4. `WORKBENCH-SHELL-READONLY-01`
5. `UNIVERSE-EXPLORER-CONTRACT-01`
6. `UNIVERSE-EXPLORER-HEADLESS-01`
7. `PROVIDER-MANIFEST-WEDGE-01`
8. `SERVICE-CONTRACT-WEDGE-01`
9. `THIRD-PARTY-FENCE-01`
10. `RAYLIB-PROVIDER-WEDGE-01`
11. `UNIVERSE-EXPLORER-VISUAL-01`

## Execution rule

Verify live repo state before each prompt. Do not assume the pasted status remains current. Do not run broad Workbench, renderer, gameplay, package runtime, provider runtime, or module loader work until gates authorize it.



---

# FILE: dominium_full_conversation_companion_report__04_specbook_bridge.md

# Spec Book Bridge — Dominium Companion Report

## Chapters this chat should inform

1. Domino/Dominium architecture overview.
2. Workbench Platform.
3. AIDE/Codex development process.
4. Presentation/projection architecture.
5. TUI and rendered GUI doctrine.
6. Theme/style/control/widget system.
7. Provider strategy and third-party fencing.
8. Product-spine task sequence.
9. Targeted maintenance/full-gate debt.
10. Universe Explorer north-star.
11. Progressive self-hosting.

## Formal requirements candidates

- Workbench is not authority.
- CLI/TUI/rendered/native/headless are projections of the same semantic spine.
- Every user-visible action maps to a command or documented view/action binding.
- All edits go through document/patch/transaction/evidence flow.
- Third-party providers must not leak stable types into contracts/engine/game/content/save/replay/public SDK.
- Provider profiles select providers; apps remain generic.
- Development is non-blocking; promotion is evidence-blocked.
- Capability status must distinguish planned, specified, fixture-only, stubbed, implemented, tested, exposed, release-supported.

## Background context candidates

- The original UI Editor/Tool Editor exploration.
- Minecraft-style launcher/setup logical layout test.
- Screenshot/mockup themes and UI inspiration.
- Early open-world/civilization/domain ambitions.

## Items needing verification before spec merge

- Live repo task queue and audits.
- C17/C++17 build baseline.
- Current full-gate/CTest status.
- Actual provider/contract directories in repo.
- Whether each generated prompt has been executed.



---

# FILE: dominium_full_conversation_companion_report__05_verification_checklist.md

# Verification Checklist and Audit — Dominium Companion Report

## Verification queue

1. Check `.aide/queue/current.toml` before generating or executing the next prompt.
2. Check whether `FULL-GATE-LEGACY-TEST-ROUTE-01` has already been run.
3. Check whether the current repo still reports `PRESENTATION-CONTRACT-01` as latest completed mainline task.
4. Check whether the six maintenance tasks remain the selected next sequence.
5. Verify C17/C++17 in live build files.
6. Verify current full CTest/T4 debt status.
7. Verify whether provider manifest/service/fence tasks already exist in repo.
8. Verify whether the previous preservation package is complete and not superseded.

## Self-audit

| Issue | Severity | Correction needed | Correction applied? | Residual risk |
|---|---|---|---|---|
| No raw complete transcript export | High | Mark coverage as partial-to-broad | Yes | Some early details may be missing |
| Live repo facts may be stale | High | Add verification queue | Yes | Must verify before action |
| Assistant suggestions could be mistaken for decisions | Medium | Label decisions and inferences | Yes | Some acceptance inferred from user agreement |
| Screenshots could be overinterpreted | Medium | Treat as visual references | Yes | Future visual spec should review them |
| Prior generated files may be superseded | Medium | Bundle but mark as supporting material | Yes | Future package may be needed |

## Reliability

- Completeness: 4/5
- Reliability: 4/5 for chat doctrine, 3/5 for live repo state
- Human-readability: 4/5
- Aggregation-readiness: 4/5

Manual review is recommended before merging into a master Project Spec Book.



---

# FILE: dominium_full_conversation_companion_report__06_artifact_index.md

# Artifact Index — Dominium Companion Report

## Included report files

This companion package includes new report files plus previously generated preservation files.

## Included prior packages

The ZIP includes, if present:

- `dominium_workbench_aide_architecture_preservation__handoff_package.zip`
- `Dominium_Workbench_AIDE_Presentation_Provider_Strategy__handoff_package.zip`
- individual prior preservation `.md` and `.yaml` files

## Included uploaded/reference artifacts

The ZIP includes, if present:

- `Pasted text.txt` — uploaded preservation instructions.
- Screenshot/mockup images from May 18, 2026.
- Additional uploaded image-like files named `file_000...` where present.

## Important generated prompt artifact

The most recent major prompt generated in the chat was `FULL-GATE-LEGACY-TEST-ROUTE-01`, a targeted maintenance task for routing stale full-gate tests that still expect retired roots.



---

# FILE: dominium_full_conversation_companion_report__07_reader_brief.md

# Reader Brief — Dominium Companion Report

## Top things to know

1. The old UI Editor/Tool Editor plan was superseded.
2. Dominium Workbench is now the central production-environment concept.
3. Workbench is not authority; it operates over contracts, commands, services, documents, patches, providers, packs, modules, diagnostics, evidence, and tests.
4. AIDE governs development; Codex executes bounded patches.
5. Development is non-blocking; promotion is evidence-blocked.
6. CLI/TUI/rendered/native/headless are projections of one semantic spine.
7. TUI is first-class.
8. Rendered GUI must be modular and backend-agnostic.
9. OS-native GUI is optional projection, not core semantic law.
10. Raylib/SDL/Lua are seed providers, not architecture.
11. Apps stay generic; profiles select providers.
12. Broad structure cleanup should stop.
13. Targeted maintenance remains.
14. `PRESENTATION-CONTRACT-01` was reported complete with warnings.
15. `FULL-GATE-LEGACY-TEST-ROUTE-01` was generated next.
16. The next likely prompt is `PACK-INTERNAL-LAYOUT-CANON-01`, pending live status.
17. Universe Explorer is a future read-only/headless north-star before visual/gameplay work.
18. Workbench should start read-only, then progressively self-host.
19. Live repo facts must be verified before execution.
20. This package is a preservation and aggregation aid, not a live repo authority.

## Best next action

Verify current repo state and whether `FULL-GATE-LEGACY-TEST-ROUTE-01` has run. If it has not, run/review it. If it has, generate `PACK-INTERNAL-LAYOUT-CANON-01`.



---

# FILE: dominium_full_conversation_companion_report__08_future_chat_bootstrap_prompt.md

# Future Chat Bootstrap Prompt — Dominium Companion Report

I am continuing from a long Dominium/Domino/Workbench/AIDE planning chat. Treat the following as starting context, not live repo truth.

Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not assume access to the old chat. Do not re-ask answered questions. Verify stale facts before relying on them. Flag contradictions. Use the task register and open questions to determine next actions.

Core carry-forward:

- Domino = reusable deterministic substrate.
- Dominium = game/product family.
- Workbench = production, validation, editing, inspection, packaging, and evidence environment.
- AIDE = repo/control-plane harness.
- Codex = bounded patch executor.
- Contracts = law.
- Tests/replay/evidence = proof.
- Workbench is not authority.
- CLI/TUI/rendered/native/headless are projections of one command/result/refusal/document/view/action spine.
- Raylib/SDL/Lua are providers, not architecture.
- Broad structure cleanup should stop; targeted maintenance remains.
- The latest visible user-selected next sequence starts with `FULL-GATE-LEGACY-TEST-ROUTE-01`, then `PACK-INTERNAL-LAYOUT-CANON-01`, then other maintenance tasks, before returning to projection/Workbench/Universe Explorer tasks.

When you respond, state:

- context loaded;
- active priorities;
- key constraints;
- open questions;
- contradictions or uncertainties;
- recommended next action.
