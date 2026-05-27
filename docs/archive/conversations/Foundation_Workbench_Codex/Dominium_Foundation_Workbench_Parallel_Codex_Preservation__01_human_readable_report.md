# COMPLETE CHAT PRESERVATION REPORT — Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial / high-context |
| Previously generated files available? | No prior downloadable package was available to this run; prior in-chat handoff text was visible |
| Uploaded files or artifacts present? | Yes — current uploaded preservation prompt is available; some older uploads may have expired |
| Contains future plans? | Yes |
| Contains decisions? | Yes |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium |
| Extraction confidence | 4 / 5 |
| Safe for later aggregation? | Yes, with caveats |
| Main limitations | The visible transcript contains extensive excerpts and generated prompts, but some earlier turns were elided as “Skipped”; live repo state after the latest pasted transcript was not independently rechecked in this preservation step; some older uploaded files have expired. |

Plain-language limitation statement:

This report reconstructs the visible substance of this chat and the user-uploaded preservation instructions. It does not claim access to every hidden or skipped turn. It also does not claim to have rerun live GitHub checks at the end of the chat. When repo state is described, the report distinguishes between state that was explicitly checked earlier in the conversation and state that was later pasted by the user. Some previous uploaded files are no longer available; if the user wants those exact files incorporated later, they should be re-uploaded.

The current uploaded preservation instruction file is part of the source context for this response. fileciteturn85file0

## 1. One-Page Orientation

This chat was a high-intensity strategic, architectural, and operational continuation of the Dominium project: a large simulation/game/engine ecosystem in the `Julesc013/dominium` repository. The user’s central concern was that the project had spent a very long time in refactor and restructuring work, and that without a clear, enforceable architecture and faster execution model, the project would either drift back into chaos or stall forever before reaching real Workbench and gameplay/product work.

The conversation began from the aftermath of extensive repo cleanup, AIDE installation, build proof, internal pilot proof, and directory/root restructuring work. Earlier in the project, Dominium had a large number of root-level folders such as `core/`, `control/`, `data/`, `packs/`, `profiles/`, `bundles/`, `lib/`, `libs/`, `validation/`, `meta/`, `governance/`, `net/`, and others. The user was extremely frustrated by how long the cleanup took and repeatedly threatened to manually move folders if the process did not converge. This created the need for a more aggressive but still governed model: deterministic routing of bad-root files, quarantine for unknowns, canonical roots, and later a move away from physical folder cleanup into contract/governance hardening.

The conversation ultimately converged on a stable architectural model: **Domino** is the reusable deterministic/runtime substrate; **Dominium** is the game/product family built on Domino; **Workbench** is the production, validation, editing, inspection, packaging, and evidence environment; **AIDE** is the repo/control-plane harness; **Codex** is a bounded patch executor; **Contracts are law**; and **tests, replay, diagnostics, and evidence are proof**. The most important principles became: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth.

The project’s root skeleton and governance spine were treated as mostly established by the end of the chat. Foundation Lock was originally blocked by dependency-direction strict validation, with 358 violations and 38 warnings. Later the user and assistant verified/preserved a state where `FOUNDATION-CLOSEOUT-02` closed Foundation Lock with warnings: dependency-direction strict had 0 violations and 68 warnings, fast strict passed, CMake configure/build and smoke CTest passed through fast strict, and full CTest remained T4/full-gate debt. Narrow product slices were authorized, but broad feature work remained blocked.

A major operational shift occurred near the end of the chat: instead of queueing all prompts sequentially, the user decided to run many tasks in parallel through multiple Codex chats and git worktrees. The assistant defined strict parallel-worker rules to prevent conflicts: no direct pushes to `main`, no edits to global AIDE latest-status files, task-local evidence only, explicit allowed paths, targeted validators instead of full test suites, and coordinator-controlled serial merges.

Several Wave 1 parallel prompts were generated: `SERVICE-CONFORMANCE-LAW-01`, `DOCUMENT-PATCH-TRANSACTION-RUNTIME-01`, `PROJECT-GRAPH-SERVICE-01`, `COMPOSITION-RESOLVER-LAW-01`, and `DOMINIUM-DOCTRINE-RECOVERY-MATRIX-01`. A later pasted transcript stated that Wave 1 and `WORKBENCH-VALIDATION-SLICE-01` were effectively complete, and that the next task should be `COMMAND-RESULT-VIEW-SLICE-01`. That task is now the most important next action unless live repo verification contradicts it.

