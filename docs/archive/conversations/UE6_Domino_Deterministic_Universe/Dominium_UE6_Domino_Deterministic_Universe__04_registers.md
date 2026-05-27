# STRUCTURED REGISTERS — Dominium UE6, Domino, and Deterministic Universe Feasibility

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Engine/runtime strategy | Decide how UE5, UE6, Domino, and custom systems should relate | Recommended hybrid architecture exists | Explicit project-level engine strategy | Active | P0 | 4/5 | INFERENCE |
| WORKSTREAM-02 | Deterministic core | Build engine-independent canonical simulation | Concept defined | Cross-platform deterministic prototype | Active | P0 | 5/5 | INFERENCE |
| WORKSTREAM-03 | Sparse planetary world | Store procedural planets plus player deltas | Concept defined | Chunked sparse terrain/world database | Active | P0 | 4/5 | INFERENCE |
| WORKSTREAM-04 | Collapse/refine simulation | Simulate unseen regions cheaply while preserving accounting | Conceptual models listed | Tested macro/micro transition design | Active | P0 | 4/5 | INFERENCE |
| WORKSTREAM-05 | MMO authority/fog of war | Prevent cheating and hidden-state leakage | Principles defined | Server-authoritative interest-filtered prototype | Active | P0 | 5/5 | INFERENCE |
| WORKSTREAM-06 | Unreal client adapter | Use Unreal for rendering/tooling without owning game truth | Recommended | Thin client consuming Dominium state/API | Candidate | P1 | 4/5 | INFERENCE |
| WORKSTREAM-07 | Domino portability | Preserve later port path | Requirement inferred from user question | Domino adapter possible without rewriting core | Candidate | P1 | 3/5 | INFERENCE |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Do not start directly on UE6 today | Recommended, not user-final | Visible answer on UE6 availability | Avoids basing architecture on unavailable/uncertain tech | Use UE5/custom core first | WORKSTREAM-01 | 4/5 | INFERENCE / UNVERIFIED |
| DECISION-02 | Unreal should be client/tooling, not canonical simulation | Recommended | Visible answer repeatedly states this | Protects determinism and portability | Custom core required | WORKSTREAM-01, WORKSTREAM-06 | 5/5 | INFERENCE |
| DECISION-03 | Build DominiumSim as custom deterministic core | Recommended | User requires determinism | Unreal gameplay stack unsuitable as truth layer | Headless prototype first | WORKSTREAM-02 | 5/5 | INFERENCE |
| DECISION-04 | Store planets as procedural base plus sparse deltas | Recommended | User requires full planets and edits | Avoids storing/simulating everything | WorldDB/event log needed | WORKSTREAM-03 | 4/5 | INFERENCE |
| DECISION-05 | Use server authority for persistent MMO outcomes | Recommended | Fog-of-war and cheating risks | Prevents client manipulation of resources/secrets | Client compute limited | WORKSTREAM-05 | 5/5 | INFERENCE |
| DECISION-06 | Define single universe as shared persistence with partitioned regions | Recommended | Millions in same local space rejected | Makes MMO goal tractable | Need region authority/interest management | WORKSTREAM-05 | 5/5 | INFERENCE |
| DECISION-07 | Keep Domino as future adapter | Recommended | User asked about later portability | Portability requires clean adapter boundary | Do not embed rules in Unreal | WORKSTREAM-07 | 4/5 | INFERENCE |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Define deterministic simulation MVP | P0 | U0 | User/project | None | Scope for machines/terrain/players | MVP spec | Choose minimal entities and tick model | WORKSTREAM-02 | INFERENCE |
| TASK-02 | Prototype fixed-tick command-log simulation | P0 | U1 | Project | TASK-01 | Language/toolchain | Running headless sim | Implement tick loop and state hashes | WORKSTREAM-02 | INFERENCE |
| TASK-03 | Define coordinate hierarchy | P0 | U1 | Project | TASK-01 | Solar-system scale targets | Coordinate spec | Pick integer/fixed-point representation | WORKSTREAM-03 | INFERENCE |
| TASK-04 | Prototype sparse terrain chunk edits | P0 | U1 | Project | TASK-03 | Terrain model choice | Save/load chunk delta demo | Implement chunk edit log | WORKSTREAM-03 | INFERENCE |
| TASK-05 | Model factory graph simulation | P0 | U1 | Project | TASK-01 | Machine/resource examples | Graph update prototype | Define node/edge invariants | WORKSTREAM-02 | INFERENCE |
| TASK-06 | Design collapse/refine rules | P0 | U1 | Project | TASK-05 | Macrostate invariants | Collapse/refine spec | Define accounting-preserving macro model | WORKSTREAM-04 | INFERENCE |
| TASK-07 | Define fog-of-war sensory model | P0 | U1 | Project | TASK-02 | Sensor/entity rules | Visibility and interest spec | List knowable vs hidden state | WORKSTREAM-05 | INFERENCE |
| TASK-08 | Define client authority boundaries | P0 | U1 | Project | TASK-07 | Trust model | Client/server authority matrix | Classify actions as propose/verify/commit | WORKSTREAM-05 | INFERENCE |
| TASK-09 | Build minimal server authority prototype | P1 | U2 | Project | TASK-02, TASK-07 | Networking/runtime choice | Server-owned state demo | Implement one region authority loop | WORKSTREAM-05 | INFERENCE |
| TASK-10 | Build Unreal visualization adapter | P1 | U2 | Project | TASK-02, TASK-04 | State API and mesh output | UE client demo | Render a local chunk from core data | WORKSTREAM-06 | INFERENCE |
| TASK-11 | Define Domino adapter contract | P1 | U2 | Project | TASK-01 | Domino capabilities | Adapter interface doc | Clarify Domino role | WORKSTREAM-07 | INFERENCE |
| TASK-12 | Verify current UE5/UE6 claims | P1 | U1 | Project | None | Official Epic docs/current sources | Verification memo | Browse official docs before hard decisions | WORKSTREAM-01 | UNVERIFIED |
| TASK-13 | Create engine strategy spec-book chapter | P1 | U2 | Project | This report | Aggregated Dominium context | Formal chapter | Merge with other Dominium reports | WORKSTREAM-01 | INFERENCE |
| TASK-14 | Define anti-lag/anti-abuse limits for player machines | P1 | U2 | Project | TASK-05 | Machine design goals | Limits/gas policy | Identify exploit classes | WORKSTREAM-02, WORKSTREAM-05 | INFERENCE |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Canonical simulation must be deterministic if determinism remains a requirement | Technical | Hard | User requirement | Use fixed-step, deterministic math/order | Desyncs, broken replay | 5/5 | INFERENCE |
| CONSTRAINT-02 | Hidden state must not be sent to unauthorized clients | Security/gameplay | Hard | Fog-of-war requirement | Server-side interest filtering | Cheating and espionage | 5/5 | INFERENCE |
| CONSTRAINT-03 | Persistent MMO outcomes must be server-authoritative | Security | Hard | Client-cheat risk | Client propose/server verify | Economy corruption | 5/5 | INFERENCE |
| CONSTRAINT-04 | Commercial engine systems cannot own portable core rules | Architecture | Hard if Domino portability matters | User asks about porting | Adapter boundaries required | Port becomes rewrite | 5/5 | INFERENCE |
| CONSTRAINT-05 | Full-fidelity simulation everywhere is impossible | Compute | Hard | Scale requirements | Use simulation LOD | Lag/cost explosion | 5/5 | INFERENCE |
| CONSTRAINT-06 | A single local area cannot support millions of fully interacting players at low latency | Networking | Hard | Bandwidth/interest limits | Partition/LOD/caps/time dilation | Unrealistic promises | 5/5 | INFERENCE |
| CONSTRAINT-07 | External UE6 facts are stale-prone | Factual | Hard | UE6 roadmap changes | Verify before relying | Bad planning assumptions | 5/5 | UNVERIFIED |
| CONSTRAINT-08 | Player-designed machines need compute/resource limits | Design/security | Hard | Lag-abuse risk | Gas budgets/operation caps | Lag weapons | 4/5 | INFERENCE |
| CONSTRAINT-09 | File/report outputs must distinguish fact from inference | Documentation | Hard | Uploaded prompt | Use labels | Bad aggregation | 5/5 | FACT |
| CONSTRAINT-10 | This package cannot claim full-chat coverage beyond available context | Epistemic | Hard | Limited transcript access | Mark partial coverage | False preservation | 5/5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Human-readable explanation before machine-readable registers | Documentation | Explicit | Strong | Lead with prose | Output feels unusable | FACT |
| PREF-02 | Direct, source-grounded, audit-ready answers | Communication | Explicit from user profile | Strong | Include uncertainty and caveats | Loss of trust | PROJECT-CONTEXT |
| PREF-03 | Do not over-compress | Documentation | Explicit in prompt | Strong | Preserve rationale and alternatives | Missing context | FACT |
| PREF-04 | Preserve rejected and tentative ideas | Documentation | Explicit in prompt | Strong | Track status carefully | Bad future decisions | FACT |
| PREF-05 | Avoid asking to proceed when enough info exists | Workflow | Explicit in prompt | Strong | Proceed with best effort | Unnecessary delay | FACT |
| PREF-06 | Downloadable files when available | Artifact | Explicit in prompt | Strong | Create package files | Incomplete deliverable | FACT |
| PREF-07 | Use labels FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT | Epistemic | Explicit in prompt | Strong | Label uncertain claims | False certainty | FACT |
| PREF-08 | Prefer long-term architectural correctness over short-term convenience | Technical | Inferred | Medium-high | Recommend custom core | Over-engineering if wrong | INFERENCE |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Should Unreal be first renderer/client? | Affects tooling and prototype path | Unreal recommended as useful frontend | Final choice not user-confirmed | Compare prototype costs | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-02 | What exactly is Domino? | Determines portability target | Domino referenced as alternative/future runtime | Detailed capabilities not visible here | Retrieve/define Domino spec | P0 | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-03 | What language for DominiumSim? | Affects determinism/tooling | C++/Rust/C possible | No final language choice in this chat | Decide based on portability and tests | P0 | WORKSTREAM-02 | UNCERTAIN |
| QUESTION-04 | What determinism standard is required? | Drives math/networking | Determinism required broadly | Exact standard not specified | Define deterministic test contract | P0 | WORKSTREAM-02 | UNCERTAIN |
| QUESTION-05 | What terrain representation should be used? | Affects planets/terraforming | Sparse voxel/SDF/hybrid discussed | Final representation undecided | Prototype alternatives | P0 | WORKSTREAM-03 | UNCERTAIN |
| QUESTION-06 | How exact must collapse/refine be? | Affects simulation LOD | Three models listed | Tolerance not specified | Define invariants | P0 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-07 | What MMO scale target is first? | Avoids impossible milestone | Millions local rejected | First player/bot target undecided | Choose test ladder | P1 | WORKSTREAM-05 | UNCERTAIN |
| QUESTION-08 | How to handle player-made lag machines? | Prevents abuse | Need gas/limits | Concrete limits undecided | Threat model and budget policy | P1 | WORKSTREAM-02 | INFERENCE |
| QUESTION-09 | Which UE5/UE6 facts are currently true? | Avoids stale planning | Earlier answers used external claims | Current 2026 state not verified in this pass | Check official docs/news | P1 | WORKSTREAM-01 | UNVERIFIED |
| QUESTION-10 | What source assets and schemas preserve portability? | Avoids Unreal lock-in | Source assets should stay portable | Exact formats/pipeline not specified | Define asset/data pipeline | P1 | WORKSTREAM-01 | INFERENCE |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | User-pasted UE6 requirements answer | Pasted text | Triggered UE6 vs Domino question | Preserved in visible chat | User | Yes, with verification caveat | External claims may be stale/wrong | FACT / UNVERIFIED |
| ARTIFACT-02 | Assistant UE5-now/UE6-later answer | Chat answer | Strategic engine guidance | Preserved | Assistant | Yes | Not user-final by itself | FACT |
| ARTIFACT-03 | User deterministic solar-system/MMO question | Chat prompt | Defines full technical challenge | Preserved | User | Yes | High-value requirements source | FACT |
| ARTIFACT-04 | Assistant hybrid architecture answer | Chat answer | Defines DominiumSim/WorldDB/Server pattern | Preserved | Assistant | Yes | Main architecture artifact | FACT |
| ARTIFACT-05 | Pasted text.txt | Uploaded prompt | Requests this preservation package | Available | User | Yes | Current uploaded file | FACT |
| ARTIFACT-06 | 00_manifest.md | Generated file | Package overview | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-07 | 01_human_readable_report.md | Generated file | Sections 0–16 | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-08 | 02_context_transfer_packet.md | Generated file | Future chat packet | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-09 | 03_spec_sheet.yaml | Generated file | Aggregation spec | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-10 | 04_registers.md | Generated file | Sections 17–28 | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-11 | 05_aggregator_packet.md | Generated file | Central aggregation input | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-12 | 06_reader_brief.md | Generated file | Short brief | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-13 | 07_verification_and_audit.md | Generated file | Audit and verification | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-14 | 08_future_chat_bootstrap_prompt.md | Generated file | Reuse prompt | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-15 | 09_in_chat_reader.md | Generated file | Reader guide | Created by this task | Assistant/tool | Yes | New artifact | FACT |
| ARTIFACT-16 | handoff_package.zip | Generated ZIP | Bundled files | Created by this task | Assistant/tool | Yes | New artifact | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Unreal as entire game | Rejected | Blocks determinism/portability | Tentative but strong | Only if goals are reduced | WORKSTREAM-01 | INFERENCE |
| REJECTED-02 | Wait for UE6 | Deprioritised | UE6 uncertain/unavailable | Tentative | If UE6 becomes public and uniquely useful | WORKSTREAM-01 | INFERENCE / UNVERIFIED |
| REJECTED-03 | Client authority for MMO simulation | Rejected | Cheating/secrecy/economy risk | Strong | Private single-player/co-op only | WORKSTREAM-05 | INFERENCE |
| REJECTED-04 | Millions in one local fully interactive space | Rejected | Networking/computation limits | Strong | Only abstracted/time-dilated/instanced | WORKSTREAM-05 | INFERENCE |
| REJECTED-05 | Full-fidelity sim everywhere | Rejected | Compute/storage impossible | Strong | Small offline worlds only | WORKSTREAM-04 | INFERENCE |
| REJECTED-06 | Unreal Blueprints as core source of truth | Rejected | Not portable to Domino | Strong if portability matters | Throwaway prototype only | WORKSTREAM-07 | INFERENCE |
| REJECTED-07 | Every factory object as active physics | Rejected | Scale infeasible | Strong | Tiny demos only | WORKSTREAM-02 | INFERENCE |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Treating assistant recommendation as user-final decision | Misleading spec | Medium | High | Mark status and ask for confirmation before formalizing | All | INFERENCE |
| RISK-02 | Building too much inside Unreal | Domino port becomes rewrite | High | High | Enforce core/adapter separation | WORKSTREAM-01 | INFERENCE |
| RISK-03 | Determinism failure across platforms | Desync/replay breakage | High | High | Fixed math, state hashes, CI tests | WORKSTREAM-02 | INFERENCE |
| RISK-04 | Terrain storage explosion | Storage/cost failure | Medium | High | Sparse deltas/compression/snapshots | WORKSTREAM-03 | INFERENCE |
| RISK-05 | Collapse/refine breaks resource accounting | Economy inconsistency | Medium | High | Define invariants and audits | WORKSTREAM-04 | INFERENCE |
| RISK-06 | Fog-of-war leakage | Cheating/spoilers | Medium | High | Server interest filtering | WORKSTREAM-05 | INFERENCE |
| RISK-07 | Client compute abuse | Economy corruption | High | High | Server verification/commit only | WORKSTREAM-05 | INFERENCE |
| RISK-08 | MMO scale overpromise | Failed architecture expectations | High | High | Define scale tiers and load tests | WORKSTREAM-05 | INFERENCE |
| RISK-09 | UE6 claims become stale | Bad technology plan | High | Medium | Verify current official sources | WORKSTREAM-01 | UNVERIFIED |
| RISK-10 | Player machines become lag weapons | Server degradation | High | High | Gas/operation budgets | WORKSTREAM-02 | INFERENCE |
| RISK-11 | Spec book merges tentative content as requirement | Wrong commitments | Medium | High | Preserve labels | All | FACT |
| RISK-12 | Missing broader project context | Incomplete preservation | Medium | Medium | Merge with other chat reports later | All | PROJECT-CONTEXT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current UE6 public availability and roadmap | Time-sensitive | Official Epic announcements/docs | P0 | WORKSTREAM-01 | UNVERIFIED |
| VERIFY-02 | Current UE5 minimum/recommended platform requirements | Time-sensitive | Official Epic docs | P1 | WORKSTREAM-01 | UNVERIFIED |
| VERIFY-03 | Current Unreal determinism/networking capabilities | Version-sensitive | Epic docs/source/release notes | P1 | WORKSTREAM-02 | UNVERIFIED |
| VERIFY-04 | Domino technical capabilities | Missing definition | Project docs/source | P0 | WORKSTREAM-07 | UNCERTAIN |
| VERIFY-05 | Viability of Voxel Plugin/runtime terrain for MMO | Product/version-sensitive | Plugin docs/prototype | P2 | WORKSTREAM-03 | UNVERIFIED |
| VERIFY-06 | Best fixed-point/deterministic math library choices | Technical selection | Benchmarks/prototypes | P1 | WORKSTREAM-02 | UNVERIFIED |
| VERIFY-07 | Persistence backend options for sparse chunks/events | Architecture selection | Prototype/DB docs | P1 | WORKSTREAM-03 | UNVERIFIED |
| VERIFY-08 | Practical player-count targets by phase | Product planning | Benchmarks/design docs | P1 | WORKSTREAM-05 | UNCERTAIN |
| VERIFY-09 | Licensing implications of Unreal vs custom/Domino | Business/legal | Official licenses/legal review | P1 | WORKSTREAM-01 | UNVERIFIED |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | User pasted UE6 platform answer | Introduced UE6 as possible Dominium base | Triggered architecture question | External claims need verification | 4/5 |
| 2 | User asked UE6 instead of Domino | Need for engine strategy became explicit | Dominium portability at stake | Core question remains relevant | 5/5 |
| 3 | Assistant recommended UE5 now/UE6 later/Domino portability | Set hybrid direction | Avoided waiting for UE6 | Main strategic guidance | 4/5 |
| 4 | User expanded to deterministic solar-system/MMO requirements | Scope widened dramatically | Engine choice became system architecture question | Central project framing | 5/5 |
| 5 | Assistant rejected out-of-box engine solution | Clarified no commercial engine solves all | Avoids unrealistic expectations | Important caveat | 5/5 |
| 6 | Assistant proposed DominiumSim/WorldDB/Server | Established core architecture | Gives portable path | Main carry-forward | 5/5 |
| 7 | Assistant detailed determinism, sparse terrain, fog, client trust, MMO limits | Created design principles | Identifies future work | High relevance | 5/5 |
| 8 | User uploaded preservation prompt | Requested report/files/registers | Turned chat into archival task | Current deliverable | 5/5 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Engine strategy | Unreal as frontend, not canonical simulation | DECISION-02 | Requirement candidate | 5/5 | Needs user confirmation |
| Deterministic simulation | Fixed-step custom core | DECISION-03 | Requirement candidate | 5/5 | Core prototype first |
| World persistence | Procedural planets plus sparse deltas | DECISION-04 | Requirement candidate | 4/5 | Terrain model still open |
| MMO authority | Server-authoritative persistent outcomes | DECISION-05 | Requirement candidate | 5/5 | Hard security constraint |
| Portability | Domino as adapter target | DECISION-07 | Context/open issue | 4/5 | Domino capabilities needed |
| Simulation LOD | Collapse/refine as core mechanic | WORKSTREAM-04 | Requirement candidate | 4/5 | Must prototype |
| Scale limits | Single universe not single local million-player room | DECISION-06 | Requirement/context | 5/5 | Prevents overpromise |
