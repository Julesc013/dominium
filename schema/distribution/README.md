# Distribution Schema (DIST0)

This folder defines the canonical, deterministic shard model and cross-shard
messaging rules. It is a specification layer only; no runtime logic lives here.

## Contents
- `SPEC_SHARD_MODEL.md` — shard identity, determinism domains, ownership scopes.
- `SPEC_SHARD_OWNERSHIP.md` — ownership boundaries and migration rules.
- `SPEC_CROSS_SHARD_MESSAGES.md` — cross-shard message schema and ordering.

## Authority
These specs are binding for DIST0 and subordinate to ARCH0. If any runtime
implementation conflicts with these specs, the specs win.
