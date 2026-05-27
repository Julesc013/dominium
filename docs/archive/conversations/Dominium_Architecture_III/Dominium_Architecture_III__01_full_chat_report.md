# Full Chat Report — Dominium Architecture III

## 0. Report Metadata

| Field | Assessment |
| --- | --- |
| Chat label | Dominium Architecture III |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This visible chat only, plus the previously generated Context Transfer Packet and OC-1 inventory in this chat. Uploaded file contents are not treated as verified unless explicitly inspected later. |
| Apparent coverage | Full visible chat appears available; uploaded file contents are only known through file names and prior unverified assistant summaries. |
| Extraction confidence | 4/5 |
| Staleness risk | Medium-High for external OS/library/toolchain claims; low for internal user decisions. |
| Future plans present | Yes |
| Pending tasks present | Yes |
| Artifacts/files present | Yes |
| Safe for aggregation | Yes, with caveats about unverified uploaded files and external compatibility claims. |
| Main limitations | Repo archive not inspected; uploaded launcher file summaries unverified; Codex prompts not confirmed applied; platform compatibility claims require verification. |

## 1. Executive Summary

This chat, labelled **Dominium Architecture III**, focused on Dominium’s launcher, platform/render backend strategy, scripts, input bindings, support tiers, and handoff packaging. The user supplied the standing Dominium project contract: deterministic fixed-step simulation, strict C89/C++98-era constraints, no floats in `/engine/core` or `/engine/sim`, fixed tick phase ordering, deterministic serialization, renderer/audio/UI never mutating simulation, OS boundaries isolated under `/engine/platform`, and explicit CMake sources with no network fetches. Those constraints remain binding for every future implementation decision in this chat.

The central workstream was the **launcher**. The user first described a launcher UI with tabs **News, Changes, Mods, Instances, Accounts, Settings** and bottom selectors for account, instance, platform, renderer, graphical/headless, and client/server. The architecture then evolved: the launcher is not an in-process mode switcher; selected launcher settings execute separate client or server binaries. The launcher backend/core must be C89, while frontend code for each binary may use C++98. Client/server binaries may be single-system builds, with the launcher and scripts selecting the correct executable. The current desired launcher architecture is system-agnostic and modular: a C89 core for configuration, capabilities, state, view model, and launch-plan creation; platform-specific process adapters; and multiple frontend skins such as engine-rendered software UI, native Win32, CLI, or TUI.

The user also finalized user-facing entrypoints. The current primary commands are **`dominium`** to launch the launcher, **`setup`** to launch installer/repair/uninstaller, **`dom-client`** to dispatch a client binary, and **`dom-server`** to dispatch a server binary. Earlier names such as `dom-launcher` and `dom-setup` were superseded or relegated to possible aliases.

The render/platform plan changed significantly. Earlier `vector_soft` and minimal/full backend splits were superseded. The user explicitly removed minimal/full duplicate implementations and requested one full implementation per backend. The public renderer fallback is now **`software`**, not `vector_soft`: it must work on all platforms and support both vector primitives and textured graphics. Every renderer should support vector-only and full graphics modes, so the user can instantly toggle CAD-style vector views, full graphics views, missing-asset fallback, and performance modes. The latest renderer list from the user is **DX9.0c, DX11, GL1.1, GL2, VK1, software**. DX12 was discussed earlier but omitted from the latest list, so it is unresolved/deferred unless the user confirms it. The latest platform categories are **POSIX, SDL1, SDL2, Native**; earlier X11 and Wayland were discussed, so their final placement under Native or as explicit values remains unresolved.

The client/render view model also expanded. The user wants instant seamless zoom to any scale, instant switching between top-down 2D and first-person 3D, vector or graphics mode for each view, and arbitrary cameras for free cam, map viewing, content creation, custom HUD cameras, overlays, new windows, and in-game CCTV. These are client/render concerns and must not enter deterministic sim state.

The user finalized platform support tiers. Tier 1 targets Windows NT 2000 SP4 to latest, Mac OS X 10.6 to 10.14, and Linux 3.2 to current. Tier 2 adds Windows 98 SE to Me, Mac OS 9 to 9.2, Mac OS X 10.6 to 15.0, and Linux 2.6.18 to current while still including Windows NT 2000 SP4 to latest. Tier 3 adds MS-DOS 3.3 to 6.2, Windows 3, Windows 95 to Me, Mac OS 8.5 to 9.2, Mac OS X 10.0 to latest, and Linux 2.4 to current. These are user decisions, but external feasibility and library support require verification.

Files uploaded in this chat include `/mnt/data/dominium.7z`, `/mnt/data/dom_launcher_view.c`, `/mnt/data/dom_launcher_view.h`, `/mnt/data/CMakeLists.txt`, and `/mnt/data/dom_launcher_main.c`. The prior assistant summarized the launcher files as mixing an engine-rendered view with a native Win32 launcher, but that summary must be treated as **UNCERTAIN / UNVERIFIED** until the files are inspected. The highest-priority next work is to inspect actual files, resolve platform taxonomy and DX12 status, update documentation, and implement launcher core/model/viewmodel, scripts, software renderer, and capability filtering in small verifiable steps.

## 2. How to Use This Report

This report covers only the retired chat labelled **Dominium Architecture III**. It is not a whole-project summary. It should be used as one per-chat source packet for later master aggregation.

Use the following hierarchy:

1. Direct user statements in this chat outrank assistant suggestions.
2. Later user statements supersede earlier brainstorms unless explicitly marked otherwise.
3. Assistant-generated prompts and code suggestions are artifacts, not proof of implementation.
4. Uploaded file names are facts; file contents must be re-inspected before code changes.
5. External-world compatibility claims are stale until verified.

Labels used:

- **FACT:** Explicitly stated in this chat or directly visible from uploaded file metadata/visible context.
- **INFERENCE:** Reasonably inferred from visible chat but not directly stated.
- **UNCERTAIN / UNVERIFIED:** Unclear, incomplete, stale, contradicted, or dependent on file/external verification.
- **PROJECT-CONTEXT:** From visible Project/user context rather than this chat’s direct dialogue.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Area | Explicit/Inferred | Strength | Implication | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Concise but complete responses. | tone/length | explicit | strong | Avoid fluff but preserve actionable detail. | High | FACT |
| PREF-02 | Cite paths in coding/design work. | coding/evidence | explicit | strong | Use file paths and concrete repo locations. | High | FACT |
| PREF-03 | Propose concrete next steps. | planning | explicit | strong | End architecture with implementation steps when appropriate. | High | FACT |
| PREF-04 | Ask clarification only when blocking. | planning | explicit | strong | Proceed with best-effort when possible. | High | FACT |
| PREF-05 | Prefer Codex-ready prompts when asked. | coding workflow | explicit | strong | Generate complete implementation prompts. | High | FACT |
| PREF-06 | Design for system-agnostic portability and modular extensibility. | architecture | explicit | strong | Separate core from frontends/adapters. | High | FACT |
| PREF-07 | Preserve uncertainty labels in handoffs. | handoff | explicit | strong | Use FACT/INFERENCE/UNCERTAIN. | High | FACT |
| PREF-08 | Do not invent or silently infer. | reasoning | explicit | strong | Mark assumptions and unknowns. | High | FACT |
| PREF-09 | Preserve rejected and superseded options. | handoff | explicit | strong | Keep history and rationale. | High | FACT |
| PREF-10 | Use tables for support/capability matrices. | formatting | explicit | strong | Matrix-style docs are preferred. | High | FACT |
| PREF-11 | Produce downloadable/shareable files when asked. | artifact | explicit | strong | Create Markdown/YAML/ZIP package. | High | FACT |

