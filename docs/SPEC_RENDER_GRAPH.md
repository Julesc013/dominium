# Render Graph Spec (Phase 1, High-Level) (REND0)

This document defines the high-level render graph contract.
Implementation details are deferred to later phases.

## Pass Model

- A render graph is a DAG of passes.
- Each pass has a stable `pass_id` and explicit inputs/outputs.
- Pass order MUST be deterministic for identical inputs.

## Deterministic Ordering

- Passes MUST be topologically sorted deterministically.
- Ties MUST be broken by stable `pass_id` ordering.
- No frame-time or wall-clock inputs may influence graph ordering.

## Collapsible/Expandable Graph

- Features MAY expand into multiple passes or collapse into a single pass.
- Collapse MUST be driven by RenderCaps and tier only.
- Collapse MUST NOT change simulation semantics.

## Resource Lifetime Tracking

- Resource lifetimes MUST be explicit (creation, usage range, release).
- Transient aliasing MUST be explicit and deterministic.
- No hidden global resources in the graph.

## Prohibitions

- Nondeterministic pass ordering is FORBIDDEN.
- Backend-specific graph branching outside `engine/render/**` is FORBIDDEN.
