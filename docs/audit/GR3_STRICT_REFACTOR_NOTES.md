Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GR3 STRICT Refactor Notes

## Applied Refactors
1. [`tools/xstack/sessionx/process_runtime.py`](/d:/Projects/Dominium/dominium/tools/xstack/sessionx/process_runtime.py)
- Renamed branch-local signal/switch machine maps to avoid shadowing the imported `machine_rows_by_id(...)` helper.
- Kept the process-only mutation path unchanged; this is a correctness repair for runtime name resolution.

2. [`src/control/control_plane_engine.py`](/d:/Projects/Dominium/dominium/src/control/control_plane_engine.py)
- Made decision-log artifact naming deterministic for repeated identical resolutions.
- Removed the filesystem-state dependency that changed `decision_log_ref` across equivalent runs.

3. [`src/system/system_expand_engine.py`](/d:/Projects/Dominium/dominium/src/system/system_expand_engine.py)
- Added explicit provenance-anchor verification of `state_vector_row.serialized_internal_state` before accepting expand.
- Closed a tamper-acceptance gap without changing successful expand outputs.

4. [`src/electric/protection/protection_engine.py`](/d:/Projects/Dominium/dominium/src/electric/protection/protection_engine.py)
- Normalized trip candidacy to use the observed fault measure for overcurrent faults.
- Preserved existing deterministic ordering, coordination, and safety-event routing.

5. [`schemas/control_proof_bundle.schema.json`](/d:/Projects/Dominium/dominium/schemas/control_proof_bundle.schema.json)
- Added schema coverage for emitted reaction, QC, pollution, drift, compiled-model, equivalence, and process-capsule hash chains.
- No schema version bump was required because the runtime payload already emitted these fields and the change is additive-only.

6. [`tools/xstack/testx/tests/plan_testlib.py`](/d:/Projects/Dominium/dominium/tools/xstack/testx/tests/plan_testlib.py)
- Added deterministic default capability bindings for planner fixtures so strict control gating reflects intended planner authority.

7. [`tools/xstack/testx/tests/lod_invariance_testlib.py`](/d:/Projects/Dominium/dominium/tools/xstack/testx/tests/lod_invariance_testlib.py)
- Added deterministic quantity-dimension bindings needed by the stricter conservation runtime.
- This aligns the fixture with GR3 enforcement; it does not relax the runtime contract.

8. [`docs/impact/GR3_NO_STOPS_HARDENING.md`](/d:/Projects/Dominium/dominium/docs/impact/GR3_NO_STOPS_HARDENING.md)
- Added demand coverage mapping required by META-GENRE-0/RepoX for the repaired runtime-domain paths.

## Safety Statement
- No new feature work was introduced.
- No wall-clock or nondeterministic dependency was added.
- Runtime semantics changed only where prior behavior was demonstrably incorrect.
