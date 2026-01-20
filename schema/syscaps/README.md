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

See:
- `SPEC_SYS_CAPS.md`
- `SPEC_SYS_CAPS_FIELDS.md`
- `SPEC_PLATFORM_PROFILES.md`
