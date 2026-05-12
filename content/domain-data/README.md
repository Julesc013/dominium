# Domain Data Root

Status: PROVISIONAL
Phase: CONVERGE-09

`content/domain-data/` is the target source root for authored domain datasets, source data, fixtures intended as product/content inputs, and non-code domain material.

This root is not a mutable runtime store, not generated distribution output, and not schema authority. Machine-readable schemas, registries, capabilities, and protocols belong under `contracts/`.

Pack content belongs under `content/packs/` when it is actual pack material. Test-only fixtures belong under `tests/fixtures/`.
