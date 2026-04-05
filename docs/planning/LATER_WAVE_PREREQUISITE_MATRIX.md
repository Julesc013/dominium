Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: `Ζ-B2`, `C-ZETA_B_ADMISSION_REVIEW`, later bounded `Ζ`
Replacement Target: later `Ζ-B2` and the later-wave admission checkpoint may refine gate posture and family readiness without replacing the later-wave matrix law frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_POST_ZETA_A_FIRST_WAVE_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZA_FIRST_WAVE.md`, `docs/planning/ZETA_BLOCKER_RECONCILIATION.md`, `docs/planning/LIVE_OPERATIONS_PREREQUISITE_MATRIX.md`, `docs/planning/ZETA_EXECUTION_GATES.md`, `docs/planning/LATER_WAVE_BOUNDARY_RECONCILIATION.md`, `docs/runtime/DISTRIBUTED_AUTHORITY_FOUNDATIONS.md`, `docs/runtime/DISTRIBUTED_REPLAY_AND_PROOF_ANCHOR_VERIFICATION.md`, `docs/runtime/BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL.md`, `docs/runtime/ROLLBACK_BEARING_STAGED_TRANSITION_VALIDATION.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`, `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`, `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `data/planning/checkpoints/checkpoint_c_post_zeta_a_first_wave_review.json`, `data/planning/zeta_blocker_reconciliation_registry.json`, `data/planning/live_operations_prerequisite_matrix.json`, `data/planning/zeta_execution_gates_registry.json`, `data/planning/later_wave_boundary_reconciliation_registry.json`, `data/registries/net_replication_policy_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/provenance_classification_registry.json`, `server/shard/dom_cross_shard_log.h`, `server/net/dom_server_protocol.h`, `server/net/dom_server_runtime.h`, `security/trust/trust_verifier.py`

# Later-Wave Prerequisite Matrix

## A. Purpose And Scope

This matrix exists because `Ζ-B0` froze the later-wave candidate boundary but did not yet map each later-wave family to the prerequisites, review posture, blocker dependencies, and missing realization that still govern it.

It solves a specific planning problem:

- later-wave bounded `Ζ` is still `premature`
- first-wave completion must not be mistaken for later-wave readiness
- realization-heavy families remain too easy to over-admit if they are only named and not matrixed
- `Ζ-B2` needs one family-by-family prerequisite surface rather than interpretive drift

This artifact governs:

- the candidate later-wave families frozen by `Ζ-B0`
- the prerequisite categories those families depend on
- the distinction among doctrinal availability, candidacy status, realization dependency, execution admissibility, and later-wave suitability
- the matrix baseline that `Ζ-B2` and the later-wave admission checkpoint must extend rather than replace

This artifact does not:

- execute later-wave bounded `Ζ`
- freeze final later-wave gates
- implement runtime, trust, publication, receipt-pipeline, transfer, or relocation machinery
- widen first-wave families into later-wave realization work

## B. Current Admission Context

This is a:

- `post-bounded-first-wave-Ζ-A / pre-later-wave-gate-refresh` matrix

Later-wave bounded `Ζ` remains `premature` because:

- `Ζ-A0` remains bounded-only
- `Ζ-A1` remains proof-only
- `Ζ-A2` remains proof-only and frozen pending unresolved blockers
- `Ζ-B0` only reconciled later-wave boundary; it did not admit any later-wave family
- trust roots remain empty, trust policies remain provisional, and replication policies remain provisional
- receipt and provenance law exists, but a realized live receipt pipeline does not

Family-level prerequisite mapping is therefore required before later-wave gate freezing so `Ζ-B2` can distinguish:

- plausible refresh candidates
- candidates only with cautions
- review-gated families
- blocked realization-heavy families
- future-only perimeter families

## C. Source-Of-Truth Inputs

The authoritative inputs for this matrix are:

- latest post-first-wave checkpoint law
  - `CHECKPOINT_C_POST_ZETA_A_FIRST_WAVE_REVIEW`
  - `NEXT_EXECUTION_ORDER_POST_ZA_FIRST_WAVE`
- later-wave boundary baseline
  - `LATER_WAVE_BOUNDARY_RECONCILIATION`
  - `later_wave_boundary_reconciliation_registry.json`
- pre-`Ζ` blocker, matrix, and gate law
  - `ZETA_BLOCKER_RECONCILIATION`
  - `LIVE_OPERATIONS_PREREQUISITE_MATRIX`
  - `ZETA_EXECUTION_GATES`
