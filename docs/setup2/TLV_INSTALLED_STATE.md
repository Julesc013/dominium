# installed_state.tlv (SR-1)

All integers are little-endian.

## File header
Same as `install_manifest.tlv` (magic `DSK1`, version `1`, endian `0xFFFE`).

## Top-level TLVs
- `0x3001` `product_id` (string)
- `0x3002` `installed_version` (string)
- `0x3003` `selected_splat` (string)
- `0x3004` `install_scope` (u16)
- `0x3005` `install_root` (string; primary install root)
- `0x3006` `installed_components` (container)
- `0x3007` `manifest_digest64` (u64)
- `0x3008` `request_digest64` (u64)
- `0x3009` `install_roots` (container; optional)
- `0x300A` `ownership` (u16; optional)
- `0x300B` `artifacts` (container; optional)
- `0x300C` `registrations` (container; optional)
- `0x300D` `previous_state_digest64` (u64; optional)
- `0x300E` `import_source` (string; optional)
- `0x300F` `import_details` (container; optional)
- `0x3013` `state_version` (u32)
- `0x3014` `migration_applied` (container; optional)

### installed_components container
- `0x3010` `installed_component_entry` (string)

### install_roots container
- `0x3011` `install_root_entry` (string)

### import_details container
- `0x3012` `import_detail_entry` (string)

### migration_applied container
- `0x3015` `migration_entry` (string)

### artifacts container
- `0x3020` `artifact_entry` (container)
  - `0x3021` `artifact_root_id` (u32)
  - `0x3022` `artifact_path` (string)
  - `0x3023` `artifact_digest64` (u64)
  - `0x3024` `artifact_size` (u64)

### registrations container
- `0x3030` `registration_entry` (container)
  - `0x3031` `registration_kind` (u16)
  - `0x3032` `registration_value` (string)
  - `0x3033` `registration_status` (u16)

## Canonical ordering
- `installed_components` sorted by string.
- `install_roots` sorted by string.
- `import_details` sorted by string.
- `migration_applied` sorted by string.
- `artifacts` sorted by `(artifact_root_id, artifact_path)`.
- `registrations` sorted by `(registration_kind, registration_value, registration_status)`.
