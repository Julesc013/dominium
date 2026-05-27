# Registers — Dominium UI Editor + Tool Editor Planning


## 1. Workstream Register
| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Existing Dominium DUI/TLV Runtime System | Preserve and extend the existing in-tree Dominium UI system rather than replacing it. | Existing DUI schema/state TLV system with win32, dgfx, and null backends was described by the user; actual source contents are unverified in this package. | DUI remains the shared runtime/editor UI substrate for launcher, setup, game, tools, and future Tool Editor. | active | high | 4/5 | FACT |
| WORKSTREAM-02 | Phase A Windows UI Editor | Create a minimal Windows-only UI authoring tool that can create and modify DUI TLV UIs and bootstrap the Tool Editor. | Planned in detail through foundational and UU prompts; implementation status unverified. | Windows NT/latest UI Editor with Win32 native preview, hierarchy tree, canvas, property inspector, validation, save/load, import/export, CLI, ops.json automation, and codegen. | active | critical | 4/5 | FACT |
| WORKSTREAM-03 | Phase B Self-Hosting Tool Editor | Build the full internal DUI authoring environment that can edit itself and all Dominium tools. | Planned as the second major phase; no implementation in this chat. | Cross-platform, self-hosting Tool Editor that edits setup, launcher, game, other tools, and its own UI through DUI documents. | active/future | high | 4/5 | FACT |
| WORKSTREAM-04 | Canonical UI IR / TLV / JSON Toolchain | Provide deterministic, safe, maintainable UI document infrastructure. | Designed in prompts; implementation status unverified. | Canonical in-memory IR, TLV source of truth, deterministic JSON mirror, migrations, atomic saves, backups, legacy import. | active | critical | 4/5 | FACT |
| WORKSTREAM-05 | Generic Backend Capability System | Define backend/tier capabilities for validation and cross-platform portability. | Planned in Prompt 4; user explicitly requested generic extensible system. | Declarative backend capability descriptors and deterministic validation across win32, dgfx, null, future appkit/gtk, and compatibility tiers. | active | high | 4/5 | FACT |
| WORKSTREAM-06 | Deterministic Layout Engine | Compute layout geometry consistently for editor preview and runtime backends. | Planned in Prompt 5. | Backend-agnostic integer layout engine with absolute, anchor, dock, stack row/col, constraints, and later grid. | active | high | 4/5 | FACT |
| WORKSTREAM-07 | Splitter / Tabs / ScrollPanel Widgets | Add first-class widgets needed to build complex editors and tool UIs. | Planned in Prompt 6; user confirmed these are required. | SPLITTER, TABS/TAB_PAGE, and SCROLLPANEL supported in IR, TLV, layout, capability tables, and Win32 runtime where feasible. | active | high | 4/5 | FACT |
| WORKSTREAM-08 | Action/Event System and Codegen | Generate stable C/C++ action wiring from UI document event bindings. | Planned in Prompt 7. | Stable string action keys in TLV; registry-assigned numeric IDs; generated `_gen.*` and user-owned `_user.*`; unified C-compatible event ABI. | active | high | 4/5 | FACT |
| WORKSTREAM-09 | DUI Win32 Structural Runtime Fixes | Reduce flicker and make live preview/runtime relayout smoother using structural batching. | Planned in Prompt 10; explicit debugging deferred by user. | Batch update API, coalesced WM_SIZE relayout, batched list/visibility changes, clip styles, optional debug counters. | deferred/active later | medium-high | 4/5 | FACT |
| WORKSTREAM-10 | UI Discovery + Legacy Import/Export | Allow UI Editor to find existing tool UIs, import legacy files, and export canonical docs safely. | Planned in UU1. | Open Tool UI dialog, Import Legacy UI workflow, Export Tool UI workflow, deterministic ui_index.json, machine-readable import reports. | active | high | 4/5 | FACT |
| WORKSTREAM-11 | UI Editor CLI Headless Modes | Expose non-interactive UI toolchain commands for Codex and CI. | Planned in UU2. | Headless validate, format, codegen, build-ui, scan-ui commands with deterministic report JSON. | active | critical | 4/5 | FACT |
| WORKSTREAM-12 | ops.json Deterministic Script Engine | Provide a pure-data edit DSL for Codex to create and modify UI documents. | Planned in UU3. | `--headless-apply` supports create/delete/reparent/set layout/set prop/bind event/validate/save, with ID/path selectors and deterministic reports. | active | critical | 4/5 | FACT |
| WORKSTREAM-13 | Launcher Minecraft-Style Logical Layout Capability Test | Use UI Editor CLI and ops.json to generate a new canonical launcher UI doc using a Minecraft-like logical structure with native Win32 controls. | Planned in UU4; screenshot bundles uploaded but unverified. | Canonical launcher UI doc/script/registry/actions/build integration; launcher loads canonical doc with legacy fallback. | active/future test | high | 4/5 | FACT |
| WORKSTREAM-14 | Setup Minecraft-Style Logical Wizard Capability Test | Use UI Editor CLI and ops.json to generate a new canonical setup wizard UI with native Win32 controls. | Planned in UU5; setup screenshot bundle uploaded but unverified. | Canonical setup UI doc/script/registry/actions/build integration; setup loads canonical doc with fallback. | active/future test | high | 4/5 | FACT |
| WORKSTREAM-15 | Hardening, Determinism, CI Capability Test | Make UI toolchain reproducible, auditable, and usable in CI/headless Codex workflows. | Planned in UU6 and foundational Prompt 11. | CMake regen/validate/capability targets, deterministic tests for apply/codegen/index, documentation and checklists. | active/future | high | 4/5 | FACT |
| WORKSTREAM-16 | IDE-Native Live Editing Workflows | Enable Visual Studio 2026, Xcode, and Linux development tools to live edit or preview Dominium tool UIs while preserving canonical DUI TLV. | A Codex prompt was generated in a txt block; user acceptance of preview-host interpretation is not yet verified. | Platform preview hosts with IDE launch/build integration and hot reload, using canonical UI docs and ops pipelines. | future/planned | medium-high | 3/5 | FACT / INFERENCE |