- bounded first-wave doctrine
  - `ROLLBACK_BEARING_STAGED_TRANSITION_VALIDATION`
  - `DISTRIBUTED_REPLAY_AND_PROOF_ANCHOR_VERIFICATION`
  - `BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL`
- runtime and release/trust doctrine
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `HOTSWAP_BOUNDARIES`
  - `EVENT_LOG_AND_REPLAY_DOCTRINE`
  - `SNAPSHOT_SERVICE_DOCTRINE`
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
  - `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`
- evidence roots used only as evidence
  - `data/registries/net_replication_policy_registry.json`
  - `data/registries/trust_policy_registry.json`
  - `data/registries/trust_root_registry.json`
  - `data/registries/provenance_classification_registry.json`
  - `server/shard/dom_cross_shard_log.h`
  - `server/net/dom_server_protocol.h`
  - `server/net/dom_server_runtime.h`
  - `security/trust/trust_verifier.py`

## D. Candidate Later-Wave Families

The candidate later-wave families assessed here are:

- `zeta.family.trust_aware_refusal_and_containment`
  - trust/publication realization-adjacent family
- `zeta.family.live_cutover_receipt_pipeline_anchorization`
  - cutover receipt-pipeline family
- `zeta.family.bounded_authority_handoff_and_state_transfer`
  - replication and state-transfer proof family
- `zeta.family.live_trust_revocation_and_publication_execution`
  - realization-heavy trust/publication family
- `zeta.family.live_shard_relocation`
  - future-only perimeter distributed movement family

Category note:

- `later_wave.category.replay_and_proof_continuity_realization_adjacent_families` remains a valid later-wave category
- no standalone later-wave family is named inside it yet because widening `Ζ-A1` into realization scope would violate the first-wave freeze

## E. Matrix Dimensions

The later-wave matrix assesses each family across these dimensions:

- `doctrinal_availability`
  - whether governing law exists already
- `candidacy_status`
  - whether the family is only a candidate, review-sensitive, excluded, or perimeter-only
- `blocker_dependency`
  - which unresolved blocker entries remain binding
- `realization_dependency`
  - which missing live capabilities still block honest admission
- `proof_requirement`
  - whether replication, replay, cutover, or proof-anchor proof remains upstream
- `trust_convergence_requirement`
  - whether distributed trust convergence or live trust posture remains upstream
- `replay_proof_continuity_requirement`
  - whether replay, snapshot, state, and proof-anchor continuity remain upstream
- `cutover_legality_requirement`
  - whether lawful hotswap and distributed-authority cutover posture remain upstream
- `receipt_provenance_requirement`
  - whether stronger cutover receipts and provenance anchors remain upstream
- `review_privilege_posture`
  - whether explicit human review remains mandatory
- `later_wave_suitability`
  - whether the family is a plausible refresh candidate, candidate only with cautions, blocked, or future-only

Readiness vocabulary frozen for later-wave assessment:

- `later_wave_candidate_pending_gate_refresh`
  - plausible later-wave matrix candidate, but no gate passage exists yet
- `candidate_only_with_cautions`
  - candidate remains matrix-refreshable only under stronger blocker visibility and guardrails
- `review_gated_only`
  - candidate remains full-review-sensitive and is not near automatic later-wave admission
- `blocked_by_unresolved_realization`
  - family remains too central to unresolved realization blockers
- `future_only_perimeter`
  - family remains outside bounded near-term later-wave scope

## F. Family-By-Family Matrix

### F.1 `zeta.family.trust_aware_refusal_and_containment`

- Title: Trust-aware refusal and containment
- Current readiness class: `review_gated_only`
- Required prerequisite categories:
  - admission and governance refresh
  - first-wave freeze preservation
  - release contract and operator continuity
  - trust prerequisites and convergence
  - receipt and provenance anchorization
  - review and privilege posture
  - operational realization substrate
