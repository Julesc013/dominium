# Full Chat Report — Dominium Launcher Application Layer Handoff

## 0. Report Metadata

| Field | Value |
|---|---|
| Chat label | Dominium Launcher Application Layer Handoff |
| Filesystem-safe label | `dominium_launcher_app_layer_handoff` |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only; project-level material pasted into this chat is labelled PROJECT-CONTEXT. |
| Apparent coverage | Full visible chat coverage, based on visible transcript plus prior Context Transfer Packet. |
| Extraction confidence | 4 / 5 |
| Staleness risk | Medium: repository state and applied Codex prompt results require verification. |
| Future plans present | Yes |
| Pending tasks present | Yes |
| Artifacts/files present | Yes |
| Safe for aggregation | Yes, with caveats about unverified repo state and assistant-generated suggestions. |
| Main limitations | Uploaded file contents and current repository state were not inspected in this final packaging step; applied Codex prompt results are user-reported but unverified here. |

## 1. Executive Summary

This chat was about preserving and hardening the Dominium / Domino application-layer plan, with the Dominium Launcher as the immediate focal product. It began with a concrete launcher question: whether the post-Plan 8 system could support a single common launcher codebase across operating systems, using native OS elements and minimal rendering, inspired by pre-2016 Minecraft launcher examples. The answer evolved through several stages: native widgets require per-platform presentation adapters, while one common launcher “brain” is achieved by separating control-plane logic, interaction semantics, command graph, and platform rendering/input shells.

The early launcher plan was later substantially rebased. Initial suggestions such as a standalone `dominium-launcher/` tree, hand-authored authoritative Visual Studio/Xcode projects, and generic `core/source` directories are now historical and superseded. The user later supplied a canonical product-first repository layout and explicit boundary rules. The current authoritative structure is a monorepo with top-level products including `engine/`, `game/`, `client/`, `server/`, `launcher/`, `setup/`, `tools/`, `libs/`, `schema/`, `docs/`, `ci/`, `sdk/`, and `legacy/`. The launcher is a first-class product under `launcher/`, not an engine subcomponent. The canonical launcher modules are `launcher/core/discover`, `launcher/core/profile`, `launcher/core/invoke`, `launcher/ui`, `launcher/platform`, and `launcher/tests`.

The most important architectural outcome is boundary clarity. Engine purity is non-negotiable: `engine/` must be buildable without launcher/setup/tools, must export only `engine/include/domino/**`, and must not include `dom_contracts`. Cross-product contracts are neutral and live under `libs/contracts/include/dom_contracts`. Setup is the sole authority for install mutation, update, repair, rollback, and installed-state manifests. Launcher consumes setup output only through schemas, manifests, and contracts; it may orchestrate and invoke but must not install, silently repair, mutate installed files, or hide failures.

The user also pasted application-layer canon from another chat. That canon is project-level context but was made authoritative for this chat. It states that architecture is closed and canon locked; this chat exists only for implementation, audit, optimisation, documentation, and maintenance. Applications are content-agnostic orchestration shells. They do not contain gameplay logic, mutate authoritative state, invent defaults, bypass law/authority/epistemics, or bypass RepoX/TestX. CLI is canonical. GUI/TUI are views over the same command graph. UI is data via UI IR, never business logic. Accessibility and localisation are mandatory. Tools are read-only by default. RepoX is the source of truth for changelogs, build metadata, canon-clean tags, and compatibility data. BUILD-ID-0 governs product version strings and mismatch refusal.

Two large Codex prompts were pasted as already applied: one for one-pass refactor/build repair/future-proofing for VS2026+CMake, and one for final engine purity and contract ownership repair. These prompts make CMakePresets the authoritative Visual Studio workflow, require target-based include/link boundaries, introduce or enforce `libs/contracts`, and add sanity scripts such as `verify_tree_sanity.bat` and `verify_includes_sanity.py`. Actual repository success was not independently verified in this chat; all such claims must be checked against the current repo.

The immediate next work is not more planning. The next assistant should first run the verification gates, then determine whether the generated “Dominium Launcher: Spec Completion, Gap Closure, and Documentation Hardening” prompt has been applied. If not, that closure prompt is the correct next action: it documents launcher ownership, boundaries, core modules, interaction model, platform adapters, contract/schema usage, determinism, build workflow, and final status without adding features or redesigning APIs. This report package exists to preserve that state, with stable IDs, uncertainty labels, and aggregation-ready files.

## 2. How to Use This Report

This report covers only this old chat. It is not a whole-project specification, although it includes project-level canon that the user pasted into this chat. Items labelled `PROJECT-CONTEXT` are sourced from project-level context introduced here, not independently verified from source files. Items labelled `UNCERTAIN / UNVERIFIED` must not be treated as facts until checked against the repository or user confirmation.

Direct user statements outrank assistant suggestions. Later user-supplied canon outranks earlier assistant-generated plans. Superseded options are preserved so future assistants do not repeat them. Tentative assistant recommendations, such as concrete filenames for UI IR artifacts, are not canon unless the repository or user later confirms them.

