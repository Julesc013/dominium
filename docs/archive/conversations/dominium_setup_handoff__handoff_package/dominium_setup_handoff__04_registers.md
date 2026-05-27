# Registers — Dominium Setup Handoff

## 1. Workstream Register

| ID | Name | Objective | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Dominium Setup / Installer System | Maintain and finish the deterministic setup product: install, upgrade, downgrade, verify, repair, uninstall, rollback, and packaging layout enforcement. | active | highest | 4 | FACT |
| WORKSTREAM-02 | Canonical Repository Structure and CMake/VS2026 Build Enforcement | Ensure the full repository builds through CMake/Visual Studio 2026 and enforces product boundaries mechanically. | active / needs verification | highest | 3 | FACT |
| WORKSTREAM-03 | Engine Purity and Neutral Contract Ownership | Remove setup/launcher/tools/game contamination from engine and relocate cross-product contracts to libs/contracts. | active / claimed applied / needs verification | highest | 3 | FACT |
| WORKSTREAM-04 | Setup Schemas and Setup ↔ Launcher Handoff | Define and enforce schema-only communication between setup and launcher: install plans, installed-state snapshots, verification reports, audit logs, and exit/status contracts. | active | high | 4 | FACT |
| WORKSTREAM-05 | Application Layer Canon | Implement applications as content-agnostic orchestration shells over engine/game without mutating authoritative simulation state. | active / authoritative project context | high | 4 | FACT / PROJECT-CONTEXT |
| WORKSTREAM-06 | Packaging, Reproducibility, Offline and Network Acquisition | Support reproducible package layouts, offline installs, network fetch, update checking, and package/component customization without hidden mutation. | active / design accepted unless contradicted later | high | 4 | FACT |
| WORKSTREAM-07 | CLI/TUI/GUI Command Model and UI IR | Make CLI the canonical command graph while GUI/TUI are views over the same commands; UI layouts are declarative data. | active / some implementation details tentative | medium-high | 3 | FACT / INFERENCE |
| WORKSTREAM-08 | RepoX/TestX/BUILD-ID-0 Governance | Use RepoX/TestX to enforce canon, schemas, UI binding, changelog generation, build metadata, and release version rules. | active / needs repo verification | high | 3 | FACT / PROJECT-CONTEXT |
| WORKSTREAM-09 | Legacy Platform Support | Preserve architectural support for Windows NT, Windows 9x/OpenWatcom, macOS X, classic macOS, Linux circa 2000+, Steam/Epic/web/consoles/retro. | active but lower immediate urgency | medium | 4 | FACT |
| WORKSTREAM-10 | Context Transfer and Report Packaging | Produce durable per-chat reports that can be saved, shared, aggregated, and used as input to a future Project Spec Book. | active in current response | highest for this turn | 5 | FACT |

