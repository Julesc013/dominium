# UI Modes

All products accept `--ui=none|tui|gui`. The legacy `--tui` flag remains as an
alias for `--ui=tui`.

## Selection order
1) CLI flags (`--ui` / `--tui`)
2) Environment (`DOM_UI` or `DOM_UI_MODE`)
3) Product default

CLI flags always override the environment default.

## Mode behavior
- `none`: CLI-only mode (TESTX uses this path).
- `tui`: terminal UI layer (client/tools implemented in APR3).
- `gui`: optional windowed layer.

GUI selection is explicit: if a GUI implementation is missing, the product
returns a non-zero exit code and logs a clear error.

## CLI conflict rule
When `--ui` selects `tui` or `gui`, per-product CLI actions (commands, `--smoke`,
`--status`, etc.) are rejected with a usage error.
