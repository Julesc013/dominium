Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Instance Model

Doc Version: 1

An “instance” is an isolated, auditable launcher-managed environment containing a pinned manifest, configuration defaults, logs, and transactional state required for safe updates and recovery.

## Identifiers

- `instance_id` is the stable identifier for an instance and is used as a directory name.
- For safety and portability, it must be a single path component (no separators, no traversal segments).

## State Roots and Layout

The launcher operates under a single “state root” (often derived from `--home` and platform defaults). Under this root:

- `instances/<instance_id>/` contains per-instance state.
- `artifacts/` contains the shared content-addressed artifact store (see `docs/launcher/ARTIFACT_STORE.md`).
- `audit/` (or equivalent) contains per-run audit logs.

Within `instances/<instance_id>/` (conceptual view):

- `manifest.tlv` – instance lockfile (pinned engine/game and ordered content graph).
- `config/config.tlv` – persistent configuration defaults.
- `logs/launch_history.tlv` – failure tracking and recovery inputs.
- `known_good.tlv` – pointer to the last known-good snapshot.
- `previous/` – archived snapshots (manifest + payload references) and prior states.
- `staging/` – transaction working area (never treated as live state).

The exact on-disk layout is defined by the instance layout spec: `docs/specs/SPEC_INSTANCE_LAYOUT.md`.

## Manifest (Lockfile)

The instance manifest is a versioned TLV schema that represents:
- A stable `instance_id`
- Pinned engine/game identifiers
- An ordered list of content entries (packs/mods/runtime artifacts)
- Provenance fields used by clone/import operations
- State markers (known-good, last verified time)

The manifest has a deterministic hash computed over its canonical TLV bytes. This hash is used for provenance and auditing.

## Configuration

`config/config.tlv` stores persistent defaults such as:
- Preferred gfx backend / renderer API
- Window and device options
- Network allowance policy
- Recovery thresholds and history sizing

Safe mode applies an overlay during launch planning without persisting changes unless explicitly confirmed. See `docs/launcher/RECOVERY_AND_SAFE_MODE.md`.

## Transactions and Atomicity

Instance mutations (install/update/remove/rollback) are performed via a transaction engine:
- Writes occur only under `staging/`.
- Commit swaps staged state into place and archives prior state under `previous/`.
- On crash or interruption, recovery deletes staged artifacts and preserves live state.
- All phases emit audit reasons.

## Import / Export

Two modes exist:
- Definition-only: transfers manifest/config only.
- Full bundle: includes instance payloads as a portable bundle.

Imports record provenance (source instance + manifest hash). Verification can be enforced, with safe mode allowing best-effort import when explicitly requested.

See `docs/specs/SPEC_LAUNCHER_PACKS.md` and `docs/launcher/RECOVERY_AND_SAFE_MODE.md`.