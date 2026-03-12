# MVP Smoke Final

## Run Summary

- result: `complete`
- scenario_id: `scenario.mvp.smoke.03e9363b1cf3`
- scenario_seed: `456`
- refusal_count: `0`
- deterministic_fingerprint: `4971589744161ccced1db37bfd53e7a80d0fc03b919951b2f1b2ffbe71923491`
- readiness: Ready for MVP-GATE-1 stress and RELEASE series.

## Hashes

- pack_lock_hash: `45bf16251b647cca6133e3ad4c88f62b4984ed01fed858491b798bcc4dfc4208`
- smoke_runtime pack_lock_hash: `60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
- compat_status negotiation hash: `0265e6c1ba9b35bbdb207fd4ecae0ed15d8a109a83b76a00bc1301b680195c2c`
- server proof anchors: `e67503787b7b49bd5a786119c5e9c47eb0c8da5cecc241e4444a8711ac603261`
- logic compiled model hash: `e77913379dc7d8ec5d88133605e85f2c73d739f58113aadeaf5b5d529e19087d`
- replay bundle hash: `ca062c0412578d4a2a9116d1635fd2f16f135280e24f6cdd2c858010d5ae1f01`

## Degradations

- rendered_disabled: `compat.degraded` -> `cli`
- tui_unavailable: `compat.degraded` -> `cli` logged=`True`

## Gates

- RepoX STRICT: `PASS` (smoke invariant scope; full repo strict is blocked by pre-existing debt)
- AuditX STRICT: `PASS` (smoke analyzer scope; full repo verify still reports legacy findings)
- TestX: `PASS` (4 smoke tests)
- smoke harness: `PASS` (seed 456)

## Regression Lock

- baseline_id: `mvp.smoke.baseline.v1`
- baseline_fingerprint: `3338fd1f1b55eb692c05b247c947689a8f73927cb4cb283e6fbd3607343c8f2c`
- baseline runtime_pack_lock_hash: `60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
- required_commit_tag: `MVP-SMOKE-REGRESSION-UPDATE`
