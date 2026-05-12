Status: PROVISIONAL
Phase: CONVERGE-04
Machine-Readable Authority: `contracts/distribution/layout.contract.toml`

# Cache And Staging Layout

Package cache, download partials, verification reports, staging, and rollback state are mutable operational projections. They are not source repository roots.

## Example Paths

```text
cache/
  packages/
  indexes/
  verify/
  staging/
  downloads/
    partial/
ops/
  transactions/
    <transaction_id>/
```

## Cache Rules

- Package cache keys are content hashes.
- Cache admission verifies `.dompkg` content before storing it as valid.
- Cache verification is deterministic and side-effect free.
- Partial downloads live under `cache/downloads/partial/` and must never appear as valid packages.
- Indexes and verification reports are evidence, not package identity by themselves.

## Staging Rules

- Staging is setup-owned mutable state.
- Staged payloads are not committed until verification succeeds.
- Failed staging rolls back through explicit transaction records.
- No package or install identity may depend on staging path names.

## Transaction And Rollback Rules

Setup, update, repair, uninstall, and rollback records live under `OPS_TRANSACTION_ROOT`, typically `ops/transactions/<transaction_id>/`.

Rollback is projection/lockfile based:

- previous lock/projection state is recorded
- rollback reprojects from verified cache and manifests
- previous layout digest must be restored exactly
- failures produce explicit refusal outcomes

Rollback is not ad hoc copying from whatever files happen to remain on disk.