External-world facts and tool/version details, including Visual Studio 2026 behavior, CMake availability, and file existence in the current repository, require verification before future use. This report is designed for later master-spec aggregation: merge by stable IDs and source labels, preserve contradictions, and do not silently promote inferences into requirements.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Source type | Source basis | Strength | Implication | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Responses should start with model/date/time prefix. | Explicit | User profile instruction. | strong | Future assistants should preserve requested prefix when possible. | May conflict with strict output formats; higher-priority instructions win. | FACT |
| PREF-02 | Epistemic accuracy, decision utility, long-term correctness. | Explicit | User profile. | strong | Prioritize rigorous labeled facts over engagement. | Overconfident inference will frustrate user. | FACT |
| PREF-03 | Correctly cited sources and unbiased rigorously tested facts. | Explicit | User profile. | strong | Use citations/verification when external or current facts matter. | Unverified current claims should be labelled. | FACT |
| PREF-04 | Deliver answers, not dialogue; ask only if missing info blocks correctness. | Explicit | User profile. | medium-high | Prefer concrete outputs and next actions. | Unnecessary questions slow implementation. | FACT |
| PREF-07 | Preserve uncertainty, rejected options, and changes of direction. | Explicit | Context transfer/package request. | strong | Do not compress away superseded options. | Future aggregation may repeat mistakes. | FACT |

### 3.2 Inferred Preferences

| ID | Preference | Source type | Source basis | Strength | Implication | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-05 | Mechanical enforcement over convention. | Inferred | Repeated emphasis on CMake/CI/scripts/boundaries. | high | Design prompts should include scripts, tests, stop conditions. | Purely aspirational docs may be rejected. | INFERENCE |
| PREF-06 | Codex-style phased prompts with commits and verification commands. | Inferred | User repeatedly requested/generated such prompts. | high | When asked for prompts, use execution phases and stop conditions. | Vague plans will be less useful. | INFERENCE |

### 3.3 Preferences Not Established by This Chat

- FACT: The chat does not establish a preference for a specific final GUI toolkit.
- FACT: The chat does not establish that a specific UI IR file format has already been implemented.
- FACT: The chat does not establish that the user wants hand-authored IDE projects to remain authoritative; later prompts explicitly supersede that.
- FACT: The chat does not establish tolerance for hidden defaults, silent repair, or architecture redesign; it establishes the opposite.

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Dominium / Domino application-layer canon | Continue implementation, audit, optimisation, and maintenance for applications without redesigning the closed engine/game/simulation architecture. | Architecture and canon were stated as closed/locked. The chat is now scoped to application-layer implementation and maintenance only. | All application work proceeds within APP-CANON0/1, APP-AUTO-0, APP-UI-BIND-0, BUILD-ID-0, RepoX/TestX/VALIDATE-0, and the product-first repo structure. | active | critical | high | PROJECT-CONTEXT |
| WORKSTREAM-02 | Dominium Launcher product | Maintain and harden the launcher as a first-class product and reference application. | Launcher was realigned to the canonical product layout. A closure prompt was generated to bring code and docs up to spec. It is not confirmed in this chat that the closure prompt has been applied. | Launcher builds, runs, documents its boundaries, uses common command graph/UI IR, passes zero-pack smoke tests, and does not violate product boundaries. | active | critical | high for plan; medium for implementation status | FACT |
| WORKSTREAM-03 | Engine purity and boundary enforcement | Ensure engine remains reusable and independent, with no launcher/setup/tools/contracts contamination. | User stated two Codex prompts have been applied, including final purity and contract ownership repair. Actual repository state was not verified in this chat. | engine/ contains only include/domino, modules, render, tests, CMakeLists.txt; engine does not include dom_contracts or app/product internals. | active verification target | critical | medium until repo verification | FACT |
| WORKSTREAM-04 | Setup product and launcher/setup boundary | Keep setup as the sole install mutation authority and launcher as a consumer/invoker via contracts. | Setup was covered by an earlier generated setup prompt and by the applied one-pass refactor prompt. Actual implementation is unverified. | setup builds and runs at least CLI help; setup owns install, update, verify, repair, rollback, and installed-state manifests. | active boundary condition | critical | high for rule; medium for implementation | FACT |
| WORKSTREAM-05 | Neutral contracts and canonical schemas | Use libs/contracts and schema as the only cross-product channels. | The final purity prompt introduced libs/contracts/include/dom_contracts. The latest canon requires schemas and manifests as setup-launcher channels. | All cross-product data is schema-defined or dom_contracts-defined; product internals are not included across boundaries. | active | critical | high for desired model; medium for implementation | FACT |
| WORKSTREAM-06 | UI command graph, UI IR, accessibility, and localisation | Ensure CLI/TUI/GUI share one canonical command graph and UI is data, not logic. | Application canon requires this. Assistant suggested concrete artifacts such as launcher/ui/command_graph and schema/ui. Implementation status is unknown. | CLI canonical; GUI/TUI views over command graph; UI IR validates bindings, strings, accessibility, keyboard navigation, localisation fallback. | active, likely incomplete until verified | high | high for requirements; unknown implementation | FACT |
| WORKSTREAM-07 | VS2026, CMake, CI, and build/test gates | Use CMakePresets and target-based boundaries to build and verify the repo, especially on Visual Studio 2026. | One-pass Codex prompt required CMakePresets, target graph normalization, setup/launcher/tools builds, and CTest smoke tests. Actual result unverified. | Open Folder in VS2026 works; cmake configure/build/ctest pass; launcher/setup help run. | active verification target | critical | medium until repo verification | FACT |
| WORKSTREAM-08 | RepoX, TestX, VALIDATE-0, and BUILD-ID-0 governance | Enforce canon, versioning, changelogs, compatibility, schema validation, and UI binding validation mechanically. | Latest canon locks these systems. Implementation status is not verified in this chat. | RepoX/TestX gates prevent invalid states; applications display build IDs/changelogs and refuse mismatches loudly. | active | critical | high for requirement; unknown implementation | PROJECT-CONTEXT |
| WORKSTREAM-09 | Tools and validators | Keep tools first-class, read-only by default, and use them for validation such as UI binding/schema checks. | Tools are part of canonical layout. UI binding validator was recommended but implementation unknown. | tools/_shared and tools validators build; tools do not include launcher/setup internals; write modes explicit. | active | medium-high | medium | FACT |
| WORKSTREAM-10 | Client and server application constraints | Preserve client/server app-layer boundaries while focusing on launcher. | Mentioned in application canon; not directly implemented in this chat. | Client handles presentation/input/inspection with no authority; server is headless-first and authoritative/SRZ-aware. | background active | medium | high for constraints; no implementation facts | PROJECT-CONTEXT |
| WORKSTREAM-11 | This chat handoff and report package | Produce a final downloadable, shareable, reusable report package for this old chat. | This package is being generated from the previous context transfer packet and visible chat context. | Seven report files plus ZIP exist and are safe for later aggregation with caveats. | active finalization | critical for continuity | high | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — Dominium / Domino application-layer canon

