Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: immediate post-first-wave checkpoint, later bounded `Ζ-A`, later broader `Ζ`
Replacement Target: later bounded runtime-cutover, post-first-wave checkpoint, and broader `Ζ` doctrine may refine procedures and evidence structures without replacing the proof-only rehearsal semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PRE_ZETA_ADMISSION.md`, `docs/planning/CHECKPOINT_C_ZETA_A_ADMISSION_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZP.md`, `docs/planning/ZETA_BLOCKER_RECONCILIATION.md`, `docs/planning/LIVE_OPERATIONS_PREREQUISITE_MATRIX.md`, `docs/planning/ZETA_EXECUTION_GATES.md`, `docs/runtime/DISTRIBUTED_AUTHORITY_FOUNDATIONS.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/runtime/ROLLBACK_BEARING_STAGED_TRANSITION_VALIDATION.md`, `docs/runtime/DISTRIBUTED_REPLAY_AND_PROOF_ANCHOR_VERIFICATION.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`, `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`, `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `server/net/dom_server_runtime.h`, `server/net/dom_server_protocol.h`, `server/shard/dom_shard_lifecycle.h`, `server/shard/dom_cross_shard_log.h`, `data/registries/net_replication_policy_registry.json`, `data/registries/provenance_classification_registry.json`, `data/registries/provenance_event_type_registry.json`

# Dominium Bounded Runtime Cutover Proof Rehearsal

## A. Purpose And Scope

This doctrine exists because the post-`Ζ-P` checkpoint admitted `bounded_runtime_cutover_proof_rehearsal` only with tighter proof-only guardrails.

It solves a specific problem: Dominium now has a reconciled blocker baseline, a prerequisite matrix, a frozen execution-gate model, one first bounded `Ζ-A` family for rollback-bearing staged transition validation, and one proof-only distributed replay and proof-anchor verification family. Those layers admit bounded cutover-proof rehearsal narrowly, but they do not yet freeze what this family constitutionally is, what counts as rehearsal rather than realization, what evidence it may produce, and what open blockers it must never pretend to close.

Without one explicit doctrine, later bounded work could drift into:

- cutover rehearsal treated as live cutover
- proof-bearing rehearsal treated as operational readiness
- bounded first-wave work expanding into authority handoff, state transfer, live shard relocation, or trust/publication realization
- hotswap or distributed-authority doctrine being bypassed by convenience
- one rehearsal harness, trace stream, or tool report becoming architectural canon

This artifact governs:

- what bounded runtime cutover means in this first-wave context
- what proof rehearsal means in this family
- what rehearsal classes and evidence classes belong in scope
- what blocker posture and guardrails remain binding
- what later checkpoints and later bounded `Ζ-A` families must consume rather than reinvent

This artifact does not implement:

- live cutover systems
- shard relocation or state-partition transfer
- production failover
- trust execution systems
- publication execution systems
- live receipt pipelines

Checkpoint relation:

- `Ζ-P0` froze the canonical blocker baseline
- `Ζ-P1` froze the family-level prerequisite matrix
- `Ζ-P2` froze this family as `admitted_with_cautions`
- `C-ZETA_A_ADMISSION_REVIEW` tightened the guardrails to rehearsal-only, proof-only, non-live work
- `Ζ-A0` froze the bounded validation model
- `Ζ-A1` froze the proof-only distributed replay and proof-anchor verification model that this family must remain compatible with

This is a bounded rehearsal doctrine, not live runtime execution.

## B. Core Definition

In this bounded first-wave context, `bounded runtime cutover` means a governed runtime-adjacent boundary candidate in which lifecycle posture, realization identity, checkpoint horizon, replay horizon, or bounded version-bearing runtime posture may change across a declared cutover-sensitive window without claiming that lawful live runtime cutover has actually occurred.

`Proof rehearsal` in this family means the constitutional act of rehearsing whether a bounded cutover candidate would satisfy declared lifecycle legality, state externalization, replay intelligibility, snapshot legality, hotswap-boundary compatibility, distributed-authority-boundary compatibility, operator transaction posture, and generalized receipt continuity requirements, while remaining explicitly non-live and non-realized.

This family differs from nearby concepts:

- `live runtime cutover realization`
  - live realization would claim that the boundary was crossed lawfully in actual runtime posture; this family only rehearses proof obligations
- `distributed state transfer realization`
  - state transfer remains outside this family, even if rehearsal packets discuss why transfer would matter later
