# Structured Registers

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Repo convergence and ownership | Keep source layout governed by ownership roots and contracts | CONVERGE docs established authority; exceptions remain | Strict layout with retired exceptions and no root sprawl | Active | P0 | High | FACT |
| WORKSTREAM-02 | Proof spine / build and boot | Prove build, product boot, portable projection, and test gates | Partial/blocked in inspected docs; later docs show build progress but RepoX/CTest blockers | Green product boot and portable projection proof | Active | P0 | Medium | FACT |
| WORKSTREAM-03 | Operating environment doctrine | Formalize Dominium as deterministic simulation operating environment | Strong conceptual direction; not yet formal doctrine | Approved doctrine mapping kernel/contracts/services/drivers/domains/apps/packs | Proposed | P1 | Medium-high | INFERENCE |
| WORKSTREAM-04 | Interface Operating Layer | Create shared CLI/TUI/rendered/headless command/document/result spine | Defined in discussion; not implemented | Reusable interface law across products/modules | Proposed | P0 | Medium-high | INFERENCE |
| WORKSTREAM-05 | Command dispatch unification | Replace product-local command forks with one dispatch path | Current adoption partial | Same command/result/refusal across projections | Active/proposed | P0 | High | FACT/INFERENCE |
| WORKSTREAM-06 | Dominium Workbench | Build modular rendered tools host as proof surface | Concept accepted direction; law conflict remains | Workbench shell + modules over shared runtime services | Proposed | P1 | Medium-high | INFERENCE |
| WORKSTREAM-07 | No-assets UI floor | Guarantee primitive rendered UI works without optional assets | GUI baseline doc supports this; current implementation minimal | Product-grade primitive UI controls and themes | Active/proposed | P1 | High | FACT/INFERENCE |
| WORKSTREAM-08 | Packaging/release/distribution | Use deterministic packages, profiles, manifests, thin installers | Docs support model; implementation status varied | Offline-verifiable bundle/package/release pipeline | Active | P1 | High | FACT |
| WORKSTREAM-09 | Platform/render/native lanes | Plan old/compat/modern binary and GUI lanes | Discussed; not ready for expansion | Matrix-driven support tiers and proof-backed binaries | Deferred | P2 | Medium | INFERENCE |
| WORKSTREAM-10 | Domain/modding/data-driven evolution | Split domains and externalize registries/descriptors | Domain split rules exist; runtime data-driven behavior partial | Pack/module/domain activation through contracts and validators | Active/proposed | P1 | Medium | FACT/INFERENCE |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | CLI mandatory, TUI expected, GUI modular | Accepted direction | Repeated baseline and AppShell docs | Avoids GUI lock-in | Defines all products | WORKSTREAM-04 | High | FACT |
| DECISION-02 | Thin shells over shared backend/contracts | Accepted direction | GUI and AppShell discussions | Prevents product drift | Shapes client/launcher/setup/server/tools | WORKSTREAM-04 | High | FACT/INFERENCE |
| DECISION-03 | Ownership-based repo layout | Accepted/current authority | Post-CONVERGE docs | Makes validation possible | Guides all future moves | WORKSTREAM-01 | High | FACT |
| DECISION-04 | Domain split across contracts/game/content/docs/tests | Accepted/current rule | Domain split docs | Avoids topic-root chaos | Guides domain work | WORKSTREAM-10 | High | FACT |
| DECISION-05 | Deterministic simulation operating environment framing | Strong direction | User proposed; assistant endorsed | Fits full ambition better than game-only | Needs doctrine | WORKSTREAM-03 | Medium-high | INFERENCE |
| DECISION-06 | Workbench modular host, not monolithic editor | Accepted direction | User supplied and assistant agreed | Avoids old UI Editor failure | Shapes tools architecture | WORKSTREAM-06 | High | FACT/INFERENCE |
| DECISION-07 | Interface Operating Layer under all products | Strong proposed direction | Final UI discussion | Generalizes Workbench into platform | Needs INTERFACE-LAW-00 | WORKSTREAM-04 | Medium-high | INFERENCE |
| DECISION-08 | Rendered mode product-declared, not client-only | Proposed required change | AppShell conflict identified | Enables rendered Workbench lawfully | Requires contract update | WORKSTREAM-04 | Medium | INFERENCE |
| DECISION-09 | Shipped tool modules outside repo-only tools/ | Proposed/current-rule aligned | Ownership rules | Avoids runtime depending on dev tooling | Guides paths | WORKSTREAM-06 | High | FACT/INFERENCE |
| DECISION-10 | No-assets GUI guaranteed floor | Accepted direction | GUI baseline docs and user plan | Recovery and cross-product UX | Shapes UI controls/themes | WORKSTREAM-07 | High | FACT/INFERENCE |
| DECISION-11 | Layered deterministic packaging | Accepted direction | Distribution/versioning docs | Supports verification/rollback | Shapes releases | WORKSTREAM-08 | High | FACT |
| DECISION-12 | Compatibility lanes, not all products/all eras | Accepted direction | Binary discussion | Controls matrix explosion | Shapes support tiers | WORKSTREAM-09 | Medium-high | INFERENCE |
| DECISION-13 | Avoid arbitrary native plugins early | Proposed direction | Trust/replay risk rationale | Protects determinism/security | Plugin model deferred | WORKSTREAM-06 | Medium | INFERENCE |
| DECISION-14 | Boot-to-replay proof as better MVP | Proposed direction | OS-like discussion | Proves architecture before gameplay sprawl | Shapes MVP | WORKSTREAM-03 | Medium-high | INFERENCE |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Resolve or classify RepoX/CTest blockers | P0 | U0 | Project maintainer | Current repo state | Latest build/test logs | Classified or green gates | Run focused diagnostics | WORKSTREAM-02 | FACT/INFERENCE |
| TASK-02 | Repair canonical verify discovery | P0 | U0 | Project maintainer | Build contract/presets | CTest output | Canonical verify discovers expected tests | Inspect CMake presets/test registration | WORKSTREAM-02 | FACT |
| TASK-03 | Rerun native product boot proof | P0 | U1 | Project maintainer | Built binaries | setup/launcher/client/server/tools binaries | Updated PRODUCT_BOOT_PROOF | Run product help/status/smoke | WORKSTREAM-02 | FACT |
| TASK-04 | Prove portable projection assembly | P0 | U1 | Project maintainer | Product binaries + manifest generators | dist/projection tools | Portable root with manifests | Run projection tool and verification | WORKSTREAM-08 | FACT |
| TASK-05 | Draft DOMINIUM_OPERATING_ENVIRONMENT doctrine | P1 | U1 | Architect | This chat + repo docs | Architecture decisions | Doctrine doc | Draft and review | WORKSTREAM-03 | INFERENCE |
| TASK-06 | Draft INTERFACE-LAW-00 | P0 | U1 | Architect | AppShell/GUI baseline + this chat | Command/result/UI constraints | Interface law doc | Define projections and rules | WORKSTREAM-04 | INFERENCE |
| TASK-07 | Update AppShell rendered-mode law | P0 | U1 | Architect/dev | AppShell constitution | Rendered capability contract | Rendered mode allowed by product declaration | Patch docs/contracts | WORKSTREAM-04 | INFERENCE |
| TASK-08 | Design command_result_v1 and refusal model | P0 | U1 | Architect/dev | Existing command registries | Schemas/registry docs | Shared result/refusal schema | Draft schema | WORKSTREAM-05 | INFERENCE |
| TASK-09 | Unify command dispatch path | P0 | U1 | Dev | Command schemas and registry | Current product command code | Shared dispatch used by CLI/TUI/rendered/headless | Implement service/adapters | WORKSTREAM-05 | FACT/INFERENCE |
| TASK-10 | Externalize first command descriptors | P1 | U1 | Dev | Current C registries | Descriptor schema | Generated/loaded command tables | Pilot client/tools commands | WORKSTREAM-05 | INFERENCE |
| TASK-11 | Design module_descriptor_v1 | P1 | U1 | Architect/dev | Workbench plan | Module registry requirements | Module descriptor schema | Draft contracts/modules schema | WORKSTREAM-06 | INFERENCE |
| TASK-12 | Implement Workbench shell skeleton | P1 | U2 | Dev | Rendered-mode law + command service | runtime UI/render services | Booting software-rendered shell | Create apps/tools/workbench | WORKSTREAM-06 | INFERENCE |
| TASK-13 | Implement Validation Dashboard module | P1 | U2 | Dev | Command service + validators | Validator outputs | Workbench module with CLI/TUI/rendered parity | Wrap validators via command service | WORKSTREAM-06 | INFERENCE |
| TASK-14 | Implement Pack Browser module | P1 | U2 | Dev | Package service/pack metadata | Pack manifests | Inspect/validate packs | Build module | WORKSTREAM-06 | INFERENCE |
| TASK-15 | Build draw-list UI primitives | P1 | U2 | Dev | Software renderer | UI contracts | Rect/line/text/clip/scroll controls | Implement runtime/ui | WORKSTREAM-07 | INFERENCE |
| TASK-16 | Create primitive themes | P2 | U2 | Designer/dev | Theme descriptor | Style tokens | Barebones dark/light/high-contrast etc. | Draft theme registry | WORKSTREAM-07 | INFERENCE |
| TASK-17 | Build renderer sandbox | P2 | U2 | Dev | Renderer service | Draw-list tests | Golden screenshots | Create module | WORKSTREAM-06 | INFERENCE |
| TASK-18 | Build UI/HUD sandbox | P2 | U2 | Dev | UI document schema | UI renderer path | Load/edit/preview UI docs | Create module | WORKSTREAM-06 | INFERENCE |
| TASK-19 | Define boot-to-replay MVP acceptance test | P0 | U1 | Architect/dev | Operating environment doctrine | Kernel/service APIs | Formal MVP gate | Write test plan | WORKSTREAM-03 | INFERENCE |
| TASK-20 | Audit old UI Editor assets/prompts for salvage | P2 | U3 | Architect | Other old chats/files | Old UI editor plans | Salvage/reject ledger | Review artifacts | WORKSTREAM-06 | UNCERTAIN |
| TASK-21 | Update component matrix for Workbench/rendered tools | P1 | U2 | Architect/dev | Component matrix contract | Workbench capability row | Updated matrix | Patch contract/docs | WORKSTREAM-06 | INFERENCE |
| TASK-22 | Retire remaining layout exceptions | P1 | U2 | Maintainer | layout_exceptions.toml | Exception queue | Narrowed/retired exceptions | Scoped passes | WORKSTREAM-01 | FACT |
| TASK-23 | Classify plugin execution tiers | P2 | U2 | Architect/security | Trust model | Module policy | T0-T3 plugin policy | Draft doc | WORKSTREAM-06 | INFERENCE |
| TASK-24 | Design document_patch_v1 | P0 | U1 | Architect/dev | UI/editor workflows | Schema needs | Typed patch/transaction model | Draft schema | WORKSTREAM-04 | INFERENCE |
| TASK-25 | Design evidence packet model for UI/actions | P1 | U2 | Architect/dev | Evidence/release docs | Audit requirements | Command evidence output | Draft schema | WORKSTREAM-04 | INFERENCE |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Source layout authority is post-CONVERGE contract stack | Architecture | Hard | Repo docs | Do not recreate old root sprawl | High | High | FACT |
| CONSTRAINT-02 | Runtime/product code must not depend on repo-only tools/ | Architecture | Hard | Ownership rules | Shipped modules go under apps/runtime/contracts | High | High | FACT |
| CONSTRAINT-03 | UI projections must not own product semantics | Architecture | Hard | GUI/AppShell doctrine | All behavior routes through commands/services | High | High | FACT/INFERENCE |
| CONSTRAINT-04 | Renderer must not own simulation truth | Architecture | Hard | GUI baseline | Render consumes view/draw data only | High | High | FACT |
| CONSTRAINT-05 | No-assets GUI must work | UX/recovery | Hard | GUI baseline + chat | No optional assets required for recovery/product use | Medium | High | FACT/INFERENCE |
| CONSTRAINT-06 | Rendered mode currently client-only in AppShell docs | Doctrine | Hard until changed | AppShell constitution | Workbench rendered mode requires law update | High | High | FACT |
| CONSTRAINT-07 | Facts from repo may be stale later | Verification | Hard | Temporal context | Re-verify before coding/release claims | Medium | High | INFERENCE |
| CONSTRAINT-08 | Do not treat assistant proposals as accepted user decisions | Preservation | Hard | User prompt | Maintain decision statuses | High | High | FACT |
| CONSTRAINT-09 | External platform/toolchain facts require verification | Factuality | Hard | System/user preference | Use official sources before relying | Medium | High | FACT |
| CONSTRAINT-10 | Domain work must split across contracts/game/content/docs/tests | Architecture | Hard | Domain split rules | No new root-level domain folders | High | High | FACT |
| CONSTRAINT-11 | Packs/modules should be capability/trust governed | Modding/security | Hard/soft | Architecture rationale | Avoid unsafe arbitrary mutation | Medium | Medium | INFERENCE |
| CONSTRAINT-12 | CLI/TUI/rendered/headless parity is mandatory goal for serious modules | UX/architecture | Soft-to-hard once formalized | Chat direction | Same command/result/refusal across projections | High | Medium | INFERENCE |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Direct, audit-ready, source-grounded answers | Communication | Explicit | High | Use citations/labels/uncertainty | User distrust if vague | FACT |
| PREF-02 | Human-readable explanation before machine packet | Preservation | Explicit | High | Start with prose narrative | Report becomes unusable | FACT |
| PREF-03 | Preserve tentative vs final status | Accuracy | Explicit | High | Do not overstate decisions | Wrong future work | FACT |
| PREF-04 | Prefer modular/extensible/future-proof architecture | Technical | Explicit/inferred | High | Optimize long-term boundaries | Architecture drift | FACT/INFERENCE |
| PREF-05 | Avoid re-asking answered questions | Workflow | Explicit | High | Proceed with best effort | Wasted time | FACT |
| PREF-06 | Use structured registers and IDs | Aggregation | Explicit | High | Stable IDs for merge | Aggregator failure | FACT |
| PREF-07 | Verify stale facts | Factuality | Explicit | High | Use web/official docs if current facts matter | Stale claims | FACT |
| PREF-08 | Do not hide uncertainty | Epistemic | Explicit | High | Use FACT/INFERENCE/UNCERTAIN | False confidence | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Should operating environment doctrine be formalized before code changes? | It affects all future work | Strongly recommended | User approval/priority | Draft doctrine | P0 | WORKSTREAM-03 | INFERENCE |
| QUESTION-02 | What exact rendered-mode law replaces client-only rule? | Workbench depends on it | Need product-declared capability | Exact contract wording | Patch AppShell/registry | P0 | WORKSTREAM-04 | FACT/INFERENCE |
| QUESTION-03 | Which command registry is canonical runtime authority? | Command parity depends on it | Existing appcore/client registries differ | Final chosen source | Design command service | P0 | WORKSTREAM-05 | FACT |
| QUESTION-04 | What is module_descriptor_v1? | Workbench modules require it | Fields proposed | Schema details | Draft contract | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-05 | What is the first Workbench module? | Determines MVP slice | Validation Dashboard recommended | User confirmation | Pick WB module 1 | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-06 | How much hard-coded client code should be externalized first? | Avoids over-refactor | Commands/stages/UI/interaction identified | Ordering | Create migration map | P1 | WORKSTREAM-05 | INFERENCE |
| QUESTION-07 | Is `engine` renamed or only conceptually kernel? | Affects repo churn | Suggested not to rename yet | User preference | Decide doctrine wording | P2 | WORKSTREAM-03 | UNCERTAIN |
| QUESTION-08 | What plugin tiers are allowed after built-in modules? | Security/modding issue | T0-T3 proposal | Policy details | Draft plugin policy | P2 | WORKSTREAM-06 | INFERENCE |
| QUESTION-09 | What repo build/test status is current today? | Implementation planning depends on it | Prior docs show evolving state | Current logs | Re-run/verify | P0 | WORKSTREAM-02 | UNVERIFIED |
| QUESTION-10 | How should other old-chat reports be merged? | Spec book aggregation | This report has packet | Other reports unknown | Aggregator process | P1 | WORKSTREAM-01 | UNCERTAIN |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Pasted text.txt preservation prompt | Uploaded file | Defines this task and required output | Loaded | User upload | Yes | Must cite in response | FACT |
| ARTIFACT-02 | docs/repo/REPO_LAYOUT_TARGET.md | Repo doc | Current human source layout explanation | Inspected | GitHub connector | Yes | Defines roots and CONVERGE notes | FACT |
| ARTIFACT-03 | docs/repo/OWNERSHIP_RULES.md | Repo doc | Ownership model | Inspected | GitHub connector | Yes | Key for paths/modules | FACT |
| ARTIFACT-04 | docs/repo/DOMAIN_SPLIT_RULES.md | Repo doc | Domain split model | Inspected | GitHub connector | Yes | Key for domain work | FACT |
| ARTIFACT-05 | docs/repo/audits/CONVERGE_12_FINAL_AUDIT.md | Repo doc | Final convergence audit | Inspected | GitHub connector | Yes | Authority stack | FACT |
| ARTIFACT-06 | docs/repo/POST_CONVERGE_NEXT_STEPS.md | Repo doc | Current blockers/next work | Inspected | GitHub connector | Yes | Proof spine priorities | FACT |
| ARTIFACT-07 | docs/appshell/APPSHELL_CONSTITUTION.md | Repo doc | AppShell modes/lifecycle | Inspected | GitHub connector | Yes | Rendered-mode conflict | FACT |
| ARTIFACT-08 | docs/architecture/GUI_BASELINE.md | Repo doc | Zero-asset GUI baseline | Inspected | GitHub connector | Yes | UI floor | FACT |
| ARTIFACT-09 | docs/audit/CODE_DATA_SEPARATION_REPORT.md | Repo doc | Code/data reality | Inspected | GitHub connector | Yes | Command drift evidence | FACT |
| ARTIFACT-10 | docs/audit/MODULARITY_EXTENSION_PROOF.md | Repo doc | Data extension proof | Inspected | GitHub connector | Yes | Modularity limits | FACT |
| ARTIFACT-11 | docs/release/PRODUCT_BOOT_PROOF.md | Repo doc | Product boot status | Inspected | GitHub connector | Yes | Proof limitations | FACT |
| ARTIFACT-12 | data/registries/product_registry.json | Repo data | Product capabilities/degrade ladders | Inspected | GitHub connector | Yes | Capability basis | FACT |
| ARTIFACT-13 | This human-readable report | Generated file/content | Preserve chat for human readers | Created now | Assistant | Yes | File 01 | FACT |
| ARTIFACT-14 | Spec sheet YAML | Generated file | Aggregation-friendly spec | Created now | Assistant | Yes | File 03 | FACT |
| ARTIFACT-15 | Aggregator packet | Generated file | Merge with other old-chat reports | Created now | Assistant | Yes | File 05 | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | One universal GUI framework | Rejected | Cannot cover host eras well | Tentative but strong | Reconsider only if project scope shrinks | WORKSTREAM-09 | INFERENCE |
| REJECTED-02 | One GUI per OS version | Rejected | Matrix explosion | Strong | Never unless generated/profiles only | WORKSTREAM-09 | INFERENCE |
| REJECTED-03 | Old UI Editor as final product | Superseded | Workbench/interface layer better | Strong | Could salvage pieces | WORKSTREAM-06 | FACT/INFERENCE |
| REJECTED-04 | Monolithic everything editor | Rejected | God app risk | Strong | No | WORKSTREAM-06 | INFERENCE |
| REJECTED-05 | Native-widget-first tooling | Deprioritized | Would not prove client/runtime UI | Tentative | Native wrappers later | WORKSTREAM-06 | INFERENCE |
| REJECTED-06 | .NET 2.0 old Windows GUI default | Rejected/deprioritized | Wrong dependency for setup/server | Medium | Only for historical compatibility experiments | WORKSTREAM-09 | INFERENCE |
| REJECTED-07 | Raw binaries as primary release artifact | Rejected | Weak verification/rollback | Strong | Raw binaries still inside bundles | WORKSTREAM-08 | FACT/INFERENCE |
| REJECTED-08 | Arbitrary plugins early | Deferred | Trust/determinism risk | Strong for early phase | After sandbox/trust law | WORKSTREAM-06 | INFERENCE |
| REJECTED-09 | Client as the whole game | Superseded | OS-like environment better | Strong | Client remains major shell | WORKSTREAM-03 | INFERENCE |
| REJECTED-10 | Workbench as entire UI platform | Superseded | Interface layer broader | Strong | Workbench remains proof host | WORKSTREAM-04 | INFERENCE |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Overstating implementation status | Future plans mistaken for current code | Medium | High | Use status labels and proof docs | ALL | FACT/INFERENCE |
| RISK-02 | Workbench becomes monolithic editor | Unmaintainable tool drift | Medium | High | Module descriptors + command service | WORKSTREAM-06 | INFERENCE |
| RISK-03 | GUI owns semantics | Product divergence | Medium | High | All UI through commands/services | WORKSTREAM-04 | FACT/INFERENCE |
| RISK-04 | Runtime depends on repo-only tools | Bad shipping architecture | Medium | High | Keep shipped modules under apps/runtime/contracts | WORKSTREAM-06 | FACT |
| RISK-05 | Rendered-mode law conflict ignored | Workbench violates AppShell doctrine | High | High | Update AppShell/product capability law | WORKSTREAM-04 | FACT |
| RISK-06 | Root sprawl returns | Repo convergence undone | Medium | High | Strict validators/exceptions | WORKSTREAM-01 | FACT |
| RISK-07 | Arbitrary plugin mutation breaks determinism | Unsafe modding | Medium | High | T0/T1 first; sandbox later | WORKSTREAM-06 | INFERENCE |
| RISK-08 | No-assets UI underpowered/slow | Poor UX | Medium | Medium | Retained UI, dirty regions, virtualization | WORKSTREAM-07 | INFERENCE |
| RISK-09 | Data-driven becomes runtime chaos | Unreliable behavior | Medium | High | Validation/codegen/typed contracts | WORKSTREAM-10 | INFERENCE |
| RISK-10 | Packaging support claims overrun proof | Release trust loss | Medium | High | Matrix/support tiers and verification | WORKSTREAM-08 | FACT/INFERENCE |
| RISK-11 | Other chat reports conflict | Spec book inconsistency | High | Medium | Aggregator conflict rules | WORKSTREAM-01 | UNCERTAIN |
| RISK-12 | Current repo facts stale | Wrong implementation plan | Medium | Medium | Re-verify before coding | ALL | UNVERIFIED |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current repo build/test status | Docs observed may be stale | Local CI/build logs | P0 | WORKSTREAM-02 | UNVERIFIED |
| VERIFY-02 | Current AppShell rendered-mode contract | Needed before Workbench | Repo docs/contracts | P0 | WORKSTREAM-04 | FACT/UNVERIFIED |
| VERIFY-03 | Current product registry capabilities | Needed for tools rendered mode | data/registries/product_registry.json | P0 | WORKSTREAM-04 | UNVERIFIED |
| VERIFY-04 | Whether docs.zip exists in another context | User referenced it earlier | Uploaded files/library | P1 | ALL | UNCERTAIN |
| VERIFY-05 | Current platform/toolchain support floors | Time-sensitive | Official docs | P1 | WORKSTREAM-09 | UNVERIFIED |
| VERIFY-06 | Current packaging/projection tooling status | Needed for release path | Repo tools/build artifacts | P1 | WORKSTREAM-08 | UNVERIFIED |
| VERIFY-07 | Which old UI Editor artifacts exist in other chats | Needed for salvage | Other chat reports/files | P2 | WORKSTREAM-06 | UNCERTAIN |
| VERIFY-08 | Whether CTest canonical discovery is fixed | Blocking proof spine | ctest --preset verify | P0 | WORKSTREAM-02 | UNVERIFIED |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | GUI/binary baseline | CLI/TUI/GUI thin-shell doctrine established | Started architecture baseline | Still relevant | High |
| 2 | Repo restructure | Ownership layout and domain split refined | Avoid root chaos | Current root authority | High |
| 3 | Shipping/versioning | Layered deterministic distribution model discussed | Release planning | Relevant to spec book | High |
| 4 | Platform lanes | Old/compat/modern lanes distinguished | Controls matrix scope | Deferred work | Medium |
| 5 | Current code audit | Repo code found partly modular but not fully data-driven | Reality check | Important caveat | High |
| 6 | OS-like reframing | Dominium treated as deterministic operating environment | Unifies ambition | Core doctrine candidate | Medium-high |
| 7 | Workbench direction | Old UI editor superseded by modular rendered tools host | Product strategy | Needs law/contracts | High |
| 8 | Interface layer | Workbench generalized into reusable Interface Operating Layer | Highest synthesis | Next doctrine task | Medium-high |
| 9 | Preservation task | User requested complete report/files/registers | Export/handoff | This package | High |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Architecture doctrine | Deterministic simulation operating environment model | DECISION-05, WORKSTREAM-03 | Requirement/context | Medium-high | Needs formal doctrine |
| Repo layout | Post-CONVERGE ownership roots and domain split | DECISION-03, DECISION-04 | Requirement | High | Already repo authority |
| AppShell/interface | CLI/TUI/rendered/headless projections over one command spine | DECISION-01, DECISION-07 | Requirement candidate | Medium-high | Needs law update |
| Workbench/tools | Modular Workbench host and modules | DECISION-06 | Requirement/context | Medium-high | Product naming pending |
| UI/UX | No-assets product-grade UI floor | DECISION-10 | Requirement | High | Existing GUI baseline supports |
| Release/distribution | Deterministic packages/bundles/manifests | DECISION-11 | Requirement/context | High | Verify current implementation |
| MVP | Boot-to-replay proof as MVP | DECISION-14 | Requirement candidate | Medium-high | Needs acceptance criteria |
| Modding | Capability/trust governed packs/modules | DECISION-13 | Requirement candidate | Medium | Needs more policy |
