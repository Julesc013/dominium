# Standards and Meta-Systems Model (STD0)

Status: binding.  
Scope: standards, toolchains, and meta-tools as deterministic, data-defined constraints.

## Core invariant
**Standards are voluntary, enforceable agreements that constrain how processes,
assemblies, and information are interpreted and exchanged.**

Standards are not:
- global defaults
- universally adopted
- immutable
- purely technical

## Authoritative primitives
Standards and meta-systems are represented through five data primitives:
- **Standard definitions** (`schema/standard.definition.schema`)
- **Standard versions** (`schema/standard.version.schema`)
- **Standard scopes** (`schema/standard.scope.schema`)
- **Toolchain graphs** (`schema/toolchain.graph.schema`)
- **Meta-tools** (`schema/meta.tool.schema`)

All numeric values are fixed-point in authoritative logic and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Process-only mutation
Standards only change through Processes. Canonical process families (data-defined) include:
- `org.dominium.process.standard.propose`
- `org.dominium.process.standard.adopt`
- `org.dominium.process.standard.audit`
- `org.dominium.process.standard.enforce`
- `org.dominium.process.standard.revoke`

No per-tick standard recomputation or hidden compatibility inference is allowed.

## Adoption, compliance, and enforcement
- Adoption depends on trust (T17), legitimacy (T19), and incentives (T20).
- Compliance is auditable and may diverge from adoption.
- Enforcement is explicit and may be refused for legal or capacity reasons.

Refusals must follow `docs/architecture/REFUSAL_SEMANTICS.md`.

## Toolchains and meta-tools
Meta-tools (compilers, CAD, validators, certifiers) are assemblies that:
- consume energy (T11) and produce heat (T12),
- embed assumptions and bias,
- emit explicit information artifacts (T14).

Toolchains are explicit graphs; compatibility must be declared, never implied.

## Compatibility, lock-in, and fragmentation
- Compatibility is expressed via version policies and explicit bridges.
- Lock-in is a measurable outcome of adoption + tooling + enforcement.
- Fragmentation emerges from incompatible standards and split adoption.

Compatibility resolution is explicit and inspectable; no silent translations exist.

## Collapse/expand compatibility
Macro capsules store:
- active standards per domain (invariant)
- adoption/compliance distributions
- compatibility summaries
- RNG cursor continuity (if used)

Expanded domains reconstruct deterministic microstates consistent with capsules.

## Save/load/replay
- Standards, scopes, toolchains, and events are saved as data + processes.
- No cached compatibility results are persisted.
- Replays reproduce adoption and enforcement deterministically.

## Non-goals (STD0)
- No global default standard.
- No irreversible global rule changes.
- No new physics or material primitives.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/architecture/UNIT_SYSTEM_POLICY.md`
