# dominium-tools replay

Deterministic replay inspector.

Usage:
```
dominium-tools replay --input <replay_file> [--summary] [--dump-timeline <out_file>]
```

- Reads a replay file via `dsys_*` I/O.
- `--summary` prints byte count, checksum, and basic counters.
- `--dump-timeline` emits a CSV-like file with tick/event/checksum snapshots for offline inspection.
