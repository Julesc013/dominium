# COMPLETE CHAT PRESERVATION REPORT — Dominium Architecture, Workbench, AIDE, and Product-Spine Planning

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium Architecture, Workbench, AIDE, and Product-Spine Planning |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial, with high contextual coverage |
| Previously generated files available? | No previously generated downloadable handoff files were visible; this task creates new files. |
| Uploaded files or artifacts present? | Yes. The uploaded `Pasted text.txt` contains the preservation/export instructions for this task. |
| Contains future plans? | Yes |
| Contains decisions? | Yes |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium |
| Extraction confidence | 4 / 5 |
| Safe for later aggregation? | Yes, with caveats |
| Main limitations | The visible transcript contains skipped-message markers; not every earlier raw turn is available. Several repo states were reported by the user/Codex and/or queried during this chat, but the live repo can advance after this report. This preservation therefore records the conversation state and flags live repo verification as required. |

Plain-language limitations:

This report is not a perfect raw transcript substitute. It reconstructs the working state from the visible conversation, user-pasted transcripts, assistant outputs, repo-state checks performed in this chat, and the final uploaded preservation instruction. Some prior messages were collapsed as “Skipped messages” in the visible conversation. Therefore, this report should be treated as a high-fidelity reconstruction, not a legal archive of every token. The next chat should always verify live repo state before acting on task order or claiming a prompt has been executed.

The largest uncertainty is not the conceptual architecture; that has converged. The largest uncertainty is live execution state: whether prompts generated near the end of the chat have already been run locally, committed, or pushed. The next chat should first inspect `.aide/queue/current.toml`, recent commits, and relevant audit files.

## 1. One-Page Orientation

This chat was primarily about moving Dominium from a large, ambitious but risk-prone game/simulation project into a disciplined, contract-governed, deterministic simulation platform with a reusable engine substrate, a production Workbench, and an AIDE-driven development workflow. The user’s underlying concern was that Dominium should not become a one-off indie project with ad hoc code, drifting folders, duplicated UI systems, unverified docs, and fragile feature work. The conversation repeatedly returned to the same long-term aim: make all code, data, systems, and development workflows portable, modular, extensible, deterministic where needed, replaceable, testable, and compatible with future refactors or even total rewrites.

The main architectural identity that emerged is:

```text
Domino    = reusable deterministic substrate
Dominium  = game/product family on Domino
Workbench = production, validation, editing, inspection, packaging, and evidence environment
AIDE      = repo/control-plane harness
Codex     = bounded patch executor
Contracts = law
Diagnostics / tests / replay / evidence = proof
```

A major shift was that the discussion stopped treating “the game,” “the UI,” “the Workbench,” or “the folders” as the center. Instead, the center became contracts, commands, services, providers, packs, modules, artifacts, capabilities, diagnostics, tests, replay, and evidence. The system should be able to replace private implementations and even directories while stable semantic IDs, public contracts, conformance tests, and artifact identities remain intact.

The user also wanted to understand how to build extremely realistic worlds without brute-force simulation. Earlier in the conversation, the thread moved from “procedurally generate a world and simulate billions of years” to “truth is total, materialization is sparse, history can be lazily and deterministically evaluated, and observation/causality controls refinement.” That thinking later generalized into the whole project: sparse materialization, macro/micro collapse, epistemic/diegetic gating, process-only mutation, representation ladders, and formalization chains should apply across worldgen, fabrication, ecology, civilization, UI, tools, and agentic development.

A second major stream focused on player creation and deep primitives. Rather than hardcoding every object as a primitive, the conversation converged on materials, geometry, fields, constraints, processes, affordances, recognizers, formalizations, blueprints, standards, and production routes. This is how players might eventually make things like tools, wheels, machines, vehicles, rails, computers, factories, infrastructure, and civilizations without the engine requiring every object to be hand-coded as a special case.

A third stream focused on Workbench. The old idea of a UI Editor / Tool Editor was superseded by the Dominium Workbench Platform: a modular, command-driven, visual and agentic production environment for building Dominium itself. Workbench should eventually help create, validate, preview, package, and prove code, data, contracts, packs, modules, UI/HUD documents, themes, renderer tests, release artifacts, and AIDE/Codex work units. But Workbench must not become a monolith or authority. It edits documents and dispatches registered commands; runtime executes services; contracts define legality; content packages authored payloads; tools validate.

A fourth stream focused on AIDE and development workflow. The final doctrine is: development should be non-blocking, but promotion should be evidence-blocked. The user wants to run many prompts in parallel across dev branches, machines, and Codex sessions. The agreed architecture is task branches/worktrees per prompt, AIDE-managed blocker classification and repair queues, `origin/dev` as an integration branch, checkpoint branches for proof, and `origin/main` as promoted truth. The new chat must not let agents directly mutate shared `dev` without isolation.

At the end of the conversation, the immediate repo plan was narrow and sequenced. Foundation Lock is `PASS_WITH_WARNINGS`, broad feature work remains blocked, `PACKAGE-MOUNT-SLICE-01` is complete, and the next intended product-spine work is `REPLAY-PROOF-SLICE-01`, then `BAREBONES-CLIENT-SHELL-01`, then `PRODUCT-SPINE-REVIEW-01`. After that, the project can begin limited parallel development, especially AIDE workflow law and presentation contracts.

## 2. The Story of the Conversation

### 2.1 Starting point: preserving architecture while expanding worldgen

The conversation began from a handoff prompt for continuing Dominium worldgen and life systems after a prior architecture freeze. The user established that the project already had a Constitutional Architecture with pinned semantic contracts, determinism discipline, stability tags, CAP-NEG, PACK-COMPAT, LIB/APPSHELL/TIME-ANCHOR concepts, and frozen v0.0.0-mock architecture. The new development focus was procedural worldgen and domain realism: erosion, hydrology, ecology, evolution, speciation, biomes, climate feedback loops, geology, resource formation, and long time-scale planetary transformations.

The user asked whether realistic worlds could be generated by simulating years to billions of years, and whether that conflicts with sparse, on-the-fly generation. The resulting decision was that brute-force global simulation is not required or desirable. Instead, Dominium should use deterministic lazy historical evaluation: total truth defined by seed/laws/processes, but materialized only where observation, interaction, or causality requires it.

### 2.2 Generalizing worldgen into a project-wide doctrine

The user then asked whether epistemics and diegetics could further optimize what is simulated, loaded, or rendered. This expanded the idea beyond worldgen. The conversation converged on a general pattern: the simulation’s authoritative truth can be total and deterministic, while representation, materialization, detail, and presentation can vary based on observation, capability, epistemic state, and causal need.

This logic was then applied to terrain modification, structures, intelligent life, machines, civilizations, and player-authored worlds. The assistant repeatedly framed Dominium as a multi-representation reality substrate rather than a feature pile.

### 2.3 Player construction, machines, and civilization realism

A large portion of the chat explored how a player might create things from first principles: screws, planks, pottery wheels, kilns, vehicles, switches, wires, rails, solenoids, CPUs, factories, cities, and more. The problem was how the game knows when arbitrary shapes become a vehicle, a pipe, a rail, a chair, a table, or a machine.

