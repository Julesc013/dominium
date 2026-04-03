Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-8, later checkpoints, future Ζ continuity and disaster-recovery planning
Replacement Target: later publication, trust, archive hosting, and disaster-recovery doctrine may refine operational procedures without replacing archive and mirror semantics
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB1_Y0_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB1.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `docs/release/PRESET_AND_TOOLCHAIN_CONSOLIDATION.md`, `docs/release/VERSIONING_CONSTITUTION.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/ARTIFACT_NAMING_CHANGELOG_TARGET_POLICY.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/ARCHIVE_AND_RETENTION_POLICY.md`, `docs/release/OFFLINE_ARCHIVE_MODEL_v0_0_0.md`, `docs/release/DIST_FINAL_PLAN_v0_0_0_mock.md`, `docs/release/RELEASE_INDEX_MODEL.md`, `docs/release/RELEASE_MANIFEST_MODEL.md`, `repo/release_policy.toml`, `release/archive_policy.py`, `release/update_resolver.py`, `updates/stable.json`, `updates/pinned.json`, `updates/nightly.json`, `data/registries/archive_policy_registry.json`, `data/registries/retention_policy_registry.json`, `data/registries/release_channel_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/install_profile_registry.json`, `data/registries/target_matrix_registry.json`, `data/release/dist_final_expected_artifacts.json`, `data/registries/derived_artifacts.json`

# Archive And Mirror Constitution

## A. Purpose And Scope

Archive and mirror doctrine exists to freeze one canonical interpretation of how Dominium preserves exact release history and how it exposes retained artifacts through derived availability surfaces.

It solves a specific problem: the repo already contains immutable-release retention rules, release-index history snapshots, deterministic offline archive bundles, archive records, mirror requirements, and operator-transaction continuity expectations, but those surfaces can still be misread as if mirrors were just loose copies or as if archives were incidental leftovers in storage. Later `Υ` prompts, future checkpoints, and eventual `Ζ` continuity work need one constitutional answer to the question "what must be preserved exactly, what may be mirrored selectively, and what never becomes truth by being stored somewhere?" before they can safely define publication and trust gating, disaster recovery, and long-horizon continuity operations.

This constitution sits downstream of build graph lock, preset/toolchain consolidation, versioning constitution, release contract profile, release-index and resolution alignment, operator transaction doctrine, governance mirror law, and safety policy. It freezes how release-facing artifacts are retained or exposed after those upstream layers define what the artifacts mean.

This document governs:

- what an archive is in Dominium
- what a mirror is in Dominium
- which artifact classes carry archival duty, mirror duty, or neither
- how archive and mirror semantics remain subordinate to release identity, release contract profile, release index and resolution law, and operator transaction doctrine
- how historical recoverability, offline survivability, and derived-surface caution must be preserved

It does not govern:

- storage backends
- CDN or hosting implementation
- publication automation
- trust-root operations
- operational release hosting layout
- deletion or migration procedures in full

Those are later prompts. This prompt freezes the archival and mirroring semantics they must consume.

## B. Core Definition

An archive in Dominium is a governed retention surface that preserves exact historical release continuity, reconstructable identity, and required recovery evidence for artifacts that carry archival duty.

A mirror in Dominium is a governed derived availability or distribution surface that exposes archive-carried or release-carried artifacts under explicit policy without becoming the source of truth for those artifacts.

They differ:

- an archive is about exact historical preservation and recoverability
- a mirror is about policy-governed availability, distribution, or discoverability

They also differ from nearby surfaces:

- release identity says what a release is
- release index says what release records and selection inputs exist
- build outputs are realization surfaces and may be pre-publication or local
- local caches are convenience surfaces, not archival canon
- checkpoints are planning or support continuity artifacts, not release truth
- generated bundles are carriers and projections, not semantic or release authority
- publication channels classify exposure posture, but they are not archives and not mirrors by themselves

Archive and mirror require a distinct constitutional layer because Dominium needs both:

- exact retained history
- governed derived availability

without letting storage layout, bundle names, or current hosting state redefine release truth.

## C. Why Archive And Mirror Doctrine Is Necessary

Archive and mirror doctrine is necessary because:

- exact historical continuity requires explicit preservation semantics
- availability and discoverability require explicit mirror semantics
- downgrade, rollback, supersession, yank, and disaster recovery later depend on exact retained history
- offline survivability is a constitutional continuity concern, not a packaging afterthought
- mirrors and archives must not become informal leftovers that are reinterpreted differently by different tools or operators

Without this doctrine, later work would drift toward:

- mirrors as hidden canon
- archives as whatever storage happens to retain
- yanked or superseded artifacts disappearing from exact recovery
- bundle paths and hosting layout becoming identity truth
- checkpoint or support bundles being mistaken for release canon

## D. Artifact Classes And Archival Duties

The constitutional artifact classes and their default archival or mirroring posture are:

These duties are downstream of build graph lock and preset/toolchain consolidation. Archive and mirror law preserve or expose realized artifacts and histories; it does not redefine target topology, preset lanes, or product realization semantics.

### D1. Canonical Release Identity Artifacts

This class includes release identity anchors and canonical machine-readable release-control artifacts such as release identity records and exact release references.

Archival duty:

- exact archival retention is required for published or governed release history

Mirror duty:

- mirrors may expose them directly or by reference where policy requires, but mirrors remain derived carriers

### D2. Release Manifest And Release-Index Artifacts

This class includes release manifests, current release indices, and retained historical release-index snapshots.

Archival duty:

- exact archival retention is required
- historical release-index snapshots are append-only and no-overwrite

Mirror duty:

- current and policy-allowed historical views may be mirrored
- mirror visibility may be partial or channel-filtered

### D3. Contract And Compatibility Artifacts

This class includes release contract profiles, referenced semantic contract pins, governance profile anchors, trust-policy references, and other compatibility-envelope surfaces needed to reconstruct release admissibility.

Archival duty:

- archival retention is required whenever those artifacts are part of governed release interpretation

Mirror duty:

- mirrors may expose them alongside release records or through bounded references
- mirrors do not redefine their machine-readable meaning

### D4. Distributable Release Payload Artifacts

This class includes the shipped bundle root, content-addressed payloads, profiles, bundles, packs, locks, and other distributable release artifacts.

Archival duty:

- published or governed payloads must remain archivally recoverable under explicit policy

Mirror duty:

- mirrors may expose primary, secondary, filtered, or cold-storage copies according to policy
- mirror absence does not erase archival existence

### D5. Historical Control-Plane Records

This class includes changelog layers, operator transaction records where later doctrine defines them, yank or deprecation or supersession records, and other history-bearing release-control metadata.

Archival duty:

- historical continuity retention is required where the record affects reconstruction, audit, downgrade, rollback, or later review

Mirror duty:

- mirrors may expose current or filtered views
- not every mirror must expose full history

### D6. Continuity-Support And Offline-Reconstruction Artifacts

This class includes offline archive bundles, archive records, retained release-index history trees, and explicitly frozen baselines or verification fixtures needed for offline re-verification or extinction-prevention workflows.

Archival duty:

- archival retention is required when the artifact is part of the explicit recovery or continuity model

Mirror duty:

- mirrors may include cold-storage seeds or selected reconstruction packages
- these surfaces may be archive-required but only selectively mirrored

### D7. Checkpoint And Support Bundles

This class includes planning checkpoints, support zips, temporary continuity bundles, and other support artifacts.

Archival duty:

- these may be archived under separate support or planning continuity rules

Mirror duty:

- they are not mirrored as release canon by default
- they must not be mistaken for release identity or release continuity truth

### D8. Ephemeral, Local, And Staging Outputs

This class includes temporary caches, scratch outputs, local build products, intermediate staging trees, and other convenience artifacts.

Archival duty:

- none by default

Mirror duty:

- none by default

These surfaces remain intentionally non-archival and non-mirrorable unless a later prompt explicitly promotes a specific artifact class through governed review.

## E. Archive Semantics

For an artifact to be archived in Dominium means:

- it is retained under explicit continuity duty
- its exact identity or governed projection is reconstructable
- its retention posture is explicit
- its historical existence remains auditable
- later recovery or audit consumers can reconnect it to release identity, release index, release contract profile, or operator history as required

Archive semantics may include immutability or an immutability class where relevant. For published or governed release history, the important rule is no silent overwrite of archived historical meaning.

Archive does not mean:

- preferred
- current
- latest
- mirrored everywhere
- automatically admissible for selection

An archived release may be deprecated, yanked, superseded, or retired while remaining historically preserved.

## F. Mirror Semantics

For an artifact to be mirrored in Dominium means:

- it is exposed through a derived availability surface
- the exposure is governed by explicit policy
- the surface may be partial, delayed, filtered, or lane-specific
- the mirrored copy remains subordinate to canonical truth

Mirrors exist to support:

- availability
- distribution
- discoverability
- cold-storage seeding
- policy-filtered access

Mirror exposure later remains subordinate to safety policy and to later publication or trust review posture. Being mirrorable does not by itself authorize unrestricted distribution or automated promotion.

Mirrors do not mean:

- canonical authorship
- exact completeness in every location
- guaranteed permanence in every mirror
- release existence by themselves

Release mirrors in this constitution are release-control derived surfaces. They are distinct from governance instruction mirrors, but they obey the same constitutional principle: derived mirrors never outrank canonical artifacts.

## G. Relationship To Release Identity And Contract Profile

Release identity remains canonical.
Release contract profile remains the machine-readable compatibility envelope.

Archives and mirrors may carry or expose these artifacts, but they do not redefine them.

The governing consequences are:

- archival retention must preserve their machine-readable role
- mirrors may project them directly or indirectly
- storage location, filename, bundle path, or host layout must not replace their structured meaning
- exact historical recovery must remain able to reconnect archived payloads to identity and contract-profile truth

## H. Relationship To Release Index And Resolution

Archives preserve exact historical entries and resolvable history.

Mirrors may expose:

- current index views
- history subsets
- policy-filtered channel views
- derived distribution-facing projections

Resolution later consumes archival and mirrored surfaces only under explicit law:

- canonical release-index semantics remain upstream
- mirror visibility is not the same as release existence
- absence from one mirror does not imply historical nonexistence
- archive presence does not imply current preference or latest status

The key rule is that resolution and recovery later must read mirrored or archived surfaces as carriers of governed release truth, not as self-authoring truth owners.

## I. Relationship To Operator Transaction And Downgrade Doctrine

Downgrade, rollback, yank, deprecation, and supersession later depend on historical recoverability.

Archive law must therefore preserve:

- the artifacts needed to reconstruct prior release state
- the historical records needed to explain why visibility or eligibility changed
- exact retained identity for yanked or superseded artifacts

Mirror law must therefore avoid:

- erasing or confusing transactional semantics
- treating a hidden or filtered mirror view as if the historical record disappeared

Yanked artifacts may become non-preferred or non-default in mirrors without ceasing to exist archivally.
Superseded releases may yield mirror preference to successors without losing exact historical recoverability.

## J. Relationship To Provenance, Auditability, And Runtime Continuity

Archive continuity and mirror policy must support provenance and auditability.

At minimum, later consumers must be able to reconnect archived or mirrored artifacts to:

- release identity
- release contract profile
- release-index state
- operator transaction history where relevant
- deterministic hashes and content-addressed payload identity

Where archived continuity packages carry runtime-relevant baselines, snapshots, replay fixtures, or other continuity-support artifacts, archive carriage does not redefine runtime doctrine. Replay, snapshot, lifecycle, and isolation law remain upstream of how those artifacts are interpreted or restored.

Archive and mirror doctrine therefore supports runtime continuity without turning storage policy into runtime semantics.

## K. Relationship To Checkpoint And Support Bundles

Checkpoint bundles are support artifacts, not release canon.

They may be archived for planning or continuity support under separate rules, but:

- their names do not define release identity
- their presence does not define release history
- their structure does not replace release manifest, release index, or release contract profile law

Support-bundle retention and release retention must remain distinct, even when both are valuable to later review or recovery work.

## L. Relationship To Canonical Vs Derived Distinctions

Canonical release and control-plane truth remains upstream of archive and mirror surfaces.

The governing consequences are:

- archive copies preserve artifacts; they do not create canon
- mirrored or generated summaries remain derived
- filenames and storage layout remain projections
- bundle roots, host URLs, and mirror identifiers are carriers, not semantic or release authority

This caution is especially important where the repo already uses generated bundles, release trees, history directories, and support outputs. Those layouts are evidence of continuity practice, not self-authoring doctrine.

## M. Availability, Retention, And Survivability

Archive duty and mirror duty are not the same thing.

Archive duty answers:

- what must remain recoverable
- what history must remain exact
- what later audits or recovery operations must be able to reconstruct

Mirror duty answers:

- what should remain available or discoverable through derived surfaces
- what may be replicated across primary, secondary, or cold-storage carriers
- what may be filtered by channel, policy, or operational posture

Retention and survivability classes therefore remain explicit:

- archival exact-history retention
- policy-retained active distribution availability
- cold-storage or offline survivability
- support-artifact retention distinct from release canon
- ephemeral non-retained outputs

Offline survivability is a constitutional concern. Not every mirror must preserve full retention, but explicit archive obligations must remain sufficient for exact historical recovery, audit, and later disaster-resilience work.

## N. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- mirror as source of truth
- archive as equivalent to preferred or latest
- yanked artifact silently deleted from archival continuity
- superseded artifact silently removed from exact recovery
- bundle path or hosting layout treated as identity truth
- cache or tmp outputs treated as archive canon
- checkpoint bundles treated as release identity
- archive and mirror collapsed into one vague storage concept

## O. Stability And Evolution

This artifact is `provisional` but canonical for the current `Υ-A` execution band.

Later prompts may refine:

- publication and trust gating
- mirror promotion procedures
- archive-hosting and transport operations
- continuity-sensitive checkpoint reassessment
- disaster-recovery and future `Ζ` continuity planning

Those later prompts must extend this constitution rather than replacing it silently.

Updates must remain explicit, auditable, and non-silent. In particular, later work must not:

- let a mirror become shadow canon
- reinterpret archive presence as release preference
- erase yanked or superseded history
- let support bundles redefine release truth

Under the active execution chain, this constitution enables `Υ-8` next and gives later checkpoints a stable archival and mirroring substrate for reassessing the remaining risky runtime and continuity work.
