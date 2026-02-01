Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Epistemics Model (EPI0)

Status: binding.
Scope: knowledge, uncertainty, and visibility constraints in authoritative simulation.

## Core invariant

> Knowledge is derived from measurement, communication, and memory.
> Ignorance and misinformation are first-class and persistent.

Epistemic constraints apply to all agents, tools, and servers.
No system is omniscient by default.

## Epistemic sources

Allowed knowledge sources:
- sensor-derived measurements
- communicated information (signals, reports, logs)
- historical memory (replay-derived artifacts)

Disallowed sources:
- hidden or future state
- omniscient queries
- authoritative "truth leaks" without lawful process

## Epistemic states

All fields and observations may be:
- known (exact or bounded)
- unknown (latent)
- contradictory (multiple competing claims)

Epistemic state must be preserved through collapse/expand.

## Authority and epistemics

Authority does not grant omniscience.
Verification checks legality and provenance only; it must not inject truth.

## Enforcement

Epistemic violations are refusals, not silent corrections.
Refusal reasons MUST reference canonical refusal semantics.

## See also

- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/EPISTEMICS_AND_SCALED_MMO.md`
- `docs/architecture/UNKNOWN_UNKNOWNS.md`