Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: `Ζ-A1`, `Ζ-A2`, immediate post-first-wave checkpoint, later bounded `Ζ-A`, later broader `Ζ`
Replacement Target: later bounded `Ζ-A` family doctrine and later post-first-wave checkpoints may refine procedures and evidence structures without replacing the bounded first-wave validation semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PRE_ZETA_ADMISSION.md`, `docs/planning/CHECKPOINT_C_ZETA_A_ADMISSION_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB5.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZP.md`, `docs/planning/ZETA_BLOCKER_RECONCILIATION.md`, `docs/planning/LIVE_OPERATIONS_PREREQUISITE_MATRIX.md`, `docs/planning/ZETA_EXECUTION_GATES.md`, `docs/runtime/DISTRIBUTED_AUTHORITY_FOUNDATIONS.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`, `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`, `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`, `docs/release/RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT.md`, `docs/release/CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `docs/blueprint/CAPABILITY_LADDER.md`, `docs/blueprint/MANUAL_REVIEW_GATES.md`, `docs/blueprint/STOP_CONDITIONS_AND_ESCALATION.md`, `server/shard/shard_api.h`, `server/shard/dom_cross_shard_log.h`, `server/net/dom_server_protocol.h`, `server/net/dom_server_runtime.h`, `release/update_resolver.py`, `security/trust/trust_verifier.py`, `data/registries/net_replication_policy_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/provenance_classification_registry.json`

# Dominium Rollback-Bearing Staged Transition Validation

## A. Purpose And Scope

This doctrine exists because the post-`Ζ-P` checkpoint explicitly admitted `rollback_bearing_staged_transition_validation` as the first bounded `Ζ-A` family while keeping broader `Ζ` blocked by unresolved replication, replay, cutover, trust, and receipt-pipeline realization work.

It solves a specific problem: Dominium now has a reconciled blocker baseline, a family-level prerequisite matrix, and a frozen execution-gate model. Those artifacts admit one narrow first-wave family, but they do not yet define what that family constitutionally is, what it may validate, and what it must never pretend to realize.

Without one explicit doctrine, later work could drift into:

- “staged transition” meaning any live change
- rollback-bearing validation being treated as live realization
- proof-only validation being mistaken for production authority
- bounded first-wave work expanding into distributed transfer, trust execution, or publication execution
- hotswap or distributed-authority boundaries being bypassed by convenience
- one resolver, CLI, or rehearsal workflow becoming architectural canon

This artifact governs:

- what a rollback-bearing staged transition is in Dominium
- what validation means for that first-wave family
- what transition and validation classes belong inside the family
- what blockers this family may work under and what it must not claim to close
- how the family remains subordinate to runtime, release, trust, provenance, and checkpoint law
- what later bounded `Ζ-A` families and later checkpoints must consume rather than reinvent

This artifact does not implement:

- live transition systems
- production rollback pipelines
- trust execution systems
- publication execution systems
- distributed state transfer or live shard relocation
- broader `Ζ` live-ops realization

Checkpoint relation:

- `Ζ-P0` froze the active blocker truth
- `Ζ-P1` froze the family prerequisite matrix
- `Ζ-P2` froze the first-wave perimeter and explicit guardrails
- `C-ZETA_A_ADMISSION_REVIEW` confirmed that this family remains the admitted first bounded `Ζ-A` family

## B. Core Definition

In Dominium, a `rollback-bearing staged transition` is a declared, bounded, proof-bearing transition candidate whose validation posture preserves explicit rollback, downgrade, refusal, continuity, and evidence obligations while remaining narrower than live realization.

In this family, `validation` means the constitutional act of determining whether a staged transition candidate is structurally coherent, compatibility-coherent, rollback-bearing, receipt-bearing, provenance-coherent, trust-aware within bounds, and explicitly reconstructable under first-wave limits.

This family differs from nearby concepts:

- `live realization`
  - realization mutates or operationalizes the live posture; this family validates bounded candidates without claiming that live realization has occurred
