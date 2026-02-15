Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Bound to run-meta contract, anti-cheat event schema, handshake schema, and hash-anchor chain.

# Esports Proof Artifacts

## Purpose
Define deterministic proof bundle contents for ranked/esports session audit and dispute workflows.

## Required Bundle Contents

1. Handshake transcript
2. lockfile snapshot
3. pack signature table
4. registry hash table
5. per-tick hash anchors or deterministic checkpoint map
6. anti-cheat event log
7. enforcement action log

## Canonical Structure
Proof bundle is a deterministic JSON object with:

1. `schema_version`
2. `proof_bundle_id`
3. `server_profile_id`
4. `securex_policy_id`
5. `anti_cheat_policy_id`
6. `pack_lock_hash`
7. `registry_hashes`
8. `handshake`
9. `pack_signatures`
10. `hash_anchor_frames`
11. `anti_cheat_events`
12. `enforcement_actions`
13. `provenance`

## Deterministic Requirements

1. Stable key ordering (canonical serializer).
2. Stable array ordering:
   - signatures by `pack_id`
   - anchors by `(tick, shard_id)`
   - anti-cheat events by deterministic fingerprint
3. Run timestamps are informational and excluded from canonical comparison hashes.

## Content Addressing

1. Proof bundle hash:
   - canonical hash over deterministic fields.
2. Provenance header includes:
   - `pack_lock_hash`
   - registry hashes
   - generator tool id/version

## Export Tool Contract
`tools/net/tool_export_ranked_proof_bundle` must emit:

1. JSON artifact
2. deterministic Markdown summary
3. refusal on missing required components

Example:

```text
python tools/net/tool_export_ranked_proof_bundle.py --run-meta saves/<save_id>/run_meta/<run_id>.json --out-dir build/net/proofs --out-prefix ranked_proof_bundle
```

## Cross-References

- `docs/net/RANKED_SERVER_GOVERNANCE.md`
- `docs/security/SECUREX_TRUST_MODEL.md`
- `schemas/net_handshake.schema.json`
- `schemas/net_hash_anchor_frame.schema.json`
- `schemas/net_anti_cheat_event.schema.json`
