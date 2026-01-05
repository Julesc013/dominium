# Launcher → Game Handshake (Game View)

This spec defines the launcher-owned handshake data consumed by the game. The
handshake is a versioned TLV container and MUST NOT contain absolute paths.

## 1. Required fields
- `instance_id` (string, logical)
- `run_id` (u64)
- `installed_state_id` or `installed_state_hash` (bytes/string; launcher-defined)
- `resolved_packs[]` (pack graph + hashes; ordered)
- `flags` (safe/offline/etc; launcher-defined)

## 2. Optional fields
- `run_root_ref` (PATH_REF): tagged logical ref (relative only). This is
  metadata and MUST NOT be treated as a physical root.
- `universe_id` (string, logical)
- `universe_bundle_hash` (`u64_le`, DTLV canonical content hash)
- `universe_bundle_ref` (PATH_REF): tagged logical ref for an instance-scoped
  bundle path (relative only).
- Additional launcher-defined metadata fields (skip-unknown).

## 3. Path rules
- Absolute filesystem paths are forbidden in all handshake fields.
- Any path references are `PATH_REF` with `base` (`RUN_ROOT` or `HOME`) and
  relative `rel` values only.
- Physical layout is defined by environment variables:
  - `DOMINIUM_RUN_ROOT` (preferred; writable root)
  - `DOMINIUM_HOME` (allowed; logical instance/content root)

## 4. Resolution behavior (game side)
- The game resolves all filesystem access via `DOMINIUM_RUN_ROOT` and/or
  `DOMINIUM_HOME` per `docs/SPEC_FS_CONTRACT.md`.
- Handshake path refs are validated as relative and used only as tagged,
  reproducible references; they do not introduce new absolute roots.
- Universe selection and bundle identity are validated per
  `docs/SPEC_UNIVERSE_BUNDLE.md`.

## Related specs
- `docs/SPEC_FS_CONTRACT.md`
- `docs/SPEC_UNIVERSE_BUNDLE.md`
