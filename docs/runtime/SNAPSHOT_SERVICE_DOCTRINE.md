Status: CANONICAL
Last Reviewed: 2026-04-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Φ-B, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_POST_SIGMA_B_PRE_PHIB_UPSILON.md`, `docs/planning/NEXT_TWO_SERIES_PLAN_PHIB_UPSILON.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`, `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`, `specs/reality/SPEC_CAPABILITY_SURFACES.md`, `specs/reality/SPEC_REPRESENTATION_LADDERS.md`, `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md`, `specs/reality/SPEC_FORMALIZATION_CHAIN.md`, `specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`

# Dominium Snapshot Service Doctrine

## 1. Purpose And Scope

`SNAPSHOT_SERVICE_DOCTRINE.md` defines the canonical constitutional law for runtime snapshots in Dominium.

It exists because post-`Λ`, post-`Σ-B`, and post-`Φ-B0` Dominium now has explicit law for:

- semantic truth, ownership, bridges, representation, and formalization
- governance, task, MCP, and safety boundaries
- kernel, component, service, binding, state, lifecycle, and replay/reconstruction boundaries

Snapshot doctrine is the missing continuity layer that explains how bounded captures of runtime-relevant state may be created, interpreted, audited, and later consumed without allowing persistence convenience to redefine truth, authority, or replay semantics.

This artifact governs:

- what a snapshot is
- what classes of snapshots exist
- what lawful snapshot boundaries must preserve
- how snapshots relate to replay, state externalization, lifecycle, bindings, bridges, representation, and provenance
- what invalidity, degradation, and review cautions must remain explicit

This artifact does not implement:

- snapshot storage engines
- save/load backends
- delta formats
- migration engines
- restartless restore or handoff mechanics
- distributed snapshot transfer
- operator transaction machinery

Those later prompts must consume this doctrine rather than invent their own snapshot semantics.

This is a post-`Σ-B` / post-`Φ-A2` / post-`Φ-B0` artifact. It carries forward the checkpoint judgment that snapshot doctrine is `ready_with_cautions`, and it establishes the constitutional floor required by later `Φ-B2`, later `Φ-B3..Φ-B5`, `Υ`, and eventually `Ζ`.

## 2. Core Definition

In Dominium, a snapshot is a declared, bounded, law-governed capture of runtime-relevant state at an identified continuity point, together with the metadata required to interpret the capture's authority posture, scope, representation posture, lifecycle posture, and provenance posture.

A snapshot is a distinct layer because it is neither:

- truth itself
- replay history itself
- a save-file format
- a cache
- a product save point
- a projected or generated artifact by default
- a release or control-plane state capture by default

A snapshot differs from nearby concepts in the following ways:

- Event log: an event log records ordered replay-relevant transitions; a snapshot captures a bounded state horizon.
- Replay: replay reconstructs or validates lawful evolution through history; a snapshot captures a lawful continuity anchor within that evolution.
- Save file: a save file is one possible implementation artifact; it does not define snapshot law.
- Cache: a cache is convenience state and may be discardable; a snapshot is a declared continuity artifact with explicit legal posture.
- Product or session save point: a UX-facing save point is a product concern unless it is explicitly grounded in snapshot law.
- Projected/generated artifact: a projection may summarize or transform state; it is not canonical snapshot truth unless doctrine explicitly classifies it otherwise.
- Release/control-plane capture: build and publication evidence may record operator or release posture, but that does not make them runtime truth snapshots.

## 3. Why Snapshot Law Is Necessary

Snapshot law is necessary because lawful persistence, recovery, continuity analysis, rollback analysis, migration planning, operator transaction review, and later live-ops caution all depend on bounded capture semantics that are explicit rather than assumed.

Without constitutional snapshot doctrine, later architecture tends to collapse into unsafe shortcuts:

- treating snapshots as just save files
- treating snapshots as interchangeable with replay
- trapping authoritative truth inside hidden service-local state and then serializing it opportunistically
- freezing projected/generated views as if they were canonical truth
- treating product checkpoint language as if it were runtime law
- building recovery, downgrade, or handoff behavior on unsound capture assumptions

Snapshot convenience must not redefine truth, ownership, replay lineage, or bridge legality. Snapshot doctrine therefore exists to ensure continuity support remains subordinate to semantic law and compatible with replay law rather than competing with it.

## 4. Snapshot Classes

Dominium recognizes the following constitutional snapshot classes.

### 4.1 Authoritative Truth Snapshots

These are bounded captures of authoritative or authoritative-for-scope state under explicit semantic authority. They are the highest-risk and highest-discipline snapshot class and must preserve ownership, bridge, representation, lifecycle, and provenance law.

### 4.2 Runtime-Support Snapshots

These capture runtime-managed state that may be necessary for lawful continuity, recovery, restart analysis, or bounded execution support, but that does not itself redefine semantic ownership. They remain subordinate to state externalization law.

### 4.3 Replay-Assist Snapshots

These are continuity anchors used to accelerate, delimit, or contextualize replay work. They may assist replay, but they are not replacements for replay lineage where replay remains required.

### 4.4 Operator/Control-Plane-Visible Snapshots

These are snapshots surfaced to operator or control-plane workflows for visibility, audit, or operational reasoning. Visibility does not by itself make them authoritative truth captures.

### 4.5 Projected/Presentation Snapshots

These are bounded captures intended for reporting, presentation, UI, or other derived surfaces. They are explicitly non-canonical unless promoted by stronger law.

### 4.6 Provisional/Diagnostic Snapshots

These are bounded captures useful for diagnostics, debugging, temporary analysis, or validation support. They may be useful evidence, but they must not silently become the source of authoritative restoration claims.

## 5. Snapshot Scope And Boundaries

Snapshot boundaries must be explicit. A lawful snapshot may contain:

- authoritative truth state when the snapshot class and authority posture allow it
- lawful derived runtime-managed state needed for continuity or interpretation
- lifecycle posture relevant to interpreting the capture
- ownership, binding, and bridge metadata needed to preserve legal meaning
- representation horizon metadata
- provenance, contract, compatibility, or policy metadata needed to preserve lawful interpretation

A snapshot must not silently contain the following as authoritative truth:

- projected-only state
- generated-only state
- cache state elevated by convenience
- UI or presentation state treated as semantic authority
- hidden service-local state that never passed lawful externalization discipline
- cross-domain capture with erased bridge mediation
- state whose ownership boundary has been silently collapsed

Snapshot boundaries must declare, at minimum:

- what state classes are included
- what state classes are excluded
- what domain or runtime scope is covered
- what representation posture the capture uses
- what lifecycle posture applied at capture time
- what provenance and compatibility anchors are required for lawful interpretation

Hidden scope assumptions are constitutionally dangerous because they allow later restore, migration, or operator work to treat absence, compression, or convenience as semantic fact.

## 6. Snapshot Relationship To Truth

Snapshots do not define truth. They capture bounded representations of authoritative or runtime-relevant state under explicit rules.

Truth in Dominium remains total, while materialization remains sparse. Snapshot doctrine must therefore preserve the following consequences:

- absence from a snapshot does not imply nonexistence of truth outside the capture boundary
- a lawful snapshot may be authoritative for a bounded horizon without becoming the whole ontology
- materialized capture does not outrank semantic law
- a snapshot cannot make unowned or projected state canonical by serialization alone

Snapshot doctrine must therefore preserve total-truth / sparse-materialization discipline rather than collapsing truth into whatever happened to be captured.

## 7. Snapshot Relationship To Replay

Snapshots and replay are distinct but complementary.

Replay doctrine governs lawful history semantics, ordered transitions, and replay-relevant verification. Snapshot doctrine governs lawful bounded capture semantics.

The binding consequences are:

- snapshots may assist replay
- snapshots may delimit replay cost or recovery work
- snapshots may provide lawful continuity anchors
- snapshots must not replace replay lineage when replay lineage is required
- replay may still be needed to interpret whether a snapshot is sufficient, complete, or lawful for a particular purpose

Equating snapshots with replay is forbidden. Replay is historical law; snapshots are bounded continuity captures.

## 8. Snapshot Relationship To State Externalization

Snapshot doctrine consumes state externalization law rather than replacing it.

This means:

- authoritative truth state remains domain-owned according to domain law
- lawful derived runtime-managed state may be snapshotted when doctrine permits
- transient execution state is not automatically snapshot-authoritative
- projected, presentation, or cache state must remain explicitly non-authoritative unless stronger law says otherwise
- hidden service-local truth is not a lawful snapshot source merely because it is easy to serialize

Snapshot doctrine therefore depends on the state classes already established in `STATE_EXTERNALIZATION.md`, and later snapshot machinery must preserve those distinctions rather than collapsing them into one storage format.

## 9. Snapshot Relationship To Lifecycle

Lifecycle law constrains when snapshots are lawful, partial, degraded, blocked, or invalid.

Snapshot legality must remain sensitive to whether the relevant runtime subject is:

- initialized but not yet available
- active
- quiescent
- suspended
- degraded
- blocked
- stopped
- failed
- retired

This matters because capture posture changes meaning. A snapshot taken during degraded, contested, failed, or partial lifecycle conditions may still be useful, but only if the degradation is explicit. Snapshot law must therefore preserve lifecycle posture rather than pretending every capture was equally fit for recovery or audit.

## 10. Snapshot Relationship To Bindings And Bridges

If a snapshot spans bound domain-service interactions, the snapshot must remain compatible with domain-service binding law.

If a snapshot spans cross-domain effects, bridge law remains binding. Snapshot semantics must not erase:

- which domains were involved
- which bridge categories governed the interaction
- which ownership checks were relevant
- whether a capture reflects local authority, mediated authority, or contested authority

A snapshot that hides bridge mediation or ownership transitions is not a lawful simplification. It is a semantic distortion.

## 11. Snapshot Relationship To Representation Ladders

Snapshots may lawfully exist at different representation scales or viewpoints, but representation ladders remain binding.

Snapshot law must therefore preserve:

- macro/micro continuity
- lawful substitution boundaries
- capsuled versus expanded posture where relevant
- objective versus subjective posture where relevant
- lineage from one representation layer to another

Snapshot serialization does not automatically make a subjective or projected view into objective truth. Likewise, finer granularity does not automatically outrank lawful macro representation.

Snapshot doctrine must remain representation-aware so that later recovery, audit, or operator reasoning does not silently rewrite meaning across representation steps.

## 12. Snapshot Relationship To Formalization And Provenance

Where a snapshot involves formalized artifacts, protocols, institutional lineage, or contract-significant state, provenance remains relevant.

Snapshot doctrine must preserve compatibility with:

- formalization lineage
- revision and supersession context
- contract or schema identity
- compatibility anchors
- later `Υ` provenance, versioning, release-index, and control-plane separation work

Snapshots must not silently erase revision context, institutional meaning, or provenance anchors when those anchors are necessary to determine whether later reuse, comparison, recovery, downgrade, or audit is lawful.

## 13. Snapshot Invalidity And Degradation

Not all snapshots are equally lawful for all purposes. Snapshot doctrine therefore recognizes explicit fitness and invalidity classes.

Possible postures include:

- complete
- partial
- degraded
- provisional
- projected-only
- stale
- ownership-invalid
- bridge-invalid
- lifecycle-invalid
- representation-lossy for claimed purpose
- provenance-incomplete
- unsafe-for-authoritative-restore

Later machinery must not assume that the mere existence of a snapshot implies lawful recovery, lawful comparison, or lawful replay substitution.

## 14. Verification And Auditability

Snapshot doctrine must support auditability and testability in principle.

Later systems should be able to verify:

- the snapshot class and declared scope
- authoritative versus derived versus projected contents
- lifecycle legality at capture time
- ownership legality
- bridge legality
- representation continuity
- provenance completeness where relevant
- compatibility with replay law

This doctrine therefore requires snapshot semantics to stay explicit enough for audit rather than disappearing into opaque file formats or backend behavior.

## 15. Ownership And Anti-Reinvention Cautions

The following cautions remain binding for snapshot doctrine:

- `fields/` is canonical semantic field substrate; `field/` remains a transitional compatibility facade
- `schema/` is canonical semantic contract law; `schemas/` remains a validator-facing projection or advisory mirror
- `packs/` is canonical in runtime packaging, activation, compatibility, and distribution-descriptor scope
- `data/packs/` remains authoritative within authored pack content and declaration scope, but stays transitional and residual-quarantined for attempted single-root convergence
- canonical versus projected/generated distinctions remain binding
- the thin `runtime/` root is not automatically canonical just because it is runtime-adjacent
- older planning numbering drift does not override the active checkpoint path

Snapshot law must be extracted from current doctrine and repo reality, not invented greenfield. Existing snapshot-adjacent repo surfaces are evidence to extend carefully, not permission to erase authority or ownership distinctions.

## 16. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- treating a save-file format as if it defines snapshot doctrine
- treating snapshots as the same thing as replay
- snapshot silently capturing projected/generated state as canonical truth
- using service-local hidden state as lawful snapshot authority
- treating a product or session save point as universal snapshot law
- treating a planning checkpoint as runtime snapshot law
- using a snapshot to erase bridge mediation or ownership transitions
- using a snapshot to rewrite macro/micro or objective/subjective meaning silently
- claiming authoritative restore fitness without lawful basis
- using snapshot convenience to replace replay lineage where replay lineage is required

## 17. Stability And Evolution

This artifact is `canonical` but `provisional`.

It is stable enough to guide downstream work, but it is expected to be refined explicitly by later prompts that consume it, especially:

- `Φ-B2` isolation and sandbox boundary work
- later `Φ-B3..Φ-B5` review work around multi-version coexistence, hotswap boundaries, and distributed authority
- `Υ` work involving provenance, versioning, release index, operator transaction records, archive behavior, and downgrade/recovery caution
- later `Ζ` work involving migration, restartless continuity, recovery, and live-ops discipline

Any update to this doctrine must remain:

- explicit
- auditable
- non-silent
- subordinate to semantic law, ownership review, bridge law, representation law, state law, lifecycle law, and replay law

Snapshot doctrine is therefore a continuity-support constitutional layer, not a shortcut around existing doctrine.