The solution that emerged was not to hardcode every object and not to rely purely on player declarations. Instead, use deep primitives: materials, geometry, constraints, fields, processes, affordances, recognizers, formalizations, and design knowledge. The system can detect stable useful patterns, classify affordances, and let players formalize them into blueprints, standards, production routes, and mass-manufacturable artifacts.

This same approach supports distant civilizations: macro truth for unvisited places, expansion into detail when observed, and collapse back to capsules while preserving observed facts and causal continuity.

### 2.4 Repo convergence and Foundation Lock

A major later phase shifted from pure architecture into repo-specific planning. The repo had undergone extensive CONVERGE and POST-CONVERGE work: layout contracts, root allowlists, stale doc supersession, root recycling, AIDE control plane, build proof recovery, product boot proof, package projection, internal release baseline, move-family cleanup, Foundation scaffolding, C17/C++17 language-policy direction, public surface registry, ABI policy, dependency direction law, command/diagnostic/artifact/provider/module/replacement/version/trust/portability scaffolds, and fast strict gates.

The live repo state changed repeatedly during the conversation. Earlier, Foundation Lock was blocked by dependency-direction violations. Later, Foundation Lock closed as `PASS_WITH_WARNINGS`. The user and assistant repeatedly emphasized that `PASS_WITH_WARNINGS` is not “clean/no warnings”; full CTest remains T4/full-gate debt, and broad feature work remains blocked.

### 2.5 Workbench and Interface Operating Layer

The old “UI Editor / Tool Editor” plan was superseded by the Dominium Workbench Platform. Workbench should become the visual and agentic production environment for building Dominium: code, data, contracts, packs, modules, UI/HUD layouts, renderer tests, sounds/assets, tests, releases, and AIDE work units.

The conversation refined this further: the real platform is not Workbench itself, but the reusable Interface Operating Layer underneath it. CLI, text/TUI, rendered GUI, native GUI, and headless modes should be projections over the same command/result/refusal/document/view/action spine. Workbench is the richest consumer and authoring environment for that spine.

### 2.6 Prompt-generation and task sequencing

In the later chat, the user requested a series of Codex/AIDE prompts. The assistant generated prompts for:

```text
MATRIX-CLEANUP-00
WORKBENCH-VALIDATION-SLICE-01
SERVICE-CONFORMANCE-LAW-01
DOCUMENT-PATCH-TRANSACTION-RUNTIME-01
PROJECT-GRAPH-SERVICE-01
COMPOSITION-RESOLVER-LAW-01
DOMINIUM-DOCTRINE-RECOVERY-MATRIX-01
COMMAND-RESULT-VIEW-SLICE-01
PHASE-REVIEW-02
QUEUE-RECONCILE-01
REPLAY-PROOF-SLICE-01
BAREBONES-CLIENT-SHELL-01
```

The user noted that earlier prompts were hard to copy because they were not always contained in one code block, and that prompts should better handle dirty worktrees and concurrent tasks. From then on, generated prompts included detailed dirty worktree handling, allowed/forbidden paths, non-goals, validation, blocker classification, and commit/final-response formats.

### 2.7 Parallel development and AIDE OS

Near the end, the user wanted to run prompts in parallel on a permanent `origin/dev` and `local/dev`, then checkpoint/merge to `main`. The conversation converged on the AIDE OS model: agents should not mutate shared dev directly; each prompt should run in a task branch/worktree; AIDE integrates to dev; checkpoint branches prove waves; main receives only evidence-backed promotions.

The final recommended sequence was: finish replay proof and barebones client, run product spine review, then begin limited parallel dev. Larger parallel waves should wait until minimum AIDE workflow law exists.

### 2.8 Chat retirement / preservation

The user then requested this full preservation package so a new chat could continue without re-explaining everything. This final handoff is itself part of the preservation output.

## 3. Main Topics Discussed

### Topic 1 — Deterministic Sparse Worldgen and Aged Worlds

The user wanted worlds that feel geologically, biologically, historically, and civilizationally real. The first idea considered was generating a world and simulating it for years to billions of years. The refined conclusion was that naive full simulation is incompatible with scale and unnecessary. Instead, Dominium should define a total deterministic truth and materialize/evaluate detail lazily.

Key conclusions:

```text
Truth is total.
Materialization is conditional.
History can be lazily evaluated.
Observation and causality drive refinement.
Global brute-force simulation is avoided.
```

Remaining uncertainty: exact implementation of erosion/ecology/evolution proxies remains future domain work.

### Topic 2 — Epistemics and Diegetics as Optimization Doctrine

The conversation treated epistemics and diegetics as more than flavor. They determine what must be simulated, loaded, rendered, or refined. If a player has not observed something, it can remain summarized so long as future expansion is consistent with seed, law, and causal history.

This supports:

```text
unknown/unobserved detail summarized
measured domains refined
instrumentation affects knowledge
observation anchors prevent continuity breaks
```

### Topic 3 — Deep Primitives for Player Creation

The user asked how players could make arbitrary things: axes, tables, screws, kilns, pottery wheels, springs, machines, switches, wires, vehicles, rails, computers, factories, and more.

The concluded primitive stack:

```text
materials
geometry
fields
constraints
processes
affordances
recognizers
formalizations
measurements
tolerances
standards
blueprints
production procedures
institutions/knowledge
```

Rejected: hardcoding all objects as primary truth or requiring all player intent through non-diegetic declarations.

### Topic 4 — Civilization Macro/Micro Expansion

Distant societies should not require continuous detailed simulation. They can exist as macro truth: population distributions, infrastructure, culture, industry, governance, institutions, logistics corridors, and knowledge propagation. When observed, they expand into buildings, agents, institutions, and local histories. They can collapse back while preserving observed facts.

### Topic 5 — Repo Architecture and Foundation Lock

The chat discussed multiple repo states over time: CONVERGE, POST-CONVERGE, AIDE, root cleanup, Foundation Lock, public surface registry, ABI law, dependency-direction, language baseline, component matrix cleanup, package mount, and command-result-view.

Current expected state:

```text
Foundation Lock = PASS_WITH_WARNINGS
fast strict = PASS
dependency direction = 0 violations, known warnings
full CTest = T4/full-gate debt
broad feature work = blocked
```

### Topic 6 — Workbench Platform

Workbench evolved from “UI editor/tool editor” into “visual and agentic production environment.” It should eventually author views, layouts, themes, widgets, TUI panels, rendered screens, HUDs, setup flows, launcher pages, admin dashboards, packs, modules, release evidence, and AIDE/Codex work units.

Key correction: Workbench should host workflows but not own truth.

### Topic 7 — Interface / Presentation Architecture

The UI architecture converged on:

```text
command/result/refusal/document spine
→ view model
→ projection adapter
→ CLI / text / rendered / native / headless
```

CLI, text/TUI, rendered GUI, native GUI, and headless are projections, not separate semantic systems.

### Topic 8 — AIDE Development Operating System

