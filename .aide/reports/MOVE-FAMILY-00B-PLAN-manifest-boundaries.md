# MOVE-FAMILY-00B-PLAN Manifest Boundaries

Status: DRAFT
Last Reviewed: 2026-05-17

## Manifest Files

| Path | Classification | Target Owner | Target Path | Risk |
| --- | --- | --- | --- | --- |
| `ide/manifests/projection_manifest.schema.json` | projection contract metadata | `contracts/projection/ide` | `contracts/projection/ide/projection_manifest.schema.json` | medium |
| `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json` | projection contract metadata / example fixture | `contracts/projection/ide` | `contracts/projection/ide/examples/example_linux_clang_modern_client_gui.projection.json` | medium |
| `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json` | projection contract metadata / legacy example fixture | `contracts/projection/ide` | `contracts/projection/ide/examples/example_win_vc6_win9x_client_gui.projection.json` | medium |

## Ownership Boundary

The tracked schema and examples are source metadata. They are not generated release/projection proof output and should not be archived as generated evidence.

`contracts/projection/ide/**` is the preferred owner because:

- `contracts/` owns machine-readable and compatibility-sensitive authority surfaces;
- projection manifest shape is the primary identity, with IDE as a projection family qualifier;
- docs already own the human explanation under `docs/architecture/IDE_PROJECTIONS.md`;
- tools and CMake consume or generate manifests but do not own the schema/example contract.

## Generated Output Boundary

Generated projection manifests may still be written to:

```text
ide/manifests/<projection_id>.projection.json
```

Those generated files must remain ignored and uncommitted. The planned move only relocates the tracked source schema and examples.

## Contract Slot Note

`contracts/projection/ide/**` does not exist yet. A later apply task should create it as a scoped contract/projection ownership path and update the relevant references. This plan does not modify `contracts/**`.
