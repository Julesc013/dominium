Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: `Ζ-P1`, `Ζ-P2`, later post-`Ζ-P` checkpoint, bounded later `Ζ-A`
Replacement Target: later post-`Ζ-P` checkpoint may refine blocker status and downstream sequencing without replacing the blocker-baseline law frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PRE_DISTRIBUTED_AUTHORITY_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB5_ADMISSION_REVIEW.md`, `docs/planning/CHECKPOINT_C_PRE_ZETA_ADMISSION.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB5.md`, `docs/runtime/DISTRIBUTED_AUTHORITY_FOUNDATIONS.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`, `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`, `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/RELEASE_OPS_EXECUTION_ENVELOPE.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `docs/blueprint/CAPABILITY_LADDER.md`, `docs/blueprint/MANUAL_REVIEW_GATES.md`, `docs/blueprint/STOP_CONDITIONS_AND_ESCALATION.md`, `data/runtime/distributed_authority_foundations_registry.json`, `data/planning/readiness/prompt_status_registry.json`, `data/registries/net_replication_policy_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/provenance_classification_registry.json`, `server/shard/shard_api.h`, `server/shard/dom_cross_shard_log.h`, `server/net/dom_server_protocol.h`, `server/net/dom_server_runtime.h`, `release/update_resolver.py`, `security/trust/trust_verifier.py`

# Zeta Blocker Reconciliation

## A. Purpose And Scope

Blocker reconciliation exists because Dominium has now completed the doctrine needed to enter a pre-`Ζ` admission band, but it still does not have one canonical blocker baseline for later `Ζ-P1`, `Ζ-P2`, and bounded `Ζ-A` work.

This artifact solves a specific planning problem:

- older checkpoints carried partially overlapping blocker wording
- several blocker families have now been reduced or resolved doctrinally
- several other blocker families remain active because realization, proof, or gate-freezing is still absent
- later `Ζ-P` work must consume one reconciled baseline rather than improvise or silently drift

This artifact governs:

- the active canonical `Ζ` blocker set after `Φ-B5`
- the normalized blocker taxonomy and status vocabulary
- the mapping from each blocker to the doctrines and evidence surfaces that now govern it
- the distinction among doctrinal readiness, operational admission, and live realization
- the blocker baseline that `Ζ-P1`, `Ζ-P2`, and later bounded `Ζ-A` planning must extend rather than replace

This artifact does not:

- execute `Ζ` work
- implement live-ops machinery
- redefine runtime or release doctrine
- redefine `Φ-B5`
- produce the full `Ζ` plan

## B. Current Admission Context

This is a:

- `post-Φ-B5 / pre-Ζ-P` blocker reconciliation

`Ζ-P` is `ready_with_cautions` because:

- hotswap boundaries are explicit
- distributed authority foundations are explicit
- live trust-transition prerequisites are explicit
- live-cutover receipt and provenance generalization is explicit
- publication and trust execution operationalization gates are explicit

`Ζ-P` is not `Ζ` readiness because:

- replication proof is still absent
- distributed replay and proof-anchor continuity realization is still absent
- runtime cutover proof is still absent
- distributed trust convergence is still absent
- live trust, revocation, publication, and live-cutover receipt realization is still absent

Blocker freezing is therefore required before later gate work so that `Ζ-P1` and `Ζ-P2` do not inherit mixed old/new blocker lists or silently convert doctrine into readiness.

## C. Source-Of-Truth Inputs

The authoritative inputs for this reconciliation are:

- latest checkpoints
  - `CHECKPOINT_C_PRE_DISTRIBUTED_AUTHORITY_REVIEW`
  - `CHECKPOINT_C_PHIB5_ADMISSION_REVIEW`
  - `CHECKPOINT_C_PRE_ZETA_ADMISSION`
- latest forward order
  - `NEXT_EXECUTION_ORDER_POST_PHIB5`
- latest runtime doctrine
  - `HOTSWAP_BOUNDARIES`
  - `DISTRIBUTED_AUTHORITY_FOUNDATIONS`
  - `MULTI_VERSION_COEXISTENCE`
  - `LIFECYCLE_MANAGER`
  - `EVENT_LOG_AND_REPLAY_DOCTRINE`
  - `SNAPSHOT_SERVICE_DOCTRINE`
  - `SANDBOXING_AND_ISOLATION_MODEL`
