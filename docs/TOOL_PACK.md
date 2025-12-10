# dominium-tools pack

Pack/version builder.

Usage:
```
dominium-tools pack --version <ver> --output <versions_dir> [--include base,space,war]
```

- Reads existing packs under `data/packs/`.
- Produces `data/versions/<ver>/manifest.txt` listing included packs and basic metadata.
- Uses `dsys_*` I/O; ensure the destination directory exists.