AIDE should evolve from prompt generator into task operating system:

```text
Scheduler
Ledger
Repair Engine
Checkpoint Engine
Promotion Engine
```

Core rule:

```text
Development is non-blocking.
Promotion is evidence-blocked.
```

### Topic 9 — Prompt Design

The user needed copyable prompts in a single code block. Future prompts should include:

```text
status
context
goal
allowed paths
forbidden paths
dirty worktree handling
task details
non-goals
validation
expected result
block conditions
commit format
final response format
```

### Topic 10 — Parallel Dev and Branching

Agents should not all mutate `dev` directly. Use:

```text
task/<task-id>
repair/<task-id>
origin/dev
checkpoint/<wave-id>
origin/main
```

### Topic 11 — Replay Proof and Barebones Client

`PACKAGE-MOUNT-SLICE-01` completed; next product-spine tasks are replay proof and barebones client shell.

### Topic 12 — Future Domain Systems

Worldgen, ecology, evolution, fabrication, economy, institutions, cities, conflict, and offworld systems remain future domain constitution work, not immediate implementation.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

1. Build realistic procedural worlds without brute-force global simulation.
2. Make Dominium modular, extensible, deterministic, portable, and future-proof.
3. Avoid repeating refactor spirals.
4. Create a Workbench that helps build the project.
5. Use AIDE/Codex effectively for repo development.
6. Generate copyable prompts for each next task.
7. Transition to parallel dev safely.
8. Preserve this chat fully for a new chat.

### 4.2 Inferred Goals

1. Preserve project momentum without losing accumulated reasoning.
2. Reduce user’s cognitive load by making AIDE manage blockers and tasks.
3. Ensure future assistants do not restart settled debates.
4. Turn a highly ambitious game idea into a disciplined platform.

### 4.3 Goals That Changed Over Time

- Worldgen realism expanded into full platform architecture.
- UI Editor/Tool Editor became Workbench Platform.
- Workbench-centered view was refined into contracts-centered architecture with Workbench as surface.
- Serial prompt execution evolved toward AIDE-managed parallel development.
- Old C89/C++98 portability discipline shifted toward C17/C++17 with C-compatible ABI.

### 4.4 Goals Still Unresolved

- Full CTest cleanup.
- Runtime package mount.
- Provider runtime.
- Runtime module loader.
- Workbench shell.
- Presentation contracts.
- Replay proof execution status.
- Barebones client execution status.
- AIDE dev/main workflow law.
- Actual gameplay/domain implementation.

## 5. Decisions Made and Why

### Decision Overview Table

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | Dominium is a deterministic simulation operating environment | Accepted | Avoid feature pile, enable platform longevity | High | FACT |
| DECISION-02 | Domino is reusable substrate; Dominium is product family | Accepted | Enables reuse in other games/projects | High | FACT |
| DECISION-03 | Workbench is production environment, not authority | Accepted | Prevents editor truth drift | High | FACT |
| DECISION-04 | AIDE is repo/control-plane harness | Accepted | Needed for parallel, repairable development | High | FACT |
| DECISION-05 | Development non-blocking, promotion evidence-blocked | Accepted | Balances speed and correctness | High | FACT |
| DECISION-06 | Use task branches/worktrees, not direct shared-dev mutation | Accepted | Prevents concurrency chaos | High | FACT |
| DECISION-07 | Keep canonical source roots closed | Accepted | Prevents root sprawl | High | FACT |
| DECISION-08 | C17/C++17 target baseline with C-compatible ABI | Accepted as doctrine; verify implementation | Modernizes without ABI loss | Medium-high | FACT + VERIFY |
| DECISION-09 | CLI/text/rendered/native/headless are projections | Accepted | Avoids four UI systems | High | FACT |
| DECISION-10 | Full CTest remains T4 debt | Accepted | Keeps product-spine progress moving | High | FACT |
| DECISION-11 | Renderer first wave: null, software, OpenGL 3.3, D3D11 | Accepted | Practical platform floor | High | FACT |
| DECISION-12 | `vector2d` is drawing/canvas, not renderer backend | Accepted | Avoids matrix confusion | High | FACT |
| DECISION-13 | Broad feature work remains blocked | Accepted | Prevents premature implementation | High | FACT |
| DECISION-14 | Package mount is fixture-level, not runtime | Accepted / current | Avoid false support claims | High | FACT |

### Prose Explanation of Key Decisions

DECISION-01 matters because the user’s ambitions include worldgen, player invention, civilizations, modding, Workbench, AIDE, and future interfaces. A normal game-feature model would collapse. A deterministic simulation operating environment lets each capability become a contract-backed subsystem.

DECISION-05 matters because the user wants many agents and machines to work in parallel without being stopped by every blocker. But main cannot become a dumping ground. This is why dev is permissive and main is evidence-blocked.

DECISION-09 matters because separate CLI, TUI, GUI, and native systems would duplicate behavior and drift. The chosen architecture makes command/result/refusal/view/action the truth and projections the surface.

DECISION-14 matters because `PACKAGE-MOUNT-SLICE-01` has only proven fixtures and reports. Treating it as package runtime would create false implementation claims.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

| ID | Option | Status | Reason | Reconsider conditions | Label |
|---|---|---|---|---|---|
| REJECTED-01 | Simulate whole worlds continuously for billions of years | Rejected | Too expensive; lazy deterministic history preferred | Local/refined time simulation remains possible | FACT |
| REJECTED-02 | Hardcode every object/machine/vehicle | Rejected | Does not scale to arbitrary creation | Specific built-ins may exist as modules/templates | FACT |
| REJECTED-03 | Require all player-created things be manually declared | Rejected as sole method | Too rigid/non-diegetic | Optional formalization remains useful | FACT |
| REJECTED-04 | Pure intent inference | Rejected | Engine should detect patterns/affordances, not read minds | Assistant/UX can infer suggestions | FACT |
| REJECTED-05 | Workbench as monolithic everything editor | Rejected | Would become a second platform/authority | Integrated shell with modules is accepted | FACT |
| REJECTED-06 | Native-widget-first UI editor | Rejected | Does not reuse client/rendered UI path | OS-native projections later | FACT |
| REJECTED-07 | Separate CLI/TUI/rendered/native semantics | Rejected | Causes drift | Projection model accepted | FACT |
| REJECTED-08 | All agents mutate dev directly | Rejected | Conflict/attribution risk | Task branches/worktrees accepted | FACT |
| REJECTED-09 | Build full AIDE OS before product-spine work | Deprioritised | Would stall product progress | Minimum AIDE law before large parallel wave | FACT |
| REJECTED-10 | Treat full CTest as normal immediate blocker | Deprioritised | Too heavy; T4/full-gate debt | Release/trust phase | FACT |
| REJECTED-11 | OpenGL 1.1/D3D9 first-wave renderer | Rejected | Back-port/research only | Future constrained lanes | FACT |
| REJECTED-12 | C89/C++98 as active mainline constraint | Superseded | C17/C++17 baseline accepted | Retro/research lanes | FACT + VERIFY |

## 7. Important Reasoning, Rationale, and Tradeoffs

