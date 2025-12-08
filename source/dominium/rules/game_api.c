#include "dominium/game_api.h"

struct dom_game_runtime {
    const dom_game_runtime_desc* desc;
};

dom_status dom_game_runtime_create(const dom_game_runtime_desc* desc,
                                   dom_game_runtime** out_runtime)
{
    (void)desc;
    (void)out_runtime;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_game_runtime_destroy(dom_game_runtime* runtime)
{
    (void)runtime;
}

dom_status dom_game_runtime_tick(dom_game_runtime* runtime, uint32_t dt_millis)
{
    (void)runtime;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_game_runtime_execute(dom_game_runtime* runtime,
                                    const dom_game_command* cmd)
{
    (void)runtime;
    (void)cmd;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_game_runtime_query(dom_game_runtime* runtime,
                                  const dom_game_query* query,
                                  void* response_buffer,
                                  size_t response_buffer_size)
{
    (void)runtime;
    (void)query;
    (void)response_buffer;
    (void)response_buffer_size;
    return DOM_STATUS_UNSUPPORTED;
}
