--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Collects SysCaps and exposes APIs (engine/modules/sys).
GAME:
- Consumes SysCaps via execution policy selection (non-authoritative).
SCHEMA:
- Defines SysCaps fields and platform profile schemas.
TOOLS:
- Validation and inspection tooling for SysCaps data.
FORBIDDEN:
- No runtime logic or benchmarking in schema docs.
DEPENDENCIES:
- Engine -> engine public API only.
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SysCaps Schema (HWCAPS0)

This folder defines the SysCaps descriptor and platform profile schema used
for deterministic execution policy selection.

Scope: SysCaps fields and platform profile formats.

## Invariants
- SysCaps are conservative signals, not benchmarks.
- Unknown values are treated conservatively.
- Schemas do not encode runtime logic.

## Forbidden assumptions
- SysCaps can be inferred from wall-clock timing.
- Unknown hardware implies availability.

## Dependencies
- `docs/architecture/SYS_CAPS_AND_EXEC_POLICY.md`
- `docs/architecture/EXECUTION_MODEL.md`

See:
- `SPEC_SYS_CAPS.md`
- `SPEC_SYS_CAPS_FIELDS.md`
- `SPEC_PLATFORM_PROFILES.md`

## See also
- `docs/architecture/HARDWARE_EVOLUTION_STRATEGY.md`
