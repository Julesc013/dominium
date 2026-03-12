Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, RS-5, MAT-0..MAT-9.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Performance And Scale Strategy (MAT-10)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define MAT-10 scale guarantees for worst-case factory-planet workloads while preserving deterministic outcomes and invariant correctness.

## No Lag Spikes Contract
In MAT architecture, "no lag spikes" means:
- Per-tick authoritative work is bounded by declared deterministic cost envelopes.
- When demand exceeds envelopes, deterministic degradation/refusal is applied.
- Correctness and invariants are preserved; only fidelity/throughput are reduced.

## Worst-Case Scenario Class
Stress baseline models:
- many factory complexes distributed planet-wide
- dense logistics manifests and active construction projects
- many players requesting micro ROI and constant inspection
- historical and reenactment demand under the same tick budgets

No global micro simulation is required.

## Deterministic Degradation Priorities
When budgets are exceeded, MAT workloads degrade in fixed order:
1. reduce inspection fidelity (`micro -> meso -> macro`)
2. cap micro materialization deterministically
3. reduce construction parallelism
4. batch logistics processing in deterministic subsets
5. defer low-priority maintenance scheduling
6. refuse new project/manifest creation if still required

Degradation is explicit run-meta data, not hidden fallback.

## Bounded Work Policies
- inspection:
  - cache snapshots by deterministic input hash anchors
  - reuse cached artifacts instead of recomputation
- materialization:
  - enforce max micro parts per ROI
  - deterministic truncation order
- logistics:
  - cap manifests processed per tick
  - deterministic order by manifest ID
- construction:
  - cap active/parallel step progression deterministically
- decay and reenactment:
  - compute from deterministic cost units and bounded per-tick work plans

## Time Warp
Large `Δt_sim` must remain deterministic and bounded:
- cost scales by deterministic bounded factor or closed-form integration
- no wall-clock coupling
- same inputs produce same cost/degradation stream and hash anchors

## Multiplayer Fairness
Under policies A/B/C:
- equal-share inspection arbitration is deterministic
- allocations are stable under sorted peer/player ordering
- proof/replay anchors remain stable across identical runs

## Regression Locks
MAT scale regressions are tracked in `data/regression/mat_scale_baseline.json`:
- deterministic degradation ordering fingerprints
- short-run per-tick hash anchor stream
- inspection cache hit pattern bounds

Baseline updates require explicit `MAT-SCALE-REGRESSION-UPDATE` commit tagging.
