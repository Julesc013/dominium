# TLV Job Journal (job_journal.tlv)

Purpose: record job DAG execution progress for resume/rollback.

## File Header
- Standard TLV header (magic, version, endian, header_size, payload_size, header_crc).

## Top-Level Fields (v1)
- `run_id` (u64)
- `plan_digest64` (u64)
- `selected_splat_id` (string)
- `stage_root` (string; may be relative when using fake services)
- `rollback_ref` (string, optional)
- `plan_bytes` (bytes; embedded install_plan.tlv)
- `last_error` (container)
  - `err_domain` (u16)
  - `err_code` (u16)
  - `err_subcode` (u16)
  - `err_flags` (u16)
  - `err_msg_id` (u32)
  - `err_detail` (list of key/value detail TLVs)
- `checkpoints` (list)
  - `job_id` (u32)
  - `status` (u16)
  - `last_completed_step` (u32)

## Job Status Values
- `DSK_JOB_STATUS_PENDING` = 1
- `DSK_JOB_STATUS_IN_PROGRESS` = 2
- `DSK_JOB_STATUS_COMPLETE` = 3
- `DSK_JOB_STATUS_FAILED` = 4
- `DSK_JOB_STATUS_SKIPPED` = 5

## Notes
- Journals are written before execution and updated after each job checkpoint.
- Unknown TLVs must be skipped.
- `stage_root` is derived from the temp root + plan digest (`dsk_stage_<digest>`).