- `trust or publication execution realization`
  - trust-aware or publication-aware conditions may constrain rehearsal, but no trust or publication execution is realized here
- `ordinary rehearsal or dry-run`
  - ordinary rehearsal may show that a path was exercised; this family requires cutover-legality meaning, stronger proof packets, and explicit first-wave non-realization markers

The critical distinction is explicit:

- doctrine defines the meaning of this family
- admission allows the family to be attempted inside first-wave bounds
- rehearsal produces bounded proof or refusal outputs
- realization remains outside this family

## C. Why This Family Is Admitted Only With Proof-Only Guardrails

This family is admitted only with proof-only guardrails because it reduces a central blocker through rehearsal discipline rather than through live runtime movement.

The repo already contains meaningful precursor substrate:

- `server/net/dom_server_runtime.h` freezes checkpoint, recovery, shard lifecycle, shard version, capability mask, baseline hash, event, and cross-shard message-log surfaces
- `server/net/dom_server_protocol.h` freezes checkpoint, recover, shard lifecycle, rolling-update, resync, and refusal event classes
- `server/shard/dom_shard_lifecycle.h` freezes explicit shard lifecycle transitions among initializing, active, draining, frozen, and offline states
- `server/shard/dom_cross_shard_log.h` freezes deterministic cross-shard message ordering and hashable continuity surfaces
- `docs/runtime/HOTSWAP_BOUNDARIES.md` freezes that live replacement legality is never inferred from coexistence or convenience
- `docs/runtime/DISTRIBUTED_AUTHORITY_FOUNDATIONS.md` freezes that hotswap is not distributed handoff and authority transfer remains separately governed
- `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md` freezes stronger evidence requirements for cutover-shaped transitions

That substrate is enough to justify proof-bearing rehearsal.
It is not enough to justify claims that:

- live runtime cutover is realized
- distributed authority movement is lawful
- deterministic replication is proven
- live cutover receipt-pipeline realization is complete
- distributed trust convergence or live trust/publication execution are operational

This family is therefore first-wave admissible only because it can remain:

- rehearsal-only
- proof-only
- bounded
- rollback-aware
- non-live
- non-transfer-bearing
- subordinate to the still-open blocker field

The governing caution is strict:

- cutover rehearsal is not live cutover realization
- proof-bearing rehearsal is not operational readiness
- evidence exists is not blocker resolved
- first-wave admission is not broader `Ζ` readiness

## D. Rehearsal Classes In Scope

The following rehearsal classes define what this family may lawfully produce.

### 1. Bounded Cutover Proof Rehearsal

Rehearses whether a bounded cutover candidate preserves the declared proof obligations needed for a later lawful cutover claim while remaining non-live.

### 2. Hotswap-Boundary-Aware Rehearsal

Rehearses whether a candidate respects declared hotswap-boundary legality, including lifecycle posture, state externalization, replay continuity, and refusal posture.

### 3. Distributed-Authority-Boundary-Aware Rehearsal

Rehearses whether a candidate stays inside distributed-authority boundary law without claiming authority handoff, state transfer, or convergence realization.

### 4. Rollback-Bearing Cutover Rehearsal

Rehearses whether a cutover-shaped candidate remains rollback-aware, refusal-aware, and reconstructable under first-wave bounds.

### 5. Blocked Or Refusal Rehearsal Outcome

Records that the rehearsal result is blocked, partial, insufficient, out of scope, or otherwise not lawfully supportive of stronger cutover language.

### 6. Proof-Only Non-Realization Rehearsal

Rehearses whether the packet itself preserves explicit non-realization markers so the family cannot silently widen into live cutover or broader distributed live-ops realization.

## E. Evidence And Proof Classes

This family recognizes the following high-level evidence and proof classes.

### 1. Cutover-Proof Evidence

Evidence showing the bounded cutover claim, its declared horizon, its proof packet, and the exact scope of what was or was not rehearsed.

### 2. Lifecycle Legality Evidence

Evidence showing whether lifecycle posture across the rehearsal horizon remains explicit, legal, and non-contradictory.

### 3. Replay And Snapshot Compatibility Evidence

Evidence showing whether the candidate preserves replay intelligibility, checkpoint intelligibility, and snapshot legality across the rehearsal boundary.

### 4. Continuity Mismatch Evidence