- Label: PROJECT-CONTEXT
- Objective: Continue implementation, audit, optimisation, and maintenance for applications without redesigning the closed engine/game/simulation architecture.
- Background: User pasted project-level canon from another chat into this chat, including ontology, invariants, application-layer rules, and build governance.
- Current state: Architecture and canon were stated as closed/locked. The chat is now scoped to application-layer implementation and maintenance only.
- Desired end state: All application work proceeds within APP-CANON0/1, APP-AUTO-0, APP-UI-BIND-0, BUILD-ID-0, RepoX/TestX/VALIDATE-0, and the product-first repo structure.
- Importance: This is the authority boundary preventing future assistants from re-opening engine/game/simulation design.
- Decisions made: Architecture closed; applications are orchestration shells; applications do not contain gameplay logic or mutate authoritative state.
- Decisions pending: None at architecture level; implementation verification remains pending.
- Pending tasks: Verify canon anchors and app docs; ensure app tooling enforces constraints.
- Constraints: No redesign; no hidden defaults; no bypassing RepoX/TestX; content-agnostic apps.
- Dependencies: CANON_INDEX.md, APP-CANON0/1, APP-AUTO-0, APP-UI-BIND-0, BUILD-ID-0, RepoX, TestX.
- Timeline / sequencing: Must be treated as prior context before any launcher implementation work.
- Blockers: Unknown current repo state.
- Risks: Assistant may re-plan or reinterpret canon.
- Artifacts: Latest application-layer canon prompt; latest overall canon prompt.
- Success criteria: Future work treats canon as locked and verifies implementation against it.
- Recommended next action: Use this report to bootstrap the next chat, then run repo verification gates.
- Verification needed: Confirm repo docs and scripts actually encode the canon.
- Confidence: high
- Carry-forward priority: highest
### WORKSTREAM-02 — Dominium Launcher product

- Label: FACT
- Objective: Maintain and harden the launcher as a first-class product and reference application.
- Background: Initial discussion was about a fast native cross-platform launcher similar to pre-2016 Minecraft launchers, then shifted into product-first repo governance.
- Current state: Launcher was realigned to the canonical product layout. A closure prompt was generated to bring code and docs up to spec. It is not confirmed in this chat that the closure prompt has been applied.
- Desired end state: Launcher builds, runs, documents its boundaries, uses common command graph/UI IR, passes zero-pack smoke tests, and does not violate product boundaries.
- Importance: The launcher is the reference application and sets patterns for setup, tools, client, and server frontends.
- Decisions made: Launcher lives under launcher/; canonical structure uses core/discover, core/profile, core/invoke, ui, platform, tests.
- Decisions pending: Whether current implementation has command graph, UI IR binding validation, RepoX integration, and complete docs.
- Pending tasks: Run launcher hardening prompt or audit its results.
- Constraints: No setup internals; no engine internals; no gameplay logic; no install mutation; content-agnostic.
- Dependencies: libs/, schema/, libs/contracts/, engine public API, optional game metadata/launch contracts.
- Timeline / sequencing: Complete launcher code/doc hardening before regenerating further plans.
- Blockers: Current repo state and closure prompt application status unknown.
- Risks: Reintroducing older standalone launcher layout or adapter-level business logic.
- Artifacts: Launcher master prompt, realignment plan, hardening prompt.
- Success criteria: launcher --help passes; docs/status headers present; boundary checks pass; zero-pack tests pass.
- Recommended next action: Verify repo gates and execute/audit the hardening prompt phases.
- Verification needed: Inspect launcher tree, CMake targets, docs, tests, command graph, UI IR.
- Confidence: high for plan; medium for implementation status
- Carry-forward priority: highest
### WORKSTREAM-03 — Engine purity and boundary enforcement

- Label: FACT
- Objective: Ensure engine remains reusable and independent, with no launcher/setup/tools/contracts contamination.
- Background: A prior prompt listed violations such as engine/include/dsu, engine/include/dui, engine/launcher_core_launcher, engine/setup_core_setup, engine/source, engine/external/xxhash.
- Current state: User stated two Codex prompts have been applied, including final purity and contract ownership repair. Actual repository state was not verified in this chat.
- Desired end state: engine/ contains only include/domino, modules, render, tests, CMakeLists.txt; engine does not include dom_contracts or app/product internals.
- Importance: Engine purity is non-negotiable and protects the reusable deterministic engine from application-layer churn.
- Decisions made: Non-engine content is evicted to legacy or correct owners; neutral contracts are not engine-owned.
- Decisions pending: Any ambiguous headers must be classified if found.
- Pending tasks: Run verify_tree_sanity and verify_includes_sanity.
- Constraints: Engine C89; public headers parseable forever; no C++ ABI leakage.
- Dependencies: CMake enforcement; sanity scripts; include ownership.
- Timeline / sequencing: Verification must precede further launcher planning.
- Blockers: Unverified current tree.
- Risks: Hidden include paths or legacy references can keep contamination alive.
- Artifacts: Final purity Codex prompt; verify scripts.
- Success criteria: Scripts pass; engine builds without launcher/setup/tools.
- Recommended next action: Run the verification commands.
- Verification needed: Actual repository inspection.
- Confidence: medium until repo verification
- Carry-forward priority: highest
### WORKSTREAM-04 — Setup product and launcher/setup boundary

