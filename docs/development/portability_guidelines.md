Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Portability Guidelines

Dominium mainline full-native products are governed by `source_native_64`: `x86_64` and `arm64`, 64-bit word size, little endian, C17/C++17, and C-compatible public ABI. The architecture policy is `contracts/platform/architecture_policy.contract.toml`.

32-bit targets are constrained or research lanes unless a future reviewed policy promotes them with explicit evidence. Legacy and vintage systems use constrained-native, projection, replay/snapshot, or archive-runner lanes rather than changing the mainline product obligation.

Use the portability matrix when adding or changing platform, toolchain, provider, product mode, package, or release claims.

## Adding A Target

Add or update the relevant registry/matrix row under `contracts/platform/`. Declare platform floor, architecture, architecture tier, word size, endian policy, toolchain, ABI, language floor, filesystem/path policy, dynamic loading, threading, provider capabilities, product modes, support status, diagnostics, refusals, and evidence paths.

Choose `planned` or `research` unless proof already exists. Do not call a target supported because a directory, preset, or local compiler exists.

## Proving Status

Use `build_proven` only with build/configure evidence. Use `smoke_proven` only with smoke evidence. Use `product_proven` only with product boot/projection proof. Use `supported` only when build, smoke, product, package, and release proof all exist.

Evidence paths should be committed reports or task evidence. Do not record machine-local install paths.

## Providers And Modes

Provider support must reference provider or capability IDs. Product mode rows must reference runtime capabilities. Unsupported requests must produce typed diagnostics/refusals instead of silent fallback.

## Pointer Width

Native pointer size is not simulation truth. Stable data uses fixed-width explicit little-endian formats; see `docs/development/pointer_width_and_serialization.md`.

## Validation

Run:

```text
python tools/validators/platform/check_portability_matrix.py --repo-root . --strict
python tools/validators/platform/check_portability_matrix.py --repo-root . --fixtures
```

Use inventory mode for gap analysis only; it does not prove support.
