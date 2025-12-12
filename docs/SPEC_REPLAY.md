# DREPLAY – deterministic record/playback

- **Frames:** `dreplay_frame` binds a `tick_index` to an array of `d_net_input_frame` entries. Payload bytes are copied and owned by the replay when recording/deserializing.
- **Context:** `d_replay_context` stores mode (OFF/RECORD/PLAYBACK), the frame array, capacity, and a playback cursor.
  - `d_replay_init_record(ctx, cap)` allocates optional initial capacity and switches to RECORD.
  - `d_replay_init_playback(ctx, frames, count)` points at external frames (non-owned) and switches to PLAYBACK.
  - `d_replay_shutdown` frees owned frames/payloads and resets the context.
- **Recording:** `d_replay_record_frame` appends or replaces the frame for a tick, deep-copying input payloads; grows storage as needed.
- **Playback:** `d_replay_get_frame` locates the frame for `tick_index` (cursor fast-path + linear search) and copies metadata to caller-provided buffers; returns the required count if capacity is insufficient.
- **Serialization:** `d_replay_serialize` emits a TLV blob with one entry per frame (tag `1`):
  - Payload layout: `tick_index (u32)`, `input_count (u32)`, then for each input `{tick_index, player_id, payload_size, payload bytes}`.
  - `d_replay_deserialize` parses the blob, allocates owned frames/payloads, and prepares a PLAYBACK context.
- **Subsystem:** `d_replay_register_subsystem` registers `D_SUBSYS_REPLAY` with no-op tick and empty instance serialization; replay data is expected to be stored by higher-level game flows around `d_sim_step`.
