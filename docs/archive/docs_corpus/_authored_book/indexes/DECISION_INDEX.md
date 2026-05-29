Status: DERIVED
Last Reviewed: 2026-05-29
Supersedes: docs/archive/docs_corpus/_integrated_book_v2/**
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Decision Index

- Domain permissions + existence/refinement - visitability decision.
- Travel scheduling, replay, and law decisions become nondeterministic.
- Calendars are pure renderers and never affect physics.
- HPC-E Year Day and Leap Day are appended after February; canonical mode is undated and compatibility mode may use Feb 29/30.
- Adopt base-16 spatial ladder from subnano to surface.
- Store surfaces as sparse microgrids/chunks, not continuous dense arrays.
- Support canonical surface plus multiple surface instances for shards/mirrors.
- Final support tiers are user-defined and must be preserved.
- See through . Strongest user-stated decisions: science-bounded procedural planets, robotic mothership premise, robot bodies, nanobot construction, automation over worker NPCs, mothership-limited fabrication, machine process.
- Which decisions are confirmed versus recommendations?
- Review decisions with uncertainty labels, then formalise the vertical slice.
- The key technical conclusion was that the world cannot be treated as a normal game-engine level full of live actors. The world must be a deterministic simulation and data system first. Domino should store the true universe as seeds, rules, fields, sparse.
- This preservation package explains the chat, records decisions, tasks, artifacts, risks, and open questions, and exports a structured spec/aggregation packet for future merging.
- Additional points: DDAP/DIL is proposed; repo not inspected; conformance tests prove modularity; data compatibility must be formalized; generated output needs validation; future aggregation must preserve recommendation-vs-decision labels.
- The most important repo-supported decision is that Dominium authority must remain logical ACT, not wall-clock. The strongest recommendations are to freeze ACT units/serialization, audit DSYS timers, and keep civil time as projection-only.
- Which repo files supported the Dominium conclusion?
- The answer distinguished system width from time representation. The important conclusion was that 2038 is caused by signed 32-bit time counters reaching their maximum representable value. The risk appears where signed 32-bit Unix-style timestamps are.
- Main decision candidates: custom deterministic core; Unreal as frontend only; server-authoritative MMO state; sparse procedural planets; single universe via partitioning; Domino as future adapter.
- The conclusion was not to globally simulate everything. Instead, the architecture should support deterministic lazy historical evaluation.
- '': What disposition should be chosen for this unresolved claim: Future work must define the client's allowed dependency surface and whether it can access any simulation-adjacent prediction layer.?
- The conclusion was not a finalized implementation but a working architecture: each simulation domain should be deterministic, fixed-point, content-driven, versioned, replayable, and integrated through clear read/write boundaries.
- This context matters because the rest of the conversation happened inside those constraints. The launcher could not become a dumping ground for OS-specific behavior, sim mutation, renderer decisions, or nondeterministic game-state changes. It had to fit.
- The idea is attractive because it supports broad distribution and long-term extensibility. But it is not a final decision. Dynamic plugins introduce ABI, packaging, security, and platform restrictions. Static registration may be simpler. A hybrid may be.
- A large set of prompts was then generated to lock down architecture, determinism, performance, schema governance, rendering, epistemic UI, sharding, interest sets, and fidelity projection. This became the Phase 1 hardening layer. Additional audit prompts.
- The final state of the conversation is therefore: the architecture and implementation-roadmap discussion has been preserved, but the actual next work is elsewhere-especially the Path D advanced simulation conversation.
- The most important conclusion is that determinism is central. Systems are repeatedly specified to avoid hidden randomness, OS timers, platform dependence, uncontrolled floating point, and runtime allocation during simulation ticks. The visible rationale.
- A central decision was to separate the project into two conceptual layers. Domino is the reusable engine layer: platform abstraction, renderer abstraction, audio, UI, core services, package/instance management, simulation control, events, plugins.
- The visible conclusion was that the engine has real deterministic substrate pieces, but these must be hardened through small playable slices and proof/replay tests. Determinism is not only a mathematical preference; it enables multiplayer authority.
- There was also an early suggestion to create a 'DUI' facade, a Dominium UI abstraction, to support native widgets and fallback rendering. This idea was useful as a conceptual stepping stone but was not ultimately locked as a final requirement in the form.
- The conversation implies a goal of turning Dominium into a long-lived product-line platform rather than a single-game repository. It also implies a desire for auditability: decisions should be grounded, visible, mechanically enforceable, and later.
- The final strategic direction before this preservation request was to run a ?-series: snapshot intake, reality extraction, blueprint reconciliation, foundation readiness, and final prompt synthesis. This is needed because plans must now be mapped onto.
- A major middle phase focused on XStack. XStack began as a Dominium-specific governance stack grown out of TestX, then expanded into RepoX, AuditX, and other concepts. We initially explored making XStack a general portable metaharness, but that proved too.
- The final plan accepted the newer repo structure is clean enough to stop giant structure prompts. Remaining cleanup should be targeted: stale full-gate tests, pack layout canon, residual taxonomy, AIDE state classification, public header ABI.
- Safe now: archive reading, decision review, promotion review, reconciliation crosswalks, docs-only microtask preparation, and validators.
- Most important: actual repo structure, existing GPT-5.2 refactor plan contents, final Q formats, orientation representation, grid assumptions in current code, microsegment length, packing VM instruction set, bridge/tunnel ownership, and checksum rules.
- How are 'DOMINIUM RUN ROOT' and 'DOMINIUM HOME' finalized?
- The final UI/UX synthesis connects directly to that premise. The interface should feel like a robot operating system. The player boots into an OS, connects to a universe, downloads consciousness into a fabricated robot body, and disconnects into.
- Read file 01 first if you want to understand what happened. Read file 04 if you need tasks and decisions. Read file 05 if merging into a master Project Spec Book. Read file 07 before treating external support claims as implementation truth.
- Ask: "What decisions are final?", "What is still uncertain?", "What is the next prompt?", "Which rejected options should we avoid?", "What should go into the master spec book?".
- All platform interaction must go through dsys. (FACT).
- Verify actual repository state, then execute or audit the generated "Dominium Setup: Final Spec Alignment, Gap Closure, and Hardening Pass" prompt.
- Which ideas are final decisions and which are recommendations?
- Final active plan is the 9-prompt pack, not earlier superseded plans.
- Use: design intent, review backlog, decision and promotion candidates.
- Decision items are review prompts. The default disposition is defer unless a later explicit task opens the scope.
- Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.
- Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.
- Renderer selection follows the standard policy: explicit selection fails loudly when unavailable, and auto selection logs the chosen backend.
- '--format' is accepted only for 'inspect' and 'validate'.
- Non-canonical command accepted as legacy path.
- Logs must record control decisions and reasons.
- From law decisions and recorded in audit logs.
- 'manifest relpath' is the final tie-breaker and MUST be relative to the.
- The final world MUST be identical regardless of physical execution order,.
- Parallel execution is a backend choice, not a gameplay decision. Different.
- Produce audit records for provenance and law decisions.
- Authoritative writes are committed only after a law gate decision at commit.
- Record law decisions, effects, and rationale.
- If a component is not applicable for a given subsystem, it MUST be encoded into the provided base seed so that the final derived seed still matches the canonical rule.
- The descriptor does not own the implementation of those services. Runtime services remain governed by service/provider law. Pack activation remains governed by package and trust law. Module enablement remains governed by module law and the composition.
- ROI expand/collapse decisions therefore depend on deterministic tick order, not wall-clock cadence.
- No wall-clock input is used in anti-cheat decisions.
- Required policy: primary plus secondary mirror, with offline cold storage recommended.
- Date: 2026-03-05 Scope: CHEM-4 phases 0-9 completion (stress envelope, deterministic degradation, conservation verification, proof/replay, regression lock, enforcement, TestX, final baseline).
- Date: 2026-03-05 Scope: CHEM-3 phases 11-12 completion (TestX coverage, gate validation, final baseline report).
- Date: 2026-03-05 Scope: CHEM-1 phases 7-10 completion (proof/replay, enforcement, tests, final baseline report).
- Requests compute units per capsule eval and emits compute decision/consumption outputs.
- 'control decision log' schema shape unchanged ('extensions' open-map used for IR metadata).
- Decision logs are emitted per control resolution under.
- This baseline hardens the control plane as the sole interaction gateway and locks regression behavior for control decisions, fidelity arbitration, and replay-safe execution.
- 3. Replace control-plane inline downgrade logic with kernel invocation. 4. Replace MAT-9 fidelity fallback with kernel negotiation result (no inline downgrade policy). 5. Replace MAT-7 budget truncate decision path with kernel arbitration output (engine.
- Omega-5 must not alter install-profile resolution, trust policy, migration decisions, or yanked-selection behavior.
- All degradation decisions are logged with deterministic decision IDs.
- Chosen provider capabilities flow into CAP-NEG and may drive explicit degrade/refuse outcomes.
- Route non-Euclidean distance/neighbor decisions outside the local solver through GEO APIs.
- Replay verification compared a selected marker's stored replay hash directly against the final full-state replay hash.
- Proof hash chains present (emission, field, exposure, compliance, decision/degrade).
- Date: 2026-03-05 Scope: CHEM-2 phases 8-11 completion (proof/replay, enforcement, TestX, final gate report).
- Explicit refusal path accepted for intentional stubs.
- There is no equivalent deterministic replay surface yet for LIB save-open policy decisions, and no envelope report tying provider resolution, pack verification, save open, and bundle verification together.
- Conclusion: LOGIC wiring must specialize 'NetworkGraph', not replace it.
- Conclusion: LOGIC-4 should evaluate these data-defined models directly and must not introduce engine-owned special gate objects.
- Stress summaries expose 'recommended speed cap permille' for downstream speed capping via Effects.
- Release index, component graph, and install plan canonicalizers assume current semantics without emitting a migration decision record.
- Conclusion: capability declarations can be introduced through manifest data and validated without runtime code edits.
- Final composite hash anchor is identical.
- Canonical release comparison used host-meta-normalized hashes only; no platform-specific degrade decision entered the truth-facing artifact set.
- Expected Result: 'replaying from the baseline seed reproduces the same final anchor as reload'.
- 'session begin' binds the connection to the chosen contract bundle hash and pack lock hash.
- The blueprint is ready for final snapshot-driven planning.
- POLL-0 must preserve null boot behavior with explicit 'poll.policy.none' and empty registries accepted.
- Dispatches via SIG channel when available; deterministic degrade decision when unavailable.
- All degrade actions emit decision/event rows and preserve canonical emission totals.
- Emits canonical capsule generation record rows and decision metadata.
- All degrade decisions are written through deterministic decision/event rows in the harness state.
- Ready for 'RELEASE-3' final pre-DIST freeze.
- Inference jobs are budgeted by policy ('max inference jobs per tick') and can be deferred with logged decisions.
- Decision influence is recorded ('DecisionLog' rows and 'mobility signal control decisions').
- Crash handling captures a diag bundle before restart decisions are evaluated.
- Introduce causality checks that forbid future-receipt references in control/schedule decisions.
- All degrade decisions emit DecisionLog rows and RECORD artifacts.
- Emits deterministic decision log entries for both verify-claim and trust-update paths.
- 'setup rollback' restores from the recorded backup path chosen by the transaction log and appends a deterministic 'update.rollback' transaction.
- XI-5A Preflight Disaster Cleanup Fix Final.
- No src-domain mapping lock, approved layout, repository structure decision, runtime code path, or semantic contract was changed.
- Recommended next phase: 'Xi-5x2' focused on legacy source pockets, content-source policy, and blocked external-project residuals.
- Categories: appshell.ad hoc entry point smell=2, arch.duplicate semantic engine smell=6, architecture.adhoc speed limit smell=1, architecture.adhoc valve smell=1, architecture.affordance gap smell=317, architecture.architecture drift smell=1.
- 'RUN META' content is never used for determinism decisions.
- No halting mechanical blockers were accepted; failures are tracked for remediation and regression locks.
- Identity and integrity canonical artifacts were refreshed during this finalization.
- Update call sites and includes to the chosen canonical implementations, then rerun review and STRICT validation.
- XI-5 readiness conclusion: 'can proceed as bounded XI-5a under the approved lock contract'.
- Distribution sampling must be deterministic for identical inputs, including budget truncation decisions.
- Commitments are strongly recommended and required for process families that already define commitment artifacts (construction, logistics, maintenance), but missing commitment does not globally refuse all macro changes.
- Deterministic base decision + deterministic risk uplift from batch/process quality severity.
- Candidate references to compiled models are accepted only when COMPILE artifacts include valid equivalence proof and validity-domain bindings.
- "North/South" is defined only by the chosen coordinate frame.
- Provenance record: identifiers for inputs, models, and decisions.
- Refinement must preserve deterministic final output.
- Audit/provenance traces for model evaluation decisions - 'RECORD'.
- Replay from genesis and replay from any accepted compaction anchor must converge to identical TruthModel state hash.
- If a transcript summary claims a decision that is not visible in the repo, the next prompt must treat it as advisory and either.
- 2) Remains are registered with the decay scheduler. 3) Observation hooks emit a death/remains notice for epistemic systems. 4) Salvage claims resolve deterministically via rights order. 5) Accepted salvage produces ledger transactions and provenance records.
- Launcher integration flags are accepted but not required: '--launcher- ' (ignored by the game runtime unless explicitly wired).
- Profiling MUST NOT use wall-clock time for any authoritative decision.
- All of the following must pass before Omega-11 signoff is accepted.
- DIST-5 defines the final user-facing polish bar for 'v0.0.0-mock'. It does not add features. It standardizes help text, menu wording, refusals, and status output across CLI, TUI, rendered UI, and optional native adapters.
- Series Scope: repo-structure discovery and design Series Role: authoritative pre-relayout validation, decision, and packaging checkpoint for the completed repo-structure series; downstream of stronger canon, the six repo-structure packets, post-Zeta.
- Full repository finalization remains incomplete because deeper schema, runtime, Workbench, and test taxonomy debt is still active and needs focused routing tasks with compatibility review.
- This pass continued canonical structure convergence after CANON STRUCTURE FINALIZE NOW 01. It was limited to structure, naming, ownership, validator, generated-map, and proof cleanup. It did not implement runtime, product, Workbench, renderer, native.
- Previously landed route decisions remain correct in the active tree.
- CONVERGE-00 through CONVERGE-12 established a machine-readable source layout authority, root allowlist, exception ledger, distribution projection contract, component matrix contract, physical convergence for low-risk roots, and final stale-document audit.
- The router consumes the post-CONVERGE root set, NAME-00 naming canon, layout exceptions, root-recycling runbook, MOVE-BULK batch sequence, RESTRUCTURE-REPAIR-00 final root matrix, and prior MOVE-BULK evidence.
- POST-CONVERGE-12 stopped before projection tooling discovery or output generation because POST-CONVERGE-11 is blocked and not accepted as sufficient input for portable projection.
- The accepted portable projection input is.
- This sweep applied the user-directed structure cleanup where it could be done without creating a new authority model or claiming unimplemented runtime features. It kept the accepted top-level root model intact and focused on active path debt that could.
- The fast tier found and fixed an AIDE self-test writer compatibility issue before final validation.
- Recommended next task: 'AIDE-MOVE-02-REFINE - Identify Second Low-Risk Candidate'.
- Engine, game, contracts, content, docs, tests, tools, and release roots were routed toward the final ownership grammar.
- MOVE-BULK-08 closes the current wave as a blocker snapshot, not a clean final retirement.
- The repository is not yet ready for final proof. The build-triggered broader TestX suite still has 140 failures, and RepoX ruleset discovery remains stale.
- Every terminate/refuse decision must have matching event + action artifacts.
- Must not inject nondeterministic decisions into protocol acceptance/refusal logic.
- Unsigned artifacts accepted without warning escalation.
- License capability artifacts are only accepted when signature verification succeeds under trusted official roots.
- Agent Work Board features may create, inspect, compare, and review transactions. They must show status, dry-run result, diagnostics, refusal refs, affected documents/artifacts, and evidence refs. They must not silently write source truth or package.
