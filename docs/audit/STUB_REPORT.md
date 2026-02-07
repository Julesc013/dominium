Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# Stub Detection & Classification

Source: `docs/audit/MARKER_SCAN.txt`

## Classification Rules

- Acceptable permanent stub: non-authoritative placeholder with explicit
  refusal semantics or quarantined legacy code.
- Temporary stub requiring completion: scaffolding in active products that
  should be replaced with real implementation under a scoped prompt.
- Forbidden stub: authoritative runtime mutation path that silently no-ops.

## Acceptable permanent stubs (non-authoritative or quarantined)

- `legacy/**` stubs (archived/quarantined legacy sources).
- `game/tests/**` stubs (test scaffolding only).
- `game/rules/*/*_stub.*` (explicit refusal paths; see `docs/audit/BR0_STUB_RESOLUTION.md`).
- `engine/render/stub/*` and `engine/render/d_gfx_caps_stub.c` (null render backend).
- UI backend placeholders:
  - `libs/ui_backends/win32/src/*_stub.c`
  - `tools/ui_shared/src/dui_gtk.c`
  - `tools/ui_shared/src/dui_macos.c`

## Temporary stubs requiring completion (active products)

- Launcher scaffolding:
  - `launcher/core/*_stub.c`
  - `launcher/gui/*_stub.c`
  - `launcher/tui/*_stub.c`
- Setup scaffolding:
  - `setup/gui/*_stub.c`
  - `setup/tui/*_stub.c`
- Tool scaffolding:
  - `tools/coredata_*_stub.c`
  - `tools/_shared/tools_shared_stub.c`
- Platform system stubs (ensure supported OS does not bind to stub module):
  - `engine/modules/system/dsys_*_stub.c`

## Forbidden stubs

None detected in authoritative runtime. Explicit refusal behavior now covers
previously forbidden rule stubs.

## Notes

Any promotion of temporary stubs to production must be done via scoped prompts
and must preserve refusal semantics until replaced.
