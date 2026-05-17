# BASELINE-00 Status

Status: DERIVED
Last Reviewed: 2026-05-17

## Result

PASS_WITH_WARNINGS.

BASELINE-00 freezes RELEASE-00 as the structural regression baseline for future MOVE-FAMILY cleanup waves. The tracked baseline HEAD is:

```text
0b631fc5f09f3d927a54e8312976b926d111a72e
```

`origin/main` matched the same commit after `git fetch --all --prune`.

## Release Baseline

- Release root: `.dominium.local/releases/internal-pilot-0`
- Projection input: `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium`
- Required manifests: present
- Proof reports: present
- Native binaries: `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, `tools.exe`
- Checksums: `manifest/checksums.sha256`, 4718 entries
- Generated output status: ignored/local and untracked

## Scope Guard

- No files were moved, deleted, or renamed.
- No references were rewritten.
- No move maps, salvage maps, active path aliases, or layout exception retirements were applied.
- No public release, GitHub release, tag, upload, installer, package publication, or generated package output was created.
- No product/runtime/source behavior changed.

## Next

```text
MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan
```
