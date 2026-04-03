Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-7, Υ-8, later checkpoints, future Ζ continuity reassessment
Replacement Target: later archive, publication, trust, live-ops, and continuity doctrine may refine operator procedures and control-plane machinery without replacing the transaction and downgrade semantics
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB1_Y0_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB1.md`, `docs/agents/AGENT_TASKS.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `docs/release/PRESET_AND_TOOLCHAIN_CONSOLIDATION.md`, `docs/release/VERSIONING_CONSTITUTION.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/ARTIFACT_NAMING_CHANGELOG_TARGET_POLICY.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/RELEASE_IDENTITY_CONSTITUTION.md`, `docs/release/RELEASE_INDEX_MODEL.md`, `docs/release/RELEASE_INDEX_RESOLUTION_POLICY.md`, `docs/release/RELEASE_MANIFEST_MODEL.md`, `docs/release/UPDATE_SIM_MODEL_v0_0_0.md`, `repo/release_policy.toml`, `release/update_resolver.py`, `updates/stable.json`, `updates/pinned.json`, `updates/nightly.json`, `data/registries/release_channel_registry.json`, `data/registries/install_profile_registry.json`, `data/registries/target_matrix_registry.json`, `data/registries/component_graph_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/refusal_code_registry.json`, `tools/controlx/README.md`

# Operator Transaction And Downgrade Doctrine

## A. Purpose And Scope

Operator transaction and downgrade doctrine exists to freeze one canonical interpretation of release-control actions that affect availability, selection, rollback, downgrade, and recovery posture in Dominium.

It solves a specific problem: the repo already contains release-index semantics, deterministic resolution policy, trust refusal, install transaction log handling, yanked-candidate rules, and control-plane tooling surfaces, but those surfaces can still be misread as if operator action were an unstructured manual override or as if downgrade and rollback were just implementation tricks. Later `Υ` prompts, future risky `Φ-B` reassessment, and eventual `Ζ` continuity work need one constitutional answer to the question "what kind of control-plane transaction is this, what does it lawfully mean, and what history must it preserve?" before they can safely refine archive, publication, trust, or recovery machinery.

This document governs:

- what an operator transaction is in Dominium
- how downgrade, rollback, yank, deprecation, supersession, partial reversion, and recovery differ
- which operator actions require explicit transactional framing
- what transactional elements and review posture are required
- how operator transaction semantics stay subordinate to governance, safety, release-contract, and release-resolution law

It does not govern:

- deployment-engine implementation
- updater or rollback automation
- live-ops consoles
- publication execution
- trust-root rotation
- archive transport mechanics

Those are later `Υ` and future-series prompts. This prompt freezes the constitutional control-plane model they must consume.

## B. Core Definition

An operator transaction is a governed, typed, attributable control-plane action that attempts to change release-facing selection, availability, recovery posture, or historical interpretation under explicit authority, explicit preconditions, explicit review posture, and explicit traceability expectations.

Downgrade means a governed operator decision to move from a currently selected release or component set to an older but still lawful target under explicit compatibility, trust, target, and policy checks.

Rollback means transactionally restoring a previously recorded managed state or release selection by using explicit transaction history, preserved reversibility anchors, and deterministic restoration rules.

Yank means changing release-selection posture so that a release or component candidate is no longer normally eligible for selection under default policy, while preserving its historical record and identity.

Supersession means declaring that another release or candidate is the preferred successor for future selection or operational guidance without erasing the superseded record.

Deprecation means warning-bearing reduced preference or planned retirement posture that preserves visibility while signaling that future use should narrow or cease.

These are not interchangeable:

- downgrade is a deliberate controlled move to an older target
- rollback is a recovery transaction against recorded prior state
- yank is a visibility and eligibility change, not historical erasure
- deprecation is a warning-bearing transition posture, not immediate exclusion
- supersession is preferred-successor declaration, not automatic deletion or rollback

They require explicit doctrine because local scripts, UI flows, updater affordances, or operator habits must not define release-control semantics by convenience.

## C. Why Transaction Doctrine Is Necessary

Transaction doctrine is necessary because:

- release-control actions can change availability, selection, continuity, and recoverability without changing semantic law directly
- those actions still carry high governance, trust, auditability, and irreversibility risk
- deterministic rollback and recovery depend on preserved transaction semantics rather than vague "undo" expectations
- operator convenience must not override release contract profile, release index, or safety policy
- later archive, publication, and live-ops doctrine needs one stable transactional vocabulary instead of scattered ad hoc behavior

Without this doctrine, later work would drift toward treating manual overrides as shadow authority, treating yanks as deletion, or treating downgrade as version-string reversal without compatibility and traceability law.

## D. Operator Transaction Classes

The constitutional operator transaction classes are:

### D1. Selection-Affecting Transactions

Transactions that choose, pin, or redirect which compatible release or component set should be selected under explicit policy.

