# Aggregator Packet — Dominium Setup Handoff

## 1. Packet Metadata

* Chat label: Dominium Setup Handoff
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: THIS CHAT ONLY; project context pasted from other chats is labelled PROJECT-CONTEXT.
* Coverage: full for visible chat and previous Context Transfer Packet; repo state unverified.
* Confidence: 4 / 5
* Staleness risk: medium
* Merge priority: high
* Main limitations: actual repository state after applied prompts is not verified; some assistant proposals remain tentative.

## 2. Ultra-Condensed Carry-Forward Capsule

FACT: This chat’s core contribution is the evolution and preservation of the Dominium Setup system as a deterministic, auditable, schema-backed, cross-platform installation authority. The user began with a setup-specific master prompt about installers, package managers, and distribution pipelines. Setup was defined as a deployment control plane, not a UI gimmick, background service, store, DRM layer, or launcher. It must be deterministic, auditable, reversible, scriptable, headless-capable, modular, and future-proof. One common setup core must be shared across platforms; platform-specific frontends are thin only.

FACT: Earlier directory proposals using `setup/adapters`, `setup/packaging`, and `core/source` were superseded. The current authoritative repository layout was later locked by the user: top-level products are `engine`, `game`, `client`, `server`, `launcher`, `setup`, `tools`, `libs`, `schema`, `sdk`, `docs`, `ci`, and `legacy`. The canonical setup layout is `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages/{client,server,tools,scripts}`, `setup/platform/{win/{win9x,winnt},linux,bsd,mac/{classic,osx}}`, `setup/tests`, `setup/ui`, and `setup/CMakeLists.txt`.

FACT: Setup is the sole authority for installation, upgrade, downgrade, verification, repair, uninstall, rollback, and packaging layout enforcement. Launcher may invoke setup, but must not reimplement setup logic. Engine must not know setup exists. Setup may depend only on `libs/` and `schema/`. Public setup kernel API lives under `setup/include/dsk`; execution/platform interfaces live under `setup/include/dsu`; internal setup headers stay under `setup/core/**`.

FACT: The user pasted two Codex prompts as already applied. The first required a one-pass refactor/repair/future-proof pass for VS2026, CMake, and Codex; the repo must build through CMake presets, expose setup/launcher CLIs, keep GUI/TUI as stubs if necessary, provide smoke tests, and document VS2026 workflow. The second required final engine purity and contract ownership repair: evict non-engine content from engine, move setup headers to setup, move UI headers to tools/ui_shared, create neutral `libs/contracts/include/dom_contracts`, enforce boundaries in CMake, and harden sanity scripts. Actual post-application repo state remains UNCERTAIN / UNVERIFIED.

FACT: A pasteable prompt was generated in this chat: “Dominium Setup: Final Spec Alignment, Gap Closure, and Hardening Pass.” It should be executed or audited next unless already done. It treats existing implementation as authoritative and completes setup gaps through phases A-H: inventory, schema normalization, kernel contract hardening, platform audit, UI audit, packaging/reproducibility, tests, and final docs/freeze marker.

FACT: Setup supports offline and network installation, update checking, individual package/component customization, repair, uninstall, upgrade, downgrade, and rollback by architecture. Network is optional transport; update checking is non-mutating; repair is explicit; uninstall is ownership-based through installed-state; rollback is journaled.

FACT / PROJECT-CONTEXT: Application-layer canon pasted later states that applications are content-agnostic orchestration shells, CLI is canonical, GUI/TUI are command-graph views, UI is declarative data, tools are read-only by default, RepoX/TestX enforce validation/changelogs, and BUILD-ID-0 governs release identity. This should be merged with other application-layer packages carefully because it likely duplicates broader project canon.

