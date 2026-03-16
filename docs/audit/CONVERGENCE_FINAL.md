Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
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
- deterministic_fingerprint: `68babbd31e66df54fb0596dfd714011d28b5b70ac94246c2c1135702100eb625`

## Step Results

| # | Step | Result | Fingerprint |
| --- | --- | --- | --- |
| `1` | `VALIDATION-UNIFY STRICT` | `complete` | `48ccc0d6a5a6ed760672a2f9f812c1636fab32330362b8045b2a45f410329d5a` |
| `2` | `META-STABILITY validator` | `complete` | `ea5181af6ba9877a47b0ef1f23467e34749a5f6a35951f349496d44a2c24ce90` |
| `3` | `TIME-ANCHOR verifier` | `complete` | `d700adf983326072f2a2a92f5df3420566785fabb5338e184e98ce4f78de78d7` |
| `4` | `ARCH-AUDIT tool` | `complete` | `644d67881bd9f35ec9f021f6e02cae24dee9304de4d77313610b1cf90053eed1` |
| `5` | `CAP-NEG-4 interop stress` | `complete` | `da203e03c29586d65877a260d33ee1703da9db4314457fd2d6b5b52911da89d4` |
| `6` | `PACK-COMPAT verification stress` | `complete` | `504196961dc76c90534211fb7ec9252955a61e256c029e9b3a79d8803f759588` |
| `7` | `LIB-7 stress` | `complete` | `a89bc9b36875ace01b08c55dfabee469bbc68ceabd0213a846da8a44c04e85b5` |
| `8` | `PROD-GATE-0 boot matrix` | `complete` | `64b4e82ec7183031cd00b6d27b45e5b2745f29b05e416990a25f6806f0088d0c` |
| `9` | `IPC-UNIFY attach smoke` | `complete` | `f0507f195273885f9c9c53c847f4c9927a44e74a70bc4397eb5c2ce0df6874b6` |
| `10` | `SUPERVISOR-HARDEN checks` | `complete` | `2f6852c638d6ee6c09b2bf77d004867f33b3acc7e5a9ece8361fcb892209facd` |
| `11` | `MVP-GATE-0 smoke suite` | `complete` | `40242d8cb50ad5acc3114083f17b088b38dc0a2f9efd0471b0d1903712bc0c22` |
| `12` | `MVP-GATE-1 stress suite` | `complete` | `274a3256c1dde6611ec5c393bcfb094755eb370022b78a9aa9b449320b0e7c74` |
| `13` | `MVP-GATE-2 cross-platform agreement` | `complete` | `d5f0bc2dd6ba8d22d55ba098a40287d0b0091ee5d124fed23571fc3ab532c9e6` |

## Key Hashes

- contract_bundle_hash: ``
- cross_platform_comparison_fingerprint: `b86a92adfdf933fe009bcddd9c85c22788e86ed98a256f95215c8c84ce3a0c27`
- deterministic_fingerprint: `3672e670a2d986710341349dd53fac9f5b75c2bbbae4154c5ce00a8d3e1cb627`
- negotiation_record_hashes: `d16b7af9484464e13d9070cacc1b425d466fb10110e4b70b7d30b41b1863215d`
- pack_lock_hash: `45bf16251b647cca6133e3ad4c88f62b4984ed01fed858491b798bcc4dfc4208`
- proof_anchor_hash: `b8ef9a775383fd80c6d594348bc99c7354ac2663df6fdc8af1aa2e4d5c0e55da`
- repro_bundle_hash: `a58f261dc8d58b6200e004a509f26f6a16c460689323dbab96598efcdb4c010f`

## Refusal/Degrade Logs

- default_path_refusal_count: `0`
- default_path_degrade_count: `0`
- synthetic_refusal_count: `8`
- synthetic_degrade_count: `10`

## Remediation

- none
