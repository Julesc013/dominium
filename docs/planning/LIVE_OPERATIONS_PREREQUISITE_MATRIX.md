Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: `Ζ-P2`, immediate post-`Ζ-P` checkpoint, bounded later `Ζ-A`
Replacement Target: later `Ζ-P2` and the immediate post-`Ζ-P` checkpoint may refine gate posture and wave selection without replacing the matrix law frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PRE_ZETA_ADMISSION.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB5.md`, `docs/planning/ZETA_BLOCKER_RECONCILIATION.md`, `docs/runtime/DISTRIBUTED_AUTHORITY_FOUNDATIONS.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`, `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`, `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT.md`, `docs/release/CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `docs/blueprint/CAPABILITY_LADDER.md`, `docs/blueprint/MANUAL_REVIEW_GATES.md`, `docs/blueprint/STOP_CONDITIONS_AND_ESCALATION.md`, `data/planning/zeta_blocker_reconciliation_registry.json`, `data/registries/net_replication_policy_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/provenance_classification_registry.json`, `server/shard/shard_api.h`, `server/shard/dom_cross_shard_log.h`, `server/net/dom_server_protocol.h`, `server/net/dom_server_runtime.h`, `release/update_resolver.py`, `security/trust/trust_verifier.py`

# Live Operations Prerequisite Matrix

## A. Purpose And Scope

This matrix exists because Dominium has now completed the doctrine needed to enter a pre-`Ζ` admission band, but it still does not have one canonical family-by-family admission surface for bounded live-operation planning.

It solves a specific planning problem:

- `Ζ-P0` froze the surviving blocker ledger, but did not yet map each candidate live-operation family to the prerequisites it needs
- some families are plausible early bounded candidates only because they are proof-oriented, rehearsal-oriented, or rollback-bearing
- other families remain later-wave, blocked, or future-only even though their governing doctrine now exists
- `Ζ-P2` needs one matrix baseline rather than vague "ready with cautions" prose

This artifact governs:

- the candidate live-operation families relevant to bounded `Ζ-A` entry
- the matrix dimensions used to assess those families
- the prerequisite categories each family depends on
- the mapping from each family to blocker dependencies, governing doctrine, and evidence surfaces
- the distinction among doctrinal availability, matrix admission, realization status, execution admissibility, and bounded-entry suitability

This artifact does not:

- execute `Ζ`
- freeze final execution gates
- implement runtime, trust, publication, or distributed machinery
- replace `Ζ-P0`
- select the final bounded `Ζ-A` package by itself

## B. Current Admission Context

This is a:

- `post-Φ-B5 / in-Ζ-P / pre-gate-freeze` prerequisite matrix

`Ζ-P` is `ready_with_cautions` because:

- coexistence, hotswap, and distributed-authority boundaries are explicit
- live trust-transition prerequisites are explicit
- live-cutover receipt and provenance generalization is explicit
- publication and trust execution operationalization gates are explicit
- `Ζ-P0` has already frozen the canonical blocker baseline

`Ζ-P` is not `Ζ` readiness because:

- deterministic replication and lawful partition transfer remain unproven
- distributed replay and proof-anchor continuity remain unrealized
- runtime cutover proof remains unresolved
- distributed trust convergence remains unrealized
- live trust, revocation, publication, and live-cutover receipt execution remain unrealized

Family-level prerequisite mapping is needed before gate freezing because `Ζ-P2` must decide which bounded families are even gateable, which are review-gated, and which remain later-wave or prohibited.

## C. Source-Of-Truth Inputs

The authoritative inputs for this matrix are:

- latest checkpoint law
  - `CHECKPOINT_C_PRE_ZETA_ADMISSION`
  - `NEXT_EXECUTION_ORDER_POST_PHIB5`
- latest blocker baseline
  - `ZETA_BLOCKER_RECONCILIATION`
  - `zeta_blocker_reconciliation_registry.json`
- latest runtime doctrine
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `HOTSWAP_BOUNDARIES`
  - `EVENT_LOG_AND_REPLAY_DOCTRINE`
  - `SNAPSHOT_SERVICE_DOCTRINE`
  - `LIFECYCLE_MANAGER`
  - `STATE_EXTERNALIZATION`
  - `SANDBOXING_AND_ISOLATION_MODEL`
  - `MULTI_VERSION_COEXISTENCE`
