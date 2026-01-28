# ARCHIVED — OUTDATED

This document is archived and superseded by `docs/architecture/WHAT_THIS_IS_NOT.md`.
Reason: EG-H canon designates `docs/architecture/` as authoritative; this file may
conflict or duplicate canonical non-goals.
Status: archived for historical reference only.

# Non-Goals

Status: canonical.
Scope: explicit limits on what the system will NEVER attempt or guarantee.
Authority: canonical. All other docs MUST defer to this file for non-goals.

Each non-goal is binding and includes a rationale, an abstraction boundary, and
acceptable approximations. Any change to these non-goals SHALL be treated as an
explicit breaking revision.

## Physical fidelity exclusions
- The system MUST NOT simulate molecular-level chemistry beyond defined
  abstractions. Why: determinism and performance require bounded complexity.
  Boundary: only coarse material and reaction abstractions declared by content.
  Acceptable approximations: deterministic bulk properties and declared
  reactions.
- The system MUST NOT simulate quantum mechanics. Why: the core contract is
  deterministic and auditable. Boundary: only deterministic macro-scale
  abstractions are allowed. Acceptable approximations: deterministic physics
  models defined in content.
- The system MUST NOT provide perfect weather CFD at all scales. Why:
  deterministic and bounded-cost simulation is required. Boundary: weather is
  represented by coarse fields and rules. Acceptable approximations:
  deterministic climate and weather fields at defined resolution.

## Cognition exclusions
- The system MUST NOT simulate neuron-level human cognition. Why: the model
  must remain deterministic and computationally bounded. Boundary: agent
  behavior is defined by abstract, deterministic decision models. Acceptable
  approximations: deterministic agent state machines and policy rules.

## Precision and identity exclusions
- The system MUST NOT guarantee infinite spatial or temporal precision. Why:
  determinism requires fixed, declared precision. Boundary: space and time are
  represented at declared resolution. Acceptable approximations: fixed-point or
  quantized representations declared by policy.
- The system MUST NOT guarantee semantic identity across engine versions. Why:
  rules and schemas evolve under versioning and migration. Boundary: semantics
  are guaranteed only within declared compatibility contracts. Acceptable
  approximations: explicit migrations, refusals, or compatibility modes.

## Execution scope exclusions
- The system MUST NOT attempt step-everything or global-scan simulation. Why:
  bounded cost and determinism require event-driven work. Boundary: only
  explicitly scheduled processes run. Acceptable approximations: event-driven
  aggregation and refinement.
- The system MUST NOT fabricate existence or history. Why: provenance and audit
  must remain explicit. Boundary: existence and changes require declared
  processes. Acceptable approximations: explicit refinement and collapse with
  preserved provenance.

## Product scope exclusions
- The system MUST NOT embed content in executables. Why: content must remain
  external and optional. Boundary: executables contain mechanisms only.
  Acceptable approximations: pack-delivered content and assets.
- The system MUST NOT allow renderer, platform, client, or UI to be
  authoritative. Why: presentation and transport cannot define truth. Boundary:
  these components are derived and read-only. Acceptable approximations:
  read-only inspection and presentation layers.
