# MVP Smoke Final

## Run Summary

- result: `complete`
- scenario_id: `scenario.mvp.smoke.03e9363b1cf3`
- scenario_seed: `456`
- refusal_count: `0`
- deterministic_fingerprint: `bfb1b59e3417eef6b763f9c8cce56037ee97d8c0fdf691e00ed592474b3b8f43`
- readiness: Ready for MVP-GATE-1 stress and RELEASE series.

## Hashes

- pack_lock_hash: `45bf16251b647cca6133e3ad4c88f62b4984ed01fed858491b798bcc4dfc4208`
- smoke_runtime pack_lock_hash: `60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
- compat_status negotiation hash: `43f466bfbc5904a4280d6c6da867cc53a2dd56f92f233e042df360f4548c438b`
- server proof anchors: `b8ef9a775383fd80c6d594348bc99c7354ac2663df6fdc8af1aa2e4d5c0e55da`
- logic compiled model hash: `c44de1dac0c41cd1903286964fe89d4aedf434c5b1505e25e61bfea25ff2c9eb`
- replay bundle hash: `a58f261dc8d58b6200e004a509f26f6a16c460689323dbab96598efcdb4c010f`

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
- baseline_fingerprint: `60e5b82d2d925260a4066c427624752738addd044f142b1a790d40a567110987`
- baseline runtime_pack_lock_hash: `60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
- required_commit_tag: `MVP-SMOKE-REGRESSION-UPDATE`
