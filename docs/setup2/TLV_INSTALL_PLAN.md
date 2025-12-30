# install_plan.tlv (SR-4)

All integers are little-endian.

## File header
Same as `install_manifest.tlv` (magic `DSK1`, version `1`, endian `0xFFFE`).

## Top-level TLVs
- `0x5001` `product_id` (string)
- `0x5002` `product_version` (string)
- `0x5003` `selected_splat_id` (string)
- `0x5004` `selected_splat_caps_digest64` (u64)
- `0x5005` `operation` (u16)
- `0x5006` `install_scope` (u16)
- `0x5007` `install_roots` (container)
- `0x5008` `manifest_digest64` (u64)
- `0x5009` `request_digest64` (u64)
- `0x500A` `resolved_set_digest64` (u64)
- `0x500B` `plan_digest64` (u64)
- `0x500C` `resolved_components` (container)
- `0x500D` `job_graph_stub` (container)
- `0x500E` `file_operations` (container)
- `0x500F` `registrations` (container)

### install_roots container
- `0x5010` `install_root_entry` (string)

### resolved_components container
- `0x5101` `component_entry` (container)

#### component_entry fields
- `0x5102` `component_id` (string)
- `0x5103` `component_version` (string)
- `0x5104` `kind` (string)
- `0x5105` `source` (u16: default=1, user=2, dependency=3, installed=4)

### job_graph_stub container
- `0x5201` `step_entry` (container)

#### step_entry fields
- `0x5202` `step_id` (u32)
- `0x5203` `step_kind` (u16: stage_artifact=1, verify_hashes=2, commit_swap=3, register_actions=4, write_state=5, write_audit=6)
- `0x5204` `component_id` (string, optional)
- `0x5205` `artifact_id` (string, optional)
- `0x5206` `target_root_id` (u32)
- `0x5207` `intent` (bytes, optional)

### file_operations container
- `0x5301` `file_op_entry` (container)

#### file_op_entry fields
- `0x5302` `op_kind` (u16: copy=1, extract=2, remove=3, mkdir=4)
- `0x5303` `from` (string, optional)
- `0x5304` `to` (string, optional)
- `0x5305` `ownership` (u16)
- `0x5306` `digest64` (u64)
- `0x5307` `size` (u64)

### registrations container
- `0x5401` `shortcuts` (container, optional)
- `0x5402` `file_associations` (container, optional)
- `0x5403` `url_handlers` (container, optional)

#### shortcuts container
- `0x5410` `shortcut_entry` (string)

#### file_associations container
- `0x5411` `file_assoc_entry` (string)

#### url_handlers container
- `0x5412` `url_handler_entry` (string)

## Canonical ordering
- `install_roots` sorted by string.
- `resolved_components` sorted by `component_id`, then `component_version`.
- `job_graph_stub` sorted by `step_id`.
- `file_operations` sorted by `to`, then `from`, then `op_kind`.
- `registrations` lists sorted by string.
