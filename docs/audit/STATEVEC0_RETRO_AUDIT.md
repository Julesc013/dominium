Status: AUDIT
Last Reviewed: 2026-03-06
Scope: STATEVEC-0 retro-consistency audit for explicit output-affecting state exposure.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# STATEVEC0 Retro Audit

## Objective
Identify output-affecting internal state across SYS/COMPILE/process runtimes and verify whether it is explicitly captured in deterministic state vectors used for collapse/expand and compiled execution.

## Existing Explicit State Capture Surfaces
- `src/system/system_collapse_engine.py`
  - `build_system_state_vector_row(...)`
  - `serialized_internal_state` capture and `provenance_anchor_hash`
- `src/system/system_expand_engine.py`
  - restore from `serialized_internal_state`
  - hash validation via `REFUSAL_SYSTEM_EXPAND_HASH_MISMATCH`
- `src/system/macro/macro_capsule_engine.py`
  - `internal_state_vector` in runtime rows/capsules (currently map-based, schema-light)
- `src/chem/process_run_engine.py`
  - deterministic process run state rows (`process_run_state`) but no universal state-vector declaration link
- `src/meta/compile/compile_engine.py`
  - compile artifacts/proofs are explicit, but runtime state memory is extension-based and not governed by a declared state-vector definition.

## Candidate Hidden State Inventory

| System/Domain | Candidate hidden state variables | Current capture status | Migration plan |
| --- | --- | --- | --- |
| SYS collapse/expand | placeholder assembly linkage, last collapse tick, active state vector id, restored capsule id | partly in `extensions` and `system_state_vector_rows` | add explicit `state_vector_definition` and `state_vector_snapshot` rows, tie collapse/expand to deterministic serialize/deserialize engine |
| SYS macro capsule runtime | runtime hysteresis counters, last inputs hash, fail-safe latch, deferred update bucket | runtime map/extension fields, not schema-declared | require declared owner state vector for capsule owner and snapshot hash chain |
| SYS reliability | warning/failure band crossings, fallback action latches, stochastic stream outcome memory | split across health/reliability rows | expose as explicit state snapshot entries for system owner |
| CHEM process runs (process capsule analog) | progress, end_tick, status latch, output batch linkage | explicit `process_run_state` rows | register process-capsule default state vector definition and bridge process state rows to owner snapshots |
| COMPILE runtime | compiled-model execution memory (`execution_count`, prior input/output hashes, hysteresis memory when enabled) | not explicitly governed by state-vector schema | add compiled-model default state vector definition and runtime serialize/deserialize hooks |
| POLL exposure/compliance | rolling exposure cache, scheduled report cursor, degrade bucket position | mostly explicit rows, some extension caches in runtime | keep as explicit rows; prohibit output-affecting cache outside declared vector fields |
| CTRL/session runtime wrappers | memoized per-process intermediate values that can alter output ordering/decisions | mixed, often extension-based | enforce debug guard against undeclared output-affecting mutation for state-vector owners |

## Gaps Found
- No universal schema requiring owner-level explicit state vector declaration.
- No universal deterministic serializer/deserializer for state vectors.
- No cross-owner state vector hash chain in proof surfaces.
- Hidden-state detection currently focuses on SYS composition heuristics, not declared-field validation.

## Migration Plan
1. Add system-level state vector definition/snapshot schemas and registry defaults.
2. Introduce `src/system/statevec/statevec_engine.py` for deterministic serialize/deserialize and hash-stable snapshots.
3. Integrate collapse/expand and compile runtime with statevec engine.
4. Add RepoX/AuditX checks for undeclared output-affecting state mutation.
5. Extend proof/replay surfaces with state vector definition/snapshot hash chains.