## 2. Decision Register
| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Build Phase A UI Editor before Phase B Tool Editor | decided | User explicitly selected UI Editor first, Tool Editor second. | Fastest path to a working authoring tool and bootstrap path. | Tool Editor prompts should wait until UI Editor capability is verified. | WORKSTREAM-02, WORKSTREAM-03 | 5/5 | FACT |
| DECISION-02 | Phase A UI Editor is Windows NT/latest / Windows 10+ only | decided | User stated UI Editor only Windows 10 and later Windows NT latest. | Reduces initial platform scope. | No macOS/Linux UI Editor host in Phase A. | WORKSTREAM-02 | 5/5 | FACT |
| DECISION-03 | Phase A UI Editor uses system DPI and 100% design scale only | decided | User explicitly stated system DPI only and design at 100 only for UI Editor. | Simplifies editor canvas and preview. | Per-monitor DPI and zoom deferred to Tool Editor. | WORKSTREAM-02 | 5/5 | FACT |
| DECISION-04 | Tool Editor eventual target is broad cross-platform/self-hosting support | decided | User said Tool Editor should run on any system it is compiled for and eventually edit itself. | Long-term universal UI authoring. | Requires capability system and future platform backends. | WORKSTREAM-03 | 5/5 | FACT |
| DECISION-05 | Use true native OS controls for standard widgets | decided | User said true OS controls/native widgets and native/pixel-perfect across systems. | Native fidelity is core product requirement. | Custom rendering limited to custom widgets/fallbacks. | WORKSTREAM-01, WORKSTREAM-02, WORKSTREAM-13, WORKSTREAM-14 | 5/5 | FACT |
| DECISION-06 | C++98-compatible implementation is acceptable/required for editor/tooling prompts | decided | User said editors can be in C++98; prompts consistently preserve C++98. | Maximizes compatibility. | Avoid C++11+ assumptions. | WORKSTREAM-02, WORKSTREAM-03 | 5/5 | FACT |
| DECISION-07 | CMake remains primary build system; MSVC/Xcode allowed | decided | User said CMake primarily, but MSVC, Xcode etc allowed. | Supports repo consistency plus IDE integrations. | Generated prompts use CMake and IDE projects/presets. | WORKSTREAM-16 | 5/5 | FACT |
| DECISION-08 | Extend existing DUI rather than replacing it with external UI toolkit | decided | User described existing DUI; assistant proposed DUI-centric plan; user continued with it. | Avoids parallel UI system and aligns with all products. | Prompts target DUI IR/TLV/backends. | WORKSTREAM-01 | 4/5 | FACT |
| DECISION-09 | Canonical edit model/IR writes TLV deterministically | decided | User selected Option A1 after recommendations. | Safer than patching TLV bytes. | Need IR, canonical writer, migrations. | WORKSTREAM-04 | 5/5 | FACT |
| DECISION-10 | TLV is canonical source of truth | decided | Assistant recommended; user accepted overall and no objection; later plans use this. | Runtime/editor stability and deterministic format. | JSON is mirror only. | WORKSTREAM-04 | 4/5 | FACT |
| DECISION-11 | Deterministic JSON mirror enabled by default if small | decided | User: “On by default if the file sizes are small.” | Supports diffs/review/debug. | Need size guard; not hand-edited. | WORKSTREAM-04 | 5/5 | FACT |
| DECISION-12 | Separate ui_doc.tlv from optional runtime ui_state.tlv | accepted recommendation | User said separation seems logical. | Prevents editor saves capturing runtime state. | Need loader that can combine doc/state and legacy compatibility. | WORKSTREAM-04 | 4/5 | FACT |
| DECISION-13 | Generic backend capability system across all backends | decided | User explicitly said definitely design modular extensible generic capability system for all backends. | Prevents Windows-only schema bias. | Validation needed before export/build. | WORKSTREAM-05 | 5/5 | FACT |
| DECISION-14 | Stable widget IDs are monotonic u32 and never reused | planned recommendation | Assistant recommended and prompts adopted; user did not object. | Stable diffs and references. | Implementation should avoid hash/rename-derived identity. | WORKSTREAM-04 | 4/5 | INFERENCE |
| DECISION-15 | Action bindings stored as stable strings and compiled to numeric IDs via registry | planned recommendation | Assistant recommended; prompts adopted; user did not object. | Readable authoring and stable runtime dispatch. | Need per-document registry and collision-safe mapping. | WORKSTREAM-08 | 4/5 | INFERENCE |
| DECISION-16 | Unified C-compatible domui_event for actions | planned recommendation | User asked recommendation; assistant recommended; prompts use it. | Backend/tool compatibility. | Not explicitly confirmed but carried forward. | WORKSTREAM-08 | 4/5 | INFERENCE |
| DECISION-17 | Splitter, Tabs, and Scroll containers are first-class Phase A widgets | decided | User answered yes. | Required for Tool Editor and complex layouts. | Prompt 6 and UU4/UU5 depend on them. | WORKSTREAM-07 | 5/5 | FACT |
| DECISION-18 | Layout precedence Dock > Anchors > Absolute | planned recommendation | Assistant recommended deterministic precedence; no objection. | Simplifies layout reasoning. | Should be documented/tested. | WORKSTREAM-06 | 4/5 | INFERENCE |
| DECISION-19 | GRID can be deferred from Phase A; ABS/ANCHOR/DOCK/STACK/SPLITTER/TABS/SCROLL are enough initially | tentative | Assistant recommended smaller Phase A set; user allowed smaller set if Tool Editor can begin. | Keeps UI Editor scope manageable. | May need user confirmation if full grid is requested. | WORKSTREAM-06, WORKSTREAM-02 | 3/5 | INFERENCE |
| DECISION-20 | Flicker debugging deferred until after implementation | decided | User: “Let’s defer all of that debugging until after the implementation.” | Avoid premature debugging. | Structural batching can still be implemented later. | WORKSTREAM-09 | 5/5 | FACT |
| DECISION-21 | Legacy UI files are never overwritten implicitly | planned requirement | Repeated in prompts and accepted plan; user wants import/modify existing tools safely. | Protects existing launcher/setup. | Import/export must be explicit. | WORKSTREAM-10, WORKSTREAM-13, WORKSTREAM-14 | 4/5 | FACT |
| DECISION-22 | Minecraft-style launcher/setup means logical layout only, not graphical design | decided | User explicitly clarified. | Keeps capability test objective and native. | No custom skinning/owner draw. | WORKSTREAM-13, WORKSTREAM-14 | 5/5 | FACT |
| DECISION-23 | Launcher/setup capability tests use native Win32 widgets only | decided | User explicitly stated native Win32 widgets only. | Ensures test reflects native runtime. | No graphical style imitation. | WORKSTREAM-13, WORKSTREAM-14 | 5/5 | FACT |
| DECISION-24 | UI Editor must include CLI so Codex can implement designs automatically | decided | User explicitly requested CLI interface for Codex. | Requires headless modes and ops DSL. | GUI-only editor insufficient. | WORKSTREAM-11, WORKSTREAM-12 | 5/5 | FACT |
| DECISION-25 | IDE live editing should be supported through IDE integration and preview hosts while preserving canonical DUI | assistant proposal; unconfirmed | Assistant generated txt prompt with preview-host architecture after user requested VS/Xcode/Linux IDE live editing. | Realistic way to integrate IDEs without replacing DUI. | Needs user confirmation before treating as final design. | WORKSTREAM-16 | 3/5 | INFERENCE |


