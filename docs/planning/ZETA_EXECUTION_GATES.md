Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: immediate post-`Ζ-P` checkpoint, bounded later `Ζ-A`, conditional later `Υ-D3`
Replacement Target: later bounded `Ζ-A` admission work and the immediate post-`Ζ-P` checkpoint may refine gate posture without replacing the canonical gate model frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PRE_ZETA_ADMISSION.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB5.md`, `docs/planning/ZETA_BLOCKER_RECONCILIATION.md`, `docs/planning/LIVE_OPERATIONS_PREREQUISITE_MATRIX.md`, `docs/runtime/DISTRIBUTED_AUTHORITY_FOUNDATIONS.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`, `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`, `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT.md`, `docs/release/CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `docs/blueprint/CAPABILITY_LADDER.md`, `docs/blueprint/MANUAL_REVIEW_GATES.md`, `docs/blueprint/STOP_CONDITIONS_AND_ESCALATION.md`, `data/planning/zeta_blocker_reconciliation_registry.json`, `data/planning/live_operations_prerequisite_matrix.json`, `data/registries/net_replication_policy_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/provenance_classification_registry.json`, `server/shard/shard_api.h`, `server/shard/dom_cross_shard_log.h`, `server/net/dom_server_protocol.h`, `server/net/dom_server_runtime.h`, `release/update_resolver.py`, `security/trust/trust_verifier.py`

# Zeta Execution Gates

## A. Purpose And Scope

Execution gates exist because Dominium now has:

- a reconciled blocker baseline in `Ζ-P0`
- a family-by-family prerequisite matrix in `Ζ-P1`

but it still needs one canonical gate freeze that decides what bounded `Ζ-A` work may, may not, or may only conditionally enter.

This artifact solves a specific planning problem:

- `ready_with_cautions` is not actionable by itself
- `Ζ-P0` and `Ζ-P1` contain the necessary analysis, but later bounded entry still needs explicit gate consequences
- first-wave and later-wave families must not be blurred together
- implementation substrate must not be mistaken for gate passage

This artifact governs:

- the canonical gate classes for bounded `Ζ` entry
- the criteria used to assign those gate classes
- the family-by-family gate ledger derived from `Ζ-P0` and `Ζ-P1`
- the frozen first-wave, later-wave, blocked, and prohibited perimeter
- the admission baseline that later bounded `Ζ-A` work must obey

This artifact does not:

- execute `Ζ`
- implement live operations
- define post-entry procedures
- replace `Ζ-P0` or `Ζ-P1`
- widen bounded entry by convenience

## B. Current Admission Context

This is a:

- `post-Φ-B5 / in-Ζ-P / pre-bounded-Ζ-entry` gate freeze

A gate freeze is needed now because:

- `Ζ-P0` has already reconciled the remaining blocker set
- `Ζ-P1` has already mapped live-operation families to prerequisites and bounded-entry suitability
- later bounded `Ζ-A` work needs explicit admission law instead of interpretive drift

`Ζ-P` readiness does not itself admit all families because:

- replication proof is still unresolved
- distributed replay and proof-anchor continuity are still unresolved
- runtime cutover proof is still unresolved
- distributed trust convergence is still unresolved
- live trust, revocation, publication, and receipt-pipeline realization are still unresolved

The gate freeze therefore converts analysis into consequences while keeping those unresolved blockers visible.

## C. Source-Of-Truth Inputs

The authoritative inputs for gate setting are:

- latest checkpoint law
  - `CHECKPOINT_C_PRE_ZETA_ADMISSION`
  - `NEXT_EXECUTION_ORDER_POST_PHIB5`
- blocker baseline
  - `ZETA_BLOCKER_RECONCILIATION`
  - `zeta_blocker_reconciliation_registry.json`
- family matrix
  - `LIVE_OPERATIONS_PREREQUISITE_MATRIX`
  - `live_operations_prerequisite_matrix.json`
- latest runtime doctrine
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `HOTSWAP_BOUNDARIES`
  - `EVENT_LOG_AND_REPLAY_DOCTRINE`
  - `SNAPSHOT_SERVICE_DOCTRINE`
  - `LIFECYCLE_MANAGER`
  - `STATE_EXTERNALIZATION`
  - `SANDBOXING_AND_ISOLATION_MODEL`
  - `MULTI_VERSION_COEXISTENCE`
