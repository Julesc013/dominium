Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
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

- release index hash: `140b9943619390778a8d2fce87d32faa861b3d3718878bb58308885485b1bf20`
- governance profile hash: `09273dc808ff2cf8edab36eb30ce4139212bcce8903a3ab5a3043a9fcfd08187`
- update plan fingerprint: `4afa2588a1e1321a09fc0ff7a02d4b877bae19da3d5c038fb1158072079e4d40`
- report fingerprint: `024060e8eae7bf67c0d33729efa60c3e2a9e0ddc30d67187dc8371021e649fd7`

## Readiness

- ARCH-MATRIX-0: ready
- TRUST-MODEL-0: ready
