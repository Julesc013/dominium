Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# World Manager

## Scope

World manager behavior is client orchestration for world metadata and launch intent.
Authoritative world mutation remains in process execution surfaces.

## Data Model

World records include:

- `world_id`
- `metadata_path`
- `pack_set_hash`
- `schema_versions`
- `last_build_identity`

The in-memory model is deterministic and digestible in `client/core/client_models_world.c`.

## Canonical Commands

- `client.world.list`
- `client.world.create`
- `client.world.inspect`
- `client.world.modify`
- `client.world.delete`
- `client.world.play`

Current bridge implementation:

- create/inspect/list/play: mapped to existing handlers
- modify/delete: explicit refusal until dedicated operations are implemented

## Refusals

- `REFUSE_CAPABILITY_MISSING` for gated commands
- `REFUSE_INVALID_STATE` for invalid state transitions
- `REFUSE_UNAVAILABLE` for unimplemented operations

