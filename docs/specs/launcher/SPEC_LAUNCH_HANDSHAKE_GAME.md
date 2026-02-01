Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `launcher/`.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Launcher → Game Handshake (Game View)

This spec defines the launcher-owned handshake data consumed by the game. The
handshake is a versioned TLV container and MUST NOT contain absolute paths.

## 1. Required fields
- `instance_id` (string, logical)
- `run_id` (u64)
- `installed_state_id` or `installed_state_hash` (bytes/string; launcher-defined)
- `resolved_packs[]` (pack graph + hashes; ordered)
- `flags` (safe/offline/etc; launcher-defined)
- `sim_caps` (TLV container; SIM_CAPS, versioned)

## 2. Optional fields
- `run_root_ref` (PATH_REF): tagged logical ref (relative only). This is
  metadata and MUST NOT be treated as a physical root.
- `universe_id` (string, logical)
- `universe_bundle_hash` (`u64_le`, DTLV canonical content hash)
- `universe_bundle_ref` (PATH_REF): tagged logical ref for an instance-scoped
  bundle path (relative only).
- `perf_caps` (TLV container; PERF_CAPS, negotiable)
- `provider_bindings_hash` (`u64_le`): digest of provider bindings; missing
  values are treated as `0` for legacy inputs.
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
  `DOMINIUM_HOME` per `docs/specs/SPEC_FS_CONTRACT.md`.
- Handshake path refs are validated as relative and used only as tagged,
  reproducible references; they do not introduce new absolute roots.
- Universe selection and bundle identity are validated per
  `docs/specs/SPEC_UNIVERSE_BUNDLE.md`.

## 5. Identity digest (sim-bound)
The handshake identity digest is computed from:
- SIM_CAPS (canonical TLV)
- content digests and sim-affecting flags
- provider bindings digest

PERF_CAPS and other presentation metadata MUST NOT influence the identity
digest.

## Related specs
- `docs/specs/SPEC_FS_CONTRACT.md`
- `docs/specs/SPEC_UNIVERSE_BUNDLE.md`
- `docs/specs/SPEC_TIERS.md`