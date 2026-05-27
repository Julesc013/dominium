# Registers

## 16. Compact Human Summary

This chat was about turning Dominium into a durable, deterministic, modular simulation platform rather than a one-off game. It began around worldgen and realism, asking whether worlds should be procedurally generated and then simulated for years to billions of years. The answer became a larger doctrine: truth can be deterministic and total, while materialization can be lazy and sparse. Instead of simulating everything everywhere, the system can use seeds, laws, processes, checkpoints, capsules, and observation-driven refinement to create aged worlds, histories, terrain, climates, biomes, species, and civilizations without brute-force global simulation.

That idea expanded to the whole project. The user wanted players to be able to make arbitrary things: tools, screws, pottery wheels, kilns, rails, vehicles, switches, computers, factories, infrastructure, and cities. The answer was not to hardcode every object or force players to declare everything. Instead, Dominium should use deep primitives: materials, geometry, fields, constraints, processes, affordances, recognizers, formalizations, blueprints, standards, and production routes. Useful structures can be recognized, formalized, optimized, and later mass-produced.

The project’s architecture then became the main focus. Dominium should be a deterministic simulation operating environment. Domino is the reusable substrate; Dominium is the game/product family; Workbench is the production and validation environment; AIDE is the repo/control-plane harness; Codex is a bounded patch executor; contracts are law; diagnostics, replay, tests, and evidence are proof. The core laws are: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth.

Repo planning converged on a stable root structure: `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`. The project moved through Foundation Lock, component matrix cleanup, Workbench validation, service conformance, document/patch/transaction law, project graph law, composition resolver law, doctrine recovery, command-result-view proof, and package mount proof. The current status is `PASS_WITH_WARNINGS`, not warning-free. Fast strict passes. Dependency-direction strict has zero violations but known warnings. Full CTest remains T4/full-gate debt. Broad feature work remains blocked.

Workbench was another major topic. The old idea of a UI Editor / Tool Editor was superseded. Workbench should eventually become the visual and agentic production environment for building Dominium itself: views, layouts, themes, widgets, workspaces, packs, modules, release evidence, and AIDE/Codex work units. But Workbench must not become a separate authority. It should edit documents, emit patches, run validation, preview outputs, and package artifacts. Runtime executes; contracts constrain; content supplies; apps consume; tests prove.

The presentation architecture also converged. CLI, text/TUI, rendered GUI, native GUI, and headless are not separate semantic systems. They are projections of the same command/result/refusal/document/view/action spine. This prevents drift and allows client, server, launcher, setup, Workbench, CI, and future tools to reuse the same semantics.

At the end, the user wanted to run many prompts in parallel on `dev`. The answer was yes, but only after the next product-spine slices and a product-spine review. The doctrine is: development is non-blocking, promotion is evidence-blocked. Agents should not all mutate shared `dev`; each prompt should run on its own task branch/worktree. AIDE integrates into `dev`, checkpoint branches prove waves, and `main` receives only evidence-backed promotions.

The immediate next steps are to verify live repo state, reconcile the queue if stale, run `REPLAY-PROOF-SLICE-01` if missing, run `BAREBONES-CLIENT-SHELL-01` if missing, then run `PRODUCT-SPINE-REVIEW-01`. After that, limited parallel development can begin with `AIDE-WORKFLOW-LAW-01`, `PRESENTATION-CONTRACT-01`, and `POINTER-WIDTH-SERIALIZATION-AUDIT-01`. Larger parallel waves should wait until AIDE work-unit schema, dev/main policy, and checkpoint loop are defined.

---


## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Domino/Dominium Platform Architecture | Establish deterministic, modular platform identity | Converged doctrine | Reusable substrate + game family + evidence-backed runtime | Active | P0 | High | FACT |
| WORKSTREAM-02 | Repo Foundation and Governance | Keep repo governable and validated | Foundation PASS_WITH_WARNINGS | Stable foundation with classified warnings | Active | P0 | High | FACT |
| WORKSTREAM-03 | Product Spine | Build narrow usable command/package/replay/client spine | Package mount done; replay/barebones pending/uncertain | Package mount + replay proof + barebones client + review | Active | P0 | High | FACT |
| WORKSTREAM-04 | AIDE Task OS | Enable parallel non-blocking development | Conceptual, partial AIDE exists | Scheduler/ledger/repair/checkpoint/promotion system | Planned | P1 | High | FACT |
| WORKSTREAM-05 | Workbench | Production/validation/editing environment | Validation slice only | Self-hosting modular authoring environment | Planned/partial | P1 | High | FACT |
| WORKSTREAM-06 | Presentation Architecture | Unify CLI/text/rendered/native/headless | Command-result-view slice exists | Projection conformance and presentation contracts | Planned/partial | P1 | High | FACT |
| WORKSTREAM-07 | Package/Composition | Compose apps from packs/modules/providers | Composition law + package mount fixture | Runtime-safe package/profile/provider composition | Active/planned | P1 | High | FACT |
| WORKSTREAM-08 | Replay/Proof | Prove deterministic command replay | Prompt generated, execution uncertain | Replay/proof slice and later full replay systems | Pending | P0 | Medium | UNCERTAIN |
| WORKSTREAM-09 | Barebones Product Floors | Products run without optional content | Client prompt generated, execution uncertain | No-content help/status/diag floor | Pending | P0 | Medium | UNCERTAIN |
| WORKSTREAM-10 | Worldgen/Simulation Domains | Realistic long-term simulation domains | Future doctrine only | Domain constitutions and slices | Deferred | P2 | High | FACT |
| WORKSTREAM-11 | Renderer/Platform | Define and later implement render/platform providers | Matrix cleaned | Software + OpenGL + D3D11 etc. providers | Deferred implementation | P2 | High | FACT |
| WORKSTREAM-12 | Spec Book Aggregation | Merge old-chat reports into master project spec | This report created | Master Project Spec Book | Planned | P1 | High | FACT |


## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Dominium is a deterministic simulation platform | Accepted | Repeated user acceptance | Needed for full ambition | Contracts/evidence centered architecture | WORKSTREAM-01 | High | FACT |
| DECISION-02 | Domino is reusable substrate | Accepted | Chat doctrine | Enables other games/projects | Split engine/runtime/contracts from game/content | WORKSTREAM-01 | High | FACT |
| DECISION-03 | Workbench is not authority | Accepted | Repeated corrections | Prevents editor truth drift | Workbench must use commands/services | WORKSTREAM-05 | High | FACT |
| DECISION-04 | AIDE should become repo task OS | Accepted | User explicitly agreed | Needed for parallel agents | Workflow law and work-unit schema needed | WORKSTREAM-04 | High | FACT |
| DECISION-05 | Development non-blocking, promotion evidence-blocked | Accepted | User + Codex agreement | Allows dev progress but protects main | dev/task/checkpoint/main policy | WORKSTREAM-04 | High | FACT |
| DECISION-06 | Task branches/worktrees per prompt | Accepted | Final correction | Avoid shared dev chaos | Future parallel prompt model | WORKSTREAM-04 | High | FACT |
| DECISION-07 | Full CTest is T4 debt | Accepted | Repo status | Keeps current work unblocked | Must remain visible | WORKSTREAM-02 | High | FACT |
| DECISION-08 | Package mount slice is fixture-level only | Accepted | Package audit | Avoid false runtime claims | Next replay proof | WORKSTREAM-07 | High | FACT |
| DECISION-09 | C17/C++17 target baseline | Accepted as doctrine | User/Codex plan | Modern code while keeping ABI | Verify live CMake | WORKSTREAM-01 | Medium | FACT + VERIFY |
| DECISION-10 | CLI/text/rendered/native/headless are projections | Accepted | UI architecture discussion | Avoid duplicate UI systems | Presentation contract needed | WORKSTREAM-06 | High | FACT |
| DECISION-11 | Use closed source-root model | Accepted | Repo convergence | Avoid root sprawl | No new top roots | WORKSTREAM-02 | High | FACT |
| DECISION-12 | Vector2D is canvas/drawing, not renderer | Accepted | Matrix cleanup | Avoid backend confusion | Renderer matrix updated | WORKSTREAM-11 | High | FACT |


## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Verify current repo state | P0 | U0 | Next chat | None | Repo access | Accurate next task | Inspect queue/audits/commits | All | FACT |
| TASK-02 | QUEUE-RECONCILE-01 | P0 if queue stale | U0 | Codex/AIDE | PACKAGE-MOUNT done | Queue and package audit | Queue points replay | Run/generate if stale | WORKSTREAM-03 | FACT |
| TASK-03 | REPLAY-PROOF-SLICE-01 | P0 | U0 | Codex/AIDE | Package mount | Prompt generated | Command replay/proof fixture | Run if missing | WORKSTREAM-08 | FACT |
| TASK-04 | BAREBONES-CLIENT-SHELL-01 | P0 | U1 | Codex/AIDE | Replay proof preferred | Prompt generated | Client no-content floor | Run if missing | WORKSTREAM-09 | FACT |
| TASK-05 | PRODUCT-SPINE-REVIEW-01 | P0 | U1 | Codex/AIDE | Replay + barebones | New prompt needed | Decide limited parallel readiness | Generate after prior tasks | WORKSTREAM-03 | FACT |
| TASK-06 | AIDE-WORKFLOW-LAW-01 | P1 | U1 | Codex/AIDE | Product spine review | Plan | Branch/lifecycle/blocker law | Generate after review | WORKSTREAM-04 | FACT |
| TASK-07 | AIDE-WORKUNIT-SCHEMA-01 | P1 | U1 | Codex/AIDE | AIDE workflow law | Schemas | WorkUnit/task attempt schemas | Later | WORKSTREAM-04 | FACT |
| TASK-08 | AIDE-DEV-MAIN-POLICY-01 | P1 | U1 | Codex/AIDE | AIDE workflow law | Branch doctrine | dev/main/checkpoint policy | Later | WORKSTREAM-04 | FACT |
| TASK-09 | PRESENTATION-CONTRACT-01 | P1 | U1 | Codex/AIDE | Command/result/view proof | Existing view/action docs | Presentation/action contracts | Parallel candidate | WORKSTREAM-06 | FACT |
| TASK-10 | POINTER-WIDTH-SERIALIZATION-AUDIT-01 | P1 | U2 | Codex/AIDE | Arch policy | Code/audit access | Serialization audit | Parallel candidate | WORKSTREAM-01 | FACT |
| TASK-11 | PROJECTION-CONFORMANCE-01 | P1 | U2 | Codex/AIDE | Presentation contract | Fixtures | Projection conformance tests | Later | WORKSTREAM-06 | FACT |
| TASK-12 | ACCESSIBILITY-CONTRACT-01 | P2 | U2 | Codex/AIDE | Presentation contract | View/action model | Accessibility law | Later | WORKSTREAM-06 | FACT |
| TASK-13 | TEXT-LOCALIZATION-CONTRACT-01 | P2 | U2 | Codex/AIDE | Presentation contract | Text/UI docs | Text catalog law | Later | WORKSTREAM-06 | FACT |
| TASK-14 | WORKBENCH-SHELL-01 | P2 | U2 | Codex/AIDE | Product/presentation spine | Workbench descriptors | Minimal shell | Later | WORKSTREAM-05 | FACT |
| TASK-15 | DOMAIN-CONSTITUTION-WAVE-01 | P2 | U3 | Codex/AIDE | Product/AIDE/presentation layers | Doctrine matrix | Domain constitutions | Much later | WORKSTREAM-10 | FACT |


## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Broad feature work blocked | Technical/process | Hard | Queue/foundation state | Only narrow slices | Refactor spiral | High | FACT |
| CONSTRAINT-02 | Full CTest not green | Testing | Hard fact | Repo status | Do not claim release-ready | Release risk | High | FACT |
| CONSTRAINT-03 | Runtime package/provider/module not implemented | Technical | Hard fact | Audits | Avoid runtime claims | False support | High | FACT |
| CONSTRAINT-04 | Workbench shell not implemented | Technical | Hard fact | Audits | Use projections/fixtures | False UI claims | High | FACT |
| CONSTRAINT-05 | Public ABI C-compatible | Architecture | Hard | Doctrine | No C++ ABI leakage | Portability break | High | FACT |
| CONSTRAINT-06 | Paths are not identity | Architecture | Hard | Doctrine | Use stable IDs | Incompatibility | High | FACT |
| CONSTRAINT-07 | Runtime must not depend on tools | Dependency | Hard | Ownership law | Tools repo-only | Product fragility | High | FACT |
| CONSTRAINT-08 | Prompts in one code block | UX/process | Hard preference | User explicit | Easy copy/paste | User friction | High | FACT |
| CONSTRAINT-09 | No destructive git cleanup in prompts | Safety | Hard | Prompt design | Protect concurrent work | Data loss | High | FACT |
| CONSTRAINT-10 | Evidence-backed promotion | Process | Hard | AIDE doctrine | main protected | False completion | High | FACT |
| CONSTRAINT-11 | Dev non-blocking but structured | Process | Soft-to-hard future | User/Codex | Blockers become tasks | Chaotic dev | High | FACT |
| CONSTRAINT-12 | Do not invent facts | Epistemic | Hard | User explicit | Label uncertainty | Trust loss | High | FACT |


## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, audit-ready answers | Communication | Explicit | Strong | Use structured evidence | Frustration | FACT |
| PREF-02 | Distinguish facts/inferences/uncertainty | Epistemic | Explicit | Strong | Label claims | Loss of trust | FACT |
| PREF-03 | Preserve detail, do not over-compress | Output | Explicit | Strong | Long reports acceptable | Missing context | FACT |
| PREF-04 | Generate prompts in one code block | Prompting | Explicit | Strong | Use single fenced block | Copy failure | FACT |
| PREF-05 | Challenge bad framing | Reasoning | Explicit/inferred | Strong | Correct user when needed | Bad plans | FACT |
| PREF-06 | No re-explaining settled issues | Continuity | Explicit | Strong | Use handoff | Wasted time | FACT |
| PREF-07 | Source/repo-grounded planning | Evidence | Explicit/inferred | Strong | Verify repo | Stale plan | FACT |
| PREF-08 | Proceed unless clarification materially needed | Workflow | Explicit/inferred | Medium-high | Avoid blocking questions | Slowdown | FACT |
| PREF-09 | Preserve rejected options | Continuity | Explicit | Strong | Include rejected register | Repeated work | FACT |
| PREF-10 | Prefer modular/reusable design | Architecture | Explicit | Strong | Enforce contracts/providers | Fragility | FACT |


## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Has `REPLAY-PROOF-SLICE-01` executed? | Determines next prompt | Prompt generated | Live status | Check commits/audit | P0 | WORKSTREAM-08 | UNCERTAIN |
| QUESTION-02 | Has `BAREBONES-CLIENT-SHELL-01` executed? | Determines Product Spine Review | Prompt generated | Live status | Check commits/audit | P0 | WORKSTREAM-09 | UNCERTAIN |
| QUESTION-03 | Is queue reconciled after package mount? | Avoid stale prompts | Queue may be stale | Live status | Inspect `.aide/queue/current.toml` | P0 | WORKSTREAM-03 | UNCERTAIN |
| QUESTION-04 | Is C17/C++17 fully implemented in build? | Avoid docs/build mismatch | Doctrine accepted | Live CMake status | Inspect build files | P1 | WORKSTREAM-01 | VERIFY |
| QUESTION-05 | Does origin/dev exist? | Parallel dev | Desired | Repo status | `git branch -r` | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-06 | What are current warning counts? | Promotion gates | Known categories | Exact live counts | Run validators | P1 | WORKSTREAM-02 | UNCERTAIN |
| QUESTION-07 | When to burn down full CTest? | Release readiness | T4 debt | Schedule | Plan full-gate phase | P2 | WORKSTREAM-02 | OPEN |
| QUESTION-08 | Which product should follow client shell? | Roadmap | Launcher/setup/server later | Order | Product Spine Review | P2 | WORKSTREAM-03 | OPEN |


## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Pasted text.txt | Uploaded file | Preservation task instruction | Loaded | User upload | Yes | Cite if referencing uploaded instruction | FACT |
| ARTIFACT-02 | `FOUNDATION_LOCK.md` | Repo doc | Foundation status | Existing | Repo | Yes | Verify live | FACT |
| ARTIFACT-03 | `.aide/queue/current.toml` | Repo status | Current queue | Existing | Repo | Yes | Must inspect first | FACT |
| ARTIFACT-04 | `PACKAGE_MOUNT_SLICE_01.md` | Audit | Package mount slice result | Existing | Repo | Yes | Said PASS_WITH_WARNINGS | FACT |
| ARTIFACT-05 | `QUEUE-RECONCILE-01` prompt | Prompt | Update queue after package mount | Generated | This chat | Yes | May need to run | FACT |
| ARTIFACT-06 | `REPLAY-PROOF-SLICE-01` prompt | Prompt | Command-level replay proof | Generated | This chat | Yes | Next if missing | FACT |
| ARTIFACT-07 | `BAREBONES-CLIENT-SHELL-01` prompt | Prompt | Minimal client floor | Generated | This chat | Yes | After replay | FACT |
| ARTIFACT-08 | `PRODUCT-SPINE-REVIEW-01` | Future prompt | Review product spine | Not yet generated | Planned | Yes | Generate after replay + barebones | FACT |
| ARTIFACT-09 | Workbench validation slice audit | Audit | First Workbench validation proof | Existing | Repo | Yes | No full shell | FACT |
| ARTIFACT-10 | Command-result-view slice audit | Audit | View/projection proof | Existing/expected | Repo | Yes | Verify live | FACT |
| ARTIFACT-11 | Handoff package files | Generated package | Preserve this chat | Created by this response | This task | Yes | See file links | FACT |


## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Brute-force global simulation | Rejected | Too costly | Final for global approach | Local refinement remains | WORKSTREAM-10 | FACT |
| REJECTED-02 | Hardcode all objects/machines | Rejected | Does not scale | Final as core model | Templates okay | WORKSTREAM-10 | FACT |
| REJECTED-03 | Workbench monolith | Rejected | Becomes authority/blob | Final | Shell+modules accepted | WORKSTREAM-05 | FACT |
| REJECTED-04 | Native-widget-first editor | Rejected | Not reusable with client UI | Final for first wave | Native projection later | WORKSTREAM-06 | FACT |
| REJECTED-05 | Separate UI systems | Rejected | Causes drift | Final | Projection model accepted | WORKSTREAM-06 | FACT |
| REJECTED-06 | Agents directly mutate shared dev | Rejected | Concurrency chaos | Final | Task branches accepted | WORKSTREAM-04 | FACT |
| REJECTED-07 | Build full AIDE OS before product spine | Deprioritised | Would stall progress | Tentative | Minimum AIDE layer soon | WORKSTREAM-04 | FACT |
| REJECTED-08 | Treat full CTest as current blocker | Deprioritised | Too broad now | Tentative | Release/full-gate | WORKSTREAM-02 | FACT |
| REJECTED-09 | OpenGL 1.1/D3D9 first wave | Rejected | Back-port only | Final first-wave | Research lanes later | WORKSTREAM-11 | FACT |
| REJECTED-10 | C89/C++98 active mainline | Superseded | Modern baseline accepted | Tentative until build verified | Retro lanes | WORKSTREAM-01 | FACT+VERIFY |


## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Stale AIDE queue | Wrong prompts run | Medium | High | Verify queue first | WORKSTREAM-04 | FACT |
| RISK-02 | Docs outrun code | False support claims | High | High | Capability Reality Ledger | WORKSTREAM-04 | FACT |
| RISK-03 | Broad feature work starts early | Refactor spiral | Medium | High | Preserve blockers | All | FACT |
| RISK-04 | Agents mutate dev directly | Merge chaos | Medium | High | Task branches/worktrees | WORKSTREAM-04 | FACT |
| RISK-05 | Full CTest ignored forever | Release weakness | Medium | Medium-high | FULL-GATE-DEBT-01 | WORKSTREAM-02 | FACT |
| RISK-06 | Workbench becomes authority | Architecture drift | Medium | High | Command/service boundaries | WORKSTREAM-05 | FACT |
| RISK-07 | Runtime depends on tools | Product fragility | Medium | High | Dependency-direction law | WORKSTREAM-02 | FACT |
| RISK-08 | UI projections diverge | Duplicated behavior | Medium | High | Presentation contract | WORKSTREAM-06 | FACT |
| RISK-09 | C17/C++17 docs/build mismatch | Build confusion | Medium | Medium | Verify CMake | WORKSTREAM-01 | VERIFY |
| RISK-10 | New chat restarts doctrine | Wasted time | Medium | Medium | Use handoff | All | FACT |


## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current `.aide/queue/current.toml` | Determines next task | Repo file | P0 | WORKSTREAM-03 | VERIFY |
| VERIFY-02 | Recent commits | Check which prompts landed | `git log` | P0 | All | VERIFY |
| VERIFY-03 | `REPLAY_PROOF_SLICE_01.md` | Determine replay status | Repo audit | P0 | WORKSTREAM-08 | VERIFY |
| VERIFY-04 | `BAREBONES_CLIENT_SHELL_01.md` | Determine barebones status | Repo audit | P0 | WORKSTREAM-09 | VERIFY |
| VERIFY-05 | CMake language standard | Confirm C17/C++17 | CMake files | P1 | WORKSTREAM-01 | VERIFY |
| VERIFY-06 | `origin/dev` existence | Parallel plan | Git branches | P1 | WORKSTREAM-04 | VERIFY |
| VERIFY-07 | Warning counts | Avoid false clean claim | Validator output | P1 | WORKSTREAM-02 | VERIFY |
| VERIFY-08 | Full CTest status | Release readiness | CI/local test | P2 | WORKSTREAM-02 | VERIFY |
| VERIFY-09 | Product app descriptor state | Barebones client | contracts/apps | P1 | WORKSTREAM-09 | VERIFY |
| VERIFY-10 | Package runtime absence | Avoid false claims | repo/audits/code | P1 | WORKSTREAM-07 | VERIFY |


## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | Worldgen handoff | Continue after architecture freeze | Preserves invariants | Background doctrine | High |
| 2 | Aged worlds question | Lazy deterministic history preferred | Avoid brute force | Domain future | High |
| 3 | Epistemics/diegetics | Became optimization doctrine | Sparse refinement | Platform doctrine | High |
| 4 | Player construction | Deep primitives identified | Arbitrary invention | Future domain work | High |
| 5 | Civilization macro/micro | Collapse/expand model | Scales societies | Future domain work | High |
| 6 | Universal reality framework | Domain contracts proposed | Avoid feature creep | Superseded by repo-grounded tasks | Medium |
| 7 | Repo CONVERGE | Layout and authority cleanup | Governed repo | Foundation context | High |
| 8 | AIDE introduced | Control plane installed | Refactor management | Still active | High |
| 9 | Foundation Lock | Scaffolds/gates built | Enables narrow slices | Current base | High |
| 10 | Language baseline | C17/C++17 doctrine | Modernize | Verify build | Medium |
| 11 | Workbench direction | Production environment | Replaces UI editor | Active future | High |
| 12 | Presentation model | Projection architecture | Avoid UI drift | Future prompt | High |
| 13 | Prompt phase | Generated seven prompts | Built contract layers | Mostly complete | High |
| 14 | Package mount | Fixture proof landed | Product spine progress | Done | High |
| 15 | AIDE dev/main | Non-blocking dev/evidence main | Parallel future | Next phase | High |
| 16 | Preservation request | Full handoff required | Retire chat | This document | High |