## 3. Task Register
| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Determine actual implementation status of all generated prompts | critical | immediate | future assistant / user / Codex | Access to repo or Codex run results | User confirmation or file inspection | Known true state of repo/toolchain | Ask whether prompts were executed; otherwise inspect repo. | WORKSTREAM-02 | FACT |
| TASK-02 | Inspect uploaded source.zip and repo tree if implementation work starts | high | immediate if coding | future assistant / Codex | File availability | /mnt/data/source.zip or repo checkout | Verified file paths, targets, and code state | Extract and map files before changing code. | WORKSTREAM-01 | FACT |
| TASK-03 | Implement/review Prompt 1 repo scan and scaffolding | high | if not done | Codex | Repo checkout | Prompt 1 | New targets and REPO_MAP_UI_SYSTEM.md | Run Prompt 1 or verify equivalent commits. | WORKSTREAM-01, WORKSTREAM-02 | FACT |
| TASK-04 | Implement/review Prompt 2 canonical UI IR | critical | before UI Editor | Codex | Prompt 1 | UI IR spec | domino_ui_ir library and tests | Run Prompt 2 or verify. | WORKSTREAM-04 | FACT |
| TASK-05 | Implement/review Prompt 3 TLV/JSON/legacy import | critical | before import/export | Codex | UI IR and TLV code | Existing TLV files | canonical TLV I/O and importer | Run Prompt 3 or verify. | WORKSTREAM-04, WORKSTREAM-10 | FACT |
| TASK-06 | Implement/review Prompt 4 capability system | high | before validation/export | Codex | UI IR | Backend capabilities | validator and tests | Run Prompt 4 or verify. | WORKSTREAM-05 | FACT |
| TASK-07 | Implement/review Prompt 5 layout engine | high | before preview/runtime parity | Codex | UI IR | Layout rules | deterministic layout engine | Run Prompt 5 or verify. | WORKSTREAM-06 | FACT |
| TASK-08 | Implement/review Prompt 6 Splitter/Tabs/Scroll widgets | high | before Tool Editor/launcher/setup layouts | Codex | IR/TLV/layout/backend | Widget semantics | runtime support and tests | Run Prompt 6 or verify. | WORKSTREAM-07 | FACT |
| TASK-09 | Implement/review Prompt 7 action/event codegen | high | before functional stubs | Codex | UI doc events | Action registry rules | domui_event, codegen, dispatch | Run Prompt 7 or verify. | WORKSTREAM-08 | FACT |
| TASK-10 | Implement/review final UI Editor GUI prompt | critical | after foundational components | Codex | Prompts 1-7 | Final UI Editor prompt | working dominium-ui-editor | Run final UI Editor prompt or verify. | WORKSTREAM-02 | FACT |
| TASK-11 | Implement/review UU1 discovery/import/export | high | after UI Editor core | Codex | UI Editor, legacy import | UU1 prompt | tool discovery/import/export workflows | Run UU1 or verify. | WORKSTREAM-10 | FACT |
| TASK-12 | Implement/review UU2 CLI modes | critical | before automation | Codex | UI Editor core | UU2 prompt | headless validate/format/codegen/build-ui | Run UU2 or verify. | WORKSTREAM-11 | FACT |
| TASK-13 | Implement/review UU3 ops.json engine | critical | before design automation | Codex | CLI and IR ops | UU3 prompt | headless apply script engine | Run UU3 or verify. | WORKSTREAM-12 | FACT |
| TASK-14 | Implement/review UU4 launcher canonical UI script/test | high | after UU2-UU3 | Codex | Launcher build and CLI | UU4 prompt | minecraft_launcher_v1.ops.json and canonical launcher UI | Run UU4 or verify. | WORKSTREAM-13 | FACT |
| TASK-15 | Implement/review UU5 setup canonical UI script/test | high | after UU2-UU3 | Codex | Setup build and CLI | UU5 prompt | minecraft_setup_v1.ops.json and canonical setup UI | Run UU5 or verify. | WORKSTREAM-14 | FACT |
| TASK-16 | Implement/review UU6 hardening and capability test | high | after UU4-UU5 | Codex | UU1-UU5 outputs | UU6 prompt | ui_capability_test and deterministic CI checks | Run UU6 or verify. | WORKSTREAM-15 | FACT |
| TASK-17 | Clarify and implement/refine IDE live editing prompt | medium-high | after UI CLI stable | Codex / future assistant | IDE prompt and platform backends | User confirmation | preview hosts and IDE integrations | Confirm preview-host approach then execute/refine. | WORKSTREAM-16 | INFERENCE |
| TASK-18 | Inspect LauncherC.zip and SetupC.zip if layout fidelity matters | medium | before final visual/layout tests | future assistant | Uploaded screenshots accessible | /mnt/data/LauncherC.zip and /mnt/data/SetupC.zip | Verified screenshot-derived layout notes | Extract and inspect images; revise layout specs if needed. | WORKSTREAM-13, WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| TASK-19 | Generate Tool Editor implementation plan after capability tests pass | high | after UI Editor validation | future assistant | UI Editor and launcher/setup test results | Actual repo status | Tool Editor prompt plan | Do not proceed blindly unless user requests. | WORKSTREAM-03 | FACT |


