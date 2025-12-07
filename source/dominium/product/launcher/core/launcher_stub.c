#include <stdio.h>
#include "domino/sys.h"
#include "dominium/launch_api.h"

int main(int argc, char** argv)
{
    dm_sys_context* sys = dm_sys_init();
    (void)argc; (void)argv;
    dm_sys_log(DM_SYS_LOG_INFO, "launcher", "Dominium launcher stub");
    dm_sys_shutdown(sys);
    return 0;
}
