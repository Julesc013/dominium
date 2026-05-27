# STRUCTURED REGISTERS — Domino/Dominium Engine Baseline, Architecture, and Feasibility

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Project identity and architecture boundary | Preserve Domino substrate / Dominium game distinction | Strongly established in chat and canon | Formalized across docs/code/API boundaries | Active | P0 | High | FACT |
| WORKSTREAM-02 | Engine readiness and baseline path | Establish honest runnable baseline | Substrate exists; playable path blocked/fragile | One canonical repo-local baseline command passes strict validation | Active | P0 | High | FACT |
| WORKSTREAM-03 | Deterministic execution and proof | Ensure replayable deterministic simulation | Existing source/docs show substrate | Golden proof/replay path for gameplay slice | Active | P0 | High | FACT |
| WORKSTREAM-04 | Portability/modularity/reuse doctrine | Make code reusable across games/projects | Strong principles discussed | Public contracts + replaceable providers + compatibility tests | Active | P1 | High | INFERENCE |
| WORKSTREAM-05 | Pack/mod/capability architecture | Enable data-driven extensibility | Repo has pack verification and capability negotiation docs | Pack-driven gameplay slice with proof | Active | P1 | High | FACT |
| WORKSTREAM-06 | CAD/design/building substrate | Support build-anything without requiring CAD | Conceptual architecture + early FAB/physical code | Canonical DesignArtifact + layered authoring | Future | P1 | Medium | INFERENCE |
| WORKSTREAM-07 | Geometry/destruction representation | Choose building/destruction data model | Hybrid recommended | Formal geometry provider/contracts | Future | P1 | Medium | INFERENCE |
| WORKSTREAM-08 | Sparse full-scale universe | Support solar systems/planets/civilizations at scale | Strategic architecture discussed | Domain/capsule/overlay/shard model | Future | P1 | Medium | INFERENCE |
| WORKSTREAM-09 | Accessibility and low-performance play | Support low-skill and low-hardware users | Strong user preference | CLI/TUI/simple UI/templates/proxy modes | Future | P1 | Medium-high | FACT / INFERENCE |
| WORKSTREAM-10 | Future spec book / aggregation | Preserve chat for master spec | This package created | Merge with other chat reports | Active | P0 | High | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Domino is reusable substrate; Dominium is one game/product layer | Accepted direction | User goals + repo canon | Prevents coupling | Enforce engine/game boundary | WORKSTREAM-01 | High | FACT |
| DECISION-02 | Engine is not a finished playable game engine | Accepted correction | User pasted assessment + client `support_claim_playable=false` | Avoid premature gameplay expansion | Focus baseline | WORKSTREAM-02 | High | FACT |
| DECISION-03 | Milestone 0 precedes builder/destruction lab | Accepted sequencing | User explicitly endorsed correction | Fix blocked runtime first | P0 tasks dominate | WORKSTREAM-02 | High | FACT |
| DECISION-04 | Use contract/capability/registry/proof architecture | Strong direction | Repo docs and assistant plan | Modularity/extensibility | Formalize extension system | WORKSTREAM-04/05 | Medium-high | INFERENCE |
| DECISION-05 | CAD-capable but not CAD-required gameplay | Strong direction | User stated freedom + accessibility | Balance power and ease | Layered authoring | WORKSTREAM-06/09 | Medium-high | INFERENCE |
| DECISION-06 | No default recipes/tech trees/levels | User preference | User explicitly stated | Preserve freedom | Support only via packs/law/modes | WORKSTREAM-05/06 | High | FACT |
| DECISION-07 | Hybrid geometry, not voxel-first | Recommendation | Building/destruction discussion | Precise machines + sparse terrain | Future geometry contracts | WORKSTREAM-07 | Medium | INFERENCE |
| DECISION-08 | Unreal not authoritative core | Recommendation | Full-scale universe discussion | Determinism/proof needs | Maybe renderer/editor only | WORKSTREAM-08 | Medium | INFERENCE |
| DECISION-09 | Full scale requires collapsed multi-resolution fidelity | Strong conclusion | Feasibility reasoning | Avoid impossible full fidelity | Domain/capsule architecture | WORKSTREAM-08 | High | INFERENCE |
| DECISION-10 | Avoid broad restructure before baseline | Recommendation | Repo current reality + fragility | Avoid breaking paths | Stabilize first | WORKSTREAM-02/04 | High | INFERENCE |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Fix server/runtime circular import | P0 | U0 | Developer / future assistant | Current server/runtime files | Error trace, files | `server_main --help` works | Inspect import graph | WORKSTREAM-02 | FACT |
| TASK-02 | Fix server CLI forwarding/import path | P0 | U0 | Developer | TASK-01 | CLI contract | Server public entrypoint works | Define CLI adapter boundary | WORKSTREAM-02 | FACT |
| TASK-03 | Make `session_create -> session_boot` pass | P0 | U0 | Developer | Bundle/lock/session artifacts | Current refusal reports | Baseline session boots | Reproduce refusal | WORKSTREAM-02 | FACT |
| TASK-04 | Resolve baseline bundle seam | P0 | U0 | Developer | TASK-03 | `bundle.base.lab`, MVP bundle docs | Explicit baseline bundle selection | Decide wrapper/default behavior | WORKSTREAM-02 | FACT |
| TASK-05 | Fix time-anchor policy registry | P0 | U0 | Developer | Registry compile/lockfile | Failing verifier output | Baseline universe verifier passes | Locate missing/invalid registry | WORKSTREAM-02 | FACT |
| TASK-06 | Add canonical repo-local playtest command | P0 | U0 | Developer | TASK-01–05 | Existing scripts | One strict command | Design command interface | WORKSTREAM-02 | FACT |
| TASK-07 | Make `check_local_playtest_path.py --strict` pass | P0 | U0 | Developer | TASK-01–06 | Validator output | `proof_status` unblocked | Run/fix iteratively | WORKSTREAM-02 | FACT |
| TASK-08 | Preserve/re-run local validation evidence | P1 | U1 | Developer | Build environment | Logs/outputs | Audit-grade evidence | Upload or store logs | WORKSTREAM-02/10 | INFERENCE |
| TASK-09 | Implement one deterministic build action | P1 | U1 | Developer | Milestone 0 | Part/assembly code | Accepted/refused action proof | Define minimal intent | WORKSTREAM-03/06 | INFERENCE |
| TASK-10 | Implement one deterministic removal/damage action | P1 | U2 | Developer | TASK-09 | Assembly support state | Replayable damage/removal | Use simple part state | WORKSTREAM-07 | INFERENCE |
| TASK-11 | Draft DesignArtifact contract | P1 | U2 | Developer/spec assistant | TASK-09 | CAD/building goals | Schema/spec draft | Extract requirements | WORKSTREAM-06 | INFERENCE |
| TASK-12 | Define geometry provider strategy | P2 | U2 | Developer/spec assistant | TASK-11 | B-Rep/CSG/NURBS analysis | Provider/contract proposal | Research options | WORKSTREAM-07 | INFERENCE |
| TASK-13 | Create platform/validation unification docs | P1 | U1 | Developer/spec assistant | Baseline paths | Existing docs | Reduced drift | Draft docs | WORKSTREAM-04 | INFERENCE |
| TASK-14 | Aggregate this chat into master spec book | P1 | U2 | User / future assistant | This package | Other chat reports | Spec book inputs | Use aggregator packet | WORKSTREAM-10 | FACT |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Determinism is primary | Technical/canon | Hard | Repo canon | All authoritative outputs reproducible | Replay/MP invalid | High | FACT |
| CONSTRAINT-02 | Process-only mutation | Technical/canon | Hard | Repo canon | No direct authoritative writes | Hidden state drift | High | FACT |
| CONSTRAINT-03 | Engine/game boundary | Architecture | Hard | Repo canon + user goal | No Dominium meaning in Domino | Reuse failure | High | FACT |
| CONSTRAINT-04 | Client/render projection only | Architecture | Hard | Repo canon | Client sends intents, does not author truth | Cheat/drift | High | FACT |
| CONSTRAINT-05 | Packs data-only | Modding/security | Hard | Repo canon | No executable code in packs | Security/determinism risk | High | FACT |
| CONSTRAINT-06 | No silent fallback | Reliability | Hard | Repo canon | Degrade/refuse explicitly | Hidden bugs | High | FACT |
| CONSTRAINT-07 | No default recipes/tech trees/levels | Product preference | Hard for default game | User statement | Use affordances/constraints instead | Wrong gameplay feel | High | FACT |
| CONSTRAINT-08 | Baseline first | Project sequencing | Hard near-term | User correction | Do not start CAD/destruction now | Wasted effort | High | FACT |
| CONSTRAINT-09 | Full scale, not full fidelity everywhere | Feasibility | Hard | Reasoned conclusion | Use collapse/sparse domains | Impossible compute | High | INFERENCE |
| CONSTRAINT-10 | Accessibility/low-performance support | Product | Soft-to-hard | User preference | Multiple authoring/UI tiers | Excludes players | Medium-high | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, source-grounded, audit-ready answers | Communication | Explicit | Strong | Cite, label uncertainty | Low trust | FACT |
| PREF-02 | Preserve uncertainty and corrections | Reasoning | Explicit | Strong | Do not overstate | False decisions | FACT |
| PREF-03 | Portable/modular/reusable code | Engineering | Explicit | Strong | Stable contracts/providers | Engine lock-in | FACT |
| PREF-04 | No default tech trees/recipes/XP | Game design | Explicit | Strong | Use constraints/affordances | Wrong game identity | FACT |
| PREF-05 | Full player freedom with low-skill accessibility | Game design | Explicit | Strong | Layered authoring | Too hard or too restrictive | FACT |
| PREF-06 | Low-performance/minimal GUI/disability support | UX | Explicit | Strong | CLI/TUI/simple modes | Exclusion | FACT |
| PREF-07 | Broad/deep thinking | Assistance | Explicit | Strong | Explore options/tradeoffs | Missed context | FACT |
| PREF-08 | Avoid impossible-scope overwhelm | Project management | Inferred | Strong | Milestones, baseline-first | Burnout | INFERENCE |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | What exact code causes circular import? | Blocks server baseline | User identified modules | Current stack trace/details | Reproduce locally | P0 | WORKSTREAM-02 | FACT |
| QUESTION-02 | Which baseline bundle should wrapper use? | Blocks session path | Default is `bundle.base.lab`; MVP trio exists | Desired final default | Decide explicit wrapper/default | P0 | WORKSTREAM-02 | FACT |
| QUESTION-03 | What time-anchor registry artifact is missing? | Blocks universe verifier | User reported error | Exact file/hash failure | Run verifier, inspect lock | P0 | WORKSTREAM-02 | FACT |
| QUESTION-04 | What is canonical playtest command? | Needed for baseline | Current path is recipe, not command | Command name/interface | Design and implement | P0 | WORKSTREAM-02 | FACT |
| QUESTION-05 | How much of local validation is reproducible? | Audit confidence | User pasted results | Logs unavailable | Upload/rerun logs | P1 | WORKSTREAM-10 | UNCERTAIN |
| QUESTION-06 | Exact DesignArtifact schema? | CAD/building future | Concept described | Field-level schema | Draft contract | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-07 | Which geometry kernel/provider? | Future building/destruction | Hybrid recommended | Library/implementation choice | Research/prototype | P2 | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-08 | Should Unreal be used as shell? | Product strategy | Not authoritative core | Whether useful at all | Dedicated comparison | P2 | WORKSTREAM-08 | UNCERTAIN |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | `Pasted text.txt` | Uploaded prompt | Preservation task instructions | Available | User upload | Yes | Must cite/preserve | FACT |
| ARTIFACT-02 | `engine/CMakeLists.txt` | Repo file | Evidence of engine target/modules | Fetched | GitHub | Yes | Shows `domino_engine` | FACT |
| ARTIFACT-03 | `game/CMakeLists.txt` | Repo file | Evidence of game target/modules | Fetched | GitHub | Yes | Shows `dominium_game` | FACT |
| ARTIFACT-04 | `docs/canon/constitution_v1.md` | Canon doc | Architecture/execution constraints | Fetched | GitHub | Yes | Strong source | FACT |
| ARTIFACT-05 | `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md` | Repo reality doc | Baseline-first current state | Fetched | GitHub | Yes | Crucial correction | FACT |
| ARTIFACT-06 | `apps/client/main_client.c` | Source | Playability false evidence | Fetched | GitHub | Yes | Critical readiness evidence | FACT |
| ARTIFACT-07 | `tools/xstack/registry_compile/constants.py` | Source | Default bundle seam | Fetched | GitHub | Yes | `bundle.base.lab` | FACT |
| ARTIFACT-08 | Physical/FAB source files | Source | Early construction/fabrication substrate | Fetched | GitHub | Yes | Future build slice | FACT |
| ARTIFACT-09 | User pasted readiness assessment | Text in chat | Local validation/blocker evidence | Visible | User | Yes | Needs verification | FACT/UNVERIFIED |
| ARTIFACT-10 | This handoff package | Generated files | Preservation/export | Created now | Assistant | Yes | Aggregation-ready | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Build full engine before game | Rejected | Infinite engine trap | Strong | Never as primary path | WORKSTREAM-02 | INFERENCE |
| REJECTED-02 | Start CAD/destruction immediately | Superseded | Baseline blocked | Temporary | After Milestone 0 | WORKSTREAM-06/07 | FACT |
| REJECTED-03 | Voxel-first universal engine | Rejected | Poor CAD/machine semantics | Strong recommendation | For terrain/damage fields only | WORKSTREAM-07 | INFERENCE |
| REJECTED-04 | Full fidelity universe everywhere | Rejected | Impossible compute | Final | Only if scope radically shrinks | WORKSTREAM-08 | INFERENCE |
| REJECTED-05 | Unreal as authoritative core | Rejected/deprioritized | Determinism/proof mismatch | Tentative | If architecture changes | WORKSTREAM-08 | INFERENCE |
| REJECTED-06 | Default recipes/tech trees/levels | Rejected for default | User preference | Strong | Mods/game modes | WORKSTREAM-06 | FACT |
| REJECTED-07 | Broad repo restructure now | Deprioritized | Fragile baseline | Temporary | After baseline proof | WORKSTREAM-04 | INFERENCE |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Overstating readiness | Premature feature work | Medium | High | Keep `support_claim_playable=false` visible | WORKSTREAM-02 | FACT |
| RISK-02 | Skipping Milestone 0 | Builds on broken runtime | Medium | High | Make strict playtest command P0 | WORKSTREAM-02 | FACT |
| RISK-03 | Scope explosion | Project becomes impossible | High | High | Vertical slices only | All | INFERENCE |
| RISK-04 | Treating recommendations as decisions | False spec commitments | Medium | Medium | Preserve labels | WORKSTREAM-10 | FACT |
| RISK-05 | Full-fidelity simulation assumption | Impossible compute | Medium | High | Collapse/active-fidelity doctrine | WORKSTREAM-08 | INFERENCE |
| RISK-06 | Engine/game coupling | Reuse failure | Medium | High | Boundary checks/contracts | WORKSTREAM-01 | FACT |
| RISK-07 | CAD complexity overwhelming players | Bad UX | Medium | Medium-high | Layered authoring | WORKSTREAM-06/09 | INFERENCE |
| RISK-08 | Geometry kernel nondeterminism | Replay drift | Medium | High | Canonical validation/refusal | WORKSTREAM-07 | INFERENCE |
| RISK-09 | Stale repo facts | Wrong tasks | Medium | Medium | Re-verify live repo | WORKSTREAM-10 | FACT |
| RISK-10 | Losing local validation evidence | Low audit confidence | Medium | Medium | Upload/store logs | WORKSTREAM-02/10 | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | User-reported targeted CTest pass | Not independently run | Local logs / CI output | P0 | WORKSTREAM-02 | UNVERIFIED |
| VERIFY-02 | MP0 hash equivalence | Important substrate proof | Logs/artifacts | P0 | WORKSTREAM-02 | UNVERIFIED |
| VERIFY-03 | Current circular import stack | Need exact fix | Re-run command | P0 | WORKSTREAM-02 | FACT/UNVERIFIED |
| VERIFY-04 | `session_create -> session_boot` current failure | Need blocker detail | Command output | P0 | WORKSTREAM-02 | FACT/UNVERIFIED |
| VERIFY-05 | Time-anchor registry failure | Need file-level fix | Verifier report | P0 | WORKSTREAM-02 | FACT/UNVERIFIED |
| VERIFY-06 | Live repo still matches fetched GitHub files | Repo may change | Git pull/current fetch | P1 | All | UNVERIFIED |
| VERIFY-07 | Unreal current capabilities | External tooling changes | Official Unreal docs | P2 | WORKSTREAM-08 | UNVERIFIED |
| VERIFY-08 | Geometry provider/library options | Needed for future CAD | Library docs/prototype | P2 | WORKSTREAM-07 | UNVERIFIED |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | Project description request | Domino/Dominium/XStack framing established | Foundation | High | High |
| 2 | Historical engine lessons | Virtualize expensive things, tools matter | Strategy | Medium | High |
| 3 | Live repo correction | Existing infrastructure recognized | Avoid stale plan | High | High |
| 4 | Modularity/future-proofing | Stable contracts over folders | Reuse doctrine | High | High |
| 5 | CAD/building freedom | Layered authoring model | Future gameplay | Medium-high | Medium |
| 6 | B-Rep/CSG/NURBS | Hybrid geometry recommended | Future destruction/building | Medium | Medium |
| 7 | Engine readiness anxiety | Project reframed as substrate not finished game | Feasibility | High | High |
| 8 | User pasted local readiness | Milestone 0 inserted before gameplay | Critical correction | Very high | High |
| 9 | Full-scale universe | Multi-resolution sparse domain model | Long-term architecture | Medium-high | Medium |
| 10 | Preservation request | This package created | Future aggregation | Very high | High |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Engine/game boundary | Domino substrate vs Dominium meaning | DECISION-01, CONSTRAINT-03 | Requirement | High | Core architecture |
| Readiness roadmap | Milestone 0 before features | DECISION-03, TASK-01–07 | Requirement | High | Most important |
| Determinism/proof | Replay/hash/process-only mutation | CONSTRAINT-01/02 | Requirement | High | Canon-aligned |
| Modding/extensibility | Packs/capabilities/contracts | WORKSTREAM-05 | Requirement/context | High | Needs exact schemas |
| CAD/building | Layered authoring, DesignArtifact | WORKSTREAM-06 | Context/future requirement | Medium | Not near-term |
| Geometry/destruction | Hybrid CSG/B-Rep/NURBS/SDF | WORKSTREAM-07 | Context/open issue | Medium | Needs verification |
| Full-scale universe | Domain/capsule/sparse/fog/shards | WORKSTREAM-08 | Context/future requirement | Medium | Long-term |
| UX/accessibility | Simple/low-perf/disability support | PREF-05/06 | Requirement | Medium-high | Product principle |
| Unreal comparison | Use only as shell if at all | DECISION-08 | Context/open issue | Medium | Verify later |
| Preservation | Full handoff | ARTIFACT-10 | Aggregation input | High | This package |
