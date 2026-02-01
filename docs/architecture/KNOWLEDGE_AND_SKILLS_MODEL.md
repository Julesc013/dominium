Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Knowledge and Skills Model (KNS0)

Status: binding.  
Scope: knowledge artifacts, skill profiles, education programs, and learning processes.

## Core invariant
**Knowledge is reduced uncertainty about the outcome of processes; skill is reduced
variance in execution.**

Knowledge is not:
- power
- permission
- a tech unlock

## Primitives (authoritative)
Knowledge and skill are represented via these data primitives:
- **Knowledge artifacts** (`schema/knowledge.artifact.schema`)  
  Claims, evidence, confidence, and uncertainty envelopes.
- **Skill profiles** (`schema/skill.profile.schema`)  
  Variance and failure-bias reduction for process execution.
- **Education programs** (`schema/education.program.schema`)  
  Structured training with time/energy/resource costs and outputs.

All numeric values are fixed-point in authoritative logic and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Process-only mutation
Knowledge and skills change only via processes:
- `process.learn.practice`
- `process.learn.study`
- `process.learn.train`
- `process.learn.certify`

There is no per-tick learning simulation. Learning occurs only when events run.

## Uncertainty & variance propagation
Process outcomes are shaped by:
- input uncertainty (M0-LITE epistemics)
- operator skill variance and failure bias

Higher uncertainty expands outcome distributions; higher skill narrows them.
Propagation is deterministic and fully inspectable.

## Education programs
Education programs are data-defined and constrained by:
- duration (time)
- energy and resource costs
- instructor availability
- accreditation (optional)

Programs never grant instant mastery and do not override law or trust.

## Institutional knowledge
Institutions can store, transmit, or suppress knowledge artifacts. Knowledge can:
- decay without maintenance
- be corrupted or falsified
- be gated by accreditation

There is no omniscient truth source; evidence and audits drive corrections.

## Collapse/expand compatibility
Collapse stores macro capsule stats:
- knowledge coverage per domain (invariant)
- confidence and skill distributions (sufficient statistics)
- RNG cursor continuity if configured

Expand reconstructs deterministic microstate consistent with capsule stats.

## Law & refusal semantics
Learning processes must obey law/meta-law and capability boundaries. Refusals
must explain missing permission, instructors, resources, or accreditation.

Refusal semantics are governed by `docs/architecture/REFUSAL_SEMANTICS.md`.

## Non-goals (KNS0)
- No XP, levels, or tech trees.
- No per-tick learning simulation.
- No instant mastery or hidden skill meters.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/SCALING_MODEL.md`