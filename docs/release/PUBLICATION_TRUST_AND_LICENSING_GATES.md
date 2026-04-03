Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: later checkpoints, future Ζ planning, later publication and trust operational doctrine
Replacement Target: later publication, trust, licensing, and live-ops operational doctrine may refine procedures and infrastructure without replacing the gate semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB1_Y0_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB1.md`, `docs/agents/AGENT_TASKS.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `docs/release/PRESET_AND_TOOLCHAIN_CONSOLIDATION.md`, `docs/release/VERSIONING_CONSTITUTION.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/ARTIFACT_NAMING_CHANGELOG_TARGET_POLICY.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/ARCHIVE_AND_MIRROR_CONSTITUTION.md`, `docs/release/SIGNING_POLICY.md`, `docs/release/ARCHIVE_AND_RETENTION_POLICY.md`, `docs/release/RELEASE_IDENTITY_CONSTITUTION.md`, `docs/release/RELEASE_INDEX_MODEL.md`, `docs/release/RELEASE_MANIFEST_MODEL.md`, `repo/release_policy.toml`, `release/update_resolver.py`, `release/release_manifest_engine.py`, `security/trust/trust_verifier.py`, `security/trust/license_capability.py`, `updates/stable.json`, `updates/beta.json`, `updates/pinned.json`, `updates/nightly.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/entitlement_registry.json`, `data/registries/release_channel_registry.json`

# Publication, Trust, And Licensing Gates

## A. Purpose And Scope

Publication, trust, and licensing gates exist to freeze one canonical interpretation of when Dominium may expose a release externally, when it may change trust-bearing acceptance posture, and when it may alter licensing-bearing rights or obligations posture.

It solves a specific problem: the repo already contains release identity, release index, archive and mirror doctrine, trust-policy registries, signing hooks, release-policy rules, MCP exposure law, task-catalog classifications, and safety posture rules, but those surfaces can still be misread as if a completed build, a mirrorable artifact, or an exposed control-plane tool automatically implied lawful publication or trust change. Later checkpoints and future `Ζ` planning need one constitutional answer to the question "what kind of action is this, what gate posture applies, and what never becomes lawful merely because the repo can technically express it?" before they can safely refine publication, trust, licensing, or live-ops operations.

This doctrine sits downstream of canonical governance, safety law, build graph lock, preset and toolchain consolidation, versioning constitution, release contract profile, artifact naming and changelog policy, release-index and resolution alignment, operator transaction doctrine, and archive and mirror doctrine. It freezes the gate semantics those upstream layers constrain.

This document governs:

- what publication means in Dominium
- what trust posture means in Dominium
- what licensing posture means in Dominium
- what a gate means for release-facing control-plane work
- which action classes remain informational, validation-bearing, review-bearing, privileged, or prohibited
- how archive, mirror, release identity, trust policy, signing, licensing, task catalog, and MCP exposure remain subordinate inputs rather than automatic approval surfaces

It does not govern:

- publication pipeline implementation
- trust-root rotation mechanics
- signing infrastructure implementation
- license enforcement engines
- release portal or store workflows
- mirror hosting operations
- live-ops operational choreography

Those are later prompts. This prompt freezes the gate law they must consume.

## B. Core Definition

Publication in Dominium is a governed control-plane act that changes external visibility, supported-distribution posture, or public commitment posture for a release-facing artifact set.

Trust posture in Dominium is the governed acceptance and authenticity posture attached to release-facing artifacts, trust policies, signer expectations, trust roots, or signing-bearing verification rules.

Licensing posture in Dominium is the governed rights, obligations, entitlement, or capability-posture declaration attached to distributable or trust-bearing release surfaces.

A gate in this context is an explicit constitutional decision layer that determines what review, privilege, validation, attribution, and traceability posture must be satisfied before a publication, trust, or licensing action may lawfully proceed.

These meanings differ from nearby surfaces:

- build completion says a realization step finished; it does not authorize publication
- archive presence says an artifact is retained; it does not authorize publication
- mirror availability says an artifact can be exposed or copied under policy; it does not authorize publication
- task catalog inclusion says a work family exists; it does not grant operator authority
- MCP exposure says a tool or surface may be reachable; it does not grant operator authority
- release identity existence says an artifact set is identified; it does not authorize external commitment

Publication, trust, and licensing therefore require explicit gates because they alter external commitment posture, acceptance posture, or rights posture rather than merely describing existing release state.

## C. Why Gates Are Necessary

Gates are necessary because:

- publication changes external visibility and support expectations
- trust posture changes affect authenticity and acceptance semantics for release-facing artifacts
- licensing posture changes affect rights, obligations, entitlement, or distribution posture
- these changes carry higher blast radius than ordinary metadata edits
- safety policy already classifies release, publication, signing, trust, and external-commitment work as strongly gated or privileged
- task or MCP exposure must never be confused with authority to cross a release-facing boundary

Without explicit gates, later work would drift toward:

- build succeeded, therefore publish
- archive exists, therefore released
- mirror exists, therefore approved for exposure
- task or MCP availability as shadow authority
- trust-root or signing changes treated like normal configuration edits
- licensing changes treated like changelog or label edits

## D. Action Classes

The constitutional action classes for this doctrine are:

### D1. Publication-Preparation Actions

Actions that assemble, validate, stage, or inspect release-facing artifacts without changing external visibility or commitment posture.

Examples include:

- release artifact verification
- manifest generation or inspection
- archive-only preparation
- mirror-readiness inspection

### D2. Publication-Approval Actions

Actions that approve or deny transition from private, internal, staged, archived, or mirror-capable state into governed public or externally committed release posture.

### D3. Channel And Visibility Actions

Actions that alter how a release becomes visible through channels, visibility classes, or policy-governed exposure lanes without redefining the underlying release identity.

### D4. Trust, Signer, And Trust-Root Posture Actions

Actions that change trust policy, signature requirements, signer acceptance posture, trust-root selection, or trust-bearing verification semantics.

### D5. Licensing And Rights-Posture Actions

Actions that declare, change, constrain, or broaden license capability posture, entitlement posture, or rights-bearing distribution semantics.

### D6. Mirror Exposure Actions

Actions that expose, suppress, filter, or scope mirrors without changing the upstream archival or identity truth those mirrors carry.

### D7. Archive-Only Actions

Actions that preserve or retain artifacts under archive law without authorizing publication or trust-policy change.

### D8. Review-Gated Metadata Actions

Actions that appear metadata-shaped but carry publication, trust, licensing, or external-commitment consequences and therefore remain review-aware rather than routine.

## E. Gate Classes

The main gate classes are:

### E1. Informational Or Non-Publishing

Read-only, inspection-only, or support-only actions that do not change publication, trust, or licensing posture.

### E2. Validation-Required

Actions that may proceed only after required structural, compatibility, or policy validation passes, but that still do not cross a privileged external-commitment boundary by themselves.

### E3. Review-Required

Actions that may affect release-facing posture and therefore require explicit human review or approval even when technically bounded and deterministic.

### E4. Privileged Or Operator-Only

Actions whose blast radius, authenticity posture, rights posture, public commitment posture, or external impact is high enough that they remain strongly gated, explicitly attributable, and outside routine automation.

### E5. Prohibited Or Out Of Scope

Actions that current doctrine, checkpoint posture, or safety law forbid for routine or autonomous execution, including trust-root mutation, publication automation by convenience, or licensing repurposing without explicit governing authority.

Gate passage is not implied by successful validation, available tooling, or existing artifact presence. Gate posture remains an explicit constitutional requirement.

## F. Relationship To Safety Policy

Safety policy remains upstream on action permission posture. This doctrine specializes that posture for publication, trust, and licensing work.

The controlling rules are:

- `allowed_bounded` does not normally cover publication, trust, or licensing boundary changes
- `allowed_with_required_validation` may apply to preparation or archive-only work but not to approval-bearing publication or trust changes by itself
- `allowed_with_explicit_human_review` may apply to bounded review-bearing metadata or visibility work
- `strongly_gated_privileged` is the default floor for publication change, trust-root or signing posture change, release-channel advancement, and other external-commitment shifts
- `prohibited_or_out_of_scope` remains available when the requested action exceeds current doctrine or safety posture

Task catalog and MCP exposure do not imply gate passage. Exposure and permission remain distinct.

## G. Relationship To Release Identity, Contract Profile, And Resolution

Publication does not create release identity. Release identity already says what the artifact set is.

Trust posture does not replace the release contract profile. The release contract profile remains the machine-readable compatibility envelope.

Licensing posture does not replace release compatibility law. Rights posture and compatibility posture remain distinct.

Publication, trust, and licensing actions must therefore remain downstream of:

- release identity
- release contract profile
- release index and resolution alignment
- target applicability and policy posture

These gates may decide whether a release is exposed, signed, trusted, or licensed for a context. They do not redefine what the release means or what it is compatible with.

## H. Relationship To Archive And Mirrors

Archive and mirror semantics remain upstream constraints on publication-bearing work.

The controlling rules are:

- archive presence is not publication approval
- archive retention is not public commitment
- mirrorability is not publication approval
- mirrors may be private, filtered, delayed, partial, cold-storage-oriented, or policy-constrained
- mirror exposure actions remain derived availability actions, not canon-creating actions

Publication law therefore consumes archive and mirror law rather than replacing it. An artifact may be archived without being published, mirrored without being publicly approved, or published through only selected mirrors under explicit policy.

## I. Relationship To Operator Transaction Doctrine

Publication, trust, and licensing actions are operator-transaction-bearing control-plane actions whenever they change visibility, trust acceptance, rights posture, or external commitment.

They must therefore remain:

- typed
- attributable
- reviewable
- traceable
- reconstructable in historical context