- latest release, trust, and evidence doctrine
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`
  - `RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT`
  - `CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION`
  - `RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT`
  - `RELEASE_CONTRACT_PROFILE`
- live precursor substrate
  - `server/shard/shard_api.h`
  - `server/shard/dom_cross_shard_log.h`
  - `server/net/dom_server_protocol.h`
  - `server/net/dom_server_runtime.h`
  - `data/registries/net_replication_policy_registry.json`
  - `data/registries/trust_policy_registry.json`
  - `data/registries/trust_root_registry.json`
  - `data/registries/provenance_classification_registry.json`
  - `release/update_resolver.py`
  - `security/trust/trust_verifier.py`
- derived caution surfaces
  - `FOUNDATION_READINESS_MATRIX`
  - `CAPABILITY_LADDER`
  - `MANUAL_REVIEW_GATES`
  - `STOP_CONDITIONS_AND_ESCALATION`

Authority ordering remains strict:

- canon and governance law outrank this matrix
- active checkpoint law and `Ζ-P0` outrank older planning drift
- doctrine outranks evidence surfaces when evidence is only precursor substrate
- evidence surfaces still matter for showing whether a family is realized, only partially prepared, or still entirely absent

## D. Candidate Live-Operation Families

The candidate live-operation families assessed here are:

### D.1 Bounded Live Transition Families

Families that aim to prove or rehearse bounded runtime-adjacent cutover legality without yet claiming full distributed handoff or trust realization.

### D.2 Rollback-Bearing Live Transition Families

Families that rely on rollback, downgrade, rehearsal, and staged transition law to keep bounded live movement reversible.

### D.3 Distributed Continuity Verification Families

Families that validate replay, proof-anchor, and distributed continuity claims before authority transfer is admitted.

### D.4 Distributed Handoff Families

Families that would move authority or state across explicit authority regions and therefore remain downstream of stronger replication, transfer, trust, and proof requirements.

### D.5 Trust-Aware Refusal And Remediation Families

Families that contain, refuse, or remediate unsafe live transitions where trust posture, revocation posture, or authority convergence is not yet satisfactory.

### D.6 Publication And Trust Realization Families

Families that would operationalize live trust, revocation, or publication execution rather than merely describing it doctrinally.

### D.7 Cutover Receipt-Pipeline Families

Families that would realize canonical boundary-sensitive receipt emission and stronger provenance anchors for live cutover events.

### D.8 Future-Only Perimeter Families

Families such as live shard relocation that remain outside bounded near-term `Ζ-A` entry even after `Φ-B5`.

## E. Matrix Dimensions

The matrix assesses each family across these dimensions:

### E.1 Doctrinal Availability

Whether the family already has the governing constitutional law it needs.

### E.2 Blocker Dependency

Which unresolved `Ζ-P0` blocker entries must remain visible for that family.

### E.3 Proof Requirement

Whether the family depends on explicit replication proof, replay proof, cutover proof, or proof-anchor continuity.

### E.4 Trust Convergence Requirement

Whether the family depends on distributed trust posture, revocation continuity, or publication/trust operationalization posture.

### E.5 Replay And Snapshot Continuity Requirement

Whether replay intelligibility, state externalization, snapshot legality, and continuity across handoff or cutover remain upstream.

### E.6 Cutover Legality Requirement

Whether hotswap boundaries, distributed-authority boundaries, lifecycle legality, or rollback posture constrain the family.

### E.7 Receipt And Provenance Requirement

Whether the family depends on stronger live-cutover receipts, proof anchors, or provenance generalization.

### E.8 Operational Realization Requirement

Whether the family needs live machinery that is not yet realized.

### E.9 Review And Privilege Posture

Whether the family can only be discussed under explicit human review, privileged operator posture, or stronger refusal policy.

### E.10 Bounded-Entry Suitability

Whether the family is a plausible first-wave candidate, a later-wave candidate, or not admissible for bounded `Ζ-A`.

## F. Family-By-Family Matrix

### F.1 `zeta.family.rollback_bearing_staged_transition_validation`

- Title: Rollback-bearing staged transition validation
- Current readiness class: `admissible_first_wave_candidate`
- Required prerequisite categories:
  - admission and governance freeze
  - release and rollback envelope
  - runtime cutover legality
  - receipt and provenance anchorization
  - review and privilege posture
- Governing doctrine:
  - `RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT`
  - `CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION`
  - `HOTSWAP_BOUNDARIES`
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
  - `RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT`
- Unresolved blocker dependencies:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Notes on bounded-entry suitability:
  - plausible early bounded candidate because rollback, rehearsal, downgrade, and release selection law are already explicit
  - must stay bounded to staged validation and refusal-aware rollback posture
  - must not be used to smuggle in live trust execution or distributed authority handoff
- Wave classification:
  - first-wave candidate

### F.2 `zeta.family.bounded_runtime_cutover_proof_rehearsal`

- Title: Bounded runtime cutover proof and rehearsal
- Current readiness class: `admissible_only_with_cautions`
- Required prerequisite categories:
  - admission and governance freeze
  - replay, snapshot, and proof-anchor continuity
  - runtime cutover legality
  - receipt and provenance anchorization
  - release and rollback envelope
  - review and privilege posture
- Governing doctrine:
  - `HOTSWAP_BOUNDARIES`
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `LIFECYCLE_MANAGER`
  - `EVENT_LOG_AND_REPLAY_DOCTRINE`
  - `SNAPSHOT_SERVICE_DOCTRINE`
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
- Unresolved blocker dependencies:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Notes on bounded-entry suitability:
  - plausible early bounded candidate only because it can be structured as proof-bearing rehearsal rather than live authority movement
  - remains caution-heavy because cutover legality across hotswap and distributed boundaries is still an active blocker
  - must preserve explicit non-live and rehearsal-only markers when realization remains absent
- Wave classification:
  - first-wave candidate

### F.3 `zeta.family.distributed_replay_and_proof_anchor_verification`

- Title: Distributed replay and proof-anchor verification
- Current readiness class: `admissible_only_with_cautions`
- Required prerequisite categories:
  - admission and governance freeze
  - distributed continuity proof
  - replay, snapshot, and proof-anchor continuity
  - receipt and provenance anchorization
  - review and privilege posture
- Governing doctrine:
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `EVENT_LOG_AND_REPLAY_DOCTRINE`
  - `SNAPSHOT_SERVICE_DOCTRINE`
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
  - `STATE_EXTERNALIZATION`
- Unresolved blocker dependencies:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.deterministic_replication_and_state_partition_transfer_proof`
  - `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
- Notes on bounded-entry suitability:
  - plausible first-wave candidate because it reduces a blocker through verification, continuity proving, and rehearsal substrate rather than direct live transfer
  - must not claim that replay substrate or cross-shard logs already prove lawful distributed continuity
  - proof-anchor continuity remains a prerequisite outcome, not an implied property
- Wave classification:
  - first-wave candidate

### F.4 `zeta.family.trust_aware_refusal_and_containment`

- Title: Trust-aware refusal and containment
- Current readiness class: `review_gated`
- Required prerequisite categories:
  - admission and governance freeze
  - trust prerequisites and convergence
  - receipt and provenance anchorization
  - review and privilege posture
  - operational realization substrate
- Governing doctrine:
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`
  - refusal and remediation registries
