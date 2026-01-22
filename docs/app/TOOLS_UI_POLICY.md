# Tools UI Policy

- Tools are CLI-first; TUI is optional (`--ui=tui` or `--tui`) and never
  required by tests.
- GUI usage is allowed via `--ui=gui` but remains optional and bypassable in
  CLI-only modes.
- Any future GUI uses the platform runtime (`dsys_window_*`); no toolkit is
  mandated by policy.
- Tools remain read-only by default; elevation or write actions are explicit.
