# DSIM – deterministic simulation orchestrator

DSIM is the engine-level tick loop that advances ECS-style systems in a fixed order.

- **Context:** `d_sim_context` stores the current world pointer, global tick counter, and fixed tick duration (`q16_16`).
- **Systems:** `dsim_system_vtable` identifies each system (`system_id`, `name`) and optional `init`, `tick`, and `shutdown` callbacks. Systems are invoked in registration order for determinism.
- **Registration:** `d_sim_register_system` adds a vtable to the global list; duplicates or capacity overflow fail.
- **Init/Shutdown:** `d_sim_init` seeds the context (resets tick index, sets world/dt, calls each system `init`). `d_sim_shutdown` calls `shutdown` callbacks and clears the context.
- **Ticking:** `d_sim_step(ctx, ticks)` advances `ctx->tick_index` once per tick and runs:
  1. All registered `d_subsystem_desc.tick` callbacks (registration order).
  2. All DSIM systems’ `tick` callbacks (registration order).
- **Integration path:** Higher layers gather inputs → run net/replay to produce authoritative input frames → call `d_sim_step` to advance the deterministic world.
