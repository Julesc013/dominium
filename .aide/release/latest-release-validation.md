# Release Validation

- result: FAIL
- pack_status: FAIL
- checksum_validation: FAIL
- fixture_extract: FAIL
- no_publish: true
- provider_or_model_calls: none
- network_calls: none

## Blockers
- release artifact exists: .aide/release/dist/aide-lite-pack-v0.zip
- release artifact exists: .aide/release/dist/aide-lite-pack-v0.tar.gz
- release artifact exists: .aide/release/dist/aide-lite-pack-v0.checksums.json
- release artifact exists: .aide/release/dist/SHA256SUMS.txt
- release artifact exists: .aide/release/dist/manifest.yaml
- release artifact exists: .aide/release/dist/install.md
- release artifact exists: .aide/release/dist/CHANGELOG.preview.md
- release artifact exists: .aide/release/dist/RELEASE_NOTES.preview.md
- release artifact exists: .aide/release/dist/release-provenance.json
- release artifact exists: .aide/release/dist/release-assets.json
- release checksum problem: missing release checksums JSON
- fixture extraction .aide/release/dist/aide-lite-pack-v0.zip: FAIL
- fixture extraction .aide/release/dist/aide-lite-pack-v0.tar.gz: FAIL
- pack-status problem: export pack missing

## Warnings
- none