### 3.2 Inferred Preferences

No major inferred-only preferences were required beyond explicit instructions.

### 3.3 Preferences Not Established by This Chat

- **UNCERTAIN / UNVERIFIED:** Exact preferred config file format for launcher settings.
- **UNCERTAIN / UNVERIFIED:** Whether the user wants `dom-launcher` and `dom-setup` retained as aliases.
- **UNCERTAIN / UNVERIFIED:** Whether DX12 should remain in scope.

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Deterministic Dominium core and repository contract | Preserve the deterministic fixed-step simulation model and repo layering while launcher/platform/render work proceeds. | Project contract was explicitly supplied by the user in the chat: C89/C++98-era constraints, deterministic tick model, strict directories, no floats in core/sim, stable serialization. | All new launcher/render/platform/input code obeys deterministic and layering rules. | active | P0 | High | FACT |
| WORKSTREAM-02 | System-agnostic launcher architecture | Design the launcher as portable, modular, extensible C89 core logic plus thin frontends. | Architecture designed conceptually; implementation is not confirmed. | A C89 launch core/model/config/capability/launch-plan layer, platform process adapters, and multiple frontend skins over a shared view model. | active | P0 | High | FACT |
| WORKSTREAM-03 | Launcher backend/frontend language split | Keep backend launcher logic C89 and allow frontend code for each binary to use C++98. | Explicit user decision. | C89 backend compiles independently of OS/UI; C++98 max frontends handle platform-specific shells. | active | P0 | High | FACT |
| WORKSTREAM-04 | Launcher-to-client/server process execution | Launcher settings resolve to external client/server binary execution. | Explicit user decision. | A DomLaunchPlan-like structure resolves role, account, instance, platform, renderer, headless mode, executable, args, environment, and working directory. | active | P0 | High | FACT |
| WORKSTREAM-05 | Unified user-facing entrypoint scripts | Provide scripts/commands for dominium, setup, dom-client, and dom-server. | Script templates and CMake configure/install plans were generated, but implementation is unverified. | Consistent commands across OSes dispatch to correct launcher/setup/client/server binaries. | active | P0 | High | FACT |
| WORKSTREAM-06 | Setup / installer / repair / uninstaller wrapper | Implement setup entrypoint for install, repair, and uninstall modes. | Script behavior was specified; real setup binaries may not exist yet. | setup [install\|repair\|uninstall] calls dom_setup-* with --mode=<mode>. | active | P1 | High | FACT |
| WORKSTREAM-07 | Platform backend taxonomy and capability model | Normalize platform backend categories and encode allowed/conditional combinations. | Latest user categories are POSIX, SDL1, SDL2, Native. Earlier chat also discussed win32, macosx, X11, Wayland, and POSIX headless. | A single documented platform taxonomy used by CMake, launcher capabilities, scripts, and docs. | active | P0 | Medium | FACT / UNCERTAIN |
| WORKSTREAM-08 | Renderer backend taxonomy and capability model | Normalize render backends and expose vector/full graphics capability across all. | Latest user renderer list is DX9.0c, DX11, GL1.1, GL2, VK1, software. DX12 appeared earlier but was omitted later. | Renderer enum/docs/CMake/scripts use the final list and mark DX12 as deferred/unconfirmed unless the user confirms it. | active | P0 | Medium | FACT / UNCERTAIN |
| WORKSTREAM-09 | Universal all-platform software renderer | Replace vector_soft with one software renderer capable of vector and textured graphics on all platforms. | User-finalized design goal; implementation unverified. | engine/render/software supports vector-only mode, full graphics mode, textured primitives, missing-texture placeholders, and platform present callbacks. | active | P0 | High | FACT |
| WORKSTREAM-10 | Vector/full graphics render modes | Every renderer supports vector-only and graphics modes. | Design accepted; not confirmed implemented. | Runtime view/render mode can switch between CAD/vector and full textured graphics without backend replacement. | active | P0 | High | FACT |
| WORKSTREAM-11 | Instant zoom and 2D/3D view switching | Support seamless zoom at any scale and instant switching between top-down 2D and first-person 3D, each in vector or graphics. | Architecture designed conceptually; implementation unverified. | View type and mode are runtime view state; command generation changes without renderer reinitialization. | active | P1 | High | FACT |
| WORKSTREAM-12 | Arbitrary cameras, multi-view, overlays, and offscreen targets | Support free cam, maps, HUD cameras, CCTV, content creation cameras, overlays, windows, and offscreen views. | Architecture proposed with camera/view/target registries. | Render core supports arbitrary camera IDs, view IDs, target IDs, and per-frame view instances. | active | P1 | High | FACT |
| WORKSTREAM-13 | Launcher UI tabs and bottom selectors | Define launcher UI structure. | User specified UI; uploaded code may differ. | Tabs: News, Changes, Mods, Instances, Accounts, Settings. Bottom: Account, Instance, Platform, Renderer, Graphical/Headless, Client/Server. | active | P1 | High | FACT |
| WORKSTREAM-14 | Input and keybinding specification | Document and implement canonical F1–F12 and core controls. | F-key map and Codex prompt generated; implementation unverified. | docs/SPEC_INPUT.md, default_bindings.json, action enum, and mapping layer consistent with launcher/game contexts. | active | P1 | High | FACT |
| WORKSTREAM-15 | Platform support tiers | Formalize Tier 1/2/3 OS support ranges. | User finalized tier ranges. | Docs, build tooling, and capability matrix reflect final support tiers, with feasibility verified. | active | P0 | High for user decision; Medium for feasibility | FACT |
| WORKSTREAM-16 | Capability matrix | Map supported and conditional platform/renderer combinations per OS/tier. | Draft matrix generated; external facts and taxonomy require verification. | Launcher filters invalid choices through static support matrix plus runtime probes. | active | P0 | Medium | FACT / UNCERTAIN |
| WORKSTREAM-17 | Launcher build/test flow | Build and test launcher binaries and scripts. | Build/test plan and Codex prompt generated. | CMake targets, scripts, setup stubs, direct/script smoke tests, spawn dry-run tests. | active | P1 | High | FACT |
| WORKSTREAM-18 | Uploaded launcher code refactor | Reconcile uploaded launcher code with intended architecture. | Files uploaded; prior assistant summary says native Win32 launcher and engine-rendered view are mixed; exact contents unverified. | Engine-based launcher canonical, Win32 native launcher as separate frontend/tool if retained. | active | P0 | Medium | FACT / UNCERTAIN |
| WORKSTREAM-19 | Documentation and Codex implementation prompts | Generate prompts and docs updates for implementation. | Multiple prompts generated, but not confirmed applied. | Use consolidated final decisions to update docs/code, not stale prompt fragments. | historical/active artifact | P1 | High | FACT |
| WORKSTREAM-20 | Chat handoff and report packaging | Produce downloadable per-chat report package for future aggregation. | This file package is being created from prior CTP and visible chat. | Markdown/YAML/ZIP package preserving state with labels and stable IDs. | active | P0 | High | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — Deterministic Dominium core and repository contract
- **Label:** FACT
- **Objective:** Preserve the deterministic fixed-step simulation model and repo layering while launcher/platform/render work proceeds.
- **Background:** Based on user-provided summaries of docs/DIRECTORY_CONTEXT.md, docs/SPEC_CORE.md, docs/DATA_FORMATS.md, docs/BUILDING.md, and docs/dev/dominium_new_root.txt.
- **Current state:** Project contract was explicitly supplied by the user in the chat: C89/C++98-era constraints, deterministic tick model, strict directories, no floats in core/sim, stable serialization.
- **Desired end state:** All new launcher/render/platform/input code obeys deterministic and layering rules.
- **Importance:** This is the non-negotiable base that prevents sim nondeterminism and architecture drift.
- **Decisions made:** DECISION-01: Dominium deterministic core and layering contract remains binding.
- **Decisions pending:** None recorded.
- **Pending tasks:** None specifically linked.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** No explicit blocker recorded.
- **Risks:** No specific risk linked; global risks apply.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P0
### WORKSTREAM-02 — System-agnostic launcher architecture
- **Label:** FACT
- **Objective:** Design the launcher as portable, modular, extensible C89 core logic plus thin frontends.
- **Background:** User asked how to design the launcher from the ground up to be system agnostic, portable, modular, and extensible.
- **Current state:** Architecture designed conceptually; implementation is not confirmed.
- **Desired end state:** A C89 launch core/model/config/capability/launch-plan layer, platform process adapters, and multiple frontend skins over a shared view model.
- **Importance:** Prevents Win32-native UI or any one frontend from owning launch logic.
- **Decisions made:** None specifically linked beyond global project decisions.
- **Decisions pending:** QUESTION-14: What launcher config file format should be used?
- **Pending tasks:** TASK-07: Implement launcher C89 core types/config/caps/launch plan., TASK-08: Implement launcher state and viewmodel.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** QUESTION-14: What launcher config file format should be used?
- **Risks:** RISK-08: Leaking OS APIs into launcher core.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P0
### WORKSTREAM-03 — Launcher backend/frontend language split
- **Label:** FACT
- **Objective:** Keep backend launcher logic C89 and allow frontend code for each binary to use C++98.
- **Background:** User stated: “The backend launcher code should use C89, the front end code for each binary can use C++98.”
- **Current state:** Explicit user decision.
- **Desired end state:** C89 backend compiles independently of OS/UI; C++98 max frontends handle platform-specific shells.
- **Importance:** Supports portability across legacy and modern systems.
- **Decisions made:** DECISION-03: Launcher backend/core must use C89., DECISION-04: Launcher frontends may use C++98.
- **Decisions pending:** None recorded.
- **Pending tasks:** None specifically linked.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** No explicit blocker recorded.
- **Risks:** No specific risk linked; global risks apply.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P0
### WORKSTREAM-04 — Launcher-to-client/server process execution
- **Label:** FACT
- **Objective:** Launcher settings resolve to external client/server binary execution.
- **Background:** User clarified that settings selected in the launcher will be used to execute client or server binaries.
- **Current state:** Explicit user decision.
- **Desired end state:** A DomLaunchPlan-like structure resolves role, account, instance, platform, renderer, headless mode, executable, args, environment, and working directory.
- **Importance:** Avoids in-process platform/render/client/server switching.
- **Decisions made:** DECISION-02: Launcher settings execute separate client/server binaries., DECISION-05: Client/server binaries can be single-system builds.
- **Decisions pending:** QUESTION-12: Will retro systems run servers?
- **Pending tasks:** TASK-09: Implement platform process spawn API.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** QUESTION-12: Will retro systems run servers?
- **Risks:** No specific risk linked; global risks apply.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P0
### WORKSTREAM-05 — Unified user-facing entrypoint scripts
- **Label:** FACT
- **Objective:** Provide scripts/commands for dominium, setup, dom-client, and dom-server.
- **Background:** User asked for unified scripts, later specifically adding “setup” and “dominium”.
- **Current state:** Script templates and CMake configure/install plans were generated, but implementation is unverified.
- **Desired end state:** Consistent commands across OSes dispatch to correct launcher/setup/client/server binaries.
- **Importance:** Gives users stable command names despite multiple backend-specific binaries.
- **Decisions made:** DECISION-05: Client/server binaries can be single-system builds., DECISION-06: Use unified entrypoints for launcher/client/server/setup., DECISION-07: Use dominium as the main launcher command.
- **Decisions pending:** QUESTION-15: Should dom-launcher/dom-setup remain aliases?
- **Pending tasks:** TASK-17: Add packaging scripts., TASK-18: Add CMake configure/install rules for scripts.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** QUESTION-15: Should dom-launcher/dom-setup remain aliases?
- **Risks:** RISK-13: Scripts fail on old shells/CMD.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P0
### WORKSTREAM-06 — Setup / installer / repair / uninstaller wrapper
- **Label:** FACT
- **Objective:** Implement setup entrypoint for install, repair, and uninstall modes.
- **Background:** User requested “setup” to launch installer/repair/uninstaller.
- **Current state:** Script behavior was specified; real setup binaries may not exist yet.
- **Desired end state:** setup [install|repair|uninstall] calls dom_setup-* with --mode=<mode>.
- **Importance:** Completes packaging lifecycle commands.
- **Decisions made:** DECISION-08: Use setup as installer/repair/uninstaller command., DECISION-23: Setup binaries may be stubs initially if real installer is absent.
- **Decisions pending:** QUESTION-16: What installer technology should setup wrap?
- **Pending tasks:** TASK-19: Add setup binaries or stubs.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Important but can follow P0 blockers
- **Blockers:** QUESTION-16: What installer technology should setup wrap?
- **Risks:** No specific risk linked; global risks apply.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P1
### WORKSTREAM-07 — Platform backend taxonomy and capability model
- **Label:** FACT / UNCERTAIN
- **Objective:** Normalize platform backend categories and encode allowed/conditional combinations.
- **Background:** User requested a capability matrix and said to remember POSIX, SDL1, SDL2, and native.
- **Current state:** Latest user categories are POSIX, SDL1, SDL2, Native. Earlier chat also discussed win32, macosx, X11, Wayland, and POSIX headless.
- **Desired end state:** A single documented platform taxonomy used by CMake, launcher capabilities, scripts, and docs.
- **Importance:** Ambiguity here blocks clean binary naming and launcher filtering.
- **Decisions made:** DECISION-09: Remove minimal/full backend split and use full single implementations., DECISION-20: Latest platform implementation categories are POSIX, SDL1, SDL2, and Native.
- **Decisions pending:** QUESTION-02: Are X11 and Wayland explicit platforms or Native Linux subtypes?, QUESTION-03: Is POSIX headless-only?, QUESTION-04: What exactly is Native per OS/tier?
- **Pending tasks:** TASK-02: Resolve final platform taxonomy.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** QUESTION-02: Are X11 and Wayland explicit platforms or Native Linux subtypes?, QUESTION-03: Is POSIX headless-only?, QUESTION-04: What exactly is Native per OS/tier?
- **Risks:** RISK-04: Ignoring X11/Wayland taxonomy ambiguity.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Inspect repo/files and resolve blockers.
- **Verification needed:** Yes, especially external compatibility and uploaded code state.
- **Confidence:** Medium
- **Carry-forward priority:** P0
### WORKSTREAM-08 — Renderer backend taxonomy and capability model
- **Label:** FACT / UNCERTAIN
- **Objective:** Normalize render backends and expose vector/full graphics capability across all.
- **Background:** User requested capability matrix with these renderers.
- **Current state:** Latest user renderer list is DX9.0c, DX11, GL1.1, GL2, VK1, software. DX12 appeared earlier but was omitted later.
- **Desired end state:** Renderer enum/docs/CMake/scripts use the final list and mark DX12 as deferred/unconfirmed unless the user confirms it.
- **Importance:** Renderer list drives binaries, scripts, docs, and fallback behavior.
- **Decisions made:** DECISION-19: Latest renderer implementation set is DX9.0c, DX11, GL1.1, GL2, VK1, and software., DECISION-24: DX12 is unresolved/deferred, not confirmed current scope.
- **Decisions pending:** QUESTION-01: Is DX12 in scope now, deferred, or dropped?
- **Pending tasks:** TASK-03: Resolve DX12 status.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** QUESTION-01: Is DX12 in scope now, deferred, or dropped?
- **Risks:** RISK-03: Including DX12 without confirmation.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Inspect repo/files and resolve blockers.
- **Verification needed:** Yes, especially external compatibility and uploaded code state.
- **Confidence:** Medium
- **Carry-forward priority:** P0
### WORKSTREAM-09 — Universal all-platform software renderer
- **Label:** FACT
- **Objective:** Replace vector_soft with one software renderer capable of vector and textured graphics on all platforms.
- **Background:** User explicitly asked to replace vector_soft with software renderer capable of vector and graphics using texture files.
- **Current state:** User-finalized design goal; implementation unverified.
- **Desired end state:** engine/render/software supports vector-only mode, full graphics mode, textured primitives, missing-texture placeholders, and platform present callbacks.
- **Importance:** Universal fallback for launchers, old systems, missing assets, and no working GPU backend.
- **Decisions made:** DECISION-10: Replace vector_soft with a universal software renderer., DECISION-12: Software renderer must work on all platforms.
- **Decisions pending:** None recorded.
- **Pending tasks:** TASK-13: Implement universal software renderer., TASK-14: Implement shared draw command core.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** No explicit blocker recorded.
- **Risks:** RISK-02: Resurrecting vector_soft as public renderer., RISK-10: Software renderer delayed.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P0
### WORKSTREAM-10 — Vector/full graphics render modes
- **Label:** FACT
- **Objective:** Every renderer supports vector-only and graphics modes.
- **Background:** User wanted vector and graphics modes on all renderers and missing-file fallback.
- **Current state:** Design accepted; not confirmed implemented.
- **Desired end state:** Runtime view/render mode can switch between CAD/vector and full textured graphics without backend replacement.
- **Importance:** Enables CAD-style viewing and performance/missing asset modes.
- **Decisions made:** DECISION-11: All renderers must support vector-only and graphics modes.
- **Decisions pending:** None recorded.
- **Pending tasks:** TASK-14: Implement shared draw command core., TASK-15: Add vector/full render mode to API and backends.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** No explicit blocker recorded.
- **Risks:** No specific risk linked; global risks apply.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P0
### WORKSTREAM-11 — Instant zoom and 2D/3D view switching
- **Label:** FACT
- **Objective:** Support seamless zoom at any scale and instant switching between top-down 2D and first-person 3D, each in vector or graphics.
- **Background:** User explicitly requested instant zoom, vector/graphics toggle, and 2D/3D switching.
- **Current state:** Architecture designed conceptually; implementation unverified.
- **Desired end state:** View type and mode are runtime view state; command generation changes without renderer reinitialization.
- **Importance:** Core UX requirement for CAD-style city/sim views and first-person immersion.
- **Decisions made:** DECISION-13: Support instant seamless zoom to any scale., DECISION-14: Support instant switching between top-down 2D and first-person 3D.
- **Decisions pending:** QUESTION-13: Is visual replay determinism required?
- **Pending tasks:** TASK-16: Implement camera/view/target registries.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Important but can follow P0 blockers
- **Blockers:** QUESTION-13: Is visual replay determinism required?
- **Risks:** RISK-09: Camera/view/render state mutating sim.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P1
### WORKSTREAM-12 — Arbitrary cameras, multi-view, overlays, and offscreen targets
- **Label:** FACT
- **Objective:** Support free cam, maps, HUD cameras, CCTV, content creation cameras, overlays, windows, and offscreen views.
- **Background:** User explicitly requested arbitrary cameras for multiple use cases.
- **Current state:** Architecture proposed with camera/view/target registries.
- **Desired end state:** Render core supports arbitrary camera IDs, view IDs, target IDs, and per-frame view instances.
- **Importance:** Enables tools, surveillance gameplay, mini-maps, and flexible UI.
- **Decisions made:** DECISION-15: Support arbitrary cameras for free cam, map, HUD, CCTV, content creation, windows, overlays.
- **Decisions pending:** None recorded.
- **Pending tasks:** TASK-16: Implement camera/view/target registries.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Important but can follow P0 blockers
- **Blockers:** No explicit blocker recorded.
- **Risks:** RISK-09: Camera/view/render state mutating sim.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P1
### WORKSTREAM-13 — Launcher UI tabs and bottom selectors
- **Label:** FACT
- **Objective:** Define launcher UI structure.
- **Background:** User’s first launcher-specific request.
- **Current state:** User specified UI; uploaded code may differ.
- **Desired end state:** Tabs: News, Changes, Mods, Instances, Accounts, Settings. Bottom: Account, Instance, Platform, Renderer, Graphical/Headless, Client/Server.
- **Importance:** Defines viewmodel and frontend expectations.
- **Decisions made:** None specifically linked beyond global project decisions.
- **Decisions pending:** None recorded.
- **Pending tasks:** TASK-08: Implement launcher state and viewmodel.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Important but can follow P0 blockers
- **Blockers:** No explicit blocker recorded.
- **Risks:** No specific risk linked; global risks apply.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P1
### WORKSTREAM-14 — Input and keybinding specification
- **Label:** FACT
- **Objective:** Document and implement canonical F1–F12 and core controls.
- **Background:** User asked what keybindings should be and then asked for Codex prompt.
- **Current state:** F-key map and Codex prompt generated; implementation unverified.
- **Desired end state:** docs/SPEC_INPUT.md, default_bindings.json, action enum, and mapping layer consistent with launcher/game contexts.
- **Importance:** Prevents future input conflicts and stabilizes UX.
- **Decisions made:** DECISION-21: F1-F12 keybinding map is accepted enough to generate implementation prompt.
- **Decisions pending:** None recorded.
- **Pending tasks:** TASK-20: Add input spec/default bindings/action enum., TASK-21: Extend or create input mapping layer.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Important but can follow P0 blockers
- **Blockers:** No explicit blocker recorded.
- **Risks:** RISK-14: Quick load/save semantics in multiplayer cause desync.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P1
### WORKSTREAM-15 — Platform support tiers
- **Label:** FACT
- **Objective:** Formalize Tier 1/2/3 OS support ranges.
- **Background:** User asked for Linux tiers, then finalized all OS tiers.
- **Current state:** User finalized tier ranges.
- **Desired end state:** Docs, build tooling, and capability matrix reflect final support tiers, with feasibility verified.
- **Importance:** Determines support policy, toolchains, renderer/platform gating.
- **Decisions made:** DECISION-16: Use final Tier 1 support: Windows NT 2000 SP4-latest, Mac OS X 10.6-10.14, Linux 3.2-current., DECISION-17: Use final Tier 2 support: Win98SE-Me, NT 2000 SP4-latest, Mac OS 9-9.2, Mac OS X 10.6-15.0, Linux 2.6.18-current., DECISION-18: Use final Tier 3 support: MS-DOS 3.3-6.2, Windows 3, Windows 95-Me, NT 2000 SP4-latest, Mac OS 8.5-9.2, Mac OS X 10.0-latest, Linux 2.4-current.
- **Decisions pending:** QUESTION-07: What libc/libstdc++ baselines accompany Linux kernel tiers?, QUESTION-09: How feasible are Mac OS 8.5/9.x targets?, QUESTION-10: How feasible is Mac OS X 10.0-latest support?, QUESTION-11: How to support Windows NT 2000 SP4-latest with modern toolchains?
- **Pending tasks:** TASK-05: Create docs/SPEC_PLATFORM_SUPPORT.md or equivalent., TASK-22: Verify Linux kernel/libc/toolchain/distro claims.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** QUESTION-07: What libc/libstdc++ baselines accompany Linux kernel tiers?, QUESTION-09: How feasible are Mac OS 8.5/9.x targets?, QUESTION-10: How feasible is Mac OS X 10.0-latest support?, QUESTION-11: How to support Windows NT 2000 SP4-latest with modern toolchains?
- **Risks:** RISK-12: Tier 3 consumes disproportionate effort., RISK-17: External platform/library facts stale.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Yes, especially external compatibility and uploaded code state.
- **Confidence:** High for user decision; Medium for feasibility
- **Carry-forward priority:** P0
### WORKSTREAM-16 — Capability matrix
- **Label:** FACT / UNCERTAIN
- **Objective:** Map supported and conditional platform/renderer combinations per OS/tier.
- **Background:** User explicitly requested capability matrix.
- **Current state:** Draft matrix generated; external facts and taxonomy require verification.
- **Desired end state:** Launcher filters invalid choices through static support matrix plus runtime probes.
- **Importance:** Prevents invalid or misleading launch choices.
- **Decisions made:** DECISION-19: Latest renderer implementation set is DX9.0c, DX11, GL1.1, GL2, VK1, and software., DECISION-20: Latest platform implementation categories are POSIX, SDL1, SDL2, and Native.
- **Decisions pending:** QUESTION-08: Can SDL2 be supported on Win9x?
- **Pending tasks:** TASK-02: Resolve final platform taxonomy., TASK-06: Create/verify capability matrix data and docs., TASK-23: Verify DirectX/OpenGL/Vulkan/SDL/macOS/Mac OS support claims.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** QUESTION-08: Can SDL2 be supported on Win9x?
- **Risks:** RISK-11: Capability matrix overpromises support., RISK-17: External platform/library facts stale.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Yes, especially external compatibility and uploaded code state.
- **Confidence:** Medium
- **Carry-forward priority:** P0
### WORKSTREAM-17 — Launcher build/test flow
- **Label:** FACT
- **Objective:** Build and test launcher binaries and scripts.
- **Background:** User asked how to build and test launcher.
- **Current state:** Build/test plan and Codex prompt generated.
- **Desired end state:** CMake targets, scripts, setup stubs, direct/script smoke tests, spawn dry-run tests.
- **Importance:** Turns architecture into verifiable working targets.
- **Decisions made:** None specifically linked beyond global project decisions.
- **Decisions pending:** None recorded.
- **Pending tasks:** TASK-10: Refactor launcher CMake and targets., TASK-18: Add CMake configure/install rules for scripts., TASK-24: Smoke-test launcher/scripts.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Important but can follow P0 blockers
- **Blockers:** No explicit blocker recorded.
- **Risks:** No specific risk linked; global risks apply.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P1
### WORKSTREAM-18 — Uploaded launcher code refactor
- **Label:** FACT / UNCERTAIN
- **Objective:** Reconcile uploaded launcher code with intended architecture.
- **Background:** User uploaded dom_launcher_view.c/.h, CMakeLists.txt, dom_launcher_main.c.
- **Current state:** Files uploaded; prior assistant summary says native Win32 launcher and engine-rendered view are mixed; exact contents unverified.
- **Desired end state:** Engine-based launcher canonical, Win32 native launcher as separate frontend/tool if retained.
- **Importance:** Actual implementation must start from current files, not just design.
- **Decisions made:** DECISION-22: Uploaded native Win32 launcher should likely become a separate frontend/tool, not the cross-platform core.
- **Decisions pending:** QUESTION-05: What is the actual current repo state?, QUESTION-06: Are prior uploaded-file summaries accurate?
- **Pending tasks:** TASK-01: Inspect uploaded/repo files before implementation., TASK-10: Refactor launcher CMake and targets., TASK-11: Create engine-based launcher main., TASK-12: Preserve native Win32 launcher as separate target if desired.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** QUESTION-05: What is the actual current repo state?, QUESTION-06: Are prior uploaded-file summaries accurate?
- **Risks:** RISK-05: Assuming uploaded file summaries are accurate., RISK-07: Compiling Win32 native launcher on non-Windows.
- **Artifacts:** ARTIFACT-01: /mnt/data/dominium.7z, ARTIFACT-02: /mnt/data/dom_launcher_view.c, ARTIFACT-03: /mnt/data/dom_launcher_view.h, ARTIFACT-04: /mnt/data/CMakeLists.txt, ARTIFACT-05: /mnt/data/dom_launcher_main.c
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Inspect repo/files and resolve blockers.
- **Verification needed:** Yes, especially external compatibility and uploaded code state.
- **Confidence:** Medium
- **Carry-forward priority:** P0
### WORKSTREAM-19 — Documentation and Codex implementation prompts
- **Label:** FACT
- **Objective:** Generate prompts and docs updates for implementation.
- **Background:** User repeatedly asked for Codex-ready prompts.
- **Current state:** Multiple prompts generated, but not confirmed applied.
- **Desired end state:** Use consolidated final decisions to update docs/code, not stale prompt fragments.
- **Importance:** Prompts are useful artifacts but not implementation evidence.
- **Decisions made:** None specifically linked beyond global project decisions.
- **Decisions pending:** None recorded.
- **Pending tasks:** TASK-04: Update project docs with final launcher/platform/render/support/input decisions.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Important but can follow P0 blockers
- **Blockers:** No explicit blocker recorded.
- **Risks:** RISK-06: Assuming generated prompts were applied., RISK-15: Docs diverge from code.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P1
### WORKSTREAM-20 — Chat handoff and report packaging
- **Label:** FACT
- **Objective:** Produce downloadable per-chat report package for future aggregation.
- **Background:** User asked to finish job by creating final downloadable package.
- **Current state:** This file package is being created from prior CTP and visible chat.
- **Desired end state:** Markdown/YAML/ZIP package preserving state with labels and stable IDs.
- **Importance:** Enables future master Project Spec Book aggregation.
- **Decisions made:** None specifically linked beyond global project decisions.
- **Decisions pending:** None recorded.
- **Pending tasks:** TASK-25: Create final per-chat package files and ZIP.
- **Constraints:** Deterministic/layering constraints apply where relevant; see Constraint Register.
- **Dependencies:** Related decisions, artifacts, and tasks listed above; repository inspection where code is involved.
- **Timeline / sequencing:** Immediate / early
- **Blockers:** No explicit blocker recorded.
- **Risks:** RISK-01: Treating brainstorms or assistant suggestions as final user decisions., RISK-16: Over-compressing handoff loses rejected options., RISK-18: Using hidden reasoning rather than visible rationale in handoff.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Desired end state achieved without violating deterministic/layering constraints.
- **Recommended next action:** Use this report and registers to drive implementation or aggregation.
- **Verification needed:** Low; mostly internal user decision.
- **Confidence:** High
- **Carry-forward priority:** P0

## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | User supplied Dominium project identity and deterministic repo constraints. | Established baseline. | Everything must respect architecture. | Active | High |
| 02 | User uploaded dominium.7z. | Repo archive provided but not inspected. | Actual repo state remains unknown. | Needs verification | High |
| 03 | User asked for project explanation. | Assistant summarized architecture. | Contextual orientation. | Historical | High |
| 04 | User proposed tackling launcher with tabs and bottom selectors. | Launcher workstream began. | Defined UI concept. | Active | High |
| 05 | User clarified launcher settings execute binaries. | Separated launcher from client/server execution. | Major architecture decision. | Active | High |
| 06 | User required C89 backend and C++98 frontends. | Language split finalized. | Implementation constraint. | Active | High |
| 07 | Unified scripts discussed. | dom-launcher/dom-client/dom-server/dom-setup idea formed. | Later renamed partly. | Superseded/active | High |
| 08 | User explored minimum platform/render launchers and legacy OS families. | Initial minimal backend idea. | Later removed. | Superseded | High |
| 09 | User removed minimal/full split. | Single full implementation per backend. | Simplified backend architecture. | Active | High |
| 10 | User replaced vector_soft with universal software renderer. | Renderer direction changed. | Critical render decision. | Active | High |
| 11 | User requested instant zoom and vector/graphics toggle. | View-mode requirement added. | Render/view architecture. | Active | High |
| 12 | User requested 2D/3D switching. | View type requirement added. | Render/view architecture. | Active | High |
| 13 | User requested arbitrary cameras. | Camera/view/target architecture added. | Tools/gameplay UI potential. | Active | High |
| 14 | User asked platform/render binaries and scripts. | Matrix and script planning. | Packaging/build decisions. | Active | High |
| 15 | User added setup and dominium scripts. | Primary commands changed. | dominium/setup now primary. | Active | High |
| 16 | User requested Codex prompt for docs/implementation. | Prompt generated. | Implementation artifact. | Historical active | High |
| 17 | User asked build/test launcher plan. | Plan generated. | Implementation path. | Active | High |
| 18 | User asked keybindings and F1-F12. | Canonical keymap generated. | Input workstream. | Active | High |
| 19 | User requested Codex prompt for keybindings. | Prompt generated. | Implementation artifact. | Historical active | High |
| 20 | User uploaded launcher source files. | Implementation artifacts appeared. | Need inspect/refactor. | Active | High |
| 21 | Assistant summarized uploaded files and recommended refactor. | Potential current-state diagnosis. | Must verify. | Unverified | Medium |
| 22 | User asked ground-up modular design. | C89 core/model/viewmodel architecture proposed. | Launcher architecture refined. | Active | High |
| 23 | User asked Linux version tiers and distro mapping. | Assistant proposed Linux baselines. | External claims need verification. | Stale/verify | Medium |
| 24 | User finalized Tier 1/2/3 support lists. | Support tier decision finalized. | Docs/matrix. | Active | High |
| 25 | User requested capability matrix. | Draft platform/render matrix produced. | Needs verification. | Active | Medium |
| 26 | User requested OC-1 discovery. | OC-1 inventory generated. | Handoff process began. | Historical | High |
| 27 | User requested OC-2 registers. | OC-2 began but was superseded by final package request. | Registers integrated here. | Historical | High |
| 28 | User requested Context Transfer Packet. | CTP generated. | Basis for this package. | Historical active | High |
| 29 | User requested final downloadable report package. | This package created. | Final per-chat export. | Active | High |

