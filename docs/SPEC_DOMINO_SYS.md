# Platform API (domino_sys)

Public header: `include/domino/sys.h`  
Core code: `source/domino/system/core`  
Backends: `source/domino/system/plat/*`

## ABI (dsys_*) snapshot
- Opaque `dsys_context` via `dsys_create(const dsys_desc*, dsys_context**)` / `dsys_destroy`; `dsys_desc` is versioned and carries a profile hint plus optional log hook.
- Platform + paths: `dsys_get_platform_info` returns `dsys_platform_info` (`os`, `cpu`, `pointer_size`, `page_size`, `flags`), `dsys_get_paths` returns `dsys_paths` (`install/program/data/user/state/temp` roots).
- Facilities: `dsys_time_ticks/time_seconds/sleep_millis`, `dsys_file_*`, `dsys_dir_*`, and `dsys_process_*` mirror the legacy API but keep opaque handles and versioned structs; all are stubbed today.
- Logging: `dsys_set_log_hook` installs a callback for higher layers; if unset the stub does nothing.
- Legacy `domino_sys_*` surface stays for existing runtime code; `dsys_*` is the public, C89-safe ABI exported to external consumers.

## Surface
- `domino_sys_context` opaque handle; create with `domino_sys_init(const domino_sys_desc*, domino_sys_context**)`, destroy with `domino_sys_shutdown`.
- Platform info: `domino_sys_platform_info` (`os`, `cpu`, `profile`, `is_legacy`, `has_threads`, `has_fork`, `has_unicode`) via `domino_sys_get_platform_info`.
- Profiles: `AUTO/TINY/REDUCED/FULL` hint at capability level.
- Paths: `domino_sys_paths` (`install_root`, `program_root`, `data_root`, `user_root`, `state_root`, `temp_root`) via `domino_sys_get_paths`.
- Filesystem: `domino_sys_file` with `fopen/fread/fwrite/fclose`, `domino_sys_file_exists`, `domino_sys_mkdirs`.
- Directory iteration: `domino_sys_dir_iter` with `dir_open/dir_next/dir_close`.
- Time: `domino_sys_time_seconds`, `domino_sys_time_millis`, `domino_sys_sleep_millis`.
- Processes: `domino_sys_process_desc` (`path`, `argv`, `working_dir`), `domino_sys_process_spawn/wait/destroy`.
- Logging: `domino_sys_log(domino_log_level, subsystem, message)`; falls back to stdio if no backend hook.
- Terminal: `domino_term_context` with `domino_term_init/shutdown`, `domino_term_write`, `domino_term_read_line` (stdio stub for now).

## Availability by profile
- TINY/legacy: expect stubs for processes/dirs and reduced path handling.
- REDUCED: basic filesystem/time/logging; processes may be limited.
- FULL: all above; best-effort process spawning and directory walk.

## Backends (this pass)
- Win32 (`source/domino/system/plat/windows/win32/sys_win32.c`): stdio file I/O, FindFirstFile dir walk, QueryPerformanceCounter timing, CreateProcess, Sleep, path discovery from module path.
- POSIX (`source/domino/system/plat/unix/posix/sys_posix.c`): stdio file I/O, `opendir/readdir`, `clock_gettime`, `posix_spawn`/`waitpid`, `usleep`.
- Stub (`source/domino/system/plat/null/sys_null.c`): minimal stdio-backed file I/O and monotonic-ish timing; mkdir/process/dir are TODO.

## Notes
- `domino_sys_init` picks backend from compile-time platform; falls back to stub.
- Paths default to cwd-based roots (`./program`, `./data`, `./user`, `./state`, `./temp`) if the backend does not supply better values.
- Terminal/native UI are intentionally minimal; a fuller UI backend will replace `domino_ui_*` stubs later.

## Products on top of domino_sys
- Setup: reads `domino_sys_paths` to find install/data/user/state roots; uses `domino_sys_mkdirs` for root creation and `domino_sys_dir_*` to scan `program/` for installed product manifests.
- Launcher: uses `domino_sys_get_paths` for install/data/user/state roots, `domino_sys_dir_*` to enumerate packages and instances under `state_root/instances`, and `domino_sys_process_spawn/wait` to start game binaries.
- Tools: reuse the same path discovery, filesystem, and process utilities for batch validators (for example, `dominium_modcheck`).
- Game: uses `domino_sys_init` for platform info, filesystem, and timing, then hands the context to `domino_gfx_create_device`.
