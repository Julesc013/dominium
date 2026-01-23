# Compatibility Enforcement

Compatibility checks are centralized in `dom_app_compat_check` and reused by
read-only adapter entrypoints and tools.

## Checked fields
- Build-info ABI and struct size (`dom_build_info_v1_get`)
- Engine version (`DOMINO_VERSION_STRING`)
- Game version (`DOMINIUM_GAME_VERSION`)
- Build id (`dom_build_id()`)
- Simulation schema id (`dom_sim_schema_id()`)
- Caps ABI (`DOM_CAPS_ABI_VERSION`)
- Gfx API protocol (`DGFX_PROTOCOL_VERSION`)

## Where enforced
- `dom_app_ro_open` (client observability and `tools inspect`)
- `tools validate`
- `--expect-*` flags on client/tools

## Failure behavior
- Non-zero exit from callers
- `compat_status=failed` and `compat_error=...` in reports
- No silent fallback
