# Registers — Dominium Launcher Setup Architecture

## 1. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Global Dominium architecture and repo strategy | Maintain a coherent monorepo architecture spanning engine, runtime, launcher, setup, tools, content, mods, SDK, docs, and scripts. | Architectural direction was specified in this chat; no repository was inspected or modified in this chat. | One coherent repository with strict layering, stable APIs/ABIs, versioned file formats, migration paths, and reusable libraries. | active | highest | 5 | FACT |
| WORKSTREAM-02 | Deterministic C89 engine core | Preserve the engine as a deterministic, platform-independent C89 core with stable C APIs. | Only constraints and desired architecture were discussed here; engine code was not inspected. | C89 fixed-point deterministic simulation library with stable C ABI, versioned file IO, and optional ABI-versioned engine plugins. | active | highest | 5 | FACT |
| WORKSTREAM-03 | Runtime/game executable integration | Support direct standalone game execution and optional launcher-supervised execution through a stable CLI/capabilities contract. | CLI contract and display modes were specified; no runtime code was edited. | Runtime binaries support role/display selection, version/capabilities JSON or equivalent metadata, launcher IDs, and standalone operation. | active | high | 4 | FACT |
| WORKSTREAM-04 | Setup system (`dom_setup`) | Provide canonical install, repair, uninstall, list, and info functionality for portable, user-local, and system-wide installs. | A detailed C++98/JSON-based Codex prompt was generated. Latest dsys/dgfx/TLV direction may require adaptation. | A setup tool that supports defaults, full customization, non-interactive config files, conservative uninstall, and optional setup plugins. | active, partly unresolved | high | 4 | FACT |
| WORKSTREAM-05 | Launcher as all-in-one Dominium hub | Build the optional Dominium launcher as a full management hub for news, changes, mods, instances, installs, profiles, settings, and future modules. | Extensive architecture specified. Latest implementation target is C89 + dsys + dgfx. | A modular, extensible launcher capable of GUI/TUI/CLI operation across modern and retro backends, with process supervision and full tab workflows. | active | highest | 5 | FACT |
| WORKSTREAM-06 | Launcher tabs and user interaction model | Define full user interactions for News, Changes, Mods, Instances, and Settings tabs. | Detailed behavior for each tab was specified; no UI implementation exists in chat. | Each tab is fully interactive and uses shared state/actions/widgets, with plugin extensibility. | active | high | 5 | FACT |
| WORKSTREAM-07 | Launcher/setup/plugin extensibility | Make launcher, setup, and instances extensible through ABI-versioned plugins, modules, and sidecars. | Architecture specified conceptually; no code implemented. | Built-in modules and external plugins can register tabs, commands, hooks, profiles, and instance observers without destabilizing core. | active | medium-high | 4 | FACT |
| WORKSTREAM-08 | dSys/dgfx C89 launcher implementation | Implement launcher using the Domino system/rendering stack: dsys for platform services and dgfx for rendering. | Latest architecture response specified lifecycle, rendering pipeline, headers, work orders, platform constraints, and harness. | C89 launcher runs over dsys/dgfx across all declared backends with appropriate fallback/degradation. | active / latest direction | highest | 5 | FACT |

## 2. Decision Register

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

## 3. Task Register

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

## 4. Constraint Register

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

## 5. User Preference Register

| ID | Preference | Basis type | Source basis | Strength | Implication | Risk if misunderstood | Label |
|---|---|---|---|---|---|---|---|
| PREFERENCE-01 | Strict engineering tone | explicit | User latest dsys/dgfx prompt and report instructions | strong | Use specs, tables, exact APIs; avoid filler. | Future assistant may over-soften output. | FACT |
| PREFERENCE-02 | Maximum-fidelity preservation | explicit | User requested context transfer and report package | strong | Preserve contradictions, tentative status, artifacts, IDs. | Summaries may lose key details. | FACT |
| PREFERENCE-03 | Codex-ready implementation prompts | inferred from repeated requests | User repeatedly requested Codex prompts | strong | Produce work orders with files, APIs, end conditions. | Answers may be too vague for implementation. | INFERENCE |
| PREFERENCE-04 | No invented facts | explicit | User report instructions | strong | Label uncertainty and do not fabricate repo state. | Critical trust failure if ignored. | FACT |
| PREFERENCE-05 | Preserve rejected/superseded options | explicit | User report instructions | strong | Registers must keep old C++98 model and rejected monolith option. | Future assistant may repeat rejected work. | FACT |
| PREFERENCE-06 | Prefer rigorous boundaries and modularity | explicit/inferred | User opening philosophy and modularity requests | strong | Separate engine/runtime/setup/launcher/modules/plugins. | Hidden coupling risk. | FACT |
| PREFERENCE-07 | Start responses with model version/build date | PROJECT-CONTEXT | System/user profile context, not visible chat request text | medium | Future assistant may include model/build header. | Not established solely by visible chat. | PROJECT-CONTEXT |
| PREFERENCE-08 | Citations/fact checking generally desired | PROJECT-CONTEXT | User profile context | medium | For external current facts, verify with sources. | Could overburden purely internal spec responses. | PROJECT-CONTEXT |

