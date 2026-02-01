Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# install_manifest.tlv (SR-4)

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
- `0x1008` `layout_templates` (container)
- `0x1009` `uninstall_rules` (container, optional; reserved)
- `0x100A` `repair_rules` (container, optional; reserved)
- `0x100B` `migration_rules` (container, optional; reserved)
- `0x100C` `splat_overrides` (container, optional; reserved)

### supported_targets container
- `0x1101` `platform_entry` (string)

### allowed_splats container
- `0x1102` `allowed_splat_entry` (string)

### components container
- `0x1201` `component_entry` (container)

#### component_entry fields
- `0x1202` `component_id` (string)
- `0x1208` `component_version` (string, optional)
- `0x1203` `kind` (string)
- `0x1204` `default_selected` (u8: 0/1)
- `0x1205` `deps` (container)
- `0x1206` `conflicts` (container)
- `0x1207` `artifacts` (container)
- `0x1209` `supported_targets` (container, optional)

##### deps container
- `0x1210` `dep_entry` (string)

##### conflicts container
- `0x1211` `conflict_entry` (string)

##### supported_targets container
- `0x1212` `component_target_entry` (string)

##### artifacts container
- `0x1220` `artifact_entry` (container)

###### artifact_entry fields
- `0x1224` `artifact_id` (string)
- `0x1221` `hash` (string, optional)
- `0x1226` `digest64` (u64)
- `0x1222` `size` (u64)
- `0x1225` `source_path` (string)
- `0x1227` `layout_template_id` (string)

### layout_templates container
- `0x1301` `layout_template_entry` (container)

#### layout_template_entry fields
- `0x1302` `template_id` (string)
- `0x1303` `target_root` (string; `primary` or root token)
- `0x1304` `path_prefix` (string)

## Canonical ordering
- `supported_targets` sorted by string.
- `allowed_splats` sorted by string.
- `layout_templates` sorted by `template_id`.
- `components` sorted by `component_id`.
- `deps` and `conflicts` sorted by string.
- `component_supported_targets` sorted by string.
- `artifacts` sorted by `artifact_id`, then `source_path`, then `layout_template_id`.