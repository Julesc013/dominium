# MVP Smoke Final

## Run Summary

- result: `complete`
- scenario_id: `scenario.mvp.smoke.03e9363b1cf3`
- scenario_seed: `456`
- refusal_count: `0`
- deterministic_fingerprint: `4731aca275640e24cc9e9a5403bfb4068ab403469517395993d6a344b2926758`
- readiness: Ready for MVP-GATE-1 stress and RELEASE series.

## Hashes

- pack_lock_hash: `45bf16251b647cca6133e3ad4c88f62b4984ed01fed858491b798bcc4dfc4208`
- smoke_runtime pack_lock_hash: `60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
- compat_status negotiation hash: `6cf409c5e07fe4fac5e2d30e3df91bca589e718d8838e00f00e4508143dd53f7`
- server proof anchors: `b8ef9a775383fd80c6d594348bc99c7354ac2663df6fdc8af1aa2e4d5c0e55da`
- logic compiled model hash: `c44de1dac0c41cd1903286964fe89d4aedf434c5b1505e25e61bfea25ff2c9eb`
- replay bundle hash: `d4482ad0925532635dadde0a7e2cb87e3588e4def8a0eee1363860e8150cb8dc`

## Degradations

- rendered_disabled: `compat.degraded` -> `tui`
- tui_unavailable: `compat.degraded` -> `cli` logged=`True`

## Gates

- RepoX STRICT: `PASS`
- AuditX STRICT: `PASS`
- TestX: `PASS`
- smoke harness: `PASS`

## Regression Lock

- baseline_id: `mvp.smoke.baseline.v1`
- baseline_fingerprint: `baaa6589ef47a0d66cb3d002831323a91a103ce4c7a521bc362098536c03bdd0`
- baseline runtime_pack_lock_hash: `60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
- required_commit_tag: `MVP-SMOKE-REGRESSION-UPDATE`
