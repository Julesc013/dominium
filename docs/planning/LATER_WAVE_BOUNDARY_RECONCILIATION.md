Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: `Ζ-B1`, `Ζ-B2`, `C-ZETA_B_ADMISSION_REVIEW`, later bounded `Ζ`
Replacement Target: later `Ζ-B1`, `Ζ-B2`, and the later-wave admission checkpoint may refine family readiness and gate posture without replacing the later-wave boundary law frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_ZETA_A_ADMISSION_REVIEW.md`, `docs/planning/CHECKPOINT_C_POST_ZETA_A_FIRST_WAVE_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZP.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZA_FIRST_WAVE.md`, `docs/planning/ZETA_BLOCKER_RECONCILIATION.md`, `docs/planning/LIVE_OPERATIONS_PREREQUISITE_MATRIX.md`, `docs/planning/ZETA_EXECUTION_GATES.md`, `docs/runtime/ROLLBACK_BEARING_STAGED_TRANSITION_VALIDATION.md`, `docs/runtime/DISTRIBUTED_REPLAY_AND_PROOF_ANCHOR_VERIFICATION.md`, `docs/runtime/BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL.md`, `docs/runtime/DISTRIBUTED_AUTHORITY_FOUNDATIONS.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`, `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`, `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `data/planning/checkpoints/checkpoint_c_zeta_a_admission_review.json`, `data/planning/checkpoints/checkpoint_c_post_zeta_a_first_wave_review.json`, `data/planning/zeta_blocker_reconciliation_registry.json`, `data/planning/live_operations_prerequisite_matrix.json`, `data/planning/zeta_execution_gates_registry.json`, `data/registries/net_replication_policy_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/provenance_classification_registry.json`, `server/shard/dom_cross_shard_log.h`, `server/net/dom_server_protocol.h`, `server/net/dom_server_runtime.h`, `security/trust/trust_verifier.py`

# Later-Wave Boundary Reconciliation

## A. Purpose And Scope

Later-wave boundary reconciliation exists because the post-first-wave checkpoint explicitly held later-wave bounded `Ζ` to `premature` while also naming a narrow planning band that must happen before any later-wave matrix refresh or gate refresh can be honest.

It solves a specific planning problem:

- the first wave now has explicit doctrine, but that doctrine is intentionally bounded and proof-only in key areas
- the remaining broader `Ζ` blockers are still realization-heavy
- earlier `Ζ-P` artifacts named later-wave, blocked, and perimeter families, but did not yet re-reconcile those families against the completed first-wave packet
- later `Ζ-B1`, `Ζ-B2`, and the later-wave admission checkpoint need one finite boundary baseline rather than scope drift

This artifact governs:

- the candidate later-wave bounded `Ζ` families that may be considered after the first wave
- the boundary classes those families now occupy
- the explicit interaction between first-wave freeze law and later-wave scope
- the distinction among doctrine, later-wave candidacy, later-wave admission, and realization
- the baseline that `Ζ-B1`, `Ζ-B2`, and the next later-wave checkpoint must extend rather than replace

This artifact does not:

- execute later-wave bounded `Ζ`
- set final later-wave execution gates
- implement runtime, trust, publication, receipt-pipeline, transfer, or relocation machinery
- redefine the first-wave doctrines
- widen broader `Ζ` by convenience

## B. Current Admission Context

This is a:

- `post-bounded-first-wave-Ζ-A / pre-later-wave` boundary reconciliation

Later-wave bounded `Ζ` is currently `premature` because:

- `Ζ-A0` froze rollback-bearing staged transition validation as bounded-only
- `Ζ-A1` froze distributed replay and proof-anchor work as proof-only
- `Ζ-A2` froze bounded runtime cutover work as proof-only rehearsal
- the blocker stack for replication proof, state-partition transfer proof, distributed continuity realization, trust convergence, live trust and publication execution, and live receipt-pipeline realization remains materially open

A fresh boundary pass is required before `Ζ-B1` or `Ζ-B2` because later-wave work must not inherit scope from:

- first-wave family names
- doctrinal existence alone
- shard, net, trust, or provenance substrate alone
- old aspirational `Ζ` wording that predates the current checkpoint chain

## C. Source-Of-Truth Inputs

The authoritative inputs for this reconciliation are:

- latest checkpoint law
  - `CHECKPOINT_C_ZETA_A_ADMISSION_REVIEW`
  - `CHECKPOINT_C_POST_ZETA_A_FIRST_WAVE_REVIEW`
  - `NEXT_EXECUTION_ORDER_POST_ZP`
  - `NEXT_EXECUTION_ORDER_POST_ZA_FIRST_WAVE`
- pre-`Ζ` admission law
  - `ZETA_BLOCKER_RECONCILIATION`
  - `LIVE_OPERATIONS_PREREQUISITE_MATRIX`
  - `ZETA_EXECUTION_GATES`
- completed bounded first-wave doctrine
  - `ROLLBACK_BEARING_STAGED_TRANSITION_VALIDATION`
  - `DISTRIBUTED_REPLAY_AND_PROOF_ANCHOR_VERIFICATION`
  - `BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL`
- relevant runtime and release/trust doctrine
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `HOTSWAP_BOUNDARIES`
  - `LIFECYCLE_MANAGER`
  - `EVENT_LOG_AND_REPLAY_DOCTRINE`
  - `SNAPSHOT_SERVICE_DOCTRINE`
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
- evidence roots used only as evidence
  - `data/registries/net_replication_policy_registry.json`
  - `data/registries/trust_policy_registry.json`
  - `data/registries/trust_root_registry.json`
  - `data/registries/provenance_classification_registry.json`
  - `server/shard/dom_cross_shard_log.h`
  - `server/net/dom_server_protocol.h`
  - `server/net/dom_server_runtime.h`
  - `security/trust/trust_verifier.py`

## D. Candidate Later-Wave Family Taxonomy

The canonical later-wave candidate categories are:

- `replication_and_state_transfer_proof_families`
  - families that would move or rebind authoritative state and therefore depend on deterministic replication and lawful partition-transfer proof
- `replay_and_proof_continuity_realization_adjacent_families`
  - families that would require realized distributed replay and proof-anchor continuity, not merely first-wave verification doctrine
- `trust_publication_realization_adjacent_families`
  - families that touch trust convergence, refusal/remediation posture, revocation, or publication execution
- `cutover_receipt_pipeline_families`
  - families that depend on stronger live-cutover receipt and provenance anchorization
- `perimeter_distributed_movement_families`
  - future-only movement families that remain outside bounded near-term `Ζ`

Taxonomy discipline:

- the category exists even when no standalone candidate family is yet admissible inside it
- replay/proof continuity realization-adjacent scope remains a prerequisite category, not a newly named standalone family, because renaming first-wave replay verification into later-wave realization would be scope creep
- later-wave means "candidate for refreshed analysis", not "already admitted"

## E. Reconciled Later-Wave Ledger

### `zeta.family.trust_aware_refusal_and_containment`

- Title: Trust-aware refusal and containment
- Current status: `plausible_later_wave_candidate`
- Boundary class: `candidate_for_matrix_refresh`
- Why it remains a candidate:
  - it is narrower than live trust execution and can stay in refusal, containment, and remediation posture
  - it was already review-gated and later-wave-only in `Ζ-P2`
- Governing doctrine:
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `ZETA_EXECUTION_GATES`
- Still missing:
  - distributed trust and authority convergence realization
  - non-empty promoted trust-root posture
  - non-provisional trust policy posture
  - stronger receipt lineage for later-wave trials
- Later-wave posture:
  - candidate for `Ζ-B1` matrix refresh
  - not admitted by this artifact

### `zeta.family.live_cutover_receipt_pipeline_anchorization`

- Title: Live cutover receipt pipeline and anchorization
- Current status: `plausible_later_wave_candidate`
- Boundary class: `candidate_for_matrix_refresh`
- Why it remains a candidate:
  - first-wave doctrine sharpened receipt obligations, cutover evidence posture, and proof-bearing boundaries
  - later-wave review can now assess whether shadow or parallel anchorization is even matrix-refreshable