The future relevance of this chat is high. It contains the transition from repo cleanup to governed product development; the final architectural vocabulary; the current parallel Codex workflow; the task ordering for Workbench/product spine; the rejected paths; the user’s frustration and speed requirements; and a doctrine recovery thread that preserves old Dominium design ambitions such as truth totality, sparse materialization, Truth/Perceived/Render separation, representation ladders, semantic ascent/descent, formalization chains, failure ontology, domain constitutions, ordinary life, and civilization-scale simulation.

## 2. The Story of the Conversation

### 2.1 From root cleanup frustration to controlled refactor

The early visible part of the conversation was dominated by the user’s frustration with the Dominium repository’s directory structure. The user wanted the ugly old root folders gone and did not want to keep fixing builds only to move directories again. The assistant initially argued for cautious, AIDE-controlled moves: inventory, salvage maps, move plans, gates, apply waves, and proof after every move. Over time, as Codex reports came back, the process generated small moves, root inventories, and proof reports.

The user became increasingly impatient because the visible root mess persisted after many tasks. The assistant eventually shifted from tiny low-risk moves to a deterministic bad-root router model: known files should move to their canonical homes, and unknown files should be routed to `archive/quarantine/<root>/`, rather than blocking cleanup. This was a major change in tempo. It preserved the principle of not guessing unknown semantics while allowing the directory structure to become clean.

### 2.2 From folders to semantic authority

After the root skeleton improved, the assistant and user recognized that the deeper problem was no longer top-level directories. The problem became semantic duplication and governance: what is public, what is private, what is stable, what is provisional, what is generated, what is a fixture, what must stay compatible, what can be replaced, and what proof is required.

This led to the Foundation Lock queue: public surface registry, API/ABI canon, dependency direction, command surface, diagnostics/evidence, artifact identity, schema/protocol evolution, capability/refusal, provider model, module/workbench/app composition, replacement protocol, version/deprecation, mod/pack trust, portability matrix, and fast strict test tiers.

### 2.3 Language and architecture pivot

Earlier project doctrine emphasized C89/C++98 to preserve broad historical portability. The conversation later revised this. Once the effective platform floor was treated as Windows 7 SP1, macOS 10.9.5, and Linux, the user and assistant concluded that C17 + C++17 was the better mainline baseline. Public ABI must remain C-compatible, but internal C++17 can be used for resource ownership, providers, runtime systems, apps, and Workbench. Later, the project also adopted a 64-bit source-native doctrine for full native products: x86_64 and arm64, little-endian, fixed-width persisted formats, and no pointer-sized truth.

### 2.4 Foundation Lock and dependency direction

The live repo check showed Foundation Lock initially blocked by dependency-direction strict validation. This was the first serious foundation validator still red: 358 violations and 38 warnings. The next prompt was generated to repair dependency direction. A later check showed Foundation Lock closed with warnings after dependency repair: 0 violations and 68 warnings. This unlocked narrow product slices such as `WORKBENCH-VALIDATION-SLICE-01`, while broad feature work remained blocked.

### 2.5 Workbench as product surface, not authority

The user and assistant explored Workbench deeply. The user proposed large modules such as Project Editor, UI Editor, Module Editor, and App Editor. The assistant refined these into workspaces: Project Graph Explorer, Interface Studio, Module/Pack Foundry, App Composer, Release Forge, Agent Control Workspace, Renderer/Theme Laboratory, and Replay/Trace Workspace. Internally, these should be built from smaller reusable modules: validation runner, command browser, document inspector, patch/diff viewer, diagnostics viewer, evidence viewer, pack browser, provider browser, capability matrix viewer, theme previewer, renderer test panel, asset browser, graph view, build/job console, and agent task queue.

The key conclusion was that Workbench is not the general module system; it is one consumer of the module/command/service/provider/pack/artifact system. Workbench must not call private tools directly. It must route through registered commands and typed results, diagnostics, refusals, views, and evidence.

### 2.6 Parallel Codex mode

