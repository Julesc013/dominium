# Aggregator Packet — Dominium Launcher Setup Architecture

## 1. Packet Metadata

- **Chat label:** Dominium Launcher Setup Architecture
- **Date anchor:** 2026-05-27 Australia/Melbourne
- **Source scope:** This visible chat only; no repo inspection.
- **Coverage:** Full for chat architecture and prompts; no implementation verification.
- **Confidence:** 4/5
- **Staleness risk:** Medium
- **Merge priority:** High for launcher/setup/runtime architecture; highest for latest dsys/dgfx launcher direction.
- **Main limitations:** JSON-vs-TLV unresolved; actual dsys/dgfx APIs unknown; earlier C++98 launcher prompts partly superseded.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat is a Dominium Game architecture chat focused on launcher, setup, runtime integration, modularity, and later a dsys/dgfx-based launcher implementation direction. The first anchor was the user’s architectural philosophy: one deterministic C89 engine core; narrow APIs; versioned file formats, preferably header/TLV; data-first mods with optional plugins; shared libraries for tools/launcher; and explicit migrations instead of silent breaking changes. The chat expanded that philosophy into concrete subsystem responsibilities for engine, runtime, setup, launcher, tools, mods/content, plugin APIs, and documentation.

For aggregation, the most important direction is that the launcher is optional but intended to become the all-in-one Dominium control center. The game must run directly without the launcher. Launcher contracts are additive and disableable. Instances are described with role and display mode. The display modes explicitly provided by the user are NONE, CLI, TUI, and GUI. Launcher supervision should support multiple concurrent clients, servers, tools, and headless processes, with integrated logs rather than independent console windows by default.

The setup system was defined as a separate canonical binary/system, `dom_setup`, responsible for install, repair, uninstall, list, and info. It supports portable, per-user, and system-wide installations, defaults for normal users, and full customization for power users and scripts. It should preserve user data by default and support config/answer files plus non-interactive mode. The launcher should call setup rather than duplicating install mutation logic.

The built-in launcher tabs were fixed by the user: News, Changes, Mods, Instances, and Settings. Each tab must support full interaction. News browses and opens official updates/blogs/releases where supported. Changes browses full changelogs, releases, betas, alphas, and version comparisons. Mods is a complete mod manager with packs, modsets, load order, validation, and content lock generation. Instances manages both installations and running instances. Settings is an intuitive but powerful settings manager for UI, discovery, instances, mods, network/telemetry, advanced paths, and plugins.

The major direction change that must be preserved is the shift from an earlier C++98 launcher backend/frontend plan to a latest C89 launcher architecture based on dsys and dgfx. The user explicitly supplied a new architecture prompt requiring dsys for windowing, filesystem, input, processes, and timers; dgfx for all rendering through IR/canvas/multi-view 2D/3D; a unified software renderer backend; and retro plus modern OS support including DOS, Win16/32, macOS Classic/Carbon/Cocoa, Linux/X11/Wayland, SDL1/SDL2, and CP/M where possible. This latest dsys/dgfx C89 direction should be considered active for launcher implementation. The older C++98/ncurses/SDL/ImGui frontend prompts remain historical artifacts and may provide ideas, but should not drive implementation unless the user revives them.

The strongest unresolved issue is persistent format. Earlier prompts used JSON (`dominium_install.json`, `db.json`, capabilities JSON). The user’s global rules and latest dsys/dgfx architecture point toward versioned TLV `.dmeta` files. This must be resolved before implementation. Other unresolved issues include actual dsys/dgfx API names, actual repo layout/build system, whether setup should also become C89/dsys/TLV, and runtime binary structure/capabilities support.

For a future Project Spec Book, this chat should contribute to chapters on launcher architecture, setup system, runtime-launcher contract, dsys/dgfx UI/rendering, plugin/module extensibility, install modes, mod management, and retro degradation. Preserve uncertainty labels and do not treat assistant-generated prompts as implemented files.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | Latest active launcher direction is C89 + dsys + dgfx. | Architecture | DECISION-16/17/18 | Prevents using superseded frontend plan. | FACT | 5 |
| 2 | Game runs standalone; launcher optional. | Requirement | DECISION-05 | Runtime-launcher boundary. | FACT | 5 |
| 3 | Tabs are News, Changes, Mods, Instances, Settings. | Requirement | DECISION-12 | Defines UX scope. | FACT | 5 |
| 4 | Setup is separate canonical install/repair/uninstall system. | Architecture | DECISION-09 | Prevents duplicate install mutation. | FACT | 4 |
| 5 | JSON-vs-TLV/dmeta conflict unresolved. | Open issue | QUESTION-01 | Must be settled before code. | UNCERTAIN / UNVERIFIED | 5 |
| 6 | Use dsys exclusively for platform services. | Constraint | CONSTRAINT-11 | Prevents platform leakage. | FACT | 5 |
| 7 | Use dgfx exclusively for rendering. | Constraint | CONSTRAINT-12 | Prevents raw OS drawing. | FACT | 5 |
| 8 | Plugins/modules extensibility required. | Architecture | DECISION-14 | Future-proof launcher/setup/instances. | FACT | 5 |
| 9 | Portable/user/system installs required. | Requirement | DECISION-10 | Install mode support. | FACT | 5 |
| 10 | No repository files were inspected or modified. | Provenance | ARTIFACT-22 note | Avoid false assumptions. | FACT | 5 |

