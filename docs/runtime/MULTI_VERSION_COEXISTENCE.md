Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Φ-B4, Φ-B5, selected Υ-B, later checkpoints, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB1_Y0_REVIEW.md`, `docs/planning/CHECKPOINT_C_YA_SAFE_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_YA.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/release/VERSIONING_CONSTITUTION.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/ARCHIVE_AND_MIRROR_CONSTITUTION.md`, `docs/release/PUBLICATION_TRUST_AND_LICENSING_GATES.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `docs/blueprint/MANUAL_REVIEW_GATES.md`, `runtime/process_spawn.py`, `engine/modules/replay/d_replay.c`, `engine/modules/replay/d_replay.h`, `server/app/main_server.c`, `release/update_resolver.py`, `release/component_graph_resolver.py`, `release/release_manifest_engine.py`, `security/trust/trust_verifier.py`, `repo/release_policy.toml`, `updates/README.md`, `data/registries/component_graph_registry.json`, `data/registries/release_channel_registry.json`, `data/registries/target_matrix_registry.json`, `data/registries/trust_root_registry.json`

# Dominium Multi-Version Coexistence Doctrine

## A. Purpose And Scope

This doctrine exists to freeze the canonical meaning of multi-version coexistence after the post-`Υ-A` checkpoint reopened `Φ-B3` as `ready_with_cautions`.

It solves a specific problem: the repository already has real versioned release-control substrate, replay and snapshot substrate, lifecycle law, isolation law, rollback selection, trust verification, component-graph resolution, and target-matrix routing. Without one explicit coexistence doctrine, later work could wrongly treat:

- side-by-side files as lawful coexistence
- raw version comparisons as compatibility proof
- operator rollback or archive retention as runtime coexistence
- one local implementation trick as architectural canon

This document governs:

- what multi-version coexistence means in Dominium
- what classes of runtime and release-control subjects may coexist
- what classes remain prohibited or strongly review-gated
- how coexistence stays subordinate to semantic law, ownership review, replay, snapshot, lifecycle, isolation, and release-control doctrine
- what later `Φ-B4`, `Φ-B5`, selected `Υ-B`, and later checkpoints must consume rather than reinvent

It does not implement:

- side-by-side runtime loading
- hotswap or restartless replacement
- distributed coexistence protocols
- migration engines
- live-ops cutover systems
- release publication machinery

Checkpoint relation:

- the active checkpoint state is `post-Υ-A / pre-risky-Φ-B-tail-and-or-Υ-B`
- `C-ΥA_SAFE_REVIEW` judged this prompt `ready_with_cautions`
- `Φ-B4` remains `dangerous`
- `Φ-B5` remains `premature`
- older planning numbering drift remains evidence only and does not override the active checkpoint chain

Repo-grounded extension surfaces already exist and must be treated as evidence rather than as automatic canon:

- `runtime/process_spawn.py`
- `engine/modules/replay/d_replay.c`
- `engine/modules/replay/d_replay.h`
- `server/app/main_server.c`
- `release/update_resolver.py`
- `release/component_graph_resolver.py`
- `release/release_manifest_engine.py`
- `security/trust/trust_verifier.py`
- `repo/release_policy.toml`
- `updates/README.md`

## B. Core Definition

In Dominium, multi-version coexistence is the declared, bounded, law-governed simultaneous presence, availability, interpretability, or resolvability of more than one version-distinguished runtime or release-control subject within one governed continuity envelope without allowing version multiplicity to redefine semantic truth, ownership, compatibility, lifecycle legality, or control-plane authority.

Coexistence is a distinct layer because it answers a question the nearby doctrines do not answer alone:

- state law explains what may be externalized or reconstructed
- replay law explains how lawful history is reconstructed
- snapshot law explains bounded continuity captures
- lifecycle law explains posture over time
- isolation law explains containment boundaries
- release doctrine explains version, compatibility, identity, selection, downgrade, archive, and gate semantics
- coexistence law explains when more than one version-distinguished subject may be present or interpreted together without semantic drift

Coexistence is not:

- `migration`
  - migration changes state, schema, or representation posture over time; coexistence may exist before, during, or without migration
- `rollback`
  - rollback is a governed restoration or selection transaction, not the general law of simultaneous version presence
- `hotswap`
  - hotswap is a later cutover and replacement problem; coexistence may be a prerequisite for it but is not the same thing
- `archive retention`
  - archives preserve historical artifacts; that does not by itself authorize runtime or live control-plane coexistence
