Status: AUTHORITATIVE
Last Reviewed: 2026-02-16
Version: 1.0.0

# Diplomacy Stubs

## CIV-1 Intent
Diplomacy in CIV-1 is a deterministic state substrate only. It does not apply combat, trade, or governance mechanics.

## Relation State
- Diplomatic relations are stored as structured records keyed by faction pairs.
- CIV-1 uses symmetric relation updates.
- Relation values are registry-driven (`diplomatic_state_registry`).

## Process Surface
- `process.diplomacy_set_relation` is the only mutation path in CIV-1.
- Entitlement and law gating are mandatory.
- Unsupported relation states refuse deterministically.

## Deterministic Ordering
- Relation records are sorted by `(faction_a, faction_b)`.
- Pair canonicalization is lexicographic (`min`, `max`) before update.

## Future Extension Hooks
- Asymmetric relations.
- Treaty metadata and expiry.
- Trade/war integration through separate process families.