INFERENCE: The first action for any future implementation chat is to inspect actual repo state, especially `setup/`, `schema/`, `libs/contracts`, CMake presets, sanity scripts, and setup/launcher CLI smoke tests. Do not act from stale old trees.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Setup sole installation authority | decision | DECISION-01 | Central boundary | FACT | high |
| 2 | Canonical setup layout | structure | DECISION-03 | Supersedes obsolete paths | FACT | high |
| 3 | Existing implementation authoritative unless violating canon | process | DECISION-20 | Prevents redesign | FACT | high |
| 4 | Generated setup hardening prompt | artifact | ARTIFACT-17 | Most actionable next artifact | FACT | high |
| 5 | Actual repo state unverified | uncertainty | QUESTION-01 | Prevents false assumptions | UNCERTAIN / UNVERIFIED | high |
| 6 | Engine purity and libs/contracts | architecture | DECISION-08/09 | Protects engine reuse | FACT | high |
| 7 | Schema-only setup-launcher handoff | contract | DECISION-07 | Prevents private coupling | FACT | high |
| 8 | CLI canonical/UI as data | application rule | DECISION-10/11 | Prevents UI divergence | FACT / PROJECT-CONTEXT | medium-high |
| 9 | RepoX/TestX/BUILD-ID governance | release rule | DECISION-22/23 | Release reproducibility | FACT / PROJECT-CONTEXT | medium-high |
| 10 | Obsolete adapter/source trees rejected | rejected option | REJECTED-06/07/09 | Avoids repeated work | FACT | high |

## 4. Workstream Summaries

### WORKSTREAM-01 — Dominium Setup / Installer System

* Objective: Maintain and finish the deterministic setup product: install, upgrade, downgrade, verify, repair, uninstall, rollback, and packaging layout enforcement.
* Current state: The chat developed Setup plans, then superseded old directory ideas with a canonical setup/ layout. The user later stated two Codex refactor prompts had been applied. Actual post-refactor repo state remains unverified in this chat.
* Desired end state: A buildable, auditable, schema-backed setup product under setup/ with core/fetch, core/verify, core/install, core/rollback, include/dsk, include/dsu, platform, ui, packages, and tests.
* Priority: highest
* Decisions: DECISION-01, DECISION-02, DECISION-03, DECISION-04, DECISION-05, DECISION-13, DECISION-14, DECISION-17, DECISION-18, DECISION-19, DECISION-20, DECISION-25
* Tasks: TASK-02, TASK-03, TASK-08, TASK-09, TASK-12, TASK-13
* Constraints: see Constraint Register
* Artifacts: see Artifact Ledger
* Risks: RISK-01, RISK-09
* Open questions: QUESTION-02, QUESTION-03, QUESTION-06
* Next action: Verify repo state before implementation.

### WORKSTREAM-02 — Canonical Repository Structure and CMake/VS2026 Build Enforcement

* Objective: Ensure the full repository builds through CMake/Visual Studio 2026 and enforces product boundaries mechanically.
* Current state: Two user-provided Codex prompts were said to have been applied. They require CMakePresets, strict target include dirs, smoke tests, and no hand-authored IDE projects as authoritative build files.
* Desired end state: Root CMake + presets build libs, engine, setup, launcher, tools, and stubs as needed; CTest smoke tests pass; VS2026 Open Folder workflow works.
* Priority: highest
* Decisions: DECISION-03, DECISION-04, DECISION-12, DECISION-20, DECISION-21, DECISION-26
* Tasks: TASK-01, TASK-04
* Constraints: see Constraint Register
* Artifacts: see Artifact Ledger
* Risks: RISK-03, RISK-14
* Open questions: QUESTION-01, QUESTION-07, QUESTION-14
* Next action: Verify repo state before implementation.

### WORKSTREAM-03 — Engine Purity and Neutral Contract Ownership

