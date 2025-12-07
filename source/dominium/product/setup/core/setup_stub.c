#include <stdio.h>
#include "domino/sys.h"

int main(int argc, char** argv)
{
    dm_sys_context* sys = dm_sys_init();
    (void)argc; (void)argv;
    dm_sys_log(DM_SYS_LOG_INFO, "setup", "Dominium setup stub");
    dm_sys_shutdown(sys);
    return 0;
}
