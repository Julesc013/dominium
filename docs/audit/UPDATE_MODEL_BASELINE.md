Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: UPDATE/TRUST
Replacement Target: trust-governed remote release indices and signed acquisition policy

# Update Model Baseline

## Release Index Schema

- channel-aware offline-first release index
- embedded component graph for deterministic install/update resolution
- platform matrix filtered by os/arch/abi

## Update Plan Logic

- compare current install manifest against target release index
- resolve target components through install profile + component graph
- produce add/remove/upgrade sets in deterministic order
- refuse on semantic-contract or protocol incompatibility

## Rollback Model

- `.dsu/install_transaction_log.json` records update and rollback actions
- rollback selects the latest matching transaction by `from_release_id` when `--to` is supplied
- rollback falls back to the most recent successful transaction when `--to` is omitted

## Report Fingerprints

- release index hash: `5daa6e38edbf6d33e5566c17f2a3971a75b3c031281f45d395be70fa895e6b11`
- governance profile hash: `09273dc808ff2cf8edab36eb30ce4139212bcce8903a3ab5a3043a9fcfd08187`
- update plan fingerprint: `128ca041fcee45b4200e022fcf69b0acf6fed898a2b708a0c7afbaf821b5f6a1`
- report fingerprint: `8a59f217fdb0901680cda3612e40f0c9a0ba1cf790b3b406a68363f593f903d4`

## Readiness

- ARCH-MATRIX-0: ready
- TRUST-MODEL-0: ready