The conversation repeatedly balanced ambition against collapse. The user wants an ultimate simulation platform, but the chosen path is incremental proof slices. The system must avoid both extremes: building only doctrine with no usable product, and rushing into broad feature implementation that breaks modularity.

The most important tradeoff is speed versus evidence. The user wants non-blocking development on `dev`, but main must remain evidence-backed. This led to the doctrine “development is non-blocking, promotion is evidence-blocked.”

Another tradeoff is simulation realism versus compute cost. The chosen solution is deterministic sparse materialization rather than global brute-force simulation.

A third tradeoff is UI richness versus architectural reuse. Workbench should eventually be powerful, but it must use the same command/view/projection system as client, launcher, setup, server, CLI, and TUI.

A fourth tradeoff is portability versus modern code quality. The final doctrine accepts C17/C++17 for mainline while preserving C-compatible ABI and explicit serialization.

## 8. Plans, Future Work, and Next Steps

### Recommended Immediate Sequence

```text
1. Verify current repo state.
2. If queue stale after PACKAGE-MOUNT-SLICE-01, run QUEUE-RECONCILE-01.
3. Run REPLAY-PROOF-SLICE-01 if missing.
4. Run BAREBONES-CLIENT-SHELL-01 if missing.
5. Run PRODUCT-SPINE-REVIEW-01.
6. If review passes, begin limited parallel dev:
   AIDE-WORKFLOW-LAW-01
   PRESENTATION-CONTRACT-01
   POINTER-WIDTH-SERIALIZATION-AUDIT-01
```

### Why this order

Replay proof turns deterministic claims into a proof fixture. Barebones client proves product survival floor. Product Spine Review determines whether limited parallel development is safe.

### Next Phase after Product Spine Review

```text
AIDE-WORKFLOW-LAW-01
AIDE-WORKUNIT-SCHEMA-01
AIDE-DEV-MAIN-POLICY-01
AIDE-CHECKPOINT-LOOP-01
AIDE-CAPABILITY-REALITY-LEDGER-01
```

### Presentation Phase

```text
PRESENTATION-CONTRACT-01
PROJECTION-CONFORMANCE-01
ACCESSIBILITY-CONTRACT-01
TEXT-LOCALIZATION-CONTRACT-01
```

### Workbench Expansion

```text
WORKBENCH-SHELL-01
PROJECT-GRAPH-EXPLORER-01
PACK-BROWSER-01
AGENT-WORK-BOARD-01
COMPONENT-MATRIX-VIEWER-01
RENDERER-SANDBOX-01
THEME-LAB-01
INTERFACE-STUDIO-01
```

### Domain Phase

Later only:

```text
SPEC-DEEP-PRIMITIVES-01
SPEC-FAILURE-ONTOLOGY-01
SPEC-PLAYER-FORMALIZATION-WORKFLOWS-01
DOMAIN-CONSTITUTION-WAVE-01
CROSS-DOMAIN-BRIDGE-INSTANTIATION-01
```

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

- Answers should be direct, source-grounded, and audit-ready.
- Explicitly label uncertainty.
- Do not invent facts.
- Do not smooth over contradictions.
- Prompts must be copyable in one code block.
- Do not ask whether to proceed when user already asked to proceed.
- Use repo state as source of truth.
- Preserve warnings; do not claim warning-free if repo says `PASS_WITH_WARNINGS`.
- No broad feature work without gate authorization.
- No false implementation claims.
- Do not re-ask already answered questions.

### 9.2 Inferred Constraints and Preferences

- User prefers architecture before implementation.
- User wants strong challenge/correction.
- User prefers long, structured answers when preserving context.
- User wants future assistants to avoid restarting doctrine.

### 9.3 Uncertain or Unestablished Preferences

- Exact desired level of final file detail vs chat detail may vary; user requested both.
- Whether future prompts should always include optional fast strict depends on task scope.
- Whether `origin/dev` already exists needs verification.

## 10. Files, Artifacts, Outputs, and Prompts

### Uploaded File

| ID | Artifact | Type | Purpose | Status |
|---|---|---|---|---|
| ARTIFACT-01 | `/mnt/data/Pasted text.txt` | Uploaded text file | Contains the preservation/export task instruction | Loaded |

### Important repo files/audits referenced

```text
.aide/queue/current.toml
.aide/context/latest-task-packet.md
.aide/context/latest-review-packet.md
.aide/reports/latest-dominium-status.md
.aide/reports/latest-warning-disposition.md
docs/repo/FOUNDATION_LOCK.md
docs/repo/audits/PACKAGE_MOUNT_SLICE_01.md
docs/repo/audits/REPLAY_PROOF_SLICE_01.md
docs/repo/audits/BAREBONES_CLIENT_SHELL_01.md
docs/repo/audits/QUEUE_RECONCILE_01.md
docs/repo/audits/COMMAND_RESULT_VIEW_SLICE_01.md
docs/repo/audits/WORKBENCH_VALIDATION_SLICE_01.md
docs/repo/audits/PHASE_REVIEW_02.md
```

### Prompts generated in this chat

```text
MATRIX-CLEANUP-00
WORKBENCH-VALIDATION-SLICE-01
SERVICE-CONFORMANCE-LAW-01
DOCUMENT-PATCH-TRANSACTION-RUNTIME-01
PROJECT-GRAPH-SERVICE-01
COMPOSITION-RESOLVER-LAW-01
DOMINIUM-DOCTRINE-RECOVERY-MATRIX-01
COMMAND-RESULT-VIEW-SLICE-01
PHASE-REVIEW-02
QUEUE-RECONCILE-01
REPLAY-PROOF-SLICE-01
BAREBONES-CLIENT-SHELL-01
```

### Files created by this preservation task

See sections 35–39 and linked files in final chat response.

## 11. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known | Unknown | Priority |
|---|---|---|---|---|---|
| QUESTION-01 | Has `QUEUE-RECONCILE-01` run? | Determines next task | Prompt generated | Execution status | P0 |
| QUESTION-02 | Has `REPLAY-PROOF-SLICE-01` run? | Required before barebones client | Prompt generated | Execution status | P0 |
| QUESTION-03 | Has `BAREBONES-CLIENT-SHELL-01` run? | Required before product spine review | Prompt generated | Execution status | P0 |
| QUESTION-04 | Does CMake fully reflect C17/C++17? | Avoid docs/build mismatch | Doctrine says yes | Live build files need check | P1 |
| QUESTION-05 | Does `origin/dev` exist? | Parallel dev planning | Desired branch model | Repo state | P1 |
| QUESTION-06 | What warnings remain after latest prompts? | Promotion policy | Known warning categories | Exact live count | P1 |
| QUESTION-07 | When to start large parallel dev? | Workflow scale | After AIDE workflow layer | Exact readiness | P1 |
| QUESTION-08 | What should be first Workbench runtime shell task? | Workbench roadmap | Validation slice exists | Shell readiness | P2 |
| QUESTION-09 | When to tackle full CTest? | Release trust | T4 debt | Burn-down schedule | P2 |
| QUESTION-10 | When to begin domain/game work? | Main ambition | Later after product spine | Exact gate | P2 |

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

