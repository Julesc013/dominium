# PATCH-A3 Retro Audit

Date: 2026-03-04  
Scope: Field discipline and mutation purity sweep (`PATCH-A3`)

## Invariants / Contracts Audited
- `INV-FIELD-MUTATION-PROCESS-ONLY`
- `INV-FIELD-SAMPLE-API-ONLY`
- `INV-NO-CROSS-SHARD-FIELD-DIRECT`
- `docs/physics/FIELD_GENERALIZATION.md`
- `docs/physics/FIELD_SHARD_RULES.md`

## Scan Summary
1. Direct field-state writes (`field_layers`, `field_cells`, `field_sample_rows`)
2. Inline environmental/field modifiers outside approved field/process/model paths
3. Cross-shard field access without boundary artifact exchange
4. Field sampling pathways not using standardized `field_sample` API/cache discipline

## Findings
| Area | Location | Classification | Notes |
|---|---|---|---|
| Field sampling cache key discipline | `src/signals/transport/channel_executor.py` | needs migration to model/process | Legacy cache keyed by `tick::node` with ad-hoc mixed payload; migrated to per-field `(field_id, spatial_node_id, tick)` sample rows via `build_field_sample`. |
| Inline field-modifier attenuation logic | `src/signals/transport/transport_engine.py` | needs migration to model/process | Queue-extension field modifiers were applied with inline modifier assignment signatures; normalized to sampled modifier inputs to satisfy field-discipline analyzer contract. |
| Boundary field sampling replay visibility | `tools/xstack/sessionx/process_runtime.py` (`process.compartment_flow_tick`) | needs migration to model/process | Boundary sampling used `get_field_value` but did not persist sample rows/hash chains for replay/proof parity; patched to capture sample rows and emit `field_update_event` with `update_kind=boundary_exchange`. |
| Direct field mutation outside process/field engine | repo-wide scan | compliant | No non-allowed direct writes retained. |
| Cross-shard direct field access | repo-wide scan | compliant | No direct cross-shard field read/write paths detected; boundary artifact path remains canonical. |

## Migration / Deprecation Notes
- Legacy ad-hoc field sample cache shape in SIG transport is deprecated in favor of canonical `field_sample` rows.
- Field boundary exchange events now participate in deterministic hash-chain surfaces for proof/replay.

## Validation Intent
- Promote field mutation/sample/boundary rules to strict governance checks.
- Add replay verification tooling for field hash-chain reproduction.
