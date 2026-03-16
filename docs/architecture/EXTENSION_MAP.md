Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, and `AGENTS.md`.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Extension Map (5-10 Year Horizon)

## A) Safe Extension Points

1. New domain packs:
   - Add pack manifest + registry contributions.
   - Validate through domain/contract registries and RepoX/TestX.
2. New solver implementations:
   - Bind solver to `domain_ids` and `contract_ids`.
   - Declare transition support and refusal codes.
3. New UI packs:
   - Descriptor-only window contributions through `ui.registry`.
   - UI action routing remains intent/process only.
4. New worldgen modules:
   - Register module outputs and constraint bindings.
   - Keep deterministic ordering and seed discipline.
5. New profiles (`ExperienceProfile`, `LawProfile`, `ParameterBundle`):
   - Data-driven profile additions only; no mode flags.
6. New streaming hints:
   - Non-semantic hints may be added as policy/registry data.
7. New CI lanes:
   - Add lane configs without bypassing strict verification gates.
8. New tools:
   - Allowed under `tools/*` with canonical docs and invariants.

## B) Guarded Extension Points

1. New primitives:
   - Forbidden without explicit canon unlock.
2. Schema evolution:
   - CompatX migration/refusal path required.
3. Save format evolution:
   - Explicit migration contracts and compatibility policy required.
4. Contract changes:
   - `domain_contract` version bump + migration plan required.
5. Solver transition model changes:
   - Must preserve declared contracts and deterministic replay envelope.

## C) Explicitly Deferred

1. Embodiment system.
2. Full GR-grade physics integration.
3. Multiplayer authority sharding/network transport.
4. Economic macro systems at runtime scale.
5. Narrative/campaign engine.

## D) Invariant Enforcement Map

1. Domain packs:
   - RepoX: `INV-DOMAIN-REGISTRY-VALID`, `INV-SOLVER-DOMAIN-BINDING`
   - TestX: domain registry/binding suites
   - AuditX: schema usage + drift analyzers
2. Solver extensions:
   - RepoX: contract id stability + no hardcoded domain/contract literals
   - TestX: contract violation refusal tests
   - AuditX: ownership/schema analyzers
3. UI packs:
   - RepoX: UI command graph and truth-boundary checks
   - TestX: descriptor validation and action determinism tests
   - AuditX: UI bypass analyzer
4. Worldgen modules:
   - RepoX: constraint schema + deterministic seed policy invariants
   - TestX: search plan determinism tests
   - AuditX: constraint drift/seed-policy analyzers
5. Profiles/policies:
   - RepoX: no mode flags, session pipeline invariants
   - TestX: session creation/boot/lockfile determinism suites
   - AuditX: canon drift and artifact freshness analyzers

## Cross-References

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/session_lifecycle.md`
- `docs/architecture/registry_compile.md`
- `docs/architecture/hash_anchors.md`
- `docs/governance/AUDITX_MODEL.md`