| Risk | Consequence | Mitigation |
|---|---|---|
| Treating `PASS_WITH_WARNINGS` as clean | False confidence | Always preserve warnings |
| Restarting doctrine | Wasted time, inconsistent plans | Use this handoff and live repo |
| Treating Workbench as authority | Architectural drift | Workbench must use commands/services |
| Starting broad feature work too soon | Refactor spiral | Respect blockers |
| Assuming docs are implementation | False support claims | Capability Reality Ledger |
| Agents mutating shared dev | Conflicts | Use task branches/worktrees |
| Overbuilding AIDE OS before product proof | Stalls progress | Minimum AIDE layer only |
| Ignoring full CTest debt | Release risk | Keep T4 debt visible |
| Creating new roots | Root sprawl | Closed root model |
| Making separate UI systems | Drift | Projection architecture |
| Running destructive git cleanup | Data loss | Use blocker-handling rules |
| Assuming latest prompt ran | Wrong task order | Verify audits and queue |

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat should feed into future spec book chapters on:

```text
Project identity and doctrine
Repo governance and root model
Foundation Lock and gates
AIDE task operating system
Dev/main/checkpoint workflow
Workbench production environment
Presentation/projection architecture
Package/pack/module/provider composition
Replay/proof evidence
Barebones product floors
Worldgen/domain doctrine
Deep primitives and player creation
Civilization macro/micro simulation
Renderer/platform baseline
Language/ABI policy
Testing and release gates
```

Formal requirement candidates:

```text
Path is not identity.
Implementation is not contract.
UI is not authority.
Generated output is not source truth.
Development is non-blocking.
Promotion is evidence-blocked.
Every stable capability must have evidence.
Every prompt must preserve known warnings and broad blockers.
```

Context-only candidates:

```text
nixie/VFD/industrial UI inspirations
closed-eye cognitive UI concept
OEM+ OS-style theme ideas
long-term BCI/multiverse vision
```

Needs verification before merging into master spec:

```text
live status of latest prompts
C17/C++17 build implementation
AIDE branch policy files
current queue state
current warning counts
```

## 14. What I Should Remember

- The project identity has converged; do not restart it.
- The next chat should verify repo state first.
- Package mount is complete as fixture proof, not runtime.
- Replay proof and barebones client are the next product-spine tasks if not already done.
- AIDE should enable non-blocking dev but evidence-blocked promotion.
- Workbench is a production environment, not authority.
- UI modes are projections of shared semantics, not separate systems.
- Full CTest remains T4 debt.
- Broad feature work is blocked.
- Future parallel dev should use task branches/worktrees, not direct shared-dev mutation.
- Do not hide warnings.
- Do not claim support without evidence.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat

1. “Explain the final Dominium / Domino / Workbench / AIDE architecture in simple terms.”
2. “What are the three most important doctrines from this chat?”
3. “How did we get from worldgen to AIDE dev/main workflow?”

### 15.2 Decisions

4. “Which decisions are final, and which are still tentative?”
5. “Why did we reject Workbench as a monolithic editor?”
6. “Why is full CTest not blocking current product-spine work?”

### 15.3 Tasks and Next Actions

7. “Generate `PRODUCT-SPINE-REVIEW-01` if replay and barebones are complete.”
8. “Generate `AIDE-WORKFLOW-LAW-01`.”
9. “Generate `PRESENTATION-CONTRACT-01`.”

### 15.4 Artifacts and Files

10. “List all audits and queue files the next chat should inspect first.”
11. “What should be in the Capability Reality Ledger?”
12. “What file should record dev/main promotion policy?”

### 15.5 Risks and Verification

13. “What could go wrong if we start parallel dev too early?”
14. “What repo facts must be verified before the next prompt?”
15. “How do we prevent docs from outrunning implementation?”

### 15.6 Future Spec Book / Aggregation

16. “Which parts of this chat should become formal spec requirements?”
17. “Which parts are background context only?”
18. “What should be merged with other old-chat reports?”

### 15.7 Deep-Dive Questions Specific to This Chat

19. “Explain the Workbench self-hosting ladder.”
20. “Explain how player-created machines fit the deep primitive model.”

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

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Project Identity | Domino/Dominium/Workbench/AIDE roles | DECISION-01–05 | Requirement | High | Core chapter |
| Repo Architecture | Closed root model | DECISION-07 | Requirement | High | Check live docs |
| ABI/Language | C17/C++17 + C ABI | DECISION-08 | Requirement with verification | Medium | Verify CMake |
| AIDE Workflow | dev/main/task/checkpoint doctrine | DECISION-04–06 | Requirement | High | Needs files |
| Workbench | Production environment, not authority | DECISION-03 | Requirement | High | Future Workbench chapter |
| Presentation | Projection architecture | DECISION-09 | Requirement | High | UI chapter |
| Package Composition | Fixture mount, composition law | WORKSTREAM-07 | Requirement/context | High | Runtime later |
| Replay Proof | Next product-spine task | TASK-03 | Open issue | Medium | Execution unknown |
| Worldgen Doctrine | Sparse/lazy deterministic truth | WORKSTREAM-10 | Requirement/context | High | Domain chapters |
| Deep Primitives | Creation model | WORKSTREAM-10 | Requirement/context | High | Domain chapters |
| Testing Gates | Fast strict vs full gate | DECISION-10 | Requirement | High | Test strategy |
| Renderer Baseline | Null/software/OpenGL/D3D11 | DECISION-11 | Requirement | High | Renderer chapter |

## 29. Context Transfer Packet for a Future Chat

### 29.1 Ultra-Condensed Bootstrap Brief

This chat developed and preserved the current Dominium architecture and task roadmap. Dominium is no longer being treated as a normal game project. The converged identity is: Domino is the reusable deterministic substrate, Dominium is the game/product family built on it, Workbench is the production/validation/editing/evidence environment, AIDE is the repo/control-plane harness, Codex is a bounded patch executor, contracts are law, and diagnostics/tests/replay/evidence are proof.

The core doctrines are: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth; development should be non-blocking; promotion should be evidence-blocked. The project should be modular, deterministic, portable, extensible, replaceable, and evidence-backed.

Current expected state from this chat: Foundation Lock is `PASS_WITH_WARNINGS`, fast strict passes, dependency-direction strict has 0 violations with known warnings, full CTest remains T4/full-gate debt, and broad feature work remains blocked. `PACKAGE-MOUNT-SLICE-01` landed as `PASS_WITH_WARNINGS` and proved only a fixture-level package/profile mount decision, not runtime package mounting. The next intended product-spine task is `REPLAY-PROOF-SLICE-01`, followed by `BAREBONES-CLIENT-SHELL-01`, then `PRODUCT-SPINE-REVIEW-01`. Verify live repo state first, especially `.aide/queue/current.toml`, recent commits, and relevant audits.

