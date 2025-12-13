# Base Pack Example (TLV sketch)

Location on disk (relative to `DOMINIUM_HOME`): `repo/packs/base/00000001/pack.tlv`. The file is a flat list of TLV records; each record uses the schema id listed below and a payload of field TLVs (tags from `d_content_schema.h`). Unknown records are ignored by the loader.

## Materials
- Material 1
  - schema: `D_TLV_SCHEMA_MATERIAL_V1` (0x0101)
  - fields: `id=1`, `name="Generic Solid"`, `tags=D_TAG_MATERIAL_SOLID`, `density=1.0`, `hardness=0.5`, `melting_point=1.0` (Q16.16)
- Material 2
  - `id=2`, `name="Generic Fluid"`, `tags=D_TAG_MATERIAL_FLUID`, `density=1.0`, `hardness=0.0`, `melting_point=0.0`

## Item
- schema: `D_TLV_SCHEMA_ITEM_V1` (0x0102)
- `id=1`, `name="Debug Item"`, `material_id=1`, `tags=D_TAG_ITEM_BULK`, `unit_mass=1.0`, `unit_volume=1.0`

## Container
- schema: `D_TLV_SCHEMA_CONTAINER_V1` (0x0103)
- `id=1`, `name="Debug Container"`, `tags=D_TAG_CONTAINER_BULK`, `max_volume=100.0`, `max_mass=100.0`, `slot_count=0`

## Process (optional smoke test)
- schema: `D_TLV_SCHEMA_PROCESS_V1` (0x0104)
- `id=1`, `name="Debug Pass-through"`, `tags=D_TAG_PROCESS_CRAFT`, `params` = empty TLV blob

## Structure
- schema: `D_TLV_SCHEMA_STRUCTURE_V1` (0x0106)
- `id=1`, `name="Debug Marker"`, `tags=D_TAG_STRUCTURE_BUILDING`, `layout` empty TLV, `io` empty TLV, `processes` empty TLV

## Notes
- All numeric fields are little-endian. Strings should be UTF-8 and zero-terminated inside the TLV payload.
- Values use Q16.16 fixed-point encoding when noted above.
- Packs/mods add new prototypes by appending more TLV records; they must not redefine the meaning of an existing `id`.