## 4. Workstream Summaries

### WORKSTREAM-01 — Global Dominium architecture and repo strategy
- **Objective:** Maintain a coherent monorepo architecture spanning engine, runtime, launcher, setup, tools, content, mods, SDK, docs, and scripts.
- **Current state:** Architectural direction was specified in this chat; no repository was inspected or modified in this chat.
- **Desired end state:** One coherent repository with strict layering, stable APIs/ABIs, versioned file formats, migration paths, and reusable libraries.
- **Priority:** highest
- **Decisions:** DECISION-01, DECISION-02, DECISION-03, DECISION-04
- **Tasks:** TASK-01, TASK-02
- **Constraints:** CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-04, CONSTRAINT-05
- **Artifacts:** ARTIFACT-01, ARTIFACT-02, ARTIFACT-20
- **Risks:** RISK-01, RISK-02, RISK-05
- **Open questions:** QUESTION-01, QUESTION-04
- **Next action:** Inspect repo and confirm active file-format/build conventions before implementation.

### WORKSTREAM-02 — Deterministic C89 engine core
- **Objective:** Preserve the engine as a deterministic, platform-independent C89 core with stable C APIs.
- **Current state:** Only constraints and desired architecture were discussed here; engine code was not inspected.
- **Desired end state:** C89 fixed-point deterministic simulation library with stable C ABI, versioned file IO, and optional ABI-versioned engine plugins.
- **Priority:** highest
- **Decisions:** DECISION-03, DECISION-04, DECISION-08
- **Tasks:** TASK-15
- **Constraints:** CONSTRAINT-01, CONSTRAINT-05, CONSTRAINT-13
- **Artifacts:** ARTIFACT-03, ARTIFACT-04, ARTIFACT-05
- **Risks:** RISK-06, RISK-08
- **Open questions:** QUESTION-07
- **Next action:** Do not modify engine while implementing launcher/setup unless adding explicitly reviewed ABI headers.

### WORKSTREAM-03 — Runtime/game executable integration
- **Objective:** Support direct standalone game execution and optional launcher-supervised execution through a stable CLI/capabilities contract.
- **Current state:** CLI contract and display modes were specified; no runtime code was edited.
- **Desired end state:** Runtime binaries support role/display selection, version/capabilities JSON or equivalent metadata, launcher IDs, and standalone operation.
- **Priority:** high
- **Decisions:** DECISION-05, DECISION-06, DECISION-07
- **Tasks:** TASK-14
- **Constraints:** CONSTRAINT-03, CONSTRAINT-06, CONSTRAINT-07
- **Artifacts:** ARTIFACT-06, ARTIFACT-07, ARTIFACT-21
- **Risks:** RISK-07, RISK-12
- **Open questions:** QUESTION-06, QUESTION-08
- **Next action:** Generate or adapt runtime CLI/capabilities prompt after repo inspection.

### WORKSTREAM-04 — Setup system (`dom_setup`)
- **Objective:** Provide canonical install, repair, uninstall, list, and info functionality for portable, user-local, and system-wide installs.
- **Current state:** A detailed C++98/JSON-based Codex prompt was generated. Latest dsys/dgfx/TLV direction may require adaptation.
- **Desired end state:** A setup tool that supports defaults, full customization, non-interactive config files, conservative uninstall, and optional setup plugins.
- **Priority:** high
- **Decisions:** DECISION-09, DECISION-10, DECISION-11
- **Tasks:** TASK-03, TASK-04, TASK-05
- **Constraints:** CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10
- **Artifacts:** ARTIFACT-08, ARTIFACT-09, ARTIFACT-17
- **Risks:** RISK-09, RISK-10
- **Open questions:** QUESTION-01, QUESTION-03, QUESTION-05
- **Next action:** Revise setup work order around final manifest format and dsys filesystem if needed.

### WORKSTREAM-05 — Launcher as all-in-one Dominium hub
- **Objective:** Build the optional Dominium launcher as a full management hub for news, changes, mods, instances, installs, profiles, settings, and future modules.
- **Current state:** Extensive architecture specified. Latest implementation target is C89 + dsys + dgfx.
- **Desired end state:** A modular, extensible launcher capable of GUI/TUI/CLI operation across modern and retro backends, with process supervision and full tab workflows.
- **Priority:** highest
- **Decisions:** DECISION-05, DECISION-12, DECISION-13, DECISION-14, DECISION-15
- **Tasks:** TASK-06, TASK-07, TASK-08, TASK-09, TASK-10, TASK-11, TASK-12, TASK-13
- **Constraints:** CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-11, CONSTRAINT-12, CONSTRAINT-14
- **Artifacts:** ARTIFACT-10, ARTIFACT-11, ARTIFACT-12, ARTIFACT-13, ARTIFACT-18, ARTIFACT-20
- **Risks:** RISK-01, RISK-02, RISK-03, RISK-04, RISK-11
- **Open questions:** QUESTION-02, QUESTION-04, QUESTION-09
- **Next action:** Produce dsys/dgfx Work-order 1 for core config/install/profile/mods.