- Governing doctrine:
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`
- Unresolved blocker dependencies:
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_trust_revocation_publication_execution_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Notes on later-wave suitability:
  - plausible for matrix refresh because refusal and containment are narrower than live trust execution
  - still review-gated because trust roots are empty and trust policy posture remains provisional
  - not later-wave admitted by this matrix
- Later-wave classification:
  - review-gated only

### F.2 `zeta.family.live_cutover_receipt_pipeline_anchorization`

- Title: Live cutover receipt pipeline and anchorization
- Current readiness class: `candidate_only_with_cautions`
- Required prerequisite categories:
  - admission and governance refresh
  - first-wave freeze preservation
  - release contract and operator continuity
  - replay, snapshot, and proof-anchor continuity
  - runtime cutover legality
  - receipt and provenance anchorization
  - review and privilege posture
  - operational realization substrate
- Governing doctrine:
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
  - `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`
  - `BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL`
  - `ZETA_EXECUTION_GATES`
- Unresolved blocker dependencies:
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Notes on later-wave suitability:
  - plausible for matrix refresh because first-wave doctrine clarified receipt posture and cutover evidence boundaries
  - still caution-heavy because canonical live receipt emission and lawful cutover proof remain unresolved
  - local traces and logs remain derived evidence only
- Later-wave classification:
  - candidate only with cautions

### F.3 `zeta.family.bounded_authority_handoff_and_state_transfer`

- Title: Bounded authority handoff and state transfer
- Current readiness class: `blocked_by_unresolved_realization`
- Required prerequisite categories:
  - admission and governance refresh
  - first-wave freeze preservation
  - release contract and operator continuity
  - deterministic replication and partition transfer proof
  - replay, snapshot, and proof-anchor continuity
  - runtime cutover legality
  - trust prerequisites and convergence
  - receipt and provenance anchorization
  - review and privilege posture
  - operational realization substrate
- Governing doctrine:
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `HOTSWAP_BOUNDARIES`
  - `DISTRIBUTED_REPLAY_AND_PROOF_ANCHOR_VERIFICATION`
  - `BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL`
  - `ZETA_EXECUTION_GATES`
- Unresolved blocker dependencies:
  - `zeta.blocker.deterministic_replication_and_state_partition_transfer_proof`
  - `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Notes on later-wave suitability:
  - doctrinally meaningful, but still too central to the unresolved realization stack
  - first-wave verification and rehearsal doctrine must not be reinterpreted as lawful transfer proof
  - not honest matrix-refresh admission until blockers materially narrow
- Later-wave classification:
  - blocked by unresolved realization

### F.4 `zeta.family.live_trust_revocation_and_publication_execution`

- Title: Live trust, revocation, and publication execution
- Current readiness class: `blocked_by_unresolved_realization`
- Required prerequisite categories:
  - admission and governance refresh
  - first-wave freeze preservation
  - release contract and operator continuity
  - trust prerequisites and convergence
  - receipt and provenance anchorization
  - review and privilege posture
  - operational realization substrate
- Governing doctrine:
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
  - `ZETA_BLOCKER_RECONCILIATION`
- Unresolved blocker dependencies:
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_trust_revocation_publication_execution_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Notes on later-wave suitability:
  - doctrine exists, but candidacy does not honestly mature because trust roots remain empty and trust policy posture remains provisional
  - this family stays realization-heavy rather than bounded-later-wave-ready
  - not admissible in the current `Ζ-B` band
- Later-wave classification:
  - blocked by unresolved realization

### F.5 `zeta.family.live_shard_relocation`

- Title: Live shard relocation
- Current readiness class: `future_only_perimeter`
- Required prerequisite categories:
  - admission and governance refresh
  - first-wave freeze preservation
  - deterministic replication and partition transfer proof
  - replay, snapshot, and proof-anchor continuity
  - runtime cutover legality
  - trust prerequisites and convergence
  - receipt and provenance anchorization
  - review and privilege posture
  - operational realization substrate
- Governing doctrine:
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `HOTSWAP_BOUNDARIES`
  - `ZETA_EXECUTION_GATES`
  - `ZETA_BLOCKER_RECONCILIATION`