- latest release, trust, and receipt doctrine
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`
  - `RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT`
  - `CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION`
  - `RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT`
  - `RELEASE_CONTRACT_PROFILE`

Authority ordering remains strict:

- canon and governance law outrank these gates
- active checkpoint law outranks stale planning drift
- `Ζ-P0` blocker truth and `Ζ-P1` family readiness outrank convenience interpretations
- precursor code and registries remain evidence, not gate passage by themselves

## D. Gate Taxonomy

The canonical gate classes are:

### D.1 `admitted_first_wave`

The family may enter bounded first-wave `Ζ-A` planning because its scope can remain narrow, proof-oriented, reversible, and subordinate to the still-open blocker set.

### D.2 `admitted_with_cautions`

The family may enter bounded first-wave `Ζ-A` planning only under stronger guardrails because unresolved blockers still materially constrain how narrow, non-live, or proof-oriented the family must remain.

### D.3 `review_gated`

The family may not enter ordinary first-wave scope. It can be discussed only under explicit review and only when bounded later-wave posture remains visible.

### D.4 `later_wave_only`

The family is deferred out of first-wave scope and may only be reconsidered after earlier proof or convergence gates narrow materially.

### D.5 `blocked`

The family is not admitted because active blockers remain too central to honest bounded entry.

### D.6 `future_only_prohibited`

The family remains outside bounded near-term `Ζ-A` entry entirely.

## E. Gate Criteria

Family gate assignment is determined by:

- blocker status
  - unresolved blocker entries from `Ζ-P0` remain binding
- doctrinal sufficiency
  - the family must have explicit governing law
- prerequisite sufficiency
  - the prerequisite stack from `Ζ-P1` must be satisfiable for the bounded scope being admitted
- proof completeness
  - unresolved replication, replay, proof-anchor, or cutover proof blocks tighter gates
- trust convergence requirements
  - unresolved trust posture, revocation continuity, or publication execution blocks trust-bearing families
- receipt and provenance requirements
  - unresolved live-cutover receipt pipeline realization constrains evidence-bearing families
- cutover legality
  - unresolved hotswap and distributed-authority cutover proof constrains runtime-adjacent families
- bounded-entry suitability
  - first-wave suitability from `Ζ-P1` remains binding unless explicitly narrowed
- review and privilege posture
  - families touching trust, evidence, lifecycle reinterpretation, or authority movement remain review-sensitive

## F. Family Gate Ledger

### F.1 `zeta.family.rollback_bearing_staged_transition_validation`

- Gate class: `admitted_first_wave`
- Rationale:
  - this is the narrowest and most reversible bounded family
  - rollback, downgrade, rehearsal, and release-index law are already explicit
  - the remaining blockers constrain scope but do not prevent bounded staged validation
- Required guardrails:
  - bounded to staged validation, rollback, downgrade, and refusal-aware transition rehearsal
  - no claim that runtime cutover proof is already closed
  - no live authority transfer
  - no live trust, revocation, or publication execution
  - unresolved receipt-pipeline limitations must remain visible in outputs
- Unresolved blockers still attached:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Wave designation:
  - first-wave `Ζ-A` admissible

### F.2 `zeta.family.bounded_runtime_cutover_proof_rehearsal`

- Gate class: `admitted_with_cautions`
- Rationale:
  - the family is a valid first-wave candidate only as proof-bearing rehearsal
  - runtime cutover legality and stronger receipt continuity remain active blockers
  - admission is possible only because the family can stay bounded and non-live
- Required guardrails:
  - rehearsal-only or proof-only posture unless a later checkpoint says otherwise
  - no authority handoff or state transfer
  - explicit proof packet obligations before any claim of lawful cutover
  - no inference of gate passage from protocol or runtime substrate alone
  - lifecycle-sensitive reinterpretation remains `FULL` review
- Unresolved blockers still attached:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Wave designation:
  - first-wave `Ζ-A` admissible only with cautions

### F.3 `zeta.family.distributed_replay_and_proof_anchor_verification`

- Gate class: `admitted_with_cautions`
- Rationale:
  - the family reduces a central blocker through verification instead of live transfer
  - distributed replay continuity and replication proof remain unresolved
  - admission is acceptable only while the family stays verification-only
- Required guardrails:
  - verification-only and no live authority movement
  - no claim that cross-shard logs or replication policies alone prove continuity
  - explicit proof-anchor continuity criteria must remain missing until later work closes them
  - no claim that deterministic replication is already realized
- Unresolved blockers still attached:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.deterministic_replication_and_state_partition_transfer_proof`
  - `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
- Wave designation:
  - first-wave `Ζ-A` admissible only with cautions

### F.4 `zeta.family.trust_aware_refusal_and_containment`

- Gate class: `review_gated`
- Rationale:
  - bounded containment is safer than live trust execution
  - the family still touches trust posture, refusal semantics, and remediation evidence
  - distributed trust convergence and live trust/publication realization remain open blockers
- Required guardrails:
  - `FULL` review for trust and governance implications
  - refusal, containment, and remediation only
  - no trust-root rotation, revocation propagation, or publication execution
  - stronger receipt lineage required for any bounded trial
- Unresolved blockers still attached:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_trust_revocation_publication_execution_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Wave designation:
  - later-wave only and review-gated

### F.5 `zeta.family.live_cutover_receipt_pipeline_anchorization`

- Gate class: `review_gated`
- Rationale:
  - the family changes canonical evidence posture rather than only consuming it
  - receipt pipeline realization remains an active blocker
  - it may become useful later as a bounded shadow evidence path, but not as first-wave scope
- Required guardrails:
  - `FULL` review when canonical evidence semantics are reclassified
  - shadow or parallel evidence posture only
  - no claim that receipt-pipeline realization is complete
  - no promotion of local logs into canonical receipts
- Unresolved blockers still attached:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Wave designation:
  - later-wave only and review-gated

### F.6 `zeta.family.bounded_authority_handoff_and_state_transfer`

- Gate class: `later_wave_only`
- Rationale:
  - the family is now doctrinally meaningful, but it depends on proof and convergence layers that remain open
  - it is too strong for first-wave scope and too central to be treated as already admitted
  - later-wave deferral is more accurate than prohibition because the doctrine now explicitly preserves its bounded future shape
- Required guardrails:
  - not first-wave
  - no authority transfer until deterministic replication, replay continuity, cutover proof, trust convergence, and stronger receipt posture materially narrow
  - no transport success treated as lawful handoff
  - no hidden local state transfer claims
- Unresolved blockers still attached:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.deterministic_replication_and_state_partition_transfer_proof`
  - `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Wave designation:
  - later-wave only

### F.7 `zeta.family.live_trust_revocation_and_publication_execution`

- Gate class: `blocked`
- Rationale:
  - live trust and publication execution remain unrealized
  - trust roots remain empty and trust policies remain provisional
  - the blocker stack is too central to admit even bounded first-wave entry honestly
- Required guardrails:
  - not admitted
  - no live trust execution
  - no live revocation propagation execution
  - no live publication execution
  - no claim that doctrinal operationalization gates equal realized execution systems
- Unresolved blockers still attached:
  - `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_trust_revocation_publication_execution_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
