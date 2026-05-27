# STRUCTURED REGISTERS

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Workbench Platform | Build modular production environment over shared command/document/provider spine | Doctrine defined; implementation blocked/read-only next | Self-hosting production environment | Active planning | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | AIDE/Codex Workflow | Coordinate parallel task branches and evidence-gated promotion | Prompts generated; some reported complete | AIDE manages work units, checkpoints, repairs | Active | P0 | 4 | PROJECT-CONTEXT |
| WORKSTREAM-03 | Presentation/Projection Architecture | Unify CLI/TUI/rendered/native/headless projections | PRESENTATION-CONTRACT-01 reported complete | Projection conformance and read-only Workbench | Active | P0 | 4 | FACT/UNVERIFIED |
| WORKSTREAM-04 | Provider Strategy | Use raylib/SDL2/Lua as fenced providers | Doctrine agreed; implementation future | Service-first provider system with conformance | Planned | P1 | 4 | FACT |
| WORKSTREAM-05 | Structure/Full-Gate Maintenance | Clean full-gate legacy tests and warning debt | Structure reported clean enough with warnings | Targeted maintenance without broad cleanup | Active | P0 | 3 | PROJECT-CONTEXT |
| WORKSTREAM-06 | Universe Explorer | North-star read-only inspection product slice | Concept planned | Headless then visual lawful universe explorer | Planned | P1 | 3 | FACT/INFERENCE |
| WORKSTREAM-07 | UI/TUI/Theme Authoring | Make layouts, controls, themes, widgets modular | Doctrine defined | Workbench Interface Studio/Theme Lab/TUI Studio | Planned | P1 | 4 | FACT |
| WORKSTREAM-08 | Reusable Domino Engineering Law | Make code portable, modular, extensible | Doctrine developed | Engineering constitution enforced by validators | Active planning | P0 | 4 | FACT |


## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Abandon old UI Editor/Tool Editor as final products; recycle ideas into Workbench modules. | Accepted | Visible chat acceptance / repeated user confirmation | Avoid one-off Windows/native editor architecture. | Affects future prompts and architecture | Multiple | High | FACT |
| DECISION-02 | Dominium Workbench is a modular production environment, not authority. | Accepted | Visible chat acceptance / repeated user confirmation | Prevents GUI/tool drift; keeps contracts/commands/services central. | Affects future prompts and architecture | Multiple | High | FACT |
| DECISION-03 | CLI/TUI/rendered/native/headless are projections of one semantic spine. | Accepted | Visible chat acceptance / repeated user confirmation | Enables reuse across apps, tests, Workbench, AIDE, and products. | Affects future prompts and architecture | Multiple | High | FACT |
| DECISION-04 | Use progressive self-hosting. | Accepted | Visible chat acceptance / repeated user confirmation | Avoids circular bootstrap. | Affects future prompts and architecture | Multiple | High | FACT |
| DECISION-05 | Use service/provider/profile vocabulary and strict module/pack/app terms. | Accepted | Visible chat acceptance / repeated user confirmation | Prevents taxonomy collapse. | Affects future prompts and architecture | Multiple | High | FACT |
| DECISION-06 | Use AIDE as governor/ledger/scheduler and Codex as bounded patch executor. | Accepted | Visible chat acceptance / repeated user confirmation | Enables parallel dev without corrupting main. | Affects future prompts and architecture | Multiple | High | FACT |
| DECISION-07 | Use raylib/SDL2/Lua as providers, not architecture. | Accepted conceptually | Visible chat acceptance / repeated user confirmation | Accelerates visible progress without lock-in. | Affects future prompts and architecture | Multiple | Medium-High | FACT/UNVERIFIED for implementation |
| DECISION-08 | Stop broad structure cleanup once canonical structure passes; use targeted maintenance lanes. | Accepted conceptually | Visible chat acceptance / repeated user confirmation | Avoids churn after structure became credible. | Affects future prompts and architecture | Multiple | Medium-High | FACT/PROJECT-CONTEXT |
| DECISION-09 | Universe Explorer is a read-only/headless proof before visual/gameplay. | Accepted conceptually | Visible chat acceptance / repeated user confirmation | Proves scale/refinement/reference frames without broad gameplay. | Affects future prompts and architecture | Multiple | Medium | FACT |
| DECISION-10 | Full CTest remains full-gate/T4 debt, not normal prompt gate. | Accepted from pasted status | Visible chat acceptance / repeated user confirmation | Keeps dev loop practical. | Affects future prompts and architecture | Multiple | Medium | PROJECT-CONTEXT/UNVERIFIED |


## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Generate/run FULL-GATE-LEGACY-TEST-ROUTE-01 | P0 | U0 | Codex/AIDE | PRESENTATION-CONTRACT-01 reported complete | repo full-gate config | Audit and route stale retired-root tests | Prompt generated; execute if not run | WORKSTREAM-05 | FACT |
| TASK-02 | Generate PACK-INTERNAL-LAYOUT-CANON-01 | P0 | U1 | Codex/AIDE | Maintenance lane order | pack layout evidence | Define/route pack-internal content layout | Generate next prompt | WORKSTREAM-05 | FACT |
| TASK-03 | Generate RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01 | P1 | U1 | Codex/AIDE | Maintenance lane | runtime/engine taxonomy audit | Classify residual session/serialization/foundation paths | Generate prompt | WORKSTREAM-05 | FACT |
| TASK-04 | Generate PUBLIC-HEADER-ABI-PROMOTION-01 | P1 | U1 | Codex/AIDE | Maintenance lane | public header warnings | Burn down ABI promotion warning debt | Generate prompt | WORKSTREAM-08 | FACT |
| TASK-05 | Generate STORAGE-PACKAGE-PROVIDER-SPLIT-01 | P1 | U1 | Codex/AIDE | Maintenance lane | storage/package provider warnings | Clarify provider split | Generate prompt | WORKSTREAM-04 | FACT |
| TASK-06 | Generate POINTER-WIDTH-SERIALIZATION-AUDIT-01 | P1 | U1 | Codex/AIDE | Maintenance lane | serialization formats | Audit pointer/width hazards | Generate prompt | WORKSTREAM-08 | FACT |
| TASK-07 | Run PROJECTION-CONFORMANCE-01 | P0 | U1 | Codex/AIDE | Presentation contract | view/projection fixtures | Prove CLI/TUI/rendered/native/headless conformance | After maintenance/replan | WORKSTREAM-03 | FACT |
| TASK-08 | Run WORKBENCH-SHELL-READONLY-01 | P1 | U2 | Codex/AIDE | Projection conformance | Workbench read-only specs | Read-only shell over commands/evidence | Future | WORKSTREAM-01 | FACT |
| TASK-09 | Define PROVIDER-MANIFEST-WEDGE-01 | P1 | U2 | Codex/AIDE | AIDE/presentation stability | provider doctrine | Provider manifest law before raylib | Future | WORKSTREAM-04 | FACT |
| TASK-10 | Verify live repo state before acting | P0 | U0 | Future assistant | Any operational task | live repo access | Avoid stale queue/task assumptions | Do first in future chat | WORKSTREAM-02 | FACT |


## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | UI is not authority | Architecture | Hard | Repeated accepted doctrine | All UI actions must route through commands/services | High | High | FACT |
| CONSTRAINT-02 | Worktree/queue status must be verified live | Process | Hard | Status changed often in chat | Future prompts must inspect repo before acting | High | High | FACT |
| CONSTRAINT-03 | No broad Workbench/renderer/gameplay while blocked | Scope | Hard | Pasted queue/Foundation states | Keep tasks narrow | High | Medium | PROJECT-CONTEXT |
| CONSTRAINT-04 | Third-party types fenced | Engineering | Hard | Provider strategy decisions | No raylib/SDL/Lua types in contracts/game/engine truth | High | High | FACT |
| CONSTRAINT-05 | Full CTest not normal prompt gate | Testing | Soft/Policy | Repeated status reports | Use targeted/fast strict for tasks; full gate for release | Medium | Medium | PROJECT-CONTEXT |
| CONSTRAINT-06 | No new top-level roots unless authorized | Repo | Hard | Root doctrine | Use existing canonical roots | High | High | FACT |
| CONSTRAINT-07 | Promotions evidence-blocked | Process | Hard | AIDE doctrine | Main/checkpoints require proof | High | High | FACT |


## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Direct source-grounded audit-ready answers | Communication | Explicit | High | Use FACT/INFERENCE/UNCERTAIN and cite when needed | User distrusts unsupported claims | FACT |
| PREF-02 | Copy-paste prompts in one code block | Prompting | Explicit | High | Generate complete Codex prompts | Hard to use split prompts | FACT |
| PREF-03 | Do not restart settled doctrine | Continuity | Explicit/Inferred | High | Continue from queue/state | Wastes time/repeats old plans | FACT |
| PREF-04 | Preserve rejected and superseded options | Memory | Explicit | High | Keep old UI Editor plan marked superseded | Future assistant may revive it | FACT |
| PREF-05 | Prefer narrow gated slices over broad implementation | Execution | Inferred | High | Use bounded tasks | Architecture drift | INFERENCE |
| PREF-06 | Human-readable explanation first | Preservation | Explicit | High | Reports should be readable, not just machine packets | Aggregation loses context | FACT |


## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | What is the current live repo queue after this chat? | Needed before any prompt execution | Last visible state says FULL-GATE prompt generated after presentation contract | Whether maintenance prompts ran | Inspect repo queue/audits | P0 | WORKSTREAM-02 | UNVERIFIED |
| QUESTION-02 | Is C17/C++17 fully implemented in build files? | Affects provider and code policy | Pasted status says yes | Need live verification | Inspect CMake/toolchain docs | P1 | WORKSTREAM-08 | UNVERIFIED |
| QUESTION-03 | Which Lua version should be pinned? | Script provider future | Lua as provider agreed | lua54 vs lua55 | Decide before script provider wedge | P2 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-04 | Should external dir use upstream or vendor? | Third-party source policy | external/upstream suggested | Repo convention may differ | Check repo policy | P2 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-05 | When is Universe Explorer authorized? | North-star product slice | Contract/headless sequence proposed | Exact gate after Workbench/presentation? | Replan after projection conformance | P1 | WORKSTREAM-06 | UNCERTAIN |


## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Old UI Editor 11-prompt plan | Prompt plan | Original implementation strategy | Superseded as final product | This chat | Carry as historical/context | Useful ideas recycled | FACT |
| ARTIFACT-02 | UU1–UU6 UI Editor extension prompts | Prompts | Import/CLI/ops/launcher/setup/hardening plan | Superseded as final product | This chat | Carry selectively | Concepts reused in Workbench modules | FACT |
| ARTIFACT-03 | Workbench/AIDE task prompts | Prompts | Operational Codex/AIDE tasks | Active/some generated | This chat | Yes | STATUS/AIDE/FULL-GATE prompts important | FACT |
| ARTIFACT-04 | FULL-GATE-LEGACY-TEST-ROUTE-01 prompt | Prompt | Targeted full-gate cleanup | Latest generated prompt | This chat | Yes | Immediate next if not run | FACT |
| ARTIFACT-05 | Uploaded preservation instruction file | Uploaded text | Spec for this preservation task | Used now | User upload | Yes | Cited in final response | FACT |
| ARTIFACT-06 | This preservation package | Markdown/YAML/ZIP | Chat preservation and handoff | Created now | Assistant output | Yes | Primary artifact | FACT |
| ARTIFACT-07 | Theme/TUI/OEM+ design guidance | Conceptual artifact | Future UI/UX requirements | Context/planning | This chat | Yes | Feeds spec book | FACT |
| ARTIFACT-08 | Provider strategy doctrine | Conceptual artifact | Raylib/SDL2/Lua provider model | Active doctrine | This chat | Yes | Needs formal provider manifest tasks | FACT |


## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Windows-only UI Editor as final product | Superseded | Not broad/cross-platform/reusable enough | Final for product direction | Temporary bridge only | WORKSTREAM-01 | FACT |
| REJECTED-02 | Native-widget-first Tool Editor | Superseded | Would duplicate OS SDK tools and not prove rendered client architecture | Final for core Workbench | Native GUI projections remain | WORKSTREAM-03 | FACT |
| REJECTED-03 | Monolithic everything editor | Rejected | Too brittle; modules/services better | Final | None likely | WORKSTREAM-01 | FACT |
| REJECTED-04 | Raylib-shaped architecture | Rejected | Would leak vendor identity into services/apps | Final | Experiments/proofs only | WORKSTREAM-04 | FACT |
| REJECTED-05 | Broad structure cleanup after gate passes | Deprioritised | Churn risk; targeted maintenance better | Tentative depending validators | If validator blocks | WORKSTREAM-05 | FACT |


## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats stale repo status as current | Wrong prompt/task order | High | High | Verify live repo before action | WORKSTREAM-02 | FACT |
| RISK-02 | Workbench becomes authority | Semantic drift and GUI-only behavior | Medium | High | Commands/documents/patches/evidence only | WORKSTREAM-01 | FACT |
| RISK-03 | Third-party type leakage | Provider lock-in and ABI/data contamination | Medium | High | Forbidden include/type validators | WORKSTREAM-04 | FACT |
| RISK-04 | Broad implementation before gates | Refactor spiral / false claims | Medium | High | Keep Foundation/queue blockers visible | WORKSTREAM-02 | FACT |
| RISK-05 | Full CTest debt ignored or overtreated | False readiness or stalled dev | Medium | Medium | Classify full-gate debt separately | WORKSTREAM-05 | FACT |
| RISK-06 | Projection systems drift apart | Duplicate CLI/TUI/GUI logic | Medium | High | Projection conformance tests | WORKSTREAM-03 | FACT |


## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Live repo queue/current state | Status changes frequently | Repository files | P0 | WORKSTREAM-02 | UNVERIFIED |
| VERIFY-02 | Whether latest generated maintenance prompts have run | Need next task | AIDE audits/commits | P0 | WORKSTREAM-05 | UNVERIFIED |
| VERIFY-03 | C17/C++17 build baseline | Affects code policy | CMake/build docs | P1 | WORKSTREAM-08 | UNVERIFIED |
| VERIFY-04 | Full CTest current blockers | Prior reports stale quickly | Full-gate audit/CTest | P1 | WORKSTREAM-05 | UNVERIFIED |
| VERIFY-05 | Provider/task queue after AIDE ledger | May have advanced | AIDE queue/audits | P1 | WORKSTREAM-04 | UNVERIFIED |


## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | Launcher UI / flicker problem | Started UI Editor requirements | Immediate product pain | Historical; superseded | High |
| 2 | Phase A UI Editor / Phase B Tool Editor | Generated large implementation prompt plan | Created early detailed strategy | Superseded; ideas recycled | High |
| 3 | Import/CLI/ops/Minecraft layout tests | Extended UI Editor plan | Showed need for automation | Recycled into Workbench/CLI concepts | High |
| 4 | Abandon UI Editor/Tool Editor final path | Shift to rendered Workbench | Major direction change | Core current doctrine | High |
| 5 | Workbench Platform doctrine | Defined integrated modular production environment | Reframed project tools | Central | High |
| 6 | TUI/theme/OEM+/UI modularity | Defined projection and theme systems | Future UI spec basis | Important | High |
| 7 | Engineering constitution discussion | Defined reusable/portable architecture practices | Future-proofing | Important | High |
| 8 | AIDE/Codex queue prompts | Generated status/AIDE workflow prompts | Operational planning | Current/near-term | High |
| 9 | Provider/raylib/SDL/Lua doctrine | Defined providers as replaceable | Future visible progress | Important | High |
| 10 | Presentation contract and maintenance tasks | User reported PRESENTATION-CONTRACT-01 complete; generated FULL-GATE prompt | Current endpoint | Immediate continuation | High |


## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Workbench Platform | Production environment, modules, self-hosting ladder | WORKSTREAM-01,DECISION-02 | Requirement + context | High | Should formalize after projection contracts |
| AIDE/Codex Workflow | Dev/main/checkpoint/non-blocking/evidence-blocked doctrine | WORKSTREAM-02,DECISION-06 | Requirement | High | Verify latest implementation |
| Presentation Architecture | Unified CLI/TUI/rendered/native/headless projections | WORKSTREAM-03,DECISION-03 | Requirement | High | Presentation contract completed per user report |
| Provider Architecture | Raylib/SDL/Lua provider model | WORKSTREAM-04,DECISION-07 | Requirement + open issue | Medium | Implementation future |
| Engineering Constitution | Contract/service/provider/module/pack/app vocabulary | WORKSTREAM-08,DECISION-05 | Requirement | High | Could become formal doctrine |
| Universe Explorer | Read-only/headless north-star product slice | WORKSTREAM-06,DECISION-09 | Open issue/context | Medium | Future gated slice |
