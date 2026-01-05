/*
FILE: source/dominium/game/frontends/tui/dom_game_frontend_tui.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/frontends/tui
RESPONSIBILITY: Implements a thin TUI frontend loop over the runtime kernel.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_io_guard.h"

extern "C" {
#include "domino/sys.h"
#include "domino/system/d_system.h"
}

extern "C" int dom_game_frontend_tui_run(dom_game_runtime *rt, u32 max_ticks) {
    if (!rt) {
        return 1;
    }

    u64 last_us = dsys_time_now_us();
    u32 total = 0u;
    const u32 stall_threshold_ms = 100u;

    while (max_ticks == 0u || total < max_ticks) {
        const u64 frame_start_us = dsys_time_now_us();
        const u64 now_us = dsys_time_now_us();
        const u64 dt_us = (now_us >= last_us) ? (now_us - last_us) : 0u;
        u32 stepped = 0u;
        int rc;

        dom_io_guard_enter_ui();

        last_us = now_us;
        (void)dom_game_runtime_pump(rt);
        rc = dom_game_runtime_tick_wall(rt, dt_us, &stepped);
        total += stepped;

        if (rc == DOM_GAME_RUNTIME_REPLAY_END) {
            dom_io_guard_exit_ui();
            break;
        }
        if (stepped == 0u) {
            d_system_sleep_ms(1u);
        }

        dom_io_guard_exit_ui();

        {
            const u64 frame_end_us = dsys_time_now_us();
            const u64 frame_ms = (frame_end_us >= frame_start_us)
                                     ? ((frame_end_us - frame_start_us) / 1000ull)
                                     : 0ull;
            if (frame_ms > (u64)stall_threshold_ms) {
                dom_io_guard_note_stall((u32)frame_ms, stall_threshold_ms);
            }
        }
    }

    return 0;
}
