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

- release index hash: `fa59a735f5c84923bb1b377e737e4163c992fa49e3b2adaed2f466fd427885b3`
- governance profile hash: `09273dc808ff2cf8edab36eb30ce4139212bcce8903a3ab5a3043a9fcfd08187`
- update plan fingerprint: `3251f3010f0c45140c2f0b8949a641f5d508214c2ff4fb905522610b727e7a80`
- report fingerprint: `80d30f05297b93720ad24628bf96db0278c3e2a6769df73235f4c5ef87bd0c6e`

## Readiness

- ARCH-MATRIX-0: ready
- TRUST-MODEL-0: ready
