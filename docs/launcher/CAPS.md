# CAPS

The launcher exposes a deterministic capability snapshot for bug reports and CI.

## Command
```
dominium-launcher caps --format=tlv|text [--out=<path>]
```

- `--format=text` (default) prints to stdout unless `--out` is provided.
- `--format=tlv` requires `--out` and writes a binary TLV snapshot.

## Storage
- Per-run: `instances/<id>/logs/runs/<run_id>/caps.tlv`
- Latest: `logs/caps_latest.tlv`

## Fields (Snapshot)
- Build identifiers: `version_string`, `build_id`, `git_hash`
- Platform: `os_family`, `os_version_major`, `os_version_minor`, `cpu_arch`, `ram_class`
- Providers: `provider_net`, `provider_trust`, `provider_keychain`, `provider_content`
- Capabilities: `supports_stdout_capture`, `supports_file_picker`, `supports_open_folder`, `supports_tls`
- Filesystem: `fs_perm_model`, `max_path_len`
- Available backends (ordered, stable)
- Selected backends (ordered, stable)

The snapshot is produced from the Domino caps registry and selection API. Ordering is deterministic and does not depend on registration order.

