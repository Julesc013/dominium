# Aggregator Packet — Dominium Launcher Application Layer Handoff

## 1. Packet Metadata

* Chat label: Dominium Launcher Application Layer Handoff
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only; project-level context pasted into this chat is labelled PROJECT-CONTEXT.
* Coverage: Full visible chat coverage, based on previous Context Transfer Packet plus visible context.
* Confidence: 4 / 5.
* Staleness risk: Medium.
* Merge priority: High for launcher/application-layer repo-boundary work.
* Main limitations: Current repo state, uploaded file contents, and applied Codex prompt results were not independently verified here.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat was about preserving and hardening the Dominium / Domino application-layer plan, with the Dominium Launcher as the immediate focal product. It began with a concrete launcher question: whether the post-Plan 8 system could support a single common launcher codebase across operating systems, using native OS elements and minimal rendering, inspired by pre-2016 Minecraft launcher examples. The answer evolved through several stages: native widgets require per-platform presentation adapters, while one common launcher “brain” is achieved by separating control-plane logic, interaction semantics, command graph, and platform rendering/input shells.

The early launcher plan was later substantially rebased. Initial suggestions such as a standalone `dominium-launcher/` tree, hand-authored authoritative Visual Studio/Xcode projects, and generic `core/source` directories are now historical and superseded. The user later supplied a canonical product-first repository layout and explicit boundary rules. The current authoritative structure is a monorepo with top-level products including `engine/`, `game/`, `client/`, `server/`, `launcher/`, `setup/`, `tools/`, `libs/`, `schema/`, `docs/`, `ci/`, `sdk/`, and `legacy/`. The launcher is a first-class product under `launcher/`, not an engine subcomponent. The canonical launcher modules are `launcher/core/discover`, `launcher/core/profile`, `launcher/core/invoke`, `launcher/ui`, `launcher/platform`, and `launcher/tests`.

The most important architectural outcome is boundary clarity. Engine purity is non-negotiable: `engine/` must be buildable without launcher/setup/tools, must export only `engine/include/domino/**`, and must not include `dom_contracts`. Cross-product contracts are neutral and live under `libs/contracts/include/dom_contracts`. Setup is the sole authority for install mutation, update, repair, rollback, and installed-state manifests. Launcher consumes setup output only through schemas, manifests, and contracts; it may orchestrate and invoke but must not install, silently repair, mutate installed files, or hide failures.

The user also pasted application-layer canon from another chat. That canon is project-level context but was made authoritative for this chat. It states that architecture is closed and canon locked; this chat exists only for implementation, audit, optimisation, documentation, and maintenance. Applications are content-agnostic orchestration shells. They do not contain gameplay logic, mutate authoritative state, invent defaults, bypass law/authority/epistemics, or bypass RepoX/TestX. CLI is canonical. GUI/TUI are views over the same command graph. UI is data via UI IR, never business logic. Accessibility and localisation are mandatory. Tools are read-only by default. RepoX is the source of truth for changelogs, build metadata, canon-clean tags, and compatibility data. BUILD-ID-0 governs product version strings and mismatch refusal.

Two large Codex prompts were pasted as already applied: one for one-pass refactor/build repair/future-proofing for VS2026+CMake, and one for final engine purity and contract ownership repair. These prompts make CMakePresets the authoritative Visual Studio workflow, require target-based include/link boundaries, introduce or enforce `libs/contracts`, and add sanity scripts such as `verify_tree_sanity.bat` and `verify_includes_sanity.py`. Actual repository success was not independently verified in this chat; all such claims must be checked against the current repo.

The immediate next work is not more planning. The next assistant should first run the verification gates, then determine whether the generated “Dominium Launcher: Spec Completion, Gap Closure, and Documentation Hardening” prompt has been applied. If not, that closure prompt is the correct next action: it documents launcher ownership, boundaries, core modules, interaction model, platform adapters, contract/schema usage, determinism, build workflow, and final status without adding features or redesigning APIs. This report package exists to preserve that state, with stable IDs, uncertainty labels, and aggregation-ready files.

For aggregation, the strongest merge anchors are: launcher as first-class product; engine purity; `libs/contracts` as neutral cross-product contract layer; setup as sole install mutation authority; CMake as authoritative VS2026 build graph; CLI canonical command graph; UI IR and APP-UI-BIND-0; RepoX/TestX/BUILD-ID-0 governance; and the launcher hardening prompt as likely next action before future planning.

Do not merge older assistant-generated directory trees or manual IDE advice into the current spec except as superseded historical notes. Do not promote assistant-suggested exact UI IR filenames into canon unless current repo files or later user instructions confirm them.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Architecture closed; implementation/audit only. | canon | DECISION-01 | Prevents re-planning. | PROJECT-CONTEXT | high |
| 2 | Launcher lives under canonical launcher/ structure. | repo | DECISION-03/04 | Primary chat focus. | FACT | high |
| 3 | Engine purity and no dom_contracts in engine. | boundary | DECISION-05 | Critical invariant. | FACT | high |
| 4 | Contracts in libs/contracts, schemas in schema. | dependency | DECISION-06 | Cross-product channels. | FACT | high |
| 5 | CMake authoritative VS2026 workflow. | build | DECISION-09 | Supersedes old IDE advice. | FACT | high |
| 6 | CLI canonical, UI IR, APP-UI-BIND-0. | UI | DECISION-10/11 | Application-layer UI rule. | PROJECT-CONTEXT | high |
| 7 | Launcher hardening prompt is next if not applied. | task | TASK-03 | Pre-plan closure step. | FACT | medium-high |

