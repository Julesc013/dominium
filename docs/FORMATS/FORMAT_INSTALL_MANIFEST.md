# Format — `dominium_install.json`

Install roots always contain this manifest. It is the single source of truth for install metadata and install mode.

```json
{
  "schema_version": 1,
  "install_id": "uuid",
  "install_type": "portable|per-user|system",
  "platform": "win_nt|linux|mac",
  "version": "1.0.0",
  "created_at": "2025-12-06T00:00:00Z",
  "created_by": "setup|portable-zip|package"
}
```

## Field semantics
- `schema_version` — integer schema version; parsers must reject unknown future versions with a clear error.
- `install_id` — UUID string unique per install root.
- `install_type` — one of `portable`, `per-user`, `system`.
- `platform` — normalized platform string: `win_nt`, `linux`, `mac`.
- `version` — Dominium semantic version (launcher/setup/game release).
- `created_at` — ISO-8601 timestamp (UTC) of manifest creation.
- `created_by` — producer identifier (`setup` when written by `dom_setup`; `portable-zip` when shipped pre-zipped; `package` for OS-level packages).

## Rules and behavior
- The manifest lives at `INSTALL_ROOT/dominium_install.json`.
- Missing or corrupted manifests must cause a clear error in both launcher and setup flows.
- Installers/repairers may rewrite `created_by` but must never change `install_id` unless creating a brand-new install.
- Launchers and setup tools must use `schema_version` to allow forward-compatible upgrades.
