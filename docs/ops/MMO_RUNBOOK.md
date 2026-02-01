Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# MMO Runbook (MMO-2)

This runbook defines deterministic operational procedures for
checkpointing, crash recovery, and rolling updates.

All procedures MUST respect:

- commit-boundary rules,
- capability baselines,
- budget and refusal semantics.

## Checkpoint Operations

Allowed triggers:

- policy tick cadence,
- macro event stride,
- before ownership transfer,
- explicit manual checkpoint.

Operational guidance:

- Prefer policy-driven cadence.
- Use manual checkpoints before risky interventions.
- Treat checkpoint refusal as authoritative; do not force progress.

## Crash Recovery Procedure

Authoritative recovery requires:

- last committed checkpoint,
- capability lockfile reference,
- cross-shard log tail from checkpoint position.

Procedure:

1) load the checkpoint,
2) load the log tail,
3) replay deterministically,
4) resume.

If any required artifact is missing, run in frozen/inspect-only mode
and emit explicit refusals.

## Rolling Update Procedure

Safe rolling updates use checkpoint handoff:

1) checkpoint,
2) restart shard on new binary,
3) resync from checkpoint + log tail.

Mixed versions are allowed only with overlapping capabilities.

## Shard Lifecycle Controls

Lifecycle state changes MUST be:

- explicit,
- logged,
- commit-boundary only.

Use DRAINING before planned ownership handoffs.
Use FROZEN for inspect-only safety.

## Observability Checklist

At minimum, monitor:

- checkpoint cadence and refusals,
- lifecycle log growth,
- cross-shard log backlog,
- refusal codes over time,
- shard states and capability masks.