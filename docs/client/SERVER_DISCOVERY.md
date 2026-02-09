Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Server Discovery

## Scope

Server discovery is provider-based and deterministic.
Provider wiring is client-side orchestration only.

## Providers

- `provider_saved`
- `provider_manual`
- `provider_lan`
- `provider_directory_official`
- `provider_directory_custom`

Current adapter status:

- saved/manual: available
- lan/directory: explicit refusal (`REFUSE_PROVIDER_UNAVAILABLE`)

## Merge Rules

Server records merge by stable keys:

1. `server_id`
2. `provider`
3. `address`

Sorting and deduplication are deterministic in `client/core/client_models_server.c`.

## Refusal Surface

If capability or provider preconditions fail, command returns deterministic refusal:

- `REFUSE_CAPABILITY_MISSING`
- `REFUSE_PROVIDER_UNAVAILABLE`
- `REFUSE_UNAVAILABLE`