## 4. Constraint Register
| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Standard controls must use true native OS widgets where feasible | product/technical | hard | User repeated native widget requirement | Use Win32 common controls for Windows preview/runtime; future AppKit/GTK for native platforms. | high | 4/5 | FACT |
| CONSTRAINT-02 | Custom rendering only for custom widgets or fallback cases | technical | hard | User allowed custom rendering only when native cannot implement feature | Avoid owner-draw for standard controls unless required. | medium | 4/5 | FACT |
| CONSTRAINT-03 | Pixel-perfect and host-system optimized UIs are a long-term requirement | product | hard | Initial hard requirement | Requires DPI handling, platform metrics, and per-platform overrides. | high | 4/5 | FACT |
| CONSTRAINT-04 | UI Editor Phase A runs only on modern Windows NT / Windows 10+ | scope | hard | User decision | Do not spend Phase A effort on macOS/Linux host editor. | low | 4/5 | FACT |
| CONSTRAINT-05 | UI Editor Phase A uses system DPI only and 100% design scale | scope | hard | User decision | No per-monitor DPI or zoom in Phase A. | medium | 4/5 | FACT |
| CONSTRAINT-06 | Tool Editor eventual target is all supported compiled systems | scope/product | hard | User broad platform statements | Need backend capability system and future platform ports. | high | 4/5 | FACT |
| CONSTRAINT-07 | Tool Editor supports design scales 25–400 percent | product | hard | User listed exact scale set | Later UI must implement zoom/scaling. | medium | 4/5 | FACT |
| CONSTRAINT-08 | C++98 compatibility for editor/tooling prompts | technical | hard | User said editors can be in C++98; prompts enforce it | Avoid modern C++ features. | medium | 4/5 | FACT |
| CONSTRAINT-09 | CMake remains primary build integration | build | hard | User said CMake primarily | Use CMake targets/custom commands/presets. | medium | 4/5 | FACT |
| CONSTRAINT-10 | MSVC/Xcode projects are allowed where useful | build | soft/allowed | User allowed MSVC/Xcode | IDE integration can add projects/presets without replacing CMake. | low | 4/5 | FACT |
| CONSTRAINT-11 | Offline operation and reasonable/license-compatible dependencies | dependency/legal | hard | Initial hard requirement and later dependency discussion | Avoid external runtime fetches; vendor only legal deps; use fetch scripts for non-distributable assets. | medium | 4/5 | FACT |
| CONSTRAINT-12 | TLV is canonical source of truth | data | hard | Decision in plan | Do not make JSON or IDE-native files authoritative. | high | 4/5 | FACT |
| CONSTRAINT-13 | JSON mirror is read-only deterministic output | data | hard | User accepted mirror if small | Use for review/debug; do not hand-edit. | medium | 4/5 | FACT |
| CONSTRAINT-14 | Deterministic output required for TLV, JSON, reports, codegen, indexes | data/CI | hard | Repeated plan requirement | Stable ordering, no timestamps/random IDs, avoid absolute paths in compare outputs. | high | 4/5 | FACT |
| CONSTRAINT-15 | Legacy UI files must not be overwritten implicitly | safety | hard | Import/export plan and user import requirement | Import to canonical paths; export only explicit. | high | 4/5 | FACT |
| CONSTRAINT-16 | Generated code must not overwrite user edits | safety | hard | Action/codegen plan | Use gen/user split and append/create user stubs safely. | high | 4/5 | FACT |
| CONSTRAINT-17 | Headless CLI must not initialize GUI | tooling | hard | UU2 plan | Supports Codex/CI and environments without GUI. | medium | 4/5 | FACT |
| CONSTRAINT-18 | ops.json is pure deterministic data and must not execute code | security/determinism | hard | UU3 plan | Strict parser, deterministic operation order. | medium | 4/5 | FACT |
| CONSTRAINT-19 | Minecraft-style launcher/setup is logical layout only | product | hard | User explicit clarification | No visual skinning; use native Win32 widgets only. | high | 4/5 | FACT |
| CONSTRAINT-20 | Launcher/setup test uses native Win32 widgets only | technical/product | hard | User explicit clarification | No owner-draw/custom fonts/colors. | high | 4/5 | FACT |
| CONSTRAINT-21 | Do not treat assistant recommendations as user decisions unless accepted | evidence | hard | User asked in packet rules | Keep labels accurate. | high | 4/5 | FACT |
| CONSTRAINT-22 | Uploaded bundles are unverified until inspected | evidence | hard | Visible context: files uploaded but not opened | Do not claim screenshot facts beyond accepted logical spec. | high | 4/5 | FACT |
| CONSTRAINT-23 | GPL/LGPL policy not fully established | legal | soft/uncertain | Assistant recommendation only | Verify before adding dependencies. | medium | 4/5 | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-24 | Win7 supported; XP/lower only if no feature sacrifice | platform | hard/tentative edge | User statement | Use compatibility tiers, not Phase A editor support. | medium | 4/5 | FACT |
| CONSTRAINT-25 | Future reports/spec aggregation must preserve uncertainty labels | process | hard | User requested current package rules | Use FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | high | 4/5 | FACT |


## 5. User Preference Register
| ID | Preference | Label | Source | Strength | Implication | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Straightforward, critical, high-fidelity responses | FACT | User profile/instructions visible in chat | strong | Avoid filler and preserve rigor. | Future assistant may over-soften or over-summarize. |
| PREF-02 | Correct citations and fact checking where external facts are used | FACT | User profile | strong | Use sources for current/external claims. | Unsupported factual claims reduce trust. |
| PREF-03 | Few but detailed Codex prompts optimized for GPT-5.2/Codex | FACT | User requested prompt plan with few detailed prompts | strong | Generate large explicit implementation prompts, not many tiny ones. | Fragmented prompt plan wastes effort. |
| PREF-04 | Small batches of clarifying questions during requirements refinement | FACT | Initial user instructions | strong | Ask max ~10 high-impact questions when requirements are unclear. | Asking too much at once slows work. |
| PREF-05 | Use native OS controls and OEM-like native compatibility | FACT | Repeated user statements | strong | Do not propose Qt/WPF/owner-draw as default. | Violates product goal. |
| PREF-06 | Deterministic, auditable, source-control-friendly pipelines | INFERENCE | Repeated acceptance of canonical TLV, JSON mirror, tests, CI | strong | Stable IDs, stable outputs, no timestamps. | Non-determinism makes future automation unreliable. |
| PREF-07 | Temporary pragmatic bootstrap accepted if it leads to self-hosting system | INFERENCE | User accepted UI Editor first before Tool Editor | medium | Allow Phase A shortcuts if documented and temporary. | Temporary architecture may fossilize. |
| PREF-08 | Graphical skinning is not wanted for Minecraft-style test | FACT | User clarification | strong | Native controls only; layout analogy only. | Wasted work on styling. |


