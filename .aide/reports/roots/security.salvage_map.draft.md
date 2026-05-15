# security Draft Salvage Map

## Status: Draft / Not Approved

- Apply allowed: `false`
- Approval status: `not_approved`
- Entry count: 5

## Recommended Fates

- `adapt`: 4
- `preserve_unknown`: 1

## Candidate Future Target Locations

No target paths are approved. Future targets must be selected by an approved move plan.

## High-Risk Files

- `security/__init__.py`
- `security/trust/__init__.py`
- `security/trust/license_capability.py`
- `security/trust/trust_verifier.py`

## preserve_unknown Files

- `security/trust`

## References Requiring Future Rewrite

- Raw references recorded: 644

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