- `distributed transfer`
  - authority handoff or state transfer remains outside this family
- `full cutover execution`
  - runtime cutover proof may be informed by this family later, but this family does not execute full cutover
- `trust or publication realization`
  - trust-aware validation may appear in bounded form, but live trust, revocation, and publication execution remain out of scope
- `ordinary rehearsal or dry-run`
  - ordinary rehearsal may prove that a path was exercised; this family requires rollback-bearing continuity meaning, stronger validation classes, and explicit first-wave limits

The core constitutional rule is:

- validation is not realization
- rollback-bearing is not full rollback pipeline realization
- first-wave admission is not broader `Ζ` readiness

## C. Why This Family Is First-Wave Admissible

This family is first-wave admissible because it is the narrowest live-operations-adjacent family that can:

- stay proof-bearing rather than operationally realized
- remain bounded by rollback, downgrade, refusal, and staged-transition semantics already frozen upstream
- reduce ambiguity without pretending to close broader `Ζ` blockers

It is the correct first-wave family because:

- `RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT` already freezes rehearsal, sandbox, rollback-alignment, and proof classes
- `CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION` already freezes bounded staged exposure and deterministic downward movement semantics
- `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION` already freezes stronger evidence classes for boundary-sensitive transitions
- `HOTSWAP_BOUNDARIES`, `DISTRIBUTED_AUTHORITY_FOUNDATIONS`, `LIFECYCLE_MANAGER`, `EVENT_LOG_AND_REPLAY_DOCTRINE`, and `SNAPSHOT_SERVICE_DOCTRINE` already freeze the boundary conditions that this family must not exceed

It still requires cautions because:

- runtime cutover proof remains open
- live-cutover receipt-pipeline realization remains open
- deterministic replication and distributed replay continuity remain broader open blockers
- distributed trust convergence and live trust/publication execution remain out of scope

This family is therefore admissible only while it stays:

- bounded
- staged
- rollback-bearing
- refusal-aware
- proof-oriented
- non-transfer
- non-live-realized

## D. Transition Classes In Scope

The following transition classes are in scope for this family.

### D.1 Bounded Staged Control-Plane Transition

A staged release or control-plane transition candidate whose meaning stays within explicit target, release, receipt, rollback, and refusal posture without claiming live runtime realization.

### D.2 Bounded Rollback-Bearing Cutover Candidate

A bounded candidate whose validation posture depends on rollback-bearing continuity, cutover-sensitive evidence, or bounded runtime-adjacent change while still remaining non-live and proof-bearing.

### D.3 Trust-Aware But Non-Realized Staged Transition

A staged transition candidate that must remain compatible with trust posture, trust prerequisites, or revocation continuity without claiming live trust realization, revocation propagation realization, or publication execution.

### D.4 Validation-Only Staged Transition

A transition candidate that exists only to produce structural, compatibility, continuity, provenance, or proof-bearing validation outputs and remains explicitly outside realized live execution.

### D.5 Explicitly Out-Of-Scope Transition Classes

The following remain out of scope for this family:

- live authority handoff
- state transfer between authority regions
- deterministic replication realization
- proof-anchor continuity realization
- live trust-root rotation
- live revocation propagation realization
- publication execution realization
- live shard relocation
- broader `Ζ` perimeter families

## E. Validation Classes

The following validation classes are recognized for this family.

### E.1 Structural Validation

Validates that the staged transition candidate declares the correct subject, scope, intent, lifecycle posture, target context, and boundedness markers.

### E.2 Compatibility Validation

Validates that the candidate remains lawful under release contract profile, release-index and resolution semantics, target applicability, version and identity posture, and refusal law.

### E.3 Rollback-Bearing Continuity Validation

Validates that the candidate preserves a declared rollback-bearing posture, including reversible boundaries, bounded resulting state, refusal-aware restoration posture, and explicit non-reversible edges where they exist.

### E.4 Receipt And Provenance Validation