## 6. Open Questions Register
| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Were any generated Codex prompts actually executed? | Determines whether next step is implementation, verification, or further prompt generation. | Prompts were authored in chat. | Actual repo state and commits. | Ask user or inspect repository. | critical | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | What is inside /mnt/data/source.zip? | It may contain repo snapshot or relevant files. | File was uploaded. | Contents uninspected. | Extract and inspect if available. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | What exactly is in LauncherC.zip and SetupC.zip? | Could refine logical layout specs. | Files uploaded. | Screenshot contents uninspected. | Extract and inspect images. | medium | WORKSTREAM-13, WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What is the actual TLV wire format and existing parser/writer API? | Needed for canonical TLV I/O. | Existing DUI uses TLV. | Exact format unknown. | Repo scan/source inspection. | critical | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Where is the setup executable/tool and how does its UI currently work? | Needed for UU5 integration. | User wants setup UI redesigned. | Actual paths/target/UI system unknown. | Repo scan. | high | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Does DUI already separate schema, instance, and runtime state? | Affects doc/state split and migration. | User called current system schema/state TLV. | Exact separation unknown. | Inspect current TLV/generator/runtime. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What exact dependency licenses are allowed? | Needed if adding libraries. | User willing to mirror/source legal deps. | GPL/LGPL exact policy not confirmed. | Ask before adding dependencies. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Should generated code be committed or regenerated during build only? | Affects repo cleanliness and CI. | UU6 notes decision needed. | Repo convention unknown. | Inspect repo/user preference. | medium | WORKSTREAM-08, WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | How much hardcoded substrate is acceptable in Tool Editor v0? | Affects Tool Editor scope and schedule. | User wants final Tool Editor free from hardcoded limitations; assistant recommended temporary substrate. | Whether temporary substrate accepted. | Clarify before Tool Editor implementation. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | Does the user accept preview-host strategy for IDE live editing? | User asked to use IDE GUI tools; prompt used preview hosts not direct designer integration. | IDE prompt generated. | Acceptance/fit unknown. | Clarify with user before implementation. | high | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | Do AppKit/GTK backends already exist or need to be built from scratch? | Required for macOS/Linux native preview/runtime. | Known backends from user are win32/dgfx/null. | AppKit/GTK availability unknown. | Repo scan. | high | WORKSTREAM-16, WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | How should Win95/Win9x/classic Mac support be scoped? | Impacts capability tiers and runtime architecture. | User wants broad future support; Phase A editor modern Windows only. | Runtime-only vs editor-host vs tool-host expectations. | Clarify before legacy-platform work. | medium | WORKSTREAM-05, WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | What exact launcher canonical loader path should be used? | UU4 assumes tools/launcher path but repo may differ. | Launcher target exists by user statement. | Actual runtime working directory/resource path unknown. | Repo scan. | high | WORKSTREAM-13 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | Are Visual Studio 2026 and Xcode versions/environment available? | IDE prompt targets them; current availability may vary. | User requested VS2026 and Xcode. | Actual installed tools not known. | User/environment verification. | medium | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |


## 7. Artifact Ledger
| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | /mnt/data/source.zip | uploaded file | Possible repo/source bundle | uploaded; contents unverified | User upload in this chat | yes | Inspect if needed before implementation. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-02 | /mnt/data/SetupC.zip | uploaded file / screenshot bundle | Setup layout reference | uploaded; contents unverified | User upload in this chat | yes | Assistant generated logical setup spec without inspecting contents. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-03 | /mnt/data/LauncherC.zip | uploaded file / screenshot bundle | Launcher layout reference | uploaded; contents unverified | User upload in this chat | yes | Assistant generated logical launcher spec without inspecting contents. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-04 | launcher_ui_v1.tlv | existing repo file | Legacy/current launcher UI TLV | named by user; path unverified | User statement | yes | Core legacy import target. | FACT |
| ARTIFACT-05 | gen_launcher_ui_schema_v1.py | existing repo file | Current launcher UI schema generator | named by user; path unverified | User statement | yes | Inspect during repo map. | FACT |
| ARTIFACT-06 | dom_launcher_app.cpp | existing repo file | Launcher UI app/state handling | named by user; path unverified | User statement | yes | Inspect during launcher integration. | FACT |
| ARTIFACT-07 | dom_launcher_actions.cpp | existing repo file | Launcher actions | named by user; path unverified | User statement | yes | Inspect during codegen integration. | FACT |
| ARTIFACT-08 | dom_launcher_catalog.cpp | existing repo file | Launcher catalog | named by user; path unverified | User statement | yes | Inspect during integration. | FACT |
| ARTIFACT-09 | dui_win32.c | existing repo file | Win32 DUI backend using child HWND/common controls | named by user; path unverified | User statement | yes | Flicker/runtime integration target. | FACT |
| ARTIFACT-10 | dui_dgfx.c | existing repo file | DGFX DUI backend | named by user; path unverified | User statement | yes | Future custom rendering backend. | FACT |
| ARTIFACT-11 | dui_null.c | existing repo file | Headless DUI backend | named by user; path unverified | User statement | yes | Validation/headless tests. | FACT |
| ARTIFACT-12 | launch_gui.c | existing repo file | Immediate-mode DGFX GUI stub not built into launcher | named by user | User statement | maybe | Not current launcher path. | FACT |
| ARTIFACT-13 | Prompt Plan 1–11 | prompt plan | Foundational implementation sequence | authored in chat | Assistant output | yes | Planning artifact, not implementation evidence. | FACT |
| ARTIFACT-14 | Prompt 1 — Repo scan + scaffolding | Codex prompt | Map repo and add empty targets/docs | authored | Assistant output | yes | No behavior changes. | FACT |
| ARTIFACT-15 | Prompt 2 — Canonical UI IR | Codex prompt | Implement IR/types/tests | authored | Assistant output | yes | Foundation. | FACT |
| ARTIFACT-16 | Prompt 3 — TLV I/O + JSON + legacy import | Codex prompt | Canonical file I/O and importer | authored | Assistant output | yes | Foundation. | FACT |
| ARTIFACT-17 | Prompt 4 — Capability system | Codex prompt | Backend-neutral validation | authored | Assistant output | yes | Foundation. | FACT |
| ARTIFACT-18 | Prompt 5 — Layout engine | Codex prompt | Deterministic layout | authored | Assistant output | yes | Foundation. | FACT |
| ARTIFACT-19 | Prompt 6 — Splitter/Tabs/Scroll | Codex prompt | Bootstrapping widgets | authored | Assistant output | yes | Foundation. | FACT |
| ARTIFACT-20 | Prompt 7 — Action/codegen | Codex prompt | domui_event and action stubs | authored | Assistant output | yes | Foundation. | FACT |
| ARTIFACT-21 | Prompt 8 — UI Editor MVP | Codex prompt | Phase A GUI authoring tool | authored | Assistant output | yes | Foundation. | FACT |
| ARTIFACT-22 | Prompt 9 — Tool Editor bootstrap | Codex prompt | Initial Tool Editor host/doc | authored | Assistant output | yes | Future Tool Editor. | FACT |
| ARTIFACT-23 | Prompt 10 — Runtime batch/flicker structure | Codex prompt | Win32 batching/coalesced relayout | authored | Assistant output | yes | Deferred runtime improvement. | FACT |
| ARTIFACT-24 | Prompt 11 — Hardening | Codex prompt | Tests/docs/CI hooks | authored | Assistant output | yes | Foundation hardening. | FACT |
| ARTIFACT-25 | Final UI Editor implementation prompt | Codex prompt | Actually implement dominium-ui-editor using built components | authored | Assistant output | yes | Central prompt before UU plan. | FACT |
| ARTIFACT-26 | UU1 — UI Project Discovery + Import/Export | Codex prompt | Open Tool UI, import legacy, export canonical | authored | Assistant output | yes | Extension phase. | FACT |
| ARTIFACT-27 | UU2 — UI Editor CLI | Codex prompt | validate/format/codegen/build-ui headless modes | authored | Assistant output | yes | Automation phase. | FACT |
| ARTIFACT-28 | UU3 — ops.json Script Engine | Codex prompt | Headless apply and edit DSL | authored | Assistant output | yes | Automation phase. | FACT |
| ARTIFACT-29 | Minecraft logical launcher/setup structural specification | spec output | Defines layout-only native-widget target for UU4/UU5 | authored and user praised | Assistant output based on unverified bundles plus user clarification | yes | Use as planning spec, not as verified screenshot evidence. | FACT / UNCERTAIN |
| ARTIFACT-30 | UU4 — Launcher UI via ops.json | Codex prompt | Generate canonical launcher UI and integrate build | authored | Assistant output | yes | Capability test. | FACT |
| ARTIFACT-31 | UU5 — Setup UI via ops.json | Codex prompt | Generate canonical setup wizard UI and integrate build | authored | Assistant output | yes | Capability test. | FACT |
| ARTIFACT-32 | UU6 — Hardening/CI capability test | Codex prompt | Regeneration/validation targets and determinism tests | authored | Assistant output | yes | Capability test hardening. | FACT |
| ARTIFACT-33 | IDE live editing prompt in txt block | Codex prompt | VS2026/Xcode/Linux preview-host IDE integration | authored | Assistant output | yes | Future work; acceptance of preview-host interpretation uncertain. | INFERENCE |
| ARTIFACT-34 | tools/ui_index/ui_index.json | planned generated file | Repository UI discovery index | planned, not verified | UU1 prompt | yes | Should be deterministic and generated. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-35 | tools/launcher/ui/scripts/minecraft_launcher_v1.ops.json | planned file | Launcher UI ops script | planned, not verified | UU4 prompt | yes | Capability test input. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-36 | tools/launcher/ui/doc/launcher_ui_doc.tlv/json | planned files | Canonical launcher UI doc/mirror | planned, not verified | UU4 prompt | yes | Generated from ops. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-37 | tools/setup/ui/scripts/minecraft_setup_v1.ops.json | planned file | Setup UI ops script | planned, not verified | UU5 prompt | yes | Capability test input. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-38 | tools/setup/ui/doc/setup_ui_doc.tlv/json | planned files | Canonical setup UI doc/mirror | planned, not verified | UU5 prompt | yes | Generated from ops. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-39 | Context Transfer Packet | report output | Maximum-fidelity handoff for retired chat | authored in chat before this package | Assistant output | yes | This package normalizes and repairs it. | FACT |
| ARTIFACT-40 | This final report package | generated package | Downloadable/shareable per-chat handoff package | created by current response | Current assistant | yes | Includes markdown/yaml/zip. | FACT |


