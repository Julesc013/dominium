# Structured Registers — Dominium Build and Future-Proofing Architecture

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Build/toolchain governance | Replace ad hoc presets with tuple-driven build contracts and generated local presets | Recommended, not implemented in this task | Machine-probed, contract-governed builds across modern and legacy hosts | Proposed | P0 | High | RECOMMENDATION |
| WORKSTREAM-02 | Repo/source structure | Preserve and refine canonical source spine | Top-level structure appears close; deeper cleanup remains | Stable ownership-based layout with no active status/misc names | Active/proposed | P1 | Medium-High | FACT+RECOMMENDATION |
| WORKSTREAM-03 | Public surface governance | Define all public ABI/API/schema/protocol/command surfaces | Missing as explicit registry | Machine-readable public surface registry and validators | Proposed | P0 | High | RECOMMENDATION |
| WORKSTREAM-04 | Replacement protocol | Allow complete subsystem rewrites safely | Discussed as missing | Black-box conformance protocol for replacing modules/directories | Proposed | P1 | High | RECOMMENDATION |
| WORKSTREAM-05 | Schema/protocol compatibility | Ensure saves/replays/packages/protocols evolve safely | Existing schema doctrine surfaced; compatibility harness recommended | Fixture-based migration/refusal/roundtrip proof | Proposed | P1 | High | RECOMMENDATION |
| WORKSTREAM-06 | Preservation/aggregation | Preserve this chat for future reading and spec-book aggregation | Completed by this task | Downloadable package plus in-chat guide | Complete | P0 | High | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Use C89 engine/C++98 game/deterministic/no CRT mixing/per-floor artifact constraints as discussion canon | User-stated/pasted constraint | Initial user-provided context | Bounds architecture | Must guide all build/API work | WORKSTREAM-01 | High | FACT |
| DECISION-02 | Use build orchestration above CMake rather than more manual presets | Recommended | Assistant answer | Avoids preset sprawl | Needs contracts/probes/generation | WORKSTREAM-01 | High | RECOMMENDATION |
| DECISION-03 | Keep CMake as build authority | Recommended | Assistant answer | Avoids custom build-system drift | AIDE/XStack must not replace CMake | WORKSTREAM-01 | High | RECOMMENDATION |
| DECISION-04 | Treat top-level structure as close and refine below it | Recommended | Repo docs and answer | Avoids churn while fixing real debt | Focus cleanup on ownership/boundaries | WORKSTREAM-02 | Medium | RECOMMENDATION |
| DECISION-05 | Freeze contracts, not implementations | Recommended | Modularity answer | Enables rewrites | Requires conformance tests | WORKSTREAM-03/04 | High | RECOMMENDATION |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Verify current repo HEAD and validation state | P0 | U0 | User/Codex/AIDE | GitHub/local repo access | Current commit, CI/build/test state | Updated state note | Run live repo audit | WORKSTREAM-01/02 | FACT |
| TASK-02 | Decide which recommendations become canon | P0 | U0 | User | This report | User acceptance/rejection | Canon update list | Review Decision Register | All | FACT |
| TASK-03 | Add public surface registry | P0 | U1 | Codex/AIDE | Accepted design | Surface list | `contracts/public_surface` + validator | Draft schema | WORKSTREAM-03 | RECOMMENDATION |
| TASK-04 | Add build tuple contracts and machine probe | P0 | U1 | Codex/AIDE | Build canon accepted | Toolchain/floor matrix | `contracts/build` + generated presets | Draft schema/tool | WORKSTREAM-01 | RECOMMENDATION |
| TASK-05 | Add dependency-edge contract | P1 | U1 | Codex/AIDE | Current source spine | Allowed dependency edges | Validator | Draft TOML | WORKSTREAM-02 | RECOMMENDATION |
| TASK-06 | Add ABI/header conformance tests | P1 | U1 | Codex/AIDE | Public surface registry | Toolchain list | Header compile tests | Start with engine headers | WORKSTREAM-03 | RECOMMENDATION |
| TASK-07 | Add schema/protocol compatibility harness | P1 | U2 | Codex/AIDE | Schema inventory | Old/new fixtures | Migration/refusal proof | Pick first frozen schemas | WORKSTREAM-05 | RECOMMENDATION |
| TASK-08 | Continue game/content cleanup | P2 | U2 | Codex/AIDE | Current repo state | Stale references | Clean domain/content layout | Scan references | WORKSTREAM-02/05 | RECOMMENDATION |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Engine C89 | Technical | Hard | User-provided canon | Public engine headers and core must remain C89-compatible | High | High | FACT |
| CONSTRAINT-02 | Game C++98 | Technical | Hard | User-provided canon | No modern C++ assumptions in game layer | Medium | High | FACT |
| CONSTRAINT-03 | Deterministic/fixed-point/no hidden behavior | Technical | Hard | User-provided canon | Avoid wall-clock/random/thread/order drift | High | High | FACT |
| CONSTRAINT-04 | Per-floor artifacts | Release | Hard | User-provided canon | No one-binary-for-all support claim | High | High | FACT |
| CONSTRAINT-05 | No CRT mixing | Build | Hard | User-provided canon | Explicit runtime policy per tuple | High | High | FACT |
| CONSTRAINT-06 | No silent API creep | Governance | Hard | User-provided canon | Capability/API changes need explicit contract/version proof | High | High | FACT |
| CONSTRAINT-07 | Human-readable preservation first | Output | Hard | Uploaded prompt | Report must explain substance, not just registers | Medium | High | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Detailed human-readable reports | Documentation | Explicit | High | Explain narrative and rationale first | User cannot use output | FACT |
| PREF-02 | Source-grounded, uncertainty-labelled answers | Epistemic | Explicit/project | High | Label FACT/INFERENCE/UNCERTAIN | Misleading canon | FACT/PROJECT-CONTEXT |
| PREF-03 | Future-proof modular architecture | Engineering | Explicit | High | Prefer contracts and boundaries | One-off project drift | FACT |
| PREF-04 | Avoid repeated clarifying questions when enough context exists | Workflow | Explicit/project | Medium-High | Proceed with assumptions | Wasted user time | PROJECT-CONTEXT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Which recommendations become binding canon? | Prevents accidental canonization | Recommendations are listed | User acceptance | User review | P0 | All | FACT |
| QUESTION-02 | What is current live repo state? | Avoid stale implementation | Sampled in chat | Latest HEAD/CI after chat | Re-run repo audit | P0 | WORKSTREAM-01/02 | UNVERIFIED |
| QUESTION-03 | Which surfaces are public/frozen? | Required for modularity | Need public surface registry | Exact list | Inventory headers/schemas/commands | P0 | WORKSTREAM-03 | RECOMMENDATION |
| QUESTION-04 | MVP versus archival support floors? | Controls build tuple priority | Many floors mentioned | User-supported floors | Define release policy | P1 | WORKSTREAM-01 | FACT |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Pasted build/toolchain/repo-state text | Context | Frame constraints/problem | Preserved in chat | User message | Yes | Includes prior GPT outputs | FACT |
| ARTIFACT-02 | Build architecture answer | Report | Tuple-driven build strategy | Preserved | Assistant | Yes | Recommendation, not canon | RECOMMENDATION |
| ARTIFACT-03 | Modularity/future-proofing answer | Report | Contract/replacement strategy | Preserved | Assistant | Yes | Recommendation, not canon | RECOMMENDATION |
| ARTIFACT-04 | `Pasted text.txt` | Uploaded prompt | Requested this export | Used | User upload | Yes | Current task source | FACT |
| ARTIFACT-05 | Handoff package files | Generated package | Preserve and aggregate this chat | Created now | This task | Yes | See file index | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | One binary for all floors | Rejected | Violates per-floor artifacts and compatibility proof | Strong | Only for explicitly compatible floor bundle, not universal claim | WORKSTREAM-01 | FACT/RECOMMENDATION |
| REJECTED-02 | Hand-maintaining every preset in `CMakePresets.json` | Deprioritised | Causes machine/preset sprawl | Tentative | Small curated shared presets remain valid | WORKSTREAM-01 | RECOMMENDATION |
| REJECTED-03 | AIDE replacing CMake | Rejected | CMake is native build authority | Strong recommendation | None unless project abandons CMake | WORKSTREAM-01 | RECOMMENDATION |
| REJECTED-04 | Freezing implementations/files | Rejected | Blocks rewrites | Strong | Freeze contracts instead | WORKSTREAM-04 | RECOMMENDATION |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Treating recommendations as accepted decisions | Bad canon/spec merge | Medium | High | Preserve labels; ask user to accept | All | FACT |
| RISK-02 | Stale repo/toolchain facts | Wrong implementation path | Medium | High | Verify live state | WORKSTREAM-01/02 | UNVERIFIED |
| RISK-03 | Over-focusing on folders over interfaces | Modularity illusion | Medium | High | Public surface registry first | WORKSTREAM-03 | RECOMMENDATION |
| RISK-04 | Over-compressing old chats | Lost rationale | High | Medium | Use human-readable reports | WORKSTREAM-06 | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current Dominium repo HEAD and CI/build/test status | Repo changed during/after chat | GitHub/local `git status`, CI logs | P0 | WORKSTREAM-01/02 | UNVERIFIED |
| VERIFY-02 | Current CMake/VS2026/VS2022/v141_xp facts | Toolchain facts may change | Official CMake/Microsoft docs | P1 | WORKSTREAM-01 | UNVERIFIED |
| VERIFY-03 | Which schemas are frozen in current repo | Schema docs may move/change | `contracts/schema`, schema metadata | P1 | WORKSTREAM-05 | UNVERIFIED |
| VERIFY-04 | Actual old-floor support claims | Avoid unsupported release promises | Release matrix + runtime VM proof | P0 | WORKSTREAM-01 | FACT |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | User pasted build/toolchain analysis | Established locked canon and repo-state frame | Set constraints | High | High |
| 2 | User asked build-system design question | Problem shifted to multi-machine toolchain governance | Needed architecture, not preset list | High | High |
| 3 | Assistant inspected repo/docs | Found preset/build/docs context | Grounded response | Medium; stale risk | Medium |
| 4 | Assistant proposed tuple-driven build system | Build truth moves to contracts/probes/generated presets | Key carry-forward | High | High |
| 5 | User asked broader modularity question | Scope expanded to reuse/rewrite/future-proofing | Major architecture theme | High | High |
| 6 | Assistant proposed public surfaces/replacement protocol | Contracts become stability boundary | Key carry-forward | High | High |
| 7 | User uploaded preservation prompt | Task became full chat export | Produced files | Complete | High |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Build governance | Tuple-driven builds, machine probes, generated presets | WORKSTREAM-01 | Candidate requirement | High | Needs user acceptance |
| Repo architecture | Ownership-based source spine | WORKSTREAM-02 | Context + candidate requirement | Medium | Verify current repo |
| ABI/API policy | Public surface registry and C ABI rules | WORKSTREAM-03 | Candidate requirement | High | Needs implementation |
| Replacement/refactor policy | Rewrite by conformance | WORKSTREAM-04 | Candidate requirement | High | Important for future reuse |
| Schema/protocol compatibility | Frozen/evolving schemas and fixtures | WORKSTREAM-05 | Requirement candidate | High | Needs harness |
| Preservation methodology | Human-readable + structured exports | WORKSTREAM-06 | Process requirement | High | Useful across retired chats |
