# Phase 1 Audit Report (PH1-AUDIT)

Status: FAIL (see Summary)
Scope: ENF0, ENF1, ENF2, DET0, DET1, DET2, PERF0, PERF1, PERF2, PERF3, SCALE0, SCALE1, SCALE2, DATA0, DATA1, REND0, EPIS0

## Method
- Reviewed Phase-1 docs and specs: `docs/ARCH_ENFORCEMENT.md`, `docs/ARCH_BUILD_ENFORCEMENT.md`, `docs/DETERMINISM_ENFORCEMENT.md`, `docs/DETERMINISM_TEST_MATRIX.md`, `docs/DETERMINISM_HASH_PARTITIONS.md`, `docs/DETERMINISM_GATES.md`, `docs/PERFORMANCE_ENFORCEMENT.md`, `docs/NO_MODAL_LOADING.md`, `docs/STREAMING_BUDGETS.md`, `docs/FIDELITY_DEGRADATION.md`, `docs/PERF_BUDGETS.md`, `docs/PROFILING_GUIDE.md`, `docs/SPEC_EVENT_DRIVEN_STEPPING.md`, `docs/NO_GLOBAL_ITERATION_GUIDE.md`, `docs/SPEC_SHARDING_AUTHORITY.md`, `docs/SPEC_CROSS_SHARD_MESSAGES.md`, `docs/INTEREST_SET_IMPLEMENTATION.md`, `docs/FIDELITY_PROJECTION_IMPLEMENTATION.md`, `schema/SCHEMA_GOVERNANCE.md`, `schema/SCHEMA_VERSIONING.md`, `schema/SCHEMA_MIGRATION.md`, `schema/SCHEMA_VALIDATION.md`, `docs/DATA_VALIDATION_GUIDE.md`, `docs/SPEC_RENDERING_CANON.md`, `docs/SPEC_RENDER_CAPS.md`, `docs/SPEC_RENDER_FEATURES.md`, `docs/SPEC_RENDER_GRAPH.md`, `docs/SPEC_SHADER_IR.md`, `docs/SPEC_EPISTEMIC_INTERFACE.md`, `docs/UI_EPISTEMIC_BOUNDARY.md`.
- Reviewed CI matrix: `docs/CI_ENFORCEMENT_MATRIX.md`.
- Reviewed enforcement implementations: `CMakeLists.txt`, `engine/CMakeLists.txt`, `game/CMakeLists.txt`, `scripts/verify_includes_sanity.py`, `scripts/verify_cmake_no_global_includes.py`, `tools/ci/arch_checks.py`, `tools/ci/perf_budget_check.py`.
- Reviewed tests: `engine/tests/engine_det_order_test.c`, `engine/tests/engine_perf_no_modal_test.c`, `engine/tests/engine_due_sched_test.c`, `engine/tests/engine_perf_budget_test.c`, `engine/tests/engine_data_validate_test.c`, `game/tests/interest/dom_interest_tests.c`, `game/tests/fidelity/dom_fidelity_tests.c`, `game/tests/epistemic/dom_epistemic_tests.c`, `game/tests/epistemic/epistemic_ui_bypass_trycompile.cmake.in`.
- Reviewed CI pipeline wiring: `.github/workflows/ci.yml`.

## Summary

| Dimension | Status | Notes |
| --- | --- | --- |
| A) Rule Coverage | FAIL | Several Phase-1 rules lack wired enforcement and some gate IDs are duplicated. |
| B) Enforcement Coverage | FAIL | Multiple checks exist only as scripts or future hooks and are not CI-wired. |
| C) CI Coverage | FAIL | Static scans and determinism gates are not executed in CI. |
| D) Documentation Consistency | FAIL | Conflicting determinism gate IDs and mismatched check IDs remain. |
| E) Cross-Rule Interaction Safety | FAIL | Several interactions rely on discipline due to missing enforcement. |
| F) Bypass Resistance | FAIL | Multiple bypass paths exist (relative includes, missing scans, missing render checks). |
| G) Future Prompt Compatibility | PASS | Phase-1 rules do not block later phases, but enforcement gaps must be closed. |

## Rule Coverage Table

