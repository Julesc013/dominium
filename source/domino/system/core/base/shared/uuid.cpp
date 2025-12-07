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
