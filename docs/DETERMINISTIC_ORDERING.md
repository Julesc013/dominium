# Deterministic Ordering Policy (DET2)

This document defines canonical ordering rules for authoritative simulation paths.
All authoritative code MUST produce identical results regardless of insertion order.
Violations are merge-blocking.

## Scope

Applies to authoritative directories:
- `engine/modules/core/**`
- `engine/modules/sim/**`
- `engine/modules/world/**`
- `game/rules/**`
- `game/economy/**`
- authoritative parts of `game/core/**`

## Ordering contracts (mandatory)

### Event queues
- Order by `(trigger_tick, order_key, event_id)`.
- `trigger_tick` is ACT time.
- `order_key` is a stable secondary key (domain- or subsystem-defined).
- `event_id` is a monotonic deterministic tie-breaker.

### Interest sets
- Order by stable identifiers and deterministic spatial keys.
- Interest volume lists MUST be canonicalized after collection.
- Tie-breaks MUST use explicit stable fields (domain_id, src_entity, quantized position).

### Ledger transactions
- Order by stable `transaction_id`.
- Obligations scheduled for the same ACT MUST use `obligation_id` as order_key.
- No insertion order may affect execution order.

### Market order books
- Price-time priority with stable `order_id` tie-break.
- Equal price/time orders MUST resolve by `order_id`.

### Effect fields (if present)
- Composition order MUST be stable and keyed (effect_id, source_id, tick).
- No pointer-order or insertion-order iteration.

## Allowed containers and patterns

Allowed in authoritative code:
- Arrays/vectors with explicit canonical sorting.
- Ordered maps with stable key ordering.
- Deterministic heaps with explicit secondary keys.

Forbidden in authoritative code unless normalized:
- `std::unordered_map`
- `std::unordered_set`
- Hash iteration without normalization

## Utilities (engine)

Use deterministic ordering helpers:
- `domino/core/det_order.h`
  - `dom_det_order_sort` (stable in-place sort)
  - `dom_det_heap_*` (deterministic min-heap)

Use deterministic ordering keys where appropriate:
- `core/dg_order_key.h` (engine internal)
- `core/det_invariants.h` ordering macros

## How to add new containers safely

1) Define a stable ordering key for every item.
2) Sort or normalize by that key before iteration.
3) Add explicit tie-breakers (never rely on insertion order).
4) Add a permutation-insertion test that proves invariance.
5) Update the CI matrix with a new DET-ORDER check ID.

## Tie-break key guidance

- Prefer stable IDs: entity_id, domain_id, transaction_id, order_id.
- Avoid pointer addresses, hash table bucket order, or allocation order.
- Ensure every comparison has a deterministic final tie-breaker.

## Examples

Good (canonical ordering):
```
dom_det_order_item items[3];
dom_det_order_sort(items, 3u);
```

Bad (nondeterministic):
```
for (auto &kv : unordered_map) { ... }
```

## Enforcement

CI enforces:
- `DET-ORD-004` (unordered container usage in authoritative dirs)
- `DET-ORDER-TEST-001..003` (permutation tests)

Violations are merge-blocking.
