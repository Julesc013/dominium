# No-Modal-Loading Backlog (Render/UI Thread)

Status: audit (P0.1).
Scope: game main loop, UI thread, runtime glue, save/replay/handshake IO.

Each item lists the blocking behavior and the intended replacement (derived job,
snapshot, or refusal-first path).

- source/dominium/game/dom_game_app.cpp:105
  - Blocking behavior: replay recording writes to disk per tick via
    `dom_game_replay_record_write_cmd` inside `dom_net_replay_tick_observer`.
  - Replacement: enqueue derived IO job to append replay packets; keep an
    in-memory ring buffer and flush via derived queue with budgets.

- source/dominium/game/dom_game_app.cpp:250-276
  - Blocking behavior: `emit_refusal` writes refusal TLV to disk in UI thread
    via `write_refusal_tlv`.
  - Replacement: derived IO job for refusal TLV; fall back to stderr logging if
    queue is unavailable.

- source/dominium/game/dom_game_app.cpp:258-303
  - Blocking behavior: `find_dominium_home_from` + `dir_exists` walk filesystem
    during init when dev ad-hoc paths are enabled.
  - Replacement: disallow ad-hoc scanning in launcher mode; move any optional
    probing to derived job and surface as non-blocking status.

- source/dominium/game/dom_game_app.cpp:922
  - Blocking behavior: `dom_game_runtime_save` called during shutdown to write
    save file.
  - Replacement: schedule derived save write; if shutdown must proceed, emit
    refusal/diagnostic and skip save (refusal-first).

- source/dominium/game/dom_game_app.cpp:935-939
  - Blocking behavior: replay record/play close during shutdown (file IO).
  - Replacement: defer close/flush to derived IO; finalize on best-effort and
    report status.

- source/dominium/game/dom_game_app.cpp:1016
  - Blocking behavior: `dom_game_handshake_from_file` loads handshake via
    synchronous file read.
  - Replacement: derived IO read + parse; refuse to enter session if handshake
    missing after timeout; never block UI thread.

- source/dominium/game/dom_game_app.cpp:1175-1177
  - Blocking behavior: `m_instance.load` / `m_instance.save` perform synchronous
    file IO during init.
  - Replacement: derived IO jobs to read/write instance TLV; phase gates on
    readiness without blocking.

- source/dominium/game/dom_game_app.cpp:1258-1302
  - Blocking behavior: `dom_game_replay_play_open` / `dom_game_replay_record_open`
    open replay files synchronously.
  - Replacement: derived IO open + header parse; UI shows non-authoritative
    readiness flags.

- source/dominium/game/dom_game_app.cpp:1359
  - Blocking behavior: `dom_game_runtime_load_save` reads and parses save file
    synchronously during session init.
  - Replacement: derived IO read + parse; runtime waits on readiness flags and
    degrades fidelity until loaded.

- source/dominium/game/dom_game_app.cpp:1673
  - Blocking behavior: `d_system_sleep_ms` in `main_loop` blocks UI thread.
  - Replacement: frame pacing via non-blocking yield or budgeted pump; allow
    idle without sleep (or move sleep to headless only).

- source/dominium/game/frontends/gui/dom_game_frontend_gui.cpp:24-47
  - Blocking behavior: `d_system_sleep_ms(1u)` used when no ticks are stepped.
  - Replacement: no blocking sleeps on GUI thread; use derived queue pump and
    non-blocking event polling.

- source/dominium/game/frontends/tui/dom_game_frontend_tui.cpp:24-47
  - Blocking behavior: `d_system_sleep_ms(1u)` in TUI loop.
  - Replacement: same as GUI; budgeted pump, non-blocking idle handling.

- source/dominium/game/frontends/headless/dom_game_frontend_headless.cpp:24-47
  - Blocking behavior: `d_system_sleep_ms(1u)` in headless loop.
  - Replacement: non-blocking pacing; if sleep remains, isolate to headless
    worker thread (not UI thread).

- source/dominium/game/runtime/dom_game_handshake.cpp:55-93, 128-142
  - Blocking behavior: `std::ifstream` read of handshake TLV.
  - Replacement: derived IO read; parser must accept bytes from job result.

- source/dominium/game/runtime/dom_game_save.cpp:426-489
  - Blocking behavior: `read_file_alloc` / `write_file` used by save load/write.
  - Replacement: derived IO job for read/write; runtime should consume prepared
    buffers without blocking.

- source/dominium/game/runtime/dom_game_replay.cpp:60-139, 178-218
  - Blocking behavior: `dsys_file_open/read/write/close` in replay read/write
    helpers.
  - Replacement: derived IO read/write/append jobs; keep replay packets in
    memory until flushed.

- source/dominium/common/dom_instance.cpp:34-92, 150-219
  - Blocking behavior: instance TLV read/write via `dsys_file_*`.
  - Replacement: derived IO jobs; instance info becomes a readiness snapshot.

