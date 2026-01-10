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

## Relationship to Net Commands

- **Recording net sessions:** Dominium can record the *applied* deterministic command stream by capturing encoded `D_NET_MSG_CMD` packets per tick (see `d_net_set_tick_cmds_observer` in `source/domino/net/d_net_apply.c` and usage in `source/dominium/game/dom_game_app.cpp`).
- **Replay payloads:** For net capture, each `d_net_input_frame.payload` is a full framed packet (the same bytes that would be sent over the transport), which allows playback to use the same decode/enqueue path.
- **Playback injection:** During playback, Dominium re-injects recorded packets by calling `d_net_receive_packet(...)` before `d_sim_step`, ensuring deterministic equivalence between offline replay and online command reception.

## Tooling (read-only)
- Replay analysis tools are read-only and must not modify replay data in-place.
- When launched via the launcher, tools validate the handshake/instance identity before analysis.
- Tool outputs (reports, diffs) are written under `DOMINIUM_RUN_ROOT`.