- Unresolved blocker dependencies:
  - `zeta.blocker.deterministic_replication_and_state_partition_transfer_proof`
  - `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_trust_revocation_publication_execution_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
  - `zeta.blocker.distributed_shard_relocation_live_execution`
- Notes on later-wave suitability:
  - remains perimeter-only and outside the current `Ζ-B` band
  - no server, shard, transport, or replication substrate narrows this enough for later-wave candidacy
  - may not be pulled inward by convenience
- Later-wave classification:
  - future-only / perimeter

## G. Candidate Later-Wave Analysis

The plausible later-wave refresh candidates are:

- `zeta.family.trust_aware_refusal_and_containment`
  - plausible only because bounded refusal and containment are narrower than live trust execution
  - still full-review-sensitive and not near admission
- `zeta.family.live_cutover_receipt_pipeline_anchorization`
  - plausible only because first-wave doctrine clarified receipt posture and cutover evidence boundaries
  - still caution-heavy and not near realization

These are matrix-refresh candidates, not later-wave admissions.

## H. Non-Admissible / Perimeter Analysis

The following families must remain outside later-wave admission for now:

- `zeta.family.bounded_authority_handoff_and_state_transfer`
  - blocked because authority transfer still depends on nearly the full unresolved realization stack
- `zeta.family.live_trust_revocation_and_publication_execution`
  - blocked because doctrine existence does not compensate for empty trust-root posture, provisional trust policy posture, and missing live execution machinery
- `zeta.family.live_shard_relocation`
  - future-only perimeter because relocation remains beyond bounded near-term `Ζ`

Additional boundary note:

- replay/proof continuity realization-adjacent scope remains a category, not an admitted family
- first-wave replay verification must not be relabeled into later-wave realization scope

## I. Doctrine Vs Candidacy Vs Realization Distinction

The binding distinctions are:

- doctrine may exist
  - the family can be described lawfully
- candidacy may exist
  - the family may enter `Ζ-B1` or `Ζ-B2` analysis
- later-wave suitability may exist
  - the family may be plausible, caution-heavy, review-gated, blocked, or future-only
- realization may still be absent
  - proof, trust, transfer, cutover, and receipt machinery still do not exist in admissible form

These are not the same thing:

- doctrine exists does not mean later-wave admissible
- candidate does not mean admitted
- code surface exists does not mean realization complete
- first-wave completion does not mean later-wave readiness

## J. Extension-Over-Replacement Directives

`Ζ-B2` and the later-wave admission checkpoint must extend or preserve:

- `LATER_WAVE_BOUNDARY_RECONCILIATION`
- `ZETA_BLOCKER_RECONCILIATION`
- `LIVE_OPERATIONS_PREREQUISITE_MATRIX`
- `ZETA_EXECUTION_GATES`
- `ROLLBACK_BEARING_STAGED_TRANSITION_VALIDATION`
- `DISTRIBUTED_REPLAY_AND_PROOF_ANCHOR_VERIFICATION`
- `BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL`
- the active blocker truth that trust roots remain empty, trust and replication policies remain provisional, and receipt-pipeline realization remains absent

Later work must avoid replacing:

- first-wave freeze law with later-wave naming convenience
- blocker truth with substrate optimism
- canonical planning law with stale numbering or legacy `Ζ` placeholders
- doctrine-versus-realization discipline with implementation wishfulness

## K. Ownership And Anti-Reinvention Cautions

The following cautions remain binding:

- `fields/` remains canonical semantic field substrate while `field/` remains transitional
- `schema/` remains canonical semantic contract law while `schemas/` remains projection-facing
- `packs/` remains canonical for runtime packaging and activation scope while `data/packs/` remains scoped authored-pack authority
- canonical prose and semantic specs outrank projected or generated mirrors
- the thin `runtime/` root is not canonical by name alone
- family selection must come from `Ζ-B0` and checkpoint law, not invention
- stale numbering or titles do not override the active checkpoint chain
- later-wave matrix wording must not loosen first-wave guardrails by convenience

## L. Anti-Patterns / Forbidden Shapes

The following shapes are forbidden:

- every later-wave family treated as equally close
- doctrine existence treated as later-wave admission
- unresolved realization blockers ignored because code evidence exists
- perimeter families pulled inward by convenience
- first-wave completion treated as later-wave blocker closure
- relabeling proof-only or rehearsal-only first-wave outputs as realization support

## M. Stability And Evolution

Stability class:

- `provisional`

This artifact is intended to be consumed by:

- `Ζ-B2 — LATER_WAVE_EXECUTION_GATES_REFRESH-0`
- `C-ZETA_B_ADMISSION_REVIEW — POST_LATER_WAVE_GATE_FREEZE_REASSESSMENT-0`

Update discipline:

- revise this artifact only when a later-wave refresh prompt or later checkpoint explicitly targets it
- do not add new later-wave families merely because a runtime or trust surface exists
- do not promote blocked or perimeter families without explicit later checkpoint authorization
