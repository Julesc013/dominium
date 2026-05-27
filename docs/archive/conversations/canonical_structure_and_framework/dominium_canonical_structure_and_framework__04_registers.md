# STRUCTURED REGISTERS — Dominium Canonical Structure and Domino Framework Architecture

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Canonical Repository Structure | End root/path chaos and enforce ownership roots. | Mostly clean; residual warnings remain. | Closed root set with validators and no stale active paths. | PASS_WITH_WARNINGS | P0 | High | FACT |
| WORKSTREAM-02 | Domino Framework Boundary | Define framework without new top-level root. | Reported committed and validated. | Framework identity lives in contracts/public headers/service law. | PASS_WITH_WARNINGS | P0 | High | FACT |
| WORKSTREAM-03 | Public Surface / ABI Governance | Register stable/public surfaces and enforce C-compatible ABI. | Scaffolds exist; warnings remain. | Every stable surface registered, versioned, tested. | Active | P0 | Medium | FACT |
| WORKSTREAM-04 | Service-first Provider Architecture | Make raylib/SDL/Lua providers, not architecture. | Provider structure partly committed; implementation still pending. | Runtime service providers with conformance tests and profiles. | Active | P0 | High | FACT |
| WORKSTREAM-05 | Presentation / Projection Spine | Unify CLI/TUI/rendered/native/headless over semantic views/actions. | Concept accepted; task remains active. | Projection conformance over shared commands/views/evidence. | Active | P1 | High | FACT |
| WORKSTREAM-06 | Workbench Product Spine | Build Workbench modules/workspaces through contracts. | Validation slice reported done; broad UI blocked. | Workbench shell/module/workspace over command/view/projection system. | Limited | P1 | High | FACT |
| WORKSTREAM-07 | Full-gate Proof / CTest | Remove stale tests and achieve full release proof. | Legacy path subset fixed; full CTest not green. | Full CTest/T4 classified or green. | Active debt | P0 | High | FACT |
| WORKSTREAM-08 | AIDE Control Plane | Govern AIDE queue/tasks/evidence and avoid stale generated state. | Some warnings remain. | AIDE workflow law and clean evidence/queue state. | Active debt | P1 | Medium | FACT |
| WORKSTREAM-09 | Pack/Content Authority | Keep authored packs under content and package law under contracts. | Mostly fixed; pack internal layout warnings remain. | Clear pack authority and consistent internal layout. | Active debt | P1 | High | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Keep closed canonical root set. | Accepted | Repeated prompts/reports. | Prevent root sprawl. | No casual new roots. | WORKSTREAM-01 | High | FACT |
| DECISION-02 | No first-party `src`/`source`. | Accepted | User explicit objection. | Avoid generic wrappers. | Validators should enforce. | WORKSTREAM-01 | High | FACT |
| DECISION-03 | Domino ≠ Dominium. | Accepted | Multiple later summaries. | Enables reuse. | Separate reusable substrate from game/product. | WORKSTREAM-02 | High | FACT |
| DECISION-04 | No top-level `framework/`. | Accepted | User-reported commit `repo: define Domino framework boundary`. | Avoid root ambiguity. | Framework is contracts/public headers. | WORKSTREAM-02 | High | FACT |
| DECISION-05 | C17/C++17 mainline with C-compatible ABI. | Accepted doctrine. | User pasted language-baseline synthesis. | Modern implementation plus portable boundary. | ABI validators and public header rules. | WORKSTREAM-03 | Medium | FACT/VERIFY |
| DECISION-06 | Third-party libraries are providers. | Accepted | Raylib/SDL/Lua discussions. | Avoid vendor lock-in. | Runtime provider paths and manifests. | WORKSTREAM-04 | High | FACT |
| DECISION-07 | Workbench is not authority. | Accepted | Workbench/presentation discussions. | Prevent UI bypass. | Workbench calls commands/services. | WORKSTREAM-06 | High | FACT |
| DECISION-08 | CLI/TUI/rendered/native are projections. | Accepted | Presentation spine discussions. | Avoid four UI systems. | `runtime/projection/*`, semantic contracts. | WORKSTREAM-05 | High | FACT |
| DECISION-09 | Provider choices live in profiles, not app paths. | Accepted | Provider structure reports. | Avoid product variants. | Use `release/profiles`/`content/profiles`. | WORKSTREAM-04 | High | FACT |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Repair stale AuditX/identity/launcher marker fast-strict debt. | P0 | U0 | AIDE/Codex | Current repo state | Latest fast-strict failure output | Clean normal gate | Generate/execute repair prompt | WORKSTREAM-07 | FACT |
| TASK-02 | Projection conformance. | P1 | U1 | AIDE/Codex | Presentation contract basics | Existing command/result/view artifacts | Conformance tests for projection modes | Run `PROJECTION-CONFORMANCE-01` | WORKSTREAM-05 | FACT |
| TASK-03 | Presentation contract finalization. | P1 | U1 | AIDE/Codex | Command/diagnostic contracts | Current contracts tree | View/action/projection schemas and validators | Run `PRESENTATION-CONTRACT-01` | WORKSTREAM-05 | FACT |
| TASK-04 | Raylib/SDL/Lua provider wedge. | P1 | U2 | AIDE/Codex | Provider structure and third-party fences | Provider manifests, vendored sources | First provider implementation scaffold | Run `PROVIDER-WEDGE-01` | WORKSTREAM-04 | INFERENCE |
| TASK-05 | Full CTest audit nonpath failures. | P0 | U1 | AIDE/Codex | Legacy path route done | Full CTest output | Failure ledger | Run `FULL-CTEST-AUDIT-NONPATH-01` | WORKSTREAM-07 | FACT |
| TASK-06 | Pack internal layout canon. | P1 | U2 | AIDE/Codex | Pack authority mostly fixed | Current pack leaves | Documented or normalized pack internals | Run pack layout task | WORKSTREAM-09 | FACT |
| TASK-07 | AIDE state classification. | P1 | U2 | AIDE/Codex | AIDE control-plane model | `.aide` tree | Clear source/local/generated classification | Run AIDE state task | WORKSTREAM-08 | FACT |
| TASK-08 | Runtime/engine residual taxonomy. | P2 | U2 | AIDE/Codex | Canonical structure cleanup | Current roots | Classified session/serialization/foundation etc. | Targeted cleanup | WORKSTREAM-01 | FACT |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | No new top-level roots without contract approval. | Structure | Hard | User and repeated doctrine. | Reject `framework/`, `modules/`, `profiles/`, `labs`. | Root sprawl. | High | FACT |
| CONSTRAINT-02 | No first-party `src`/`source` wrappers. | Structure | Hard | User explicit objection. | Implementation lives under ownership paths. | Refactor recurrence. | High | FACT |
| CONSTRAINT-03 | No third-party type leakage into stable law. | Architecture | Hard | Provider doctrine. | Raylib/SDL/Lua only in providers/proofs. | Vendor lock-in. | High | FACT |
| CONSTRAINT-04 | Public ABI is C-compatible, not C++ ABI. | ABI | Hard | Language baseline doctrine. | POD/opaque/versioned structs. | Binary instability. | Medium-High | FACT |
| CONSTRAINT-05 | Workbench must use command/service/evidence spine. | Product | Hard | Workbench doctrine. | No private validator/tool bypass. | UI becomes authority. | High | FACT |
| CONSTRAINT-06 | Full release readiness requires full-gate proof. | Testing | Hard for release | Reported status. | Do not claim release green. | False readiness. | High | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, rigorous, audit-ready answers. | Communication | Explicit profile + behavior | Strong | Use clear status, caveats, evidence. | User distrust. | FACT |
| PREF-02 | Avoid vague/soft language when structure is bad. | Communication | Inferred | Strong | Say not done when not done. | Misleading reassurance. | INFERENCE |
| PREF-03 | Prefer executable prompts for Codex/AIDE. | Workflow | Explicit through repeated requests | Strong | Generate concrete tasks with acceptance criteria. | Work stalls. | FACT |
| PREF-04 | Do not ask unnecessary clarifying questions. | Workflow | Explicit system/user preference | Strong | Proceed with assumptions and labels. | User frustration. | FACT |
| PREF-05 | Keep architecture future-proof and reusable. | Technical | Explicit | Strong | Favor contracts/providers/profiles over vendor/product paths. | Future refactor. | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Is full CTest green after latest fixes? | Determines release/full proof readiness. | Last visible status: not green/not fully run. | Current live status. | Run full CTest or audited shard. | P0 | WORKSTREAM-07 | FACT |
| QUESTION-02 | Lua 5.4 or 5.5? | Script ABI/provider pinning. | Chat says pin one. | Final choice. | Decide after compatibility/security review. | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-03 | `external/upstream` or `external/vendor`? | Consistency and provenance. | Both discussed; final should choose one. | Latest repo canon. | Check contracts/docs. | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-04 | Is pack internal `content/` canonical? | Pack layout and tooling. | Warning remains. | Pack law. | Run pack internal layout task. | P1 | WORKSTREAM-09 | FACT |
| QUESTION-05 | Are `.aide/cache` and `.aide/queue` source or local state? | Prevent generated/live state confusion. | Need classification. | Exact contents. | AIDE state classification task. | P1 | WORKSTREAM-08 | FACT |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | `dominium_canonical_handoff.md/.txt` | Handoff files | Earlier self-contained summary. | Created earlier | This chat | Yes | Historical snapshot as of 2026-05-20. | FACT |
| ARTIFACT-02 | `dir_tree.json`, `dirfiles_manifest.json`, ZIP exports | Structure evidence | Inspect repo tree. | Mixed quality | User uploads | Yes with caveats | Many bundles were inconsistent/stale. | FACT |
| ARTIFACT-03 | `CANON_STRUCTURE_ACTUAL_FINAL_CLEANUP_01.md` | Audit | Actual structure cleanup. | User-reported committed | Repo | Yes | Key proof of structure cleanup. | FACT |
| ARTIFACT-04 | `FULL_GATE_LEGACY_TEST_ROUTE_01.md` | Audit | Routed stale full-gate tests. | User-reported committed | Repo | Yes | Important proof-gate improvement. | FACT |
| ARTIFACT-05 | `domino_framework_boundary.md` | Architecture doc | Defines framework without root. | User-reported committed | Repo | Yes | Core decision artifact. | FACT |
| ARTIFACT-06 | Large Codex/AIDE prompts | Prompts | Execute cleanup and governance tasks. | Many generated in chat | This chat | Yes | Useful prompt templates. | FACT |
| ARTIFACT-07 | Current preservation package | Report package | Preserve this chat. | Created now | This response | Yes | See file links. | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Top-level `framework/` | Rejected | Competes with contracts/public headers. | Mostly final | External SDK/root contract requires it. | WORKSTREAM-02 | FACT |
| REJECTED-02 | Top-level `modules/` | Rejected | Would become junk drawer. | Final unless separate module repo. | True module repository. | WORKSTREAM-06 | FACT |
| REJECTED-03 | Product paths like `apps/client/rendered/raylib` | Rejected | Provider choice belongs in profiles. | Final | Temporary proof boot only. | WORKSTREAM-04 | FACT |
| REJECTED-04 | Raylib as engine architecture | Rejected | Vendor lock-in. | Final | None; raylib remains provider. | WORKSTREAM-04 | FACT |
| REJECTED-05 | C89/C++98 as mainline | Superseded | Too restrictive for current target. | Tentative on platform verification | Retro/research lane. | WORKSTREAM-03 | FACT |
| REJECTED-06 | Separate UI systems for CLI/TUI/rendered/native | Rejected | Duplicates behavior. | Final | None; projections only. | WORKSTREAM-05 | FACT |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Future assistant restarts broad structure churn. | Lost time/regression. | Medium | High | Use targeted tasks only; check validators. | WORKSTREAM-01 | INFERENCE |
| RISK-02 | PASS_WITH_WARNINGS treated as full green. | Premature feature/release work. | Medium | High | Preserve readiness labels. | WORKSTREAM-07 | FACT |
| RISK-03 | Third-party types leak into contracts/game/saves. | Vendor lock-in. | Medium | High | Forbidden include/type validators. | WORKSTREAM-04 | FACT |
| RISK-04 | Workbench calls private tools directly. | UI becomes authority. | Medium | High | Command/view/action contracts. | WORKSTREAM-06 | FACT |
| RISK-05 | Mixed structure reports mislead agents. | Chasing stale paths. | High historically | Medium | Structure report integrity validator. | WORKSTREAM-01 | FACT |
| RISK-06 | Full CTest remains unclassified. | Hidden release blockers. | Medium | High | Full-gate audit ledger. | WORKSTREAM-07 | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Latest live repo status after last commit. | User reports may be stale. | Git status / latest audit. | P0 | All | FACT |
| VERIFY-02 | Full CTest result. | Full release readiness. | CTest output ledger. | P0 | WORKSTREAM-07 | FACT |
| VERIFY-03 | Third-party versions/support floors. | External facts change. | Official raylib/SDL/Lua docs. | P1 | WORKSTREAM-04 | VERIFY |
| VERIFY-04 | Provider profile path convention. | Avoid path churn. | Current contracts/docs. | P1 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-05 | AIDE state classification. | Prevent local/generated contamination. | Inspect `.aide` dirs. | P1 | WORKSTREAM-08 | FACT |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | Initial directory-layout debate | Need multiple layouts but one virtual-root/projection model. | Prevent install/package/source confusion. | Background doctrine. | High |
| 2 | User backlash against `src`/root sprawl | No `src/source`, no new roots. | Core constraint. | Still active. | High |
| 3 | Canonical root model established | Closed source root set. | End root chaos. | Current basis. | High |
| 4 | Cleanup prompts generated/executed | Runtime/game/schema/content/tools/docs/tests moved. | Practical convergence. | Historical/audit context. | High |
| 5 | Public surface/API/ABI phase | Need stable contract governance. | Reuse/future-proofing. | Active. | High |
| 6 | C17/C++17 baseline | Mainline implementation modernized. | Language policy. | Active, verify toolchains. | Medium |
| 7 | Module/workbench vocabulary split | Component/service/provider/pack/module/workspace/app terms. | Prevent junk drawers. | Active. | High |
| 8 | Presentation spine | UI modes become projections. | Reusable Workbench/client/UI. | Active. | High |
| 9 | Provider/raylib/SDL/Lua model | Third-party as providers. | Fast progress + replaceability. | Active. | High |
| 10 | Framework boundary | No `framework/` root. | Prevent root sprawl. | Active. | High |
| 11 | Full-gate legacy routing | Retired path tests updated. | Cleaner proof signal. | Recent status. | High |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Repo structure | Closed root model, no src/source. | DECISION-01, DECISION-02 | Requirement | High | Core canon. |
| Framework architecture | Domino framework via contracts/public headers. | DECISION-03, DECISION-04 | Requirement | High | Avoid top-level framework. |
| Provider architecture | Service-first providers and profiles. | DECISION-06 | Requirement | High | Raylib/SDL/Lua policy. |
| Workbench architecture | Workbench as projection/operator. | DECISION-07, DECISION-08 | Requirement/context | High | Guides first UI work. |
| ABI/language policy | C17/C++17 + C-compatible ABI. | DECISION-05 | Requirement after verification | Medium | External facts need verification. |
| Testing/proof gates | Fast strict vs full gate. | TASK-01, TASK-05 | Requirement/open issue | High | Full CTest debt remains. |
