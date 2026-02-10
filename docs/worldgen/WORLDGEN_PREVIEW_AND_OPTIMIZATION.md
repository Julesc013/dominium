Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Worldgen Preview And Optimization

Preview generation provides fast, deterministic feedback without changing simulation semantics.

## Preview Layers

- Terrain elevation
- Hydrology channels
- Climate placeholder layer (stub)
- Resources placeholder layer (stub)

## Cache Contract

- Cache key is derived from module ID, seed, and input hash.
- Cache hits are deterministic and read-only.
- Cache invalidation is deterministic on input change.

## Progressive Rendering

- Low-resolution results may render first.
- Refinement must preserve deterministic final output.
- Preview-only fields are marked non-authoritative.

## Performance Boundaries

- Preview work runs within declared budget policy.
- Refusals are explicit on budget or capability mismatch.
- Profiling output is derived and non-authoritative.

