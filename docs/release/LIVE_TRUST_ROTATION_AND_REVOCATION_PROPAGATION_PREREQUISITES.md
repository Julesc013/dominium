Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-D1, Υ-D2, next checkpoint before Φ-B5, later Φ-B5 reassessment, future Ζ planning
Replacement Target: later live trust, revocation, cutover, publication, and distributed-authority operational doctrine may refine procedures and infrastructure without replacing the prerequisite and admissibility semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_YC_SAFE_REVIEW.md`, `docs/planning/CHECKPOINT_C_PRE_DISTRIBUTED_AUTHORITY_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_YC.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB4.md`, `docs/agents/AGENT_TASKS.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/release/PUBLICATION_TRUST_AND_LICENSING_GATES.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT.md`, `docs/release/CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `docs/blueprint/MANUAL_REVIEW_GATES.md`, `security/trust/trust_verifier.py`, `release/update_resolver.py`, `repo/release_policy.toml`, `data/registries/trust_root_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/provenance_classification_registry.json`

# Live Trust Rotation And Revocation Propagation Prerequisites

## A. Purpose And Scope

This doctrine exists because the post-`Φ-B4` checkpoint explicitly kept `Φ-B5 — DISTRIBUTED_AUTHORITY_FOUNDATIONS-0` blocked and identified live trust-root rotation prerequisites plus live revocation propagation continuity as part of the remaining blocker cluster.

It solves a specific problem: Dominium now has explicit law for publication and trust gates, operator transactions, receipts and provenance continuity, rehearsal and rollback alignment, canary and deterministic downgrade execution, trust execution and revocation continuity, and hotswap boundaries. Those layers are necessary, but they still do not say when a live trust transition is even admissible for later operationalization. Without one explicit prerequisite layer, later work could drift into assuming that:

- trust-root rotation is just another review-heavy metadata change
- revocation propagation is proven because one verifier can reject locally
- publication or mirror movement proves trust convergence
- doctrine existence alone proves operational admission
- distributed-authority planning may assume trust convergence that has never been constitutionally admitted

This document governs:

- what live trust rotation means in Dominium
- what revocation propagation means in Dominium
- what prerequisite means for those transition families
- which trust-transition candidate classes exist
- which prerequisite classes must be satisfied before later operationalization is even discussable
- how those prerequisites remain subordinate to governance, safety, release, receipt, archive, canary, hotswap, and runtime law
- what later `Υ-D1`, `Υ-D2`, the next checkpoint, `Φ-B5`, and future `Ζ` planning must consume rather than reinvent

It does not govern:

- trust-root rotation implementation
- revocation propagation services
- verifier synchronization infrastructure
- publication automation
- distributed-authority implementation
- live trust-cutover choreography

This is an admission layer, not execution machinery.

## B. Core Definition

`Live trust rotation` in Dominium is a prospective governed transition that would change trust-root, signer-validity, verifier-acceptance, or equivalent live trust-bearing posture while affected release, verification, or runtime-adjacent surfaces remain materially active.

`Revocation propagation` in Dominium is the prospective governed carrying-forward of revocation meaning across canonical declaration, operator transaction posture, receipt continuity, release resolution, archive and mirror interpretation, consumer-facing visibility, and local validation behavior.

`Prerequisite` in this doctrine means the explicit admissibility floor that must be satisfied before a later prompt may lawfully operationalize or even claim readiness for live trust rotation or revocation propagation. A prerequisite is not a runtime implementation, not a dashboard signal, and not a local success anecdote.

These meanings differ from nearby surfaces:

- static trust policy text declares policy posture; it does not prove live transition readiness
- local verifier behavior proves local acceptance or rejection behavior; it does not prove propagation continuity
- archive or mirror state may preserve historical evidence; it does not prove live trust convergence
- publication visibility changes may reflect a gate outcome; they do not define trust truth
- ordinary metadata edits do not carry live trust-transition meaning
- already-implemented live trust operations do not exist merely because doctrine now names the prerequisites

## C. Why This Prerequisite Layer Is Necessary

This layer is necessary because later distributed-authority and live-cutover work require explicit admission criteria, not only abstract doctrine.

The repo already contains strong precursor evidence:

- `security/trust/trust_verifier.py` proves deterministic local trust-policy and trust-root evaluation behavior
- `release/update_resolver.py` proves that release selection already carries `trust_policy_id`, `trust_result`, rollback transaction anchors, and deterministic refusal posture
- `docs/blueprint/FOUNDATION_READINESS_MATRIX.md` already classifies live trust-root rotation as foundation-ready in concept but not implemented, and it names missing blocks such as online trust-root distribution, rotation receipts, and coordinated revoke workflow
- `docs/blueprint/MANUAL_REVIEW_GATES.md` already marks trust-root governance changes as `FULL` review work
- `data/registries/trust_root_registry.json` remains empty and `data/registries/trust_policy_registry.json` remains provisional, proving that later distributed-authority planning cannot honestly assume converged live trust posture yet

