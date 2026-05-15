# repo Draft Salvage Map

## Status: Draft / Not Approved

- Apply allowed: `false`
- Approval status: `not_approved`
- Entry count: 13

## Recommended Fates

- `preserve_unknown`: 13

## Candidate Future Target Locations

No target paths are approved. Future targets must be selected by an approved move plan.

## High-Risk Files

- `repo/canon_state.json`
- `repo/release_policy.toml`
- `repo/repox/repox_exemptions.json`
- `repo/repox/rulesets/abstraction.json`
- `repo/repox/rulesets/change_shape.json`
- `repo/repox/rulesets/core.json`
- `repo/repox/rulesets/data_first.json`
- `repo/repox/rulesets/derived_artifacts.json`
- `repo/repox/rulesets/packaging.json`
- `repo/repox/rulesets/security.json`
- `repo/repox/rulesets/ui_parity.json`

## preserve_unknown Files

- `repo/canon_state.json`
- `repo/release_policy.toml`
- `repo/repox`
- `repo/repox/repox_exemptions.json`
- `repo/repox/rulesets`
- `repo/repox/rulesets/abstraction.json`
- `repo/repox/rulesets/change_shape.json`
- `repo/repox/rulesets/core.json`
- `repo/repox/rulesets/data_first.json`
- `repo/repox/rulesets/derived_artifacts.json`
- `repo/repox/rulesets/packaging.json`
- `repo/repox/rulesets/security.json`
- `repo/repox/rulesets/ui_parity.json`

## References Requiring Future Rewrite

- Raw references recorded: 1107

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
