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
- None. Game consumes engine primitives where applicable.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC: Facades + Backends (Versioned Vtables)

This document defines the facade/backend architecture used for Domino/DOMinium subsystems (e.g. `dsys`, `dgfx`) and future modules (jobs, SIMD kernels, IO streaming).

Related:
- `docs/specs/SPEC_LANGUAGE_BASELINES.md`
- `docs/specs/SPEC_ABI_TEMPLATES.md`

## Definitions

- **Facade**: A public, baseline-visible ABI surface expressed as a POD function table (vtable). Facades are stable, versioned, and extension-ready.
- **Backend**: A concrete implementation behind a facade. Backends can vary per platform and per build profile, but must not change facade ABI.

## Language Baselines (Hard Rules)

- **Domino core is C89/C90 forever.**
- **Dominium is C++98 forever.**
- Public headers under `include/` that are baseline-visible must remain compatible with these baselines.
- Newer language standards may be used only in optional acceleration layers and must never be required for correctness or compatibility.

### Explicitly Rejected: Runtime Language Standard Switching

The project does not support any runtime “C89 vs C11” (or “C++98 vs C++11”) switching. Language standard selection is a **compile-time** property only. Build/profile flags are represented as macros (see `domino/config_base.h`), not runtime toggles.

## Facade ABI Pattern

Each facade vtable:
- is **POD** (no C++ types, no templates, no exceptions),
- begins with `{ abi_version, struct_size }`,
- exposes functions only via table entries (no required `static inline` helpers),
- supports extension discovery via `query_interface` where applicable.

Recommended retrieval pattern:
- A single exported entry point returns the requested vtable version by value-copy into a caller-provided struct (e.g., `dsys_get_core_api(1, &out)`).
- If the requested ABI version is unsupported, return an “unsupported” error code and leave the output unmodified or set to a safe default.

## Extension Discovery

Facades reserve growth via:
- `query_interface(iid, &out_iface)` returning additional facet vtables, optional surfaces, or vendor/platform extensions.
- Stable `dom_iid` constants for each interface version.

Rules:
- Unknown/unsupported IIDs must return “unsupported”.
- Returned interface pointers must remain valid for at least the lifetime documented by the module (typically process lifetime for static vtables).

## Ownership and Handles

- Cross-module ownership must be explicit (create/destroy pairs, or “borrowed” pointers with documented lifetime).
- Avoid transferring raw pointers to heap memory across boundaries unless the allocation/freeing conventions are explicitly part of the ABI.
- If a platform “native handle” is exposed, it must be via an explicit optional extension surface (or clearly documented as such).

## Current Facades

- **DSYS**: Versioned `dsys_*_api_v1` vtables with `dsys_get_core_api()` and facet discovery via `query_interface`.
- **DGFX**: Versioned `dgfx_ir_api_v1` as the baseline graphics IR surface; optional `dgfx_native_api_v1` reserved for platform-native extensions.

## Future Facade Templates

Header-only templates exist for:
- Jobs: `include/domino/jobs.h`
- SIMD kernels: `include/domino/simd.h`
- Streaming IO: `include/domino/io.h`

These templates are ABI-shape commitments only; they are not wired into runtime behavior until explicitly implemented and selected by later prompts.