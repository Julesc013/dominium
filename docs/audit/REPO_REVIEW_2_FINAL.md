Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Repo Review 2 Final

Status: `DERIVED`
Source: `tools/review/tool_repo_inventory.py`

## Module Inventory Summary

- Result: `complete`
- Inventory fingerprint: `ff125c945b4e57d2ef2d61ed8ea05193521e9cd2f1b8b5296532608455e5913d`
- Entries scanned: `5493`
- Unknown layer entries: `0`

## Product Map

- Product registry entries: `7`
- AppShell bypasses: `0`

## Platform Surface Map

- Platform-specific heuristic count: `128`
- Renderer backends indexed: `3`

## Validation Surface Map

- Validation entrypoints: `13`

## Duplication/Drift Findings

- Semantic surfaces indexed: `8`
- Path-resolution heuristic candidates: `2172`
- RNG initialization heuristic candidates: `149`

## Stability Coverage Status

- Registry missing markers: `0`
- Pack manifests missing stability: `5`
- Artifact manifests missing stability: `66`

## Convergence Risk Areas

- `high` `validation surface fragmentation`: 13 validation entrypoints remain distributed across tooling surfaces
- `high` `virtual path bypass heuristics`: 2172 scanned files still use direct path heuristics
- `medium` `platform-gated surfaces`: 128 scanned files are platform-specific by heuristic
- `medium` `artifact stability coverage`: 66 artifact manifests do not declare stability metadata
- `low` `legacy-aligned modules`: 166 entries remain classified as legacy rather than core/domain/ui/platform

## Structural Unknowns

- No fatal structural unknowns detected.
