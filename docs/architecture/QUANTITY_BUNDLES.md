Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Quantity Bundles

Status: Authoritative (META-MODEL-2)

## Purpose

`QuantityBundle` upgrades FlowSystem from scalar-only channels to deterministic coupled multi-quantity channels without breaking legacy single-quantity flows.

## Definition

A `QuantityBundle` is an ordered list of `quantity_id` values describing components carried by a flow channel as one coupled transfer vector.

- Single quantity channel: equivalent to bundle size `1`.
- Bundle channel: explicit multi-component transfer with per-component policy handling.

## Channel Semantics

A flow channel may operate in either mode:

1. Legacy scalar mode:
   - `quantity_id` present.
   - Existing scalar transfer behavior remains unchanged.

2. Bundle mode:
   - `quantity_bundle_id` present.
   - Transfer/loss computed per component.
   - Optional component capacity and loss policies apply per `quantity_id`.

## Capacity and Loss

Capacity/loss can be evaluated at two levels:

- Bundle-level baseline: existing channel capacity/loss fields.
- Component-level overrides: policy maps keyed by `quantity_id`.

Component loss policy may specify deterministic transform behavior:

- `transform_to_quantity_id` allows explicit conversion of lost amount into another quantity component.
- If no transform target is declared for conserved components, engine must log an exception path (no silent disappearance).

## Deterministic Ordering and Hashing

- Bundle `quantity_ids` are ordered and persisted in canonical order.
- Component transfer/loss maps are normalized by sorted `quantity_id` keys.
- Event fingerprints include canonical component maps.

## Model Integration

Constitutive models can read/write bundle components by explicit component selector.

- Inputs: `flow_quantity` supports component selector semantics.
- Outputs: `flow_adjustment` can target specific bundle components.

All model-driven flow mutation remains process-only (`process.flow_adjust`).

## Backward Compatibility

- Legacy channels without `quantity_bundle_id` remain valid.
- Legacy transfer events remain valid with scalar fields.
- Bundle fields are additive and optional.
- CompatX supports both prior and upgraded flow schema versions.
- Adapter helpers are provided for legacy scalar callers:
  - `flow_channel_primary_quantity_id(...)`
  - `flow_transfer_components(...)`
  - `flow_loss_components(...)`

## Performance/Budget

- Channel iteration order remains `channel_id` sorted.
- Budget degradation remains deterministic first-N channel processing.
- Bundle component loops are deterministic by sorted `quantity_id` order.
