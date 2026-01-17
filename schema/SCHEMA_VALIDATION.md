# Schema Validation Law (DATA0)

All schema-bound data MUST pass validation at authoring time, load time, and merge time.
Validation outcomes are enforceable and merge-blocking when required.

## Validation Layers (Mandatory)

### Structural Validation

- Field presence, types, ranges, and cardinality.
- Required/optional fields enforced by schema.
- Unknown fields preserved and reported.

### Semantic Validation

- Invariants, constraints, and cross-field rules.
- Referential integrity (stable IDs, foreign keys).
- Domain-specific invariants required by simulation.

### Performance Validation

- No unbounded lists or maps in authoritative data.
- Required LOD/fidelity ladders are present where applicable.
- Budget-related fields must fall within defined caps.

### Determinism Validation

- No forbidden constructs (nondeterministic time, RNG, floats) in authoritative data.
- Ordering keys and tie-breakers must be present where required.
- Skip-unknown preserved and round-trippable.

## Validation Outcomes

Validators MUST return exactly one of:

- `ACCEPT`: valid and safe to load.
- `ACCEPT_WITH_WARNINGS`: valid but non-blocking issues exist.
- `REFUSE`: invalid or unsafe; MUST NOT load or merge.

`REFUSE` is mandatory for determinism or performance violations.

## Integration Points

- Tools: validate on authoring/export; warnings are surfaced immediately.
- Runtime: validate on load; `REFUSE` blocks session start or asset load.
- CI: validate on merge; violations block merge.

## Prohibitions

- Loading authoritative data that fails validation.
- Skipping validation for performance reasons.
- Allowing warnings to bypass determinism or performance rules.
