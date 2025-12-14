#ifndef DOM_GAME_REPLAY_H
#define DOM_GAME_REPLAY_H

#include <string>

extern "C" {
#include "replay/d_replay.h"
}

namespace dom {

bool game_save_replay(const d_replay_context *ctx, const std::string &path);
bool game_load_replay(const std::string &path, d_replay_context *out_ctx);
u32  game_replay_last_tick(const d_replay_context *ctx);

} // namespace dom

#endif