- latest release and trust doctrine
  - `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`
  - `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`
  - `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
  - `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
  - `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`
  - `RELEASE_OPS_EXECUTION_ENVELOPE`
- live evidence surfaces
  - `data/registries/net_replication_policy_registry.json`
  - `data/registries/trust_policy_registry.json`
  - `data/registries/trust_root_registry.json`
  - `data/registries/provenance_classification_registry.json`
  - `server/shard/shard_api.h`
  - `server/shard/dom_cross_shard_log.h`
  - `server/net/dom_server_protocol.h`
  - `server/net/dom_server_runtime.h`
  - `release/update_resolver.py`
  - `security/trust/trust_verifier.py`

Authority ordering remains strict:

- canon and governance law outrank checkpoint prose
- active checkpoint law outranks older planning drift
- doctrine outranks evidence surfaces when evidence is only precursor substrate
- evidence surfaces still matter for proving whether a blocker is realized or only doctrinally covered

## D. Reconciled Blocker Taxonomy

The canonical blocker categories are:

### D.1 Historical Doctrine-Gap Reductions

Older blocker names that were valid earlier in the checkpoint chain but are no longer active because the missing doctrine layer has now landed.

### D.2 Admission And Governance Blockers

Blockers that remain because the pre-`Ζ` admission packet, prerequisite matrix, or execution-gate freeze is not yet complete.

### D.3 Distributed Continuity Blockers

Blockers tied to deterministic replication, lawful state-partition transfer, distributed replay continuity, and proof-anchor continuity.

### D.4 Cutover Proof Blockers

Blockers tied to runtime cutover proof under the now-explicit hotswap and distributed-authority boundaries.

### D.5 Trust, Revocation, And Publication Realization Blockers

Blockers whose governing doctrine exists, but whose live trust, revocation, publication, or distributed convergence realization remains absent.

### D.6 Receipt And Provenance Realization Blockers

Blockers whose evidence model is explicit, but whose live boundary-sensitive receipt pipeline does not yet exist.

### D.7 Future-Only Perimeter Blockers

Capability families that remain dangerous or future-only and must not be silently normalized into bounded `Ζ-A` scope.

The canonical status vocabulary is:

- `resolved`
- `partially_resolved`
- `doctrinally_established_but_not_operationalized`
- `still_blocked`
- `still_dangerous`
- `still_future_only`

## E. Reconciled Blocker Ledger

### E.1 Historical Doctrine-Gap Reductions

#### `zeta.blocker.distributed_authority_foundation_gap`

- Title: Missing distributed authority foundations
- Status: `resolved`
- Why it no longer remains as an active blocker: `Φ-B5` froze distributed authority meaning, authority regions, handoff boundaries, proof-anchor/quorum subject classes, and invalidity classes.
- Doctrine currently covering it: `docs/runtime/DISTRIBUTED_AUTHORITY_FOUNDATIONS.md`
- What is still missing: realization work now survives under active blockers for replication proof, distributed replay/proof-anchor continuity, runtime cutover proof, and distributed trust convergence.
- Future prompt family: consumed by `Ζ-P1`, `Ζ-P2`, and later bounded `Ζ-A` proof work; not an active doctrine-gap blocker anymore.

#### `zeta.blocker.live_trust_transition_prerequisite_gap`

- Title: Missing live trust rotation and revocation propagation prerequisites
- Status: `resolved`
- Why it no longer remains as an active blocker: `Υ-D0` froze admissibility law for live trust-transition candidates and revocation propagation candidates.
- Doctrine currently covering it: `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`
- What is still missing: live trust, revocation, and publication execution realization still remains active.
- Future prompt family: consumed by `Ζ-P1`, `Ζ-P2`, and later bounded trust/publication realization work.

#### `zeta.blocker.live_cutover_receipt_generalization_gap`

- Title: Missing live-cutover receipt and provenance generalization
- Status: `resolved`
- Why it no longer remains as an active blocker: `Υ-D1` froze the stronger receipt and provenance model needed for live-boundary transitions.
- Doctrine currently covering it: `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`
- What is still missing: a live cutover receipt pipeline remains unrealized.
- Future prompt family: consumed by `Ζ-P1`, `Ζ-P2`, and later bounded receipt-pipeline realization work.

#### `zeta.blocker.publication_trust_operationalization_gate_gap`

