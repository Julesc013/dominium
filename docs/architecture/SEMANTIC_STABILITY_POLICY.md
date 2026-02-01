Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Semantic Stability Policy (STAB0)





Status: binding.


Scope: immutable semantics for identifiers, contracts, and persistent formats.





## Purpose


Preserve meaning over time. Once semantics are released, they must never drift.


Evolution is allowed only through explicit versioning, transforms, and refusal.





## Immutable Semantics (once released)


The following meanings are immutable:


- Field meaning (what a field represents and how to interpret it)


- Process input/output meaning (what a process consumes/produces)


- Capability meaning (what action or access a capability allows)


- Authority semantics (how authority gates actions)


- Refusal code meaning (why a refusal occurred)


- Chunk type meaning (what a serialized chunk represents)





## Mutable Aspects (allowed)


The following may change without altering semantics:


- Implementations


- Performance optimizations


- Compression or encoding details


- UI labels and presentation text


- Metrics collection and reporting





## Allowed Evolution Mechanisms


- New versioned artifacts (new schema_id, new chunk_type, new capability_id)


- Additive schemas only (skip-unknown, extension-preserving)


- Transform-only pipelines (derived outputs, non-authoritative)


- Frozen/degraded compatibility modes (explicit, deterministic)





## Explicit Prohibitions (immutable contracts)


- Reusing identifiers with new meaning


- Silent reinterpretation of old data


- Retroactive changes to released semantics without versioning


- Deleting required fields without a major version bump





## Semantic Anchor Registry (locked)


Immutable meanings are locked in:


`docs/architecture/SEMANTIC_STABILITY_LOCK.json`





Rules:


- Entries are append-only.


- Existing entries MUST NOT change.


- If meaning must change, create a new identifier and deprecate the old.





## Enforcement


- TestX: semantic stability lock checks.


- Change protocol: `docs/architecture/CHANGE_PROTOCOL.md`.


- Schema versioning: `schema/SCHEMA_VERSIONING.md`.





## See also


- `docs/architecture/INVARIANTS.md`


- `docs/architecture/REFUSAL_AND_EXPLANATION_MODEL.md`


- `docs/architecture/EXTEND_VS_CREATE.md`
