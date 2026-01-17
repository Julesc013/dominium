/*
Intentionally forbidden UI include to ensure compile-time boundary enforcement.
This file is used by a try-compile test that expects failure.
*/
#include "engine/modules/sim/d_sim.h"

int ui_bypass_should_fail(void)
{
    return 0;
}
