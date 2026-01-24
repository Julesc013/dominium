# Mental Model

Status: canonical.
Scope: normative framing for the whole stack.
Authority: canonical. All other docs MUST defer to this file for the mental model.
Any change to this mental model SHALL be treated as an explicit breaking revision.

## Kernel framing
Dominium SHALL be treated as a deterministic simulation kernel. The kernel MUST
enforce invariants and execute authoritative state transitions. It MUST NOT
embed content or presentation behavior.

## Topology and scale
The system MUST model a scale-free topology. Topology nodes are the canonical
identities, and refinement MUST add detail without changing identity or
history.

## Processes and capabilities
All authoritative changes MUST occur via declared processes. Capabilities MUST
gate which processes may be attempted, and authority tokens MUST be explicit.

## Packs and external content
All content is external and optional via packs resolved by UPS. Executables MUST
remain content-agnostic and MUST boot with zero assets.

## Truth vs perception
Authoritative truth and derived perception MUST be distinct. Clients, renderers,
and platform layers MUST be non-authoritative and MUST NOT define truth.

## Costs and constraints
The ability to express a process does not imply it is free. Conservation,
causality, and law gates MUST constrain all authoritative changes.

## Realism boundary
Realism is a content concern. The engine MUST provide deterministic
abstractions, not domain realism guarantees.

## OS kernel analogy
The engine SHALL be treated as closer to an OS kernel than a traditional game
engine. It provides primitives and enforcement, not game behavior.

## References
- `docs/architecture/INVARIANTS.md`
- `docs/architecture/TERMINOLOGY.md`
- `docs/architecture/COMPATIBILITY_PHILOSOPHY.md`
