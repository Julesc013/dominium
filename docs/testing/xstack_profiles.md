Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `tools/xstack/run.py` and subsystem modules under `tools/xstack/{controlx,repox,auditx,testx,performx,compatx,securex}/`.

# XStack Profiles v1

## Purpose
Define deterministic profile behavior for the stable entrypoint `tools/xstack/run`.

## Schema References
- `schemas/session_spec.schema.json`
- `schemas/bundle_profile.schema.json`
- `schemas/registry_outputs.schema.json`

## Entrypoint
- `tools/xstack/run fast`
- `tools/xstack/run strict`
- `tools/xstack/run full --shards N --shard-index I --cache on|off`
- Implementation module: `tools/xstack/run.py`

Windows wrapper:
- `tools/xstack/run.cmd ...`

Cross-platform launcher:
- `tools/xstack/run` (shebang wrapper)

Related lifecycle commands:
- `tools/xstack/bundle_list`
- `tools/xstack/bundle_validate <bundle.json>`
- `tools/xstack/session_create --save-id <id> --bundle bundle.base.lab`
- `tools/xstack/session_boot saves/<save_id>/session_spec.json [--compile-if-missing on|off]`
- `tools/xstack/session_script_run saves/<save_id>/session_spec.json <script.json> [--workers N] [--logical-shards N]`
- `tools/xstack/srz_status saves/<save_id>/session_spec.json`
- `tools/setup/build --bundle bundle.base.lab --out dist`
- `tools/launcher/launch run --dist dist --session saves/<save_id>/session_spec.json`

## Deterministic Step Order
Each profile executes deterministic step IDs:
1. `01.compatx.check`
2. `02.bundle.validate`
3. `03.pack.validate`
4. `04.registry.compile`
5. `05.lockfile.validate`
6. `06.session_spec.fixture.validate`
7. `07.session_boot.smoke`
8. `08.repox.scan`
9. `09.auditx.scan`
10. `10.testx.run`
11. `11.performx.check`
12. `12.securex.check`
13. `13.packaging.verify`

`duration_ms` is run-meta and does not affect pass/fail/refusal semantics.

## FAST
Scope:
- CompatX schema/version/example checks (strict top-level enabled)
- Bundle profile validation (`schemas/bundle_profile.schema.json`)
- Pack manifest loading and contribution path checks
- Registry compile smoke via `tools/xstack/registry_compile/compiler.py`
  - includes policy registries: activation/budget/fidelity
- Lockfile schema/hash validation
- SessionSpec fixture validation (`tools/xstack/testdata/session/session_spec.fixture.json`)
- Session boot/shutdown smoke (`save.xstack.smoke.fast`)
- SRZ schema checks:
  - `schemas/srz_shard.schema.json`
  - `schemas/intent_envelope.schema.json`
- RepoX minimal deterministic pattern scan
- AuditX minimal drift checks (packs/registries/docs)
- TestX tool-suite FAST selection (`tools/xstack/testx/tests/`)
- PerformX and SecureX placeholder checks
- Packaging smoke check:
  - deterministic dist build/validation via `tools/setup/build` backend (`tools/xstack/packagingx`)

## STRICT
Scope:
- Everything in FAST
- CompatX strict unknown-field guard checks across schema examples
- Strict lockfile vs bundle composition check (`resolved_packs` equivalence)
- RepoX strict mode-flag and placeholder checks
- RepoX strict renderer boundary checks:
  - `repox.renderer_truth_import`
  - `repox.renderer_truth_symbol`
- AuditX strict doc-schema version linkage heuristics
- TestX runs all `tools/xstack/testx/tests/test_*.py`
  - includes Observation Kernel determinism and lens-gating refusal tests.
  - includes process-driven camera/time script determinism and authority/law gating refusal tests.
  - includes region-management traversal determinism, budget exceed behavior, conservation checks, and worker-count invariance stubs.
  - includes SRZ structural/hash tests:
    - `testx.srz.init`
    - `testx.srz.hash_anchor_replay`
    - `testx.srz.logical_two_shard_consistency`
    - `testx.srz.worker_invariance`
    - `testx.srz.target_shard_invalid_refusal`
- Strict packaging validation:
  - two deterministic dist builds compared for canonical content hash parity
  - launcher lockfile enforcement refusal checks
  - full lab build validation replay (dist -> launch -> scripted traversal -> composite hash match)

## FULL
Scope:
- Everything in STRICT
- Deterministic TestX sharding:
  - `--shards N`
  - `--shard-index I`
- TestX cache control:
  - `--cache on` (default)
  - `--cache off`
- FULL bounds come from sharding and cache usage, not hardcoded runtime timeouts.

## Exit Codes
- `0` success
- `1` failure (test/invariant failure)
- `2` refusal (policy/contract violation)
- `3` internal error (tool crash)

## Artifacts
Primary report artifact:
- `tools/xstack/out/<profile>/latest/report.json`

Companion summary:
- `tools/xstack/out/<profile>/latest/summary.txt`

Per-step findings/details:
- `tools/xstack/out/<profile>/latest/steps/*.json`

Registry and lockfile artifacts referenced by report:
- `build/registries/*.json`
- `build/lockfile.json`

Packaging artifacts:
- `build/dist.smoke.<profile>/`
- `build/dist.lab_validation.a/`
- `build/dist.lab_validation.b/`

Session smoke artifacts:
- `saves/save.xstack.smoke.<profile>/session_spec.json`
- `saves/save.xstack.smoke.<profile>/universe_identity.json`
- `saves/save.xstack.smoke.<profile>/universe_state.json`
- `saves/save.xstack.smoke.<profile>/run_meta/<run_id>.json`

TestX cache:
- `.xstack_cache/xstack_testx/*.json`

Registry compile cache:
- `.xstack_cache/registry_compile_cache/<cache_key>/`

## Report Contract
`report.json` contains:
- `profile`, `result`, `exit_code`
- `lab_build_status`, `composite_hash_anchor`, `pack_lock_hash`, `registry_hashes`
- deterministic `steps[]` ordering
- per-step:
  - `step_id`
  - `subsystem`
  - `status` (`pass|fail|refusal|error`)
  - `duration_ms` (run-meta)
  - `message`
  - `artifacts[]` (`path`, `sha256`)

## Example Usage
```text
tools/xstack/run fast
tools/xstack/run strict
tools/xstack/run full --shards 2 --shard-index 0 --cache on
tools/xstack/run full --shards 2 --shard-index 1 --cache on
```

## TODO
- Promote RepoX/AuditX heuristics into richer rule registries with severity config.
- Add impact-graph driven FAST test selection with explicit dependency metadata.
- Add FULL multi-shard aggregate report merge artifact.

## Cross-References
- `docs/contracts/versioning_and_migration.md`
- `docs/architecture/registry_compile.md`
- `docs/architecture/lockfile.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