## 7. Decisions

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
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

Highest-impact decisions: the launcher executes separate binaries; launcher core is C89 while frontends may be C++98; the old `vector_soft` concept is superseded by a universal software renderer; every renderer supports vector and full graphics; final support tiers are user-defined; final platform/render taxonomies still need limited cleanup around DX12 and X11/Wayland.

## 8. Pending Tasks and Next Actions

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
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

### 8.1 Recommended Task Order

1. Inspect uploaded/repo files: `dom_launcher_view.c`, `dom_launcher_view.h`, `CMakeLists.txt`, `dom_launcher_main.c`, and repo archive if possible.
2. Resolve platform taxonomy: POSIX / SDL1 / SDL2 / Native, including X11/Wayland placement.
3. Resolve DX12 status.
4. Update docs with final launcher, support tier, render/platform, script, and input decisions.
5. Implement launcher C89 core/model/viewmodel and process spawn API.
6. Implement universal software renderer and render mode support.
7. Add scripts and CMake targets, then smoke test.
8. Implement camera/view/target architecture and input mapping after core blockers are resolved.

### 8.2 Blocked Tasks

- Capability matrix implementation is blocked by platform taxonomy and external verification.
- Renderer enum finalization is blocked by DX12 status.
- Code refactor is blocked by direct file/repo inspection.