- Unresolved blocker dependencies:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_trust_revocation_publication_execution_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Notes on bounded-entry suitability:
  - bounded containment is safer than live trust execution, but it still touches trust posture and therefore remains review-gated
  - suitable only when the family stays on refusal, containment, and remediation paths
  - not suitable as a first-wave family if it silently becomes trust-root rotation, revocation propagation, or publication execution
- Wave classification:
  - later-wave candidate

### F.5 `zeta.family.live_cutover_receipt_pipeline_anchorization`

- Title: Live cutover receipt pipeline and anchorization
- Current readiness class: `review_gated`
- Required prerequisite categories:
  - admission and governance freeze
  - receipt and provenance anchorization
  - release and rollback envelope
  - runtime cutover legality
  - review and privilege posture
  - operational realization substrate
- Governing doctrine:
  - `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
  - `RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT`
  - `CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION`
- Unresolved blocker dependencies:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Notes on bounded-entry suitability:
  - helpful enabling family, but it affects canonical evidence truth and must not outrun the gate freeze
  - may become suitable as a bounded shadow or parallel evidence path only after `Ζ-P2` freezes the exact gate posture
  - not a first-wave family while its own blocker remains active and unbounded
- Wave classification:
  - later-wave candidate

### F.6 `zeta.family.bounded_authority_handoff_and_state_transfer`

- Title: Bounded authority handoff and state transfer
- Current readiness class: `blocked`
- Required prerequisite categories:
  - admission and governance freeze
  - distributed continuity proof
  - replay, snapshot, and proof-anchor continuity
  - runtime cutover legality
  - trust prerequisites and convergence
  - receipt and provenance anchorization
  - review and privilege posture
  - operational realization substrate
- Governing doctrine:
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `STATE_EXTERNALIZATION`
  - `EVENT_LOG_AND_REPLAY_DOCTRINE`
  - `SNAPSHOT_SERVICE_DOCTRINE`
  - `HOTSWAP_BOUNDARIES`
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
- Unresolved blocker dependencies:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.deterministic_replication_and_state_partition_transfer_proof`
  - `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Notes on bounded-entry suitability:
  - not appropriate for a first wave because the core authority-transfer proof stack is still missing
  - remains a later-wave family that can only become admissible after proof, trust, and receipt blockers narrow materially
  - authority regions and handoff meaning now exist doctrinally, but that does not admit live transfer
- Wave classification:
  - later-wave candidate

### F.7 `zeta.family.live_trust_revocation_and_publication_execution`

- Title: Live trust, revocation, and publication execution
- Current readiness class: `blocked`
- Required prerequisite categories:
  - admission and governance freeze
  - trust prerequisites and convergence
  - release and rollback envelope
  - receipt and provenance anchorization
  - review and privilege posture
  - operational realization substrate
- Governing doctrine:
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT`
  - `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`