Status legend:
- Live: CI-wired and merge-blocking.
- Partial: Implemented but not CI-wired or bypassable.
- Missing: Documented only; no implementation.

### Architecture / Rendering / Build / UI

| ID | Description | Enforced By | Where Implemented | Status |
| --- | --- | --- | --- | --- |
| ARCH-TOP-001 | Top-level source/src/common_source forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| ARCH-OWN-002 | Engine and game responsibilities must not be merged. | Not implemented. | Not implemented. | Missing |
| ARCH-DEP-001 | Engine must not reference or link game/launcher/setup/tools. | CMake link assertion + include sanity. | `CMakeLists.txt`, `scripts/verify_includes_sanity.py` | Partial |
| ARCH-DEP-002 | Game depends only on engine. | CMake link assertion. | `CMakeLists.txt` | Live |
| ARCH-DEP-003 | Client depends only on engine and game. | Not implemented. | Not implemented. | Missing |
| ARCH-DEP-004 | Server depends only on engine and game. | Not implemented. | Not implemented. | Missing |
| ARCH-DEP-005 | Tools depend only on engine and game. | Not implemented. | Not implemented. | Missing |
| ARCH-DEP-006 | Launcher/setup depend only on libs and schema. | Not implemented. | Not implemented. | Missing |
| ARCH-INC-001 | Game includes engine/modules or platform headers forbidden. | Build include paths + include sanity + arch_checks. | `game/CMakeLists.txt`, `scripts/verify_includes_sanity.py`, `tools/ci/arch_checks.py` | Partial |
| ARCH-INC-002 | Client/server/tools include engine/modules forbidden. | Build include paths + arch_checks. | `client/CMakeLists.txt`, `server/CMakeLists.txt`, `tools/ci/arch_checks.py` | Partial |
| ARCH-INC-003 | Public headers only under engine/include. | CMake public include assertion. | `engine/CMakeLists.txt` | Live |
| ARCH-RENDER-001 | Renderer tokens outside engine/render forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| ARCH-REN-002 | Game must not branch on graphics APIs. | Not implemented. | Not implemented. | Missing |
| ARCH-REN-003 | Client must not own renderer backends. | Not implemented. | Not implemented. | Missing |
| ARCH-SETUP-001 | Launcher/setup must not depend on engine internals. | Not implemented. | Not implemented. | Missing |
| BUILD-GLOBAL-001 | include_directories/link_directories forbidden. | Configure-time include_directories check + arch_checks. | `scripts/verify_cmake_no_global_includes.py`, `tools/ci/arch_checks.py` | Partial |
| UI-BYPASS-001 | UI reads authoritative world state forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| EPIS-BYPASS-001 | UI includes authoritative headers forbidden. | CTest + static scan. | `game/tests/epistemic/epistemic_ui_bypass_trycompile.cmake.in`, `tools/ci/arch_checks.py` | Partial |
| EPIS-API-002 | UI calls forbidden sim/world APIs. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| EPIS-CAP-003 | UI displays info without capability justification forbidden. | CTest dominium_epistemic. | `game/tests/epistemic/dom_epistemic_tests.c` | Live |
| REND-DIR-001 | Backend dirs outside engine/render/backends forbidden. | Not implemented (future hook). | Not implemented. | Missing |
| REND-DIR-002 | Capability-named backend folders forbidden. | Not implemented (future hook). | Not implemented. | Missing |
| REND-DIR-003 | Version bucket folders forbidden. | Not implemented (future hook). | Not implemented. | Missing |
| REND-API-001 | Game references backend headers/types forbidden. | Not implemented (future hook). | Not implemented. | Missing |
| REND-LEG-001 | Fixed-function backends must not modify core contracts. | Not implemented (future hook). | Not implemented. | Missing |
| REND-FEAT-001 | Render feature modules require requires/fallback/cost. | Not implemented (future hook). | Not implemented. | Missing |
| REND-DET-001 | Renderer writes to authoritative state forbidden. | Not implemented (future hook). | Not implemented. | Missing |

### Determinism