### 8.3 Quick Wins

- Add `docs/SPEC_PLATFORM_SUPPORT.md` with user-finalized tier table and verification caveats.
- Add `docs/SPEC_INPUT.md` with F1–F12 map.
- Add script templates under `packaging/scripts/` after confirming target names.

### 8.4 Tasks Requiring Verification

See Verification Queue, especially Linux/libc/toolchain baselines, SDL support, DirectX support, Vulkan/MoltenVK support, OpenGL support, and uploaded file contents.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
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

### 9.2 Soft Preferences

No major soft-only project requirements were established; most relevant items are hard constraints or explicit preferences.

### 9.3 Technical Constraints

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
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
| CONSTRAINT-13 | Software renderer must work on all platforms. | technical | hard | User decision | Universal fallback renderer. | Platform-specific software renderer dependency. | High | FACT |
| CONSTRAINT-14 | Every renderer supports vector and graphics modes. | technical | hard | User decision | Mode must be runtime-capable. | Backend only supports textured path. | High | FACT |
| CONSTRAINT-15 | Every platform should be capable of renderer or headless. | technical | hard | User decision | Platform init must support no-window/headless. | Headless server opening a window. | High | FACT |

### 9.4 Time / Resource Constraints

- **INFERENCE:** Tier 3 likely requires separate retro build/toolchain effort and may be resource-intensive. No explicit deadline was stated.

