Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: next checkpoint before Φ-B4, risky Φ-B4, risky Φ-B5, later publication and trust operational doctrine, future Ζ planning
Replacement Target: later trust-root rotation, revocation, publication, downgrade, and live-ops operational doctrine may refine procedures and tooling without replacing the trust-execution and revocation-continuity semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB3_YB_SAFE_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB3_YB.md`, `docs/agents/AGENT_TASKS.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/ARCHIVE_AND_MIRROR_CONSTITUTION.md`, `docs/release/PUBLICATION_TRUST_AND_LICENSING_GATES.md`, `docs/release/RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT.md`, `docs/release/CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION.md`, `docs/release/SIGNING_POLICY.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `docs/blueprint/MANUAL_REVIEW_GATES.md`, `security/trust/trust_verifier.py`, `security/trust/license_capability.py`, `repo/release_policy.toml`, `release/update_resolver.py`, `updates/README.md`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/entitlement_registry.json`, `data/registries/provenance_classification_registry.json`, `data/registries/explain_contract_registry.json`, `data/registries/refusal_code_registry.json`, `data/registries/remediation_playbooks.json`

# Trust Execution And Revocation Continuity

## A. Purpose And Scope

This doctrine exists to freeze the canonical meaning of trust execution and revocation continuity in the post-`Φ-B3`, post-`Υ-B`, and in-`Υ-C` control-plane maturity band.

It solves a specific problem. The repository already contains offline-first trust verification, signing policy, provisional trust policies, empty but governed trust-root registry surfaces, release-plan trust checks, publication and trust gates, and provisional provenance types for certificate revocation. Without one explicit doctrine, later work could still drift into dangerous folklore:

- trust posture changes treated like ordinary metadata edits
- revocation treated as silent disappearance
- mirror or publication visibility being mistaken for trust truth
- signer or verifier posture changes happening with no continuity-bearing receipt
- local verifier behavior becoming the real trust authority by convenience
- doctrine being mistaken for proof that live trust mutation is already safe

This document governs:

- what trust execution means in Dominium
- what revocation continuity means in Dominium
- which trust-affecting action classes exist
- which continuity classes must remain explicit across revocation-bearing history
- how trust execution and revocation continuity remain subordinate to governance, safety, publication gates, operator transactions, receipts, release identity and resolution law, archive and mirror law, canary and downgrade law, and runtime doctrine
- what later checkpoints, risky `Φ-B4`, risky `Φ-B5`, and future `Ζ` planning must consume rather than reinvent

It does not govern:

- trust-root rotation implementation
- revocation infrastructure implementation
- signing or verification service implementation
- publication automation
- live cutover or hotswap
- distributed authority implementation

This layer sits after `Υ-C1` because canary and downgrade execution had to be frozen before trust-gated exposure and revocation-sensitive movement could be described honestly.

## B. Core Definition

Trust execution in Dominium is a governed control-plane action that changes trust acceptance, trust refusal, signer or verifier posture, trust-scope applicability, or trust-gated release exposure posture for release-facing artifacts.

Revocation continuity in Dominium is the reconstructable linkage that preserves what was revoked, why it was revoked, under which authority and gate posture it was revoked, how that revocation affected visibility and trust acceptance, and how historical records remain recoverable without confusing present acceptance with past existence.

These meanings differ from nearby surfaces:

- static trust policy text describes a policy surface; it does not by itself execute a trust-bearing change
- generic security events may be informative, but they do not automatically carry canonical release-control meaning
- publication visibility changes alone do not equal trust execution
- archive retention preserves history; it does not define current trust acceptance
- changelog notes summarize; they do not constitute full trust or revocation continuity
- local verification behavior can express one consumer's current posture, but it does not become canonical trust truth by convenience

Trust execution is therefore about governed state transition and acceptance posture. Revocation continuity is about preserving the meaning and history of those transitions across time.

## C. Why This Doctrine Is Necessary

This doctrine is necessary because trust-affecting actions alter acceptance and execution posture for release-facing artifacts, and those changes carry stronger continuity requirements than ordinary metadata updates.

The repo already shows the foundation and the gap:

- `security/trust/trust_verifier.py` already distinguishes `signature_missing`, `signature_invalid`, `verified`, trusted-root matching, and policy-missing refusal outcomes
- `release/update_resolver.py` already carries `trust_policy_id` and `trust_result` into governed update planning
- `data/registries/trust_policy_registry.json` already defines trust-policy ids and unsigned or untrusted-root behavior
- `data/registries/trust_root_registry.json` is still empty, proving that live trust-root maturity is not established
- `data/registries/provenance_classification_registry.json` already distinguishes derived and canonical certificate-revocation artifact classes, proving that the repo expects continuity semantics even before live infrastructure exists

Without this doctrine, later work would still lack one stable answer to:

- what counts as a trust-affecting control-plane action
- what must remain continuous when revocation happens
- how visibility changes relate to trust truth without replacing it
- why local verifier behavior and mirror state are not enough by themselves

Later risky runtime and live-cutover work depend on that distinction.

## D. Trust Action Classes

The following high-level trust action classes are recognized:

### D.1 Trust Posture Activation

A governed action that activates a specific trust posture, trust-policy selection, or trust-bearing acceptance envelope for release-facing artifacts.

### D.2 Trust Posture Reduction

A governed action that narrows what trust posture permits, accepts, or tolerates, including stricter signature requirements or stricter untrusted-root behavior.

### D.3 Signer Or Verifier Posture Change

A governed action that changes signer acceptance posture, verifier strictness, accepted trust levels, or related verification-bearing semantics without pretending that the verifier implementation itself becomes canon.

### D.4 Revocation Declaration

A governed action that declares a signer, artifact, trust path, or trust-bearing acceptance route revoked or otherwise no longer acceptable under current policy.

### D.5 Revocation Propagation Posture

A governed action that defines how revocation-bearing meaning must be carried through trust-bearing records, release-control decisions, consumer-facing interpretation, and historical continuity.

### D.6 Trust-Gated Publication Action

A publication-adjacent action whose visibility or eligibility is explicitly constrained by trust posture, while still preserving that publication visibility and trust acceptance remain distinct.

### D.7 Trust Emergency Containment

A bounded, high-urgency trust-bearing action used to reduce exposure or acceptance posture under explicit review or privilege conditions when a trust incident or signing concern requires containment.

### D.8 Trust Restoration Or Supersession

A governed action that restores acceptance posture, introduces a superseding trust route, or records a successor trust posture without erasing the revoked or reduced history.

## E. Revocation Continuity Classes

The following high-level revocation continuity classes are recognized:

### E.1 Declaration Continuity

The revocation declaration itself must remain reconstructable as a typed, attributable, review-aware control-plane act rather than disappearing into local state.

### E.2 Receipt Continuity

Revocation-bearing actions must preserve canonical receipt continuity, including actor posture, gate posture, affected scope, and resulting trust-bearing meaning.

### E.3 Archive Continuity

Historical artifacts and trust-bearing records may remain archived even after revocation. Archive continuity preserves what existed and what was later revoked without implying current acceptance.

### E.4 Mirror Visibility Continuity

Mirror visibility may change under revocation-bearing policy, but mirror state must remain distinguishable from trust truth. Revocation continuity tracks how that visibility changed without letting the mirror define the revocation.

### E.5 Consumer-Facing Continuity

Consumer-facing summaries, refusal surfaces, and downgraded or warned interpretation must remain coherent enough that a later reader can tell whether a release is hidden, visible, warned, revoked, or historically retained.

### E.6 Local Validation Continuity

Because `security/trust/trust_verifier.py` merges repo-root and install-local trust-root registries, local validation continuity must record that local verifier behavior can vary in bounded ways while remaining subordinate to canonical trust truth.

### E.7 Non-Continuous Or Prohibited Revocation Shapes

Any supposed revocation whose declaration, receipts, archive linkage, visibility consequences, or local-verifier interpretation cannot be reconstructed canonically remains non-continuous and constitutionally deficient.

## F. Relationship To Publication, Trust, And Licensing Gates

Trust execution remains downstream of gate posture.

Therefore:

- trust execution does not create permission by itself
- publication changes and trust changes remain distinct but connected
- publication visibility does not equal trust acceptance
- licensing posture remains separate from trust acceptance even when both are gate-bearing

This doctrine therefore consumes `docs/release/PUBLICATION_TRUST_AND_LICENSING_GATES.md` rather than replacing it. Trust execution is a gated control-plane act, not a shortcut around gate law.

## G. Relationship To Operator Transaction And Receipts

Trust-affecting actions are operator-transaction-bearing.

That means:

- trust posture changes must remain typed
- revocation declarations must remain typed
- trust emergency containment must remain attributable
- restoration or supersession must remain reconstructable

Receipts must preserve trust and revocation semantics explicitly. Revocation continuity therefore depends on canonical evidence, not local heuristics, dashboards, or current verifier state alone.

Trust execution does not replace operator transaction doctrine. It refines the trust-bearing transaction classes that later work must record.

## H. Relationship To Release Contract Profile And Release Index

Trust posture changes must not silently redefine compatibility envelopes.

The governing consequences are:

- release contract profile remains the compatibility envelope
- trust posture remains the acceptance and authenticity posture
- release-index visibility remains distinct from trust acceptance
- revocation continuity must stay compatible with release identity and resolution law

A release may remain indexed and archived while no longer being acceptable under a stricter trust posture. That distinction must remain explicit.

## I. Relationship To Archive And Mirrors

Archive presence does not equal trust acceptance.

Mirror visibility does not equal trust validity.

Revocation continuity must therefore preserve both:

- historical recovery and auditability
- present trust-bearing meaning

The key rules are:

- archive presence is necessary for some historical reconstruction but not sufficient for current acceptance
- mirror removal is not by itself revocation proof
- mirror visibility is not by itself trust validity
- revocation continuity must preserve why an artifact is still historically present even when its trust posture has been reduced or revoked

## J. Relationship To Canary And Downgrade Doctrine

Canary and downgrade execution may be trust-gated.

Revocation continuity may therefore constrain:

- which canary scopes remain lawful
- whether a downgrade target remains acceptable
- whether a recovery downgrade may proceed under current trust posture

But trust changes must not be conflated with downgrade semantics. A revoked trust path is not automatically a downgrade. A downgrade is not automatically a trust restoration. These remain distinct control-plane meanings.

## K. Relationship To Runtime Doctrine

This doctrine must not overclaim live runtime cutover maturity.

If trust changes later imply runtime-affecting behavior, all of the following remain binding:

- lifecycle doctrine
- replay doctrine
- snapshot doctrine
- isolation doctrine
- coexistence doctrine

Trust execution and revocation continuity may prepare the control-plane meaning needed for later work, but they do not prove that live trust mutation, live trust-root rotation, or runtime cutover is safe today.

## L. Invalidity And Failure

The following invalidity and failure classes must remain explicit:

- trust_action_under_authorized: the action was attempted without the required review or privilege posture
- trust_policy_missing_or_undeclared: the requested trust posture is not canonically declared
- trust_root_state_non_governed: signer or root behavior depends on undeclared or non-canonical root state
- revocation_declaration_missing: the supposed revocation has no reconstructable canonical declaration
- revocation_non_propagating: the revocation exists in one local surface but not in the continuity-bearing record
- revocation_local_only: the effect exists only in one local verifier state with no canonical continuity record
- trust_visibility_conflation: publication or mirror state was treated as trust truth
- archive_or_mirror_inference_error: archive or mirror state was treated as sufficient trust evidence
- receipt_chain_incomplete: trust-bearing action history cannot be reconstructed canonically
- restoration_without_supersession_or_receipt: trust posture was widened again without explicit continuity
- runtime_boundary_overclaim: a trust-bearing claim exceeds current runtime maturity

Later checkpoints and tools must not assume that all trust-bearing actions are equally continuous or equally reconstructable.

## M. Canonical Vs Derived Distinctions

Canonical truth in this area lives in:

- the doctrine frozen here
- upstream governance, safety, runtime, and release doctrine
- canonical operator transaction and receipt continuity records
- canonical trust policies, governed trust-root records, and governed release-control records

Derived surfaces include:

- dashboards
- CI summaries
- mirror listings
- changelog notes
- local tool output
- local verifier readouts
- human summaries

Derived views may describe trust or revocation state, but they must not redefine:

- what counts as trust execution
- what counts as revocation
- what counts as continuity
- what counts as current acceptance

## N. Ownership And Anti-Reinvention Cautions

The following cautions remain binding:

- `field/` and `fields/` are not interchangeable ownership roots
- `schema/` and `schemas/` are not interchangeable ownership roots
- `packs/` and `data/packs/` are not interchangeable ownership roots
- canonical artifacts remain upstream of projected or generated mirrors
- convenience wrappers, mirror surfaces, and local verifier outputs are not automatically canonical
- stale planning numbering or titles must not override the active checkpoint chain
- this doctrine must be extracted from current repo reality and already-frozen law rather than invented as a generic security policy story

## O. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- trust-root change treated as metadata edit
- revocation treated as disappearance
- mirror removal treated as revocation proof
- archive absence treated as revocation
- publication visibility treated as trust truth
- local verifier behavior treated as canonical trust truth
- trust execution assumed safe for live runtime cutover because doctrine exists
- signer or verifier posture changes recorded with no continuity-bearing receipt

## P. Stability And Evolution

This artifact is `provisional` because it freezes a necessary trust-bearing continuity layer before the next checkpoint and before any honest reconsideration of `Φ-B4` or `Φ-B5`, but it does not claim live trust-operation maturity.

Later work must consume this artifact as upstream law:

- the next checkpoint before any move toward `Φ-B4`
- later reassessment of risky `Φ-B4` and `Φ-B5`
- future `Ζ` blocker reduction and live-ops planning
- later trust-root rotation, publication, and revocation operational doctrine

Updates to this doctrine must remain:

- explicit
- review-aware
- aligned with gate, receipt, archive, release, and runtime law
- non-silent about what remains unproven

This document answers the current ambiguity set directly:

- trust execution is not publication visibility
- mirror state is not trust truth
- archive presence is not trust acceptance
- revocation continuity is not disappearance from view
