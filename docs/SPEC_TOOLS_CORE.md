# Dominium Tool Core

Common ABI and host wiring for Dominium command-line tools. Each tool shares the same entry shape so it can be invoked directly or through the unified `dominium-tools` host binary.

## Core types

- `dom_tool_env`: runtime environment passed to tools. Size/version fields must be set by the caller. I/O callbacks are optional; when `NULL`, tools use stdio. `core` can point at a `dom_core_t` instance if the tool needs engine services.
- `dom_tool_ctx`: wraps the environment plus an opaque `user_data` pointer owned by the tool.
- `dom_tool_desc`: registry entry describing a tool (id, name, description, kind, entry function). The registry lives in `tool_core.c`.

## Adding a new tool

1. Implement a `dom_tool_<id>_main(dom_tool_ctx *ctx, int argc, char **argv)` entry point. Populate `ctx->env` fields as needed and return an exit code.
2. Add a `dom_tool_reg_entry` entry in `g_tools` inside `source/dominium/tools/core/tool_core.c` with struct size/version set and `entry` pointing at the function from step 1.
3. Link the tool’s target against `dominium_tools_core` so the registry and ABI types are available.

## Running tools

- Unified host: `dominium-tools <tool-id> [args]` (for example `dominium-tools assetc ...` or `dominium-tools world-edit ...` once added). With no arguments, the host prints available tools and descriptions.
- From code: call `dom_tool_run("assetc", &env, argc, argv)` or enumerate via `dom_tool_list`.

The host and registry currently seed `assetc` and `pack`; additional editors and analyzers can be added following the steps above.
