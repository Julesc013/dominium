Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Null Renderer

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: normative  
Version: 1.0.0  
Scope: RND-2 null renderer contract

## Purpose

The null renderer is a deterministic renderer backend for:

1. server/headless sessions
2. CI pipelines
3. deterministic render-contract tests

It consumes `RenderModel` only and does not produce pixels.

## Inputs and Outputs

Input:

1. `RenderModel` artifact

Derived outputs:

1. `frame_summary.json`
2. `frame_layers.json`
3. `render_snapshot.json` (renderer_id=`null`)

## Determinism

The null renderer must guarantee:

1. stable ordering of primitive/layer/count summaries
2. deterministic summary fingerprint and hash from canonical serialization
3. no wall-clock, thread, or hardware dependence

## Isolation

Forbidden:

1. TruthModel imports
2. simulation mutation
3. asset dependencies

The null renderer is a pure derived-artifact producer over `RenderModel`.
