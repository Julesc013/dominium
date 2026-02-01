Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Update Model (OPS0)

Status: binding.
Scope: update channels, rollbacks, and install/instance coordination.

## Update channels

Install roots may be associated with multiple channels. Instances may pin or
follow channels independently.

Channels:

- stable
- beta
- nightly
- pinned

## Rollback safety

Rollback is safe because:

- install_root is immutable
- packs are content-addressed
- lockfiles define deterministic resolution

Rollback restores the previous manifest set and lockfile without partial state.

## Requirements

- Install roots can support multiple channels at once.
- Instances can pin or follow channels without changing simulation semantics.
- Rollback MUST restore previous state exactly and log the transaction.
- Offline-first behavior is required.

## See also

- `docs/architecture/INSTALL_MODEL.md`
- `docs/architecture/INSTANCE_MODEL.md`
- `docs/architecture/OPS_TRANSACTION_MODEL.md`