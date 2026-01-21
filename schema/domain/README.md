--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Runtime domain volume queries and deterministic SDF evaluation.
GAME:
- Domain rules, jurisdiction bindings, travel and refinement integration.
SCHEMA:
- Domain volume schemas and authoring formats (data-only).
TOOLS:
- Editors and validators for authoring inputs.
FORBIDDEN:
- No runtime logic in schema specs.
DEPENDENCIES:
- Engine -> none (schema only).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Domain Schema (DOMAIN0)

This folder defines the canonical spatial domain volume model used to decide
where simulation, travel, and refinement may occur.

See:
- `SPEC_DOMAIN_VOLUMES.md`
- `SPEC_DOMAIN_RUNTIME_SDF.md`
- `SPEC_DOMAIN_AUTHORING.md`
- `SPEC_DOMAIN_NESTING.md`
- `SPEC_REACHABILITY.md`
- `SPEC_VISITABILITY.md`
Law bindings and jurisdiction precedence:
- `schema/law/SPEC_DOMAIN_JURISDICTIONS.md`
- `schema/law/SPEC_JURISDICTION_PRECEDENCE.md`

Reality layer:
- `docs/arch/REALITY_LAYER.md`
- `docs/arch/SPACE_TIME_EXISTENCE.md`
- `docs/arch/VISITABILITY_AND_REFINEMENT.md`
