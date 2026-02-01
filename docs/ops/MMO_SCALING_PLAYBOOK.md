Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# MMO Scaling Playbook (OPS-SRZ)

Status: EVOLVING.
Scope: operational guidance for SRZ scaling and verification load.

## Objectives

- Keep outcomes deterministic and replayable.
- Scale server cost with verification, not full simulation.
- Preserve epistemic constraints at all times.

## Monitoring signals

- SRZ mode distribution (server/delegated/dormant)
- Verification failure rate per SRZ
- Verification backlog and budget pressure
- Escalation/deescalation counts per commit window

## Scaling actions

### Sparse worlds (many isolated players)
- Prefer delegated SRZs with spot_check verification.
- Escalate to strict_replay when failure rate exceeds policy threshold.
- Keep dormant SRZs collapsed unless queried.

### Dense worlds (many co-located players)
- Consolidate into server SRZs for shared simulation.
- Use strict_replay by default during high contention.
- Deescalate only after sustained clean windows.

## Escalation rules

- Escalation and deescalation occur at commit boundaries only.
- Thresholds are deterministic and audited.
- Changes must emit explicit reasons.

## Epistemic safety checklist

- Delegated SRZs receive only sensor + communication views.
- Verification never injects hidden truth.
- Refusals do not leak unseen state.

## Failure response

- On repeated verification failures: escalate SRZ and increase strict_replay.
- On proof malformation: revoke delegation and quarantine logs.
- On client abuse: enforce law/meta-law and issue refusal reasons.

## Do not

- Do not trust client results without verification.
- Do not use wall-clock time in authoritative logic.
- Do not change execution mode mid-tick.

## References

- `docs/architecture/SRZ_MODEL.md`
- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md`
- `docs/architecture/EPISTEMICS_AND_SCALED_MMO.md`