- Unresolved blocker dependencies:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_trust_revocation_publication_execution_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Notes on bounded-entry suitability:
  - not suitable for a first wave because trust-root bundles remain absent, trust policies remain provisional, and live publication or trust execution systems are not realized
  - remains a later-wave family only after trust convergence and live execution posture move out of blocker status
  - doctrine existence here is not operational maturity
- Wave classification:
  - not admissible for first wave

### F.8 `zeta.family.live_shard_relocation`

- Title: Live shard relocation
- Current readiness class: `future_only_prohibited_for_now`
- Required prerequisite categories:
  - admission and governance freeze
  - distributed continuity proof
  - replay, snapshot, and proof-anchor continuity
  - runtime cutover legality
  - trust prerequisites and convergence
  - receipt and provenance anchorization
  - review and privilege posture
  - operational realization substrate
- Governing doctrine:
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `FOUNDATION_READINESS_MATRIX`
  - `CAPABILITY_LADDER`
  - `STOP_CONDITIONS_AND_ESCALATION`
- Unresolved blocker dependencies:
  - `zeta.blocker.deterministic_replication_and_state_partition_transfer_proof`
  - `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_trust_revocation_publication_execution_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
  - `zeta.blocker.distributed_shard_relocation_live_execution`
- Notes on bounded-entry suitability:
  - explicitly outside bounded near-term `Ζ-A`
  - remains a perimeter family because readiness artifacts still mark distributed shard relocation as unrealistic currently
  - must not be normalized into first-wave or general `Ζ` readiness language
- Wave classification:
  - not admissible

## G. First-Wave Candidate Analysis

The most plausible bounded `Ζ-A` first-wave families are:

- `zeta.family.rollback_bearing_staged_transition_validation`
- `zeta.family.bounded_runtime_cutover_proof_rehearsal`
- `zeta.family.distributed_replay_and_proof_anchor_verification`

Why these are the best first-wave candidates:

- they are proof-oriented, rehearsal-oriented, or rollback-bearing rather than live authority-transfer or live trust-execution families
- their governing doctrine is already explicit across runtime, release, receipt, and blocker-baseline law
- they reduce the most central open blockers without requiring premature claims about trust convergence or shard relocation
- they can be bounded more honestly around verification, rehearsal, refusal, and rollback posture

Even these are not automatically executable. They remain bounded candidates only after `Ζ-P2` freezes gates against the unresolved blocker stack.

## H. Non-Admissible And Later-Wave Analysis

Families that must not be part of a first wave are:

- `zeta.family.bounded_authority_handoff_and_state_transfer`
- `zeta.family.live_trust_revocation_and_publication_execution`
- `zeta.family.live_shard_relocation`

Why these remain later-wave or non-admissible:

- authority handoff and state transfer still depend on deterministic replication proof, distributed replay continuity, runtime cutover proof, trust convergence, and stronger receipt realization
- live trust, revocation, and publication execution still depend on unrealized live trust posture, trust-root distribution, revocation propagation, and stronger receipt continuity
- live shard relocation remains explicitly unrealistic in the current readiness ladder and foundation matrix

Families that are later-wave but potentially useful after the first wave narrows blockers are:

- `zeta.family.trust_aware_refusal_and_containment`
- `zeta.family.live_cutover_receipt_pipeline_anchorization`

These can only move once `Ζ-P2` freezes stricter admission posture and later checkpoints verify that they remain bounded and non-deceptive.

## I. Doctrine Vs Admission Vs Realization Distinction

The governing distinction is:

- doctrine
  - the repo has frozen the governing meaning, boundary classes, and invalidity classes
- admission
  - the matrix says a family may later be gateable or reviewable under bounded conditions
- realization
  - the repo has actual live machinery, proof packets, and exercised execution posture
- bounded-entry suitability
  - the family is or is not a good candidate for a bounded first wave

Those are not the same.

Explicit eliminations of ambiguity:

- doctrine exists is not family admissible
- blocker reduced is not blocker gone
- code surface exists is not realization complete
- Ζ-P readiness is not all candidate families equally ready
- matrix admission is not execution permission

## J. Extension-Over-Replacement Directives

`Ζ-P2` and later bounded `Ζ-A` work must:

- consume `Ζ-P0` and this matrix as the canonical pre-gate baseline
- preserve family ids unless a later prompt records an explicit split, merge, or supersession mapping
- preserve unresolved blocker visibility instead of silently promoting families into readiness
- preserve doctrine vs admission vs realization vs bounded-entry suitability distinctions
- preserve the first-wave versus later-wave separation frozen here unless later checkpoint law explicitly changes it

Later work must not:

- restate family selection from stale checkpoint wording
- infer admission from doctrine alone
- infer realization from shard, net, CI, mirror, or archive substrate
- choose convenience families because they look easier to demo
- promote live trust or distributed handoff families into first-wave scope without explicit blocker reduction

## K. Ownership And Anti-Reinvention Cautions

The prior cautions remain fully binding:

- ownership-sensitive roots remain active:
  - `field/` versus `fields/`
  - `schema/` versus `schemas/`
  - `packs/` versus `data/packs/`
- canonical prose and semantic specs outrank projected or generated mirrors
- stale numbering or titles in older planning artifacts remain evidence rather than authority
- family selection must come from doctrine and blocker reconciliation, not invention

Additional caution applies here because shard, net, trust, and release substrate can look operationally mature while still remaining only precursor evidence. Local capability surfaces do not by themselves establish bounded-entry suitability.

## L. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- treating every family as equally ready because `Ζ-P` is ready with cautions
- treating doctrine existence as bounded-entry admission
- ignoring unresolved blockers because code evidence exists
- selecting first-wave families by convenience instead of matrix logic
- admitting live trust, publication, or authority-transfer families into first-wave scope without the missing prerequisites
- flattening doctrine, admission, realization, and bounded-entry suitability into one readiness concept
- silently promoting live shard relocation or other perimeter families into bounded `Ζ-A`

## M. Stability And Evolution

This matrix is:

- canonical for the `Ζ-P1` horizon
- provisional until `Ζ-P2` freezes execution gates and the immediate post-`Ζ-P` checkpoint confirms the resulting bounded-entry surface

Later prompts that must consume this artifact:

- `Ζ-P2 — ZETA_EXECUTION_GATES-0`
- immediate post-`Ζ-P` checkpoint
- later bounded `Ζ-A` planning and admission work

Update discipline:

- later prompts may refine family status only by explicit mapping
- later prompts may split or merge family entries only if they preserve ancestry back to this matrix
- later prompts must not silently delete later-wave or non-admissible families merely because earlier proof-oriented families advance