| ID | Description | Enforced By | Where Implemented | Status |
| --- | --- | --- | --- | --- |
| DET-FLOAT-003 | Floating point or math headers in authoritative zones forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| DET-TIME-001 | OS time usage in authoritative zones forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| DET-RNG-002 | Nondeterministic RNG usage in authoritative zones forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| DET-ORD-004 | Unordered container usage without normalization forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| DET-ORDER-TEST-001 | Event queue ordering deterministic under permutations. | CTest engine_det_order. | `engine/tests/engine_det_order_test.c` | Live |
| DET-ORDER-TEST-002 | Ledger obligation ordering deterministic under permutations. | CTest engine_det_order. | `engine/tests/engine_det_order_test.c` | Live |
| DET-ORDER-TEST-003 | Interest set ordering deterministic under permutations. | CTest engine_det_order. | `engine/tests/engine_det_order_test.c` | Live |
| DET-THREAD-005 | Shared mutable state races forbidden. | Not implemented. | Not implemented. | Missing |
| DET-GATE-STEP-001 | Step vs batch equivalence. | Not implemented. | Not implemented. | Missing |
| DET-GATE-REPLAY-002 | Replay equivalence. | Not implemented. | Not implemented. | Missing |
| DET-GATE-LOCKSTEP-003 | Lockstep vs server-auth equivalence. | Not implemented. | Not implemented. | Missing |
| DET-GATE-HASH-004 | Hash partition invariance. | Not implemented. | Not implemented. | Missing |
| DET-EXC-006 | Determinism exceptions forbidden. | Not implemented. | Not implemented. | Missing |
| DET-G1 | Step vs batch equivalence. | Not implemented. | Not implemented. | Missing |
| DET-G2 | Replay equivalence. | Not implemented. | Not implemented. | Missing |
| DET-G3 | Lockstep parity. | Not implemented. | Not implemented. | Missing |
| DET-G4 | Server-auth parity. | Not implemented. | Not implemented. | Missing |
| DET-G5 | No float/OS time/nondeterministic RNG. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| DET-G6 | Canonical ordering under permutations. | CTest engine_det_order (partial coverage). | `engine/tests/engine_det_order_test.c` | Partial |

### Performance

| ID | Description | Enforced By | Where Implemented | Status |
| --- | --- | --- | --- | --- |
| PERF-GLOBAL-002 | Global iteration patterns forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| PERF-EVT-001 | Macro scheduler processes only due entries. | CTest engine_due_sched. | `engine/tests/engine_due_sched_test.c` | Live |
| PERF-EVT-002 | Deterministic due-event ordering enforced. | CTest engine_due_sched. | `engine/tests/engine_due_sched_test.c` | Live |
| PERF-IOBAN-001 | Render/UI thread IO forbidden. | Runtime guard + CTest engine_perf_no_modal. | `engine/tests/engine_perf_no_modal_test.c` | Live |
| PERF-MODAL-001 | Blocking IO on render/UI threads forbidden. | Not implemented. | Not implemented. | Missing |
| PERF-SHADER-002 | Shader compilation on demand forbidden. | Not implemented. | Not implemented. | Missing |
| PERF-ASSET-003 | Synchronous asset decode on render/UI threads forbidden. | Not implemented. | Not implemented. | Missing |
| PERF-STALL-001 | Stall watchdog thresholds must not be exceeded. | Runtime watchdog + CTest engine_perf_no_modal. | `engine/tests/engine_perf_no_modal_test.c` | Live |
| PERF-STALL-004 | Stall watchdog thresholds must not be exceeded. | Not implemented. | Not implemented. | Missing |
| PERF-PROFILE-001 | PERF3 fixtures emit telemetry and required metrics. | CTest engine_perf_budget_fixture + perf_budget_check. | `engine/tests/engine_perf_budget_test.c`, `tools/ci/perf_budget_check.py` | Live |
| PERF-FID-005 | Forbidden fidelity degradation forbidden. | Not implemented. | Not implemented. | Missing |
| PERF-STREAM-001 | Streaming budgets must not be exceeded. | Not implemented. | Not implemented. | Missing |
| PERF-BUDGET-001 | Tier performance budgets must not be exceeded. | Not implemented. | Not implemented. | Missing |
| PERF-BUDGET-002 | Tier performance budgets must not be exceeded. | perf_budget_check. | `tools/ci/perf_budget_check.py` | Live |
| PERF-NOMODAL-001 | Modal loading forbidden. | Not implemented. | Not implemented. | Missing |

