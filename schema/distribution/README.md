# Distribution Schema (DIST0)

This folder defines canonical distribution contracts for packaging, install
projection, and legacy shard-model references. It is a specification layer only;
no runtime logic lives here.

## Contents
- `SPEC_SHARD_MODEL.md` — shard identity, determinism domains, ownership scopes.
- `SPEC_SHARD_OWNERSHIP.md` — ownership boundaries and migration rules.
- `SPEC_CROSS_SHARD_MESSAGES.md` — cross-shard message schema and ordering.
- `pkg_manifest.schema` — package manifest contract for dompkg artifacts.
- `pkg_index.schema` — package index contract.
- `install_lock.schema` — deterministic install lock and projection digest contract.
- `profile.schema` — package profile selection contract.
- `trust_policy.schema` — signature/trust verification contract.

## Authority
These specs are binding for DIST0 and subordinate to ARCH0. If any runtime
implementation conflicts with these specs, the specs win.
