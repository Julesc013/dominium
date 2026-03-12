# MVP Smoke Final

## Run Summary

- result: `complete`
- scenario_id: `scenario.mvp.smoke.03e9363b1cf3`
- scenario_seed: `456`
- refusal_count: `0`
- deterministic_fingerprint: `be96595494e1f9d7e69f2ff98f5549c05bf1830e904211bac8ce8f5411136f73`
- readiness: Not ready for MVP-GATE-1 stress or RELEASE series.

## Hashes

- pack_lock_hash: `45bf16251b647cca6133e3ad4c88f62b4984ed01fed858491b798bcc4dfc4208`
- smoke_runtime pack_lock_hash: `60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
- compat_status negotiation hash: `84c9cc4597fbb552de8c6f2abbeb93ca2d4c190a5de06999684e81c4b0a0c8ac`
- server proof anchors: `e55251e4abec03861f0059107d235ad845d0e7ff2be1094601740e0734a78880`
- logic compiled model hash: `c44de1dac0c41cd1903286964fe89d4aedf434c5b1505e25e61bfea25ff2c9eb`
- replay bundle hash: `3c54acc2d8e5647812b08d3c747d0a11f639d58f5bd85b0ab67ac3d80350827d`

## Degradations

- rendered_disabled: `compat.degraded` -> `cli`
- tui_unavailable: `compat.degraded` -> `cli` logged=`True`

## Gates

- RepoX STRICT: `NOT_RUN`
- AuditX STRICT: `NOT_RUN`
- TestX: `NOT_RUN`
- smoke harness: `NOT_RUN`

## Regression Lock

- baseline_id: `mvp.smoke.baseline.v1`
- baseline_fingerprint: `94a33cc31c9ef6bd03f482dc586b6eaafc24c3da71633c5555e2460f7c3729ba`
- baseline runtime_pack_lock_hash: `60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
- required_commit_tag: `MVP-SMOKE-REGRESSION-UPDATE`
