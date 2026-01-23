--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

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
# Content Specification (Proto Layer)

This layer defines data-only prototypes and manifests. The engine only sees IDs, tags, and opaque TLV blobs; all domain-specific strings live in pack/mod data, never in core code.

## Packs and Mods
- **Pack**: versioned content bundle resolved by UPS. Identified by numeric `id`
  + `version`. Location is determined by UPS/launcher; the content layer does no
  file I/O.
- **Mod**: extends packs with additional prototypes and metadata. Identified by
  numeric `id` + `version`; location is determined by UPS/launcher.
- Higher layers resolve packs and pass TLVs to `d_content_load_pack` /
  `d_content_load_mod`; the content layer performs no file I/O.

## Manifests
- `d_proto_pack_manifest`: `{ id, version, name, description, content_tlv }`.
- `d_proto_mod_manifest`: `{ id, version, name, description, deps_tlv, content_tlv }`.
- Dependency encoding is left to `deps_tlv` for extensibility; `name`/`description` are optional strings carried alongside the TLV blob.

## Proto Types and Schema IDs
- Schema ids (version 1 unless noted): materials `0x0101`, items `0x0102`, containers `0x0103`, processes `0x0104`, deposits `0x0105`, structures `0x0106`, vehicles `0x0107`, spline profiles `0x0108`, job templates `0x0109`, building protos `0x010A`, blueprints `0x010B`, pack `0x0201`, mod `0x0202`.
- Common fields: `id` (u32), `name` (string), `tags` (u32 bitmask). Type-specific extras live in TLV blobs (e.g., process `params`, structure `layout/io/processes`, building `shell`).
- Fixed-point values use Q16.16 encoded as signed 32-bit integers.

## Registries and IDs
- Each proto type has a capped `d_registry`; IDs come from the TLV payload (duplicates are rejected).
- Tag flags are generic (solid/fluid/organic/etc.) and never encode balance or domain lore.
- Lifecycle: `d_content_register_schemas` → `d_content_init` → repeated `d_content_load_pack/mod` → optional `d_content_debug_dump` for inspection → `d_content_reset`/`d_content_shutdown` when tearing down.

## Base Pack and compatibility rules
- Zero-pack boot is valid; no pack is required for executables to start.
- If a base pack is selected, it loads before instance-specified packs.
- Additional packs/mods extend via new IDs and tags rather than mutating
  existing meanings.
- Engine logic stays tag-driven and generic; gameplay semantics belong to data
  shipped in packs/mods.