## 6. Open Questions Register

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

## 7. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
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

## 8. Rejected / Superseded Options Register

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Single monolithic setup+launcher+game binary | rejected/strongly discouraged | Privilege separation, packaging, and crash isolation concerns. | tentative but strongly preferred | Reconsider only for extremely constrained retro builds where process separation is impossible. | WORKSTREAM-01 | FACT |
| REJECTED-02 | Launcher required for gameplay | rejected | User explicitly requires direct executable running without launcher. | final unless user reverses | Only if user changes product model. | WORKSTREAM-03, WORKSTREAM-05 | FACT |
| REJECTED-03 | Independent console windows by default | rejected as default | Breaks aggregated logging and fails in text-only environments. | tentative | May be optional debug/external-console mode. | WORKSTREAM-05 | FACT |
| REJECTED-04 | Launcher linking engine core or sim internals | rejected | Violates layering and deterministic boundary. | final | Do not reconsider; tools may use engine IO separately. | WORKSTREAM-02, WORKSTREAM-05 | FACT |
| REJECTED-05 | Raw OS drawing in launcher | superseded/rejected | Latest user says dgfx exclusively. | final for latest launcher | Only if user explicitly allows emergency fallback. | WORKSTREAM-08 | FACT |
| REJECTED-06 | Direct ncurses/SDL/ImGui launcher UI plan | superseded | Latest dsys/dgfx direction supersedes earlier C++98 frontend prompt. | tentative/latest | Reconsider only if user returns to desktop-only launcher plan. | WORKSTREAM-05, WORKSTREAM-08 | FACT |
| REJECTED-07 | Unversioned or silently changed file formats | rejected | User requires version+TLV/migration. | final | Never; all formats need versions and migrations. | WORKSTREAM-01 | FACT |
| REJECTED-08 | Tools or launcher hand-roll parsers | rejected | User explicitly says tools/launcher reuse same libraries. | final | Only small bootstrap parser if no shared library exists, then centralize. | WORKSTREAM-01, WORKSTREAM-04 | FACT |
| REJECTED-09 | Full graphical feature parity on CP/M | deprioritized/degraded | CP/M is text-mode; user said where possible. | final as degradation | Reconsider only if actual backend supports richer graphics. | WORKSTREAM-08 | INFERENCE |
| REJECTED-10 | Deleting user data by default during uninstall | rejected | Safety rationale in setup design. | final unless user requests destructive uninstall default | Only with explicit user confirmation/flag. | WORKSTREAM-04 | FACT |

## 9. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
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

## 10. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
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

