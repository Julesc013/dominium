# Install Model (OPS0)

Status: binding.
Scope: immutable installs, their identity, and how tools/launcher resolve them.

## Canonical manifest

The authoritative install manifest is defined by:

- `schema/install.manifest.schema`

The manifest is stored at:

- `INSTALL_ROOT/install.manifest.json`

Install roots are immutable after creation. All tools and the launcher must
operate relative to an explicit install manifest path; no code may assume a
single install on the machine.

## Compatibility with legacy formats

Legacy setup formats remain supported for compatibility and auditing:

- `dominium_install.json` (legacy JSON)
- `install_manifest.tlv` (setup TLV format)

These legacy files are adapters and must map to the canonical fields. If both
canonical and legacy manifests exist, the canonical manifest is authoritative.

## Required fields (summary)

- install_id (UUID, stable)
- install_root (immutable path)
- binaries (engine/game/client/server/tools versions)
- supported_capabilities (capability baselines)
- protocol_versions (net/save/mod/replay)
- build_identity (global build number)
- trust_tier (official | community | local | experimental)
- created_at
- extensions (open map)

## Rules

- Multiple install manifests may coexist on the same machine.
- install_root is read-only after creation.
- Tools and launcher must reference the manifest explicitly for all ops actions.
- Missing or malformed manifests are refusal outcomes.

## See also

- `docs/architecture/INSTANCE_MODEL.md`
- `docs/architecture/UPDATE_MODEL.md`
- `docs/architecture/OPS_TRANSACTION_MODEL.md`
