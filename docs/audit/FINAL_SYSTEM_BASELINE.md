Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Scope: Prompt 20 Phase 7 hardened baseline sweep
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, and `AGENTS.md`.

# Final System Baseline

## Gate Sweep Results

| Gate | Command | Result |
|---|---|---|
| RepoX strict | `python tools/xstack/repox/check.py --repo-root . --profile STRICT` | `pass` (`findings=0`) |
| AuditX full | `python tools/auditx/auditx.py scan --repo-root . --format both` | `scan_complete` (`findings=746`) |
| TestX strict full | `python tools/xstack/testx_all.py --repo-root . --profile STRICT --cache on` | `pass` (`selected_tests=93`) |
| Strict build/profile | `python tools/xstack/run.py strict --repo-root . --cache on` | `pass` |
| UI bind check | `python tools/xstack/ui_bind.py --repo-root . --check` | `complete` (`checked_windows=7`) |
| Packaging verification | `python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.final20.verify --cache on` | `complete` |
| Impact graph rebuild | `python tools/dev/dev.py --repo-root . impact-graph --out build/impact_graph.json` | `complete` |
| Determinism envelope test | `python tools/xstack/testx_all.py --repo-root . --profile STRICT --cache off --subset test_determinism_envelope_full_stack` | `pass` |

## Canon Conformance Summary

1. Process-only mutation and session-stage invariants pass strict RepoX enforcement.
2. Observation and renderer boundaries remain enforced; no strict violations.
3. No mode-flag bypasses or hardcoded domain/contract-token violations surfaced in strict RepoX.
4. Command routing, authority gating, and lockfile enforcement remain active across strict TestX and strict xstack profile.

## Determinism Envelope Summary

Canonical anchors captured from strict run and packaging verification:

1. `composite_hash_anchor`:
   - `16d6f5b6333bb1cbb5a5e8670c95095ce795967afb1318829afa4c5060fc12b7`
2. `pack_lock_hash`:
   - `83e022ebf2ffc2686d0c2b8854b24b3febd5c80edbe06b3f4a0931575d8eb1b8`
3. Packaging canonical hashes:
   - `canonical_content_hash`: `fa5957dea9014c8cba6f258b33e9af54f5780b50d13a7760e96b548e6d6aeb02`
   - `manifest_hash`: `9a3952053d742764b2c5097f0d2db85b7dc1c1dd2d42c9b7b0dae8937b13b7ad`
   - `lockfile_hash`: `e8565fb99ed1b4f1458d6305b6bb077016fc81d939ce81c70306367f3a30f91a`

Registry hash baseline:

- `activation_policy_registry_hash`: `6398ffcaf26b22584f69f629ab900dd5b724a0100f8e1b1152b255ed3c4cf2f9`
- `astronomy_catalog_index_hash`: `f8f4b532336e24efa06526b48ab53edc3c5caa0daa3f8ec49b37a96e5b8b2415`
- `budget_policy_registry_hash`: `1f9f967af6080f281bd3bb3ea465d154d910a0db3612be4149ce8d96afbd67d4`
- `domain_registry_hash`: `b6bca2ac2c5db685ff362383f26cc1530e90e96522f33f9133c7db4f38528537`
- `ephemeris_registry_hash`: `694eddbd245046e5e0a16bc45555ed00f6bc9f3d13104136c60b5d259ad176e8`
- `experience_registry_hash`: `43b10356eb61ff3840b0536bd37b9b01fbc65a5384c292f0a212c55844f78052`
- `fidelity_policy_registry_hash`: `f1f9a8f9eac54bc7706f328bab3136396d2c59a016feb62638993e01fad17de3`
- `law_registry_hash`: `be2f8fcfde47fdbab66caeb08de747ec7c2b9ab93264792d8de286828c74d106`
- `lens_registry_hash`: `ea487768e8912b1036ee7005e8f7c87c814a404312148493d9827514c9324b59`
- `site_registry_index_hash`: `bd58943c4947f58fe1598786714634499ed18bb1570c34ba72edaef6f7973adb`
- `terrain_tile_registry_hash`: `fe003e69d5339172ebf15bc16c18bdc5fcb7b19b21ebb6e4472cf738306ed529`
- `ui_registry_hash`: `0d3f31c76a15c9c481b29dcb2b3d4556c944d1ba8b1d4a710cb83c6202e94b05`
- `worldgen_constraints_registry_hash`: `5d3fed78f9bfd0698e2d1f3b783308e1bbb83b998296e7d5fcb8a6c56d1661f2`

## Regression / Drift Status

1. Observer regression lock remains present (`data/regression/observer_baseline.json`) and strict regression tests pass.
2. No strict-gating drift detected in RepoX/TestX/xstack strict.
3. AuditX semantic findings remain visible and non-gating by policy.

## Domain / Contract Foundation Summary

1. Domain, contract, and solver registries remain present and validated by strict TestX/RepoX checks.
2. Solver-domain-contract bindings remain structurally enforced; no unbound solver failures in strict gate sweep.
3. Registry-driven extensibility remains active without introducing new primitives.

## Impact Graph Snapshot

1. Path: `build/impact_graph.json`
2. Graph hash: `349e21310fd89b0eb69a3b190601f6678f9be27582fdf512a73e8fb351dc0b2b`
3. Node count: `2021`
4. Edge count: `4396`

## TODO-BLOCKED (Non-Gating)

1. `TODO-BLOCKED-AUDITX-CANON-DRIFT`:
   - High volume of semantic canon-drift findings remains and requires a dedicated docs-harmonization pass.
2. `TODO-BLOCKED-AUDITX-SCHEMA-SHADOWING`:
   - Legacy-path schema shadowing warnings remain and require compatibility-aware cleanup planning.

## Cross-References

- `docs/audit/CANON_CONFORMANCE_REPORT.md`
- `docs/audit/DETERMINISM_ENVELOPE_REPORT.md`
- `docs/audit/CROSS_SYSTEM_CONSISTENCY_MATRIX.md`
- `docs/audit/DEVELOPER_ACCELERATION_BASELINE.md`
- `docs/architecture/EXTENSION_MAP.md`
