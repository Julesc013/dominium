# Launcher CLI

The CLI launcher is a headless/front-end for servers, remote shells, and quick
testing. It runs in a terminal and talks only to the launcher core API
(`dom_launch_*`) plus Domino table models; no curses or GUI dependencies.

## Commands
- `help` — show command list.
- `list instances` — print the `instances_table`.
- `create instance <name>` — create a new instance (name optional; defaults to
  "New Instance").
- `delete instance <id>` — delete by instance id.
- `launch <id>` — launch the instance via `dom_launch_run_instance`.
- `list packages` — print the `packages_table`.
- `quit` / `exit` — leave the launcher.

## Example session
```
$ dominium-launcher-cli
Dominium CLI launcher. Type 'help' for commands.
dominium> list instances
id      name    path    flags   pkg_count       last_played
1       demo    /home/user/.dominium/instances/demo   0       1
dominium> create instance MyWorld
id      name    path    flags   pkg_count       last_played
1       demo    ...
2       MyWorld ...
dominium> launch 2
dominium> list packages
id      name    version kind    path
1       dominium        0.1.0   product /home/user/.dominium/packages/dominium
dominium> quit
```

## Notes
- The CLI keeps the launcher core state machine in sync by emitting
  `dom_launch_handle_action` calls for every command.
- Table rendering uses Domino's view/model APIs (`dom_table_get_meta` and
  `dom_table_get_cell`); no cached state is kept in the front-end.