- Label: FACT
- Objective: Keep setup as the sole install mutation authority and launcher as a consumer/invoker via contracts.
- Background: User repeatedly distinguished launcher from setup; launcher must not install software.
- Current state: Setup was covered by an earlier generated setup prompt and by the applied one-pass refactor prompt. Actual implementation is unverified.
- Desired end state: setup builds and runs at least CLI help; setup owns install, update, verify, repair, rollback, and installed-state manifests.
- Importance: Prevents silent repairs, hidden mutation, and architectural leakage.
- Decisions made: Launcher/setup communicate only via schema/manifests/contracts; setup owns installed-state mutation.
- Decisions pending: Whether existing launcher code has any leftover repair/install paths.
- Pending tasks: Run setup --help; scan launcher includes/links for setup internals.
- Constraints: No setup internals in launcher; no hidden mutation.
- Dependencies: schema/, libs/contracts/, setup product build.
- Timeline / sequencing: Boundary verification belongs in launcher hardening phase.
- Blockers: Repo not inspected in this report-generation step.
- Risks: Launcher convenience actions may become install repair logic.
- Artifacts: Setup master prompt; one-pass Codex prompt.
- Success criteria: setup help works; launcher invokes setup only through declared contracts.
- Recommended next action: Verify boundary with include script and tests.
- Verification needed: Inspect launcher/setup integration.
- Confidence: high for rule; medium for implementation
- Carry-forward priority: high
### WORKSTREAM-05 — Neutral contracts and canonical schemas

- Label: FACT
- Objective: Use libs/contracts and schema as the only cross-product channels.
- Background: Earlier contamination involved game/include/dominium exporting launcher/setup/tool APIs and engine exporting dsu/dui.
- Current state: The final purity prompt introduced libs/contracts/include/dom_contracts. The latest canon requires schemas and manifests as setup-launcher channels.
- Desired end state: All cross-product data is schema-defined or dom_contracts-defined; product internals are not included across boundaries.
- Importance: Neutral ownership prevents product coupling and future boundary regression.
- Decisions made: launcher/setup/tools/game may include dom_contracts; engine must not.
- Decisions pending: Exact contract coverage for build IDs, launch requests, product manifests, command graph, UI IR remains implementation-dependent.
- Pending tasks: Enumerate contracts used by launcher; add docs/CONTRACT_USAGE.md in launcher hardening.
- Constraints: No foreign product private headers.
- Dependencies: libs/contracts target; schema validation; CMake target include dirs.
- Timeline / sequencing: Must be audited before further features.
- Blockers: Unknown current header set.
- Risks: Shared headers might be incorrectly placed in game or tools.
- Artifacts: libs/contracts target definition from prompt; schema references.
- Success criteria: Contract usage documented and enforced; schema validation passes.
- Recommended next action: Inspect include graph and contract headers.
- Verification needed: Actual file and CMake target inspection.
- Confidence: high for desired model; medium for implementation
- Carry-forward priority: highest
### WORKSTREAM-06 — UI command graph, UI IR, accessibility, and localisation

- Label: FACT
- Objective: Ensure CLI/TUI/GUI share one canonical command graph and UI is data, not logic.
- Background: The user clarified that CLI/TUI/GUI core functionality belongs in one common core; later canon locked UI IR and command graph requirements.
- Current state: Application canon requires this. Assistant suggested concrete artifacts such as launcher/ui/command_graph and schema/ui. Implementation status is unknown.
- Desired end state: CLI canonical; GUI/TUI views over command graph; UI IR validates bindings, strings, accessibility, keyboard navigation, localisation fallback.
- Importance: Prevents divergent UI behavior and supports accessibility, localisation, portability, and deterministic automation.
- Decisions made: CLI is canonical; UI is data; no business logic embedded in UI.
- Decisions pending: Exact file format and location for command graph/UI IR if not already established in repo.
- Pending tasks: Verify command graph, UI IR schema, binding validator, and zero-pack/missing-locale tests.
- Constraints: All strings externalised; no color-only semantics; keyboard-only operation; screen reader tags.
- Dependencies: schema/, tools validator, launcher/ui, TestX/RepoX gates.
- Timeline / sequencing: Should be included in launcher spec completion before new plans.
- Blockers: No repo inspection in this step.
- Risks: Treating assistant-suggested filenames as locked canon; only the requirements are locked unless files exist.
- Artifacts: APP-UI-BIND-0, UI/UX canon, assistant checklist.
- Success criteria: Binding validator passes; CLI/TUI/GUI parity is mechanically checked.
- Recommended next action: Inspect current UI implementation and add missing docs/tests under closure scope.
- Verification needed: Repo files and tests.
- Confidence: high for requirements; unknown implementation
- Carry-forward priority: high
### WORKSTREAM-07 — VS2026, CMake, CI, and build/test gates

