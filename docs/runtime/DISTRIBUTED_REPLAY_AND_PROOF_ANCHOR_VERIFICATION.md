Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: `Ζ-A2`, immediate post-first-wave checkpoint, later bounded `Ζ-A`, later broader `Ζ`
Replacement Target: later bounded distributed continuity, cutover-proof, and post-first-wave checkpoint doctrine may refine procedures and evidence structures without replacing the proof-only verification semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PRE_ZETA_ADMISSION.md`, `docs/planning/CHECKPOINT_C_ZETA_A_ADMISSION_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZP.md`, `docs/planning/ZETA_BLOCKER_RECONCILIATION.md`, `docs/planning/LIVE_OPERATIONS_PREREQUISITE_MATRIX.md`, `docs/planning/ZETA_EXECUTION_GATES.md`, `docs/runtime/DISTRIBUTED_AUTHORITY_FOUNDATIONS.md`, `docs/runtime/ROLLBACK_BEARING_STAGED_TRANSITION_VALIDATION.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`, `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`, `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `server/shard/shard_api.h`, `server/shard/dom_cross_shard_log.h`, `server/net/dom_server_protocol.h`, `server/net/dom_server_runtime.h`, `data/registries/net_replication_policy_registry.json`, `data/registries/provenance_classification_registry.json`, `data/registries/provenance_event_type_registry.json`

# Dominium Distributed Replay And Proof-Anchor Verification

## A. Purpose And Scope

This doctrine exists because the post-`Ζ-P` checkpoint admitted `distributed_replay_and_proof_anchor_verification` only with tighter proof-only guardrails.

It solves a specific problem: Dominium now has a reconciled `Ζ` blocker baseline, a prerequisite matrix, a frozen execution-gate model, and one first bounded `Ζ-A` family for rollback-bearing staged transition validation. Those layers admit this family narrowly, but they do not yet freeze what distributed replay verification constitutionally is, what a proof anchor means, what counts as lawful verification evidence, and what this family must never pretend to realize.

Without one explicit doctrine, later bounded work could drift into:

- replay verification treated as distributed replay realization
- proof-anchor checking treated as authority convergence realization
- verification packets widening into deterministic replication or state-transfer claims
- local harness traces or partial replay windows treated as canonical distributed continuity proof
- one trace or harness format becoming architectural canon

This artifact governs:

- what distributed replay means in this proof-only first-wave family
- what a proof anchor means in this bounded verification context
- what verification classes and evidence classes belong in scope
- what guardrails preserve proof-only posture
- what blockers this family may work under and what it must not claim to close
- what later checkpoints and later bounded `Ζ-A` families must consume rather than reinvent

This artifact does not implement:

- distributed replay services
- proof-anchor infrastructure
- deterministic replication
- state-partition transfer
- live authority handoff
- distributed trust convergence
- live cutover systems

Checkpoint relation:

- `Ζ-P0` froze the canonical blocker baseline
- `Ζ-P1` froze the family-level prerequisite matrix
- `Ζ-P2` froze this family as `admitted_with_cautions`
- `C-ZETA_A_ADMISSION_REVIEW` tightened the guardrails to proof-only, blocker-reduction work
- `Ζ-A0` froze the first bounded `Ζ-A` family and the rule that first-wave admission is not broader `Ζ` readiness

This is a bounded verification doctrine, not distributed live execution.

## B. Core Definition

In this bounded first-wave context, `distributed replay` means the governed verification of whether replay-relevant history, checkpoints, snapshots, and continuity anchors remain reconstructable and intelligible across more than one declared shard, partition, authority region, or replay window horizon without claiming that live distributed runtime realization already exists.

A `proof anchor` in this context is the declared continuity-bearing anchor, linkage, or anchor chain that allows later consumers to relate replay windows, checkpoint horizons, snapshot posture, cross-shard or cross-partition log posture, receipt lineage, and authority-region identity without collapsing them into one local trace.

`Verification` in this family means the bounded constitutional act of checking whether a distributed continuity claim is:

- semantically coherent
- replay-intelligible
- snapshot-compatible
- proof-anchor-linked
- receipt-bearing where required
- trust-aware within admitted limits
- explicitly non-realized

This family is not:

- `distributed runtime realization`
  - runtime realization would require live authority movement, convergence, and stronger operational proof than this family may claim
- `replication realization`
  - verifying replay continuity does not prove deterministic replication or lawful state convergence
- `state transfer realization`
  - no transfer semantics, transfer success, or relocation semantics are admitted here
- `broader distributed trust convergence`
  - trust-relevant continuity may be checked narrowly, but trust convergence is not realized by this family
- `ordinary replay validation`
  - ordinary replay validation may stay within a single authority horizon; this family exists only where replay continuity must be checked across bounded distributed horizons and anchor linkages

The critical distinction is explicit:

- doctrine defines the meaning of this family
- admission allows the family to be attempted within first-wave bounds
- verification produces bounded proof or refusal outputs
- realization remains outside this family

