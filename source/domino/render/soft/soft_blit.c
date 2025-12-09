#include "soft_blit.h"

static soft_present_fn g_soft_present = (soft_present_fn)0;

void soft_blit_set_present_callback(soft_present_fn fn)
{
    g_soft_present = fn;
}

soft_present_fn soft_blit_get_present_callback(void)
{
    return g_soft_present;
}
