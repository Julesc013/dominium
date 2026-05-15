# ide Draft Salvage Map

## Status: Draft / Not Approved

- Apply allowed: `false`
- Approval status: `not_approved`
- Entry count: 6

## Recommended Fates

- `adapt`: 1
- `preserve_unknown`: 5

## Candidate Future Target Locations

No target paths are approved. Future targets must be selected by an approved move plan.

## High-Risk Files

- none

## preserve_unknown Files

- `ide/manifests`
- `ide/manifests/projection_manifest.schema.json`
- `ide/manifests/projection_manifest_examples`
- `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json`
- `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json`

## References Requiring Future Rewrite

- Raw references recorded: 21553

## Validators Required Before Any Move

- AIDE salvage-map check
- repo layout strict validator
- root allowlist strict validator
- distribution/component validators
- docs/build/UI/ABI checks as applicable

## Blockers Before Move

- No approved salvage map.
- No approved move map.
- No reference rewrite plan.
- No rollback evidence packet.
