/*
FILE: source/domino/system/core/base/shared/uuid.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/shared/uuid
RESPONSIBILITY: Implements `uuid`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_shared/uuid.h"

#include <sstream>
#include <cstdlib>
#include <ctime>
#include <cstdio>

namespace dom_shared {

static unsigned int next_rand()
{
    static bool seeded = false;
    if (!seeded) {
        std::srand((unsigned int)std::time(0));
        seeded = true;
    }
    return (unsigned int)std::rand();
}

std::string generate_uuid()
{
    unsigned char bytes[16];
    for (int i = 0; i < 16; ++i) {
        bytes[i] = (unsigned char)(next_rand() & 0xFF);
    }
    bytes[6] = (unsigned char)((bytes[6] & 0x0F) | 0x40); // version 4
    bytes[8] = (unsigned char)((bytes[8] & 0x3F) | 0x80); // variant

    char buf[37];
    std::sprintf(buf,
                 "%02x%02x%02x%02x-"
                 "%02x%02x-"
                 "%02x%02x-"
                 "%02x%02x-"
                 "%02x%02x%02x%02x%02x%02x",
                 bytes[0], bytes[1], bytes[2], bytes[3],
                 bytes[4], bytes[5],
                 bytes[6], bytes[7],
                 bytes[8], bytes[9],
                 bytes[10], bytes[11], bytes[12], bytes[13], bytes[14], bytes[15]);
    return std::string(buf);
}

} // namespace dom_shared
