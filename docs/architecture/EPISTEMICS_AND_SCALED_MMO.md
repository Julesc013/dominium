# Epistemics and Scaled MMO (EPI-SCALE)

Status: binding.
Scope: preserving fog-of-war and misinformation under SRZ scaling.

## Core promise

> Scaling must not weaken epistemic constraints.
> Fog-of-war becomes stronger, never weaker, under delegation.

## Delegation and visibility

Delegated SRZs receive only:
- sensor-derived knowledge
- communicated information
- historical memory

They never receive:
- hidden actors
- unknown hazards
- future information

Verification MUST NOT inject or correct beliefs.

## SRZ boundaries

SRZ boundaries define execution responsibility, not information access.
SRZ reassignment must preserve epistemic boundaries and should not
retroactively expose truth.

## Misinformation persistence

Misinformation and ignorance persist unless corrected by lawful processes.
Server verification may refuse illegal outcomes but must not reveal why
if it would leak hidden state.

## Scaled execution

Sparse worlds:
- Many delegated SRZs
- Server cost scales with verification only

Dense worlds:
- Fewer server SRZs
- Shared simulation cost

In all cases, epistemic filtering is mandatory.

## See also

- `docs/architecture/SRZ_MODEL.md`
- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md`
- `docs/architecture/EPISTEMICS_MODEL.md`
- `docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md`
