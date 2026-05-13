# AIDE Cache Key Report

## CACHE_KEYS

- schema_version: q18.cache-keys.v0
- generated_by: aide-lite q24.existing-tool-adapter-compiler.v0
- contents_inline: false
- raw_prompt_storage: false
- raw_response_storage: false
- git_commit: f2a1b4412cbeac0c5da1d5e357a5dfdee59a8959
- dirty_state: true

## LOCAL_STATE_BOUNDARY

- committed_contract_root: .aide/
- local_state_root: .aide.local/
- local_state_ignored: true
- tracked_local_state_paths: 0

## SURFACES

- latest_context_packet: `.aide/context/latest-context-packet.md`
  - surface: context_packet
  - key_id: aide-cache-v0:context_packet:237ab91f777eb83e
  - content_sha256: 908339c11e07d5434c642d996e00141c267c7961f79f5fa943143a8140b7d054
  - dependency_count: 6
  - dirty_state: true
- latest_golden_tasks_report: `.aide/evals/runs/latest-golden-tasks.json`
  - surface: golden_tasks_report
  - key_id: aide-cache-v0:golden_tasks_report:466ff742ab97081b
  - content_sha256: fa637111d1b1d754f4de8a274df5d443b58400ef783e5c78f012b350b7298f66
  - dependency_count: 2
  - dirty_state: true
- latest_review_packet: `.aide/context/latest-review-packet.md`
  - surface: review_packet
  - key_id: aide-cache-v0:review_packet:87276d644833e6e6
  - content_sha256: 82526a120d3dc925ea39568b19be3b268cd662d991ff21064aec453044cffcbc
  - dependency_count: 4
  - dirty_state: true
- latest_route_decision: `.aide/routing/latest-route-decision.json`
  - surface: route_decision
  - key_id: aide-cache-v0:route_decision:6ca3eb3723ab1c17
  - content_sha256: 7e111a433aec13216c89af1a3285f143c4dff771c5eeb9f62e0db7f3c223c952
  - dependency_count: 6
  - dirty_state: true
- latest_task_packet: `.aide/context/latest-task-packet.md`
  - surface: task_packet
  - key_id: aide-cache-v0:task_packet:276e43431066a484
  - content_sha256: dbf05fa678c213e400e8fe342ed84307cbfb1f09be20e1ee20e9f7f3010f8bbe
  - dependency_count: 5
  - dirty_state: true
- latest_verification_report: `.aide/verification/latest-verification-report.md`
  - surface: verification_report
  - key_id: aide-cache-v0:verification_report:d6dff4de8b455e84
  - content_sha256: 8e2e3c3658e73d87f2f2583efeff7cd855ae7e0b255c6db9e9c6ea60df0aa6fd
  - dependency_count: 4
  - dirty_state: true
- token_savings_summary: `.aide/reports/token-savings-summary.md`
  - surface: token_savings_summary
  - key_id: aide-cache-v0:token_savings_summary:c1917d135fd36795
  - content_sha256: f9b36555fa2c78941c75d320d7b8aa964751d9829a0303b059c7827760cd608d
  - dependency_count: 3
  - dirty_state: true

## LIMITS

- Cache keys are deterministic metadata, not permission to reuse stale or unsafe content.
- Cache hits must not bypass verifier, review gates, or golden tasks.
- Provider response and semantic caches remain disabled until future reviewed policy enables them.
- Raw prompts, raw responses, secrets, traces, and real cache blobs must stay out of committed files.