* Objective: Remove setup/launcher/tools/game contamination from engine and relocate cross-product contracts to libs/contracts.
* Current state: The final purity prompt listed concrete prior violations under engine and game. It required relocation/quarantine and creation of libs/contracts.
* Desired end state: engine/ contains only include/domino, modules, render, tests, CMakeLists. Cross-product APIs live under libs/contracts/include/dom_contracts.
* Priority: highest
* Decisions: DECISION-08, DECISION-09
* Tasks: TASK-05, TASK-06
* Constraints: see Constraint Register
* Artifacts: see Artifact Ledger
* Risks: RISK-05
* Open questions: QUESTION-05, QUESTION-07
* Next action: Verify repo state before implementation.

### WORKSTREAM-04 — Setup Schemas and Setup ↔ Launcher Handoff

* Objective: Define and enforce schema-only communication between setup and launcher: install plans, installed-state snapshots, verification reports, audit logs, and exit/status contracts.
* Current state: Assistant produced Phase 3 schema definitions after the applied prompts. Actual schema files under schema/ were not verified.
* Desired end state: All setup inputs/outputs are backed by schema/setup/* and shared contracts; launcher reads artifacts and invokes setup, never repairs or writes installed state.
* Priority: high
* Decisions: DECISION-01, DECISION-07, DECISION-16, DECISION-18, DECISION-27
* Tasks: TASK-07
* Constraints: see Constraint Register
* Artifacts: see Artifact Ledger
* Risks: RISK-04, RISK-06
* Open questions: QUESTION-04
* Next action: Verify repo state before implementation.

### WORKSTREAM-05 — Application Layer Canon

* Objective: Implement applications as content-agnostic orchestration shells over engine/game without mutating authoritative simulation state.
* Current state: User pasted application-layer canon from other chats and latest project canon. It is visible in this chat but originated from broader project context.
* Desired end state: Setup, launcher, client, server, and tools obey APP-CANON0/1, APP-AUTO-0, and APP-UI-BIND-0. CLI is canonical; GUI/TUI are views.
* Priority: high
* Decisions: DECISION-24
* Tasks: none indexed
* Constraints: see Constraint Register
* Artifacts: see Artifact Ledger
* Risks: see Risk Register
* Open questions: QUESTION-06
* Next action: Verify repo state before implementation.

### WORKSTREAM-06 — Packaging, Reproducibility, Offline and Network Acquisition

* Objective: Support reproducible package layouts, offline installs, network fetch, update checking, and package/component customization without hidden mutation.
* Current state: Assistant mapped these capabilities to setup/core/fetch, verify, install plans, and reports; implementation state unverified.
* Desired end state: setup/packages/* produces installers/packages; setup/core/fetch supports local/cache/network payload acquisition; all artifacts are hash-verified and reproducible.
* Priority: high
* Decisions: DECISION-06, DECISION-15, DECISION-16
* Tasks: TASK-11, TASK-14, TASK-15
* Constraints: see Constraint Register
* Artifacts: see Artifact Ledger
* Risks: RISK-08
* Open questions: QUESTION-10, QUESTION-11
* Next action: Verify repo state before implementation.

### WORKSTREAM-07 — CLI/TUI/GUI Command Model and UI IR

* Objective: Make CLI the canonical command graph while GUI/TUI are views over the same commands; UI layouts are declarative data.
* Current state: Application canon locked the rule. Assistant proposed an app command spine such as libs/appcmd and UI IR under schema, but exact paths were not user-locked.
* Desired end state: All app frontends share command graph, deterministic output, accessibility, localization, and binding validation.
* Priority: medium-high
* Decisions: DECISION-10, DECISION-11
* Tasks: TASK-10, TASK-16, TASK-17
* Constraints: see Constraint Register
* Artifacts: see Artifact Ledger
* Risks: RISK-07
* Open questions: QUESTION-08, QUESTION-09
* Next action: Verify repo state before implementation.

### WORKSTREAM-08 — RepoX/TestX/BUILD-ID-0 Governance

* Objective: Use RepoX/TestX to enforce canon, schemas, UI binding, changelog generation, build metadata, and release version rules.
* Current state: Latest pasted canon defines Product SemVer, Build Kind, GBN, BII, channels, and no manual changelog editing. Actual tooling not inspected.
* Desired end state: Apps display RepoX-generated changelogs and refuse incompatible versions loudly; no distributed artifact without GBN.
* Priority: high
* Decisions: DECISION-22, DECISION-23
* Tasks: TASK-18
* Constraints: see Constraint Register
* Artifacts: see Artifact Ledger
* Risks: RISK-10
* Open questions: QUESTION-13, QUESTION-15
* Next action: Verify repo state before implementation.

### WORKSTREAM-09 — Legacy Platform Support

* Objective: Preserve architectural support for Windows NT, Windows 9x/OpenWatcom, macOS X, classic macOS, Linux circa 2000+, Steam/Epic/web/consoles/retro.
* Current state: Discussed early as setup support goals. Later canonical layout includes platform/win/{win9x,winnt}, platform/mac/{classic,osx}, linux, bsd.
* Desired end state: Modern and legacy platform code isolated; unsupported legacy targets not built accidentally; constraints documented.
* Priority: medium
* Decisions: DECISION-02, DECISION-13
* Tasks: TASK-09
* Constraints: see Constraint Register
* Artifacts: see Artifact Ledger
* Risks: RISK-11
* Open questions: QUESTION-12
* Next action: Verify repo state before implementation.

### WORKSTREAM-10 — Context Transfer and Report Packaging

* Objective: Produce durable per-chat reports that can be saved, shared, aggregated, and used as input to a future Project Spec Book.
* Current state: A maximum-fidelity Context Transfer Packet was produced; this task converts it into a downloadable report package.
* Desired end state: Seven files plus ZIP: full report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit, manifest.
* Priority: highest for this turn
* Decisions: none indexed
* Tasks: TASK-19, TASK-20
* Constraints: see Constraint Register
* Artifacts: see Artifact Ledger
* Risks: RISK-02, RISK-12, RISK-13, RISK-15
* Open questions: none indexed
* Next action: Verify repo state before implementation.

## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Label |
| --- | --- | --- | --- |
| DECISION-01 | Setup is the sole authority for installation, upgrade, downgrade, verification, rollback, repair, uninstall, and packaging layout enforcement. | locked | FACT |
| DECISION-02 | Use one common setup core shared across all platforms. | locked | FACT |
| DECISION-03 | The canonical setup layout is setup/core/{fetch,verify,install,rollback}, setup/include/{dsk,dsu}, setup/packages, setup/platform, setup/tests, setup/ui. | locked | FACT |
| DECISION-04 | Setup may depend only on libs/ and schema/. | locked | FACT |
| DECISION-05 | setup/include/dsk owns public setup kernel API; setup/include/dsu owns execution/platform interfaces. | locked | FACT |
| DECISION-06 | All packaging outputs and recipes are produced from setup/packages/. | locked | FACT |
| DECISION-07 | Setup ↔ launcher handoff occurs only through manifests, schemas, installed-state snapshots, and exit/status contracts. | locked | FACT |
| DECISION-08 | Engine must be pure and unaware of setup/launcher/tools. | locked | FACT |
| DECISION-09 | Cross-product contracts belong under libs/contracts/include/dom_contracts. | locked | FACT |
| DECISION-10 | CLI is canonical; GUI/TUI are views over the same command graph. | locked | FACT / PROJECT-CONTEXT |
| DECISION-11 | UI is declarative data / UI IR, not logic. | locked | FACT / PROJECT-CONTEXT |
| DECISION-12 | CMake is authoritative; VS/Xcode projects are generated and not authoritative source files. | accepted | FACT |
| DECISION-13 | Use Visual Studio Desktop Development with C++ for setup; do not use .NET for authoritative setup execution. | accepted | FACT / INFERENCE |
| DECISION-14 | Setup core language should be C/C++ with stable C ABI; C89/C90 and C++98 compatibility where targeted. | locked | FACT |
| DECISION-15 | Offline and network installation are both supported; network is optional transport, not dependency. | accepted | FACT / INFERENCE |
| DECISION-16 | Update checking is non-mutating plan/state comparison unless explicit update is invoked. | accepted | FACT / INFERENCE |
| DECISION-17 | Repair is explicit and never silent. | locked | FACT |
| DECISION-18 | Uninstall is ownership-based using installed-state manifests. | locked | FACT |
| DECISION-19 | Rollback is journal-driven and first-class. | locked | FACT |
| DECISION-20 | Existing implementation is authoritative unless it violates locked rules. | locked | FACT |
| DECISION-21 | Do not delete code during refactors; quarantine under legacy/ with README. | locked | FACT |
| DECISION-22 | RepoX-generated changelogs only; no manual changelog editing. | locked | FACT / PROJECT-CONTEXT |
| DECISION-23 | BUILD-ID-0 version model is locked: SemVer + build kind + GBN/BII + channel rules. | locked | FACT / PROJECT-CONTEXT |
| DECISION-24 | Tools are read-only by default. | locked | FACT / PROJECT-CONTEXT |
| DECISION-25 | Do not reintroduce generic source/ directories under setup canonical layout. | locked | FACT |
| DECISION-26 | Top-level products are locked as engine, game, client, server, launcher, setup, tools, libs, schema, sdk, docs, ci, legacy. | locked | FACT |
| DECISION-27 | Schema is the canonical data-format location; setup must not invent private formats. | locked | FACT |

### Task Register

| ID | Task | Priority | Urgency | Label |
| --- | --- | --- | --- | --- |
| TASK-01 | Verify actual repo state after the two applied Codex prompts. | highest | immediate | FACT / INFERENCE |
| TASK-02 | Execute or verify the generated Setup final spec alignment prompt. | highest | immediate | FACT |
| TASK-03 | Validate setup/ canonical layout. | high | immediate | FACT |
| TASK-04 | Run CMake configure/build/test and smoke commands. | high | immediate | FACT |
| TASK-05 | Verify engine purity and include ownership. | high | soon | FACT |
| TASK-06 | Verify libs/contracts exists and is used correctly. | high | soon | FACT |
| TASK-07 | Normalize setup schemas under schema/setup/. | high | soon | FACT |
| TASK-08 | Audit setup/include/dsk and setup/include/dsu. | high | soon | FACT |
| TASK-09 | Audit setup/platform adapters. | medium-high | soon | FACT |
| TASK-10 | Audit setup/ui and canonical CLI. | medium-high | soon | FACT |
| TASK-11 | Audit setup/packages reproducibility. | high | soon | FACT |
| TASK-12 | Align setup tests with spec requirements. | high | soon | FACT |
| TASK-13 | Create/verify setup baseline docs and freeze marker. | high | soon | FACT |
| TASK-14 | Verify offline and network acquisition implementation. | medium | later | INFERENCE |
| TASK-15 | Verify update/downgrade CLI and schema semantics. | medium | later | INFERENCE |
| TASK-16 | Define or verify app command spine for CLI/TUI/GUI parity. | medium | later | INFERENCE |
| TASK-17 | Define or verify UI IR schema and binding validation. | medium | later | INFERENCE |
| TASK-18 | Verify RepoX/TestX/BUILD-ID integration. | high | later | PROJECT-CONTEXT |
| TASK-19 | Preserve old-chat report package and store with future chat packages. | highest | current | FACT |
| TASK-20 | Aggregate this package with other old-chat packages later. | medium | later | FACT |

### Constraint Register

| ID | Constraint | Type | Risk | Label |
| --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Setup is sole authority for installation/system state mutation. | Architectural | high | FACT |
| CONSTRAINT-02 | Launcher may invoke setup but must not reimplement setup logic. | Architectural | high | FACT |
| CONSTRAINT-03 | Engine must not know setup exists. | Architectural | high | FACT |
| CONSTRAINT-04 | Setup may depend only on libs/ and schema/. | Dependency | high | FACT |
| CONSTRAINT-05 | Public setup APIs live only under setup/include/dsk and setup/include/dsu. | Include ownership | medium-high | FACT |
| CONSTRAINT-06 | Setup internal headers stay under setup/core/**. | Include ownership | medium | FACT |
| CONSTRAINT-07 | No setup headers may be included by engine or game. | Include ownership | high | FACT |
| CONSTRAINT-08 | Engine/include exports only domino engine ABI. | Include ownership | high | FACT |
| CONSTRAINT-09 | Cross-product contracts live in libs/contracts/include/dom_contracts. | Architecture | medium-high | FACT |
| CONSTRAINT-10 | No global include_directories except minimal config headers. | Build | medium | FACT |
| CONSTRAINT-11 | CMake is authoritative; generated IDE projects are not source-of-truth. | Build | medium | FACT |
| CONSTRAINT-12 | Keep repo buildable after each commit in Codex phases. | Process | high | FACT |
| CONSTRAINT-13 | Do not delete code; quarantine obsolete code under legacy/ with README. | Process | medium | FACT |
| CONSTRAINT-14 | Do not redesign settled architecture or simulation rules. | Scope | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-15 | Applications are content-agnostic and contain no gameplay logic. | Application | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-16 | Applications must run with zero content packs installed. | Application | medium-high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-17 | CLI is canonical; GUI/TUI are views over same command graph. | Application/UI | medium-high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-18 | UI is declarative IR/data; no business logic embedded. | UI | medium-high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-19 | Accessibility requirements apply to GUIs. | UI | medium | FACT / PROJECT-CONTEXT |
| CONSTRAINT-20 | Localization strings externalized; raw-key fallback if locale missing. | UI | medium | FACT / PROJECT-CONTEXT |
| CONSTRAINT-21 | Tools are read-only by default. | Application | medium | FACT / PROJECT-CONTEXT |
| CONSTRAINT-22 | RepoX is source of truth for changelogs and compatibility/build metadata. | Release | medium-high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-23 | BUILD-ID-0 versioning model is locked. | Release | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-24 | No distributed artifact without GBN. | Release | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-25 | Engine is C89; game is C++98. | Language | medium-high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-26 | No C++ ABI leakage across public boundaries. | ABI | medium-high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-27 | Setup manifests must avoid arbitrary executable scripts; actions are declarative/sandboxed. | Security | medium | FACT |
| CONSTRAINT-28 | No silent repair or hidden mutation. | Behavior | high | FACT |
| CONSTRAINT-29 | Installed-state is setup-written and launcher-read-only. | State | high | FACT |
| CONSTRAINT-30 | Transactions use preflight/stage/install/verify/commit/rollback and avoid live in-place mutation. | Behavior | high | FACT |
| CONSTRAINT-31 | Package scripts/templates must not decide install logic. | Packaging | medium-high | FACT |
| CONSTRAINT-32 | Offline installs must not require network. | Distribution | medium | FACT / INFERENCE |
| CONSTRAINT-33 | External/world-current facts and tool versions require verification before future use. | Evidence | medium | FACT |
| CONSTRAINT-34 | Do not copy third-party installer branding/text/logos/assets. | Legal/IP | medium | FACT |
| CONSTRAINT-35 | Report package must label important items as FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | Output | medium | FACT |

### Open Questions Register

| ID | Question | Priority | Label |
| --- | --- | --- | --- |
| QUESTION-01 | Were the two applied Codex prompts completed successfully in the actual repo? | highest | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Has the generated Setup final spec alignment prompt been executed? | highest | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | What is the current exact setup/ tree? | highest | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What schema files exist under schema/setup/? | high | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Does libs/contracts exist and compile? | high | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Do setup --help and launcher --help run? | highest | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Do verify_tree_sanity and verify_includes_sanity reflect current invariants? | high | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Is app command spine already implemented? | medium | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | Where exactly should UI IR live? | medium | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | How mature is setup/core/fetch network support? | medium | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | Are update/downgrade operations represented in CLI, schema, tests? | medium | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | How much legacy Win9x/macOS Classic work is expected now? | medium-low | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Are RepoX/TestX/BUILD-ID tools present and wired into CI? | high | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | Are old IDE artifacts removed/quarantined? | medium | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | Does documentation status header policy exist and pass checks? | medium | UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact | Type | Status | Carry forward | Label |
| --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Initial six installer reference images | image attachments | historical | low | FACT |
| ARTIFACT-02 | Initial GPT-5.2 MASTER PROMPT — DOMINIUM / DOMINO SETUP & INSTALLATION SYSTEM | prompt | superseded structurally; core invariants persist | yes | FACT |
| ARTIFACT-03 | Phase 1 Setup Core Architecture output | assistant plan | conceptually useful; paths superseded | yes | FACT |
| ARTIFACT-04 | Plan S | assistant plan | conceptually useful; paths updated by later canon | yes | FACT |
| ARTIFACT-05 | Early /source/setup directory skeletons | assistant/user trees | superseded | historical only | FACT |
| ARTIFACT-06 | VS workload and language recommendation | assistant output | still relevant unless canon changes | yes | FACT / INFERENCE |
| ARTIFACT-07 | VS/Xcode CMake workflow guidance | assistant output | still relevant | yes | FACT |
| ARTIFACT-08 | Second setup master prompt: DOMINIUM / DOMINO SETUP SYSTEM | prompt | superseded by existing implementation/canonical repo | partial | FACT |
| ARTIFACT-09 | Old/current setup directory tree from Windows tree output | repo snapshot text | historical; actual state now unverified | yes | FACT |
| ARTIFACT-10 | Assistant analysis of old tree | assistant output | partially superseded | yes | FACT |
| ARTIFACT-11 | Canonical repo/setup structure prompt | prompt | current authoritative | critical | FACT |
| ARTIFACT-12 | Plan S amendments for canonical repo | assistant output | current where consistent | yes | FACT |
| ARTIFACT-13 | Phase 2 authoritative setup directory tree | assistant output | useful reference; actual repo unverified | yes | FACT |
| ARTIFACT-14 | Applied Codex Prompt 1 — One-pass refactor + repair + future-proof for VS2026 + CMake + Codex | prompt | authoritative and said applied | critical | FACT |
| ARTIFACT-15 | Applied Codex Prompt 2 — Final purity + contract ownership repair | prompt | authoritative and said applied | critical | FACT |
| ARTIFACT-16 | Phase 3 schema definitions assistant output | assistant plan | useful; implementation unverified | yes | FACT |
| ARTIFACT-17 | Generated prompt — Dominium Setup: Final Spec Alignment, Gap Closure, and Hardening Pass | prompt | critical next action if not executed | critical | FACT |
| ARTIFACT-18 | Offline/net/update/customization capability mapping | assistant output | accepted unless contradicted | yes | FACT / INFERENCE |
| ARTIFACT-19 | Application-layer canon prompt | prompt | authoritative project context pasted here | critical | FACT / PROJECT-CONTEXT |
| ARTIFACT-20 | Latest other-chat project/application/release canon prompt | prompt | authoritative project context pasted here | critical | FACT / PROJECT-CONTEXT |
| ARTIFACT-21 | Assistant app-layer spine proposal | assistant output | proposal, not fully locked | carry with caution | INFERENCE |
| ARTIFACT-22 | Maximum-fidelity Context Transfer Packet | assistant output | input to this report package | critical | FACT |
| ARTIFACT-23 | This final report package | generated files | created by this response | critical | FACT |

### Risk Register

| ID | Risk | Severity | Mitigation | Label |
| --- | --- | --- | --- | --- |
| RISK-01 | Future assistant follows obsolete adapters/packaging/source layout. | high | Always start from latest canonical setup/ layout. | FACT / INFERENCE |
| RISK-02 | Assistant suggestions are mistaken for user decisions. | high | Keep FACT/INFERENCE labels and require user/canon confirmation. | FACT |
| RISK-03 | Repo state differs from this packet. | high | Inspect repo before acting. | UNCERTAIN / UNVERIFIED |
| RISK-04 | Launcher duplicates setup update/repair logic. | high | Use setup invocation + schema reports only. | FACT |
| RISK-05 | Engine purity regresses. | high | Run tree/include sanity checks in CI. | FACT |
| RISK-06 | Ad-hoc setup formats drift from schema. | high | Execute schema normalization phase. | FACT / INFERENCE |
| RISK-07 | GUI/TUI embeds business logic. | medium-high | Use command graph + UI IR binding validation. | FACT / PROJECT-CONTEXT |
| RISK-08 | Network install becomes required unintentionally. | medium-high | Test offline install paths and treat network as transport. | FACT / INFERENCE |
| RISK-09 | Rollback is under-tested. | high | Fault-injection tests for each transaction phase. | FACT |
| RISK-10 | Build metadata/changelog manually edited. | medium-high | Use RepoX-generated outputs only. | FACT / PROJECT-CONTEXT |
| RISK-11 | Legacy platform goals impose modern app constraints on engine/game. | medium | Keep app toolchains isolated from engine/game. | FACT |
| RISK-12 | Context package omits exact old prompt wording. | medium | Use artifact ledger and request original prompt if exact replay required. | UNCERTAIN / UNVERIFIED |
| RISK-13 | Future aggregation deduplicates conflicting chats too aggressively. | high | Preserve provenance and contradictions during aggregation. | FACT |
| RISK-14 | Dates/tool versions become stale. | medium | Verify external/toolchain facts before use. | FACT |
| RISK-15 | Generated report files are edited manually and diverge. | medium | Store ZIP and Markdown/YAML together; note manual changes. | FACT |

### Verification Queue

| ID | Item | Priority | Label |
| --- | --- | --- | --- |
| VERIFY-01 | Current setup/ tree | highest | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Current schema/ tree | highest | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | libs/contracts existence and CMake target | high | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | CMake configure/build/test | highest | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | setup --help and launcher --help | highest | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | verify_tree_sanity and verify_includes_sanity scripts | high | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | docs/SETUP_GAPS.md and related setup docs | high | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | setup/core/fetch offline/network behavior | medium | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | update/downgrade operation semantics | medium | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | UI IR and binding validation path | medium | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | RepoX/TestX/BUILD-ID tooling status | high | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Legacy platform support status | medium-low | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Old IDE artifacts are quarantined or non-authoritative | medium | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Docs status-header policy | medium | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | This package contents after generation | high | FACT |

## 6. Possible Cross-Chat Duplicates

- Application-layer canon.
- BUILD-ID-0 and release versioning.
- RepoX/TestX/VALIDATE/CLEAN-2/DEV-OPS.
- Engine purity and contract ownership.
- UI IR and CLI command graph.
- Setup authority likely appears in launcher/setup chats.

## 7. Possible Cross-Chat Conflicts

- Earlier setup layouts vs canonical setup layout.
- Assistant proposals such as `libs/appcmd` vs actual canon.
- Project-level context from other chats vs chat-specific facts.
- Implementation status claims vs actual repo state.

## 8. Spec Book Integration Guidance

Feed this chat into chapters on setup architecture, repository boundaries, build enforcement, setup-launcher contracts, packaging/reproducibility, application-layer command/UI rules, and release governance. Formalize user-locked decisions only. Keep early directory brainstorms as historical context. Verify repo state before turning implementation claims into spec.

## 9. Aggregator Warnings

Do not merge away uncertainty. Do not treat assistant proposals as locked. Do not use obsolete paths. Do not assume the two Codex prompts succeeded without verification. Do not treat project-level pasted context as unique to this chat; likely duplicate with other reports.