Workbench should eventually be a visual and agentic production environment, but it is not authority. It edits documents and dispatches registered commands; runtime executes; contracts constrain; content packages; apps consume; tests prove. CLI, text/TUI, rendered GUI, native GUI, and headless must be projections of one command/result/refusal/document/view/action spine, not separate UI systems.

Future AIDE workflow: do not let agents all mutate shared `dev`. Use one task branch/worktree per prompt. AIDE integrates safe work into `origin/dev`; checkpoint branches prove integrated waves; `origin/main` receives only evidence-backed promotion. Limited parallel dev can start after replay proof, barebones client, and product-spine review. Large parallel dev should wait for `AIDE-WORKFLOW-LAW-01`, `AIDE-WORKUNIT-SCHEMA-01`, and `AIDE-DEV-MAIN-POLICY-01`.

### 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

### 29.3 Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Verify live repo state before acting.
- Do not re-ask answered questions.
- Ask clarifying questions only when materially necessary.
- Do not invent missing details.
- Do not treat tentative items as final.
- Do not repeat rejected options.
- Preserve artifacts and warnings.
- Use structured outputs.
- Put future Codex prompts in one code block.
- Do not start broad feature work prematurely.

### 29.4 Active Workstreams

Active: product spine, AIDE workflow, Workbench platform, presentation architecture, package/replay/barebones product proof, repo governance.

Deferred: gameplay, renderer implementation, native GUI, runtime package/provider/module loaders, domain constitutions.

### 29.5 Current Priorities

1. Verify current repo state.
2. Run missing queue/replay/barebones prompts.
3. Run Product Spine Review.
4. Add minimum AIDE workflow law.
5. Begin limited parallel task-branch development.
6. Add presentation contracts.
7. Continue Workbench/runtime/product slices.

### 29.6 Current Open Questions

- Has replay proof run?
- Has barebones client shell run?
- Is queue reconciled?
- Does live build use C17/C++17?
- Does origin/dev exist?
- What warnings remain?

### 29.7 Recommended First Action

Inspect the live repo. Determine whether `REPLAY-PROOF-SLICE-01` and `BAREBONES-CLIENT-SHELL-01` have run. Generate the next missing prompt accordingly.

## 30. Spec Sheet

```yaml
spec_sheet:
  metadata:
    chat_label: "Dominium Architecture, Workbench, AIDE, and Product-Spine Planning"
    date_anchor: "2026-05-27 Australia/Melbourne"
    source_scope: "This chat only unless labelled PROJECT-CONTEXT"
    apparent_coverage: "Partial transcript with high contextual reconstruction"
    confidence_1_to_5: 4
    staleness_risk: "Medium"
    safe_for_aggregation: "Yes, with caveats"
    main_limitations:
      - "Visible transcript includes skipped-message markers."
      - "Live repo may advance after report creation."
      - "Execution status of latest generated prompts must be verified."

  summary:
    one_sentence: "This chat converged Dominium into a deterministic, contract-governed simulation platform with Workbench as production environment and AIDE as evidence-backed development control plane."
    short_brief: "The chat established architecture, repo gates, Workbench direction, AIDE dev/main workflow, product-spine task sequencing, and future domain roadmap."
    main_topics:
      - "Deterministic sparse worldgen"
      - "Deep primitives and player creation"
      - "Repo Foundation Lock"
      - "Workbench production environment"
      - "AIDE task operating system"
      - "Package/replay/barebones product spine"
      - "Presentation/projection architecture"
    main_outputs:
      - "Prompt series for post-foundation slices"
      - "AIDE dev/main workflow doctrine"
      - "Product-spine roadmap"
      - "This preservation report"
    highest_priority_carry_forward:
      - "Verify repo state."
      - "Run missing REPLAY-PROOF-SLICE-01 and BAREBONES-CLIENT-SHELL-01."
      - "Generate PRODUCT-SPINE-REVIEW-01."
      - "Add AIDE-WORKFLOW-LAW-01 before large parallel dev."

  source_rules:
    labels_used:
      - "FACT"
      - "INFERENCE"
      - "UNCERTAIN / UNVERIFIED"
      - "PROJECT-CONTEXT"
    conflict_rules:
      - "Live repo evidence overrides this handoff."
      - "User-accepted decisions override assistant brainstorms."
      - "Prompt-generated plans are not implementation proof."
    staleness_rules:
      - "Verify current queue and commits before acting."
      - "Treat repo statuses as potentially stale if not checked live."

  user_preferences:
    explicit:
      - "Detailed, source-grounded, audit-ready answers."
      - "Do not invent facts."
      - "Prompts in one code block."
      - "Preserve uncertainty and rejected options."
      - "Do not over-compress."
    inferred:
      - "Prefers architecture and proof before broad implementation."
      - "Values correction over agreement."
      - "Wants future assistants to avoid repeated doctrine discussion."
    uncertain_or_not_established:
      - "Exact desired cadence once parallel dev begins."

  workstreams:
    - id: "WORKSTREAM-03"
      name: "Product Spine"
      label: "FACT"
      objective: "Build package mount, replay proof, and barebones product floor."
      current_state: "Package mount complete; replay and barebones execution uncertain."
      desired_end_state: "Product spine review authorizes limited parallel development."
      status: "Active"
      priority: "P0"
      background: "Current narrow product slices are permitted after Foundation Lock."
      decisions_made:
        - "Package mount is fixture-level only."
      decisions_pending:
        - "Whether product spine review passes."
      tasks:
        - "REPLAY-PROOF-SLICE-01"
        - "BAREBONES-CLIENT-SHELL-01"
        - "PRODUCT-SPINE-REVIEW-01"
      constraints:
        - "No broad package runtime."
        - "No gameplay."
      dependencies:
        - "PACKAGE-MOUNT-SLICE-01"
      timeline: "Immediate"
      blockers:
        - "Execution status unknown."
      risks:
        - "False runtime claims."
      artifacts:
        - "PACKAGE_MOUNT_SLICE_01.md"
      success_criteria:
        - "Replay proof and barebones client pass with warnings or better."
      next_action: "Verify live repo and run missing prompt."
      verification_needed:
        - "Check REPLAY_PROOF_SLICE_01 audit."
      confidence: "High"

  decisions:
    - id: "DECISION-05"
      decision: "Development is non-blocking; promotion is evidence-blocked."
      status: "accepted"
      label: "FACT"
      evidence_or_basis: "User and assistant convergence near end of chat."
      rationale: "Allows parallel progress without corrupting main."
      implications: "Use dev/task/checkpoint/main model."
      related_workstreams:
        - "WORKSTREAM-04"
      uncertainty: "Exact automation not implemented yet."

  tasks:
    - id: "TASK-03"
      task: "REPLAY-PROOF-SLICE-01"
      priority: "P0"
      urgency: "U0"
      owner: "Codex/AIDE"
      dependencies:
        - "PACKAGE-MOUNT-SLICE-01"
      inputs_needed:
        - "Package mount command/result fixture"
      expected_output: "Command-level replay/proof fixture and validator."
      next_step: "Run if audit missing."
      related_workstreams:
        - "WORKSTREAM-08"
      label: "FACT"
      confidence: "Medium"

  constraints:
    - id: "CONSTRAINT-01"
      constraint: "Broad feature work remains blocked."
      type: "process"
      hard_or_soft: "hard"
      source_or_basis: "Queue/Foundation status"
      implication: "Only narrow slices."
      violation_risk: "Refactor spiral"
      label: "FACT"
      confidence: "High"

  open_questions:
    - id: "QUESTION-01"
      question: "Has REPLAY-PROOF-SLICE-01 executed?"
      why_it_matters: "Determines next task."
      known: "Prompt generated."
      unknown: "Execution status."
      resolution_path: "Check commits and audit file."
      priority: "P0"
      related_workstreams:
        - "WORKSTREAM-08"
      label: "UNCERTAIN"

  rejected_or_superseded_options:
    - id: "REJECTED-05"
      option: "Workbench as monolithic editor."
      status: "rejected"
      reason: "Would become authority/blob."
      final_or_tentative: "final for current architecture"
      reconsider_conditions: "None for near term."
      related_workstreams:
        - "WORKSTREAM-05"
      label: "FACT"

  artifacts:
    - id: "ARTIFACT-06"
      name_or_description: "REPLAY-PROOF-SLICE-01 prompt"
      type: "prompt"
      purpose: "Generate narrow command-level replay proof."
      status: "generated; execution uncertain"
      origin: "This chat"
      carry_forward: true
      notes: "Run after queue reconciliation if missing."
      label: "FACT"

  risks:
    - id: "RISK-02"
      risk: "Docs outrun code."
      consequence: "False support claims."
      likelihood: "High"
      severity: "High"
      mitigation: "Capability Reality Ledger."
      related_workstreams:
        - "WORKSTREAM-04"
      label: "FACT"

  verification_queue:
    - id: "VERIFY-01"
      item: "Current AIDE queue"
      why_verification_needed: "Determines next prompt."
      suggested_source_type: ".aide/queue/current.toml"
      priority: "P0"
      related_workstreams:
        - "WORKSTREAM-03"
      label: "VERIFY"

  spec_book_notes:
    likely_sections:
      - "Architecture doctrine"
      - "Repo governance"
      - "AIDE workflow"
      - "Workbench"
      - "Presentation system"
      - "Domain primitives"
      - "Testing gates"
    unique_contributions:
      - "Development non-blocking / promotion evidence-blocked doctrine."
      - "Workbench progressive self-hosting."
      - "Product-spine sequencing."
    possible_duplicates_with_other_chats:
      - "Worldgen architecture"
      - "Constitutional Architecture"
      - "Repo convergence"
    conflicts_to_watch_for:
      - "C89/C++98 vs C17/C++17 status."
      - "Queue next-task state."
    formal_requirements_candidates:
      - "Path is not identity."
      - "UI is not authority."
      - "Task branches per prompt."
    background_context_candidates:
      - "Nixie/VFD/OEM+ UI inspirations."
    needs_user_confirmation:
      - "Whether origin/dev exists and should become official."

  final_recommendations:
    next_action_if_continuing_this_chat: "Verify queue and run the next missing product-spine prompt."
    next_action_for_aggregator: "Merge this report under architecture/AIDE/Workbench/product-spine sections."
    user_checks_required:
      - "Check live repo state."
      - "Confirm whether latest prompts have run."
```