- `mirror availability`
  - mirrors expose or distribute artifacts; they do not define coexistence truth
- `simple side-by-side storage`
  - two files in one directory are not automatically two lawfully coexisting versions

## C. Why Coexistence Law Is Necessary

Coexistence law is necessary because Dominium already has several real signs of version multiplicity:

- `server/app/main_server.c` already exposes compatibility reports and replay-oriented inspection posture
- `release/update_resolver.py` already resolves among multiple component candidates and yanked states
- `release/component_graph_resolver.py` already models versioned component descriptors with trust and contract requirements
- `release/release_manifest_engine.py` already projects versioned artifact identities and manifest state
- `security/trust/trust_verifier.py` already distinguishes trust posture from artifact identity
- `updates/README.md` already treats feeds as generated control-plane projections rather than hand-edited truth

Without explicit coexistence law, later work would drift toward forbidden shortcuts:

- incompatible semantic meanings present in the same continuity horizon by convenience
- release-control coexistence based on filenames, channels, or build ids instead of explicit compatibility envelopes
- lifecycle or isolation gaps being disguised as harmless coexistence
- hotswap-by-stealth hidden inside "temporary coexistence"
- distributed split authority hidden inside "both versions are live for now"

Coexistence law therefore exists to make side-by-side presence and interpretation explicit, bounded, and reviewable rather than folkloric.

## D. Coexistence Subject Classes

The coexistence subject taxonomy is constitutional and intentionally general.

### D1. Runtime Component Realizations

Bounded component realizations that may be version-distinguished while still remaining subordinate to component, state, lifecycle, and isolation law.

### D2. Runtime Service Realizations

Service realizations whose mediation, routing, compatibility handling, or replay-support posture may be version-distinguished without becoming semantic owners.

### D3. Kernel-Adjacent Runtime Structures

Execution-hosting or continuity-support structures whose implementation version may differ while the semantic and lifecycle floors remain explicit.

### D4. Release And Control-Plane Artifacts

Release identities, manifests, component graphs, install plans, release indices, archive records, rollback candidates, and other release-control records that may coexist as governed artifacts.

### D5. Compatibility Envelopes

Release contract profiles, semantic contract pins, protocol ranges, schema ranges, format ranges, target descriptors, and trust-policy references that may coexist as explicit machine-readable declarations.

### D6. Operator-Visible Release States

Selected, pinned, deprecated, yanked, superseded, rollback-eligible, rehearse-only, or otherwise operator-visible control-plane states that may coexist as records without implying equivalent live admissibility.

### D7. Schema And Format Family Lines

Schema or format families that may coexist only under explicit compatibility, refusal, or migration law while remaining subordinate to canonical schema authority.

### D8. Exact-Target Distribution Lanes

Artifact lanes differentiated by exact target, platform, arch, ABI, toolchain, or environment that may coexist in release-control records and archives without collapsing family labels into exact binary meaning.

## E. Allowed Coexistence Classes

The following coexistence classes are lawful only under explicit conditions.

### E1. Historical Release-Record Coexistence

Multiple release identities, manifests, indices, archive entries, and superseded or yanked records may coexist when:

- each retains explicit release identity
- release-contract-profile or equivalent compatibility meaning remains explicit
- deprecation, yank, supersession, and rollback posture remain typed rather than implicit
- archive and mirror law remain upstream

### E2. Candidate-Set Coexistence In Resolution

Multiple versioned component or release candidates may coexist in index and resolution surfaces when:

- exact identity remains explicit
- compatibility envelopes remain explicit
- target-family and exact-target distinctions remain preserved
- selection policy stays downstream of compatibility
- yanked or blocked candidates remain visible as governed history rather than deleted folklore

### E3. Operator-State Coexistence

Current, prior, rollback-target, pinned, deprecated, yanked, and superseded states may coexist as control-plane facts when:

- operator transaction typing remains explicit
- traceability and reversibility posture remain explicit
- coexistence of records is not confused with simultaneous live authority

### E4. Schema Or Format Family Coexistence

Multiple schema or format families may coexist only when:

- canonical `schema/` authority remains explicit over `schemas/`
- compatibility, refusal, or migration rules are explicit
- shared storage or parsing convenience does not collapse incompatible meaning into one lane

### E5. Runtime Realization Coexistence Under Bounded Isolation

Version-distinguished runtime components, services, or kernel-adjacent structures may coexist only when all of the following hold:

- subject identities remain explicit
- lifecycle posture for each subject remains explicit
- authoritative truth ownership is not duplicated or hidden
- state externalization obligations remain satisfied
- replay and snapshot interpretation remain possible
- isolation boundaries remain explicit
- coexistence does not silently claim restartless replacement, handoff, or distributed authority

### E6. Target-Lane Artifact Coexistence

Different exact-target artifacts may coexist across release, archive, and mirror surfaces when:

- target family is not used as a substitute for exact target
- release contract profile or equivalent compatibility envelope remains explicit
- build identity remains provenance only, not semantic compatibility

## F. Non-Allowed Or Strongly Gated Coexistence Classes

The following classes must not be treated as casually lawful coexistence.

### F1. Dual-Writer Shared-Truth Coexistence

Two version-distinguished runtime subjects must not simultaneously mutate the same authoritative truth scope by convenience. If a subject appears to share live write authority with another version, the situation is blocked unless stronger law explicitly proves legality.

### F2. Semantic-Conflict Coexistence

Different semantic contract meanings must not coexist as if they were interchangeable merely because product versions look similar or artifacts can be loaded together.

### F3. Hotswap-By-Stealth

Coexistence must not be used as a hidden excuse for restartless replacement, live state handoff, or partial hot reload. Those remain later prompts.

### F4. Distributed Split-Authority Coexistence

Multiple versions must not share or race distributed authority envelopes by convenience. Coexistence doctrine does not authorize quorum drift, authority handoff, or shard relocation.

### F5. Projection-Led Coexistence

`field/`, `schemas/`, generated manifests, feeds, or other projected surfaces must not be treated as lawful independent coexistence lanes against their canonical owners.

### F6. Publication-Or-Archive Shortcut Coexistence

Archive presence, mirror presence, or generated feed presence must not be treated as permission for live coexistence, live selection, or trust-bearing operational use.

### F7. Shared Hidden-State Coexistence

Two version-distinguished runtime realizations must not coexist while relying on hidden service-local or component-local truth that replay, snapshot, and state law cannot reconstruct lawfully.

## G. Relationship To Semantic Doctrine

Coexistence remains subordinate to semantic and domain law.

The governing consequences are:

- domains remain owners of semantic truth
- coexistence applies to realizations, envelopes, and records, not to competing semantic truths
- ownership review remains binding
- bridge law remains binding
- representation ladders remain binding
- formalization and provenance continuity remain binding
- coexistence must not convert semantic drift into tolerated plurality

Coexistence therefore cannot be used to:

- override canonical semantic roots
- normalize `schema/` versus `schemas/` disagreement into "both versions are valid"
- normalize `packs/` versus `data/packs/` ambiguity into free substitution
- infer domain law from build, file-layout, or loader convenience

## H. Relationship To State, Replay, Snapshot, Lifecycle, And Isolation

Coexistence depends on these layers and does not replace them.

### H1. State Externalization

Coexistence is only lawful when authoritative or continuity-relevant state is not trapped inside one version container by convenience.

### H2. Replay

Replay must remain able to distinguish which versioned subject emitted or consumed replay-relevant history. Coexistence that erases versioned causality or history boundaries is invalid.

### H3. Snapshot

Snapshots spanning coexistence horizons must preserve version posture, authority posture, lifecycle posture, and compatibility anchors explicitly. Snapshot capture is not a proof that coexistence itself is lawful.

### H4. Lifecycle

Lifecycle posture remains upstream. Two versions may coexist in different lifecycle states such as `available`, `quiescent`, or `retired`, but coexistence does not imply all versions may be simultaneously `active` in the same authority envelope.

### H5. Isolation

Isolation remains upstream. Coexistence requires explicit separation of authority, state, execution, visibility, or control-plane posture where version multiplicity would otherwise blur lawful boundaries.

Coexistence is therefore not a substitute for replay, snapshot, lifecycle, or isolation law. It is a consumer of them.

## I. Relationship To Versioning And Release Contract Profile

Coexistence uses explicit compatibility envelopes rather than raw version comparison.

The governing consequences are:

- raw version equality is not enough to justify coexistence
- raw version inequality is not enough to forbid coexistence
- semantic contract bundle hash remains explicit meaning compatibility
- protocol, schema, and format compatibility remain explicit
- release contract profile remains the release-surface compatibility envelope
- target family remains distinct from exact target
- build identity remains provenance and exact artifact identity, not semantic compatibility

Release-control coexistence must therefore be evaluated through:

- semantic contract binding
- explicit compatibility ranges
- release identity
- exact target descriptors
- trust and governance posture where relevant
- typed operator transaction context where selection or rollback is involved

