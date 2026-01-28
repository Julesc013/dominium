# ARCHIVED: Phase 1 Enforcement Summary

Archived: point-in-time enforcement summary.
Reason: Historical snapshot; current enforcement status is tracked elsewhere.
Superseded by:
- `docs/ci/CI_ENFORCEMENT_MATRIX.md`
- `docs/ci/EXECUTION_ENFORCEMENT_CHECKS.md`
- `docs/architecture/INVARIANTS.md`
Still useful: background on early enforcement coverage.

# Phase 1 Enforcement Summary

This summary is a one-page view of what Phase-1 guarantees, forbids, and what later phases can assume.
It reflects the current enforcement wiring in CI and CMake.

## Guarantees (enforced now)
- Engine public headers are restricted to `engine/include` via CMake checks (ARCH-INC-003).
- Engine and game link boundaries are enforced at configure time (ARCH-DEP-001/002).
- Deterministic ordering tests run in CI for event queues, ledger obligations, and interest ordering (DET-ORDER-TEST-001/002/003).
- No-modal-loading enforcement exists for IO ban and stall watchdog (PERF-IOBAN-001, PERF-STALL-001).
- Due-event scheduler tests run (PERF-EVT-001/002).
- Performance telemetry and budget checks run (PERF-PROFILE-001, PERF-BUDGET-002).
- Data validation tests exist for structural, semantic, determinism, performance, and migration paths (DATA-VALID-001/002, DATA-MIGRATE-001).
- Interest set and fidelity projection tests run (SCALE-INT-TEST-001, SCALE-FID-TEST-001).
- Epistemic capability gating test runs and UI bypass compile test exists (EPIS-CAP-003, EPIS-BYPASS-001).

## Forbidden (law)
- Engine and game responsibilities MUST NOT be merged; no top-level source/src directories may be reintroduced.
- Engine internal headers under `engine/modules` are forbidden in game/client/server/tools.
- Non-deterministic math/RNG/time usage is forbidden in authoritative zones.
- Global iteration and modal loading are forbidden in runtime stepping paths.
- Renderer backends must live under `engine/render`, and rendering must never affect sim state.
- UI must not access authoritative world state; all UI must use epistemic capability snapshots.
- Schema changes must be versioned, validated, and migrated or refused.

## Not yet enforced in CI (gaps to close)
- `tools/ci/arch_checks.py` is not invoked by CI; many static scans are not merge-blocking.
- Determinism gate suites (step/batch, replay, lockstep, hash partition) are not implemented.
- Rendering enforcement checks (REND-*) are not implemented.
- Sharding policy checks (SCALE-SHARD-001, SCALE-MSG-002, SCALE-CLOCK-003) are not implemented.
- Streaming/shader/asset no-modal checks are not implemented.
- Data pack validation via `data_validate` is not run in CI.

## Assumptions for future phases
- Engine/game boundary stays locked; `engine/include` remains the only public engine API surface.
- Authoritative math and RNG remain deterministic, and ordering is canonical.
- Interest sets and fidelity skeletons are the only activation and refinement paths.
- Rendering remains deterministic-safe and cannot influence authoritative hashes.
- Schemas remain versioned with explicit migration rules; mods must declare compatible schema versions.