### 9.5 Legal / Ethical / Safety Constraints

- No specific legal or safety constraints beyond not misrepresenting unverified external compatibility claims.

### 9.6 Evidence / Citation Requirements

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-17 | Direct user statements outrank assistant suggestions. | handoff/evidence | hard | User current request | Do not promote unaccepted suggestions. | Treating assistant idea as user decision. | High | FACT |
| CONSTRAINT-18 | External facts require verification before future use. | evidence | hard | User current request | Mark OS/library claims stale. | Publishing unverified compatibility. | High | FACT |
| CONSTRAINT-19 | Preserve rejected/superseded options and contradictions. | handoff | hard | User current request | Record changes of direction. | Repeating rejected designs. | High | FACT |

### 9.7 Formatting / Output Requirements

- Stable IDs for registers.
- Markdown/YAML report package.
- Downloadable files/ZIP where tools allow.
- Labels on important items.

### 9.8 Things to Avoid

- Do not treat assistant suggestions as user decisions unless accepted.
- Do not assume generated prompts were applied.
- Do not assume uploaded file summaries are accurate.
- Do not resurrect rejected designs such as public `vector_soft` or in-process launcher switching.

## 10. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
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

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | In-process client/server switching from launcher. | rejected | User clarified launcher executes binaries. | final | Only reconsider if architecture changes. | WORKSTREAM-04 | FACT |
| REJECTED-02 | One universal all-system client/server binary. | deprioritised | User allowed single-system client/server binaries. | final for current plan | Reconsider if backend plugin architecture is desired. | WORKSTREAM-04 | FACT |
| REJECTED-03 | Minimal vs full backend split. | rejected | User said remove minimal versions and use full single implementation. | final | Reconsider only if legacy support requires special backend. | WORKSTREAM-07 | FACT |
| REJECTED-04 | Separate public vector_soft renderer. | superseded | User requested one software renderer. | final | Could survive only as internal implementation detail. | WORKSTREAM-09 | FACT |
| REJECTED-05 | Launcher requiring GPU renderer. | deprioritised | Launcher should use software fallback. | final | Optional future themed launcher only. | WORKSTREAM-09 | FACT |
| REJECTED-06 | Native Win32 launcher as cross-platform canonical launcher. | deprioritised | Win-only code cannot be cross-platform core. | tentative | Could be official Windows frontend if user chooses. | WORKSTREAM-18 | INFERENCE |
| REJECTED-07 | dom-launcher as primary command. | superseded | User later requested dominium. | likely final | Keep as alias if desired. | WORKSTREAM-05 | INFERENCE |
| REJECTED-08 | dom-setup as primary command. | superseded | User later requested setup. | likely final | Keep as alias if desired. | WORKSTREAM-05 | INFERENCE |
| REJECTED-09 | Linux kernel 2.0/libc5 baseline. | rejected/deprioritised | User chose Linux 2.4 for Tier 3. | final for current tiers | Special retro-port beyond Tier 3. | WORKSTREAM-15 | FACT |
| REJECTED-10 | Mac OS X 10.0 in Tier 1/2. | superseded | Final tiers place 10.0 only in Tier 3. | final | If user changes tiers. | WORKSTREAM-15 | FACT |
| REJECTED-11 | Treat generated Codex prompts as implemented. | rejected | No evidence of application. | final | Inspect repo to verify implementation. | WORKSTREAM-19 | FACT |
| REJECTED-12 | Treat external compatibility claims as verified. | rejected | User requires stale/current facts be marked for verification. | final | Verify with sources/tests. | WORKSTREAM-15, WORKSTREAM-16 | FACT |
| REJECTED-13 | Assume prior assistant uploaded-file summaries are exact. | rejected | Files need reinspection. | final | Inspect files. | WORKSTREAM-18 | FACT |

