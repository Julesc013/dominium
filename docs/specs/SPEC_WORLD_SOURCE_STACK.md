Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES (Phase 1 overrides apply):
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Tools -> engine public API + game public API only.
- Launcher/Setup -> libs/ + schema only (no engine/game dependencies).
--------------------------------
# SPEC_WORLD_SOURCE_STACK — World Source Stack Canon

Status: draft
Version: 1

## Purpose
Define the canonical World Source Stack (WSS): a unified, deterministic mechanism
for answering world queries without caring whether the answer comes from procedural
generation, real-world datasets, derived data, or player overrides.

This is a documentation-only contract. No runtime logic is defined here.

## Core axioms (locked)
1) The engine never knows or cares about data origin.
2) All data sources are deterministic providers.
3) All providers are versioned and hashable.
4) Overrides always win over datasets.
5) Datasets always win over procedural generation.
6) Procedural generation always wins over analytic baselines.
7) Missing data is filled deterministically, never fabricated ad hoc.
8) Sampling is lazy, interest-bounded, and cacheable.
9) All queries are pure functions of inputs.
10) World definition must be portable and replayable.

## Definitions

### World Source Stack (WSS)
An ordered stack of data layers for a given world object. Queries are evaluated
top-down until a layer can answer. The stack is deterministic and portable.

### Layer
A provider of values for a defined domain. Each layer declares:
- coverage mask
- precision/LOD availability
- version and schema
- deterministic hash

### Coverage mask
A declaration of where a layer has authoritative data. Outside the mask, a query
falls through to the next layer.

### Provider
A pure interface:

    sample(query, lod, context) -> value | UNKNOWN

Providers have no side effects and do not mutate state.

### Overrides
Sparse, authoritative changes that always win:
- terrain edits
- constructions
- scars
- governance overlays
Stored in universe bundles and applied at the top of the stack.

## Canonical stack order (mandatory)

Layer 0 — Overrides  
Layer 1 — Imported Datasets  
Layer 2 — Derived Datasets  
Layer 3 — Procedural Generators  
Layer 4 — Analytic Baselines

This order is fixed. Silent fallback or reordering is forbidden.

ASCII diagram:

  Query -> [L0 Overrides] -> [L1 Imported] -> [L2 Derived] -> [L3 Procedural] -> [L4 Analytic]
             | hit? yes -> return
             | hit? no  -> fall through

## Domains (must be supported)
Each domain has its own providers, coverage masks, and LOD policy.

- Ephemerides (position vs ACT time)
- Surface geometry / height
- Surface topology
- Biomes / land cover
- Lithology / geology
- Resource fields
- Climate parameters
- Atmospheric parameters (later stages)

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- define provider interfaces
- perform deterministic sampling
- cache sampled results
- provide deterministic LOD helpers and cache containers
- hash provider outputs

Engine MUST NOT:
- know file formats (GeoTIFF, etc.)
- parse real-world datasets
- know procedural recipes as content

Game (Dominium, C++98) MAY:
- load provider bindings from data packs
- configure stacks per body/system
- define interest-set and LOD selection policy
- expose tools for import and inspection

## Determinism and identity binding

### Pinned order and versions
For each world instance:
- stack order is pinned and recorded
- provider ids, versions, and parameters are recorded
- provider hashes are recorded

### Identity digest inputs
Changes to any of the following are sim-affecting and must change the identity digest:
- stack order
- provider id/version
- provider parameters
- coverage mask definition

Any such change must:
- create a new feature epoch, or
- require explicit migration

### Sampling determinism
Sampling is a pure function of:
- query parameters
- LOD
- provider parameters
- deterministic inputs (seed, if any)
Caching must not affect results.

## Performance requirements
- No global dataset loading.
- Tile-addressable providers only.
- Lazy loading driven by interest sets.
- Multi-LOD queries and deterministic LOD selection.
- Cache eviction policies are deterministic and do not affect results.

## Integration points

### Effect fields
Effect fields are derived views that query the WSS for authoritative inputs. They
do not define new canonical data. Effect field generation must not fabricate data.

### Fidelity projection
WSS outputs are projected into presentation fidelity layers. Reduced fidelity is
allowed, but it must not alter authoritative quantities or order.

### Interest sets
Interest sets bound sampling and cache scope. WSS queries are driven by active
interest sets (bubbles, views, or tools) and never by global iteration.

### Provenance and non-fabrication law
Every WSS value must have provenance metadata (layer, provider id/version).
Unknown data stays UNKNOWN. Derived datasets must declare their source inputs.

## Prohibitions (enforced)
- Mixing procedural and dataset logic in one provider.
- Runtime data imports.
- Non-deterministic interpolation.
- Floating-point nondeterminism.
- Implicit fallback order changes.
- Hidden data synthesis.

## Worked examples (mandatory)

### 1) Procedural planet only
Stack:
- L0: none
- L1: none
- L2: none
- L3: procedural generator (full coverage)
- L4: analytic baseline (fallback)

Coverage:
- L3 provides full coverage; L4 is never used.

Determinism:
- Sampling depends only on seed + query; cache is non-authoritative.

### 2) Earth with mixed DEM
Stack:
- L0: player edits (cities)
- L1: high-res DEM for city tiles, coarse DEM global
- L2: derived slope/roughness tiles
- L3: procedural infill for missing tiles
- L4: analytic ellipsoid

Coverage:
- City tiles: L1 high-res
- Elsewhere: L1 coarse or L3 procedural

Sampling order:
- Overrides -> imported DEM -> derived -> procedural -> ellipsoid

### 3) Planet with no lithology dataset
Stack for lithology domain:
- L0: overrides (mining scars)
- L1: none
- L2: derived geology from height/climate (offline)
- L3: procedural geology generator
- L4: analytic baseline (constant lithology)

Determinism:
- L2 is fixed and versioned; no runtime inference.

### 4) Terraform edit overriding dataset terrain
Stack for height domain:
- L0: local terraforming edits
- L1: imported DEM
- L2: derived smoothing tiles
- L3: procedural fallback
- L4: analytic baseline

Result:
- L0 edits always win, even if they conflict with imported data.

### 5) Ephemerides fallback
Stack for ephemerides:
- L0: mission overrides (if any)
- L1: imported JPL ephemerides
- L2: derived orbital fit (offline)
- L3: procedural on-rails generator
- L4: analytic baseline (simple Keplerian)

Determinism:
- Provider versions and parameters are pinned; changes require migration.

## Test and validation requirements (spec-only)
Implementations must provide:
- provider determinism tests
- tile seam consistency tests
- stack order enforcement tests
- migration refusal tests
- latent universe performance tests (interest-bounded sampling)