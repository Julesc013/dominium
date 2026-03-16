Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# POLL-1 Retro-Consistency Audit

Date: 2026-03-05
Scope: Deterministic P1 dispersion and transport integration over POLL-0 canonical emission/totals baseline.

## Inputs Audited
- `tools/xstack/sessionx/process_runtime.py`
- `src/pollution/pollution_engine.py`
- `src/fields/field_engine.py`
- `src/client/interaction/inspection_overlays.py`
- `src/interior/compartment_flow_engine.py`

## Findings
1. Pollution emissions are canonical and process-mediated.
- `process.pollution_emit` validates `pollutant_id` against `pollutant_type_registry`.
- Emissions are normalized into `pollution_source_event_rows`, recorded as RECORD artifacts, and hash-chained.
- P0 totals (`pollution_total_rows`) are deterministic and replay-stable.

2. No direct renderer writes to pollution concentration fields were found.
- Renderer/overlay code currently consumes inspection sections and visual overlays only.
- There are no existing direct writes to `field.pollution.*` concentration layers because P1 concentration layers are not yet introduced.

3. Legacy smoke/visibility pathways still exist and remain transitional.
- Interior smoke summaries and smoke alarms are present.
- Visibility coupling currently includes smoke-derived pathways in runtime/interior pipelines.
- This remains a known migration seam: POLL concentration layers must become the canonical source for pollution-driven visibility effects.

4. Field sampling discipline is intact for read paths.
- Runtime field reads route through `get_field_value` / `field_modifier_snapshot` APIs.
- Existing field writes are process-mediated and policy-gated via `_apply_field_updates`.

## Integration Decisions for POLL-1
1. Introduce concentration fields as first-class `field.pollution.<type>_concentration` layers with `field.profile_defined` policy.
2. Keep mutation process-mediated: dispersion computes deterministic deltas, then applies updates via field-update process pathways.
3. Keep smoke visuals derived-only; no canonical pollution writes from render/inspection systems.
4. Preserve POLL-0 null-boot behavior: empty pollutant registries remain valid and deterministic.

## Risks
- Dual semantics risk (legacy `smoke_density` and new pollution concentration) can cause interpretive drift until visibility coupling fully migrates to constitutive POLL models.
- Unbounded cell loops must be guarded by deterministic budget/degrade policy and explicit degrade logs.
