# Aggregator Packet — Dominium Architecture III

## 1. Packet Metadata

- **Chat label:** Dominium Architecture III
- **Date anchor:** 2026-05-27 Australia/Melbourne
- **Source scope:** This chat only, including its prior Context Transfer Packet and OC-1 inventory.
- **Coverage:** Full visible chat appears available; uploaded files not independently inspected here.
- **Confidence:** 4/5
- **Staleness risk:** Medium-High for external compatibility claims.
- **Merge priority:** High for launcher/render/platform/support-tier decisions.
- **Main limitations:** Repo archive not inspected; uploaded launcher summaries unverified; generated Codex prompts not confirmed applied.

## 2. Ultra-Condensed Carry-Forward Capsule

Dominium Architecture III is a launcher/platform/render architecture chat. It assumes the Dominium deterministic core contract remains binding: core and sim are C89, no floats in core/sim, fixed tick phases, renderer/audio/UI cannot mutate sim, and OS-specific APIs stay behind platform/render/audio boundaries. The chat’s unique contribution is not core sim design, but the launcher and surrounding platform/render support plan.

The user finalized that launcher settings execute separate client/server binaries. The launcher is therefore a process-spawning selector, not an in-process runtime switcher. The launcher backend/core must be C89; frontend code per binary can use C++98. Client/server binaries may be single-system builds. A modular architecture was designed: C89 launcher core/model/config/capability/launch-plan logic, platform process spawn adapters, and multiple frontend skins such as engine-rendered software UI, native Win32, CLI, or TUI.

The current user-facing command decisions are: `dominium` launches the launcher; `setup` launches installer/repair/uninstaller; `dom-client` dispatches the client; `dom-server` dispatches the server. Earlier `dom-launcher` and `dom-setup` names were superseded or may only remain aliases.

Render/platform direction changed materially. The user rejected minimal/full backend duplication and requested one full implementation per backend. `vector_soft` was superseded. The current public fallback renderer is `software`, and it must work on all platforms while supporting both vector primitives and textured graphics. Every renderer must support vector-only and full graphics modes. The latest renderer list is DX9.0c, DX11, GL1.1, GL2, VK1, and software. DX12 appeared earlier but was omitted from the latest user list; treat it as unresolved/deferred. The latest platform categories are POSIX, SDL1, SDL2, and Native. Earlier X11 and Wayland were discussed; their final placement as explicit backends or Native/Linux subtypes remains unresolved.

The view/camera model expanded beyond launcher needs. The user wants instant seamless zoom to any scale, instant switching between top-down 2D and first-person 3D, vector or graphics mode for every view, and arbitrary cameras for free cam, map views, custom HUD cameras, CCTV, content creation, overlays, extra windows, and offscreen targets. These are client/render-side concepts and must not enter deterministic sim state.

The user finalized platform support tiers: Tier 1 is Windows NT 2000 SP4-latest, Mac OS X 10.6-10.14, Linux 3.2-current. Tier 2 is Windows 98 SE-Me, Windows NT 2000 SP4-latest, Mac OS 9-9.2, Mac OS X 10.6-15.0, Linux 2.6.18-current. Tier 3 is MS-DOS 3.3-6.2, Windows 3, Windows 95-Me, Windows NT 2000 SP4-latest, Mac OS 8.5-9.2, Mac OS X 10.0-latest, Linux 2.4-current. These are user decisions, but feasibility and external library/API support require verification.

Uploaded files exist and must be preserved: `/mnt/data/dominium.7z`, `/mnt/data/dom_launcher_view.c`, `/mnt/data/dom_launcher_view.h`, `/mnt/data/CMakeLists.txt`, and `/mnt/data/dom_launcher_main.c`. Prior assistant summaries described mixed engine-rendered and native Win32 launcher code, but that must be verified by inspecting the files.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Launcher executes separate binaries | Decision | DECISION-02 | Central architecture | FACT | High |
| 2 | C89 launcher core / C++98 frontends | Decision | DECISION-03/04 | Portability and language constraints | FACT | High |
| 3 | Universal software renderer replaces vector_soft | Decision | DECISION-10 | Renderer fallback architecture | FACT | High |
| 4 | Renderer modes vector/full everywhere | Decision | DECISION-11 | CAD/performance/missing asset fallback | FACT | High |
| 5 | Final support tiers | Decision | DECISION-16/17/18 | Product platform policy | FACT | High |
| 6 | Latest renderer list + DX12 uncertainty | Decision/Open question | DECISION-19/24 | Implementation scope | FACT / UNCERTAIN | Medium |
| 7 | Platform categories + X11/Wayland uncertainty | Decision/Open question | DECISION-20/QUESTION-02 | Capability matrix scope | FACT / UNCERTAIN | Medium |
| 8 | dominium/setup/dom-client/dom-server | Decision | DECISION-06/07/08 | User-facing scripts | FACT | High |
| 9 | Arbitrary cameras and view switching | Goal | DECISION-13/14/15 | Render/client architecture | FACT | High |
| 10 | Uploaded files require reinspection | Artifact/Task | ARTIFACT-01..05/TASK-01 | Implementation state unknown | FACT / UNCERTAIN | High |

## 4. Workstream Summaries


