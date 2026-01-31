# Standards and Toolchains Baseline (STD0)

Status: binding for T23 baseline.  
Scope: standards, compatibility, and toolchains without new physics.

## What standards are in T23
- Data-defined agreements with versions and explicit scopes.
- Adoption, compliance, and enforcement are inspectable fields.
- Compatibility is explicit via policies and bridges.

All values are fixed-point and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## What exists
**Standard definitions**
- Namespaced identifiers, subject domains, and issuing institutions.
- Explicit references to current versions and compatibility policies.

**Standard versions**
- Version tags and compatibility scores.
- Adoption thresholds and release timing (symbolic).
- Status flags: active, deprecated, revoked.

**Standard scopes**
- Adoption rate and compliance rate (distinct).
- Lock-in index and enforcement level.
- Spatial and subject-domain scoping.

**Toolchains and meta-tools**
- Explicit graphs of tools that produce or validate other tools.
- Meta-tools consume energy and produce heat.
- Bias and error rates are explicit and inspectable.

**Resolution**
- Event-driven via propose/adopt/audit/enforce/revoke processes.
- Deterministic ordering and budget-bounded queries.
- No per-tick compatibility scans.

## What is NOT included yet
- No global default standards or automatic convergence.
- No irreversible standard mandates.
- No new physics or materials.
- No silent compatibility inference or hidden translations.

## Collapse/expand compatibility
Standards collapse stores:
- active standards per domain (invariant)
- adoption/compliance/lock-in distributions
- compatibility summaries

Expanded domains reconstruct deterministic microstates.

## Inspection and tooling
Inspection exposes:
- standards in force and their issuers
- compatibility relationships and bridges
- adoption/compliance status
- toolchain graphs and meta-tool metrics

Visualization is symbolic and never authoritative.

## Maturity labels
- Standard definitions: **BOUNDED** (explicit, auditable).
- Standard versions: **BOUNDED** (versioned, deterministic).
- Standard scopes: **BOUNDED** (adoption/compliance tracked).
- Toolchains/meta-tools: **BOUNDED** (graph-based, event-driven).

## See also
- `docs/architecture/STANDARDS_AND_META_SYSTEMS_MODEL.md`
- `docs/architecture/INFORMATION_MODEL.md`
- `docs/architecture/ENERGY_MODEL.md`
- `docs/architecture/THERMAL_MODEL.md`