## 8. Rejected / Superseded Options Register
| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Immediate native-per-OS editor frontends for all platforms | superseded | Too high cost/fragmentation for initial path; user chose UI Editor first. | tentative | Reconsider if native fidelity outranks speed after Phase A. | WORKSTREAM-02, WORKSTREAM-03 | FACT |
| REJECTED-02 | Cross-platform editor shell as only initial strategy | superseded | User chose Windows-first UI Editor plus later Tool Editor. | tentative | Reconsider for later cross-platform Tool Editor chrome. | WORKSTREAM-02, WORKSTREAM-03 | FACT |
| REJECTED-03 | Windows-only approach as final architecture | superseded | User wants all systems/products eventually. | final for final state | Never final unless project scope changes. | WORKSTREAM-03 | FACT |
| REJECTED-04 | Direct in-place TLV byte patching | rejected | Unsafe, brittle, hard to migrate; user selected canonical IR model. | final | Only emergency binary repair tool. | WORKSTREAM-04 | FACT |
| REJECTED-05 | JSON/YAML as hand-authored source of truth | rejected as canonical | User saw no need for humans to manually edit because editor exists; TLV canonical chosen. | final unless changed | Reconsider if human-editable workflows become essential. | WORKSTREAM-04 | FACT |
| REJECTED-06 | Manual editing of JSON mirror | rejected | Mirror intended for diff/debug, not source. | final unless changed | If editor/CLI unavailable and user explicitly asks. | WORKSTREAM-04 | FACT |
| REJECTED-07 | Premature flicker debugging before implementation | deferred | User explicitly deferred debugging until after implementation. | tentative/deferred | Reconsider if UI Editor preview is unusably flickery. | WORKSTREAM-09 | FACT |
| REJECTED-08 | Blanket WS_EX_COMPOSITED for flicker | rejected in prompts | Assistant warned it can introduce lag/artifacts. | tentative | Only gated and justified case. | WORKSTREAM-09 | INFERENCE |
| REJECTED-09 | Permanent hardcoded Tool Editor UI limitations | rejected as final state | User wants Tool Editor eventually free of hardcoded limitations. | final for end state | Temporary substrate may be reconsidered with explicit plan to remove. | WORKSTREAM-03 | FACT |
| REJECTED-10 | Graphical Minecraft skinning | rejected | User clarified style means logical layout only. | final unless user changes request | Reconsider only if custom visual design requested. | WORKSTREAM-13, WORKSTREAM-14 | FACT |
| REJECTED-11 | Owner-draw/custom styling for launcher/setup capability test | rejected | User said native Win32 widgets only. | final for capability test | Could be future DGFX/custom theme work, not this test. | WORKSTREAM-13, WORKSTREAM-14 | FACT |
| REJECTED-12 | Replacing DUI with Qt/wx/WPF or another external toolkit | rejected/deprioritized | Contradicts in-tree DUI and native/offline direction. | final unless project pivots | Reconsider only if user explicitly changes architecture. | WORKSTREAM-01 | INFERENCE |
| REJECTED-13 | Treating VS/Xcode native designer files as canonical UI source | deprioritized in IDE prompt | Assistant proposed preview/import bridge instead to preserve TLV canonical. | tentative | Reconsider if user explicitly requires .rc/.xib/GtkBuilder roundtrip. | WORKSTREAM-16 | INFERENCE |
| REJECTED-14 | Assuming screenshot-derived layout without verification | rejected as evidence | Files were uploaded but not inspected. | final evidence rule | Inspect bundles before citing exact screenshot facts. | WORKSTREAM-13, WORKSTREAM-14 | FACT |
| REJECTED-15 | Treating assistant recommendations as final user decisions automatically | rejected by user packet rules | User required labels and not turning brainstorms into decisions. | final process rule | Never. | WORKSTREAM-15 | FACT |


