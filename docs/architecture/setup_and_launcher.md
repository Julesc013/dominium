Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0, `docs/canon/glossary_v1.md` v1.0.0, `schemas/session_spec.schema.json` v1.0.0, and `schemas/bundle_lockfile.schema.json` v1.0.0.

# Setup and Launcher v1

## Purpose
Define deterministic setup/launch tooling for reproducible Lab Galaxy test builds.

## Setup Tool
Command:
- `tools/setup/build --bundle bundle.base.lab --out dist`
- Windows wrapper: `tools/setup/build.cmd`

Responsibilities:
1. Validate requested bundle profile.
2. Compile registries + lockfile through XStack registry compile.
3. Build deterministic dist layout.
4. Validate dist layout hashes and lockfile consistency.
5. Emit deterministic JSON summary.

No duplicated pack-resolution logic is allowed in setup; setup delegates to tooling in `tools/xstack/*`.

## Launcher Tool
Commands:
- `tools/launcher/launch list-builds --root dist`
- `tools/launcher/launch list-saves --saves-root saves`
- `tools/launcher/launch run --dist dist --session saves/<save_id>/session_spec.json [--script <script.json>]`
- Windows wrapper: `tools/launcher/launch.cmd`

Responsibilities:
1. Validate dist lockfile + registries.
2. Validate SessionSpec schema and bundle compatibility.
3. Enforce lockfile match (`pack_lock_hash` and registry hash map) before boot.
4. Boot session headless using dist lockfile/registries path overrides.
5. Optionally run deterministic scripted traversal from launcher invocation.

## Lockfile Enforcement
`lockfile_enforcement` is always required for launcher run paths.

Launch path refuses when:
- SessionSpec `pack_lock_hash` differs from dist lockfile (`LOCKFILE_MISMATCH`).
- Session bundle does not match dist lockfile bundle (`PACK_INCOMPATIBLE`).
- Existing save run-meta registry hashes conflict with dist lockfile (`REGISTRY_MISMATCH`).

No implicit migration or upgrade is performed by launcher.

## Deterministic Launch Inputs
Launcher forwards exact paths:
- `--lockfile <dist>/lockfile.json`
- `--registries-dir <dist>/registries`

Session boot/script tooling must consume those paths directly and must not silently fall back to `build/*`.

## Example
```text
tools/setup/build --bundle bundle.base.lab --out dist
tools/launcher/launch run --dist dist --session saves/save.example/session_spec.json --script tools/xstack/testdata/session/script.region_traversal.fixture.json
```

## TODO
- Add minimal interactive launcher UI facade backed by the same deterministic command path.
- Add save selection filters by compatibility hash class.

## Cross-References
- `docs/architecture/deterministic_packaging.md`
- `docs/architecture/session_lifecycle.md`
- `docs/architecture/hash_anchors.md`
- `docs/contracts/refusal_contract.md`
- `docs/testing/xstack_profiles.md`
