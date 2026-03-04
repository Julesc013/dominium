# TEMP1 Retro Audit

Date: 2026-03-04
Scope: TEMP-1 TimeMappings and schedule-domain integration

## Findings

| Surface | Status | Notes |
|---|---|---|
| Schedule bindings | Gap found | `schedule_time_binding` rows existed in schema/registry, but runtime did not route all schedule ticks through domain resolution. |
| Canonical vs civil time usage | Gap found | Several schedule paths implicitly treated canonical tick as execution time without consulting `time_mapping` outputs for non-canonical domains. |
| Proper time assumptions in MOB/PHYS | Partial | Momentum/field inputs were available, but proper-time mapping was not executed each tick in runtime. |
| Hardcoded day/night behavior | No direct runtime source found | No explicit wall-clock day/night branch was found in authoritative runtime paths. |
| Wall-clock dependency | Guarded | Existing TEMP-0 checks for wall-clock APIs were present and retained. |

## Migration Notes

1. Route schedule execution through `tick_schedules(..., schedule_time_binding_rows, resolve_domain_time_fn)` in authoritative runtime paths.
2. Evaluate TEMP-1 mappings each canonical tick in `execute_intent` and persist:
   - `time_mapping_cache_rows`
   - `time_stamp_artifacts`
   - `proper_time_states`
3. Backfill `schedule_time_binding` creation in `process.travel_schedule_set`.
4. Add proof-chain coverage for:
   - `time_mapping_hash_chain`
   - `schedule_domain_evaluation_hash`
5. Add enforcement for:
   - model-only time mapping
   - no direct canonical tick mutation
   - deterministic schedule-domain resolution
