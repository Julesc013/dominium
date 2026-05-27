# Structured Registers — Dominium Full Conversation Companion

## Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Workbench Platform | Build a modular production environment over Dominium contracts/services. | Planned; validation/static/projection slices discussed. | Read-only then authoring Workbench that builds artifacts and products. | Active future | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | AIDE/Codex Process | Safely automate development. | Workflow prompts generated; some reported done. | Task branches, dev integration, checkpoint main promotion. | Active | P0 | 4 | FACT |
| WORKSTREAM-03 | Presentation Architecture | Unify CLI/TUI/rendered/native/headless. | `PRESENTATION-CONTRACT-01` reported complete. | Projection conformance and read-only shell. | Active | P0 | 4 | FACT stated in chat |
| WORKSTREAM-04 | Provider Strategy | Use third-party libraries as replaceable providers. | Doctrine established. | Provider manifests/fences/conformance and raylib wedge. | Planned | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-05 | Maintenance/Full-Gate Debt | Resolve targeted structural/test debt. | Six maintenance tasks selected; first prompt generated. | Full-gate debt reduced without broad cleanup. | Active | P0 | 4 | FACT |
| WORKSTREAM-06 | Universe Explorer | Prove read-only seamless universe inspection. | Conceptual north-star. | Headless proof then visual explorer. | Future | P1 | 3 | INFERENCE |
| WORKSTREAM-07 | UI/TUI/Theme System | Modular layouts, controls, themes, TUI/rendered profiles. | Conceptual architecture settled. | Theme Lab, Interface Studio, Renderer Sandbox. | Future | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-08 | Product Apps | Reuse same modules/packs/UI across client/server/launcher/setup. | Barebones/product-spine discussion. | Apps as thin compositions over shared services. | Active/future | P1 | 4 | FACT/INFERENCE |

## Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Supersede old UI Editor/Tool Editor as final products. | Accepted | User explicitly said abandon/recycle them. | Avoid one-off Windows-first editor architecture. | Recycle ideas into Workbench modules. | WORKSTREAM-01 | 5 | FACT |
| DECISION-02 | Workbench is not authority. | Accepted | Repeated in chat. | Prevent GUI/tools from bypassing contracts. | Workbench uses commands/services/documents/patches. | WORKSTREAM-01 | 5 | FACT |
| DECISION-03 | AIDE governs, Codex patches. | Accepted | Repeated in plans. | Enables parallel automation safely. | Create WorkUnits, checkpoints, evidence. | WORKSTREAM-02 | 5 | FACT |
| DECISION-04 | Development non-blocking, promotion evidence-blocked. | Accepted | User handoff/plan. | Speeds dev while protecting main. | dev/task branches vs main/checkpoints. | WORKSTREAM-02 | 5 | FACT |
| DECISION-05 | Presentation modes are projections. | Accepted | Repeated doctrine. | Prevent separate CLI/TUI/GUI implementations. | Projection contract/conformance required. | WORKSTREAM-03 | 5 | FACT |
| DECISION-06 | Use raylib/SDL/Lua as providers. | Accepted conceptually | User asked and accepted doctrine. | Fast progress without lock-in. | Provider manifests/fencing needed. | WORKSTREAM-04 | 4 | FACT/INFERENCE |
| DECISION-07 | Stop broad structure cleanup. | Accepted | User/current plans. | Avoid churn after structure is clean enough. | Run targeted maintenance tasks. | WORKSTREAM-05 | 4 | FACT |
| DECISION-08 | Workbench starts read-only. | Accepted conceptually | Assistant recommendation accepted in later plan. | Avoid unsafe self-hosting. | Workbench shell read-only before authoring. | WORKSTREAM-01 | 4 | INFERENCE |

## Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Verify live repo state. | P0 | U0 | Human/Codex | None | repo checkout | current queue/audits/status | inspect before next task | all | UNCERTAIN |
| TASK-02 | Run/review FULL-GATE-LEGACY-TEST-ROUTE-01. | P0 | U0 | Codex | Presentation complete | generated prompt | stale full-gate paths routed | generate next maintenance prompt | WORKSTREAM-05 | FACT |
| TASK-03 | Generate PACK-INTERNAL-LAYOUT-CANON-01. | P0 | U1 | Assistant/Codex | TASK-02 or live approval | status | prompt/report | execute if selected | WORKSTREAM-05 | FACT |
| TASK-04 | PROJECTION-CONFORMANCE-01. | P0 | U1 | Codex | presentation contract | schemas/fixtures | proof of projection parity | continue UI path | WORKSTREAM-03 | FACT |
| TASK-05 | WORKBENCH-SHELL-READONLY-01. | P1 | U2 | Codex | projection conformance | runtime/app context | read-only Workbench shell | validate usefulness | WORKSTREAM-01 | INFERENCE |
| TASK-06 | PROVIDER-MANIFEST-WEDGE-01. | P1 | U2 | Codex | AIDE/presentation path | provider doctrine | provider schemas/manifests | service/fence wedge | WORKSTREAM-04 | INFERENCE |
| TASK-07 | UNIVERSE-EXPLORER-CONTRACT-01. | P1 | U2 | Codex | Workbench/read-only/projection | explorer doctrine | contract-only explorer spec | headless proof | WORKSTREAM-06 | INFERENCE |

## Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Treat stale repo status as current. | Wrong next prompt. | Medium | High | Verify live repo. | all | FACT/INFERENCE |
| RISK-02 | Build Workbench UI too early. | Parallel UI system. | Medium | High | Complete projection conformance first. | WORKSTREAM-01 | INFERENCE |
| RISK-03 | Raylib types leak into contracts/engine/game. | Provider lock-in. | Medium | High | Forbidden include/type validators. | WORKSTREAM-04 | INFERENCE |
| RISK-04 | Full-gate debt hidden as pass. | False readiness. | Medium | High | Keep warning/T4 status explicit. | WORKSTREAM-05 | FACT/INFERENCE |
| RISK-05 | Assistant suggestions treated as decisions. | Spec corruption. | Medium | Medium | Use labels and decision evidence. | all | FACT |
| RISK-06 | Screenshots treated as specs. | Overfitted UI. | Medium | Medium | Treat as references/moodboards only. | WORKSTREAM-07 | INFERENCE |

## Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Live `.aide/queue/current.toml`. | Determines next prompt. | repo file | P0 | all | UNCERTAIN |
| VERIFY-02 | Execution status of maintenance prompts. | Avoid duplicate work. | git log/audits | P0 | WORKSTREAM-05 | UNCERTAIN |
| VERIFY-03 | C17/C++17 baseline. | Affects provider/build policy. | CMake/docs | P1 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-04 | Full CTest debt status. | Affects release readiness. | test reports | P1 | WORKSTREAM-05 | UNCERTAIN |
| VERIFY-05 | Existing prior preservation files completeness. | Affects aggregation. | file package | P2 | archival | UNCERTAIN |
