# Lockfiles (LOCK0)

Status: binding.
Scope: deterministic capability resolution lockfiles.

## Purpose
Lockfiles make capability resolution deterministic across pack ordering.
They prevent "mod order roulette" and guarantee reproducible worlds.

## capabilities.lock
Format: JSON mapped to `schema/capability_lockfile.schema`.

Required fields:
- lock_id
- lock_format_version
- generated_by
- resolution_rules
- missing_mode
- resolutions[]
- extensions{}

Resolution entry:
- capability_id -> provider_pack_id@version

## Storage rules
- Stored with save or referenced by hash.
- No absolute paths inside lockfiles.
- Unknown fields MUST be preserved.

## Determinism rules
- Same save + different pack order => identical resolution.
- Missing capability => explicit refusal or frozen mode (never silent fallback).

## See also
- `schema/capability_lockfile.schema`
- `docs/arch/PACK_FORMAT.md`