## C. Why This Family Is Admitted Only With Proof-Only Guardrails

This family is admitted only with proof-only guardrails because it reduces a central blocker through verification rather than through live movement.

The repo already contains meaningful precursor substrate:

- `server/shard/shard_api.h` freezes shard-local event and message logs plus replay-state hashing
- `server/shard/dom_cross_shard_log.h` freezes deterministic cross-shard message ordering, idempotency, and log hashing
- `server/net/dom_server_protocol.h` freezes checkpoint, resync, ownership-transfer, shard-lifecycle, and rolling-update event classes
- `server/net/dom_server_runtime.h` freezes checkpoint-store, lifecycle-log, cross-shard message-log, and runtime-hash surfaces
- `data/registries/net_replication_policy_registry.json` freezes named replication-policy precursors, but only as provisional policy substrate
- `data/registries/provenance_classification_registry.json` and `data/registries/provenance_event_type_registry.json` freeze evidence-layer distinctions that later proof packets must respect

That substrate is enough to justify bounded verification work.
It is not enough to justify claims that:

- proof-anchor continuity is already realized
- deterministic replication is already proven
- state-partition transfer is already lawful
- authority convergence or quorum semantics are already solved

This family is therefore first-wave admissible only because it can remain:

- proof-only
- non-live
- non-transfer-bearing
- non-convergent in claim scope
- explicitly subordinate to the still-open blocker field

The governing caution is strict:

- replay verification is not distributed replay realization
- proof-anchor verification is not authority convergence realization
- evidence exists is not blocker resolved
- first-wave admission is not broader `Ζ` readiness

## D. Verification Classes In Scope

The following verification classes define what this family may lawfully produce.

### 1. Replay Continuity Verification

Verifies whether replay-relevant history remains reconstructable across a bounded distributed horizon, including event ordering, message ordering, checkpoint boundaries, and declared replay-window identity.

### 2. Proof-Anchor Chain Verification

Verifies whether the declared proof-anchor chain linking replay windows, checkpoints, snapshots, or related continuity markers is intelligible, attributable, and non-contradictory.

### 3. Cross-Partition Continuity Verification

Verifies whether bounded continuity claims across more than one shard, partition, or authority-region-adjacent horizon remain coherent without claiming that live handoff or transfer is already lawful.

### 4. Replay-Window Equivalence Verification

Verifies whether two or more bounded replay windows are claimed to be equivalent, comparable, superseding, or continuity-linked under explicit criteria rather than informal similarity.

### 5. Bounded Continuity Refusal Verification

Verifies that refusal or blockage outcomes are explicit when continuity, equivalence, or proof-anchor criteria are missing, contradictory, or out of scope.

### 6. Proof-Only Non-Realization Verification

Verifies that the packet itself preserves explicit non-realization markers so the family cannot be silently widened into deterministic replication, transfer, convergence, or live cutover realization.

## E. Evidence And Proof Classes

This family recognizes the following high-level evidence and proof classes.

### 1. Replay-Window Evidence

Evidence identifying the bounded replay horizon under review, including scope identity, sequencing horizon, lifecycle posture, and replay boundary markers.

### 2. Checkpoint And Snapshot Anchor Evidence

Evidence linking replay claims to lawful checkpoints, snapshots, or continuity anchors without collapsing snapshots into replay or replay into snapshots.

### 3. Proof-Anchor Lineage Evidence

Evidence showing the declared lineage or chain posture of anchors that tie replay windows, checkpoints, receipts, and authority-region identity together.

### 4. Continuity Mismatch Evidence

Evidence that the bounded continuity claim is contradictory, incomplete, non-equivalent, non-reconstructable, or otherwise insufficient.

### 5. Receipt And Provenance Linkage Evidence

Evidence that operator-transaction, generalized live-cutover receipt, or provenance posture remains reconstructable where distributed replay claims intersect boundary-sensitive transitions.

### 6. Refusal Evidence

Evidence that the correct outcome is refusal, blocked status, partial status, or out-of-scope classification rather than affirmative continuity.

### 7. Non-Convergence Or Out-Of-Scope Evidence

Evidence that a claim drifted into deterministic replication, state transfer, distributed trust convergence, or other later-wave realization territory and must therefore be refused under this family.

## F. Relationship To Blocker Baseline

This family is allowed to work under the active blocker baseline.

It may operate while all of the following remain unresolved:

- deterministic replication and state-partition transfer proof
- distributed replay and proof-anchor continuity realization
- runtime cutover proof under lawful hotswap and distributed-authority boundaries
- distributed trust and authority convergence realization
- live-cutover receipt pipeline realization

This family may contribute bounded evidence toward:

- sharper distributed replay verification criteria
- sharper proof-anchor lineage and refusal criteria
- bounded replay-window equivalence rules
- clearer later cutover-proof and continuity-packet expectations

This family must not claim to resolve:

- deterministic replication realization
- state-partition transfer realization
- distributed replay and proof-anchor continuity realization itself
- runtime cutover proof itself
- distributed trust convergence realization
- live cutover receipt-pipeline realization
- broader distributed live-ops realization

