Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# TEMP0 Retro Audit

Date: 2026-03-04  
Scope: temporal semantics constitution baseline (`TEMP-0`)

## Invariants / Contracts Audited
- `INV-SCHEDULE-DOMAIN-DECLARED`
- `INV-NO-WALLCLOCK-TIME`
- `INV-NO-FUTURE-RECEIPTS`
- `INV-DETERMINISTIC-SUBSTEP-POLICY`
- `docs/reality/TIME_CONSTITUTION.md`

## Scan Coverage
- Schedule components and schedule normalizers
- Hazard/flow delay and transport delay paths
- Signal receipt and trust timelines
- Macro travel and interior substep code paths
- Replay and branch lineage helpers

## Findings
| Area | Location | Classification | Notes |
|---|---|---|---|
| Schedule domain declaration | `schema/core/schedule.schema`, `schemas/schedule.schema.json`, `src/core/schedule/schedule_engine.py`, `src/signals/aggregation/aggregation_engine.py` | needs migration to TemporalDomain | Existing schedule rows are canonical-tick based but did not explicitly declare `temporal_domain_id`; migrate with default `time.canonical_tick` while preserving semantics. |
| Wall-clock dependencies | `tools/xstack/sessionx/common.py`, multiple non-authoritative tooling paths (`tools/*`) | compliant (non-authoritative) | Wall-clock calls are present in tooling/report metadata, not in authoritative tick advancement; keep forbidden in authoritative runtime paths. |
| Ad-hoc warp behavior | interior flow substeps (`src/interior/compartment_flow_engine.py`) | compliant with migration note | Deterministic fixed substeps already used; formalize under explicit substep policy registry to avoid drift. |
| Future receipt causality | SIG receipt generation (`src/signals/transport/transport_engine.py`) | compliant | Receipt acquisition tick is bound to canonical current tick; no future-receipt dependency pattern found in authoritative paths. |
| Real-time coupling | schedule/transport/flow runtime scans | compliant | Authoritative paths are tick-index driven; no required migration for runtime semantics. |

## Migration Notes
- Add `TemporalDomain` + `TimeMapping` declarations as first-class schemas and registries.
- Backfill schedule rows with explicit `temporal_domain_id` default (`time.canonical_tick`) in canonical normalizers.
- Formalize deterministic batching/substepping policy IDs for constitutional governance.
- Introduce causality checks that forbid future-receipt references in control/schedule decisions.

## Deprecation Notes
- Legacy implicit schedule-time assumptions are deprecated in favor of explicit `temporal_domain_id`.
- Legacy references to "time warp" as variable real-time behavior remain forbidden; only deterministic batching/substepping is canonical.
