# install_manifest.tlv (SR-3)

All integers are little-endian.

## File header
Fields (in order):
- `magic[4]` = `DSK1`
- `version_u16` = `1`
- `endian_u16` = `0xFFFE`
- `header_size_u32` = `20`
- `payload_size_u32`
- `header_crc_u32` (CRC32 of header with this field zeroed)

## Top-level TLVs
Tags are `u16` with `u32` length.

- `0x1001` `product_id` (string)
- `0x1002` `version` (string)
- `0x1003` `build_id` (string)
- `0x1004` `supported_targets` (container)
- `0x1005` `components` (container)
- `0x1006` `allowed_splats` (container, optional)
- `0x1007` `target_rules` (container, optional; reserved)

### supported_targets container
- `0x1101` `platform_entry` (string)

### allowed_splats container
- `0x1102` `allowed_splat_entry` (string)

### components container
- `0x1201` `component_entry` (container)

#### component_entry fields
- `0x1202` `component_id` (string)
- `0x1203` `kind` (string)
- `0x1204` `default_selected` (u8: 0/1)
- `0x1205` `deps` (container)
- `0x1206` `conflicts` (container)
- `0x1207` `artifacts` (container)

##### deps container
- `0x1210` `dep_entry` (string)

##### conflicts container
- `0x1211` `conflict_entry` (string)

##### artifacts container
- `0x1220` `artifact_entry` (container)

###### artifact_entry fields
- `0x1221` `hash` (string)
- `0x1222` `size` (u64)
- `0x1223` `path` (string)

## Canonical ordering
- `supported_targets` sorted by string.
- `allowed_splats` sorted by string.
- `components` sorted by `component_id`.
- `deps` and `conflicts` sorted by string.
- `artifacts` sorted by `path`, then `hash`.