- Title: Missing publication and trust execution operationalization gates
- Status: `resolved`
- Why it no longer remains as an active blocker: `Υ-D2` froze the admission layer between doctrine-only meaning and bounded execution posture.
- Doctrine currently covering it: `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`
- What is still missing: live trust, revocation, and publication execution realization remains active.
- Future prompt family: consumed by `Ζ-P1`, `Ζ-P2`, and later bounded trust/publication realization work.

### E.2 Active Admission And Governance Blocker

#### `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`

- Title: Pre-`Ζ` blocker reconciliation and gate freeze
- Status: `still_blocked`
- Why it remains: the active checkpoint explicitly says the surviving blocker set must be reconciled and then fed into a prerequisite matrix and execution-gate layer before any bounded `Ζ` entry.
- Doctrine currently covering it: `CHECKPOINT_C_PRE_ZETA_ADMISSION`, `NEXT_EXECUTION_ORDER_POST_PHIB5`, `AUTHORITY_ORDER`, `GATES_AND_PROOFS`
- What is still missing: `Ζ-P0`, `Ζ-P1`, and `Ζ-P2` outputs do not yet exist as a frozen admission packet.
- Future prompt family: `Ζ-P0`, `Ζ-P1`, `Ζ-P2`

### E.3 Active Distributed Continuity Blockers

#### `zeta.blocker.deterministic_replication_and_state_partition_transfer_proof`

- Title: Deterministic replication and lawful state-partition transfer proof
- Status: `still_blocked`
- Why it remains: replication policy substrate exists, but proof-backed replication, lawful transfer criteria, and verification posture remain absent.
- Doctrine currently covering it: `DISTRIBUTED_AUTHORITY_FOUNDATIONS`, `STATE_EXTERNALIZATION`, `SNAPSHOT_SERVICE_DOCTRINE`, `EVENT_LOG_AND_REPLAY_DOCTRINE`
- Evidence surfaces: `data/registries/net_replication_policy_registry.json`, `server/net/dom_server_runtime.h`, `server/net/dom_server_runtime.cpp`
- What is still missing: proof-backed replication model, explicit partition-transfer proof, admissible verification criteria, and later execution-gate posture.
- Future prompt family: `Ζ-P1`, `Ζ-P2`, later bounded `Ζ-A` distributed continuity proof work

#### `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`

- Title: Distributed replay and proof-anchor continuity realization
- Status: `partially_resolved`
- Why it remains: replay, snapshot, checkpoint, and proof-anchor subject classes are now explicit, but distributed continuity verification is still not realized.
- Doctrine currently covering it: `EVENT_LOG_AND_REPLAY_DOCTRINE`, `SNAPSHOT_SERVICE_DOCTRINE`, `DISTRIBUTED_AUTHORITY_FOUNDATIONS`, `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
- Evidence surfaces: `server/shard/dom_cross_shard_log.h`, `server/shard/shard_api.h`, `server/net/dom_server_protocol.h`, `server/net/dom_server_runtime.h`
- What is still missing: distributed replay verification criteria, proof-anchor continuity records across handoff, and later execution-gate posture.
- Future prompt family: `Ζ-P1`, `Ζ-P2`, later bounded `Ζ-A` distributed replay and proof work

### E.4 Active Cutover Proof Blocker

#### `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`

- Title: Runtime cutover proof under lawful hotswap and distributed-authority boundaries
- Status: `partially_resolved`
- Why it remains: boundary law now exists, but proof that cutover can remain lawful across those boundaries does not.
- Doctrine currently covering it: `HOTSWAP_BOUNDARIES`, `DISTRIBUTED_AUTHORITY_FOUNDATIONS`, `LIFECYCLE_MANAGER`, `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
- Evidence surfaces: `server/net/dom_server_runtime.cpp` transfer checkpoints, lifecycle and checkpoint policy surfaces, `docs/blueprint/STOP_CONDITIONS_AND_ESCALATION.md`
- What is still missing: explicit runtime cutover proof obligations, admissible proof packet structure, and later execution-gate posture.
- Future prompt family: `Ζ-P1`, `Ζ-P2`, later bounded `Ζ-A` runtime cutover proof work

### E.5 Active Trust, Revocation, And Publication Realization Blockers

#### `zeta.blocker.distributed_trust_and_authority_convergence_realization`

