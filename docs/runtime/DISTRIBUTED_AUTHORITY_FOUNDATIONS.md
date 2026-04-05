Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: post-`Φ-B5` checkpoint, later selected `Υ-D3`, future `Ζ`
Replacement Target: later post-`Φ-B5` checkpoint and later distributed live-ops doctrine may refine procedures and infrastructure without replacing the distributed-authority semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PRE_DISTRIBUTED_AUTHORITY_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB5_ADMISSION_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB4.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_YD.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`, `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`, `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `docs/blueprint/MANUAL_REVIEW_GATES.md`, `docs/blueprint/STOP_CONDITIONS_AND_ESCALATION.md`, `server/shard/shard_api.h`, `server/shard/dom_shard_lifecycle.h`, `server/shard/dom_cross_shard_log.h`, `server/net/dom_server_types.h`, `server/net/dom_server_protocol.h`, `server/net/dom_server_runtime.h`, `data/registries/net_replication_policy_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/provenance_classification_registry.json`

# Dominium Distributed Authority Foundations

## A. Purpose And Scope

This doctrine exists because the post-`Υ-D` checkpoint reclassified `Φ-B5 — DISTRIBUTED_AUTHORITY_FOUNDATIONS-0` as `ready_with_cautions`.

It solves a specific problem: Dominium now has explicit law for coexistence, hotswap boundaries, live trust-transition prerequisites, live-cutover receipts and provenance, and publication/trust execution operationalization. Those layers make distributed authority discussable, but they do not yet freeze what distributed authority itself means, what may be partitioned or transferred, and what proof and continuity obligations remain non-negotiable.

Without one explicit distributed-authority doctrine, later work could wrongly treat:

- shard layout as lawful authority partition
- replication policy as authority convergence
- handoff as an implementation detail instead of a truth-bearing boundary
- state transfer as a transport concern instead of a continuity concern
- trust convergence as assumed rather than declared
- one shard runtime pattern as architectural canon

This artifact governs:

- what distributed authority means in Dominium
- what authority regions, authority domains, and authority handoff mean
- what classes of subjects may be partitioned, transferred, or must remain single-authority
- what proof, continuity, lifecycle, replay, trust, and release obligations stay upstream
- what later checkpoints and future `Ζ` planning must consume rather than reinvent

This artifact does not implement:

- clustering, consensus, or distributed execution systems
- shard relocation or state-partition transfer machinery
- live authority handoff systems
- trust-root rotation or revocation propagation systems
- publication or release automation

Checkpoint relation:

- this is the next risky-tail `Φ` doctrine prompt after the post-`Υ-D` checkpoint
- it remains doctrine-level only
- it must preserve the checkpoint caution that distributed live operations remain blocked even if distributed-authority foundations are now ready to define

## B. Core Definition

In Dominium, `distributed authority` is the declared, bounded, proof-bearing partitioning, holding, or transfer of authoritative runtime responsibility across more than one authority region while preserving one lawful truth owner for each governed scope at every relevant horizon.

An `authority region` is a bounded runtime responsibility envelope inside which one declared authority-bearing subject may lawfully act for a defined domain, partition, or shard scope.

An `authority domain` is the truth-bearing scope to which that authority region applies, such as a domain owner mapping, partitioned simulation scope, or other explicitly named governed scope. Authority domains are semantic and continuity concepts, not only process or host placement labels.

An `authority handoff` is the governed transfer of responsibility for one bounded authority domain from one lawful authority region to another under explicit lifecycle, state, replay, proof-anchor, trust, and receipt continuity constraints.

Distributed authority is not:

- `generic sharding`
  - partitioning work or data does not by itself define lawful authority
- `simple replication`
  - replicated state or mirrored events do not by themselves define authority convergence
- `hotswap`
  - local live replacement remains a distinct boundary problem
- `rollback`
  - restoring or reselection of a prior state or release does not define distributed authority
- `publication or control-plane action`
  - release, visibility, or trust-bearing control-plane movement remains downstream and distinct
- `implementation-level clustering`
  - process layout, host layout, or message routing convenience does not define constitutional authority truth

## C. Why This Doctrine Is Necessary

Distributed authority changes truth-bearing execution assumptions.

The repo already contains real precursor substrate:

- `server/shard/shard_api.h` freezes shard placement, ownership scope, access validation, replay state, and shard-local logs
- `server/shard/dom_shard_lifecycle.h` freezes explicit shard lifecycle states and transitions
- `server/shard/dom_cross_shard_log.h` freezes deterministic cross-shard message ordering, idempotency, and log hashing
- `server/net/dom_server_types.h` freezes explicit domain-owner to shard-owner mapping
- `server/net/dom_server_protocol.h` freezes typed ownership-transfer and rolling-update event kinds
- `server/net/dom_server_runtime.h` freezes shard version, capability, baseline-hash, checkpoint, lifecycle, and cross-shard message-log surfaces
- `data/registries/net_replication_policy_registry.json` freezes replication policy names, but only as provisional precursor substrate

