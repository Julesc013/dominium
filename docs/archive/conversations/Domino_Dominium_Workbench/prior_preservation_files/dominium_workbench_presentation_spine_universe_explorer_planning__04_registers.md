# STRUCTURED REGISTERS — Dominium Workbench, Presentation Spine, and Universe Explorer Planning

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Foundation / engineering law | Keep project modular, portable, replaceable | Concept and queue discussed; current repo status unverified here | Enforced public surfaces, dependency directions, ABI, schemas, docs, capabilities, providers | Active | P0 | 4 | FACT/PROJECT-CONTEXT |
| WORKSTREAM-02 | Unified presentation spine | One command/result/refusal/document/view system across CLI/TUI/rendered/native/headless | Core doctrine accepted | Shared projections for all products | Active | P0 | 5 | FACT |
| WORKSTREAM-03 | Workbench Platform | Modular production environment for Domino/Dominium | Concept accepted; implementation not started in this chat | Cross-platform rendered/TUI/CLI production shell with modules | Active | P1 | 5 | FACT |
| WORKSTREAM-04 | UI/theme/renderer system | Modular layouts, controls, themes, draw-list renderer | Architecture discussed | Software-first renderer with packable themes/widgets/layouts | Active | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-05 | TUI projection | First-class terminal projection | Detailed doctrine discussed | Shared TUI widgets/views for server/setup/Workbench/client fallback | Active | P1 | 4 | FACT |
| WORKSTREAM-06 | Modules/packs/providers/apps model | Clarify extension vocabulary | Accepted conceptually | Descriptor-driven modules/packs/apps/providers with conformance tests | Active | P0 | 5 | FACT |
| WORKSTREAM-07 | Progressive self-hosting | Build Workbench safely | Accepted conceptually | Workbench edits safe artifacts, then itself, then products | Active | P1 | 5 | FACT |
| WORKSTREAM-08 | Universe Explorer | Lawful scale/materialization inspection | Proposed and refined | Workbench module proving reference frames, no modal loading, materialization | Future | P2 | 4 | FACT/INFERENCE |
| WORKSTREAM-09 | Robot seed-civilization systems | Game design and Workbench authoring modules | Concept explored | Runtime artifacts and Workbench labs for planet, terrain, machines, city systems | Future | P2 | 4 | FACT |
| WORKSTREAM-10 | AIDE/Codex workflow | Govern agentic development | Strong concept | Workbench Agent Board + AIDE work units + Codex patch execution | Future/active planning | P1 | 4 | FACT/INFERENCE |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Old UI Editor/Tool Editor are abandoned as final products and recycled into Workbench modules | Accepted | User explicitly said abandon/recycle | Avoid one-off Windows/native-widget path | Interface Studio replaces UI Editor | WS03/WS04 | 5 | FACT |
| DECISION-02 | Workbench is a production environment, not architectural authority | Accepted | Repeated discussion | Prevents GUI from owning semantics | Contracts/services/proof remain center | WS03 | 5 | FACT |
| DECISION-03 | All app modes should share one command/result/refusal/document/view spine | Accepted | User repeatedly asked unified CLI/TUI/rendered/native | Reuse and semantic parity | Affects all apps | WS02 | 5 | FACT |
| DECISION-04 | Rendered mode should be product-declared, not client-only | Accepted conceptually | User pasted/accepted correction | Enables Workbench rendered mode lawfully | Requires app/capability law | WS02/WS03 | 4 | FACT/PROJECT-CONTEXT |
| DECISION-05 | Software renderer baseline comes before hardware | Accepted conceptually | Repeated design conclusions | Portable, testable, CI-friendly | Renderer Sandbox/Theme Lab first | WS04 | 5 | FACT |
| DECISION-06 | OEM+ themes are rendered mimic profiles, not OS SDK widgets or copied assets | Accepted conceptually | User wanted themes; assistant boundary accepted | Modder-friendly while safer | Theme packs and Theme Lab | WS04 | 4 | FACT/INFERENCE |
| DECISION-07 | TUI is first-class projection | Accepted | User provided TUI doctrine; assistant agreed | Server/recovery/SSH/CI/agents | TUI runtime and projections | WS05 | 5 | FACT |
| DECISION-08 | Module/pack/provider/app/workspace/component vocabulary is adopted | Accepted conceptually | User pasted and asked; assistant agreed | Prevents taxonomy drift | Contracts/module/app/workbench | WS06 | 5 | FACT |
| DECISION-09 | Progressive self-hosting is required | Accepted | User pasted model and asked; assistant agreed | Avoid circular bootstrap | Workbench build staircase | WS07 | 5 | FACT |
| DECISION-10 | Universe Explorer should be lawful inspection/materialization proof | Accepted as recommendation | User asked and proceeded around it | Prevents renderer demo trap | Future world/client proof | WS08 | 4 | INFERENCE |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Verify current live repo gate/queue status | P0 | U0 | User/AIDE/Codex | repo access | latest docs/gates | verified current state | run AIDE/repo status checks | WS01 | VERIFY |
| TASK-02 | Execute or plan COMMAND-RESULT-VIEW-SLICE-01 | P0 | U1 | AIDE/Codex | foundation gate status | command/result/view schemas | minimal projection proof | draft Codex prompt | WS02 | FACT/INFERENCE |
| TASK-03 | Define minimal presentation/projection descriptor | P0 | U1 | Planning/AIDE | TASK-02 | view requirements | schema/contract | include in slice or next plan | WS02 | INFERENCE |
| TASK-04 | Build Validation Dashboard slice | P1 | U1 | Codex later | TASK-02 | validation command/result/evidence | CLI/TUI/rendered Workbench proof | after slice | WS03 | INFERENCE |
| TASK-05 | Define Workbench product/module law | P1 | U1 | AIDE/Codex | foundation | module/app/workspace contracts | Workbench descriptor law | no-apply plan | WS03/WS06 | FACT/INFERENCE |
| TASK-06 | Build Project Graph Explorer | P1 | U2 | Codex later | command/view/project graph service | graph data | architecture readability module | after Validation Dashboard | WS03/WS06 | INFERENCE |
| TASK-07 | Design Interface Studio artifact taxonomy | P1 | U2 | Planning | presentation contracts | UI/TUI/theme docs | authoring plan | after projection proof | WS04 | INFERENCE |
| TASK-08 | Design Universe Explorer 0 | P2 | U2 | Planning/Codex later | Workbench shell, views, packages, replay | universe model refs | inspection/materialization proof | after base product slices | WS08 | INFERENCE |
| TASK-09 | Define robot seed-civilization Workbench labs | P2 | U3 | Planning | runtime artifact schemas | game design | module roadmap | after field/world substrate | WS09 | INFERENCE |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Workbench must not be semantic authority | Architecture | Hard | Repeated decisions | Use commands/services/documents | GUI drift | 5 | FACT |
| CONSTRAINT-02 | CLI/TUI/rendered/native/headless share command/result/refusal spine | Architecture | Hard | Repeated decisions | No separate app logic per mode | Semantic fork | 5 | FACT |
| CONSTRAINT-03 | Native SDK GUIs are optional projections | Architecture | Hard/soft | User clarified Visual Studio/Xcode role | Native widgets don't define core behavior | OS lock-in | 4 | FACT |
| CONSTRAINT-04 | Code must be portable/modular/extensible/reusable | Engineering | Hard | User explicit | Stable contracts and boundaries | Engine reuse failure | 5 | FACT |
| CONSTRAINT-05 | Themes must not copy proprietary OS assets by default | Legal/design | Hard | Discussed boundary | Use generic mimic/tokens/assets | Legal risk | 4 | INFERENCE |
| CONSTRAINT-06 | Direct file/runtime mutation by GUI should be avoided | Safety | Hard | Document/patch model | Use patch/transaction/evidence | Unsafe edits | 5 | FACT/INFERENCE |
| CONSTRAINT-07 | Current repo facts require verification | Epistemic | Hard | Many pasted from other chats | Verify before implementation | Stale plan | 5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, rigorous, audit-ready answers | Communication | Explicit | Strong | Use labels, caveats, structure | Low trust | FACT |
| PREF-02 | Think broad and deep; preserve future-proofing | Planning | Explicit | Strong | Include architecture and edge cases | Underbuilt plan | FACT |
| PREF-03 | Prefer modular reusable systems over one-offs | Architecture | Explicit | Strong | Use contracts/services/modules | Rework | FACT |
| PREF-04 | Workbench should be usable by sole developer + agents | UX/process | Explicit | Strong | Agent Board and evidence loops | Tool misses purpose | FACT |
| PREF-05 | Code-only baseline with optional packs/assets | Technical | Inferred/explicit | Medium-high | Build primitive renderer/themes first | Asset dependency too early | INFERENCE |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | What is the verified current repo state? | Determines next task | Pasted context suggests latest queue changed | actual live state | AIDE/repo validation | P0 | WS01 | VERIFY |
| QUESTION-02 | Is COMMAND-RESULT-VIEW-SLICE-01 already active? | Avoid duplicate work | User pasted it as next | exact status | inspect task docs | P0 | WS02 | VERIFY |
| QUESTION-03 | What is the minimal view/projection schema? | Blocks presentation spine | Concept exists | concrete fields | design prompt | P0 | WS02 | OPEN |
| QUESTION-04 | When can Workbench be classified under apps? | Affects structure | apps/tools requires explicit classification | current policy | repo contract review | P1 | WS03 | OPEN |
| QUESTION-05 | How much native GUI integration is needed? | Work split | optional projection | product priorities | decide later | P2 | WS02 | OPEN |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | source.zip | uploaded zip | early repo/UI reference | uploaded | user | yes if available | Not deeply reprocessed in final package | FACT |
| ARTIFACT-02 | SetupC.zip | uploaded screenshot bundle | setup logical layout references | uploaded | user | yes | Used for layout reasoning | FACT |
| ARTIFACT-03 | LauncherC.zip | uploaded screenshot bundle | launcher logical layout references | uploaded | user | yes | Used for layout reasoning | FACT |
| ARTIFACT-04 | Workbench/theme/module screenshots | images | visual style and module references | uploaded | user | yes | Reference only | FACT |
| ARTIFACT-05 | Prompt 1–11 old UI Editor plan | in-chat prompts | obsolete detailed Codex plan | generated in chat | assistant | preserve as superseded | Useful historical | FACT |
| ARTIFACT-06 | UU1–UU6 prompt plan | in-chat prompts | CLI/import/ops/launcher/setup hardening | generated in chat | assistant | preserve as superseded/partial | Pre-pivot | FACT |
| ARTIFACT-07 | IDE live editing prompt | in-chat prompt | VS/Xcode/Linux preview-host idea | generated | assistant | preserve background | Superseded by Workbench focus | FACT |
| ARTIFACT-08 | Pasted markdown.md | uploaded text | preservation task instructions | uploaded | user | yes | Source for this package | FACT |
| ARTIFACT-09 | Pasted text.txt | uploaded text | Universe Explorer doctrine | uploaded | user | yes | Source for Universe Explorer discussion | FACT |
| ARTIFACT-10 | This preservation package | generated files | handoff/report/spec | generated now | assistant | yes | New output | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Windows-only UI Editor as final product | Superseded | Too narrow and one-off | Mostly final | As temporary tool only | WS11 | FACT |
| REJECTED-02 | Native-widget Tool Editor final product | Superseded | Doesn't prove client/rendered architecture | Mostly final | Native projection tools only | WS11 | FACT |
| REJECTED-03 | Workbench as monolithic all-in-one editor | Rejected | Would become God app | Final principle | No | WS03 | FACT |
| REJECTED-04 | Renderer/free-camera Universe Explorer without law | Rejected | Violates truth/materialization doctrine | Final principle | No | WS08 | FACT/INFERENCE |
| REJECTED-05 | Arbitrary native plugins early | Deferred | Trust/sandbox not ready | Temporary | After trust law/conformance | WS06 | FACT |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Workbench becomes authority | Semantic drift | Medium | High | Commands/services/documents only | WS03 | FACT/INFERENCE |
| RISK-02 | UI modes fork behavior | Duplicate bugs and inconsistent products | Medium | High | Projection contract and parity tests | WS02 | FACT |
| RISK-03 | Paths become identity | Refactors break system | Medium | High | Registries, IDs, manifests | WS01/WS06 | FACT |
| RISK-04 | Modules become junk drawer | Poor extensibility | Medium | High | Vocabulary and contracts | WS06 | FACT |
| RISK-05 | Universe Explorer becomes renderer demo | Violates world doctrine | Medium | High | Lawful inspection/materialization contract | WS08 | FACT/INFERENCE |
| RISK-06 | Repo-state assumptions stale | Wrong next task | High | Medium-high | Verify live repo | WS01 | VERIFY |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current repo gate and queue status | Determines next action | live repo/AIDE docs | P0 | WS01 | VERIFY |
| VERIFY-02 | Current directory layout authority | Prevents path mistakes | layout contracts | P0 | WS01 | VERIFY |
| VERIFY-03 | Existing command/result/view implementation state | Avoids duplicate work | code + docs | P0 | WS02 | VERIFY |
| VERIFY-04 | Existing Workbench/app classification | Determines apps/tools/workbench viability | contracts/component matrix | P1 | WS03 | VERIFY |
| VERIFY-05 | Renderer backend current implementation | Determines feasibility of rendered proof | runtime/render code | P1 | WS04 | VERIFY |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | UI Editor planning begins | Windows-first native/TLV UI editor explored | Solved launcher UI/flicker goal | Superseded but useful background | 5 |
| 2 | DUI/TLV details discussed | Existing Win32/DGFX/null backends identified | Grounded initial plan | Historical | 4 |
| 3 | Codex prompt plans generated | Detailed UI Editor/Tool Editor prompts | Provided implementation path | Superseded | 5 |
| 4 | Import/CLI/ops/Minecraft tests added | UI Editor became scriptable | Codex automation | Recycled into Workbench/Interface Studio | 5 |
| 5 | User pivots | Old editor plan abandoned/recycled | Major direction change | Central | 5 |
| 6 | Workbench Platform emerges | Cross-platform rendered modular tools environment | New product direction | Central | 5 |
| 7 | Unified presentation spine | CLI/TUI/rendered/native/headless projections | Reuse across apps | Central | 5 |
| 8 | UI/theme/renderer/TUI doctrines | Data-driven themes and projections specified | Enables rendered app reuse | Central | 4 |
| 9 | Engineering law queues | Foundation public surface/ABI/dependency/etc | Future-proofing | High | 4 |
| 10 | Self-hosting model | Workbench built progressively | Avoids circularity | Central | 5 |
| 11 | Universe Explorer | Lawful scale/materialization explorer | First world proof | Future | 4 |
| 12 | Robot seed-civilization modules | Workbench labs for game systems | Connects tools to game vision | Future | 4 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Workbench Platform | Definition, goals, modules, self-hosting | WS03, D01-D03 | Requirement/context | 5 | Core contribution |
| Presentation Architecture | CLI/TUI/rendered/native/headless projections | WS02 | Requirement | 5 | Very important |
| UI/Theme/Renderer | Themes, controls, draw-list renderer | WS04 | Requirement/context | 4 | Needs implementation specs |
| TUI | First-class TUI doctrine | WS05 | Requirement | 4 | Good for server/setup/CI |
| Module/Pack/App Model | Vocabulary and composition law | WS06 | Requirement | 5 | Cross-cutting |
| Engineering Governance | Foundation queues, API/ABI, replacement | WS01 | Requirement/context | 4 | Verify latest repo state |
| Universe Explorer | Lawful reference/materialization proof | WS08 | Future requirement | 4 | Needs later spec |
| Robot Seed-Civilization | Game systems and Workbench labs | WS09 | Context/future requirements | 4 | Needs separate game design spec |