## 9. Risk Register
| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Assuming generated prompts were implemented | Future assistant may skip necessary work or trust nonexistent files. | medium | high | Verify repo state or ask user before acting. | WORKSTREAM-02 | FACT |
| RISK-02 | Treating screenshot bundle interpretation as verified | Layout specs may diverge from actual screenshots. | medium | medium | Inspect uploaded images before fidelity-sensitive work. | WORKSTREAM-13, WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| RISK-03 | Misreading Minecraft-style as graphical skinning | Would produce forbidden owner-draw/custom style work. | medium | high | Preserve “logical layout only, native controls only” constraint. | WORKSTREAM-13, WORKSTREAM-14 | FACT |
| RISK-04 | Overpromising pixel-perfect native parity across OS versions | Native controls vary by OS/theme/DPI. | medium | high | Use capability tiers and per-platform overrides; validate constraints. | WORKSTREAM-03, WORKSTREAM-05 | INFERENCE |
| RISK-05 | Windows bias leaking into canonical schema | Cross-platform Tool Editor/runtime could be compromised. | medium | high | Implement generic capability system early. | WORKSTREAM-05 | FACT |
| RISK-06 | Codegen overwrites user edits | Loss of developer work. | low-medium | high | Use gen/user split and append-only user stubs. | WORKSTREAM-08 | FACT |
| RISK-07 | Legacy import silently drops data | Existing launcher/setup UI behavior may be lost. | medium | high | Generate import reports with warnings and ID maps. | WORKSTREAM-10 | FACT |
| RISK-08 | Headless CLI opens GUI or depends on Win32 window init | Codex/CI automation fails. | medium | medium | Separate CLI paths from GUI initialization. | WORKSTREAM-11 | FACT |
| RISK-09 | Non-deterministic reports/artifacts | CI/goldens and git diffs become noisy. | medium | high | Sort outputs, avoid timestamps/absolute paths. | WORKSTREAM-15 | FACT |
| RISK-10 | Tool Editor self-hosting attempted too early | Schedule stalls on hard subsystem. | medium | medium-high | Validate UI Editor capability tests before Tool Editor. | WORKSTREAM-03 | INFERENCE |
| RISK-11 | Win95/Win9x compatibility mis-scoped | Could force unnecessary Phase A compromises or break future runtime goals. | medium | medium | Treat as capability/runtime tier unless user says editor host. | WORKSTREAM-05 | INFERENCE |
| RISK-12 | IDE live editing expectation mismatch | Preview-host approach may not satisfy user’s desire for IDE GUI tools. | medium | medium-high | Clarify before implementation. | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| RISK-13 | Dependency license policy misunderstood | Legal or redistribution risk. | low-medium | high | Verify before adding non-permissive deps. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-14 | Mac/Linux native backends missing | Cross-platform preview/editor plans may be blocked. | high | medium | Verify backend availability; use null validation fallback if needed. | WORKSTREAM-16, WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| RISK-15 | Future aggregation treats assistant recommendations as user decisions | Spec book may include unaccepted requirements. | medium | high | Preserve labels and evidence. | WORKSTREAM-15 | FACT |
| RISK-16 | Over-compression of prompt artifacts | Future assistant may not recover implementation details. | medium | medium | Use artifact ledger and regenerate exact prompts if needed from summaries. | WORKSTREAM-15 | INFERENCE |


## 10. Verification Queue
| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Inspect repo/source bundle to verify existing DUI files and paths | User named files but paths/contents are unverified. | Repo tree or /mnt/data/source.zip extraction | critical | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Confirm current CMake target names and build layout | Prompts assume targets and folders. | CMake files/repo build | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Confirm whether UI Editor implementation exists | Generated prompts may not have been executed. | Repo commits/files or user confirmation | critical | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Confirm Tool Editor scope before implementation | Hardcoded substrate issue unresolved. | User confirmation after UI Editor status | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Verify TLV wire format and legacy import feasibility | Canonical toolchain depends on actual TLV format. | Existing TLV code and files | critical | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Verify backend capability details | Validation tables need real feature support. | Backend source inspection | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Run layout golden tests after implementation | Ensures determinism and correctness. | CTest/test output | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Confirm generated code commit policy | Affects UU6 and build reproducibility. | Repo conventions/user preference | medium | WORKSTREAM-08, WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Inspect LauncherC.zip screenshots if exact layout fidelity is needed | Previous description unverified. | Image extraction/visual inspection | medium | WORKSTREAM-13 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Inspect SetupC.zip screenshots if exact setup layout fidelity is needed | Previous description unverified. | Image extraction/visual inspection | medium | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Confirm setup executable target and UI integration point | UU5 assumes setup tool exists. | Repo scan | high | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Confirm preview-host approach for IDE live editing | User may expect deeper IDE designer integration. | User confirmation | high | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Verify AppKit/GTK backend availability or plan | IDE/cross-platform tooling requires native backends or null fallback. | Repo scan | high | WORKSTREAM-16, WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Clarify dependency license policy before adding third-party code | Assistant policy recommendations were not explicitly accepted. | User confirmation/legal review | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | Check all current external/tool version assumptions before use | Current software versions/API behavior can change. | Official docs/toolchain environment | medium | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |


## 11. Timeline Register
| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | Initial request | User asked for requirements refinement, tech-stack choices, and final Codex implementation prompt for Dominium Tool Editor/UI tool. | Set overall objective and workflow. | Defines entire chat scope. | 5/5 |
| 2 | Initial clarifying questions | Assistant asked about OSes, language/toolchain, native widgets, editor requirements, output expectations. | Needed to constrain architecture. | Superseded by user answers but still frames requirements. | 5/5 |
| 3 | Initial answers | User specified future Windows/Mac/Linux, first Windows NT, C++98, CMake with MSVC/Xcode allowed, true native widgets, both absolute and layout authoring. | Established hard technical direction. | Core constraints. | 5/5 |
| 4 | Architecture options A/B/C | Assistant proposed native-per-OS, cross-platform shell/native preview, or Windows-first editor. | Gave decision space. | Superseded by hybrid. | 4/5 |
| 5 | Hybrid selected | User chose mix of Option B and C; Windows 10 mandatory, Windows 7 supported, XP lower only if no sacrifice. | Set pragmatic Windows-first path. | Core platform scope. | 5/5 |
| 6 | DUI repo details supplied | User described existing DUI TLV system, files, backends, likely flicker vectors. | Shifted plan from generic UI tool to DUI-native authoring. | Critical architecture input. | 5/5 |
| 7 | source.zip uploaded | User uploaded /mnt/data/source.zip. | Potential repo/source evidence. | Unverified artifact. | 5/5 |
| 8 | DUI-centric options | Assistant proposed first-class DUI Tool Editor vs minimal Windows UI Editor. | Aligned architecture with existing system. | Led to Phase A/Phase B decision. | 4/5 |
| 9 | Phase order decided | User decided UI Editor first, Tool Editor second. | Created bootstrap strategy. | Central sequencing decision. | 5/5 |
| 10 | Phase A/B details | User set UI Editor Windows/system DPI/100%; Tool Editor all systems/per-monitor/scale set; both generate stubs; prerequisite fixes allowed. | Defined scopes. | Core requirements. | 5/5 |
| 11 | Canonical model selected | User selected Option A1; assistant recommended layout, IDs, events, file safety. | Set data architecture. | Core design. | 5/5 |
| 12 | Needed layers enumerated | Assistant listed IR, layout, capability model, style/assets/events/preview diagnostics/tests/repo integration. | Created roadmap. | Basis for prompt plan. | 4/5 |
| 13 | Licensing/dependencies/chrome answers | User said dependencies can be mirrored/fetched legally; UI Editor only bootstrap; final native compatible; Win95 through NT minimum widgets. | Established dependency attitude and final native goal. | Important constraints. | 5/5 |
| 14 | Recommendations made | Assistant recommended TLV canonical, doc/state split, generic capabilities, per-doc codegen registry, canonical diffs. | Narrowed design. | Adopted or carried into prompts. | 4/5 |
| 15 | Tool Editor future clarified | User said UI Editor latest NT; Tool Editor eventually any compiled system; eventually Tool Editor edits itself/all tools. | Reinforced self-hosting and cross-platform goals. | Core future state. | 5/5 |
| 16 | Final recommendations before prompt plan | Assistant recommended TLV-only canonical + JSON mirror, generic caps, minimal Phase A layout, codegen model, batch primitives, self-hosting boundary. | Prepared prompt plan. | Mostly adopted/tentative. | 4/5 |
| 17 | Remaining answers | User chose JSON mirror on by default if small, Splitter/Tabs/Scroll yes, broad platform list. | Closed key open decisions. | Core feature set. | 5/5 |
| 18 | 11-prompt plan generated | Assistant produced prompts 1–11 sequence. | Created implementation roadmap. | Prompt artifacts. | 5/5 |
| 19 | Prompts 1–11 generated | User requested prompt 1 then Next repeatedly; assistant output all detailed prompts. | Created copy-paste implementation prompts. | Artifacts; not implementation evidence. | 5/5 |
| 20 | Final UI Editor prompt generated | User asked for one final prompt to actually create UI Editor; assistant generated it. | Consolidated implementation ask. | Artifact. | 5/5 |
| 21 | New requirements added | User wanted UI Editor to import existing tools, have CLI for Codex, and generate launcher/setup Minecraft-like designs as a test. | Expanded Phase A beyond GUI editor. | Led to UU plan. | 5/5 |
| 22 | UU plan produced | Assistant generated six-prompt plan UU1–UU6. | Focused on import/CLI/ops/launcher/setup/hardening. | Current implementation extension plan. | 5/5 |
| 23 | UU1–UU3 generated | Assistant produced detailed prompts for discovery/import/export, CLI, and ops.json engine. | Prepared automation substrate. | Artifacts. | 5/5 |
| 24 | Screenshots uploaded and clarification | User clarified Minecraft style is logical layout only, native Win32 widgets; uploaded SetupC.zip and LauncherC.zip. | Prevented styling misinterpretation. | Critical constraint. | 5/5 |
| 25 | Logical layout spec generated | Assistant described launcher/setup structure; user approved. | Provided UU4/UU5 design input. | Artifact but screenshot contents unverified. | 4/5 |
| 26 | UU4–UU6 plan folded | Assistant updated plan with structure-only native constraints. | Aligned remaining prompts. | Current plan. | 5/5 |
| 27 | UU4–UU6 generated | Assistant produced detailed prompts for launcher, setup, and hardening. | Completed six-prompt extension package. | Artifacts. | 5/5 |
| 28 | IDE live editing request | User requested VS2026, Xcode, Linux dev tools live editing prompt. | Opened future workflow workstream. | Prompt artifact. | 5/5 |
| 29 | IDE prompt generated | Assistant proposed preview-host architecture in txt block. | Preserved canonical DUI while integrating IDEs. | Needs acceptance/verification. | 4/5 |
| 30 | Context Transfer Packet requested and generated | User requested max-fidelity transfer; assistant produced packet. | Provided continuity source for current package. | Source for this report. | 5/5 |
| 31 | Final report package requested | User asked to normalize, repair, export report package with files and zip. | Current task. | This package result. | 5/5 |


## 12. Spec Book Contribution Register
| ID | Contribution | Likely spec section | Status | Verification needed | Label |
| --- | --- | --- | --- | --- | --- |
| SPEC-01 | Phase A UI Editor scope and requirements | UI Editor | candidate requirement | implementation state | FACT |
| SPEC-02 | Tool Editor self-hosting and cross-platform desired state | Tool Editor | candidate requirement | scope before implementation | FACT |
| SPEC-03 | Canonical TLV/IR/JSON pipeline | UI Document Format | candidate requirement | actual TLV implementation | FACT |
| SPEC-04 | Native-widget launcher/setup logical layout tests | Capability Tests | candidate requirement | screenshot inspection if needed | FACT |
| SPEC-05 | IDE live-preview host approach | Developer Workflow | proposal | user acceptance | INFERENCE |