Evidence showing that the rehearsal exposed incompatible continuity claims, ambiguous restarts, hidden state, or non-reconstructable runtime posture.

### 5. Receipt And Provenance Linkage Evidence

Evidence showing whether operator-transaction, generalized live-cutover receipt, and provenance posture remain reconstructable where required.

### 6. Refusal Evidence

Evidence that the correct outcome is refusal, blocked posture, partial posture, or insufficiency rather than affirmative cutover-legality language.

### 7. Out-Of-Scope Evidence

Evidence that a rehearsal packet drifted into live runtime swap claims, authority handoff, transfer, trust execution, publication execution, or other later-wave territory.

## F. Relationship To Blocker Baseline

This family is allowed to work under the active blocker baseline.

It may operate while all of the following remain unresolved:

- runtime cutover proof under lawful hotswap and distributed-authority boundaries
- distributed replay and proof-anchor continuity realization
- live cutover receipt-pipeline realization
- deterministic replication and state-partition transfer proof
- distributed trust and authority convergence realization
- live trust, revocation, and publication execution realization

This family may contribute bounded evidence toward:

- sharper cutover-legality criteria
- sharper lifecycle-sensitive refusal criteria
- stronger proof-packet obligations for later cutover work
- stronger receipt and provenance expectations for later cutover-shaped families

This family must not claim to resolve:

- runtime cutover realization
- runtime cutover proof itself
- deterministic replication realization
- state-partition transfer realization
- distributed replay and proof-anchor continuity realization
- distributed trust convergence realization
- live trust, revocation, or publication execution realization
- live cutover receipt-pipeline realization

The governing rule is simple: this family may rehearse inside the blocker field; it may not rename that blocker field as solved.

## G. Relationship To Runtime Doctrine

This family must remain fully compatible with runtime doctrine.

Therefore:

- lifecycle legality remains binding
- state externalization remains binding
- replay intelligibility remains binding
- snapshot legality remains binding
- isolation law remains binding
- coexistence law remains binding
- hotswap boundaries remain binding
- distributed-authority foundations remain binding

The concrete runtime consequences are:

- no rehearsal packet may hide truth in undocumented local state
- no rehearsal packet may erase lifecycle posture distinctions such as active, quiescent, suspended, degraded, blocked, stopped, failed, draining, frozen, or offline
- no rehearsal packet may present `checkpoint`, `recover`, `set_shard_state`, `set_shard_version`, or rolling-update substrate as if lawful live cutover were already solved
- no cutover-proof rehearsal may rewrite an undeclared restart, restart-required transition, or hidden authority movement as lawful cutover

This family may rehearse cutover-proof obligations.
It must not overclaim runtime realization.

## H. Relationship To Release/Control-Plane Doctrine

This family must remain compatible with:

- operator transaction doctrine
- generalized live-cutover receipt and provenance doctrine
- trust-transition prerequisite doctrine
- publication and trust execution operationalization gates
- release contract profile
- release-index and resolution semantics
- archive and mirror continuity doctrine

The governing consequences are:

- generalized receipts remain upstream wherever a rehearsal packet touches a boundary-sensitive transition candidate
- exact release identity, target context, and operator posture remain reconstructable where relevant
- archive presence, mirror visibility, logs, local traces, and CI output are insufficient as canonical cutover-proof evidence
- rehearsal packets must preserve explicit non-live, non-realized, and bounded-scope markers

This family therefore composes with release/control doctrine without implying realized publication or trust execution.

## I. Relationship To Trust And Revocation Continuity

This family may rehearse trust-relevant bounded continuity conditions only where the work stays proof-only and non-realized.

It may therefore examine, within first-wave limits:

- whether a cutover-shaped candidate depends on declared trust posture
- whether trust or revocation posture introduces an explicit refusal condition
- whether trust-sensitive continuity cannot honestly be preserved under the bounded rehearsal packet

It must not claim:

- live trust realization
- live revocation realization
- distributed trust convergence realization
- publication execution realization

Trust-aware rehearsal is therefore permitted only as bounded continuity-sensitive evidence work.
Trust realization remains outside this family.

## J. Invalidity And Failure

Rehearsal outcomes in this family may be explicit failures or refusals.

The canonical invalidity and failure categories are:

- `proof_only_scope_expanded`
  - the work drifted into live cutover, transfer, convergence, or execution claims
- `lifecycle_incoherent`
  - lifecycle posture across the rehearsal horizon is contradictory, hidden, or non-legal