## J. Relationship To Operator Transaction And Archive/Mirror Law

Coexistence must remain compatible with release-control continuity and historical recoverability.

The governing consequences are:

- downgrade and rollback remain distinct from coexistence
- yanked, deprecated, superseded, and rollback-eligible states may coexist as historical and operator-visible records
- archive law preserves historical versions without making them preferred or live
- mirror law exposes availability surfaces without becoming canonical truth
- publication, trust, and licensing gates remain upstream
- operator transactions must remain typed, attributable, reviewable, and traceable

Archive or mirror coexistence is therefore lawful historical or availability coexistence, not automatic runtime or publication approval.

## K. Invalidity And Failure

Coexistence validity must be classifiable explicitly.

The key categories are:

- `bounded_lawful`
  - the coexistence scope is explicit and satisfies the declared constraints
- `review_gated`
  - coexistence may be discussable, but requires explicit human review before stronger claims
- `provisional`
  - coexistence evidence exists, but compatibility or continuity proof is not yet strong enough
- `compatibility_unproven`
  - explicit compatibility envelope is missing, incomplete, or contradictory
- `semantic_conflict`
  - the versions imply incompatible semantic meaning or erased bridge semantics
- `ownership_invalid`
  - coexistence conflicts with ownership review or canonical-root discipline
- `state_entangled`
  - authoritative or continuity-relevant state is trapped across versions unsafely
- `replay_snapshot_incompatible`
  - lawful replay or lawful snapshot interpretation would be broken or ambiguous
- `lifecycle_invalid`
  - coexistence posture conflicts with lifecycle legality for the claim being made
- `isolation_invalid`
  - containment boundaries are missing or insufficient
- `release_contract_invalid`
  - release-control coexistence bypasses release contract profile, exact target, or trust posture
- `hotswap_by_stealth`
  - coexistence is being used to smuggle restartless replacement or live cutover semantics
- `distributed_authority_leak`
  - coexistence silently introduces split authority or handoff assumptions

Later systems must not assume all coexistence claims are equally lawful.

## L. Ownership And Anti-Reinvention Cautions

The following cautions remain fully active:

- `fields/` remains canonical semantic field substrate; `field/` remains transitional
- `schema/` remains canonical semantic contract law; `schemas/` remains projection-facing
- `packs/` remains canonical for runtime packaging and activation scope; `data/packs/` remains scoped authored-pack authority in residual split territory
- canonical versus projected/generated distinctions remain binding
- the thin `runtime/` root is not canonical by name alone
- release/control-plane convenience must not infer coexistence canon or permission
- stale planning numbering and stale titles remain evidence rather than authority

Coexistence law must therefore be extracted from current doctrine and repo reality, not invented from:

- loader folklore
- packaging habits
- one platform lane
- one local side-by-side binary trick
- one generated feed or mirror view

## M. Anti-Patterns And Forbidden Shapes

The following shapes are constitutionally forbidden:

- coexistence as arbitrary side-by-side binaries
- coexistence that bypasses explicit compatibility envelopes
- coexistence that silently changes truth or state semantics
- coexistence used as hotswap-by-stealth
- coexistence that treats archive retention as runtime legality
- coexistence that treats mirror availability as source-of-truth authority
- coexistence that treats `schemas/` as a peer semantic owner to `schema/`
- coexistence that normalizes `packs/` and `data/packs/` into free substitution
- coexistence that treats build ids or filenames as sufficient compatibility proof
- coexistence that hides lifecycle posture, replay lineage, or isolation boundaries
- coexistence that introduces distributed split authority under a local convenience label

## N. Stability And Evolution

This artifact is `provisional` but canonical.

It directly enables:

- the next checkpointed runtime review after `Φ-B3`
- selected `Υ-B0`, `Υ-B1`, and `Υ-B2` consumers that must align release-ops and operator receipts with coexistence law
- later guarded reassessment of `Φ-B4 — HOTSWAP_BOUNDARIES-0`
- later guarded reassessment of `Φ-B5 — DISTRIBUTED_AUTHORITY_FOUNDATIONS-0`
- later `Ζ` blocker reduction and continuity reassessment

Update discipline remains explicit:

- later prompts may refine coexistence procedures or operational consumers
- later prompts may not silently redefine coexistence into migration, rollback, archive retention, or hotswap
- any update that weakens ownership, replay, snapshot, lifecycle, isolation, or release-contract constraints requires explicit review