Validates that the candidate preserves operator transaction meaning, generalized live-cutover receipt posture, provenance continuity, and reconstructable evidence anchors rather than ordinary logs alone.

### E.5 Trust-Continuity Validation

Validates that any trust-aware staged transition remains compatible with trust and revocation continuity doctrine without claiming live trust realization or distributed trust convergence realization.

### E.6 Proof-Only Validation

Validates that the candidate produces bounded proof packets, continuity packets, refusal packets, or rollback-alignment packets that remain explicitly non-live and non-realized.

### E.7 Blocked Or Refusal Validation Outcome

Records that a candidate is blocked, partial, out-of-scope, trust-incoherent, proof-insufficient, or otherwise not lawfully valid for this family.

## F. Relationship To Blocker Baseline

This family is allowed to work under the broader blocker baseline frozen by `Ζ-P0`, but it does not dissolve that baseline.

This family may operate while the following blockers remain open:

- `runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
- `live_cutover_receipt_pipeline_realization`
- `deterministic_replication_and_state_partition_transfer_proof`
- `distributed_replay_and_proof_anchor_continuity_realization`
- `distributed_trust_and_authority_convergence_realization`
- `live_trust_revocation_publication_execution_realization`

This family may contribute bounded evidence toward:

- rollback-bearing continuity understanding
- runtime cutover proof scoping
- refusal-aware staged-transition legality
- stronger receipt and provenance expectations for later families

This family must not claim to resolve:

- deterministic replication proof
- distributed replay and proof-anchor continuity realization
- runtime cutover proof itself
- distributed trust convergence realization
- live trust, revocation, or publication execution realization
- live-cutover receipt-pipeline realization

The governing rule is simple: this family may validate within the blocker field; it may not rename that blocker field as solved.

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
- distributed-authority boundaries remain binding

The specific runtime consequences are:

- no staged candidate may hide truth in undocumented local state
- no validation may erase the distinction between active, quiescent, suspended, degraded, blocked, stopped, or failed lifecycle posture
- no proof packet may present replay, checkpoint, or cross-shard substrate as if broader distributed continuity were already solved
- no bounded staged transition may be rewritten as lawful authority movement

This family may validate bounded runtime-adjacent candidates.
It must not overclaim runtime realization.

## H. Relationship To Release/Control-Plane Doctrine

This family must remain compatible with:

- operator transaction doctrine
- generalized live-cutover receipt and provenance doctrine
- release contract profile
- release-index and resolution semantics
- archive and mirror continuity doctrine
- release rehearsal sandbox and proof-backed rollback alignment
- canary and deterministic downgrade doctrine
- publication and trust execution operationalization gates

The governing consequences are:

- a staged transition candidate must remain typed as an operator-transaction-bearing action where relevant
- exact release identity, target context, and selection posture remain reconstructable
- archive or mirror presence does not prove validation success
- ordinary logs, CI traces, or filenames are insufficient as canonical validation evidence
- publication or trust-bearing meaning remains upstream of this family and may not be flattened into “a staged release change”

This family therefore consumes release-control doctrine; it does not replace or widen it.

## I. Relationship To Trust And Revocation Continuity

This family may validate bounded trust-aware staged transitions only in the following sense:

- it may verify that trust posture was considered
- it may verify that trust prerequisites were not violated by the candidate
- it may verify that revocation continuity or trust-aware refusal posture was not silently erased

It must not claim:

- live trust execution realization
- live revocation propagation realization
- distributed trust convergence realization
- publication execution realization

Trust-aware is not the same thing as trust-realized.
Trust-aware is therefore not trust execution realization.

## J. Invalidity And Failure

The following invalidity and failure classes are canonical for this family:

- `scope_expanded_beyond_first_wave`
  - the candidate crossed into transfer, trust execution, publication execution, or other later-wave territory
- `non_rollback_bearing_candidate`
  - rollback-bearing posture is absent, ambiguous, or asserted without continuity support
- `proof_insufficient`
  - proof packet, continuity packet, or refusal packet is too weak to support bounded validation claims
- `receipt_or_provenance_missing`
  - operator transaction or generalized receipt continuity is absent where required
- `trust_incoherent`
  - trust-aware posture is contradictory, absent, or exceeds admitted first-wave bounds
- `runtime_boundary_overclaim`
  - the candidate claims lawful runtime cutover, handoff, or distributed continuity beyond current doctrine
- `partial_or_non_reconstructable`
  - the candidate or result cannot be reconstructed canonically across intent, review, proof, refusal, and outcome
- `out_of_scope_transition`
  - the candidate belongs to later-wave, blocked, or future-only families instead of this one

## K. Canonical Vs Derived Distinctions

Canonical staged-transition validation truth consists of:

- this doctrine
- upstream checkpoint, blocker, matrix, and gate doctrine
- canonical validation packets, refusal packets, and proof packets later defined under this doctrine
- canonical operator transaction, receipt, and provenance records where relevant

Derived surfaces include:

- dashboards
- CI output
- local traces
- mirror or publication views
- changelog prose
- filenames
- tool-local reports

Derived views must not redefine validation truth.

## L. Ownership And Anti-Reinvention Cautions

The prior cautions remain fully binding:

- `fields/` remains canonical semantic field substrate while `field/` remains transitional
- `schema/` remains canonical semantic contract law while `schemas/` remains projection-facing
- `packs/` remains canonical for runtime packaging and activation scope while `data/packs/` remains scoped authored-pack authority
- canonical prose and semantic specs outrank projected or generated mirrors
- stale numbering or titles do not override active checkpoint law
- bounded first-wave scope must not be widened by convenience

Additional caution applies here because this family sits near runtime, release, and trust evidence surfaces:

- shard or net precursor code must not become constitutional truth by familiarity
- trust verifier or release resolver substrate must not be mistaken for live execution maturity
- local workflow convenience must not decide which staged-transition meaning is canonical

## M. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- validation treated as realization
- rollback-bearing claim with no continuity proof
- bounded first-wave used to smuggle in distributed transfer
- trust-aware validation treated as trust execution realization
- unresolved blockers silently treated as solved
- ordinary rehearsal or dry-run presented as rollback-bearing validation
- code substrate, local traces, or dashboards treated as gate passage
- first-wave admission rewritten as broader `Ζ` readiness

## N. Stability And Evolution

This doctrine is `provisional`.

It is intended to be consumed by:

- `Ζ-A1 — DISTRIBUTED_REPLAY_AND_PROOF_ANCHOR_VERIFICATION-0`
- `Ζ-A2 — BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL-0`
- the immediate post-first-wave checkpoint
- later bounded `Ζ-A` families that must remain subordinate to first-wave perimeter law

Update discipline:

- later prompts may refine evidence structures, proof packets, or narrower subclassifications
- later checkpoints may narrow this family further if first-wave evidence shows that admission was still too broad
- no later prompt may widen this family into authority transfer, live trust/publication execution, or broader `Ζ` live-ops realization without explicit new checkpoint law

This artifact therefore answers the mandatory questions directly:

- a rollback-bearing staged transition is a bounded, proof-bearing transition candidate whose validation posture preserves explicit rollback, downgrade, refusal, continuity, and evidence obligations without claiming realization
- this family is first-wave admissible because it is the narrowest, most reversible, and most already-supported bounded `Ζ-A` family
- bounded staged control-plane transitions, rollback-bearing cutover candidates, bounded trust-aware but non-realized staged transitions, and validation-only staged transitions are in scope
- this family does not realize live cutover, distributed transfer, trust execution, publication execution, deterministic replication, proof-anchor continuity realization, or broader `Ζ` readiness
- it enables `Ζ-A1`, `Ζ-A2`, and the immediate post-first-wave checkpoint to consume one explicit first-wave validation model instead of inventing one ad hoc
