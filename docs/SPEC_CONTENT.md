# Content Specification (Proto Layer)

This layer defines data-only prototypes for all gameplay content: materials, items, structures, vehicles, blueprints, and the manifests that wrap them. No simulation, rendering, or UI behavior is implemented here; higher layers interpret these protos via model families and subsystem logic.

## Packs and Mods
- **Pack**: a self-contained bundle of content protos and assets. Identified by `pack_id` + `pack_version`. Dependencies on other packs are declared via `d_content_dep`.
- **Mod**: extends a pack with additional metadata and optional scripting. Identified by `mod_id` + `mod_version`. A mod embeds or references a base pack TLV and may provide `extra_tlv` for future scripting/model hooks.
- Both are supplied to the engine as already-loaded TLV blobs; file I/O is handled by launcher/setup/game code.

## Manifests
- `d_proto_pack_manifest`: fields `pack_id`, `pack_version`, `title`, `author`, `flags`, `deps[16]`, and `content_tlv` (root TLV containing all proto sections).
- `d_proto_mod_manifest`: fields `mod_id`, `mod_version`, `title`, `author`, `flags`, `deps[16]`, `base_pack_tlv` (embedded pack content) and `extra_tlv` (mod-only metadata).
- Dependencies are inclusive ranges (`min_version`, `max_version`, zero meaning “no bound”).

## Proto Types and IDs
Each proto has a TLV schema id (version 1 unless otherwise noted):
- Materials (`D_TLV_SCHEMA_MATERIAL` = 0x0200)
- Items (`D_TLV_SCHEMA_ITEM` = 0x0201)
- Containers (`D_TLV_SCHEMA_CONTAINER` = 0x0202)
- Processes (`D_TLV_SCHEMA_PROCESS` = 0x0203)
- Deposits (`D_TLV_SCHEMA_DEPOSIT` = 0x0204)
- Structures/machines (`D_TLV_SCHEMA_STRUCTURE` = 0x0205)
- Modules (`D_TLV_SCHEMA_MODULE` = 0x0206)
- Vehicles (`D_TLV_SCHEMA_VEHICLE` = 0x0207)
- Spline profiles (`D_TLV_SCHEMA_SPLINE_PROFILE` = 0x0208)
- Job templates (`D_TLV_SCHEMA_JOB_TEMPLATE` = 0x0209)
- Building protos (`D_TLV_SCHEMA_BUILDING_PROTO` = 0x020A)
- Blueprints (`D_TLV_SCHEMA_BLUEPRINT` = 0x020B)
- Pack manifest (`D_TLV_SCHEMA_PACK_MANIFEST` = 0x0100) and mod manifest (`D_TLV_SCHEMA_MOD_MANIFEST` = 0x0101) schemas gate the wrapper blobs.

## Registries and IDs
- Each proto type has its own `d_registry` instance with a fixed upper bound (materials, items, containers, processes, deposits, structures, modules, vehicles, spline profiles, job templates, building protos).
- IDs are assigned at load time and stored in the proto’s `id` field. Consumers use IDs for cross-references; subsystems never store raw pointers to foreign registries.
- `d_content_init`/`d_content_shutdown` manage these registries; loaders populate them from validated TLVs.

## Blueprint Core
- `d_blueprint`: holds `id`, `kind_id`, `version`, and a payload TLV.
- `dblueprint_kind_vtable`: per-kind validate/compile callbacks.
- Built-in kinds: `building`, `vehicle`, `weapon`, `subassembly/module`, `spline_profile`, `machine_config`. Validators currently accept any payload; compilers are stubs that will later populate engine protos via `d_content`.

## Notes and Non-goals
- All structures are deterministic and C89-only. No platform headers or OS drawing APIs are used here.
- Behavior lives in model families (`D_MODEL_FAMILY_*`) and subsystem logic in later layers. This pass only defines schemas, data containers, registries, and minimal TLV loaders/validators.
- Launcher/setup never touch schema internals: they hand validated TLV blobs from `dom_packset` straight into `d_content_load_pack` / `d_content_load_mod`. Forward/backward compatibility is enforced by TLV schema ids and dependency ranges, keeping Dominium products decoupled from content format evolution.