Later yanks, reversals, supersessions, trust-posture changes, or licensing remediations depend on exact records of what gate-bearing decision occurred and under what authority posture.

## J. Trust Posture Semantics

Trust posture changes are constitutional control-plane changes because they alter what authenticity evidence, signer identities, trust roots, or trust-policy envelopes are accepted for release-facing artifacts.

Trust posture includes, at a minimum:

- trust-policy selection or replacement
- signing requirement changes
- signer acceptance posture changes
- trust-root introduction, rotation, revocation, or removal posture
- signature-verification strictness changes

These are not casual metadata edits because they can alter external acceptance and authenticity semantics across release index, release manifest, or license-capability verification surfaces.

Trust posture changes therefore remain privileged, review-heavy, and auditable even when a deterministic tool can express them.

## K. Licensing Posture Semantics

Licensing posture changes are constitutional control-plane changes because they alter rights, obligations, entitlement-bearing posture, or capability-bearing distribution semantics.

Licensing posture includes, at a minimum:

- release-facing license posture declarations
- entitlement-bearing exposure posture
- license capability artifact posture
- rights or obligations changes attached to a release or distribution action

These are not casual metadata edits because they affect what the project claims users or operators may do, receive, accept, or redistribute.

Licensing posture changes therefore remain review-heavy, attributable, and auditable even when they are stored as machine-readable records.

## L. Publication Invalidity And Failure

Publication, trust, and licensing actions may be:

- invalid
- under-authorized
- incomplete
- policy-blocked
- trust-inconsistent
- licensing-inconsistent
- resolution-inconsistent
- archive-or-mirror-misclassified
- externally unsafe

Examples include:

- attempting publication without required gate posture
- treating a mirror-only action as public release approval
- treating archive retention as public release approval
- changing trust-root posture without privileged review
- changing licensing posture without explicit review and attribution
- attempting to publish artifacts whose release identity or contract profile posture is incomplete or inconsistent

Later tooling must therefore treat gate-bearing actions as potentially refused, blocked, or only partially admissible rather than assuming every publish-adjacent action is lawful.

## M. Verification And Auditability

Later systems should be able to verify:

- which action class applies
- which gate class applies
- whether the action was publication, archive-only, mirror-only, trust-bearing, or licensing-bearing
- what review or privilege posture was required
- what authority or actor class performed or approved it
- whether release identity and release contract profile references remained intact
- whether canonical versus derived distinctions were preserved
- whether the action is reconstructable from later operator and archival history

Auditability is mandatory because later checkpoint reassessment, future `Ζ` planning, and any later live-ops maturation depend on clear operational-boundary evidence rather than folklore.

## N. Canonical Vs Derived Distinctions

Publication, trust, and licensing gate decisions are canonical control-plane decisions when constitutionally defined and recorded.

Derived surfaces include:

- filenames
- host layout
- mirror availability
- UI or dashboard summaries
- support reports
- convenience status views
- MCP exposure lists

These derived surfaces may reflect gate outcomes, but they must not redefine gate truth.

The governing rule is simple: gate decisions may control publication, trust, or licensing posture, but projections of those decisions never outrank the canonical gate-bearing records and doctrine.

## O. Ownership And Anti-Reinvention Cautions

This doctrine carries forward the repo-wide cautions:

- ownership-sensitive roots remain binding
- canonical versus projected or generated distinctions remain binding
- old planning-numbering drift must not override the active checkpoint or active prompt chain
- publication, trust, and licensing gate law must be extracted from repo doctrine and existing release-control evidence rather than invented as a greenfield workflow

Additional caution is required because `docs/release/**`, `release/**`, `updates/**`, `repo/**`, and `security/**` are release-control or trust-bearing roots. Convenience, exposure, or implementation locality does not change their governance posture.

## P. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- build succeeded, therefore publish
- archive exists, therefore released
- mirror exists, therefore approved for publication
- MCP exposure implies publish authority
- task catalog inclusion implies publish authority
- trust-root or signing posture changed like normal metadata
- licensing posture changed like a changelog edit
- release identity existence treated as public-release approval
- derived dashboard, host layout, or mirror listing treated as gate truth
- publication, trust, and licensing collapsed into one generic review flag

## Q. Stability And Evolution

This doctrine is `provisional` but canonical. It freezes the gate semantics later checkpoints and future `Ζ` planning must consume.

Later work may refine:

- publication procedures
- trust-root operational flows
- signing infrastructure
- licensing enforcement or entitlement machinery
- mirror-promotion procedures
- live-ops operational boundaries

Later work may not:

- treat archive or mirror posture as publication approval
- treat MCP or task exposure as authority
- downgrade trust or licensing changes into ordinary metadata edits
- silently repurpose gate classes or permission posture

Under the active execution chain, this doctrine gives later checkpoints a stable basis for reassessing risky `Φ-B` tail work, future `Ζ` blocker reduction, and any later operationalization of publication, trust, licensing, or live-ops boundaries.