Preserving these prevents future assistants or aggregators from repeating earlier discarded designs, especially `vector_soft`, minimal/full backend duplication, in-process mode switching, and treating old command names as primary.

## 12. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
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

## 13. Rationale and Assumptions

Visible rationale:

- Launcher as a process spawner simplifies layering and avoids in-process backend/mode switching.
- C89 launcher core maximizes portability; C++98 frontends allow platform-specific UI shells.
- Unified scripts provide stable user-facing commands across many backend-specific binaries.
- Universal software renderer provides fallback on every platform and replaces fragmented vector-only backend design.
- Vector/full modes enable CAD-style viewing, missing asset fallback, and performance toggles.
- Camera/view/target abstractions support free cam, map views, overlays, HUD cameras, CCTV, content tools, and multi-window use without touching sim.
- Capability matrices prevent invalid platform/render selections.
- Tiered support separates primary modern support from extended legacy and retro/heritage support.

Assumptions needing care:

- Uploaded file summaries are not verified.
- External compatibility claims require verification.
- DX12 status is unresolved.
- X11/Wayland placement is unresolved.
- Scripts and CMake names may need adjustment to actual repo.

## 14. Risks and Failure Modes

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
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

## 15. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
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

## 16. Spec Book Contribution Notes

Likely future Spec Book chapters/sections:

