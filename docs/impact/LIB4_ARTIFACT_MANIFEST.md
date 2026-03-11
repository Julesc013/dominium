Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# LIB4_ARTIFACT_MANIFEST

## Changed

- `schema/lib/artifact_manifest.schema`
- `schema/lib/artifact_reference.schema`
- `src/lib/artifact/__init__.py`
- `src/lib/artifact/artifact_validator.py`
- `tools/lib/content_store.py`
- `tools/share/share_cli.py`
- `tools/launcher/launcher_cli.py`

## Demand IDs

- `surv.knap_stone_tools`

## Contract Meaning

- shareable artifact bundles now carry a canonical artifact manifest or validated manifest sidecar
- profile bundles are treated as validated shareable artifacts during launcher preflight/start
- shareable artifact load now verifies content hash plus contract/capability compatibility before degrade/refuse
- artifact migration remains explicit invoke-only

## Unchanged

- pack loading remains on the PACK-COMPAT path
- instance/save identity stays hash-pinned as established by LIB-0 through LIB-3
- simulation behavior and authoritative mutation rules remain unchanged
