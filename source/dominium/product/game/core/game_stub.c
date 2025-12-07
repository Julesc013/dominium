#include <stdio.h>
#include "domino/sys.h"
#include "domino/sim.h"
#include "domino/mod.h"

int main(int argc, char** argv)
{
    (void)argc; (void)argv;
    domino_sys_context* sys = NULL;
    domino_sys_desc sdesc;
    dm_mod_context* mod;
    dm_sim_context* sim;

    sdesc.profile_hint = DOMINO_SYS_PROFILE_AUTO;
    if (domino_sys_init(&sdesc, &sys) != 0 || !sys) {
        return 1;
    }

    mod = dm_mod_create();
    sim = dm_sim_create(NULL);
    domino_sys_log(sys, DOMINO_LOG_INFO, "game", "Dominium game stub");
    dm_sim_tick(sim, 0);
    dm_mod_destroy(mod);
    dm_sim_destroy(sim);
    domino_sys_shutdown(sys);
    return 0;
}
