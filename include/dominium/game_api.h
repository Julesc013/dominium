#ifndef DOMINIUM_GAME_API_H
#define DOMINIUM_GAME_API_H

#include <stddef.h>
#include <stdint.h>

#include "domino/core.h"
#include "domino/mod.h"
#include "domino/sim.h"
#include "domino/canvas.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_game_runtime dom_game_runtime;

typedef struct dom_game_runtime_desc {
    uint32_t struct_size;
    uint32_t struct_version;
    dom_core* core;
    dom_sim* sim;
    dom_canvas* canvas;
    void*     user_data;
} dom_game_runtime_desc;

typedef struct dom_game_command {
    uint32_t    struct_size;
    uint32_t    struct_version;
    const char* name;
    const void* payload;
    size_t      payload_size;
} dom_game_command;

typedef struct dom_game_query {
    uint32_t    struct_size;
    uint32_t    struct_version;
    const char* name;
    const void* payload;
    size_t      payload_size;
} dom_game_query;

typedef struct dom_game_sim_step_args {
    uint32_t        struct_size;
    uint32_t        struct_version;
    dom_instance_id inst;
    double          dt_s;
} dom_game_sim_step_args;

dom_status dom_game_runtime_create(const dom_game_runtime_desc* desc,
                                   dom_game_runtime** out_runtime);
void       dom_game_runtime_destroy(dom_game_runtime* runtime);
dom_status dom_game_runtime_tick(dom_game_runtime* runtime, uint32_t dt_millis);
dom_status dom_game_runtime_execute(dom_game_runtime* runtime,
                                    const dom_game_command* cmd);
dom_status dom_game_runtime_query(dom_game_runtime* runtime,
                                  const dom_game_query* query,
                                  void* response_buffer,
                                  size_t response_buffer_size);

/* Called by Domino sim for each instance tick */
void dom_game_sim_step(dom_core* core, const dom_game_sim_step_args* args);
uint64_t dom_game_debug_sim_steps(dom_instance_id inst);

/* Convenience entry point used by current product layer */
int dominium_game_run(const domino_instance_desc* inst);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_GAME_API_H */
