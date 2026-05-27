# STRUCTURED REGISTERS

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Canonical repo structure | Stabilize roots and internal ownership taxonomy | Broad structure credible with warnings | No active old paths, validators green, targeted residuals only | Active / mostly complete | P0 | High | FACT |
| WORKSTREAM-02 | Domino framework boundary | Define framework as public surfaces/contracts/headers, not root | Reported commit added boundary docs/validator | Stable exported public surface model | Active | P0 | High | FACT |
| WORKSTREAM-03 | API/ABI governance | C-compatible public ABI over C17/C++17 internals | Doctrine established; validators partly reported | Public surfaces registered and tested | Active | P0 | Medium | FACT/INFERENCE |
| WORKSTREAM-04 | Provider architecture | Service-first provider model for raylib/SDL/Lua/etc. | Provider structure reported landed with warnings | Providers selected by profiles and conformance-tested | Active | P0 | High | FACT |
| WORKSTREAM-05 | Workbench/product spine | Build Workbench and product slices through command/view/evidence contracts | Validation slice reported landed; projection work pending | Workbench consumes shared command/view/document spine | Active | P1 | Medium | FACT |
| WORKSTREAM-06 | Full-gate proof | Remove stale full-gate failures and prove full suite | Targeted stale path subset fixed; full CTest not green | Full CTest/T4 green or all failures classified | Active | P0/P1 | High | FACT |
| WORKSTREAM-07 | Third-party provider fencing | Use raylib/SDL/Lua fast without contaminating contracts/game/engine | Doctrine established; implementation pending | Forbidden include + provider manifests + conformance tests | Active | P1 | High | FACT/INFERENCE |
| WORKSTREAM-08 | Chat preservation | Preserve this chat for future handoff/spec aggregation | This package generated | Aggregator-ready report and files | Active | P0 | High | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Keep closed top-level root set | Current | Repeated accepted doctrine | Prevent root sprawl | Future roots require contract update | WORKSTREAM-01 | High | FACT |
| DECISION-02 | No first-party `src/source` wrappers | Current | User explicitly objected | Avoid meaningless nesting | Ownership dirs are source roots | WORKSTREAM-01 | High | FACT |
| DECISION-03 | Domino/Dominium split | Current | Repeated synthesis accepted in discussion | Enables reuse | Public surfaces become Domino framework | WORKSTREAM-02 | High | FACT |
| DECISION-04 | No top-level `framework/` root | Current | User reported commit defining boundary | Avoid root competition | Framework lives in contracts/headers | WORKSTREAM-02 | High | FACT |
| DECISION-05 | C17+C++17 mainline with C-compatible ABI | Current | Discussion and user status text | Balance portability and implementation power | C++ internals, C ABI boundaries | WORKSTREAM-03 | Medium-High | FACT/VERIFY |
| DECISION-06 | Service-first provider directories | Current | Provider structure discussions and status report | Keeps third-party replaceable | `runtime/<service>/providers/<provider>` | WORKSTREAM-04 | High | FACT |
| DECISION-07 | Apps do not hardwire providers | Current | Repeated doctrine | Avoid product variant explosion | Profiles choose providers | WORKSTREAM-04 | High | FACT |
| DECISION-08 | Workbench not authority | Current | Repeated doctrine | Prevent GUI-specific truth | Workbench uses commands/views/evidence | WORKSTREAM-05 | High | FACT |
| DECISION-09 | Fast strict normal gate; full CTest full-gate debt | Current | Reported test-tier doctrine | Keeps dev loop usable | Full release proof remains separate | WORKSTREAM-06 | High | FACT |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Verify current repo state from fresh export | P0 | U0 | User/Codex | None | Fresh tracked export | Truthful status | Run report-integrity checks | WORKSTREAM-01 | FACT |
| TASK-02 | Repair stale generated evidence/markers if fast strict fails | P0 | U0/U1 | Codex/AIDE | Current validation logs | AuditX/identity/launcher failure logs | Fast strict green | Run targeted repair | WORKSTREAM-06 | FACT/UNCERTAIN |
| TASK-03 | Run full CTest audit | P1 | U1 | Codex/AIDE | Fast strict green | Full CTest output | Failure ledger | Classify/fix/defer failures | WORKSTREAM-06 | FACT |
| TASK-04 | Implement/validate projection conformance | P1 | U1 | Codex/AIDE | Presentation contracts | Command/result/view fixtures | Projection tests | Generate PROJECTION-CONFORMANCE prompt | WORKSTREAM-05 | FACT |
| TASK-05 | Define/finish presentation contracts | P1 | U1 | Codex/AIDE | Command/result/refusal contracts | View/action/projection schemas | Semantic presentation law | Run PRESENTATION-CONTRACT | WORKSTREAM-05 | FACT |
| TASK-06 | Provider wedge for raylib/SDL/Lua | P2 | U2 | Codex/AIDE | Provider structure green | Third-party source policy, manifests | Seed providers | Run provider wedge tasks | WORKSTREAM-04 | INFERENCE |
| TASK-07 | Pack internal layout canon | P2 | U2 | Codex/AIDE | Pack authority check | Pack tree + manifests | Canonical pack internals | Decide content/ vs data/ law | WORKSTREAM-01 | FACT |
| TASK-08 | Generate master spec book from old-chat reports | P2 | U2 | User/future assistant | This and other chat reports | Aggregator packets | Master spec | Use spec sheet/aggregator packet | WORKSTREAM-08 | FACT |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | No new top-level roots without contract | Repo structure | Hard | User and doctrine | Route concepts into existing roots | Root sprawl | High | FACT |
| CONSTRAINT-02 | No first-party src/source wrappers | Repo structure | Hard | User explicitly objected | Use ownership dirs directly | Redundant nesting | High | FACT |
| CONSTRAINT-03 | Third-party types must not cross stable boundaries | Architecture | Hard | Provider doctrine | Fence raylib/SDL/Lua/ImGui | Vendor lock-in | High | FACT |
| CONSTRAINT-04 | Public ABI is C-compatible | API/ABI | Hard | Doctrine | No C++ ABI/STL/exceptions across ABI | ABI breakage | High | FACT |
| CONSTRAINT-05 | Workbench must use commands/views/evidence | Product architecture | Hard | Doctrine | No private validator/tool bypass | Divergent behavior | High | FACT |
| CONSTRAINT-06 | Do not treat assistant suggestions as user decisions | Reporting | Hard | User prompt | Preserve tentative status | False history | High | FACT |
| CONSTRAINT-07 | Verify current facts that may have changed | Factuality | Hard | User/system preference | Search/live verify current repo/library claims | Stale answers | High | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, audit-ready answers | Communication | Explicit | High | State verdict and evidence | Loss of trust | FACT |
| PREF-02 | Mark uncertainty | Factuality | Explicit | High | Use FACT/INFERENCE/UNCERTAIN | Overclaiming | FACT |
| PREF-03 | Avoid endless planning without execution | Workflow | Explicit/inferred | High | Give actionable prompts/tasks | Frustration/stall | FACT |
| PREF-04 | Preserve rejected/superseded options | Handoff | Explicit | High | Include rejection register | Repeated mistakes | FACT |
| PREF-05 | Future-proof modular architecture | Technical | Explicit | High | Favor contracts/providers/profiles | Structural lock-in | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Is full CTest green now? | Release/full proof | Reports say not green/not run | Current live result | Run full CTest or audit shard | P0/P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-02 | Which provider implementation comes first? | Product progress | raylib/SDL/Lua doctrine established | Exact current queue | Check queue/current, priorities | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-03 | Lua 5.4 or 5.5? | Script ABI stability | Pin one version; script API separate | Chosen version | Decide based on compatibility/toolchain | P2 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-04 | Is pack-internal content/ canonical? | Pack compatibility | Mixed layouts discussed | Actual pack law | Inspect contracts/package | P1/P2 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-05 | Are AIDE cache/queue/reports canonical? | Source/generated boundary | State-like dirs discussed | Exact current classification | AIDE state classification task | P1 | WORKSTREAM-01 | UNCERTAIN |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | dominium_canonical_handoff.md/txt | Generated handoff | Earlier project handoff | Available in sandbox | This chat | Yes | Compare with this report | FACT |
| ARTIFACT-02 | dir_tree / dirfiles bundles | Uploaded reports | Structure assessment | Mixed reliability | User uploads | Yes with caveats | Verify integrity before use | FACT |
| ARTIFACT-03 | CANON_STRUCTURE_ACTUAL_FINAL_CLEANUP_01 prompt/report | Task/audit | Actual structure cleanup | Reported committed | Chat/user status | Yes | Key structural milestone | FACT |
| ARTIFACT-04 | FULL_GATE_LEGACY_TEST_ROUTE_01 | Task/audit | Route stale full-gate test paths | Reported committed | Chat/user status | Yes | Improves full-gate signal | FACT |
| ARTIFACT-05 | Domino framework boundary docs/validator | Docs/validator | Prevent framework root sprawl | Reported committed | Chat/user status | Yes | Important architecture decision | FACT |
| ARTIFACT-06 | This preservation package | Report package | Preserve chat for aggregation | Created now | Current response | Yes | Use as cross-chat input | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Top-level framework/ | Rejected | Competes with contracts/public headers | Mostly final | If multiple external framework packages require root and root contract changes | WORKSTREAM-02 | FACT |
| REJECTED-02 | Top-level modules/plugins/services/profiles/labs | Rejected | Reopens root sprawl | Mostly final | Explicit root contract change | WORKSTREAM-01 | FACT |
| REJECTED-03 | Vendor-shaped runtime/raylib tree | Rejected | Violates service-first provider model | Final for architecture | None except experiments | WORKSTREAM-04 | FACT |
| REJECTED-04 | Workbench as authority | Rejected | Would diverge from CLI/headless/CI | Final | None | WORKSTREAM-05 | FACT |
| REJECTED-05 | Pure C99 mainline | Rejected | Insufficient for large modular architecture | Current | If project scope radically shrinks | WORKSTREAM-03 | FACT |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Stale/mixed structure reports | Wrong cleanup decisions | Medium | High | Structure report integrity validator | WORKSTREAM-01 | FACT |
| RISK-02 | More broad cleanup churn | Delays product work | Medium | High | Targeted tasks only after structure credible | WORKSTREAM-01 | INFERENCE |
| RISK-03 | Third-party leakage | Vendor lock-in, broken saves/replays | Medium | High | Forbidden include/type validators | WORKSTREAM-04 | FACT |
| RISK-04 | Full CTest ignored too long | Release proof unreliable | Medium | High | Full-gate audit ledger | WORKSTREAM-06 | FACT |
| RISK-05 | Assistant treats suggestions as decisions | Bad handoff/spec | Medium | Medium | Preserve labels and evidence basis | WORKSTREAM-08 | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current live repo HEAD/status | User reports changed over time | Fresh git status/export | P0 | WORKSTREAM-01 | FACT |
| VERIFY-02 | Full CTest current result | Release readiness unknown | Run full CTest/T4 audit | P0/P1 | WORKSTREAM-06 | FACT |
| VERIFY-03 | Current fast strict blockers | Reports mention stale evidence/marker debt | Run fast strict/RepoX | P0 | WORKSTREAM-06 | FACT |
| VERIFY-04 | Raylib/SDL/Lua current versions/support | External facts can change | Official upstream docs/releases | P1/P2 | WORKSTREAM-04 | VERIFY |
| VERIFY-05 | Pack internal layout law | Avoid breaking packs | contracts/package + manifests | P1/P2 | WORKSTREAM-01 | FACT |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | Early layout critique | User rejected root sprawl and src/source wrappers | Set hard structural doctrine | Foundational | High |
| 2 | Canonical root model | Closed root set established | Stopped top-level churn | Still current | High |
| 3 | Distribution/install discussion | Source layout separated from runtime/package layouts | Prevented source/runtime confusion | Current | High |
| 4 | Move scripts/prompts | Generated many cleanup prompts | Drove actual repo changes | Historical and artifact value | High |
| 5 | Public API/ABI shift | Stable surfaces > stable folders | Future-proofing | Current | High |
| 6 | C17/C++17 baseline | Superseded C89/C++98 mainline | Implementation policy | Current but verify repo | Medium |
| 7 | Workbench/module model | Modules/workspaces/services/providers distinguished | Prevented module junk drawer | Current | High |
| 8 | Provider model | raylib/SDL/Lua as providers | Enabled acceleration without lock-in | Current | High |
| 9 | Framework boundary | Rejected top-level framework root | Prevented new root sprawl | Current | High |
| 10 | Preservation prompt | User requested maximum-fidelity package | Enables future handoff/spec book | Current | High |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Repo layout | Closed root model, no src/source, no root sprawl | DECISION-01, CONSTRAINT-01 | Requirement | High | Central contribution |
| Framework/API | Domino framework boundary, public surface model | DECISION-03, DECISION-04 | Requirement | High | Avoid framework root |
| Provider architecture | Service-first provider folders, profiles | DECISION-06, WORKSTREAM-04 | Requirement | High | Important for raylib/SDL/Lua |
| Presentation | Command/result/view/action/projection spine | WORKSTREAM-05 | Requirement/context | Medium-High | Needs implementation proof |
| Proof gates | Fast strict vs full CTest/T4 distinction | DECISION-09 | Requirement/context | High | Prevents dev-loop paralysis |
| Third-party policy | Fence provider types from stable surfaces | CONSTRAINT-03 | Requirement | High | Essential to modularity |
