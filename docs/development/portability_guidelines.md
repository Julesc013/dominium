Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Portability Guidelines

Use the portability matrix when adding or changing platform, toolchain, provider, product mode, package, or release claims.

## Adding A Target

Add or update the relevant registry/matrix row under `contracts/platform/`. Declare platform floor, architecture, toolchain, ABI, language floor, filesystem/path policy, dynamic loading, threading, provider capabilities, product modes, support status, diagnostics, refusals, and evidence paths.

Choose `planned` or `research` unless proof already exists. Do not call a target supported because a directory, preset, or local compiler exists.

## Proving Status

Use `build_proven` only with build/configure evidence. Use `smoke_proven` only with smoke evidence. Use `product_proven` only with product boot/projection proof. Use `supported` only when build, smoke, product, package, and release proof all exist.

Evidence paths should be committed reports or task evidence. Do not record machine-local install paths.

## Providers And Modes

Provider support must reference provider or capability IDs. Product mode rows must reference runtime capabilities. Unsupported requests must produce typed diagnostics/refusals instead of silent fallback.

## Validation

Run:

```text
python tools/validators/platform/check_portability_matrix.py --repo-root . --strict
python tools/validators/platform/check_portability_matrix.py --repo-root . --fixtures
```

Use inventory mode for gap analysis only; it does not prove support.
