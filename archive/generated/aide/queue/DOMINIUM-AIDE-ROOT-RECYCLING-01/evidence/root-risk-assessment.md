# Root Risk Assessment

Status: needs_review

## Root Risk

- Root: `ide/`
- Risk class: high / review_required
- Reason: binding README, schema identity, generated-output policy, and baseline unknown ownership.

## Authority-Sensitive Files

- `ide/README.md`: declares binding root behavior and regeneration rules.

## Identity-Sensitive Files

- `ide/manifests/projection_manifest.schema.json`: schema identity for IDE projection manifests.

## Generated-Sensitive Files

- `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json`
- `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json`

## Build-Sensitive Files

No selected tracked file is directly build-sensitive, but the examples reference generated IDE projection outputs and regeneration commands, so future work must check build/projection effects before any path change.

## Unknown-Risk Files

Dominium Q52 overlay classified all four tracked files. Baseline AIDE classification still marks the two example projection manifests as unknown, which should drive future classifier improvement rather than file movement.

## No-Move / No-Delete Explanation

`ide/` is not cleanup-ready. It contains a binding README, schema truth, and tracked fixtures. Any future change requires a reviewed salvage map, reference inventory, schema validation, and path-alias/rewrite analysis.
