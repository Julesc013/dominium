# Registers — Dominium Launcher Application Layer Handoff

## 1. Workstream Register

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

## 2. Decision Register

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

## 3. Task Register

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

## 4. Constraint Register

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

## 5. User Preference Register

| ID | Preference | Source type | Source basis | Strength | Implication | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Responses should start with model/date/time prefix. | Explicit | User profile instruction. | strong | Future assistants should preserve requested prefix when possible. | May conflict with strict output formats; higher-priority instructions win. | FACT |
| PREF-02 | Epistemic accuracy, decision utility, long-term correctness. | Explicit | User profile. | strong | Prioritize rigorous labeled facts over engagement. | Overconfident inference will frustrate user. | FACT |
| PREF-03 | Correctly cited sources and unbiased rigorously tested facts. | Explicit | User profile. | strong | Use citations/verification when external or current facts matter. | Unverified current claims should be labelled. | FACT |
| PREF-04 | Deliver answers, not dialogue; ask only if missing info blocks correctness. | Explicit | User profile. | medium-high | Prefer concrete outputs and next actions. | Unnecessary questions slow implementation. | FACT |
| PREF-05 | Mechanical enforcement over convention. | Inferred | Repeated emphasis on CMake/CI/scripts/boundaries. | high | Design prompts should include scripts, tests, stop conditions. | Purely aspirational docs may be rejected. | INFERENCE |
| PREF-06 | Codex-style phased prompts with commits and verification commands. | Inferred | User repeatedly requested/generated such prompts. | high | When asked for prompts, use execution phases and stop conditions. | Vague plans will be less useful. | INFERENCE |
| PREF-07 | Preserve uncertainty, rejected options, and changes of direction. | Explicit | Context transfer/package request. | strong | Do not compress away superseded options. | Future aggregation may repeat mistakes. | FACT |

## 6. Open Questions Register

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

## 7. Artifact Ledger

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

## 8. Rejected / Superseded Options Register

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

## 9. Risk Register

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

## 10. Verification Queue

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

## 11. Timeline Register

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

## 12. Spec Book Contribution Register

| ID | Contribution | Likely spec section | Requirement candidate | Needs verification | Label |
| --- | --- | --- | --- | --- | --- |
| SPEC-01 | Launcher product structure and boundaries | Applications / Launcher | launcher/ canonical structure; no engine/setup internals | Current repo matches structure | FACT |
| SPEC-02 | Application command graph and UI IR requirements | Application UI/UX | CLI canonical; GUI/TUI views; UI is data; binding validation | Implementation files/tests exist | PROJECT-CONTEXT |
| SPEC-03 | Engine purity and contracts model | Repository Boundaries / Contracts | engine exports only domino; neutral dom_contracts | Scripts/build pass | FACT |
| SPEC-04 | Setup/launcher separation | Setup and Launcher | setup only install mutation authority; launcher consumes manifests/contracts | No direct launcher setup internals | FACT |
| SPEC-05 | Build governance and VS2026 workflow | Build and CI | CMakePresets authoritative; no hand-authored authoritative IDE projects | CMake presets pass | FACT |
| SPEC-06 | RepoX/TestX/BUILD-ID application obligations | Release Governance | build IDs/changelogs/compatibility from RepoX; mismatch refusal | Launcher implementation/tests | PROJECT-CONTEXT |
