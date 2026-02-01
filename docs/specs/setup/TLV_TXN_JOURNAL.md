Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# TLV Transaction Journal (txn_journal.tlv)

Purpose: record concrete file operations and their rollback inverses.

## File Header
- Standard TLV header (magic, version, endian, header_size, payload_size, header_crc).

## Top-Level Fields (v1)
- `plan_digest64` (u64)
- `stage_root` (string; may be relative when using fake services)
- `steps` (list)
  - `step_id` (u32)
  - `op_kind` (u16)
  - `src_path` (string, optional)
  - `dst_path` (string, optional)
  - `rollback_kind` (u16)
  - `rollback_src` (string, optional)
  - `rollback_dst` (string, optional)

## Step Kinds
- `DSS_TXN_STEP_MKDIR` = 1
- `DSS_TXN_STEP_COPY_FILE` = 2
- `DSS_TXN_STEP_EXTRACT_ARCHIVE` = 3
- `DSS_TXN_STEP_ATOMIC_RENAME` = 4
- `DSS_TXN_STEP_DIR_SWAP` = 5
- `DSS_TXN_STEP_DELETE_FILE` = 6
- `DSS_TXN_STEP_REMOVE_DIR` = 7

## Notes
- Steps are ordered deterministically.
- Rollback is executed in reverse order using the recorded rollback steps.
- Unknown TLVs must be skipped.