### D2. Availability-Affecting Transactions

Transactions that change visibility, channel exposure, or eligibility posture for release records without redefining the underlying identity.

### D3. Downgrade And Rollback Transactions

Transactions that move backward in selected release state or restore earlier recorded state under explicit reversibility and compatibility conditions.

### D4. Yank, Deprecation, And Supersession Transactions

Transactions that change future selection posture or guidance while preserving history and traceability.

### D5. Recovery And Remediation Transactions

Transactions that address failed, partial, unsafe, or incompatible control-plane state through explicit recovery intent and bounded corrective scope.

### D6. Metadata-Only Control-Plane Transactions

Transactions that alter governed release-control metadata, review posture, or recorded operator annotations without changing the selected release payload directly.

### D7. Review-Gated Or Publication-Adjacent Transactions

Transactions whose blast radius, public-policy meaning, trust posture, or archive effect is high enough that they remain strongly review-aware and later-consumer constrained.

## E. Transaction Elements

A lawful operator transaction must carry enough information to be attributable, reviewable, and reconstructable.

At minimum, the core transaction elements are:

- actor or authority class
- transaction id or equivalent exact identity anchor
- target release, artifact, component, or scope reference
- transaction intent and class
- explicit preconditions
- review or approval posture
- release-contract-profile and resolution context
- resulting state, visibility, or eligibility changes
- reversibility or non-reversibility posture
- traceability and audit anchors
- refusal or warning outcomes where applicable

The governing consequences are:

- operator action must be typed, not freeform
- scope must be explicit, not inferred from UI context or filename shorthand
- transaction intent must be stable enough to distinguish selection, downgrade, rollback, yank, deprecation, supersession, recovery, and metadata-only changes
- reversibility posture must be explicit because not all transactions are reversible
- traceability must persist even when a transaction reduces availability or prefers a successor

## F. Relationship To Release Contract Profile And Resolution

Operator actions do not replace compatibility law.

Release contract profile remains the upstream machine-readable compatibility envelope.
Release index and resolution alignment remain the upstream admission and selection grammar.

The governing consequences are:

- operator actions may constrain, choose among, or annotate compatible candidates
- operator actions may trigger controlled refusal, warning, downgrade, yank, or rollback posture changes
- operator actions must not redefine semantic contract binding, target compatibility, or governance and trust posture by convenience
- downgrade and rollback decisions must remain compatible with release-index and resolution semantics

An operator may select among lawful candidates under explicit review posture, but operator choice cannot make an incompatible release compatible.

## G. Relationship To Versioning And Identity

Downgrade is not "pick the smaller version number."

Rollback is not "pick the previous build."

Suite version, product version, build identity, release identity, release contract profile, target family, and exact target remain distinct inputs.

The governing consequences are:

- a lower suite or product version does not by itself define a lawful downgrade target
- a prior build id does not by itself define a lawful rollback target
- build identity remains provenance and exact-artifact identity, not semantic compatibility or downgrade truth
- transaction reasoning must consider release profile, target applicability, trust posture, and prior transaction state rather than version arithmetic alone

Layered version and identity truth remains upstream of operator semantics.

## H. Relationship To Deprecation, Yank, And Supersession

Deprecation, yank, and supersession must remain distinct.

Deprecation means:

- visible but warning-bearing reduced-preference posture
- continuing historical and often operational visibility
- future narrowing or removal expectations may be announced explicitly

Yank means:

- default selection exclusion or stronger warning or refusal posture
- preservation of identity and historical traceability
- no silent deletion from canonical history

Supersession means:

- a preferred successor or replacement relationship is declared explicitly
- future operator and resolver reasoning may prefer the successor
- the superseded record remains part of history and may remain selectable under bounded policy

These distinctions matter because visibility, eligibility, preference, and history are not the same thing. A release may be deprecated without being yanked, yanked without being deleted, or superseded without being invalid for all recovery use.

## I. Relationship To Safety Policy

Safety policy remains upstream for permission posture.

Operator transaction doctrine must align with:

- `allowed_bounded`
- `allowed_with_required_validation`
- `allowed_with_explicit_human_review`
- `strongly_gated_privileged`
- `prohibited_or_out_of_scope`

This doctrine does not create permission where safety policy does not allow it.

The governing consequences are:

- transaction typing does not authorize execution
- privileged or review-gated release-control actions remain review-gated even if tooling can technically express them
- release, publication, trust, archive, or high-irreversibility transactions stay constrained by safety action classes and safety dimensions
- auditability and traceability are mandatory, not optional convenience features

## J. Relationship To MCP And Task Catalog

Task catalog inclusion and MCP exposure do not imply operator transaction authority.

The `release_distribution_control_plane` task family remains review-heavy.
MCP exposure remains a bounded interface layer, not a permission layer.

The governing consequences are:

- operator transaction surfaces remain special, review-aware control-plane surfaces
- task catalog entries may describe operator-facing work without authorizing autonomous mutation
- MCP endpoints, wrapper commands, dashboards, or consoles may expose request surfaces later, but they do not define transaction legality
- local updater behavior and control-plane wrappers remain implementation evidence rather than constitutional authority

Exposure and authority must stay separate.

## K. Relationship To Provenance, Archive, And Continuity

Operator transactions must remain traceable because later archive, mirror, downgrade, rollback, and live-ops continuity work depends on exact historical reconstruction.

The governing consequences are:

- silent erasure of release history is forbidden
- yanks, supersession, deprecation, downgrade, and rollback must preserve identity continuity
- transaction records must be auditable enough to reconnect action intent, target scope, review posture, and resulting state
- archive and mirror doctrine later must consume operator transaction semantics rather than invent a second historical record model

History-preserving control-plane law is necessary because later continuity work cannot safely reason about reversibility or failure if operator actions vanish into dashboards, filenames, or overwritten status rows.

## L. Relationship To Risky Φ-B Tail And Ζ

Stronger operator transaction doctrine is a prerequisite for later risky runtime and continuity work because:

- multi-version coexistence needs explicit transactional meaning for pinning, downgrade, and fallback decisions
- hotswap and live recovery review later needs explicit rollback and partial-reversion semantics
- distributed authority and continuity planning later needs review-aware control-plane traceability
- future `Ζ` work needs a stable model for rollback, yank, downgrade, and recovery history instead of local operator folklore

This doctrine does not unblock the risky `Φ-B` tail by itself, but it reduces a concrete blocker by freezing the control-plane vocabulary those later checkpoints require.

## M. Invalidity And Failure

Operator transactions may be:

- invalid
- unauthorized
- unsafe
- blocked by review posture
- incompatible with release profile law
- incompatible with target or trust posture
- non-reversible
- incomplete
- partially applied
- stale relative to current release state

These invalidity and failure classes must remain explicit.

Later tooling must not assume all transactions are equally lawful or equally reversible. In particular:

- a failed recovery is not the same as a refused transaction
- a non-reversible transaction is not the same as an invalid one
- a stale transaction request is not the same as a canonical history rewrite

## N. Verification And Auditability

Later systems should be able to verify:

- transaction class and intent
- actor or authority posture
- review or approval posture
- release-contract-profile and resolution compatibility context
- target scope and exact identity anchors
- reversibility or non-reversibility class
- traceability records and retained evidence
- relation to yanked, deprecated, superseded, or rolled-back state

Verification must remain deterministic and reviewable.
Operator convenience must not outrun the repo's ability to explain what happened, why it was allowed, and which history it affected.

## O. Canonical Vs Derived Distinctions

Canonical operator-transaction surfaces include:

- this doctrine
- paired machine-readable operator-transaction registries
- governed transaction records where later doctrine explicitly defines them
- release-index and release-profile references with intact provenance

Derived surfaces include:

- UI summaries
- dashboard tiles
- filenames
- changelog prose
- operator convenience reports
- local updater text output

Derived views may summarize transactions, but they must not redefine transaction truth, review posture, or history.

## P. Ownership And Anti-Reinvention Cautions

The existing cautions remain binding:

- ownership-sensitive roots remain review-aware
- canonical versus projected or generated distinctions remain binding
- thin convenience roots and dashboards are not automatically canonical
- stale planning-number drift does not override the active prompt chain and current doctrine
- operator law must be extracted from doctrine and repo reality rather than invented greenfield

This is especially important in control-plane work because local wrappers, caches, support bundles, or generated feeds can appear more convenient than the actual canonical release and governance surfaces.

## Q. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- downgrade equals smaller version
- rollback equals previous build by convenience
- yank equals delete from history
- supersession equals silent removal of the prior record
- tool exposure equals operator authority
- local updater behavior defines doctrine
- operator action silently bypasses release contract profile or safety policy
- partial recovery silently rewrites history without transaction traceability
- convenience dashboards or filenames treated as canonical control-plane truth

## R. Stability And Evolution

This artifact is `provisional` but canonical for the current `Υ-A` execution band.

Later prompts may refine:

- archive and mirror doctrine
- publication and trust gating
- operator-facing control-plane machinery
- downgrade, yank, and supersession operational procedures
- continuity-sensitive checkpoint reassessment for the risky `Φ-B` tail and future `Ζ`

Those later prompts must extend this doctrine rather than replacing it silently.

Updates must remain explicit, auditable, and non-silent. In particular, later work must not:

- flatten all operator actions into one generic manual override class
- repurpose version strings into transaction meaning
- erase historical records when availability posture changes
- let exposed tooling become shadow authority

Under the active execution chain, this doctrine enables `Υ-7` next and gives later checkpoints a stable control-plane and rollback vocabulary for reassessing the remaining risky runtime and continuity work.
