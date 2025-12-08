#include <stdio.h>
#include "domino/sys.h"
#include "dominium/launch_api.h"

int main(int argc, char** argv)
{
    domino_sys_context* sys = NULL;
    domino_sys_desc sdesc;
    (void)argc; (void)argv;

    sdesc.profile_hint = DOMINO_SYS_PROFILE_AUTO;
    if (domino_sys_init(&sdesc, &sys) != 0 || !sys) {
        return 1;
    }
    domino_sys_log(sys, DOMINO_LOG_INFO, "launcher", "Dominium launcher stub");
    domino_sys_shutdown(sys);
    return 0;
}