The governing rule is simple: this family may verify within the blocker field; it may not rename that blocker field as solved.

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

- no verification packet may hide truth in undocumented local state
- no verification packet may erase lifecycle posture distinctions such as active, quiescent, suspended, degraded, blocked, stopped, or failed
- no replay proof may present checkpoint or cross-shard substrate as if authority handoff were already lawful
- no continuity proof may claim that hotswap legality or distributed handoff legality has already been demonstrated

This family may verify replay continuity claims.
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

- ordinary logs, local traces, and CI output are insufficient as canonical distributed continuity proof
- generalized receipts remain upstream wherever replay verification touches a boundary-sensitive transition candidate
- archive presence does not prove continuity
- mirror visibility does not prove continuity
- proof packets must preserve exact bounded scope, review posture, and non-realization posture

This family therefore composes with release/control doctrine without implying live publication or trust execution realization.

## I. Relationship To Trust And Revocation Continuity

This family may verify trust-relevant continuity conditions only where the work stays bounded and proof-only.

It may therefore examine, within first-wave limits:

- whether a replay continuity claim depends on declared trust posture
- whether refusal or incompatibility must remain visible when trust posture breaks continuity
- whether revocation-relevant discontinuity must remain explicit in proof packets

It must not claim:

- distributed trust convergence realization
- live revocation propagation realization
- live trust execution realization
- publication execution realization

Trust-aware verification is therefore permitted only as continuity-sensitive evidence work.
Trust realization remains outside this family.

## J. Invalidity And Failure

Verification outcomes in this family may be explicit failures or refusals.

The canonical invalidity and failure categories are:

- `proof_only_scope_expanded`
  - the work drifted into replication, transfer, convergence, or live cutover claims
- `local_or_partial_evidence_only`
  - only local traces, partial replay windows, or non-canonical evidence were provided
- `proof_anchor_chain_missing_or_incoherent`
  - declared proof-anchor linkage is absent, contradictory, or non-reconstructable
- `replay_window_non_equivalent`
  - replay windows claimed as equivalent are not lawfully comparable
- `continuity_mismatch_detected`
  - continuity claim conflicts with event, message, checkpoint, or receipt posture
- `receipt_or_provenance_link_missing`
  - canonical linkage to operator or generalized receipt/provenance posture is absent where required
- `trust_or_revocation_overclaim`
  - verification packet silently turned into trust realization or revocation realization
- `out_of_scope_for_first_wave`
  - the candidate belongs to later-wave, blocked, or future-only families instead
- `inconclusive_or_blocked`
  - the proof packet is insufficient to support either affirmative continuity or a narrower lawful conclusion

## K. Canonical Vs Derived Distinctions

Canonical verification truth for this family lives in:

- this doctrine
- the upstream checkpoint, blocker, matrix, gate, and `Ζ-A0` doctrine stack
- canonical verification packets, refusal packets, and bounded proof packets later defined under this doctrine
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
They must not redefine verification truth.

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
It must not be invented greenfield and must not be widened by convenience because shard, net, or replay substrate happens to exist.

## M. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- verification treated as realization
- proof-anchor existence treated as convergence realization
- replay continuity proof treated as deterministic replication realization
- cross-shard log presence treated as lawful distributed continuity proof
- bounded first-wave used to smuggle in state transfer or live shard relocation
- unresolved blockers silently treated as solved
- local traces or one harness format treated as architectural canon
- first-wave admission rewritten as broader `Ζ` readiness

## N. Stability And Evolution

This doctrine is `provisional`.

Later consumers include:

- `Ζ-A2 — BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL-0`
- the immediate post-first-wave checkpoint
- later bounded `Ζ-A` family doctrine prompts
- later broader `Ζ` planning that must preserve proof-only versus realization distinctions

Update discipline:

- later prompts may refine verification criteria, evidence packet shapes, or refusal vocabulary
- later checkpoints may narrow this family further if first-wave evidence shows that admission was still too broad
- no later prompt may widen this family into replication realization, state transfer, live cutover, or distributed trust convergence without an explicit later checkpoint and doctrine update

## O. Explicit Answers For Later Consumers

- Distributed replay and proof-anchor verification in Dominium is the bounded, proof-only verification of reconstructable replay continuity and anchor lineage across distributed or cross-partition horizons.
- This family is proof-only and caution-gated because it reduces blockers through verification substrate rather than through live authority movement, while deterministic replication, proof-anchor continuity realization, and broader convergence remain unresolved.
- In-scope verification classes include replay continuity verification, proof-anchor chain verification, cross-partition continuity verification, replay-window equivalence verification, bounded refusal verification, and explicit non-realization verification.
- This family does not realize deterministic replication, state-partition transfer, distributed trust convergence, live cutover pipeline realization, or broader distributed live operations.
- It enables `Ζ-A2`, the immediate post-first-wave checkpoint, and later bounded `Ζ-A` families to consume one explicit proof-only distributed continuity model instead of inventing one ad hoc.
