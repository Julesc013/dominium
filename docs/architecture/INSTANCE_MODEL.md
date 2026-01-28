# Instance Model (OPS0)

Status: binding.
Scope: portable instances, data roots, and operational configuration.

## Canonical manifest

The authoritative instance manifest is defined by:

- `schema/instance.manifest.schema`

The manifest is stored at:

- `INSTANCE_ROOT/instance.manifest.json`

## Required fields (summary)

- instance_id (UUID, stable)
- install_id (reference to install.manifest)
- data_root (writable root; relative to instance root when possible)
- active_profiles / active_modpacks
- capability_lockfile (path relative to data_root)
- sandbox_policy_ref
- update_channel (stable | beta | nightly | pinned)
- created_at / last_used_at
- extensions (open map)

## Rules

- Instances are fully portable by copying the instance directory.
- Multiple instances may share a single install.
- Instances must not share writable state.
- Saves, replays, and logs are relative to data_root.
- Switching active instance must be explicit and logged.

## See also

- `docs/architecture/INSTALL_MODEL.md`
- `docs/architecture/SANDBOX_MODEL.md`
- `docs/architecture/OPS_TRANSACTION_MODEL.md`
