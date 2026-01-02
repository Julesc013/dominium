/*
FILE: source/dominium/game/runtime/dom_game_runtime.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_runtime
RESPONSIBILITY: Defines internal runtime kernel contract; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal struct versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_RUNTIME_H
#define DOM_GAME_RUNTIME_H

#include "domino/core/types.h"

#include "runtime/dom_game_command.h"
#include "runtime/dom_game_query.h"

#ifdef __cplusplus
extern "C" {
#endif
struct d_world;
struct d_sim_context;
struct d_replay_context;
#ifdef __cplusplus
} /* extern "C" */
#endif

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_GAME_RUNTIME_OK = 0,
    DOM_GAME_RUNTIME_ERR = -1,
    DOM_GAME_RUNTIME_REPLAY_END = 1
};

enum {
    DOM_GAME_RUNTIME_INIT_DESC_VERSION = 1u
};

typedef struct dom_game_runtime dom_game_runtime;

typedef struct dom_game_runtime_init_desc {
    u32 struct_size;
    u32 struct_version;
    void *session;        /* dom::DomSession* */
    void *net;            /* dom::DomGameNet* */
    const void *instance; /* dom::InstanceInfo* */
    u32 ups;
} dom_game_runtime_init_desc;

dom_game_runtime *dom_game_runtime_create(const dom_game_runtime_init_desc *desc);
void dom_game_runtime_destroy(dom_game_runtime *rt);

int dom_game_runtime_pump(dom_game_runtime *rt);
int dom_game_runtime_step(dom_game_runtime *rt);
int dom_game_runtime_tick_wall(dom_game_runtime *rt, u64 wall_dt_usec, u32 *out_ticks);

int dom_game_runtime_execute(dom_game_runtime *rt, const dom_game_command *cmd, u32 *out_tick);

u64 dom_game_runtime_get_tick(const dom_game_runtime *rt);
u64 dom_game_runtime_get_seed(const dom_game_runtime *rt);
u32 dom_game_runtime_get_ups(const dom_game_runtime *rt);
u64 dom_game_runtime_get_hash(const dom_game_runtime *rt);
int dom_game_runtime_get_counts(const dom_game_runtime *rt, dom_game_counts *out_counts);

u32 dom_game_runtime_input_delay(const dom_game_runtime *rt);
u32 dom_game_runtime_next_cmd_tick(const dom_game_runtime *rt);

struct d_world *dom_game_runtime_world(dom_game_runtime *rt);
struct d_sim_context *dom_game_runtime_sim(dom_game_runtime *rt);
struct d_replay_context *dom_game_runtime_replay(dom_game_runtime *rt);
const void *dom_game_runtime_session(const dom_game_runtime *rt);
const void *dom_game_runtime_instance(const dom_game_runtime *rt);

int dom_game_runtime_set_replay_last_tick(dom_game_runtime *rt, u32 last_tick);
int dom_game_runtime_set_replay_playback(dom_game_runtime *rt, void *playback);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_GAME_RUNTIME_H */
