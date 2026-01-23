# Observability Pipelines

APR4 adds read-only observability outputs for client and tools. All paths are
pack-agnostic and deterministic in CLI mode.

## CLI
### Client
- `client --topology` prints `packages_tree` summary using
  `dom_app_ro_print_topology_bundle`.
- `client --snapshot` and `client --events` report unsupported and exit
  non-zero.
- `--format text|json` selects output format; JSON ordering is stable.

### Tools
- `tools inspect` prints core info + topology + support flags.
- `tools validate` prints compatibility report; no gameplay validation.
- `tools replay` is unsupported and exits non-zero.

## TUI
- `client --ui=tui` shows a list of topology nodes with metadata
  (snapshot unsupported).
- `tools --ui=tui` uses the tools TUI shell and dispatches
  inspect/validate/replay after exit.
- TUI is optional and not used by tests.

## GUI
- `client --ui=gui` opens a window via the platform runtime and draws a
  procedural overlay.
- Overlay shows package/instance counts and supported/unsupported flags.
- GUI is optional and not used by tests.
