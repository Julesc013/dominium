Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Simulation Responsibility Zones (SRZ0)

Status: binding.
Scope: execution location, verification policy, and commit authority for deterministic simulation.

## Core invariant

> Simulation Responsibility Zones (SRZs) define who executes simulation,
> who verifies it, and how results are committed — never what is allowed.

SRZs govern execution location, verification policy, and authority scope.
SRZs do NOT change physics, law, epistemics, or capabilities.

## SRZ modes (exhaustive)

SRZs MUST use exactly one of these modes:

1) server
   - Server executes all processes.
   - Clients submit intents only.

2) delegated
   - Client executes processes.
   - Client submits ProcessLog, HashChain, and MacroCapsule summary.
   - Server verifies and commits.

3) dormant
   - No micro simulation.
   - Macro capsules evolve via event-driven rules.
   - Zero cost unless queried.

No other modes are permitted.

## Execution artifacts

Delegated execution MUST emit:
- ProcessLog (ordered, deterministic process list)
- HashChain (hash-linked proof of order, inputs, outputs, RNG usage)
- MacroCapsule (invariants and sufficient statistics)

StateDelta is optional and may be used as an optimization only.
No state may be committed without proof.

## Verification policies

Supported policies:
- strict_replay: server replays full ProcessLog
- spot_check: server replays deterministic segments
- invariant_only: server verifies invariants + macro capsule only

Verification MUST be deterministic, auditable, and refusal-explainable.

## Epistemic safety

SRZ execution MUST preserve epistemic constraints:
- Delegated clients receive only sensor-derived knowledge, communicated data,
  and historical memory.
- Verification MUST NOT inject hidden knowledge or correct beliefs.
- Misinformation and ignorance persist unless revealed by lawful processes.

## Escalation / deescalation

SRZs may define deterministic thresholds to change verification intensity
or mode at commit boundaries. Thresholds are expressed as ratios and must
be auditable and explainable.

## Uniformity across systems

All systems (physical, social, informational) MUST obey SRZ execution rules.
No system may bypass SRZ delegation or verification requirements.

## See also

- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md`
- `docs/architecture/EPISTEMICS_MODEL.md`
- `docs/architecture/EPISTEMICS_AND_SCALED_MMO.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `schema/srz.zone.schema`
- `schema/srz.assignment.schema`
- `schema/srz.policy.schema`
- `schema/process.log.schema`
- `schema/process.hashchain.schema`
- `schema/state.delta.schema`