- Label: FACT
- Objective: Use CMakePresets and target-based boundaries to build and verify the repo, especially on Visual Studio 2026.
- Background: Earlier manual IDE project advice was superseded by CMake as authoritative.
- Current state: One-pass Codex prompt required CMakePresets, target graph normalization, setup/launcher/tools builds, and CTest smoke tests. Actual result unverified.
- Desired end state: Open Folder in VS2026 works; cmake configure/build/ctest pass; launcher/setup help run.
- Importance: Build graph enforces architecture and enables Codex/CI workflows.
- Decisions made: CMake generates VS projects; no hand-written vcxproj as authoritative build.
- Decisions pending: Whether current presets and smoke tests pass.
- Pending tasks: Run cmake --preset vs2026-x64-debug; build; ctest; help commands.
- Constraints: No global include dirs; target_include_directories with PUBLIC/PRIVATE.
- Dependencies: CMakePresets.json; scripts; CTest; product CMakeLists.
- Timeline / sequencing: First verification step in new chat.
- Blockers: Actual environment/toolchain availability.
- Risks: Old IDE advice may be revived; CMake target graph may be incomplete.
- Artifacts: One-pass Codex prompt; docs/BUILDING.md requirement.
- Success criteria: All specified verification commands pass.
- Recommended next action: Run commands and record results.
- Verification needed: Actual build output.
- Confidence: medium until repo verification
- Carry-forward priority: highest
### WORKSTREAM-08 — RepoX, TestX, VALIDATE-0, and BUILD-ID-0 governance

- Label: PROJECT-CONTEXT
- Objective: Enforce canon, versioning, changelogs, compatibility, schema validation, and UI binding validation mechanically.
- Background: User pasted versioning model and application automation requirements.
- Current state: Latest canon locks these systems. Implementation status is not verified in this chat.
- Desired end state: RepoX/TestX gates prevent invalid states; applications display build IDs/changelogs and refuse mismatches loudly.
- Importance: Prevents manual drift and release-governance failures.
- Decisions made: No manual changelog editing; no distributed artifact without GBN; build identity format locked.
- Decisions pending: How launcher currently surfaces RepoX metadata.
- Pending tasks: Verify CANON_INDEX, RepoX outputs, build identity parsing/enforcement, TestX gates.
- Constraints: GBN only centrally allocated for beta/rc/release/hotfix; dev/ci use BII.
- Dependencies: RepoX metadata, TestX gates, schema validation, UI binding validator.
- Timeline / sequencing: Should be audited as part of launcher hardening.
- Blockers: Unknown current tooling state.
- Risks: Manual changelogs or silent version mismatch.
- Artifacts: BUILD-ID-0; APP-AUTO-0; APP-UI-BIND-0.
- Success criteria: Launcher displays generated changelogs/build IDs and refuses incompatible product mismatches.
- Recommended next action: Add to verification queue and tests.
- Verification needed: Inspect/build/run tooling.
- Confidence: high for requirement; unknown implementation
- Carry-forward priority: highest
### WORKSTREAM-09 — Tools and validators

- Label: FACT
- Objective: Keep tools first-class, read-only by default, and use them for validation such as UI binding/schema checks.
- Background: Tools were elevated from utility folder to first-class products in earlier structural discussion and later canon.
- Current state: Tools are part of canonical layout. UI binding validator was recommended but implementation unknown.
- Desired end state: tools/_shared and tools validators build; tools do not include launcher/setup internals; write modes explicit.
- Importance: Validation and inspection should not mutate authoritative state or become hidden product dependencies.
- Decisions made: Tools are read-only by default; tools use tools/_shared plus libs/contracts/schema as needed.
- Decisions pending: Exact validator inventory.
- Pending tasks: Verify UI binding validator and schema validators.
- Constraints: No launcher/setup internals unless public; explicit --write for mutation if ever allowed.
- Dependencies: TestX/RepoX integration.
- Timeline / sequencing: After base build verification, before relying on UI/command graph.
- Blockers: Unknown tools tree.
- Risks: Validators missing or not wired to CI.
- Artifacts: One-pass Codex prompt tools phase; APP-UI-BIND-0.
- Success criteria: Required validators build and run in CI/TestX.
- Recommended next action: Inspect tools targets.
- Verification needed: Current repo inspection.
- Confidence: medium
- Carry-forward priority: medium
### WORKSTREAM-10 — Client and server application constraints

- Label: PROJECT-CONTEXT
- Objective: Preserve client/server app-layer boundaries while focusing on launcher.
- Background: Canonical top-level products include client/ and server/. Latest canon specifies their app responsibilities.
- Current state: Mentioned in application canon; not directly implemented in this chat.
- Desired end state: Client handles presentation/input/inspection with no authority; server is headless-first and authoritative/SRZ-aware.
- Importance: Future plans should not confuse launcher/client/server roles.
- Decisions made: Client no authority; server assigns SRZ authority; apps do not change SRZ authority.
- Decisions pending: None in this chat.
- Pending tasks: None before launcher closure.
- Constraints: No UI assumptions for server; no world mutation by client UI.
- Dependencies: Engine/game public APIs, SRZ-0 canon.
- Timeline / sequencing: Deferred until launcher/spec closure.
- Blockers: Not in scope.
- Risks: Future assistant may conflate launcher/client/server.
- Artifacts: Latest application canon.
- Success criteria: Future implementation preserves roles.
- Recommended next action: Do not act until launcher closure unless user asks.
- Verification needed: None for this chat beyond noting scope.
- Confidence: high for constraints; no implementation facts
- Carry-forward priority: medium
### WORKSTREAM-11 — This chat handoff and report package