Once Foundation Lock closed with warnings and Workbench validation was authorized, the user wanted to generate multiple prompts in parallel rather than continue sequentially. The assistant designed a parallel worktree system. The first wave included service conformance law, document/patch/transaction law, project graph law, composition resolver law, and doctrine recovery matrix. Each prompt included branch/worktree rules, path allowlists, non-goals, deliverables, targeted validators, evidence, and commit instructions. A later pasted transcript said Wave 1 was effectively complete and the next task should be `COMMAND-RESULT-VIEW-SLICE-01`.

### 2.7 Final state before preservation

By the end, the conversation had produced a complete continuity handoff and then this more detailed preservation request. The current working interpretation is that the next substantive Codex prompt should be `COMMAND-RESULT-VIEW-SLICE-01`. This task should prove that one command result can become a semantic view with multiple projections, using `dominium.validation.run` if possible, without building a full Workbench shell, rendered GUI, native GUI, module loader, package runtime, provider runtime, gameplay, renderer implementation, or release publication.

## 3. Main Topics Discussed

### Topic 1 — Dominium’s final architecture

Dominium’s final architecture was repeatedly refined. The strongest synthesis is that Dominium is not merely a game repo or a literal OS, but a deterministic, contract-governed simulation platform. Domino is the reusable substrate. Dominium is the game/product family. Workbench is the production and evidence environment. AIDE is the repo-control harness. Contracts are law. Tests, replay, diagnostics, and evidence are proof.

The topic came up because the project needed a model that could support world simulation, modding, tooling, Workbench, release, portability, and future games without repeating endless refactors. The conclusion was that stable contracts and semantic IDs must be separated from replaceable private implementation.

What remains uncertain is how quickly this architecture will move from contracts and fixtures into runtime implementations and product slices. The next chat should not assume runtime provider resolvers, package runtime, or Workbench shell exist.

### Topic 2 — Repository structure and root cleanup

The repo root cleanup dominated much of the conversation. The old root structure was visibly unacceptable and triggered intense user frustration. The conversation explored cautious moves, gates, root inventories, salvage maps, bulk routing, and deterministic quarantine. The final stance was that the root skeleton is now mostly settled and should not be re-litigated unless validators show a live violation.

