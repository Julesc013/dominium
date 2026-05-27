# STRUCTURED REGISTERS — Dominium Universe Explorer Planning and Repo Handoff

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Chat preservation | Preserve this chat for future reading and aggregation | Current task | Complete package and ZIP | Active | P0 | High | FACT |
| WORKSTREAM-02 | Doctrine recovery | Preserve/align old Dominium concepts with repo doctrine | Repo has doctrine matrix and Λ spine | No lost concepts, clear gaps | Active/ongoing | P1 | High | FACT/PROJECT-CONTEXT |
| WORKSTREAM-03 | Repo structure stabilization | Stop broad cleanup, keep targeted cleanup | Structure PASS_WITH_WARNINGS | Stable targeted cleanup only | Active | P1 | High | PROJECT-CONTEXT |
| WORKSTREAM-04 | Presentation/projection contracts | Define read-only presentation/projection law | Queue says next task | Contracted projection surfaces | Pending | P0 | High | PROJECT-CONTEXT |
| WORKSTREAM-05 | Workbench read-only shell | Provide governed shell for typed results/evidence | Narrow slices allowed | Read-only shell ready | Pending | P1 | Medium | INFERENCE |
| WORKSTREAM-06 | Universe Explorer | Prove seamless 1:1-scale inspection/materialization | User-proposed objective | Headless then visual/interacting explorer | Proposed | P0 | Medium-high | FACT/INFERENCE |
| WORKSTREAM-07 | No-modal-loading / streaming | Prove no stalls, budgeted derived work, degradation | Docs exist | Explorer proof passes | Proposed | P1 | Medium | PROJECT-CONTEXT |
| WORKSTREAM-08 | Reference frames / spacetime | Prove 1:1-scale coordinate/frame switching | Docs exist | Stable frame-switch proof | Proposed | P1 | Medium | PROJECT-CONTEXT |
| WORKSTREAM-09 | Materialization/refinement | Prove sparse materialization without fake detail | Docs exist | Explicit requests/provenance/refusal | Proposed | P1 | Medium | PROJECT-CONTEXT |
| WORKSTREAM-10 | Deep primitives and failure ontology | Consolidate remaining conceptual gaps | Partially preserved | Master planning specs | Open | P2 | Medium | INFERENCE |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | This chat is planning/exploration, not implementation | Accepted | User said so explicitly | Prevent drift into coding | All outputs should stay planning-level | WORKSTREAM-01 | High | FACT |
| DECISION-02 | Repo truth outranks chat memory | Established | AGENTS/authority model read in chat | Avoid stale reconstruction | Future work must verify repo | WORKSTREAM-02 | High | FACT/PROJECT-CONTEXT |
| DECISION-03 | Do not rewrite master doctrine from scratch | Recommended | Repo has Λ spine | Avoid competing canon | Use reconciliation/gap specs | WORKSTREAM-02 | Medium-high | INFERENCE |
| DECISION-04 | First major objective should be Universe Explorer | User-proposed | User stated it | Gives first product target | Drives explorer workstream | WORKSTREAM-06 | Medium-high | FACT |
| DECISION-05 | Explorer must be governed inspection/projection, not free-camera renderer | Recommended | No-modal/render/workbench doctrines | Prevent truth-authority leaks | Contract/headless first | WORKSTREAM-06 | Medium | INFERENCE |
| DECISION-06 | Stop broad structure cleanup | Recommended | Structure audit pass with warnings | Avoid churn | Targeted cleanup only | WORKSTREAM-03 | Medium | INFERENCE |
| DECISION-07 | Presentation/projection before Workbench UI/explorer | Strongly supported | Queue/Foundation Lock | Required by current gates | Start with PRESENTATION-CONTRACT-01 | WORKSTREAM-04 | High | PROJECT-CONTEXT |
| DECISION-08 | Headless explorer before visual explorer | Recommended | Renderer blocked; narrow slices allowed | Prove law before visuals | Null/headless proof first | WORKSTREAM-06 | Medium | INFERENCE |
| DECISION-09 | Embodiment after explorer proof | Recommended | User sequence and doctrine | Avoid observer/entity confusion | Embodiment later | WORKSTREAM-06 | Medium-high | INFERENCE |
| DECISION-10 | Create export files and ZIP for this chat | Accepted | User requested file export if possible | Preserve chat | Files generated | WORKSTREAM-01 | High | FACT |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Generate preservation package | P0 | U0 | Assistant | Current chat context | Visible chat + uploaded prompt | Report + files + ZIP | Complete now | WORKSTREAM-01 | FACT |
| TASK-02 | Run/author PRESENTATION-CONTRACT-01 | P0 | U1 | Future repo agent/human | Current queue | Presentation docs, contracts | Presentation contract | Draft prompt/spec | WORKSTREAM-04 | PROJECT-CONTEXT |
| TASK-03 | Run PROJECTION-CONFORMANCE-01 | P0 | U1 | Future repo agent/human | TASK-02 or queue decision | Projection docs/validators | Conformance contract/proof | Draft | WORKSTREAM-04 | PROJECT-CONTEXT |
| TASK-04 | Workbench shell read-only | P1 | U1 | Future repo agent | TASK-02/03 | Workbench docs | Read-only shell | Define narrow scope | WORKSTREAM-05 | INFERENCE |
| TASK-05 | Universe Explorer contract | P0 | U1 | Future planning chat/repo agent | TASK-02/03 | Universe/refinement/frame/no-loading docs | Contract spec | Draft `UNIVERSE-EXPLORER-CONTRACT-01` | WORKSTREAM-06 | INFERENCE |
| TASK-06 | Headless Universe Explorer proof | P0 | U1 | Future repo agent | TASK-05 | Contracts + headless projection | Headless proof | Design acceptance tests | WORKSTREAM-06 | INFERENCE |
| TASK-07 | No-modal-loading proof | P1 | U2 | Future repo agent | TASK-06 | Loading/streaming specs | Stall-free proof | Define harness | WORKSTREAM-07 | INFERENCE |
| TASK-08 | Reference-frame proof | P1 | U2 | Future repo agent | TASK-06 | Spacetime/frame docs | Stable frame switching | Define proof cases | WORKSTREAM-08 | INFERENCE |
| TASK-09 | Materialization request proof | P1 | U2 | Future repo agent | TASK-06 | Refinement docs | Explicit materialization lifecycle | Define proof cases | WORKSTREAM-09 | INFERENCE |
| TASK-10 | Visual Universe Explorer proof | P1 | U2 | Future repo agent | Headless + renderer authorization | Render docs/provider model | Minimal visual proof | Wait for gates | WORKSTREAM-06 | INFERENCE |
| TASK-11 | Interactive explorer | P1 | U2 | Future repo agent | Visual proof | UI contracts | Interactive inspection | Later | WORKSTREAM-06 | INFERENCE |
| TASK-12 | Embodiment anchor | P2 | U3 | Future repo agent | Explorer/refinement proof | Embodiment/visitability docs | First embodied entry | Later | WORKSTREAM-06 | INFERENCE |
| TASK-13 | Full-gate legacy test route | P1 | U1 | Future repo agent | Structure audit | Full CTest failures | Updated/retired stale tests | Targeted cleanup | WORKSTREAM-03 | PROJECT-CONTEXT |
| TASK-14 | Pack internal layout canon | P2 | U2 | Future repo agent/human | Pack warning | Pack docs/content | Pack layout decision | Targeted review | WORKSTREAM-03 | PROJECT-CONTEXT |
| TASK-15 | Runtime/engine residual taxonomy | P2 | U2 | Future repo agent | Residual warnings | structure audit | classification | Targeted review | WORKSTREAM-03 | PROJECT-CONTEXT |
| TASK-16 | Deep primitives spec | P2 | U3 | Future planning chat | Doctrine matrix | Old chat content + repo docs | Planning spec | Draft if requested | WORKSTREAM-10 | INFERENCE |
| TASK-17 | Failure ontology spec | P2 | U3 | Future planning chat | Domain template | Old chat content + repo docs | Planning spec | Draft if requested | WORKSTREAM-10 | INFERENCE |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Planning-only chat | Scope | Hard | User statement | No implementation claims | Drift into coding | High | FACT |
| CONSTRAINT-02 | Repo canon outranks chat | Authority | Hard | Repo doctrine read in chat | Verify before acting | Stale chat overrides repo | High | PROJECT-CONTEXT |
| CONSTRAINT-03 | Broad feature work blocked | Repo gate | Hard until changed | Foundation Lock / queue | Narrow slices only | Unauthorized scope | High | PROJECT-CONTEXT |
| CONSTRAINT-04 | Workbench is projection, not authority | Architecture | Hard | Workbench docs | No private mutation | UI authority leak | Medium-high | PROJECT-CONTEXT |
| CONSTRAINT-05 | Renderer is presentation-only | Architecture | Hard | Renderer docs | No truth mutation | Renderer-driven sim | Medium-high | PROJECT-CONTEXT |
| CONSTRAINT-06 | No modal loading | UX/runtime | Hard target | No-modal docs | Degrade instead of stall | Loading screens/freezes | Medium-high | PROJECT-CONTEXT |
| CONSTRAINT-07 | Interest/fidelity not camera-only | Simulation | Hard | Interest/fidelity docs | Camera may request, not create truth | Fake materialization | Medium | PROJECT-CONTEXT |
| CONSTRAINT-08 | Explicit materialization/refinement | Simulation | Hard | Refinement docs | Requests need budget/seed/provenance | Fake detail | Medium | PROJECT-CONTEXT |
| CONSTRAINT-09 | Assistant suggestions ≠ user decisions | Epistemic | Hard | User preservation prompt | Preserve tentative status | False history | High | FACT |
| CONSTRAINT-10 | External repo facts can stale | Verification | Hard | Temporal logic | Re-check before implementation | Acting on stale queue | High | INFERENCE |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, source-grounded answers | Communication | Explicit from profile/context | Strong | Cite and label uncertainty | Loss of trust | FACT/PROJECT-CONTEXT |
| PREF-02 | Planning before implementation in this chat | Scope | Explicit | Strong | No coding focus | Wrong mode | FACT |
| PREF-03 | Human-readable explanation first | Preservation | Explicit uploaded prompt | Strong | Narrative before registers | Unusable package | FACT |
| PREF-04 | Maximum-fidelity preservation | Preservation | Explicit | Strong | Do not overcompress | Lost context | FACT |
| PREF-05 | Distinguish FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT | Epistemic | Explicit | Strong | Use labels | False certainty | FACT |
| PREF-06 | Create downloadable files if possible | Artifacts | Explicit | Strong | Export package | Missing deliverable | FACT |
| PREF-07 | Avoid re-asking answered questions | Workflow | Explicit | Strong | Proceed with assumptions | Frustration | FACT |
| PREF-08 | Audit-ready plans | Planning | Inferred/profile | Strong | Registers/tasks/risks | Poor continuity | INFERENCE |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Has queue changed after 2026-05-23? | Next task may differ | Queue read showed Presentation next | Latest repo state | Re-fetch `.aide/queue/current.toml` | P0 | WORKSTREAM-04 | VERIFY |
| QUESTION-02 | Should Universe Explorer contract be next after presentation? | Determines next planning artifact | User proposed explorer | Whether user formally accepts sequence | Ask/confirm or draft as proposal | P0 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-03 | Has full CTest been fixed? | Release/proof readiness | It was blocked in audit | Current status | Run/check latest CI | P1 | WORKSTREAM-03 | VERIFY |
| QUESTION-04 | Should Deep Primitives become a formal spec? | Preserves old chat content | Gap identified | User priority | Draft planning spec | P2 | WORKSTREAM-10 | UNCERTAIN |
| QUESTION-05 | Should Failure Ontology become a formal spec? | Domain reliability | Gap identified | User priority | Draft planning spec | P2 | WORKSTREAM-10 | UNCERTAIN |
| QUESTION-06 | How to merge with Dominium One/Two reports? | Future spec book | This is current-chat only | Other reports | Aggregator comparison | P1 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-07 | Which assistant recommendations are user-approved? | Prevent false decisions | Some recs made | User acceptance | User marks accepted decisions | P1 | all | UNCERTAIN |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | `Pasted text.txt` | Uploaded prompt | Defines preservation task | Used | User upload | Yes | Must cite in response | FACT |
| ARTIFACT-02 | Prior pasted Dominium architecture text | In-chat content | Recover old doctrine | Preserved in report | User pasted | Yes | Not independently original transcript | FACT |
| ARTIFACT-03 | Repo docs read through GitHub | External docs in chat | Ground plan in live repo | Used | GitHub connector | Yes | Staleness risk | PROJECT-CONTEXT |
| ARTIFACT-04 | Assistant recap/live repo audit | Chat output | Summarized repo/doctrine | Preserve | This chat | Yes | Assistant conclusions need labels | FACT |
| ARTIFACT-05 | Universe Explorer requirements answer | Chat output | Framed first objective | Preserve | This chat | Yes | Key contribution | FACT |
| ARTIFACT-06 | Best plan forward answer | Chat output | Proposed task sequence | Preserve | This chat | Yes | Recommendations not all accepted | FACT |
| ARTIFACT-07 | Current preservation package files | Generated files | Handoff/export | Created now | This task | Yes | ZIP included | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Atom-by-atom simulation | Rejected/deprioritised | Not tractable as game substrate | Likely final | Research/limited domains | WORKSTREAM-10 | INFERENCE |
| REJECTED-02 | Hardcoded object taxonomy as primitive | Rejected | Blocks arbitrary invention | Likely final | For specific UX conveniences only | WORKSTREAM-10 | INFERENCE |
| REJECTED-03 | Graphics LOD as scale doctrine | Superseded | Representation ladders are stronger | Final | Only renderer layer | WORKSTREAM-06 | FACT/PROJECT-CONTEXT |
| REJECTED-04 | Recipe-only crafting | Rejected | Too shallow for formalization/civilization | Likely final | Recipes as derived formalizations | WORKSTREAM-10 | INFERENCE |
| REJECTED-05 | Clean-room master doctrine replacement | Deprioritised | Repo already has Λ spine | Tentative | If repo canon is superseded | WORKSTREAM-02 | INFERENCE |
| REJECTED-06 | Broad structure refactors | Deprioritised | Structure now passes with warnings | Tentative | If new blocker appears | WORKSTREAM-03 | PROJECT-CONTEXT |
| REJECTED-07 | Renderer-first Universe Explorer | Rejected as unsafe | Violates projection/truth discipline | Tentative but strong | If contracts/gates change | WORKSTREAM-06 | INFERENCE |
| REJECTED-08 | Embodiment before explorer proof | Deprioritised | Need materialization/frame proof first | Tentative | If user changes priority | WORKSTREAM-06 | INFERENCE |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Treating suggestions as decisions | False project history | Medium | High | Preserve labels | all | FACT |
| RISK-02 | Repo status stales | Wrong task order | High | High | Re-fetch before action | WORKSTREAM-03/04 | VERIFY |
| RISK-03 | Broad feature work starts too early | Violates Foundation Lock | Medium | High | Follow queue/gates | WORKSTREAM-04/06 | PROJECT-CONTEXT |
| RISK-04 | Explorer becomes renderer/free camera | Doctrine violation | Medium | High | Contract/headless first | WORKSTREAM-06 | INFERENCE |
| RISK-05 | Camera drives materialization/truth | Fake simulation | Medium | High | Interest/refinement law | WORKSTREAM-06/09 | PROJECT-CONTEXT |
| RISK-06 | Workbench mutates truth | Authority leak | Low-medium | High | Projection contracts | WORKSTREAM-05 | PROJECT-CONTEXT |
| RISK-07 | Full-gate debt ignored | Release/proof blockage | Medium | Medium-high | Targeted cleanup | WORKSTREAM-03 | PROJECT-CONTEXT |
| RISK-08 | Old chats over-assumed | Invented context | Medium | High | Limit to visible excerpts | WORKSTREAM-01 | FACT |
| RISK-09 | Deep primitives gap forgotten | Weak domain foundation | Medium | Medium | Draft spec | WORKSTREAM-10 | INFERENCE |
| RISK-10 | Failure ontology gap forgotten | Unrealistic systems | Medium | Medium | Draft spec | WORKSTREAM-10 | INFERENCE |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Latest `.aide/queue/current.toml` | Task order may change | GitHub repo | P0 | WORKSTREAM-04 | VERIFY |
| VERIFY-02 | Latest `FOUNDATION_LOCK.md` | Allowed work may change | GitHub repo | P0 | WORKSTREAM-04/06 | VERIFY |
| VERIFY-03 | Full CTest status | Proof/release readiness | CI/local run | P1 | WORKSTREAM-03 | VERIFY |
| VERIFY-04 | Completion of `PRESENTATION-CONTRACT-01` | Determines next task | repo/audit/queue | P0 | WORKSTREAM-04 | VERIFY |
| VERIFY-05 | Existing Universe Explorer work | Avoid duplicate plan | repo search | P1 | WORKSTREAM-06 | VERIFY |
| VERIFY-06 | Latest structure warnings | Cleanup priority | repo audit | P1 | WORKSTREAM-03 | VERIFY |
| VERIFY-07 | Provider/render gates | Visual explorer timing | provider docs/queue | P1 | WORKSTREAM-06 | VERIFY |
| VERIFY-08 | Other old-chat reports | Aggregation consistency | user-provided reports | P1 | WORKSTREAM-01 | VERIFY |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | User pasted old architecture doctrine | Established seven-layer/meta architecture and deep primitives | Preserves months of thinking | Background/spec book | High |
| 2 | User asked to recover Dominium Two | Assistant reconstructed repo-grounded Λ/Σ/Φ/Υ/Ζ direction | Bridged old chats to repo | Context | Medium |
| 3 | User corrected planning-only scope | Chat mode fixed | Prevents implementation drift | Hard constraint | High |
| 4 | User asked repo recap | Assistant read many docs | Grounded discussion in live repo | Core evidence | High |
| 5 | Repo audit answer | Most doctrine preserved; gaps identified | Avoids rewriting canon | Carry forward | Medium-high |
| 6 | User proposed Universe Explorer | First major objective shifted concrete | Product direction | Very important | High |
| 7 | Explorer requirements answer | Refined as governed inspection/materialization proof | Avoids renderer-first trap | Core plan | Medium-high |
| 8 | User pasted latest structure status | Structure considered clean enough with warnings | Stops broad cleanup | Current strategy | Medium-high |
| 9 | Best plan forward answer | Recommended presentation/projection → explorer sequence | Immediate next plan | Core plan | Medium |
| 10 | User uploaded preservation prompt | Current task created | Export/handoff | Current output | High |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Project Continuity | Recovery of old doctrine and repo alignment | ARTIFACT-02/04 | Context + requirement | High | Merge with other chats |
| Universal Reality | Truth/materialization/representations | WORKSTREAM-02 | Requirement | Medium-high | Already repo-captured |
| Deep Primitives | Material/geometry/constraint/process/affordance/design knowledge | WORKSTREAM-10 | Open issue / future requirement | Medium | Needs master spec |
| Failure Ontology | Cross-domain failure classes | WORKSTREAM-10 | Open issue | Medium | Needs master spec |
| Workbench | Projection-first product shell | WORKSTREAM-05 | Requirement | Medium-high | Must not own truth |
| Universe Explorer | First major objective | WORKSTREAM-06 | Requirement candidate | Medium-high | Needs formal contract |
| No Modal Loading | Seamless experience law | WORKSTREAM-07 | Requirement | Medium-high | Already repo docs |
| Reference Frames | 1:1 scale frame switching | WORKSTREAM-08 | Requirement | Medium-high | Needs proof |
| Materialization | Explicit refinement/provenance | WORKSTREAM-09 | Requirement | Medium-high | Needs proof |
| Repo Governance | Stop broad cleanup; targeted cleanup | WORKSTREAM-03 | Context/requirement | Medium-high | Verify latest repo |
