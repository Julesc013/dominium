Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# MAT-8 Commitments and Reenactment Baseline

## Strictness Levels
- `causality.C0`
  - Events required for macro/meso material changes.
  - Commitments optional unless process family already emits them.
- `causality.C1`
  - Major macro/meso changes require commitment linkage.
  - Enforced for logistics/construction/maintenance mutation paths.
- `causality.C2`
  - Reserved for bounded micro commitment enforcement zones.

## Commitment Types
- `commit.construction.project`
- `commit.construction.step`
- `commit.logistics.shipment`
- `commit.maintenance.inspect`
- `commit.maintenance.repair`
- `commit.demography.tick` (optional macro trace type)
- `commit.custom` (extension stub)

Canonical commitment artifacts persist in `universe_state.material_commitments` with deterministic fingerprints.

## Event Stream Indexing
- Deterministic stream indices are built per target + tick range.
- Source events are derived from logistics, construction, and maintenance provenance event logs.
- Output index rows persist in `universe_state.event_stream_indices`.

## Reenactment Generator Behavior
- Generator inputs:
  - reenactment request
  - event stream index
  - linked commitments
  - batch lineage rows
  - max cost units
- Deterministic output:
  - `reenactment_artifact` row (`inputs_hash`, `fidelity_achieved`, fingerprint)
  - timeline payload keyed by `output_timeline_ref`
- Deterministic fidelity degrade:
  - `micro -> meso -> macro` under budget pressure.
- Epistemic law gating:
  - micro detail refuses when authority/law disallow hidden-state detail.

## Performance Characteristics
- Event stream rebuild and reenactment generation are explicit process executions.
- Reenactment artifacts are cacheable by deterministic `inputs_hash`.
- Playback is derived-only (`skip_state_log=true`) and does not mutate canonical truth.

## RepoX/AuditX/TestX Coverage
- RepoX:
  - `INV-NO_SILENT_MACRO_CHANGE`
  - `INV-REENACTMENT_DERIVED_ONLY`
- AuditX analyzers:
  - `UncommittedMacroChangeSmell`
  - `ReenactmentLeakSmell`
- TestX:
  - `test_commitment_required_under_C1`
  - `test_events_always_required_under_C0`
  - `test_event_stream_index_deterministic`
  - `test_reenactment_deterministic_hash`
  - `test_reenactment_budget_degrades`
  - `test_epistemic_gating_of_reenactment_detail`

## Extension Points (MAT-9+)
- C2 bounded micro-zone commitments.
- Dedicated micro reenactment scene solver hooks.
- Ranked proof-bundle enrichment with reenactment artifact witnesses.