The key outcome is the closed root set: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`, plus control roots like `.aide/` and `.github/`. Generated/local roots stay local. Old junk roots should not return.

### Topic 3 — Foundation Lock

Foundation Lock was the governance gate that determined whether narrow product work could begin. It initially blocked on dependency-direction strict validation. After repair, it reportedly closed with warnings. This topic matters because it marks the transition from infrastructure cleanup to narrow product slices.

It remains important not to misread Foundation Lock. It does not mean full CTest is green, broad Workbench exists, providers are implemented, or gameplay can start. It means the governance spine exists and narrow slices may proceed under its laws.

### Topic 4 — C17/C++17 and 64-bit mainline

The language policy shifted from historical C89/C++98 to C17/C++17. The mainline native architecture policy shifted toward 64-bit source-native: x86_64 and arm64. Public ABI remains C-compatible. Persisted formats must be fixed-width, explicit little-endian, and pointer-width independent.

This matters because it enables modern implementation patterns while preserving stable ABI and artifact compatibility. The risk is overusing C++17 library features that break macOS 10.9.5 or allowing `size_t`, `long`, raw pointers, or native layout to leak into save/replay/network/package formats.

### Topic 5 — Workbench

Workbench is a future product surface, not the center of authority. The user wants to get to Workbench and code soon, but Workbench must route through commands/services/views/evidence rather than private direct mutation. The first Workbench slice was narrow validation. The next needed bridge is command-result-view projection.

Workbench’s final shape is a shell hosting modules and workspaces. It eventually includes Project Graph Explorer, Interface Studio, Module/Pack Foundry, App Composer, Release Forge, Agent Work Board, Pack Browser, Renderer/Theme Laboratory, Replay/Trace Viewer, and related tools.

### Topic 6 — Commands, results, views, projections

This became the immediate next frontier. The system must avoid separate CLI, TUI, Workbench, rendered, native, and headless implementations of the same behavior. The next slice should prove a command result can become a semantic view projected across multiple surfaces, preserving the same result schema, refusal codes, diagnostics, and evidence.

### Topic 7 — Parallel Codex work

The user wanted to run many autonomous tasks concurrently. The assistant designed branch/worktree isolation and strict parallel-worker rules. Workers do not push to main, do not update global latest AIDE files, and produce task-local evidence. Coordinator merges serially and runs fast strict.

This topic matters operationally because the user wants speed. The new chat should be ready to generate more parallel prompts or a coordinator review prompt depending on current repo state.

### Topic 8 — Doctrine preservation

An uploaded transcript/audit said much of the old Dominium doctrine was preserved in repo canon, but some important areas remain partial: deep primitives, failure ontology, player-facing formalization workflows, ordinary life grounding, domain constitutions, playable-baseline hardening, and domain-by-domain verification. The doctrine recovery matrix was generated to prevent old requirements from being forgotten.

This matters for the eventual master Project Spec Book and future domain feature work.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted:
- to stop endless refactor churn,
- to make the repository tidy and future-proof,
- to preserve all old requirements and design decisions,
- to front-load autonomous Codex work in parallel,
- to get to Workbench and code as soon as possible,
- to avoid repeating explanations in new chats,
- to produce a comprehensive preservation package for this chat.

### 4.2 Inferred Goals

Reasonably inferred goals:
- minimize future architectural reversals;
- ensure assistants do not lose constraints;
- make Codex prompts operational rather than theoretical;
- preserve emotional and motivational context so future chats do not repeat slow, cautious patterns;
- build toward a master Project Spec Book.

### 4.3 Goals That Changed Over Time

The goal changed from:
```text
clean up the directory structure
```
to:
```text
close Foundation Lock and build governed product slices
```
to:
```text
parallelize autonomous contract/product-spine tasks
```
to:
```text
preserve this chat for future aggregation.
```

### 4.4 Goals Still Unresolved

Still unresolved:
- verify latest live repo state after user-pasted Wave 1 completion;
- generate/run `COMMAND-RESULT-VIEW-SLICE-01`;
- prove package mount, replay proof, barebones client shell;
- instantiate domain constitutions;
- stabilize playable baseline;
- build Workbench shell and tools;
- classify/fix full CTest/T4 debt;
- merge this chat with other old-chat reports into a master spec book.

## 5. Decisions Made and Why

### Decision overview

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | Dominium should be a deterministic contract-governed simulation platform, not merely a game repo. | final | Enables modularity, replacement, proof-driven development. | High | FACT |
| DECISION-02 | Domino is the reusable substrate; Dominium is the product family; Workbench is production environment; AIDE is control-plane harness. | final | Prevents Workbench/Dominium from becoming vague everything-platform. | High | FACT |
| DECISION-03 | Contracts are law; tests/replay/evidence are proof. | final | Docs explain, generated output is evidence unless promoted. | High | FACT |
| DECISION-04 | Path is not identity; implementation is not contract; UI is not authority; generated output is not source truth. | final | Stable IDs/contracts/registries/manifests own identity; paths are replaceable. | High | FACT |
| DECISION-05 | Keep the closed canonical source-root set. | final-with-caveats | No new top-level modules/plugins/services/sdk roots unless future contract introduces them. | High | FACT |
| DECISION-06 | Unknown files should not remain in bad roots; route to archive/quarantine rather than guess active ownership. | final for cleanup phase | Prevents unknown files blocking cleanup or being wrongly active. | Medium | FACT |
| DECISION-07 | Mainline language baseline is C17 + C++17, not C89/C++98. | final/live per checks | C-compatible public ABI remains; C89/C++98 becomes research/historical. | Medium | FACT/VERIFY |
| DECISION-08 | Full native products should be 64-bit source-native: x86_64 + arm64; 32-bit is constrained/projection/archive-runner. | decided, policy encoding pending/in-flight | Avoid old-toolchain/memory/matrix drag; keep pointer-width out of persisted law. | Medium | FACT/UNCERTAIN |
| DECISION-09 | Little-endian mainline with explicit little-endian persisted/protocol encodings. | decided | Avoid expensive big-endian support; formats are explicit. | Medium | FACT |
| DECISION-10 | Fast strict is normal dev gate; full CTest is T4/full-gate debt. | final | Prompts use targeted validators; full CTest only release/trust or specific need. | High | FACT |
| DECISION-11 | Foundation Lock gates narrow product work; broad feature work remains blocked. | final for current phase | Narrow slices allowed; not gameplay/renderer/native GUI/release. | High | FACT |
| DECISION-12 | Workbench must use registered commands/services/evidence, not private validators/tools. | final | Prevents Workbench from becoming authority or bypass. | High | FACT |
| DECISION-13 | Use parallel Codex worktrees with strict worker rules. | active decision | Speed up setup while limiting merge conflicts. | High | FACT |
| DECISION-14 | Wave 1 prompt set: service conformance, document/patch/transaction, project graph, composition resolver, doctrine recovery. | executed in chat; completion user-reported | Foundation hardening runs in parallel. | High | FACT |
| DECISION-15 | Next task after Wave 1 is COMMAND-RESULT-VIEW-SLICE-01. | current plan | Bridge command result to semantic view/projection before package mount. | Medium | FACT/UNCERTAIN |
| DECISION-16 | Do not start broad Workbench UI before command/result/view/projection law. | final for sequencing | Presentation spine first. | High | FACT |
| DECISION-17 | Composition is the product. | architectural decision | Apps compose profiles/packs/modules/providers/capabilities into lockfiles/evidence. | High | FACT |
| DECISION-18 | Doctrine recovery should map old doctrine to current canon rather than create a competing master doctrine. | final for doctrine phase | Preserve old requirements without overriding contracts. | High | FACT |
| DECISION-19 | Major game features must enter as domain constitutions/bridges/capabilities/representation/failure/proof, not ad hoc features. | future design law | Prevents shallow feature scripts and semantic drift. | Medium | FACT/INFERENCE |
| DECISION-20 | Do not put domino/dominium in every path; use project prefixes for public C symbols and fully qualified stable IDs. | final naming law | Short readable paths; collision-proof public symbols/IDs. | High | FACT |

### Decision explanation

The decisions above should be treated as the working canon of this chat. The strongest decisions are the architectural identity split, the contract/proof law, the closed root model, the C17/C++17 + C-compatible ABI baseline, fast strict as the normal gate, and the sequencing rule that Workbench/product work must be narrow and command/service/evidence-backed.

The most tentative decisions are those depending on current live repo state after the latest pasted transcript: Wave 1 completion, current queue state, and exact readiness for `COMMAND-RESULT-VIEW-SLICE-01`. These should be verified before action.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

- Manual drag/drop directory cleanup was rejected as dangerous, even though the user threatened it out of frustration.
- Tiny sequential micro-move waves were superseded by deterministic routing and later by governed parallel task work.
- C89/C++98 as mainline was superseded by C17/C++17.
- 32-bit full-native mainline was rejected/deprioritized in favor of constrained/projection/archive lanes.
- Literal OS framing was softened into deterministic simulation operating environment / platform.
- Workbench as authority was rejected.
- Top-level `modules/`, `plugins/`, `services/`, or `sdk/` roots were rejected for now.
- Full Workbench UI before command/view/projection spine was rejected.
- Full CTest as routine gate was rejected.
- Broad feature work before product/runtime spine was rejected.

## 7. Important Reasoning, Rationale, and Tradeoffs

The main tradeoff throughout was speed versus safety. The user wanted speed because the project had spent months in refactor; the assistant tried to preserve correctness by moving from cautious sequential gates to parallel but isolated worktrees.

Another tradeoff was governance versus product progress. Too little governance risks repeating the refactor disaster. Too much governance before product work risks stalling again. The compromise was Foundation Lock plus narrow product slices.

The C17/C++17 choice balanced modern implementation power against portability. The compromise was C++17 internally but C-compatible ABI and fixed-width persisted formats externally.

The 64-bit choice balanced modern platform practicality against legacy reach. The compromise was 64-bit full-native products while retaining 32-bit/vintage through constrained-native, contract-projection, or archive-runner lanes.

The Workbench plan balanced ambition against authority separation. Workbench should become powerful, but only as a command/evidence surface over contracts and services.

## 8. Plans, Future Work, and Next Steps

Immediate:
1. Verify live repo state.
2. If accurate, generate `COMMAND-RESULT-VIEW-SLICE-01`.
3. After completion, run `PHASE-REVIEW-02`.

Then:
1. `PACKAGE-MOUNT-SLICE-01`
2. `REPLAY-PROOF-SLICE-01`
3. `BAREBONES-CLIENT-SHELL-01`
4. `RUNTIME-SPINE-REVIEW-01`

Then:
1. `PRESENTATION-CONTRACT-01`
2. `PROJECTION-CONFORMANCE-01`
3. `ACCESSIBILITY-CONTRACT-01`
4. `TEXT-LOCALIZATION-CONTRACT-01`
5. `PRESENTATION-SPINE-REVIEW-01`

Then:
1. `WORKBENCH-SHELL-01`
2. `PROJECT-GRAPH-EXPLORER-01`
3. `PACK-BROWSER-01`
4. `AGENT-WORK-BOARD-01`

Hardening:
1. `COMPATIBILITY-CORPUS-01`
2. `PERFORMANCE-BUDGETS-01`
3. `ASSURANCE-PROFILE-00`
4. `RELEASE-PROMOTION-GATE-01`
5. `FULL-GATE-DEBT-01`
6. `POINTER-WIDTH-SERIALIZATION-AUDIT-01`
7. `GENERATED-SOURCE-LAW-01`

Doctrine/domain:
1. `SPEC-DEEP-PRIMITIVES-01`
2. `SPEC-FAILURE-ONTOLOGY-01`
3. `SPEC-PLAYER-FORMALIZATION-WORKFLOWS-01`
4. `SPEC-REPRESENTATION-PROOF-01`
5. `DOMAIN-CONSTITUTION-WAVE-01`

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user wants direct, evidence-grounded, audit-ready answers; timestamps/model labels; explicit uncertainty; no repeated clarification unless necessary; large continuous Codex prompt blocks when generating prompts; targeted tests instead of full suites; and rapid progress toward Workbench/code.

### 9.2 Inferred Constraints and Preferences

The user is likely to reject slow, report-only, overcautious process. Future assistants should produce executable next prompts quickly after verifying state.

### 9.3 Uncertain or Unestablished Preferences

It is uncertain how many concurrent Codex workers the user will actually run at once and whether the user wants coordinator prompts or worker prompts next.

## 10. Files, Artifacts, Outputs, and Prompts

Important artifacts include:
- current uploaded preservation prompt file;
- prior handoff text;
- Foundation docs/audits;
- language baseline docs;
- portability docs;
- Wave 1 generated prompts;
- proposed `COMMAND-RESULT-VIEW-SLICE-01` task;
- doctrine recovery matrix prompt;
- root cleanup/router prompts.

See Artifact Ledger for details.

## 11. Open Questions and Unresolved Issues

Key unresolved issues:
- latest live repo state;
- whether Wave 1 is merged;
- whether `PORTABILITY-ARCH-POLICY-02` completed;
- exact implementation state of Workbench validation slice;
- exact command/result schema for `dominium.validation.run`;
- current warning disposition;
- full CTest/T4 debt;
- doctrine gaps such as deep primitives and failure ontology.

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

The highest-risk misunderstanding is to restart root cleanup or broad planning instead of moving to `COMMAND-RESULT-VIEW-SLICE-01`. Another risk is assuming Workbench may call private validators directly. Another risk is treating user-pasted state as live without verification. A future assistant may also accidentally run full CTest or edit global AIDE latest files in a parallel worker.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat contributes:
- final architecture split;
- root cleanup to foundation transition;
- language/architecture baseline;
- Foundation Lock/governed product-slice model;
- parallel Codex workflow;
- Wave 1 task prompts;
- next product-spine plan;
- doctrine recovery strategy;
- user preferences and frustration context.

It should feed spec-book chapters on:
- Project Architecture,
- Repo Governance,
- Build/Language/Portability,
- Workbench,
- Command/View/Diagnostics,
- Composition/Providers/Packs,
- Testing/Proof,
- Doctrine and Domain Constitutions,
- Development Workflow.

## 14. What I Should Remember

- The next task is `COMMAND-RESULT-VIEW-SLICE-01` unless live repo says otherwise.
- Workbench is not authority.
- Commands/services/results/views/diagnostics/evidence are the bridge from governance to product.
- Foundation Lock is closed with warnings, not “everything complete.”
- Full CTest remains T4 debt.
- Broad feature work remains blocked.
- Parallel Codex workers must not edit global AIDE latest files.
- Old doctrine is mostly preserved but needs domain instantiation.
- The user wants speed, concrete prompts, targeted tests, and no repeated slow refactor cycles.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- “Explain why `COMMAND-RESULT-VIEW-SLICE-01` comes before `PACKAGE-MOUNT-SLICE-01`.”
- “What is the difference between Workbench module, workspace, service, provider, pack, and app?”

### 15.2 Decisions
- “Which decisions in this chat are final versus tentative?”
- “What would make us revisit the C17/C++17 or 64-bit decisions?”

### 15.3 Tasks and Next Actions
- “Generate the `COMMAND-RESULT-VIEW-SLICE-01` prompt.”
- “Generate `PHASE-REVIEW-02`.”
- “What should the coordinator do after merging Wave 1?”

### 15.4 Artifacts and Files
- “List all generated Codex prompts from this chat.”
- “Which files should a future assistant inspect first?”

### 15.5 Risks and Verification
- “What live repo facts must be verified before the next prompt?”
- “What could go wrong if Workbench bypasses registered commands?”

### 15.6 Future Spec Book / Aggregation
- “Convert this chat into spec-book chapter candidates.”
- “Merge this preservation package with another old-chat report.”

### 15.7 Deep-Dive Questions Specific to This Chat
- “What is the doctrine recovery matrix meant to preserve?”
- “How should deep primitives and failure ontology be turned into future specs?”
- “How do composition resolver, project graph, service conformance, and document/patch/transaction law fit together?”

## 16. Compact Human Summary

This chat was about the Dominium project’s transition from painful repo restructuring into a coherent, governed product-building phase. The project had spent a long time cleaning up a messy repo full of bad roots and partial systems. The user was frustrated by how slowly the cleanup moved and wanted to stop endlessly planning so Workbench and real code could begin. The assistant and user gradually converged on a model where directory structure matters, but stable contracts, IDs, commands, services, providers, modules, packs, artifacts, and proof matter more.

The final architecture is that Domino is the reusable deterministic/runtime substrate; Dominium is the game/product family; Workbench is the production and validation environment; AIDE is the repo/control harness; and Codex is a bounded patch executor. The most important rules are: path is not identity, implementation is not contract, UI is not authority, and generated output is not source truth. This protects the project from future folder-name mistakes and allows implementation replacement behind stable surfaces.

The repo was treated as having moved beyond broad root cleanup. Foundation Lock became the main governance gate. It was first blocked by dependency-direction strict validation, then reportedly closed with warnings after repair. Fast strict passed, CMake configure/build and smoke CTest passed through fast strict, and full CTest remained T4/full-gate debt. Narrow product slices became allowed, but broad Workbench UI, gameplay, renderer expansion, native GUI, runtime module/package/provider systems, and release publication remained blocked.

The conversation then shifted to a parallel Codex workflow. The user wanted multiple concurrent Codex chats working on isolated worktrees. The assistant created strict worker rules: no direct pushes to main, no editing global AIDE latest files, task-local evidence only, allowed path lists, targeted validators only, and local commits on task branches. Five Wave 1 prompts were generated: service conformance law, document/patch/transaction law, project graph law, composition resolver law, and doctrine recovery matrix. A later transcript said these were effectively complete, along with a narrow Workbench validation slice.

The next correct task is `COMMAND-RESULT-VIEW-SLICE-01`. It should prove that one registered command result can become a semantic view and be projected consistently across CLI/headless/text/TUI/Workbench-style surfaces. It should use `dominium.validation.run` if possible. It must preserve the same command, result schema, refusal codes, diagnostics, and evidence packet. It must not implement a full Workbench shell, rendered GUI, native GUI, runtime view engine, module loader, package runtime, provider runtime, gameplay, renderer implementation, or release.

The chat also preserved long-running Dominium doctrine: deterministic law, Truth/Perceived/Render separation, sparse materialization, representation ladders, semantic ascent/descent, formalization chains, cross-domain bridges, process-only mutation, pack-driven integration, explicit refusal/degradation, ordinary life, institutions, and civilization-scale simulation. The remaining doctrine gaps are deep primitives, failure ontology, player-facing formalization workflows, domain constitutions, and playable-baseline hardening.

The most important continuation is: verify current `origin/main`, confirm Wave 1 and Workbench validation state, then generate or run `COMMAND-RESULT-VIEW-SLICE-01`.
