# AIDE Cache Key Report

## CACHE_KEYS

- schema_version: q18.cache-keys.v0
- generated_by: aide-lite q24.existing-tool-adapter-compiler.v0
- contents_inline: false
- raw_prompt_storage: false
- raw_response_storage: false
- git_commit: 14da8a822909af6c77c6d788ac36a556c319e513
- dirty_state: true

## LOCAL_STATE_BOUNDARY

- committed_contract_root: .aide/
- local_state_root: .aide.local/
- local_state_ignored: true
- tracked_local_state_paths: 0

## SURFACES

- latest_context_packet: `.aide/context/latest-context-packet.md`
  - surface: context_packet
  - key_id: aide-cache-v0:context_packet:ce36301c283c9860
  - content_sha256: ef0aa1977cf5be51b97a32c9450057bff40f405856bd5abf584c8ab184b9516d
  - dependency_count: 6
  - dirty_state: true
- latest_golden_tasks_report: `.aide/evals/runs/latest-golden-tasks.json`
  - surface: golden_tasks_report
  - key_id: aide-cache-v0:golden_tasks_report:c3f6cb1f59821ed6
  - content_sha256: 46cdf442409a11823f3322b384b31e07f88d2e6efaeb64f5be0da70e7f6c3d4f
  - dependency_count: 2
  - dirty_state: true
- latest_review_packet: `.aide/context/latest-review-packet.md`
  - surface: review_packet
  - key_id: aide-cache-v0:review_packet:45e000d4d72840ff
  - content_sha256: 65c649e16c5ad82fe10889a0e80f56a1c12a6033fb6fc52b3b7d0aaaf720b83d
  - dependency_count: 4
  - dirty_state: true
- latest_route_decision: `.aide/routing/latest-route-decision.json`
  - surface: route_decision
  - key_id: aide-cache-v0:route_decision:1d006bfad2970040
  - content_sha256: 055b512e91419b8ff15dd5ab0f7a10a13a80242ca8c4f8c0b6c358c153dff78a
  - dependency_count: 6
  - dirty_state: true
- latest_task_packet: `.aide/context/latest-task-packet.md`
  - surface: task_packet
  - key_id: aide-cache-v0:task_packet:9db05307fbe36da2
  - content_sha256: 68b001c444b764e917683c74af9760fcbe994365b330849d34bd70141c255d88
  - dependency_count: 5
  - dirty_state: true
- latest_verification_report: `.aide/verification/latest-verification-report.md`
  - surface: verification_report
  - key_id: aide-cache-v0:verification_report:c222cb5318001515
  - content_sha256: 8237a351276c29a29913a370f090943aa5c57cd262f21d839773a840b6f68c9c
  - dependency_count: 4
  - dirty_state: true
- token_savings_summary: `.aide/reports/token-savings-summary.md`
  - surface: token_savings_summary
  - key_id: aide-cache-v0:token_savings_summary:422f507f0099b0c4
  - content_sha256: 09669523feae01f587b0d7c3653fc87fe763ea56e94cfa53e14fc7e26d381a69
  - dependency_count: 3
  - dirty_state: true

## LIMITS

- Cache keys are deterministic metadata, not permission to reuse stale or unsafe content.
- Cache hits must not bypass verifier, review gates, or golden tasks.
- Provider response and semantic caches remain disabled until future reviewed policy enables them.
- Raw prompts, raw responses, secrets, traces, and real cache blobs must stay out of committed files.
