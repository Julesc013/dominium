#include "res/d_res.h"
#include "env/d_env.h"
#include "build/d_build.h"
#include "trans/d_trans.h"
#include "struct/d_struct.h"
#include "vehicle/d_vehicle.h"
#include "job/d_job.h"

static int g_subsystems_initialized = 0;

void d_subsystems_init(void) {
    if (g_subsystems_initialized) {
        return;
    }
    d_res_init();
    d_env_init();
    d_build_init();
    d_trans_init();
    d_struct_init();
    d_vehicle_init();
    d_job_init();
    g_subsystems_initialized = 1;
}