### Scale

| ID | Description | Enforced By | Where Implemented | Status |
| --- | --- | --- | --- | --- |
| SCALE-SHARD-001 | Single-writer shard authority required. | Not implemented. | Not implemented. | Missing |
| SCALE-MSG-002 | Cross-shard interaction via scheduled messages only. | Not implemented. | Not implemented. | Missing |
| SCALE-CLOCK-003 | Per-shard clocks or drift forbidden. | Not implemented. | Not implemented. | Missing |
| SCALE-INT-001 | Update paths must accept InterestSet parameter. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| SCALE-INT-002 | Camera/view-driven activation forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| SCALE-FID-001 | Direct spawn/despawn outside fidelity interfaces forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| SCALE-FID-002 | Ad-hoc approximation/LOD shortcuts forbidden. | Static scan (arch_checks). | `tools/ci/arch_checks.py` | Partial |
| SCALE-INT-TEST-001 | Interest set determinism, latency, hysteresis. | CTest dominium_interest. | `game/tests/interest/dom_interest_tests.c` | Live |
| SCALE-FID-TEST-001 | Fidelity continuity and provenance preservation. | CTest dominium_fidelity. | `game/tests/fidelity/dom_fidelity_tests.c` | Live |

### Data

| ID | Description | Enforced By | Where Implemented | Status |
| --- | --- | --- | --- | --- |
| DATA-SCHEMA-001 | Missing schema version metadata forbidden. | Data validator test only (no pack scan). | `engine/tests/engine_data_validate_test.c` | Partial |
| DATA-SCHEMA-002 | Invalid schema version progression forbidden. | Data validator test only (no pack scan). | `engine/tests/engine_data_validate_test.c` | Partial |
| DATA-VALID-001 | Structural validation failure forbidden. | CTest engine_data_validate. | `engine/tests/engine_data_validate_test.c` | Partial |
| DATA-VALID-002 | Determinism/perf schema violation forbidden. | CTest engine_data_validate. | `engine/tests/engine_data_validate_test.c` | Partial |
| DATA-MIGRATE-001 | Missing migration for major bump forbidden. | CTest engine_data_validate. | `engine/tests/engine_data_validate_test.c` | Partial |

## B) Enforcement Coverage Audit

- CMake boundary locks exist for `domino_engine` and `dominium_game`, but there are no explicit guards for `client/`, `server/`, `tools/`, `launcher/`, or `setup/` target links.
- `scripts/verify_includes_sanity.py` is wired to engine and game builds only; it does not run for client/server/tools.
- `tools/ci/arch_checks.py` covers many critical rules but is not executed by CI (no `check_arch` step).
- Determinism gates (step/batch, replay, lockstep, hash partition invariance) are documented but have no implementation.
- Rendering enforcement rules are documented but have no CI scans or tests.
- Data validation exists as tests, but CI does not validate core data packs via `data_validate`.
- PERF1 no-modal IO ban and stall watchdog are implemented and tested; PERF0 streaming and shader/asset bans are not.

## C) CI Coverage Audit

Checklist of CI coverage for Phase-1 rules (from `.github/workflows/ci.yml`):

| CI Stage | Checks Executed | Prompt Origin | Failure Mode |
| --- | --- | --- | --- |
| Configure | `scripts/verify_cmake_no_global_includes.py`, CMake target link assertions, engine public include assertion | ENF1, ENF2 | Configure failure |
| Build | `scripts/verify_includes_sanity.py` (engine/game), compile-time include visibility | ENF1, ENF2 | Build failure |
| Test | `engine_det_order`, `engine_perf_no_modal`, `engine_due_sched`, `engine_perf_budget_fixture`, `engine_perf_budget_check`, `engine_data_validate`, `dominium_interest`, `dominium_fidelity`, `dominium_epistemic`, `dominium_epistemic_ui_bypass` | DET2, PERF1-3, SCALE1-2, DATA1, EPIS0 | CTest failure |

