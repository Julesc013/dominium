# REPLACEMENT-PROTOCOL-01 Initial Replacement Inventory

Status: warning

This inventory is descriptive only. It does not retrofit historical move,
router, repair, or restructure work into formal replacement packets.

Command:

```text
python tools/validators/repo/check_replacement_packet.py --repo-root . --inventory --json
```

Result:

- files scanned: 17,942
- replacement-like files: 1,824
- inventory status: warning

## Categories

| Category | Count | Examples |
| --- | ---: | --- |
| historical_directory_replacement | 318 | `.aide/reports/AIDE-MOVE-01-APPLY-evidence.json`, `.aide/reports/MOVE-ROUTER-01-rollback.md`, `docs/repo/root-recycling/MOVE_ROUTER_01_APPLY_RESULT.md` |
| tooling_replacement | 40 | AIDE repair and router generated/evaluation evidence under `archive/generated/aide/**` |
| schema_protocol_replacement | 163 | `SCHEMA-PROTOCOL-LAW-01` evidence, schema-related AIDE generated fixtures, schema reports |
| provider_module_candidate | 42 | `PROVIDER-MODEL-01` and `MODULE-COMPOSITION-LAW-01` evidence packets and reports |
| future_replacement_candidate | 21 | `contracts/repo/dependency_directions.contract.toml`, `contracts/repo/layout.contract.toml`, `contracts/repo/root_allowlist.toml` |
| governance_replacement_history | 47 | API/ABI and canon audit reports |
| archive_generated_history | 659 | `archive/generated/**` AIDE exports and restructure reports |
| deferred | 534 | Older AIDE gate/readiness reports requiring case-by-case classification |

## Observations

- Historical directory moves already generated rollback, moved-item, skipped-item,
  reference-rewrite, and validation evidence.
- Root-recycling docs provide useful examples for future directory-restructure
  replacement packets.
- Generated archives preserve historical state but are not promoted to active
  replacement authority by this task.
- Future packets should capture old/new surface IDs, compatibility impact,
  proof, rollback, diagnostics, and refusal behavior explicitly.
