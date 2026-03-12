# Time Anchor Model

Purpose: define the deterministic long-run tick and epoch-anchor model that protects replay, compaction, and proof stability across very long universe lifetimes.

## Canonical Tick

- `tick_t` is canonical unsigned 64-bit integer time.
- `tick_t` starts at `0`.
- `tick_t` is monotonic.
- `tick_t` is never derived from wall-clock time.
- All authoritative truth mutation remains ordered only by canonical tick.

## Epoch Anchor

Epoch anchors are canonical record artifacts emitted on deterministic boundaries.

Required canonical fields:

- `anchor_id`
- `tick`
- `truth_hash`
- `contract_bundle_hash`
- `pack_lock_hash`
- `overlay_manifest_hash`
- `deterministic_fingerprint`
- `extensions`

The anchor payload must also carry the replay and proof context needed to validate a compacted or replayed window, including:

- hash-anchor or proof-anchor references
- anchor reason
- any bounding checkpoint or snapshot references when present

## Anchor Policy

The anchor cadence is governed by `data/registries/time_anchor_policy_registry.json`.

The canonical MVP policy requires:

- `anchor.interval_ticks = 10000`
- `anchor.emit_on_save = true`
- `anchor.emit_on_migration = true`

Anchors emitted because of save or migration policy still remain aligned to absolute canonical tick. The emission reason may differ, but the anchor tick itself is canonical.

## Time Warp / Batching

Time warp and other batched advancement remain lawful only when they preserve canonical per-tick semantics.

Required rules:

- batching advances canonical tick by deterministic integer steps
- process ordering remains deterministic
- anchor emission is evaluated against absolute tick, not against batch boundaries
- `advance N ticks` and `advance 1 tick N times` must yield the same truth hashes and anchor positions

## Compaction Boundary Contract

- compaction may only cut between epoch anchors
- compaction windows must be bounded by anchor IDs
- compaction outputs must record the lower and upper epoch-anchor IDs for the compacted region
- replay validation across a compacted region must succeed using those anchors

Epoch anchors are proof boundaries, not new truth semantics.

## Overflow Policy

The canonical `tick_t` maximum is:

- `18446744073709551615` (`2^64 - 1`)

TIME-ANCHOR-0 reserves the last `1,000,000` ticks for explicit rollover remediation only.

The refusal threshold is therefore:

- `18446744073708551615`

If advancing would move authoritative time above the refusal threshold, the system must refuse with:

- `refusal.time.tick_overflow_imminent`

Required remediation:

- start a new universe epoch or execute an explicit migration/rollover workflow

This is a theoretical guardrail for long-run universe safety. It does not change normal MVP behavior.

## Verification Obligations

The tooling and gates must verify:

- no mixed-width tick usage in scoped truth paths
- anchors are present at the configured interval
- anchors are stable across replay
- compaction boundaries align with anchors
- batched advancement preserves anchor placement and hashes