- `replay_or_snapshot_incoherent`
  - replay or snapshot posture is insufficient to support the rehearsal claim
- `continuity_mismatch_detected`
  - continuity expectations conflict with declared runtime, receipt, or boundary posture
- `proof_insufficient`
  - the rehearsal packet is too weak to support a lawful cutover-proof claim
- `receipt_or_provenance_link_missing`
  - canonical operator or generalized receipt/provenance linkage is absent where required
- `trust_or_revocation_overclaim`
  - rehearsal packet silently turned into trust or revocation realization language
- `non_canonical_or_local_only_evidence`
  - only local traces, dashboards, or harness-local evidence were provided
- `out_of_scope_for_first_wave`
  - the candidate belongs to later-wave, blocked, or future-only families instead
- `inconclusive_or_blocked`
  - the rehearsal packet is insufficient to support either affirmative bounded rehearsal conclusions or a narrower lawful conclusion

## K. Canonical Vs Derived Distinctions

Canonical rehearsal truth for this family lives in:

- this doctrine
- the upstream checkpoint, blocker, matrix, gate, `Ζ-A0`, and `Ζ-A1` doctrine stack
- canonical rehearsal packets, refusal packets, and bounded proof packets later defined under this doctrine
- canonical operator transaction and generalized receipt records where relevant

Derived surfaces include:

- dashboards
- local traces
- ad hoc harness output
- logs
- mirror or publication views
- filenames
- convenience summaries

Derived surfaces may assist investigation.
They must not redefine rehearsal truth.

## L. Ownership And Anti-Reinvention Cautions

All ownership and projection cautions remain binding.

In particular:

- `fields/` remains distinct from `field/`
- `schema/` remains distinct from `schemas/`
- `packs/` remains distinct from `data/packs/`
- `specs/reality/` remains canonical over `data/reality/`
- `docs/planning/` remains canonical over `data/planning/`
- canonical runtime and release doctrine remain distinct from projected, generated, or tooling-local views
- stale numbering or titles do not override active checkpoint law

This family must be extracted from active doctrine and live repo evidence.
It must not be invented greenfield and must not be widened by convenience because checkpoint, lifecycle, or protocol substrate happens to exist.

## M. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- rehearsal treated as realization
- proof-bearing rehearsal treated as operational readiness
- runtime substrate presence treated as cutover-legality proof
- bounded first-wave used to smuggle in authority handoff, state transfer, or live shard relocation
- unresolved blockers silently treated as solved
- local traces or one rehearsal harness treated as architectural canon
- first-wave admission rewritten as broader `Ζ` readiness

## N. Stability And Evolution

This doctrine is `provisional`.

Later consumers include:

- `C-POST_ZETA_A_FIRST_WAVE_REVIEW`
- later bounded `Ζ-A` family doctrine prompts
- later broader `Ζ` planning that must preserve rehearsal versus realization distinctions

Update discipline:

- later prompts may refine rehearsal criteria, refusal vocabulary, or proof-packet shapes
- later checkpoints may narrow this family further if first-wave evidence shows that admission was still too broad
- no later prompt may widen this family into live cutover realization, transfer realization, trust execution, publication execution, or broader distributed live operations without an explicit later checkpoint and doctrine update

## O. Explicit Answers For Later Consumers

- Bounded runtime cutover proof rehearsal in Dominium is the proof-only rehearsal of whether a cutover-shaped runtime boundary candidate would satisfy declared lifecycle, replay, snapshot, receipt, hotswap, and distributed-authority constraints while remaining explicitly non-live.
- This family is proof-only and caution-gated because it reduces the runtime cutover blocker through rehearsal discipline rather than through live runtime movement, while runtime cutover realization, distributed replay continuity realization, trust convergence, and live receipt-pipeline realization remain unresolved.
- In-scope rehearsal classes include bounded cutover proof rehearsal, hotswap-boundary-aware rehearsal, distributed-authority-boundary-aware rehearsal, rollback-bearing cutover rehearsal, blocked or refusal rehearsal outcomes, and explicit non-realization rehearsal.
- This family does not realize live runtime cutover, deterministic replication, state-partition transfer, distributed trust convergence, live trust/revocation/publication execution, or live cutover receipt-pipeline realization.
- It enables the immediate post-first-wave checkpoint and later bounded `Ζ-A` families to consume one explicit proof-only cutover rehearsal model instead of inventing one ad hoc.
