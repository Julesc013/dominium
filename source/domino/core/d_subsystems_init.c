#include "res/d_res.h"
#include "env/d_env.h"
#include "world/d_litho.h"
#include "hydro/d_hydro.h"
#include "build/d_build.h"
#include "core/d_org.h"
#include "policy/d_policy.h"
#include "research/d_research_state.h"
#include "econ/d_econ_metrics.h"
#include "trans/d_trans.h"
#include "struct/d_struct.h"
#include "vehicle/d_vehicle.h"
#include "job/d_job.h"
#include "net/d_net.h"
#include "replay/d_replay.h"

static int g_subsystems_initialized = 0;

void d_subsystems_init(void) {
    if (g_subsystems_initialized) {
        return;
    }
    d_res_init();
    d_env_init();
    d_litho_init();
    d_hydro_init();
    d_build_register_subsystem();
    d_trans_register_subsystem();
    d_org_register_subsystem();
    d_policy_register_subsystem();
    d_research_register_subsystem();
    d_struct_init();
    d_econ_register_subsystem();
    d_vehicle_init();
    d_job_init();
    d_net_register_subsystem();
    d_replay_register_subsystem();
    g_subsystems_initialized = 1;
}
