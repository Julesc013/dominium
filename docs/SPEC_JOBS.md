# Jobs / Tasks (JOB)

Jobs are engine-level task instances parameterized by content templates. The engine only enforces generic feasibility constraints (including environment ranges) and does not embed product/gameplay semantics.

## 1. Instances
- `d_job_instance` stores id, template id, flags, subject/target ids, target position, and an opaque TLV `params` blob.
- Instance persistence is currently instance-level (world) under `TAG_SUBSYS_DJOB`.

## 2. Environment Constraints (Generic)
- `job_template.params` may contain `D_TLV_JOB_ENV_RANGE` records:
  - `FIELD_ID` (u16): an ENV field id (e.g. `D_ENV_FIELD_TEMPERATURE`)
  - `MIN`/`MAX` (Q16.16): acceptable range (optional; omitted means unbounded)
- During tick, JOB evaluates requirements against `d_env_sample_at` at the job target position.
  - If any requirement fails (or the field is missing), the job sets `D_JOB_FLAG_ENV_UNSUITABLE`.