### WORKSTREAM-06 — Launcher tabs and user interaction model
- **Objective:** Define full user interactions for News, Changes, Mods, Instances, and Settings tabs.
- **Current state:** Detailed behavior for each tab was specified; no UI implementation exists in chat.
- **Desired end state:** Each tab is fully interactive and uses shared state/actions/widgets, with plugin extensibility.
- **Priority:** high
- **Decisions:** DECISION-12, DECISION-13
- **Tasks:** TASK-10, TASK-11
- **Constraints:** CONSTRAINT-11, CONSTRAINT-12, CONSTRAINT-15
- **Artifacts:** ARTIFACT-12, ARTIFACT-15
- **Risks:** RISK-03, RISK-11
- **Open questions:** QUESTION-09, QUESTION-10
- **Next action:** Convert tab interaction model into C89 module UI work order after UI core/rendering.

### WORKSTREAM-07 — Launcher/setup/plugin extensibility
- **Objective:** Make launcher, setup, and instances extensible through ABI-versioned plugins, modules, and sidecars.
- **Current state:** Architecture specified conceptually; no code implemented.
- **Desired end state:** Built-in modules and external plugins can register tabs, commands, hooks, profiles, and instance observers without destabilizing core.
- **Priority:** medium-high
- **Decisions:** DECISION-14, DECISION-15
- **Tasks:** TASK-12
- **Constraints:** CONSTRAINT-16, CONSTRAINT-17
- **Artifacts:** ARTIFACT-13, ARTIFACT-14
- **Risks:** RISK-08, RISK-13
- **Open questions:** QUESTION-11
- **Next action:** Formalize C89 plugin ABI after core launcher context/state exists.

### WORKSTREAM-08 — dSys/dgfx C89 launcher implementation
- **Objective:** Implement launcher using the Domino system/rendering stack: dsys for platform services and dgfx for rendering.
- **Current state:** Latest architecture response specified lifecycle, rendering pipeline, headers, work orders, platform constraints, and harness.
- **Desired end state:** C89 launcher runs over dsys/dgfx across all declared backends with appropriate fallback/degradation.
- **Priority:** highest
- **Decisions:** DECISION-16, DECISION-17, DECISION-18
- **Tasks:** TASK-06, TASK-07, TASK-08, TASK-09, TASK-10, TASK-11, TASK-12, TASK-13
- **Constraints:** CONSTRAINT-02, CONSTRAINT-11, CONSTRAINT-12, CONSTRAINT-14, CONSTRAINT-18
- **Artifacts:** ARTIFACT-18, ARTIFACT-19, ARTIFACT-20
- **Risks:** RISK-01, RISK-02, RISK-04, RISK-14
- **Open questions:** QUESTION-02, QUESTION-12
- **Next action:** Generate implementation-ready Codex Work-order 1 for launcher core/config/install/profile/mods using dsys FS and versioned metadata.


## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Use one monorepo / one codebase for Dominium subsystems. | accepted by continuation | User asked one codebase vs separate; assistant recommended one codebase and user continued. | Avoid duplicated implementations; centralize shared logic. | Shared utilities and common specs feed setup/launcher/runtime/tools. | ['WORKSTREAM-01'] | 4 | FACT |
| DECISION-02 | Use separate binaries for setup, launcher, and game/runtime. | accepted by continuation | Assistant recommended `dom_setup`, `dom_launcher`, runtime binaries; user continued with that model. | Privilege separation, packaging clarity, crash isolation. | Do not merge setup/launcher/game into one monolithic executable by default. | ['WORKSTREAM-01', 'WORKSTREAM-04', 'WORKSTREAM-05'] | 4 | FACT |
| DECISION-03 | Engine core remains deterministic C89 with no platform/rendering concerns. | active | User’s opening philosophy and repeated constraints. | Protect simulation determinism and portability. | Launcher/setup/tool code cannot leak into engine core. | ['WORKSTREAM-02'] | 5 | FACT |
| DECISION-04 | All file formats should be versioned and migration-based, with TLV preferred by philosophy. | active, format detail unresolved | User opening: version+TLV everywhere; later dmeta/TLV spec. | No silent breakage; future-compatible data. | Must resolve JSON-vs-TLV before implementation. | ['WORKSTREAM-01', 'WORKSTREAM-04', 'WORKSTREAM-08'] | 4 | FACT |
| DECISION-05 | Game must run standalone without launcher. | final unless user reverses | User explicitly stated game should run perfectly fine with no launcher. | Launcher is optional; runtime contracts must degrade cleanly. | Runtime must not require launcher IDs, IPC, or launcher DB. | ['WORKSTREAM-03', 'WORKSTREAM-05'] | 5 | FACT |
| DECISION-06 | Instances use display types NONE, CLI, TUI, GUI. | active | User explicitly specified these display types. | Unifies runtime and launcher instance metadata. | All spawn/UI code should represent display mode explicitly. | ['WORKSTREAM-03', 'WORKSTREAM-05'] | 5 | FACT |
| DECISION-07 | Launcher supervision metadata is optional and disableable. | active | User said contracts can be disabled if unused; assistant specified `--launcher-integration=off`. | Standalone and supervised modes can share binaries. | Launch flags/env vars must not affect gameplay semantics. | ['WORKSTREAM-03'] | 4 | FACT |
| DECISION-08 | Launcher/tools must not hand-roll simulation formats or inspect engine internals. | active | User opening philosophy and assistant stress tests. | Prevents drift between game and tools/launcher. | Launcher reads metadata/manifests, not chunk/sim internals. | ['WORKSTREAM-02', 'WORKSTREAM-05'] | 5 | FACT |
| DECISION-09 | Setup is the canonical install/repair/uninstall authority. | active | Assistant proposal after user asked setup behavior; user continued. | Centralizes install mutation logic. | Launcher should call setup or shared setup APIs rather than duplicating install logic. | ['WORKSTREAM-04'] | 4 | FACT |
| DECISION-10 | Setup must support portable, per-user, and system-wide modes. | active | User explicitly asked about these modes across Windows/Linux/macOS. | Covers USB/non-install and OS-integrated installs. | Path logic and manifests must encode install type. | ['WORKSTREAM-04'] | 5 | FACT |
| DECISION-11 | Setup must support defaults and fully customized operation. | active | User explicitly stated setup should work with defaults or fully customized. | Supports normal users, scripts, CI, and custom layouts. | Requires CLI flags, config/answer files, non-interactive behavior. | ['WORKSTREAM-04'] | 5 | FACT |
| DECISION-12 | Launcher built-in tabs are News, Changes, Mods, Instances, Settings. | active | User explicitly listed the tabs. | Defines core UI surface. | All future UI plans should preserve these tab identities. | ['WORKSTREAM-05', 'WORKSTREAM-06'] | 5 | FACT |
| DECISION-13 | Each launcher tab should be fully interactive, not decorative. | active | User explicitly requested full interaction in each tab. | Drives widget/state/action design. | Need deep workflows for browsing, mod management, instance management, settings. | ['WORKSTREAM-06'] | 5 | FACT |
| DECISION-14 | Launcher/setup/instances should be modular and extensible. | active | User explicitly asked to extend modularity to launcher/setup/instances. | Prevents monolithic code and enables future modules/plugins. | Need module registries, ABI versioning, hook points. | ['WORKSTREAM-07'] | 5 | FACT |
| DECISION-15 | Built-in launcher modules should use the same conceptual registration model as plugins. | proposed/accepted by continuation | Assistant proposed tab descriptors; user continued. | Simplifies extensibility and future plugin tabs. | Tabs should be registered through descriptors, not hard-coded UI blocks only. | ['WORKSTREAM-05', 'WORKSTREAM-07'] | 4 | INFERENCE |
| DECISION-16 | Latest launcher implementation should use dsys for all platform services. | active/latest | User latest major prompt explicitly required dsys for windowing/filesystem/input/processes. | No raw platform calls in launcher. | Codex prompts must inspect/use dsys APIs. | ['WORKSTREAM-08'] | 5 | FACT |
| DECISION-17 | Latest launcher rendering should use dgfx exclusively. | active/latest | User latest major prompt explicitly required dgfx rendering. | No raw OS drawing; no direct ImGui/ncurses/SDL drawing model. | UI tree emits dgfx IR/canvas commands. | ['WORKSTREAM-08'] | 5 | FACT |
| DECISION-18 | Latest launcher API/header direction is strict C89. | active/latest | User latest prompt requested C89 headers for launcher APIs. | Earlier C++98 launcher frontend prompts are superseded for launcher implementation. | Implement launcher core/UI headers and likely source in C89 unless user says otherwise. | ['WORKSTREAM-08'] | 5 | FACT |

### Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Inspect actual repository layout and build system. | highest | immediate | New assistant/Codex | none | Repo access | Verified directory/build conventions. | Run repo scan before any generated code changes. | WORKSTREAM-01 | FACT |
| TASK-02 | Resolve JSON vs TLV/dmeta persistent format direction. | highest | immediate | User/new assistant | TASK-01 | Existing format library, User confirmation | Final format choice for manifests/config/profile/mods. | Ask user or inspect repo conventions. | WORKSTREAM-01, WORKSTREAM-04, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| TASK-03 | Adapt setup work order to final format and dsys if needed. | high | soon | New assistant | TASK-02 | Setup prompt, dsys FS APIs | Implementation-ready setup prompt/spec. | Revise earlier C++98/JSON setup prompt only after format decision. | WORKSTREAM-04 | INFERENCE |
| TASK-04 | Define conservative uninstall policy. | high | soon | Codex/new assistant | TASK-03 | Install ID/data root strategy | Uninstall behavior preserving user data by default. | Include explicit remove-user-data option and safe path checks. | WORKSTREAM-04 | FACT |
| TASK-05 | Define setup plugin hooks and install profiles. | medium | later | Codex/new assistant | TASK-03 | Dynamic loading API | Setup plugin ABI scaffold. | Implement after core setup commands. | WORKSTREAM-04, WORKSTREAM-07 | FACT |
| TASK-06 | Generate dsys/dgfx Work-order 1. | highest | immediate | New assistant | TASK-01, TASK-02 | Latest dsys/dgfx architecture | Codex prompt for core/config/install/profile/mods data layer. | Produce staged prompt with C89 files and end conditions. | WORKSTREAM-08 | FACT |
| TASK-07 | Implement launcher config/install/profile/mods data layer. | high | after TASK-06 | Codex | TASK-06 | dsys FS, TLV schema | C89 modules and harness tests. | Run Work-order 1. | WORKSTREAM-08 | INFERENCE |
| TASK-08 | Implement UI widget/layout/events system. | high | after core data | Codex | TASK-07 | UI header specs | C89 UI tree, layout, focus, input routing. | Run Work-order 2. | WORKSTREAM-08 | FACT |
| TASK-09 | Implement dgfx renderer integration. | high | after UI core | Codex | TASK-08 | dgfx drawing APIs | Widget-to-dgfx IR renderer plus 3D scene module. | Run Work-order 3. | WORKSTREAM-08 | FACT |
| TASK-10 | Implement launcher loop and process supervision. | high | after renderer/core | Codex | TASK-07, TASK-09 | dsys event/process APIs | Main loop, dsys event handling, instance supervision. | Run Work-order 4. | WORKSTREAM-05, WORKSTREAM-08 | FACT |
| TASK-11 | Implement built-in tab UIs. | high | after UI/render/process | Codex | TASK-08, TASK-09, TASK-10 | Tab interaction specs | News/Changes/Mods/Instances/Settings modules. | Run Work-order 5. | WORKSTREAM-06, WORKSTREAM-08 | FACT |
| TASK-12 | Implement launcher plugin/module ABI. | medium-high | after core and tabs | Codex | TASK-10, TASK-11 | dsys dynamic loading | Plugin loader and ABI for tabs/commands/KV/hooks. | Run Work-order 6. | WORKSTREAM-07, WORKSTREAM-08 | FACT |
| TASK-13 | Implement launcher harness and retro degradation tests. | high | after UI/render/core | Codex | TASK-07, TASK-08, TASK-09, TASK-10 | dgfx soft backend, test framework | Runnable harness and CLI/text tests. | Run Work-order 7. | WORKSTREAM-08 | FACT |
| TASK-14 | Implement or verify runtime CLI/capabilities. | high | parallel | Codex | TASK-01 | Runtime source tree | Runtime binaries support role/display/capabilities. | Generate separate prompt if not present. | WORKSTREAM-03 | FACT |
| TASK-15 | Protect engine boundary during launcher/setup implementation. | highest | continuous | All implementers | none | Engine API docs | No accidental engine coupling. | Review build dependencies and includes. | WORKSTREAM-02 | FACT |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Engine core must remain deterministic C89. | technical | hard | User opening philosophy. | No platform/launcher/render dependencies in engine. | high | 5 | FACT |
| CONSTRAINT-02 | Latest launcher direction uses C89 APIs and likely C89 source. | technical | hard unless revised | User latest dsys/dgfx prompt. | Do not blindly implement C++98 launcher frontends. | high | 5 | FACT |
| CONSTRAINT-03 | Game must run standalone without launcher. | product | hard | User explicit clarification. | Launcher IDs/contracts optional. | medium | 5 | FACT |
| CONSTRAINT-04 | Use stable explicit APIs and ABIs. | architecture | hard | User opening philosophy. | Version C ABI/plugin contracts. | medium | 5 | FACT |
| CONSTRAINT-05 | Files should be versioned; TLV preferred by philosophy. | format | hard direction, exact format pending | User opening and latest dmeta mention. | Avoid unversioned JSON blobs unless deliberately accepted. | high | 4 | FACT |
| CONSTRAINT-06 | Instance display types are NONE, CLI, TUI, GUI. | product/technical | hard | User explicit statement. | UI/process/runtime metadata must support all four. | medium | 5 | FACT |
| CONSTRAINT-07 | Launcher supervision contracts must be disableable/unused-safe. | runtime | hard | User explicit statement. | Runtime behavior cannot depend on launcher. | medium | 5 | FACT |
| CONSTRAINT-08 | Setup supports portable, per-user, and system installs. | platform | hard | User explicit question accepted as requirement. | Install root/data root/path logic needed. | medium | 5 | FACT |
| CONSTRAINT-09 | Setup preserves user data by default. | safety | hard | Assistant design accepted by continuation. | Uninstall requires explicit remove-user-data. | high | 4 | FACT |
| CONSTRAINT-10 | Setup supports defaults and full customization. | product | hard | User explicit statement. | CLI/config/non-interactive modes required. | medium | 5 | FACT |
| CONSTRAINT-11 | Launcher uses dsys exclusively for platform services. | technical | hard/latest | User latest prompt. | No direct WinAPI/POSIX/SDL/file calls in launcher. | high | 5 | FACT |
| CONSTRAINT-12 | Launcher uses dgfx exclusively for rendering. | technical | hard/latest | User latest prompt. | No raw OS drawing, no direct ImGui/ncurses rendering. | high | 5 | FACT |
| CONSTRAINT-13 | No floats in deterministic engine/file formats. | determinism | hard | User opening philosophy. | Renderer/UI can use floats if not feeding sim state; engine cannot. | high | 5 | FACT |
| CONSTRAINT-14 | Retro platforms require degradation paths. | platform | hard direction | User latest prompt lists retro platforms. | CP/M likely TUI/CLI only; DOS full-screen soft/TUI. | medium | 5 | FACT |
| CONSTRAINT-15 | Launcher tabs must be fully interactive. | UX | hard | User explicit request. | Need real workflows, not decorative pages. | medium | 5 | FACT |
| CONSTRAINT-16 | Core must work with zero plugins. | extensibility | hard | Assistant architecture for safe modularity. | Plugins optional; failures logged/refused. | medium | 4 | INFERENCE |
| CONSTRAINT-17 | Plugins must be ABI-versioned and refused on mismatch. | extensibility | hard | Assistant architecture based on user modularity requirement. | Requires ABI version constants and symbol checks. | medium | 4 | INFERENCE |
| CONSTRAINT-18 | All external/current software/API facts require verification before use. | evidence | hard for future implementation | User package instructions and system guidance. | Do not trust unstated dsys/dgfx exact APIs. | high | 5 | FACT |

### Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Should install/config/profile/mod files use JSON or TLV `.dmeta`? | Affects all persistent files and setup/launcher compatibility. | Earlier prompts used JSON; user's philosophy and latest dsys/dgfx spec use versioned TLV/dmeta. | Final format choice and existing repo utilities. | Ask user or inspect repo TLV library. | highest | WORKSTREAM-01, WORKSTREAM-04, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | What are the exact dsys and dgfx API names/signatures? | Implementation prompts/code must compile. | User assumes all backends and IR/canvas exist. | Actual header names/function signatures. | Inspect repo. | highest | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Should `dom_setup` also be rewritten to C89/dsys/TLV? | Earlier setup prompt was C++98/JSON; latest launcher direction is C89/dsys/dgfx. | Setup remains separate conceptually. | Language/system-layer requirements for setup. | Ask user after presenting tradeoff. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What is the actual build system and directory layout? | All Codex work orders depend on real target names and paths. | Earlier prompts assumed CMake and proposed directories. | Repo reality. | Inspect repo. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | How should system registration work on retro systems? | Setup and install discovery may not map cleanly to DOS/CP/M. | Modern OS path models were specified; retro support added later. | Retro install conventions. | Design per backend after repo/platform policy. | medium | WORKSTREAM-04, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Is `dom_main` the canonical runtime binary or are there role-specific binaries? | Launcher runtime registry needs binary selection rules. | Both models were discussed. | Repo/runtime structure. | Inspect runtime directory or ask user. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Does engine IO/TLV library already exist? | Launcher/setup should reuse it if appropriate. | User wants one format implementation. | Actual library presence/API. | Inspect repo. | high | WORKSTREAM-02, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Should runtime display modes use dsys/dgfx too? | Launcher and game UI may share system/rendering layers. | Latest prompt focuses launcher using dsys/dgfx; engine supports UI rendering on any backend. | Runtime implementation plan. | Ask user/inspect design docs. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | How should News/Changes fetch/open external content on unsupported platforms? | News/Changes tabs require browsing/opening; retro systems may lack browser/network. | User wants browse/open; dsys system services are where supported. | Fallback UX and cache format. | Design explicit backend capability flags. | medium | WORKSTREAM-06, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | How much account/social/server browser functionality belongs in current tab set? | Earlier all-in-one launcher included these; final tabs do not list separate social/server tabs. | Server/browser/social mentioned as future modules; tabs fixed to five. | Whether these are plugin modules or hidden within tabs/settings. | Ask user when implementing modules. | low-medium | WORKSTREAM-05, WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | Does dsys provide dynamic library loading for plugins? | Plugin ABI implementation depends on loader APIs. | Plugin system desired. | Actual dsys dynamic loading API. | Inspect dsys. | medium-high | WORKSTREAM-07, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | What memory allocation strategy should UI use on retro platforms? | Immutable UI tree per frame may allocate heavily. | C89 retro support required. | Arena/static pool strategy and limits. | Design in Work-order 2. | medium | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact | Type | Purpose | Status | Origin | Carry forward | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Global architecture philosophy text | user statement | Foundational design constraints. | source context | User first message in visible chat. | yes | Includes deterministic C89 core, stable APIs, TLV, mods/plugins, tools reuse libraries. | FACT |
| ARTIFACT-02 | Proposed top-level repo layout | architecture proposal | Organize engine/runtime/launcher/setup/tools/modsdk/content/mods/docs/scripts. | proposed | Assistant early architecture response. | yes | Needs repo verification. | FACT |
| ARTIFACT-03 | `engine_api.h` C ABI sketch | API proposal | Engine-runtime boundary. | proposed | Assistant response. | yes | Exact API unverified. | FACT |
| ARTIFACT-04 | `engine_plugin.h` sketch | API proposal | Engine plugin ABI. | proposed | Assistant response. | yes | Versioned plugin symbol proposed. | FACT |
| ARTIFACT-05 | `DomFileHeader` / `DomTLV` format sketch | format proposal | Shared versioned file pattern. | proposed | Assistant response. | yes | Should be reconciled with existing TLV library. | FACT |
| ARTIFACT-06 | Runtime CLI contract | API proposal | Standalone/supervised runtime integration. | proposed | Assistant response after user optional launcher clarification. | yes | Includes role/display/capabilities/launcher IDs. | FACT |
| ARTIFACT-07 | Display mode enum NONE/CLI/TUI/GUI | model | Instance display abstraction. | accepted concept | User and assistant. | yes | Core carry-forward item. | FACT |
| ARTIFACT-08 | `dom_setup` architecture spec | system spec | Setup install/repair/uninstall. | proposed/accepted by continuation | Assistant response. | yes | Needs adaptation to dsys/TLV if latest direction applies. | FACT |
| ARTIFACT-09 | Portable/user/system install path spec | platform spec | Install modes across Windows/Linux/macOS. | proposed | Assistant response. | yes | External OS paths should be verified before implementation. | FACT |
| ARTIFACT-10 | All-in-one launcher hub spec | system spec | Launcher functions beyond game launching. | proposed/continued | Assistant response. | yes | Future modules include accounts/social/server browser/tools. | FACT |
| ARTIFACT-11 | Launcher tab set | user requirement | News, Changes, Mods, Instances, Settings. | active | User explicit statement. | yes | Highest priority UI artifact. | FACT |
| ARTIFACT-12 | Full tab interaction model | UX spec | What users can do in each tab. | proposed | Assistant response. | yes | Should be carried into dsys/dgfx work orders. | FACT |
| ARTIFACT-13 | Launcher plugin ABI concepts | extensibility spec | Tabs, commands, instance hooks, plugin KV. | proposed | Assistant response. | yes | Needs C89/dsys adaptation. | FACT |
| ARTIFACT-14 | Setup plugin ABI concepts | extensibility spec | Install profiles and post hooks. | proposed | Assistant response. | yes | Needs final language/format decision. | FACT |
| ARTIFACT-15 | Prompt 1: shared foundation + manifests + launcher state skeleton | Codex prompt | Initial implementation plan for earlier architecture. | generated | Assistant output. | historical/partial | Superseded partly by dsys/dgfx but useful for data-layer thinking. | FACT |
| ARTIFACT-16 | Prompt 2: setup system | Codex prompt | Implementation plan for `dom_setup`. | generated | Assistant output. | yes/adapt | C++98/JSON orientation may need revision. | FACT |
| ARTIFACT-17 | Prompt 3: launcher core + tabs + actions + plugin ABI | Codex prompt | Backend launcher implementation for earlier architecture. | generated | Assistant output. | historical/adapt | Superseded by C89/dsys/dgfx for launcher but concepts remain useful. | FACT |
| ARTIFACT-18 | Prompt 4: launcher frontends | Codex prompt | CLI/TUI/GUI frontends for earlier architecture. | generated | Assistant output. | historical | Direct ncurses/SDL/ImGui plan superseded. | FACT |
| ARTIFACT-19 | dSys/dgfx launcher architecture response | architecture + API sketches | Latest active launcher direction. | generated from user latest prompt | Assistant latest architecture response before transfer request. | yes/highest | Includes headers, lifecycle, rendering pipeline, work orders, platform constraints, harness. | FACT |
| ARTIFACT-20 | Context Transfer Packet | handoff text | State transfer for new chat. | generated | Assistant previous final answer. | yes | This package normalizes and exports it. | FACT |
| ARTIFACT-21 | Runtime `--version`/`--capabilities` JSON examples | API proposal | Launcher runtime probing. | generated | Assistant prior prompts. | yes | May need TLV/dsys runtime equivalent if JSON is rejected. | FACT |
| ARTIFACT-22 | This report package | exported files | Downloadable/shareable per-chat report package. | created now | Current assistant response. | yes | Contains Markdown/YAML/ZIP outputs. | FACT |

