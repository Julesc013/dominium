Status: DEFERRED
Last Reviewed: 2026-05-23
Supersedes: none
Superseded By: none
Stability: provisional

# Workbench Shell

This directory reserves the Workbench shell ownership boundary.

The shell owns the composed workspace manager, command palette, module registry
viewer, status/evidence surfaces, and layout persistence when those
implementations exist. Reusable UI, projection, diagnostics, provider, and
runtime behavior belongs under `runtime/` or `contracts/`, not in this shell
boundary.