- Label: FACT
- Objective: Produce a final downloadable, shareable, reusable report package for this old chat.
- Background: User explicitly requested a maximum-fidelity Context Transfer Packet, then requested this final package.
- Current state: This package is being generated from the previous context transfer packet and visible chat context.
- Desired end state: Seven report files plus ZIP exist and are safe for later aggregation with caveats.
- Importance: Prevents context loss when the chat is retired.
- Decisions made: Chat label inferred as Dominium Launcher Application Layer Handoff.
- Decisions pending: None.
- Pending tasks: Download and store package files.
- Constraints: Do not invent facts; label uncertainty; include stable IDs; create actual files if possible.
- Dependencies: Visible conversation and previous packet.
- Timeline / sequencing: Final action in this chat.
- Blockers: None.
- Risks: Over-compression or future aggregation misread.
- Artifacts: All files in this package.
- Success criteria: Files created and ZIP downloadable.
- Recommended next action: Save ZIP and key Markdown/YAML files.
- Verification needed: User should inspect manifest and audit file.
- Confidence: high
- Carry-forward priority: highest


## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | Asked whether post-Plan 8 system supports common launcher with native OS elements and minimal/no renderer. | Established target UX and architectural question. | Framed common-codebase/native-ui launcher problem. | historical goal context | high |
| 02 | Assistant answered Plan 8 supports common codebase via renderer path but not native widgets without new UI abstraction. | Introduced need for per-OS native backends or UI facade. | Clarified renderer-vs-native-widget tradeoff. | partly superseded by UI IR/application canon | medium |
| 03 | User asked how to make desires reality. | Assistant proposed DUI facade, common launcher core, native backends, DGFX fallback. | First modular launcher strategy. | historical; carry common core/native-shell idea only | medium |
| 04 | User asked about modularity/extensibility with mods/packs. | Assistant proposed facade/registry/TLV and data-first pack extensions. | Connected launcher extensibility to existing systems. | use only if aligned with schema/contracts canon | medium |
| 05 | User pasted launcher master prompt and requested Phase 1. | Launcher core architecture defined as deterministic control-plane library. | Produced initial launcher concepts. | rebased under launcher/core/discover/profile/invoke | high |
| 06 | VS/Xcode project location and generation discussion. | Assistant initially recommended manual IDE projects, then manual+generated. | IDE strategy discussed. | superseded by CMake-authoritative applied prompt | high |
| 07 | User requested and received initial box-drawing launcher tree. | Standalone dominium-launcher tree proposed. | Helped think through migration. | superseded | high |
| 08 | CLI/TUI/GUI common functionality discussion. | User clarified common core; assistant distinguished shared interaction semantics from presentation adapters. | Precursor to command graph/UI IR model. | active concept under app canon | high |
| 09 | Setup prompt generated. | Created setup-system prompt analogous to launcher. | Clarified setup vs launcher roles. | partly superseded by applied Codex prompt | high |
| 10 | User provided old directory tree and asked for improvement. | Assistant diagnosed core contamination, adapter drift, macOS taxonomy issue. | Identified structural problems. | historical migration evidence | high |
| 11 | Product-first repo structure discussion. | Assistant recommended product-first top-level and no generic source dirs. | Moved away from layer-first/standalone layout. | concept adopted/refined by user canonical layout | high |
| 12 | User locked canonical repo and launcher structure. | Top-level products, engine purity, canonical launcher location, dependencies, include ownership became authoritative. | Major turning point; superseded older layouts. | current law | high |
| 13 | Assistant realigned launcher plan to canonical repo. | Launcher became first-class product with core/discover/profile/invoke/ui/platform. | Updated plan to current filesystem law. | active guidance | high |
| 14 | User pasted two applied Codex prompts. | CMake/VS2026/build enforcement and engine purity/contracts repairs treated as applied. | CMake became authoritative and libs/contracts introduced. | active, but implementation unverified | high for prompt text; medium for results |
| 15 | Assistant summarized applied-prompt implications. | Immediate verification gates and contract-surface sections were recommended. | Defined next verification posture. | active | high |
| 16 | User requested launcher code/docs up-to-spec prompt before future plans. | Assistant generated closure/hardening prompt. | Set next action: finish docs/code, do not redesign. | likely immediate next action | high |
| 17 | User pasted application-layer canon. | Apps are content-agnostic orchestration shells; UI/UX, RepoX, SRZ rules locked. | Expanded launcher context to all applications. | current law | high |
| 18 | User pasted latest overall canon from another chat. | Ontology, invariants, APP-CANON, BUILD-ID-0, RepoX/TestX governance locked. | Highest-level project context for implementation work. | current law | high |
| 19 | Assistant produced prior Context Transfer Packet. | Conversation state was preserved for a new chat. | Base for this final report package. | consumed and normalized here | high |
| 20 | User requested final downloadable report package. | This package was created with stable IDs, registers, YAML, and ZIP. | Makes chat reusable and aggregatable. | final output | high |

## 7. Decisions

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

Highest-impact decisions: the launcher is a first-class product under `launcher/`; engine purity is non-negotiable; cross-product contracts belong in `libs/contracts`; CMake is authoritative for VS2026; setup is the sole install mutation authority; CLI is canonical; UI is data; RepoX/TestX/BUILD-ID-0 govern application release and compatibility behavior. These decisions override earlier assistant suggestions where conflicts exist.

## 8. Pending Tasks and Next Actions

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

### 8.1 Recommended Task Order

1. Run verification gates: tree sanity, include sanity, CMake configure/build, CTest, launcher/setup help.
2. Determine whether the launcher hardening prompt has been applied.
3. If not applied, execute its phases without adding features or redesigning APIs.
4. Verify CANON_INDEX, docs status headers, command graph, UI IR, binding validator, zero-pack tests, RepoX/build identity behavior.
5. Only after closure, regenerate further implementation plans from the hardened current state.