### Risk Register

| ID | Risk | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Future assistant follows superseded C++98/SDL/ncurses launcher plan. | Wrong implementation direction. | medium | high | Treat latest dsys/dgfx C89 launcher direction as active. | WORKSTREAM-05, WORKSTREAM-08 | FACT |
| RISK-02 | Codex invents dsys/dgfx API names. | Generated code may not compile. | high | high | Require repo inspection and adaptation to actual APIs. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| RISK-03 | Tabs are implemented as decorative pages rather than full workflows. | Launcher fails user’s UX requirement. | medium | high | Carry detailed tab interaction model into work orders. | WORKSTREAM-06 | FACT |
| RISK-04 | Retro platform support overpromised. | Impossible or unusable implementation on CP/M/DOS/Win16. | medium | medium-high | Define explicit degradation paths and capability flags. | WORKSTREAM-08 | FACT |
| RISK-05 | JSON/TLV contradiction causes incompatible files. | Setup/launcher/tools disagree on manifests/config. | high | high | Resolve format decision before implementation. | WORKSTREAM-01, WORKSTREAM-04, WORKSTREAM-08 | FACT |
| RISK-06 | Engine determinism boundary leaks. | Simulation divergence or hidden coupling. | medium | high | Review includes/dependencies; keep launcher/setup out of engine. | WORKSTREAM-02 | FACT |
| RISK-07 | Runtime capabilities not implemented but launcher assumes them. | Instance launch selection fails. | medium | high | Implement or stub runtime capability probing clearly. | WORKSTREAM-03, WORKSTREAM-05 | FACT |
| RISK-08 | Plugin ABI changes silently. | Plugins break unpredictably. | medium | medium-high | Use ABI version checks and exported symbol contracts. | WORKSTREAM-07 | INFERENCE |
| RISK-09 | Setup uninstall deletes wrong data. | User data loss. | low-medium | critical | Preserve user data by default; conservative path checks. | WORKSTREAM-04 | FACT |
| RISK-10 | System install permissions mishandled. | Install/repair/uninstall fail or require unsafe elevation. | medium | medium | Separate portable/user/system logic and privilege boundaries. | WORKSTREAM-04 | FACT |
| RISK-11 | UI tree per-frame allocation too heavy for retro systems. | Memory/performance problems. | medium | medium | Use arenas/static pools and low-memory fallbacks. | WORKSTREAM-08 | INFERENCE |
| RISK-12 | Game becomes dependent on launcher paths/DB. | Standalone requirement violated. | medium | high | Runtime reads its own config/CLI; launcher metadata optional. | WORKSTREAM-03 | FACT |
| RISK-13 | Plugin failures crash launcher/setup. | Extensibility destabilizes core. | medium | medium-high | Core must run with zero plugins; plugin load failures logged/refused. | WORKSTREAM-07 | INFERENCE |
| RISK-14 | Package report treated as proof code exists. | Future implementation assumes nonexistent files. | medium | medium | Manifest/report states no repo was inspected and artifacts are proposed. | WORKSTREAM-01 | FACT |