## 2. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Setup is the sole authority for installation, upgrade, downgrade, verification, rollback, repair, uninstall, and packaging layout enforcement. | locked | Repeated user prompts; canonical setup authority rule | Prevents launcher/engine bypass and preserves auditability | Launcher may invoke setup only; setup writes state | WORKSTREAM-01, WORKSTREAM-04 | high | FACT |
| DECISION-02 | Use one common setup core shared across all platforms. | locked | Initial and later setup prompts | Avoid duplicated OS logic | Platform code remains thin | WORKSTREAM-01, WORKSTREAM-09 | high | FACT |
| DECISION-03 | The canonical setup layout is setup/core/{fetch,verify,install,rollback}, setup/include/{dsk,dsu}, setup/packages, setup/platform, setup/tests, setup/ui. | locked | User canonical setup prompt | Filesystem is fixed ground truth | Earlier adapters/packaging/source layouts are superseded | WORKSTREAM-01, WORKSTREAM-02 | high | FACT |
| DECISION-04 | Setup may depend only on libs/ and schema/. | locked | Canonical dependency rules | Enforces isolation | No engine/launcher/game internals in setup | WORKSTREAM-01, WORKSTREAM-02 | high | FACT |
| DECISION-05 | setup/include/dsk owns public setup kernel API; setup/include/dsu owns execution/platform interfaces. | locked | Include ownership rules | Stable boundaries | Internal setup headers stay under setup/core/** | WORKSTREAM-01 | high | FACT |
| DECISION-06 | All packaging outputs and recipes are produced from setup/packages/. | locked | User required update #4 | Separates packaging from platform/UI adapters | Old adapter-local packaging must be moved/quarantined | WORKSTREAM-06 | high | FACT |
| DECISION-07 | Setup ↔ launcher handoff occurs only through manifests, schemas, installed-state snapshots, and exit/status contracts. | locked | Canonical dependency rules | Prevents private coupling | Launcher must not infer install success from filesystem heuristics | WORKSTREAM-04 | high | FACT |
| DECISION-08 | Engine must be pure and unaware of setup/launcher/tools. | locked | Final purity prompt | Keeps engine reusable | Forbidden engine paths/includes must fail CI | WORKSTREAM-03 | high | FACT |
| DECISION-09 | Cross-product contracts belong under libs/contracts/include/dom_contracts. | locked | Final purity prompt | Moves shared contracts out of engine/game internals | Engine must not include dom_contracts | WORKSTREAM-03 | high | FACT |
| DECISION-10 | CLI is canonical; GUI/TUI are views over the same command graph. | locked | Application-layer canon | Ensures parity/scriptability | UI cannot contain business logic | WORKSTREAM-07 | high | FACT / PROJECT-CONTEXT |
| DECISION-11 | UI is declarative data / UI IR, not logic. | locked | Application-layer canon | Supports accessibility/localization/binding validation | UI backends must be interchangeable | WORKSTREAM-07 | high | FACT / PROJECT-CONTEXT |
| DECISION-12 | CMake is authoritative; VS/Xcode projects are generated and not authoritative source files. | accepted | Assistant recommendation and later Codex prompt | Prevents IDE drift | No hand-written .vcxproj/.xcodeproj as build truth | WORKSTREAM-02 | medium-high | FACT |
| DECISION-13 | Use Visual Studio Desktop Development with C++ for setup; do not use .NET for authoritative setup execution. | accepted | User asked; assistant recommended; no contradiction | Legacy/offline/ABI requirements | C/C++ setup; .NET only for optional non-authoritative tooling | WORKSTREAM-01, WORKSTREAM-09 | medium-high | FACT / INFERENCE |
| DECISION-14 | Setup core language should be C/C++ with stable C ABI; C89/C90 and C++98 compatibility where targeted. | locked | User prompts and tooling constraints | Long-term ABI/toolchain support | No C++ ABI leakage across boundaries | WORKSTREAM-01 | high | FACT |
| DECISION-15 | Offline and network installation are both supported; network is optional transport, not dependency. | accepted | User asked; assistant capability mapping | Air-gapped installs and online fetch share fetch abstraction | Payloads must be content-addressed/verified | WORKSTREAM-06 | medium-high | FACT / INFERENCE |
| DECISION-16 | Update checking is non-mutating plan/state comparison unless explicit update is invoked. | accepted | Assistant response to user question | Prevents hidden mutation | Launcher can display reports but setup applies changes | WORKSTREAM-06, WORKSTREAM-04 | medium-high | FACT / INFERENCE |
| DECISION-17 | Repair is explicit and never silent. | locked | Multiple setup prompts | Avoid hidden mutations | Repair command must be invoked deliberately | WORKSTREAM-01 | high | FACT |
| DECISION-18 | Uninstall is ownership-based using installed-state manifests. | locked | Setup state rules | Clean uninstall and user-data preservation | Launcher/client cannot delete owned install files | WORKSTREAM-01, WORKSTREAM-04 | high | FACT |
| DECISION-19 | Rollback is journal-driven and first-class. | locked | Transaction model prompts | Resilience to partial installs | Fault-injection tests required | WORKSTREAM-01 | high | FACT |
| DECISION-20 | Existing implementation is authoritative unless it violates locked rules. | locked | User request for final setup prompt | Avoids redesign after refactor | Audit/repair rather than restart | WORKSTREAM-01, WORKSTREAM-02 | high | FACT |
| DECISION-21 | Do not delete code during refactors; quarantine under legacy/ with README. | locked | Codex prompts | Preserves history and behavior | Legacy content moved, not erased | WORKSTREAM-02 | high | FACT |
| DECISION-22 | RepoX-generated changelogs only; no manual changelog editing. | locked | Application/release canon | Release data reproducibility | Apps display RepoX output | WORKSTREAM-08 | high | FACT / PROJECT-CONTEXT |
| DECISION-23 | BUILD-ID-0 version model is locked: SemVer + build kind + GBN/BII + channel rules. | locked | Latest project canon | Consistent distributed artifact identity | Mismatch refuses loudly | WORKSTREAM-08 | high | FACT / PROJECT-CONTEXT |
| DECISION-24 | Tools are read-only by default. | locked | Application-layer canon | Prevents accidental mutation | Mutating tools must be explicit/gated | WORKSTREAM-05 | high | FACT / PROJECT-CONTEXT |
| DECISION-25 | Do not reintroduce generic source/ directories under setup canonical layout. | locked | Canonical update prompt prohibitions | Preserves module clarity | Old core/source pattern superseded | WORKSTREAM-01 | medium-high | FACT |
| DECISION-26 | Top-level products are locked as engine, game, client, server, launcher, setup, tools, libs, schema, sdk, docs, ci, legacy. | locked | Canonical repository prompt | Future paths must align | Old source/setup-only assumptions superseded | WORKSTREAM-02 | high | FACT |
| DECISION-27 | Schema is the canonical data-format location; setup must not invent private formats. | locked | Canonical dependency/schema handoff rules | Enables validation and launcher handoff | Ad-hoc JSON/TLV must map to schema | WORKSTREAM-04 | high | FACT |

## 3. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Verify actual repo state after the two applied Codex prompts. | highest | immediate | New chat / Codex / user | Repo access | tree outputs, git log/status, CMake logs | Confirmed state vs canonical layout | Inspect setup/, schema/, libs/contracts/, CMake, scripts | WORKSTREAM-02 | FACT / INFERENCE |
| TASK-02 | Execute or verify the generated Setup final spec alignment prompt. | highest | immediate | Codex | TASK-01 | Whether docs/SETUP_GAPS.md and related outputs exist | Setup gaps closed or audited | Run phases A-H if not already done | WORKSTREAM-01 | FACT |
| TASK-03 | Validate setup/ canonical layout. | high | immediate | Codex | TASK-01 | Current setup tree | Pass/fail against canonical layout | Compare with setup/core, include, packages, platform, tests, ui | WORKSTREAM-01 | FACT |
| TASK-04 | Run CMake configure/build/test and smoke commands. | high | immediate | Codex | Repo, presets | cmake and ctest output; setup/launcher executable paths | Build/smoke baseline | Run vs2026 preset and setup --help / launcher --help | WORKSTREAM-02 | FACT |
| TASK-05 | Verify engine purity and include ownership. | high | soon | Codex | Scripts, repo tree | verify_tree_sanity and include scan outputs | No engine contamination | Run enforcement scripts; inspect engine include dirs | WORKSTREAM-03 | FACT |
| TASK-06 | Verify libs/contracts exists and is used correctly. | high | soon | Codex | Repo tree, CMake | Contract headers and target graph | Neutral contracts enforce boundary | Inspect libs/contracts/include/dom_contracts | WORKSTREAM-03 | FACT |
| TASK-07 | Normalize setup schemas under schema/setup/. | high | soon | Codex | Current schema files | install_plan, installed_state, verify_report, audit_log docs/specs | Schema-backed setup I/O | Execute prompt Phase B | WORKSTREAM-04 | FACT |
| TASK-08 | Audit setup/include/dsk and setup/include/dsu. | high | soon | Codex | Header files | Minimal public APIs and ABI versioning | No internal header exposure | Execute prompt Phase C | WORKSTREAM-01 | FACT |
| TASK-09 | Audit setup/platform adapters. | medium-high | soon | Codex | setup/platform tree | Per-platform README and thin adapter compliance | Adapters provide OS services only | Execute prompt Phase D | WORKSTREAM-01, WORKSTREAM-09 | FACT |
| TASK-10 | Audit setup/ui and canonical CLI. | medium-high | soon | Codex | setup/ui tree | Deterministic CLI commands and docs | CLI help/status/version and operation commands | Execute prompt Phase E | WORKSTREAM-07 | FACT |
| TASK-11 | Audit setup/packages reproducibility. | high | soon | Codex | setup/packages scripts/templates | No install logic in packages; hash/layout validation | Reproducible package flow | Execute prompt Phase F | WORKSTREAM-06 | FACT |
| TASK-12 | Align setup tests with spec requirements. | high | soon | Codex | setup/tests, CTest/TestX | Coverage map and missing minimal tests | Partial/corrupt/idempotent/uninstall/rollback tests | Execute prompt Phase G | WORKSTREAM-01 | FACT |
| TASK-13 | Create/verify setup baseline docs and freeze marker. | high | soon | Codex | docs/ | SETUP_ARCHITECTURE, CONTRACTS, FAILURE_MODES, BASELINE_FROZEN | Stable baseline for future planning | Execute prompt Phase H | WORKSTREAM-01 | FACT |
| TASK-14 | Verify offline and network acquisition implementation. | medium | later | Setup developer | setup/core/fetch, schemas | Fetch behavior and tests | Offline/local/cache and optional network path documented | Audit after schema baseline | WORKSTREAM-06 | INFERENCE |
| TASK-15 | Verify update/downgrade CLI and schema semantics. | medium | later | Setup developer | setup CLI/schema | Commands/reports/status codes | Explicit update/downgrade flows documented/testable | Audit operation matrix | WORKSTREAM-06 | INFERENCE |
| TASK-16 | Define or verify app command spine for CLI/TUI/GUI parity. | medium | later | Application layer developer | APP canon, repo state | Existing appcmd or equivalent | Shared command graph, deterministic output | Inspect existing libs/tools; create only if absent and canon permits | WORKSTREAM-07 | INFERENCE |
| TASK-17 | Define or verify UI IR schema and binding validation. | medium | later | Application/UI developer | APP-UI-BIND-0, schema/ | UI IR path and validation scripts | Declarative UI with accessibility/localization metadata | Consult CANON_INDEX.md then inspect schema | WORKSTREAM-07 | INFERENCE |
| TASK-18 | Verify RepoX/TestX/BUILD-ID integration. | high | later | Build/release developer | RepoX/TestX docs/tools | Build ID stamping and changelog generation | Apps display generated metadata and refuse mismatches | Inspect CANON_INDEX.md and tooling | WORKSTREAM-08 | PROJECT-CONTEXT |
| TASK-19 | Preserve old-chat report package and store with future chat packages. | highest | current | Assistant/user | This response | Markdown/YAML/ZIP outputs | Reusable report package | Download/store ZIP and key files | WORKSTREAM-10 | FACT |
| TASK-20 | Aggregate this package with other old-chat packages later. | medium | later | Future aggregator chat | Multiple packages | All per-chat reports | Project Spec Book and Master Living State File | Use aggregator prompt once all packages collected | WORKSTREAM-10 | FACT |

## 4. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Setup is sole authority for installation/system state mutation. | Architectural | hard | User canonical setup prompts | No launcher/client/tools install logic | high | FACT | 5 |
| CONSTRAINT-02 | Launcher may invoke setup but must not reimplement setup logic. | Architectural | hard | User prompts | Launcher reads reports and calls setup | high | FACT | 5 |
| CONSTRAINT-03 | Engine must not know setup exists. | Architectural | hard | User prompts | No setup headers/links/concepts in engine | high | FACT | 5 |
| CONSTRAINT-04 | Setup may depend only on libs/ and schema/. | Dependency | hard | Canonical dependency rules | No engine/game/launcher internals | high | FACT | 5 |
| CONSTRAINT-05 | Public setup APIs live only under setup/include/dsk and setup/include/dsu. | Include ownership | hard | Canonical include rules | No setup exports elsewhere | medium-high | FACT | 5 |
| CONSTRAINT-06 | Setup internal headers stay under setup/core/**. | Include ownership | hard | Canonical include rules | No platform/ui private leaks | medium | FACT | 5 |
| CONSTRAINT-07 | No setup headers may be included by engine or game. | Include ownership | hard | Canonical include rules | CMake/scripts must fail violations | high | FACT | 5 |
| CONSTRAINT-08 | Engine/include exports only domino engine ABI. | Include ownership | hard | Final purity prompt | No dsu/dui/dominium in engine include | high | FACT | 5 |
| CONSTRAINT-09 | Cross-product contracts live in libs/contracts/include/dom_contracts. | Architecture | hard | Final purity prompt | Launcher/setup/tools/game use neutral contracts; engine not | medium-high | FACT | 5 |
| CONSTRAINT-10 | No global include_directories except minimal config headers. | Build | hard | Codex prompt | All includes are target-scoped | medium | FACT | 4 |
| CONSTRAINT-11 | CMake is authoritative; generated IDE projects are not source-of-truth. | Build | hard | Codex prompt and earlier recommendation | No hand-authored vcxproj/xcodeproj authority | medium | FACT | 4 |
| CONSTRAINT-12 | Keep repo buildable after each commit in Codex phases. | Process | hard | Codex prompts | Small commits and smoke tests | high | FACT | 5 |
| CONSTRAINT-13 | Do not delete code; quarantine obsolete code under legacy/ with README. | Process | hard | Codex prompts | Preserve history and behavior | medium | FACT | 5 |
| CONSTRAINT-14 | Do not redesign settled architecture or simulation rules. | Scope | hard | Application/project canon | Implementation/audit only | high | FACT / PROJECT-CONTEXT | 5 |
| CONSTRAINT-15 | Applications are content-agnostic and contain no gameplay logic. | Application | hard | Application canon | No pack/rule assumptions in apps | high | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-16 | Applications must run with zero content packs installed. | Application | hard | Application canon | Missing content is diagnostic/raw keys, not crash or defaults | medium-high | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-17 | CLI is canonical; GUI/TUI are views over same command graph. | Application/UI | hard | Application canon | No UI-specific behavior drift | medium-high | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-18 | UI is declarative IR/data; no business logic embedded. | UI | hard | Application canon | Binding validation required | medium-high | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-19 | Accessibility requirements apply to GUIs. | UI | hard | Application canon | Keyboard, screen-reader tags, font/contrast, no color-only semantics | medium | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-20 | Localization strings externalized; raw-key fallback if locale missing. | UI | hard | Application canon | Locale packs are normal packs; no hardcoded UI strings | medium | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-21 | Tools are read-only by default. | Application | hard | Application canon | Mutating tools explicit and gated | medium | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-22 | RepoX is source of truth for changelogs and compatibility/build metadata. | Release | hard | Application/release canon | No manual changelog editing | medium-high | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-23 | BUILD-ID-0 versioning model is locked. | Release | hard | Latest canon | SemVer + build kind + GBN/BII; mismatch refuses loudly | high | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-24 | No distributed artifact without GBN. | Release | hard | BUILD-ID-0 canon | Release gating required | high | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-25 | Engine is C89; game is C++98. | Language | hard | Latest canon | Application choices must not impose newer requirements | medium-high | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-26 | No C++ ABI leakage across public boundaries. | ABI | hard | Latest canon | Stable C ABI preferred where needed | medium-high | FACT / PROJECT-CONTEXT | 4 |
| CONSTRAINT-27 | Setup manifests must avoid arbitrary executable scripts; actions are declarative/sandboxed. | Security | hard | Initial setup prompt | Deterministic and safe installs | medium | FACT | 4 |
| CONSTRAINT-28 | No silent repair or hidden mutation. | Behavior | hard | Setup prompts | Repair/update/downgrade are explicit | high | FACT | 5 |
| CONSTRAINT-29 | Installed-state is setup-written and launcher-read-only. | State | hard | Setup handoff rules | No launcher state mutation | high | FACT | 5 |
| CONSTRAINT-30 | Transactions use preflight/stage/install/verify/commit/rollback and avoid live in-place mutation. | Behavior | hard | Setup transaction model | Journaled rollback and fault tests | high | FACT | 5 |
| CONSTRAINT-31 | Package scripts/templates must not decide install logic. | Packaging | hard | Canonical packaging model | Packages assemble artifacts only | medium-high | FACT | 4 |
| CONSTRAINT-32 | Offline installs must not require network. | Distribution | hard | User asked/offline support accepted | Network is optional fetch transport | medium | FACT / INFERENCE | 4 |
| CONSTRAINT-33 | External/world-current facts and tool versions require verification before future use. | Evidence | hard | User/report requirements | VS2026/toolchain details may change | medium | FACT | 5 |
| CONSTRAINT-34 | Do not copy third-party installer branding/text/logos/assets. | Legal/IP | hard | Initial user prompt | Original generic UI text/assets only | medium | FACT | 5 |
| CONSTRAINT-35 | Report package must label important items as FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | Output | hard | Current user request | Aggregation can preserve provenance | medium | FACT | 5 |

## 5. User Preference Register

| ID | Preference | Source type | Source basis | Strength | Implication | Risk | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Responses should start with GPT-X.Y — YYYY-MM-DD HH:MM:SS local time. | Explicit | User profile/instructions | high | Future assistants should preserve prefix unless higher-priority rules conflict. | User may consider response malformed if omitted. | FACT |
| PREF-02 | Optimize for epistemic accuracy, decision utility, and long-term correctness. | Explicit | User profile/instructions | high | Use labels, verification queues, avoid unsupported claims. | Overconfident summaries degrade trust. | FACT |
| PREF-03 | Separate FACT, INFERENCE, ESTIMATE/UNCERTAIN where relevant. | Explicit | User profile/instructions and current request | high | Registers should preserve provenance. | Tentative items may become false decisions. | FACT |
| PREF-04 | Engineering precision, no marketing tone. | Explicit | Multiple user prompts | high | Use concrete file-level plans and checklists. | Verbose hype or vague prose is unwanted. | FACT |
| PREF-05 | Do not restart locked plans; continue and amend. | Explicit | User canonical setup prompt | high | Respect canon and existing implementation. | Redesign wastes work and may violate canon. | FACT |
| PREF-06 | User values direct copy-paste prompts for Codex. | Inferred | User asked for prompts and applied prompts | medium-high | When generating prompts, make them self-contained and phased. | Non-actionable prompts are less useful. | INFERENCE |
| PREF-07 | User prefers shallow, logical, industry-practice directory structures. | Explicit | User asked directory-tree questions | medium-high | Avoid unnecessary nesting and generic source dirs. | Structural complexity causes confusion. | FACT |
| PREF-08 | User wants downloadable, reusable report packages for old chats. | Explicit | Current request | high | Create files/ZIP if possible. | Plain summary alone is insufficient. | FACT |

## 6. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Were the two applied Codex prompts completed successfully in the actual repo? | Determines whether to audit outputs or execute remaining fixes. | User says they were applied. | Build/test/file state not shown in this chat. | Inspect git commits, tree, CMake, scripts. | highest | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Has the generated Setup final spec alignment prompt been executed? | Determines immediate next action. | Prompt was generated in this chat. | No execution result visible. | Check for docs/SETUP_GAPS.md and related files/commits. | highest | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | What is the current exact setup/ tree? | Avoids acting on stale paths. | Canonical layout known. | Actual file state unknown. | Inspect tree /f setup. | highest | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What schema files exist under schema/setup/? | Setup I/O must be schema-backed. | Schema families were planned. | Actual files unknown. | Inspect schema/ and schema docs. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Does libs/contracts exist and compile? | Neutral contracts are mandatory. | Final purity prompt mandates it. | Actual headers/CMake unknown. | Inspect libs/contracts and build graph. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Do setup --help and launcher --help run? | Smoke test for application products. | Prompts require CLI stubs at minimum. | Build output not shown. | Run built executables. | highest | WORKSTREAM-01, WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Do verify_tree_sanity and verify_includes_sanity reflect current invariants? | Enforcement must match canon. | Prompts require hardened scripts. | Script contents/results unknown. | Run/inspect scripts. | high | WORKSTREAM-02, WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Is app command spine already implemented? | Needed for CLI/TUI/GUI parity. | Application canon requires shared command graph. | Exact implementation/path unknown. | Inspect libs/tools/application code; consult CANON_INDEX.md. | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | Where exactly should UI IR live? | Avoids inventing schema path. | UI IR required by canon. | Exact path not locked in visible chat. | Consult CANON_INDEX.md / APP-UI-BIND-0. | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | How mature is setup/core/fetch network support? | Affects offline/online install claims. | Architecture supports it. | Implementation unknown. | Inspect setup/core/fetch and tests. | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | Are update/downgrade operations represented in CLI, schema, tests? | Required capabilities may be stubs. | Design supports them. | Implementation unknown. | Inspect CLI help, schemas, tests. | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | How much legacy Win9x/macOS Classic work is expected now? | Avoids overbuilding low-priority legacy targets. | Legacy support desired. | Immediate implementation priority unclear. | Ask user or inspect roadmap/docs. | medium-low | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Are RepoX/TestX/BUILD-ID tools present and wired into CI? | Release/app metadata governance depends on them. | Canon requires them. | Actual tool state unknown. | Inspect ci/, tools/, docs, scripts. | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | Are old IDE artifacts removed/quarantined? | Prevents build divergence. | Old tree had .sln/.vcxproj/.xcodeproj. | Post-refactor state unknown. | Inspect repo for project files and legacy READMEs. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | Does documentation status header policy exist and pass checks? | CLEAN-2/canon management requires status headers. | Latest canon says docs have status headers. | Actual docs unknown. | Inspect docs and RepoX checks. | medium | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |

## 7. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Initial six installer reference images | image attachments | Visual setup/installer references | historical | User first message / developer file IDs | low | No design dependency established | FACT |
| ARTIFACT-02 | Initial GPT-5.2 MASTER PROMPT — DOMINIUM / DOMINO SETUP & INSTALLATION SYSTEM | prompt | Original setup scope and constraints | superseded structurally; core invariants persist | User | yes | Includes legal/IP, common setup core, platform adapters, CLI, transactions | FACT |
| ARTIFACT-03 | Phase 1 Setup Core Architecture output | assistant plan | Core module architecture | conceptually useful; paths superseded | Assistant | yes | Modules: manifest, resolve, plan, txn, fs, state, log, platform_iface | FACT |
| ARTIFACT-04 | Plan S | assistant plan | Plan of plans S-0..S-15 | conceptually useful; paths updated by later canon | Assistant | yes | Setup Core, schemas, transaction, adapters, testing/docs | FACT |
| ARTIFACT-05 | Early /source/setup directory skeletons | assistant/user trees | Early structure exploration | superseded | User/Assistant | historical only | Includes setup/adapters/packaging/tests/docs | FACT |
| ARTIFACT-06 | VS workload and language recommendation | assistant output | Toolchain decision support | still relevant unless canon changes | Assistant | yes | Desktop Development with C++; C/C++ not .NET for setup execution | FACT / INFERENCE |
| ARTIFACT-07 | VS/Xcode CMake workflow guidance | assistant output | IDE integration model | still relevant | Assistant | yes | Open folder/generate projects; build dirs disposable | FACT |
| ARTIFACT-08 | Second setup master prompt: DOMINIUM / DOMINO SETUP SYSTEM | prompt | Restarted setup planning from scratch | superseded by existing implementation/canonical repo | User | partial | Invariants persist | FACT |
| ARTIFACT-09 | Old/current setup directory tree from Windows tree output | repo snapshot text | Evidence of outdated/redundant setup files | historical; actual state now unverified | User | yes | Showed adapters, core/source, dsk/dsu, package dirs, tests/golden | FACT |
| ARTIFACT-10 | Assistant analysis of old tree | assistant output | Structural diagnosis | partially superseded | Assistant | yes | Identified mixed concerns, DSK/DSU drift, IDE artifacts, duplicate mains | FACT |
| ARTIFACT-11 | Canonical repo/setup structure prompt | prompt | Locked top-level and setup filesystem/dependencies | current authoritative | User | critical | Defines setup/core, include, packages, platform, tests, ui | FACT |
| ARTIFACT-12 | Plan S amendments for canonical repo | assistant output | Updated setup plan to canonical structure | current where consistent | Assistant | yes | Maps old paths to new; defines enforcement | FACT |
| ARTIFACT-13 | Phase 2 authoritative setup directory tree | assistant output | Concrete canonical setup file tree | useful reference; actual repo unverified | Assistant | yes | Expected files under dsk/dsu/core/platform/ui/packages/tests | FACT |
| ARTIFACT-14 | Applied Codex Prompt 1 — One-pass refactor + repair + future-proof for VS2026 + CMake + Codex | prompt | Repo build/refactor enforcement | authoritative and said applied | User | critical | Phases 0-8; build smoke tests; CMakePresets | FACT |
| ARTIFACT-15 | Applied Codex Prompt 2 — Final purity + contract ownership repair | prompt | Engine purity and contract relocation | authoritative and said applied | User | critical | Evict engine contamination; create libs/contracts; harden scripts | FACT |
| ARTIFACT-16 | Phase 3 schema definitions assistant output | assistant plan | Install plan/state/verify/audit schema proposal | useful; implementation unverified | Assistant | yes | Defines launcher handoff by schema only | FACT |
| ARTIFACT-17 | Generated prompt — Dominium Setup: Final Spec Alignment, Gap Closure, and Hardening Pass | prompt | Setup code/docs final hardening | critical next action if not executed | Assistant | critical | Phases A-H; setup gaps, schemas, kernel, platform, UI, packages, tests, docs | FACT |
| ARTIFACT-18 | Offline/net/update/customization capability mapping | assistant output | Capability decision explanation | accepted unless contradicted | Assistant | yes | Offline, network, update check, repair, uninstall, upgrade, downgrade, rollback | FACT / INFERENCE |
| ARTIFACT-19 | Application-layer canon prompt | prompt | Application layer rules | authoritative project context pasted here | User | critical | CLI canonical, UI IR, content-agnostic apps, setup authority | FACT / PROJECT-CONTEXT |
| ARTIFACT-20 | Latest other-chat project/application/release canon prompt | prompt | Full project status and release governance | authoritative project context pasted here | User | critical | Core ontology, T0-T24, BUILD-ID-0, RepoX/TestX, APP canon | FACT / PROJECT-CONTEXT |
| ARTIFACT-21 | Assistant app-layer spine proposal | assistant output | Potential implementation next steps | proposal, not fully locked | Assistant | carry with caution | libs/appcmd, UI IR, RepoX metadata library | INFERENCE |
| ARTIFACT-22 | Maximum-fidelity Context Transfer Packet | assistant output | Retired-chat handoff | input to this report package | Assistant | critical | Contains bootstrap, registers, artifact ledger, audit | FACT |
| ARTIFACT-23 | This final report package | generated files | Downloadable/shareable report bundle | created by this response | Assistant | critical | Seven files plus ZIP if generation succeeds | FACT |

## 8. Rejected / Superseded Options Register

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Put setup business logic in per-OS installers/adapters. | rejected | Violates one common setup core and no duplicated OS logic. | final | Only if canon changes | WORKSTREAM-01 | FACT |
| REJECTED-02 | Launcher directly installs, repairs, or updates files. | rejected | Violates setup authority. | final | Never under current canon | WORKSTREAM-04 | FACT |
| REJECTED-03 | Engine references setup/launcher/tools APIs. | rejected | Violates engine purity. | final | Never under current canon | WORKSTREAM-03 | FACT |
| REJECTED-04 | Use .NET for authoritative setup execution path. | rejected | Runtime/legacy/offline/ABI risk; C/C++ recommended and continued. | final for setup execution | Only for non-authoritative developer/management tools | WORKSTREAM-01, WORKSTREAM-09 | FACT / INFERENCE |
| REJECTED-05 | Hand-authored VS/Xcode projects as authoritative build files. | rejected | Causes IDE drift; CMake is authority. | final | Generated build-dir projects allowed | WORKSTREAM-02 | FACT |
| REJECTED-06 | Store packaging under adapters/platform directories. | superseded | Canonical model uses setup/packages/. | final | Only if canonical layout changes | WORKSTREAM-06 | FACT |
| REJECTED-07 | Old setup/adapters/** tree as active layout. | superseded | Canonical setup/platform + setup/ui superseded it. | final | Only as legacy/quarantine | WORKSTREAM-01 | FACT |
| REJECTED-08 | Old top-level setup/packaging/** layout. | superseded | Canonical setup/packages/** superseded it. | final | Only if canon changes | WORKSTREAM-06 | FACT |
| REJECTED-09 | Generic source/ directories under canonical setup layout. | rejected | User prohibited reintroducing generic source directories. | final | Never under setup canon | WORKSTREAM-01 | FACT |
| REJECTED-10 | Top-level components/ proposal. | superseded | User later locked top-level products instead. | final | Only if repo canon changes | WORKSTREAM-02 | FACT / INFERENCE |
| REJECTED-11 | Shared/foundation proposal as named structure. | superseded | Canon uses libs/ and schema/ instead. | tentative | Could reappear as specific libs module if canon permits | WORKSTREAM-02 | INFERENCE |
| REJECTED-12 | Arbitrary executable scripts in install manifests. | rejected | Security/determinism risk; declarative actions only. | final | Only sandboxed/declarative equivalents | WORKSTREAM-01 | FACT |
| REJECTED-13 | Silent repair or hidden mutation. | rejected | Violates auditability and explicit operation rules. | final | Never | WORKSTREAM-01 | FACT |
| REJECTED-14 | Manual changelog editing. | rejected | RepoX is source of truth. | final | Never under current canon | WORKSTREAM-08 | FACT / PROJECT-CONTEXT |
| REJECTED-15 | Tools mutating by default. | rejected | Tools are read-only by default. | final | Explicit/gated mutation tools only | WORKSTREAM-05 | FACT / PROJECT-CONTEXT |

## 9. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant follows obsolete adapters/packaging/source layout. | Canonical setup structure may be corrupted. | medium | high | Always start from latest canonical setup/ layout. | WORKSTREAM-01 | FACT / INFERENCE |
| RISK-02 | Assistant suggestions are mistaken for user decisions. | Spec may harden tentative ideas incorrectly. | medium | high | Keep FACT/INFERENCE labels and require user/canon confirmation. | WORKSTREAM-10 | FACT |
| RISK-03 | Repo state differs from this packet. | Implementation may target missing or moved files. | high | high | Inspect repo before acting. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-04 | Launcher duplicates setup update/repair logic. | Authority and audit guarantees break. | medium | high | Use setup invocation + schema reports only. | WORKSTREAM-04 | FACT |
| RISK-05 | Engine purity regresses. | Engine becomes unreusable and contaminated. | medium | high | Run tree/include sanity checks in CI. | WORKSTREAM-03 | FACT |
| RISK-06 | Ad-hoc setup formats drift from schema. | Launcher/setup incompatibility and unverifiable state. | medium | high | Execute schema normalization phase. | WORKSTREAM-04 | FACT / INFERENCE |
| RISK-07 | GUI/TUI embeds business logic. | CLI parity and determinism are broken. | medium | medium-high | Use command graph + UI IR binding validation. | WORKSTREAM-07 | FACT / PROJECT-CONTEXT |
| RISK-08 | Network install becomes required unintentionally. | Offline/air-gapped support fails. | medium | medium-high | Test offline install paths and treat network as transport. | WORKSTREAM-06 | FACT / INFERENCE |
| RISK-09 | Rollback is under-tested. | Partial installs may corrupt state. | medium | high | Fault-injection tests for each transaction phase. | WORKSTREAM-01 | FACT |
| RISK-10 | Build metadata/changelog manually edited. | Release traceability lost. | medium | medium-high | Use RepoX-generated outputs only. | WORKSTREAM-08 | FACT / PROJECT-CONTEXT |
| RISK-11 | Legacy platform goals impose modern app constraints on engine/game. | Toolchain compatibility breaks. | medium | medium | Keep app toolchains isolated from engine/game. | WORKSTREAM-09 | FACT |
| RISK-12 | Context package omits exact old prompt wording. | Future re-execution may miss nuance. | medium | medium | Use artifact ledger and request original prompt if exact replay required. | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| RISK-13 | Future aggregation deduplicates conflicting chats too aggressively. | Contradictions may be erased. | medium | high | Preserve provenance and contradictions during aggregation. | WORKSTREAM-10 | FACT |
| RISK-14 | Dates/tool versions become stale. | Build instructions may fail later. | medium | medium | Verify external/toolchain facts before use. | WORKSTREAM-02 | FACT |
| RISK-15 | Generated report files are edited manually and diverge. | Aggregation data integrity weakens. | low | medium | Store ZIP and Markdown/YAML together; note manual changes. | WORKSTREAM-10 | FACT |

## 10. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current setup/ tree | Needed to determine actual post-refactor state. | tree /f setup or repo inspection | highest | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Current schema/ tree | Schema-backed setup I/O is required. | tree /f schema and schema docs | highest | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | libs/contracts existence and CMake target | Neutral contracts are mandatory. | tree /f libs/contracts, CMake build | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | CMake configure/build/test | Build claims require proof. | cmake --preset, build, ctest | highest | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | setup --help and launcher --help | Smoke tests required by prompts. | Run built executables | highest | WORKSTREAM-01, WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | verify_tree_sanity and verify_includes_sanity scripts | Boundary enforcement must work. | Run/inspect scripts | high | WORKSTREAM-02, WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | docs/SETUP_GAPS.md and related setup docs | Shows generated hardening prompt executed. | docs inspection | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | setup/core/fetch offline/network behavior | Capability accepted but implementation unknown. | Source/tests inspection | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | update/downgrade operation semantics | Required flows need explicit schemas/tests. | CLI/schema/tests inspection | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | UI IR and binding validation path | Canon requires UI as data. | CANON_INDEX.md, APP-UI-BIND-0, schema/ | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | RepoX/TestX/BUILD-ID tooling status | Release governance depends on it. | RepoX/TestX docs/tools/CI | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Legacy platform support status | Avoids assuming implementation exists. | platform/win9x, mac/classic, docs | medium-low | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Old IDE artifacts are quarantined or non-authoritative | Prevents IDE build drift. | find .sln/.vcxproj/.xcodeproj; inspect legacy READMEs | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Docs status-header policy | CLEAN-2/canon management requires it. | docs and RepoX checks | medium | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | This package contents after generation | Ensure files and ZIP saved correctly. | Open downloaded files/ZIP | high | WORKSTREAM-10 | FACT |

## 11. Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | Initial setup master prompt | User defined setup/installer system scope, legal/IP limits, common core, manifests, transaction model, adapters, CLI, testing/docs. | Established initial setup architecture frame. | Historical but foundational | high |
| 2 | Phase 1 setup core architecture | Assistant designed modules and transaction/determinism model. | Created baseline conceptual architecture. | Conceptually relevant; paths superseded | high |
| 3 | Plan S requested and produced | User asked for plan-of-plans; assistant produced S-0..S-15. | Organized future setup design work. | Conceptually relevant | high |
| 4 | Empty /source/setup implementation discussion | User wanted VS2026, Watcom, Xcode, Linux/storefront/legacy support with native IDEs. | Drove early directory and toolchain thinking. | Superseded structurally | high |
| 5 | Early directory trees and refinements | Assistant and user iterated on setup/core/adapters/packaging/tests/docs and macosc. | Produced historical layout ideas. | Superseded by canonical repo | high |
| 6 | Improvement suggestions | Assistant proposed ABI headers, platform iface split, policy module, bridge common, declarative packaging. | Some ideas carried forward conceptually. | Partially relevant | medium-high |
| 7 | Step-by-step skeleton and minimal CMake | Assistant gave skeleton and minimal core/CLI build steps. | Early implementation path. | Superseded by actual repo/canonical layout | medium |
| 8 | VS workload and language question | Assistant recommended Desktop Development with C++ and C/C++ setup, not .NET execution. | Toolchain rationale accepted by continuation. | Still relevant | medium-high |
| 9 | VS/Xcode project location question | Assistant recommended generated projects via CMake and disposable build dirs. | Build authority direction reinforced later. | Still relevant | high |
| 10 | New setup master prompt: start from scratch | User reset setup planning with core/adapters/schemas/tests philosophy. | Prompt drove another Phase 1. | Later superseded by existing implementation/canonical repo | medium-high |
| 11 | User posted old/current setup tree | User showed extensive redundant/outdated setup tree. | Provided concrete evidence of structural drift. | Historical risk source | high |
| 12 | Old tree improvement analysis | Assistant recommended moving packaging, removing IDE artifacts, clarifying DSK/DSU. | Fed later canonical thinking. | Partially superseded | medium-high |
| 13 | Future components and nested source critique | User questioned source subdirectories and future tools/components; assistant proposed broader structure. | Raised scalability concerns. | Superseded by canonical top-level products | medium |
| 14 | Canonical repo/setup structure prompt | User locked top-level products, setup authority, canonical setup layout, dependencies, include ownership. | Changed ground truth and superseded old layouts. | Current critical | high |
| 15 | Plan S amendments | Assistant realigned setup plan to canonical repo. | Updated phase mapping and enforcement model. | Current relevant | high |
| 16 | Phase 2 canonical directory tree | Assistant produced expected setup tree and target naming contract. | Reference for implementation checks. | Useful but actual repo unverified | high |
| 17 | Two applied Codex prompts pasted | User stated refactor/build and purity/contract prompts had been applied. | Established new implementation baseline assumptions. | Critical; verify actual repo | high |
| 18 | Phase 3 schema definitions | Assistant defined schema families and launcher handoff. | Continued plan under new constraints. | Useful; implementation unverified | medium-high |
| 19 | Generated setup hardening prompt | User requested prompt to close gaps; assistant produced phases A-H. | Actionable artifact for next implementation pass. | Critical if not executed | high |
| 20 | Capability question | User asked about offline/net/update/customization/repair/uninstall/downgrade; assistant mapped support. | Clarified intended setup capabilities. | Current relevant | medium-high |
| 21 | Application-layer canon pasted | User provided locked application scope and UI/UX/RepoX/SRZ rules. | Expanded context to application layer. | Current project context | high |
| 22 | Latest other-chat canon pasted | User provided full project status, ontology, versioning, automation. | Reinforced no redesign and release governance. | Current project context | high |
| 23 | Context Transfer Packet requested and produced | User retired chat; assistant created maximum-fidelity packet. | Baseline for this report. | Input to current package | high |
| 24 | Final report package requested | User asked to convert packet into downloadable, reusable package. | Current output task. | Current | high |

## 12. Spec Book Contribution Register

| ID | Contribution | Likely spec section | Status | Needs verification | Label |
| --- | --- | --- | --- | --- | --- |
| SPEC-01 | Setup sole authority and deterministic transaction model | Setup System Architecture | formal requirement candidate | implementation tests | FACT |
| SPEC-02 | Canonical setup filesystem layout | Repository Layout | formal requirement | repo tree | FACT |
| SPEC-03 | Schema-only setup-launcher handoff | Contracts and Schemas | formal requirement | schema files | FACT |
| SPEC-04 | Engine purity and neutral contracts | Architecture Boundaries | formal requirement | CMake/scripts | FACT |
| SPEC-05 | CMake/VS2026 build enforcement | Build System | formal requirement | configure/build/test | FACT |
| SPEC-06 | Offline/online and update/repair/downgrade support | Distribution and Setup Operations | formal requirement candidate | implementation status | FACT / INFERENCE |
| SPEC-07 | Application command graph and UI IR | Application Layer | formal requirement from project context | canon docs/path | FACT / PROJECT-CONTEXT |
| SPEC-08 | RepoX/TestX/BUILD-ID release governance | Release Governance | formal requirement from project context | tooling | FACT / PROJECT-CONTEXT |
| SPEC-09 | Legacy platform support goals | Platform Support | background/context plus future requirement | priority and implementation | FACT |
| SPEC-10 | Per-chat report packaging workflow | Project Knowledge Management | process requirement candidate | aggregation test | FACT |
