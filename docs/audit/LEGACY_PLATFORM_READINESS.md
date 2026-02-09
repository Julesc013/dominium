Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Legacy Platform Readiness

## Scope

Validation of declared-not-built legacy targets for governance and deterministic refusal behavior.

## Implemented

- `data/registries/platform_registry.json` declares:
  - `win9x/x86_32/abi:win9x:mingw-legacy`
  - `win16/x86_16/abi:win16:watcom-16`
  - `dos/x86_16/abi:dos:watcom`
  - `dos/x86_32/abi:dos:djgpp`
- Legacy tuples include:
  - `extensions.support_status=declared_not_built`
  - explicit `supported_modes` (`cli`, `tui`)
  - deflate-required compression policy metadata
  - path/memory constraints in extensions metadata.
- Legacy minimal profiles added:
  - `data/profiles/profile.runtime_min.win9x.json`
  - `data/profiles/profile.runtime_min.win16.json`
  - `data/profiles/profile.runtime_min.dos.json`
- Deterministic refusal fixtures added:
  - `tests/distribution/fixtures/legacy_platform_pkg_manifests/*.pkg_manifest.json`
  - refusal marker `REFUSE_PLATFORM_UNSUPPORTED`.

## Test Coverage

- `tests/distribution/distribution_legacy_platform_profiles_tests.py`
  - validates legacy tuple presence and metadata;
  - validates legacy profile resolution refuses deterministically with `REFUSE_CAPABILITY_MISSING`;
  - validates stub manifests carry optional install scope + unsupported refusal code.

## Readiness Statement

- Governance surface: ready.
- Resolver/refusal surface: ready.
- Binary availability: intentionally not built yet (declared-not-built only).
