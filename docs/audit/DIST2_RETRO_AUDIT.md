Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-2 finalized distribution verification baseline and DIST-3 clean-room distribution runbook

# DIST2 Retro Audit

## Existing Verification Surfaces

- `tools/release/tool_verify_release_manifest.py`
  - already performs offline release-manifest verification
  - verifies artifact presence, content hashes, descriptor hashes, build_id consistency, and optional detached signatures
- `tools/setup/setup_cli.py packs verify`
  - already performs offline pack verification against bundled store content
  - expected to work in portable mode through AppShell, install discovery, and virtual paths
- `tools/dist/tool_assemble_dist_tree.py`
  - already assembles the canonical DIST-1 portable tree
  - already runs a narrow standalone smoke set during assembly

## Known Absolute-Path Leak Risk Areas

- `install.manifest.json`
  - install-root and descriptor references must remain relative or logical
- `manifests/release_manifest.json`
  - artifact names and extensions must remain content-addressed and path-normalized
- descriptor and compat outputs emitted by bundled binaries
  - may expose runtime-selected roots if command surfaces persist host paths into files
- generated config/manifests under `instances/`, `store/`, and `manifests/`
  - must not capture build-time or repo-local absolute paths

## Current Distribution Reality

- The assembled bundle at `dist/v0.0.0-mock/win64/dominium` is the current canonical DIST-1 surface for verification.
- Offline release-manifest verification is already available and should be reused, not replaced.
- Portable products currently require a runtime subset of `tools/xstack/*` compiled into the bundle:
  - `tools/xstack/cache_store`
  - `tools/xstack/compatx`
  - `tools/xstack/pack_contrib`
  - `tools/xstack/pack_loader`
  - `tools/xstack/packagingx`
  - `tools/xstack/registry_compile`
  - `tools/xstack/sessionx`
- Non-runtime XStack governance/dev surfaces remain forbidden in distribution:
  - `auditx`, `controlx`, `core`, `extensions`, `performx`, `securex`, `repox`, `testx`, and legacy root entrypoints not required for product execution

## Safest DIST-2 Insertion Points

- Add a dedicated verifier under `tools/dist/` that:
  - reuses RELEASE-1 manifest verification
  - reuses bundled `setup packs verify`
  - scans bundle files deterministically for forbidden/dev payload and absolute path leaks
  - does not mutate bundle contents
- Keep convergence integration optional so canonical CONVERGENCE-GATE-0 ordering remains stable by default.
- Extend RepoX and AuditX using the machine-readable DIST-2 report instead of inventing parallel scan logic.
