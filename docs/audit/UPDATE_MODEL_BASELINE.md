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

- release index hash: `befe97b00d8aa96e1a768a34864c4f643c5d1b277834931d78a8b140220eec73`
- governance profile hash: `09273dc808ff2cf8edab36eb30ce4139212bcce8903a3ab5a3043a9fcfd08187`
- update plan fingerprint: `7369f2c66dfdbbb31b6d75b3298975742dd1ee1fa98bb61a2ba0a19177c6a008`
- report fingerprint: `e42e88e42d035378fd7909f93b4fcbb61771a644e790a96f848228eade3f2edc`

## Readiness

- ARCH-MATRIX-0: ready
- TRUST-MODEL-0: ready
