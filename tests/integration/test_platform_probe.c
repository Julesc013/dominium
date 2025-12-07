#include "dominium/dom_plat_sys.h"
#include "dominium/dom_plat_term.h"
#include "dominium/dom_plat_ui.h"
#include "dominium/dom_core.h"

int main(void)
{
    const struct dom_sys_vtable* sys = dom_plat_sys_choose_best();
    const struct dom_term_vtable* term = dom_plat_term_probe(sys);
    const struct dom_ui_vtable* ui = dom_plat_ui_probe(sys);
    if (!sys) {
        dom_log(DOM_LOG_ERROR, "test_platform_probe", "no sys vtable");
        return 1;
    }
    dom_log(DOM_LOG_INFO, "test_platform_probe", term ? "term=yes" : "term=no");
    dom_log(DOM_LOG_INFO, "test_platform_probe", ui ? "ui=yes" : "ui=no");
    return 0;
}
