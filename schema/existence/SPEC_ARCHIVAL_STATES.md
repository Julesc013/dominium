# SPEC_ARCHIVAL_STATES (EXIST2)

Schema ID: ARCHIVAL_STATES
Schema Version: 1.0.0
Status: binding.
Scope: archival-related states orthogonal to existence.

## Purpose
Define explicit archival states so freezing, preservation, and forking are
auditable and never implicit.

## Orthogonality
Archival state is orthogonal to existence state (EXIST0):
- An entity can be REALIZED + LIVE.
- An entity can be LATENT + ARCHIVED.
- An entity can be DECLARED + FROZEN (contract-only).

## Canonical Archival States
### LIVE
- Subject participates in simulation.
- State may change via explicit effects.

### FROZEN
- Subject state immutable.
- Simulation does not advance locally.
- Read-only inspection allowed (subject to epistemic law).

### ARCHIVED
- Persisted snapshot with provenance.
- No simulation or mutation.
- May be replayed or forked.

### FORKED
- New timeline created from ARCHIVED or FROZEN state.
- Original remains unchanged and immutable.
- Forked subject carries parent provenance pointer.

## Invariants (Absolute)
- Archival states must be explicit and auditable.
- No implicit transitions or silent edits.
- Freezing and archiving must not corrupt provenance.

## Integration Points
- Law kernel: transitions are law-gated.
- Work IR: transitions are explicit effects.
- Sharding: ownership respects archival state.
- Tools: inspection allowed; mutation requires explicit effect.

## References
- `schema/existence/SPEC_FREEZE_SEMANTICS.md`
- `schema/existence/SPEC_FORKING_RULES.md`
