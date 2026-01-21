--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (policy docs only).
GAME:
- Enforcement integrations and runtime usage (via tools/validation).
SCHEMA:
- Policy references only; no runtime logic here.
TOOLS:
- Validator tooling consumes policy references.
FORBIDDEN:
- No runtime logic in policy docs.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Schema Policy References

This folder anchors governance and enforcement references for schema policies.
See:
- `docs/policies/VALIDATION_AND_GOVERNANCE.md`
- `docs/ci/CI_ENFORCEMENT_MATRIX.md`
- `schema/SCHEMA_GOVERNANCE.md`

--------------------------------
EXEC0c LAW KERNEL SPECS
--------------------------------
This folder also defines the canonical law kernel schemas used by Work IR and
execution backends. See:
- `schema/law/SPEC_LAW_KERNEL.md`
- `schema/law/SPEC_LAW_SCOPES.md`
- `schema/law/SPEC_LAW_TARGETS.md`
- `schema/law/SPEC_LAW_EFFECTS.md`
- `schema/law/SPEC_DOMAIN_JURISDICTIONS.md`
- `schema/law/SPEC_JURISDICTION_PRECEDENCE.md`
- `docs/arch/LAW_ENFORCEMENT_POINTS.md`