## 11. Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | User introduced global architecture philosophy. | Established deterministic C89 core, stable APIs, TLV formats, data-first mods, reused tool/launcher libraries. | Foundation for every later subsystem. | highest | 5 |
| 2 | Assistant stress-tested the philosophy. | Added warnings on Lua/plugin determinism, ABI details, TLV structure, CLI capabilities, plugin trust/security. | Converted philosophy into actionable contracts. | high | 4 |
| 3 | User shifted to gameplay/user flow. | Download/install, launcher profiles, game version, mods, settings, concurrent clients/servers, console aggregation. | Defined launcher as process supervisor and UX hub. | high | 5 |
| 4 | Assistant proposed process supervisor model. | No independent consoles by default; integrated log capture; GUI/TUI/CLI distinctions; DOS exception. | Shaped instance management and logs. | medium-high | 4 |
| 5 | User clarified game must run without launcher. | Launcher contracts optional; display types NONE/CLI/TUI/GUI. | Prevented hard launcher dependency. | highest | 5 |
| 6 | Assistant specified supervised vs standalone modes. | Launcher IDs optional; `--display`; display enum; build/runtime integration toggle. | Runtime contract stabilized conceptually. | high | 4 |
| 7 | User expanded launcher to all-in-one Dominium hub. | Mods, accounts, tools, installs, server browser, wiki/forum, DMs, playtime. | Expanded launcher scope. | medium-high | 5 |
| 8 | Assistant specified launcher hub modules. | Instances, installs, mods, accounts, servers, social, web, telemetry. | Module architecture emerged. | medium-high | 4 |
| 9 | User asked about install modes across OSes. | Portable, per-user, system-wide install requirements introduced. | Setup/install architecture needed. | high | 5 |
| 10 | Assistant specified install roots/data roots/manifests. | Windows/Linux/macOS paths; `dominium_install.json`. | Created install discovery basis. | medium-high | 4 |
| 11 | User asked setup system behavior. | Installer/repair/uninstaller interaction with launcher/game. | Led to `dom_setup` authority model. | high | 5 |
| 12 | Assistant specified setup system. | `dom_setup`, install/repair/uninstall/list/info, launcher delegates setup. | Setup architecture defined. | high | 4 |
| 13 | User requested summary/detail of launcher/setup. | Assistant produced canonical system spec. | Consolidated architecture. | medium | 4 |
| 14 | User requested Codex prompt. | Assistant generated combined implementation prompt. | Implementation planning began. | medium | 4 |
| 15 | User asked one binary vs separate. | Assistant recommended one codebase, multiple binaries. | Important boundary decision. | high | 4 |
| 16 | User clarified launcher install modes and managing game installs. | Assistant described self-install detection and game install discovery. | Separated launcher install from game install. | high | 4 |
| 17 | User asked setup defaults/customization. | Assistant defined `SetupConfig`, CLI flags, config files, non-interactive behavior. | Setup flexibility established. | high | 5 |
| 18 | User requested modularity for launcher/setup/instances. | Assistant specified plugins, modules, sidecars. | Extensibility became first-class. | medium-high | 5 |
| 19 | User asked to detail entire system. | Assistant created full setup/launcher/instance modular spec. | Precursor to prompts. | medium-high | 4 |
| 20 | User requested three Codex prompts. | Assistant generated setup, launcher, game runtime prompts. | Implementation planning split by subsystem. | medium | 4 |
| 21 | User specified launcher tabs. | News, Changes, Mods, Instances, Settings fixed. | UI scope clarified. | highest | 5 |
| 22 | Assistant detailed tabs. | Data models and behavior for each tab. | UX model built. | high | 4 |
| 23 | User asked structure: agnostic vs binary-dependent. | Assistant defined layers: core state/services, domain modules, runtime registry, UI frontends. | Important separation for implementation. | high | 4 |
| 24 | User asked what users interact with. | Assistant detailed full interactivity per tab. | UX requirements strengthened. | high | 5 |
| 25 | User asked prompt count. | Assistant recommended four main prompts plus optional runtime. | Codex execution plan. | medium-high | 4 |
| 26 | User requested Prompt 1. | Assistant generated shared foundation/manifest/launcher skeleton prompt. | First work-order artifact. | medium | 4 |
| 27 | User requested next. | Assistant generated setup prompt. | Second work-order artifact. | medium | 4 |
| 28 | User requested next. | Assistant generated launcher core/tabs/actions/plugin ABI prompt. | Third work-order artifact. | medium | 4 |
| 29 | User requested next. | Assistant generated UI frontends prompt. | Fourth work-order artifact. | medium | 4 |
| 30 | User introduced dsys/dgfx launcher architecture requirements. | Strict C89, dsys/dgfx, retro/modern platforms, full launcher system. | Major direction change superseding earlier frontend assumptions. | highest | 5 |
| 31 | Assistant produced dsys/dgfx launcher architecture. | Lifecycle, UI framework, rendering pipeline, C89 headers, work orders, harness, platform degradation. | Latest active launcher spec. | highest | 4 |
| 32 | User requested maximum-fidelity Context Transfer Packet. | Assistant produced context packet. | First formal handoff. | highest | 5 |
| 33 | User requested final downloadable report package. | Current task creates normalized files and ZIP. | Makes chat reusable/shareable/aggregatable. | highest | 5 |

## 12. Spec Book Contribution Register

| ID | Contribution | Likely Spec Book Section | Should become requirement? | Needs confirmation? | Notes |
|---|---|---|---|---|---|
| SPECBOOK-01 | Optional launcher and standalone runtime contract | Runtime/Launcher Contract | yes | no | User explicitly required direct executable running. |
| SPECBOOK-02 | Five launcher tabs and full interaction model | Launcher UX | yes | no | User explicitly listed tabs and required full interaction. |
| SPECBOOK-03 | dSys/dgfx launcher architecture | Launcher Platform/Rendering | yes | verify APIs | Latest user direction. |
| SPECBOOK-04 | Setup install/repair/uninstall authority | Setup System | yes | format/language | Assistant design accepted by continuation. |
| SPECBOOK-05 | Portable/user/system install modes | Installation Model | yes | retro behavior | User explicitly asked for these modes. |
| SPECBOOK-06 | Plugin/module extensibility | Extensibility | yes | ABI details | User asked for launcher/setup/instance extensibility. |
| SPECBOOK-07 | JSON vs TLV conflict | Format Policy | not until resolved | yes | Must not be silently merged. |
| SPECBOOK-08 | Earlier C++98 prompts | Historical Design Context | no | no | Useful only as background after latest dsys/dgfx shift. |