## 4. Workstream Summaries

### WORKSTREAM-01: Dominium / Domino application-layer canon

* Objective: Continue implementation, audit, optimisation, and maintenance for applications without redesigning the closed engine/game/simulation architecture.
* Current state: Architecture and canon were stated as closed/locked. The chat is now scoped to application-layer implementation and maintenance only.
* Desired end state: All application work proceeds within APP-CANON0/1, APP-AUTO-0, APP-UI-BIND-0, BUILD-ID-0, RepoX/TestX/VALIDATE-0, and the product-first repo structure.
* Priority: critical
* Decisions: Architecture closed; applications are orchestration shells; applications do not contain gameplay logic or mutate authoritative state.
* Tasks: Verify canon anchors and app docs; ensure app tooling enforces constraints.
* Constraints: No redesign; no hidden defaults; no bypassing RepoX/TestX; content-agnostic apps.
* Artifacts: Latest application-layer canon prompt; latest overall canon prompt.
* Risks: Assistant may re-plan or reinterpret canon.
* Open questions: None at architecture level; implementation verification remains pending.
* Next action: Use this report to bootstrap the next chat, then run repo verification gates.

### WORKSTREAM-02: Dominium Launcher product

* Objective: Maintain and harden the launcher as a first-class product and reference application.
* Current state: Launcher was realigned to the canonical product layout. A closure prompt was generated to bring code and docs up to spec. It is not confirmed in this chat that the closure prompt has been applied.
* Desired end state: Launcher builds, runs, documents its boundaries, uses common command graph/UI IR, passes zero-pack smoke tests, and does not violate product boundaries.
* Priority: critical
* Decisions: Launcher lives under launcher/; canonical structure uses core/discover, core/profile, core/invoke, ui, platform, tests.
* Tasks: Run launcher hardening prompt or audit its results.
* Constraints: No setup internals; no engine internals; no gameplay logic; no install mutation; content-agnostic.
* Artifacts: Launcher master prompt, realignment plan, hardening prompt.
* Risks: Reintroducing older standalone launcher layout or adapter-level business logic.
* Open questions: Whether current implementation has command graph, UI IR binding validation, RepoX integration, and complete docs.
* Next action: Verify repo gates and execute/audit the hardening prompt phases.

### WORKSTREAM-03: Engine purity and boundary enforcement

* Objective: Ensure engine remains reusable and independent, with no launcher/setup/tools/contracts contamination.
* Current state: User stated two Codex prompts have been applied, including final purity and contract ownership repair. Actual repository state was not verified in this chat.
* Desired end state: engine/ contains only include/domino, modules, render, tests, CMakeLists.txt; engine does not include dom_contracts or app/product internals.
* Priority: critical
* Decisions: Non-engine content is evicted to legacy or correct owners; neutral contracts are not engine-owned.
* Tasks: Run verify_tree_sanity and verify_includes_sanity.
* Constraints: Engine C89; public headers parseable forever; no C++ ABI leakage.
* Artifacts: Final purity Codex prompt; verify scripts.
* Risks: Hidden include paths or legacy references can keep contamination alive.
* Open questions: Any ambiguous headers must be classified if found.
* Next action: Run the verification commands.

### WORKSTREAM-04: Setup product and launcher/setup boundary

* Objective: Keep setup as the sole install mutation authority and launcher as a consumer/invoker via contracts.
* Current state: Setup was covered by an earlier generated setup prompt and by the applied one-pass refactor prompt. Actual implementation is unverified.
* Desired end state: setup builds and runs at least CLI help; setup owns install, update, verify, repair, rollback, and installed-state manifests.
* Priority: critical
* Decisions: Launcher/setup communicate only via schema/manifests/contracts; setup owns installed-state mutation.
* Tasks: Run setup --help; scan launcher includes/links for setup internals.
* Constraints: No setup internals in launcher; no hidden mutation.
* Artifacts: Setup master prompt; one-pass Codex prompt.
* Risks: Launcher convenience actions may become install repair logic.
* Open questions: Whether existing launcher code has any leftover repair/install paths.
* Next action: Verify boundary with include script and tests.

### WORKSTREAM-05: Neutral contracts and canonical schemas

* Objective: Use libs/contracts and schema as the only cross-product channels.
* Current state: The final purity prompt introduced libs/contracts/include/dom_contracts. The latest canon requires schemas and manifests as setup-launcher channels.
* Desired end state: All cross-product data is schema-defined or dom_contracts-defined; product internals are not included across boundaries.
* Priority: critical
* Decisions: launcher/setup/tools/game may include dom_contracts; engine must not.
* Tasks: Enumerate contracts used by launcher; add docs/CONTRACT_USAGE.md in launcher hardening.
* Constraints: No foreign product private headers.
* Artifacts: libs/contracts target definition from prompt; schema references.
* Risks: Shared headers might be incorrectly placed in game or tools.
* Open questions: Exact contract coverage for build IDs, launch requests, product manifests, command graph, UI IR remains implementation-dependent.
* Next action: Inspect include graph and contract headers.

