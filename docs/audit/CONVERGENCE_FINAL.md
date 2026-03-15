Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence gate summary for pre-release validation

# CONVERGENCE Final

## Summary

- result: `complete`
- report_id: `release.convergence.gate.v1`
- step_count: `13`
- completed_step_count: `13`
- default_path_refusal_count: `0`
- default_path_degrade_count: `0`
- deterministic_fingerprint: `5c0e5013f1326ef975d09634ecb24a8bf76bfa48168bb89c0dfc77e52730b3ba`

## Step Results

| # | Step | Result | Fingerprint |
| --- | --- | --- | --- |
| `1` | `VALIDATION-UNIFY STRICT` | `complete` | `e0bbf8001eeedf4ae4eed101c04c16d0f3fd01a53cda2ee917296d4f01b4a48f` |
| `2` | `META-STABILITY validator` | `complete` | `ea5181af6ba9877a47b0ef1f23467e34749a5f6a35951f349496d44a2c24ce90` |
| `3` | `TIME-ANCHOR verifier` | `complete` | `d700adf983326072f2a2a92f5df3420566785fabb5338e184e98ce4f78de78d7` |
| `4` | `ARCH-AUDIT tool` | `complete` | `644d67881bd9f35ec9f021f6e02cae24dee9304de4d77313610b1cf90053eed1` |
| `5` | `CAP-NEG-4 interop stress` | `complete` | `e3bb42d5ff31343d5ce6a39c41411e24f0aa049d5ef85f9b516aec9796a1052f` |
| `6` | `PACK-COMPAT verification stress` | `complete` | `504196961dc76c90534211fb7ec9252955a61e256c029e9b3a79d8803f759588` |
| `7` | `LIB-7 stress` | `complete` | `4e8ddbf7b8f219f2cf77f5cc7b534d5a053273679ab5f9fb0a87ba4dcced6674` |
| `8` | `PROD-GATE-0 boot matrix` | `complete` | `a6f42f95222495f0fd7056208adc0f4b373e13f8bffe4d99493bb8a9bb2b9ec4` |
| `9` | `IPC-UNIFY attach smoke` | `complete` | `92cb78a7509bdc902e1db1dff825a4df84bd13e63c35e9c1712a194eab6b9f4d` |
| `10` | `SUPERVISOR-HARDEN checks` | `complete` | `e1a3c0c99f729603d845309e90bcb47d8d67c86b8fedc8c343b06a6654d106ce` |
| `11` | `MVP-GATE-0 smoke suite` | `complete` | `ece0616c94e2d085b642e2726cb30967ee3f8ed2fe9d40824806d62d8e5b388e` |
| `12` | `MVP-GATE-1 stress suite` | `complete` | `274a3256c1dde6611ec5c393bcfb094755eb370022b78a9aa9b449320b0e7c74` |
| `13` | `MVP-GATE-2 cross-platform agreement` | `complete` | `d5f0bc2dd6ba8d22d55ba098a40287d0b0091ee5d124fed23571fc3ab532c9e6` |

## Key Hashes

- contract_bundle_hash: ``
- cross_platform_comparison_fingerprint: `b86a92adfdf933fe009bcddd9c85c22788e86ed98a256f95215c8c84ce3a0c27`
- deterministic_fingerprint: `dbe4d23573d1fbc0e3f1cb4d683feddda96002a44d524a404f1c2d10c20b8e7b`
- negotiation_record_hashes: `d070a170f9b03e3bde73ba1a6c8182ecc6d3214bc06aa43c4069409261179954`
- pack_lock_hash: `45bf16251b647cca6133e3ad4c88f62b4984ed01fed858491b798bcc4dfc4208`
- proof_anchor_hash: `b8ef9a775383fd80c6d594348bc99c7354ac2663df6fdc8af1aa2e4d5c0e55da`
- repro_bundle_hash: `d4482ad0925532635dadde0a7e2cb87e3588e4def8a0eee1363860e8150cb8dc`

## Refusal/Degrade Logs

- default_path_refusal_count: `0`
- default_path_degrade_count: `0`
- synthetic_refusal_count: `8`
- synthetic_degrade_count: `10`

## Remediation

- none
