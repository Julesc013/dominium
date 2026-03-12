# ARCH Audit Fix Plan

## Current Audit Snapshot

- report_id: `arch.audit.v1`
- result: `complete`
- blocking_findings: `0`
- known_exceptions: `12`
- source_artifacts:
  - `docs/audit/ARCH_AUDIT_REPORT.md`
  - `data/audit/arch_audit_report.json`

## Classification Policy

- `must-fix for v0.0.0`: truth-path determinism hazards that can be removed with local ordering or arithmetic refactors and no semantic drift.
- `acceptable provisional`: reserved for items that cannot be removed without changing intended semantics. None are accepted in this pass.

## Must-Fix Items

| Path | Line | Category | Minimal change |
| --- | ---: | --- | --- |
| `src/fields/field_engine.py` | 649 | unordered iteration | Iterate `layer_by_field_id` in sorted `field_id` order when deriving `value_kind_by_field_id`. |
| `src/geo/index/geo_index_engine.py` | 208 | float usage | Replace float-based grid cell indexing with integer floor-division helper over canonical integer coordinates. |
| `src/geo/index/geo_index_engine.py` | 228 | float usage | Replace float-based tree cell indexing with integer floor-division helper over canonical integer coordinates. |
| `src/geo/index/geo_index_engine.py` | 244 | float usage | Replace float-based atlas `u_idx` calculation with integer floor-division helper. |
| `src/geo/index/geo_index_engine.py` | 245 | float usage | Replace float-based atlas `v_idx` calculation with integer floor-division helper. |
| `src/geo/profile_binding.py` | 111 | unordered iteration | Iterate `GEO_RULE_TO_PROFILE_KEY` by sorted `rule_id` so exception event derivation is canonical. |
| `src/logic/compile/logic_proof_engine.py` | 148 | unordered iteration | Compare proof extension keys in sorted order before canonical equality checks. |
| `src/logic/eval/common.py` | 264 | unordered iteration | Apply `_FUNCTION_REPLACEMENTS` in sorted source-token order so expression rewrite order is explicit. |
| `src/logic/eval/compute_engine.py` | 285 | unordered iteration | Iterate output ports in sorted `port_id` order before materializing payloads. |
| `src/logic/eval/sense_engine.py` | 276 | unordered iteration | Iterate input ports in sorted `port_id` order before snapshotting sensed values. |
| `src/logic/fault/fault_engine.py` | 206 | unordered iteration | Search existing faults in sorted `fault_id` order before deriving the target match. |
| `src/worldgen/refinement/refinement_cache.py` | 155 | unordered iteration | Apply max-entry overrides in sorted refinement-level order before eviction. |

## Audit Families Already Clean

- Truth purity: no forbidden presentation fields found in canonical schemas or materializers.
- Renderer truth access: no direct truth/runtime reads in renderer-facing modules.
- Duplicate semantic engines: authoritative negotiation, overlay merge, ID generation, and illumination entry points are singular.
- Stability marker discipline: governed registries validate cleanly.
- Contract pin / pack compat discipline: ARCH-AUDIT governed checks pass as-is.

## Acceptable Provisional Exceptions

- None for this pass.

## Execution Status

### Phase 1

- Verified `truth_purity_scan` remains `pass`.
- No canonical truth schemas or materializers contained forbidden presentation state, so no truth-model field removal was required in this pass.

### Phase 2

- Verified `duplicate_semantics_scan` remains `pass`.
- Capability negotiation, overlay merge, GEO ID generation, and illumination entry points were already singular, so no engine refactor was required in this pass.
- Canonical engine paths retained:
  - `src/compat/capability_negotiation.py`
  - `src/geo/overlay/overlay_merge_engine.py`
  - `src/geo/index/object_id_engine.py`
  - `src/worldgen/earth/lighting/illumination_engine.py`
