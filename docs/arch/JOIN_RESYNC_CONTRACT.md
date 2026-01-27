# Join and Resync Contract (MMO0)

Status: binding.
Scope: deterministic join, resync, and snapshot transfer rules for clients and
shards.

## Join contract (required inputs)

To join a running universe, a client or shard MUST receive a deterministic
bundle that includes:

- WorldDefinition
- capability lockfile
- the latest snapshot or macro capsule set
- the event log tail (including cross-shard logs where applicable)

Join MUST refuse explicitly if the required bundle is incomplete.

## Deterministic resync rules

Resync MUST be deterministic and auditable:

1) Validate WorldDefinition and capability lockfile.
2) Load the latest snapshot or macro capsules.
3) Apply the event log tail in deterministic order.
4) Verify deterministic hashes or invariants where defined.

No step may depend on wall-clock time.

## Partial data refusal semantics

Partial, inconsistent, or capability-incompatible data MUST result in explicit
refusal or a deterministic fallback mode.

Canonical outcomes:

- REFUSE_CAPABILITY_MISSING
- REFUSE_INVALID_INTENT
- frozen inspect-only participation

## Snapshot and macro capsule transfer

Snapshot transfer MUST preserve determinism:

- snapshots and macro capsules are authoritative inputs
- unknown fields MUST be preserved
- transfers are commit-boundary artifacts, not mid-commit mutations

## Frozen and inspect-only modes

When capabilities are missing or live participation is unsupported:

- frozen and inspect-only modes are allowed
- live participation MUST refuse explicitly
- replay MUST remain deterministic

## Related invariants

- MMO0-RESYNC-017
- MMO0-COMPAT-018
- SCALE0-REPLAY-008

## See also

- `docs/arch/MMO_COMPATIBILITY.md`
- `docs/arch/REFUSAL_SEMANTICS.md`
- `docs/arch/MACRO_TIME_MODEL.md`
