Status: DERIVED
Last Reviewed: 2026-03-05
Supersedes: none
Superseded By: none

# PROV0 Retro Consistency Audit

Task: PROV-0  
Scope: provenance/event-sourcing and compaction discipline baseline audit

## Inputs Audited
- `tools/xstack/sessionx/process_runtime.py`
- `src/signals/transport/transport_engine.py`
- `tools/xstack/sessionx/time_lineage.py`
- `src/control/proof/control_proof_bundle.py`
- `schemas/control_proof_bundle.schema.json`
- `data/registries/info_artifact_family_registry.json`
- `data/registries/derived_artifacts.json`

## Artifact Family Audit (Current State)

| Family | Observed usage | Current status |
|---|---|---|
| RECORD | `artifact.energy_ledger_entry`, `artifact.boundary_flux_event`, `artifact.exception_event`, `artifact.time_adjust_event`, fault/leak/burst style incidents | Present and actively emitted |
| MODEL | Cached model outputs appear in `state.model_evaluation_results` but no dedicated provenance compaction classification policy yet | Partial (unclassified for compaction) |
| OBSERVATION | `artifact.measurement`, fluid pressure observations | Present |
| CREDENTIAL | Info family exists; institutional/cert artifacts are represented in registries and signal systems | Present |

## Canonical vs Derived Classification Gaps

1. Canonical mutation events are emitted, but there is no single explicit classification registry declaring what is canonical vs derived for compaction decisions.
2. Derived outputs (`explain` artifacts, inspection snapshots, cached model evaluations) are not centrally classified for deterministic compaction eligibility.
3. Proof bundles currently track many domain hash chains but do not include explicit compaction marker hash chains or compaction anchor hashes.

## Canonical Logging Gap Check

- Checked mutation-heavy paths in `process_runtime.py`:
  - Energy transformations and boundary flux are logged and mirrored as RECORD info artifacts.
  - Exception events are logged and mirrored as RECORD info artifacts.
  - Time adjust events are logged and mirrored as RECORD info artifacts.
- Gap:
  - No dedicated compaction marker event family/registry entry exists yet.

## Existing Compaction/Pruning Logic Audit

`tools/xstack/sessionx/time_lineage.py::compact_save` currently:
- prunes checkpoint/snapshot artifacts per policy,
- merges/prunes intent logs,
- optionally prunes run-meta.

Findings:
- Compaction behavior is deterministic and hash-checked for retained files.
- It is save-artifact oriented, not provenance-classification oriented.
- There is no canonical/derived classifier gate in compaction logic.
- There is no compaction marker RECORD inserted into runtime/state proof surfaces.

## Gap List

1. Missing schema/contracts for:
   - `compaction_marker`
   - provenance artifact classification for compaction policy.
2. Missing registry:
   - explicit artifact-type classification (`canonical|derived`) and `compaction_allowed`.
3. Missing deterministic compaction engine at provenance layer:
   - compact derived artifacts only,
   - preserve canonical event stream,
   - emit deterministic compaction marker.
4. Missing proof fields for compaction marker chain and pre/post anchors.
5. Missing RepoX/AuditX hard enforcement for canonical-event retention and marker requirements.

## Migration Notes

- Keep canonical event rows immutable and retained.
- Allow deterministic compaction only for derived/cached artifacts.
- Add compaction marker RECORD as canonical witness artifact.
- Extend proof surface with compaction marker + pre/post anchor hashes.
- Keep current save compaction path, but align it under explicit provenance classification and marker discipline.
