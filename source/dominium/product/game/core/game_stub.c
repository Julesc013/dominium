#include <stdio.h>
#include "domino/sys.h"
#include "domino/sim.h"
#include "domino/mod.h"

int main(int argc, char** argv)
{
    (void)argc; (void)argv;
    dm_sys_context* sys = dm_sys_init();
    dm_mod_context* mod = dm_mod_create();
    dm_sim_context* sim = dm_sim_create(NULL);
    dm_sys_log(DM_SYS_LOG_INFO, "game", "Dominium game stub");
    dm_sim_tick(sim, 0);
    dm_mod_destroy(mod);
    dm_sim_destroy(sim);
    dm_sys_shutdown(sys);
    return 0;
}
