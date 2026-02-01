Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# dominium-tools assetc

Asset compiler for authoring data.

Usage:
```
dominium-tools assetc --input <src_dir> --output <pack_dir> [--type graphics|sounds|music] [--name <pack_name>]
```

- Reads raw authoring data from `data/authoring/<type>/`.
- Emits pack output under `data/packs/<type>/<pack_name>/` with a simple manifest listing packed files.
- Uses Domino’s `dsys_*` filesystem API; ensure output directories exist.