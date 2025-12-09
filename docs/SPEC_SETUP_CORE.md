# Setup Core

The setup core is a shared, OS-agnostic engine for installing, repairing,
uninstalling, and verifying Dominium builds. Native installers (MSI/pkg/deb)
and the setup CLI call into this layer instead of duplicating logic.

## Public API
- Header: `include/dominium/setup_api.h`
- `dom_setup_desc` (struct_size/struct_version = 1) selects product metadata,
  install scope, optional target directory, and flags (`quiet`, `no_launcher`,
  `no_desktop_shortcuts`).
- `dom_setup_command` (struct_size/struct_version = 1) selects an action
  (`install`, `repair`, `uninstall`, `verify`) and optionally points at an
  existing install root.
- `dom_setup_progress` (struct_size/struct_version = 1) carries simple counters
  (`bytes_total/done`, `files_total/done`) plus a `current_step` string for
  progress callbacks.
- Lifecycle: `dom_setup_create(dom_core*, desc, &ctx)` → work → `dom_setup_destroy(ctx)`.
- Execution: `dom_setup_execute(ctx, cmd, progress_cb, user)` drives the action;
  callbacks are optional.

## Scope and paths
- `portable`: install root is `desc.target_dir` or the current app root; data
  and logs live under the install root. Instances are created at
  `<install>/instances/default` to keep the install self-contained.
- `per-user`: install root defaults to `<DSYS_PATH_USER_DATA>/Dominium` unless
  overridden; data/log roots use `DSYS_PATH_USER_DATA`.
- `all-users`: install root defaults to `<DSYS_PATH_APP_ROOT>/Dominium` unless
  overridden; data/log roots still use `DSYS_PATH_USER_DATA`.
- `log_dir` is always `<data_root>/logs`.

## Actions
- `install`: create install/data/log roots, copy the distribution manifest from
  `<app_root>/dist/` into the install root, and ensure a default instance is
  registered via `dom_inst_create`.
- `repair`: re-run the copy/instance steps, replacing missing or damaged files.
- `uninstall`: remove the default instance (if present) and delete the install
  root.
- `verify`: walk the manifest under the install root and report missing files.

## Distribution seed
- The current manifest is a stub: it copies `dist/bin/dominium-placeholder.txt`
  and `dist/data/readme.txt` into the install root. Later prompts replace this
  with an auto-generated package manifest.

## CLI wrapper
- Target: `dominium-setup-cli`
- Flags: `--scope=portable|user|system`, `--action=install|repair|uninstall|verify`,
  optional `--dir=<path>`, and `--quiet`.
- Uses the same API to drive installs; progress prints simple counters unless
  `--quiet` is set.