### WORKSTREAM-01 — Deterministic Dominium core and repository contract
- **Objective:** Preserve the deterministic fixed-step simulation model and repo layering while launcher/platform/render work proceeds.
- **Current state:** Project contract was explicitly supplied by the user in the chat: C89/C++98-era constraints, deterministic tick model, strict directories, no floats in core/sim, stable serialization.
- **Desired end state:** All new launcher/render/platform/input code obeys deterministic and layering rules.
- **Priority:** P0
- **Decisions:** DECISION-01
- **Tasks:** None specifically linked.
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** Global risks apply.
- **Open questions:** None recorded.
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-02 — System-agnostic launcher architecture
- **Objective:** Design the launcher as portable, modular, extensible C89 core logic plus thin frontends.
- **Current state:** Architecture designed conceptually; implementation is not confirmed.
- **Desired end state:** A C89 launch core/model/config/capability/launch-plan layer, platform process adapters, and multiple frontend skins over a shared view model.
- **Priority:** P0
- **Decisions:** None specifically linked.
- **Tasks:** TASK-07, TASK-08
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-08
- **Open questions:** QUESTION-14
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-03 — Launcher backend/frontend language split
- **Objective:** Keep backend launcher logic C89 and allow frontend code for each binary to use C++98.
- **Current state:** Explicit user decision.
- **Desired end state:** C89 backend compiles independently of OS/UI; C++98 max frontends handle platform-specific shells.
- **Priority:** P0
- **Decisions:** DECISION-03, DECISION-04
- **Tasks:** None specifically linked.
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** Global risks apply.
- **Open questions:** None recorded.
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-04 — Launcher-to-client/server process execution
- **Objective:** Launcher settings resolve to external client/server binary execution.
- **Current state:** Explicit user decision.
- **Desired end state:** A DomLaunchPlan-like structure resolves role, account, instance, platform, renderer, headless mode, executable, args, environment, and working directory.
- **Priority:** P0
- **Decisions:** DECISION-02, DECISION-05
- **Tasks:** TASK-09
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** Global risks apply.
- **Open questions:** QUESTION-12
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-05 — Unified user-facing entrypoint scripts
- **Objective:** Provide scripts/commands for dominium, setup, dom-client, and dom-server.
- **Current state:** Script templates and CMake configure/install plans were generated, but implementation is unverified.
- **Desired end state:** Consistent commands across OSes dispatch to correct launcher/setup/client/server binaries.
- **Priority:** P0
- **Decisions:** DECISION-05, DECISION-06, DECISION-07
- **Tasks:** TASK-17, TASK-18
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-13
- **Open questions:** QUESTION-15
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-06 — Setup / installer / repair / uninstaller wrapper
- **Objective:** Implement setup entrypoint for install, repair, and uninstall modes.
- **Current state:** Script behavior was specified; real setup binaries may not exist yet.
- **Desired end state:** setup [install|repair|uninstall] calls dom_setup-* with --mode=<mode>.
- **Priority:** P1
- **Decisions:** DECISION-08, DECISION-23
- **Tasks:** TASK-19
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** Global risks apply.
- **Open questions:** QUESTION-16
- **Next action:** Carry into master spec as supporting context.

### WORKSTREAM-07 — Platform backend taxonomy and capability model
- **Objective:** Normalize platform backend categories and encode allowed/conditional combinations.
- **Current state:** Latest user categories are POSIX, SDL1, SDL2, Native. Earlier chat also discussed win32, macosx, X11, Wayland, and POSIX headless.
- **Desired end state:** A single documented platform taxonomy used by CMake, launcher capabilities, scripts, and docs.
- **Priority:** P0
- **Decisions:** DECISION-09, DECISION-20
- **Tasks:** TASK-02
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-04
- **Open questions:** QUESTION-02, QUESTION-03, QUESTION-04
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-08 — Renderer backend taxonomy and capability model
- **Objective:** Normalize render backends and expose vector/full graphics capability across all.
- **Current state:** Latest user renderer list is DX9.0c, DX11, GL1.1, GL2, VK1, software. DX12 appeared earlier but was omitted later.
- **Desired end state:** Renderer enum/docs/CMake/scripts use the final list and mark DX12 as deferred/unconfirmed unless the user confirms it.
- **Priority:** P0
- **Decisions:** DECISION-19, DECISION-24
- **Tasks:** TASK-03
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-03
- **Open questions:** QUESTION-01
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-09 — Universal all-platform software renderer
- **Objective:** Replace vector_soft with one software renderer capable of vector and textured graphics on all platforms.
- **Current state:** User-finalized design goal; implementation unverified.
- **Desired end state:** engine/render/software supports vector-only mode, full graphics mode, textured primitives, missing-texture placeholders, and platform present callbacks.
- **Priority:** P0
- **Decisions:** DECISION-10, DECISION-12
- **Tasks:** TASK-13, TASK-14
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-02, RISK-10
- **Open questions:** None recorded.
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-10 — Vector/full graphics render modes
- **Objective:** Every renderer supports vector-only and graphics modes.
- **Current state:** Design accepted; not confirmed implemented.
- **Desired end state:** Runtime view/render mode can switch between CAD/vector and full textured graphics without backend replacement.
- **Priority:** P0
- **Decisions:** DECISION-11
- **Tasks:** TASK-14, TASK-15
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** Global risks apply.
- **Open questions:** None recorded.
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-11 — Instant zoom and 2D/3D view switching
- **Objective:** Support seamless zoom at any scale and instant switching between top-down 2D and first-person 3D, each in vector or graphics.
- **Current state:** Architecture designed conceptually; implementation unverified.
- **Desired end state:** View type and mode are runtime view state; command generation changes without renderer reinitialization.
- **Priority:** P1
- **Decisions:** DECISION-13, DECISION-14
- **Tasks:** TASK-16
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-09
- **Open questions:** QUESTION-13
- **Next action:** Carry into master spec as supporting context.

### WORKSTREAM-12 — Arbitrary cameras, multi-view, overlays, and offscreen targets
- **Objective:** Support free cam, maps, HUD cameras, CCTV, content creation cameras, overlays, windows, and offscreen views.
- **Current state:** Architecture proposed with camera/view/target registries.
- **Desired end state:** Render core supports arbitrary camera IDs, view IDs, target IDs, and per-frame view instances.
- **Priority:** P1
- **Decisions:** DECISION-15
- **Tasks:** TASK-16
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-09
- **Open questions:** None recorded.
- **Next action:** Carry into master spec as supporting context.

### WORKSTREAM-13 — Launcher UI tabs and bottom selectors
- **Objective:** Define launcher UI structure.
- **Current state:** User specified UI; uploaded code may differ.
- **Desired end state:** Tabs: News, Changes, Mods, Instances, Accounts, Settings. Bottom: Account, Instance, Platform, Renderer, Graphical/Headless, Client/Server.
- **Priority:** P1
- **Decisions:** None specifically linked.
- **Tasks:** TASK-08
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** Global risks apply.
- **Open questions:** None recorded.
- **Next action:** Carry into master spec as supporting context.

### WORKSTREAM-14 — Input and keybinding specification
- **Objective:** Document and implement canonical F1–F12 and core controls.
- **Current state:** F-key map and Codex prompt generated; implementation unverified.
- **Desired end state:** docs/SPEC_INPUT.md, default_bindings.json, action enum, and mapping layer consistent with launcher/game contexts.
- **Priority:** P1
- **Decisions:** DECISION-21
- **Tasks:** TASK-20, TASK-21
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-14
- **Open questions:** None recorded.
- **Next action:** Carry into master spec as supporting context.

