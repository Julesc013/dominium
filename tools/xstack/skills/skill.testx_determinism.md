Status: TEMPLATE
Version: 1.0.0
Last Reviewed: 2026-02-14
Compatibility: Use with deterministic policy docs and canon v1.0.0.

# Skill Template: testx_determinism

## Purpose
Plan and execute determinism-focused TestX coverage for authoritative simulation changes.

## Constraints
- No flaky tolerance for determinism gates.
- Do not weaken determinism checks to pass unstable code.
- Keep test additions targeted to changed invariant surfaces.
- Avoid over-engineered fixture expansion beyond required invariant coverage.

## Checklist
1. Identify affected determinism invariants (ordering, reduction, RNG, replay, partitions).
2. Confirm named RNG streams are used for authoritative randomness.
3. Confirm thread-count invariance expectations are test-covered.
4. Run or define step-vs-batch and replay equivalence checks.
5. Validate required hash partitions:
   - `HASH_SIM_CORE`
   - `HASH_SIM_ECON`
   - `HASH_SIM_INFO`
   - `HASH_SIM_TIME`
   - `HASH_SIM_WORLD`
6. Record allowed non-gating divergence (`HASH_PRESENTATION`) explicitly.
7. Publish failure artifact expectations (event log, queue snapshot, hash diffs).
8. Run Observation Kernel determinism and lens-gating checks in STRICT:
   - `testx.observation.determinism`
   - `testx.observation.lens_forbidden`
   - `testx.observation.entitlement_missing`
9. Verify renderer boundary regressions are blocked:
   - `testx.repox.renderer_truth_boundary`
10. Run deterministic profile checks:
   - `tools/xstack/run fast`
   - `tools/xstack/run full --shards 2 --shard-index 0`
   - `tools/xstack/run full --shards 2 --shard-index 1`
   - inspect `tools/xstack/out/full/latest/report.json`
11. Run SRZ invariance checks in STRICT:
   - `testx.srz.hash_anchor_replay`
   - `testx.srz.logical_two_shard_consistency`
   - `testx.srz.worker_invariance`
   - `testx.srz.target_shard_invalid_refusal`
12. Verify shard status tooling output for deterministic ownership:
   - `tools/xstack/srz_status saves/<save_id>/session_spec.json`
13. Run packaging determinism gates:
   - `tools/setup/build --bundle bundle.base.lab --out dist`
   - `tools/launcher/launch run --dist dist --session saves/<save_id>/session_spec.json --script tools/xstack/testdata/session/script.region_traversal.fixture.json`
   - verify `canonical_content_hash`, `pack_lock_hash`, and final `composite_hash` stability across repeated runs.

## Output Format
- Invariant coverage matrix (what was tested, what remains).
- Gate results summary.
- Any determinism risk with mitigation TODOs.

## Example Invocation
```text
Use skill.testx_determinism after changing scheduling:
- run FAST determinism gates
- compare hashes across thread profiles t1/t2/t8
- report replay equivalence outcome
Run:
- tools/xstack/run fast
- tools/xstack/run strict
```

## TODO
- Add deterministic artifact path template for desync bundles.
- Add canonical command snippets once run wrappers are standardized.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/architecture/deterministic_parallelism.md`
- `docs/ci/DETERMINISM_TEST_MATRIX.md`
- `docs/policies/DETERMINISM_HASH_PARTITIONS.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/truth_perceived_render.md`
- `docs/architecture/observation_kernel.md`
- `docs/architecture/deterministic_packaging.md`
- `docs/architecture/setup_and_launcher.md`
