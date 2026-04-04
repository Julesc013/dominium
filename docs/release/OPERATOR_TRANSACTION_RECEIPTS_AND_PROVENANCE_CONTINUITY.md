Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-B2, later checkpoints, risky Φ-B4, risky Φ-B5, future Ζ planning
Replacement Target: later release-ops, operator-transaction, archive, publication, and live-ops operational doctrine may refine receipt transport and storage procedures without replacing the receipt and continuity semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_YA_SAFE_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_YA.md`, `docs/agents/AGENT_TASKS.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/ARCHIVE_AND_MIRROR_CONSTITUTION.md`, `docs/release/PUBLICATION_TRUST_AND_LICENSING_GATES.md`, `docs/release/MANUAL_AUTOMATION_PARITY_AND_REHEARSAL.md`, `docs/release/ARCHIVE_AND_RETENTION_POLICY.md`, `release/update_resolver.py`, `release/archive_policy.py`, `repo/release_policy.toml`, `updates/README.md`, `updates/changelog.json`, `data/registries/provenance_classification_registry.json`, `data/registries/provenance_event_type_registry.json`, `data/registries/deprecation_registry.json`, `data/registries/remediation_playbooks.json`, `data/registries/refusal_code_registry.json`, `data/registries/refusal_to_exit_registry.json`

# Operator Transaction Receipts And Provenance Continuity

## A. Purpose And Scope

This doctrine exists to freeze the canonical meaning of operator transaction receipts and provenance continuity inside the narrow post-`Υ-A` and post-`Φ-B3` operational-alignment band selected by `C-ΥA_SAFE_REVIEW`.

It solves a specific problem: the repository already has pieces of continuity evidence spread across deterministic install transaction logs, archive-history snapshots, release indices, deprecation and remediation registries, refusal registries, provenance classifications, and derived human-facing summaries. Those surfaces are useful, but without one explicit doctrine later work could still drift into unsafe ambiguity:

- operator actions happening with no canonical receipt
- rollback, downgrade, yank, or recovery actions that cannot be reconstructed exactly
- archive presence being mistaken for continuity evidence
- changelog prose or dashboard output being mistaken for the real record
- manual and automated paths producing incompatible evidence about the same action

This document governs:

- what an operator transaction receipt is in Dominium
- what provenance continuity means for release and control-plane history
- which operator and release-control actions require receipt-bearing outcomes
- what those receipts must capture
- how receipt continuity remains subordinate to governance, safety, runtime, and release doctrine
- what later `Υ-B2`, the next checkpoint, risky `Φ-B4`, risky `Φ-B5`, and future `Ζ` planning must consume rather than reinvent

It does not govern:

- receipt storage pipeline implementation
- dashboards or consoles
- release or deployment machinery
- publication workflow implementation
- trust-root operations
- live cutover, hotswap, or distributed authority execution

This is a constitutional receipt-and-continuity standard, not tooling.

## B. Core Definition

An operator transaction receipt in Dominium is the canonical evidence artifact for a typed operator or release-control-plane action outcome. A receipt records the governed meaning of what action was attempted or completed, under what authority and review posture, against which release or artifact scope, using which compatibility and selection context, with what result, refusal, or reversible posture.

Provenance continuity in Dominium is the reconstructable linkage across release and control-plane history that allows later consumers to answer, exactly and without folklore:

- what release or artifact state existed
- what operator transaction affected it
- why the action was allowed, blocked, refused, or reviewed
- what release-contract-profile, release-index, target, and channel facts were relied on
- what resulting visibility, eligibility, archive, mirror, downgrade, rollback, or recovery posture followed

Receipts and provenance continuity differ from nearby surfaces:

- generic logs
  - logs may contain useful telemetry, but they do not automatically carry canonical transaction meaning
- changelog prose
  - changelogs summarize release history for humans; they are not full control-plane continuity
- release manifests
  - manifests describe release artifacts and identities, not the full operator action history that changed visibility, preference, or recovery posture
- archive storage presence
  - retained files prove storage, not the complete meaning of the actions that led to that state
- UI summaries or dashboards
  - they are derived views
- checkpoint bundles
  - they summarize planning or evidence state and do not become operator-control canon by presence alone

The repo already contains deterministic install transaction logging in `release/update_resolver.py` and historical archive-index retention rules in `docs/release/ARCHIVE_AND_RETENTION_POLICY.md`, but those surfaces remain evidence of continuity practice rather than the full constitutional receipt model by themselves.

## C. Why Receipts Are Necessary

Receipts are necessary because typed operator actions must remain attributable, reconstructable, and reviewable even when later tooling changes.

The repository already shows why this layer is needed:

- `release/update_resolver.py` records deterministic install transactions and exposes rollback-selection helpers, proving that transaction history already matters
- `docs/release/ARCHIVE_AND_MIRROR_CONSTITUTION.md` and `docs/release/ARCHIVE_AND_RETENTION_POLICY.md` preserve archive-history snapshots, proving that exact historical retention matters
- `data/registries/provenance_classification_registry.json` distinguishes canonical provenance artifacts from derived explain artifacts, proving that the repo already treats provenance classes as layered, not flat
- `data/registries/refusal_code_registry.json`, `data/registries/refusal_to_exit_registry.json`, and `data/registries/remediation_playbooks.json` preserve refusal and remediation meaning, proving that blocked outcomes also need structured evidence

Without explicit receipt doctrine, later work could keep the files but lose the meaning:

- a rollback could be visible only as a different selected version string
- a yank could be visible only as a changed feed
- a recovery operation could be visible only as a new archive layout
- a rehearsal could be mistaken for a live completion

Receipt law therefore must outlive any specific tool, wrapper, or dashboard.

## D. Receipt Classes

The constitutional receipt classes are:

### D1. Selection Receipts

Record lawful selection-affecting actions such as pinning, redirecting, or resolving a release or component choice under explicit compatibility and policy context.

### D2. Downgrade And Rollback Receipts

Record governed moves to older lawful states or restorations of previously recorded managed states, including the reversibility anchor and the specific prior state being referenced.

### D3. Yank, Deprecation, And Supersession Receipts

Record changes to visibility, default eligibility, warning posture, or preferred-successor relationships without erasing history.

### D4. Recovery And Remediation Receipts

Record bounded corrective actions taken after failed, partial, blocked, unsafe, or inconsistent control-plane outcomes.

### D5. Publication And Trust-Adjacent Receipts

Record review-bearing or privilege-bearing publication, trust, licensing, or visibility transitions where later doctrine permits those actions to be executed.

### D6. Rehearsal Receipts

Record typed rehearsal, dry-run, preflight, or structural-validation outcomes as explicitly non-live evidence.

### D7. Non-Mutating Inspection Receipts

Where later systems require an attributable record of a high-impact inspection or readiness evaluation, non-mutating inspection may produce receipt-bearing evidence. This class remains narrower than generic diagnostic logging.

## E. Receipt Elements

A lawful operator transaction receipt must carry enough evidence to reconstruct both action meaning and resulting continuity posture. Depending on class, a receipt may contain:

- actor or authority class
- transaction class and typed intent
- target release, artifact, component, or scope anchors
- release identity facts
- release contract profile facts
- release index and resolution facts
- target family facts and exact target facts where relevant
- channel or lane facts where relevant
- upstream doctrine inputs relied on
- preconditions, validations, and refusal checks applied
- rehearsal status and rehearsal class where relevant
- review, approval, privilege, or gate posture
- resulting state change or explicit no-change outcome
- reversibility, downgrade, rollback, or non-reversible posture
- archive and mirror consequences
- refusal or blocked outcome class where relevant
- timestamps, ordered sequence anchors, identifiers, and prior-receipt linkage where relevant

The key rule is not that every class must contain every field. The key rule is that a receipt must preserve the real decision and continuity envelope, not merely a human summary or a version string.

## F. Provenance Continuity

Provenance continuity means that release and control-plane history remains reconstructable across time even when visibility, preference, or operational posture changes.

Continuity must preserve linkage across:

- release identity
- release contract profile and compatibility context
- release-index and resolution context
- operator transaction class
- review and safety posture
- archive-history retention
- mirror exposure or non-exposure
- downgrade, rollback, recovery, deprecation, yank, or supersession posture

Continuity does not require that every view be public, mirrored, or human-friendly.

Continuity does require that the canonical record remain coherent enough to answer:

- why a release became visible
- why it became hidden or de-preferred
- why it was yanked or superseded
- why a rollback or downgrade was allowed or refused
- whether a later recovery action restored a prior state or introduced a new one

Historical continuity is therefore a linkage property, not just a storage property.

## G. Relationship To Operator Transaction Doctrine

Receipts refine operator transaction doctrine. They do not replace it.

The governing consequences are:

- operator classes and transaction classes remain upstream in `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`
- receipts provide evidence of those typed actions
- receipts do not create new permission
- missing or ambiguous receipts do not convert an otherwise governed action into a lawful one

This means:

- transaction typing remains upstream
- review posture remains upstream
- receipt law records the evidence of what was attempted or completed under those rules

## H. Relationship To Release Contract Profile And Release Index

Receipts must preserve the real compatibility and selection envelope used.

The governing consequences are:

- raw version strings are insufficient
- build identity is insufficient by itself
- target family labels are insufficient by themselves
- channel or lane labels are insufficient by themselves

When a receipt records a release-control decision, it must preserve enough context to reconnect later readers to:

- the relevant release contract profile
- the relevant release index and selection posture
- the exact target facts where required
- the lane or channel posture when relevant
- the actual selection or refusal reasoning class

Continuity must therefore preserve the real decision envelope, not only the visible winner.

## I. Relationship To Archive And Mirror Doctrine

Archive continuity and receipt continuity must remain compatible.

The governing consequences are:

- mirror visibility is not enough to prove provenance continuity
- archived existence is not enough to prove provenance continuity
- archive history snapshots, retained manifests, and stored bundles may carry necessary evidence, but they are not automatically full receipts
- yanked or superseded artifacts remain historically recoverable, and receipt continuity must make that recoverability intelligible rather than ambiguous

This is why archive law and receipt law remain distinct:

- archive law answers what must be preserved
- receipt law answers what action history must remain reconstructable

## J. Relationship To Safety Policy And Parity/Rehearsal

Safety posture and review posture must remain visible in receipts where applicable.

The governing consequences are:

- receipts must not erase whether an action was allowed, validation-required, review-required, privileged, prohibited, or refused
- rehearsal outcomes must remain clearly marked as rehearsal outcomes
- manual and automated routes should produce compatible receipt classes where `Υ-B0` requires parity
- parity of receipt class does not imply permission to automate the action

This preserves four central distinctions:

- logs do not equal receipts
- exposure does not equal permission
- parity does not equal permission
- rehearsal receipt does not equal live execution receipt

## K. Relationship To Runtime Doctrine

Receipts and provenance continuity remain primarily release and control-plane doctrine, but they must not flatten runtime law where release actions interact with runtime-facing assumptions.

The governing consequences are:

- receipts must not overclaim live cutover maturity
- receipts must not treat coexistence as proof of hotswap legality
- receipts must not collapse lifecycle, replay, snapshot, and isolation distinctions into generic action text
- where operator actions interact with runtime-sensitive envelopes, the receipt should preserve that the runtime boundary was relevant without pretending the runtime boundary was fully solved

This matters especially for later `Φ-B4`, `Φ-B5`, and `Ζ` work.

## L. Invalidity And Failure

Later systems must not assume every control-plane history is equally complete or equally canonical.

The main invalidity and failure categories are:

- `missing_receipt`
- `partial_receipt`
- `noncanonical_receipt_only`
- `ambiguous_target_or_scope`
- `profile_context_missing`
- `resolution_context_missing`
- `review_or_authority_posture_missing`
- `rehearsal_live_confusion`
- `archive_presence_without_receipt_continuity`
- `mirror_visibility_without_receipt_continuity`
- `contradictory_receipt_chain`
- `non_reconstructable_history`
- `runtime_boundary_overclaim`

Continuity gaps must remain visible rather than being silently papered over by friendly summaries.

## M. Canonical Vs Derived Distinctions

Canonical receipt and continuity surfaces include:

- this doctrine
- its paired machine-readable registry
- governed operator transaction records where later doctrine explicitly defines them
- governed archive-history and release-index linkage when tied to canonical receipt-bearing meaning

Derived or projection surfaces include:

- dashboards
- UI summaries
- CLI summaries
- filenames
- mirror layout
- changelog prose
- checkpoint bundles
- convenience reports

Derived surfaces may summarize continuity, but they must not redefine receipt truth or stand in for missing canonical receipts.

## N. Ownership And Anti-Reinvention Cautions

The repo-wide cautions remain fully active:

- `fields/` remains canonical semantic field substrate; `field/` remains transitional
- `schema/` remains canonical semantic contract law; `schemas/` remains projection-facing
- `packs/` remains canonical for runtime packaging and activation scope; `data/packs/` remains scoped authored-pack authority in residual split territory
- canonical versus projected/generated distinctions remain binding
- planning drift and stale numbering do not override the active checkpoint chain
- receipt and continuity law must be extracted from current doctrine and repo evidence rather than invented greenfield

Additional caution:

- existing deterministic logs, history snapshots, and provenance registries are strong evidence surfaces, but they do not by themselves prove that the full receipt model has already been operationalized

## O. Anti-Patterns And Forbidden Shapes

The following shapes are constitutionally forbidden:

- operator action with no receipt where receipt-bearing class is required
- release history inferred only from filenames
- archive presence treated as full provenance continuity
- mirror existence treated as receipt continuity
- changelog prose treated as full control-plane provenance
- dashboard or UI summary treated as canonical receipt
- rehearsal receipt treated as live completion receipt
- downgrade or rollback recorded only as a new version string
- receipt that omits review posture, refusal posture, or compatibility context for a governed action
- receipt chain that silently rewrites history instead of linking it

## P. Stability And Evolution

This artifact is `provisional` but canonical.

It directly enables:

- `Υ-B2`
- the next checkpoint before any move toward `Φ-B4`
- later guarded reassessment of `Φ-B4` and `Φ-B5`
- future `Ζ` blocker reduction around operator transaction generalization and continuity maturity

Updates must remain:

- explicit
- auditable
- non-silent about changed receipt classes
- non-silent about changed continuity guarantees
- non-silent about changed rehearsal versus live evidence posture

Later work may refine storage, transport, dashboards, and operational procedures, but it may not silently:

- collapse logs into receipts
- collapse archive presence into provenance continuity
- collapse changelog prose into full history
- collapse rehearsal evidence into live completion evidence