### WORKSTREAM-15 — Platform support tiers
- **Objective:** Formalize Tier 1/2/3 OS support ranges.
- **Current state:** User finalized tier ranges.
- **Desired end state:** Docs, build tooling, and capability matrix reflect final support tiers, with feasibility verified.
- **Priority:** P0
- **Decisions:** DECISION-16, DECISION-17, DECISION-18
- **Tasks:** TASK-05, TASK-22
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-12, RISK-17
- **Open questions:** QUESTION-07, QUESTION-09, QUESTION-10, QUESTION-11
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-16 — Capability matrix
- **Objective:** Map supported and conditional platform/renderer combinations per OS/tier.
- **Current state:** Draft matrix generated; external facts and taxonomy require verification.
- **Desired end state:** Launcher filters invalid choices through static support matrix plus runtime probes.
- **Priority:** P0
- **Decisions:** DECISION-19, DECISION-20
- **Tasks:** TASK-02, TASK-06, TASK-23
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-11, RISK-17
- **Open questions:** QUESTION-08
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-17 — Launcher build/test flow
- **Objective:** Build and test launcher binaries and scripts.
- **Current state:** Build/test plan and Codex prompt generated.
- **Desired end state:** CMake targets, scripts, setup stubs, direct/script smoke tests, spawn dry-run tests.
- **Priority:** P1
- **Decisions:** None specifically linked.
- **Tasks:** TASK-10, TASK-18, TASK-24
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** Global risks apply.
- **Open questions:** None recorded.
- **Next action:** Carry into master spec as supporting context.

### WORKSTREAM-18 — Uploaded launcher code refactor
- **Objective:** Reconcile uploaded launcher code with intended architecture.
- **Current state:** Files uploaded; prior assistant summary says native Win32 launcher and engine-rendered view are mixed; exact contents unverified.
- **Desired end state:** Engine-based launcher canonical, Win32 native launcher as separate frontend/tool if retained.
- **Priority:** P0
- **Decisions:** DECISION-22
- **Tasks:** TASK-01, TASK-10, TASK-11, TASK-12
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-05, RISK-07
- **Open questions:** QUESTION-05, QUESTION-06
- **Next action:** Resolve uncertainty/inspect files.

### WORKSTREAM-19 — Documentation and Codex implementation prompts
- **Objective:** Generate prompts and docs updates for implementation.
- **Current state:** Multiple prompts generated, but not confirmed applied.
- **Desired end state:** Use consolidated final decisions to update docs/code, not stale prompt fragments.
- **Priority:** P1
- **Decisions:** None specifically linked.
- **Tasks:** TASK-04
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-06, RISK-15
- **Open questions:** None recorded.
- **Next action:** Carry into master spec as supporting context.

### WORKSTREAM-20 — Chat handoff and report packaging
- **Objective:** Produce downloadable per-chat report package for future aggregation.
- **Current state:** This file package is being created from prior CTP and visible chat.
- **Desired end state:** Markdown/YAML/ZIP package preserving state with labels and stable IDs.
- **Priority:** P0
- **Decisions:** None specifically linked.
- **Tasks:** TASK-25
- **Constraints:** Global Dominium deterministic/layering constraints apply.
- **Artifacts:** See Artifact Ledger.
- **Risks:** RISK-01, RISK-16, RISK-18
- **Open questions:** None recorded.
- **Next action:** Resolve uncertainty/inspect files.

## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Evidence | Rationale | Implications | Related | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Dominium deterministic core and layering contract remains binding. | final | User supplied project identity and docs summary. | Preserve deterministic sim and architecture. | All code/docs must obey no-floats core/sim, C89/C++98 limits, and layering. | WORKSTREAM-01 | High | FACT |
| DECISION-02 | Launcher settings execute separate client/server binaries. | final | User: settings selected in launcher will execute client or server binaries. | Simplifies platform/render/client/server separation. | Requires launch plan and spawn API. | WORKSTREAM-04 | High | FACT |
| DECISION-03 | Launcher backend/core must use C89. | final | User explicit statement. | Portability and legacy support. | Launcher core cannot rely on C++. | WORKSTREAM-03 | High | FACT |
| DECISION-04 | Launcher frontends may use C++98. | final | User explicit statement. | Permits system-specific UI shell code while staying inside project era constraints. | Frontend code should not exceed C++98. | WORKSTREAM-03 | High | FACT |
| DECISION-05 | Client/server binaries can be single-system builds. | final | User explicit statement. | Avoids universal binary complexity. | Launcher/scripts choose correct binary. | WORKSTREAM-04, WORKSTREAM-05 | High | FACT |
| DECISION-06 | Use unified entrypoints for launcher/client/server/setup. | final | User requested scripts. | Consistent UX across OSes. | Packaging scripts needed. | WORKSTREAM-05 | High | FACT |
| DECISION-07 | Use dominium as the main launcher command. | final | User requested “dominium” to launch launcher. | Product-facing command name. | dom-launcher becomes optional alias only. | WORKSTREAM-05 | High | FACT |
| DECISION-08 | Use setup as installer/repair/uninstaller command. | final | User requested “setup”. | Simple lifecycle command. | setup dispatches install/repair/uninstall. | WORKSTREAM-06 | High | FACT |
| DECISION-09 | Remove minimal/full backend split and use full single implementations. | final | User: remove minimal versions, use full single implementation. | Avoid duplicated backend code. | Launcher and game share platform/render implementations. | WORKSTREAM-07 | High | FACT |
| DECISION-10 | Replace vector_soft with a universal software renderer. | final | User explicitly requested software renderer instead of vector_soft. | One fallback renderer handles vector and textures. | Public backend is software, not vector_soft. | WORKSTREAM-09 | High | FACT |
| DECISION-11 | All renderers must support vector-only and graphics modes. | final | User explicit statement. | CAD, performance, and missing file fallback. | Every backend must implement or emulate both modes. | WORKSTREAM-10 | High | FACT |
| DECISION-12 | Software renderer must work on all platforms. | final | User explicit statement. | Universal fallback. | Renderer must be OS-independent with platform present callbacks. | WORKSTREAM-09 | High | FACT |
| DECISION-13 | Support instant seamless zoom to any scale. | final | User explicit request. | CAD-style viewing. | Camera transforms must be view-layer state. | WORKSTREAM-11 | High | FACT |
| DECISION-14 | Support instant switching between top-down 2D and first-person 3D. | final | User explicit request. | View flexibility. | View type/mode should not require renderer reinit. | WORKSTREAM-11 | High | FACT |
| DECISION-15 | Support arbitrary cameras for free cam, map, HUD, CCTV, content creation, windows, overlays. | final | User explicit request. | Extensible UI/game/tooling. | Need camera/view/target registries. | WORKSTREAM-12 | High | FACT |
| DECISION-16 | Use final Tier 1 support: Windows NT 2000 SP4-latest, Mac OS X 10.6-10.14, Linux 3.2-current. | final | User final tier list. | Main support target. | Docs and matrix must include. | WORKSTREAM-15 | High | FACT |
| DECISION-17 | Use final Tier 2 support: Win98SE-Me, NT 2000 SP4-latest, Mac OS 9-9.2, Mac OS X 10.6-15.0, Linux 2.6.18-current. | final | User final tier list. | Extended legacy support. | Docs and matrix must include. | WORKSTREAM-15 | High | FACT |
| DECISION-18 | Use final Tier 3 support: MS-DOS 3.3-6.2, Windows 3, Windows 95-Me, NT 2000 SP4-latest, Mac OS 8.5-9.2, Mac OS X 10.0-latest, Linux 2.4-current. | final | User final tier list. | Retro/heritage support. | Docs and matrix must include with feasibility caveats. | WORKSTREAM-15 | High | FACT |
| DECISION-19 | Latest renderer implementation set is DX9.0c, DX11, GL1.1, GL2, VK1, and software. | final latest / with caveat | User capability matrix request. | Defines current renderer scope. | DX12 must not be assumed final. | WORKSTREAM-08, WORKSTREAM-16 | Medium | FACT |
| DECISION-20 | Latest platform implementation categories are POSIX, SDL1, SDL2, and Native. | final latest / unresolved taxonomy | User capability matrix request. | Defines current platform scope. | X11/Wayland mapping must be resolved. | WORKSTREAM-07, WORKSTREAM-16 | Medium | FACT / UNCERTAIN |
| DECISION-21 | F1-F12 keybinding map is accepted enough to generate implementation prompt. | accepted plan | User asked for Codex prompt after keybinding proposal. | Stabilizes input semantics. | Implement SPEC_INPUT/default bindings unless revised. | WORKSTREAM-14 | Medium-High | FACT |
| DECISION-22 | Uploaded native Win32 launcher should likely become a separate frontend/tool, not the cross-platform core. | tentative | Assistant recommendation after uploaded files; user did not explicitly finalize. | Prevents Win32-only code from breaking non-Windows launcher builds. | Re-inspect files and confirm before refactor. | WORKSTREAM-18 | Medium | INFERENCE |
| DECISION-23 | Setup binaries may be stubs initially if real installer is absent. | tentative | Generated Codex prompt. | Allows scripts to test before real installer exists. | Must mark stubs clearly. | WORKSTREAM-06 | Medium | INFERENCE |
| DECISION-24 | DX12 is unresolved/deferred, not confirmed current scope. | unclear | Earlier assistant included DX12; latest user omitted it. | Avoid wrong scope. | Ask user or mark deferred. | WORKSTREAM-08 | High uncertainty | UNCERTAIN / UNVERIFIED |

### Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Inspect uploaded/repo files before implementation. | P0 | U0 | new assistant/developer | ARTIFACT-01, ARTIFACT-02, ARTIFACT-03, ARTIFACT-04, ARTIFACT-05 | Uploaded files/repo access | Verified current code state | Open launcher files and CMake; extract repo if possible. | WORKSTREAM-18 | FACT |
| TASK-02 | Resolve final platform taxonomy. | P0 | U0 | user/developer | WORKSTREAM-07 | Decision on POSIX/SDL/native/X11/Wayland | Canonical platform enum/model | Ask/decide whether X11/Wayland are Native subtypes or explicit. | WORKSTREAM-07, WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| TASK-03 | Resolve DX12 status. | P0 | U0 | user/developer | WORKSTREAM-08 | User confirmation | Renderer list finalized | Treat DX12 as deferred until confirmed. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| TASK-04 | Update project docs with final launcher/platform/render/support/input decisions. | P0 | U1 | Codex/developer | TASK-02, TASK-03 | This package and existing docs | Updated docs | Patch docs/DIRECTORY_CONTEXT.md, docs/BUILDING.md, SPEC_LAUNCHER, SPEC_PLATFORM_SUPPORT, SPEC_INPUT. | WORKSTREAM-19 | FACT |
| TASK-05 | Create docs/SPEC_PLATFORM_SUPPORT.md or equivalent. | P0 | U1 | Codex/developer | WORKSTREAM-15 | Final tier list | Support tier doc | Add Tier 1/2/3 table and caveats. | WORKSTREAM-15 | FACT |
| TASK-06 | Create/verify capability matrix data and docs. | P0 | U1 | Codex/developer | TASK-02, TASK-03, VERIFY-01 | Renderer/platform taxonomy and verified external facts | Static+runtime capability filtering | Encode matrix with Y/conditional/not supported. | WORKSTREAM-16 | FACT / UNCERTAIN |
| TASK-07 | Implement launcher C89 core types/config/caps/launch plan. | P0 | U1 | Codex/developer | TASK-01, TASK-02 | Existing launcher code and design | game/launcher/core/* | Add pure C89 core. | WORKSTREAM-02 | FACT |
| TASK-08 | Implement launcher state and viewmodel. | P0 | U1 | Codex/developer | TASK-07 | Core config/caps | game/launcher/ui/* | Add action handling and viewmodel. | WORKSTREAM-02, WORKSTREAM-13 | FACT |
| TASK-09 | Implement platform process spawn API. | P0 | U1 | Codex/developer | TASK-07 | Launch plan and platform APIs | dom_platform_launch_spawn and adapters | Add Win32/POSIX/macOS implementations. | WORKSTREAM-04 | FACT |
| TASK-10 | Refactor launcher CMake and targets. | P0 | U1 | Codex/developer | TASK-01 | Current CMake | Separated targets | Ensure Win32 code not built on non-Windows. | WORKSTREAM-17, WORKSTREAM-18 | FACT |
| TASK-11 | Create engine-based launcher main. | P0 | U1 | Codex/developer | TASK-01, TASK-08 | Engine platform/render APIs | dom_launcher_engine_main.c | Loop polls input, draws view, presents. | WORKSTREAM-18 | FACT |
| TASK-12 | Preserve native Win32 launcher as separate target if desired. | P1 | U2 | Codex/developer | TASK-01, TASK-10 | dom_launcher_main.c | dom_launcher-win32-native | Guard under WIN32 only. | WORKSTREAM-18 | INFERENCE |
| TASK-13 | Implement universal software renderer. | P0 | U1 | Codex/developer | WORKSTREAM-09 | Render API/draw commands | engine/render/software | Support vector/full and textures/placeholders. | WORKSTREAM-09 | FACT |
| TASK-14 | Implement shared draw command core. | P0 | U1 | Codex/developer | TASK-13 | Draw command format | engine/render/core/dom_draw_common | Normalize commands for all renderers. | WORKSTREAM-09, WORKSTREAM-10 | FACT |
| TASK-15 | Add vector/full render mode to API and backends. | P0 | U1 | Codex/developer | TASK-13, TASK-14 | Render API | dom_render_mode support | Mode controls vector vs full graphics. | WORKSTREAM-10 | FACT |
| TASK-16 | Implement camera/view/target registries. | P1 | U2 | Codex/developer | TASK-14 | View/camera design | dom_camera/dom_view/dom_target | Enable arbitrary cameras and views. | WORKSTREAM-11, WORKSTREAM-12 | FACT |
| TASK-17 | Add packaging scripts. | P0 | U1 | Codex/developer | TASK-02, TASK-03 | Binary naming | Script templates | Add dominium, setup, dom-client, dom-server. | WORKSTREAM-05 | FACT |
| TASK-18 | Add CMake configure/install rules for scripts. | P0 | U1 | Codex/developer | TASK-17 | CMake target names | Generated install scripts | Use configure_file/install(PROGRAMS). | WORKSTREAM-05, WORKSTREAM-17 | FACT |
| TASK-19 | Add setup binaries or stubs. | P1 | U2 | Codex/developer | TASK-17 | Installer path decision | dom_setup-* | Stub if no installer exists. | WORKSTREAM-06 | FACT |
| TASK-20 | Add input spec/default bindings/action enum. | P1 | U2 | Codex/developer | WORKSTREAM-14 | Keybinding map | SPEC_INPUT/default_bindings/actions | Implement documented controls. | WORKSTREAM-14 | FACT |
| TASK-21 | Extend or create input mapping layer. | P1 | U3 | Codex/developer | TASK-20 | Existing input stack | Mapping layer | Avoid duplicate systems; extend existing if present. | WORKSTREAM-14 | FACT |
| TASK-22 | Verify Linux kernel/libc/toolchain/distro claims. | P1 | U1 | developer/research | WORKSTREAM-15 | External docs/tests | Verified support docs | Research before publishing. | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| TASK-23 | Verify DirectX/OpenGL/Vulkan/SDL/macOS/Mac OS support claims. | P1 | U1 | developer/research | WORKSTREAM-16 | External docs/tests | Accurate matrix | Research and test. | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| TASK-24 | Smoke-test launcher/scripts. | P0 | U2 | developer/tester | TASK-10, TASK-17, TASK-18 | Built targets | Test results | Run direct and via scripts; test setup/client/server wrappers. | WORKSTREAM-17 | FACT |
| TASK-25 | Create final per-chat package files and ZIP. | P0 | U0 | assistant | WORKSTREAM-20 | Prior CTP and visible chat | Markdown/YAML/ZIP package | This task. | WORKSTREAM-20 | FACT |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Source | Implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | /engine/core and /engine/sim are C89 only. | technical | hard | User project contract | No C++/C99 in deterministic core/sim. | Using newer language features there. | High | FACT |
| CONSTRAINT-02 | Other engine modules are C++98 max unless explicitly allowed. | technical | hard | User project contract | Avoid C++11+ APIs/features. | Using modern C++ in engine modules. | High | FACT |
| CONSTRAINT-03 | No floats in /engine/core or /engine/sim. | technical/determinism | hard | User project contract | Use integer/fixed point only in core sim. | Any float/double use in core/sim. | High | FACT |
| CONSTRAINT-04 | Fixed tick phase order must be preserved. | technical/determinism | hard | User project contract | Do not reorder INPUT→PRE-STATE→SIMULATION→NETWORKS→MERGE→POST-PROCESS→FINALIZE. | Changing order. | High | FACT |
| CONSTRAINT-05 | Sim is single-threaded deterministic; background threads cannot mutate sim. | technical/determinism | hard | User project contract | Keep async work non-sim or mediated deterministically. | Threaded sim mutation. | High | FACT |
| CONSTRAINT-06 | Renderer/audio/UI never mutate sim state. | technical/layering | hard | User project contract | Render/audio/UI consume state/commands only. | Render-side sim writes. | High | FACT |
| CONSTRAINT-07 | OS headers only in appropriate platform/render/audio boundaries. | technical/layering | hard | User project contract | Launcher core must be OS-free. | Including windows.h in core/model. | High | FACT |
| CONSTRAINT-08 | CMake uses explicit sources and no network fetch. | technical/build | hard | User project contract | No globbing or configure/build downloads. | Network dependency fetch. | High | FACT |
| CONSTRAINT-09 | Launcher backend/core must be C89. | technical | hard | User decision | Write launcher core in C89. | Using C++ in launcher core. | High | FACT |
| CONSTRAINT-10 | Launcher frontends may use C++98, not newer by default. | technical | hard | User decision | Frontend code can be C++98 max. | C++11+ frontend code without approval. | High | FACT |
| CONSTRAINT-11 | Launcher launches separate binaries. | architecture | hard | User decision | Implement spawn plan/API. | In-process client/server switch. | High | FACT |
| CONSTRAINT-12 | Client/server binaries may be single-system. | architecture | hard | User decision | Do not require universal binary. | Assuming one client supports all systems. | High | FACT |
| CONSTRAINT-13 | Software renderer must work on all platforms. | technical | hard | User decision | Universal fallback renderer. | Platform-specific software renderer dependency. | High | FACT |
| CONSTRAINT-14 | Every renderer supports vector and graphics modes. | technical | hard | User decision | Mode must be runtime-capable. | Backend only supports textured path. | High | FACT |
| CONSTRAINT-15 | Every platform should be capable of renderer or headless. | technical | hard | User decision | Platform init must support no-window/headless. | Headless server opening a window. | High | FACT |
| CONSTRAINT-16 | Final OS support tiers must be preserved. | product | hard | User final tier list | Docs/matrix use user-specified ranges. | Dropping tier without user decision. | High | FACT |
| CONSTRAINT-17 | Direct user statements outrank assistant suggestions. | handoff/evidence | hard | User current request | Do not promote unaccepted suggestions. | Treating assistant idea as user decision. | High | FACT |
| CONSTRAINT-18 | External facts require verification before future use. | evidence | hard | User current request | Mark OS/library claims stale. | Publishing unverified compatibility. | High | FACT |
| CONSTRAINT-19 | Preserve rejected/superseded options and contradictions. | handoff | hard | User current request | Record changes of direction. | Repeating rejected designs. | High | FACT |
| CONSTRAINT-20 | Final package must be self-contained and downloadable if tools allow. | formatting | hard | User current request | Create files/ZIP and links. | Only inline summary when files can be made. | High | FACT |

### Open Questions Register

| ID | Question | Why it matters | Known | Unknown | Resolution | Priority | Related | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Is DX12 in scope now, deferred, or dropped? | Affects renderer enum, CMake, scripts, docs. | DX12 was discussed earlier. Latest user list omitted DX12. | Final status. | Ask user or treat deferred. | P0 | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Are X11 and Wayland explicit platforms or Native Linux subtypes? | Affects platform taxonomy and matrix. | Earlier discussed explicitly; latest platform categories are POSIX/SDL1/SDL2/Native. | Final mapping. | User/developer taxonomy decision. | P0 | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Is POSIX headless-only? | Affects server/client capabilities. | POSIX used for headless in generated scripts. | Whether POSIX can render or only provide file/process/timers. | Platform API decision. | P0 | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What exactly is Native per OS/tier? | Needed for support matrix. | Native is final category. | Mapping to Win32/Win16/Cocoa/Carbon/X11/Wayland/DOS. | Document platform taxonomy. | P0 | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What is the actual current repo state? | Implementation must not assume prompts were applied. | Files were uploaded. | Exact contents and build state. | Inspect repo/files. | P0 | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Are prior uploaded-file summaries accurate? | Refactor path depends on them. | Prior assistant summarized them. | Exact code. | Reopen files. | P0 | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What libc/libstdc++ baselines accompany Linux kernel tiers? | Kernel ranges alone insufficient. | User finalized kernel versions. | libc/toolchain minima. | External verification and toolchain decision. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Can SDL2 be supported on Win9x? | Tier 2/3 matrix. | Likely conditional at best. | Exact feasibility/shim. | Research/test. | P1 | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | How feasible are Mac OS 8.5/9.x targets? | Tier 2/3 support. | User wants them. | Toolchains/API/render strategy. | Research/toolchain proof. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | How feasible is Mac OS X 10.0-latest support? | Tier 3. | User wants 10.0-latest. | Deployment/API split. | Research/test. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | How to support Windows NT 2000 SP4-latest with modern toolchains? | All tiers include NT 2000+. | User wants it. | CRT/toolchain/API split. | Research/test. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Will retro systems run servers? | Binary matrix. | Servers discussed generally. | DOS/Win3/Mac classic server support. | Product decision. | P2 | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Is visual replay determinism required? | Render math choices. | Sim determinism required. | Visual determinism not established. | Product decision. | P2 | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | What launcher config file format should be used? | Core implementation. | Config needed. | JSON/custom/TOML. | Design decision. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | Should dom-launcher/dom-setup remain aliases? | User-facing UX. | dominium/setup are final primary names. | Alias policy. | User/developer decision. | P2 | WORKSTREAM-05 | INFERENCE |
| QUESTION-16 | What installer technology should setup wrap? | Setup command. | Wrapper contract known. | Real installer backend. | Packaging decision. | P2 | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact | Type | Purpose | Status | Origin | Carry forward | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | /mnt/data/dominium.7z | file | Repo archive uploaded by user. | Uploaded; prior assistant said .7z could not be opened. | User upload | yes | Exact contents unverified. | FACT / UNCERTAIN |
| ARTIFACT-02 | /mnt/data/dom_launcher_view.c | file/code | Launcher engine-rendered view code. | Uploaded; content summary unverified. | User upload | yes | Reinspect before use. | FACT / UNCERTAIN |
| ARTIFACT-03 | /mnt/data/dom_launcher_view.h | file/code | Header for launcher view. | Uploaded; content summary unverified. | User upload | yes | Reinspect before use. | FACT / UNCERTAIN |
| ARTIFACT-04 | /mnt/data/CMakeLists.txt | file/code | Launcher build configuration. | Uploaded; content summary unverified. | User upload | yes | Reinspect before use. | FACT / UNCERTAIN |
| ARTIFACT-05 | /mnt/data/dom_launcher_main.c | file/code | Native launcher implementation, reportedly Win32. | Uploaded; content summary unverified. | User upload | yes | Reinspect before use. | FACT / UNCERTAIN |
| ARTIFACT-06 | docs/DIRECTORY_CONTEXT.md | reference doc | Canonical repo layout. | Referenced by user. | User initial context | yes | Not fully pasted, but summarized. | FACT |
| ARTIFACT-07 | docs/SPEC_CORE.md | reference doc | Deterministic core spec. | Referenced by user. | User initial context | yes | Summarized in chat. | FACT |
| ARTIFACT-08 | docs/DATA_FORMATS.md | reference doc | Serialization/data formats. | Referenced by user. | User initial context | yes | Summarized in chat. | FACT |
| ARTIFACT-09 | docs/BUILDING.md | reference doc | Build/language contract. | Referenced by user. | User initial context | yes | Summarized in chat. | FACT |
| ARTIFACT-10 | docs/dev/dominium_new_root.txt | reference doc | Annotated tree/responsibilities. | Referenced by user. | User initial context | yes | Not pasted in full. | FACT |
| ARTIFACT-11 | docs/SPEC_LAUNCHER.md | proposed doc | Launcher architecture spec. | Proposed, not confirmed created. | Assistant prompt | yes | Use latest decisions. | FACT |
| ARTIFACT-12 | docs/SPEC_ENTRYPOINTS.md | proposed doc | Entrypoint/script semantics. | Proposed earlier; may be merged into launcher/build docs. | Assistant response | maybe | Earlier dom-launcher names superseded. | FACT |
| ARTIFACT-13 | docs/SPEC_INPUT.md | proposed doc | Input/keybinding spec. | Prompt generated. | Assistant prompt | yes | Should include F1-F12 map. | FACT |
| ARTIFACT-14 | docs/SPEC_PLATFORM_SUPPORT.md | proposed doc | Support tiers and capability matrix. | Proposed. | Assistant response | yes | Needs verification caveats. | FACT |
| ARTIFACT-15 | game/launcher/core/dom_launch_types.h | proposed code | Launcher core types. | Proposed. | Assistant design | yes | C89. | FACT |
| ARTIFACT-16 | game/launcher/core/dom_launch_config.{h,c} | proposed code | Accounts/instances/profiles config. | Proposed. | Assistant design | yes | Format undecided. | FACT |
| ARTIFACT-17 | game/launcher/core/dom_launch_caps.{h,c} | proposed code | Capability data. | Proposed. | Assistant design | yes | Uses platform/render matrix. | FACT |
| ARTIFACT-18 | game/launcher/core/dom_launch_plan.{h,c} | proposed code | Launch plan builder. | Proposed. | Assistant design | yes | Pure C89 logic. | FACT |
| ARTIFACT-19 | game/launcher/ui/dom_launcher_state.{h,c} | proposed code | Launcher state/action handling. | Proposed. | Assistant design | yes | C89. | FACT |
| ARTIFACT-20 | game/launcher/ui/dom_launcher_viewmodel.{h,c} | proposed code | Frontend-neutral launcher viewmodel. | Proposed. | Assistant design | yes | Feeds native/vector/CLI UIs. | FACT |
| ARTIFACT-21 | engine/platform/dom_platform_launch.h | proposed code | Platform-agnostic process spawn API. | Proposed. | Assistant design | yes | Implement per OS. | FACT |
| ARTIFACT-22 | engine/render/dom_render_api.h | proposed code | Render API, modes, caps. | Proposed. | Assistant design | yes | Check existing API first. | FACT |
| ARTIFACT-23 | engine/render/software/dom_render_software.{c,h} | proposed code | Universal software renderer. | Proposed. | Assistant design | yes | Replaces vector_soft. | FACT |
| ARTIFACT-24 | engine/render/core/dom_draw_common.{h,c} | proposed code | Draw command format. | Proposed. | Assistant design | yes | Shared by renderers. | FACT |
| ARTIFACT-25 | engine/render/core/dom_view.h/.c | proposed code | View/camera helpers. | Proposed. | Assistant design | yes | 2D/3D view state. | FACT |
| ARTIFACT-26 | engine/render/core/dom_camera.h / registry | proposed code | Arbitrary camera registry. | Proposed. | Assistant design | yes | Future camera system. | FACT |
| ARTIFACT-27 | engine/render/core/dom_target.h/.c | proposed code | Render target/window/offscreen mapping. | Proposed. | Assistant design | yes | Needed for cameras/overlays/CCTV. | FACT |
| ARTIFACT-28 | game/client/input/default_bindings.json | proposed data | Default keybindings. | Prompt generated. | Assistant prompt | yes | No comments in JSON. | FACT |
| ARTIFACT-29 | game/client/input/dom_input_actions.h | proposed code | Input action enum. | Prompt generated. | Assistant prompt | yes | F1-F12 actions. | FACT |
| ARTIFACT-30 | game/client/input/dom_input_mapping.{h,c} | proposed code | Input mapping layer. | Prompt generated. | Assistant prompt | yes | Extend existing if present. | FACT |
| ARTIFACT-31 | packaging/scripts/dominium.sh.in and .cmd.in | proposed script | Launch launcher. | Template generated. | Assistant prompt | yes | Primary launcher command. | FACT |
| ARTIFACT-32 | packaging/scripts/setup.sh.in and .cmd.in | proposed script | Setup wrapper. | Template generated. | Assistant prompt | yes | install/repair/uninstall. | FACT |
| ARTIFACT-33 | packaging/scripts/dom-client.sh.in and .cmd.in | proposed script | Client dispatch wrapper. | Template generated. | Assistant prompt | yes | Renderer selection. | FACT |
| ARTIFACT-34 | packaging/scripts/dom-server.sh.in and .cmd.in | proposed script | Server dispatch wrapper. | Template generated. | Assistant prompt | yes | Headless. | FACT |
| ARTIFACT-35 | Codex prompt: docs/platform/render/scripts implementation | prompt | Instruct Codex to update docs and implement architecture. | Generated. | Assistant response | yes | Review for superseded details before use. | FACT |
| ARTIFACT-36 | Codex prompt: launcher build/test/scripts | prompt | Implement CMake targets/scripts/stubs. | Generated. | Assistant response | yes | Review target names. | FACT |
| ARTIFACT-37 | Codex prompt: input/keybindings | prompt | Implement input spec/default bindings. | Generated. | Assistant response | yes | Use latest keymap. | FACT |
| ARTIFACT-38 | Codex prompt: uploaded launcher refactor | prompt | Refactor current launcher files. | Generated. | Assistant response | yes | File summaries unverified. | FACT / UNCERTAIN |
| ARTIFACT-39 | F1-F12 keybinding table | table/output | Canonical input reference. | Generated. | Assistant response | yes | Accepted enough for implementation prompt. | FACT |
| ARTIFACT-40 | Support tier table | table/output | OS support policy. | Generated from user final list. | Assistant response/user list | yes | Needs feasibility verification. | FACT |
| ARTIFACT-41 | Capability matrix draft | table/output | Renderer/platform filtering. | Generated. | Assistant response | yes | Needs verification and taxonomy cleanup. | FACT / UNCERTAIN |
| ARTIFACT-42 | OC-1 Discovery Inventory | handoff output | Inventory of chat state. | Generated. | Assistant response | yes | Basis for this package. | FACT |
| ARTIFACT-43 | Context Transfer Packet | handoff output | Maximum-fidelity state transfer. | Generated. | Assistant response | yes | Basis for this package. | FACT |
| ARTIFACT-44 | This report package | generated document package | Final per-chat downloadable package. | Created now. | Assistant file generation | yes | Markdown/YAML/ZIP. | FACT |

### Risk Register

| ID | Risk | Consequence | Likelihood | Severity | Mitigation | Related | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Treating brainstorms or assistant suggestions as final user decisions. | Wrong implementation/spec. | medium | high | Prioritize latest direct user statements. | WORKSTREAM-20 | FACT |
| RISK-02 | Resurrecting vector_soft as public renderer. | Violates user decision and fragments fallback path. | medium | high | Use software renderer with vector/full modes. | WORKSTREAM-09 | FACT |
| RISK-03 | Including DX12 without confirmation. | Scope and docs mismatch. | medium | medium | Mark DX12 unresolved/deferred. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| RISK-04 | Ignoring X11/Wayland taxonomy ambiguity. | Invalid platform model. | medium | high | Resolve Native/POSIX mapping. | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| RISK-05 | Assuming uploaded file summaries are accurate. | Bad refactor. | medium | high | Inspect actual files. | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |
| RISK-06 | Assuming generated prompts were applied. | Duplicate/conflicting work. | medium | high | Inspect repo state. | WORKSTREAM-19 | FACT |
| RISK-07 | Compiling Win32 native launcher on non-Windows. | Build failure. | medium | high | Separate source lists/targets. | WORKSTREAM-18 | FACT |
| RISK-08 | Leaking OS APIs into launcher core. | Portability break. | medium | high | Keep core C89/OS-free. | WORKSTREAM-02 | FACT |
| RISK-09 | Camera/view/render state mutating sim. | Determinism violation. | low | critical | Keep view state client/render-side. | WORKSTREAM-11, WORKSTREAM-12 | FACT |
| RISK-10 | Software renderer delayed. | Launcher/fallback blocked. | medium | high | Prioritize software renderer. | WORKSTREAM-09 | FACT |
| RISK-11 | Capability matrix overpromises support. | User launches unsupported backends. | medium | high | Mark conditional and verify. | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| RISK-12 | Tier 3 consumes disproportionate effort. | Schedule/resource drag. | medium | medium | Treat as separate retro toolchain track. | WORKSTREAM-15 | INFERENCE |
| RISK-13 | Scripts fail on old shells/CMD. | Entrypoints unusable. | medium | medium | Test per tier and simplify scripts. | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| RISK-14 | Quick load/save semantics in multiplayer cause desync. | Authority/desync issue. | low | high | Disable or route through server/admin. | WORKSTREAM-14 | FACT |
| RISK-15 | Docs diverge from code. | Future confusion. | medium | high | Update docs and code together. | WORKSTREAM-19 | FACT |
| RISK-16 | Over-compressing handoff loses rejected options. | Future assistant repeats old work. | medium | medium | Use registers and stable IDs. | WORKSTREAM-20 | FACT |
| RISK-17 | External platform/library facts stale. | Incorrect support promises. | high | high | Verify before publication. | WORKSTREAM-15, WORKSTREAM-16 | FACT |
| RISK-18 | Using hidden reasoning rather than visible rationale in handoff. | Unusable/unsafe provenance. | low | medium | Only include visible rationale. | WORKSTREAM-20 | FACT |

### Verification Queue

| ID | Item | Why | Source/type | Priority | Related | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Linux kernel 3.2 + modern toolchain/glibc baseline. | Kernel-only support claim may be insufficient. | Linux distro/toolchain docs and build tests. | High | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Linux kernel 2.6.18 + libc/toolchain feasibility. | Tier 2 support depends on old ABI. | RHEL5/Debian/Ubuntu docs and test builds. | High | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Linux kernel 2.4 feasibility. | Tier 3 very old. | Toolchain, libc, X11, SDL1 docs/tests. | High | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Distro mappings for Tier 1. | Assistant-proposed distro mappings may be stale. | Distro release/kernel/glibc records. | Medium | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Distro mappings for Tier 2. | Assistant-proposed distro mappings may be stale. | Distro release/kernel/glibc records. | Medium | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Distro mappings for Tier 3. | Very old distro data uncertain. | Distro archives/docs. | Medium | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | DX9.0c support on Windows 98SE-Me and NT 2000+. | Renderer matrix depends on API/runtime reality. | Microsoft DirectX docs/tests. | High | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | DX11 OS/runtime minimum. | Must not expose on unsupported NT 2000/XP systems. | Microsoft DirectX docs/tests. | High | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Vulkan VK1 availability on Windows/Linux/macOS. | Runtime driver/API support varies. | Vulkan loader/driver/MoltenVK docs/tests. | High | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | MoltenVK support across macOS tiers. | macOS VK1 depends on translation layer. | MoltenVK docs/license/deployment tests. | High | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | OpenGL 1.1 and GL2 support by OS/tier. | Renderer matrix depends on this. | Apple/Microsoft/Mesa/vendor docs/tests. | High | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Classic Mac OS 8.5/9.x graphics/toolchain feasibility. | Tier 2/3 Mac support. | CodeWarrior/Carbon/QuickDraw/OpenGL docs/tests. | High | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | SDL1 and SDL2 support on legacy Windows/Mac/Linux. | Platform matrix depends on this. | SDL docs/source compatibility/tests. | High | WORKSTREAM-07, WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Wayland support availability by Linux tier. | Wayland is modern; older tiers likely X11 only. | Wayland release/docs. | Medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | Windows NT 2000 SP4 to latest toolchain/runtime feasibility. | All tiers include NT 2000+. | Compiler/CRT/Win32 API docs/tests. | High | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-16 | Shell script portability on old POSIX systems. | readlink and shell features may differ. | POSIX shell tests on target systems. | Medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-17 | Windows CMD script parsing on supported Windows versions. | Batch parser differs across versions. | Windows test matrix. | Medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-18 | Actual CMake target/library names. | Prompt names may not match repo. | Inspect repo CMake. | High | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-19 | Existing input system and render API. | Avoid duplicate systems. | Inspect repo. | High | WORKSTREAM-14, WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-20 | Uploaded launcher file summaries. | Prior summary unverified. | Inspect files directly. | High | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |

## 6. Possible Cross-Chat Duplicates

- Deterministic engine constraints.
- Repository layout and build contract.
- Platform/render backend naming.
- Modding and data format constraints.
- Input/keybindings.
- Renderer/camera architecture.
- Support tier discussions.

## 7. Possible Cross-Chat Conflicts

- Other chats may still use `vector_soft` as public renderer.
- Other chats may include DX12 as final.
- Other chats may treat X11/Wayland as explicit platform values.
- Other chats may use `dom-launcher` instead of `dominium`.
- Other chats may define different platform support tiers.

## 8. Spec Book Integration Guidance

Feed this chat into Launcher Architecture, Platform/Renderer Backends, Software Renderer, Camera/View System, Entry Scripts, Input/Controls, Platform Support Tiers, Capability Matrix, Build/Test, and Handoff sections. Make launcher process-spawning, C89 backend/C++98 frontend split, universal software renderer, final support tiers, and script names formal requirements. Keep external compatibility claims as verification items. Do not merge DX12 or X11/Wayland taxonomy prematurely.

## 9. Aggregator Warnings

Do not treat prior file summaries as verified. Do not treat generated Codex prompts as applied. Do not erase changes of direction. Do not convert external compatibility claims into hard facts until verified. Do not assume later chats agree with this chat’s final tier table without checking provenance.
