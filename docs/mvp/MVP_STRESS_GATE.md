# MVP Stress Gate

Purpose: define the deterministic full-stress gate that must pass before release governance and distribution.

## Scope

The MVP stress gate executes the release-lane stress envelope in this stable order:

1. GEO-10 stress
2. LOGIC-10 stress
3. PROC-9 stress
4. SYS-8 stress
5. POLL-3 stress
6. EARTH-9 stress
7. CAP-NEG-4 stress
8. PACK-COMPAT verification stress across multiple pack sets
9. LIB-7 stress
10. SERVER stress with multiple loopback clients, attach/detach cycles, and proof-anchor emission under load

## Seed Policy

- The canonical gate seed is `70101`.
- Established subsystem suites keep their canonical suite-local seeds.
- Gate-owned orchestration surfaces derive only deterministic naming and artifact paths from the gate seed.
- Baseline updates require `MVP-STRESS-REGRESSION-UPDATE`.

## Required Proof Checks

The proof verifier must confirm:

- proof anchors stable across runs
- negotiation records stable across runs
- contract bundle pins remain explicit and unchanged
- runtime pack locks and pack-compat verification locks remain stable
- PROC compaction replay matches
- selected cross-thread hashes match exactly

## Acceptable Degrade Behavior

- deterministic degrade behavior only
- Only deterministic, explicitly recorded degrade behavior is allowed.
- No silent degrade is allowed.
- The default gate lane must report `gate_degrade_event_count = 0`.
- Suite-local deterministic degradation that is already part of a governed suite envelope may exist, but it must remain explicit, bounded, and fingerprinted inside that suite report.

## Acceptance Thresholds

The gate passes only when all of the following are true:

- every required suite reports pass or complete according to its governed result contract
- proof verification reports `complete`
- `unexpected_refusal_count = 0`
- known refusal counts are pinned in the regression lock only for suites whose scenario matrices intentionally exercise refusal paths
- cross-thread hashes match exactly for the selected suites
- runtime pack lock hash and pack-compat verification lock hashes match the regression lock
- server proof-anchor hashes and contract-bundle pins match the regression lock

## Outputs

The gate writes deterministic artifacts to:

- `build/mvp/mvp_stress_report.json`
- `build/mvp/mvp_stress_hashes.json`
- `build/mvp/mvp_stress_proof_report.json`
- `data/regression/mvp_stress_baseline.json`
- `docs/audit/MVP_STRESS_FINAL.md`
