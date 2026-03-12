Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Demand Impact Mapping

Use this directory to map runtime-domain changes to one or more `demand_id` entries from `data/meta/player_demand_matrix.json`.

## Why

- Prevents technically-correct but player-irrelevant drift.
- Feeds RepoX (`INV-CHANGE-MUST-REFERENCE-DEMAND`) and AuditX (`OrphanFeatureSmell`) enforcement.

## Minimal Format

```text
Change:
Touched Paths:
Demand IDs:
- <cluster>.<snake_case_demand>
Notes:
```

## Notes

- Keep IDs stable and copy exact tokens from the matrix registry.
- FAST lanes may warn for missing mapping; STRICT/FULL lanes escalate.