### Verification Queue

| ID | Item | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Final persistent format: JSON vs TLV `.dmeta`. | Current chat contains both earlier JSON and latest TLV/dmeta direction. | User confirmation and repo format library inspection. | highest | WORKSTREAM-01, WORKSTREAM-04, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Actual dsys and dgfx API names/signatures. | Latest architecture assumes layers exist but did not provide exact APIs. | Repository headers/docs. | highest | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Actual repository layout/build system. | All file paths/targets are proposed. | Repo inspection. | highest | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Setup implementation language and platform layer. | Earlier setup prompt is C++98; latest launcher direction is C89/dsys. | User confirmation. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Install path policy for retro platforms. | Modern paths are specified; retro install conventions are not. | Platform policy/design docs. | medium | WORKSTREAM-04, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Runtime binary names and capabilities support. | Launcher instance manager depends on it. | Runtime source inspection. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Engine C ABI availability. | Runtime and tools need stable boundary. | Engine headers/docs. | high | WORKSTREAM-02, WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | dgfx support for text/fonts/icons/themes and 3D primitives. | UI renderer and splash scene depend on it. | dgfx docs/headers/test harness. | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Network/browser/open URL support through dsys. | News/Changes open/browse behavior depends on backend capability. | dsys service APIs. | medium | WORKSTREAM-06, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | File dialog/clipboard support through dsys. | Mods/settings/user paths UX depends on it. | dsys service APIs. | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Dynamic plugin loading support. | Launcher/setup plugin loaders depend on it. | dsys dynamic library API or platform abstraction. | medium-high | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Whether project has existing TLV migrators. | Migration requirement depends on available tooling. | Repo/docs inspection. | medium | WORKSTREAM-01, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |

## 6. Possible Cross-Chat Duplicates

- Engine C89 determinism.
- Versioned TLV file formats.
- Runtime capabilities contracts.
- Plugin ABI/versioning.
- Setup/install modes.
- Mods/content lock architecture.
- dsys/dgfx platform/rendering layers.

## 7. Possible Cross-Chat Conflicts

- JSON manifests vs TLV/dmeta files.
- Earlier C++98 launcher frontend plan vs latest C89 dsys/dgfx launcher plan.
- Exact list of supported platforms and which are first-class vs scaffold-only.
- Whether setup is C++98/shared-utility based or C89/dsys-based.
- Runtime binary structure: one `dom_main` vs multiple role-specific binaries.

## 8. Spec Book Integration Guidance

Feed this chat into sections on launcher, setup, runtime-launcher contract, dsys/dgfx GUI architecture, mod management, plugin extensibility, and retro support. Convert user-stated requirements into formal requirements. Keep assistant-generated API sketches as draft proposals until checked against repository reality. Do not merge the JSON schemas as final without resolving the TLV conflict.

## 9. Aggregator Warnings

- Do not treat proposed files as existing repository files.
- Do not erase the late dsys/dgfx change of direction.
- Do not treat assistant suggestions as user decisions unless accepted or built on.
- Do not assume external platform/API details are current.
- Do not collapse unresolved questions into decisions.