## 31. Aggregator Packet

# Aggregator Packet — Dominium Architecture, Workbench, AIDE, and Product-Spine Planning

## Packet Metadata

* Chat label: Dominium Architecture, Workbench, AIDE, and Product-Spine Planning
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial raw transcript, high reconstruction from visible content
* Confidence: 4 / 5
* Staleness risk: Medium
* Merge priority: High
* Main limitations: latest repo prompt execution state must be verified

## Ultra-Condensed Carry-Forward Capsule

This chat is a major architecture and planning checkpoint for Dominium. It converged the project identity around Domino as reusable deterministic substrate, Dominium as the game/product family, Workbench as the production and validation environment, AIDE as repo/control-plane harness, and contracts/evidence as the core truth layer. The chat should feed into the master spec as a core source for repo governance, Workbench, AIDE, presentation architecture, package/replay/product spine, and future simulation-domain planning.

The strongest doctrines are: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth; development is non-blocking; promotion is evidence-blocked. These should become formal requirements.

The repo state during this chat moved through Foundation Lock and multiple post-foundation slices. Foundation Lock is `PASS_WITH_WARNINGS`, not warning-free. Fast strict passes. Dependency-direction strict is green with known warnings. Full CTest remains T4/full-gate debt. Broad feature work remains blocked. `PACKAGE-MOUNT-SLICE-01` is complete as a fixture-level proof, not package runtime. The next tasks are queue reconciliation if stale, replay proof, barebones client shell, and product spine review.

Workbench should become the visual and agentic production environment, but not authority. It edits documents and dispatches commands. Runtime executes services; contracts constrain; content packages; apps consume; tests prove. UI modes are projections: CLI, text/TUI, rendered GUI, native GUI, and headless share command/result/refusal/view/action semantics.

AIDE should evolve into a repo-native task operating system. The branch doctrine is task branches/worktrees per prompt, `origin/dev` for integration, checkpoint branches for proof, and `origin/main` for promoted truth. Ordinary blockers should become repair/prerequisite/resume tasks. Unsafe/destructive/authority blockers require human decision.

The chat also preserves future domain doctrine: deterministic sparse worldgen, lazy history, truth/perceived/render separation, epistemic/diegetic refinement, process-only mutation, deep primitives for player creation, macro/micro civilization capsules, and future domain constitutions. These are not immediate implementation tasks.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Verify live repo state | Task | TASK-01 | Prevent stale next-task errors | FACT | High |
| P0 | Run missing replay proof | Task | TASK-03 | Deterministic evidence spine | FACT | Medium |
| P0 | Run missing barebones client | Task | TASK-04 | Product survival floor | FACT | Medium |
| P0 | Product Spine Review | Task | TASK-05 | Authorize limited parallel dev | FACT | High |
| P1 | AIDE workflow law | Task | TASK-06 | Enables safe parallel dev | FACT | High |
| P1 | Presentation contract | Task | TASK-09 | Prevents UI drift | FACT | High |
| P1 | Capability Reality Ledger | Task | Future | Prevents docs/code drift | FACT | High |

## Compact Registers for Merge

See sections 17–28 above for full registers. Merge the following as high priority:

- DECISION-05: development non-blocking / promotion evidence-blocked.
- DECISION-09: UI modes are projections.
- TASK-03 to TASK-05: replay, barebones, product spine review.
- CONSTRAINT-01: broad feature work blocked.
- RISK-02: docs outrun code.
- VERIFY-01 to VERIFY-04: queue/replay/barebones/CMake verification.

## Possible Cross-Chat Duplicates

- Constitutional Architecture
- Worldgen sparse materialization
- Repo convergence
- AIDE planning
- Workbench/UI editor discussions
- Domain constitution planning

## Possible Cross-Chat Conflicts