### 8.2 Blocked Tasks

- Further launcher feature planning is blocked until current implementation and docs are verified.
- Contract/header relocation decisions are blocked if header ownership is ambiguous.
- UI binding enforcement is blocked if UI IR schema or validator does not yet exist.

### 8.3 Quick Wins

- Run sanity/build/test commands.
- Inspect `launcher/docs`.
- Check `CANON_INDEX.md`.
- Confirm `launcher --help` and `setup --help`.

### 8.4 Tasks Requiring Verification

Tasks TASK-01 through TASK-11 all require current repository verification before claims can be made.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

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

### 9.2 Soft Preferences

No purely soft project preferences dominated this chat. Most preferences were hard constraints or strong implementation preferences.

### 9.3 Technical Constraints

Key technical constraints include C89 engine, C++98 game, CMake as authoritative build, public header stability, target-based includes, no engine contamination, and UI IR/command graph validation.

### 9.4 Time / Resource Constraints

No explicit calendar timeline was established. Sequencing constraints were established: verification and launcher hardening precede further plan regeneration.

### 9.5 Legal / Ethical / Safety Constraints

No legal advice or safety-sensitive external facts were decided. The relevant safety-like constraints are project-internal: do not bypass authority, epistemics, determinism, or install mutation boundaries.

### 9.6 Evidence / Citation Requirements

The user generally prefers rigorous facts and citations. For this report, the evidence base is the visible chat. External facts and current software behavior should be verified before future use.

### 9.7 Formatting / Output Requirements

For this package, the user required structured headings, tables, stable IDs, consistent terminology, and downloadable files if possible.

### 9.8 Things to Avoid

Avoid redesigning architecture, reintroducing old layouts, treating assistant suggestions as canon, inventing facts, weakening constraints, manual changelogs, hardcoded UI strings, and launcher install mutation.

## 10. Open Questions and Unresolved Issues

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

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Launcher as engine subcomponent. | superseded/rejected | Violates engine purity and canonical product-first layout. | final | Only reconsider if canon explicitly changes. | WORKSTREAM-02 | FACT |
| REJECTED-02 | Launcher code or headers inside engine/. | rejected | Violates engine ownership and purity. | final | Never under current canon. | WORKSTREAM-03 | FACT |
| REJECTED-03 | Engine exporting setup/launcher/tool headers. | rejected | Engine include must export only domino engine ABI. | final | Never under current canon. | WORKSTREAM-03 | FACT |
| REJECTED-04 | Hand-authored VS/Xcode projects as authoritative build graph. | superseded | Applied prompt requires CMake-generated VS solution/projects. | final as authoritative build | Native designer artifacts may exist only if CMake remains authoritative. | WORKSTREAM-07 | FACT |
| REJECTED-05 | Standalone dominium-launcher/ repository tree as current plan. | superseded | Canonical repo is product-first monorepo with launcher/. | final under current repo | Only if project intentionally splits repos later. | WORKSTREAM-02 | FACT |
| REJECTED-06 | Generic source/ or core/source/ directories. | rejected | User objected to source-within-source; later canon forbids generic source dirs. | final | Avoid unless canon changes. | WORKSTREAM-02 | FACT |
| REJECTED-07 | CLI/TUI/GUI business logic separately per platform adapter. | rejected | CLI canonical and common command graph require shared semantics. | final | Platform presentation/input remains separate. | WORKSTREAM-06 | PROJECT-CONTEXT |
| REJECTED-08 | Platform adapters inventing commands or resolving profiles/packs. | rejected | Adapters are host/UI glue only; business logic belongs in launcher core/ui command graph. | final | Never under current canon. | WORKSTREAM-02 | FACT |
| REJECTED-09 | Launcher directly installing, repairing, or mutating installed files. | rejected | Setup is only install mutation authority. | final | Launcher may invoke setup repair via contract only. | WORKSTREAM-04 | FACT |
| REJECTED-10 | Launcher reading engine/setup/game internals for capabilities or state. | rejected | Dependencies restrict to public APIs, schemas, and contracts. | final | Add public API/schema/contract if needed. | WORKSTREAM-05 | FACT |
| REJECTED-11 | Manual changelog editing. | rejected | RepoX generates changelogs from commits. | final | Never for canonical/distributed artifacts. | WORKSTREAM-08 | PROJECT-CONTEXT |
| REJECTED-12 | Hardcoded UI strings or color-only UI semantics. | rejected | Accessibility and localisation canon requires externalised strings and non-color semantics. | final | Temporary stubs must be documented and replaced. | WORKSTREAM-06 | PROJECT-CONTEXT |
| REJECTED-13 | UI business logic embedded in widgets or event handlers. | rejected | UI is data and bindings map to command graph/intents. | final | Never under current canon. | WORKSTREAM-06 | PROJECT-CONTEXT |

Preserving these rejected and superseded options is important because this chat changed direction several times. Without this register, a future assistant might revive the standalone launcher tree, manual authoritative IDE projects, or launcher-in-engine assumptions that are now explicitly invalid.

## 12. Artifact Ledger

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

## 13. Rationale and Assumptions

Major choices were made to preserve long-term correctness and mechanical enforceability. Product-first layout prevents layers and products from being mixed. Engine purity protects reusable deterministic engine code from application churn. Neutral contracts prevent game or engine headers from becoming dumping grounds for cross-product APIs. CMake as authoritative build graph supports Visual Studio Open Folder while preserving boundary enforcement through target include/link rules.