That evidence is enough to justify a prerequisite doctrine. It is not enough to admit live trust operations by itself.

## D. Trust-Transition Candidate Classes

The following high-level trust-transition candidate classes are recognized.

### D.1 Trust-Root Rotation Candidate

A prospective live change in accepted trust-root posture, including introduction, retirement, narrowing, replacement, or staged supersession of root-bearing acceptance anchors.

### D.2 Verifier-Acceptance Transition Candidate

A prospective live change in verifier-side acceptance posture, strictness, fallback behavior, or canonical trust-policy interpretation.

### D.3 Signer-Validity Transition Candidate

A prospective live change in which signer identities, signature chains, or signing-bearing validity envelopes remain accepted for release-facing artifacts.

### D.4 Revocation Declaration Candidate

A prospective canonical declaration that a signer, root, chain, artifact class, or equivalent trust-bearing path is revoked or no longer acceptable.

### D.5 Revocation Propagation Candidate

A prospective live carrying-forward of revocation meaning across release selection, trust-bearing visibility, consumer interpretation, and local validation posture.

### D.6 Trust Emergency Containment Candidate

A prospective bounded, high-urgency reduction of trust acceptance posture intended to contain active risk without pretending that full propagation and later restoration are already solved.

### D.7 Trust Restoration Or Supersession Candidate

A prospective live widening, replacement, or superseding trust posture that must preserve continuity with the previously reduced, revoked, or contained state.

## E. Prerequisite Classes

The following high-level prerequisite classes define what must be true before a live trust-transition candidate is even admissible for later operationalization.

### E.1 Governance Prerequisite

The transition must remain subordinate to canonical governance, authority ordering, checkpoint law, and ownership or bridge cautions. Task catalog presence and MCP exposure do not satisfy this prerequisite.

### E.2 Safety And Approval Prerequisite

The transition must have explicit safety posture, privilege posture, and human-review posture appropriate to its blast radius. This is especially strict for trust-root, signer, verifier, revocation, and emergency-containment candidates.

### E.3 Release-Identity And Profile Prerequisite

The transition must preserve release identity, release contract profile, release-index and resolution semantics, target applicability, and trust-bearing selection meaning. It must not silently redefine compatibility or target truth.

### E.4 Receipt And Provenance Prerequisite

The transition must be operator-transaction-bearing, receipt-bearing, and provenance-continuous. Local logs, CI output, or manual notes do not satisfy this prerequisite.

### E.5 Archive And Mirror Continuity Prerequisite

The transition must preserve the difference among archive continuity, mirror visibility, publication posture, and trust truth. Historical recovery must remain intelligible without implying present acceptance.

### E.6 Runtime Cutover Prerequisite

Any candidate whose trust meaning reaches lifecycle, replay, snapshot, isolation, coexistence, or hotswap boundaries must satisfy those runtime constraints explicitly. If those runtime constraints are still unsolved, the transition remains non-admissible.

### E.7 Non-Admissible Or Prohibited States

Some states remain constitutionally outside admission today, including:

- trust convergence inferred only from local verification
- trust-root rotation with no continuity-bearing receipts
- revocation propagation inferred only from mirror disappearance
- trust change claims that depend on unproven distributed authority
- runtime-affecting trust transitions that exceed current hotswap and cutover maturity

## F. Relationship To Publication/Trust/Licensing Gates

Publication, trust, and licensing gates remain upstream.

This doctrine freezes the distinction between:

- gate passage
- trust-transition admissibility
- later live trust-transition execution

Those are related but not identical.

Gate posture may say that a trust-bearing action class is review-heavy or privileged. This prerequisite doctrine says whether later operationalization is even constitutionally discussable. Publication or mirror visibility must not be mistaken for trust convergence, and trust convergence must not be inferred from a gate-bearing publication posture alone.

## G. Relationship To Operator Transactions And Receipts

Live trust-transition candidates are operator-transaction-bearing control-plane actions.

Therefore:

- they require typed transaction meaning
- they require attributable review and privilege posture
- they require canonical receipt continuity
- they require provenance continuity across declaration, propagation, containment, restoration, or supersession steps
- local logs are insufficient as the canonical record

This doctrine does not replace operator transaction law or receipt law. It adds the admission floor that later trust-transition execution must satisfy before those laws can be applied operationally.

## H. Relationship To Release Profile, Index, Archive, And Mirror Doctrine

Live trust-transition prerequisites must remain compatible with:

- release identity
- release contract profile
- release-index and resolution semantics
- exact target posture where relevant
- archive continuity
- mirror semantics

The governing consequences are:

- archive presence is not live trust readiness
- archive absence is not revocation truth
- mirror disappearance is not revocation propagation proof
- mirror visibility is not trust convergence
- release-index visibility and trust acceptance remain distinct concepts

A trust-transition candidate that cannot preserve these distinctions is not admissible.

## I. Relationship To Canary/Downgrade And Rehearsal/Rollback Doctrine

Later live trust-transition operationalization may depend on bounded canary, downgrade, rehearsal, or rollback-alignment classes. This doctrine preserves those dependencies without overclaiming that they are already operationalized.

The governing consequences are:

- a canary-shaped trust posture remains possible only as a later, explicitly admitted operational class
- downgrade semantics remain distinct from trust-transition semantics
- rehearsal success is not operational admission
- rollback alignment does not prove live trust rotation readiness

This prompt therefore freezes prerequisites for later trust-bearing motion without pretending that the motion already exists.

## J. Relationship To Runtime Doctrine And Hotswap

Live trust-transition prerequisites may intersect with:

- lifecycle legality
- replay continuity
- snapshot legality
- isolation boundaries
- coexistence law
- hotswap boundaries

This doctrine does not prove live runtime cutover maturity.

It instead freezes a stricter rule: if a trust-transition candidate would rely on live cutover assumptions, authority handoff, restartless trust mutation, or runtime convergence behavior not yet admitted by current runtime doctrine, then that candidate remains blocked or future-only.

Hotswap boundaries remain upstream. Trust-transition prerequisites must not silently smuggle distributed-authority or live-cutover claims through release-control convenience.

## K. Invalidity And Failure

The following invalidity and failure classes must remain explicit:

- `governance_under_specified`
- `safety_or_approval_missing`
- `release_identity_or_profile_incoherent`
- `receipt_chain_incomplete`
- `provenance_continuity_missing`
- `archive_or_mirror_inference_error`
- `local_only_behavior_presented_as_propagation`
- `revocation_non_propagating`
- `publication_visibility_conflated_with_trust_convergence`
- `runtime_cutover_overclaim`
- `distributed_authority_dependency_unadmitted`
- `future_only_or_policy_prohibited`

Later checkpoints and tools must not assume that all trust-transition candidates are equally admissible. A candidate may be conceptually meaningful yet still remain constitutionally non-admissible.

## L. Canonical Vs Derived Distinctions

Canonical truth in this area lives in:

- this doctrine
- its paired machine-readable registry
- upstream governance, safety, release, trust, runtime, and hotswap doctrine
- canonical operator transaction and receipt continuity records
- canonical trust policy and trust-root registries with intact provenance

Derived surfaces include:

- dashboards
- summaries
- filenames
- mirror listings
- publication views
- local verifier readouts
- CI or wrapper output

Derived views may summarize candidate posture or local effects. They must not redefine prerequisite truth.

## M. Ownership And Anti-Reinvention Cautions

The repo-wide cautions remain binding:

- ownership-sensitive roots remain active
- canonical versus projected/generated distinctions remain binding
- stale planning titles do not override the active checkpoint chain
- thin convenience roots are not automatically canonical
- prerequisite law must be extracted from current repo doctrine and evidence, not invented as a greenfield trust workflow

Additional caution applies because `docs/release/**`, `release/**`, `updates/**`, `repo/**`, and `security/**` can look operationally central while still remaining subordinate to stronger doctrine and checkpoint law.

## N. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- trust-root change treated as metadata edit
- local verifier behavior treated as revocation propagation proof
- mirror removal treated as revocation proof
- archive absence treated as revocation
- publication visibility treated as trust convergence
- mirror state treated as trust truth
- archive presence treated as live trust readiness
- doctrine existence treated as operational admission
- distributed-authority planning assuming trust convergence that has not passed this prerequisite layer

## O. Stability And Evolution

This artifact is `provisional` because it freezes an admission model needed before `Φ-B5`, not a completed live trust system.

It directly enables:

- `Υ-D1 — LIVE_CUTOVER_RECEIPTS_AND_RUNTIME_CONTINUITY-0`
- `Υ-D2 — PUBLICATION_AND_TRUST_OPERATIONALIZATION_ALIGNMENT-0`
- the next checkpoint after the `Υ-D` band
- later reassessment of `Φ-B5 — DISTRIBUTED_AUTHORITY_FOUNDATIONS-0`
- future `Ζ` blocker reduction around distributed trust and authority convergence

Updates to this doctrine must remain:

- explicit
- review-aware
- aligned with gate, receipt, release, archive, hotswap, and runtime law
- non-silent about what remains unadmitted

This document answers the current checkpoint ambiguity set directly:

- local verifier behavior is not revocation propagation proof
- mirror or publication state is not trust convergence
- archive presence is not live trust readiness
- doctrine existence is not operational admission