- Wave designation:
  - not admitted

### F.8 `zeta.family.live_shard_relocation`

- Gate class: `future_only_prohibited`
- Rationale:
  - readiness artifacts still mark shard relocation as unrealistic currently
  - the proof, trust, cutover, and receipt prerequisites remain far from satisfied
  - bounded near-term `Ζ-A` must not absorb this perimeter family
- Required guardrails:
  - prohibited for bounded near-term entry
  - no shrink-wrapping relocation into first-wave wording
  - no claim that shard substrate proves relocation readiness
- Unresolved blockers still attached:
  - `zeta.blocker.deterministic_replication_and_state_partition_transfer_proof`
  - `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
  - `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`
  - `zeta.blocker.distributed_trust_and_authority_convergence_realization`
  - `zeta.blocker.live_trust_revocation_publication_execution_realization`
  - `zeta.blocker.live_cutover_receipt_pipeline_realization`
  - `zeta.blocker.distributed_shard_relocation_live_execution`
- Wave designation:
  - prohibited

## G. First-Wave Freeze

The bounded first-wave families admissible after this gate freeze are:

- `zeta.family.rollback_bearing_staged_transition_validation`
- `zeta.family.bounded_runtime_cutover_proof_rehearsal`
- `zeta.family.distributed_replay_and_proof_anchor_verification`

First-wave guardrails that apply to all admitted families:

- bounded entry must remain proof-oriented, verification-oriented, rehearsal-oriented, or rollback-bearing
- unresolved blockers remain attached and must not be restated as solved
- no live authority handoff or state transfer
- no live trust, revocation, or publication execution
- no live shard relocation
- code substrate, registries, or logs do not by themselves establish gate passage

## H. Later-Wave And Prohibited Freeze

Later-wave only families are:

- `zeta.family.trust_aware_refusal_and_containment`
- `zeta.family.live_cutover_receipt_pipeline_anchorization`
- `zeta.family.bounded_authority_handoff_and_state_transfer`

Blocked family:

- `zeta.family.live_trust_revocation_and_publication_execution`

Prohibited family:

- `zeta.family.live_shard_relocation`

This freeze is intentional:

- later-wave families remain bounded future candidates, not current first-wave scope
- blocked families remain outside honest admission until central blockers narrow
- prohibited families remain outside bounded near-term `Ζ-A`

## I. Doctrine Vs Admission Vs Realization Distinction

The governing distinction is:

- doctrine
  - the repo has explicit meaning, boundaries, and invalidity classes
- admission
  - a family has passed or failed the current gate freeze
- realization
  - the repo has actual live systems, proof packets, and exercised execution posture

Those are not the same.

Explicit eliminations of ambiguity:

- Ζ-P readiness is not universal admission
- doctrine exists is not first-wave eligible
- blocker reduced is not blocker gone
- admission is not realization

## J. Extension-Over-Replacement Directives

Later bounded `Ζ-A` work must:

- consume `Ζ-P0`, `Ζ-P1`, and this gate freeze together
- preserve family ids and blocker ids unless a later prompt records explicit ancestry mappings
- preserve the first-wave perimeter frozen here
- preserve doctrine vs admission vs realization distinctions
- preserve unresolved blocker visibility in every bounded family

Later work must not:

- widen first-wave scope by convenience
- promote later-wave families into first-wave scope without explicit later checkpoint law
- reinterpret code substrate as gate passage
- treat review-gated families as ordinary admitted scope
- treat blocked or prohibited families as implicitly deferred demos

## K. Ownership And Anti-Reinvention Cautions

The prior cautions remain fully binding:

- ownership-sensitive roots remain active:
  - `field/` versus `fields/`
  - `schema/` versus `schemas/`
  - `packs/` versus `data/packs/`
- canonical prose and semantic specs outrank projected or generated mirrors
- stale numbering or titles do not override active checkpoint law
- gates must come from blocker reconciliation and matrix results, not invention

Additional caution applies because distributed, trust, and release substrate can look more operational than it really is. Familiar implementation surfaces must not be promoted into gate truth.

## L. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- admitting all families because `Ζ-P` exists
- widening first-wave scope by convenience
- ignoring unresolved blockers because doctrine exists
- treating shard, net, trust, or release code surfaces as gate passage
- treating admission as realization
- silently downgrading blocked families into later-wave scope without justification
- silently downgrading prohibited perimeter families into bounded entry

## M. Stability And Evolution

This gate freeze is:

- canonical for the `Ζ-P2` horizon
- provisional until the immediate post-`Ζ-P` checkpoint reassesses the resulting bounded-entry packet

Later prompts and checkpoints that must consume this artifact:

- immediate post-`Ζ-P` checkpoint
- bounded `Ζ-A` planning and admission prompts
- any later conditional `Υ-D3` consolidation only if the checkpoint finds genuine controller residue

Update discipline:

- later prompts may refine gate class only by explicit mapping
- later prompts may narrow first-wave scope without replacing this artifact
- later prompts may expand scope only after a later checkpoint explicitly records blocker reduction and gate change
