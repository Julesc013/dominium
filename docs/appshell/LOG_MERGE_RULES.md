Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/LOGGING_AND_TRACING.md`, and `docs/appshell/SUPERVISOR_MODEL.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Log Merge Rules

## Canonical Merge Key

Supervisor log aggregation merges rows in ascending order by:

1. `source_product_id`
2. `channel_id`
3. `seq_no`
4. `endpoint_id`
5. `event_id`

Arrival timing must never affect the merged order.

## Channel Discipline

- Aggregated child log rows carry `channel_id = log`.
- `seq_no` remains monotonic within each channel.
- Truncation keeps the last 128 rows after deterministic sorting, not after arrival-order append.

## Canonical Args Reference

- Sample `args_hash`: `183556376e904a88f526eb19a760320e9b8d5ec2ef018b4c2818114f6b9937b3`
- Sample `argv_text_hash`: `06c19aa48202ec1dd20e367b9010359eff749c19657cee5ce10fda262773d4ea`