Missing CI wiring:
- `tools/ci/arch_checks.py` (ARCH-INC-001/002, DET-FLOAT-003, PERF-GLOBAL-002, SCALE-INT-001/002, SCALE-FID-001/002, UI-BYPASS-001, EPIS-API-002, BUILD-GLOBAL-001 link_directories).
- Determinism gate suites (DET-G* and DET-GATE-*).
- Rendering checks (REND-*).
- Sharding/spec lint checks (SCALE-SHARD-001, SCALE-MSG-002, SCALE-CLOCK-003).
- Streaming/asset/shader no-modal checks (PERF-MODAL-001, PERF-SHADER-002, PERF-ASSET-003, PERF-STREAM-001).

## D) Documentation Consistency Audit

Conflicts and mismatches:
- `docs/DETERMINISM_ENFORCEMENT.md` uses DET-GATE-* IDs while `docs/DETERMINISM_GATES.md` uses DET-G1..DET-G6. The CI matrix currently lists both.
- `docs/ARCH_BUILD_ENFORCEMENT.md` references `DET-FLOAT-001`, but the implemented ID is `DET-FLOAT-003`.
- `docs/ARCH_BUILD_ENFORCEMENT.md` states CI runs `python tools/ci/arch_checks.py`, but `.github/workflows/ci.yml` does not invoke it.
- `BUILD-GLOBAL-001` claims coverage of link_directories, but the only CI-wired script checks include_directories.

## E) Cross-Rule Interaction Safety

| Interaction | Why It Is Safe | What Breaks It | Enforcement |
| --- | --- | --- | --- |
| Interest Sets x Event-Driven Stepping | Due scheduler + interest set tests bound work to relevant IDs. | Global sweeps or camera-driven activation. | `engine_due_sched` and `dominium_interest` tests, but static scans are not CI-wired. |
| Fidelity Projection x Determinism | Fidelity tests preserve counts/inventory/provenance. | Ad-hoc spawn/despawn or unordered iteration. | `dominium_fidelity` test plus DET-ORDER tests, but fidelity static scans are not CI-wired. |
| Rendering x Simulation Hashes | Render ownership is documented and render must not touch sim state. | Renderer writes to authoritative state or hashes. | REND-DET-001 is not implemented. |
| UI x Epistemic Boundary | EIL tests and UI bypass compile check exist. | UI calling sim APIs or including world headers in real UI files. | EPIS-CAP-003 and EPIS-BYPASS test exist, but EPIS-API-002 scan is not CI-wired. |
| Data Validation x Mod Support | Validator tests exist for schema rules. | Mods bypassing schema validation or missing migrations. | DATA tests exist, but no CI step validates data packs. |
| Sharding x Time Warp | ACT single time and message scheduling are defined. | Per-shard clocks or direct cross-shard reads. | SCALE-SHARD/MESSAGE/CLOCK checks are not implemented. |

## F) Bypass Resistance Audit

| Bypass Attempt | Why It Fails | Enforcement That Stops It |
| --- | --- | --- |
| Game includes engine/modules via relative path. | Not blocked by include paths alone. | Requires `tools/ci/arch_checks.py` (not CI-wired). |
| Client links tools or launcher targets. | No explicit CMake guard. | None (missing enforcement). |
| Authoritative code uses unordered_map and iterates. | Static scan exists but is not CI-wired. | `tools/ci/arch_checks.py`. |
| Renderer backend code added under client/. | No render directory scan in CI. | None (REND-DIR-* missing). |
| UI calls dom_time_* or sim APIs. | Static scan exists but is not CI-wired. | `tools/ci/arch_checks.py`. |
| link_directories() reintroduced. | Configure script checks include_directories only. | None in CI unless arch_checks is added. |

## G) Future Prompt Compatibility

Phase-1 rules are compatible with planned future phases:
- LIFE0/LIFE1: Determinism and provenance rules support continuity.
- CIV0+: Interest sets and event-driven stepping do not block population or institutions.
- Rendering Phase 8: Render canon and RenderCaps spec are compatible with future backends.
- MMO sharding: Sharding authority model aligns with server-auth and ACT time.
- Tooling and mods: Schema governance and validation enable forward-compatible content pipelines.

## Conclusion

Phase-1 is NOT complete. Critical enforcement gaps remain, especially around CI wiring of static scans,
determinism gates, rendering rules, and sharding policy checks. These must be closed before declaring
Phase-1 complete and resuming gameplay feature work.
