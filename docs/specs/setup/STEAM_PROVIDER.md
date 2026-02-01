Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Steam Provider Adapter (SR-7)

The Steam adapter is a thin provider that emits a Steam-owned request and invokes `dominium-setup`.

## Behavior
- `requested_splat_id = splat_steam`
- `ownership_preference = steam`
- `frontend_id = dominium-setup-steam` (overrideable)

## Usage
```
dominium-setup-steam request-make --manifest manifest.tlv --platform steam --out-request steam_request.tlv
dominium-setup-steam run --manifest manifest.tlv --out-plan steam_plan.tlv --out-state installed_state.tlv --out-audit setup_audit.tlv --out-journal job_journal.tlv --dry-run
```

Default outputs:
- `steam_request.tlv`
- `steam_plan.tlv`
- `installed_state.tlv`
- `setup_audit.tlv`
- `job_journal.tlv`

## Environment
- `STEAM_INSTALL_PATH` can be used as the default install root.
- Use `--platform <triple>` with `--use-fake-services` to set a deterministic target platform (default is `steam`).