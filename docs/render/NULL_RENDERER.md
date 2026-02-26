# Null Renderer

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
