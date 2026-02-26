Status: CANONICAL
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: MAT-0 macro/meso/micro material representation rules
Binding Sources: docs/canon/constitution_v1.md, docs/canon/glossary_v1.md

# Tiered Material Representation

This document defines canonical material/part representation across macro, meso, and micro tiers.

## Macro Representation

- Macro stores material quantities only as ledger-compatible stock state.
- Macro stores quality and defect as statistical vectors/distributions.
- Macro is the canonical always-present scale.

## Meso Representation

- Meso logistics nodes store:
  - inventory counts,
  - batch references,
  - shipment commitments.
- Meso is used for deterministic routing/scheduling abstractions without global micro simulation.

## Micro Representation

- Micro stores explicit part assemblies and local part state, including:
  - wear markers,
  - defect flags,
  - geometry details.
- Micro exists only inside bounded ROI and is derived from macro + provenance + commitments.

## Cross-Tier Rules

- Macro never stores per-bolt/per-fastener entity records.
- Micro entities are ephemeral and derivable from macro + provenance state.
- Collapse and expand must preserve invariants and deterministic traceability.

