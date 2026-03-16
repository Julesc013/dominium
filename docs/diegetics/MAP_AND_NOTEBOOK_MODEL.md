Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Map And Notebook Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: Canon-Consistent (ED-2 baseline)  
Version: 1.0.0  
Last Updated: 2026-02-16

## Local Map (`instr.map_local`)

### Non-Omniscient Constraint
`map_local` is derived from observed memory only. Undiscovered regions and unobserved truth fields are never synthesized.

### Inputs
1. `Perceived.now` navigation channels.
2. `Perceived.memory` region/spatial entries.
3. Current viewpoint/camera position (already perception-filtered).

### Output Channel
- `ch.diegetic.map_local`

### Data Shape (conceptual)
1. `region_key` or `tile_key`
2. `discovered` bool
3. `confidence` (deterministic bounded integer)
4. `last_seen_tick`
5. Optional observed class tags (terrain/site stubs)

### Determinism
1. Stable sort by `(region_key, last_seen_tick)`.
2. Capacity bounded by policy.
3. Eviction uses deterministic rule from epistemic retention policy.

## Notebook (`instr.notebook`)

### Role
Notebook is a deterministic subjective log. It does not alter simulation truth.

### Inputs
1. Selected observed events from memory:
   - sightings
   - landmarks
   - received messages
2. Optional user-authored notes through explicit command.

### Command Path
- `diegetic.notebook.add_note`

### Entitlement Gate
- `entitlement.diegetic.notebook_write`

### Output Channel
- `ch.diegetic.notebook`

### Determinism
1. Entries are ordered by `(created_tick, author_subject_id, message_id)`.
2. Notes are bounded and schema-validated.
3. No wall-clock timestamps.

## Security / Epistemics
1. Map and notebook can only contain channels allowed by active epistemic policy.
2. Forbidden channels are rejected or redacted before persistence.
