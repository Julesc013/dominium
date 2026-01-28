# Legacy Compatibility (SHIP-0)

Status: binding.
Scope: behavior when older binaries or installs encounter newer packs/saves.

## Compatibility Modes
Legacy compatibility must be explicit and deterministic. The system uses three
non-exclusive modes:

Degraded mode:
- Runs with reduced capabilities.
- Non-essential features are disabled.
- Missing capabilities produce warnings or refusals, not silent substitution.

Frozen mode:
- World loads read-only or paused until required packs are present.
- No authoritative state changes are allowed.

Transform-only mode:
- Allows data migration or conversion without executing simulation.
- Deterministic transforms only; no side effects.

## Pack and Save Interactions
When a legacy binary encounters a pack or save requiring newer formats:
- The launcher or tool must report incompatibility.
- Behavior must be deterministic and refusal-based.
- No automatic downgrade or silent data loss is allowed.

## Refusal Semantics
Refusals use canonical codes from `docs/architecture/REFUSAL_SEMANTICS.md`.
Recommended mappings:
- Unsupported pack or lockfile format: REFUSE_INTEGRITY_VIOLATION.
- Missing required capability: REFUSE_CAPABILITY_MISSING.
- Forbidden by policy or law: REFUSE_LAW_FORBIDDEN.
- Invalid request or malformed data: REFUSE_INVALID_INTENT.

## Legacy SKU Expectations
Legacy distributions must:
- Boot without packs.
- Inspect packs and report compatibility before load.
- Decline execution when required capabilities are absent.

