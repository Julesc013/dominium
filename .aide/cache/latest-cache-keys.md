# AIDE Cache Key Report

## CACHE_KEYS

- schema_version: q18.cache-keys.v0
- generated_by: aide-lite q24.existing-tool-adapter-compiler.v0
- contents_inline: false
- raw_prompt_storage: false
- raw_response_storage: false
- git_commit: b0feec713e05710a370157b006bbca9561c7db34
- dirty_state: true

## LOCAL_STATE_BOUNDARY

- committed_contract_root: .aide/
- local_state_root: .aide.local/
- local_state_ignored: true
- tracked_local_state_paths: 0

## SURFACES

- latest_context_packet: `.aide/context/latest-context-packet.md`
  - surface: context_packet
  - key_id: aide-cache-v0:context_packet:f9023026252ae650
  - content_sha256: 35364a334316964761eae5148e66f25bd515ac1c18f357442627e1a17c6d30e4
  - dependency_count: 6
  - dirty_state: true
- latest_golden_tasks_report: `.aide/evals/runs/latest-golden-tasks.json`
  - surface: golden_tasks_report
  - key_id: aide-cache-v0:golden_tasks_report:02090843cdb9f0fc
  - content_sha256: 353c5427506e0a32186a7399b77ec97382a514952c6b073703ac69c48efc18fb
  - dependency_count: 2
  - dirty_state: true
- latest_review_packet: `.aide/context/latest-review-packet.md`
  - surface: review_packet
  - key_id: aide-cache-v0:review_packet:1a90b093a153c945
  - content_sha256: b80b2f40d9f500bf9a712eb7e74709907d695ab8d692c494c77f4555f8f5360c
  - dependency_count: 4
  - dirty_state: true
- latest_route_decision: `.aide/routing/latest-route-decision.json`
  - surface: route_decision
  - key_id: aide-cache-v0:route_decision:16897f02ca775603
  - content_sha256: 652ed23e95f81aae76c7e9b65b916d994fd932fcc4b1412fa89353100bd560bf
  - dependency_count: 6
  - dirty_state: true
- latest_task_packet: `.aide/context/latest-task-packet.md`
  - surface: task_packet
  - key_id: aide-cache-v0:task_packet:c7b2adbc03b39ab0
  - content_sha256: 68b001c444b764e917683c74af9760fcbe994365b330849d34bd70141c255d88
  - dependency_count: 5
  - dirty_state: true
- latest_verification_report: `.aide/verification/latest-verification-report.md`
  - surface: verification_report
  - key_id: aide-cache-v0:verification_report:ce95d45c16ed0a3a
  - content_sha256: f669ffed3abe7019c79e552e6ff773683a478e6bfb1d350ab22cfdf5dbdd5c06
  - dependency_count: 4
  - dirty_state: true
- token_savings_summary: `.aide/reports/token-savings-summary.md`
  - surface: token_savings_summary
  - key_id: aide-cache-v0:token_savings_summary:e45062042c71ccb4
  - content_sha256: ccb2b3eafed93ba9dbeeb39226d5c3ac3d554989e956c82be9d7c66886448dca
  - dependency_count: 3
  - dirty_state: true

## LIMITS

- Cache keys are deterministic metadata, not permission to reuse stale or unsafe content.
- Cache hits must not bypass verifier, review gates, or golden tasks.
- Provider response and semantic caches remain disabled until future reviewed policy enables them.
- Raw prompts, raw responses, secrets, traces, and real cache blobs must stay out of committed files.
