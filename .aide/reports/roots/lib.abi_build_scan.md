# lib Abi Build Scan

## Status

- Scan type: `abi_build_scan`
- Findings: 270
- Moves/rewrites applied: `false`

## Markers Found

- `lib/artifact/artifact_validator.py:10` contract
- `lib/artifact/artifact_validator.py:12` tool
- `lib/artifact/artifact_validator.py:47` contract
- `lib/artifact/artifact_validator.py:48` ABI
- `lib/artifact/artifact_validator.py:66` schema
- `lib/artifact/artifact_validator.py:67` schema
- `lib/artifact/artifact_validator.py:68` schema
- `lib/artifact/artifact_validator.py:69` schema
- `lib/artifact/artifact_validator.py:70` schema
- `lib/artifact/artifact_validator.py:156` contract
- `lib/artifact/artifact_validator.py:158` contract
- `lib/artifact/artifact_validator.py:159` contract
- `lib/artifact/artifact_validator.py:162` contract
- `lib/artifact/artifact_validator.py:163` contract
- `lib/artifact/artifact_validator.py:164` contract
- `lib/artifact/artifact_validator.py:198` schema
- `lib/artifact/artifact_validator.py:199` schema
- `lib/artifact/artifact_validator.py:200` schema
- `lib/artifact/artifact_validator.py:282` schema
- `lib/artifact/artifact_validator.py:293` contract
- `lib/artifact/artifact_validator.py:294` contract
- `lib/artifact/artifact_validator.py:314` contract
- `lib/artifact/artifact_validator.py:326` contract
- `lib/artifact/artifact_validator.py:554` contract
- `lib/artifact/artifact_validator.py:559` contract
- `lib/artifact/artifact_validator.py:560` contract
- `lib/artifact/artifact_validator.py:561` contract
- `lib/artifact/artifact_validator.py:562` contract
- `lib/artifact/artifact_validator.py:567` contract
- `lib/artifact/artifact_validator.py:568` contract
- `lib/artifact/artifact_validator.py:581` ABI
- `lib/artifact/artifact_validator.py:633` contract
- `lib/artifact/artifact_validator.py:634` contract
- `lib/artifact/artifact_validator.py:661` ABI
- `lib/artifact/artifact_validator.py:662` contract
- `lib/artifact/__init__.py:17` ABI
- `lib/artifact/__init__.py:18` contract
- `lib/artifact/__init__.py:57` ABI
- `lib/artifact/__init__.py:58` contract
- `lib/bundle/bundle_manifest.py:186` contract
- `lib/bundle/bundle_manifest.py:205` contract
- `lib/bundle/bundle_manifest.py:216` contract
- `lib/bundle/bundle_manifest.py:301` contract
- `lib/bundle/bundle_manifest.py:335` contract
- `lib/export/export_engine.py:10` runtime
- `lib/export/export_engine.py:28` contract
- `lib/export/export_engine.py:31` tool
- `lib/export/export_engine.py:99` contract
- `lib/export/export_engine.py:401` contract
- `lib/export/export_engine.py:402` contract

## Highest-Risk Files

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

## Unknowns

- preserve_unknown entries: 9

## Future Validator Needs

Dedicated validators are required before moving any sensitive files from this root.
