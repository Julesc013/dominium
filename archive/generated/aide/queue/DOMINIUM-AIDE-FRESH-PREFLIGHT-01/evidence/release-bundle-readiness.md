# Release Bundle Readiness

## Source Selected

- Selected source: sibling local AIDE release dist, `C:/Inbox/Git Repos/aide/.aide/release/dist`.
- Environment variables `AIDE_RELEASE_BUNDLE`, `AIDE_RELEASE_DIR`, and `AIDE_REPO`: unset.
- Fallback export source also exists at `C:/Inbox/Git Repos/aide/.aide/export/aide-lite-pack-v0`, but the release dist source has priority and was used.

## Artifacts Found

- `aide-lite-pack-v0.zip`: present, 747612 bytes.
- `aide-lite-pack-v0.tar.gz`: present, 493160 bytes.
- `aide-lite-pack-v0.checksums.json`: present.
- `SHA256SUMS.txt`: present.
- `manifest.yaml`: present.
- `install.md`: present.
- `CHANGELOG.preview.md`: present.
- `RELEASE_NOTES.preview.md`: present.
- `release-assets.json`: present.
- `release-provenance.json`: present.
- `release-validation.json` and `release-validation.md`: present.

## Checksum Status

Read-only SHA256 validation passed for the checksum-scoped release artifacts:

- `CHANGELOG.preview.md`: PASS.
- `RELEASE_NOTES.preview.md`: PASS.
- `aide-lite-pack-v0.tar.gz`: PASS.
- `aide-lite-pack-v0.zip`: PASS.
- `install.md`: PASS.
- `manifest.yaml`: PASS.
- `release-assets.json`: PASS.
- `release-provenance.json`: PASS.

`SHA256SUMS.txt` matches the same scoped entries. Validation metadata files are explicitly excluded by `aide-lite-pack-v0.checksums.json`.

## Manifest And Install Notes

- Manifest schema: `aide.release-manifest.v0`.
- Bundle id: `aide-lite-pack-v0-2b2a00f7c4628311`.
- Bundle name: `aide-lite-pack-v0`.
- Manifest `no_publish`: true.
- Install notes `pack_status`: `DIRTY_SOURCE_RECORDED`.
- Install notes `publication_status`: `local_preview_no_publish`.
- Install notes `apply_mode_available`: false.

## Archive Listing

- Zip listing performed read-only: 634 entries.
- Tar.gz listing performed read-only: 634 entries.
- No extraction into Dominium was performed.
- Forbidden path scan inside both archive listings found 0 matches for `.git`, `.aide.local`, `.env`, raw prompt/response paths, provider key names, or private-key markers.
- First entries show a contained root `aide-lite-pack-v0/` with `checksums.json`, `export-report.md`, `install.md`, `manifest.yaml`, and `files/.aide/**` content.

## Readiness

- Release bundle readiness: ready for Q50 dry-run/observe/compare/plan.
- Not ready for blind apply: the bundle itself says apply mode is unavailable and local preview no-publish.
- Q50 must not copy this bundle into Dominium `.aide/` except through an explicitly approved future install/upgrade apply phase.
