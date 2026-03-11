Status: BASELINE
Last Reviewed: 2026-03-11
Version: 1.0.0
Scope: LIB-7 deterministic stress/proof/regression envelope for installs, instances, saves, packs, providers, and export/import.

# LIB Final Baseline

## Stress Results Summary
Deterministic LIB-7 regression lock established at `data/regression/lib_full_baseline.json`.

Fixed seed scenario:
- `scenario.lib7.635f8375baecd938` (`seed=71007`, `slash_mode=forward`) -> `result=complete`
- repeated-run projection hash: `6e48d97ec870ff9fc7436bce9caf3d643363bd1fd397edd931efb2ed18ae1506`
- stress report fingerprint: `ae90db9a983a64f833d28719afe10bcd018fbc362e3c64cc99beec1b136128e1`

Regression lock update control:
- `required_commit_tag = LIB-REGRESSION-UPDATE`

## Bundle + Import Envelope
Pinned bundle hashes:
- `instance_linked = 4faca3d5a82cda3663caa96a5069f87f89f4e94c99abb15f24ebe3653a990e3c`
- `instance_portable = af4bbbc2908cc40419260a633add35459e61449c790febfd923f51b4123b0e4d`
- `save = 55c9d255890cf34506e1271b3e675261c5212858327fb28acb1ce1fc9d8d5e37`
- `pack = 5756dc708fa4c237a05c8f5f4ccfe9b7cce1b5c6083a22300301d172dfec3d97`

Deterministic envelope assertions:
- repeated runs keep identical projection hashes
- forward- and backslash-shaped scenarios keep identical bundle hashes
- external-temp and in-repo workspaces keep identical bundle hashes
- `tool_verify_bundle` returns `result=complete` for instance, save, and pack bundles
- import previews complete for linked instance, portable instance, save, and pack bundles

## Provider + Save Decisions
Provider policy outcomes:
- strict policy refuses ambiguity with `refusal.provides.ambiguous`
- explicit policy completes with pinned provider `fork.official.dominium.dem.primary.alt.demx`
- anarchy policy completes deterministically with the same provider and `selection_logged = true`

Save/open policy outcomes:
- same-install save open completes without degrade
- build mismatch save open refuses when read-only fallback is not allowed
- contract-bundle mismatch save open degrades to read-only with `save_contract_bundle_mismatch`
- launcher preflight records `inspect-only` for the read-only save case

Pinned decision-log fingerprints:
- `pack_verify_official = 384401cc1c8026f294903eacae50c231ed2d13bc78d1b8bd628c96dccf03b915`
- `provider_resolution_strict = 3f47fe7a09117b3baeeba828d9a90bca7013794f2c4f7a1354115a46f5a663af`
- `save_open_contract_mismatch = ea8e5e50f3af4657de7c3e8fbd10e626bbee620977b5b22ab339308e320c8b06`

## Metrics + Refusals
Bundle metrics:
- linked instance: `20` items, `37530` bytes, `313` logical time units
- portable instance: `25` items, `58133` bytes, `479` logical time units
- save: `21` items, `27999` bytes, `239` logical time units
- pack: `8` items, `9839` bytes, `84` logical time units

Refusal counts:
- `refusal.provides.ambiguous = 3`
- `refusal.pack.conflict_in_strict = 1`
- `refusal.save.build_mismatch = 1`

## Gate Snapshot
- RepoX STRICT: REFUSAL in repository-wide strict lane due pre-existing non-LIB findings; LIB-7 invariants and regression lock are wired
- AuditX STRICT: PASS (`scan_complete`)
- TestX (LIB-7 required subset): PASS
  - `test_lib_stress_scenario_deterministic`
  - `test_export_import_roundtrip_hash_match`
  - `test_bundle_hash_independent_of_workspace_root`
  - `test_provider_resolution_policies`
  - `test_strict_refuses_ambiguous_provides`
  - `test_save_read_only_fallback_logged`
  - `test_cross_platform_lib_hash_match`
- stress harness: PASS (`build/lib/lib_stress_report_gate.json`)
- strict build: REFUSAL due pre-existing repository-wide `mod_pack_builder` / `mod_pack_validator` runtime-library mismatch

## Readiness For MVP-GATE / RELEASE-DIST
- multi-install, instance, save, provider, and bundle lifecycles are covered by deterministic stress: complete
- bundle proof/replay surfaces are pinned and replayable offline: complete
- read-only fallback and strict refusal paths are logged and regression-locked: complete
- cross-platform bundle hash stability is covered in both harness and TestX: complete
- regression lock governance with explicit update tag is in place: complete