The common CLI/TUI/GUI approach was refined from earlier adapter discussion into a stricter command graph/UI IR model. The rationale is parity, scriptability, accessibility, localisation, and testability. UI presentation can vary by platform, but command semantics must not.

The key assumptions are that the user-reported Codex prompts were applied and that the current repo is close to the target state. These assumptions remain unverified in this report. Future assistants must verify actual files, scripts, build output, and tests before making claims.

## 14. Risks and Failure Modes

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

## 15. Verification Queue

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

## 16. Spec Book Contribution Notes

Likely future Project Spec Book sections:
- Repository Architecture and Product Boundaries
- Engine Purity and Public API Ownership
- Application Layer Canon
- Launcher Product Specification
- Setup/Launcher Contract
- UI Command Graph and UI IR
- Accessibility and Localisation Requirements
- Build, CMake, CI, VS2026 Workflow
- RepoX/TestX/BUILD-ID Governance
- Contract and Schema Ownership

Unique contributions from this chat:
- Launcher-specific migration from Plan 8/native launcher discussion to canonical product-first repo.
- Supersession of manual IDE-project advice by CMake-authoritative VS2026 workflow.
- Explicit launcher closure/hardening prompt.
- Detailed boundary mapping for launcher/setup/engine/contracts.

Likely duplicate topics in other chats:
- APP-CANON0/1, BUILD-ID-0, RepoX/TestX, CLEAN-2, engine purity, setup system, UI IR.

Conflicts to watch:
- Older assistant advice vs later user canon.
- Concrete assistant-suggested filenames vs actual repo implementation.
- User-reported applied prompts vs actual build state.

Items that should become formal requirements:
- Launcher canonical structure.
- CMake-authoritative VS workflow.
- No launcher/setup/tools in engine.
- CLI canonical command graph.
- UI IR binding validation.
- Zero-pack launcher operation.
- RepoX changelog/build identity display and mismatch refusal.

Items that should remain background:
- Minecraft launcher images as UX inspiration.
- Plan 8 details unless needed for historical traceability.
- Superseded standalone launcher tree.

Items needing user or repo confirmation:
- Current repo status after applied prompts.
- Whether launcher hardening prompt has been executed.
- Exact command graph/UI IR file names and validator implementation.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Architecture is closed; no redesign. | canon | Prevents re-litigation of settled systems. | Assistant may restart planning. | PROJECT-CONTEXT | high |
| 2 | Launcher is first-class under launcher/. | repo boundary | Prevents engine contamination. | Launcher code may be placed in engine or legacy layouts. | FACT | high |
| 3 | Engine purity: only domino engine ABI under engine/include. | boundary | Engine reuse and build independence. | Cross-product pollution. | FACT | high |
| 4 | Neutral contracts live in libs/contracts/include/dom_contracts. | dependency | Shared contracts need neutral ownership. | Contracts drift into game/engine internals. | FACT | high |
| 5 | Setup is the sole install mutation authority. | application boundary | Prevents hidden repair/mutation by launcher. | Launcher becomes package manager. | FACT | high |
| 6 | CMake is authoritative for VS2026; manual IDE advice is superseded. | build | Target graph enforces boundaries. | Conflicting project files and include leakage. | FACT | high |
| 7 | CLI canonical; GUI/TUI views over command graph. | UI architecture | Parity and scriptability. | Divergent UI semantics. | PROJECT-CONTEXT | high |
| 8 | UI is data via UI IR, no business logic. | UI architecture | Accessibility/localisation/portability. | Unvalidated GUI logic. | PROJECT-CONTEXT | high |
| 9 | RepoX/TestX/BUILD-ID-0 must not be bypassed. | governance | Canon and release enforcement. | Manual drift and version mismatches. | PROJECT-CONTEXT | high |
| 10 | Run verification before acting. | process | Applied prompt results are unverified here. | Future work based on false assumptions. | FACT | high |
| 11 | Launcher hardening prompt is likely next action if not already applied. | task | Prepares code/docs before new plans. | Plans generated from implicit/incomplete state. | FACT | medium-high |
| 12 | Preserve superseded options and uncertainty labels. | handoff quality | Prevents repeated mistakes in aggregation. | Spec book may canonize false items. | FACT | high |

## 18. What Future Assistants Must Not Assume

- Do not assume the two Codex prompts succeeded without running verification.
- Do not assume the launcher hardening prompt was applied.
- Do not assume concrete UI IR filenames exist unless the repo confirms them.
- Do not assume uploaded files are accessible in a new chat.
- Do not assume old Plan 8 details override later canon.
- Do not assume hand-authored VS/Xcode projects are authoritative.
- Do not assume GUI/TUI may define commands independently from CLI.
- Do not assume launcher may repair installs directly.
- Do not assume engine can include `dom_contracts`.
- Do not assume RepoX/TestX implementation exists just because canon requires it.

## 19. Recommended Next Action

If continuing this chat’s work alone: run the verification queue, then execute or audit the “Launcher Spec Completion, Gap Closure, and Documentation Hardening” prompt.

If aggregating this chat with other chat reports: ingest `*_02_spec_sheet.yaml` and `*_03_aggregator_packet.md` first, preserve labels and stable IDs, and reconcile duplicates around APP-CANON, BUILD-ID-0, engine purity, and setup/launcher boundaries.

User verification needed before acting: confirm current repository checkout, confirm whether the launcher hardening prompt has already been applied, and provide build/script results if available.

## 20. Appendix: Possibly Relevant Details

The old launcher directory tree, uploaded files/images, and all generated prompt titles are preserved in the artifact ledger and earlier sections. The earlier standalone launcher tree and manual IDE project advice are historical only. The latest canonical layout and application canon supersede them.
