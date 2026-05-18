Status: DERIVED
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-02

# MOVE-ROUTER-02 Repair Ledger

## Summary

| Issue class | Count |
| --- | ---: |
| `historical_reference_ok` | 3 |
| `quarantine_reference_ok` | 71 |
| `stale_path_reference` | 1698 |
| `unknown` | 1 |


Total issues recorded: 1773.

## Initial Disposition

- Semantic route items are candidates for active exact path/import repair.
- Quarantine route items are not active targets unless an archival reference is
  intended.
- Historical, audit, and generated evidence references are preserved.
- Validation failures discovered later in MOVE-ROUTER-02 are appended to this
  ledger through the repair reports rather than silently fixed.