- Title: Distributed trust and authority convergence realization
- Status: `doctrinally_established_but_not_operationalized`
- Why it remains: `Φ-B5` now freezes trust-convergence subjects, but nothing yet realizes how distributed authority and trust posture converge lawfully across regions.
- Doctrine currently covering it: `DISTRIBUTED_AUTHORITY_FOUNDATIONS`, `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`, `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`, `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
- Evidence surfaces: `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `security/trust/trust_verifier.py`
- What is still missing: converged distributed trust posture, revocation behavior across regions, and later execution-gate posture.
- Future prompt family: `Ζ-P1`, `Ζ-P2`, later bounded `Ζ-A` distributed trust-convergence work

#### `zeta.blocker.live_trust_revocation_publication_execution_realization`

- Title: Live trust, revocation, and publication execution realization
- Status: `doctrinally_established_but_not_operationalized`
- Why it remains: the prerequisite, continuity, and operationalization doctrine exists, but live trust execution, revocation propagation, and publication execution systems remain unrealized.
- Doctrine currently covering it: `TRUST_EXECUTION_AND_REVOCATION_CONTINUITY`, `LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES`, `PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES`
- Evidence surfaces: `data/registries/trust_root_registry.json` is empty, `data/registries/trust_policy_registry.json` remains provisional, `release/update_resolver.py`, `security/trust/trust_verifier.py`
- What is still missing: live trust-root rotation realization, live revocation propagation realization, publication execution realization, and later execution-gate posture.
- Future prompt family: `Ζ-P1`, `Ζ-P2`, later bounded `Ζ-A` trust/publication execution work

### E.6 Active Receipt And Provenance Realization Blocker

#### `zeta.blocker.live_cutover_receipt_pipeline_realization`

- Title: Live-cutover receipt pipeline realization
- Status: `doctrinally_established_but_not_operationalized`
- Why it remains: the generalized evidence model now exists, but no canonical live-boundary receipt pipeline has been realized.
- Doctrine currently covering it: `OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY`, `LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION`
- Evidence surfaces: `data/registries/provenance_classification_registry.json`, `release/update_resolver.py`
- What is still missing: canonical boundary-sensitive receipt emission, stronger proof anchors in live pathways, and later execution-gate posture.
- Future prompt family: `Ζ-P1`, `Ζ-P2`, later bounded `Ζ-A` receipt-pipeline realization work

### E.7 Future-Only Perimeter Blockers

#### `zeta.blocker.distributed_shard_relocation_live_execution`

- Title: Distributed shard relocation live execution
- Status: `still_dangerous`
- Why it remains: the blueprint still marks relocation as unrealistic without deterministic replication, authority handoff proof, and state-partition transfer proof.
- Doctrine currently covering it: `DISTRIBUTED_AUTHORITY_FOUNDATIONS`, `FOUNDATION_READINESS_MATRIX`, `CAPABILITY_LADDER`
- What is still missing: nearly all realization and proof layers required for live relocation.
- Future prompt family: much later bounded `Ζ-A` or later `Ζ` distributed live-ops work only after admission and proof blockers are closed.

#### `zeta.blocker.extreme_pipe_dream_live_operations`

- Title: Extreme pipe-dream live operations
- Status: `still_future_only`
- Why it remains: cluster-of-clusters, restartless core replacement, and similar families remain outside the bounded `Ζ-A` horizon.
- Doctrine currently covering it: `CAPABILITY_LADDER`, `PIPE_DREAMS_MATRIX`, `STOP_CONDITIONS_AND_ESCALATION`
- What is still missing: multiple earlier runtime, trust, receipt, and live-ops proof layers, plus explicit later admission.
- Future prompt family: not part of current bounded `Ζ-P` or bounded `Ζ-A` planning.

## F. Resolved Vs Unresolved Distinction

Fully resolved doctrinal blockers:

- `zeta.blocker.distributed_authority_foundation_gap`
- `zeta.blocker.live_trust_transition_prerequisite_gap`
- `zeta.blocker.live_cutover_receipt_generalization_gap`
- `zeta.blocker.publication_trust_operationalization_gate_gap`

These are resolved only as doctrine gaps. Their descendant realization blockers remain active where named above.

Partially reduced blockers:

- `zeta.blocker.distributed_replay_and_proof_anchor_continuity_realization`
- `zeta.blocker.runtime_cutover_proof_under_lawful_hotswap_and_distributed_authority_boundaries`

These are partially reduced because their governing law is explicit now, but proof or realization is still absent.

