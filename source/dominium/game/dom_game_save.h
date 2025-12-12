#ifndef DOM_GAME_SAVE_H
#define DOM_GAME_SAVE_H

#include <string>

extern "C" {
#include "d_world.h"
#include "d_serialize.h"
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

} // namespace dom

#endif
