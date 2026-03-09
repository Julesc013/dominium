Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`, `docs/mvp/MVP_RUNTIME_BUNDLE.md`, and `docs/mvp/MVP_INSTALL_LAYOUT.md`.

# MVP Runtime Baseline

## Bundle Contents

- Canonical runtime bundle: `profile.bundle.mvp_default`
- Canonical profile bundle hash: `2f1d1fa1afacd6d315ecd34126226e3cff2b694b81f5bd68e5a756bd3b9931f3`
- Canonical pack lock: `pack_lock.mvp_default`
- Canonical pack lock hash: `a9f8a220673736ccf8ba226425958a2428ba9d5a730fb98025b60f265cfa6f06`
- Canonical generator version lock: `gen.v0_stub`
- Canonical install-visible packs:
  - `pack.base.procedural`
  - `pack.sol.pin_minimal`
  - `pack.earth.procedural`

The default bundle freezes:

- GEO topology `geo.topology.r3_infinite`
- GEO metric `geo.metric.euclidean`
- GEO partition `geo.partition.grid_zd`
- GEO projections `geo.projection.perspective_3d` and `geo.projection.ortho_2d`
- realism `realism.realistic_default_milkyway_stub`
- physics `physics.default_realistic`
- law `law.lab_freecam` (dev) and `law.softcore_observer` (release stub)
- epistemic `epistemic.admin_full` (dev) and `epistemic.diegetic_default` (release stub)
- compute `compute.default`
- coupling `coupling.default`
- overlay `overlay.default`
- logic `logic.default`

## Session And Install Baseline

- Canonical SessionSpec template: `data/session_templates/session.mvp_default.json`
- Required session fields present:
  - `universe_id`
  - `universe_seed`
  - `generator_version_id`
  - `realism_profile_id`
  - `profile_bundle_id`
  - `pack_lock_hash`
  - `authority_context`
  - `budget_policy_id`
  - `fidelity_policy_id`
- Dev seed policy: explicit `--seed` or deterministic fallback `0`
- Release seed policy: explicit seed required
- Named RNG stream roots derive from `universe_seed + generator_version_id`

Canonical dist skeleton now ships:

- `dist/bin/dominium_client` and `dist/bin/dominium_server`
- `dist/packs/base/pack.base.procedural/pack.alias.json`
- `dist/packs/official/pack.sol.pin_minimal/pack.alias.json`
- `dist/packs/official/pack.earth.procedural/pack.alias.json`
- `dist/profiles/bundle.mvp_default.json`
- `dist/locks/pack_lock.mvp_default.json`
- `dist/saves/`
- `dist/logs/`

Entrypoint expectations:

- CLI/runtime bootstrap accepts `--seed`, `--profile_bundle`, `--pack_lock`, and `--teleport`
- Client defaults to GUI freecam bootstrap
- Server defaults to headless bootstrap
- Release authority refuses omitted seeds

## Validation Snapshot

- TestX targeted MVP subset: PASS on 2026-03-09
  - `test_bundle.mvp_default_valid`
  - `test_pack_lock_hash_stable`
  - `test_session_template_contains_pack_lock`
  - `test_dist_layout_contains_required_dirs`
  - `test_cli_parses_seed_and_bundle`
- RepoX targeted MVP checks: PASS on 2026-03-09
  - `INV-MVP-PACKS-MINIMAL`
  - `INV-PACK-LOCK-REQUIRED`
  - `INV-PROFILE-BUNDLE-REQUIRED`
- RepoX STRICT full-repo run: FAIL on 2026-03-09 due pre-existing repository-wide governance drift
  - dominant blocker classes remained `INV-DOC-STATUS-HEADER`, `INV-CANON-INDEX`, `INV-REPOX-STRUCTURE`, `INV-TOOL-VERSION-MISMATCH`, and stale identity artifacts
  - runtime-bundle enforcement outputs were redirected to `build/mvp1/repox/`
- AuditX full strict scan: PASS by promotion semantics on 2026-03-09
  - scan output: `2264` findings
  - promoted strict blockers: `0`
  - outputs written under `build/mvp1/auditx/`
- Strict build lane: BLOCKED on 2026-03-09
  - `cmake --build --preset msvc-verify`
  - environment lacks `Visual Studio 18 2026`, so the configured strict preset cannot resolve its generator

## Topology Map

- `docs/audit/TOPOLOGY_MAP.json` regenerated on 2026-03-09
- deterministic fingerprint: `54a5a4bb801bdcba905af14f60f043c5c74a8a1664ac75fde2f7daa0e17e91f9`
- node count: `4315`
- edge count: `9089`

## MW-0 Readiness

The v0.0.0 runtime substrate is ready for MW-0 integration in the narrow sense intended by MVP-1:

- one canonical default runtime bundle exists
- one canonical pack lock exists
- one canonical SessionSpec template exists
- one canonical portable dist skeleton exists
- bootstrap surfaces are deterministic and versioned

MW-0 may now layer Milky Way procedural content onto this runtime baseline without reopening bundle identity, pack lock semantics, or install layout for v0.0.0.
