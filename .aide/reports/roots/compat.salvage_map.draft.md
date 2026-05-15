# compat Draft Salvage Map

## Status: Draft / Not Approved

- Apply allowed: `false`
- Approval status: `not_approved`
- Entry count: 21

## Recommended Fates

- `adapt`: 17
- `preserve_unknown`: 4

## Candidate Future Target Locations

No target paths are approved. Future targets must be selected by an approved move plan.

## High-Risk Files

- `compat/__init__.py`
- `compat/capability_negotiation.py`
- `compat/data_format_loader.py`
- `compat/migration_lifecycle.py`
- `compat/descriptor/__init__.py`
- `compat/descriptor/descriptor_engine.py`
- `compat/handshake/__init__.py`
- `compat/handshake/handshake_engine.py`
- `compat/negotiation/__init__.py`
- `compat/negotiation/degrade_enforcer.py`
- `compat/negotiation/negotiation_engine.py`
- `compat/shims/__init__.py`
- `compat/shims/common.py`
- `compat/shims/flag_shims.py`
- `compat/shims/path_shims.py`
- `compat/shims/tool_shims.py`
- `compat/shims/validation_shims.py`

## preserve_unknown Files

- `compat/descriptor`
- `compat/handshake`
- `compat/negotiation`
- `compat/shims`

## References Requiring Future Rewrite

- Raw references recorded: 1942

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
