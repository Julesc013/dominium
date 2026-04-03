Status: CANONICAL
Last Reviewed: 2026-04-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Φ-B, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_POST_SIGMA_B_PRE_PHIB_UPSILON.md`, `docs/planning/NEXT_TWO_SERIES_PLAN_PHIB_UPSILON.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`, `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`, `specs/reality/SPEC_CAPABILITY_SURFACES.md`, `specs/reality/SPEC_REPRESENTATION_LADDERS.md`, `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md`, `specs/reality/SPEC_FORMALIZATION_CHAIN.md`, `specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`

# Dominium Event Log And Replay Doctrine

## 1. Purpose and Scope

This document defines the constitutional event log and replay doctrine for Dominium.
It exists because the completed `Λ` block froze truth totality, sparse materialization, domain contracts, bridge law, representation law, formalization law, and ownership law, while the completed `Σ` and `Φ-A2` blocks froze governance, task/interface/safety law, kernel law, component law, service law, binding law, state law, and lifecycle law without yet defining the lawful history grammar that later continuity work must consume.

The event log and replay doctrine governs:

- what an event log means in Dominium
- what replay means in Dominium
- why replay and event history form a distinct constitutional layer
- which event classes matter for authoritative replay and which do not
- how replay must remain subordinate to semantic law, deterministic law, ownership review, bridge law, representation ladders, provenance lineage, state law, and lifecycle law
- what later `Φ-B1`, `Φ-B2`, `Υ`, and `Ζ` work may rely on once replay law is explicit

This prompt is not:

- an append-only log implementation
- a write-ahead log implementation
- an event bus implementation
- a snapshot implementation
- a save-file or persistence format definition
- a migration or distributed replay implementation
- a hotswap or live-ops implementation
- a doctrine rewrite of semantic, governance, runtime, or release law

Checkpoint relation:

- the active execution path is `post-Σ-B / post-Φ-A2 / pre-Φ-B-and-Υ`
- the latest checkpoint judged event/log doctrine `ready_with_cautions`
- this is the first `Φ-B` prompt after that checkpoint
- older planning artifacts may still retain stale numbering drift, but this document follows active checkpoint law rather than legacy sequence text

Repo-grounded extension surfaces already exist and must be treated as evidence rather than as automatic canon:

- `engine/modules/replay`
- `server/shard/dom_cross_shard_log.h`
- `server/shard/dom_cross_shard_log.cpp`
- `server/persistence/dom_checkpointing.h`
- `engine/include/domino/snapshot.h`
- `app/ui_event_log.c`
- `app/include/dominium/app/ui_event_log.h`
- `control/control_plane_engine.py`
- `net/anti_cheat/anti_cheat_engine.py`

## 2. Core Definition

In Dominium, an event log is a declared, auditable, externalized or externalizable ordered record of replay-relevant transitions or evidence classes produced under explicit semantic, runtime, and governance law.
It is not defined by one file shape, one storage backend, one transport, or one subsystem.

In Dominium, replay is the lawful reconstruction, validation, reenactment, or dispute-oriented re-examination of runtime and truth-relevant history using authoritative event classes, explicit state law, deterministic ordering law, and declared continuity rules.

Event logs and replay are distinct but linked:

- event logs record or externalize replay-relevant history
- replay consumes lawful history plus state and contract context
- neither one replaces truth itself
- neither one becomes semantic authority by convenience

Event logs and replay are not:

- `diagnostic logs`
  - diagnostics may be useful evidence, but diagnostics alone are not authoritative replay history
- `save files`
  - save files are state artifacts, not ordered transition doctrine
- `snapshots`
  - snapshots are immutable state anchors or views, not the same thing as ordered replay history
- `caches`
  - caches are reconstructable convenience state, not canonical replay source
- `UI history`
  - UI event history is presentation-local unless explicitly promoted under stronger law
- `control-plane changelogs`
  - operator-visible change records may matter, but they are not automatically authoritative replay
- `release provenance records`
  - release and publication lineage is related but distinct from runtime replay history

The distinction is already visible in repo reality:

- `app/ui_event_log.*` is an optional UI event helper and is not sufficient as authoritative replay
- `engine/modules/replay` is a deterministic replay subsystem surface and points toward authoritative replay concerns
- `server/persistence/dom_checkpointing.h` and `engine/include/domino/snapshot.h` show checkpoints and snapshots as distinct continuity artifacts
- `control/control_plane_engine.py` explicitly restricts replay-only mode to read-only reenactment and view behavior

## 3. Why Replay Law Is Necessary

Replay law is necessary because Dominium is already committed to deterministic Process execution, truth/perceived/render separation, explicit authority, and non-silent semantic drift refusal.

Without explicit replay law, the architecture is vulnerable to forbidden shortcuts:

- replay treated as developer debugging only
- logs treated as ad hoc diagnostics with no authority discipline
- lifecycle or control transitions becoming irreconstructable
- service-local history being mistaken for complete truth history
- projected or generated artifacts being mistaken for canonical replay source
- distributed or live-ops work inventing continuity semantics after the fact

Replay law is therefore required for:

- deterministic verification
- lawful continuity reasoning
- auditability and dispute analysis
- simulation debugging without semantic drift
- later snapshot doctrine
- later isolation and sandbox audit boundaries
- later operator transaction, downgrade, and provenance work in `Υ`
- later multi-version, hotswap, distributed-authority, and `Ζ` caution

Replay convenience must not redefine truth, ownership, bridge legality, or runtime authority.

## 4. Event Classes

The event taxonomy is constitutional and intentionally general.
It defines replay-relevant classes, not every concrete emitter or storage format.

### 4.1 Truth-Affecting Events

These are events that record lawful transitions relevant to authoritative truth evolution, Process execution, or deterministic state progression.

They include:

- Process-triggered truth transitions
- accepted authoritative inputs that lawfully alter truth
- committed macro or micro transition events when they matter to authoritative evolution
- deterministic hash or anchor transitions when those are part of authoritative validation

These events are primary candidates for authoritative replay.

### 4.2 Authority and Ownership-Sensitive Events

These are events that materially affect who may lawfully act, who has authority, or whether an action was refused because authority, entitlement, capability, or ownership conditions were not met.

They include:

- authority grant or refusal events
- ownership-sensitive refusal or validation events
- compatibility or capability gate outcomes when they determine lawful execution posture

These events are replay-relevant because legality is part of runtime truth about what happened.

### 4.3 Bridge-Mediated Events

These are events whose meaning depends on explicit cross-domain bridge law.

They include:

- cross-domain transfers
- cross-shard or cross-domain routing where causal ordering matters
- events whose legality depends on a declared bridge family rather than local domain action alone

These events are authoritative only when replay preserves the bridge-mediated nature of the transition.

### 4.4 Lifecycle Transition Events

These are events that record declared, initialized, available, active, quiescent, suspended, degraded, blocked, stopped, retired, failed, recovered, or later handoff-related posture changes for runtime subjects.

They matter because replay must preserve continuity and legality, not just truth deltas.

### 4.5 Binding Transition Events

These are events that record service-domain attachment, detachment, mediation posture changes, replay-anchor attachment, or other changes whose legality depends on explicit domain-service binding law.

They matter when replay needs to preserve how a runtime structure was lawfully connected to domain authority.

### 4.6 Provenance and Formalization-Relevant Events

These are events that affect lineage, revision posture, formalization stage, protocol state, institutional posture, or explicit provenance anchors required to interpret history lawfully.

They include:

- lineage anchor creation
- supersession or revision events
- formalized protocol or institutional state transitions when those affect validity

These events are authoritative when omission would erase lawful interpretation of history.

### 4.7 Observation-Only and Presentation-Only Events

These are events that describe view changes, observation posture, rendered output posture, or presentation-local interaction without changing authoritative truth or runtime legality.

They include:

- UI event history
- camera or view posture history used only for presentation
- observation-only traces

These events may be useful for reenactment or diagnostics, but they are not authoritative by default.

### 4.8 Control-Plane and Operator-Visible Events

These are events visible to operators or control surfaces.

They include:

- control-plane refusals
- policy-mediated read-only replay controls
- operator-visible degradation or refusal events
- checkpoint trigger events

Some of these are replay-relevant, but operator visibility alone does not make them authoritative.

### 4.9 Diagnostic-Only Events

These are diagnostic, debugging, instrumentation, or performance-oriented events whose main purpose is observability rather than constitutional replay.

They may be retained as auxiliary evidence.
They are not authoritative replay history unless a stronger doctrine explicitly promotes them.

## 5. Authoritative Replay Scope

Authoritative replay is the subset of replay that may be used to reconstruct, validate, or contest lawful truth and runtime legality over time.

Authoritative replay ordinarily includes:

- truth-affecting events
- authority and ownership-sensitive events
- bridge-mediated events
- lifecycle transition events when continuity or legality depends on them
- binding transition events when runtime legality depends on them
- provenance and formalization-relevant events when lineage or revision posture affects validity

Auxiliary but non-authoritative replay evidence may include:

- observation-only events
- presentation-only events
- operator-visible control surfaces
- diagnostics and performance traces

Non-authoritative history classes include:

- UI event logs by default
- cache churn
- projection generation history
- mirrored or generated artifact outputs
- release changelogs
- product-local session history unless separately promoted under stronger law

The governing scope rules are:

- authoritative replay must not be polluted by convenience-only projected state
- auxiliary logs may support investigation without becoming truth source
- replay law must preserve canonical versus projected or generated distinctions
- replay scope may be partial or horizon-scoped, but the partiality must remain explicit rather than hidden

## 6. Event and Log Relationship to Truth

Events do not replace truth.
They record lawful transitions or legality-relevant history about truth evolution and runtime posture.

The governing truth rules are:

- truth remains total even when materialization is sparse
- replay reconstructs or validates lawful evolution without redefining ontology
- absence of an eagerly emitted event does not imply that no truth existed
- event logs must not be mistaken for the whole of reality
- replay may depend on authoritative events plus explicit state law plus lawful reconstruction rules

This matters because sparse materialization and lawful replay are compatible only when replay is treated as continuity evidence, not as ontology replacement.

## 7. Event and Log Relationship to State Externalization

Replay doctrine depends on explicit state law.
It may not invent hidden truth ownership or treat runtime-local memory as sufficient history.

The governing state rules are:

- authoritative replay cannot rely on hidden service-local truth
- replay must align with authoritative truth state, lawful derived runtime-managed state, transient execution state, projection state, presentation state, and provenance state distinctions
- replay history and state externalization must remain mutually intelligible
- authoritative replay may rely on externalized authoritative state anchors, but those anchors are not identical to ordered replay history
- snapshot doctrine later consumes replay law; replay law does not assume snapshot implementation here

Replay and state law therefore meet at continuity boundaries.
Neither one replaces the other.

## 8. Event and Log Relationship to Lifecycle

Lifecycle transitions are replay-relevant because lawful history includes runtime posture, not only truth deltas.

Replay must preserve:

- active versus suspended posture
- degraded versus fully lawful posture
- blocked or refused posture
- stop versus retire distinction
- invalid or failed transitions

Replay must not:

- treat runtime availability as truth existence
- erase degraded or blocked meaning
- flatten suspend, quiesce, stop, and fail into one generic interruption

Later hotswap, recovery, rollback, and live continuity work depends on this distinction remaining explicit.

## 9. Event and Log Relationship to Bindings and Bridges

Replay must remain binding-aware and bridge-aware.

The governing rules are:

- replay must preserve domain-service binding legality where runtime services mediate or coordinate domain-facing behavior
- if an event crosses domain boundaries, explicit bridge legality remains binding
- replay must not erase mediation, ownership checks, compatibility checks, or bridge dependencies from history
- service-local history is not sufficient as whole-history authority when bridge-mediated or multi-domain effects occurred

The repo already shows this pressure:

- `server/shard/dom_cross_shard_log.*` preserves deterministic ordering, causal keys, and idempotency for cross-shard messages
- `control/control_plane_engine.py` explicitly refuses replay-mode mutation

Those surfaces are evidence that replay history must preserve legality, not just payload order.

## 10. Event and Log Relationship to Representation Ladders

Replay must remain representation-aware.

The governing representation rules are:

- macro and micro history must not be silently collapsed into semantically lossy history
- substituted or capsuled representations may support replay only when ladder invariants and lawful expansion/descent remain preserved
- replay history must not fabricate detail that was never lawfully present
- micro detail is not intrinsically more true than macro summary
- macro history is lawful only when it preserves the commitments needed for later lawful descent

Replay therefore may be horizon-scoped, but only under explicit ladder-aware rules.

## 11. Event and Log Relationship to Formalization and Provenance

Replay law must remain compatible with provenance, revision, and formalization lineage.

The governing provenance rules are:

- if an event affects formalized artifacts, protocols, standards, or institutional structures, replay must preserve enough lineage context to interpret the event lawfully
- revision or supersession events must not erase prior lineage silently
- replay must remain compatible with later `Υ` versioning, release contract, index, archive, and operator transaction doctrine
- provenance-relevant anchors, deterministic hashes, and revision identifiers may be replay-relevant even when they are not the truth itself

Repo evidence already points in this direction:

- `engine/include/domino/provenance.h` makes lineage deterministic and namespace-scoped
- `server/server_console.py` emits epoch anchors alongside snapshots

## 12. Event and Log Relationship to Operator and Control-Plane Activity

Some control-plane or operator actions are replay-relevant.
Not all operator logs are authoritative replay logs.

The governing operator rules are:

- operator or control actions are replay-relevant when they alter lawful runtime posture, checkpoint triggers, refusal posture, or truth-affecting execution legality
- control-plane visibility is not itself authoritative replay
- replay must distinguish between authoritative runtime history and explanatory operator evidence
- release changelogs, update indices, and publication history remain distinct from runtime replay even when later `Υ` work aligns them through provenance law

This distinction is already visible in repo surfaces:

- `control/control_plane_engine.py` restricts replay mode to read-only reenactment controls
- `net/anti_cheat/anti_cheat_engine.py` treats replay detection as an enforcement and audit concern
- `app/ui_event_log.*` remains a UI-facing event helper and not authoritative replay by default

## 13. Event and Log Invalidity and Failure

Replay law must not assume perfect history.
Histories may be missing, malformed, partial, ambiguous, degraded, or contested.

The constitutional invalidity and failure families include:

- `missing_or_truncated_history`
  - required replay-relevant events are absent or incomplete
- `malformed_event`
  - event structure cannot be parsed or validated lawfully
- `ordering_or_causality_invalid`
  - deterministic ordering, causal ordering, or declared sequencing is broken
- `determinism_mismatch`
  - replay equivalence or deterministic validation fails
- `ownership_invalid`
  - events imply authority or ownership transitions not supported by ownership law
- `bridge_invalid`
  - cross-domain effects appear without lawful bridge basis
- `lifecycle_invalid`
  - lifecycle transitions are missing, contradictory, or unlawful
- `projection_only_history`
  - only projected or generated artifacts remain where canonical replay source is required
- `provenance_or_formalization_incomplete`
  - lineage or formalization context needed for lawful interpretation is missing
- `compatibility_or_contract_mismatch`
  - event meaning depends on absent or incompatible contract, capability, or version context
- `partial_or_degraded_replay`
  - replay is possible only for bounded questions and may not claim full authority
- `contested_history`
  - multiple incompatible histories or evidentiary claims remain unresolved

Replay may therefore be:

- complete
- bounded
- partial
- degraded
- blocked
- contested
- invalid

Those states must remain explicit.

## 14. Verification and Auditability

Replay must support auditability and testability in principle.

Later systems should be able to verify:

- deterministic ordering expectations
- authoritative versus auxiliary event classes
- lifecycle legality
- ownership legality
- bridge legality
- binding legality
- representation continuity
- provenance relevance and lineage continuity
- refusal and degradation visibility

Replay verification must also be able to distinguish:

- authoritative replay history from diagnostic evidence
- snapshots from ordered event history
- operator/control-plane records from truth-affecting history
- canonical history sources from projected or generated echoes

## 15. Ownership and Anti-Reinvention Cautions

The following cautions remain active and binding:

- `fields/` remains canonical semantic field substrate; `field/` remains transitional compatibility surface
- `schema/` remains canonical semantic contract law; `schemas/` remains a projection or validator-facing mirror
- `packs/` remains canonical for runtime packaging, activation, compatibility, and distribution-descriptor scope
- `data/packs/` remains authoritative only within authored pack-content and declaration scope and may not be silently promoted into full runtime owner
- canonical prose and semantic specs outrank projected or generated mirrors
- the thin `runtime/` root is not canonical by name alone
- older planning numbering drift remains evidence rather than authority
- replay and log law must be extracted from repo reality and doctrine rather than invented as a greenfield logging platform

Extension-over-replacement therefore means:

- treat `engine/modules/replay` as evidence of deterministic replay substrate, not as the whole doctrine
- treat `server/shard/dom_cross_shard_log.*` as evidence of causal and idempotent bridge-sensitive history, not as universal replay law
- treat `server/persistence/dom_checkpointing.h` and `engine/include/domino/snapshot.h` as distinct continuity anchors, not as substitutes for replay doctrine
- treat `app/ui_event_log.*` as evidence of presentation-local history, not as authoritative replay source
- treat control, anti-cheat, and server console surfaces as evidence of replay-sensitive legality, not as a hidden super-log design

## 16. Anti-Patterns and Forbidden Shapes

The following shapes are forbidden:

- treating replay as just debugging
- treating debug logs as authoritative replay
- treating projected or generated artifacts as canonical replay source
- treating service-local history as sufficient truth history
- equating snapshots with replay
- equating save files with replay
- equating control-plane changelogs with authoritative event logs
- replay that ignores lifecycle legality
- replay that ignores bridge legality
- replay that silently rewrites macro or micro meaning
- replay that hides ownership or authority checks
- replay that treats operator visibility as semantic authority
- replay law invented around one backend or one file format as if that backend were canon

## 17. Stability and Evolution

This artifact is `canonical` but `provisional`.
It freezes the replay and event-law floor for the current post-checkpoint `Φ-B` band.

Later prompts may refine:

- `Φ-B1` snapshot-service doctrine
- `Φ-B2` isolation and sandbox audit posture
- later `Υ` provenance, operator transaction, downgrade, archive, and control-plane separation work
- later `Ζ` migration, restartless continuity, live-ops, and distributed-authority caution

Those later prompts must consume this doctrine rather than inventing their own event history semantics.

Updates must remain:

- explicit
- auditable
- non-silent
- subordinate to semantic law, ownership law, bridge law, state law, lifecycle law, and the active checkpoint path