- C89/C++98 vs C17/C++17.
- Earlier roadmap saying Workbench next vs later product-spine sequencing.
- Old root layout vs canonical root layout.
- Full CTest as blocker vs T4 debt.
- Workbench as product vs Workbench as authority.

## Spec Book Integration Guidance

This chat should inform chapters on:

```text
Project identity
Repo governance
AIDE workflow
Workbench
Presentation system
Package/composition/replay/product spine
Testing gates
Domain doctrine
Worldgen/deep primitives
```

Formalize:

```text
Path is not identity.
Implementation is not contract.
UI is not authority.
Generated output is not source truth.
Development non-blocking.
Promotion evidence-blocked.
```

Do not merge as implemented features:

```text
runtime package mount
runtime replay
provider runtime
module loader
Workbench shell
renderer
native GUI
gameplay
release publication
```

## Aggregator Warnings

- Do not assume latest prompts executed.
- Do not flatten `PASS_WITH_WARNINGS` into clean.
- Do not treat doctrine recovery as canon supersession.
- Do not treat fixture proof as runtime implementation.
- Do not restart doctrine from scratch.

## 32. Adversarial Self-Audit

| Issue | Severity | Correction needed | Correction applied? | Residual risk |
|---|---|---|---|---|
| Raw transcript incomplete due skipped messages | High | Label access as partial | Yes | Some details may be missing |
| Live repo may advance | High | Add verification queue | Yes | New chat must verify |
| C17/C++17 implementation uncertain | Medium | Mark VERIFY | Yes | Still requires repo check |
| Latest prompts execution unknown | High | Mark replay/barebones uncertain | Yes | Must inspect audits |
| Domain/worldgen details compressed | Medium | Added doctrine summary | Partial | Full old brainstorm not exhaustive |
| Generated prompts not fully reproduced | Medium | Listed prompt names and roles | Partial | User can regenerate |
| Artifacts may be incomplete | Medium | Ledger includes known artifacts | Yes | Missing repo files possible |
| Assistant suggestions vs decisions | High | Decision status and confidence included | Yes | Some acceptance inferred from user continuation |
| Emotional/motivational context limited | Low-medium | Added platform/avoid-rework motivation | Yes | User may have more unstated motivation |
| Time/date state | Medium | Date anchor set | Yes | Live repo state after date can change |

## 33. Corrections Applied

After audit, the handoff was revised to:

- Mark transcript access as partial, not full.
- Add explicit verification items for live repo state.
- Add uncertainty around `REPLAY-PROOF-SLICE-01` and `BAREBONES-CLIENT-SHELL-01`.
- Clarify C17/C++17 as doctrine needing live build verification.
- Preserve `PASS_WITH_WARNINGS` warnings.
- Add branch model and AIDE workflow doctrine.
- Add rejected/superseded options register.
- Add product-spine next-task sequence.
- Include worldgen and deep primitive context.
- Add “what new chat should not assume.”

## 34. Final Reliability Assessment

* Completeness rating: 4 / 5
* Reliability rating: 4 / 5
* Human-readability rating: 4 / 5
* Aggregation-readiness rating: 4 / 5
* Main remaining uncertainty sources:
  - skipped transcript sections,
  - live repo changes after this report,
  - execution status of latest prompts,
  - CMake language baseline,
  - exact current warning counts.
* Manual review recommended before merging into a master spec: Yes.

## 35. File Export Package

Files were created for this preservation package. See final chat links.

## 36. File Index and Explanation

| File | Purpose | What it contains | When to use it | Importance |
|---|---|---|---|---|
| Manifest | Package overview | File list, caveats, counts | First when downloading | High |
| Human-readable report | Main preservation report | Sections 0–16 | Read for understanding | Highest |
| Context transfer packet | New-chat context | Section 29 | Paste/brief future chat | Highest |
| Spec sheet | YAML-style structured data | Section 30 | Aggregation/spec merge | High |
| Registers | Tables/IDs | Sections 17–28 | Tracking decisions/tasks | High |
| Aggregator packet | Cross-chat merge | Section 31 | Master spec aggregation | High |
| Reader brief | Shorter human brief | Top items and next steps | Quick review | Medium-high |
| Verification/audit | Self-audit and verification | Sections 32–34 + queue | Before relying on state | High |
| Bootstrap prompt | Future chat starter | Copy-paste prompt | Start new chat | Highest |
| In-chat reader | Guide to package | What to read, questions | Human navigation | Medium |
| ZIP | Bundle | All files | Archive/download | Highest |

## 37. Human Reader Guide

Read first:

1. Section A / Ultra-condensed brief.
2. Section 0 / Coverage and Reliability.
3. Section 1 / Orientation.
4. Section 16 / Compact summary.
5. Section 29 / Context Transfer Packet.
6. Task Register and Verification Queue if continuing work.

For aggregation:

- Use sections 17–31.
- Use Spec Sheet YAML.
- Use Aggregator Packet.

For verification:

- Use sections 11, 26, 32–34.
- Check live repo before acting.

For next actions:

- Verify queue/current.
- Determine whether replay and barebones tasks have run.
- Generate Product Spine Review when ready.

## 38. Best Follow-Up Questions

### Understanding

1. “Explain the final project identity in 5 minutes.”
2. “What does ‘development non-blocking, promotion evidence-blocked’ mean in practice?”

### Decisions

3. “Which decisions are final and which need verification?”
4. “Why did we decide Workbench is not authority?”

### Tasks

5. “What prompt should be generated next given current repo state?”
6. “Generate PRODUCT-SPINE-REVIEW-01.”

### Artifacts

7. “Which repo files should I inspect first?”
8. “What audits prove the product-spine state?”

### Risks

9. “What are the top risks before starting parallel dev?”
10. “How do we prevent docs outrunning code?”

### Verification

11. “Create a checklist for verifying live repo state.”
12. “What does `PASS_WITH_WARNINGS` currently mean?”

### Spec Book / Aggregation

13. “Which parts of this chat should become formal spec requirements?”
14. “Which parts are background only?”

### Deep Dive

15. “Explain Workbench progressive self-hosting.”
16. “Explain the deep primitives model for player-created machines.”
17. “Explain sparse worldgen and lazy historical evaluation.”

## 39. Final Package Status

* Chat label: Dominium Architecture, Workbench, AIDE, and Product-Spine Planning
* Report type: full human-readable + structured handoff + spec-prep package
* Files created: yes
* ZIP created: yes
* Safe for later aggregation: yes, with caveats
* Extraction confidence: 4 / 5
* Main value of this chat: converged project identity, AIDE workflow doctrine, Workbench architecture, and product-spine sequencing.
* Most important decision: development should be non-blocking, promotion evidence-blocked.
* Most important unresolved issue: verify whether replay proof and barebones client prompts have executed.
* Most important next action: verify live repo state and run/generate the next missing product-spine prompt.
* Main caveats: visible transcript was partial; live repo may have advanced; latest prompts execution status uncertain.
* Best thing for me to read first: Ultra-Condensed Brief and Context Transfer Packet.
* Best question for me to ask next: “Given the live repo state, what is the next prompt to generate?”
