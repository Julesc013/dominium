# Modpack Format (MODPACK0)

Status: binding.
Scope: portable modpack bundles.

## Layout
```
modpack/
├── modpack.toml
├── capabilities.lock
└── packs/              # optional embedded packs
```

Rules:
- modpack.toml REQUIRED.
- capabilities.lock REQUIRED.
- Embedded packs are optional.
- No absolute paths.

## modpack.toml (required)
Fields:
- modpack_id
- modpack_version
- pack_format_version
- packs[]
- lockfile (default: capabilities.lock)
- extensions{}

## See also
- `docs/architecture/LOCKFILES.md`
- `docs/architecture/WORKSPACES.md`
