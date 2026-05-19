# Pack Contracts

Status: PROVISIONAL
Phase: CONVERGE-06

This directory is reserved for pack format, pack compatibility, pack verification, and pack contract definitions.

Authored pack payloads and pack-local manifests live under `content/packs/`.
Do not mirror real pack IDs or payload trees here; use `contracts/package/`
for schemas, policy, compatibility law, verification contracts, and package
format definitions only.

Test-only pack fixtures belong under `tests/fixtures/package/` or the existing
package fixture taxonomy. Generated package artifacts and evidence belong under
`archive/generated/package/` or the owning generated-output root, not here.
