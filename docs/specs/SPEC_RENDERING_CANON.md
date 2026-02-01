Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Rendering Canon & Enforcement (REND0)

This document defines non-negotiable rendering architecture law.
It is enforceable and merge-blocking.

## Scope

- Rendering must remain modular, multi-backend, and deterministic with respect to simulation.
- Rendering MUST NOT influence authoritative simulation state or hashes.
- Rendering backends are owned by `engine/render/**` only.

## Immutable Directory Law

`engine/render/` is the canonical, immutable root for all rendering code.

```
engine/render/
├─ core/
├─ graph/
├─ features/
├─ shader/
├─ backends/
│  ├─ null/
│  ├─ software/
│  ├─ vulkan/
│  ├─ d3d12/
│  ├─ metal/
│  ├─ d3d11/
│  ├─ gl/
│  ├─ d3d9/
│  ├─ d3d7/
│  └─ gl_fixed/
└─ tests/
```

**Rules**
- Folder names are renderer identities.
- Version buckets are FORBIDDEN (no `gl2_3/`, `metal3_4/`, etc.).
- Capability-named folders are FORBIDDEN (no `implicit/`, `legacy/`, etc.).

**Rationale**
Folder names are stable identities; capability and version are expressed via RenderCaps, not path layout.

## Backend Family Semantics (Code-Level)

Each backend MUST report a `RenderBackendFamily`:
- Null
- Software
- Explicit (Vulkan, D3D12, Metal 2+)
- Implicit (D3D11, OpenGL core)
- ProgrammableLegacy (D3D9, OpenGL compat)
- FixedFunction (D3D7, OpenGL 1.x)

Backend family is metadata, not a folder taxonomy.

## Architecture Laws (Non-Negotiable)

### 1) API ≠ capability
- Backend selection MUST be by RenderCaps and tier, not API name.
- User intent MUST NOT mention API names or driver terminology.

**Rationale**
API names are mechanism; capabilities are intent and portability.

### 2) Explicit-first design law
- Core contracts MUST be valid for Vulkan/D3D12/Metal.
- Legacy backends MUST NOT introduce new abstractions.

**Rationale**
Explicit APIs are the future baseline; legacy is compatibility only.

### 3) Legacy-as-sink law
- `d3d7/` and `gl_fixed/` are emulation sinks only.
- They MAY consume collapsed graphs and fixed-function paths.
- They MUST NOT define core features, resource lifetime rules, or sync models.

**Rationale**
Fixed-function backends must not shape core architecture.

### 4) Rendering determinism law
- Rendering MUST NOT influence simulation state or hashes.
- Visual randomness is independently seeded and non-authoritative.
- Rendering feedback into authoritative systems is FORBIDDEN.

**Rationale**
Simulation determinism is a hard boundary.

### 5) Content scaling law
- Content MUST declare requirements, fallbacks, and cost model.
- Feature modules MUST declare caps requirements, fallback behavior, and cost model.
- Missing fallback is REFUSE.

**Rationale**
Scaling must be explicit and enforceable; no silent degradations.

## User Intent vs Mechanism

Users MAY select:
- Tier (auto/manual).
- Feature toggles.
- Quality/perf bias.

Users MUST NOT select:
- API names.
- Shader model numbers.
- Driver or backend terminology.

## Prohibitions (Absolute)

- Rendering backends under `client/` are FORBIDDEN.
- Renderer selection by API name in UI is FORBIDDEN.
- Backend-specific branching outside `engine/render/**` is FORBIDDEN.
- Legacy backends introducing new abstractions is FORBIDDEN.
- Continuous runtime shader compilation on UI thread is FORBIDDEN.