That substrate is enough to make distributed authority doctrinally necessary. It is not enough to let implementation folklore decide:

- who is authoritative
- when authority may move
- how proof anchors or quorums constrain the move
- how replay and snapshots remain reconstructable
- how trust convergence remains subordinate to upstream admission law

Earlier checkpoints made this admissible only with caution. This doctrine preserves that caution while finally freezing the missing model.

## D. Distributed-Authority Subject Classes

The following high-level subject classes define what distributed authority may refer to.

### 1. Authority-Bearing Domain Subjects

These are truth-bearing runtime scopes whose owner must remain explicit at every relevant horizon. Examples include domain-owner mappings, domain-bound service scopes, or other explicitly governed truth carriers.

### 2. Partition Or Shard Authority Subjects

These are bounded shard or partition scopes that may host or carry authority-bearing work under explicit ownership, lifecycle, and replay law. They are not automatically lawful just because a shard exists.

### 3. Handoff-Boundary Subjects

These are subjects whose meaning changes when authority moves from one lawful region to another. They include transitions across shard ownership, active-to-draining-to-frozen boundaries, and other explicit authority-boundary crossings.

### 4. State-Transfer Subjects

These are state-bearing scopes whose lawful movement requires explicit externalization, snapshot legality, transfer legality, and non-ambiguous ownership after handoff.

### 5. Proof-Anchor Or Quorum Subjects

These are continuity-bearing structures that later work may use to prove distributed handoff, replay integrity, or converged authority posture. This doctrine freezes that they are required classes, not that their implementation is already solved.

### 6. Replay And Continuity Subjects

These are event, message, checkpoint, snapshot, baseline-hash, and other reconstructability-bearing surfaces whose continuity remains upstream of any distributed claim.

### 7. Trust-Convergence Subjects

These are distributed-authority subjects whose lawful meaning depends on trust posture, trust prerequisites, revocation continuity, or publication/trust operationalization gates remaining satisfied across multiple authority regions.

### 8. Explicitly Non-Distributable Subjects

These are semantic or authority-bearing subjects that must remain single-authority because distribution would erase truth ownership, bridge legality, or lawful continuity under current doctrine.

## E. Authority Boundary Classes

Dominium recognizes the following authority-boundary classes.

### 1. Single-Authority-Only Boundaries

Use this class when semantic truth, authority, or bridge legality requires exactly one authority region and no partition or handoff is currently admitted.

### 2. Partitionable But Non-Transferable Boundaries

Use this class when work or visibility may be partitioned across regions, but authority may not move once declared. This prevents convenience-based handoff claims.

### 3. Bounded Transferable Boundaries

Use this class when later work may discuss explicit handoff under declared lifecycle, state, replay, snapshot, proof-anchor, trust, and receipt conditions.

### 4. Review-Gated Distributed Boundaries

Use this class when partition or transfer is thinkable only under explicit human review because blast radius, trust posture, or continuity burden remains high.

### 5. Future-Only Or Prohibited Distributed Boundaries

Use this class when the subject depends on unsolved replication proof, quorum proof, runtime cutover proof, or trust convergence behavior that remains outside current maturity.

## F. Relationship To Semantic Doctrine

Semantic law outranks distributed-authority law.

Distributed authority must not:

- redefine semantic truth
- redefine domain ownership
- erase cross-domain bridge legality
- convert projected or generated surfaces into semantic owners
- split semantic authority by convenience

Some semantic or authority-bearing structures therefore remain non-distributable under the current doctrine horizon.

Distributed authority is about lawful hosting, partition, handoff, and continuity of already-declared truth-bearing scopes. It is not a license to create multiple competing truths.

## G. Relationship To Lifecycle And State

Lifecycle legality and state externalization remain upstream.

Distributed authority claims must preserve all of the following:

- authority posture is explicit before, during, and after any partition or handoff
- active, draining, frozen, offline, suspended, degraded, or equivalent authority states remain distinguishable
- authoritative truth is not trapped in undocumented local state
- state transfer cannot occur lawfully unless the relevant state is externalizable or otherwise explicitly reconstructable
- state handoff cannot be disguised as hidden local mutation followed by reassignment folklore

If a subject cannot state what state remains local, what state is externalized, and what state is transferred, the authority claim is not yet lawful.

## H. Relationship To Replay, Snapshots, And Proof Anchors

Distributed authority must preserve replay intelligibility.

This means:

- event and message history must remain attributable across authority regions
- snapshot legality must remain explicit when a partition or handoff horizon is involved
- state-transfer legality must remain explicit rather than implied by transport success
- proof-anchor continuity must remain reconstructable across authority movement
- quorum semantics, where later needed, must be defined constitutionally rather than inferred from cluster implementation

Distributed replay continuity is a prerequisite, not an afterthought.

This doctrine therefore freezes a stronger rule: no distributed authority claim is honest unless later consumers can say how replay, snapshots, and proof-anchor continuity remain reconstructable after partition or handoff.

## I. Relationship To Isolation, Coexistence, And Hotswap

Isolation, coexistence, and hotswap remain distinct and upstream.

