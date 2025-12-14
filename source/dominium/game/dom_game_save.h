#ifndef DOM_GAME_SAVE_H
#define DOM_GAME_SAVE_H

#include <string>
#include <vector>

extern "C" {
#include "world/d_world.h"
#include "world/d_serialize.h"
}

namespace dom {

bool game_save_world(
    d_world             *world,
    const std::string   &path
);

bool game_load_world(
    d_world             *world,
    const std::string   &path
);

/* In-memory save/load helpers for snapshotting. */
bool game_save_world_blob(
    d_world                       *world,
    std::vector<unsigned char>    &out
);

bool game_load_world_blob(
    d_world                  *world,
    const unsigned char      *data,
    size_t                    size
);

} // namespace dom

#endif