- Deterministic Engine and Layering Contract.
- Launcher Architecture.
- Platform and Renderer Backend Model.
- Universal Software Renderer and Render Modes.
- Camera/View/Target System.
- Entrypoint Scripts and Packaging.
- Input and Keybindings.
- Platform Support Tiers.
- Capability Matrix.
- Build and Test Procedures.

Unique contributions from this chat:

- Final launcher process-spawner model.
- C89 backend / C++98 frontend split.
- `dominium` and `setup` command decisions.
- Replacement of `vector_soft` with universal `software` renderer.
- Final OS support tier ranges.
- Final latest renderer list excluding unresolved DX12.
- Camera/view flexibility requirements.

Possible duplicates with other chats:

- Deterministic core constraints.
- Directory layout.
- Serialization/data format rules.
- Build contract.
- Platform/render backend names.

Conflicts to watch:

- Any other chat that still treats `vector_soft` as public renderer.
- Any other chat that includes DX12 as confirmed.
- Any other chat that uses explicit X11/Wayland differently.
- Any other chat that uses `dom-launcher` instead of `dominium` as primary command.

Items needing user confirmation before formal spec:

- DX12 status.
- X11/Wayland/POSIX/Native taxonomy.
- Alias policy for old script names.
- Launcher config file format.
- Actual Tier 3 feasibility commitments.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Deterministic core constraints | constraint | All architecture depends on them. | Sim/layering violation. | FACT | High |
| 2 | Launcher executes separate binaries | decision | Defines launch architecture. | Wrong in-process design. | FACT | High |
| 3 | Launcher backend C89, frontends C++98 | decision/constraint | Defines code split. | Portability loss. | FACT | High |
| 4 | dominium/setup/dom-client/dom-server scripts | decision | User-facing command plan. | Wrong packaging UX. | FACT | High |
| 5 | Universal software renderer replaces vector_soft | decision | Renderer architecture. | Fragmented fallback. | FACT | High |
| 6 | Every renderer supports vector/full modes | decision | CAD/performance/fallback behavior. | Broken mode toggles. | FACT | High |
| 7 | Instant zoom, 2D/3D switching, arbitrary cameras | goal | Major render/view requirements. | Inadequate view architecture. | FACT | High |
| 8 | Final support tier table | decision | Product support policy. | Wrong support docs. | FACT | High |
| 9 | Latest renderer list and DX12 uncertainty | decision/open question | Scope correctness. | Wrong implementation scope. | FACT / UNCERTAIN | Medium |
| 10 | Platform taxonomy uncertainty | open question | Blocks clean matrix. | Ambiguous binaries. | UNCERTAIN / UNVERIFIED | Medium |
| 11 | Uploaded files require inspection | artifact/task | Actual code state unknown. | Bad refactor. | FACT / UNCERTAIN | High |
| 12 | Generated prompts are not implementation evidence | risk | Avoid assuming code changed. | False state. | FACT | High |
| 13 | F1-F12 keymap | decision/plan | Input UX. | Input conflict. | FACT | High |
| 14 | Capability matrix needs verification | task/open question | Launcher filtering. | Overpromised support. | UNCERTAIN / UNVERIFIED | High |
| 15 | Preserve rejected options | handoff rule | Avoid repeated work. | Old ideas resurrected. | FACT | High |

## 18. What Future Assistants Must Not Assume

- Do not assume DX12 is confirmed.
- Do not assume X11/Wayland are explicit final platform values.
- Do not assume POSIX means graphical unless clarified.
- Do not assume uploaded file summaries are correct.
- Do not assume the `.7z` repo was inspected.
- Do not assume any Codex prompt was applied.
- Do not assume support tiers are technically feasible without verification.
- Do not assume `dom-launcher` and `dom-setup` are primary commands.
- Do not assume visual replay determinism is required.
- Do not assume setup binaries exist.
- Do not assume input/render APIs do not already exist in the repo.

## 19. Recommended Next Action

If continuing this chat’s work alone:

1. Inspect actual uploaded/repo files.
2. Resolve platform taxonomy and DX12 status.
3. Patch docs with final tier/script/render/launcher decisions.
4. Implement launcher core/model/viewmodel and scripts in small verifiable steps.

If aggregating this chat with other chat reports:

1. Merge this chat’s final user decisions into master registers.
2. Mark platform/render taxonomy and DX12 as conflicts/open questions.
3. Preserve this chat’s support tier table as a user-finalized decision pending feasibility verification.
4. Do not overwrite later confirmed implementation details from other reports without provenance.

User verification needed before acting:

- Confirm DX12 status.
- Confirm X11/Wayland/POSIX/Native taxonomy.
- Confirm alias policy for `dom-launcher` and `dom-setup`.

## 20. Appendix: Possibly Relevant Details

### F1–F12 Map

| Key | Function | Label |
| --- | --- | --- |
| F1 | Help Overlay / Documentation | FACT |
| F2 | Screenshot / Frame Capture | FACT |
| F3 | Debug Overlay | FACT |
| F4 | View Mode Toggle | FACT |
| F5 | Quick Save | FACT |
| F6 | Quick Load | FACT |
| F7 | Replay / Time Controls | FACT |
| F8 | Mods / Tools / Editor Mode | FACT |
| F9 | World Map / Strategic View | FACT |
| F10 | Settings / System Menu | FACT |
| F11 | Fullscreen / UI-less Mode | FACT |
| F12 | Developer Console | FACT |

### Final Support Tier Table

| Tier | OS Family | Versions Supported | Label |
| --- | --- | --- | --- |
| Tier 1 | Windows NT | 2000 SP4 to latest | FACT |
| Tier 1 | Mac OS X | 10.6 to 10.14 | FACT |
| Tier 1 | Linux | 3.2 to current | FACT |
| Tier 2 | Windows 98 SE to Me | 98 SE to Me | FACT |
| Tier 2 | Windows NT | 2000 SP4 to latest | FACT |
| Tier 2 | Mac OS 9 | 9 to 9.2 | FACT |
| Tier 2 | Mac OS X | 10.6 to 15.0 | FACT |
| Tier 2 | Linux | 2.6.18 to current | FACT |
| Tier 3 | MS-DOS | 3.3 to 6.2 | FACT |
| Tier 3 | Windows 3 | Windows 3 | FACT |
| Tier 3 | Windows 95 to Me | 95 to Me | FACT |
| Tier 3 | Windows NT | 2000 SP4 to latest | FACT |
| Tier 3 | Mac OS | 8.5 to 9.2 | FACT |
| Tier 3 | Mac OS X | 10.0 to latest | FACT |
| Tier 3 | Linux | 2.4 to current | FACT |