### WORKSTREAM-06: UI command graph, UI IR, accessibility, and localisation

* Objective: Ensure CLI/TUI/GUI share one canonical command graph and UI is data, not logic.
* Current state: Application canon requires this. Assistant suggested concrete artifacts such as launcher/ui/command_graph and schema/ui. Implementation status is unknown.
* Desired end state: CLI canonical; GUI/TUI views over command graph; UI IR validates bindings, strings, accessibility, keyboard navigation, localisation fallback.
* Priority: high
* Decisions: CLI is canonical; UI is data; no business logic embedded in UI.
* Tasks: Verify command graph, UI IR schema, binding validator, and zero-pack/missing-locale tests.
* Constraints: All strings externalised; no color-only semantics; keyboard-only operation; screen reader tags.
* Artifacts: APP-UI-BIND-0, UI/UX canon, assistant checklist.
* Risks: Treating assistant-suggested filenames as locked canon; only the requirements are locked unless files exist.
* Open questions: Exact file format and location for command graph/UI IR if not already established in repo.
* Next action: Inspect current UI implementation and add missing docs/tests under closure scope.

### WORKSTREAM-07: VS2026, CMake, CI, and build/test gates

* Objective: Use CMakePresets and target-based boundaries to build and verify the repo, especially on Visual Studio 2026.
* Current state: One-pass Codex prompt required CMakePresets, target graph normalization, setup/launcher/tools builds, and CTest smoke tests. Actual result unverified.
* Desired end state: Open Folder in VS2026 works; cmake configure/build/ctest pass; launcher/setup help run.
* Priority: critical
* Decisions: CMake generates VS projects; no hand-written vcxproj as authoritative build.
* Tasks: Run cmake --preset vs2026-x64-debug; build; ctest; help commands.
* Constraints: No global include dirs; target_include_directories with PUBLIC/PRIVATE.
* Artifacts: One-pass Codex prompt; docs/BUILDING.md requirement.
* Risks: Old IDE advice may be revived; CMake target graph may be incomplete.
* Open questions: Whether current presets and smoke tests pass.
* Next action: Run commands and record results.

### WORKSTREAM-08: RepoX, TestX, VALIDATE-0, and BUILD-ID-0 governance

* Objective: Enforce canon, versioning, changelogs, compatibility, schema validation, and UI binding validation mechanically.
* Current state: Latest canon locks these systems. Implementation status is not verified in this chat.
* Desired end state: RepoX/TestX gates prevent invalid states; applications display build IDs/changelogs and refuse mismatches loudly.
* Priority: critical
* Decisions: No manual changelog editing; no distributed artifact without GBN; build identity format locked.
* Tasks: Verify CANON_INDEX, RepoX outputs, build identity parsing/enforcement, TestX gates.
* Constraints: GBN only centrally allocated for beta/rc/release/hotfix; dev/ci use BII.
* Artifacts: BUILD-ID-0; APP-AUTO-0; APP-UI-BIND-0.
* Risks: Manual changelogs or silent version mismatch.
* Open questions: How launcher currently surfaces RepoX metadata.
* Next action: Add to verification queue and tests.

### WORKSTREAM-09: Tools and validators

* Objective: Keep tools first-class, read-only by default, and use them for validation such as UI binding/schema checks.
* Current state: Tools are part of canonical layout. UI binding validator was recommended but implementation unknown.
* Desired end state: tools/_shared and tools validators build; tools do not include launcher/setup internals; write modes explicit.
* Priority: medium-high
* Decisions: Tools are read-only by default; tools use tools/_shared plus libs/contracts/schema as needed.
* Tasks: Verify UI binding validator and schema validators.
* Constraints: No launcher/setup internals unless public; explicit --write for mutation if ever allowed.
* Artifacts: One-pass Codex prompt tools phase; APP-UI-BIND-0.
* Risks: Validators missing or not wired to CI.
* Open questions: Exact validator inventory.
* Next action: Inspect tools targets.

### WORKSTREAM-10: Client and server application constraints

* Objective: Preserve client/server app-layer boundaries while focusing on launcher.
* Current state: Mentioned in application canon; not directly implemented in this chat.
* Desired end state: Client handles presentation/input/inspection with no authority; server is headless-first and authoritative/SRZ-aware.
* Priority: medium
* Decisions: Client no authority; server assigns SRZ authority; apps do not change SRZ authority.
* Tasks: None before launcher closure.
* Constraints: No UI assumptions for server; no world mutation by client UI.
* Artifacts: Latest application canon.
* Risks: Future assistant may conflate launcher/client/server.
* Open questions: None in this chat.
* Next action: Do not act until launcher closure unless user asks.

### WORKSTREAM-11: This chat handoff and report package

* Objective: Produce a final downloadable, shareable, reusable report package for this old chat.
* Current state: This package is being generated from the previous context transfer packet and visible chat context.
* Desired end state: Seven report files plus ZIP exist and are safe for later aggregation with caveats.
* Priority: critical for continuity
* Decisions: Chat label inferred as Dominium Launcher Application Layer Handoff.
* Tasks: Download and store package files.
* Constraints: Do not invent facts; label uncertainty; include stable IDs; create actual files if possible.
* Artifacts: All files in this package.
* Risks: Over-compression or future aggregation misread.
* Open questions: None.
* Next action: Save ZIP and key Markdown/YAML files.



## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Architecture is closed; canon is locked. | locked | User pasted multiple canon prompts stating this directly. | Prevent redesign and keep work implementation-focused. | All future work must operate within canon. | WORKSTREAM-01 | high | PROJECT-CONTEXT |
| DECISION-02 | Applications are orchestration shells and must not contain gameplay logic or mutate authoritative state. | locked | Application-layer canon pasted by user. | Protect deterministic simulation authority and epistemics. | Launcher/setup/client/server/tools cannot decide rules or alter world state. | WORKSTREAM-01 | high | PROJECT-CONTEXT |
| DECISION-03 | Launcher is a first-class product under launcher/. | locked | User canonical repository prompt. | Avoid engine contamination and make application boundaries explicit. | Launcher code/docs/tests belong under launcher/ or neutral schema/contracts. | WORKSTREAM-02 | high | FACT |
| DECISION-04 | Canonical launcher modules are core/discover, core/profile, core/invoke, ui, platform, tests. | locked | User canonical launcher location. | Clear responsibility split and no generic source directories. | Old standalone launcher/core/source structures are obsolete. | WORKSTREAM-02 | high | FACT |
| DECISION-05 | Engine purity is non-negotiable. | locked | User canonical prompt and final purity Codex prompt. | Engine must remain reusable and independent. | No launcher/setup/tools/dom_contracts in engine. | WORKSTREAM-03 | high | FACT |
| DECISION-06 | Cross-product contracts live in libs/contracts/include/dom_contracts. | locked | Final purity Codex prompt. | Neutral ownership for shared product contracts. | Launcher/setup/tools/game can include; engine cannot. | WORKSTREAM-05 | high | FACT |
| DECISION-07 | Setup is the only install mutation authority. | locked | Application-layer canon and earlier launcher/setup boundary prompts. | Separate install mutation from orchestration. | Launcher cannot install, silently repair, or mutate installed payloads. | WORKSTREAM-04 | high | FACT |
| DECISION-08 | Launcher/setup communicate only via schemas, manifests, and contracts. | locked | User dependency rules. | Prevent setup internals from leaking into launcher. | Launcher must not link/include setup internals. | WORKSTREAM-04 | high | FACT |
| DECISION-09 | CMake is the authoritative VS2026 build path. | locked | Applied one-pass Codex prompt says no hand-written vcxproj as authoritative build. | CMake target graph enforces boundaries and supports VS Open Folder. | Earlier manual IDE project advice is superseded. | WORKSTREAM-07 | high | FACT |
| DECISION-10 | CLI is canonical and GUI/TUI are views over the same command graph. | locked | Application-layer canon. | Ensures scriptability, parity, and testability. | Platform adapters must not invent commands. | WORKSTREAM-06 | high | PROJECT-CONTEXT |
| DECISION-11 | UI is data via UI IR; UI must contain no business logic. | locked | UI/UX requirements and APP-UI-BIND-0. | Supports accessibility, localisation, portability, validation. | UI binding validation is required. | WORKSTREAM-06 | high | PROJECT-CONTEXT |
| DECISION-12 | All app strings are externalised and locale packs are normal packs with raw-key fallback. | locked | UI/UX requirements pasted by user. | Ensures i18n and content-agnostic app behavior. | Hardcoded UI strings are violations except possibly documented temporary stubs. | WORKSTREAM-06 | high | PROJECT-CONTEXT |
| DECISION-13 | RepoX is source of truth for changelogs, build metadata, canon tags, and compatibility data. | locked | RepoX/versioning canon pasted by user. | Eliminates manual drift and hidden release state. | Launcher must display generated changelogs and warn/refuse incompatibilities. | WORKSTREAM-08 | high | PROJECT-CONTEXT |
| DECISION-14 | Versioning format is <product>-<semver>+<build_kind>.<id>, with GBN rules from BUILD-ID-0. | locked | Latest canon pasted by user. | Release traceability and compatibility enforcement. | No distributed artifact without GBN; local builds use BII; mismatch refuses loudly. | WORKSTREAM-08 | high | PROJECT-CONTEXT |
| DECISION-15 | Tools are first-class and read-only by default. | locked | Application-layer canon. | Prevents tooling from becoming hidden mutation authority. | Validators/inspectors should not mutate unless explicitly flagged. | WORKSTREAM-09 | high | PROJECT-CONTEXT |
| DECISION-16 | The launcher code/docs must be hardened before regenerating further plans. | active | User requested a prompt for that purpose; assistant generated closure prompt. | Avoid planning on implicit/incomplete implementation state. | Next work should be audit/spec completion, not feature design. | WORKSTREAM-02 | medium-high | FACT |

### Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Run repo sanity, include, build, ctest, launcher/setup help gates. | critical | immediate | User/Codex/new assistant | Current repo checkout, VS2026/CMake environment | Repo files, CMakePresets.json | Verified baseline status. | Execute commands listed in VERIFY-01 through VERIFY-07. | WORKSTREAM-07 | FACT |
| TASK-02 | Determine whether the Launcher Spec Completion prompt has been applied. | critical | immediate after baseline | User/Codex | Current git history/docs | Repo commits, launcher/docs | Clear applied/not-applied status. | Inspect docs/LAUNCHER_AUDIT.md, launcher/docs/*, and commit history. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| TASK-03 | If not applied, execute the Launcher Spec Completion, Gap Closure, and Documentation Hardening phases. | critical | soon | Codex | Passing baseline gates | Generated prompt, current implementation | Launcher docs/code made explicit and boundary-safe. | Start phase 0 baseline audit snapshot. | WORKSTREAM-02 | FACT |
| TASK-04 | Audit CANON_INDEX.md for APP-CANON0/1, APP-AUTO-0, APP-UI-BIND-0, BUILD-ID-0. | high | soon | Codex | Repo docs | CANON_INDEX.md | Canon anchors present and referenced. | Open/update CANON_INDEX.md. | WORKSTREAM-08 | PROJECT-CONTEXT |
| TASK-05 | Ensure application docs have status headers and canon refs. | high | soon | Codex | CLEAN-2/app canon | Docs tree | Docs have STATUS, CANON REF, SCOPE, NON-GOALS. | Scan and update launcher/app docs. | WORKSTREAM-01 | PROJECT-CONTEXT |
| TASK-06 | Verify launcher command graph exists and drives CLI help. | high | soon | Codex | Launcher UI layer | launcher/ui, schema | Single canonical command graph is used by CLI/TUI/GUI. | Inspect and add missing tests/docs if needed. | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| TASK-07 | Verify UI IR schema and UI binding validator exist and are wired to TestX/RepoX. | high | soon | Codex | schema, tools, TestX/RepoX | schema/ui, tools validators | APP-UI-BIND-0 enforceable gate. | Inspect schema/tools and add closure work if absent. | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| TASK-08 | Add/verify zero-pack and missing-locale launcher smoke tests. | high | soon | Codex | Launcher test harness | Test fixtures | Launcher runs with zero content packs and raw key fallback. | Run or add smoke tests. | WORKSTREAM-02 | PROJECT-CONTEXT |
| TASK-09 | Verify RepoX changelog/build identity display and mismatch refusal in launcher. | high | soon | Codex | RepoX metadata, BUILD-ID-0 | Build metadata outputs | Launcher surfaces changelog/build IDs and refuses incompatible mismatches. | Inspect version modules/tests and add missing coverage. | WORKSTREAM-08 | PROJECT-CONTEXT |
| TASK-10 | Audit launcher/setup boundary for direct internals or mutation. | critical | soon | Codex | Include/link scanners | Launcher/setup code | No setup internals or install mutation in launcher. | Run include scanner and inspect invoke/repair paths. | WORKSTREAM-04 | FACT |
| TASK-11 | Classify ambiguous shared headers if scanners reveal them. | medium | as needed | User + Codex | Offending headers | Header contents and include graph | Headers moved to correct owner/contracts/schema. | Stop and ask user if ownership cannot be determined. | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| TASK-12 | Save this handoff package and use it as input to a future aggregator. | high | now | User | Generated files | ZIP and individual files | Package preserved for future spec-book construction. | Download ZIP and store in per-chat folder. | WORKSTREAM-11 | FACT |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Architecture closed; canon locked. | Governance | hard | User canon prompts | Implementation only; no redesign. | Very high | high | PROJECT-CONTEXT |
| CONSTRAINT-02 | All systems reduce to Assemblies, Fields, Processes, Agents, Law. | Ontology | hard | Latest canon prompt | No new primitives or fake systems. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-03 | Process-only mutation. | Simulation | hard | Latest canon prompt | Apps cannot mutate authoritative world state. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-04 | Deterministic, replayable simulation with fixed-point authoritative logic and named RNG streams. | Simulation | hard | Latest canon prompt | Apps cannot introduce hidden nondeterministic defaults. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-05 | Strong epistemics and fog of war everywhere. | Simulation | hard | Latest canon prompt | Apps/tools must not reveal omniscient state unless authorized inspection semantics exist. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-06 | Applications are content-agnostic and must run with zero content packs installed. | Application | hard | Application-layer canon | Launcher/help/diagnostics cannot require content packs. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-07 | Applications do not contain gameplay logic or mutate authoritative state. | Application | hard | Application-layer canon | Launcher/client/tools do not decide rules. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-08 | Setup is the only install mutation authority. | Application | hard | Application-layer canon | Launcher cannot install or repair directly. | High | high | FACT |
| CONSTRAINT-09 | Launcher is first-class under launcher/. | Repository | hard | Canonical repo prompt | No launcher code in engine/ or standalone old tree. | High | high | FACT |
| CONSTRAINT-10 | Engine must not include or link launcher/setup/tools/dom_contracts. | Repository | hard | Engine purity prompt | Engine PUBLIC include is engine/include only. | High | high | FACT |
| CONSTRAINT-11 | Cross-product contracts live in libs/contracts/include/dom_contracts. | Repository | hard | Final purity prompt | Shared APIs must not live in engine/game internals. | High | high | FACT |
| CONSTRAINT-12 | Launcher depends only on libs, engine public API, schema, dom_contracts, and optional game metadata contracts. | Dependency | hard | Canonical launcher dependency rules | No engine internals, setup internals, tools internals. | High | high | FACT |
| CONSTRAINT-13 | CMake is authoritative for VS2026 builds. | Build | hard | Applied one-pass Codex prompt | No hand-written vcxproj as authoritative build graph. | Medium-high | high | FACT |
| CONSTRAINT-14 | Use target include dirs; no global include_directories except minimal generated config. | Build | hard | Applied one-pass Codex prompt | Boundary enforcement through CMake. | Medium-high | high | FACT |
| CONSTRAINT-15 | Engine C89; game C++98; public headers parseable forever; no C++ ABI leakage across boundaries. | Toolchain/API | hard | Latest canon prompt | Shared/public contracts must stay conservative. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-16 | CLI is canonical; GUI/TUI are views over same command graph. | UI | hard | Application-layer canon | Adapters cannot invent commands or semantics. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-17 | UI is data via UI IR; no business logic in UI. | UI | hard | Application-layer canon and APP-UI-BIND-0 | Bindings must be validated; render backend interchangeable. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-18 | Accessibility and localisation mandatory. | UI/UX | hard | Application-layer UI/UX requirements | Keyboard-only, screen reader tags, font/contrast, no color-only semantics, externalised strings, raw-key fallback. | Medium-high | high | PROJECT-CONTEXT |
| CONSTRAINT-19 | RepoX/TestX enforce canon, changelogs, schema validation, UI binding validation, metadata stamping. | Automation | hard | Latest canon prompt | No manual changelog editing or bypassed gates. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-20 | BUILD-ID-0 versioning and mismatch refusal are locked. | Release governance | hard | Latest canon prompt | No distributed artifact without GBN; mismatch refuses loudly. | High | high | PROJECT-CONTEXT |
| CONSTRAINT-21 | Do not invent facts; label uncertainty; preserve superseded options. | Reporting | hard | User request for this package | Future readers must distinguish facts from inferences. | Medium | high | FACT |

### Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Did the two applied Codex prompts fully succeed in the actual repo? | All next actions depend on current build and boundary status. | User says they were applied. | Actual build/script results unknown. | Run sanity scripts, CMake configure/build, CTest, launcher/setup help. | critical | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Has the launcher spec completion/hardening prompt been applied? | Determines whether to execute it or audit its outputs. | Prompt was generated. | No confirmation it was run. | Inspect commits/docs such as docs/LAUNCHER_AUDIT.md and launcher/docs/*. | critical | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Does CANON_INDEX.md contain required app/build canon IDs? | Docs and enforcement need canonical anchors. | Latest canon requires it. | File content unknown. | Open CANON_INDEX.md. | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | Does launcher/ui contain a command graph artifact used by CLI help? | CLI canonicality must be mechanical. | Requirement is locked. | Implementation unknown. | Inspect launcher/ui and CLI help generation. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Does schema/ui or equivalent UI IR schema exist? | UI is data and binding validation require schemas. | UI IR requirement locked. | Exact schema files unknown. | Inspect schema/ and tools validators. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Is APP-UI-BIND-0 enforced by a validator in tools/TestX? | Prevents GUI/TUI drift and logic leakage. | Binding validation required. | Tool implementation unknown. | Inspect tools and CI/TestX configuration. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Does launcher run with zero packs and missing locale pack? | Content-agnostic app requirement. | Requirement locked. | Test coverage unknown. | Run/add zero-pack and raw-key fallback tests. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Does launcher display RepoX changelog/build metadata and enforce BUILD-ID-0 mismatches? | Release governance and compatibility depend on this. | Requirement locked. | Implementation unknown. | Inspect RepoX outputs and launcher version/diagnostic code. | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | Are any shared headers ambiguously owned? | Misplaced headers cause boundary violations. | Final purity prompt anticipated stop conditions. | Current header inventory unknown. | Run include sanity script and inspect offenders. | medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | Do any old launcher files from the earlier current tree remain in obsolete locations? | Old structure can cause duplicate logic or drift. | Old tree was provided before refactors. | Current tree unknown. | Inspect repository tree and legacy/ quarantine. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | Do setup and launcher communicate only through schema/contracts? | Boundary requirement is critical. | Rule locked. | Actual integration unknown. | Scan includes/links and invoke paths. | critical | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Are uploaded Plan 8/repo files still needed for future work? | They may contain historical context but are superseded by later canon. | Files were uploaded in this chat. | Contents were not inspected in this final package. | Only open if resolving historical Plan 8 questions. | low | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | dominium.zip | uploaded repo archive | Copy of repo as of Plan 8 prompt 3 completion. | Unverified in this report; user uploaded earlier. | User upload | yes if available | Not inspected in final package generation. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-02 | PLAN-8-CODEX-PROMPTS.txt | uploaded text file | Plan 8 structure and changes. | Unverified in this report. | User upload | yes if resolving Plan 8 history | Superseded by later canon where conflicting. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-03 | Minecraft launcher reference images | uploaded images | Visual/UX inspiration for fast native cross-platform launcher. | Available earlier in chat context; not analyzed for technical facts. | User upload | optional UX reference | Includes Screen_Shot_2022-08-08 images, yDYjX.png, 638238760876459333.png, hvD9R.png, LauncherC.png, LauncherCover.png, minecraftlauncher.png. | FACT |
| ARTIFACT-04 | GPT-5.2 MASTER PROMPT — DOMINIUM / DOMINO LAUNCHER SYSTEM | user-pasted prompt | Initial launcher architecture phases. | Partially superseded/rebased. | User | carry non-conflicting concepts | Use only where aligned with canonical repo. | FACT |
| ARTIFACT-05 | Phase 1 Launcher Core Architecture answer | assistant output | Pure control-plane launcher architecture with host APIs/determinism/error model. | Useful but rebased. | Assistant | yes selectively | Map to launcher/core/discover/profile/invoke. | FACT |
| ARTIFACT-06 | VS/Xcode manual project advice | assistant output | Earlier advice on IDE project locations. | Superseded. | Assistant | no except rejected history | Contradicted by CMake authoritative prompt. | FACT |
| ARTIFACT-07 | Box-drawing dominium-launcher directory tree | assistant output | Initial standalone launcher tree. | Superseded. | Assistant | historical only | Do not implement as current layout. | FACT |
| ARTIFACT-08 | Setup master prompt | assistant-generated prompt | Deterministic setup core and adapters plan. | Partially superseded by one-pass Codex prompt. | Assistant | yes if setup chat needs context | Respect current setup canon first. | FACT |
| ARTIFACT-09 | User-provided old current directory tree | pasted file tree | Evidence of prior redundant/outdated launcher layout. | Historical after later refactors. | User | yes as migration history | Contains adapters/core/schemas/tests tree with old files. | FACT |
| ARTIFACT-10 | Canonical repo update prompt | user-pasted prompt | Locked top-level products, engine purity, canonical launcher structure, dependencies. | Authoritative. | User | yes | Major turning point in chat. | FACT |
| ARTIFACT-11 | Plan Continuation: Launcher Realignment | assistant output | Rebased launcher plan to canonical repo. | Relevant if aligned with latest canon. | Assistant | yes | Use as implementation guidance, not higher than user canon. | FACT |
| ARTIFACT-12 | One-pass refactor + repair + future-proof Codex prompt | user-pasted applied prompt | CMake/VS2026 build repair, target normalization, setup/launcher/tools smoke tests. | Applied per user; actual result unverified. | User | yes | Authoritative applied context. | FACT |
| ARTIFACT-13 | Final purity + contract ownership repair Codex prompt | user-pasted applied prompt | Engine purity, neutral contracts, sanity scripts. | Applied per user; actual result unverified. | User | yes | Authoritative applied context. | FACT |
| ARTIFACT-14 | Launcher Spec Completion, Gap Closure, and Documentation Hardening prompt | assistant-generated prompt | Closure task to finish launcher code/docs before future planning. | Not confirmed applied. | Assistant | yes, likely next action | Strictly no feature additions/redesign. | FACT |
| ARTIFACT-15 | Application-layer canon prompt | user-pasted prompt | Applications only, UI/UX, RepoX/versioning, SRZ, allowed work. | Authoritative context. | User | yes | Project-level canon pasted in chat. | PROJECT-CONTEXT |
| ARTIFACT-16 | Latest overall canon prompt from other chat | user-pasted prompt | Full architecture closed, ontology, invariants, APP-CANON, BUILD-ID-0, RepoX/TestX. | Authoritative context. | User | yes | Highest-level project context. | PROJECT-CONTEXT |
| ARTIFACT-17 | Previous Context Transfer Packet | assistant output | Maximum-fidelity handoff for new chat. | Consumed and normalized into this package. | Assistant | yes | This package is derived from and repairs it. | FACT |
| ARTIFACT-18 | This final report package | generated files | Downloadable package for this old chat. | Created by current response. | Assistant | yes | Contains full report, YAML, aggregator packet, registers, brief, audit, manifest, ZIP. | FACT |

### Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant reopens architecture or proposes new layouts. | Wastes time and violates canon. | medium | high | Use canon and rejected options registers; verify before planning. | WORKSTREAM-01 | PROJECT-CONTEXT |
| RISK-02 | Old manual IDE project advice is followed. | Conflicts with CMake-authoritative build and enforcement. | medium | medium-high | Mark as superseded; use CMakePresets. | WORKSTREAM-07 | FACT |
| RISK-03 | Engine contamination reappears. | Engine loses reusability/purity. | medium | critical | Run sanity scripts and CMake include/link checks. | WORKSTREAM-03 | FACT |
| RISK-04 | Launcher becomes installer/repair tool. | Violates setup authority and hides mutation. | medium | high | Restrict to setup invocation contracts. | WORKSTREAM-04 | FACT |
| RISK-05 | UI command semantics diverge between CLI/TUI/GUI. | Breaks canonical CLI and parity. | medium | high | Single command graph and binding validator. | WORKSTREAM-06 | PROJECT-CONTEXT |
| RISK-06 | Hardcoded UI strings or content assumptions persist. | Breaks localisation and zero-pack requirement. | medium | medium-high | Externalize strings; raw-key fallback; zero-pack tests. | WORKSTREAM-06 | PROJECT-CONTEXT |
| RISK-07 | RepoX/BUILD-ID mismatches are silently ignored. | Release/compatibility failures. | medium | high | BUILD-ID-0 tests and loud refusal paths. | WORKSTREAM-08 | PROJECT-CONTEXT |
| RISK-08 | Shared headers remain incorrectly owned. | Boundary regression and hidden coupling. | medium | high | Contract usage audit and header classification. | WORKSTREAM-05 | FACT |
| RISK-09 | This report overstates unverified implementation status. | Future work assumes missing tools/tests exist. | medium | medium | Respect UNCERTAIN labels and run verification queue. | WORKSTREAM-11 | FACT |
| RISK-10 | Aggregator merges assistant suggestions as final decisions. | Spec book gains false requirements. | medium | high | Preserve labels and source hierarchy. | WORKSTREAM-11 | FACT |
| RISK-11 | Uploaded historical files are lost or unavailable. | Some Plan 8 context unavailable. | low-medium | medium | Treat as optional/historical; request re-upload if needed. | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| RISK-12 | Tools mutate or bypass authority. | Could violate read-only/default and epistemics constraints. | low-medium | high | Explicit write gates; tools read-only by default. | WORKSTREAM-09 | PROJECT-CONTEXT |

### Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Run scripts/verify_tree_sanity.bat. | Confirms engine purity and forbidden directories. | Repo script on current checkout. | critical | WORKSTREAM-03 | FACT |
| VERIFY-02 | Run python scripts/verify_includes_sanity.py. | Confirms forbidden cross-product includes are absent. | Repo script on current checkout. | critical | WORKSTREAM-03 | FACT |
| VERIFY-03 | Run cmake --preset vs2026-x64-debug. | Confirms CMakePresets and configure path. | CMake/VS2026 environment. | critical | WORKSTREAM-07 | FACT |
| VERIFY-04 | Run cmake --build --preset vs2026-x64-debug. | Confirms build targets compile. | CMake build output. | critical | WORKSTREAM-07 | FACT |
| VERIFY-05 | Run ctest --preset vs2026-x64-debug. | Confirms test suite baseline. | CTest output. | critical | WORKSTREAM-07 | FACT |
| VERIFY-06 | Run launcher --help from build output. | Confirms launcher executable works. | Built executable. | critical | WORKSTREAM-02 | FACT |
| VERIFY-07 | Run setup --help from build output. | Confirms setup executable works. | Built executable. | critical | WORKSTREAM-04 | FACT |
| VERIFY-08 | Inspect CANON_INDEX.md for required canon IDs. | Docs must cite valid canon anchors. | Repo docs. | high | WORKSTREAM-08 | PROJECT-CONTEXT |
| VERIFY-09 | Inspect launcher/docs status headers and boundary docs. | Ensures docs reflect canon and current implementation. | launcher/docs. | high | WORKSTREAM-02 | FACT |
| VERIFY-10 | Confirm command graph drives CLI help and GUI/TUI bindings. | Required by CLI canonicality. | launcher/ui, tests, tool validators. | high | WORKSTREAM-06 | PROJECT-CONTEXT |
| VERIFY-11 | Confirm UI IR schema and binding validator exist and run in TestX/RepoX. | Required by APP-UI-BIND-0. | schema/, tools/, CI/TestX. | high | WORKSTREAM-06 | PROJECT-CONTEXT |
| VERIFY-12 | Run zero-pack and missing-locale launcher smoke tests. | Confirms app content-agnostic and i18n fallback behavior. | Launcher test suite. | high | WORKSTREAM-02 | PROJECT-CONTEXT |
| VERIFY-13 | Verify launcher displays RepoX changelog/build identity and refuses mismatches. | Required by BUILD-ID-0 and RepoX canon. | Launcher diagnostics/version tests. | high | WORKSTREAM-08 | PROJECT-CONTEXT |
| VERIFY-14 | Open uploaded Plan 8/repo artifacts only if historical Plan 8 details are needed. | Contents were not inspected here. | Uploaded files or re-upload from user. | low | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |

## 6. Possible Cross-Chat Duplicates

Likely duplicates: APP-CANON0/1, APP-AUTO-0, APP-UI-BIND-0, BUILD-ID-0, RepoX/TestX, CLEAN-2, engine purity, setup system, UI IR, CMake/VS2026 build governance, and product-first repository layout.

## 7. Possible Cross-Chat Conflicts

Watch for older chats that treat launcher as engine-hosted, use standalone launcher repo layouts, require hand-authored authoritative IDE projects, place contracts in engine/game, or allow manual changelog editing.

## 8. Spec Book Integration Guidance

Feed this chat into chapters for application layer, launcher, setup/launcher boundary, repo boundaries, build governance, UI/UX, and release governance. Requirements candidates include launcher canonical structure, engine purity, neutral contracts, setup-only install mutation, CMake authoritative build, CLI command graph, UI IR validation, zero-pack app operation, and BUILD-ID-0 mismatch refusal. Keep Minecraft launcher screenshots and Plan 8-specific claims as background/historical unless confirmed elsewhere.

## 9. Aggregator Warnings

Do not treat assistant-generated concrete file names as canon unless the repo confirms them. Do not treat applied Codex prompts as verified implementation without build/script results. Do not erase the supersession of manual IDE project advice. Do not merge project-level canon into this chat as if it originated here; it was pasted from another chat but is authoritative context for this chat.
