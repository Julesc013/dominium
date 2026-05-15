# lib Draft Salvage Map

## Status: Draft / Not Approved

- Apply allowed: `false`
- Approval status: `not_approved`
- Entry count: 31

## Recommended Fates

- `adapt`: 22
- `preserve_unknown`: 9

## Candidate Future Target Locations

No target paths are approved. Future targets must be selected by an approved move plan.

## High-Risk Files

- `lib/__init__.py`
- `lib/artifact/__init__.py`
- `lib/artifact/artifact_validator.py`
- `lib/bundle/__init__.py`
- `lib/bundle/bundle_manifest.py`
- `lib/export/__init__.py`
- `lib/export/export_engine.py`
- `lib/import/__init__.py`
- `lib/import/import_engine.py`
- `lib/install/__init__.py`
- `lib/install/install_discovery_engine.py`
- `lib/install/install_validator.py`
- `lib/instance/__init__.py`
- `lib/instance/instance_clone.py`
- `lib/instance/instance_validator.py`
- `lib/provides/__init__.py`
- `lib/provides/provider_resolution.py`
- `lib/save/__init__.py`
- `lib/save/save_validator.py`
- `lib/store/__init__.py`
- `lib/store/gc_engine.py`
- `lib/store/reachability_engine.py`

## preserve_unknown Files

- `lib/artifact`
- `lib/bundle`
- `lib/export`
- `lib/import`
- `lib/install`
- `lib/instance`
- `lib/provides`
- `lib/save`
- `lib/store`

## References Requiring Future Rewrite

- Raw references recorded: 1241

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
