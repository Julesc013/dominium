Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Storage Backend Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

Related projection authority: `contracts/distribution/layout.contract.toml`

## Backend Rows

| Backend | Status | Tier | Notes |
| --- | --- | --- | --- |
| local_fs | provisional | T0 | Local filesystem binding surfaces exist. |
| pack_fs | planned | T0 | Pack filesystem lane. |
| cas_store | provisional | T0 | Content-addressed store lane. |
| save_export_roots | provisional | T0 | Save/export logical roots from distribution projection contract. |
| cache_staging | provisional | T0 | Cache/staging and ops transaction projection. |
| cloud_sync | research | T5 | Future cloud/sync research lane. |

## Rule

Source content, runtime mutable store, and generated distribution output are different layouts. Storage backends must not collapse those ownership surfaces.
