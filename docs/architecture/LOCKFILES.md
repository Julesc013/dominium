Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Lockfiles (LOCK0 / LIB-0)

Status: binding.
Scope: deterministic capability and pack resolution artifacts.

## Authoritative Forms

- Legacy adapter: `schema/capability_lockfile.schema`
- LIB-0 canonical pack lock artifact: `schema/packs/pack_lock.schema`

## Storage Rules

- Lock artifacts are immutable CAS entries under `store/locks/<hash>/` or `embedded_artifacts/locks/<hash>/`.
- Instances and saves pin lock identity by `pack_lock_hash`.
- Path-based `capability_lockfile` references remain compatibility adapters only.

## Determinism Rules

- Same pack set and policy inputs must produce the same `pack_lock_hash`.
- `ordered_pack_ids` ordering is canonical.
- Missing required packs must refuse or degrade explicitly according to declared missing-mode policy.
- No absolute host paths may appear in canonical lock payloads.

## Related Contracts

- `schema/packs/pack_lock.schema`
- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
- `docs/architecture/INSTANCE_MODEL.md`