Doctrinally established but not operationalized blockers:

- `zeta.blocker.distributed_trust_and_authority_convergence_realization`
- `zeta.blocker.live_trust_revocation_publication_execution_realization`
- `zeta.blocker.live_cutover_receipt_pipeline_realization`

These are not resolved. They are active precisely because doctrine exists but live realization does not.

Still blocked admission blockers:

- `zeta.blocker.pre_zeta_blocker_reconciliation_and_gate_freeze`
- `zeta.blocker.deterministic_replication_and_state_partition_transfer_proof`

Still dangerous or future-only perimeter blockers:

- `zeta.blocker.distributed_shard_relocation_live_execution`
- `zeta.blocker.extreme_pipe_dream_live_operations`

## G. Doctrine Vs Realization Distinction

The governing distinction is:

- doctrine
  - the repo has frozen the meaning, boundaries, and invalidity classes
- admission
  - the repo has allowed bounded planning or gate work to continue
- realization
  - the repo has actual live systems, proof packets, and execution posture in place

Those are not the same.

Explicit eliminations of ambiguity:

- doctrine exists is not blocker resolved
- code surface exists is not realization complete
- older checkpoint wording is not current blocker truth
- Ζ-P readiness is not Ζ readiness

Examples:

- `Υ-D0` resolved the trust-transition prerequisite doctrine gap, but did not realize live trust rotation
- `Υ-D1` resolved the live-cutover receipt generalization doctrine gap, but did not realize a live-cutover receipt pipeline
- `Υ-D2` resolved the operationalization-gate doctrine gap, but did not realize live publication or trust execution systems
- `Φ-B5` resolved the distributed-authority foundations doctrine gap, but did not realize replication proof, distributed trust convergence, or shard relocation
- `C-PRE_ZETA_ADMISSION` made `Ζ-P` ready with cautions, but did not make `Ζ` ready

## H. Extension-Over-Replacement Directives

Later `Ζ-P1`, `Ζ-P2`, and bounded `Ζ-A` work must:

- consume this reconciled blocker ledger as the canonical baseline
- preserve blocker ids unless an explicit later prompt records a split, merge, or supersession mapping
- extend current checkpoint law instead of reusing stale checkpoint wording directly
- preserve doctrine vs admission vs realization distinctions
- preserve the current active blocker set unless a later prompt explicitly changes status with justification

Later work must not:

- silently delete blockers because doctrine exists
- invent new blocker names for issues already covered here
- promote code-surface evidence into operational readiness
- collapse perimeter blockers into bounded `Ζ-A` scope by convenience

## I. Ownership And Anti-Reinvention Cautions

The repo-wide cautions remain binding:

- ownership-sensitive roots remain active
- canonical versus projected/generated distinctions remain binding
- stale numbering or titles do not override active checkpoint law
- blocker truth must be reconciled from current doctrine plus active checkpoints, not invented greenfield
- implementation filenames may be evidence, but they are not blocker truth on their own

Additional caution applies because shard, net, release, and trust surfaces can look more mature than they are. Evidence of code presence is not evidence of live operational maturity.

## J. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- deleting blockers because doctrine exists
- inventing new blocker names for already-covered issues
- using implementation filenames as blocker truth
- treating evidence of code surfaces as live-ops readiness
- mixing stale checkpoint wording with current law without reconciliation
- treating `Ζ-P` readiness as `Ζ` readiness
- flattening doctrine, admission, and realization into one readiness concept

## K. Stability And Evolution

This blocker baseline is `provisional` because later `Ζ-P1`, `Ζ-P2`, and the post-`Ζ-P` checkpoint may legitimately change blocker status.

This artifact now enables:

- `Ζ-P1 — LIVE_OPERATIONS_PREREQUISITE_MATRIX-0`
- `Ζ-P2 — ZETA_EXECUTION_GATES-0`
- later bounded `Ζ-A` planning that must start from a reconciled blocker baseline
- the immediate post-`Ζ-P` checkpoint

Update discipline:

- later prompts may refine blocker status only by explicit extension
- any blocker rename must record which older blocker ids it absorbs or replaces
- any blocker deletion must record whether it became `resolved`, `partially_resolved`, or `doctrinally_established_but_not_operationalized`
- derived mirrors and dashboards must remain subordinate to this baseline until a later authoritative checkpoint supersedes it
