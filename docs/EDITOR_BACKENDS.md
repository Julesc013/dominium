# Editor Backends

Pure logic editing layers used by CLI/TUI/GUI tools. Each backend exposes a C API and a matching `dominium-tools` subcommand.

- `dom_world_edit_*` (`world_edit_core.c`): open a world, read/write chunks, flush changes.
- `dom_save_edit_*` (`save_edit_core.c`): enumerate and mutate save data via simple section/key pairs.
- `dom_game_edit_*` (`game_edit_core.c`): list and edit game-definition entities (recipes/items/machines) as JSON blobs.
- `dom_launcher_edit_*` (`launcher_edit_core.c`): manage launcher layout tabs and ordering.

Front-ends (CLI today, GUI later) should depend only on these APIs; the backends handle on-disk format details via Domino/DSYS I/O.
