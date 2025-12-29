# installed_state.tlv (SR-1)

All integers are little-endian.

## File header
Same as `install_manifest.tlv` (magic `DSK1`, version `1`, endian `0xFFFE`).

## Top-level TLVs
- `0x3001` `product_id` (string)
- `0x3002` `installed_version` (string)
- `0x3003` `selected_splat` (string)
- `0x3004` `install_scope` (u16)
- `0x3005` `install_root` (string; may be empty in SR-1)
- `0x3006` `installed_components` (container)
- `0x3007` `manifest_digest64` (u64)
- `0x3008` `request_digest64` (u64)

### installed_components container
- `0x3010` `installed_component_entry` (string)

## Canonical ordering
- `installed_components` sorted by string.
