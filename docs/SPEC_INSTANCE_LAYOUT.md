# Instance Layout (STATE roots)

Instances persist to disk and are rebuilt into memory on every
`dom_core_create`. All paths are anchored to `dsys_get_path(DSYS_PATH_USER_DATA)`
unless a caller explicitly provides an override path.

## Directory layout
```
<user_data>/instances/<instance_name>/
  instance.ini       (descriptor)
  saves/
  config/
  logs/
```
- `<instance_name>` is used as the directory name when no explicit path is
  provided.
- Descriptor and subdirectories are created when an instance is created.
- Portable installs created by the setup engine override the base path to
  `<install_root>/instances/<instance_name>` to keep the install self-contained;
  the same subdirectory layout is used inside that root.

## Descriptor format (`instance.ini`)
Plain text `key=value` lines:
- `id` – integer instance id (stable across restarts).
- `name` – display name.
- `flags` – bitfield for instance mode (portable/per-user/system, etc).
- `packages` – comma-separated list of package ids (names). Resolved against the
  package registry on load.
- `path` – absolute or relative path to the instance root.
- `saves_path`, `config_path`, `logs_path` – absolute/relative paths for those
  folders. Defaults live under the instance root.

## Behaviour
- On startup the core walks `<user_data>/instances/`, loads every
  `instance.ini`, resolves package references by name, and assigns ids in sorted
  path order to keep behaviour deterministic.
- Instance ids are monotonically increasing; the next id is
  `max(scanned ids)+1`.
- Creating/updating an instance rewrites `instance.ini` to mirror the in-memory
  `dom_instance_info`.
- Deleting an instance removes it from the registry and recursively deletes the
  instance directory tree.
