# setup_audit.tlv (SR-4)

All integers are little-endian.

## File header
Same as `install_manifest.tlv` (magic `DSK1`, version `1`, endian `0xFFFE`).

## Top-level TLVs
- `0x4001` `run_id` (u64; deterministic mode => `0`)
- `0x4002` `manifest_digest64` (u64)
- `0x4003` `request_digest64` (u64)
- `0x4009` `splat_caps_digest64` (u64)
- `0x400A` `resolved_set_digest64` (u64)
- `0x400B` `plan_digest64` (u64)
- `0x4004` `selected_splat` (string)
- `0x4005` `selection` (container)
- `0x4006` `operation` (u16)
- `0x4007` `result` (container)
- `0x4008` `events` (container)
- `0x400C` `refusals` (container, optional)

### selection container
- `0x4101` `selection_candidates` (container)
- `0x4102` `selection_rejections` (container)
- `0x4103` `selected_splat_id` (string)
- `0x4107` `selected_reason_code` (u16)

#### selection_candidates container
- `0x4104` `candidate_entry` (container)

##### candidate_entry fields
- `0x4105` `id` (string)
- `0x4106` `caps_digest64` (u64)

#### selection_rejections container
- `0x4110` `rejection_entry` (container)

##### rejection_entry fields
- `0x4111` `id` (string)
- `0x4112` `code` (u16)
- `0x4113` `detail` (string, optional)

### refusals container
- `0x4120` `refusal_entry` (container)

#### refusal_entry fields
- `0x4121` `code` (u16)
- `0x4122` `detail` (string, optional)

### result container
- `0x4302` `domain` (u16)
- `0x4303` `code` (u16)
- `0x4304` `subcode` (u16)
- `0x4305` `flags` (u16)

### events container
- `0x4201` `event_entry` (container)

#### event_entry fields
- `0x4202` `event_id` (u16)
- `0x4203` `error_domain` (u16)
- `0x4204` `error_code` (u16)
- `0x4205` `error_subcode` (u16)
- `0x4206` `error_flags` (u16)

## Ordering
- Candidates and rejections are sorted by ID.
- Refusals are emitted in detection order.
- Events are emitted in execution order.
