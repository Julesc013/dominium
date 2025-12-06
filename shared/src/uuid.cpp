#include "dom_shared/uuid.h"

#include <sstream>
#include <cstdlib>
#include <ctime>
#include <cstdio>

static unsigned int next_rand()
{
    return (unsigned int)std::rand();
}

static std::string hex4(unsigned int v)
{
    char buf[9];
    std::sprintf(buf, "%04x%04x", (v >> 16) & 0xFFFFu, v & 0xFFFFu);
    return std::string(buf, 8);
}

std::string generate_uuid()
{
    std::srand((unsigned int)std::time(0));
    std::string a = hex4(next_rand());
    std::string b = hex4(next_rand());
    std::string c = hex4(next_rand());
    std::string d = hex4(next_rand());
    std::string e = hex4(next_rand());
    return a + "-" + b + "-" + c + "-" + d + "-" + e;
}
