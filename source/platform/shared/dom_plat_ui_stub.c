#include "dominium/dom_plat_ui.h"

static const struct dom_ui_vtable* g_ui_none = 0;

const struct dom_ui_vtable* dom_plat_ui_probe(const struct dom_sys_vtable* sys)
{
    (void)sys;
    return g_ui_none;
}