The governing consequences are:

- coexistence may be necessary for some distributed horizons, but coexistence alone is not distributed authority
- hotswap may be relevant to a local replacement boundary, but hotswap is not distributed handoff
- isolation boundaries remain binding and must not be blurred into convenience-based shared authority
- distributed authority must not collapse these earlier doctrines into generic “the system stayed up” folklore

If a distributed claim depends on hidden shared writers, blurred isolation, or undeclared coexistence semantics, it is invalid.

## J. Relationship To Trust And Revocation Continuity

Distributed authority must remain compatible with live trust-transition prerequisites, trust execution and revocation continuity, and publication/trust execution operationalization gates.

This means:

- trust convergence may not be assumed merely because multiple regions can verify locally
- revocation continuity must remain explicit across authority regions
- distributed authority cannot outrun live trust admission
- this doctrine does not assume that live trust realization is already implemented

Trust-convergence subjects therefore remain explicit classes in this doctrine, not solved behaviors.

## K. Relationship To Release/Control-Plane Doctrine

Distributed authority must remain compatible with:

- release contract profile
- release-index and resolution semantics
- operator transactions
- generalized live-cutover receipts and provenance continuity
- archive and mirror continuity
- publication and trust operationalization gates

Release or control-plane convenience does not imply lawful distributed authority.

The existence of versioned shards, rolling-update events, baseline hashes, or release-control receipts does not by itself prove that authority handoff or distributed convergence is lawful. These remain inputs, not proofs.

## L. Invalidity And Failure

Distributed-authority claims must be classifiable explicitly.

The canonical invalidity and failure categories are:

- `single_authority_only`
  - the subject remains constitutionally non-distributable
- `partitionable_non_transferable`
  - partition is discussable, but handoff is not lawful
- `bounded_transfer_requires_review`
  - transfer may be discussable only under explicit human review
- `proof_anchor_or_quorum_missing`
  - continuity anchors or quorum semantics are absent
- `replication_not_proven`
  - replication substrate exists, but proof-backed convergence does not
- `state_transfer_incoherent`
  - state externalization or transfer legality is missing or ambiguous
- `replay_snapshot_incompatible`
  - replay or snapshot continuity would become non-reconstructable
- `lifecycle_invalid`
  - lifecycle posture is incompatible with the authority claim
- `isolation_invalid`
  - isolation boundaries are insufficient
- `trust_convergence_unadmitted`
  - trust prerequisites or revocation continuity do not admit the distributed claim
- `release_control_overclaim`
  - release or control-plane signals are being mistaken for distributed authority proof
- `future_only_or_policy_prohibited`
  - the claim depends on later doctrine or remains outside current policy

## M. Canonical Vs Derived Distinctions

Canonical truth about distributed authority lives in:

- this doctrine
- its paired machine-readable registry
- upstream runtime, trust, receipt, and release doctrine
- later explicitly promoted authority, handoff, or proof records where doctrine names them

Derived surfaces include:

- dashboards
- shard maps
- local cluster views
- routing tables
- logs
- profiling output
- convenience topology diagrams

Derived views may summarize distributed posture. They must not redefine authority truth.

## N. Ownership And Anti-Reinvention Cautions

The following cautions remain fully binding:

- `fields/` remains canonical over `field/`
- `schema/` remains canonical over `schemas/`
- `packs/` and `data/packs/` are not freely collapsible
- canonical versus projected/generated distinctions remain binding
- the thin `runtime/` root is not canonical by name alone
- stale numbering or older checkpoint titles do not override active checkpoint law
- doctrine must be extracted from current repo reality rather than invented as greenfield distributed-systems folklore

Additional caution applies because shard and net code can look operationally authoritative while still remaining only precursor substrate. One implementation pattern must not become constitutional truth by familiarity alone.

## O. Anti-Patterns / Forbidden Shapes

The following shapes are forbidden:

- shard layout implies lawful authority partition
- replication implies authority convergence
- hotswap implies transferability
- local cluster behavior treated as architectural truth
- distributed authority bypassing replay, snapshot, proof-anchor, trust, or receipt continuity
- publication or rolling-update signals treated as authority proof
- authority handoff with no explicit proof-anchor or quorum semantics
- partition transfer with undocumented local state
- coexistence or isolation shortcuts treated as distributed legality
- doctrine existence treated as operational realization

## P. Stability And Evolution

This artifact is `provisional` because the current checkpoint only moved distributed authority into `ready_with_cautions`, not into implemented or proven live maturity.

This doctrine now enables:

- the immediate post-`Φ-B5` checkpoint
- later pre-`Ζ` planning and blocker reduction
- later refinement prompts around authority handoff, deterministic replication proof, proof-anchor or quorum semantics, and distributed replay continuity

Later prompts may refine this doctrine only by extending it explicitly. They may not:

- reinterpret sharding as lawful authority
- reinterpret replication as convergence proof
- reinterpret hotswap as distributed handoff
- erase the preserved distinctions among distributed authority, release/control-plane movement, replay continuity, and trust convergence