- Governing doctrine:
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
  - `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`
  - `BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL`
  - `ZETA_EXECUTION_GATES`
- Still missing:
  - realized live receipt-pipeline machinery
  - lawful cutover proof across hotswap and distributed-authority boundaries
  - any basis for promoting local logs or traces into canonical receipts
- Later-wave posture:
  - candidate for `Ζ-B1` matrix refresh
  - still review-sensitive and not admitted

### `zeta.family.bounded_authority_handoff_and_state_transfer`

- Title: Bounded authority handoff and state transfer
- Current status: `deferred_until_realization_blockers_reduce`
- Boundary class: `realization_adjacent_but_not_yet_admissible`
- Why it remains deferred:
  - it sits directly on the unresolved replication, replay continuity, cutover legality, trust convergence, and receipt-pipeline blockers
  - first-wave doctrine explicitly refused to smuggle transfer semantics into validation, verification, or rehearsal
- Governing doctrine:
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `HOTSWAP_BOUNDARIES`
  - `DISTRIBUTED_REPLAY_AND_PROOF_ANCHOR_VERIFICATION`
  - `BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL`
  - `ZETA_EXECUTION_GATES`
- Still missing:
  - deterministic replication and state-partition transfer proof
  - realized distributed replay and proof-anchor continuity
  - lawful runtime cutover proof
  - distributed trust and authority convergence realization
  - stronger canonical receipt posture
- Later-wave posture:
  - not matrix-refreshable as an admitted family yet
  - may be re-evaluated only after `Ζ-B1`, `Ζ-B2`, and a checkpoint materially narrow those blockers

### `zeta.family.live_trust_revocation_and_publication_execution`

- Title: Live trust, revocation, and publication execution
- Current status: `still_out_of_scope`
- Boundary class: `excluded_from_current_wave_planning`
- Why it remains out of scope:
  - this is a realization-heavy family rather than a bounded later-wave candidate
  - trust roots remain empty and trust policy posture remains provisional
  - first-wave doctrine did not narrow live execution machinery blockers
- Governing doctrine:
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
  - `ZETA_BLOCKER_RECONCILIATION`
- Still missing:
  - distributed trust convergence realization
  - live revocation propagation realization
  - live publication execution realization
  - stronger receipt-pipeline support for execution evidence
- Later-wave posture:
  - excluded from current later-wave planning
  - remains broader `Ζ` or later-future material only

### `zeta.family.live_shard_relocation`

- Title: Live shard relocation
- Current status: `future_only_perimeter`
- Boundary class: `future_only_perimeter`
- Why it remains perimeter-only:
  - the family depends on nearly the entire unresolved realization stack
  - the post-first-wave checkpoint explicitly kept relocation future-only
  - no first-wave artifact reduced the prerequisites enough to treat relocation as near-term later-wave scope
- Governing doctrine:
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `HOTSWAP_BOUNDARIES`
  - `ZETA_EXECUTION_GATES`
  - `ZETA_BLOCKER_RECONCILIATION`
- Still missing:
  - deterministic replication and state-partition transfer proof
  - distributed replay and proof-anchor continuity realization
  - lawful runtime cutover proof
  - distributed trust convergence realization
  - live receipt-pipeline realization
  - live trust, revocation, and publication execution realization
- Later-wave posture:
  - outside the `Ζ-B` planning band
  - must not be shrink-wrapped into later-wave scope by renaming or transport success

## F. First-Wave Freeze Interaction

The completed first-wave families remain frozen as follows:

- `zeta.family.rollback_bearing_staged_transition_validation` remains bounded-only
- `zeta.family.distributed_replay_and_proof_anchor_verification` remains proof-only
- `zeta.family.bounded_runtime_cutover_proof_rehearsal` remains proof-only and frozen pending unresolved blockers

Later-wave candidates must not implicitly consume first-wave work as:

- realized distributed replay continuity
- realized proof-anchor convergence
- lawful authority handoff proof
- lawful live cutover proof
- live trust, revocation, or publication execution readiness
- canonical live receipt-pipeline realization

The first wave may only be consumed as:

- blocker-boundary clarification
- bounded proof expectations
- replay, receipt, and cutover evidence posture refinement
- refusal of false realization claims

## G. Doctrine Vs Realization Distinction

Later-wave candidacy does not imply realization readiness.

The binding distinctions are:

- doctrine exists
  - law is explicit enough to describe a family honestly
- later-wave candidate exists
  - the family may be reconsidered in `Ζ-B1` and `Ζ-B2`
- later-wave admission exists
  - a later checkpoint explicitly says the family may enter bounded execution
- realization exists
  - proof, trust, transfer, cutover, and receipt machinery actually satisfies the governing blockers

Dominium is not yet at the last two steps for any later-wave family.

## H. Boundary Classes

The canonical later-wave boundary classes are:

- `candidate_for_matrix_refresh`
  - plausible later-wave candidate whose bounded posture may be re-analyzed in `Ζ-B1`
- `realization_adjacent_but_not_yet_admissible`
  - family is doctrinally meaningful but still too central to unresolved realization blockers
- `future_only_perimeter`
  - family stays outside bounded near-term `Ζ-B` planning entirely
- `excluded_from_current_wave_planning`
  - family is not honest later-wave bounded scope yet even though governing doctrine exists

## I. Extension-Over-Replacement Directives

Later `Ζ-B1`, `Ζ-B2`, and the later-wave admission checkpoint must extend or preserve:

- `ZETA_BLOCKER_RECONCILIATION`
- `LIVE_OPERATIONS_PREREQUISITE_MATRIX`
- `ZETA_EXECUTION_GATES`
- `ROLLBACK_BEARING_STAGED_TRANSITION_VALIDATION`
- `DISTRIBUTED_REPLAY_AND_PROOF_ANCHOR_VERIFICATION`
- `BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL`
- `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
- `HOTSWAP_BOUNDARIES`
- `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
- `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
- `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
- `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
- the active blocker truth that trust roots remain empty, trust and replication policy posture remains provisional, and provenance vocabulary does not equal a realized receipt pipeline

Later work must avoid replacing:

- the first-wave freeze with "later-wave" relabeling
- blocker truth with code-surface optimism
- canonical planning law with stale blueprint or pre-checkpoint wording
- doctrine-evidence distinction with implementation convenience

## J. Ownership And Anti-Reinvention Cautions

The following cautions remain binding:

- `fields/` remains canonical semantic field substrate while `field/` remains transitional
- `schema/` remains canonical semantic contract law while `schemas/` remains projection-facing
- `packs/` remains canonical for runtime packaging and activation scope while `data/packs/` remains scoped authored-pack authority
- canonical prose and semantic specs outrank projected or generated mirrors
- the thin `runtime/` root is not canonical by name alone
- later-wave family selection must come from doctrine and blocker reconciliation, not invention
- stale numbering or titles do not override the active checkpoint chain
- later-wave scope must not be widened because a server, shard, trust, or provenance file already exists

## K. Anti-Patterns / Forbidden Shapes

The following shapes are forbidden:

- widening first-wave by renaming it later-wave
- later-wave candidate meaning later-wave admitted
- doctrine existing meaning realization ready
- code surface existing meaning later-wave candidate
- treating realized replay continuity, trust convergence, or receipt-pipeline posture as already satisfied because proof-only first-wave doctrine exists
- silently deleting blocker-heavy later-wave candidates because they are inconvenient
- promoting perimeter families because transport or cluster substrate exists

## L. Stability And Evolution

Stability class:

- `provisional`

This artifact is intended to be consumed by:

- `Ζ-B1 — LATER_WAVE_PREREQUISITE_MATRIX_REFRESH-0`
- `Ζ-B2 — LATER_WAVE_EXECUTION_GATES_REFRESH-0`
- `C-ZETA_B_ADMISSION_REVIEW — POST_LATER_WAVE_GATE_FREEZE_REASSESSMENT-0`

Update discipline:

- revise this artifact only when a later checkpoint or later-wave refresh prompt explicitly targets it
- do not add new later-wave families merely because an evidence root looks promising
- do not promote candidate families into admitted families without an explicit later checkpoint
