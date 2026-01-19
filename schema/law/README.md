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
