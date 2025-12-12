# DNET – deterministic networking model

- **Profiles:** `d_proto_net_profile` describes a network profile (`id`, `name`, `mode`, `flags`, `params` TLV payload). Kept as proto-level data for future backends.
- **Inputs:** `d_net_input_frame` wraps per-tick player inputs (tick index, player id, payload bytes). Payload encoding is owned by higher layers.
- **Context:** `d_net_context` tracks the active profile, local player id, and peer count. `d_net_init` sets up the context; `d_net_shutdown` clears it.
- **Lockstep API:** `d_net_step_lockstep` accepts local input frames and returns authoritative frames. Current implementation is single-player: it echoes local frames up to caller-provided capacity.
- **Subsystem:** `d_net_register_subsystem` registers `D_SUBSYS_NET` with empty serialization and a no-op tick so save/load containers reserve the NET tag without data.
- **Status:** Implementation is stubbed for single-player determinism; API is stable for future socket/backends without changing callers.
